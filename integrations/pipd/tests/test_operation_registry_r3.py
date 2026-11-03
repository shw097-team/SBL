"""CT-03: the operation→effect binding must come from the canonical repo.

POS: the committed contract loads and yields one effect per operation.
NEG: an untracked, edited, duplicated, unknown or escaping contract is refused,
and a path representation can never reclassify an effect.
Integration POS: the original adapter accepts the loaded contract and still
emits ``EFFECT_UNBOUND`` / ``grant_state=NOT_GRANTED``.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import operation_registry as reg  # noqa: E402

CONTRACT = ROOT / "contracts" / "operation-registry.pre-v2-r3.json"


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "canonical"
    (root / "integrations" / "pipd" / "contracts").mkdir(parents=True)
    shutil.copy2(CONTRACT, root / reg.CANONICAL_CONTRACT)
    git(root, "init", "-q")
    # Windows global core.autocrlf would rewrite the committed blob and make the
    # byte comparison in the loader meaningless for the fixture.
    git(root, "config", "core.autocrlf", "false")
    git(root, "config", "user.email", "r3@example.invalid")
    git(root, "config", "user.name", "r3")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "operation registry contract")
    return root


def rewrite(root: Path, mutate) -> None:
    path = root / reg.CANONICAL_CONTRACT
    body = json.loads(path.read_text(encoding="utf-8"))
    mutate(body)
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")


def test_pos_contract_loads_from_committed_head(repo: Path) -> None:
    body, sha = reg.load_from_repo(repo)
    assert body["schema"] == reg.CONTRACT_SCHEMA
    assert reg.authority_state(body) == "SOURCE_BOUND_OWNER_UNVERIFIED"
    assert len(sha) == 64
    assert reg.owner_ratified(body) is False


def test_pos_each_operation_maps_to_its_effect(repo: Path) -> None:
    body, _ = reg.load_from_repo(repo)
    assert reg.effect_for_operation(body, "SOURCE_READ") == "SOURCE_READ"
    assert reg.effect_for_operation(body, "LOCAL_DRAFT_WRITE") == "LOCAL_DRAFT_WRITE"
    assert reg.effect_for_operation(body, "REPOSITORY_WRITE") == "REPOSITORY_WRITE"


def test_neg_untracked_contract_is_refused(repo: Path) -> None:
    (repo / reg.CANONICAL_CONTRACT).unlink()
    git(repo, "commit", "-qam", "drop contract")
    with pytest.raises(reg.OperationRegistryError) as exc:
        reg.load_from_repo(repo)
    assert str(exc.value) == "OPERATION_REGISTRY_MISSING"


def test_neg_worktree_edit_does_not_become_authority(repo: Path) -> None:
    rewrite(repo, lambda body: body["operations"][0].update(effect_class="HOST_OPERATIONS"))
    with pytest.raises(reg.OperationRegistryError) as exc:
        reg.load_from_repo(repo)
    assert str(exc.value) == "OPERATION_REGISTRY_WORKTREE_DIVERGES_FROM_HEAD"


def test_neg_duplicate_operation_type(repo: Path) -> None:
    rewrite(repo, lambda body: body["operations"].append(dict(body["operations"][0])))
    git(repo, "commit", "-qam", "duplicate")
    with pytest.raises(reg.OperationRegistryError) as exc:
        reg.load_from_repo(repo)
    assert str(exc.value) == "OPERATION_REGISTRY_DUPLICATE_OPERATION"


def test_neg_unknown_effect(repo: Path) -> None:
    rewrite(repo, lambda body: body["operations"][0].update(effect_class="READ_ANYTHING"))
    git(repo, "commit", "-qam", "unknown effect")
    with pytest.raises(reg.OperationRegistryError) as exc:
        reg.load_from_repo(repo)
    assert str(exc.value) == "OPERATION_REGISTRY_UNKNOWN_EFFECT"


def test_neg_absolute_scope_representation(repo: Path) -> None:
    rewrite(repo, lambda body: body["operation_scopes"].update(SOURCE_READ=["C:\\repo\\src\\demo\\billing.py"]))
    git(repo, "commit", "-qam", "absolute scope")
    with pytest.raises(reg.OperationRegistryError) as exc:
        reg.load_from_repo(repo)
    assert str(exc.value) == "OPERATION_REGISTRY_SCOPE_NOT_RELATIVE"


def test_neg_unknown_operation_is_not_reclassified(repo: Path) -> None:
    body, _ = reg.load_from_repo(repo)
    with pytest.raises(reg.OperationRegistryError) as exc:
        reg.effect_for_operation(body, "OP-DOES-NOT-EXIST")
    assert str(exc.value) == "OPERATION_TYPE_UNKNOWN_OR_DUPLICATE"


def test_k4_path_representation_never_changes_effect(repo: Path) -> None:
    body, _ = reg.load_from_repo(repo)
    relative = reg.scope_representation_invariant(body, "REPOSITORY_WRITE", "src/demo/billing.py")
    assert relative == "REPOSITORY_WRITE"
    for outside in ("C:/repo/src/demo/billing.py", "//server/share/billing.py", "../billing.py"):
        with pytest.raises(reg.OperationRegistryError) as exc:
            reg.scope_representation_invariant(body, "REPOSITORY_WRITE", outside)
        assert str(exc.value) == "SCOPE_LEAVES_OPERATION_SCOPE"


def test_integration_adapter_accepts_the_loaded_contract(repo: Path) -> None:
    from pipd_ls_sp import pre_v2_adapter as adapter

    body, _ = reg.load_from_repo(repo)
    context = {
        "subject_id": "SUBJ-R3-001",
        "candidate_sha256": "1" * 64,
        "scope": ["src/demo/billing.py"],
        "host": "HOST-GJ02",
        "policy_epoch": "2026-11-03T00:00:00Z",
    }
    details = {
        "source_locator": "src/demo/billing.py",
        "acl_ref": "ACL-SOURCE-READ-1",
        "expected_sha256": "2" * 64,
        "precondition": "SOURCE_EXISTS",
        "expected_postcondition": "NO_WORLD_WRITE",
        "permission_basis": "ACL_READ",
        "idempotency_key": "IDEM-R3-001",
        "on_unknown": "RECONCILE_NO_BLIND_RETRY",
        "reconcile_reader": "SBL-SOURCE-READER",
        "readback_kind": "SOURCE_SHA256",
    }
    intent = adapter.ecp_intent(context, "SOURCE_READ", body, details)
    assert intent["effect_state"] == "EFFECT_UNBOUND"
    assert intent["grant_state"] == "NOT_GRANTED"
    assert intent["claim_ceiling"] == "AUTHOR_DESIGN_ONLY"
    assert intent["operation"]["operation_id"] == "OP-SRC-READ-01"


def test_neg_adapter_refuses_read_labelled_as_repository_write(repo: Path) -> None:
    """A read operation cannot borrow the write effect from the registry row."""
    from pipd_ls_sp import pre_v2_adapter as adapter

    body, _ = reg.load_from_repo(repo)
    context = {
        "subject_id": "SUBJ-R3-002",
        "candidate_sha256": "3" * 64,
        "scope": ["src/demo/billing.py"],
        "host": "HOST-GJ02",
        "policy_epoch": "2026-11-03T00:00:00Z",
    }
    details = {
        "source_locator": "src/demo/billing.py",
        "postimages": {"src/demo/billing.py": "4" * 64},
        "rollback_commit": "5" * 40,
        "repo_binding": str(repo),
        "precondition": "HEAD_IS_PREIMAGE",
        "expected_postcondition": "WRITE_SCOPE_ONLY",
        "permission_basis": "DEV_ECP",
        "idempotency_key": "IDEM-R3-002",
        "on_unknown": "RECONCILE_NO_BLIND_RETRY",
        "reconcile_reader": "SBL-REPO-READER",
        "readback_kind": "GIT_POSTIMAGE",
    }
    # SOURCE_READ details cannot satisfy REPOSITORY_WRITE, and vice versa: the
    # effect comes from the row, so the mismatch surfaces as missing fields.
    with pytest.raises(adapter.Refusal):
        adapter.ecp_intent(context, "SOURCE_READ", body, details)
