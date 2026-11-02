#!/usr/bin/env python3
"""Recompute the per-entry sha256 recorded in the evidence manifest against the bytes on disk.

Why this exists: nothing else recomputes the digest each entry of
``.hgk/artifacts/evidence_manifest.json`` claims for its file, and
``tools/build_publication_manifest.py`` folds those digests into ``crosswalk_digest``. A silent class
of drift (a file edited after the manifest was sealed) therefore stays invisible. On the tree this
tool was written for, 41 of 1085 entries are stale -- a PRE-EXISTING condition this tool only makes
visible; it never repairs the manifest and never rewrites any file.

It also reports generation-identity fields: for every JSON payload that carries ``candidate_head``,
it records whether that revision is an ancestor of HEAD. This is REPORT-ONLY (never fatal): the
committed identity is necessarily an ancestor, and reporting the few that are not makes the class
visible instead of silent.

Writes nothing except the optional ``--json`` output path; ``--strict`` is opt-in and only escalates
a non-empty ``stale`` list to a non-zero exit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / ".hgk" / "artifacts" / "evidence_manifest.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity_check(rel: str, value: object) -> dict:
    """Report whether a recorded ``candidate_head`` is an ancestor of HEAD. Never raises."""
    rec: dict = {"path": rel, "candidate_head": value, "is_ancestor": False, "error": None}
    commit = value.strip() if isinstance(value, str) else ""
    if not commit:
        rec["error"] = "candidate_head is empty or not a string"
        return rec
    try:
        resolved = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", "--quiet",
                                   f"{commit}^{{commit}}"], capture_output=True, text=True)
    except OSError:
        rec["error"] = "git unavailable"
        return rec
    if resolved.returncode != 0:
        rec["error"] = "candidate_head does not resolve to a commit"
        return rec
    ancestor = subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", commit, "HEAD"],
                              capture_output=True, text=True)
    if ancestor.returncode == 0:
        rec["is_ancestor"] = True
    elif ancestor.returncode == 1:
        rec["is_ancestor"] = False
    else:
        rec["error"] = (ancestor.stderr or "git merge-base --is-ancestor failed").strip()
    return rec


def build_report(manifest_path: Path) -> dict:
    """Recompute every recorded digest by readback and collect generation-identity checks."""
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    match = 0
    missing = 0
    stale: list[str] = []
    identity_checks: list[dict] = []
    for rel in sorted(entries):
        target = ROOT / rel
        if not target.is_file():
            missing += 1
            continue
        if _sha256(target) == entries[rel]:
            match += 1
        else:
            stale.append(rel)
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            continue
        if isinstance(payload, dict) and "candidate_head" in payload:
            identity_checks.append(_identity_check(rel, payload["candidate_head"]))
    return {
        "checked": len(entries),
        "match": match,
        "missing": missing,
        "stale": stale,
        "identity_checks": identity_checks,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Recompute evidence-manifest digests and report generation-identity ancestry.")
    ap.add_argument("--manifest", metavar="PATH", default=None,
                    help=f"manifest to verify (default: {DEFAULT_MANIFEST})")
    ap.add_argument("--json", metavar="PATH", default=None,
                    help="also write the JSON report to this path (the only file ever written)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when the stale list is non-empty (opt-in; report-only otherwise)")
    args = ap.parse_args(argv)

    report = build_report(Path(args.manifest) if args.manifest else DEFAULT_MANIFEST)
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.json:
        Path(args.json).write_text(text, encoding="utf-8", newline="")
    print(text)
    return 1 if (args.strict and report["stale"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
