"""Operation *instances*: one repo-bound, write-set-bound candidate per operation type.

WHY THIS MODULE EXISTS
----------------------
``operation_registry`` binds an operation type to an effect class. It does not bind an
operation to a *repository*. ``operation_scopes.REPOSITORY_WRITE`` is the demo path list
``src/demo/billing.py``; nothing in the loader compares the owner's signed scope against the
request's actual write set, so a write set that the owner never saw can sit inside a
signature that looks valid. This module adds the missing quantifier without widening anything:

  * an instance is a separate, named row — the effect class is NOT redefined and the demo
    scope is NOT extended;
  * an instance is bound to one repository identity (id + full name), one head, and one exact
    write set, each entry carrying its own preimage expectation and postimage digest;
  * ``evaluate`` refuses on any deviation and never returns an admitted state;
  * ``ratified_scope_covers`` answers the question the existing loader cannot: does the
    owner's signed scope actually name these paths?

WHAT THIS MODULE IS NOT
-----------------------
It is not a ratification, a grant, a Permit or an admission. It cannot sign, write, or read
the network, and it does not open the operation registry. ``EFFECT_UNBOUND`` is returned even
when every check passes: passing here means "this request is the request that was described",
not "this request may run". The original issuer still decides that.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

INSTANCE_SCHEMA = "SBL.OperationRegistry.Instance@1"

CLAIM_CEILING = (
    "INSTANCE_RESOLUTION_ONLY - not a ratification, not a grant, not a Permit, not an "
    "admitted effect. A resolved instance means the request matches the described operation; "
    "it never means the operation may run."
)

REFUSALS = (
    "INSTANCE_UNKNOWN",
    "INSTANCE_REPO_IDENTITY_MISMATCH",
    "INSTANCE_HEAD_DRIFT",
    "INSTANCE_SCOPE_NOT_EXACT",
    "INSTANCE_PREIMAGE_NOT_ABSENT",
    "INSTANCE_WORKTREE_NOT_CLEAN",
    "INSTANCE_DEMO_SCOPE_OVERLAP",
    "INSTANCE_CONTRACT_INCOMPLETE",
    "INSTANCE_NOT_IN_RATIFIED_SCOPE",
)


class InstanceRefused(ValueError):
    """A refusal carrying a stable code, in the style of ``pre_v2_adapter.need``."""

    def __init__(self, code: str, detail: Any = None) -> None:
        super().__init__(code)
        self.code = code
        self.detail = detail


def _need(condition: Any, code: str, detail: Any = None) -> None:
    if not condition:
        raise InstanceRefused(code, detail)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def instance_rows(contract: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    rows = contract.get("operation_instances") or []
    _need(isinstance(rows, list), "INSTANCE_CONTRACT_INCOMPLETE", "operation_instances not a list")
    return rows


def find_instance(contract: Mapping[str, Any], instance_id: str) -> Mapping[str, Any]:
    rows = [r for r in instance_rows(contract) if r.get("instance_id") == instance_id]
    _need(len(rows) == 1, "INSTANCE_UNKNOWN", {"instance_id": instance_id, "rows": len(rows)})
    row = rows[0]
    for key in ("instance_id", "operation_type", "effect_class", "repo", "write_set", "scope_policy"):
        _need(row.get(key), "INSTANCE_CONTRACT_INCOMPLETE", key)
    repo = row["repo"]
    for key in ("id", "full_name", "head_at_bind", "tree_at_bind"):
        _need(repo.get(key), "INSTANCE_CONTRACT_INCOMPLETE", "repo." + key)
    ws = row["write_set"]
    _need(isinstance(ws, list) and ws, "INSTANCE_CONTRACT_INCOMPLETE", "write_set empty")
    for entry in ws:
        for key in ("relpath", "change", "preimage", "postimage_sha256"):
            _need(entry.get(key), "INSTANCE_CONTRACT_INCOMPLETE", "write_set." + key)
    paths = [e["relpath"] for e in ws]
    _need(len(set(paths)) == len(paths), "INSTANCE_CONTRACT_INCOMPLETE", "duplicate relpath")
    return row


def demo_scope_overlap(contract: Mapping[str, Any], instance: Mapping[str, Any]) -> List[str]:
    """Instance paths that fall inside another operation's declared scope.

    Sharing a path with the demo operation would silently inherit its authorisation; that is
    the widening this design refuses to perform, so an overlap is a refusal and not a warning.
    """
    paths = [e["relpath"] for e in instance["write_set"]]
    overlap: List[str] = []
    for op_type, scope in (contract.get("operation_scopes") or {}).items():
        if op_type == instance["operation_type"]:
            continue
        for path in paths:
            if path in (scope or []):
                overlap.append(path)
    return overlap


def evaluate(
    contract: Mapping[str, Any],
    instance_id: str,
    repo_state: Mapping[str, Any],
    *,
    observed: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    """Resolve ``instance_id`` against a PROBE_OBSERVED repo state.

    ``repo_state`` is the ``repo`` mapping produced by ``pre_v2_adapter.probe_repo``; it is
    the only accepted shape, so a caller cannot describe a repository the probe did not see.
    ``observed`` optionally carries the sha256 actually about to be written, which is compared
    against the instance's postimage.
    """
    _need(contract.get("schema") == "SBL.OperationRegistry.Binding@2", "INSTANCE_CONTRACT_INCOMPLETE",
          "contract schema")
    instance = find_instance(contract, instance_id)
    repo = instance["repo"]

    _need(isinstance(repo_state, Mapping) and repo_state.get("head"), "INSTANCE_CONTRACT_INCOMPLETE",
          "repo_state is not a probe observation")
    _need(instance["write_set"] and repo_state.get("write_scope") is not None,
          "INSTANCE_CONTRACT_INCOMPLETE", "repo_state.write_scope missing")

    # 1. repository identity: an instance names exactly one repository
    _need(repo_state.get("repo_id") in (None, repo["id"]) and
          repo_state.get("full_name") in (None, repo["full_name"]),
          "INSTANCE_REPO_IDENTITY_MISMATCH",
          {"declared": {"id": repo["id"], "full_name": repo["full_name"]},
           "observed": {"id": repo_state.get("repo_id"), "full_name": repo_state.get("full_name")}})

    # 2. head: the binding head must be the head the probe just read
    _need(repo_state["head"] == repo["head_at_bind"], "INSTANCE_HEAD_DRIFT",
          {"declared": repo["head_at_bind"], "observed": repo_state["head"]})

    # 3. scope: exact set equality, not containment — a subset write is a different write
    declared_paths = [e["relpath"] for e in instance["write_set"]]
    observed_scope = list(repo_state.get("write_scope") or [])
    _need(set(observed_scope) == set(declared_paths), "INSTANCE_SCOPE_NOT_EXACT",
          {"declared": sorted(declared_paths), "observed": sorted(observed_scope)})

    # 4. preimage: an ADD requires ABSENT; an overwrite is refused, not silently allowed
    preimages = repo_state.get("preimages") or {}
    for entry in instance["write_set"]:
        seen = preimages.get(entry["relpath"])
        if entry["preimage"] == "ABSENT":
            _need(seen == "ABSENT", "INSTANCE_PREIMAGE_NOT_ABSENT",
                  {"relpath": entry["relpath"], "observed": seen})
        else:
            _need(seen == entry["preimage"], "INSTANCE_PREIMAGE_NOT_ABSENT",
                  {"relpath": entry["relpath"], "observed": seen,
                   "declared": entry["preimage"]})

    # 5. worktree: nothing outside the write set may be modified or untracked
    _need(not repo_state.get("dirty"), "INSTANCE_WORKTREE_NOT_CLEAN",
          {"status_sha256": repo_state.get("status_sha256")})
    untracked = repo_state.get("untracked_files")
    if isinstance(untracked, Sequence) and not isinstance(untracked, (str, bytes)):
        stray = sorted(set(untracked) - set(declared_paths))
        _need(not stray, "INSTANCE_WORKTREE_NOT_CLEAN", {"untracked_outside_scope": stray})

    # 6. no shared path with another operation's authorised scope
    overlap = demo_scope_overlap(contract, instance)
    _need(not overlap, "INSTANCE_DEMO_SCOPE_OVERLAP", overlap)

    # 7. declared postimage must be the bytes about to be written
    if observed is not None:
        for entry in instance["write_set"]:
            got = observed.get(entry["relpath"])
            _need(got == entry["postimage_sha256"], "INSTANCE_CONTRACT_INCOMPLETE",
                  {"relpath": entry["relpath"], "declared": entry["postimage_sha256"], "observed": got})

    return {
        "schema": INSTANCE_SCHEMA,
        "instance_id": instance["instance_id"],
        "operation_type": instance["operation_type"],
        "effect_class": instance["effect_class"],
        "repo": {"id": repo["id"], "full_name": repo["full_name"], "head": repo_state["head"]},
        "write_set": [{"relpath": e["relpath"], "change": e["change"],
                       "preimage": e["preimage"], "postimage_sha256": e["postimage_sha256"]}
                      for e in instance["write_set"]],
        "effect_state": "EFFECT_UNBOUND",
        "grant_state": "NOT_GRANTED",
        "registry_authority": contract.get("authority_state"),
        "claim_ceiling": CLAIM_CEILING,
        "admitted": False,
    }


def ratified_scope_covers(contract: Mapping[str, Any], instance_id: str,
                          ratified_scope: Iterable[str]) -> Tuple[bool, List[str]]:
    """Does the owner's signed scope name every instance path?

    ``verify_owner_sidecar`` verifies the signature over the contract sha and checks that the
    ratified *operations* are a subset of the contract's — it never compares the ratified
    *scope* with any write set. Callers must ask this question explicitly; a False answer is
    what stops an existing signature from being read as authority over new paths.
    """
    instance = find_instance(contract, instance_id)
    signed = set(ratified_scope or [])
    missing = sorted({e["relpath"] for e in instance["write_set"]} - signed)
    return (not missing, missing)


def instance_digest(contract: Mapping[str, Any], instance_id: str) -> str:
    """Stable digest of one instance, for a decision reference to quote."""
    instance = find_instance(contract, instance_id)
    body = json.dumps(instance, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(body)
