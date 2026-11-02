"""Negative / security / rollback tests for the S0-S1 surface."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline, validate, workspace  # noqa: E402
from pipd_ls_sp.errors import ExportSecretFound, RepairScopeFail, SelfAcceptForbidden  # noqa: E402


class TestNegative(unittest.TestCase):
    def test_claim_ceiling_rejects_conflicting_claims(self) -> None:
        rec = {"subject_id": "SYNTH-0000000000000000", "version": "1", "content_hash": "a"*64, "schema_version": "v@1",
               "allowed_claims": ["RELEASED"], "forbidden_escalation": ["RELEASED"],
               "close_conditions": []}
        self.assertTrue(validate.semantic_invariants("ClaimCeiling", rec))

    def test_workorder_candidate_must_be_candidate_only(self) -> None:
        rec = {"subject_id": "SYNTH-0000000000000000", "version": "1", "content_hash": "a"*64, "schema_version": "v@1",
               "candidate_only": False}
        self.assertTrue(validate.semantic_invariants("WorkOrderCandidate", rec))
        ok = {"subject_id": "SYNTH-0000000000000000", "version": "1", "content_hash": "a"*64, "schema_version": "v@1",
              "candidate_only": True}
        self.assertEqual(validate.semantic_invariants("WorkOrderCandidate", ok), [])

    def test_execution_binding_ack_requires_receiver_binding(self) -> None:
        rec = {"subject_id": "SYNTH-0000000000000000", "version": "1", "content_hash": "a"*64, "schema_version": "v@1",
               "state": "ACKED"}
        self.assertTrue(validate.semantic_invariants("ExecutionBindingRef", rec))

    def test_genie_projection_ref_must_cover_targets(self) -> None:
        rec = {"subject_id": "SYNTH-0000000000000000", "version": "1", "content_hash": "a"*64, "schema_version": "v@1",
               "target_refs": ["ProductGraph"]}
        self.assertTrue(validate.semantic_invariants("GENIEProjectionRef", rec))

    def test_intake_rejects_unknown_source(self) -> None:
        with self.assertRaises(pipeline.AuthorityUnknown):
            pipeline.intake("實作系統", sources=["C:/definitely/not/here"])

    def test_secret_scan_blocks_export(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "leak.py").write_text('TOKEN = "ghp_' + "A" * 30 + '"', encoding="utf-8", newline="")
            self.assertEqual(workspace.secret_scan(d)["verdict"], "FAIL")
            with self.assertRaises(ExportSecretFound):
                workspace.export_manifest(d, include=["leak.py"])

    def test_repair_requires_scope_and_no_self_accept(self) -> None:
        with self.assertRaises(RepairScopeFail):
            workspace.repair_candidate("S", scope=[], maker="M")
        with self.assertRaises(SelfAcceptForbidden):
            workspace.repair_candidate("S", scope=["src"], maker="M", self_accept=True)


class TestRollback(unittest.TestCase):
    def test_rollback_pointer_is_a_real_git_commit(self) -> None:
        import subprocess
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True)
        if head.returncode != 0:
            # Lane A found this test failing in a fresh copy that excludes .git. A missing git
            # checkout is an environment condition, not a product defect: skip, never pass silently.
            self.skipTest("no usable git checkout here (fresh copy excludes .git): "
                          f"git exited {head.returncode}")
        baseline = subprocess.run(["git", "-C", str(ROOT), "log", "--format=%H", "--reverse"],
                                  capture_output=True, text=True).stdout.split()
        self.assertTrue(baseline, "a baseline commit must exist for rollback")
        dirty_check = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                                     capture_output=True, text=True)
        self.assertEqual(dirty_check.returncode, 0)

    def test_repair_subject_must_also_be_inside_the_authorised_root(self) -> None:
        """A real defect found by the S2 golden pilot GP-03 negative set.

        `repair_candidate` validated the SCOPE but never the SUBJECT, so a caller could declare a
        benign scope such as `src/**` and point the subject at any path on the host. A bounded repair
        is only bounded if BOTH resolve inside the authorised root.
        """
        from pipd_ls_sp.errors import RepairScopeFail
        for bad_subject in ("C:/Windows/system32/x.dll", "/etc/passwd", "../../escape.py"):
            with self.subTest(subject=bad_subject):
                with self.assertRaises(RepairScopeFail):
                    workspace.repair_candidate(bad_subject, scope=["src/**"], maker="M",
                                               authorized_root=str(ROOT))
        # a subject genuinely inside the root still succeeds
        ok = workspace.repair_candidate("src/pipd_ls_sp/util.py", scope=["src/**"], maker="M",
                                        authorized_root=str(ROOT))
        self.assertEqual(ok["state"], "CANDIDATE")

    def test_semantic_diff_flags_schema_change(self) -> None:
        from pipd_ls_sp.errors import DiffIncompatible
        with self.assertRaises(DiffIncompatible):
            workspace.semantic_diff({"schema_version": "PI-PKG@1"}, {"schema_version": "PI-PKG@2"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
