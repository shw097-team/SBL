"""Tranche A: a small, PURE per-round role-binding validator.

This is deliberately NOT a new control plane and NOT a new store. The binding is carried by the
EXISTING ``TaskSpec.permissions_json`` column (the ExecutionBinding carrier that already exists),
under a single explicit ``role_binding`` key. Nothing here opens a database, spawns a process, reads
credentials, or signs itself: the validator only raises a typed, fail-closed error when the persisted
records and the caller's claimed identity do not line up, and returns a derived selection otherwise.

Honest scope: an opt-in binding primitive is a PRE-DISPATCH ELIGIBILITY check. On its own it does not
prove that any role executed, nor that a model was served. Completed-role evidence is tranche B/D
(``SharedSpine.record_workorder_result`` consuming an exact evidence bundle); real request telemetry
is tranche C and, until then, an unknown served identity stays UNKNOWN/refused rather than assumed.

The ``role_binding`` document shape (all fields explicit, no defaults that could vouch for nothing)::

    {
      "schema": "HGK-ROLE-BINDING/1",
      "round": "<round>",
      "session": "<session>",
      "workorder": "<WO-...>",
      "base_head": "<sha>",
      "subject": "<subject id>",
      "scope": ["<path>", ...],
      "expiry": "2026-10-15T18:00:18.067022+00:00",
      "mandate_digest": "sha256:<hex>",
      "roles": {
        "EXECUTE":        {"provider","model","surface","rank","reasoning_effort"},
        "VERIFY_SECURITY":{"provider","model","surface","rank","reasoning_effort"},
        "PLAN":           {"provider","model","surface","rank","reasoning_effort"}
      }
    }
"""
from __future__ import annotations

import json
import hashlib
from datetime import UTC, datetime
from typing import Any, Mapping

from .errors import InvariantViolation
from .util import sha256_text


ROLE_BINDING_SCHEMA = "HGK-ROLE-BINDING/1"
ROLE_BINDING_KEY = "role_binding"

# The scalar/collection fields every binding must state explicitly to mean anything. An absent one is
# a typed refusal, never a default that could let an empty document pass.
REQUIRED_BINDING_FIELDS = (
    "schema",
    "round",
    "session",
    "workorder",
    "base_head",
    "subject",
    "expiry",
    "mandate_digest",
)

ROLE_REQUIRED_FIELDS = ("provider", "model", "surface", "rank")

# The exact canonical states a bound dispatch's spine rows must be in. A WO whose Requirement is not
# FROZEN, whose TaskSpec is not ADMITTED, or whose WorkOrder is not CREATED is not an admitted
# binding carrier and must be refused -- never accepted because the caller asserted it.
REQUIRED_REQUIREMENT_STATE = "FROZEN"
REQUIRED_TASKSPEC_STATE = "ADMITTED"
REQUIRED_WORKORDER_STATE = "CREATED"
CANONICAL_LOADER_SCHEMA = "HGK-ROLE-BINDING-CANONICAL/1"


class BindingError(InvariantViolation):
    """A typed role-binding refusal.

    Subclasses :class:`InvariantViolation` so an existing ``except InvariantViolation`` at a call site
    keeps working, while carrying the precise, actionable ``code`` for a governed caller.
    """

    def __init__(self, code: str, detail: Any = None) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}:{detail}" if detail is not None else code)


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def extract_binding(permissions: Any, *, require_present: bool = False) -> dict[str, Any] | None:
    """Return the raw ``role_binding`` document carried by a TaskSpec ``permissions`` mapping.

    ``permissions`` is the parsed ``permissions_json`` object. Legacy, non-governed rows simply have no
    ``role_binding`` key: they return ``None`` (unchanged legacy behaviour) unless ``require_present``
    is set, which is what a governed/opt-in path passes.
    """
    if permissions is None:
        if require_present:
            raise BindingError("ERR_ROLE_BINDING_MISSING", "permissions_json is absent")
        return None
    if not isinstance(permissions, Mapping):
        raise BindingError("ERR_ROLE_BINDING_PERMISSIONS_NOT_OBJECT", type(permissions).__name__)
    raw = permissions.get(ROLE_BINDING_KEY)
    if raw is None:
        if require_present:
            raise BindingError("ERR_ROLE_BINDING_MISSING", f"no {ROLE_BINDING_KEY!r} in permissions_json")
        return None
    if not isinstance(raw, Mapping):
        raise BindingError("ERR_ROLE_BINDING_NOT_OBJECT", type(raw).__name__)
    return dict(raw)


