"""Guard tools/build_evidence_md.py (R-AUD-012 / FW-12): a hard gate FAIL must refuse PASS.

Why this test exists: the evidence generator used to print `failures 0, errors 0` from a hardcoded
string and would have printed an acceptance document no matter what the gates said. Two rules are
now pinned:

1. when any hard gate row is FAIL the generator REFUSES — it writes no acceptance document and
   returns a typed HARD_GATE_FAIL envelope naming the failing rows (no percentage can hide it);
2. the test counts in the document come from a real run and name the failing tests.
"""
from __future__ import annotations
import importlib.util
import sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


def _load_tool():
    spec = importlib.util.spec_from_file_location(
        "build_evidence_md_tool", ROOT / "tools" / "build_evidence_md.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BEM = _load_tool()


def _bundle(suite, *, kready_verdict="PASS", smoke_nonzero=0, manifest=True):
    return {
        "head": "0" * 40,
        "nfiles_nbytes": (10, 100),
        "pdr": {}, "led": {"active": []}, "pub": {}, "ao": {},
        "smoke": {"commands_run": 13, "expected": 13, "nonzero_exit": smoke_nonzero,
                  "verdicts": {"init": "PASS"}},
        "s1": {"trace_verdict": "PASS", "artifact_validation": "PASS",
               "atom_count": 8, "tqaep_tests": 3},
        "hsec": {}, "ttr": {"count": 0, "tts": [], "status_summary": {}},
        "knowledge_ready": {"verdict": kready_verdict,
                            "gate_predicate": {"clean_coverage": kready_verdict == "PASS",
                                               "unique_input_paths": 160}},
        "admiss": {}, "board": None,
        "manifest_sha": "a" * 64 if manifest else "NOT_FROZEN",
        "src_man": ROOT / "definitely-missing.json",
        "contract": ROOT / "definitely-missing2.json",
        "generated_at": "2026-10-09T00:00:00+00:00",
        "cli_smoke": {"commands_run": 13, "expected": 13, "nonzero_exit": smoke_nonzero,
                      "verdicts": {"init": "PASS"}},
        "suite": suite,
    }


GOOD_SUITE = {"ran": True, "tests": 47, "failures": 0, "errors": 0, "skipped": 0,
              "failed_ids": [], "raw_tail": ["Ran 47 tests in 1.0s", "", "OK"]}
BAD_SUITE = {"ran": True, "tests": 47, "failures": 2, "errors": 1, "skipped": 0,
             "failed_ids": ["tests.test_alpha.TestAlpha.test_one",
                            "tests.test_s0_contracts.TestS0Contracts.test_two",
                            "tests.test_beta.TestBeta.test_three"],
             "raw_tail": ["Ran 47 tests in 1.0s", "", "FAILED (failures=2, errors=1)"]}


class EvidenceMdHardGateRefusal(unittest.TestCase):
    def test_refuses_pass_when_a_hard_gate_row_is_fail(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "md" / "EVIDENCE.md"
            rc = BEM.main([], out_path=out,
                          collect_fn=lambda: _bundle(BAD_SUITE))
            self.assertEqual(rc, 2, "a hard gate FAIL must exit 2")
            self.assertFalse(out.exists(),
                             "no acceptance document may be written when a hard gate row is FAIL")
        # the refusal is typed and names the failing rows
        rows = BEM.evaluate_hard_gates(_bundle(BAD_SUITE))
        fails = BEM.hard_gate_failures(rows)
        self.assertTrue(fails)
        env = BEM.refusal_envelope(rows)
        self.assertEqual(env["error"], "HARD_GATE_FAIL")
        self.assertEqual(env["verdict"], "FAIL")
        self.assertIn("G-TESTS-UNIT-SUITE", env["failing_rows"])
        self.assertIn("refuses to print PASS", env["refusal"])
        # a knowledge gate in PARTIAL must never read as PASS either
        rows2 = BEM.evaluate_hard_gates(_bundle(GOOD_SUITE, kready_verdict="PARTIAL"))
        by_id = {r["id"]: r for r in rows2}
        self.assertEqual(by_id["G-KNOWLEDGE-READY"]["state"], "PARTIAL")

    def test_writes_only_when_every_hard_gate_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "EVIDENCE.md"
            rc = BEM.main([], out_path=out, collect_fn=lambda: _bundle(GOOD_SUITE))
            self.assertEqual(rc, 0)
            self.assertTrue(out.is_file())
            text = out.read_text(encoding="utf-8")
            self.assertIn("all hard gate rows PASS", text)
            self.assertIn("Ran 47 tests, failures 0, errors 0", text,
                          "counts must come from the real run")
            # --check never writes
            out2 = Path(td) / "NEVER.md"
            rc2 = BEM.main(["--check"], out_path=out2, collect_fn=lambda: _bundle(GOOD_SUITE))
            self.assertEqual(rc2, 0)
            self.assertFalse(out2.exists())

    def test_test_counts_are_real_and_failures_are_named(self) -> None:
        rows = BEM.evaluate_hard_gates(_bundle(BAD_SUITE))
        by_id = {r["id"]: r for r in rows}
        self.assertEqual(by_id["G-TESTS-UNIT-SUITE"]["state"], "FAIL")
        self.assertIn("failures 2, errors 1", by_id["G-TESTS-UNIT-SUITE"]["evidence"])
        self.assertIn("tests.test_alpha.TestAlpha.test_one", by_id["G-TESTS-UNIT-SUITE"]["evidence"])
        # S0 attribution: a failing S0 test fails the S0 gate row too
        self.assertEqual(by_id["G-S0-CONTRACTS-19"]["state"], "FAIL")
        md = BEM.render(_bundle(BAD_SUITE), rows)
        self.assertIn("failures 2, errors 1", md, "the document must show the real counts")
        self.assertIn("failing tests (named, not averaged away):", md)
        self.assertIn("FAIL — ", md, "a hard FAIL must be visible as FAIL in the document")
        self.assertNotIn("failures 0, errors 0", md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
