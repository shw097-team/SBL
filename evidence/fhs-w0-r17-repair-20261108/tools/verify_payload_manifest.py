#!/usr/bin/env python3
"""Resolve every digest inside the payload that declares it, and refuse to step outside.

`G18` used to test containment with `str.startswith`, which accepts a sibling directory whose name
merely begins with the payload's name (`payload` vs `payload-evil`).  This uses `os.path.realpath`
plus `commonpath`, so a symlink or a `../` entry cannot escape the payload it belongs to.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


def sha_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "stage"))
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    problems, totals = [], {"manifests": 0, "entries": 0, "resolved": 0}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        for fn in filenames:
            if fn not in {"MANIFEST.json", "PROVENANCE.json"}:
                continue
            mp = os.path.join(dirpath, fn)
            payload = os.path.realpath(dirpath)
            totals["manifests"] += 1
            doc = json.load(open(mp, "r", encoding="utf-8"))
            for e in doc.get("files", []):
                totals["entries"] += 1
                rel, want = e.get("path"), e.get("sha256")
                if not rel or not want:
                    problems.append({"manifest": mp, "why": "NO_PATH_OR_DIGEST"})
                    continue
                fp = os.path.realpath(os.path.join(payload, rel))
                try:
                    inside = os.path.commonpath([payload, fp]) == payload
                except ValueError:
                    inside = False
                if not inside:
                    problems.append({"manifest": os.path.relpath(mp, root), "entry": rel, "why": "PATH_OUTSIDE_PAYLOAD"})
                    continue
                if not os.path.isfile(fp):
                    problems.append({"manifest": os.path.relpath(mp, root), "entry": rel, "why": "ABSENT"})
                    continue
                got = sha_file(fp)
                if got != want:
                    problems.append({"manifest": os.path.relpath(mp, root), "entry": rel, "why": "SHA_MISMATCH", "want": want[:12], "got": got[:12]})
                    continue
                totals["resolved"] += 1
    print(json.dumps({"schema": "FHS.W0.PayloadVerify/2", "root": root.replace("\\", "/"), "totals": totals, "problems": problems}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