def binding_digest(binding: Mapping[str, Any]) -> str:
    """Stable digest of the binding document (for the receipt / mandate cross-check)."""
    from .util import canonical_json

    return sha256_text(canonical_json(dict(binding)))


def load_canonical_binding(spine: Any, workorder_id: Any) -> dict[str, Any]:
    """READ-ONLY canonical loader: join the EXACT Requirement/TaskSpec/WorkOrder rows for
    ``workorder_id`` out of an OPEN Shared Spine and return the persisted ``role_binding`` document.

    This is the source of authority a bound dispatch reads. The caller OPENS the spine (production
    callers pass the canonical root constant; unit tests may inject a throwaway temp SharedSpine);
    this module itself opens no database, reads no file, and never treats a caller-supplied file as
    authority.

    Fail-closed (typed) on: an unusable/missing spine, a blank/unknown workorder id, a Requirement
    whose state is not FROZEN, a TaskSpec whose state is not ADMITTED, a WorkOrder whose state is not
    CREATED, or a TaskSpec whose ``permissions_json`` carries no ``role_binding`` document.
    """
    if spine is None:
        raise BindingError("ERR_ROLE_BINDING_CANONICAL_SPINE", "no SharedSpine supplied")
    if not _nonempty_str(workorder_id):
        raise BindingError("ERR_ROLE_BINDING_WORKORDER_REQUIRED", repr(workorder_id))
    connection_cm = spine.connect()
    with connection_cm as connection:
        row = connection.execute(
            """SELECT w.workorder_id, w.writer, w.worktree, w.base_head, w.state AS workorder_state,
                      t.taskspec_id, t.state AS taskspec_state, t.permissions_json,
                      r.requirement_id, r.state AS requirement_state
                 FROM workorders w
                 JOIN taskspecs t ON t.taskspec_id = w.taskspec_id
                 JOIN requirements r ON r.requirement_id = t.requirement_id
                WHERE w.workorder_id = ?""",
            (str(workorder_id),),
        ).fetchone()
    if row is None:
        raise BindingError("ERR_ROLE_BINDING_WORKORDER_UNKNOWN", str(workorder_id))
    if row["requirement_state"] != REQUIRED_REQUIREMENT_STATE:
        raise BindingError("ERR_ROLE_BINDING_REQUIREMENT_NOT_FROZEN",
                           f"{row['requirement_id']}={row['requirement_state']}")
    if row["taskspec_state"] != REQUIRED_TASKSPEC_STATE:
        raise BindingError("ERR_ROLE_BINDING_TASKSPEC_NOT_ADMITTED",
                           f"{row['taskspec_id']}={row['taskspec_state']}")
    if row["workorder_state"] != REQUIRED_WORKORDER_STATE:
        raise BindingError("ERR_ROLE_BINDING_WORKORDER_NOT_CREATED",
                           f"{row['workorder_id']}={row['workorder_state']}")
    try:
        permissions = json.loads(row["permissions_json"])
    except (json.JSONDecodeError, TypeError) as exc:
        raise BindingError("ERR_ROLE_BINDING_PERMISSIONS_NOT_OBJECT",
                           f"{row['taskspec_id']}:{exc}") from exc
    binding = extract_binding(permissions, require_present=True)
    return {
        "schema": CANONICAL_LOADER_SCHEMA,
        "workorder": str(row["workorder_id"]),
        "taskspec": str(row["taskspec_id"]),
        "requirement": str(row["requirement_id"]),
        "writer": str(row["writer"]),
        "worktree": str(row["worktree"]),
        "base_head": str(row["base_head"]),
        "states": {"requirement": row["requirement_state"],
                   "taskspec": row["taskspec_state"],
                   "workorder": row["workorder_state"]},
        "binding": binding,
        "binding_digest": binding_digest(binding),
        "scope": list(binding.get("scope") or []),
    }


