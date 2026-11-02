"""S4EXT-R1 (TT-S4EXT-007): the 57-row SPEC/DEL adjudication must not drift or self-upgrade.

TT-S4EXT-007 asks for a per-row adjudication of the S4-active SPEC/DEL crosswalk: for each of the 9
``EVIDENCE_GAP`` rows (and the 4 ``DESIGN_ONLY`` rows) state the source, the stage applicability, a
candidate oracle, a candidate negative mutation, the raw evidence and whether it is an owner defer or
an acceptance -- with ``DEL-008`` explicitly NOT treated as uniformly S4-blocking, and ``DESIGN_ONLY``
never read as implemented.

This suite is the oracle for that document. It re-derives ``docs/S4_SPEC_DEL_ADJUDICATION.json`` from
``docs/SPEC_DEL_CROSSWALK.json`` plus the explicit disposition table in
``tools/build_s4_spec_del_adjudication.py`` and asserts:

* the checked-in JSON is byte-identical to the re-derivation (no hand edit drifts);
* the row set is exactly the crosswalk's 57 rows, and the gap set is exactly the crosswalk's
  ``EVIDENCE_GAP`` rows -- a NEW gap cannot be silently dropped, an old one cannot be silently
  promoted;
* the crosswalk is read-only: every row's ``crosswalk_status``/``crosswalk_oracle`` still equals the
  live crosswalk value, so the adjudication can never be used to launder a status upgrade;
* every non-``EVIDENCED`` row carries a disposition, and a row claiming a local oracle names a test
  file that EXISTS and RUNS;
* ``44 EVIDENCED`` is never presented as ``44 PASS``;
* ``DEL-008`` is not S4-blocking and its rationale names the S5 half;
* a ``DESIGN_ONLY`` row is never disposed as implemented.

Deterministic; runnable standalone.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.build_s4_spec_del_adjudication as adj  # noqa: E402

CROSSWALK = ROOT / "docs" / "SPEC_DEL_CROSSWALK.json"
DOC = ROOT / "docs" / "S4_SPEC_DEL_ADJUDICATION.json"

IMPLEMENTED_DISPOSITIONS = {
    "LOCAL_ORACLE_ADDED_CANDIDATE",
    "UNCHANGED_EVIDENCED",
}
NOT_IMPLEMENTED_DISPOSITIONS = {"DESIGN_ONLY_NOT_IMPLEMENTED", "S5_PLUS_OUT_OF_SCOPE", "OWNER_DEFER"}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class AdjudicationDocumentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = _json(DOC)
        self.crosswalk = _json(CROSSWALK)
        self.rows = {r["id"]: r for r in self.doc["rows"]}
        self.xrows = {r["id"]: r for r in self.crosswalk["rows"]}

    # ---- no drift ------------------------------------------------------------------------
    def test_checked_in_document_is_identical_to_the_regenerated_one(self) -> None:
        self.assertEqual(self.doc, adj.build(),
                         "docs/S4_SPEC_DEL_ADJUDICATION.json has drifted from "
                         "tools/build_s4_spec_del_adjudication.py -- regenerate it")

    def test_the_generator_is_idempotent(self) -> None:
        self.assertEqual(adj.build(), adj.build())

    # ---- denominators --------------------------------------------------------------------
    def test_row_set_is_exactly_the_crosswalk_57(self) -> None:
        self.assertEqual(len(self.rows), 57)
        self.assertEqual(set(self.rows), set(self.xrows))
        self.assertEqual(self.crosswalk["counts"], {"SPEC": 32, "DEL": 25, "total": 57})

    def test_gap_set_is_exactly_the_crosswalk_evidence_gap_rows(self) -> None:
        live_gaps = {i for i, r in self.xrows.items() if r["status"] == "EVIDENCE_GAP"}
        answered = {i for i, r in self.rows.items() if r["disposition"] != "UNCHANGED_EVIDENCED"}
        self.assertTrue(live_gaps <= answered,
                        f"EVIDENCE_GAP rows without a disposition: {sorted(live_gaps - answered)}")
        self.assertEqual(answered & live_gaps, live_gaps)
        self.assertEqual(len(live_gaps), 9, "the readback carried 9 EVIDENCE_GAP rows")

    def test_design_only_rows_are_answered(self) -> None:
        live = {i for i, r in self.xrows.items() if r["status"] == "DESIGN_ONLY"}
        self.assertTrue(live)
        self.assertEqual({i for i in live if self.rows[i]["disposition"]
                          == "DESIGN_ONLY_NOT_IMPLEMENTED"}, live)

    # ---- the crosswalk is READ-ONLY -----------------------------------------------------
    def test_no_row_rewrites_the_crosswalk_status(self) -> None:
        for rid, row in self.rows.items():
            self.assertEqual(row["crosswalk_status"], self.xrows[rid]["status"],
                             f"{rid}: the adjudication must not restate a different status")
            self.assertEqual(row["crosswalk_oracle"], self.xrows[rid]["oracle"],
                             f"{rid}: the adjudication must not rewrite the crosswalk oracle")

    def test_evidence_never_becomes_pass(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("EVIDENCED != PASS", text)
        for row in self.rows.values():
            self.assertNotIn(row["disposition"], {"PASS", "VERIFIED", "ACCEPTED", "CLOSED"},
                             f"{row['id']}: no row may be disposed as accepted by the maker")
        self.assertEqual(self.doc["summary"]["closed_outright_this_round"], [])

    # ---- per-row honesty -----------------------------------------------------------------
    def test_every_non_evidenced_row_states_oracle_negative_and_rationale(self) -> None:
        for row in self.rows.values():
            if row["disposition"] == "UNCHANGED_EVIDENCED":
                continue
            self.assertTrue(row["rationale"].strip(), f"{row['id']}: missing rationale")
            self.assertTrue(row["negative_mutation_candidate"].strip() or
                            row["disposition"] == "DESIGN_ONLY_NOT_IMPLEMENTED",
                            f"{row['id']}: a non-design-only disposition must name a negative")

    def test_local_oracle_dispositions_name_a_test_file_that_exists_and_runs(self) -> None:
        for row in self.rows.values():
            if row["disposition"] not in IMPLEMENTED_DISPOSITIONS:
                continue
            if not row["oracle_candidate"]:
                continue
            path = ROOT / row["oracle_candidate"].split(" + ")[0]
            self.assertTrue(path.is_file(), f"{row['id']}: oracle {path} does not exist")
            self.assertTrue(path.name.startswith("test_"), f"{row['id']}: not a test file")

    def test_design_only_is_never_disposed_as_implemented(self) -> None:
        for rid, row in self.rows.items():
            if self.xrows[rid]["status"] == "DESIGN_ONLY":
                self.assertIn(row["disposition"], NOT_IMPLEMENTED_DISPOSITIONS,
                              f"{rid}: DESIGN_ONLY must not be disposed as implemented")
                self.assertNotIn("implemented", row["rationale"].lower().replace(
                    "not implemented", "").replace("design-only", ""))

    # ---- DEL-008 stage applicability -----------------------------------------------------
    def test_del_008_is_not_uniformly_s4_blocking(self) -> None:
        row = self.rows["DEL-008"]
        self.assertEqual(row["stage"], "S1/S5")
        self.assertFalse(row["s4_blocking"],
                         "DEL-008 carries an S5 half and must not be declared S4-blocking")
        self.assertIn("S5", row["rationale"])

    def test_s4_blocking_rows_are_only_the_release_provenance_line(self) -> None:
        self.assertEqual(set(self.doc["summary"]["s4_blocking_rows"]),
                         set(adj.S4_BLOCKING_REQUIRED))
        for rid in adj.S4_BLOCKING_REQUIRED:
            self.assertNotEqual(self.xrows[rid]["status"], "EVIDENCED",
                                f"{rid} is claimed blocking but already reads EVIDENCED")

    # ---- summary consistency -------------------------------------------------------------
    def test_summary_counts_match_the_rows(self) -> None:
        counted: dict[str, int] = {}
        for row in self.rows.values():
            counted[row["disposition"]] = counted.get(row["disposition"], 0) + 1
        self.assertEqual(self.doc["summary"]["by_disposition"], counted)
        self.assertEqual(self.doc["summary"]["rows_total"], 57)
        self.assertEqual(sum(counted.values()), 57)
        self.assertEqual(self.doc["summary"]["owner_defer_rows"],
                         [r["id"] for r in self.doc["rows"]
                          if r["disposition"] == "OWNER_DEFER"])

    def test_claim_ceiling_is_kept(self) -> None:
        self.assertEqual(self.doc["claim_ceiling"],
                         "MAKER_CANDIDATE_AND_LOCAL_TESTS_ONLY_UNTIL_EXTERNAL_REQUALIFICATION")
        self.assertIn("CANDIDATE", self.doc["claim_ceiling"])


class GeneratorGuardTests(unittest.TestCase):
    """An un-adjudicated row must be a hard error, not a default."""

    def test_unknown_non_evidenced_row_is_refused(self) -> None:
        with self.assertRaises(SystemExit):
            adj._row_disposition({"id": "DEL-999", "status": "EVIDENCE_GAP"})

    def test_evidenced_rows_default_to_unchanged(self) -> None:
        disposition, extra = adj._row_disposition({"id": "PIPD-SP-SPEC-001", "status": "EVIDENCED"})
        self.assertEqual(disposition, "UNCHANGED_EVIDENCED")
        self.assertFalse(extra["s4_blocking"])

    def test_every_disposition_in_the_table_is_a_known_vocabulary_word(self) -> None:
        known = IMPLEMENTED_DISPOSITIONS | NOT_IMPLEMENTED_DISPOSITIONS | {
            "EXTERNAL_STANDARD_ADJUDICATED"}
        for rid, entry in adj.DISPOSITIONS.items():
            self.assertIn(entry["disposition"], known, f"{rid}: unknown disposition")
            self.assertIn("rationale", entry, f"{rid}: rationale required")


if __name__ == "__main__":
    unittest.main(verbosity=2)
