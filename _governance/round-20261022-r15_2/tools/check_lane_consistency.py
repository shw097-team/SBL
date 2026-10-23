"""Offline three-lane consistency checker (W08).

One question, one answer: does every lane dispatch receipt show the arm the lane
declaration says that lane should be served by?

    python tools/check_lane_consistency.py
    python tools/check_lane_consistency.py --receipts-dir <dir> --declaration <file>

Exit codes: 0 every checked receipt is CONSISTENT or SUPERSEDED; 1 any VIOLATION or
NOT_GREEN; 2 usage/IO/parse error. Exactly one JSON object is printed on stdout.

Supersession (a rebind must not rewrite history)
-----------------------------------------------
A receipt's served arm is judged against the pool that was in force when the receipt
ran, not only against today's pool. A receipt is SUPERSEDED only when all three
facts hold: the served arm is absent from the current pool, the served arm IS
declared by a prior revision (`prior_arms`, loaded from `RETIRED_ARMS_R153.json`),
and the receipt predates the pool revision. Then the model/provider/rank predicates
are reported as historical rather than as live faults, and `superseded_by` names the
current rank-1 arm. A receipt that serves a retired arm but is dated at or after the
pool revision is still a VIOLATION -- the rebind only excuses turns taken before it.

An arm that no revision ever declared -- a hijacked model, a typo, a hand-edited
receipt -- is NOT history. It is a VIOLATION carrying the sub-reason
`UNAUTHORIZED_ARM`, however old its receipt claims to be. The same holds for an
unknown timestamp: a missing time cannot prove the receipt came first.

Time policy (a checker must not invent time)
--------------------------------------------
Each clock has exactly one admissible source, and every result names it:

* Receipt time, from the receipt body only: `generated_utc`, then
  `generated_at` / `at_utc` / `generated` / `created_utc` / `timestamp` /
  `useconds` (an epoch number is accepted when it is plausibly a timestamp). The
  receipt FILE's mtime is never substituted: an old file would otherwise buy a
  SUPERSEDED with no timestamp in the receipt at all. No parsable field means
  UNKNOWN, and UNKNOWN never buys SUPERSEDED (`receipt_time_source` records the
  field, or is null).
* Pool effective time, from the pool's own revision record: a top-level
  `effective_at`, else the `history[]` entry whose `revision`/`rev` matches the
  declaration's current `revision` (`at_utc` / `at` / `effective_at`). The
  declaration file's mtime is a last resort and is labelled
  `pool_time_source: "file_mtime"`; when that label is in force every SUPERSEDED
  verdict carries `superseded_confidence: "LOW"`, so the weakness is visible
  rather than flattering the result.
* Revision membership: an optional `prior_arms_by_revision` mapping
  (`{revision: [arms]}` or `{revision: {"arms": [...], "at_utc": ...}}`) lets a
  SUPERSEDED verdict require that the arm was declared by the revision in force
  at receipt time -- an arm authorised in revision A but dropped in B is a
  VIOLATION for a receipt issued during B. Without that mapping the RETIRED_ARMS
  list stays the floor and every SUPERSEDED verdict records
  `revision_membership: "UNAVAILABLE"`.

`classify_arm()` is the pure predicate that makes this decision, so it is
unit-testable with injected values.

Claim ceiling: the excuse rests on `RETIRED_ARMS_R153.json`, which is a curated list
of arms a prior revision declared. An arm missing from that list but genuinely
served by an older revision would read as UNAUTHORIZED_ARM until the list is
extended; that direction is deliberate -- the list fails closed, so an unknown arm
is never quietly excused as history.

Declaration derivation (deliberately explicit, because this drives a pass/fail)
-----------------------------------------------------------------------------
`hermes-codex-lane.json` is the sealed-lane binding; it carries no per-lane rank
table today. The table is therefore derived, in this order:

1. An explicit table wins: `lanes` (object keyed by lane, or a list of objects
   with a `lane` key), each lane holding `arms` / `ordered_pool` entries of
   `{rank, provider, model}` -- or a mapping of rank -> `{provider, model}`.
2. Otherwise the sealed-lane binding: `/provider` + `/model` are rank 1, and
   every entry of `<lane>_additional_routes` (e.g. `execute_additional_routes`)
   is the declared arm at the next rank, in list order.
3. The lane name comes from an explicit `/lane`, else from the sole lane token
   present among the top-level key names (`execute_*` -> EXECUTE, `plan_*` ->
   PLAN, `verify*` -> VERIFY_SECURITY).

Everything that is only prose in the declaration (for example `/sod_note`
claiming that all three lanes run one model) is NOT parsed into the table: a
sentence is not a binding. A receipt for a lane with no structural binding
fails `R1_lane_declared`, and the note quotes the prose claim so the gap is
visible instead of being silently smoothed over.

Also deliberately not softened:

* `/model_fallbacks` is not treated as selectable ranks. The declaration calls
  those arms fail-closed safety, and an automatic alternate list is not a rank.
* Reading this tool's output must not mutate anything: it is read-only.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

SCHEMA = "SBL-LANE-CONSISTENCY/1"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RECEIPTS_DIR = os.path.join(REPO_ROOT, "receipts", "dispatch")
DEFAULT_DECLARATION = "C:/Projects/Agent_Workspace/HG-KSEOS/config/hermes-codex-lane.json"

LANE_ORDER = ("PLAN", "EXECUTE", "VERIFY_SECURITY")
LANE_TOKENS = {
    "EXECUTE": ("execute_", "execute-", "exec_"),
    "PLAN": ("plan_", "plan-", "plan"),
    "VERIFY_SECURITY": ("verify_security", "verify"),
}

# The three outcomes of the arm predicate. "SUPERSEDED" is not a fault: it says the
# receipt was honest under a pool revision that has since been replaced.
CONSISTENT = "CONSISTENT"
SUPERSEDED = "SUPERSEDED"
VIOLATION = "VIOLATION"

# Sub-reason attached to a VIOLATION whose served arm no revision ever declared.
# Not a verdict: the verdict stays VIOLATION so the exit code does not move.
UNAUTHORIZED_ARM = "UNAUTHORIZED_ARM"

# The other two VIOLATION sub-reasons, kept distinct so the note says which fact
# failed rather than lumping every red arm together.
REASON_UNKNOWN_TIME = "UNKNOWN_RECEIPT_TIME"
REASON_AT_OR_AFTER_POOL = "AT_OR_AFTER_POOL_REVISION"

# The curated list of arms a PRIOR pool revision really declared. It sits next to
# this tool; retiring an arm means adding it here. Read-only: nothing writes it.
RETIRED_ARMS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "RETIRED_ARMS_R153.json"
)

# The only receipt fields allowed to supply a receipt time, in precedence order.
# The receipt file's mtime is deliberately absent: an old file must not become a
# timestamp the receipt never carried.
RECEIPT_TIME_FIELDS = (
    "generated_utc",
    "generated_at",
    "at_utc",
    "generated",
    "created_utc",
    "timestamp",
    "useconds",
)

# Where a pool's effective time came from. Only "file_mtime" is a fallback, and it
# is always labelled -- it is a weakness in the input, not something to smooth over.
POOL_TIME_REVISION_RECORD = "revision_record"
POOL_TIME_EFFECTIVE_AT = "effective_at"
POOL_TIME_FILE_MTIME = "file_mtime"
POOL_TIME_UNKNOWN = "unknown"

# Sub-reason for a served arm that a prior revision declared but the revision in
# force at receipt time did not: authorised once, but not for this turn.
REASON_ARM_NOT_IN_RECEIPT_REVISION = "ARM_NOT_IN_RECEIPT_REVISION"
# The pool time came from the file mtime, which anyone can move with one touch. A label is not a control,
# so this source may never grant the excuse - it can only ever produce a VIOLATION.
REASON_POOL_TIME_NOT_AUTHORITATIVE = "POOL_TIME_NOT_AUTHORITATIVE"
REASON_PROVIDER_NOT_RETIRED = "PROVIDER_NOT_RETIRED"
REASON_ARM_LABEL_PROVIDER_CONFLICT = "ARM_LABEL_PROVIDER_CONFLICT"

# B12 (2026-10-23): the provider guard was OPT-IN. A caller that omitted `prior_pairs` got the old, weaker rule, so
# the public classifier still excused an undeclared provider/model pair. A guard that must be switched on is not a
# guard: the default is now "load the evidence myself, and refuse if it cannot be loaded".
_EVIDENCE_UNSET = object()

# Recorded whenever no `prior_arms_by_revision` mapping could pin the membership.
REVISION_MEMBERSHIP_UNAVAILABLE = "UNAVAILABLE"

# Confidence attached to a SUPERSEDED verdict: LOW only because the pool time is
# an mtime proxy rather than the revision record.
CONFIDENCE_LOW = "LOW"
CONFIDENCE_HIGH = "HIGH"


class DeclarationUnusable(Exception):
    """The declaration parsed but carries no machine-readable lane binding."""


# --------------------------------------------------------------------------- #
# declaration -> {lane: {rank: arm}}
# --------------------------------------------------------------------------- #
def _as_rank(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _arm(entry: dict[str, Any], rank: int, source: str) -> dict[str, Any]:
    arm = {
        "rank": rank,
        "provider": entry.get("provider"),
        "model": entry.get("model"),
        "source": source,
        "notes": [],
    }
    if entry.get("transport_model"):
        arm["transport_model"] = entry["transport_model"]
    if entry.get("automatic_selection") is False:
        arm["explicit_only"] = True
        arm["notes"].append("declared explicit-only route (automatic_selection=false)")
    for key in ("admission_status", "usable_now", "authorization_basis"):
        if entry.get(key):
            arm["notes"].append(f"{key}={entry[key]}")
    return arm


def _arms_from_spec(spec: Any, source: str) -> dict[int, dict[str, Any]]:
    """Parse one lane spec into {rank: arm}. Unrecognised shapes yield {}."""
    arms: dict[int, dict[str, Any]] = {}

    if isinstance(spec, dict):
        entries = spec.get("arms") or spec.get("ordered_pool")
        if isinstance(entries, list):
            for index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    continue
                rank = _as_rank(entry.get("rank"))
                if rank is None:
                    rank = index + 1
                arms[rank] = _arm(entry, rank, source)
        elif entries is None:
            for key, entry in spec.items():
                rank = _as_rank(key)
                if rank is None or not isinstance(entry, dict):
                    continue
                arms[rank] = _arm(entry, rank, source)
    return arms


def _explicit_lane_table(decl: dict[str, Any]) -> dict[str, dict[int, dict[str, Any]]]:
    table: dict[str, dict[int, dict[str, Any]]] = {}
    lanes = decl.get("lanes")
    if isinstance(lanes, dict):
        for lane, spec in lanes.items():
            if isinstance(lane, str):
                arms = _arms_from_spec(spec, f"/lanes/{lane}")
                if arms:
                    table[lane] = arms
    elif isinstance(lanes, list):
        for index, spec in enumerate(lanes):
            if not isinstance(spec, dict):
                continue
            lane = spec.get("lane")
            if not isinstance(lane, str) or not lane:
                continue
            arms = _arms_from_spec(spec, f"/lanes/{index}")
            if arms:
                table[lane] = arms
    return table


def _sealed_lane_name(decl: dict[str, Any]) -> str | None:
    explicit = decl.get("lane")
    if isinstance(explicit, str) and explicit:
        return explicit
    keys = [k.lower() for k in decl if isinstance(k, str)]
    found = {
        lane
        for lane, tokens in LANE_TOKENS.items()
        if any(key.startswith(token) for key in keys for token in tokens)
    }
    # len==1 keeps this a derivation rather than a guess.
    return found.pop() if len(found) == 1 else None


def _sealed_lane_table(decl: dict[str, Any]) -> dict[str, dict[int, dict[str, Any]]]:
    provider = decl.get("provider")
    model = decl.get("model")
    if not (isinstance(provider, str) and provider.strip()):
        raise DeclarationUnusable("no structural lane binding: /provider is absent")
    if not (isinstance(model, str) and model.strip()):
        raise DeclarationUnusable("no structural lane binding: /model is absent")
    lane = _sealed_lane_name(decl)
    if not lane:
        raise DeclarationUnusable(
            "no structural lane binding: cannot name the sealed lane (no /lane, and the "
            "top-level keys name zero or several lanes)"
        )

    primary = {"provider": provider, "model": model}
    arms: dict[int, dict[str, Any]] = {1: _arm(primary, 1, "/provider + /model")}

    prefix = lane.lower()
    routes = decl.get(f"{prefix}_additional_routes") or decl.get(f"{prefix}_routes")
    if isinstance(routes, list):
        for offset, route in enumerate(routes):
            if not isinstance(route, dict):
                continue
            rank = 2 + offset
            arms[rank] = _arm(route, rank, f"/{prefix}_additional_routes/{offset}")
    return {lane: arms}


def build_lane_table(decl: dict[str, Any]) -> dict[str, dict[int, dict[str, Any]]]:
    """Return {lane: {rank: arm}} derived from the declaration."""
    table = _explicit_lane_table(decl)
    if not table:
        table = _sealed_lane_table(decl)
    for lane, arms in table.items():
        for rank, arm in arms.items():
            if not isinstance(arm.get("provider"), str) or not arm["provider"].strip():
                raise DeclarationUnusable(f"{lane} rank {rank}: declared provider is absent")
            if not isinstance(arm.get("model"), str) or not arm["model"].strip():
                raise DeclarationUnusable(f"{lane} rank {rank}: declared model is absent")
    return table


def _prose_lane_claims(decl: dict[str, Any], lane: str) -> list[str]:
    """Strings that *mention* the lane, quoted for the note. Never parsed as a binding."""
    claims: list[str] = []
    for key, value in decl.items():
        if isinstance(value, str) and lane in value.upper():
            claims.append(f"/{key}")
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str) and lane in sub_value.upper():
                    claims.append(f"/{key}/{sub_key}")
                if isinstance(sub_value, list):
                    for index, item in enumerate(sub_value):
                        if isinstance(item, str) and lane in item.upper():
                            claims.append(f"/{key}/{sub_key}/{index}")
    return claims


# --------------------------------------------------------------------------- #
# predicates
# --------------------------------------------------------------------------- #
def _provider_ok(value: Any, declared: str) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    seen = value.strip().lower()
    want = declared.strip().lower()
    if seen == want:
        return True
    # Documented alias: the GPT arm is served either as openai-codex or as a
    # per-account openai-p* provider id.
    if want == "openai-codex":
        return seen.startswith("openai-p")
    return False


def _bare_model(value: Any) -> str | None:
    """The model part of any identity label: `provider/model` and `model` reduce to the same bare name.

    B11 (2026-10-23): R3 compared `usage_model` against `transport_model` and stopped there, so a receipt whose two
    secondary fields both said NEVER-DECLARED-MODEL was self-consistent and bought an excuse for a retired arm. Two
    fields agreeing with each other is not evidence that either equals the arm actually claimed.
    """
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    if not text:
        return None
    return text.split("/", 1)[1] if "/" in text else text


def _strip_provider_prefix(model: Any, provider: Any) -> Any:
    """`opencode-go/deepseek-v4.1-flash` and `deepseek-v4.1-flash` are one arm."""
    if not isinstance(model, str):
        return model
    text = model.strip()
    if isinstance(provider, str) and provider.strip():
        prefix = provider.strip().lower() + "/"
        if text.lower().startswith(prefix):
            return text[len(prefix):]
    return text


def _predicate(pid: str, ok: bool, rank: Any, note: str) -> dict[str, Any]:
    return {"id": pid, "ok": bool(ok), "rank": rank, "note": note}


def _normalise_arm(value: Any) -> str | None:
    """A comparable arm label, or None when there is no usable value."""
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    return text or None


def _parse_stamp(value: Any) -> datetime | None:
    """ISO-8601 string (or datetime) -> aware UTC datetime; None stays None.

    None, "" and anything unparsable return None. A naive stamp is read as UTC,
    because every receipt in this workspace writes UTC.
    """
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        text = value.strip()
        if text.endswith(("Z", "z")):
            text = text[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


# A plausible epoch window (2001-01-01 .. 2100-01-01). Anything outside it is a
# duration or a counters value, not a timestamp, so it is rejected rather than
# turned into a 1970 date that would silently predate every pool.
_EPOCH_FLOOR = 978307200.0
_EPOCH_CEILING = 4102444800.0


def _stamp_from_number(value: Any) -> datetime | None:
    """Epoch seconds or microseconds -> aware UTC datetime; else None."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    seconds = number / 1_000_000.0 if number > 1e11 else number
    if not (_EPOCH_FLOOR <= seconds <= _EPOCH_CEILING):
        return None
    return datetime.fromtimestamp(seconds, timezone.utc)


