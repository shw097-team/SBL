#!/usr/bin/env python3
"""Round self-scan: a credential-shape sweep folded together with the deny-list gate.

Scans every text file under the given paths for credential-shaped tokens and folds in the exit
status of the sibling ``deny_list_scan`` gate (``tools/deny_list_scan.py`` when present). Emits a
``PIPD-ROUND-SELFSCAN/1`` report and exits non-zero on any hit.

Design constraints, deliberately:

* Credential regexes are **assembled from fragments at runtime**, never written as one literal.
  This tool must not itself contain a literal credential-shaped string -- the environment's own
  secret redactor (and this tool) would otherwise flag it. A test asserts this.
* Each hit records a **redacted shape label** (e.g. ``sk-shaped token (24 chars)``), never the
  matched value, so the report is safe to publish.

CLI::

    python tools/round_selfscan.py --paths <dir> [<dir> ...] [--json-out PATH] [--deny-scan PATH]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "PIPD-ROUND-SELFSCAN/1"
CAP_BYTES = 2 * 1024 * 1024  # 2 MiB per-file scan cap
DEFAULT_DENY = ROOT / "tools" / "deny_list_scan.py"

# --- pattern fragments (never a literal credential shape in this file) -------------------------
# Each fragment is inert on its own; the shape only exists after runtime concatenation.
_SK = "s" + "k"
_GHP = "g" + "h" + "p" + "_"
_AKIA = "AK" + "IA"
_XOX = "xox" + "[" + "baprs" + "]"
_ALNUM = "[A-Za-z0-9]"
_UPPER = "[A-Z0-9]"

# (kind, compiled) specific credential shapes.
SHAPE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("sk", re.compile(_SK + "-" + _ALNUM + "{20,}")),
    ("ghp", re.compile(_GHP + _ALNUM + "{20,}")),
    ("akia", re.compile(_AKIA + _UPPER + "{16}")),
    ("xox", re.compile(_XOX + "-" + _ALNUM + "{20,}")),
]

# Generic "<keyword> =|: '<value>'" assignment of a plausibly-secret value.
_GENERIC = re.compile(r"""(?i)(secret|token|password)\s*[:=]\s*['"]([^'"]{12,})['"]""")


def _scan_text(text: str) -> list[tuple[int, str, str]]:
    """Return (line, kind, redacted-excerpt) for every credential shape found in ``text``."""
    hits: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for kind, rx in SHAPE_PATTERNS:
            m = rx.search(line)
            if m:
                hits.append((lineno, kind, f"{kind}-shaped token ({len(m.group(0))} chars)"))
        m = _GENERIC.search(line)
        if m:
            keyword = m.group(1).lower()
            hits.append((lineno, "generic", f"{keyword}-assignment ({len(m.group(2))} chars)"))
    return hits


def _scan_file(path: Path) -> tuple[bool, list[tuple[int, str, str]]]:
    """Read up to the cap; skip binaries. Return (scanned, hits).

    ``scanned`` is False for a binary file (a NUL byte in the read chunk) or an unreadable file,
    so callers never count a skipped file as scanned.
    """
    try:
        with path.open("rb") as fh:
            data = fh.read(CAP_BYTES)
    except OSError:
        return False, []
    if b"\x00" in data:
        return False, []
    text = data.decode("utf-8", errors="replace")
    return True, _scan_text(text)


def _iter_files(paths: list[str]):
    """Yield (path, display_path) for every scannable file under ``paths``.

    ``/.git/`` anywhere in the resolved path is skipped; duplicate files (a path listed twice, or
    reachable from two roots) are yielded once.
    """
    seen: set[str] = set()
    for raw in paths:
        base = Path(raw)
        if base.is_file():
            candidates: list[tuple[Path, Path]] = [(base, base.parent)]
        elif base.is_dir():
            candidates = [(f, base) for f in sorted(base.rglob("*")) if f.is_file()]
        else:
            continue
        for f, root in candidates:
            posix = str(f).replace("\\", "/")
            if "/.git/" in posix or posix.endswith("/.git"):
                continue
            key = str(f.resolve())
            if key in seen:
                continue
            seen.add(key)
            try:
                rel = f.resolve().relative_to(root.resolve()).as_posix()
            except ValueError:
                rel = f.name
            yield f, rel


def scan_paths(paths: list[str]) -> tuple[list[dict], int]:
    """Scan ``paths``; return (hits, files_scanned)."""
    hits: list[dict] = []
    files_scanned = 0
    for f, rel in _iter_files(paths):
        scanned, file_hits = _scan_file(f)
        if not scanned:
            continue
        files_scanned += 1
        for lineno, kind, excerpt in file_hits:
            hits.append({"path": rel, "line": lineno, "kind": kind, "excerpt": excerpt})
    return hits, files_scanned


def run_deny_scan(path: str | None) -> dict:
    """Run the deny-list scanner as a subprocess; record exit code and output tail."""
    if not path:
        return {"ran": False, "exit_code": None, "tail": ""}
    p = Path(path)
    if not p.exists():
        return {"ran": False, "exit_code": None, "tail": f"deny-scan script not found: {path}"}
    try:
        proc = subprocess.run(
            [sys.executable, str(p)], capture_output=True, text=True, timeout=300
        )
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover - defensive
        return {"ran": False, "exit_code": None, "tail": f"deny-scan failed to run: {exc}"}
    out = (proc.stdout or "") + (proc.stderr or "")
    tail = "\n".join(out.splitlines()[-20:])
    return {"ran": True, "exit_code": proc.returncode, "tail": tail}


def build_report(
    paths: list[str], deny_scan_path: str | None = None, now: datetime | None = None
) -> dict:
    """Assemble the ``PIPD-ROUND-SELFSCAN/1`` report for ``paths``."""
    hits, files_scanned = scan_paths(paths)
    deny = run_deny_scan(deny_scan_path)

    by_kind: dict[str, int] = {}
    for h in hits:
        by_kind[h["kind"]] = by_kind.get(h["kind"], 0) + 1

    deny_bad = deny["ran"] and deny["exit_code"] not in (0, None)
    verdict = "HIT" if (hits or deny_bad) else "PASS"

    return {
        "schema": SCHEMA,
        "as_of": (now or datetime.now(timezone.utc)).isoformat(),
        "scanned_paths": [str(p) for p in paths],
        "files_scanned": files_scanned,
        "hits": hits,
        "counts": {"by_kind": by_kind, "total": len(hits)},
        "deny_scan": deny,
        "verdict": verdict,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="round_selfscan",
        description="Credential-shape scan over text files, folded with the deny-list scan.",
    )
    ap.add_argument("--paths", nargs="+", required=True, help="files or directories to scan")
    ap.add_argument("--json-out", help="write the JSON report to this path")
    ap.add_argument(
        "--deny-scan",
        help="deny-list scanner to fold in (default: tools/deny_list_scan.py when it exists)",
    )
    args = ap.parse_args(argv)

    deny_path = args.deny_scan
    if deny_path is None and DEFAULT_DENY.exists():
        deny_path = str(DEFAULT_DENY)

    report = build_report(args.paths, deny_scan_path=deny_path)

    payload = json.dumps(report, ensure_ascii=False, indent=1)
    if args.json_out:
        Path(args.json_out).write_text(payload, encoding="utf-8")
    else:
        print(payload)

    for h in report["hits"]:
        print(f"HIT {h['kind']} {h['path']}:{h['line']} - {h['excerpt']}")
    if report["deny_scan"]["ran"]:
        print(f"deny_scan exit={report['deny_scan']['exit_code']}")
    print(
        f"verdict: {report['verdict']} "
        f"({report['counts']['total']} hits, {report['files_scanned']} files scanned)"
    )
    return 1 if report["verdict"] == "HIT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
