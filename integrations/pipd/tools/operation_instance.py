"""Operation *instances*: one repo-bound, write-set-bound candidate per operation type.

WHY THIS MODULE EXISTS
----------------------
``operation_registry`` binds an operation type to an effect class. It does not bind an
operation to a *repository*, and ``verify_owner_sidecar`` never compares the owner's signed
scope with a write set. This module adds the missing quantifier without widening anything:

  * an instance is a separate, named row — the effect class is NOT redefined and the demo scope
    is NOT extended;
  * an instance is bound to one repository identity (id + full name), one head, one tree, and one
    exact write set, each entry carrying its own preimage expectation and postimage digest;
  * ``evaluate`` answers the design question ("is this the operation that was described?");
    ``evaluate_write`` answers the write question and is strict about everything the design
    check tolerates: identity must be independently resolved, postimages must be supplied, the
    signed scope must be *equal* to the write set, and the TTL/op budget must still hold;
  * ``ratified_scope_exactly_matches`` is the comparison the original loader lacks.

WHAT THIS MODULE IS NOT
-----------------------
It is not a ratification, a grant, a Permit or an admission. ``EFFECT_UNBOUND`` is returned even
when every check passes: passing means "this is the request that was described", not "this
request may run". The original issuer decides that, and the original writer consumes it.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

INSTANCE_SCHEMA = "SBL.OperationRegistry.Instance@2"

CLAIM_CEILING = (
    "INSTANCE_RESOLUTION_ONLY - not a ratification, not a grant, not a Permit, not an "
    "admitted effect. A resolved instance means the request matches the described operation; "
    "it never means the operation may run."
)

#: Longest relpath this design will carry. A longer one is a Windows MAX_PATH accident waiting to
#: happen, and the measured failure mode of that accident on this host is a silently empty git
#: object (rc 128, empty stdout), not an error.
MAX_RELPATH = 180

REFUSALS = (
    "INSTANCE_UNKNOWN",
    "INSTANCE_CONTRACT_INCOMPLETE",
    "INSTANCE_CONTRACT_SHA_MISMATCH",
    "INSTANCE_REPO_IDENTITY_MISSING",
    "INSTANCE_REPO_IDENTITY_MISMATCH",
    "INSTANCE_REPO_IDENTITY_UNRESOLVED",
    "INSTANCE_HEAD_DRIFT",
    "INSTANCE_TREE_DRIFT",
    "INSTANCE_SCOPE_NOT_EXACT",
    "INSTANCE_SCOPE_NOT_SIGNED",
    "INSTANCE_DEMO_SCOPE_OVERLAP",
    "INSTANCE_PREIMAGE_NOT_ABSENT",
    "INSTANCE_POSTIMAGE_MISSING",
    "INSTANCE_POSTIMAGE_MISMATCH",
    "INSTANCE_PATHS_OUTSIDE_WRITESET",
    "INSTANCE_PATH_TOO_LONG",
    "INSTANCE_WORKTREE_NOT_CLEAN",
    "INSTANCE_TTL_EXPIRED",
    "INSTANCE_OPS_EXCEEDED",
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
        _need(len(entry["relpath"]) <= MAX_RELPATH, "INSTANCE_PATH_TOO_LONG",
              {"relpath": entry["relpath"], "chars": len(entry["relpath"]), "max": MAX_RELPATH})
    paths = [e["relpath"] for e in ws]
    _need(len(set(paths)) == len(paths), "INSTANCE_CONTRACT_INCOMPLETE", "duplicate relpath")
    # An instance that shares a path with another operation's authorised scope would silently
    # inherit that authorisation, so it is an invalid contract row rather than a bad request:
    # it fails here, at load, not later when a caller happens to pass the right arguments.
    _need(not demo_scope_overlap(contract, row), "INSTANCE_DEMO_SCOPE_OVERLAP",
          demo_scope_overlap(contract, row))
    return row


def demo_scope_overlap(contract: Mapping[str, Any], instance: Mapping[str, Any]) -> List[str]:
    """Instance paths that fall inside another operation's declared scope.

    Sharing a path with the demo operation would silently inherit its authorisation; that is the
    widening this design refuses to perform, so an overlap is a refusal and not a warning.
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