def _to_stamp(value: Any) -> datetime | None:
    """Any admissible stamp form -> aware UTC datetime; unparsable -> None."""
    stamp = _parse_stamp(value)
    if stamp is not None:
        return stamp
    if isinstance(value, str) and value.strip().isdigit():
        return _stamp_from_number(int(value.strip()))
    return _stamp_from_number(value)


def receipt_time_from_receipt(receipt: dict[str, Any]) -> tuple[str | None, str | None]:
    """(iso stamp, field name) read ONLY from the receipt body.

    The receipt file's mtime is never a substitute: a checker that accepts it
    lets an old file buy SUPERSEDED while the receipt itself carries no time at
    all. An unparsable or absent field returns (None, None) -- UNKNOWN.
    """
    for field in RECEIPT_TIME_FIELDS:
        if field not in receipt:
            continue
        stamp = _to_stamp(receipt.get(field))
        if stamp is not None:
            return stamp.astimezone(timezone.utc).isoformat(), field
    return None, None


def _decl_revision(decl: dict[str, Any]) -> Any:
    for key in ("revision", "rev", "pool_revision", "revision_id"):
        value = decl.get(key)
        if value is not None and not isinstance(value, (dict, list)):
            return value
    return None


def _history_stamp(entry: dict[str, Any]) -> datetime | None:
    """The first usable time on a history/revision record."""
    for key in ("at_utc", "at", "effective_at", "effective_utc", "at_date"):
        if key in entry:
            stamp = _to_stamp(entry.get(key))
            if stamp is not None:
                return stamp
    return None


