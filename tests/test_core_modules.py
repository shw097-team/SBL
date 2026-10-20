"""Slice A acceptance: SBLM01..SBLM06 shared-core behaviour."""

from __future__ import annotations

import os
import subprocess
import shutil
import tempfile

import pytest

from sbl_core import m04_bridge
from sbl_core.core import MODULES, SharedCore
from sbl_core.dto import (
    BuildOrder,
    Goal,
    RepoContextDTO,
    SpecAtom,
    WriteSet,
    atom_id_for,
    goal_id_for,
    order_id_for,
)
from sbl_core.errors import ERROR_CODES, SBLError
from sbl_core.m01_intake import GoalIntake
from sbl_core.m02_spec import GuidedSpecification
from sbl_core.m03_routing import DEFAULT_POLICY, GovernedRouting
from sbl_core.m04_bridge import GovernedBuildBridge, bind_repo_context
from sbl_core.m05_verify import EvidenceVerification
from sbl_core.m06_repair import BoundedRepair

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


# ---------------------------------------------------------------- M01 intake


def test_intake_positive_deterministic_goal():
    intake = GoalIntake()
    first = intake.intake("  Ship Slice A  ", "desc", "tpm")
    second = intake.intake("ship slice a")
    assert first.title == "Ship Slice A"
    assert first.description == "desc"
    assert first.requester == "tpm"
    assert first.goal_id == goal_id_for("  Ship Slice A  ")
    assert first.goal_id == second.goal_id
    assert first.goal_id.startswith("G-") and len(first.goal_id) == 14
    assert first.to_dict() == {
        "goal_id": first.goal_id,
        "title": "Ship Slice A",
        "description": "desc",
        "requester": "tpm",
    }


def test_intake_negative_empty_title():
    with pytest.raises(SBLError) as caught:
        GoalIntake().intake("   ")
    assert caught.value.code == "SBL_E_EMPTY_TITLE"
    assert caught.value.as_dict()["ok"] is False


def test_intake_negative_overlong_title():
    with pytest.raises(SBLError) as caught:
        GoalIntake().intake("x" * 201)
    assert caught.value.code == "SBL_E_BAD_STATE"


# ------------------------------------------------------------------ M02 spec


def test_spec_positive_order_and_idempotence():
    atoms = GuidedSpecification().derive(
        Goal("G-1", "g"),
        [
            {"text": "first", "locator": "a.md#L1-L2"},
            {"text": "second", "locator": "b.md#L3"},
            {"text": "first", "locator": "a.md#L1-L2"},
        ],
    )
    assert [atom.text for atom in atoms] == ["first", "second"]
    assert [atom.atom_id for atom in atoms] == [atom_id_for("first"), atom_id_for("second")]
    assert atoms[0].locator == "a.md#L1-L2"
    assert atoms[0].to_dict()["atom_id"] == atom_id_for("first")


def test_spec_negative_missing_locator():
    with pytest.raises(SBLError) as caught:
        GuidedSpecification().derive(
            Goal("G-1", "g"), [{"text": "needs a binding", "locator": ""}]
        )
    assert caught.value.code == "SBL_E_UNLOCATED_REQUIREMENT"


def test_spec_negative_zero_clauses():
    with pytest.raises(SBLError) as caught:
        GuidedSpecification().derive(Goal("G-1", "g"), [])
    assert caught.value.code == "SBL_E_BAD_STATE"


# --------------------------------------------------------------- M03 routing


def test_routing_positive_default_policy():
    atom = SpecAtom(atom_id_for("t"), "t", "x.md#L1")
    routing = GovernedRouting()
    assert routing.policy == DEFAULT_POLICY
    decision = routing.route(atom, "CLI_TOOL")
    assert decision.permitted is True
    assert decision.target == "SBLM04_GOVERNED_BUILD_BRIDGE"
    assert decision.atom_id == atom.atom_id
    assert routing.route(atom, "SKILL").target == "GJ03_SKILL_AGENT_BRIDGE"
    assert decision.to_dict()["permitted"] is True


def test_routing_negative_unknown_kind():
    atom = SpecAtom(atom_id_for("t"), "t", "x.md#L1")
    with pytest.raises(SBLError) as caught:
        GovernedRouting().route(atom, "MAGIC")
    assert caught.value.code == "SBL_E_UNKNOWN_KIND"


@pytest.mark.parametrize("kind", ["AGENT_OS", "AI_SYSTEM"])
def test_routing_negative_prohibited_kind(kind):
    atom = SpecAtom(atom_id_for("t"), "t", "x.md#L1")
    with pytest.raises(SBLError) as caught:
        GovernedRouting().route(atom, kind)
    assert caught.value.code == "SBL_E_PROHIBITED_KIND"