def find_session_binding(spine: Any, session_id: Any) -> dict[str, Any] | None:
    """READ-ONLY session-keyed lookup: return the ACTIVE governed binding for ``session_id``.

    The guard payload carries a ``session_id`` but no role/round, so a governed runtime controller
    must resolve the session's binding itself. This joins the SAME rows ``load_canonical_binding``
    uses (Requirement FROZEN, TaskSpec ADMITTED, WorkOrder CREATED) and selects the one whose
    persisted ``role_binding["session"]`` equals ``session_id``.

    Fail-closed (typed) on: a missing/unusable spine, or a blank session id. An unbound/ordinary
    session (no live admitted row carries it) is NOT an error: it returns ``None``. Exactly one live
    match returns ``{"workorder": <id>, "binding": <binding doc>}``. MORE THAN ONE live match is a
    typed refusal -- ambiguity is never a silent pick. Like the rest of the module this opens no
    database of its own and reads no file: it only queries the caller-supplied OPEN spine.
    """
    if spine is None:
        raise BindingError("ERR_ROLE_BINDING_CANONICAL_SPINE", "no SharedSpine supplied")
    if not _nonempty_str(session_id):
        raise BindingError("ERR_ROLE_BINDING_SESSION_REQUIRED", repr(session_id))
    wanted = str(session_id)
    connection_cm = spine.connect()
    with connection_cm as connection:
        rows = connection.execute(
            """SELECT w.workorder_id, w.writer, w.worktree, w.base_head, w.state AS workorder_state,
                      t.taskspec_id, t.state AS taskspec_state, t.permissions_json,
                      r.requirement_id, r.state AS requirement_state
                 FROM workorders w
                 JOIN taskspecs t ON t.taskspec_id = w.taskspec_id
                 JOIN requirements r ON r.requirement_id = t.requirement_id
                WHERE r.state = ? AND t.state = ? AND w.state = ?""",
            (REQUIRED_REQUIREMENT_STATE, REQUIRED_TASKSPEC_STATE, REQUIRED_WORKORDER_STATE),
        ).fetchall()
    matches: list[tuple[Any, dict[str, Any]]] = []
    for row in rows:
        try:
            permissions = json.loads(row["permissions_json"])
        except (json.JSONDecodeError, TypeError):
            # A row whose permissions_json is not an object cannot carry a governed binding.
            continue
        binding = extract_binding(permissions)
        if binding is None or str(binding.get("session")) != wanted:
            continue
        matches.append((row, binding))
    if not matches:
        return None
    if len(matches) > 1:
        raise BindingError("ERR_ROLE_BINDING_AMBIGUOUS_SESSION",
                           sorted(str(row["workorder_id"]) for row, _ in matches))
    row, binding = matches[0]
    return {"workorder": str(row["workorder_id"]), "binding": binding}


def require_projection_matches(persisted_binding: Mapping[str, Any], supplied_binding: Any) -> str:
    """A supplied FILE is ONLY a projection of the native persisted binding.

    If a caller hands in a binding document (e.g. via a ``--binding``/``--role-binding-file`` flag),
    it is NEVER the source of authority: it must be byte-for-byte the same document as the one read
    back from the admitted spine, or it is refused. A projection that adds, drops, or edits any field
    changes its canonical digest and is a typed refusal -- so a hand-written file can neither widen
    nor narrow the persisted selection.
    """
    if not isinstance(supplied_binding, Mapping):
        raise BindingError("ERR_ROLE_BINDING_PROJECTION_NOT_OBJECT", type(supplied_binding).__name__)
    native = binding_digest(persisted_binding)
    projected = binding_digest(supplied_binding)
    if native != projected:
        raise BindingError("ERR_ROLE_BINDING_PROJECTION_MISMATCH",
                           {"native": native, "supplied": projected})
    return projected


def _parse_expiry(value: Any) -> datetime:
    if not _nonempty_str(value):
        raise BindingError("ERR_ROLE_BINDING_EXPIRY_INVALID", repr(value))
    text = value.strip()
    # accept a trailing Z as UTC
    iso = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(iso)
    except ValueError as exc:  # pragma: no cover - defensive
        raise BindingError("ERR_ROLE_BINDING_EXPIRY_INVALID", f"{value!r}:{exc}") from exc
    if parsed.tzinfo is None:
        raise BindingError("ERR_ROLE_BINDING_EXPIRY_INVALID", f"{value!r} has no timezone")
    return parsed.astimezone(UTC)


