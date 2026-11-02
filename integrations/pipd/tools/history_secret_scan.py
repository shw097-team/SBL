#!/usr/bin/env python3
"""Scan BOTH the working tree and the git history for token-like strings (R-AUD-014 / FW-11).

Output discipline (non-negotiable): this tool prints ONLY counts and non-sensitive status codes.
It never prints a matched value and never a token prefix. The output artefact may contain pattern
names and per-file/per-object counts but no secret material.

Runs as its own process on purpose: an in-kernel import cache had once recorded pattern names from a
superseded revision of workspace.py, so the artifact disagreed with the source it claimed to
describe. Recorded facts must come from the revision being described.

The default output path (``.hgk/artifacts/history_secret_scan.json``) lies INSIDE the tracked tree,
so running this tool rewrites a committed artefact. A verifier that must leave the worktree
untouched should pass ``--out`` and write the scan elsewhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
from pipd_ls_sp.workspace import SECRET_PATTERNS  # noqa: E402


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True).stdout


def scan_worktree(root: Path = ROOT) -> tuple[dict[str, int], dict[str, int], int]:
    """Return (per_pattern_total, per_pattern_file_hits, files_scanned). Counts only.

    ``root`` is parameterisable so a caller (e.g. a test, or a receipt over a foreign subject) can
    sweep an arbitrary tree. Nothing but counts leaves this function.
    """
    totals = {n: 0 for n, _ in SECRET_PATTERNS}
    file_hits: dict[str, int] = {}
    files = 0
    for f in sorted(root.rglob("*")):
        if not f.is_file() or ".git" in f.parts or "__pycache__" in f.parts:
            continue
        if f.suffix in (".db", ".pyc"):
            continue
        files += 1
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for n, rx in SECRET_PATTERNS:
            c = len(rx.findall(txt))
            if c:
                # Key carries the pattern name + the file path only; never a matched value.
                file_hits[f"{n}::{f.relative_to(root).as_posix()}"] = c
                totals[n] += c
    return totals, file_hits, files


def scan_history(root: Path = ROOT) -> tuple[dict[str, int], int]:
    """Scan every object reachable from all refs. Return (per_pattern_total, objects_listed)."""
    shas = [l.split()[0] for l in _git("-C", str(root), "rev-list", "--objects", "--all").splitlines()
            if len(l.split()) > 1]
    batch = subprocess.run(["git", "-C", str(root), "cat-file", "--batch"],
                           input="\n".join(shas).encode(),
                           capture_output=True).stdout.decode("utf-8", "replace")
    return {n: len(rx.findall(batch)) for n, rx in SECRET_PATTERNS}, len(shas)


def printable_summary(out: dict) -> dict:
    """The ONLY projection ever printed or returned to a caller: counts + status codes."""
    return {
        "source_revision_scanned": out["source_revision_scanned"],
        "source_sha256": out["source_sha256"],
        "pattern_names": out["pattern_names"],
        "objects_listed": out["objects_listed"],
        "worktree_files_scanned": out["worktree_files_scanned"],
        "history_hits_total": out["history_hits_total"],
        "worktree_hits_total": out["worktree_hits_total"],
        "status_codes": out["status_codes"],
        "verdict": out["verdict"],
    }


DEFAULT_OUT = ROOT / ".hgk" / "artifacts" / "history_secret_scan.json"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Scan worktree + history for token-like strings.")
    ap.add_argument("--out", metavar="PATH", default=None,
                    help="write the scan artefact to this path instead of the tracked default; a "
                         "verifier that must leave the worktree untouched should pass this")
    args = ap.parse_args(argv)

    rev = _git("rev-parse", "HEAD").strip()
    src = (ROOT / "src" / "pipd_ls_sp" / "workspace.py").read_bytes()

    object_hits, objects_listed = scan_history()
    worktree_totals, worktree_hits, files = scan_worktree()

    history_total = sum(object_hits.values())
    worktree_total = sum(worktree_totals.values())
    out = {
        "schema": "PIPD-HISTORY-SECRET-SCAN/2",
        # NOTE ON SEMANTICS: this field names the revision whose SOURCE was scanned, which is
        # necessarily a commit EARLIER than the one that carries this file. A file cannot record the
        # SHA of the commit that contains it.
        "source_revision_scanned": rev,
        "candidate_binding": ("describes the source at source_revision_scanned; this file is "
                              "committed by a subsequent evidence-only commit whose src/ tests/ "
                              "schemas/ trees are identical to source_revision_scanned"),
        "source_file": "src/pipd_ls_sp/workspace.py",
        "source_sha256": hashlib.sha256(src).hexdigest(),
        "method": "each compiled pattern in pipd_ls_sp.workspace.SECRET_PATTERNS applied to "
                  "(a) every worktree file and (b) `git rev-list --objects --all | git cat-file "
                  "--batch` bytes; counts only, no matched value is ever emitted",
        "pattern_names": [n for n, _ in SECRET_PATTERNS],
        "objects_listed": objects_listed,
        "worktree_files_scanned": files,
        "history_hits": object_hits,
        "history_hits_total": history_total,
        "worktree_hits": worktree_hits,
        "worktree_hits_total": worktree_total,
        "status_codes": {
            "history": "CLEAN" if history_total == 0 else "HITS",
            "worktree": "CLEAN" if worktree_total == 0 else "HITS",
        },
        "verdict": "PASS" if (history_total == 0 and worktree_total == 0) else "FAIL",
        "note": "pattern names and the source hash are read from the revision named above, in a "
                "fresh process; only counts and status codes are printed",
    }
    p = Path(args.out) if args.out else DEFAULT_OUT
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8", newline="")

    # PRINT ONLY counts and non-sensitive status codes.
    print(json.dumps(printable_summary(out), ensure_ascii=False, indent=1))
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
