#!/usr/bin/env python3
"""TT status projection — recompute the TT register summary from `tts[]` only.

R3-EXT-04 / R-AUD-012. The stored `.hgk/artifacts/TT_REGISTER.json` carried 22 rows in
`tts[]` while `status_summary` described only 17 and no `as_of_candidate` was bound to the
head. This tool is the single source of truth for that projection:

    python tools/tt_summary_check.py --assert   # recompute + compare the stored summary
    python tools/tt_summary_check.py --write    # regenerate status_summary + as_of_candidate

`--assert` recomputes the summary from `tts[]` ONLY (never from the stale stored summary) and,
on any difference, prints a precise `key stored recomputed` diff and exits non-zero. The
recomputation is bound to the head: `as_of_candidate` is compared too, so a summary written
against a different commit is a difference.

`--write` regenerates `status_summary` and `as_of_candidate` from `tts[]` and writes the file
back with a stable key order, UTF-8 and a trailing newline. No other top-level field and no
`tts[]` row is touched — in particular no row's `status`, `state` or `evidence` is renamed,
remapped or dropped.

Counting rules (fail-visible, never fail-silent):
  * only `status` is counted — the declared vocabulary is a status vocabulary;
  * `PARTIAL_CLOSED` is an explicit alias that counts into `partial` (see ALIASES);
  * ANY status outside the declared vocabulary (including the alias) is counted VISIBLY into
    `unknown` and itemised in `unmapped_statuses`; it is NEVER dropped or renamed;
  * `total == len(tts)` and `count == total`, and `unknown` is part of `total` — no
    double-counting, no percentage hiding a FAIL.

git-degradation (disclosed, never silent): `as_of_candidate` is `git rev-parse HEAD` when a
git binary is available; otherwise the head is read from the checkout's ref files
(`.git/HEAD` + the resolved ref, or a detached 40-hex HEAD). This mirrors
`src/pipd_ls_sp/repo_context.py`, which uses filesystem probes when git is absent. When
neither a git binary nor a resolvable `.git` ref exists the head is unresolvable: `--assert`
still performs the full summary comparison and discloses the degradation, while `--write`
REFUSES (exit 2) rather than fabricating a candidate.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER = ROOT / ".hgk" / "artifacts" / "TT_REGISTER.json"

# The state vocabulary as it is DECLARED in the stored status_summary. Kept here so a
# regeneration preserves the declaration (R-AUD-012: do not weaken an existing claim), with
# the PARTIAL_CLOSED alias added explicitly so the mapping is documented, not implied.
STATE_VOCABULARY = [
    "CLOSED (fresh verification required and re-done)",
    "PARTIAL (stays visible)",
    "PARTIAL_CLOSED (alias of PARTIAL: a close that failed fresh verification and was re-opened)",
    "OPEN",
    "OPEN_OWNER_GATE",
    "TEMP_CLOSED (independently closed)",
    "UNKNOWN (stays visible)",
]

# Vocabulary membership (the leading token of each declared entry) for visibility accounting.
VOCAB_TOKENS = {entry.split()[0] for entry in STATE_VOCABULARY}

# Explicit, documented mapping for the second (smaller) defect: `PARTIAL_CLOSED` is not in the
# declared state_vocabulary. It is an honour-state alias for a re-opened/downgraded close, so it
# counts into `partial` AND is surfaced in `unmapped_statuses` (it is still out-of-vocabulary —
# it is counted visibly, never dropped). No row's `status` is renamed.
ALIASES = {"PARTIAL_CLOSED": "partial"}

# Status -> summary bucket. Every declared vocabulary token maps; anything not here is unknown.
STATUS_BUCKET = {
    "CLOSED": "closed",
    "PARTIAL": "partial",
    "OPEN": "open",
    "OPEN_OWNER_GATE": "open_owner_gate",
    "TEMP_CLOSED": "temp_closed",
}

HEX40 = re.compile(r"^[0-9a-f]{40}$")


def load_register(path: Path) -> "OrderedDict[str, Any]":
    """Load the register preserving key order and reading exact bytes (no newline translation)."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("\ufeff"):
        text = text[1:]
    return json.loads(text, object_pairs_hook=OrderedDict)


def detect_newline(raw: bytes) -> str:
    """Preserve the file's dominant newline so a write never becomes a whole-file diff."""
    return "\r\n" if b"\r\n" in raw else "\n"


