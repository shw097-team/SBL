"""M2b: a partial bundle may PASS, but the word FULL must mean four objects.

RUN-20261102-GJ02-01 found `pipd validate --bundle` returning
``{"checked": 3, "closure": "FULL"}`` with the TQAEP removed. A scoped validate is
legal, so the default keeps PASS for a partial bundle - but the result now names
what is missing, never says FULL without PI-PKG/PD-PKG/ECP/TQAEP, and
``--require-four`` turns an absent object into a typed FAIL.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline, validate  # noqa: E402

GOAL = "以 HG-KSEOS 治理控制平面實作 PIPD-LS-SP 規格包編譯系統，完成測試驗收與公開交付。"


def _slice():
    card = pipeline.intake(GOAL, sources=[str(ROOT)], constraints=["c1"], non_goals=["n1"])
    pi = pipeline.compile_pi(card, "LITE")
    pd = pipeline.bind_pd(pi, {"root": str(ROOT), "head": "HEAD", "tracked_files": 3,
                               "writable_scope": "src/**"})
    ecp = pipeline.compile_ecp(pd, pi)
    tq = pipeline.compile_tqaep(pi, ecp, maker="HERMES-MAKER", checker="GLM-5.3-FLASH-AO-LANE",
                                checker_execution_receipt="deleg_5a26d6d5/lane-C")
    return {"PI-PKG": pipeline.strip_sidecar(pi), "PD-PKG": pd, "ECP": ecp, "TQAEP": tq}


class FourObjectDenominator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = _slice()
        cls.partial = {k: v for k, v in cls.full.items() if k != "TQAEP"}

    def test_full_bundle_is_complete_and_full(self):
        out = validate.validate_bundle(self.full)
        self.assertEqual(out["verdict"], "PASS", out["findings"])
        self.assertEqual(out["closure"], "FULL")
        self.assertEqual(out["checked"], 4)
        self.assertEqual(out["missing"], [])
        self.assertTrue(out["complete"])
        self.assertEqual(out["scope"], "FOUR_OBJECT")

    def test_partial_bundle_never_claims_full_closure(self):
        out = validate.validate_bundle(self.partial)
        self.assertEqual(out["verdict"], "PASS", "a scoped partial validate stays legal")
        # `closure` still describes the graph among present records; the denominator is now named
        # separately so a reader cannot mistake a scoped result for a four-object one.
        self.assertEqual(out["scope"], "PARTIAL_BUNDLE")
        self.assertEqual(out["checked"], 3)
        self.assertEqual(out["missing"], ["TQAEP"])
        self.assertFalse(out["complete"])

    def test_require_four_refuses_the_missing_tqaep(self):
        out = validate.validate_bundle(self.partial, require_four=True)
        self.assertEqual(out["verdict"], "FAIL")
        kinds = [f["kind"] for f in out["findings"]]
        self.assertIn("DENOMINATOR", kinds)
        detail = next(f["detail"] for f in out["findings"] if f["kind"] == "DENOMINATOR")
        self.assertIn("TQAEP", detail)

    def test_cli_exposes_require_four(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bundle.json"
            path.write_text(json.dumps(self.partial), encoding="utf-8")
            ok = subprocess.run([sys.executable, "-m", "pipd_ls_sp.cli", "--root", td,
                                 "validate", "--bundle", str(path)],
                                capture_output=True, text=True, cwd=str(ROOT))
            strict = subprocess.run([sys.executable, "-m", "pipd_ls_sp.cli", "--root", td,
                                     "validate", "--bundle", str(path), "--require-four"],
                                    capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertEqual(json.loads(ok.stdout)["scope"], "PARTIAL_BUNDLE")
        self.assertFalse(json.loads(ok.stdout)["complete"])
        self.assertNotEqual(strict.returncode, 0, "the strict form must fail closed")
        self.assertIn("DENOMINATOR", strict.stdout + strict.stderr)


if __name__ == "__main__":
    unittest.main()