def resolve_pool_time(decl: dict[str, Any], declaration_path: str) -> tuple[str | None, str]:
    """(iso stamp, source) -- the pool's OWN effective time.

    Order: a top-level `effective_at`, then the `history[]` entry matching the
    current `revision`, then the declaration file's mtime. The mtime is only a
    labelled fallback (`pool_time_source: "file_mtime"`), never an equal claim:
    touching the pool file later must not retroactively excuse receipts.
    """
    for key in ("effective_at", "effective_utc"):
        if key in decl:
            stamp = _to_stamp(decl.get(key))
            if stamp is not None:
                return stamp.isoformat(), POOL_TIME_EFFECTIVE_AT

    revision = _decl_revision(decl)
    history = decl.get("history")
    if revision is not None and isinstance(history, list):
        wanted = str(revision).strip()
        for entry in history:
            if not isinstance(entry, dict):
                continue
            for key in ("revision", "rev"):
                if key in entry and str(entry[key]).strip() == wanted:
                    stamp = _history_stamp(entry)
                    if stamp is not None:
                        return stamp.isoformat(), POOL_TIME_REVISION_RECORD

    try:
        stamp = datetime.fromtimestamp(os.path.getmtime(declaration_path), timezone.utc)
    except OSError:
        return None, POOL_TIME_UNKNOWN
    return stamp.isoformat(), POOL_TIME_FILE_MTIME


def _arm_labels(entries: Any) -> set[str]:
    """Normalised labels (bare and `provider/model`) from a revision's arm entries."""
    labels: set[str] = set()
    if isinstance(entries, (str, bytes)):
        entries = [entries]
    if not isinstance(entries, (list, tuple, set)):
        return labels
    for entry in entries:
        if isinstance(entry, dict):
            provider = entry.get("provider")
            model = entry.get("model") or entry.get("arm")
            candidates: list[Any] = [model]
            if isinstance(provider, str) and provider.strip() and model:
                candidates.append(f"{provider}/{model}")
            for candidate in candidates:
                key = _normalise_arm(candidate)
                if key:
                    labels.add(key)
            continue
        key = _normalise_arm(entry)
        if key:
            labels.add(key)
    return labels


