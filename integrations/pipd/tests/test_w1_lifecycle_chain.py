"""W1 · WP-FHS-05 — the lifecycle chain's POS / NEG / EDGE contract.

Each test names the W1 first-fail it proves. The suite is deterministic and needs no network, no
host effect and no credential: it exercises the chain's own separation rules only.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline, w1_lifecycle  # noqa: E402
from pipd_ls_sp.errors import RepoContextMissing  # noqa: E402

GOAL = ("FHS W1 WP-05：以 SBL 原 PIPD 編譯器建立 Intake→SourceFreeze→Profile→PI(strict)+sidecar"
        "→真 RepoContext→PD→DEV/OPS ECP→TQAEP 的可重算鏈，strict 與 sidecar 不得混用。")
SOURCE = str(ROOT / "src" / "pipd_ls_sp" / "pipeline.py")


def run(**over) -> dict:
    kw = dict(goal=GOAL, sources=[SOURCE], repo_root=str(ROOT), writable_scope="src/**",
              maker="HERMES-EXECUTE", checker="INDEPENDENT-CHECKER-CANDIDATE",
              checker_receipt="local:unittest:w1-chain-contract")
    kw.update(over)
    return w1_lifecycle.run_chain(**kw)


class TestChainPositive(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rec = run()

    def test_all_eight_legs_are_present_in_order(self) -> None:
        legs = [s["leg"] for s in self.rec["stages"]]
        self.assertEqual(legs, ["source_freeze", "intake", "profile", "compile_pi_strict",
                                "compile_pi_sidecar", "repo_context", "bind_pd", "ecp_dev",
                                "ecp_ops", "tqaep"])

    def test_strict_bundle_validates(self) -> None:
        self.assertEqual(self.rec["validation"]["verdict"], "PASS", self.rec["validation"])

    def test_sidecar_is_not_raw_and_carries_its_own_digest(self) -> None:
        side = self.rec["artifacts"]["pi_sidecar"]
        self.assertFalse(side["is_raw"])
        self.assertEqual(side["evidence_class"], "SIDECAR_NOT_RAW")
        self.assertEqual(side["subject_id"], self.rec["artifacts"]["pi_strict"]["subject_id"])
        self.assertNotIn("content_hash", side)
        self.assertRegex(side["strict_sha256"], r"^[0-9a-f]{64}$")

    def test_strict_payload_carries_no_sidecar_key(self) -> None:
        strict = self.rec["artifacts"]["pi_strict"]
        self.assertFalse([k for k in strict if k.startswith("_")])
        self.assertIn("stable_semantic_contract", strict)

    def test_repo_context_is_the_local_probe_not_a_claim(self) -> None:
        check = self.rec["repo_context_check"]
        self.assertEqual(check["state"], "LOCAL_PROBE_MATCHES")
        self.assertEqual(check["probe"], "git")
        self.assertRegex(check["head"], r"^[0-9a-f]{40}$")

    def test_dev_and_ops_paths_are_separate(self) -> None:
        sep = self.rec["effect_paths"]
        self.assertEqual(sep["dev_class"], "DEV_REPO_WRITE")
        self.assertEqual(sep["ops_class"], "HOST_OP")
        self.assertNotEqual(sep["dev_scope"], sep["ops_scope"])
        self.assertFalse(sep["shared_permission_basis"])
        self.assertEqual(self.rec["artifacts"]["ecp_ops"]["permission"]["grant_state"], "NOT_GRANTED")

    def test_on_host_legs_are_not_claimed(self) -> None:
        for leg in ("installed", "loaded", "invoked", "consumer_ack"):
            self.assertEqual(self.rec["native"][leg], "NOT_RUN")
        self.assertEqual(self.rec["claim_ceiling"], "AUTHOR_DESIGN_ONLY")

    def test_chain_is_replay_deterministic(self) -> None:
        again = run()
        self.assertEqual(self.rec["artifacts"]["pi_strict"]["subject_id"],
                         again["artifacts"]["pi_strict"]["subject_id"])
        self.assertEqual(self.rec["artifacts"]["ecp_dev"]["content_hash"],
                         again["artifacts"]["ecp_dev"]["content_hash"])
        self.assertEqual(self.rec["artifacts"]["tqaep"]["content_hash"],
                         again["artifacts"]["tqaep"]["content_hash"])
        self.assertEqual(self.rec["source_freeze_sha256"], again["source_freeze_sha256"])


class TestChainNegative(unittest.TestCase):
    def test_sidecar_key_in_strict_payload_refuses(self) -> None:
        with self.assertRaises(w1_lifecycle.SidecarContamination) as ctx:
            w1_lifecycle.assert_strict_payload({"_profile_meta": {"profile": "LITE"}, "x": 1})
        self.assertEqual(ctx.exception.code, "PIPD_FORMAL_PROMOTION_HOLD")

    def test_pi_without_sidecar_refuses(self) -> None:
        card = pipeline.intake(GOAL, sources=[SOURCE])
        pi = pipeline.compile_pi(card, "LITE")
        stripped = {k: v for k, v in pi.items() if not k.startswith("_")}
        with self.assertRaises(w1_lifecycle.SidecarContamination):
            w1_lifecycle.split_pi(stripped)

    def test_pd_without_repo_context_refuses(self) -> None:
        card = pipeline.intake(GOAL, sources=[SOURCE])
        pi = pipeline.compile_pi(card, "LITE")
        with self.assertRaises(RepoContextMissing) as ctx:
            pipeline.bind_pd(pi, None)
        self.assertEqual(ctx.exception.code, "REPO_CONTEXT_MISSING")

    def test_foreign_head_claim_refuses(self) -> None:
        """A remote HEAD presented as the local one is refused by the ORIGINAL PD writer.

        The original writer refuses earlier (STALE_PROVIDER) than this module's own check, which is
        the desired layering: the chain gate is the second line, not the only one.
        """
        from pipd_ls_sp.errors import StaleProvider
        card = pipeline.intake(GOAL, sources=[SOURCE])
        pi = pipeline.compile_pi(card, "LITE")
        ctx = w1_lifecycle.repo_probe.derive_repo_context(str(ROOT), writable_scope="src/**")
        ctx["head"] = "0" * 40
        with self.assertRaises(StaleProvider) as raised:
            pipeline.bind_pd(pi, ctx)
        self.assertEqual(raised.exception.code, "STALE_PROVIDER")

    def test_chain_gate_refuses_a_pd_that_did_not_come_from_the_probe(self) -> None:
        card = pipeline.intake(GOAL, sources=[SOURCE])
        pi = pipeline.compile_pi(card, "LITE")
        pd = pipeline.bind_pd(pi, w1_lifecycle.repo_probe.derive_repo_context(
            str(ROOT), writable_scope="src/**"))
        pd["RepoContext"] = dict(pd["RepoContext"], head="1" * 40)
        with self.assertRaises(w1_lifecycle.RepoContextForeign) as raised:
            w1_lifecycle.assert_repo_context_local(pd, str(ROOT))
        self.assertEqual(raised.exception.code, "PD_REPOCONTEXT_UNBOUND")

    def test_collapsed_dev_ops_scope_refuses(self) -> None:
        """A PD whose bound scope equals the OPS basis collapses the two paths and is refused."""
        card = pipeline.intake(GOAL, sources=[SOURCE])
        pi = pipeline.compile_pi(card, "LITE")
        pd = pipeline.bind_pd(pi, w1_lifecycle.repo_probe.derive_repo_context(
            str(ROOT), writable_scope="src/**"))
        pd["late_bound_construction_binding"]["writable_scope"] = "HOST_OP:UNBOUND"
        pipeline._seal(pd, "PD")
        with self.assertRaises(w1_lifecycle.DevOpsPathMixed) as raised:
            w1_lifecycle.dev_ops_ecp(pipeline.strip_sidecar(pi), pd)
        self.assertEqual(raised.exception.code, "ECP_DEV_OPS_MIXED")

    def test_maker_cannot_be_its_own_checker(self) -> None:
        with self.assertRaises(Exception) as raised:
            run(maker="SAME", checker="SAME")
        self.assertEqual(getattr(raised.exception, "code", ""), "TQ_SOD")


class TestChainEdge(unittest.TestCase):
    def test_empty_source_set_refuses(self) -> None:
        with self.assertRaises(w1_lifecycle.SourceFreezeFail) as ctx:
            w1_lifecycle.source_freeze([])
        self.assertEqual(ctx.exception.code, "SOURCE_FREEZE_FAIL")

    def test_missing_locator_refuses(self) -> None:
        with self.assertRaises(w1_lifecycle.SourceFreezeFail):
            w1_lifecycle.source_freeze([str(ROOT / "no-such-source.md")])

    def test_duplicate_source_content_refuses(self) -> None:
        with self.assertRaises(w1_lifecycle.SourceFreezeFail) as ctx:
            w1_lifecycle.source_freeze([SOURCE, SOURCE])
        self.assertIn("duplicate", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
