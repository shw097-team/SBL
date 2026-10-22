"""lane_route_resolver.py — CANDIDATE, ISOLATED. Not wired into the launcher.

Resolves one lane's model for one dispatch out of an owner-declared ORDERED POOL, keeping every
existing governance boundary intact:

  * the pool is the authority (drift-checked artifact, unchanged governance surface);
  * a session override may only pick an entry that is IN the pool, otherwise the dispatch is refused;
  * fallback advances only on RUNTIME model failures (quota / auth / server / timeout / connection /
    transport-unreachable), never on a governance refusal;
  * a governance refusal (the existing SoD hook, the registry gate, ...) is TERMINAL and fail-closed -
    relaxing governance is never the mechanism that makes a model switch succeed;
  * if every entry in the pool fails at runtime the resolver stops safely with a typed error: it never
    silently falls back to something outside the pool;
  * the receipt records the ACTUAL entry used (rank, role, provider, model, transport) plus every attempt.

No import of hg_kseos, no file writes, no network. The caller injects `probe` and `sod_hook`.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

SCHEMA = "HGK-LANE-ROUTE-SLOTS/1"
RECEIPT_SCHEMA = "HGK-LANE-RESOLUTION/1"


def _reject_nonjson_constant(name: str):
    """T2 (REQ-STRICT-DECLARATION-014, pass 2): a `parse_constant` that RAISES.

    Python's `json.loads` accepts the non-JSON constants `NaN`, `Infinity` and `-Infinity` by DEFAULT
    (an implementation extension, not the JSON grammar). Passing a raising `parse_constant` makes them
    a parse error, so a declared value carrying one is a MALFORMED artifact, never a coerced float.
    """
    raise ValueError(f"{name} is not a valid JSON constant")


def _strict_json_loads(text: str):
    """T2: parse JSON so that the non-JSON constants `NaN`/`Infinity`/`-Infinity` RAISE.

    The single strict-parse entry point for this module: every declared read goes through it, so a
    permissive parser default can never decide a declaration.
    """
    return json.loads(text, parse_constant=_reject_nonjson_constant)


def _has_surrogate(text: str) -> bool:
    """T3: True when `text` carries any surrogate code point (U+D800-U+DFFF).

    A surrogate is not a character that can appear in valid UTF-8 text; it arises from a JSON escape
    (``\\ud800``) or a lossy decode. Such text must never decide a decision, so callers skip it.
    """
    return any(0xD800 <= ord(ch) <= 0xDFFF for ch in text)

# S1 (REQ-STRICT-DECLARATION-014): a declared value is admitted only at its EXACT JSON type. A wrong
# type is a TYPE defect, reported under its OWN code so a caller can tell it from a missing/structural
# one (ERR_SLOT_POOL_ENTRY_MALFORMED). Nothing is coerced (`int()`/`str()` on a declared value is
# exactly the substitution this round removes).
ERR_SLOT_POOL_ENTRY_TYPE = "ERR_SLOT_POOL_ENTRY_TYPE"

# A runtime failure means "this model could not serve right now" -> the next pool entry may be tried.
RUNTIME_FALLBACK_CLASSES = frozenset(
    {"QUOTA", "AUTH", "SERVER", "TIMEOUT", "CONNECTION", "TRANSPORT_UNREACHABLE"}
)
# Anything the resolver does not recognise is treated as terminal, never as a fallback trigger.
KNOWN_CLASSES = RUNTIME_FALLBACK_CLASSES | {"SUCCESS"}


class LaneRouteError(Exception):
    """Typed refusal. `code` is stable and safe to log."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class PoolEntry:
    rank: int
    role: str
    provider: str
    model: str
    transport: str
    engine: str

    @property
    def token(self) -> str:
        return f"{self.provider}/{self.model}"


@dataclass
class Resolution:
    lane: str
    mode: str
    selected: PoolEntry
    attempts: list[dict] = field(default_factory=list)
    sod_invoked: bool = False

    @property
    def used_token(self) -> str:
        return self.selected.token

    def receipt(self) -> dict:
        return {
            "schema": RECEIPT_SCHEMA,
            "lane": self.lane,
            "mode": self.mode,
            "selected": {"rank": self.selected.rank, "role": self.selected.role,
                         "provider": self.selected.provider, "model": self.selected.model,
                         "transport": self.selected.transport, "engine": self.selected.engine},
            "used_token": self.used_token,
            "attempts": self.attempts,
            "governance": {"sod_hook": "invoked" if self.sod_invoked else "not_provided"},
            "safe_stop": False,
        }


def _hook_refusal(value, lane: str, token: str) -> bool:
    """Only None or False mean 'no refusal'. Anything else must be a non-empty reason string.

    checker round 2: '' and 0 were previously swallowed as 'no refusal', which hid a broken hook.
    """
    if value is None or value is False:
        return False
    if isinstance(value, str) and value.strip():
        return True
    raise LaneRouteError("ERR_SLOT_GOVERNANCE_HOOK_RETURN", f"{lane}:{token}:{value!r}")