def resolve_arm(binding: Mapping[str, Any], lane: str) -> dict[str, Any]:
    """Derive the required arm (provider/model/surface/rank/effort) for ``lane`` from the binding.

    One source of truth: the dispatcher resolves BOTH the required arm and the required rank from the
    SAME persisted binding, so an outer check on arm A can never pair with an inner run on arm B.
    """
    if not isinstance(binding, Mapping):
        raise BindingError("ERR_ROLE_BINDING_NOT_OBJECT", type(binding).__name__)
    roles = binding.get("roles")
    if not isinstance(roles, Mapping) or not roles:
        raise BindingError("ERR_ROLE_BINDING_ROLES_MISSING", repr(roles))
    role = roles.get(lane)
    if not isinstance(role, Mapping):
        raise BindingError("ERR_ROLE_BINDING_LANE_UNDECLARED", lane)
    for field in ROLE_REQUIRED_FIELDS:
        if field == "rank":
            rank = role.get("rank")
            if isinstance(rank, bool) or not isinstance(rank, int):
                raise BindingError("ERR_ROLE_BINDING_ROLE_FIELD_INVALID", f"{lane}.rank={rank!r}")
        elif not _nonempty_str(role.get(field)):
            raise BindingError("ERR_ROLE_BINDING_ROLE_FIELD_INVALID", f"{lane}.{field}={role.get(field)!r}")
    return {
        "provider": str(role["provider"]),
        "model": str(role["model"]),
        "surface": str(role["surface"]),
        "rank": int(role["rank"]),
        "reasoning_effort": role.get("reasoning_effort"),
        "arm": f"{role['provider']}/{role['model']}",
    }


