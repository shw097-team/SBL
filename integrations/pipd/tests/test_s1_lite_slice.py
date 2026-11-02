"""S1: one real LITE intent -> PI -> PD -> ECP/TQAEP vertical slice, end to end."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline, validate  # noqa: E402

GOAL = "以 HG-KSEOS 治理控制平面實作 PIPD-LS-SP 規格包編譯系統，完成測試驗收與公開交付。"


class TestLiteSlice(unittest.TestCase):
    def _slice(self):
        card = pipeline.intake(GOAL, sources=[str(ROOT)], constraints=["c1"], non_goals=["n1"])
        pi = pipeline.compile_pi(card, "LITE")
        pd = pipeline.bind_pd(pi, {"root": str(ROOT), "head": "HEAD", "tracked_files": 3,
                                   "writable_scope": "src/**"})
        ecp = pipeline.compile_ecp(pd, pi)
        cc = pipeline.compile_construction_contract(pd)
        tq = pipeline.compile_tqaep(pi, ecp, maker="HERMES-MAKER", checker="GLM-5.3-FLASH-AO-LANE",
                                   checker_execution_receipt="deleg_5a26d6d5/lane-C")
        return card, pi, pd, ecp, cc, tq

    def test_slice_runs_and_binds(self) -> None:
        card, pi, pd, ecp, cc, tq = self._slice()
        self.assertGreaterEqual(len(pipeline.atoms_of(pi)), 3)
        self.assertTrue(pd["RepoContext"]["root"])
        self.assertTrue(cc["writable_scope"])
        self.assertTrue(tq["tests"])
        self.assertTrue(tq["acceptance"][0]["checker_execution_receipt"])

    def test_slice_is_replay_deterministic(self) -> None:
        a = self._slice()
        b = self._slice()
        for x, y in zip(a, b):
            self.assertEqual(x["content_hash"], y["content_hash"])
            self.assertEqual(x["subject_id"], y["subject_id"])

    def test_trace_closure_has_no_orphans(self) -> None:
        card, pi, pd, ecp, cc, tq = self._slice()
        rep = pipeline.trace_closure({"pi": pi, "pd": pd, "ecp": ecp, "tqaep": tq})
        self.assertEqual(rep["verdict"], "PASS", rep["orphans"])

    def test_slice_records_satisfy_their_schemas(self) -> None:
        card, pi, pd, ecp, cc, tq = self._slice()
        bundle = {"PI-PKG": pipeline.strip_sidecar(pi), "PD-PKG": pd, "ECP": ecp,
                  "TQAEP": tq, "ConstructionContract": cc}
        res = validate.validate_bundle(bundle, ROOT / "schemas")
        self.assertEqual(res["findings"], [], str(res["findings"])[:800])

    def test_pd_without_repo_context_fails_closed(self) -> None:
        card = pipeline.intake(GOAL, sources=[str(ROOT)])
        pi = pipeline.compile_pi(card, "LITE")
        with self.assertRaises(pipeline.RepoContextMissing):
            pipeline.bind_pd(pi, None)

    def test_maker_cannot_be_checker(self) -> None:
        card = pipeline.intake(GOAL, sources=[str(ROOT)])
        pi = pipeline.compile_pi(card, "LITE")
        pd = pipeline.bind_pd(pi, {"root": str(ROOT), "writable_scope": "src/**"})
        ecp = pipeline.compile_ecp(pd, pi)
        with self.assertRaises(pipeline.TqSodFail):
            pipeline.compile_tqaep(pi, ecp, maker="SAME", checker="SAME")

    def test_claim_ceiling_blocks_escalation(self) -> None:
        ccl = pipeline.claim_ceiling(["LOCAL_QUALIFIED"])
        self.assertIn("INDEPENDENT_PASS", ccl["forbidden_escalation"])
        self.assertNotIn("INDEPENDENT_PASS", ccl["allowed_claims"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
