"""Operation→effect binding read from the canonical repository, not from candidates.

The candidate bundle may not supply its own operation registry: authority would
then be self-declared. This loader reads the ONE contract instance that lives in
the canonical tree, requires it to be tracked at ``HEAD`` with a matching git
blob, and refuses everything else.

The contract carries effect semantics only. It cannot create a grant, a nonce, a
checker receipt or executable readiness, and its ``authority_state`` stays
``SOURCE_BOUND_OWNER_UNVERIFIED`` until the original owner ratifies the value set.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

EFFECTS = (
    "SOURCE_READ",
    "LOCAL_DRAFT_WRITE",
    "REPOSITORY_WRITE",
    "HOST_OPERATIONS",
    "USER_DATA_EFFECT",
    "REMOTE_RELEASE",
)

#: The only path an operation registry may be loaded from. A second copy would
#: be a second authority, which this design forbids.
CANONICAL_CONTRACT = "integrations/pipd/contracts/operation-registry.pre-v2-r3.json"

CONTRACT_SCHEMA = "SBL.OperationRegistry.Binding@2"
ALLOWED_AUTHORITY = ("SOURCE_BOUND_OWNER_UNVERIFIED", "SYNTHETIC_ONLY")


class OperationRegistryError(ValueError):
    """Refusal carrying a stable code, matching the adapter's style."""


def _need(value: Any, code: str) -> None:
    if not value:
        raise OperationRegistryError(code)


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=30)
    _need(proc.returncode == 0, "GIT_PROBE_FAILED")
    return proc.stdout.decode("utf-8", "strict")


def contract_path(repo_root: Path) -> Path:
    return Path(repo_root).resolve(strict=True) / CANONICAL_CONTRACT


def load_from_repo(repo_root: Path | str) -> tuple[dict[str, Any], str]:
    """Return ``(contract, sha256)`` for the canonical contract, or refuse.

    Refusals name the reason: an untracked file, an edited working copy whose
    bytes do not match ``HEAD``, an unknown authority state, an unknown effect or
    a duplicated operation type.
    """
    root = Path(repo_root).resolve(strict=True)
    path = contract_path(root)
    _need(path.is_file(), "OPERATION_REGISTRY_MISSING")
    repo_toplevel = Path(_git(root, "rev-parse", "--show-toplevel").strip()).resolve(strict=True)
    _need(repo_toplevel == root, "OPERATION_REGISTRY_NOT_AT_REPO_ROOT")
    try:
        _git(root, "cat-file", "-e", f"HEAD:{CANONICAL_CONTRACT}")
    except OperationRegistryError as exc:  # pragma: no cover - message carries the reason
        raise OperationRegistryError("OPERATION_REGISTRY_UNTRACKED") from exc
    head_blob = _git(root, "rev-parse", f"HEAD:{CANONICAL_CONTRACT}").strip()
    working = hashlib.sha256(path.read_bytes()).hexdigest()
    head_bytes = subprocess.run(
        ["git", "-C", str(root), "cat-file", "blob", head_blob], capture_output=True, timeout=30
    )
    _need(head_bytes.returncode == 0, "OPERATION_REGISTRY_BLOB_UNREADABLE")
    head_sha = hashlib.sha256(head_bytes.stdout).hexdigest()
    # A working-tree edit must not become authority: the committed bytes win and
    # have to equal what the caller sees.
    _need(working == head_sha, "OPERATION_REGISTRY_WORKTREE_DIVERGES_FROM_HEAD")
    body = json.loads(path.read_text(encoding="utf-8"))
    validate(body)
    return body, head_sha