# ---------------------------------------------------------------- M04 bridge


def test_bind_repo_context_positive_reads_real_repo():
    ctx = bind_repo_context(REPO_ROOT)
    assert len(ctx.head) == 40
    assert ctx.tracked_files > 0
    assert isinstance(ctx.dirty, bool)
    assert ctx.to_dict()["root"] == REPO_ROOT


def test_bind_repo_context_negative_not_a_repo():
    outside = tempfile.mkdtemp(prefix="sbl-not-a-repo-")
    try:
        with pytest.raises(SBLError) as caught:
            bind_repo_context(outside)
        assert caught.value.code == "SBL_E_BAD_STATE"
    finally:
        shutil.rmtree(outside, ignore_errors=True)


def _make_directory_link(link, target):
    """Create a directory link, or skip: symlinks need privilege on Windows, junctions do not."""

    try:
        os.symlink(str(target), str(link), target_is_directory=True)
        return "symlink"
    except (OSError, NotImplementedError, AttributeError):
        pass
    if os.name == "nt":
        # No text=True: mklink writes the console codepage, and decoding it can raise.
        completed = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0 and os.path.exists(str(link)):
            return "junction"
    pytest.skip("ENV: this host can create neither a symlink nor a junction")


def _fake_order(tmp_path, head="a" * 40, prefixes=("src",)):
    return BuildOrder(
        order_id=order_id_for(head, WriteSet(prefixes)),
        root=str(tmp_path),
        head=head,
        writeset=WriteSet(prefixes),
    )


def test_bridge_prepare_positive_and_empty_negative(tmp_path):
    bridge = GovernedBuildBridge()
    ctx = RepoContextDTO(root=str(tmp_path), head="b" * 40, tracked_files=3, dirty=False)
    order = bridge.prepare(ctx, WriteSet(("src", "tests")))
    assert order.head == ctx.head
    assert order.writeset.paths == ("src", "tests")
    assert order.order_id == order_id_for(ctx.head, order.writeset)
    with pytest.raises(SBLError) as caught:
        bridge.prepare(ctx, WriteSet(()))
    assert caught.value.code == "SBL_E_BAD_STATE"


def test_bridge_apply_positive_writes_under_writeset(tmp_path, monkeypatch):
    monkeypatch.setattr("sbl_core.m04_bridge._head_of", lambda root: "a" * 40)
    bridge = GovernedBuildBridge()
    order = _fake_order(tmp_path)
    applied = bridge.apply(order, "src/pkg/mod.py", "value = 1\n")
    target = tmp_path / "src" / "pkg" / "mod.py"
    assert target.read_text(encoding="utf-8") == "value = 1\n"
    assert "src/pkg/mod.py" in applied.writeset.paths
    assert applied.head == order.head
    assert order.order_id == applied.order_id


@pytest.mark.parametrize(
    "bad_path",
    ["../escape.py", "src/../../escape.py", "/abs/escape.py", "C:/escape.py", "other/x.py"],
)
def test_bridge_apply_negative_outside_writeset(tmp_path, bad_path):
    bridge = GovernedBuildBridge()
    with pytest.raises(SBLError) as caught:
        bridge.apply(_fake_order(tmp_path), bad_path, "x")
    assert caught.value.code == "SBL_E_WRITE_OUTSIDE_WRITESET"
    assert not (tmp_path.parent / "escape.py").exists()


def test_bridge_apply_refuses_a_path_that_changes_between_check_and_write(tmp_path, monkeypatch):
    """V16-BRIDGE-01: a checker swapped a directory for a junction after validation and escaped."""

    monkeypatch.setattr("sbl_core.m04_bridge._head_of", lambda root: "a" * 40)
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    target = str(root / "src" / "file.txt")
    real = m04_bridge.os.path.realpath

    calls = {"target": 0}

    def swap_after_validation(path, *args, **kwargs):
        if os.path.abspath(str(path)) == os.path.abspath(target):
            calls["target"] += 1
            if calls["target"] >= 2:  # the pre-write re-resolution
                return str(outside / "file.txt")
        return real(path, *args, **kwargs)

    monkeypatch.setattr("sbl_core.m04_bridge.os.path.realpath", swap_after_validation)
    bridge = GovernedBuildBridge()
    with pytest.raises(SBLError) as caught:
        bridge.apply(_fake_order(root), "src/file.txt", "payload")
    assert caught.value.code == "SBL_E_WRITE_OUTSIDE_WRITESET"
    assert not (outside / "file.txt").exists()


