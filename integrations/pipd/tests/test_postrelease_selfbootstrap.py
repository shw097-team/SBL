"""WO-S4-SELFBOOT-04: the shipped repository self-bootstraps end to end, replay-stable, typed.

This test drives the REAL compiler chain (intent -> compile-pi -> bind-pd -> compile-ecp ->
compile-tqaep -> validate) in an ISOLATED temp root, and pins the two refusals the example
advertises (missing source locator, stale RepoContext). It is the machine-checkable half of
examples/self-bootstrap; the example is the captured-transcript half.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from pipd_ls_sp import pipeline, validate  # noqa: E402
from pipd_ls_sp import repo_context as repo_probe  # noqa: E402
from pipd_ls_sp.errors import AuthorityUnknown, StaleProvider  # noqa: E402

CLAUSE_SOURCE = ROOT / "examples" / "self-bootstrap" / "input" / "source_clauses.txt"
GOAL = "以 HG-KSEOS 治理控制平面實作 PIPD-LS-SP 規格包編譯系統，完成測試驗收與公開交付。"


class TestSelfBootstrap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory(prefix="pipd_selfboot_")
        cls.ctx_dir = Path(cls._tmp.name) / "pd_context"
        cls.ctx_dir.mkdir(parents=True, exist_ok=True)     # pristine read-only context dir

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def _slice(self):
        card = pipeline.intake(GOAL, sources=[str(CLAUSE_SOURCE)],
                               constraints=["candidate-only, no release"],
                               non_goals=["no body copied"])
        pi = pipeline.compile_pi(card, "LITE")
        pd = pipeline.bind_pd(pi, {"root": str(self.ctx_dir), "writable_scope": "src/**"})
        ecp = pipeline.compile_ecp(pd, pi)
        cc = pipeline.compile_construction_contract(pd)
        tq = pipeline.compile_tqaep(pi, ecp, maker="HERMES-MAKER",
                                    checker="GLM-5.3-FLASH-AO-LANE",
                                    checker_execution_receipt="deleg_example/lane-C")
        return card, pi, pd, ecp, cc, tq

    def test_chain_runs_and_validates(self) -> None:
        card, pi, pd, ecp, cc, tq = self._slice()
        self.assertGreaterEqual(len(pipeline.atoms_of(pi)), 3)
        self.assertTrue(pd["RepoContext"]["root"])
        bundle = {"PI-PKG": pipeline.strip_sidecar(pi), "PD-PKG": pd, "ECP": ecp,
                  "TQAEP": tq, "ConstructionContract": cc}
        res = validate.validate_bundle(bundle, ROOT / "schemas")
        self.assertEqual(res["verdict"], "PASS", str(res["findings"])[:800])
        self.assertEqual(res["findings"], [])

    def test_chain_replay_is_deterministic(self) -> None:
        a = self._slice()
        b = self._slice()
        for x, y in zip(a, b):
            self.assertEqual(x["content_hash"], y["content_hash"])
            self.assertEqual(x["subject_id"], y["subject_id"])

    def test_replay_is_root_bound_not_root_independent(self) -> None:
        """The determinism the example advertises is bounded to identical rooted inputs (F03).

        Same ``RepoContext.root`` -> identical PD/ECP/bundle digests (and everything else).
        A *different* root -> PD and ECP digests may differ (PD digests the absolute root by
        design and ECP derives from PD), while PI and TQAEP stay identical. This pins the
        corrected, weaker claim: environment binding, not nondeterminism.
        """
        import hashlib
        import tempfile

        def slice_at(root):
            card = pipeline.intake(GOAL, sources=[str(CLAUSE_SOURCE)],
                                   constraints=["candidate-only, no release"],
                                   non_goals=["no body copied"])
            pi = pipeline.compile_pi(card, "LITE")
            pd = pipeline.bind_pd(pi, {"root": str(root), "writable_scope": "src/**"})
            ecp = pipeline.compile_ecp(pd, pi)
            tq = pipeline.compile_tqaep(pi, ecp, maker="HERMES-MAKER",
                                        checker="GLM-5.3-FLASH-AO-LANE",
                                        checker_execution_receipt="deleg_example/lane-C")
            # Bundle digest exactly as the example driver computes it (compute_digests):
            # sha256 over the sorted per-artefact content hashes.
            rows = {"intent_card": card["content_hash"], "pi": pi["content_hash"],
                    "pd": pd["content_hash"], "ecp": ecp["content_hash"],
                    "tqaep": tq["content_hash"]}
            bundle = hashlib.sha256(
                json.dumps(rows, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode("utf-8")).hexdigest()
            return {"PI": pi["content_hash"], "TQAEP": tq["content_hash"],
                    "PD": pd["content_hash"], "ECP": ecp["content_hash"],
                    "bundle": bundle}

        with tempfile.TemporaryDirectory(prefix="pipd_root_a_") as ra, tempfile.TemporaryDirectory(
                prefix="pipd_root_b_") as rb:
            # (a) same root, twice -> identical everywhere
            same_1 = slice_at(ra)
            same_2 = slice_at(ra)
            self.assertEqual(same_1, same_2, "same-root replay is not deterministic")

            # (b) different roots -> PI/TQAEP identical; PD/ECP (hence bundle) may differ
            other = slice_at(rb)
            self.assertEqual(same_1["PI"], other["PI"])
            self.assertEqual(same_1["TQAEP"], other["TQAEP"])
            self.assertNotEqual(same_1["PD"], other["PD"],
                                "PD digest did not bind RepoContext.root")
            self.assertNotEqual(same_1["ECP"], other["ECP"],
                                "ECP digest did not track its PD root binding")
            self.assertNotEqual(same_1["bundle"], other["bundle"],
                                "bundle digest did not track its root-bound components")

    def test_trace_closure_has_no_orphans(self) -> None:
        _, pi, pd, ecp, _, tq = self._slice()
        rep = pipeline.trace_closure({"pi": pi, "pd": pd, "ecp": ecp, "tqaep": tq})
        self.assertEqual(rep["verdict"], "PASS", rep["orphans"])

    def test_missing_source_is_refused_typed(self) -> None:
        with self.assertRaises(AuthorityUnknown) as ctx:
            pipeline.intake(GOAL, sources=[str(ROOT / "does_not_exist_xyz.txt")])
        self.assertEqual(ctx.exception.code, "AUTHORITY_UNKNOWN")
        self.assertEqual(ctx.exception.as_dict()["verdict"], "FAIL")

    def test_stale_context_is_refused_typed(self) -> None:
        _, pi, _, _, _, _ = self._slice()
        stale = repo_probe.derive_repo_context(self.ctx_dir)
        stale["currentness_epoch"] = "0" * 64
        with self.assertRaises(StaleProvider) as ctx:
            pipeline.bind_pd(pi, stale)
        self.assertEqual(ctx.exception.code, "STALE_PROVIDER")

    def test_shipped_cli_init_runs_in_isolated_root(self) -> None:
        out = subprocess.run(
            [sys.executable, "-m", "pipd_ls_sp.cli", "--root", str(self.ctx_dir.parent), "init"],
            cwd=str(ROOT), env={**os.environ, "PYTHONPATH": str(SRC)},
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(out.returncode, 0, out.stderr)
        payload = json.loads(out.stdout)
        self.assertEqual(payload["verdict"], "PASS")
        self.assertEqual(payload["contract_families"], 19)


if __name__ == "__main__":
    unittest.main(verbosity=2)