def _revision_records(prior_arms_by_revision: Any) -> list[dict[str, Any]]:
    """Normalise a `{revision: arms}` mapping into ordered records.

    A value may be a plain list of arm labels (no time, so it can never pin the
    revision in force) or an object carrying `arms`/`ordered_pool` plus
    `at_utc`/`at`/`effective_at`. Records with no arms are dropped rather than
    treated as "empty revision", because an empty list would claim knowledge it
    does not have.
    """
    records: list[dict[str, Any]] = []
    if not isinstance(prior_arms_by_revision, dict):
        return records
    for raw_key, value in prior_arms_by_revision.items():
        if isinstance(value, dict):
            entries = value.get("arms")
            if entries is None:
                entries = value.get("ordered_pool")
            labels = _arm_labels(entries)
            stamp = _history_stamp(value)
        else:
            labels = _arm_labels(value)
            stamp = None
        if not labels:
            continue
        records.append({"revision": str(raw_key), "stamp": stamp, "labels": labels})
    return records


def _revision_in_force(
    records: list[dict[str, Any]], receipt_stamp: datetime | None
) -> dict[str, Any] | None:
    """The stamped revision latest at or before the receipt, or None if unknowable."""
    if receipt_stamp is None:
        return None
    stamped = [record for record in records if record["stamp"] is not None]
    if not stamped:
        return None
    eligible = [record for record in stamped if record["stamp"] <= receipt_stamp]
    if not eligible:
        return None
    return max(eligible, key=lambda record: record["stamp"])


def revision_membership(
    served: Any, receipt_time: Any, prior_arms_by_revision: Any
) -> str:
    """`"UNAVAILABLE"`, or `"<revision>:PRESENT|ABSENT"` for the revision in force.

    UNAVAILABLE is recorded, not hidden: it says the verdict rests on the
    RETIRED_ARMS floor alone, which is weaker evidence than a revision record.
    """
    records = _revision_records(prior_arms_by_revision)
    if not records:
        return REVISION_MEMBERSHIP_UNAVAILABLE
    in_force = _revision_in_force(records, _to_stamp(receipt_time))
    if in_force is None:
        return REVISION_MEMBERSHIP_UNAVAILABLE
    state = "PRESENT" if _normalise_arm(served) in in_force["labels"] else "ABSENT"
    return f"{in_force['revision']}:{state}"


def _arm_keys(arms: Any) -> set[str]:
    """Normalised labels from any iterable of arm labels (or a single string)."""
    if isinstance(arms, (str, bytes)):
        arms = [arms]
    keys: set[str] = set()
    for entry in arms or ():
        key = _normalise_arm(entry)
        if key:
            keys.add(key)
    return keys


def classify_arm_with_reason(
    served: Any,
    pool_arms: Any,
    receipt_time: Any,
    pool_time: Any,
    prior_arms: Any = None,
    prior_arms_by_revision: Any = None,
    allow_supersession: bool = True,
    served_provider: Any = None,
) -> tuple[str, str | None]:
    """Public rule. The retired-arm PAIR EVIDENCE is not a parameter any more.

    B13 (2026-10-23): a caller could pass `prior_pairs={}` or `None` and the provider guard simply vanished - the seventh
    shape of the same defect. Evidence that a security decision depends on must not be injectable by the caller: this
    loads it from the declared list itself and refuses when the list cannot be read.
    """
    pairs, problem = load_prior_pairs_checked()
    if problem:
        return VIOLATION, REASON_POOL_TIME_NOT_AUTHORITATIVE
    return _classify_impl(
        served, pool_arms, receipt_time, pool_time, prior_arms, prior_arms_by_revision,
        allow_supersession=allow_supersession, served_provider=served_provider, prior_pairs=pairs,
    )


def _classify_impl(
    served: Any,
    pool_arms: Any,
    receipt_time: Any,
    pool_time: Any,
    prior_arms: Any = None,
    prior_arms_by_revision: Any = None,
    allow_supersession: bool = True,
    served_provider: Any = None,
    prior_pairs: Any = _EVIDENCE_UNSET,
) -> tuple[str, str | None]:
    """Judge one served arm: returns (verdict, sub_reason).

    Pure: no IO, no clock, no globals. `pool_arms` and `prior_arms` are any
    iterables of arm labels (bare model or `provider/model`; the caller passes
    both forms so an alias cannot masquerade as a rebind). Matching is exact on
    the normalised label.

    `prior_arms` is the only evidence that an arm the current pool no longer
    serves was ever authorized. A served arm absent from the pool is SUPERSEDED
    only when it IS in `prior_arms` AND the receipt is strictly older than the
    pool revision. Absent from both lists is a VIOLATION with sub-reason
    UNAUTHORIZED_ARM, whatever the timestamp says: an arm no revision declared
    was never authorized, so it cannot be history. An unknown time (None or
    unparsable) never buys the excuse either, because a missing timestamp cannot
    prove the receipt came first.

    `prior_arms_by_revision` is the optional membership map. When it pins the
    revision in force at receipt time, a SUPERSEDED verdict additionally requires
    that revision to declare the arm: an arm authorised in revision A but absent
    in B is not excused for a receipt issued during B (sub-reason
    ARM_NOT_IN_RECEIPT_REVISION). When it is absent or cannot pin a revision, the
    `prior_arms` floor decides and the caller records the membership as
    UNAVAILABLE -- the excuse is still granted, but it says what it rests on.

    The verdict stays one of CONSISTENT / SUPERSEDED / VIOLATION; the reason is a
    sub-reason of VIOLATION, never a fourth verdict.
    """
    if prior_pairs is _EVIDENCE_UNSET:
        prior_pairs, _pair_problem = load_prior_pairs_checked()
        if _pair_problem:
            # Cannot check the provider half of the identity -> nobody gets an excuse.
            allow_supersession = False
            prior_pairs = {}
    served_key = _normalise_arm(served)
    # A receipt may record the arm provider-qualified ("opencode-go/minimax-...") or bare. Measured 2026-10-23 (checker
    # finding, qualified label): keying the retired-pair map by the bare model meant the qualified form missed it and an
    # undeclared provider rode a retired model to SUPERSEDED. Both forms are resolved to one bare key here.
    served_bare = served_key.split("/", 1)[1] if (served_key and "/" in served_key) else served_key
    served_prefix = served_key.split("/", 1)[0] if (served_key and "/" in served_key) else None
    # B9 (2026-10-23): stripping the prefix to one bare key let a receipt label itself `evil-provider/minimax-...`
    # while its provider field said `opencode-go`. The prefix is a claim about the provider, so when both exist they
    # must agree - otherwise the label is forging the arm's identity and nothing about it may be excused.
    _prov_norm = _normalise_arm(served_provider)
    if served_prefix and _prov_norm and served_prefix != _prov_norm:
        return VIOLATION, REASON_ARM_LABEL_PROVIDER_CONFLICT
    if served_prefix and not _prov_norm:
        _prov_norm = served_prefix   # the label is the only provider statement the receipt made
    if served_key is not None and (served_key in _arm_keys(pool_arms) or served_bare in _arm_keys(pool_arms)):
        return CONSISTENT, None

    # No declared predecessor, no history to appeal to. This branch is what
    # closes the hole: an arm in neither list is VIOLATION even when very old.
    _prior_keys = _arm_keys(prior_arms)
    if served_key is None or (served_key not in _prior_keys and served_bare not in _prior_keys):
        return VIOLATION, UNAUTHORIZED_ARM

    served_stamp = _parse_stamp(receipt_time)
    pool_stamp = _parse_stamp(pool_time)
    if served_stamp is None or pool_stamp is None:
        return VIOLATION, REASON_UNKNOWN_TIME
    if served_stamp >= pool_stamp:
        return VIOLATION, REASON_AT_OR_AFTER_POOL

    # Older than the pool is necessary, not sufficient: the arm must also have
    # been declared by the revision that was in force when the receipt ran. A
    # retired arm that was already gone by then is a violation, not history.
    if not allow_supersession:
        # The pool effective time came from a file mtime. Anyone can move it, so it cannot acquit anyone:
        # a LOW-confidence label on a SUPERSEDED verdict was a label on an open hole (checker finding
        # MTIME_LABEL_ONLY, 2026-10-23).
        return VIOLATION, REASON_POOL_TIME_NOT_AUTHORITATIVE

    if isinstance(prior_pairs, dict) and prior_pairs:
        _providers = prior_pairs.get(str(served_bare).lower())
        _prov = _prov_norm
        if _providers and _prov and _prov.lower() not in _providers:
            # A retired MODEL does not authorise an undeclared PROVIDER: the pair was declared, so the pair is what
            # the excuse needs. Models the list does not know keep the pre-existing path (the bare-label floor).
            return VIOLATION, REASON_PROVIDER_NOT_RETIRED

    membership = revision_membership(served_key, receipt_time, prior_arms_by_revision)
    if membership != REVISION_MEMBERSHIP_UNAVAILABLE and membership.endswith(":ABSENT"):
        return VIOLATION, REASON_ARM_NOT_IN_RECEIPT_REVISION
    return SUPERSEDED, None


