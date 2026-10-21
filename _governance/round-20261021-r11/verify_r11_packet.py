#!/usr/bin/env python3
"""Re-derive the R11 round-20261021-r11 evidence digests from the live filesystem.

Purpose: let an external reviewer recompute every identity claim in
`20_SOURCE_LEDGER.json` WITHOUT trusting this packet's prose.

Usage:
    python verify_r11_packet.py --docs-dir "<SBL_PIPD-LS-PKG dir>" \
                               --mirror-dir "<mirror dir>" \
                               --kp-dir "<KnowledgePack dir>" \
                               --ledger "20_SOURCE_LEDGER.json"

Exit 0 = every recomputed digest equals the ledger. Exit 1 = at least one mismatch
(the mismatching rows are printed). Missing inputs = exit 2 (never a silent pass).

Claim ceiling: this verifies *source identity* only. It says nothing about whether any
DOC clause, Child, Surface or Host surface has been executed or accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rollup(lines):
    # DOC-00..DOC-13 order, LF-joined, NO trailing LF
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--docs-dir", required=True)
    ap.add_argument("--mirror-dir", default=None)
    ap.add_argument("--kp-dir", default=None)
    args = ap.parse_args()

    with open(args.ledger, encoding="utf-8") as fh:
        ledger = json.load(fh)

    problems = []
    rows = []

    lines = []
    total = 0
    for doc in ledger["control_package"]["docs"]:
        name = doc["file"]
        path = os.path.join(args.docs_dir, name)
        if not os.path.exists(path):
            problems.append(f"MISSING {name}")
            continue
        got = sha256(path)
        size = os.path.getsize(path)
        total += size
        lines.append(f"{doc['id']} {got}")
        ok = got == doc["sha256"] and size == doc["bytes"]
        rows.append((doc["id"], size, got[:16], "MATCH" if ok else "MISMATCH"))
        if not ok:
            problems.append(f"HASH/SIZE {name}")
        if args.mirror_dir:
            mpath = os.path.join(args.mirror_dir, name)
            if not os.path.exists(mpath) or sha256(mpath) != got:
                problems.append(f"MIRROR_NOT_BYTE_EQUAL {name}")

    got_rollup = rollup(lines)
    exp_rollup = ledger["control_package"]["rollup"]
    if got_rollup != exp_rollup:
        problems.append("ROLLUP_MISMATCH")
    if total != ledger["control_package"]["total_bytes"]:
        problems.append(f"TOTAL_BYTES {total} != {ledger['control_package']['total_bytes']}")

    if args.kp_dir:
        for row in ledger["kp"]:
            path = os.path.join(args.kp_dir, row["file"])
            if not os.path.exists(path) or sha256(path) != row["sha256"]:
                problems.append(f"KP {row['file']}")

    for doc_id, size, digest, verdict in rows:
        print(f"{doc_id:8s} bytes={size:>9d} sha256={digest}… {verdict}")
    print(f"{'TOTAL':8s} bytes={total:>9d}")
    print(f"rollup   {got_rollup}")
    print(f"expected {exp_rollup}")

    if problems:
        print("\nFAIL")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nPASS (source identity only; no execution/acceptance claim)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FileNotFoundError as exc:
        print(f"MISSING_INPUT: {exc}", file=sys.stderr)
        sys.exit(2)
