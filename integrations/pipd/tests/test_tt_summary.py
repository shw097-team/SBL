"""Guard the TT status projection (R3-EXT-04 / R-AUD-012).

The stored `.hgk/artifacts/TT_REGISTER.json` carried 22 rows in `tts[]` while `status_summary`
described only 17 and no `as_of_candidate` was bound to the head. `tools/tt_summary_check.py`
recomputes the projection from `tts[]` only; these tests pin that:

  1. after `--write`, the stored summary equals the recomputation (and binds the head);
  2. a status mutation makes the (previously fresh) stored summary fail `--assert` first;
  3. removing / adding a row fails `--assert` on `total`;
  4. load -> dump -> load preserves the row count, ids and statuses;
  5. the 22 rows are still present and no row's status was closed/changed by the tool.

Everything that mutates works on a COPY of the register in a temporary directory, so the tests
pass whether they run before or after the external `--write` acceptance step, and the real
register is never written by the suite.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
REGISTER = ROOT / ".hgk" / "artifacts" / "TT_REGISTER.json"

# The real histogram of the 22 rows. Pinning the exact multiset is what proves the tool neither
# renamed nor dropped a status.
EXPECTED_STATUS_COUNTS = {
    "OPEN": 16,
    "OPEN_OWNER_GATE": 2,
    "PARTIAL_CLOSED": 1,
    "PARTIAL": 1,
    "CLOSED": 1,
    "TEMP_CLOSED": 1,
}


def _load_tool():
    spec = importlib.util.spec_from_file_location("tt_summary_check",
                                                  ROOT / "tools" / "tt_summary_check.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


TT = _load_tool()


class TtSummaryProjection(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="tt-register-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.register = self.tmp / "TT_REGISTER.json"
        shutil.copyfile(REGISTER, self.register)

    # -- helpers ---------------------------------------------------------------------------
    def _run(self, *args: str) -> "tuple[int, str]":
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = TT.main([*args, "--register", str(self.register)])
        return rc, buf.getvalue()

    def _load(self, path: "Path | None" = None):
        return TT.load_register(path or self.register)

    def _dump(self, doc, path: "Path | None" = None) -> None:
        (path or self.register).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                                           encoding="utf-8")

    def _head(self):
        return TT.resolve_head(ROOT)["head"]

    # -- 1. stored summary == recomputation (after --write) --------------------------------
    def test_stored_summary_equals_recomputation_after_write(self) -> None:
        rc, _ = self._run("--write")
        self.assertEqual(rc, 0, "--write must succeed where HEAD is resolvable")
        doc = self._load()
        head = self._head()
        self.assertIsNotNone(head, "this checkout must expose a resolvable HEAD")
        expected = TT.build_projection(doc, head)
        self.assertEqual(doc["status_summary"], expected,
                         "after --write the stored summary must equal the recomputation")
        self.assertEqual(doc["as_of_candidate"], head, "candidate must be bound to HEAD")
        self.assertEqual(doc["status_summary"]["count"], doc["status_summary"]["total"])
        self.assertEqual(doc["status_summary"]["total"], len(doc["tts"]))
        # the buckets partition the rows exactly (nothing dropped, nothing double-counted)
        s = doc["status_summary"]
        self.assertEqual(s["closed"] + s["partial"] + s["open"] + s["open_owner_gate"]
                         + s["temp_closed"] + s["unknown"], s["total"])

    # -- 2. a status mutation makes the stale summary fail --assert ------------------------
    def test_status_mutation_fails_assert(self) -> None:
        rc, _ = self._run("--write")
        self.assertEqual(rc, 0)
        self.assertEqual(self._run("--assert")[0], 0, "a freshly written summary must assert OK")

        doc = self._load()
        victim = next(r for r in doc["tts"] if r["status"] == "OPEN")
        victim["status"] = "CLOSED"  # mutate one row, leave the stored summary stale
        self._dump(doc)

        rc, out = self._run("--assert")
        self.assertNotEqual(rc, 0, "the stale stored summary must make --assert fail")
        self.assertIn("TT_SUMMARY_ASSERT_FAIL", out)
        self.assertIn("open", out)   # the mutated bucket shows in the diff
        self.assertIn("closed", out)

    # -- 3. remove / add a row fails --assert on total -------------------------------------
    def test_row_removal_fails_assert_on_total(self) -> None:
        rc, _ = self._run("--write")
        self.assertEqual(rc, 0)
        doc = self._load()
        doc["tts"] = doc["tts"][:-1]  # drop one row, keep the (now stale) summary
        self._dump(doc)
        rc, out = self._run("--assert")
        self.assertNotEqual(rc, 0)
        self.assertIn("total", out)

    def test_row_addition_fails_assert_on_total(self) -> None:
        rc, _ = self._run("--write")
        self.assertEqual(rc, 0)
        doc = self._load()
        doc["tts"] = list(doc["tts"]) + [dict(doc["tts"][0])]  # duplicate a row
        self._dump(doc)
        rc, out = self._run("--assert")
        self.assertNotEqual(rc, 0)
        self.assertIn("total", out)

    # -- unknown statuses are counted visibly, never dropped -------------------------------
    def test_out_of_vocabulary_status_is_counted_visibly(self) -> None:
        doc = self._load()
        doc["tts"] = list(doc["tts"]) + [{"id": "TT-SYNTHETIC-UNKNOWN", "status": "WAT"}]
        head = self._head()
        rec = TT.recompute(doc, head)
        self.assertEqual(rec["total"], 23)
        self.assertEqual(rec["unknown"], 1)
        self.assertEqual(rec["unmapped_statuses"], {"WAT": 1})
        # the bucket sum equals total exactly: nothing dropped, nothing double-counted
        self.assertEqual(rec["closed"] + rec["partial"] + rec["open"] + rec["open_owner_gate"]
                         + rec["temp_closed"] + rec["unknown"], rec["total"])

    # -- 4. round-trip preserves ids and statuses ------------------------------------------
    def test_round_trip_preserves_rows_ids_and_statuses(self) -> None:
        before = self._load()
        rc, _ = self._run("--write")
        self.assertEqual(rc, 0)
        after = self._load()
        self.assertEqual(len(after["tts"]), len(before["tts"]))
        self.assertEqual([r["id"] for r in after["tts"]], [r["id"] for r in before["tts"]])
        self.assertEqual([r["status"] for r in after["tts"]], [r["status"] for r in before["tts"]])
        self.assertEqual([r.get("evidence") for r in after["tts"]],
                         [r.get("evidence") for r in before["tts"]])
        # a pure JSON round-trip must also be lossless
        plain = json.loads(json.dumps(after, ensure_ascii=False))
        self.assertEqual(len(plain["tts"]), len(after["tts"]))
        self.assertEqual([r["status"] for r in plain["tts"]], [r["status"] for r in after["tts"]])

    # -- 5. the 22 rows survive and no status was closed/changed by the tool ---------------
    def test_all_rows_present_and_no_status_changed(self) -> None:
        before = self._load()
        rc, _ = self._run("--write")
        self.assertEqual(rc, 0)
        after = self._load()

        self.assertEqual(len(after["tts"]), 22, "all 22 TT rows must still be present")
        self.assertEqual(len({r["id"] for r in after["tts"]}), 22, "row ids must stay unique")
        self.assertEqual(Counter(r["status"] for r in after["tts"]), EXPECTED_STATUS_COUNTS,
                         "no row status may be renamed or re-mapped by the tool")
        self.assertEqual(Counter(r["status"] for r in before["tts"]),
                         Counter(r["status"] for r in after["tts"]))
        # the tool never invents a CLOSED: exactly the one pre-existing CLOSED row remains
        self.assertEqual(sum(1 for r in after["tts"] if r["status"] == "CLOSED"), 1)

    # -- the real register's invariants (independent of the write order) -------------------
    def test_real_register_row_histogram_is_unchanged(self) -> None:
        doc = json.loads(REGISTER.read_text(encoding="utf-8"))
        self.assertEqual(len(doc["tts"]), 22)
        self.assertEqual(Counter(r["status"] for r in doc["tts"]), EXPECTED_STATUS_COUNTS)


if __name__ == "__main__":
    unittest.main()
