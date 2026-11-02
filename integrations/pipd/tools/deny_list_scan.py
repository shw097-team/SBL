#!/usr/bin/env python3
"""Classify every `danger-full-access` occurrence as a POLICY_MENTION or a WRITER_USAGE (R4 / W9).

The string `danger-full-access` appears in this tree in two very different roles:

* ``POLICY_MENTION`` - instruction / policy / contract / receipt text that *forbids* or *reports on*
  the flag (e.g. the R4 contract and the compiled prompt, which forbid it). A veto is not a usage.
* ``WRITER_USAGE``  - an actual codex invocation or sandbox setting that *enables* it, e.g. a
  ``sandbox: danger-full-access`` header on a real run, or a ``-s danger-full-access`` / 
  ``sandbox_mode=danger-full-access`` invocation.

The scan exits **non-zero only** when a ``WRITER_USAGE`` occurs inside the R4 focused-repair round
(``.hgk/rounds/R4-20261009-focused-repair/**``). Mentions and usages elsewhere are reported, not
fatal - the gate is scoped to *this round's* writers.

Exit codes: 0 = no R4 WRITER_USAGE (and, vacuously, clean); 1 = an R4 WRITER_USAGE exists.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = "danger-full-access"

# R4 writers must not enable the flag.
R4_SCOPE = ".hgk/rounds/R4-20261009-focused-repair/"

SKIP_DIRS = {".git", "__pycache__"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".so", ".dll", ".png", ".jpg", ".gif", ".zip", ".gz"}
# The classifier itself and its test contain the literal as pattern/test data, not as a live
# setting or a policy statement about this tree. Scanning them would be self-referential noise.
SELF_EXCLUDE = {"tools/deny_list_scan.py", "tests/test_deny_list_scan.py"}

# A *usage* is a sandbox directive or invocation, not prose about the flag.
_DIRECTIVE = re.compile(r"""^\s*(?:"?(?:sandbox|sandbox_mode|approval)"?\s*[:=]\s*
                             "?danger-full-access"?|danger-full-access)\s*$""", re.VERBOSE)
_INVOCATION = re.compile(r"""(?x)
    (?:^|\s)(?:-s|--sandbox|--sandbox-mode)(?:[=\s]+)"?danger-full-access"?
  | (?:^|\s)--config(?:[=\s]+)['"]?sandbox_mode['"]?\s*[=:]\s*['"]?danger-full-access
  | (?:^|\s)-c(?:[=\s]+)['"]?sandbox_mode['"]?\s*[=:]\s*['"]?danger-full-access
  | "sandbox_mode"\s*:\s*"danger-full-access"
  | sandbox_mode=danger-full-access
""")

# A TOML/INI setting that a real run toggles on, with or without a trailing `#` comment:
#   sandbox_mode = "danger-full-access"   # explicitly enabled
_TOML_SETTING = re.compile(
    r"""(?x)^\s*"?(?:sandbox|sandbox_mode|approval)"?\s*[:=]\s*
        "?danger-full-access"?\s*(?:\#.*)?$""")

# A *mention* is policy/forbidding/reporting language.
_POLICY = re.compile(r"""(?x)
    禁止 | 嚴禁 | 不得 | 不可 | 不應 | 不准          # forbid / must-not
  | forbid(?:s|den)? | prohibited | must\ not | may\ not | never\b | \bno\ file\b | \bmentions?\b
  | C9 | C10 | veto | bypass\ disclosed | receipt | disclosure
""")


def classify_line(line: str) -> str:
    """Classify one line that contains the forbidden string.

    A standalone sandbox directive / codex invocation is a WRITER_USAGE. Anything else that merely
    *contains* the string inside prose, JSON evidence, contract or prompt text is a POLICY_MENTION.
    """
    stripped = line.strip().rstrip(",")
    # A standalone sandbox directive / TOML setting is a live usage regardless of surrounding text.
    if _DIRECTIVE.match(stripped) or _TOML_SETTING.match(stripped):
        return "WRITER_USAGE"
    # An invocation *quoted inside prose that forbids it* is a mention, not a usage (e.g. a
    # contract saying "不得用 --config sandbox_mode=danger-full-access"). Forbidding language wins.
    if _INVOCATION.search(stripped):
        if _POLICY.search(line):
            return "POLICY_MENTION"
        return "WRITER_USAGE"
    if _POLICY.search(line):
        return "POLICY_MENTION"
    # Default: a quoted/reported occurrence in evidence text is a mention, not a live setting.
    return "POLICY_MENTION"


def iter_files(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if p.suffix.lower() in SKIP_SUFFIXES:
            continue
        yield p


def scan(root: Path | None = None) -> dict:
    """Return every occurrence of the forbidden string, classified."""
    root = root or ROOT
    occurrences: list[dict] = []
    for p in iter_files(root):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if FORBIDDEN not in text:
            continue
        rel = p.relative_to(root).as_posix()
        if rel in SELF_EXCLUDE:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if FORBIDDEN not in line:
                continue
            occurrences.append({"path": rel, "line": lineno, "classification": classify_line(line)})
    return {"occurrences": occurrences}


def in_r4_scope(path: str, r4_scope: str = R4_SCOPE) -> bool:
    return path.startswith(r4_scope)


def evaluate(report: dict, r4_scope: str = R4_SCOPE) -> dict:
    """Aggregate the scan: list files per class; the only fatal case is an R4 WRITER_USAGE."""
    occ = report["occurrences"]
    mentions = [o for o in occ if o["classification"] == "POLICY_MENTION"]
    usages = [o for o in occ if o["classification"] == "WRITER_USAGE"]
    r4_usages = [o for o in usages if in_r4_scope(o["path"], r4_scope)]
    return {
        "occurrences_total": len(occ),
        "policy_mention_count": len(mentions),
        "writer_usage_count": len(usages),
        "policy_mention_files": sorted({o["path"] for o in mentions}),
        "writer_usage_files": sorted({o["path"] for o in usages}),
        "r4_writer_usage": r4_usages,
        "r4_scope": r4_scope,
        "verdict": "FAIL" if r4_usages else "PASS",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Classify danger-full-access as mention vs usage (W9).")
    ap.add_argument("--root", help="scan root (default: repo root)")
    ap.add_argument("--r4-scope", default=R4_SCOPE, help="path prefix that must contain no WRITER_USAGE")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else ROOT
    report = evaluate(scan(root), r4_scope=args.r4_scope)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 1 if report["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