def test_bridge_apply_negative_symlink_escape(tmp_path, monkeypatch):
    """A link inside the writeset must not carry a write outside the repository (M2)."""

    monkeypatch.setattr("sbl_core.m04_bridge._head_of", lambda root: "a" * 40)
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    _make_directory_link(root / "src" / "link", outside)
    bridge = GovernedBuildBridge()
    with pytest.raises(SBLError) as caught:
        bridge.apply(_fake_order(root, prefixes=("src",)), "src/link/pwned.py", "owned\n")
    assert caught.value.code == "SBL_E_WRITE_OUTSIDE_WRITESET"
    assert not (outside / "pwned.py").exists()


def test_bridge_apply_positive_inside_a_link_that_stays_inside(tmp_path, monkeypatch):
    """The link check must not refuse a link whose real destination is still in scope."""

    monkeypatch.setattr("sbl_core.m04_bridge._head_of", lambda root: "a" * 40)
    root = tmp_path / "repo"
    (root / "src" / "real").mkdir(parents=True)
    _make_directory_link(root / "src" / "alias", root / "src" / "real")
    bridge = GovernedBuildBridge()
    bridge.apply(_fake_order(root, prefixes=("src",)), "src/alias/ok.py", "value = 1\n")
    assert (root / "src" / "real" / "ok.py").read_text(encoding="utf-8") == "value = 1\n"


def test_bridge_apply_negative_stale_head(tmp_path, monkeypatch):
    monkeypatch.setattr("sbl_core.m04_bridge._head_of", lambda root: "c" * 40)
    bridge = GovernedBuildBridge()
    with pytest.raises(SBLError) as caught:
        bridge.apply(_fake_order(tmp_path, head="a" * 40), "src/x.py", "x")
    assert caught.value.code == "SBL_E_STALE_HEAD"
    assert not (tmp_path / "src" / "x.py").exists()


# ------------------------------------------------------------- M05 evidence


def test_verify_positive_record_and_verdict():
    verifier = EvidenceVerification()
    item = verifier.record("G01", "pytest -q", 0, "3 passed\n", 3)
    assert item.denominator == 3
    assert len(item.stdout_sha256) == 64
    assert item.stdout_sha256 == verifier.record("G01", "pytest -q", 0, "3 passed\n", 3).stdout_sha256
    verdict = verifier.verdict("G01", "maker_sp", "checker_sp", "PASS", "LOCAL", "LOCAL")
    assert verdict.status == "PASS"
    assert verdict.claim_level == "LOCAL"
    assert verdict.to_dict()["checker"] == "checker_sp"


def test_verify_ceiling_belongs_to_the_instance():
    """SEC-02: the ceiling comes from the instance; an argument may not lift it."""

    local = EvidenceVerification()  # build ceiling LOCAL
    local.record("G01", "pytest -q", 0, "1 passed\n", 1)
    assert local.verdict("G01", "a", "b", "PASS", "LOCAL", "LOCAL").claim_level == "LOCAL"

    for requested in ("PACKAGE", "EXTERNAL_ACCEPTANCE", "PRODUCTION"):
        with pytest.raises(SBLError) as caught:
            local.verdict("G01", "a", "b", "FAIL", requested, "LOCAL")
        assert caught.value.code == "SBL_E_CLAIM_CEILING_EXCEEDED"
        assert caught.value.detail["build_ceiling"] == "LOCAL"


def test_verify_constructor_cannot_raise_the_build_ceiling():
    """NEW-01: constructing a verifier with a higher ceiling is itself a bypass attempt."""

    with pytest.raises(SBLError) as caught:
        EvidenceVerification(ceiling="PRODUCTION")
    assert caught.value.code == "SBL_E_CLAIM_CEILING_EXCEEDED"
    assert caught.value.detail["build_ceiling"] == "LOCAL"


def test_verify_ceiling_attribute_is_read_only():
    verifier = EvidenceVerification()
    with pytest.raises(AttributeError):
        verifier.ceiling = "PRODUCTION"  # type: ignore[misc]
    assert verifier.ceiling == "LOCAL"


def test_verify_negative_pass_without_evidence():
    """SEC-03: a PASS must be bound to a recorded receipt for the same gate."""

    with pytest.raises(SBLError) as caught:
        EvidenceVerification().verdict("G-never", "a", "b", "PASS", "LOCAL", "LOCAL")
    assert caught.value.code == "SBL_E_BAD_STATE"
    assert caught.value.detail["reason"] == "no_recorded_evidence"