def validate_binding(
    binding: Mapping[str, Any] | None,
    *,
    session: Any = None,
    round: Any = None,
    workorder_id: Any = None,
    subject: Any = None,
    base_head: Any = None,
    scope: Any = None,
    lane: Any = None,
    surface: Any = None,
    provider: Any = None,
    model: Any = None,
    effort: Any = None,
    mandate_digest: Any = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Fail-closed validation of a binding against a caller-claimed identity.

    Every argument is optional so that a caller may check only what it knows; every argument it DOES
    provide must match exactly. A ``None`` binding, or one missing any mandatory field, is a refusal --
    there is no empty-input pass. Returns the resolved binding doc plus its digest on success.
    """
    if binding is None:
        raise BindingError("ERR_ROLE_BINDING_MISSING", "no binding supplied")
    if not isinstance(binding, Mapping):
        raise BindingError("ERR_ROLE_BINDING_NOT_OBJECT", type(binding).__name__)
    for field in REQUIRED_BINDING_FIELDS:
        value = binding.get(field)
        if field == "schema":
            if value != ROLE_BINDING_SCHEMA:
                raise BindingError("ERR_ROLE_BINDING_SCHEMA", f"expected {ROLE_BINDING_SCHEMA!r} got {value!r}")
        elif not _nonempty_str(value):
            raise BindingError(f"ERR_ROLE_BINDING_FIELD_MISSING:{field}", repr(value))
    scope_value = binding.get("scope")
    if not isinstance(scope_value, list) or not scope_value or not all(_nonempty_str(s) for s in scope_value):
        raise BindingError("ERR_ROLE_BINDING_SCOPE_EMPTY", repr(scope_value))

    current = (now or datetime.now(UTC)).astimezone(UTC)
    if _parse_expiry(binding["expiry"]) <= current:
        raise BindingError("ERR_ROLE_BINDING_EXPIRED", binding["expiry"])

    # Cross-check the claimed identity. Each provided field must match exactly; a mismatch is typed.
    checks = (
        ("session", session, "ERR_ROLE_BINDING_SESSION_MISMATCH"),
        ("round", round, "ERR_ROLE_BINDING_ROUND_MISMATCH"),
        ("workorder", workorder_id, "ERR_ROLE_BINDING_WORKORDER_MISMATCH"),
        ("subject", subject, "ERR_ROLE_BINDING_SUBJECT_MISMATCH"),
        ("base_head", base_head, "ERR_ROLE_BINDING_BASE_MISMATCH"),
    )
    for field, claimed, code in checks:
        if claimed is not None and str(claimed) != str(binding[field]):
            raise BindingError(code, f"claimed {claimed!r} != binding {binding[field]!r}")

    if mandate_digest is not None and str(mandate_digest) != str(binding["mandate_digest"]):
        raise BindingError("ERR_ROLE_BINDING_MANDATE_MISMATCH", f"{mandate_digest!r}")

    if lane is not None:
        arm = resolve_arm(binding, str(lane))
        for claimed, actual, code in (
            (surface, arm["surface"], "ERR_ROLE_BINDING_SURFACE_MISMATCH"),
            (provider, arm["provider"], "ERR_ROLE_BINDING_PROVIDER_MISMATCH"),
            (model, arm["model"], "ERR_ROLE_BINDING_MODEL_MISMATCH"),
        ):
            if claimed is not None and str(claimed) != str(actual):
                raise BindingError(code, f"claimed {claimed!r} != binding {actual!r}")
        declared_effort = arm.get("reasoning_effort")
        if effort is not None and declared_effort is not None and str(effort) != str(declared_effort):
            raise BindingError("ERR_ROLE_BINDING_EFFORT_MISMATCH", f"claimed {effort!r} != {declared_effort!r}")
        if scope is not None:
            wanted = scope if isinstance(scope, (list, tuple)) else [scope]
            missing = [s for s in wanted if str(s) not in {str(x) for x in scope_value}]
            if missing:
                raise BindingError("ERR_ROLE_BINDING_SCOPE_MISMATCH", f"outside declared scope: {missing}")

    return {"binding": dict(binding), "binding_digest": binding_digest(binding)}


EVIDENCE_REQUIRED_FIELDS = (
    "workorder",
    "session",
    "round",
    "subject",
    "mandate_digest",
    "role",
    "surface",
    "artifact_digest",
    "checker_identity",
    "guard",
)


def validate_role_evidence(
    binding: Mapping[str, Any],
    evidence: Mapping[str, Any] | None,
    *,
    role: str,
    writer: Any = None,
) -> dict[str, Any]:
    """Tranche B: verify an EXACT completed-role evidence bundle bound to a persisted binding.

    A ``VERIFIED`` result may only be recorded from this. It refuses (typed) on any of:
      * a missing/foreign/replayed receipt (the bundle's own WO/session/round/subject/mandate digest
        must equal the persisted binding's -- a receipt for another WO or a replayed one cannot pass);
      * a missing CLI surface (the bundle surface must equal the role's declared surface);
      * a missing delivery (a nonempty substantive output artifact digest is mandatory);
      * a changed subject;
      * a lens-receipt that was not actually a successful lane turn;
      * a non-independent checker (checker identity equal to the writer);
      * a guard that is not CLEAN.
    It is a PURE function: it reads no file. Digest-of-file verification is the caller's job (the
    dispatcher/checker writes the raw refs); here we require the refs to be nonempty and exact.
    """
    if evidence is None:
        raise BindingError("ERR_ROLE_EVIDENCE_MISSING", "a bound workorder cannot be verified without evidence")
    if not isinstance(evidence, Mapping):
        raise BindingError("ERR_ROLE_EVIDENCE_NOT_OBJECT", type(evidence).__name__)
    arm = resolve_arm(binding, role)

    for field in EVIDENCE_REQUIRED_FIELDS:
        value = evidence.get(field)
        if not _nonempty_str(value):
            raise BindingError(f"ERR_ROLE_EVIDENCE_FIELD_MISSING:{field}", repr(value))

    # Exact binding to the persisted record -- this is what makes a FOREIGN or REPLAYED receipt refuse.
    for field, code in (
        ("workorder", "ERR_ROLE_EVIDENCE_WORKORDER_MISMATCH"),
        ("session", "ERR_ROLE_EVIDENCE_SESSION_MISMATCH"),
        ("round", "ERR_ROLE_EVIDENCE_ROUND_MISMATCH"),
        ("subject", "ERR_ROLE_EVIDENCE_SUBJECT_MISMATCH"),
        ("mandate_digest", "ERR_ROLE_EVIDENCE_MANDATE_MISMATCH"),
    ):
        if str(evidence[field]) != str(binding[field]):
            raise BindingError(code, f"evidence {field}={evidence[field]!r} != binding {binding[field]!r}")

    # The completed role is the checker role, and its surface must be exactly the declared surface.
    if str(evidence["role"]) != role:
        raise BindingError("ERR_ROLE_EVIDENCE_ROLE_MISMATCH", f"{evidence['role']!r} != {role!r}")
    if str(evidence["surface"]) != arm["surface"]:
        raise BindingError("ERR_ROLE_EVIDENCE_SURFACE_MISMATCH",
                           f"{evidence['surface']!r} != declared {arm['surface']!r}")

    # An ACTUAL successful lane receipt, with its raw log refs and digests, must be present.
    receipt = evidence.get("lane_receipt")
    if not isinstance(receipt, Mapping):
        raise BindingError("ERR_ROLE_EVIDENCE_NO_LANE_RECEIPT", repr(receipt))
    if receipt.get("ok") is not True:
        raise BindingError("ERR_ROLE_EVIDENCE_LANE_NOT_SERVED", repr(receipt.get("code")))
    for field in ("receipt_path", "receipt_digest"):
        if not _nonempty_str(receipt.get(field)):
            raise BindingError(f"ERR_ROLE_EVIDENCE_RECEIPT_{field.upper()}_MISSING", repr(receipt.get(field)))
    served = receipt.get("served_arm") or receipt.get("arm")
    if _nonempty_str(served) and str(served) != arm["arm"]:
        raise BindingError("ERR_ROLE_EVIDENCE_SERVED_ARM_MISMATCH", f"{served!r} != {arm['arm']!r}")

    log_refs = evidence.get("log_refs")
    if not isinstance(log_refs, list) or not log_refs:
        raise BindingError("ERR_ROLE_EVIDENCE_NO_LOG_REFS", repr(log_refs))
    for ref in log_refs:
        if not isinstance(ref, Mapping) or not _nonempty_str(ref.get("path")) or not _nonempty_str(ref.get("sha256")):
            raise BindingError("ERR_ROLE_EVIDENCE_LOG_REF_INVALID", repr(ref))

    if not _nonempty_str(evidence.get("artifact_digest")):
        raise BindingError("ERR_ROLE_EVIDENCE_NO_DELIVERY", "substantive output artifact digest required")

    # Independent checker + a CLEAN guard.
    if writer is not None and str(evidence["checker_identity"]) == str(writer):
        raise BindingError("ERR_ROLE_EVIDENCE_CHECKER_NOT_INDEPENDENT", str(writer))
    if str(evidence["guard"]) != "CLEAN":
        raise BindingError("ERR_ROLE_EVIDENCE_GUARD_NOT_CLEAN", str(evidence["guard"]))

    return {"role": role, "arm": arm["arm"], "surface": arm["surface"],
            "artifact_digest": str(evidence["artifact_digest"]),
            "checker_identity": str(evidence["checker_identity"]),
            "receipt_digest": str(receipt["receipt_digest"])}


_HEX64 = set("0123456789abcdefABCDEF")


def verify_completion_evidence(
    *,
    raw_stdout: bytes,
    deliverable_bytes: bytes | None,
    deliverable_digest_hex: str | None,
    binding: Mapping[str, Any],
) -> None | str:
    """Tranche D2a: can a lane turn be called COMPLETE from *real* evidence?

    Returns ``None`` ONLY when every check passes; otherwise returns a named refusal string. It is a
    PURE, fail-closed function: it reads no file and spawns nothing -- the caller supplies the captured
    raw stdout, the deliverable bytes, and the recorder's claimed digest.

    The FAR finding this closes: a matching usage receipt is NOT work. A nonce/receipt echoed into
    ``raw_stdout`` with a ZERO-length (or absent) deliverable must NOT be allowed to complete a turn,
    so a receipt in raw is insufficient on its own and an empty deliverable is an explicit refusal.

    Rules, in order (first failure wins):
      * ``raw_stdout`` must be non-empty -- a receipt/nonce in raw does not by itself prove work;
      * ``deliverable_bytes`` must be present and non-empty -> ``ERR_COMPLETION_NO_DELIVERABLE``;
      * ``deliverable_digest_hex`` must be a non-blank 64-hex string -> ``ERR_COMPLETION_DIGEST_MISSING``;
      * sha256(deliverable_bytes) must equal ``deliverable_digest_hex`` -> ``ERR_COMPLETION_DIGEST_MISMATCH``;
      * ``binding`` must carry non-empty workorder/session/subject -> ``ERR_COMPLETION_BINDING_INCOMPLETE``.
    """
    if not raw_stdout:
        return "ERR_COMPLETION_NO_RAW_STDOUT"
    if deliverable_bytes is None or len(deliverable_bytes) == 0:
        return "ERR_COMPLETION_NO_DELIVERABLE"
    if not _nonempty_str(deliverable_digest_hex):
        return "ERR_COMPLETION_DIGEST_MISSING"
    claimed = deliverable_digest_hex.strip()
    if len(claimed) != 64 or any(ch not in _HEX64 for ch in claimed):
        return "ERR_COMPLETION_DIGEST_MISSING"
    actual = hashlib.sha256(deliverable_bytes).hexdigest()
    if actual.lower() != claimed.lower():
        return "ERR_COMPLETION_DIGEST_MISMATCH"
    if not isinstance(binding, Mapping):
        return "ERR_COMPLETION_BINDING_INCOMPLETE"
    for field in ("workorder", "session", "subject"):
        if not _nonempty_str(binding.get(field)):
            return "ERR_COMPLETION_BINDING_INCOMPLETE"
    return None