def classify_arm(
    served: Any,
    pool_arms: Any,
    receipt_time: Any,
    pool_time: Any,
    prior_arms: Any = None,
    prior_arms_by_revision: Any = None,
    allow_supersession: bool = True,
    served_provider: Any = None,
) -> str:
    """Judge one served arm against the pool: CONSISTENT / SUPERSEDED / VIOLATION.

    The verdict alone; `classify_arm_with_reason()` carries the sub-reason. See
    that function for the rule.
    """
    return classify_arm_with_reason(
        served, pool_arms, receipt_time, pool_time, prior_arms, prior_arms_by_revision,
        allow_supersession=allow_supersession, served_provider=served_provider,
    )[0]


def _evaluate_receipt(
    path: str,
    receipt: dict[str, Any],
    table: dict[str, dict[int, dict[str, Any]]],
    decl: dict[str, Any],
    pool_time: Any = None,
    prior_arms: Any = None,
    pool_time_source: str = POOL_TIME_UNKNOWN,
    prior_arms_by_revision: Any = None,
) -> dict[str, Any]:
    lane = receipt.get("lane")
    lane_key = lane.strip() if isinstance(lane, str) else None
    attempts = receipt.get("attempts")
    if not isinstance(attempts, list):
        attempts = []

    predicates: list[dict[str, Any]] = []
    declared_arms = table.get(lane_key or "", None)

    # The pool in force today: every declared arm in both label forms, plus the
    # rank-1 arm that a superseded receipt is reported as having been replaced by.
    pool_arms: list[str] = []
    rank1_arm: str | None = None
    if declared_arms:
        for _rank in sorted(declared_arms):
            _declared = declared_arms[_rank]
            pool_arms.append(_declared["model"])
            pool_arms.append(f'{_declared["provider"]}/{_declared["model"]}')
        _top = declared_arms[sorted(declared_arms)[0]]
        rank1_arm = f'{_top["provider"]}/{_top["model"]}'

    # The receipt's own time, from the receipt body only. The file mtime is NOT a
    # fallback: accepting it would let an old file buy SUPERSEDED with no
    # timestamp in the receipt at all. No parsable field means UNKNOWN, and
    # UNKNOWN never buys the excuse.
    receipt_time, receipt_time_source = receipt_time_from_receipt(receipt)
    # Two controls the checker findings demanded (2026-10-23), both computed once here so every call site inherits them:
    #   * a pool time taken from a file mtime can never grant an excuse;
    #   * a retired MODEL never authorises an undeclared PROVIDER - the pair is the authorisation.
    allow_supersession = pool_time_source != POOL_TIME_FILE_MTIME
    prior_pairs, pair_problem = load_prior_pairs_checked()
    if pair_problem:
        # Fail CLOSED: if the retired-arm list cannot be read as pairs, nobody gets an excuse this run.
        allow_supersession = False

    # A SUPERSEDED verdict bought with an mtime proxy is weaker evidence than one
    # bought with a revision record, and the payload says so instead of hiding it.
    superseded_confidence = (
        CONFIDENCE_LOW if pool_time_source == POOL_TIME_FILE_MTIME else CONFIDENCE_HIGH
    )

    superseded_notes: list[str] = []
    # Sub-reasons behind the VIOLATION verdict. UNAUTHORIZED_ARM means the served
    # arm was declared by no revision at all, so it is not history under an older
    # pool: it was never authorized.
    unauthorized: list[str] = []

    # R1 -- the lane must have a structural binding in the declaration.
    if declared_arms:
        predicates.append(_predicate(
            "R1_lane_declared", True, None,
            f"lane {lane_key} is declared at rank(s) {sorted(declared_arms)}",
        ))
    else:
        prose = _prose_lane_claims(decl, lane_key or "")
        note = f"lane {lane_key!r} has no structural binding in the declaration"
        if prose:
            note += (
                "; the declaration mentions it only in prose ("
                + ", ".join(prose[:3])
                + "), which is not a binding and is not parsed as one"
            )
        predicates.append(_predicate("R1_lane_declared", False, None, note))

    # R5 -- every skipped arm needs a recorded reason.
    skipped = receipt.get("skipped_arms") or []
    if not isinstance(skipped, list):
        skipped = []
    if not skipped:
        predicates.append(_predicate("R5_no_silent_skip", True, None, "no skipped arms recorded"))
    for entry in skipped:
        if not isinstance(entry, dict):
            predicates.append(_predicate(
                "R5_no_silent_skip", False, None,
                "skipped_arms entry is not an object, so no reason can be recorded",
            ))
            continue
        rank = _as_rank(entry.get("rank"))
        reason = entry.get("reason")
        explained = isinstance(reason, str) and reason.strip() != ""
        if explained:
            predicates.append(_predicate(
                "R5_no_silent_skip", True, rank,
                f"skip of {entry.get('model')!r} at rank {rank} is explained: {reason.strip()[:120]}",
            ))
        else:
            predicates.append(_predicate(
                "R5_no_silent_skip", False, rank,
                f"skip of {entry.get('model')!r} at rank {rank} has no reason",
            ))

    # Per-attempt predicates: R2, R3, R4, R6.
    for attempt in attempts:
        if not isinstance(attempt, dict):
            predicates.append(_predicate("R2_rank_valid", False, None, "attempt is not an object"))
            continue
        rank = _as_rank(attempt.get("rank"))
        arm = declared_arms.get(rank) if (declared_arms and rank is not None) else None

        # R2 -- rank must be one the declaration gives this lane.
        if not declared_arms:
            predicates.append(_predicate(
                "R2_rank_valid", False, rank,
                "lane has no declared ranks, so no attempt rank can be valid",
            ))
        elif rank is None:
            predicates.append(_predicate(
                "R2_rank_valid", False, None, "attempt records no usable rank",
            ))
        elif arm is None:
            predicates.append(_predicate(
                "R2_rank_valid", False, rank,
                f"rank {rank} is not declared for {lane_key}; declared ranks are "
                f"{sorted(declared_arms)}",
            ))
        else:
            predicates.append(_predicate(
                "R2_rank_valid", True, rank,
                f"rank {rank} is declared for {lane_key}",
            ))

        # R3 -- the served model must be the declared arm, and the model the
        # relay billed must be the model that was transported.
        if arm is None:
            predicates.append(_predicate(
                "R3_model_matches_arm", False, rank,
                "no declared arm at this rank, so the served model cannot match the declaration",
            ))
        else:
            served = attempt.get("model")
            want = arm["model"]
            served_ok = isinstance(served, str) and served.strip() == want
            transport = attempt.get("transport_model")
            usage = attempt.get("usage_model")
            if not isinstance(transport, str) or not transport.strip():
                usage_ok = False
                usage_note = "transport_model is absent, so usage_model cannot be compared"
            else:
                billed = _strip_provider_prefix(usage, arm.get("provider"))
                moved = _strip_provider_prefix(transport, arm.get("provider"))
                _claim = _bare_model(served)
                _agrees = (_bare_model(moved) == _claim) and (_bare_model(billed) == _claim)
                usage_ok = isinstance(usage, str) and billed == moved and _agrees
                usage_note = (f"usage_model={usage!r} vs transport_model={transport!r} "
                              f"vs claimed model={served!r} (all three must name the same arm)")
            arm_state, arm_reason = _classify_impl(
                served, pool_arms, receipt_time, pool_time, prior_arms,
                prior_arms_by_revision,
                allow_supersession=allow_supersession,
                served_provider=attempt.get("provider"),
                prior_pairs=prior_pairs,
            )
            if served_ok:
                ok = usage_ok
                served_note = f"served model {served!r} equals declared arm at rank {rank}"
            elif arm_state == SUPERSEDED:
                # The arm matched the pool in force at receipt time; the rebind
                # must not turn that turn red. A billing mismatch is still live,
                # so the usage comparison keeps its own verdict.
                ok = usage_ok
                superseded_notes.append(
                    f"rank {rank}: served {served!r} predates the pool revision "
                    f"({receipt_time} < {pool_time}); ranked historical, superseded "
                    f"by {rank1_arm} (pool_time_source={pool_time_source}, "
                    f"confidence={superseded_confidence})"
                )
                served_note = (
                    f"served model {served!r} is not the current declared model "
                    f"{want!r} at rank {rank}; SUPERSEDED -- the receipt predates the "
                    f"pool revision, so this is history, not a live fault"
                )
            else:
                ok = served_ok and usage_ok
                served_note = f"served model {served!r} is not the declared model {want!r} at rank {rank}"
                if arm_reason == UNAUTHORIZED_ARM:
                    unauthorized.append(
                        f"rank {rank}: served {served!r} appears in neither the "
                        f"current pool nor any prior revision"
                    )
                    served_note += (
                        f"; UNAUTHORIZED_ARM -- no revision ever declared this arm, "
                        f"so the rebind cannot excuse it however old the receipt is"
                    )
                elif arm_reason == REASON_UNKNOWN_TIME:
                    served_note += (
                        "; receipt time is unknown, so it cannot prove it predates "
                        "the pool revision"
                    )
                elif arm_reason == REASON_AT_OR_AFTER_POOL:
                    served_note += (
                        "; the receipt is dated at or after the pool revision, so the "
                        "rebind does not excuse it"
                    )
            _r3 = _predicate(
                "R3_model_matches_arm", ok, rank,
                f"{served_note}; {usage_note}",
            )
            if arm_reason:
                _r3["reason"] = arm_reason
            predicates.append(_r3)

        # R4 -- provider consistency (declared provider and the billing provider).
        if arm is None:
            predicates.append(_predicate(
                "R4_provider_matches", False, rank,
                "no declared arm at this rank, so provider consistency cannot be judged",
            ))
        else:
            want_provider = arm["provider"]
            call_ok = _provider_ok(attempt.get("provider"), want_provider)
            bill_ok = _provider_ok(attempt.get("usage_provider"), want_provider)
            provider_state, provider_reason = _classify_impl(
                attempt.get("model"), pool_arms, receipt_time, pool_time, prior_arms,
                allow_supersession=allow_supersession,
                served_provider=attempt.get("provider"),
                prior_pairs=prior_pairs,
            )
            if provider_state == SUPERSEDED:
                # Historical arm: the declared provider of this rank is today's,
                # so the honest test is the receipt's own call/bill agreement --
                # a billing mismatch stays a live fault even for an old turn.
                called = _normalise_arm(attempt.get("provider"))
                billed = _normalise_arm(attempt.get("usage_provider"))
                provider_ok = called is not None and called == billed
                history = (
                    " (historical: this receipt predates the pool revision, so the "
                    "declared provider is judged as call-vs-bill agreement)"
                )
            else:
                provider_ok = call_ok and bill_ok
                history = ""
            _r4 = _predicate(
                "R4_provider_matches", provider_ok, rank,
                f"declared provider {want_provider!r}; provider={attempt.get('provider')!r}, "
                f"usage_provider={attempt.get('usage_provider')!r}{history}",
            )
            if not provider_ok and provider_reason:
                _r4["reason"] = provider_reason
            predicates.append(_r4)

        # R6 -- evidence of a real green turn; a failure here is NOT_GREEN, not
        # a consistency violation.
        nonce = attempt.get("nonce_present") is True
        exit_code = attempt.get("exit")
        exited_clean = _as_rank(exit_code) == 0 or exit_code == 0
        timed_out = attempt.get("timed_out") is True or exit_code == "TIMEOUT"
        if nonce and exited_clean and not timed_out:
            predicates.append(_predicate(
                "R6_nonce_evidence", True, rank,
                f"nonce_present=true, exit={exit_code!r}, timed_out={attempt.get('timed_out')!r}",
            ))
        else:
            missing = []
            if not nonce:
                missing.append("nonce_present is not true")
            if not exited_clean:
                missing.append(f"exit={exit_code!r} is not 0")
            if timed_out:
                missing.append("attempt timed out")
            predicates.append(_predicate(
                "R6_nonce_evidence", False, rank,
                "no green evidence: " + "; ".join(missing),
            ))

    violations = [
        p for p in predicates
        if not p["ok"] and p["id"] in {
            "R1_lane_declared", "R2_rank_valid", "R3_model_matches_arm",
            "R4_provider_matches", "R5_no_silent_skip",
        }
    ]
    green = bool(attempts) and all(
        p["ok"] for p in predicates if p["id"] == "R6_nonce_evidence"
    )
    if violations:
        verdict = "VIOLATION"
    elif not green:
        verdict = "NOT_GREEN"
    elif superseded_notes:
        verdict = SUPERSEDED
    else:
        verdict = "CONSISTENT"

    return {
        "receipt": path,
        "lane": lane,
        "predicates": predicates,
        "verdict": verdict,
        "superseded": superseded_notes,
        "superseded_by": rank1_arm if superseded_notes else None,
        "violation_reasons": sorted(
            {p["reason"] for p in violations if p.get("reason")}
        ),
        "unauthorized_arm": unauthorized,
        "receipt_time": receipt_time,
        "receipt_time_source": receipt_time_source,
        "pool_time": pool_time,
        "pool_time_source": pool_time_source,
        "superseded_confidence": superseded_confidence,
    }


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #
def _payload(
    declaration_sha256: str | None,
    receipts_checked: int,
    results: list[dict[str, Any]],
    counts: dict[str, int],
    exit_reason: str,
    **extra: Any,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "schema": SCHEMA,
        "declaration_sha256": declaration_sha256,
        "receipts_checked": receipts_checked,
        "results": results,
        "counts": counts,
        "exit_reason": exit_reason,
    }
    out.update(extra)
    return out