def test_verify_negative_pass_after_failing_evidence():
    verifier = EvidenceVerification()
    verifier.record("G01", "pytest -q", 1, "1 failed\n", 1)
    with pytest.raises(SBLError) as caught:
        verifier.verdict("G01", "a", "b", "PASS", "LOCAL", "LOCAL")
    assert caught.value.code == "SBL_E_BAD_STATE"
    assert caught.value.detail["reason"] == "evidence_exit_nonzero"


@pytest.mark.parametrize("status", ["file_exists", "FILE_EXISTS ", " File_Exists", "SYMBOL_EXISTS"])
def test_verify_negative_proxy_status_variants(status):
    """SEC-03: proxy statuses are refused after normalisation, not by exact spelling."""

    verifier = EvidenceVerification()
    verifier.record("G01", "pytest -q", 0, "1 passed\n", 1)
    with pytest.raises(SBLError) as caught:
        verifier.verdict("G01", "a", "b", status, "LOCAL", "LOCAL")
    assert caught.value.code == "SBL_E_BAD_STATE"


@pytest.mark.parametrize("status", ["OK", "DONE", ""])
def test_verify_negative_undeclared_status(status):
    verifier = EvidenceVerification()
    verifier.record("G01", "pytest -q", 0, "1 passed\n", 1)
    with pytest.raises(SBLError) as caught:
        verifier.verdict("G01", "a", "b", status, "LOCAL", "LOCAL")
    assert caught.value.code == "SBL_E_BAD_STATE"


def test_verify_negative_zero_denominator():
    with pytest.raises(SBLError) as caught:
        EvidenceVerification().record("G01", "pytest -q", 0, "", 0)
    assert caught.value.code == "SBL_E_BAD_STATE"


def test_verify_negative_self_check():
    with pytest.raises(SBLError) as caught:
        EvidenceVerification().verdict("G01", "TPM_SP", " tpm_sp ", "PASS", "LOCAL", "LOCAL")
    assert caught.value.code == "SBL_E_SELF_CHECK_FORBIDDEN"


def test_verify_negative_claim_ceiling():
    verifier = EvidenceVerification()
    verifier.record("G01", "pytest -q", 0, "1 passed\n", 1)
    with pytest.raises(SBLError) as caught:
        verifier.verdict("G01", "a", "b", "PASS", "PACKAGE", "PRODUCTION")
    assert caught.value.code == "SBL_E_CLAIM_CEILING_EXCEEDED"


@pytest.mark.parametrize(
    "status", ["FILE_EXISTS", "SYMBOL_EXISTS", "SUMMARY_ONLY", "DOCUMENTED"]
)
def test_verify_negative_proxy_status(status):
    with pytest.raises(SBLError) as caught:
        EvidenceVerification().verdict("G01", "a", "b", status, "LOCAL", "LOCAL")
    assert caught.value.code == "SBL_E_BAD_STATE"


# --------------------------------------------------------------- M06 repair


def test_repair_positive_narrow_plan():
    plan = BoundedRepair().plan("G01 failed", ["evidence/g01.log"], attempts=1)
    assert plan.action == "NARROW_REPAIR"
    assert plan.rollback_pointer == "evidence/g01.log"
    assert plan.max_attempts == 3
    assert plan.first_fail == "G01 failed"
    assert plan.to_dict()["action"] == "NARROW_REPAIR"


def test_repair_positive_escalates_at_cap():
    plan = BoundedRepair().plan("G01 failed", ["evidence/g01.log"], attempts=3)
    assert plan.action == "STOP_ESCALATE"


def test_repair_negative_without_evidence():
    with pytest.raises(SBLError) as caught:
        BoundedRepair().plan("G01 failed", [])
    assert caught.value.code == "SBL_E_REPAIR_WITHOUT_EVIDENCE"


# ----------------------------------------------------------------- core/doc


def test_shared_core_doctor_and_error_registry():
    core = SharedCore(REPO_ROOT)
    doctor = core.doctor()
    assert doctor["schema"] == "SBL-CORE-DOCTOR/1"
    assert doctor["modules"] == list(MODULES)
    assert doctor["ok"] is True
    assert doctor["root"] == REPO_ROOT
    assert isinstance(core.bridge, GovernedBuildBridge)
    assert "SBL_E_PROHIBITED_KIND" in ERROR_CODES
    assert "SBL_E_UNKNOWN_MODE" in ERROR_CODES
    with pytest.raises(SBLError) as caught:
        raise SBLError("SBL_E_BAD_STATE", "boom", {"k": "v"})
    assert caught.value.as_dict() == {
        "ok": False,
        "code": "SBL_E_BAD_STATE",
        "message": "boom",
        "detail": {"k": "v"},
    }