def validate(body: dict[str, Any]) -> dict[str, Any]:
    _need(isinstance(body, dict), "OPERATION_REGISTRY_NOT_OBJECT")
    _need(body.get("schema") == CONTRACT_SCHEMA, "OPERATION_REGISTRY_SCHEMA")
    _need(body.get("authority_state") in ALLOWED_AUTHORITY, "OPERATION_REGISTRY_AUTHORITY")
    _need(isinstance(body.get("contract_id"), str) and body["contract_id"].strip(), "OPERATION_REGISTRY_CONTRACT_ID")
    _need(isinstance(body.get("version"), str) and body["version"].strip(), "OPERATION_REGISTRY_VERSION")
    _need(isinstance(body.get("policy_epoch"), str) and body["policy_epoch"].strip(), "OPERATION_REGISTRY_EPOCH")
    owner = body.get("owner")
    _need(isinstance(owner, dict) and isinstance(owner.get("principal"), str) and owner["principal"].strip(),
          "OPERATION_REGISTRY_OWNER")
    rows = body.get("operations")
    _need(isinstance(rows, list) and rows, "OPERATION_REGISTRY_EMPTY")
    seen: set[str] = set()
    for row in rows or []:
        _need(isinstance(row, dict), "OPERATION_REGISTRY_ROW")
        operation_type = row.get("operation_type")
        _need(isinstance(operation_type, str) and operation_type.strip(), "OPERATION_REGISTRY_OPERATION_TYPE")
        _need(operation_type not in seen, "OPERATION_REGISTRY_DUPLICATE_OPERATION")
        seen.add(operation_type)
        _need(row.get("effect_class") in EFFECTS, "OPERATION_REGISTRY_UNKNOWN_EFFECT")
        for key in ("operation_id", "source_locator", "original_consumer", "consumer_abi"):
            _need(isinstance(row.get(key), str) and row[key].strip(), "OPERATION_REGISTRY_ROW_INCOMPLETE:" + key)
        scope = (body.get("operation_scopes") or {}).get(operation_type)
        _need(isinstance(scope, list) and scope, "OPERATION_REGISTRY_SCOPE_EMPTY")
        for entry in scope:
            _need(isinstance(entry, str) and entry.strip(), "OPERATION_REGISTRY_SCOPE_ENTRY")
            _need("\\" not in entry and ":" not in entry, "OPERATION_REGISTRY_SCOPE_NOT_RELATIVE")
            _need(not entry.startswith("/") and ".." not in entry.split("/"), "OPERATION_REGISTRY_SCOPE_ESCAPE")
            _need(not any(ch in entry for ch in "*?[]"), "OPERATION_REGISTRY_SCOPE_WILDCARD")
    return body


def effect_for_operation(contract: dict[str, Any], operation_type: str) -> str:
    """Effect class for an operation, from the contract only.

    Never derived from a path, an extension, a drive letter or a UNC prefix.
    """
    rows = [row for row in contract.get("operations", []) if row.get("operation_type") == operation_type]
    _need(len(rows) == 1, "OPERATION_TYPE_UNKNOWN_OR_DUPLICATE")
    return rows[0]["effect_class"]


def row_for_operation(contract: dict[str, Any], operation_type: str) -> dict[str, Any]:
    rows = [row for row in contract.get("operations", []) if row.get("operation_type") == operation_type]
    _need(len(rows) == 1, "OPERATION_TYPE_UNKNOWN_OR_DUPLICATE")
    return rows[0]


def scope_representation_invariant(contract: dict[str, Any], operation_type: str, rendered_scope: str) -> str:
    """Prove a scope *representation* cannot change the operation's effect.

    The effect is returned unchanged; a representation outside the declared
    scope is refused instead of being silently reclassified.
    """
    effect = effect_for_operation(contract, operation_type)
    row = row_for_operation(contract, operation_type)
    declared = (contract.get("operation_scopes") or {}).get(operation_type) or []
    _need(rendered_scope in declared, "SCOPE_LEAVES_OPERATION_SCOPE")
    return effect


def authority_state(contract: dict[str, Any]) -> str:
    return contract["authority_state"]


def owner_ratified(contract: dict[str, Any]) -> bool:
    """True only when the original owner recorded a decision reference.

    A candidate cannot satisfy this by writing the word RATIFIED: the state is
    accepted only from ALLOWED_AUTHORITY and a non-empty decision_ref.
    """
    owner = contract.get("owner") or {}
    ref = owner.get("decision_ref")
    return bool(isinstance(ref, str) and ref.strip()) and contract.get("authority_state") == "SOURCE_BOUND_OWNER_RATIFIED"


# ---------------------------------------------------------------------------
# Trusted loading: the CLI must not accept a caller-supplied registry.
# ---------------------------------------------------------------------------
CANONICAL_ENROLLMENT = "integrations/pipd/contracts/owner-enrollment.json"
CANONICAL_OWNER_SIG = "integrations/pipd/contracts/operation-registry.pre-v2-r3.owner.sig.json"
RATIFIED = "SOURCE_BOUND_OWNER_RATIFIED"
REQUIRED_DECISION = "RATIFY_OPERATION_EFFECT_BINDING"