# --------------------------------------------------------------------------- identity

_REMOTE_RE = re.compile(
    r"^(?:https?://[^/]+/|git@[^:]+:|ssh://git@[^/]+/)(?P<path>[^\s]+?)(?:\.git)?/?$")


def full_name_from_remote_url(url: str) -> str:
    """``shw097-team/FHS_vNEXT`` from any of the three remote URL forms git accepts.

    Raising rather than returning "" is deliberate: a caller that cannot resolve an identity must
    fail closed, not compare against an empty string that any repository satisfies.
    """
    _need(isinstance(url, str) and url.strip(), "INSTANCE_REPO_IDENTITY_UNRESOLVED", "empty remote url")
    match = _REMOTE_RE.match(url.strip())
    if match is None:
        raise InstanceRefused("INSTANCE_REPO_IDENTITY_UNRESOLVED", {"url": url})
    path = match.group("path").strip("/")
    parts = [p for p in path.split("/") if p]
    _need(len(parts) >= 2, "INSTANCE_REPO_IDENTITY_UNRESOLVED", {"url": url, "parts": parts})
    return "/".join(parts[-2:])


def check_identity(instance: Mapping[str, Any], *, observed_full_name: str) -> Dict[str, Any]:
    """The repository identity must be resolved from the repository, not asserted by the caller."""
    _need(observed_full_name, "INSTANCE_REPO_IDENTITY_UNRESOLVED", "no observed full name")
    declared = instance["repo"]["full_name"]
    _need(observed_full_name == declared, "INSTANCE_REPO_IDENTITY_MISMATCH",
          {"declared": declared, "observed": observed_full_name})
    return {"full_name": declared, "id": instance["repo"]["id"]}


# --------------------------------------------------------------------------- design check

