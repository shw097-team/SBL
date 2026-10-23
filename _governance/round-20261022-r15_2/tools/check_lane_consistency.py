"""Offline three-lane consistency checker (W08).

One question, one answer: does every lane dispatch receipt show the arm the lane
declaration says that lane should be served by?

    python tools/check_lane_consistency.py
    python tools/check_lane_consistency.py --receipts-dir <dir> --declaration <file>

Exit codes: 0 every checked receipt is CONSISTENT; 1 any VIOLATION or NOT_GREEN;
2 usage/IO/parse error. Exactly one JSON object is printed on stdout.

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


def _evaluate_receipt(
    path: str,
    receipt: dict[str, Any],
    table: dict[str, dict[int, dict[str, Any]]],
    decl: dict[str, Any],
) -> dict[str, Any]:
    lane = receipt.get("lane")
    lane_key = lane.strip() if isinstance(lane, str) else None
    attempts = receipt.get("attempts")
    if not isinstance(attempts, list):
        attempts = []

    predicates: list[dict[str, Any]] = []
    declared_arms = table.get(lane_key or "", None)

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
                usage_ok = isinstance(usage, str) and billed == moved
                usage_note = f"usage_model={usage!r} vs transport_model={transport!r}"
            ok = served_ok and usage_ok
            if served_ok:
                served_note = f"served model {served!r} equals declared arm at rank {rank}"
            else:
                served_note = f"served model {served!r} is not the declared model {want!r} at rank {rank}"
            predicates.append(_predicate(
                "R3_model_matches_arm", ok, rank,
                f"{served_note}; {usage_note}",
            ))

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
            predicates.append(_predicate(
                "R4_provider_matches", call_ok and bill_ok, rank,
                f"declared provider {want_provider!r}; provider={attempt.get('provider')!r}, "
                f"usage_provider={attempt.get('usage_provider')!r}",
            ))

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
    else:
        verdict = "CONSISTENT"

    return {
        "receipt": path,
        "lane": lane,
        "predicates": predicates,
        "verdict": verdict,
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
    return {"CONSISTENT": 0, "VIOLATION": 0, "NOT_GREEN": 0}


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

    results = [_evaluate_receipt(path, receipt, table, decl) for path, receipt in receipts]
    counts = _zero_counts()
    for result in results:
        counts[result["verdict"]] += 1

    if counts["VIOLATION"]:
        exit_code, reason = 1, "VIOLATION"
    elif counts["NOT_GREEN"]:
        exit_code, reason = 1, "NOT_GREEN"
    else:
        exit_code, reason = 0, "ALL_CONSISTENT"

    payload = _payload(
        sha, len(results), results, counts, reason,
        declaration=declaration, receipts_dir=receipts_dir,
        declared_lanes=sorted(table), skipped_files=skipped_files,
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