def repo_root_from_package() -> Path:
    """The repository that ships this code, derived from the module path.

    Callers cannot point this at their own tree: it is where the installed
    package actually lives, and the contract must be committed there.
    """
    # <root>/integrations/pipd/src/pipd_ls_sp/operation_registry.py
    return Path(__file__).resolve().parents[4]


def _committed(root: Path, relative: str) -> bytes:
    """Bytes of a file that is tracked at HEAD and identical in the worktree."""
    root = Path(root).resolve(strict=True)
    path = root / relative
    _need(path.is_file(), "NOT_COMMITTED:" + relative)
    _git(root, "cat-file", "-e", f"HEAD:{relative}")
    blob = subprocess.run(["git", "-C", str(root), "cat-file", "blob", f"HEAD:{relative}"],
                          capture_output=True, timeout=30)
    _need(blob.returncode == 0, "NOT_COMMITTED:" + relative)
    _need(blob.stdout == path.read_bytes(), "WORKTREE_DIVERGES:" + relative)
    return blob.stdout


def verify_owner_sidecar(repo_root: Path | str, contract_sha: str) -> dict[str, Any]:
    """Verify the owner's Ed25519 ratification over this exact contract.

    The public key comes from the committed enrollment file, never from the
    sidecar, so a candidate cannot sign itself. Missing `cryptography` is a
    refusal, not a pass.
    """
    root = Path(repo_root).resolve(strict=True)
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except Exception:
        raise OperationRegistryError("OWNER_SIGNATURE_VERIFIER_UNAVAILABLE") from None
    enrollment = json.loads(_committed(root, CANONICAL_ENROLLMENT))
    sidecar = json.loads(_committed(root, CANONICAL_OWNER_SIG))
    _need(enrollment.get("schema") == "SBL.PRE_V2.OWNER_ENROLLMENT@1", "ENROLLMENT_SCHEMA")
    _need(sidecar.get("contract_sha256") == contract_sha, "SIGNED_CONTRACT_SHA_MISMATCH")
    payload = (sidecar.get("payload_json") or "").encode("utf-8")
    _need(hashlib.sha256(payload).hexdigest() == sidecar.get("payload_sha256"), "PAYLOAD_SHA_MISMATCH")
    body = json.loads(payload)
    _need(body.get("decision") == REQUIRED_DECISION, "DECISION_NOT_RATIFICATION")
    _need(body.get("contract_sha256") == contract_sha, "PAYLOAD_CONTRACT_SHA_MISMATCH")
    contract = json.loads((Path(root) / CANONICAL_CONTRACT).read_text(encoding="utf-8"))
    declared = {row.get("operation_type") for row in contract.get("operations", [])}
    ratified = set(body.get("operations") or [])
    _need(ratified and ratified <= declared, "RATIFIED_OPERATIONS_NOT_IN_CONTRACT")
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(enrollment["owner_public_hex"])).verify(
            bytes.fromhex(sidecar["signature_hex"]), payload)
    except InvalidSignature:
        raise OperationRegistryError("OWNER_SIGNATURE_INVALID") from None
    except Exception as exc:
        raise OperationRegistryError("OWNER_SIGNATURE_UNREADABLE:" + type(exc).__name__) from None
    return {
        "verified": True,
        "authority": RATIFIED,
        "contract_sha256": contract_sha,
        "owner_fingerprint": enrollment.get("owner_fingerprint"),
        "window_id": sidecar.get("window_id"),
        "signed_at": sidecar.get("signed_at"),
        "operations": sorted(ratified),
        "grant_state": "NOT_GRANTED",
        "claim_ceiling": "DESIGN_ONLY",
    }


def load_trusted(repo_root: Path | str | None = None) -> tuple[dict[str, Any], str, dict[str, Any]]:
    """Canonical contract + sha + a verified owner ratification, or a refusal."""
    root = Path(repo_root) if repo_root is not None else repo_root_from_package()
    body, sha = load_from_repo(root)
    return body, sha, verify_owner_sidecar(root, sha)
