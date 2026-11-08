#!/usr/bin/env python3
"""Verify a payload manifest without leaving the payload.

Run it from anywhere:

    python verify_payload_manifest.py <payload-root-or-manifest.json>

It re-hashes each declared file from bytes inside the payload and refuses:
  * an entry whose path leaves the tree            -> PATH_OUTSIDE_PAYLOAD
  * an entry whose file is missing                 -> ABSENT_IN_PAYLOAD
  * an entry whose bytes changed                   -> SHA_MISMATCH
  * an entry with no path or no digest             -> NO_PATH_OR_DIGEST

Exit 0 when every entry resolves, 1 when one does not, 2 when there is nothing to verify.
This is the check G18 performs inside the round gate; shipping it separately means an outside
reviewer does not have to trust the gate's own prose.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    target = os.path.abspath(sys.argv[1])
    if os.path.isdir(target):
        cands = [f for f in ("MANIFEST.json", "PROVENANCE.json") if os.path.isfile(os.path.join(target, f))]
        if not cands:
            print(f"NO_MANIFEST_IN {target}")
            return 2
        target = os.path.join(target, cands[0])
    base = os.path.dirname(target)
    doc = json.load(open(target, "r", encoding="utf-8"))
    entries = doc.get("files") or doc.get("entries") or doc.get("artifacts") or []
    if isinstance(entries, dict):
        entries = [{"path": k, "sha256": v} for k, v in entries.items()]

    ok = 0
    problems = []
    for e in entries:
        if not isinstance(e, dict):
            problems.append({"why": "NOT_AN_OBJECT", "entry": str(e)[:80]})
            continue
        p = e.get("path") or e.get("file") or e.get("artifact")
        d = e.get("sha256") or e.get("digest")
        if not p or not d:
            problems.append({"why": "NO_PATH_OR_DIGEST", "entry": json.dumps(e, ensure_ascii=False)[:100]})
            continue
        fp = os.path.normpath(os.path.join(base, p))
        if not (fp == base or fp.startswith(base + os.sep)):
            problems.append({"why": "PATH_OUTSIDE_PAYLOAD", "entry": p})
            continue
        if not os.path.isfile(fp):
            problems.append({"why": "ABSENT_IN_PAYLOAD", "entry": p})
            continue
        d = str(d)
        if d.startswith("sha256:"):
            d = d.split(":", 1)[1]
        actual = sha256_file(fp)
        if actual != d:
            problems.append({"why": "SHA_MISMATCH", "entry": p, "declared": d[:16], "actual": actual[:16]})
            continue
        ok += 1

    print(f"manifest={os.path.relpath(target, os.getcwd())}")
    print(f"declared={len(entries)} resolved={ok} problems={len(problems)}")
    for pr in problems:
        print("  ", pr)
    print("VERDICT", "PASS" if not problems else "FAIL")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