def _zero_counts() -> dict[str, int]:
    return {CONSISTENT: 0, SUPERSEDED: 0, VIOLATION: 0, "NOT_GREEN": 0}


def load_prior_pairs_checked(path: str = RETIRED_ARMS_PATH) -> tuple[dict[str, set[str]], str | None]:
    """Same read as `load_prior_pairs`, but it also says WHY the map is empty.

    B10 (2026-10-23): the pair map returned {} both when the retired list declared no providers AND when the file
    could not be read, so a read failure skipped the provider guard entirely - fail-open on missing evidence. A caller
    that cannot tell "nothing to check" from "could not check" will always be exploited; this one can.
    """
    try:
        with open(path, "rb") as handle:
            data = json.loads(handle.read().decode("utf-8-sig"))
    except OSError as exc:
        return {}, "cannot read retired-arm list %s: %s" % (path, exc)
    except Exception as exc:  # noqa: BLE001
        return {}, "cannot parse retired-arm list %s: %s" % (path, exc)
    if not isinstance(data, dict):
        return {}, "retired-arm list %s is not a JSON object" % path
    pairs: dict[str, set[str]] = {}
    for entry in (data.get("arms") or []):
        if not isinstance(entry, dict):
            continue
        label = entry.get("arm")
        provider = entry.get("provider")
        if not isinstance(label, str) or not label.strip():
            continue
        label = label.strip()
        if "/" in label:
            prov, bare = label.split("/", 1)
        else:
            prov, bare = (provider if isinstance(provider, str) else None), label
        if isinstance(prov, str) and prov:
            pairs.setdefault(bare.strip().lower(), set()).add(prov.strip().lower())
    return pairs, None


