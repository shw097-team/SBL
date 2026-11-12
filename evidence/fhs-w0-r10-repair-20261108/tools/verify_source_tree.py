#!/usr/bin/env python3
"""Recompute the 31 source digests from a tree the reader supplies.

`EC-R9-011` is correct that a round cannot ship 22 MB of source into a repository and still call it
evidence, and equally correct that a gate nobody else can re-run is not a gate.  The compromise: the
round ships the per-file digest table and this program, so anyone holding the same 31 files can
reproduce the lock without trusting the round.

    python tools/verify_source_tree.py --sources <path-to-31-files>

Exit 0 when every one of the 31 matches the declared digest, 1 otherwise, 2 when the tree cannot be
read at all (which is not the same as a mismatch and must not be reported as one).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.join(HERE, "..", "lanes", "A", "SOURCE_LOCK_V3.json")


def sha(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    if not os.path.isdir(a.sources):
        print(f"source tree not readable: {a.sources}", file=sys.stderr)
        return 2
    lock = json.load(open(LOCK, encoding="utf-8"))
    rows, missing, mismatch = [], [], []
    for rec in lock["sources"]:
        p = os.path.join(a.sources, rec["file"])
        if not os.path.isfile(p):
            missing.append(rec["file"])
            rows.append({"source_id": rec["source_id"], "file": rec["file"], "state": "ABSENT"})
            continue
        raw = open(p, "rb").read()
        got = hashlib.sha256(raw).hexdigest()
        ok = got == rec["sha256"]
        if not ok:
            mismatch.append(rec["file"])
        rows.append({
            "source_id": rec["source_id"], "file": rec["file"],
            "bytes": len(raw), "lines_newline_count": raw.count(b"\n"), "sha256": got,
            "declared_sha256": rec["sha256"], "match": ok,
            "state": "MATCH" if ok else "MISMATCH",
        })
    out = {
        "schema": "FHS.W0.SourceTreeVerify/1",
        "sources_dir": os.path.abspath(a.sources).replace("\\", "/"),
        "declared_by": {"path": "lanes/A/SOURCE_LOCK_V3.json", "sha256_of_lock": sha(LOCK)},
        "totals": {"declared": len(lock["sources"]), "matched": sum(1 for r in rows if r.get("match")),
                   "missing": len(missing), "mismatched": len(mismatch)},
        "missing": missing,
        "mismatched": mismatch,
        "rows": rows,
    }
    if a.json:
        json.dump(out, open(a.json, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    t = out["totals"]
    print(f"{t['matched']}/{t['declared']} matched, {t['missing']} absent, {t['mismatched']} mismatched")
    for m in missing[:5]:
        print(f"  absent: {m}")
    for m in mismatch[:5]:
        print(f"  mismatch: {m}")
    return 0 if t["matched"] == t["declared"] else 1


if __name__ == "__main__":
    sys.exit(main())