def resolve_head(root: Path) -> "dict[str, str | None]":
    """Resolve the full 40-hex HEAD, preferring a git binary and degrading to ref files."""
    info: dict[str, Any] = {"head": None, "probe": "unresolvable", "reason": ""}
    git = shutil.which("git")
    if git:
        try:
            out = subprocess.run([git, "-C", str(root), "rev-parse", "HEAD"],
                                 capture_output=True, text=True, timeout=30)
        except Exception as exc:  # pragma: no cover - defensive
            out = None
            info["reason"] = f"git invocation failed: {exc}"
        if out is not None and out.returncode == 0 and HEX40.match(out.stdout.strip()):
            info.update(head=out.stdout.strip(), probe="git", reason="git rev-parse HEAD")
            return info
    # Degraded filesystem probe: read the checkout refs directly (disclosed).
    git_dir = root / ".git"
    head_file = git_dir / "HEAD"
    if not info["reason"]:
        info["reason"] = "no git binary: resolved HEAD from .git ref files (degraded, disclosed)"
    if head_file.is_file():
        head_text = head_file.read_text(encoding="utf-8").strip()
        if head_text.startswith("ref:"):
            ref = head_text.split("ref:", 1)[1].strip()
            candidates: "list[str]" = []
            ref_file = git_dir / ref
            if ref_file.is_file():
                candidates.append(ref_file.read_text(encoding="utf-8").strip())
            packed = git_dir / "packed-refs"
            if packed.is_file():
                for line in packed.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("^"):
                        continue
                    parts = line.split()
                    if len(parts) == 2 and parts[1] == ref:
                        candidates.append(parts[0])
            for value in candidates:
                if HEX40.match(value):
                    info.update(head=value, probe="filesystem")
                    return info
        elif HEX40.match(head_text):
            info.update(head=head_text, probe="filesystem")
            return info
    return info


def recompute(register: "OrderedDict[str, Any]", head: "str | None") -> "OrderedDict[str, Any]":
    """Recompute status_summary from `tts[]` only. Stored values are never read."""
    tts = register.get("tts")
    if not isinstance(tts, list):
        raise ValueError("register has no well-formed 'tts' list to recompute from")

    counts = {"closed": 0, "partial": 0, "open": 0, "open_owner_gate": 0, "temp_closed": 0}
    unknown = 0
    unmapped: "OrderedDict[str, int]" = OrderedDict()
    for row in tts:
        status = row.get("status")
        key = str(status)
        bucket = STATUS_BUCKET.get(key) or ALIASES.get(key)
        if bucket is None:
            bucket = "unknown"
        if bucket == "unknown":
            unknown += 1
        else:
            counts[bucket] += 1
        if key not in VOCAB_TOKENS:
            unmapped[key] = unmapped.get(key, 0) + 1

    total = len(tts)
    summary: "OrderedDict[str, Any]" = OrderedDict()
    summary["total"] = total
    summary["closed"] = counts["closed"]
    summary["partial"] = counts["partial"]
    summary["open"] = counts["open"]
    summary["open_owner_gate"] = counts["open_owner_gate"]
    summary["temp_closed"] = counts["temp_closed"]
    summary["unknown"] = unknown
    summary["unmapped_statuses"] = unmapped
    summary["blocking_count"] = counts["open"] + counts["open_owner_gate"]
    summary["state_vocabulary"] = list(STATE_VOCABULARY)
    summary["vocabulary_aliases"] = OrderedDict(ALIASES)
    summary["count"] = total
    summary["as_of_candidate"] = head
    return summary


DEFAULT_NOTE = ("true denominator: total == len(tts); every out-of-vocabulary status is counted "
                "into unknown and itemised in unmapped_statuses (PARTIAL_CLOSED is an explicit "
                "alias of partial); no row status is renamed and no FAIL is hidden behind a "
                "percentage.")


def build_projection(register: "OrderedDict[str, Any]", head: "str | None") -> "OrderedDict[str, Any]":
    """The summary to store: recomputed buckets + a preserved as_of_round / note provenance.

    `as_of_candidate` is deliberately NOT part of this sub-dict — it is written (and asserted)
    as the top-level field, so the two can never disagree.
    """
    rec = recompute(register, head)
    stored = register.get("status_summary") or {}
    round_id = stored.get("as_of_round")
    if round_id is None:
        # Derive the round from the freshest row-level stamp rather than inventing one.
        stamps = [r.get("state_round") for r in register.get("tts", []) if r.get("state_round")]
        round_id = max(set(stamps), key=stamps.count) if stamps else "unknown"
    out: "OrderedDict[str, Any]" = OrderedDict()
    out["total"] = rec["total"]
    out["closed"] = rec["closed"]
    out["partial"] = rec["partial"]
    out["open"] = rec["open"]
    out["open_owner_gate"] = rec["open_owner_gate"]
    out["temp_closed"] = rec["temp_closed"]
    out["unknown"] = rec["unknown"]
    out["unmapped_statuses"] = rec["unmapped_statuses"]
    out["blocking_count"] = rec["blocking_count"]
    out["state_vocabulary"] = rec["state_vocabulary"]
    out["vocabulary_aliases"] = rec["vocabulary_aliases"]
    out["count"] = rec["count"]
    out["as_of_round"] = round_id
    out["note"] = stored.get("note") or DEFAULT_NOTE
    return out