def load_prior_pairs(path: str = RETIRED_ARMS_PATH) -> dict[str, set[str]]:
    """The retired arms as `provider/model` PAIRS, which is what an excuse actually needs.

    Measured 2026-10-23: a receipt naming the retired model `minimax-m3.1-flash-free` with provider AND usage_provider
    set to an invented provider was reported SUPERSEDED, because the retired-arm list was expanded to bare model
    labels and the historical branch only required call/bill agreement. A retired MODEL does not authorise an
    undeclared PROVIDER: the pair is the authorisation, so the pair is what is checked.
    """
    try:
        with open(path, "rb") as handle:
            data = json.loads(handle.read().decode("utf-8-sig"))
    except Exception:  # noqa: BLE001 - the caller already treats an unreadable list as a hard finding
        return {}
    pairs: dict[str, set[str]] = {}
    for entry in (data.get("arms") or []) if isinstance(data, dict) else []:
        if not isinstance(entry, dict):
            continue
        label = entry.get("arm")
        provider = entry.get("provider")
        if not isinstance(label, str) or not label.strip():
            continue
        label = label.strip()
        if "/" in label:
            prov, bare = label.split("/", 1)
        else:
            prov, bare = (provider if isinstance(provider, str) else None), label
        if isinstance(prov, str) and prov:
            pairs.setdefault(bare.strip().lower(), set()).add(prov.strip().lower())
    return pairs


def load_prior_arms(path: str = RETIRED_ARMS_PATH) -> tuple[list[str], str | None]:
    """Read the retired-arm list: `arms[].arm` labels a prior revision declared.

    Each label is returned in both forms -- `provider/model` and the bare model --
    for the same reason the current pool is: the checker compares the served model
    exactly, and a receipt may record either form. Without the expansion a retired
    `opencode-go/minimax-m3.1-flash-free` would not match a receipt that wrote
    `minimax-m3.1-flash-free`, and an honestly retired arm would read as
    UNAUTHORIZED_ARM.

    Returns (arms, problem). A missing or unparsable file returns ([], reason)
    rather than raising: an unreadable list must not silently restore the old
    "any old arm is superseded" behaviour, so the caller turns the problem into a
    hard error instead of carrying on with an empty allow-list.
    """
    try:
        with open(path, "rb") as handle:
            data = json.loads(handle.read().decode("utf-8-sig"))
    except OSError as exc:
        return [], f"cannot read retired-arm list {path}: {exc}"
    except Exception as exc:  # noqa: BLE001 - any decode failure is one finding
        return [], f"cannot parse retired-arm list {path}: {exc}"
    if not isinstance(data, dict):
        return [], f"retired-arm list {path} is not a JSON object"
    entries = data.get("arms")
    if not isinstance(entries, list):
        return [], f"retired-arm list {path} has no arms[] array"
    arms: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        label = entry.get("arm")
        if not isinstance(label, str) or not label.strip():
            continue
        label = label.strip()
        if label not in arms:
            arms.append(label)
        paid_by = entry.get("provider")
        if "/" in label:
            bare = label.split("/", 1)[1]
            if bare and bare not in arms:
                arms.append(bare)
        elif isinstance(paid_by, str) and paid_by.strip():
            qualified = f"{paid_by.strip()}/{label}"
            if qualified not in arms:
                arms.append(qualified)
    return arms, None