def evaluate(
    contract: Mapping[str, Any],
    instance_id: str,
    repo_state: Mapping[str, Any],
    *,
    observed: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    """Design-level resolution: is this the operation that was described?

    Tolerant on purpose: identity may be supplied, postimages may be withheld. The write path uses
    ``evaluate_write`` instead, which requires both.
    """
    _need(contract.get("schema") == "SBL.OperationRegistry.Binding@2", "INSTANCE_CONTRACT_INCOMPLETE",
          "contract schema")
    instance = find_instance(contract, instance_id)
    repo = instance["repo"]

    _need(isinstance(repo_state, Mapping) and repo_state.get("head"), "INSTANCE_CONTRACT_INCOMPLETE",
          "repo_state is not a probe observation")
    _need(instance["write_set"] and repo_state.get("write_scope") is not None,
          "INSTANCE_CONTRACT_INCOMPLETE", "repo_state.write_scope missing")

    _need(repo_state.get("repo_id") in (None, repo["id"]) and
          repo_state.get("full_name") in (None, repo["full_name"]),
          "INSTANCE_REPO_IDENTITY_MISMATCH",
          {"declared": {"id": repo["id"], "full_name": repo["full_name"]},
           "observed": {"id": repo_state.get("repo_id"), "full_name": repo_state.get("full_name")}})

    _need(repo_state["head"] == repo["head_at_bind"], "INSTANCE_HEAD_DRIFT",
          {"declared": repo["head_at_bind"], "observed": repo_state["head"]})

    declared_paths = [e["relpath"] for e in instance["write_set"]]
    observed_scope = list(repo_state.get("write_scope") or [])
    _need(set(observed_scope) == set(declared_paths), "INSTANCE_SCOPE_NOT_EXACT",
          {"declared": sorted(declared_paths), "observed": sorted(observed_scope)})

    preimages = repo_state.get("preimages") or {}
    for entry in instance["write_set"]:
        seen = preimages.get(entry["relpath"])
        if entry["preimage"] == "ABSENT":
            _need(seen == "ABSENT", "INSTANCE_PREIMAGE_NOT_ABSENT",
                  {"relpath": entry["relpath"], "observed": seen})
        else:
            _need(seen == entry["preimage"], "INSTANCE_PREIMAGE_NOT_ABSENT",
                  {"relpath": entry["relpath"], "observed": seen, "declared": entry["preimage"]})

    # worktree hygiene belongs to the design check too: a design review that ignores a dirty tree
    # is reviewing a tree that is not the one described. The write path re-checks this as
    # "nothing outside the write set", which is the stricter form.
    _need(not repo_state.get("dirty"), "INSTANCE_WORKTREE_NOT_CLEAN",
          {"status_sha256": repo_state.get("status_sha256")})
    untracked = repo_state.get("untracked_files")
    if isinstance(untracked, Sequence) and not isinstance(untracked, (str, bytes)):
        stray = sorted(set(untracked) - set(declared_paths))
        _need(not stray, "INSTANCE_WORKTREE_NOT_CLEAN", {"untracked_outside_scope": stray})

    if observed is not None:
        for entry in instance["write_set"]:
            got = observed.get(entry["relpath"])
            _need(got == entry["postimage_sha256"], "INSTANCE_CONTRACT_INCOMPLETE",
                  {"relpath": entry["relpath"], "declared": entry["postimage_sha256"], "observed": got})

    return _record(instance, contract, repo_state["head"], repo_state.get("repo_id"),
                   repo_state.get("full_name"))


def _record(instance: Mapping[str, Any], contract: Mapping[str, Any], head: str,
            repo_id: Any = None, full_name: Any = None) -> Dict[str, Any]:
    repo = instance["repo"]
    return {
        "schema": INSTANCE_SCHEMA,
        "instance_id": instance["instance_id"],
        "operation_type": instance["operation_type"],
        "effect_class": instance["effect_class"],
        "repo": {"id": repo_id if repo_id is not None else repo["id"],
                 "full_name": full_name or repo["full_name"], "head": head,
                 "tree": repo.get("tree_at_bind")},
        "write_set": [{"relpath": e["relpath"], "change": e["change"],
                       "preimage": e["preimage"], "postimage_sha256": e["postimage_sha256"]}
                      for e in instance["write_set"]],
        "effect_state": "EFFECT_UNBOUND",
        "grant_state": "NOT_GRANTED",
        "registry_authority": contract.get("authority_state"),
        "claim_ceiling": CLAIM_CEILING,
        "admitted": False,
    }


# --------------------------------------------------------------------------- write check

def evaluate_write(
    contract: Mapping[str, Any],
    instance_id: str,
    *,
    signed_contract_sha256: str,
    contract_sha256: str,
    repo_state: Mapping[str, Any],
    observed: Mapping[str, str],
    changed_paths: Sequence[str] = (),
    signed_scope: Iterable[str],
    ttl_remaining_s: Optional[float] = None,
    ops_requested: int = 1,
) -> Dict[str, Any]:
    """Strict resolution for the moment before a write.

    Every parameter the design check treats as optional is mandatory here, because this is the
    function a writer calls: a missing postimage, an unresolved identity or an unsigned path must
    stop the write rather than fall back to the tolerant path.
    """
    instance = find_instance(contract, instance_id)
    repo = instance["repo"]

    # 1. the signed object must be the object being evaluated
    _need(contract_sha256 == signed_contract_sha256, "INSTANCE_CONTRACT_SHA_MISMATCH",
          {"evaluated": contract_sha256, "signed": signed_contract_sha256})

    # 2. repository identity: present, and independently resolved
    _need(repo_state.get("repo_id") is not None and repo_state.get("full_name"),
          "INSTANCE_REPO_IDENTITY_MISSING",
          {"id": repo_state.get("repo_id"), "full_name": repo_state.get("full_name")})
    _need(repo_state["repo_id"] == repo["id"], "INSTANCE_REPO_IDENTITY_MISMATCH",
          {"declared": repo["id"], "observed": repo_state["repo_id"]})
    check_identity(instance, observed_full_name=repo_state["full_name"])

    # 3. head and tree
    _need(repo_state.get("head") == repo["head_at_bind"], "INSTANCE_HEAD_DRIFT",
          {"declared": repo["head_at_bind"], "observed": repo_state.get("head")})
    _need(repo_state.get("tree") == repo["tree_at_bind"], "INSTANCE_TREE_DRIFT",
          {"declared": repo["tree_at_bind"], "observed": repo_state.get("tree")})

    # 4. scope: the write set, the request, and the SIGNED scope must be the same set
    declared = [e["relpath"] for e in instance["write_set"]]
    _need(set(repo_state.get("write_scope") or []) == set(declared), "INSTANCE_SCOPE_NOT_EXACT",
          {"declared": sorted(declared), "observed": sorted(repo_state.get("write_scope") or [])})
    ok, extra, missing = _scope_compare(declared, signed_scope)
    _need(ok, "INSTANCE_SCOPE_NOT_SIGNED",
          {"extra_in_signature": extra, "missing_from_signature": missing})

    # 5. nothing outside the write set may be touched
    stray = sorted(set(changed_paths) - set(declared))
    _need(not stray, "INSTANCE_PATHS_OUTSIDE_WRITESET", stray)

    # 6. preimage at the bound head, and the exact bytes about to be written
    preimages = repo_state.get("preimages") or {}
    for entry in instance["write_set"]:
        if entry["preimage"] == "ABSENT":
            _need(preimages.get(entry["relpath"]) == "ABSENT", "INSTANCE_PREIMAGE_NOT_ABSENT",
                  {"relpath": entry["relpath"], "observed": preimages.get(entry["relpath"])})
        else:
            _need(preimages.get(entry["relpath"]) == entry["preimage"], "INSTANCE_PREIMAGE_NOT_ABSENT",
                  {"relpath": entry["relpath"], "observed": preimages.get(entry["relpath"])})
        got = observed.get(entry["relpath"])
        _need(got, "INSTANCE_POSTIMAGE_MISSING", {"relpath": entry["relpath"]})
        _need(got == entry["postimage_sha256"], "INSTANCE_POSTIMAGE_MISMATCH",
              {"relpath": entry["relpath"], "declared": entry["postimage_sha256"], "observed": got})

    # 7. budget
    ttl = instance.get("ttl_seconds")
    if ttl is not None:
        _need(ttl_remaining_s is not None and 0 < float(ttl_remaining_s) <= float(ttl),
              "INSTANCE_TTL_EXPIRED", {"remaining_s": ttl_remaining_s, "ttl_s": ttl})
    max_ops = instance.get("max_ops")
    if max_ops is not None:
        _need(int(ops_requested) <= int(max_ops), "INSTANCE_OPS_EXCEEDED",
              {"requested": ops_requested, "max_ops": max_ops})

    out = _record(instance, contract, repo_state["head"], repo_state.get("repo_id"),
                  repo_state.get("full_name"))
    out["gate"] = "WRITE_GATE_PASSED_NOT_A_PERMIT"
    out["signed_contract_sha256"] = signed_contract_sha256
    out["changed_paths"] = sorted(set(changed_paths))
    return out


def _scope_compare(declared: Sequence[str], signed: Iterable[str]) -> Tuple[bool, List[str], List[str]]:
    signed_set = set(signed or [])
    declared_set = set(declared)
    extra = sorted(signed_set - declared_set)
    missing = sorted(declared_set - signed_set)
    return (not extra and not missing, extra, missing)


# --------------------------------------------------------------------------- signed scope

def ratified_scope_covers(contract: Mapping[str, Any], instance_id: str,
                          ratified_scope: Iterable[str]) -> Tuple[bool, List[str]]:
    """Does the owner's signed scope name every instance path? (superset test, kept for r3 use)"""
    instance = find_instance(contract, instance_id)
    signed = set(ratified_scope or [])
    missing = sorted({e["relpath"] for e in instance["write_set"]} - signed)
    return (not missing, missing)


def ratified_scope_exactly_matches(contract: Mapping[str, Any], instance_id: str,
                                   ratified_scope: Iterable[str]) -> Tuple[bool, List[str], List[str]]:
    """Equality, not containment.

    A signature that covers *more* than the write set authorises paths the writer never measured;
    one that covers *less* authorises a write it never saw. Both are refusals here, which is what
    "the signed scope must equal the write set" has to mean to be worth anything.
    """
    instance = find_instance(contract, instance_id)
    return _scope_compare([e["relpath"] for e in instance["write_set"]], ratified_scope)


def instance_digest(contract: Mapping[str, Any], instance_id: str) -> str:
    """Stable digest of one instance, for a decision reference to quote."""
    instance = find_instance(contract, instance_id)
    body = json.dumps(instance, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(body)