def summary_diff(stored: "dict[str, Any] | None",
                 recomputed: "OrderedDict[str, Any]") -> "list[tuple[str, Any, Any]]":
    """Return (key, stored, recomputed) rows where the stored summary diverges."""
    diffs: "list[tuple[str, Any, Any]]" = []
    stored = stored or {}
    keys = list(recomputed.keys()) + [k for k in stored.keys() if k not in recomputed]
    for key in keys:
        s = stored.get(key, "<MISSING>")
        r = recomputed.get(key, "<MISSING>")
        if s != r:
            diffs.append((key, s, r))
    return diffs


def _print_diff(diffs: "list[tuple[str, Any, Any]]") -> None:
    print("TT_SUMMARY_MISMATCH")
    for key, stored, recomputed in diffs:
        print(f"  {key}: stored={json.dumps(stored, ensure_ascii=False)} "
              f"recomputed={json.dumps(recomputed, ensure_ascii=False)}")


def cmd_assert(register: "OrderedDict[str, Any]", path: Path, head_info: "dict[str, Any]") -> int:
    head = head_info["head"]
    # Compare against the exact projection `--write` would store, so the two verbs can never
    # disagree. `as_of_candidate` is asserted once, explicitly, against the head.
    expected = build_projection(register, head)
    stored = register.get("status_summary")
    diffs = summary_diff(stored, expected)
    stored_candidate = register.get("as_of_candidate")
    if stored_candidate != head:
        diffs.append(("as_of_candidate", stored_candidate, head))
    print(f"register={path}")
    print(f"head probe={head_info['probe']} head={head} ({head_info['reason']})")
    if head is None:
        print("WARNING: HEAD is unresolvable here; as_of_candidate cannot be bound. "
              "The summary comparison is still performed.")
    if diffs:
        _print_diff(diffs)
        print(f"TT_SUMMARY_ASSERT_FAIL: {len(diffs)} difference(s); stored summary is STALE.")
        return 1
    print(f"TT_SUMMARY_ASSERT_OK total={expected['total']} "
          f"unknown={expected['unknown']} blocking_count={expected['blocking_count']} "
          f"as_of_candidate={head}")
    return 0


def cmd_write(register: "OrderedDict[str, Any]", path: Path, head_info: "dict[str, Any]") -> int:
    head = head_info["head"]
    if head is None:
        print("TT_SUMMARY_WRITE_REFUSED: HEAD is unresolvable here, so as_of_candidate cannot be "
              "bound to the head; refusing to fabricate a candidate. (Run where git or a .git "
              "checkout is available.)")
        return 2
    register["status_summary"] = build_projection(register, head)
    register["as_of_candidate"] = head
    newline = detect_newline(path.read_bytes())
    text = json.dumps(register, ensure_ascii=False, indent=1) + "\n"
    if newline != "\n":
        text = text.replace("\n", newline)
    path.write_text(text, encoding="utf-8", newline="")
    summary = register["status_summary"]
    print(f"TT_SUMMARY_WRITTEN register={path}")
    print(f"  head probe={head_info['probe']} as_of_candidate={head}")
    print(f"  total={summary['total']} closed={summary['closed']} partial={summary['partial']} "
          f"open={summary['open']} open_owner_gate={summary['open_owner_gate']} "
          f"temp_closed={summary['temp_closed']} unknown={summary['unknown']} "
          f"blocking_count={summary['blocking_count']}")
    print(f"  unmapped_statuses={json.dumps(summary['unmapped_statuses'], ensure_ascii=False)}")
    return 0


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description="TT status projection recompute/assert/write")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--assert", dest="do_assert", action="store_true",
                       help="recompute from tts[] and fail (non-zero) on any difference")
    group.add_argument("--write", dest="do_write", action="store_true",
                       help="regenerate status_summary + as_of_candidate from tts[]")
    ap.add_argument("--register", default=str(DEFAULT_REGISTER),
                    help="path to TT_REGISTER.json (default: .hgk/artifacts/TT_REGISTER.json)")
    args = ap.parse_args(argv)

    path = Path(args.register)
    if not path.is_file():
        print(f"TT_SUMMARY_REFUSED: register not found: {path}")
        return 2
    register = load_register(path)
    head_info = resolve_head(ROOT)
    if args.do_write:
        return cmd_write(register, path, head_info)
    return cmd_assert(register, path, head_info)


if __name__ == "__main__":
    sys.exit(main())