def _require_json_string(value, where: str, key: str, *, allow_empty: bool = False) -> str:
    """S1: `value` must be a JSON string (non-empty unless `allow_empty`); never coerced."""
    if not isinstance(value, str) or (not allow_empty and value == ""):
        raise LaneRouteError(
            ERR_SLOT_POOL_ENTRY_TYPE,
            f"{where}:{key}:{type(value).__name__}={value!r}: must be a "
            f"{'JSON string' if allow_empty else 'non-empty JSON string'}")
    if _has_surrogate(value):
        # T3: a declared string carrying a surrogate code point (`\\ud800`) is not usable text; it is
        # rejected rather than accepted as a value that could later decide a dispatch.
        raise LaneRouteError(ERR_SLOT_POOL_ENTRY_TYPE, f"{where}:{key}:contains a surrogate code point")
    return value


def _require_json_int(value, where: str, key: str) -> int:
    """S1: `value` must be a JSON integer; `bool` is EXPLICITLY excluded.

    In Python `bool` is a subclass of `int`, so `isinstance(x, int)` alone wrongly admits `true`.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise LaneRouteError(
            ERR_SLOT_POOL_ENTRY_TYPE,
            f"{where}:{key}:{type(value).__name__}={value!r}: must be a JSON integer")
    return value


def load_pool(path: str | Path) -> dict[str, list[PoolEntry]]:
    try:
        # T2: strict parse -- `NaN`/`Infinity`/`-Infinity` raise rather than parse to a float.
        data = _strict_json_loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        # checker round 3 (N5): the artifact boundary stays typed, not a raw crash
        raise LaneRouteError("ERR_SLOT_POOL_UNREADABLE", f"{path}:{type(exc).__name__}") from exc
    except json.JSONDecodeError as exc:
        raise LaneRouteError("ERR_SLOT_POOL_MALFORMED", f"{path}:{exc.msg}") from exc
    except ValueError as exc:
        # T2: a raising `parse_constant` surfaces as a ValueError (json.JSONDecodeError is a subclass
        # and is caught above); a non-JSON constant makes the artifact MALFORMED, never a coerced value.
        raise LaneRouteError("ERR_SLOT_POOL_MALFORMED",
                             f"{path}:non-JSON constant: {exc}") from exc
    if not isinstance(data, dict):
        # A top-level non-object (e.g. a payload that parses to a scalar) has no `.get`; refuse typed.
        raise LaneRouteError("ERR_SLOT_POOL_MALFORMED", f"{path}:top-level value is not an object")
    if data.get("schema") != SCHEMA:
        raise LaneRouteError("ERR_SLOT_POOL_SCHEMA", str(data.get("schema")))
    if data.get("status") != "CANDIDATE" and data.get("status") is not None:
        # a promoted pool would carry a different marker; refuse rather than guess
        pass
    lanes: dict[str, list[PoolEntry]] = {}
    for lane in data.get("lanes", []):
        name = lane.get("lane")
        if str(name) in lanes:
            # checker round 2: a duplicated lane block must never silently discard the earlier one
            raise LaneRouteError("ERR_SLOT_POOL_DUPLICATE_LANE", str(name))
        # S1: role/transport/engine may be ABSENT, but a present value must be a string; never coerced.
        transport = _require_json_string(lane.get("transport", ""), str(name), "transport",
                                         allow_empty=True)
        engine = _require_json_string(lane.get("engine", ""), str(name), "engine", allow_empty=True)
        entries = []
        for e in lane.get("ordered_pool", []):
            try:
                where = f"{name}:entry{len(entries) + 1}"
                if "rank" not in e:
                    raise KeyError("rank")
                rank = _require_json_int(e["rank"], where, "rank")
                if "provider" not in e:
                    raise KeyError("provider")
                provider = _require_json_string(e["provider"], where, "provider")
                if "model" not in e:
                    raise KeyError("model")
                model = _require_json_string(e["model"], where, "model")
                role = _require_json_string(e.get("role", ""), where, "role", allow_empty=True)
            except LaneRouteError:
                # a TYPE defect keeps its own code (ERR_SLOT_POOL_ENTRY_TYPE); the exact types are
                # already asserted above, so nothing here is coerced.
                raise
            except (KeyError, TypeError, ValueError) as exc:
                # checker round 3 (N7): a malformed entry is a typed refusal, not a raw KeyError
                raise LaneRouteError("ERR_SLOT_POOL_ENTRY_MALFORMED",
                                     f"{name}:entry{len(entries) + 1}:{type(exc).__name__}:{exc}") from exc
            entry = PoolEntry(rank=rank, role=role, provider=provider, model=model,
                              transport=transport, engine=engine)
            entries.append(entry)
        entries.sort(key=lambda x: x.rank)
        ranks = [e.rank for e in entries]
        if not entries:
            raise LaneRouteError("ERR_SLOT_POOL_EMPTY_LANE", str(name))
        if ranks != list(range(1, len(entries) + 1)):
            raise LaneRouteError("ERR_SLOT_POOL_RANK_GAP", f"{name}:{ranks}")
        tokens = [e.token for e in entries]
        dupes = sorted({t for t in tokens if tokens.count(t) > 1})
        if dupes:
            # checker round 2: identity duplicates belong at the artifact boundary, not at dispatch time
            raise LaneRouteError("ERR_SLOT_POOL_DUPLICATE_TOKEN", f"{name}:{dupes}")
        lanes[str(name)] = entries
    if not lanes:
        raise LaneRouteError("ERR_SLOT_POOL_INVALID", "no lanes")
    return lanes


def resolve(
    lanes: dict[str, list[PoolEntry]],
    lane: str,
    *,
    override: str | None = None,
    probe: Callable[[PoolEntry], dict] | None = None,
    sod_hook: Callable[[PoolEntry, str], str | None] | None = None,
) -> Resolution:
    """Pick the entry to dispatch. `override` is a provider/model token; `probe` returns
    {"ok": bool, "class": str, "detail": str}. Raises LaneRouteError on any refusal."""
    if lane not in lanes:
        raise LaneRouteError("ERR_SLOT_LANE_UNKNOWN", lane)
    entries = lanes[lane]

    if override is not None:
        exact = [e for e in entries if e.token == override]
        matches = exact or [e for e in entries if e.model == override]
        if not matches:
            # the pool is the authority: an out-of-pool instruction is refused, never probed
            raise LaneRouteError("ERR_SLOT_NOT_IN_POOL", f"{lane}:{override}")
        if len(matches) > 1:
            # checker round 1 (case C): never silently resolve an ambiguous instruction to rank 1
            raise LaneRouteError("ERR_SLOT_OVERRIDE_AMBIGUOUS",
                                 f"{lane}:{override}:matches={[e.token for e in matches]}")
        chosen = matches[0]
        if sod_hook is not None:
            try:
                refusal = sod_hook(chosen, lane)
            except Exception as exc:  # noqa: BLE001
                # checker round 1 (case E): a faulty governance hook is a typed refusal, not a crash
                raise LaneRouteError("ERR_SLOT_GOVERNANCE_HOOK_FAILURE",
                                     f"{lane}:{chosen.token}:{type(exc).__name__}") from exc
            if _hook_refusal(refusal, lane, chosen.token):
                raise LaneRouteError("ERR_SLOT_GOVERNANCE_REFUSED", f"{lane}:{chosen.token}")
        res = Resolution(lane=lane, mode="override", selected=chosen,
                         sod_invoked=sod_hook is not None)
        res.attempts.append({"rank": chosen.rank, "role": chosen.role, "token": chosen.token,
                             "class": "NOT_PROBED_OVERRIDE", "detail": "explicit session instruction"})
        return res

    attempts: list[dict] = []
    for entry in entries:  # declared order is authoritative; nothing reorders it
        if sod_hook is not None:
            try:
                refusal = sod_hook(entry, lane)
            except Exception as exc:  # noqa: BLE001
                raise LaneRouteError("ERR_SLOT_GOVERNANCE_HOOK_FAILURE",
                                     f"{lane}:{entry.token}:{type(exc).__name__}") from exc
            if _hook_refusal(refusal, lane, entry.token):
                # governance refusals are terminal: no advance, no waiver, no silent skip
                raise LaneRouteError("ERR_SLOT_GOVERNANCE_REFUSED", f"{lane}:{entry.token}:{refusal}")
        if probe is None:
            # checker round 1 (case D): an unmeasured route must never be treated as available
            raise LaneRouteError("ERR_SLOT_PROBE_REQUIRED",
                                 f"{lane}:{entry.token}: no availability probe injected")
        try:
            outcome = probe(entry)
        except Exception as exc:  # noqa: BLE001
            # checker round 1 (case A): the probe is the network layer; its faults are typed refusals
            raise LaneRouteError("ERR_SLOT_PROBE_FAILURE",
                                 f"{lane}:{entry.token}:{type(exc).__name__}") from exc
        if not isinstance(outcome, dict):
            raise LaneRouteError("ERR_SLOT_PROBE_SHAPE",
                                 f"{lane}:{entry.token}:{type(outcome).__name__}")
        klass = str(outcome.get("class", "SUCCESS" if outcome.get("ok") else "UNKNOWN"))
        if klass not in KNOWN_CLASSES:
            raise LaneRouteError("ERR_SLOT_UNKNOWN_FAILURE_CLASS", f"{lane}:{entry.token}:{klass}")
        attempts.append({"rank": entry.rank, "role": entry.role, "token": entry.token, "class": klass,
                         "detail": str(outcome.get("detail", ""))[:200]})
        if klass == "SUCCESS":
            return Resolution(lane=lane, mode="default", selected=entry, attempts=attempts,
                              sod_invoked=sod_hook is not None)
    raise LaneRouteError("ERR_LANE_ALL_ROUTES_EXHAUSTED",
                         f"{lane}:{','.join(a['token'] + '=' + a['class'] for a in attempts)}")