def check(receipts_dir: str = DEFAULT_RECEIPTS_DIR,
          declaration: str = DEFAULT_DECLARATION) -> tuple[dict[str, Any], int]:
    """Run the check. Returns (payload, exit_code); never writes anything."""
    try:
        raw = open(declaration, "rb").read()
    except OSError as exc:
        return _payload(
            None, 0, [], _zero_counts(), "DECLARATION_UNREADABLE",
            declaration=declaration, detail=f"cannot read declaration: {exc}",
        ), 2
    sha = hashlib.sha256(raw).hexdigest()
    try:
        decl = json.loads(raw.decode("utf-8-sig"))
    except Exception as exc:  # noqa: BLE001 - any decode failure is the same finding
        return _payload(
            sha, 0, [], _zero_counts(), "DECLARATION_UNREADABLE",
            declaration=declaration, detail=f"cannot parse declaration: {exc}",
        ), 2
    if not isinstance(decl, dict):
        return _payload(
            sha, 0, [], _zero_counts(), "DECLARATION_UNREADABLE",
            declaration=declaration, detail="declaration is not a JSON object",
        ), 2

    try:
        table = build_lane_table(decl)
    except DeclarationUnusable as exc:
        return _payload(
            sha, 0, [], _zero_counts(), "DECLARATION_UNREADABLE",
            declaration=declaration, detail=str(exc),
        ), 2

    if not os.path.isdir(receipts_dir):
        return _payload(
            sha, 0, [], _zero_counts(), "RECEIPTS_DIR_UNREADABLE",
            declaration=declaration, receipts_dir=receipts_dir,
            detail="receipts directory does not exist or is not a directory",
        ), 2

    paths = sorted(glob.glob(os.path.join(receipts_dir, "*.json")))
    skipped_files: list[dict[str, str]] = []
    receipts: list[tuple[str, dict[str, Any]]] = []
    for path in paths:
        try:
            with open(path, "rb") as handle:
                data = json.loads(handle.read().decode("utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            return _payload(
                sha, 0, [], _zero_counts(), "RECEIPT_UNREADABLE",
                declaration=declaration, receipts_dir=receipts_dir,
                detail=f"cannot read receipt {os.path.basename(path)}: {exc}",
            ), 2
        if isinstance(data, dict) and "lane" in data and isinstance(data.get("attempts"), list):
            receipts.append((path, data))
        else:
            skipped_files.append({
                "file": os.path.abspath(path),
                "reason": "not a lane receipt (no lane + attempts[]); not counted",
            })

    if not receipts:
        return _payload(
            sha, 0, [], _zero_counts(), "NO_RECEIPTS",
            declaration=declaration, receipts_dir=receipts_dir,
            declared_lanes=sorted(table), skipped_files=skipped_files,
            detail="no lane receipts found; an empty set is not evidence of consistency",
        ), 2

    # The pool "in force" is the file that was passed in, and an edit to it is the
    # rebind -- but the TIME comes from the pool's OWN revision record. The file
    # mtime is only a labelled last resort, and every SUPERSEDED verdict built on
    # it says so (receipts may not invent a time by touching the file either).
    pool_time, pool_time_source = resolve_pool_time(decl, declaration)

    # Without the retired-arm list every unknown arm would read as superseded
    # again, so an unreadable list is an IO error, not an empty allow-list.
    prior_arms, arms_problem = load_prior_arms()
    if arms_problem:
        return _payload(
            sha, 0, [], _zero_counts(), "RETIRED_ARMS_UNREADABLE",
            declaration=declaration, receipts_dir=receipts_dir,
            retired_arms_path=os.path.abspath(RETIRED_ARMS_PATH),
            detail=arms_problem,
        ), 2

    results = [
        _evaluate_receipt(
            path, receipt, table, decl, pool_time, prior_arms,
            pool_time_source=pool_time_source,
        )
        for path, receipt in receipts
    ]
    counts = _zero_counts()
    for result in results:
        counts[result["verdict"]] += 1

    unauthorized_count = sum(
        1 for result in results if UNAUTHORIZED_ARM in result["violation_reasons"]
    )

    if counts["VIOLATION"]:
        exit_code, reason = 1, "VIOLATION"
    elif counts["NOT_GREEN"]:
        exit_code, reason = 1, "NOT_GREEN"
    elif counts[SUPERSEDED]:
        exit_code, reason = 0, "ALL_CONSISTENT_OR_SUPERSEDED"
    else:
        exit_code, reason = 0, "ALL_CONSISTENT"

    payload = _payload(
        sha, len(results), results, counts, reason,
        declaration=declaration, receipts_dir=receipts_dir,
        declared_lanes=sorted(table), skipped_files=skipped_files,
        pool_time=pool_time,
        pool_time_source=pool_time_source,
        retired_arms_path=os.path.abspath(RETIRED_ARMS_PATH),
        prior_arms=prior_arms,
        unauthorized_arm_receipts=unauthorized_count,
    )
    return payload, exit_code


USAGE = (
    "usage: check_lane_consistency.py [--receipts-dir DIR] [--declaration FILE] [--pretty]\n"
    "  defaults: --receipts-dir <repo>/receipts/dispatch\n"
    "            --declaration C:/Projects/Agent_Workspace/HG-KSEOS/config/hermes-codex-lane.json"
)


def _parse_args(argv: list[str]) -> tuple[dict[str, str], bool] | None:
    options = {"receipts-dir": DEFAULT_RECEIPTS_DIR, "declaration": DEFAULT_DECLARATION}
    pretty = False
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--pretty":
            pretty = True
            index += 1
            continue
        if arg in ("-h", "--help"):
            return None
        matched = False
        for name in options:
            flag = "--" + name
            if arg == flag:
                if index + 1 >= len(argv):
                    print(f"missing value for {flag}\n{USAGE}", file=sys.stderr)
                    return None
                options[name] = argv[index + 1]
                index += 2
                matched = True
                break
            if arg.startswith(flag + "="):
                options[name] = arg.split("=", 1)[1]
                index += 1
                matched = True
                break
        if not matched:
            print(f"unknown argument {arg!r}\n{USAGE}", file=sys.stderr)
            return None
    return options, pretty


def main(argv: list[str] | None = None) -> int:
    parsed = _parse_args(list(sys.argv[1:] if argv is None else argv))
    if parsed is None:
        print(json.dumps(_payload(None, 0, [], _zero_counts(), "USAGE",
                                  detail="bad arguments; see stderr"), ensure_ascii=False))
        return 2
    options, pretty = parsed
    payload, code = check(options["receipts-dir"], options["declaration"])
    print(json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
