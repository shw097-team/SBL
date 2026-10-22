#!/usr/bin/env python
"""hgk-lane-dispatch.py - lane-parameterised Codex-CLI dispatch over the ordered pool.

FAR ruling (owner instruction 2026-10-10): PLAN stays on the harness engine; EXECUTE and
VERIFY_SECURITY are handed to the CODEX CLI. The pool artifact is the selection AUTHORITY; this
call site owns MEASUREMENT (it runs the real Codex turn per candidate).

Design choices, each to keep friction and drift low:
  * NO config mutation. Every routing decision is a per-invocation `-c key=value` override
    (model / openai_base_url / model_reasoning_effort), so the lane home and the human home keep
    their own contents and nothing has to be rolled back.
  * transport_model per pool entry: the measured vocabulary is per-provider (opencode-go accepts
    bare and qualified; nvidia REQUIRES '<provider>/<model>'; the openai arm REQUIRES the bare id,
    because 'openai-codex/<model>' is routed to the default provider and answers HTTP 400).
  * The transport is the relay on 10101, reached either directly or through the pool-aware front door
    (scripts/hgk-exec-model-frontdoor.py --pool, port 10103, its own ledger). The sealed single-model
    10100 door is not used: it answers 403 for every model except its one sanctioned id.
  * Sandbox defaults are role-shaped: a checker is read-only; a writer gets danger-full-access.
  * The usage receipt must come from a row APPENDED AFTER this attempt started (round-5 checker
    finding: matching only the last line lets a previous run's 200 satisfy the receipt).
  * A sandbox stricter-than-role default may only be escalated with --allow-sandbox-escalation, so a
    single flag cannot give a checker lane writer-grade access (round-5 checker finding).
  * Credential posture (REQ-HGK-GCM-APPLY-002): every spawned child gets `GIT_TERMINAL_PROMPT=0`
    (git's own askpass/terminal fallback is closed below L1), and the fail-closed GCM containment
    preflight runs BEFORE the spawn with an asymmetric policy -- FAIL blocks (a prompt-capable helper
    is a hang for an unattended lane), INCONCLUSIVE warns and continues (a detector fault must not
    become a lane outage), PASS is silent. The posture in force is recorded on every attempt.

Refusals are typed. A policy refusal is TERMINAL and never becomes an empty candidate list.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
# Phase C helpers (round HGK-GCM-REPAIR-20261013): per-attempt output dirs (C1) + the single-use
# authorization claim (C2). They live beside the other GCM containment tooling. Importing them here
# is what moves C1/C3 from prose onto the DECLARED dispatch path.
sys.path.insert(0, str(ROOT / "scripts" / "gcm-containment"))
try:
    import lane_output_dir as _lod  # noqa: E402
except Exception:  # noqa: BLE001 - a missing helper must never crash the dispatcher at import
    _lod = None
try:
    import authorization_claim as _authz  # noqa: E402
except Exception:  # noqa: BLE001
    _authz = None
from hg_kseos.lane_route_resolver import (  # noqa: E402
    ERR_SLOT_POOL_ENTRY_TYPE,
    LaneRouteError,
    load_pool,
)
try:
    from hg_kseos import role_binding as _role_binding  # noqa: E402
except Exception:  # noqa: BLE001 - a missing helper must never crash the dispatcher at import
    _role_binding = None
# D-06 (R13 follow-through): SP identity for the PRE-SPAWN gate. Loaded by path so the helper can
# sit beside this file without putting scripts/ on sys.path (it would outrank src/ for any name the
# two trees share). A missing helper is never a crash: the gate refuses typed instead.
try:
    import importlib.util as _ilu  # noqa: E402
    _sp_spec = _ilu.spec_from_file_location("hgk_sp_identity", ROOT / "scripts" / "hgk_sp_identity.py")
    _sp_loader = getattr(_sp_spec, "loader", None)
    if _sp_spec is None or _sp_loader is None:
        raise ImportError("scripts/hgk_sp_identity.py has no loader")
    _sp_identity = _ilu.module_from_spec(_sp_spec)
    _sp_loader.exec_module(_sp_identity)
except Exception:  # noqa: BLE001
    _sp_identity = None
ERR_SP_IDENTITY_MODULE_UNAVAILABLE = "ERR_SP_IDENTITY_MODULE_UNAVAILABLE"
ERR_SP_IDENTITY_FLAG_WITHOUT_IDENTITY = "ERR_SP_IDENTITY_FLAG_WITHOUT_IDENTITY"

# Tranche B: the per-round role-binding refusals, raised PRE-SPAWN immediately before run_candidate.
ERR_ROLE_BINDING_FILE_UNREADABLE = "ERR_ROLE_BINDING_FILE_UNREADABLE"
ERR_ROLE_BINDING_INVALID = "ERR_ROLE_BINDING_INVALID"
ERR_ROLE_BINDING_ARM_MISMATCH = "ERR_ROLE_BINDING_ARM_MISMATCH"
ERR_ROLE_BINDING_RANK_MISMATCH = "ERR_ROLE_BINDING_RANK_MISMATCH"
ERR_ROLE_BINDING_LANE_UNDECLARED = "ERR_ROLE_BINDING_LANE_UNDECLARED"
ERR_ROLE_BINDING_WORKORDER_REQUIRED = "ERR_ROLE_BINDING_WORKORDER_REQUIRED"

SCHEMA = "HGK-LANE-RESOLUTION/1"
DEFAULT_POOL = ROOT / "config/lane-route-slots.candidate.json"
SPINE_DB = ROOT / "var" / "shared-spine" / "hg-kseos.db"
SPINE_SCHEMA = ROOT / "src" / "hg_kseos" / "schema.sql"
DEFAULT_LANE_HOME = Path(os.environ.get("LOCALAPPDATA", "")) / "HG-KSEOS" / "codex-hermes"
DEFAULT_USAGE = Path(os.environ.get("LOCALAPPDATA", "")) / "HG-KSEOS" / "opencodex-hermes" / "usage.jsonl"
DEFAULT_RELAY = "http://127.0.0.1:10101/v1"
# Sandbox per lane. MEASURED 2026-10-10 (T5 outside the workspace root, T5b/T6 inside it): under
# `workspace-write` NO command_execution item is emitted at all and nothing lands, while the turn
# still reports exit 0 + the nonce; the only `error` item is a model-metadata warning. So the exit
# code and the nonce are not evidence that any work happened. `danger-full-access` emits a real
# command_execution item (exit 0) and the side effect lands. An artifact-writing lane therefore
# needs danger-full-access, and a read-only SUBJECT is enforced by a frozen copy plus a post-hoc
# digest comparison - not by the sandbox.
SANDBOX_BY_LANE = {"EXECUTE": "danger-full-access", "VERIFY_SECURITY": "read-only", "PLAN": "read-only"}
SANDBOX_RANK = {"read-only": 0, "workspace-write": 1, "danger-full-access": 2}


def codex_executable() -> str:
    b = json.loads((ROOT / "config/hermes-codex-lane.json").read_text(encoding="utf-8"))
    return str(b["codex_executable"])


def _reject_nonjson_constant(name: str):
    """T2 (REQ-STRICT-DECLARATION-014, pass 2): a `parse_constant` that RAISES.

    Python's `json.loads` accepts the non-JSON constants `NaN`, `Infinity` and `-Infinity` by DEFAULT.
    A raising `parse_constant` turns them into a parse error, so a carrier or usage row carrying one is
    not a row at all -- it can never decide a verdict.
    """
    raise ValueError(f"{name} is not a valid JSON constant")


def strict_json_loads(text: str):
    """T2: the ONE strict JSON parse for this module -- `NaN`/`Infinity`/`-Infinity` RAISE.

    Every place a parsed value can decide a verdict (carrier lines, usage rows, the pool, the auth
    documents) goes through here, so a permissive parser default can never stand in for evidence.
    """
    return json.loads(text, parse_constant=_reject_nonjson_constant)


def has_surrogate(text: str) -> bool:
    """T3: True when `text` carries any surrogate code point (U+D800-U+DFFF).

    A surrogate cannot appear in valid UTF-8; it comes from a JSON escape (``\\ud800``) or a lossy
    decode. Text carrying one is not usable evidence on this reader, so it is skipped and counted.
    """
    return any(0xD800 <= ord(ch) <= 0xDFFF for ch in text)


def _line_spans(blob: bytes) -> list[tuple[int, bytes]]:
    """J2: split `blob` into COMPLETE lines, each `(relative_offset, line_without_terminator)`.

    A row is evidence only when it both BEGINS on a line boundary and ENDS with a terminator. A
    trailing fragment with no newline is a partially written tail, NOT a row, so it is dropped here
    and never reaches the parser. `\\r\\n` and `\\n` are both accepted as terminators (the ledger may
    be written by either platform); the terminator is stripped from the returned bytes but its
    presence is what makes the line complete.
    """
    spans: list[tuple[int, bytes]] = []
    start = 0
    n = len(blob)
    while start < n:
        nl = blob.find(b"\n", start)
        if nl == -1:
            break                      # an unterminated tail is not a line (J2)
        line = blob[start:nl]
        if line.endswith(b"\r"):
            line = line[:-1]
        spans.append((start, line))
        start = nl + 1
    return spans


def usage_spans_since(usage_path: Path, offset: int) -> list[tuple[int, bytes]]:
    """The COMPLETE lines appended after byte `offset`, each as a `(relative_offset, bytes)` pair.

    Two independent boundaries gate a line here:
      * J2 (offset must sit on a line boundary): the turn's evidence region is `[offset, last
        newline]`. When `offset > 0` the byte at `offset-1` must be a newline -- otherwise `offset`
        sits INSIDE a pre-existing line and the region is a CONTINUATION of it, refused (0 lines).
        A partially written tail is likewise never a row: `_line_spans` drops any line without a
        terminator.
      * J1 (strict decode): the raw bytes are returned untouched; the caller decodes them with
        `errors="strict"`. A line that is not valid UTF-8 is not returned as text and is counted
        (`usage_rows_undecodable`), never substituted.
    """
    if not usage_path.is_file():
        return []
    size = usage_path.stat().st_size
    if size < offset:
        # Refuse to recover: a shrunken ledger is invalid evidence, surfaced by the caller as
        # `usage_ledger_rewritten` rather than silently mined from byte zero.
        return []
    with usage_path.open("rb") as fh:
        if offset > 0:
            fh.seek(offset - 1)
            if fh.read(1) != b"\n":
                # J2: a non-line-boundary offset means every byte after it continues a line that was
                # already in progress before the attempt; nothing in the region is a fresh row.
                return []
        fh.seek(offset)
        blob = fh.read()
    return _line_spans(blob)


def decode_usage_spans(spans) -> tuple[list[dict], int]:
    """J1: parse `(rel_offset, bytes)` spans STRICTLY, returning `(rows, undecodable_count)`.

    Each line is decoded with `errors="strict"`. A line that is not valid UTF-8 makes `.decode`
    raise, and that line is SKIPPED and COUNTED -- it is never decoded with a substitution, so a
    substituted character (U+FFFD) can never stand in for a real byte and can never match a field.
    A blank line is skipped silently (it is not undecodable, just empty).

    T2 (pass 2): each decoded line is parsed with `strict_json_loads`, so a row carrying the non-JSON
    constants `NaN`/`Infinity`/`-Infinity` RAISES and is SKIPPED and COUNTED as a parse failure
    (never accepted as a permissive float that could match a field). A line that fails to parse for
    any other reason is likewise not a row.
    """
    rows: list[dict] = []
    undecodable = 0
    for _rel, raw in spans:
        if not raw.strip():
            continue
        try:
            text = raw.decode("utf-8", "strict")
        except UnicodeDecodeError:
            undecodable += 1
            continue
        try:
            rows.append(strict_json_loads(text))
        except Exception:
            continue
    return rows, undecodable


def usage_rows_since(usage_path: Path, offset: int) -> list[dict]:
    """Only the rows APPENDED after byte `offset`, strictly decoded (J1/J2).

    The round-5 checker showed that reading just the last line lets a PREVIOUS run's 200 satisfy
    the receipt of a call that produced none. Binding to a byte offset captured before the attempt
    removes that whole class: a stale row is never even considered. H3 (pass-4): a ledger that SHRANK
    below the captured offset had been rewritten/truncated and has no honest post-attempt region, so
    the read never resets to zero to recover a stale row.

    Pass-6 J1/J2 narrow this further: an offset that is not a line boundary yields nothing (a
    continuation is not a row), an unterminated tail yields no row, and a line that fails strict
    UTF-8 decoding is dropped. `usage_spans_since` + `decode_usage_spans` is the ONE implementation;
    this thin wrapper keeps the unit surface (`usage_rows_since`) working for callers and tests that
    only need the decoded rows.
    """
    rows, _undecodable = decode_usage_spans(usage_spans_since(usage_path, offset))
    return rows


def usage_prefix_digest(usage_path: Path, offset: int):
    """I1: the sha256 of the ledger's pre-turn bytes `[0:offset)`, or None when unreadable.

    A ledger that GREW past the captured offset can still have had its pre-offset bytes shifted and a
    stale row copied PAST the offset (the pass-4 shrinking-only check never saw it). Binding the
    receipt to a DIGEST of the exact pre-turn prefix closes the whole class: at read time the prefix
    must be byte-identical, so any prepend/shift/replace is detected by CONTENT, not by size.

    A ledger that did not exist before the turn has an EMPTY prefix (`offset == 0`), so the digest is
    the sha256 of the empty string -- NOT None -- otherwise the ledger's creation during the turn
    would read as a prefix change and wrongly flag an ordinary first append as a rewrite.
    """
    if not usage_path.is_file():
        return hashlib.sha256(b"").hexdigest() if offset == 0 else None
    try:
        with usage_path.open("rb") as fh:
            return hashlib.sha256(fh.read(offset)).hexdigest()
    except Exception:
        return None


_USAGE_ROW_SCALARS = (str, int, float, bool, type(None))


def is_usage_row_shaped(row) -> bool:
    """I2: whether a decoded usage row has the object shape every consumer below requires.

    A row that is not a JSON object (a nonempty array, a bare `true`, a string, an integer) has no
    `.get`, so the pass-4 parser raised `AttributeError` and the surface exited 1 with NO receipt.
    The shape is validated HERE, once, so every wrong-shaped row is skipped and COUNTED rather than
    crashing. `bool`/scalars are excluded deliberately: only a real object can carry the provider/
    model/status fields a receipt needs.
    """
    return isinstance(row, dict)


def receipt_reject_reason(entry: dict, usage: dict | None) -> str:
    """The reason a usage row is NOT this attempt's receipt, or "" when it is.

    H2 (pass-4 checker false green): `int(200.9) == 200` accepted a fractional status. The status is
    now validated STRICTLY as an exact integer equal to 200, with `bool` excluded explicitly (in
    Python `True` is an `int` equal to 1, so a JSON `true` must never read as a status). Floats,
    strings and every other shape are rejected, and the reason is recorded rather than swallowed.

    The relay records its OWN account-scoped provider id (the openai arm reports openai-p6a1fe3), so
    the provider comparison is one explicit alias rule while model and the 200 stay exact.

    J3 (pass-6, exact typing): the model and provider are compared on EXACT types and values. A `str`
    field equals only a `str`; a JSON integer `7` is NOT the string `"7"`. The old
    `str(usage.get("model", "")) != str(entry["model"])` coerced BOTH sides through `str()`, so a
    declared string model `"7"` accepted a usage row whose model was the integer `7`. Every field is
    now validated for shape before it is compared, and a type mismatch is a RECORDED rejection (never
    a match). The provider alias (`openai-codex` accepts an `openai*` relay id) applies only when
    BOTH sides are `str`, so a non-string provider can never alias into a match.
    """
    if not usage:
        return "no usage row appended after the attempt offset"
    status = usage.get("status")
    if isinstance(status, bool) or not isinstance(status, int):
        return (f"usage status is not an exact integer: "
                f"{type(status).__name__}={status!r}; only the integer 200 is accepted")
    if status != 200:
        return f"usage status is not 200: {status!r}"
    # --- model: exact type AND value (J3) -------------------------------------------------------
    want_model = entry.get("model")
    got_model = usage.get("model")
    if not isinstance(want_model, str):
        # The pool entry itself is malformed; refuse rather than coerce it into a match.
        return f"declared model is not a string: {type(want_model).__name__}={want_model!r}"
    if not isinstance(got_model, str):
        return (f"usage model is not a string: {type(got_model).__name__}={got_model!r}; "
                f"a non-string can never equal {want_model!r}")
    if got_model != want_model:
        return f"usage model mismatch: {got_model!r} is not {want_model!r}"
    # --- provider: exact string comparison plus ONE explicit alias rule (J3) --------------------
    want_prov = entry.get("provider")
    got_prov = usage.get("provider")
    if not isinstance(want_prov, str):
        return f"declared provider is not a string: {type(want_prov).__name__}={want_prov!r}"
    if not isinstance(got_prov, str):
        return (f"usage provider is not a string: {type(got_prov).__name__}={got_prov!r}; "
                f"a non-string can never equal {want_prov!r}")
    if want_prov == got_prov:
        return ""
    if want_prov == "openai-codex" and got_prov.startswith("openai"):
        return ""
    return f"usage provider mismatch: {got_prov!r} is not {want_prov!r}"


def receipt_matches(entry: dict, usage: dict | None) -> bool:
    """True only when `receipt_reject_reason` finds nothing to reject. A single decision point, so
    the verdict and its recorded reason can never disagree."""
    return receipt_reject_reason(entry, usage) == ""


def carrier_line_texts(raw_bytes) -> tuple[list[str], int]:
    """S3 (REQ-STRICT-DECLARATION-014): split the captured stream into COMPLETE carrier lines, as BYTES
    split on `b"\\n"` only, and return `(texts, undecodable_count)`.

    The wrapper normalizes the argument to a byte stream: an already-captured byte string is split on
    `b"\\n"`; a non-UTF-8-decodable TEXT (a surrogateescape decode) is recovered to its original bytes
    via `surrogateescape`, so the byte-level rule is applied identically whether the caller passes the
    preserved bytes or the surrogate text.

    A carrier counts as evidence only when it is a COMPLETE, LF/CRLF-terminated, strictly
    UTF-8-decodable JSON value read in full:
      * iterate as BYTES split on `b"\\n"` — never `str.splitlines()`, which also splits on U+2028,
        U+2029, `\\x85`, `\\x0b` and `\\x0c` and so invents line boundaries the NDJSON protocol has not;
      * a trailing fragment with NO terminator is NOT a row;
      * each line is decoded with `errors="strict"`: a line containing an invalid byte is NOT a row and
        is COUNTED (`carrier_lines_undecodable`, returned as the second element), never turned into a
        surrogate or U+FFFD;
      * the line's bytes are EXACTLY the bytes between the terminators (T1, pass 2): the ONLY thing
        removed is at most ONE trailing `\\r`, so a CRLF stream still parses. There is NO unrestricted
        pre-cleaning strip: a leading NEL (U+0085), a trailing U+2028, a trailing vertical tab
        (U+000B) or any other non-JSON-whitespace character reaches the parser unchanged and makes it
        fail -- which is the correct outcome, because those are not JSON whitespace. JSON defines its
        own insignificant whitespace (space, tab, LF, CR) and the PARSER decides, not a sanitizer.
    """
    if isinstance(raw_bytes, (bytes, bytearray)):
        blob = bytes(raw_bytes)
    elif isinstance(raw_bytes, str):
        # a `surrogateescape` decode round-trips to the exact original bytes (including a lone surrogate
        # for 0xFF); a strict-decodable text decodes back to the same bytes.
        blob = raw_bytes.encode("utf-8", "surrogateescape")
    else:
        raise TypeError(f"carrier stream must be bytes or str, not {type(raw_bytes).__name__}")
    texts: list[str] = []
    undecodable = 0
    n = len(blob)
    start = 0
    while start < n:
        nl = blob.find(b"\n", start)
        if nl == -1:
            break                          # an unterminated trailing fragment is NOT a row (S3)
        line = blob[start:nl]
        if line.endswith(b"\r"):
            line = line[:-1]               # strip ONE trailing CR so a CRLF stream still parses (T1)
        start = nl + 1
        # T1 (pass 2): NO `line.strip()`. The line is returned verbatim (minus at most one trailing CR);
        # an empty line yielded no text and is not a row, but that is decided by DECODING it to "" and
        # letting the caller's parser reject it, NOT by a pre-clean that deletes real characters.
        try:
            text = line.decode("utf-8", "strict")
        except UnicodeDecodeError:
            undecodable += 1               # not decodable -> NOT a row, counted, never substituted
            continue
        if text == "":
            continue                       # an empty line is not a row; skipped without any strip()
        texts.append(text)
    return texts, undecodable


def agent_message_texts(out) -> list[str]:
    """G1/H5/S3: extract the assistant-message TEXT from every `item.completed`/`agent_message` carrier,
    KEEPING ONLY JSON STRING values, and guarding every carrier access so a wrongly-shaped carrier
    yields no text instead of an exception.

    The stream is read by `carrier_line_texts` (S3): bytes split on `b"\\n"`, terminated-only, strictly
    UTF-8-decoded. A line that does not decode is dropped (never a surrogate/U+FFFD). `json.loads` is
    then applied to the decoded text. Pass-2 repairs land here:
      * T1: the decoded line is used EXACTLY as `carrier_line_texts` returned it -- there is NO
        `.strip()` pre-clean, so a leading NEL / trailing U+2028 / trailing U+000B reaches the parser
        and makes it fail. A blank or whitespace-only line simply does not start with `{` and yields
        no event, which is the parser's own decision, not a sanitizer's.
      * T2: the parse is `strict_json_loads`, so a carrier carrying the non-JSON constants
        `NaN`/`Infinity`/`-Infinity` RAISES and yields no event (never a permissive float).
      * T3: a parsed `text` carrying a surrogate code point (U+D800-U+DFFF), e.g. an escaped ``\\ud800``,
        is SKIPPED and COUNTED (`carrier_lines_surrogate`) -- a surrogate can never be searched as if
        it were the arm's message.
    Two pass-4 constraints still hold here:
      * no lossy decode MANUFACTURES a character into the searchable text; and
      * a truthy non-object `item` (e.g. JSON `true`/`5`/`"x"`/a list) made `item.get(...)` raise
        `AttributeError` - a fail-closed crash with no typed receipt (H5).
    Every value is validated for shape before it is read; a non-string `text`, or a carrier whose
    `item` is not an object, contributes nothing.
    """
    lines, _undecodable = carrier_line_texts(out)
    texts: list[str] = []
    for line in lines:
        if not line.startswith("{"):
            continue
        try:
            event = strict_json_loads(line)
        except Exception:
            continue
        if not isinstance(event, dict) or event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if not isinstance(item, dict):
            continue                      # H5: wrong-shaped carrier -> no text, no crash
        text = item.get("text")
        if item.get("type") == "agent_message" and isinstance(text, str):
            if has_surrogate(text):
                # T3: text carrying a surrogate code point never decides a verdict; skip and count it.
                _CARRIER_SURROGATE_COUNT[0] += 1
                continue
            texts.append(text)
    return texts


# T3 (pass 2): a process-local counter of carrier texts SKIPPED for carrying a surrogate code point.
# `agent_message_texts` increments it; a caller (run_candidate) reads it into the attempt receipt so a
# surrogate-bearing carrier is operator-visible and can never be a silent no-op.
_CARRIER_SURROGATE_COUNT = [0]


def reset_carrier_surrogate_count() -> None:
    _CARRIER_SURROGATE_COUNT[0] = 0


def carrier_surrogate_count() -> int:
    return _CARRIER_SURROGATE_COUNT[0]


def nonce_in_agent_message(out: str, nonce: str) -> bool:
    """The nonce must appear in an ASSISTANT message item - not merely anywhere in stdout.

    MEASURED (aborted first AO attempt): a plain `nonce in stdout` check returned true on a run that
    exited 1 with zero artifacts, i.e. the old check could be satisfied WITHOUT a successful turn.
    The exact carrier of that string was not captured (the killed run's stdout was lost), so no
    mechanism is asserted here; what is asserted is that the nonce is now read only out of an
    `item.completed` / `agent_message` item, i.e. a model-produced message (N1: a non-conforming
    answer is refused even though the usage receipt matched; N2: the happy path still passes).

    G1 (pass-3 checker false green): the searchable text may be used ONLY when it is a JSON STRING.
    The old code did `str(item.get("text", ""))`, so a JSON `null` became the string "None" and - with
    `--nonce None` - a message the child never emitted "satisfied" the nonce. The value "None" is not
    the defect; the coercion is. Any non-string shape (null, number, bool, object, array) yields NO
    text, and the substring test is never run against a coerced rendering.
    """
    return any(nonce in text for text in agent_message_texts(out))


def front_door_port(relay_base: str):
    """The door port when the dispatch is routed through a front door, else None (direct to the relay).

    Deliberately NOT a hardcoded port list: any port other than the relay's own 10101 is a door, so
    the field cannot silently misreport when a new door is introduced (it did: this said False while
    the turn went through 10105).
    """
    tail = str(relay_base).split("//", 1)[-1]
    host = tail.split("/", 1)[0]
    port = host.rsplit(":", 1)[-1] if ":" in host else ""
    return port if port.isdigit() and port != "10101" else None


# ---------------------------------------------------------------------------------------------
# Identity / health gate + non-mutation guard  (FAR-AO-INDEPENDENCE-20261010)
#
# MEASURED root cause of "the AO step is not a real independent check" (round FAR-OAUTH-WINDOW-20261010):
#   1. the dispatch kept only a 400-char stdout TAIL, so an AO verdict that did not land in the tail
#      was unrecoverable (receipt E3: ADVISORY_INCONCLUSIVE_FROM_RECORD);
#   2. the checker ran under a sandbox that refuses the model's own shell commands on this host, so
#      it could not re-derive anything and could only read what it was handed.
# A third defect is NOT a harness bug and is not fixed by code: all three lanes resolve to the same
# model, so maker==checker is possible by construction. That is recorded, not silently improved.
# ---------------------------------------------------------------------------------------------

IDENTITY_NONE = "none"          # key-auth arm: the relay holds the key; no human-attended identity
IDENTITY_CLI_LOGIN = "cli_login"    # the arm needs a CLI login in ITS OWN home
IDENTITY_RELAY_POOL = "relay_pool"  # the arm consumes the relay's ChatGPT subscription credential

ERR_IDENTITY_NOT_PREAUTHORIZED = "ERR_LANE_IDENTITY_NOT_PREAUTHORIZED"
ERR_RELAY_OAUTH_NEEDS_REAUTH = "ERR_RELAY_OAUTH_NEEDS_REAUTH"
ERR_CHECKER_MUTATED_SUBJECT = "ERR_CHECKER_MUTATED_SUBJECT"
# G3 (pass-3 checker false green): a guard root that RESOLVES but holds ZERO files proves nothing,
# yet it produced exit 0 / ok:true / mutated:false over a digest of []. Distinct from
# ERR_GUARD_ROOT_MISSING (a root that does not resolve): the CAUSES differ and a diagnosis must not
# conflate them.
ERR_GUARD_ROOT_EMPTY = "ERR_GUARD_ROOT_EMPTY"
# FIX 5 (false-green): a blank/whitespace-only --nonce makes the substring check vacuously true.
ERR_NONCE_EMPTY = "ERR_NONCE_EMPTY"
# H5 (pass-4) -> J4 (pass-6): a wrongly-shaped carrier (non-object `item`) must yield a TYPED refusal,
# not an uncaught AttributeError. As of pass 6 it is a per-attempt DIAGNOSTIC DETAIL (recorded as
# `carrier_shape_invalid` + `carrier_shape_invalid_detail` on the attempt), NOT a top-level code: the
# frozen requirement's precedence table (ERR_NO_ARM_EMITTED_NONCE vs generic exhausted) owns the top
# level. The constant is retained as the NAMED diagnostic tag so the detail is machine-greppable.
ERR_CARRIER_SHAPE_INVALID = "ERR_CARRIER_SHAPE_INVALID"
# H3 (pass-4) -> J4 (pass-6): a rewritten usage ledger is likewise a per-attempt DETAIL
# (`usage_ledger_rewritten` + `usage_receipt_reason`), never a top-level code.
ERR_USAGE_LEDGER_REWRITTEN = "ERR_USAGE_LEDGER_REWRITTEN"

# ---------------------------------------------------------------------------------------------
# Credential-posture gate  (REQ-HGK-GCM-APPLY-002 / round HGK-GCM-APPLY-20261013)
#
# L1 (the user-scope gitconfig default: `helper =` reset + `manager --no-ui`) is the STRUCTURAL
# control and holds whether or not this gate works. This gate is the SECOND layer, and it is the
# only layer that lives on the REAL lane path: `scripts/lane_launcher.sh` is invoked ONLY by the
# throwaway test harness `tests/w3_solution/lane_harness.py` (stub codex binaries, no production
# caller), so a control wired only there is DETECTION_ONLY. `run_candidate` is where a lane
# actually spawns (`subprocess.run` -> codex), so the control is placed here.
#
# The policy is SINGLE-SOURCED in the sibling gate `scripts/gcm-containment/lane_credential_posture.py`
# (itself built on the canonical classifier in `credential_preflight.py`). This file CONSUMES that
# gate's decision rather than re-deriving a second, weaker check: `declared_credential_posture_decision()`
# states whether the asymmetric policy is a provable function of the preflight verdict, and
# `run_candidate` falls back to that exact asymmetric mapping only if a deployed gate disagrees. The
# mapping is deliberately ASYMMETRIC and is stated, not hidden:
#   * FAIL (the effective resolution POSITIVELY reaches a prompt-capable interactive helper)
#     -> BLOCK. A lane runs unattended; if the helper can open a window, the run hangs with nobody
#     watching. Fail-closed on the danger is the whole point.
#   * INCONCLUSIVE (the detector could NOT reach a verdict - e.g. git could not be executed)
#     -> WARN on stderr with a typed code, then CONTINUE. Blocking here would turn a detector bug
#     into a lane outage, which violates the owner's low-resistance criterion; L1 still holds
#     structurally either way.
#   * PASS -> continue silently.
# ---------------------------------------------------------------------------------------------
ERR_CREDENTIAL_POSTURE_UNCONTAINED = "ERR_CREDENTIAL_POSTURE_UNCONTAINED"
DEFAULT_CREDENTIAL_POSTURE_GATE = ROOT / "scripts" / "gcm-containment" / "lane_credential_posture.py"


def declared_credential_posture_decision(verdict) -> str:
    """The declared asymmetric policy, single-sourced so a deployed gate cannot silently drift.

    Returns ``"BLOCK"`` / ``"WARN_CONTINUE"`` / ``"CONTINUE"`` for a gate-provided verdict. An
    UNKNOWN verdict maps to ``"WARN_CONTINUE"`` -- the fail-closed direction for the DETECTOR is to
    continue and warn, never to block a lane on a detector fault, and never to treat an unrecognised
    verdict as a pass.
    """
    if verdict == "FAIL":
        return "BLOCK"
    if verdict == "PASS":
        return "CONTINUE"
    return "WARN_CONTINUE"


def run_credential_posture_gate(gate_path=None, git_path=None, test_global=None) -> dict:
    """Run the side-effect-free GCM posture gate and return its raw decision document.

    The gate is executed as its OWN process (its own exit status, its own json) so nothing it reads
    leaks back into this process. NEVER raises for a detector fault: a missing script, an unparsable
    output or an unexpected exit is reported as INCONCLUSIVE with the WARN_CONTINUE decision, which
    the caller warns on and continues past. `git_path` / `test_global` are operator/test seams passed
    straight through to the gate's own `--git` / `--test-global` flags so the three-valued policy can
    be driven deterministically against a scratch posture with NO credential window; leaving them
    unset is the production posture (the gate auto-detects git and reads the real scopes).
    """
    script = Path(gate_path or DEFAULT_CREDENTIAL_POSTURE_GATE)
    if not script.is_file():
        return {"verdict": "INCONCLUSIVE", "decision": "WARN_CONTINUE",
                "reason": f"posture gate not found: {script}"}
    argv = [sys.executable, str(script), "--json"]
    if git_path:
        argv += ["--git", str(git_path)]
    if test_global:
        argv += ["--test-global", str(test_global)]
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", stdin=subprocess.DEVNULL, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"verdict": "INCONCLUSIVE", "decision": "WARN_CONTINUE",
                "reason": f"could not run the posture gate ({type(exc).__name__}): {exc}"}
    # Capture/propagate the gate's OWN stderr verbatim so an INCONCLUSIVE detector fault is
    # operator-visible even when run_candidate is exercised inside a captured process (a test
    # harness, a relay). This is a pure pass-through: no policy is re-derived here.
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    try:
        result = strict_json_loads(proc.stdout)
    except Exception as exc:
        return {"verdict": "INCONCLUSIVE", "decision": "WARN_CONTINUE",
                "reason": f"posture gate output was not JSON ({type(exc).__name__}); rc={proc.returncode}"}
    if not isinstance(result, dict) or result.get("verdict") not in ("PASS", "FAIL", "INCONCLUSIVE"):
        return {"verdict": "INCONCLUSIVE", "decision": "WARN_CONTINUE",
                "reason": f"posture gate returned no usable verdict (rc={proc.returncode})"}
    # Declared policy: the decision is a pure function of the verdict. If a deployed gate disagrees
    # with the declared mapping, DEFER to the declared mapping -- the dispatch path owns the policy
    # and must not be silently overridden by a drifted gate.
    result["declared_decision"] = declared_credential_posture_decision(result.get("verdict"))
    if result.get("decision") not in (None, result["declared_decision"]):
        result["decision_disagreement"] = {"gate": result.get("decision"),
                                           "declared": result["declared_decision"]}
        result["decision"] = result["declared_decision"]
    return result


class IdentityRefused(Exception):
    """Typed, fail-closed pre-spawn refusal. Carries the code so a caller can act without parsing."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class CredentialPostureRefused(Exception):
    """Typed, fail-closed pre-spawn refusal for a POSITIVELY uncontained credential posture.

    Raised from `run_candidate` and caught in `main()`: `run_candidate` is contractually an attempt
    RECORD, so a policy refusal must never masquerade as one (that would both corrupt the attempt
    list and misreport the posture as a model/usage result). Carries the raw preflight verdict so the
    refusal receipt can quote the offending helper and its origin.
    """

    def __init__(self, code: str, detail: str, posture: dict):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.posture = posture


def default_identity_requirement(entry: dict, lane: str) -> str:
    """Which identity this arm actually needs when the pool artifact does not declare one.

    MEASURED, and the reason an earlier draft was wrong: an arm routed through the relay with
    `-c openai_base_url=` consumes the RELAY's credential, NOT the lane home's CLI login. The lane
    home being `Not logged in` is therefore not a reason to refuse an `openai` arm - only a lane
    that has to reach OpenAI itself needs `cli_login`.
    """
    declared = entry.get("identity_requirement")
    if declared:
        return str(declared)
    return IDENTITY_RELAY_POOL if entry.get("provider") in ("openai-codex", "openai") else IDENTITY_NONE


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def emit_refusal(args, rec: dict) -> int:
    """Print a typed refusal and persist it. Exists so every refusal path returns the same shape."""
    # FIX 3 (C3): every refusal receipt records the resolved home and whether it is the declared
    # lane home. Injected here -- one code path -- so no emitter has to duplicate the pair by hand.
    rec = dict(rec)
    rec.update(home_isolation_fields(args))
    if getattr(args, "json_out", None):
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(rec, indent=2, ensure_ascii=False))
    return 4


def refusal_body(lane: str, code: str, detail, **extra) -> dict:
    rec = {"schema": SCHEMA, "ok": False, "lane": lane, "code": code, "detail": detail,
          "generated_utc": datetime.now(UTC).isoformat()}
    rec.update(extra)
    return rec


# ---------------------------------------------------------------------------------------------
# Phase C4 (round HGK-GCM-REPAIR-20261013): non-publication lanes are not authorized to write a
# remote. DETECTION_ONLY on the DECLARED dispatch path.
#
# This is a PRE-SPAWN check of the lane BRIEF for remote-write markers. It CANNOT stop a lane that
# calls `git push` from inside its own shell once spawned; it only refuses to *dispatch* a lane
# whose brief text carries the markers without an attached publication WorkOrder reference. Do not
# describe it as preventing unintended pushes; it is a detection surface on the declared path.
#
# It is SEPARATE from the credential-posture control: "no prompt" (a hang risk) and "no unintended
# push" (a write-authorization risk) are different failure modes, and closing the first does not
# close the second.
# ---------------------------------------------------------------------------------------------
REMOTE_WRITE_MARKERS = (
    "git push", "--force", "force-with-lease", "publish", "refs/heads",
)
# D6 (round HGK-GCM-REPAIR2-20261013): the alternation captures the BARE WorkOrder id for the
# labelled forms (`WorkOrder: WO-PUB-9` -> group(1) `WO-PUB-9`; `PUBLICATION WO: X-1` -> group(2)
# `X-1`). A bare `WO-...` token matches group(0) with no label to strip. `detect_publication_workorder`
# returns the id WITHOUT the label prefix; round 1 returned group(0) ("WorkOrder: WO-PUB-9") and
# relaxed the test to `assertIn` instead of fixing the extraction (D6/D7).
PUBLICATION_WO_RE = re.compile(
    # A labelled id must LOOK like an id (contains a digit) so ordinary prose ("no workorder here")
    # is not mistaken for an authorization (D6 boundary).
    r"(?:WO-[A-Za-z0-9-]+"
    r"|WorkOrder[:\s#-]*([A-Za-z]+-[A-Za-z0-9-]+|[A-Za-z]*[0-9][A-Za-z0-9]*)"
    r"|PUBLICATION[_ -]?WO[:\s#-]*([A-Za-z]+-[A-Za-z0-9-]+|[A-Za-z]*[0-9][A-Za-z0-9]*))",
    re.IGNORECASE)


def _read_text(path) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def detect_remote_write_markers(text: str) -> list[str]:
    """The remote-write markers present in `text`, in canonical order (case-insensitive, verbatim)."""
    low = (text or "").lower()
    return [m for m in REMOTE_WRITE_MARKERS if m.lower() in low]


def detect_publication_workorder(text: str) -> str | None:
    m = PUBLICATION_WO_RE.search(text or "")
    if not m:
        return None
    # Return the BARE id: group(0) for a bare `WO-...` token; the first populated capture group for
    # the labelled `WorkOrder`/`PUBLICATION WO` forms.
    for g in (1, 2):
        if m.group(g):
            return m.group(g)
    return m.group(0)


def remote_write_precheck(*, brief_text: str, publication_wo: str | None) -> dict:
    """Decide whether a DETECTION_ONLY remote-write refusal applies for this lane dispatch.

    Returns ``{"markers": [...], "publication_wo": ..., "would_refuse": bool}``. A refusal applies
    when the brief carries markers AND no publication WorkOrder reference is provided (neither by
    the ``--publication-workorder`` flag nor by a WorkOrder-looking token inside the brief).
    """
    markers = detect_remote_write_markers(brief_text)
    wo = publication_wo or detect_publication_workorder(brief_text)
    return {"markers": markers, "publication_wo": wo,
            "would_refuse": bool(markers) and not wo}


def find_terminal_marker(log_text: str) -> str | None:
    """The last ``EXIT=`` line in a lane log, or None. This is the "attempt ended" terminal marker
    written by the launcher (``echo "EXIT=${LANE_RC}" >> "$LOG"``) and by test harnesses."""
    last = None
    for line in (log_text or "").splitlines():
        s = line.strip()
        if s.startswith("EXIT="):
            last = s
    return last


def parse_exit_code(marker: str | None) -> int | None:
    if not marker or "=" not in marker:
        return None
    try:
        return int(marker.split("=", 1)[1].strip())
    except ValueError:
        return None


def persist_attempt_logs(log_dir, rank, out: str, err: str, run_id=None,
                         out_bytes=None, err_bytes=None) -> dict:
    """Write the FULL attempt output to disk and return its locators/digests.

    MEASURED defect this closes: the receipt kept a 400-char stdout tail, so the AO verdict and the
    digest it re-derived were unrecoverable (receipt E3 = ADVISORY_INCONCLUSIVE_FROM_RECORD).

    Two further defects a hostile review found and this version closes:
      * the child's RAW BYTES are persisted when available. Decoding with errors="replace" and
        re-encoding cannot be byte-exact (a non-UTF-8 byte becomes U+FFFD, then 3 bytes), so
        "byte-identical" would have been an over-claim.
      * the run id is part of the filename. Without it, re-running with the same --json-out silently
        overwrote the previous attempt's whole log.
    """
    meta: dict = {"attempt_log_dir": str(log_dir) if log_dir else None}
    if not log_dir:
        return meta
    d = Path(log_dir)
    d.mkdir(parents=True, exist_ok=True)
    prefix = f"{run_id}-" if run_id else ""
    for kind, text, raw in (("stdout", out, out_bytes), ("stderr", err, err_bytes)):
        fp = d / f"attempt-{prefix}{rank}-{kind}.txt"
        if raw is not None:
            fp.write_bytes(raw)                 # byte-exact: the child's own bytes, untouched
            meta[f"{kind}_byte_exact"] = True
        else:
            # newline="" keeps LF as LF: Windows' default translation would rewrite every \n as
            # \r\n, so the stored digest would describe bytes the CLI never emitted.
            fp.write_text(text, encoding="utf-8", errors="replace", newline="")
            meta[f"{kind}_byte_exact"] = False
        meta[f"{kind}_path"] = str(fp)
        meta[f"{kind}_bytes"] = fp.stat().st_size
        meta[f"{kind}_sha256"] = sha256_file(fp)
    return meta


def probe_cli_login(lane_home) -> tuple[bool, str]:
    """True when this home could serve a turn with NO interactive login.

    A hostile review was right that the first version accepted any truthy `tokens` dict, so an
    empty-string access token read as a credential. It now requires a NON-EMPTY string.
    """
    ah = Path(lane_home) / "auth.json"
    if not ah.is_file():
        return False, "no auth.json in the lane home"
    try:
        # T2 (pass 2): strict parse -- a credential document carrying a non-JSON constant must not be
        # read through a permissive parser default.
        data = strict_json_loads(ah.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"auth.json unreadable: {type(exc).__name__}"
    key = data.get("OPENAI_API_KEY")
    if isinstance(key, str) and key.strip():
        return True, "API key present"
    tokens = data.get("tokens") if isinstance(data.get("tokens"), dict) else {}
    for field in ("accessToken", "access_token", "id_token"):
        v = tokens.get(field)
        if isinstance(v, str) and v.strip():
            return True, f"non-empty {field} present"
    return False, "auth.json carries no non-empty credential"


_REAUTH_MARKERS = ("needs-reauth", "needs_reauth", "reauth_required", "reauthentication required")


def _refresh_material(obj) -> bool:
    """True only for a NON-EMPTY refresh token string anywhere in the document."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("refreshToken", "refresh_token") and isinstance(v, str) and v.strip():
                return True
            if _refresh_material(v):
                return True
    elif isinstance(obj, list):
        return any(_refresh_material(v) for v in obj)
    return False


def _reauth_requested(raw: str) -> bool:
    low = raw.lower()
    return any(m in low for m in _REAUTH_MARKERS)


def probe_relay_pool_health(relay_home) -> tuple[bool, str]:
    """True when the relay's subscription credential can still refresh WITHOUT a human.

    An expired ACCESS token is NORMAL and not a failure (the relay refreshes single-flight; measured
    healthy on 2026-10-10 with the human home's expiry in the past). What actually breaks unattended
    operation is a credential with no REFRESH material - that is the state that makes the relay
    answer `reauth_required` and puts a window in front of the operator.

    A hostile review was right that `"refreshToken" in raw` was only a SUBSTRING test: a literal
    `"refreshToken": null`, an empty string, or an account marked needs-reauth all read as healthy.
    This version parses the document, requires a NON-EMPTY refresh token, and treats an explicit
    re-auth marker as unhealthy. It still does NOT contact the relay - that ceiling is unchanged and
    stays disclosed, because the real verdict on an arm is the turn's usage receipt.
    """
    root = Path(relay_home)
    if not root.is_dir():
        return False, f"relay home not found: {root}"
    candidates = [p for p in (root / "auth.json", root / "codex-accounts.json") if p.is_file()]
    if not candidates:
        return False, "no relay credential file (auth.json / codex-accounts.json)"
    notes = []
    for p in candidates:
        try:
            raw = p.read_text(encoding="utf-8")
        except Exception as exc:
            return False, f"{p.name} unreadable: {type(exc).__name__}"
        if _reauth_requested(raw):
            notes.append(f"{p.name}: re-auth marker present")
            continue
        try:
            # T2 (pass 2): strict parse -- the relay credential document must not be read through a
            # permissive parser default either. A non-JSON constant makes it unparsable (no evidence).
            doc = strict_json_loads(raw)
        except Exception:
            notes.append(f"{p.name}: unparsable")
            continue
        if _refresh_material(doc):
            return True, f"non-empty refreshable credential present in {p.name}"
        notes.append(f"{p.name}: no non-empty refresh token")
    return False, "; ".join(notes) or "no refresh material"


def identity_check(entry: dict, lane: str, lane_home, relay_home,
                   probe_login=probe_cli_login, probe_relay=probe_relay_pool_health) -> dict:
    """Return the gate verdict for one arm. Raises IdentityRefused only when the arm must not run."""
    need = default_identity_requirement(entry, lane)
    if need == IDENTITY_NONE:
        return {"rank": entry.get("rank"), "provider": entry.get("provider"), "model": entry.get("model"),
                "requirement": need, "ok": True, "detail": "key-auth arm: no human-attended identity"}
    if need == IDENTITY_CLI_LOGIN:
        ok, detail = probe_login(lane_home)
        code = ERR_IDENTITY_NOT_PREAUTHORIZED
    elif need == IDENTITY_RELAY_POOL:
        ok, detail = probe_relay(relay_home)
        code = ERR_RELAY_OAUTH_NEEDS_REAUTH
    else:
        return {"rank": entry.get("rank"), "provider": entry.get("provider"), "model": entry.get("model"),
                "requirement": need, "ok": False, "detail": "unknown identity_requirement",
                "code": "ERR_LANE_IDENTITY_UNKNOWN"}
    verdict = {"rank": entry.get("rank"), "provider": entry.get("provider"), "model": entry.get("model"),
               "requirement": need, "ok": bool(ok), "detail": detail}
    if not ok:
        verdict["code"] = code
    return verdict


def snapshot_subject(roots) -> dict[str, str]:
    """Digest every file under each root (or the file itself), so mutation can be MEASURED."""
    snap: dict[str, str] = {}
    for root in roots or []:
        r = Path(root)
        if r.is_file():
            snap[str(r).replace("\\", "/")] = sha256_file(r)
        elif r.is_dir():
            for p in sorted(r.rglob("*")):
                if p.is_file():
                    snap[str(p).replace("\\", "/")] = sha256_file(p)
    return snap


def diff_subject(before: dict, after: dict) -> dict:
    """removed/changed VOID the verdict. `added` is recorded separately: a checker may legitimately
    write its OWN verdict file, and the subject roots are chosen to exclude that.

    H4 (pass-4 checker): an empty side of the snapshot proves nothing, yet `diff_subject({}, {})`
    returned `mutated: false` with no marker - a clean verdict produced from nothing. Whenever EITHER
    side is empty the comparison is INCONCLUSIVE, and `mutated` is NOT a clean `false`.
    """
    added = sorted(k for k in after if k not in before)
    removed = sorted(k for k in before if k not in after)
    changed = sorted(k for k in after if k in before and after[k] != before[k])
    mutated = bool(removed or changed)
    empty_side = (not before) or (not after)
    # A measured removal/change still VOIDS even when it empties the subject: the removal IS the
    # evidence. INCONCLUSIVE is reserved for a comparison that measured NOTHING (empty side, no
    # removed/changed), so a clean verdict can never be produced from nothing.
    verdict = "VOID" if mutated else ("INCONCLUSIVE" if empty_side else "CLEAN")
    out = {"files_before": len(before), "files_after": len(after),
           "added": added, "removed": removed, "changed": changed,
           "mutated": mutated,
           # `mutated_known` is False whenever a side is empty: even a measured removal leaves the
           # resulting subject's state unmeasurable, so the field never vouches for an empty side.
           # `mutated` itself stays honest about the measured removed/changed difference.
           "mutated_known": not empty_side,
           "inconclusive": empty_side,
           "verdict": verdict,
           "rule": "removed/changed => verdict void; added is recorded, not fatal; "
                   "an empty side => INCONCLUSIVE (never a clean verdict from nothing)"}
    if empty_side:
        out["inconclusive_reason"] = ("a snapshot side is empty, so mutation cannot be measured; "
                                      "this comparison is INCONCLUSIVE, not clean")
    return out


def _is_dispatchable(entry: dict) -> bool:
    """C2: does this arm's own declaration permit a spawn?

    NOT dispatchable when the artifact says so (`dispatchable is False`) or when the declared
    `feasibility` string starts with UNREACHABLE / CONFIG_COMPLETE_NOT_ACTIVATED. Every other value,
    including an absent one, stays dispatchable: a declaration must never over-block.
    """
    if entry.get("dispatchable") is False:
        return False
    feasibility = entry.get("feasibility")
    if isinstance(feasibility, str) and feasibility.startswith(
            ("UNREACHABLE", "CONFIG_COMPLETE_NOT_ACTIVATED")):
        return False
    return True


SKIP_REASON_NO_FEASIBILITY = "declared not dispatchable (no feasibility text)"


def _skip_reason(entry: dict, *, declared_not_dispatchable: bool = False) -> str:
    """C2/G2: the human-readable reason a skipped arm is recorded with. NEVER empty.

    G2 (pass-3 checker): the pass-2 fix only substituted for `None`, so an empty string,
    a whitespace-only string, and an empty array still produced an EMPTY `reason` - a skip with no
    reason. The feasibility text is used ONLY when it is a non-empty string AFTER STRIPPING; every
    other shape (None, "", whitespace-only, any non-string including an empty list) falls back to a
    literal declaration reason. Passing `declared_not_dispatchable=True` yields the explicit
    `dispatchable: false` explanation; otherwise the generic declaration reason is used.
    """
    feasibility = entry.get("feasibility")
    if isinstance(feasibility, str) and feasibility.strip():
        return feasibility
    if declared_not_dispatchable:
        return "declared not dispatchable (dispatchable: false)"
    return SKIP_REASON_NO_FEASIBILITY


def lane_home_isolation(lane_home, declared_lane_home) -> dict:
    """C3: is the resolved per-run Codex home the declared isolated lane home?

    A home is NON-isolated only when it is a DIFFERENT path from the declared lane home AND holds an
    `auth.json` (i.e. a login). Equality with the declared home is never non-isolated, whatever it
    holds.
    """
    is_declared = str(Path(lane_home).resolve()) == str(Path(declared_lane_home).resolve())
    has_auth = (Path(lane_home) / "auth.json").is_file()
    return {"codex_home_is_declared_lane_home": is_declared,
            "non_isolated": (not is_declared) and has_auth}


def home_isolation_fields(args) -> dict:
    """FIX 3/4 (C3): the resolved-home verdict EVERY receipt carries, computed from one place.

    The oracle requires every receipt -- including every refusal path -- to record the resolved Codex
    home and whether it is the declared lane home. The value is RESOLVED (FIX 4) so a relative
    `--codex-home .` is recorded as an absolute path, and the same resolved form feeds the comparison
    against the declared lane home.
    """
    resolved = Path(args.codex_home).resolve()
    iso = lane_home_isolation(resolved, DEFAULT_LANE_HOME)
    return {"codex_home": str(resolved),
            "codex_home_is_declared_lane_home": iso["codex_home_is_declared_lane_home"]}


def nonce_is_blank(nonce) -> bool:
    """FIX 5: an absent or whitespace-only nonce certifies nothing -- the substring test in
    nonce_in_agent_message would be vacuously true, so `--nonce ""` must be REFUSED, not treated as
    "the check is disabled"."""
    return not isinstance(nonce, str) or nonce.strip() == ""


def failure_disposition(attempts: list) -> dict:
    """C1: the failure code for a run that produced no usable turn, without conflating conditions.

    Kept additive: a run that answered (exit 0 + a valid usage receipt) but emitted no nonce reads
    ERR_NO_ARM_EMITTED_NONCE. EVERY case where no arm produced an acceptable turn -- including a run
    where every attempt timed out -- keeps the generic ERR_LANE_ALL_ROUTES_EXHAUSTED, per the frozen
    oracle. The timeout CASE is still MEASURED via `timed_out_arms` (an additive field), but the CODE
    is never ERR_ALL_ATTEMPTS_TIMED_OUT (that constant/branch is removed, not left dead). Returns
    receipt fields to merge.

    I3 (pass-5): the FROZEN oracle's C1 classification TAKES PRECEDENCE. A turn with exit 0, a valid
    usage receipt and no nonce is ERR_NO_ARM_EMITTED_NONCE + nonce_absent_arms whatever the carrier
    shape was -- an invalid carrier merely means the TEXT is absent, which is exactly "emitted no
    nonce". A rewritten-ledger attempt zeroes its own `rec_ok`, so it never counts as `answered` here.

    J4 (pass-6, code precedence): the top level emits ONLY a code derivable from the frozen
    requirement's table -- ERR_NO_ARM_EMITTED_NONCE when some arm produced an acceptable turn, else
    the generic ERR_LANE_ALL_ROUTES_EXHAUSTED. The pass-4 diagnostics (ERR_CARRIER_SHAPE_INVALID /
    ERR_USAGE_LEDGER_REWRITTEN) are NO LONGER top-level codes: they are per-attempt DETAIL fields
    (each attempt already carries `carrier_shape_invalid` / `usage_ledger_rewritten` and its own
    `usage_receipt_reason`), so a diagnostic can never outrank the requirement's classification.
    """
    answered = [a for a in attempts if a.get("exit") == 0 and a.get("usage_receipt_ok")]
    if answered and not any(a.get("nonce_present") for a in answered):
        return {"code": "ERR_NO_ARM_EMITTED_NONCE",
                "nonce_absent_arms": [f"{a.get('provider')}/{a.get('model')}" for a in answered]}
    fields: dict = {"code": "ERR_LANE_ALL_ROUTES_EXHAUSTED"}
    if attempts and all(a.get("exit") == "TIMEOUT" for a in attempts):
        fields["timed_out_arms"] = [f"{a.get('provider')}/{a.get('model')}" for a in attempts]
    return fields


def run_candidate(entry: dict, args, codex: str, lane_home: Path, attempt_log_dir=None,
                  run_id=None) -> dict:
    sandbox = args.sandbox or SANDBOX_BY_LANE.get(args.lane, "read-only")
    # PROBE/TEST SEAM: a .py child runs under this interpreter (Windows CreateProcess cannot launch a
    # .py/.bat directly). It exists so the non-mutation guard's VOID path can be exercised end-to-end
    # and deterministically, with no model in the loop; the extra codex argv is ignored by the stub.
    launcher = [sys.executable, str(codex)] if str(codex).endswith(".py") else [codex]
    cmd = launcher + ["--model", str(entry["transport_model"]),
           "--sandbox", sandbox, "--ask-for-approval", "never",
           "-c", f"openai_base_url={args.relay_base}",
           "--cd", str(args.cwd or ROOT)]
    if entry.get("reasoning_effort"):
        cmd += ["-c", f"model_reasoning_effort={entry['reasoning_effort']}"]
    # FAR-LANE-REPAIR-20261014 (R-A): declare the lane home's Windows sandbox level on the child argv.
    # The value comes from the DECLARED pool (codex_home_config), so the injection is declaration-driven
    # and cannot be omitted at a call site. Injected BEFORE --codex-arg, so an explicit pass-through
    # token still lands later in argv (codex resolves repeated -c in order).
    _hc = getattr(args, "codex_home_config", None) or {}
    _ws = _hc.get("windows_sandbox")
    _modes = _hc.get("required_for_modes") or ["read-only", "workspace-write"]
    if _ws and sandbox in _modes:
        cmd += ["-c", f'windows.sandbox="{_ws}"']
    if getattr(args, "codex_arg", None):
        cmd += list(args.codex_arg)  # raw pass-through tokens, order preserved (bounded experiments only)
    cmd += ["exec", "--skip-git-repo-check", "--ephemeral", "--json", args.prompt]

    env = dict(os.environ)
    env["CODEX_HOME"] = str(lane_home)
    env["HERMES_CODEX_HOME"] = str(lane_home)
    # (a) REQ-HGK-GCM-APPLY-002: a lane runs UNATTENDED. The L1 user-scope gitconfig reset is the
    # structural control; the previous round's deterministic seam S2 proved that when the credential
    # helper returns nothing, git falls back to its OWN prompt path (askpass / the controlling
    # terminal). For a lane nobody is watching, that fallback is a HANG. `GIT_TERMINAL_PROMPT=0`
    # closes the surface BELOW L1 for every git call the child makes, so git fails fast instead of
    # waiting on a terminal that is not there.
    env["GIT_TERMINAL_PROMPT"] = "0"

    # (c) A WINDOWS-USABLE TEMP ROOT FOR THE CHILD. Measured 2026-10-21: on this host the shell
    # exports TMPDIR=/tmp (an MSYS virtual path). A native Windows child (python.exe, pytest) cannot
    # use it: `tempfile.mkdtemp` fails with "No usable temporary directory found", so a checker lane
    # that is asked to re-derive a test-suite result CANNOT run it and must mark the claim
    # UNVERIFIABLE -- a tooling limit dressed up as an evidence gap. The lane's own scratch root is
    # a real Windows path and is already the sanctioned write surface for lane temp files, so the
    # child is given it explicitly. Read-only lanes still get a writable TEMP: this is a temp
    # scratch, not a write to the governed tree, and the non-mutation guard (which digests the
    # governed files before and after) remains the bound that matters.
    _scratch_root = getattr(args, "lane_scratch", None) or os.environ.get("HGK_LANE_SCRATCH")
    if not _scratch_root:
        _scratch_root = str((ROOT / "var" / "far-lane-sod-003" / "scratch")
                            if (ROOT / "var" / "far-lane-sod-003").exists()
                            else (Path(lane_home) / "scratch"))
    try:
        Path(_scratch_root).mkdir(parents=True, exist_ok=True)
    except Exception:
        _scratch_root = None
    if _scratch_root:
        for _k in ("TMPDIR", "TEMP", "TMP"):
            env[_k] = _scratch_root
    env["HGK_LANE_SCRATCH"] = _scratch_root or ""
    # (d) NO BYTECODE, NO PYTEST CACHE. Measured 2026-10-21: with a read-only sandbox the child
    # still tried to write `__pycache__` next to site-packages and aborted with
    #   PermissionError: [Errno 13] Permission denied: ...\site-packages\sniffio\__init__.py
    # which reads as a broken suite rather than a blocked bytecode write. These two variables make
    # the child write NO bytecode and keep pytest's cache out of the package tree, so a checker lane
    # can actually execute a suite. The pytest tmp fixture still lands in the lane scratch root.
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_ADDOPTS"] = (env.get("PYTEST_ADDOPTS", "") + " -p no:cacheprovider").strip()

    # (b) fail-closed posture gate BEFORE the spawn. Asymmetric policy (see
    # run_credential_posture_gate): FAIL blocks, INCONCLUSIVE warns and continues, PASS is silent.
    # This is the consumer that moves the control from a test-only launcher onto the REAL lane path
    # (run_candidate is where a lane actually spawns codex). The gate is the REUSED sibling module
    # scripts/gcm-containment/lane_credential_posture.py.
    posture = run_credential_posture_gate(
        gate_path=getattr(args, "credential_posture_gate", None),
        git_path=getattr(args, "credential_posture_gate_git", None),
        test_global=getattr(args, "credential_posture_gate_test_global", None))
    posture_verdict = posture.get("verdict")
    decision = posture.get("decision")
    posture_fields = {"verdict": posture_verdict, "decision": decision,
                      "reason": posture.get("reason"),
                      "prompt_capable_helper": posture.get("helper") or posture.get("prompt_capable_helper"),
                      "origin": posture.get("origin"),
                      "git_terminal_prompt": env.get("GIT_TERMINAL_PROMPT")}
    if decision == "BLOCK":
        # POSITIVELY violated: the effective resolution still reaches a prompt-capable interactive
        # helper. Fail-closed on the danger -- name the helper and its origin file, then DO NOT spawn.
        raise CredentialPostureRefused(
            ERR_CREDENTIAL_POSTURE_UNCONTAINED,
            f"the effective credential-helper resolution reaches a prompt-capable helper "
            f"{posture_fields['prompt_capable_helper']!r} from "
            f"{posture.get('origin') or 'unknown origin'}; {posture.get('reason')}",
            posture_fields)
    if decision == "WARN_CONTINUE":
        # The detector could not reach a verdict. Deliberately NOT fail-closed: turning a detector
        # bug into a lane outage would violate the owner's low-resistance criterion. L1 still holds.
        print(f"WARN_LANE_CREDENTIAL_POSTURE_INCONCLUSIVE: credential posture could not be decided "
              f"({posture.get('reason')}); CONTINUING (a detector fault must not become a lane "
              f"outage; L1 remains the structural control; INCONCLUSIVE is NOT a pass).",
              file=sys.stderr)
    usage_path = Path(args.usage)
    offset = usage_path.stat().st_size if usage_path.is_file() else 0
    # I1: capture BOTH the offset and a digest of the pre-turn bytes `[0:offset)`. The size-only check
    # cannot see a rewrite that shifts the prefix and copies a stale row PAST the offset (the file
    # GROWS); the digest of the exact prefix can, and does.
    prefix_digest_before = usage_prefix_digest(usage_path, offset)
    t0 = time.time()
    timed_out = False
    try:
        # stdin=DEVNULL matters: `codex exec` reads stdin ("Reading additional input from stdin...")
        # and blocks forever when the parent's stdin is an open pipe that never closes - which is
        # exactly what a background shell provides. The prompt travels as an argv argument, so the
        # child must simply see EOF.
        p = subprocess.run(cmd, capture_output=True, timeout=args.timeout, env=env,
                           stdin=subprocess.DEVNULL)
        rc = p.returncode
        out_b, err_b = p.stdout or b"", p.stderr or b""
        # decode ONLY for parsing/tails; the raw bytes are what gets persisted (see
        # persist_attempt_logs: text=True + errors="replace" loses bytes and translates newlines
        # BEFORE any file is written, which made "byte-identical" untrue).
        out = out_b.decode("utf-8", errors="replace")
        err = err_b.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired as exc:
        # P1-B TIMEOUT-CAPTURE (owner-ordered reuse of the Convergence candidate patch,
        # round FAR-LANE-REUSE-RCA-20261015): subprocess.TimeoutExpired carries whatever the
        # child already wrote to stdout/stderr before it was killed. The old branch forced
        # the streams to b"" / "", so a timed-out attempt was persisted with 0 bytes and an
        # empty tail and the child's diagnostics were lost -- the exact blindness that turned
        # "one stale binary pin" into "the whole lane looks broken". Preserve the bytes
        # already read; the timeout CLASSIFICATION is unchanged (exit "TIMEOUT", no nonce,
        # usage_receipt_ok=false) -- a timeout stays a FAIL, it just stops being silent.
        timed_out = True
        rc = "TIMEOUT"
        out_b = exc.stdout if isinstance(exc.stdout, bytes) else (exc.stdout or b"")
        err_b = exc.stderr if isinstance(exc.stderr, bytes) else (exc.stderr or b"")
        out = out_b.decode("utf-8", errors="replace")
        err = err_b.decode("utf-8", errors="replace")
    dur = round(time.time() - t0, 2)
    # H1 (pass-4 checker false green): the nonce verdict is decided on the PRESERVED BYTES.
    # `errors="replace"` manufactures U+FFFD (so a raw 0xFF "satisfied" a U+FFFD nonce), and the old
    # "raw stdout" check searched the DECODED string. The binding signal is now
    # `nonce.encode("utf-8") in raw_stdout_bytes`; the text is decoded with "surrogateescape" (which
    # never manufactures a character) for the carrier signal, and `nonce_present` requires BOTH. In
    # particular, a byte that is not valid UTF-8 becomes a lone surrogate, so a real U+FFFD nonce is
    # found only when the child actually emitted the three bytes EF BF BD.
    nonce_bytes = args.nonce.encode("utf-8")
    nonce_raw = nonce_bytes in out_b
    # S3: the carrier extraction reads the stream as COMPLETE, LF/CRLF-terminated, strictly-UTF-8
    # lines (never str.splitlines()); `nonce_in_agent_message` therefore accepts the PRESERVED BYTES
    # directly and cannot be satisfied by a split-invented, unterminated or invalid-UTF-8 fragment.
    # T3 (pass 2): reset the surrogate-skip counter immediately before the extraction that decides the
    # nonce, so the count recorded on this attempt describes exactly this turn's carrier read.
    reset_carrier_surrogate_count()
    nonce_ok = nonce_in_agent_message(out_b, args.nonce) and nonce_raw
    carrier_surrogate = carrier_surrogate_count()

    # H5 (pass-4 checker) + S3: a wrongly-shaped carrier must produce a TYPED refusal rather than an
    # uncaught exception, and a line that is not strictly decodable is NOT a carrier at all -- it is
    # DROPPED and COUNTED (`carrier_lines_undecodable`), never turned into a surrogate or U+FFFD and
    # never treated as a wrong-shaped carrier. Shape validation never runs twice: it is the same
    # extraction the nonce verdict already performed.
    carrier_lines, carrier_undecodable = carrier_line_texts(out_b)
    carrier_shape_invalid = False
    for line in carrier_lines:
        if not line.startswith("{"):
            continue
        try:
            event = strict_json_loads(line)
        except Exception:
            continue
        if isinstance(event, dict) and event.get("type") == "item.completed" \
                and "item" in event and event.get("item") is not None and not isinstance(event.get("item"), dict):
            carrier_shape_invalid = True
            break

    # H3 (pass-4) + I1 (pass-5): a ledger that SHRANK below the captured offset was rewritten/
    # truncated; a ledger whose pre-offset prefix is no longer byte-identical (even if it GREW) was
    # rewritten/shifted. Both reviving a stale row as this turn's receipt are forbidden. The content
    # check is the pass-5 generalization of the size check: `rewritten` is now true for a GROWING
    # ledger too, and there is NEVER a re-read/recompute of the offset to "recover".
    ledger_rewritten = False
    rewritten_note = None
    if usage_path.is_file():
        size_now = usage_path.stat().st_size
        if size_now < offset:
            ledger_rewritten = True
            rewritten_note = ("the usage ledger shrank below the captured offset; it was rewritten or "
                              "truncated, so no row can be bound to this attempt")
        elif usage_prefix_digest(usage_path, offset) != prefix_digest_before:
            ledger_rewritten = True
            rewritten_note = ("the usage ledger's pre-turn bytes [0:offset) are no longer byte-"
                              "identical: the ledger was rewritten (a pre-offset byte was shifted or "
                              "replaced), so a row appended past the offset cannot be bound to THIS "
                              "attempt; the file SIZE alone cannot see this")
    # J1/J2: parse the appended region as COMPLETE, line-boundary-anchored lines, strictly decoded.
    # `spans` holds only bytes that begin on a line boundary (when offset > 0) and end with a
    # terminator; `undecodable_count` counts appended lines that failed strict UTF-8 decoding and were
    # therefore skipped -- never substituted into a comparable value.
    spans = usage_spans_since(usage_path, offset)
    rows_all, undecodable_count = decode_usage_spans(spans)
    # I2: a row of ANY wrong shape (a nonempty array, a bare `true`, a string, an integer) must be
    # SKIPPED and COUNTED -- never handed to a `.get`-based parser that crashes the surface with no
    # receipt. The count is recorded on the attempt (`usage_rows_shape_invalid`) and read back into
    # the top-level receipt.
    rows = [r for r in rows_all if is_usage_row_shaped(r)]
    shape_invalid_count = len(rows_all) - len(rows)
    matched = None
    observed = None
    reject_reason = ""
    if ledger_rewritten:
        reject_reason = rewritten_note
    elif rows:
        observed = next(reversed(rows))
        matched = next((r for r in reversed(rows) if receipt_matches(entry, r)), None)
        if matched is None:
            reject_reason = receipt_reject_reason(entry, observed)
    else:
        reject_reason = "no usage row was appended after the attempt offset"
        if shape_invalid_count:
            reject_reason += (f"; {shape_invalid_count} appended row(s) had a non-object shape and "
                              f"were skipped (never treated as a receipt)")
    if undecodable_count:
        reject_reason += (f"; {undecodable_count} appended line(s) were not valid UTF-8 and were "
                          f"skipped (never substituted, never compared)")
    rec_ok = (matched is not None) and not ledger_rewritten

    log_meta = persist_attempt_logs(attempt_log_dir, entry["rank"], out, err, run_id=run_id,
                                    out_bytes=out_b, err_bytes=err_b)

    attempt = {"rank": entry["rank"], "provider": entry["provider"], "model": entry["model"],
            "transport_model": entry["transport_model"], "sandbox": sandbox,
            "reasoning_effort": entry.get("reasoning_effort"), "exit": rc, "timed_out": timed_out,
            "seconds": dur, "nonce_present": nonce_ok, "nonce_present_raw_stdout": nonce_raw,
            "nonce_source": "item.completed/agent_message",
            "usage_rows_after_offset": len(rows), "usage_offset": offset,
            "usage_provider": (matched or {}).get("provider"), "usage_model": (matched or {}).get("model"),
            # The observed (even if rejected) row's status is preserved so an operator sees WHY a
            # receipt was refused (H2: `status:200.9` must be visible, not silently dropped).
            "usage_status": (matched or observed or {}).get("status"), "usage_receipt_ok": rec_ok,
            "usage_receipt_reason": reject_reason,
            "usage_ledger_rewritten": ledger_rewritten,
            "usage_rows_shape_invalid": shape_invalid_count,
            "usage_rows_undecodable": undecodable_count,
            # S3: count of captured-stream lines that FAILED strict UTF-8 decoding and were skipped
            # (never substituted, never a carrier). Operator-visible so a dropped line is not silent.
            "carrier_lines_undecodable": carrier_undecodable,
            # T3 (pass 2): count of carrier texts SKIPPED for carrying a surrogate code point
            # (U+D800-U+DFFF). Such text never decides a verdict; the count keeps the skip visible.
            "carrier_lines_surrogate": carrier_surrogate,
            # (c) REQ-HGK-GCM-APPLY-002: the credential posture ACTUALLY in force for THIS attempt,
            # read back from the attempt record rather than asserted in prose. `git_terminal_prompt`
            # is read from the SAME env dict handed to the child, so it is evidence of what the child
            # received, not of what the source says.
            "credential_posture": posture_fields,
            **log_meta,
            "stdout_tail": out[-400:], "stderr_tail": err[-300:]}
    if carrier_shape_invalid:
        # J4 (pass-6): a wrong-shaped carrier is a DIAGNOSTIC about the TEXT, recorded as a per-
        # attempt DETAIL -- never as a top-level code. `failure_disposition` owns the top-level
        # precedence table (ERR_NO_ARM_EMITTED_NONCE vs the generic exhausted code); the shape detail
        # here, like `usage_ledger_rewritten` and `usage_receipt_reason`, is additive evidence an
        # operator reads. An invalid carrier means the TEXT is absent, which is exactly "emitted no
        # nonce", so it must neither overwrite the usage MEASUREMENT nor outrank C1.
        attempt["carrier_shape_invalid"] = True
        attempt["carrier_shape_invalid_detail"] = (
            "an item.completed carrier's `item` was present but not an object; its text can never be "
            "read, so the nonce/TEXT signal is absent (a diagnostic, not a top-level code)")
        attempt["nonce_present"] = False
        if ledger_rewritten:
            attempt["usage_receipt_ok"] = False
    return attempt


def _authorization_spine():
    """Open the canonical Shared Spine for the D4 single-use authorization claim.

    Returns ``(spine, None)`` on success or ``(None, detail)`` when the Spine/claim helper cannot be
    reached. A caller MUST refuse when this returns a detail: an unacquirable boundary is a refusal,
    never a silent "no budget" pass.
    """
    if _authz is None:
        return None, "the authorization_claim helper could not be imported"
    try:
        SharedSpine = _authz._load_spine(ROOT)
        # An explicit override keeps the boundary testable against a throwaway Spine DB (and lets an
        # operator point the claim at an isolated DB); otherwise the canonical Shared Spine is used.
        db = Path(os.environ.get("HGK_SPINE_DB") or SPINE_DB)
        schema = Path(os.environ.get("HGK_SPINE_SCHEMA") or SPINE_SCHEMA)
        return SharedSpine(db, schema), None
    except Exception as exc:  # noqa: BLE001 - surface the reason; do not fall through to a pass
        return None, f"{type(exc).__name__}: {exc}"


def _resolve_completion_evidence(att, binding, root=None):
    """D2c: resolve the DELIVERABLE the WO binding declares and verify completion evidence.

    Returns ``None`` when the turn may complete, else a named refusal string. Fail-closed: an attempt
    whose raw stdout proves a matching usage receipt but whose declared deliverable is missing, empty,
    or digest-mismatched is REFUSED -- the FAR finding is that a matching usage receipt is NOT work.
    ``binding`` is the validated role binding; ``binding["deliverable"]`` is
    ``{"path": <root-relative>, "sha256": <64-hex>}``. ``root`` is the admitted writable root.
    """
    spec = (binding or {}).get("deliverable") or {}
    rel = spec.get("path") if isinstance(spec, dict) else None
    claimed = spec.get("sha256") if isinstance(spec, dict) else None
    base = Path(root) if root else ROOT
    data = None
    if rel:
        p = (base / rel)
        try:
            if p.is_file():
                data = p.read_bytes()
        except OSError:
            data = None
    raw = b""
    if att.get("stdout_path"):
        try:
            raw = Path(att["stdout_path"]).read_bytes()
        except OSError:
            raw = b""
    return _role_binding.verify_completion_evidence(
        raw_stdout=raw, deliverable_bytes=data,
        deliverable_digest_hex=claimed,
        binding={"workorder": (binding or {}).get("workorder"),
                 "session": (binding or {}).get("session"),
                 "subject": (binding or {}).get("subject")})


def main() -> int:
    ap = argparse.ArgumentParser(prog="hgk-lane-dispatch.py")
    ap.add_argument("--lane", required=True, help="PLAN | EXECUTE | VERIFY_SECURITY (validated in-contract)")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--nonce", default="HGK_LANE_NONCE_OK")
    ap.add_argument("--pool", default=str(DEFAULT_POOL))
    ap.add_argument("--codex-home", default=str(DEFAULT_LANE_HOME))
    ap.add_argument("--codex-executable", default=None,
                    help="PROBE/TEST SEAM: override the lane's child executable (a value ending in .py is "
                         "launched with this interpreter). Used to exercise the non-mutation guard's VOID "
                         "path deterministically with NO model in the loop. Default: config/hermes-codex-lane"
                         ".json. NOTE this widens what a caller can execute -- it is an operator tool.")
    ap.add_argument("--usage", default=str(DEFAULT_USAGE))
    ap.add_argument("--relay-base", default=DEFAULT_RELAY)
    ap.add_argument("--sandbox", default=None)
    ap.add_argument("--allow-sandbox-escalation", action="store_true",
                    help="required to use a sandbox stricter-than-role than the lane default")
    ap.add_argument("--cwd", default=None, help="workspace root for the Codex turn (default: the repo root)")
    ap.add_argument("--lane-scratch", default=None,
                    help="a WINDOWS-USABLE temp root handed to the child as TMPDIR/TEMP/TMP. The host shell "
                         "exports TMPDIR=/tmp (an MSYS virtual path) which a native Windows child cannot use, "
                         "so `tempfile.mkdtemp` fails and a checker lane cannot re-derive a test-suite result. "
                         "Default: <repo>/var/far-lane-sod-003/scratch when it exists, else <lane_home>/scratch.")
    ap.add_argument("--force-rank", type=int, default=None)
    ap.add_argument("--inject-429-first", action="store_true")
    ap.add_argument("--codex-arg", action="append", default=None,
                    help="extra raw argv tokens appended verbatim to the codex invocation (repeatable; "
                         "for bounded experiments such as -c prefer_websockets=false)")
    ap.add_argument("--max-candidates", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--attempt-log-dir", default=None,
                    help="persist each attempt's FULL stdout/stderr here + hash it into the receipt "
                         "(the receipt's own tails are 400/300 chars and lose evidence)")
    ap.add_argument("--relay-home", default=None,
                    help="relay home holding the ChatGPT pool credential (default: %%LOCALAPPDATA%%\\HG-KSEOS\\opencodex-hermes)")
    ap.add_argument("--no-identity-gate", action="store_true",
                    help="skip the pre-spawn identity/health gate (bounded experiments only; recorded in the receipt)")
    ap.add_argument("--require-arm", default=None,
                    help="provider/model that MUST survive the gate; if it is refused the run fails closed "
                         "instead of silently degrading to another arm (owner ruling: keep the OAuth arm unattended)")
    ap.add_argument("--guard-subject", action="append", default=None,
                    help="file/dir whose digest must not change during the turn (repeatable). removed/changed "
                         "=> the verdict is VOID; this is what makes an escalated-sandbox checker safe")
    ap.add_argument("--allow-unguarded-escalation", action="store_true",
                    help="permit an escalated lane with no --guard-subject; the exception is recorded "
                         "in the receipt instead of being silently allowed")
    ap.add_argument("--allow-human-home-transport", action="store_true",
                    help="acknowledges that the run points --codex-home at a home holding a login, so "
                         "the key-auth arms' 'no human-attended identity' claim is NOT being made for "
                         "this run (without it, a non-isolated home refuses before any spawn)")
    ap.add_argument("--credential-posture-gate", default=None,
                    help="path to the GCM lane credential-posture gate "
                         "(default: scripts/gcm-containment/lane_credential_posture.py). Operator/test seam.")
    ap.add_argument("--credential-posture-gate-git", default=None,
                    help="TEST-ONLY seam: pass a git executable to the posture gate --git so a "
                         "nonexistent binary can exercise the INCONCLUSIVE branch with no window.")
    ap.add_argument("--credential-posture-gate-test-global", default=None,
                    help="TEST-ONLY seam: pass --test-global to the posture gate so FAIL/PASS are "
                         "driven with a scratch git global and NO real credential request (zero windows).")
    ap.add_argument("--round", default=None,
                    help="round name; when set, the lane output dir is derived as "
                         "var/<round>/<lane>/attempt-<n>-<utc-ts> (C1) instead of an arbitrary path")
    ap.add_argument("--attempt", type=int, default=None,
                    help="explicit attempt number for the derived output dir (default: derived from "
                         "the existing attempt markers under var/<round>/<lane>/)")
    ap.add_argument("--output-root", default=None,
                    help="override the directory that holds the round (default: <repo>/var)")
    ap.add_argument("--prior-attempt-dir", default=None,
                    help="the previous attempt's output dir; a repair/retry refuses to spawn while "
                         "that attempt's process is still alive or its log has no EXIT= marker (C3)")
    ap.add_argument("--prior-attempt-log", default=None,
                    help="the previous attempt's log file; the C3 terminal-marker check reads here")
    ap.add_argument("--prior-attempt-pid", type=int, default=None,
                    help="the previous attempt's OS pid (D5). Used when the prior dir has no attempt "
                         "marker; a real process-liveness check on this pid is MANDATORY or the "
                         "dispatch refuses. Never treated as a decorative marker.")
    ap.add_argument("--allow-unverified-prior-gone", action="store_true",
                    help="D5 escape hatch (recorded): proceed when the prior process liveness could "
                         "NOT be proven. Without it, 'cannot prove the prior pid is gone' is a REFUSAL, "
                         "not a pass. This exists only to drive a deterministic positive control.")
    ap.add_argument("--brief", default=None,
                    help="path to the lane BRIEF text; enables the DETECTION_ONLY remote-write "
                         "pre-check (C4). When unset, no brief-level detection runs.")
    ap.add_argument("--publication-workorder", default=None,
                    help="a publication WorkOrder reference; when present, a brief that carries "
                         "remote-write markers is authorized for this dispatch (C4)")
    ap.add_argument("--authorization-resource", default=None,
                    help="the single-use authorization resource id (D4). When set, the dispatcher "
                         "ACQUIRES this Spine lease before any spawn and CONSUMES it after a "
                         "successful spawn; a resource already consumed by a prior spawn is refused.")
    ap.add_argument("--authorization-ttl", type=int, default=900,
                    help="TTL (s) of the in-flight authorization window lease (D4; anti-deadlock bound)")
    ap.add_argument("--no-authorization-claim", action="store_true",
                    help="skip the D4 single-use authorization claim entirely (recorded in the "
                         "receipt; for tests/back-compat where no round budget is named)")
    ap.add_argument("--role-binding-file", default=None,
                    help="Tranche A/B: path to the persisted per-round role binding (carried by "
                         "TaskSpec permissions_json[role_binding]). When present, the lane's required "
                         "arm AND rank are DERIVED from this one document before spawn; a caller "
                         "--require-arm/--force-rank that contradicts it is refused. Requires "
                         "--round to cross-check the round.")
    ap.add_argument("--workorder", default=None,
                    help="the canonical WorkOrder whose persisted role_binding is the authority for a "
                         "bound (role-binding) dispatch. Required whenever a role binding is in play.")
    # ---- D-06: SP identity at PRE-SPAWN (R13 follow-through) ------------------------------------
    # Deliberately NOT --workorder: --workorder is the ROLE-BINDING authority and it derives the arm
    # and rank for the turn. The SP identity only JOINs the chain (it reads ids back from the spine to
    # bind the invocation), so it must not be able to move the arm selection, and the two authorities
    # must never be half-supplied.
    ap.add_argument("--sp-identity", default=None,
                    help="SP identity to bind PRE-SPAWN: challenge (VERIFY_SECURITY) | commander (PLAN). "
                         "The registry holds the lane binding and the procedure path; a mismatch, an "
                         "unusable procedure or a nonce that is not the invocation id refuses with zero "
                         "attempts instead of dispatching an identityless turn.")
    ap.add_argument("--sp-invocation-id", default=None,
                    help="this invocation's id (SPINV-<TAG>-<12 hex>); REQUIRED with --sp-identity and "
                         "must equal --nonce, so the existing nonce oracle is what proves the child "
                         "received the identity block. Mint one with hgk_sp_identity.new_invocation_id().")
    ap.add_argument("--sp-workorder", default=None,
                    help="optional chain join: the WorkOrder whose spine ids are read back and carried "
                         "in the identity block. Unknown id / unreadable spine is a typed refusal.")
    ap.add_argument("--sp-skills-root", default=None,
                    help="root holding the SP skill packages (default: resolved from HERMES_SKILLS_ROOT "
                         "or HERMES_HOME/skills/sbl). Operator/test seam.")
    ap.add_argument("--sp-spine", default=None,
                    help="Shared Spine path used for the --sp-workorder join (default: "
                         "var/shared-spine/hg-kseos.db). Operator/test seam.")
    args = ap.parse_args()

    # ---- Tranche A/B: resolve the persisted per-round role binding (pre-spawn, fail-closed) ------
    # The required ARM and RANK for this lane are DERIVED from the SAME persisted binding document, so
    # an outer check on arm A can never pair with an inner run on arm B. A caller whose explicit
    # --require-arm / --force-rank contradicts the binding is refused; an OMITTED one is DERIVED (the
    # binding is mandatory selection), never a silent fallback. Legacy rounds pass no binding file and
    # are unchanged.
    binding_fields: dict = {}
    args.role_binding_digest = None
    args.role_binding_forced_rank = None
    validated_binding = None
    if args.role_binding_file or args.workorder:
        if _role_binding is None:
            print(json.dumps({"schema": SCHEMA, "ok": False, "code": ERR_ROLE_BINDING_INVALID,
                              "detail": "role_binding helper unavailable", **home_isolation_fields(args)},
                             sort_keys=True))
            return 2
        if not args.workorder:
            return emit_refusal(args, refusal_body(args.lane, ERR_ROLE_BINDING_WORKORDER_REQUIRED,
                "a bound dispatch must name --workorder; a supplied binding file is only a projection",
                say="no canonical WorkOrder named for a bound dispatch"))
        spine, spine_detail = _authorization_spine()
        if spine is None:
            return emit_refusal(args, refusal_body(args.lane, ERR_ROLE_BINDING_INVALID,
                f"canonical spine unreachable: {spine_detail}",
                say="the persisted role binding could not be read before any spawn"))
        try:
            persisted = _role_binding.load_canonical_binding(spine, args.workorder)   # TYPED fail-closed
        except _role_binding.BindingError as exc:
            return emit_refusal(args, refusal_body(args.lane, exc.code, exc.detail,
                say="the persisted role binding was refused before any spawn"))
        if args.role_binding_file:
            bpath = Path(args.role_binding_file)
            if not bpath.is_file():
                return emit_refusal(args, refusal_body(args.lane, ERR_ROLE_BINDING_FILE_UNREADABLE,
                    str(bpath), say="supplied projection file unreadable"))
            try:
                raw_binding = json.loads(bpath.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                return emit_refusal(args, refusal_body(args.lane, ERR_ROLE_BINDING_FILE_UNREADABLE,
                    f"{bpath}:{exc}", say="supplied projection file unreadable"))
            # the FILE is ONLY a projection of the persisted binding -- never authority
            try:
                _role_binding.require_projection_matches(persisted["binding"], raw_binding)
            except _role_binding.BindingError as exc:
                return emit_refusal(args, refusal_body(args.lane, exc.code, exc.detail,
                    say="the supplied file disagrees with the persisted binding"))
        try:
            validated = _role_binding.validate_binding(persisted["binding"], round=args.round)
            arm = _role_binding.resolve_arm(validated["binding"], args.lane)
            validated_binding = validated["binding"]
        except _role_binding.BindingError as exc:
            return emit_refusal(args, refusal_body(args.lane, exc.code, exc.detail,
                say="the persisted role binding was refused before any spawn"))
        except _role_binding.InvariantViolation as exc:
            return emit_refusal(args, refusal_body(args.lane, ERR_ROLE_BINDING_INVALID, str(exc),
                say="the persisted role binding was refused before any spawn"))
        binding_fields = {"role_binding_digest": validated["binding_digest"],
                          "role_binding_source": "canonical-spine",
                          "role_binding_session": validated["binding"]["session"],
                          "role_binding_round": validated["binding"]["round"],
                          "role_binding_workorder": validated["binding"]["workorder"],
                          "role_binding_subject": validated["binding"]["subject"],
                          "role_binding_arm": arm["arm"], "role_binding_rank": arm["rank"]}
        args.role_binding_digest = validated["binding_digest"]
        # Arm: refuse a conflicting explicit requirement; DERIVE (do not fall back) when omitted.
        if args.require_arm and str(args.require_arm) != arm["arm"]:
            return emit_refusal(args, refusal_body(args.lane, ERR_ROLE_BINDING_ARM_MISMATCH,
                f"--require-arm {args.require_arm} contradicts the binding arm {arm['arm']}",
                binding=binding_fields,
                say="the caller's required arm disagrees with the persisted role binding; refusing "
                    "before any spawn instead of running either silently"))
        args.require_arm = arm["arm"]
        # Rank: same discipline -- derive mandatory selection, refuse a contradiction.
        if args.force_rank is not None and int(args.force_rank) != int(arm["rank"]):
            return emit_refusal(args, refusal_body(args.lane, ERR_ROLE_BINDING_RANK_MISMATCH,
                f"--force-rank {args.force_rank} contradicts the binding rank {arm['rank']}",
                binding=binding_fields,
                say="the caller's forced rank disagrees with the persisted role binding; refusing "
                    "before any spawn"))
        args.force_rank = int(arm["rank"])
        args.role_binding_forced_rank = int(arm["rank"])

    try:
        lanes = load_pool(Path(args.pool))
        if args.lane not in lanes:
            raise LaneRouteError("ERR_SLOT_LANE_UNKNOWN", args.lane)
        pool = list(lanes[args.lane])
    except LaneRouteError as exc:
        print(json.dumps({"schema": SCHEMA, "ok": False, "code": exc.code, "detail": exc.detail,
                          **home_isolation_fields(args)}, sort_keys=True))
        return 2
    except Exception as exc:
        print(json.dumps({"schema": SCHEMA, "ok": False, "code": "ERR_LANE_DISPATCH_INTERNAL",
                          "detail": f"{type(exc).__name__}:{exc}",
                          **home_isolation_fields(args)}, sort_keys=True))
        return 2

    # The resolver owns validation/ordering (authority); the raw artifact supplies the transport
    # fields the resolver's PoolEntry does not carry (transport_model, reasoning_effort).
    try:
        # T2 (pass 2): strict parse -- a pool carrying a non-JSON constant (`NaN`) must not be read
        # through `json.loads`'s permissive default. A non-object top level has no `.get`; refuse typed.
        raw = strict_json_loads(Path(args.pool).read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise LaneRouteError("ERR_SLOT_POOL_MALFORMED", f"{args.pool}:top-level value is not an object")
        transport = {}
        lane_home_config = {}
        for ln in raw.get("lanes", []):
            if ln.get("lane") != args.lane:
                continue
            # FAR-LANE-REPAIR-20261014 (R-A): optional lane-level home/config declaration.
            lane_home_config = ln.get("codex_home_config") or {}
            for e in ln.get("ordered_pool", []):
                # S2 (REQ-STRICT-DECLARATION-014): the raw artifact is read with the SAME exact typing
                # the resolver applies. `int(e.get("rank"))` silently coerced a fractional/string/bool
                # rank so the transport key no longer lined up with the resolver's typed entries; a
                # non-integer rank is now a TYPED refusal at the dispatcher (no attempt is spawned),
                # never a coerced match.
                rank = e.get("rank")
                if isinstance(rank, bool) or not isinstance(rank, int):
                    raise LaneRouteError(
                        ERR_SLOT_POOL_ENTRY_TYPE,
                        f"{args.lane}:rank:{type(rank).__name__}={rank!r}: must be a JSON integer "
                        f"(no int() coercion; the transport key must line up with the resolver's typed entries)")
                transport[(rank, e.get("provider"), e.get("model"))] = e
    except LaneRouteError as exc:
        # a wrongly-typed declaration is a TYPED refusal here too, never a raw crash with no receipt
        print(json.dumps({"schema": SCHEMA, "ok": False, "code": exc.code, "detail": exc.detail,
                          **home_isolation_fields(args)}, sort_keys=True))
        return 2
    except (ValueError, TypeError) as exc:
        # T2 (pass 2): a non-JSON constant (ValueError) or a wrong-shaped entry (TypeError, e.g. a
        # non-object lane entry) is a TYPED refusal at the artifact boundary, never an uncaught crash.
        print(json.dumps({"schema": SCHEMA, "ok": False, "code": "ERR_SLOT_POOL_MALFORMED",
                          "detail": f"{args.pool}:{type(exc).__name__}:{exc}",
                          **home_isolation_fields(args)}, sort_keys=True))
        return 2
    args.codex_home_config = lane_home_config

    entries = []
    skipped: list = []          # C2: arms dropped by their own declaration, recorded never silent
    for e in pool:
        extra = transport.get((e.rank, e.provider, e.model), {})
        tm = extra.get("transport_model")
        if not tm:
            # explicit per-provider rule, measured: nvidia needs the qualified token; the openai arm
            # needs the bare id; opencode-go accepts both
            tm = f"{e.provider}/{e.model}" if e.provider == "nvidia" else e.model
        entries.append({"rank": e.rank, "provider": e.provider, "model": e.model,
                        "transport_model": tm, "reasoning_effort": extra.get("reasoning_effort"),
                        # The pool DECLARES the requirement; carrying it here is what makes the
                        # declaration real. A hostile review measured that this field was dropped at
                        # this point, so the gate silently fell back to the provider heuristic and
                        # both the declared value and ERR_LANE_IDENTITY_UNKNOWN were dead on the
                        # end-to-end path while the unit tests (which pass the field directly) stayed
                        # green.
                        "identity_requirement": extra.get("identity_requirement"),
                        # C2b: carry the declaration so it has a consumer. Without these two fields
                        # the artifact's feasibility/dispatchable were decorative and a dead arm was
                        # still spawned at full cost.
                        "feasibility": extra.get("feasibility"),
                        "dispatchable": extra.get("dispatchable")})

    # C2b: drop every entry the artifact declares not dispatchable, BEFORE the --force-rank filter.
    # The drop is recorded in `skipped` (surfaced in the receipt), never silent.
    pre_skip = list(entries)
    entries = [e for e in entries if _is_dispatchable(e)]
    for e in pre_skip:
        if not _is_dispatchable(e):
            # FIX 2 (C2) + G2: the reason is NEVER empty. The feasibility text is used ONLY when it is
            # a non-empty string after stripping; every other shape (None, "", whitespace-only, any
            # non-string including an empty list) falls back to a literal declaration reason. An empty
            # feasibility is not a reason.
            reason = _skip_reason(e, declared_not_dispatchable=e.get("dispatchable") is False)
            skipped.append({"rank": e["rank"], "arm": f"{e['provider']}/{e['model']}",
                            "reason": reason})

    if args.force_rank is not None:
        # An explicit --force-rank naming a skipped rank must still REACH it: the measurement is
        # overridable, not hidden. So the named rank is re-admitted from the pre-skip list, then the
        # existing filter narrows to it.
        if not any(e["rank"] == args.force_rank for e in entries):
            entries += [e for e in pre_skip if e["rank"] == args.force_rank]
        entries = [e for e in entries if e["rank"] == args.force_rank]
        if not entries:
            print(json.dumps({"schema": SCHEMA, "ok": False, "code": "ERR_SLOT_POOL_RANK_GAP",
                              "detail": f"{args.lane}:rank{args.force_rank}",
                              **home_isolation_fields(args)}, sort_keys=True))
            return 2
    if args.max_candidates < 0:
        # A negative slice emptied the candidate list and crashed the gate with IndexError (exit 1)
        # instead of the typed refusal the contract promises.
        print(json.dumps({"schema": SCHEMA, "ok": False, "code": "ERR_MAX_CANDIDATES_NEGATIVE",
                          "detail": str(args.max_candidates),
                          **home_isolation_fields(args)}, sort_keys=True))
        return 2
    if args.max_candidates:
        entries = entries[: args.max_candidates]

    codex = args.codex_executable or codex_executable()
    # FIX 4 (C3): resolve the lane home ONCE here -- the single point where it is read -- so both the
    # comparison against the declared lane home and the recorded `codex_home` use the resolved
    # absolute form (`--codex-home .` must record the resolved path). DEFAULT_LANE_HOME is unchanged.
    lane_home = Path(args.codex_home).resolve()

    # Sandbox separation is an invariant, not a default (round-5 checker: one flag could hand a
    # checker lane writer-grade access). Escalation above the role default needs an explicit flag
    # and is recorded in the receipt.
    role_default_sandbox = SANDBOX_BY_LANE.get(args.lane, "read-only")
    if args.sandbox and args.sandbox not in SANDBOX_RANK:
        print(json.dumps({"schema": SCHEMA, "ok": False, "code": "ERR_SANDBOX_UNKNOWN",
                          "detail": f"{args.sandbox!r}; known: {sorted(SANDBOX_RANK)}",
                          **home_isolation_fields(args)}, sort_keys=True))
        return 2
    escalated = bool(args.sandbox) and SANDBOX_RANK[args.sandbox] > SANDBOX_RANK[role_default_sandbox]
    if escalated and not args.allow_sandbox_escalation:
        print(json.dumps({"schema": SCHEMA, "ok": False, "code": "ERR_SANDBOX_ESCALATION_REFUSED",
                          "detail": f"lane {args.lane} defaults to {role_default_sandbox!r}; "
                                    f"{args.sandbox!r} needs --allow-sandbox-escalation",
                          **home_isolation_fields(args)}, sort_keys=True))
        return 2

    # ---- fail-closed identity/health gate (pre-spawn) ------------------------------------------
    # Owner ruling 2026-10-10: the OAuth arm STAYS in the unattended pool. So the gate does not
    # exclude it; it verifies that the RELAY-side credential can refresh without a human, and stops
    # only when it genuinely cannot. Refusing to spawn is what turns "a modal appears at 03:00" into
    # "the run stops with a named blocker".
    relay_home = Path(args.relay_home or (Path(os.environ.get("LOCALAPPDATA", ".")) / "HG-KSEOS" / "opencodex-hermes"))

    # ---- fail-closed blank-nonce gate (pre-spawn) ----------------------------------------------
    # FIX 5 (constructed false green): with `--nonce ""` the substring test is vacuously true, so a
    # turn that emitted NO nonce reported nonce_present: true / ok: true. A blank or whitespace-only
    # nonce must refuse BEFORE spawning anything -- never be silently treated as "the check is off".
    if nonce_is_blank(args.nonce):
        return emit_refusal(args, refusal_body(args.lane, ERR_NONCE_EMPTY,
            "the supplied --nonce is blank or whitespace-only; the nonce substring test would be "
            "vacuously true and certify a turn that emitted nothing",
            say="refusing before any spawn; the oracle requires a real nonce (no empty-string bypass)"))

    # ---- fail-closed SP identity gate (pre-spawn) ----------------------------------------------
    # D-06 (R13 follow-through): R13 honestly recorded its writer/checker as LANE_ONLY, because
    # nothing in the dispatch carried an SP identity — the lane and the SP were one thing under two
    # names. This is the adapter that separates them. The identity is resolved, digest-pinned and
    # INJECTED into the prompt here, before any candidate is considered, and --nonce is required to be
    # the invocation id, so the pre-existing nonce oracle (assistant-message read on the preserved
    # bytes) is what proves the child actually received it — no second, weaker echo check.
    args.sp_identity_receipt = None
    sp_dangling = [k for k, v in (("--sp-invocation-id", args.sp_invocation_id),
                                  ("--sp-workorder", args.sp_workorder),
                                  ("--sp-skills-root", args.sp_skills_root),
                                  ("--sp-spine", args.sp_spine)) if v]
    if sp_dangling and not args.sp_identity:
        return emit_refusal(args, refusal_body(args.lane, ERR_SP_IDENTITY_FLAG_WITHOUT_IDENTITY,
            f"{sp_dangling} given without --sp-identity: ignoring them would let a receipt read as "
            f"carrying an identity this run never resolved",
            say="refusing before any spawn rather than silently dropping an identity-shaped argument"))
    if args.sp_identity:
        if _sp_identity is None:
            return emit_refusal(args, refusal_body(args.lane, ERR_SP_IDENTITY_MODULE_UNAVAILABLE,
                "scripts/hgk_sp_identity.py could not be loaded",
                sp_identity={"sp": args.sp_identity, "ok": False},
                say="refusing before any spawn: an identity the dispatcher cannot resolve must not be "
                    "dispatched as if it were present"))
        resolved = _sp_identity.resolve_identity(
            args.sp_identity, skills_root=args.sp_skills_root, lane=args.lane, nonce=args.nonce,
            invocation_id=args.sp_invocation_id, spine=args.sp_spine or SPINE_DB,
            workorder=args.sp_workorder)
        ident = dict(resolved.get("identity") or {})
        ident["ok"] = bool(resolved["ok"])
        args.sp_identity_receipt = ident
        if not resolved["ok"]:
            return emit_refusal(args, refusal_body(args.lane, resolved["code"], resolved["detail"],
                sp_identity=ident,
                say="refusing before any spawn: the SP identity did not resolve"))
        block = _sp_identity.build_block(ident)
        ident["block_sha256"] = hashlib.sha256(block.encode("utf-8")).hexdigest()
        ident["prompt_sha256_before"] = hashlib.sha256(args.prompt.encode("utf-8")).hexdigest()
        # The injection point. Everything between here and run_candidate is a gate that can only
        # refuse; no path re-derives the prompt, so what the child gets is exactly this.
        args.prompt = block + "\n\n" + args.prompt
        ident["prompt_sha256_after"] = hashlib.sha256(args.prompt.encode("utf-8")).hexdigest()
        ident["identity_block_injected_pre_spawn"] = True
        args.sp_identity_receipt = ident

    # ---- fail-closed lane-home isolation gate (pre-spawn) --------------------------------------
    # C3: the pool declares transports PER ARM, but --codex-home is a PER-RUN flag. Pointing it at a
    # home that holds a login silently hands the human credential to EVERY key-auth arm in the run
    # while the receipt still certified them as "no human-attended identity". So the identity claim
    # is only made when the resolved home is the declared isolated lane home (or holds no auth.json).
    home_isolation = lane_home_isolation(lane_home, DEFAULT_LANE_HOME)
    if home_isolation["non_isolated"] and not args.allow_human_home_transport:
        return emit_refusal(args, refusal_body(args.lane, "ERR_LANE_HOME_NOT_ISOLATED",
            f"the resolved --codex-home {str(lane_home)} is not the declared lane home "
            f"{str(DEFAULT_LANE_HOME)} and holds an auth.json (a login); the key-auth arms' "
            f"'no human-attended identity' claim is not being made for this run",
            say="a non-isolated home would hand the human credential to every key-auth arm; "
                "refusing before any spawn (pass --allow-human-home-transport to acknowledge it)"))

    # FAR-LANE-REPAIR-20261014 (R-E): fail-closed sandbox-declaration gate (pre-spawn).
    # A read-only (or workspace-write) lane whose home declares no [windows] sandbox level and whose
    # pool declares none either cannot run ANY command: codex denies every tool call at its decision
    # layer while the turn still exits 0 with a nonce and a usage receipt (a false-green surface).
    # Refuse before the spawn, mirroring the ERR_LANE_HOME_NOT_ISOLATED shape.
    _hc = getattr(args, "codex_home_config", None) or {}
    _ws = _hc.get("windows_sandbox")
    _modes = _hc.get("required_for_modes") or ["read-only", "workspace-write"]
    _effective = args.sandbox or SANDBOX_BY_LANE.get(args.lane, "read-only")
    if _effective in _modes:
        _cfg = Path(lane_home) / "config.toml"
        _present = False
        if _cfg.is_file():
            _txt = _cfg.read_text(encoding="utf-8", errors="replace")
            _present = any(ln.split("#")[0].strip() == "[windows]" for ln in _txt.splitlines()) and "sandbox" in _txt
        if not _ws and not _present:
            return emit_refusal(args, refusal_body(args.lane, "ERR_LANE_SANDBOX_LEVEL_ABSENT",
                f"the lane home {str(lane_home)} declares no [windows] sandbox level and {args.pool} "
                f"declares no codex_home_config.windows_sandbox for {args.lane}; every tool call in "
                f"'{_effective}' mode would be denied at the decision layer while the turn still "
                f"reports exit 0",
                say="refusing before any spawn: declare codex_home_config.windows_sandbox on the lane "
                    "(or set [windows] sandbox in the home config.toml)"))

    # The pre-gate candidate set. "Is the required arm IN THE POOL?" must be answered against THIS
    # list, not against the post-gate survivors: otherwise a refused arm reads as ABSENT and the
    # caller gets ERR_LANE_REQUIRED_ARM_ABSENT instead of the refusal that actually explains it.
    candidates = list(entries)
    gate = {"state": "skipped" if args.no_identity_gate else "enforced",
            "lane_home": str(lane_home), "relay_home": str(relay_home),
            "arms": [], "degraded": False, "required_arm": args.require_arm}
    if not args.no_identity_gate:
        admitted = []
        for e in entries:
            verdict = identity_check(e, args.lane, lane_home, relay_home)
            gate["arms"].append(verdict)
            if verdict.get("ok"):
                admitted.append(e)
            else:
                gate["degraded"] = True
        if not admitted:
            # A hostile review measured that a NEGATIVE --max-candidates emptied this list and the
            # [0] access crashed with IndexError (exit 1) instead of refusing in-contract.
            first = gate["arms"][0] if gate["arms"] else {"code": "ERR_LANE_NO_CANDIDATES",
                                                          "detail": "the candidate list was empty"}
            return emit_refusal(args, refusal_body(args.lane, first.get("code", "ERR_LANE_IDENTITY_REFUSED"),
                                                   first.get("detail"), identity_gate=gate,
                                                   skipped_arms=skipped,
                                                   say="no arm survived the identity gate; nothing was spawned"))
        entries = admitted

    # The required-arm guarantee is enforced whether or not the gate ran: `--no-identity-gate`
    # switches off the gate, NOT this guarantee. A hostile review demonstrated the nesting defect,
    # where `--no-identity-gate --require-arm <refused-arm>` silently degraded to another arm.
    if args.require_arm:
        tok = str(args.require_arm)
        if not [e for e in candidates if f"{e['provider']}/{e['model']}" == tok]:
            return emit_refusal(args, refusal_body(args.lane, "ERR_LANE_REQUIRED_ARM_ABSENT",
                                                   f"{tok} is not in the {args.lane} pool",
                                                   required_arm=tok, identity_gate=gate,
                                                   say="the required arm is not in this lane's pool"))
        verified = [v for v in gate["arms"] if f"{v.get('provider')}/{v.get('model')}" == tok]
        if not verified:
            arm = next(e for e in entries if f"{e['provider']}/{e['model']}" == tok)
            verified = [identity_check(arm, args.lane, lane_home, relay_home)]
            gate["arms"].append(verified[0])
            gate["required_arm_verified_without_gate"] = True
        if not verified[0].get("ok"):
            return emit_refusal(args, refusal_body(args.lane, verified[0].get("code", "ERR_LANE_IDENTITY_REFUSED"),
                                                   verified[0].get("detail"), required_arm=tok,
                                                   identity_gate=gate,
                                                   say="the required arm did not survive the identity gate; "
                                                       "failing closed instead of silently running a "
                                                       "different arm"))

    # ---- non-mutation guard (makes an escalated-sandbox checker safe) --------------------------
    guard_roots = list(args.guard_subject or [])
    # MEASURED (probe E5b): a guard root the native process cannot resolve produced a ZERO-FILE
    # snapshot, and the receipt then read `mutated: false` - a vacuous guard reported as a clean
    # subject. An unresolvable root is a setup error, so it must refuse instead of bless.
    missing_roots = [str(r) for r in guard_roots if not Path(r).exists()]
    if missing_roots:
        refusal = {"schema": SCHEMA, "ok": False, "lane": args.lane, "code": "ERR_GUARD_ROOT_MISSING",
                   "detail": f"guard root(s) do not resolve for this process: {missing_roots}",
                   "guard_roots": [str(r) for r in guard_roots],
                   "say": "a vacuous guard would report a clean subject; refusing instead",
                   **home_isolation_fields(args),
                   "generated_utc": datetime.now(UTC).isoformat()}
        if args.json_out:
            out = Path(args.json_out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(refusal, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(refusal, indent=2, ensure_ascii=False))
        return 4
    subject_before = snapshot_subject(guard_roots)
    # G3/H4: a guard root that RESOLVES but yields a ZERO-FILE snapshot guards NOTHING. Reporting
    # `mutated: false` (both evidence digests being the hash of []) over an empty snapshot is the
    # vacuous-pass class this round closes, so it must refuse PRE-SPAWN with its own typed code.
    # ERR_GUARD_ROOT_MISSING keeps the "does not resolve" case; these causes must not be merged.
    # H4 (pass-4 checker): validation is now PER-ROOT, because checking only the AGGREGATE snapshot
    # let an empty root be MASKED by a non-empty sibling. An empty root is vacuous even then.
    if guard_roots:
        empty_roots = [str(r) for r in guard_roots if not snapshot_subject([r])]
        if empty_roots:
            refusal = {"schema": SCHEMA, "ok": False, "lane": args.lane, "code": ERR_GUARD_ROOT_EMPTY,
                       "detail": f"guard root(s) resolve but contain ZERO files: {empty_roots}",
                       "guard_roots": [str(r) for r in guard_roots],
                       "empty_guard_roots": empty_roots,
                       "guard_files_before": len(subject_before),
                       "say": "a guard over an empty root proves nothing (an empty root is vacuous "
                              "even when another root contributes files); refusing instead of "
                              "reporting a vacuous clean verdict",
                       **home_isolation_fields(args),
                       "generated_utc": datetime.now(UTC).isoformat()}
            if args.json_out:
                out = Path(args.json_out)
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(refusal, indent=2, ensure_ascii=False), encoding="utf-8")
            print(json.dumps(refusal, indent=2, ensure_ascii=False))
            return 4
    subject_digest = hashlib.sha256(json.dumps(sorted(subject_before.items()), sort_keys=True).encode()).hexdigest() \
        if guard_roots else None

    attempts: list[dict] = []
    used = None
    completion_evidence: dict = {"checked": False}
    bound = validated_binding is not None
    args._validated_binding = validated_binding
    run_started = int(time.time())
    run_id = f"{os.getpid()}-{run_started}"
    trail = Path(f"{args.json_out}.attempts.ndjson") if args.json_out else None
    log_dir = args.attempt_log_dir or (f"{args.json_out}.logs" if args.json_out else None)

    # ---- an escalated lane must be BOUNDED by measurement (hostile-review F4/F6) ----------------
    # danger-full-access has no sandbox root, so the guard is the only bound an escalated checker has.
    # Two ways for that bound to be absent while the receipt still read ok:true are closed here.
    unguarded_ack = bool(args.allow_unguarded_escalation)
    if escalated and not guard_roots and not unguarded_ack:
        return emit_refusal(args, refusal_body(args.lane, "ERR_GUARD_REQUIRED_FOR_ESCALATED_CHECKER",
            f"lane {args.lane} is escalated from {role_default_sandbox!r} to {args.sandbox!r} with no "
            f"--guard-subject: nothing would measure the subject",
            sandbox_escalation_authorised=True,
            say="an unbounded escalated lane is refused; pass --allow-unguarded-escalation to record the "
                "exception explicitly"))
    containment = []
    if guard_roots:
        harness_paths = [p for p in (log_dir, args.json_out,
                                     f"{args.json_out}.attempts.ndjson" if args.json_out else None) if p]
        for hp in harness_paths:
            h = Path(hp).resolve()
            for r in guard_roots:
                g = Path(r).resolve()
                if h == g or g in h.parents:
                    containment.append((str(r), str(hp)))
    if containment:
        return emit_refusal(args, refusal_body(args.lane, "ERR_GUARD_ROOT_CONTAINS_HARNESS_OUTPUT",
            f"harness output path(s) live inside a guard root: {containment}",
            say="the harness's own writes would register as subject changes; keep them apart"))

    # ---- Phase C1: per-lane, per-attempt output directory (loud collision) ----------------------
    # Recorded X3/X3b defect: two concurrent lanes wrote the SAME deliverable paths (an 8-line
    # stream was overwritten by a 3-line one). When --round is supplied the output dir is DERIVED as
    # var/<round>/<lane>/attempt-<n>-<utc-ts>; creating an already-existing dir is a LOUD refusal,
    # never a silent reuse. Without --round the historical --attempt-log-dir path is kept (so the
    # existing suite is unchanged), but an explicit path that collides with a LIVE attempt refuses.
    c1 = {"mode": "explicit-path", "derived": None, "collision": None, "marker": None}
    if args.round:
        if _lod is None:
            return emit_refusal(args, refusal_body(args.lane, "ERR_LANE_OUTPUT_DIR_HELPER_MISSING",
                "scripts/gcm-containment/lane_output_dir.py could not be imported; refusing to fall "
                "back to an arbitrary output path",
                say="the C1 output-dir helper is required when --round is supplied"))
        out_lane_root = _lod.lane_root(ROOT, args.round, args.lane, args.output_root)
        attempt_number = _lod.next_attempt_number(out_lane_root, args.attempt)
        derived = _lod.derive_output_dir(ROOT, args.round, args.lane, attempt=attempt_number,
                                         output_root=args.output_root)
        try:
            _lod.create_output_dir(derived)
        except _lod.LaneOutputCollision as exc:
            return emit_refusal(args, refusal_body(args.lane, "ERR_LANE_OUTPUT_DIR_EXISTS",
                f"the derived attempt output dir already exists: {exc.path}",
                output_dir=str(derived),
                say="two lanes must not share an attempt path; refusing to reuse it (exist_ok=False)"))
        marker = _lod.write_attempt_marker(derived, round_name=args.round, lane=args.lane,
                                           attempt=attempt_number,
                                           log_path=args.prior_attempt_log, nonce=args.nonce,
                                           run_id=f"{os.getpid()}-{int(time.time())}")
        log_dir = str(derived)
        c1 = {"mode": "derived", "derived": str(derived), "attempt_number": attempt_number,
              "attempt_marker": str(marker)}
    elif log_dir:
        live = _lod.live_attempt_in(log_dir) if _lod is not None else None
        live_liveness = (live or {}).get("liveness") or {}
        if live_liveness.get("alive") is True:
            return emit_refusal(args, refusal_body(args.lane, "ERR_LANE_OUTPUT_DIR_LIVE_COLLISION",
                f"the explicit --attempt-log-dir {log_dir} belongs to a LIVE attempt "
                f"(pid {live_liveness.get('pid')}, method {live_liveness.get('method')})",
                output_dir=str(log_dir), live_attempt=live,
                say="refusing to write into a directory a live attempt owns"))
        c1 = {"mode": "explicit-path", "derived": None, "existing": bool(live and live.get("exists"))}

    # ---- Phase C3: repair-dispatch precondition (prior attempt must be ENDED) --------------------
    # Recorded overrun: a repair lane was dispatched BEFORE the prior attempt was confirmed ended.
    # A repair/retry refuses to spawn unless (a) the prior attempt's process is gone AND (b) its log
    # carries a terminal EXIT= marker. Liveness is pid-based; if it cannot be reached reliably the
    # refusal is INCONCLUSIVE (labelled), never silently treated as "gone".
    #
    # D5 fix (round HGK-GCM-REPAIR2-20261013): the round-1 precondition accepted three insufficient
    # proofs (log ``EXIT=`` alone; an absent prior dir + a log; an existing dir with no marker + a
    # log). None of them established that the prior PROCESS is gone, yet all three spawned. The repair
    # must PROVE the prior attempt's process is gone with a real process-liveness check on this host.
    # If a pid is known (from the prior marker or ``--prior-attempt-pid``) the check is authoritative:
    # alive -> refuse; a reached ``alive: false`` -> proceed; cannot reach a verdict -> REFUSE. If the
    # pid is UNKNOWN (absent dir, or a dir with no marker) the process state cannot be proven, so the
    # default is REFUSAL (``ERR_REPAIR_PRIOR_ATTEMPT_LIVENESS_UNPROVEN``). A terminal log marker is a
    # NECESSARY second condition, never a sufficient one.
    c3 = {"checked": False}
    if args.prior_attempt_dir or args.prior_attempt_log or args.prior_attempt_pid is not None:
        c3["checked"] = True
        c3.setdefault("prior_process_gone", None)  # proven-True only once liveness reaches alive:false
        prior_dir = Path(args.prior_attempt_dir) if args.prior_attempt_dir else None
        liveness = None
        marker = None
        prior_pid = args.prior_attempt_pid
        prior_create_time = None
        if prior_dir is not None:
            if not prior_dir.exists():
                # D5 variant (b): an absent prior dir carries no marker and no pid. The PROCESS state
                # cannot be proven from it; the log alone must not be read as "the prior attempt
                # ended". Refuse UNLESS an explicit pid was supplied (then that pid is authoritative).
                c3.update(prior_exists=False,
                          note="the named prior-attempt dir does not exist; no marker/pid to prove a "
                               "prior process is gone")
            else:
                live = _lod.live_attempt_in(prior_dir) if _lod is not None else {"liveness": None}
                liveness = live.get("liveness")
                c3["liveness"] = liveness
                marker = live.get("marker")
                if marker and prior_pid is None:
                    prior_pid = marker.get("pid")
                    prior_create_time = marker.get("process_create_time")
                # The log to inspect for the terminal marker: explicit flag wins, else the marker's.
                if args.prior_attempt_log is None and marker and marker.get("log_path"):
                    args.prior_attempt_log = marker.get("log_path")
        # (a) the MANDATORY process-liveness proof. A recorded pid (marker or flag) is authoritative.
        if prior_pid is not None:
            live = (_lod.process_liveness(prior_pid, prior_create_time)
                    if _lod is not None else {"checked": False, "alive": None, "method": "helper-missing"})
            c3["prior_pid"] = prior_pid
            c3["prior_liveness"] = live
            if live.get("alive") is True:
                return emit_refusal(args, refusal_body(args.lane, "ERR_REPAIR_PRIOR_ATTEMPT_ALIVE",
                    f"the prior attempt process is still alive (pid {prior_pid}, method "
                    f"{live.get('method')}); refusing to start a repair",
                    prior_attempt_dir=str(prior_dir) if prior_dir else None, prior_liveness=live,
                    repair_precondition=c3,
                    say="a repair before the prior attempt ends is the recorded overrun; refusing"))
            if live.get("checked") and live.get("alive") is False:
                c3["prior_process_gone"] = True
            else:
                return emit_refusal(args, refusal_body(args.lane,
                    "ERR_REPAIR_PRIOR_ATTEMPT_LIVENESS_INCONCLUSIVE",
                    f"the prior attempt's liveness could not be reached reliably "
                    f"({live.get('method')}: {live.get('note')}); refusing to assert it is gone",
                    prior_attempt_dir=str(prior_dir) if prior_dir else None, prior_liveness=live,
                    repair_precondition=c3,
                    say="an unreliable liveness check must not be read as 'gone'; refusing"))
        elif args.allow_unverified_prior_gone:
            c3["prior_process_gone"] = None
            c3["liveness_note"] = ("no pid to check; proceeding ONLY because "
                                   "--allow-unverified-prior-gone was supplied (recorded)")
            c3["unverified_prior_gone_acknowledged"] = True
        else:
            # D5 variants (a)/(b)/(c): no reachable pid -> the prior process state is UNPROVEN. A
            # log-only ("EXIT=" alone), absent-dir, or no-marker prior attempt is exactly this case.
            return emit_refusal(args, refusal_body(args.lane,
                "ERR_REPAIR_PRIOR_ATTEMPT_LIVENESS_UNPROVEN",
                "the prior attempt's process liveness cannot be proven on this host: no pid is "
                "recorded on the prior dir and none was supplied (--prior-attempt-pid). A log EXIT= "
                "marker alone does not prove the prior process is gone; refusing by default",
                prior_attempt_dir=str(prior_dir) if prior_dir else None, prior_liveness=liveness,
                repair_precondition=c3,
                say="'cannot prove the prior process exited' is a refusal, not a pass (D5)"))
        # (b) the terminal marker (a NECESSARY condition; never sufficient on its own)
        if not args.prior_attempt_log:
            return emit_refusal(args, refusal_body(args.lane, "ERR_REPAIR_PRIOR_ATTEMPT_NO_LOG",
                "no prior-attempt log was given (and none is recorded on the prior marker), so the "
                "terminal EXIT= marker cannot be checked; refusing to start a repair",
                say="cannot confirm the prior attempt ended without its log; refusing"))
        log_text = _read_text(args.prior_attempt_log)
        if not Path(args.prior_attempt_log).is_file():
            return emit_refusal(args, refusal_body(args.lane,
                "ERR_REPAIR_PRIOR_ATTEMPT_NO_TERMINAL_MARKER",
                f"the prior log does not exist: {args.prior_attempt_log}; the attempt cannot be shown "
                f"to have ended", prior_attempt_log=str(args.prior_attempt_log),
                say="no terminal marker possible without the log; refusing"))
        terminal = find_terminal_marker(log_text)
        c3["terminal_marker"] = terminal
        if terminal is None:
            return emit_refusal(args, refusal_body(args.lane,
                "ERR_REPAIR_PRIOR_ATTEMPT_NO_TERMINAL_MARKER",
                f"the prior log {args.prior_attempt_log} carries no EXIT= terminal marker; the prior "
                f"attempt cannot be shown to have ended",
                prior_attempt_log=str(args.prior_attempt_log),
                say="a repair before the prior EXIT= is the recorded overrun; refusing"))
        c3["prior_exit_code"] = parse_exit_code(terminal)

    # ---- Phase C4: DETECTION_ONLY remote-write pre-check ----------------------------------------
    # A lane whose BRIEF carries remote-write markers (git push / --force / publish / refs/heads)
    # is not authorized to write a remote unless a publication WorkOrder is attached. This is
    # DETECTION ONLY on the declared dispatch path: it inspects the brief; it CANNOT stop a lane
    # that calls `git push` from inside its spawned shell. It is separate from the credential
    # posture control (no-prompt != no-unintended-push).
    c4 = {"mode": "DETECTION_ONLY", "ran": False}
    if args.brief:
        brief_text = _read_text(args.brief)
        pre = remote_write_precheck(brief_text=brief_text,
                                    publication_wo=args.publication_workorder)
        c4 = {"mode": "DETECTION_ONLY", "ran": True, "brief": str(args.brief), **pre}
        if pre["would_refuse"]:
            return emit_refusal(args, refusal_body(args.lane, "ERR_LANE_REMOTE_WRITE_NOT_AUTHORIZED",
                f"the lane brief carries remote-write markers {pre['markers']} and no publication "
                f"WorkOrder is attached", detection_only=True, remote_write_markers=pre["markers"],
                publication_workorder=None,
                say="DETECTION_ONLY on the declared dispatch path: refusing to DISPATCH this lane. "
                    "This cannot stop a lane that calls git push from inside its own shell."))

    # ---- D4: single-use authorization claim (acquire BEFORE any spawn; consume AFTER success) ----
    # Round-1 defect: the dispatcher imported the claim wrapper but never acquired or checked it, so a
    # named authorization budget could be taken twice. When `--authorization-resource` is set, this
    # path ACQUIRES the lease before the first spawn and CONSUMES it (a durable tombstone) after the
    # attempt that actually served. A resource already consumed by a prior successful spawn is refused
    # with `ERR_AUTHORIZATION_ALREADY_CONSUMED` before anything is spawned.
    authorization = {"checked": bool(args.authorization_resource and not args.no_authorization_claim)}
    claim_handle = None
    authz_spine = None
    if authorization["checked"]:
        authz_spine, authz_detail = _authorization_spine()
        if authz_spine is None:
            return emit_refusal(args, refusal_body(args.lane, "ERR_AUTHORIZATION_CLAIM_UNAVAILABLE",
                f"the single-use authorization claim boundary could not be opened: {authz_detail}",
                authorization_resource=args.authorization_resource,
                say="an unacquirable authorization boundary is a refusal, not a silent no-budget pass"))
        consumed_before = _authz.is_consumed(authz_spine, args.authorization_resource)
        authorization.update(resource_id=args.authorization_resource, consumed_before=consumed_before)
        if consumed_before:
            return emit_refusal(args, refusal_body(args.lane, "ERR_AUTHORIZATION_ALREADY_CONSUMED",
                f"the authorization resource {args.authorization_resource} was already consumed by a "
                f"prior successful spawn; a second use of the same budget is refused",
                authorization_resource=args.authorization_resource,
                say="the authorization overrun must be structurally impossible; refusing the second use"))
        try:
            claim_handle = _authz.claim(authz_spine, args.authorization_resource,
                                        holder=f"{args.lane}:{os.getpid()}:{run_started}",
                                        token=f"{args.lane}:{os.getpid()}:{run_started}:{args.nonce}",
                                        ttl_seconds=args.authorization_ttl)
        except Exception as exc:
            return emit_refusal(args, refusal_body(args.lane, "ERR_AUTHORIZATION_CLAIM_REFUSED",
                f"the authorization resource {args.authorization_resource} is held or consumed: {exc}",
                authorization_resource=args.authorization_resource,
                say="a live holder already owns this budget; refusing to start"))
        authorization["acquired"] = True

    # P0-A (round FAR-LANE-REUSE-RCA-20261015): fail-closed pin-assert, the LAST gate before a
    # real spawn. The 2026-10-14 binary drift (declared 2e5e00... dir -> app-update install of
    # 9614...) previously surfaced ONLY as a spawn-stage WinError 2. Ordering: the other typed
    # refusals (pool/guard/sandbox/identity/authorization) keep their own codes; the pin gate
    # runs immediately before run_candidate, validating the DECLARED pin via the canonical
    # toolchain verifier (existence + version + digest), never duplicating that logic inline.
    if not args.codex_executable and not getattr(args, "no_pin_assert", False):
        _pin_probe = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "hgk-lane-toolchain.py"),
             "--verify", "--declaration", str(ROOT / "config" / "hermes-codex-lane.json")],
            capture_output=True, text=True, timeout=120)
        if _pin_probe.returncode != 0:
            return emit_refusal(args, refusal_body(args.lane, "ERR_LANE_PIN_IDENTITY_INVALID",
                f"declared codex toolchain pin failed verification: {_pin_probe.stderr.strip() or _pin_probe.stdout.strip()[-400:]}",
                pin_exit=_pin_probe.returncode,
                say="refusing before any spawn: the declared codex executable+digest pin does not match "
                    "the actually installed binary; refresh the pin by owner-approved config change"))

    for i, e in enumerate(entries):
        if args.inject_429_first and i == 0:
            att = {"rank": e["rank"], "model": e["model"], "exit": "ERR_429_INJECTED", "injected": True,
                   "nonce_present": False, "usage_receipt_ok": False}
            attempts.append(att)
        else:
            try:
                att = run_candidate(e, args, codex, lane_home, attempt_log_dir=log_dir, run_id=run_id)
            except CredentialPostureRefused as exc:
                # (b) POSITIVE violation, fail-closed: the posture gate refused BEFORE a spawn.
                # TERMINAL and typed -- a refusal never becomes an empty attempt list, and no arm is
                # silently skipped to make the turn "succeed". No spawn log was written for this
                # attempt because the refusal precedes the subprocess.run call.
                # D4: nothing spawned, so the budget is not served -- release the window (never the
                # tombstone) so the unexercised authorization is reclaimable, then refuse.
                if claim_handle is not None:
                    authorization["consumed"] = False
                    authorization["window_released"] = bool(claim_handle.release())
                return emit_refusal(args, refusal_body(args.lane, exc.code, exc.detail,
                                                       credential_posture=exc.posture,
                                                       authorization=authorization,
                                                       attempts=[a for a in attempts],
                                                       say="the fail-closed credential-posture gate "
                                                           "refused before any spawn; failing closed "
                                                           "instead of running a lane that could hang"))
            attempts.append(att)
        if trail:
            trail.parent.mkdir(parents=True, exist_ok=True)
            with trail.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"run_id": f"{os.getpid()}-{run_started}", "at_utc": datetime.now(UTC).isoformat(),
                                     "lane": args.lane, "attempt_in_run": len(attempts), **att},
                                    ensure_ascii=False, sort_keys=True) + "\n")
        if att.get("exit") == 0 and att.get("nonce_present") and att.get("usage_receipt_ok"):
            _ce = None
            if bound:
                _ce = _resolve_completion_evidence(att, validated_binding, root=args.cwd or ROOT)
                completion_evidence = {"checked": True, "refusal": _ce}
            else:
                completion_evidence = {"checked": False}
            if _ce is None:
                used = att
                break

    # ---- D4 (cont.): CONSUME the single-use budget iff an attempt actually served this turn ----
    # A successful spawn (the attempt that serves the turn) marks the authorization resource USED via
    # the durable CONSUMED tombstone, so a second acquisition by ANY holder -- sequential or concurrent
    # -- is refused afterwards. The WINDOW lease is then released: the tombstone (not the window) is
    # what makes the budget single-use, so freeing the window is safe and avoids a lingering live lease.
    # A turn that spawned nothing that served leaves the budget UNCONSUMED and releases the window, so
    # an unexercised authorization is reclaimable after the TTL instead of being burned by a failed run.
    if claim_handle is not None:
        if used is not None:
            authorization["consumed"] = bool(claim_handle.consume())
        else:
            authorization["consumed"] = False
        authorization["window_released"] = bool(claim_handle.release())

    subject_after = snapshot_subject(guard_roots)
    mutation: dict = diff_subject(subject_before, subject_after) if guard_roots else {"state": "not_guarded"}
    if guard_roots:
        mutation["guard_roots"] = [str(r) for r in guard_roots]
        mutation["subject_digest_sha256_before"] = subject_digest
        mutation["subject_digest_sha256_after"] = hashlib.sha256(
            json.dumps(sorted(subject_after.items()), sort_keys=True).encode()).hexdigest()

    receipt = {
        "schema": SCHEMA, "lane": args.lane,
        "role": "checker" if args.lane == "VERIFY_SECURITY" else "writer",
        "role_binding_source": binding_fields.get("role_binding_source"),
        "engine": "codex-cli",
        "codex_executable": codex, "codex_home": str(lane_home), "relay_base": args.relay_base,
        "codex_home_is_declared_lane_home": home_isolation["codex_home_is_declared_lane_home"],
        "human_home_transport_acknowledged": bool(args.allow_human_home_transport),
        "skipped_arms": skipped,
        "transport": "opencodex relay via per-invocation -c openai_base_url (no config mutation)",
        "transport_target": args.relay_base,
        "front_door_port": front_door_port(args.relay_base),
        "front_door_note": "the lane-scoped pool door (10103 VERIFY_SECURITY / 10105 EXECUTE) carries the "
                           "hop and ledgers every decision; the sealed single-model 10100 door is "
                           "unchanged and unused; None here means direct to the relay on 10101",
        "sandbox": args.sandbox or role_default_sandbox,
        "sandbox_by_role_default": role_default_sandbox,
        "sandbox_escalation_authorised": bool(escalated),
        "cwd": str(args.cwd or ROOT),
        "side_effect_note": ("danger-full-access has NO sandbox root: any absolute path is writable, "
                             "so a read-only subject must be a frozen copy checked afterwards by digest"
                             if (args.sandbox or role_default_sandbox) == "danger-full-access" else
                             "no write access granted by the sandbox mode"),
        "receipt_binding": "usage rows appended after this attempt started (byte offset bound)",
        "pool": args.pool, "candidates_considered": [e["rank"] for e in entries],
        "mode": ("forced_rank" if args.force_rank is not None else
                 # attempts[0] can be a SYNTHETIC injected-429 entry, which made the first real
                 # success look like a pooled advance (hostile-review F12).
                 ("pooled_advance" if used and [a for a in attempts if not a.get("injected")][:1] != [used]
                  else "pinned_primary")),
        "unguarded_escalation_acknowledged": bool(unguarded_ack),
        "inject_429_first": bool(args.inject_429_first),
        "identity_gate": gate,
        "authorization": authorization,
        "subject_mutation": mutation,
        "attempt_log_dir": log_dir,
        "output_dir_policy": c1,
        "repair_precondition": c3,
        "remote_write_precheck": c4,
        "attempts": attempts,
        "used_rank": used["rank"] if used else None,
        "used_transport_model": used["transport_model"] if used else None,
        "used_seconds": used["seconds"] if used else None,
        "generated_utc": datetime.now(UTC).isoformat(),
        "claim_ceiling": "a pass here proves the Codex-CLI lane served this turn through the relay with a matching usage receipt; it is not an acceptance of any subject",
    }
    receipt["ok"] = used is not None
    receipt["completion_evidence"] = completion_evidence
    # I3 (pass-5): surface the USAGE MEASUREMENT at the top level too, taken from the serving attempt
    # (or the first attempt that answered when none served). A wrong-shaped CARRIER is a statement
    # about the TEXT, not about the usage row, so it must NOT overwrite this value -- the frozen C1
    # classification (exit 0 + valid usage + no nonce) reads exactly this.
    _serving = used if used is not None else next(
        (a for a in attempts if a.get("exit") == 0), None)
    receipt["usage_receipt_ok"] = bool(_serving.get("usage_receipt_ok")) if _serving else False
    # I2 (pass-5): surface the wrong-shaped-row count on the receipt itself (in every case, not only
    # the failure path), so a skipped/counted bad row is operator-visible even on a passing turn.
    receipt["usage_rows_shape_invalid"] = sum(
        int(a.get("usage_rows_shape_invalid") or 0) for a in attempts)
    # J1 (pass-6): surface the undecodable-line count too, so a line dropped by strict UTF-8 decoding
    # is operator-visible (it can never be a receipt, and it was never substituted into one).
    receipt["usage_rows_undecodable"] = sum(
        int(a.get("usage_rows_undecodable") or 0) for a in attempts)
    if not receipt["ok"]:
        # C1: the failure code no longer conflates two disjoint conditions. A run where arms answered
        # but none emitted the nonce reads differently from a run where every attempt timed out, and
        # only those fall back to the generic exhausted code.
        receipt.update(failure_disposition(attempts))
    if used is not None and args.require_arm:
        # Always record the pair positively, so a passing receipt also states WHICH arm served.
        receipt["required_arm"] = str(args.require_arm)
        receipt["served_arm"] = f"{used['provider']}/{used['model']}"
        if f"{used['provider']}/{used['model']}" != str(args.require_arm):
            # Surviving the gate is not the guarantee; BEING SERVED is. Without this, a run could pass
            # the required arm's gate and then serve a different arm after a runtime failure, reporting
            # ok:true (hostile-review F11).
            receipt["ok"] = False
            receipt["code"] = "ERR_REQUIRED_ARM_NOT_SERVED"
    # Tranche B: a BOUND round records the binding digest + session/round/subject on the invocation
    # receipt, and the SERVED identity must match the binding's role arm -- an outer check that
    # demanded arm A must never be satisfied by a turn that actually served arm B.
    if getattr(args, "role_binding_forced_rank", None) is not None:
        receipt["role_binding"] = binding_fields
        receipt["binding_forced_rank"] = args.role_binding_forced_rank
        # session/round/subject identifiers on the invocation receipt, taken from the persisted binding.
        receipt["session"] = binding_fields.get("role_binding_session")
        receipt["round"] = binding_fields.get("role_binding_round")
        receipt["subject"] = binding_fields.get("role_binding_subject")
        served = f"{used['provider']}/{used['model']}" if used is not None else None
        receipt["role_binding_served_arm"] = served
        if used is not None and served != binding_fields.get("role_binding_arm"):
            receipt["ok"] = False
            receipt["code"] = ERR_ROLE_BINDING_ARM_MISMATCH
            receipt["verdict_void_reason"] = (
                f"the served identity {served} does not match the bound role arm "
                f"{binding_fields.get('role_binding_arm')}; the role obligation is NOT fulfilled")
    if mutation.get("mutated"):
        # A checker that changed the subject has voided its own verdict, whatever it concluded --
        # this is what lets the checker run with a writable sandbox without trusting it.
        receipt["ok"] = False
        receipt["code"] = ERR_CHECKER_MUTATED_SUBJECT
        receipt["verdict_void_reason"] = (f"the guarded subject changed during the turn: "
                                          f"changed={len(mutation['changed'])} removed={len(mutation['removed'])}")
    if args.sp_identity_receipt:
        # D-06: the SP identity block the pre-spawn gate injected, carried on the invocation receipt,
        # with the join proven by the run's own nonce (the gate requires --nonce == invocation id).
        # The ERR_SP_IDENTITY_NOT_ECHOED arm is a belt over an invariant the nonce already enforces: if
        # a future change ever let ok:true stand without the child echoing the id, the receipt voids
        # itself instead of implying a join that was never observed.
        sp_rec = dict(args.sp_identity_receipt)
        real_attempts = [a for a in attempts if not a.get("injected")]
        sp_rec["attempts"] = len(real_attempts)
        sp_rec["invocation_id_echoed"] = any(bool(a.get("nonce_present")) for a in real_attempts)
        if receipt["ok"] and not sp_rec["invocation_id_echoed"]:
            receipt["ok"] = False
            receipt["code"] = "ERR_SP_IDENTITY_NOT_ECHOED"
            receipt["verdict_void_reason"] = (
                "the run reported ok but no attempt echoed the SP invocation id; the identity join is "
                "not observed and is not claimed")
        receipt["sp_identity"] = sp_rec
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0 if receipt["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
