"""HGK SP identity — resolve one SP identity and build the PRE-SPAWN identity block.

Round: R13 follow-through, deviation D-06 ("Commander/Challenge adapter"). R13 honestly recorded the
writer/checker as LANE_ONLY: the two arms were really executed, but nothing in the dispatch carried an
SP identity, so "lane" and "SP" were the same thing with two names. This module is the adapter that
makes them different: the dispatcher resolves the identity BEFORE it spawns anything, digest-pins the
procedure it is loading, injects the identity (and the invocation id) into the child prompt, and then
the ordinary nonce oracle proves the child actually saw it.

What this is, and what it is not (stated so the receipt cannot be read past its evidence):

  * IS     an identity bound pre-spawn: sp_id + procedure path + procedure sha256 + invocation id,
           each read from disk / from the Shared Spine, never supplied by the prompt author.
  * IS     a fail-closed gate: an unknown identity, a lane the identity is not bound to, an unusable
           procedure file, a nonce that is not the invocation id, or a chain that cannot be read all
           refuse BEFORE the spawn, each with its own typed code and zero attempts.
  * IS NOT a native SP binary, a host installation, a Permit or an acceptance signature. The skill
           package itself ships `claim_ceiling: HOST_PENDING`; a lane turn carrying this identity
           inherits that ceiling and never exceeds it.

Design note (why the invocation id is also the nonce): the dispatcher already has one oracle for "the
child really received this text" — the nonce must appear inside an assistant message. Rather than add
a second, weaker echo check, the gate REQUIRES `--nonce == --sp-invocation-id`, so the existing oracle
is what certifies the identity block. A mismatch is a typed refusal, not a silent downgrade.

Lane binding is in the registry, not in the caller: `challenge` is bound to VERIFY_SECURITY and
`commander` to PLAN, so a Challenge-SP can never be dispatched as an EXECUTE writer through this path.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import uuid
from pathlib import Path

SCHEMA = "HGK-SP-IDENTITY/1"
CLAIM_CEILING = (
    "SP_INVOKED_PRESPAWN: the identity was resolved from disk, digest-pinned and injected into the "
    "child prompt BEFORE the spawn, and the run's nonce (== invocation id) proves the child received "
    "it. It is a skill-loaded identity carried by a Codex lane turn: not a host-installed SP binary, "
    "it issues no Permit/ECP and signs no acceptance."
)

ERR_SP_IDENTITY_UNKNOWN = "ERR_SP_IDENTITY_UNKNOWN"
ERR_SP_IDENTITY_LANE_MISMATCH = "ERR_SP_IDENTITY_LANE_MISMATCH"
ERR_SP_IDENTITY_SKILL_UNUSABLE = "ERR_SP_IDENTITY_SKILL_UNUSABLE"
ERR_SP_IDENTITY_INVOCATION_ID_MALFORMED = "ERR_SP_IDENTITY_INVOCATION_ID_MALFORMED"
ERR_SP_IDENTITY_NONCE_MISMATCH = "ERR_SP_IDENTITY_NONCE_MISMATCH"
ERR_SP_IDENTITY_CHAIN_UNAVAILABLE = "ERR_SP_IDENTITY_CHAIN_UNAVAILABLE"
ERR_SP_IDENTITY_WORKORDER_UNKNOWN = "ERR_SP_IDENTITY_WORKORDER_UNKNOWN"

# The registry is the AUTHORITY for lane binding and procedure location; a caller may pick an entry,
# never redefine one. `commander` is declared here so the registry is complete for both D-06 halves;
# this task wires (and tests) the `challenge`/VERIFY side.
REGISTRY: dict[str, dict] = {
    "challenge": {
        "sp_id": "SBL-ACCEPTANCE-CHALLENGE-SP",
        "skill_relpath": "external-challenge-sp/SKILL.md",
        "lane": "VERIFY_SECURITY",
        "invocation_tag": "CHALLENGE",
        "role": ("independent challenge of a frozen candidate: findings that carry evidence; read-only "
                 "by construction, so any repair you feel like making is a finding, not an edit"),
    },
    "commander": {
        "sp_id": "SBL-COMMANDER-SP",
        "skill_relpath": "commander-sp/SKILL.md",
        "lane": "PLAN",
        "invocation_tag": "COMMANDER",
        "role": "bounded proposal from source to TaskSpec/WorkOrder: propose, never admit, never sign",
    },
}

INVOCATION_ID_RE = re.compile(r"^SPINV-(CHALLENGE|COMMANDER)-[0-9a-f]{12}$")


def new_invocation_id(name: str) -> str:
    """Caller-side mint. Format is validated on the dispatcher side, so a malformed id never reaches a spawn."""
    spec = REGISTRY.get(name)
    if spec is None:
        raise ValueError(f"{ERR_SP_IDENTITY_UNKNOWN}: {name!r}")
    return f"SPINV-{spec['invocation_tag']}-{uuid.uuid4().hex[:12]}"


def default_skills_root() -> Path | None:
    """Where the SP skill packages live on this host.

    Ordered: explicit override -> the Hermes home this session is running under -> the packaged default.
    The first root whose challenge procedure exists wins, so a session that sets HERMES_HOME is not
    silently reading another profile's copy.
    """
    candidates: list[Path] = []
    if os.environ.get("HERMES_SKILLS_ROOT"):
        candidates.append(Path(os.environ["HERMES_SKILLS_ROOT"]))
    if os.environ.get("HERMES_HOME"):
        candidates.append(Path(os.environ["HERMES_HOME"]) / "skills" / "sbl")
    candidates.append(Path.home() / "AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0"
                       / "LocalCache/Local/hermes/skills/sbl")
    for cand in candidates:
        if (cand / REGISTRY["challenge"]["skill_relpath"]).is_file():
            return cand
    return candidates[0] if candidates else None


def read_chain(spine, workorder: str) -> dict:
    """Read the native chain for one WorkOrder from the Shared Spine (read-only).

    Every field here is EVIDENCE read back from the control plane; none is supplied by a caller or by
    a prompt author. The values that reach the identity block are id-shaped only (ids, a git head, a
    digest, states) — no free-form spine prose is ever copied into a prompt.
    """
    path = Path(spine)
    if not path.is_file():
        raise LookupError(f"{ERR_SP_IDENTITY_CHAIN_UNAVAILABLE}: spine not readable at {path}")
    try:
        con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        try:
            row = con.execute(
                "SELECT w.workorder_id, w.taskspec_id, w.state AS workorder_state, w.base_head, "
                "w.writer, w.rollback_pointer, t.state AS taskspec_state, t.requirement_id, "
                "t.permissions_json "
                "FROM workorders w JOIN taskspecs t ON t.taskspec_id = w.taskspec_id "
                "WHERE w.workorder_id = ?", (workorder,)).fetchone()
        finally:
            con.close()
    except sqlite3.Error as exc:  # a damaged/unreadable spine is a typed refusal, never a traceback
        raise LookupError(f"{ERR_SP_IDENTITY_CHAIN_UNAVAILABLE}: {type(exc).__name__}: {exc}") from exc
    if row is None:
        raise LookupError(f"{ERR_SP_IDENTITY_WORKORDER_UNKNOWN}: {workorder}")
    perms = json.loads(row["permissions_json"] or "{}")
    binding = perms.get("role_binding") if isinstance(perms, dict) else None
    return {
        "workorder_id": row["workorder_id"],
        "taskspec_id": row["taskspec_id"],
        "workorder_state": row["workorder_state"],
        "taskspec_state": row["taskspec_state"],
        "base_head": row["base_head"],
        "writer": row["writer"],
        "rollback_pointer": row["rollback_pointer"],
        "requirement_id": row["requirement_id"],
        "spine_binding_present": bool(binding),
        "spine_binding_digest": ("sha256:" + hashlib.sha256(
            json.dumps(binding, sort_keys=True).encode()).hexdigest()) if binding else None,
    }


def resolve_identity(name, *, skills_root=None, lane=None, nonce=None, invocation_id=None,
                     spine=None, workorder=None) -> dict:
    """Resolve one SP identity for a pre-spawn gate.

    Returns {"ok": bool, "code": str|None, "detail": str|None, "identity": {...}}. On failure the
    caller must REFUSE before spawning; `identity` still carries whatever was measured (so the
    refusal receipt says which half failed), and never a block to inject.
    """
    if not name:
        return {"ok": False, "code": ERR_SP_IDENTITY_UNKNOWN, "detail": "no identity named",
                "identity": {"ok": False}}
    name = str(name)
    spec = REGISTRY.get(name)
    if spec is None:
        known = ", ".join(sorted(REGISTRY))
        return {"ok": False, "code": ERR_SP_IDENTITY_UNKNOWN,
                "detail": f"{name!r} is not an SP identity (known: {known})",
                "identity": {"ok": False, "sp": name, "code": ERR_SP_IDENTITY_UNKNOWN}}

    identity: dict = {"schema": SCHEMA, "ok": True, "sp": name, "sp_id": spec["sp_id"],
                      "bound_lane": spec["lane"], "requested_lane": lane,
                      "role": spec["role"], "claim_ceiling": CLAIM_CEILING,
                      "issued_permit": False, "signed_acceptance": False}

    # 1. the identity must be bound to the lane it is being dispatched on.
    if lane is not None and lane != spec["lane"]:
        return {"ok": False, "code": ERR_SP_IDENTITY_LANE_MISMATCH,
                "detail": f"{spec['sp_id']} is bound to lane {spec['lane']}, not {lane}",
                "identity": dict(identity, ok=False, code=ERR_SP_IDENTITY_LANE_MISMATCH)}

    # 2. the invocation id names this identity, is well formed, and IS this run's nonce.
    if not invocation_id:
        return {"ok": False, "code": ERR_SP_IDENTITY_INVOCATION_ID_MALFORMED,
                "detail": "an SP dispatch must name --sp-invocation-id (mint one per invocation)",
                "identity": dict(identity, ok=False, code=ERR_SP_IDENTITY_INVOCATION_ID_MALFORMED)}
    m = INVOCATION_ID_RE.match(str(invocation_id))
    if not m:
        return {"ok": False, "code": ERR_SP_IDENTITY_INVOCATION_ID_MALFORMED,
                "detail": f"{invocation_id!r} does not match SPINV-<TAG>-<12 hex>",
                "identity": dict(identity, ok=False, code=ERR_SP_IDENTITY_INVOCATION_ID_MALFORMED)}
    if m.group(1) != spec["invocation_tag"]:
        return {"ok": False, "code": ERR_SP_IDENTITY_INVOCATION_ID_MALFORMED,
                "detail": f"{invocation_id} names {m.group(1)} but identity {name!r} is "
                          f"{spec['invocation_tag']}",
                "identity": dict(identity, ok=False, code=ERR_SP_IDENTITY_INVOCATION_ID_MALFORMED)}
    if nonce != invocation_id:
        return {"ok": False, "code": ERR_SP_IDENTITY_NONCE_MISMATCH,
                "detail": f"--nonce {nonce!r} is not the invocation id {invocation_id}; without that "
                          f"binding the existing nonce oracle cannot certify the identity block",
                "identity": dict(identity, ok=False, code=ERR_SP_IDENTITY_NONCE_MISMATCH,
                                 invocation_id=invocation_id, nonce=nonce)}
    identity["invocation_id"] = str(invocation_id)

    # 3. the procedure must resolve on disk, non-empty, at the registry's own relative path.
    root = Path(skills_root) if skills_root else default_skills_root()
    if root is None:
        return {"ok": False, "code": ERR_SP_IDENTITY_SKILL_UNUSABLE,
                "detail": "no skills root could be resolved (set --sp-skills-root or HERMES_HOME)",
                "identity": dict(identity, ok=False, code=ERR_SP_IDENTITY_SKILL_UNUSABLE)}
    skill = root / spec["skill_relpath"]
    identity["skills_root"] = str(root)
    identity["skill_path"] = str(skill)
    if not skill.is_file():
        return {"ok": False, "code": ERR_SP_IDENTITY_SKILL_UNUSABLE,
                "detail": f"procedure not found: {skill}",
                "identity": dict(identity, ok=False, code=ERR_SP_IDENTITY_SKILL_UNUSABLE)}
    raw = skill.read_bytes()
    if not raw.strip():
        return {"ok": False, "code": ERR_SP_IDENTITY_SKILL_UNUSABLE,
                "detail": f"procedure is empty: {skill}",
                "identity": dict(identity, ok=False, code=ERR_SP_IDENTITY_SKILL_UNUSABLE)}
    identity["skill_sha256"] = hashlib.sha256(raw).hexdigest()
    identity["skill_bytes"] = len(raw)

    # 4. optional chain join: ids read back from the Shared Spine, never from the prompt author.
    if workorder:
        identity["chain_source"] = str(spine) if spine else None
        try:
            identity["chain"] = read_chain(spine, str(workorder))
        except LookupError as exc:
            code, _, detail = str(exc).partition(": ")
            return {"ok": False, "code": code or ERR_SP_IDENTITY_CHAIN_UNAVAILABLE, "detail": detail,
                    "identity": dict(identity, ok=False, code=code or ERR_SP_IDENTITY_CHAIN_UNAVAILABLE,
                                     workorder=str(workorder))}
        identity["chain_workorder"] = str(workorder)

    identity["ok"] = True
    return {"ok": True, "code": None, "detail": None, "identity": identity}


def build_block(identity: dict) -> str:
    """The text prepended to the lane prompt at pre-spawn.

    Machine-generated from the resolved identity + id-shaped chain fields only: no caller prose, no
    free-form spine text, so nothing in the block is a channel for text the gate did not measure.
    """
    lines = [
        "=== HGK SP IDENTITY (injected at pre-spawn, not authored by this prompt) ===",
        f"sp_id            : {identity['sp_id']}",
        f"identity         : {identity['sp']}  (registry-bound lane: {identity['bound_lane']})",
        f"procedure        : {identity['skill_path']}",
        f"procedure_sha256 : {identity['skill_sha256']}",
        f"invocation_id    : {identity['invocation_id']}",
        f"claim_ceiling    : {identity['claim_ceiling']}",
        "your function   : " + identity["role"],
        "you issue no Permit, no ECP and no acceptance signature; HGK issues, you review.",
    ]
    chain = identity.get("chain")
    if chain:
        lines += [
            "native chain (read back from the Shared Spine before this spawn):",
            f"  workorder_id   = {chain['workorder_id']}  (state {chain['workorder_state']})",
            f"  taskspec_id    = {chain['taskspec_id']}  (state {chain['taskspec_state']})",
            f"  requirement_id = {chain['requirement_id']}",
            f"  base_head      = {chain['base_head']}",
            f"  rollback       = {chain['rollback_pointer']}",
        ]
        if chain.get("spine_binding_digest"):
            lines.append(f"  binding_digest = {chain['spine_binding_digest']}")
    lines += [
        "output contract: your FIRST line must be the invocation id; if a chain is given, echo",
        "workorder_id, taskspec_id and binding_digest on their own lines before your findings.",
        "=== end SP identity ===",
    ]
    return "\n".join(lines)
