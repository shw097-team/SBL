"""U04 G3: the TPM -> PIPD adapter, exercised against the real compiler.

The module is skipped when ``pipd_ls_sp`` is not installed. That is deliberate: the default SBL
job installs only ``sbl-v01``, and a test that silently passes without the compiler would prove
nothing. The ``pipd-compat`` CI job installs ``integrations/pipd`` and runs this file for real.

What is asserted is the ceiling as much as the happy path: the compiled TQAEP is a design-time
candidate, ``independent_acceptance`` is ``NOT_GRANTED``, and every refusal below is a typed
``SBLError`` rather than an exception string.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

pytest.importorskip("pipd_ls_sp")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sbl_core.errors import SBLError  # noqa: E402
from sbl_sp import pipd_adapter  # noqa: E402


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _repo(tmp: Path) -> Path:
    root = tmp / "repo"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "spec.md").write_text(
        "# Goal\n\nA bounded goal statement the compiler can bind.\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@example.invalid")
    _git(root, "config", "user.name", "test")
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "spec")
    return root


HANDOFF = {
    "goal": "Compile a bounded PI from the TPM hand-off",
    "sources": ["docs/spec.md"],
    "non_goals": ["no product code"],
    "acceptance": [{"positive": "PI binds", "negative": "stale head refused"}],
}


class TpmToPipdFlow(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = _repo(Path(self._tmp.name))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _compile(self, **kw):
        kw.setdefault("checker", "external-checker")
        kw.setdefault("checker_execution_receipt", "receipt-2026-11-03-001")
        return pipd_adapter.compile_handoff(HANDOFF, self.root, **kw)

    # ---------------------------------------------------------------- POS
    def test_narrow_flow_compiles_the_five_artefacts(self) -> None:
        result = self._compile()
        arts = result["artifacts"]
        self.assertEqual(set(arts), {"PI-PKG", "PD-PKG", "ConstructionContract", "ECP", "TQAEP"})
        self.assertEqual(result["validation"]["verdict"], "PASS")
        self.assertNotEqual(result["validation"]["closure"], "SCHEMA_ONLY")
        self.assertEqual(arts["PD-PKG"]["RepoContext"]["readiness"], "PREDEV_READY")
        self.assertEqual(arts["PD-PKG"]["currentness"]["state"], "FRESH")

    def test_design_time_ceiling_is_not_upgraded(self) -> None:
        result = self._compile()
        acceptance = result["artifacts"]["TQAEP"]["acceptance"][0]
        self.assertEqual(acceptance["independent_acceptance"], "NOT_GRANTED")
        self.assertEqual(acceptance["design_time_status"], "DISTINCT_CHECKER_IDENTITY_RECORDED")
        self.assertEqual(result["claim_ceiling"]["level"], "PROMPT_COMPILE_PASS")
        self.assertNotIn("INDEPENDENT_PASS", str(acceptance["claim_ceiling"]))

    # ---------------------------------------------------------------- NEG
    def test_maker_cannot_be_its_own_checker(self) -> None:
        with self.assertRaises(SBLError) as ctx:
            self._compile(checker="SBL-TPM")
        self.assertEqual(ctx.exception.code, "SBL_E_SELF_CHECK_FORBIDDEN")

    def test_missing_checker_receipt_is_refused(self) -> None:
        with self.assertRaises(SBLError) as ctx:
            self._compile(checker_execution_receipt="")
        self.assertEqual(ctx.exception.code, "SBL_E_SELF_CHECK_FORBIDDEN")

    def test_self_attested_receipt_is_refused(self) -> None:
        with self.assertRaises(SBLError) as ctx:
            self._compile(checker_execution_receipt="SELF_ATTESTED")
        self.assertEqual(ctx.exception.code, "SBL_E_SELF_CHECK_FORBIDDEN")

    def test_stale_head_claim_is_refused(self) -> None:
        with self.assertRaises(SBLError) as ctx:
            self._compile(repo_context_claims={"currentness": "FRESH",
                                               "currentness_epoch": "deadbeef" * 8})
        self.assertEqual(ctx.exception.code, "SBL_E_STALE_HEAD")

    def test_write_scope_escape_is_refused(self) -> None:
        with self.assertRaises(SBLError) as ctx:
            self._compile(repo_context_claims={"writable_scope": "dist/**"})
        self.assertEqual(ctx.exception.code, "SBL_E_WRITE_OUTSIDE_WRITESET")

    def test_missing_source_locator_is_refused(self) -> None:
        with self.assertRaises(SBLError) as ctx:
            pipd_adapter.compile_handoff(
                {"goal": "x", "sources": ["docs/absent.md"]}, self.root,
                checker="external-checker", checker_execution_receipt="r")
        self.assertEqual(ctx.exception.code, "SBL_E_UNLOCATED_REQUIREMENT")

    def test_handoff_without_goal_is_refused_before_compile(self) -> None:
        with self.assertRaises(SBLError) as ctx:
            pipd_adapter.compile_handoff({"sources": ["docs/spec.md"]}, self.root)
        self.assertEqual(ctx.exception.code, "SBL_E_UNLOCATED_REQUIREMENT")


if __name__ == "__main__":
    unittest.main()
