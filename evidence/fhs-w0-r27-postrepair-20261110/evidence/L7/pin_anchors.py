#!/usr/bin/env python3
"""pin_anchors.py — verify every anchor line the delta relies on, against the real
knowledge-base file, and print the verbatim line text + the document digest.

An anchor is (line number, must-start-with). It is pinned so that a later
re-publication of the blueprint that shifts the line cannot silently re-point the
proposal. Read-only.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KB = "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖"
A = json.load(open(os.path.join(HERE, "anchors.json"), encoding="utf-8"))

bad = 0
for doc, spec in A["docs"].items():
    p = os.path.join(KB, spec["file"])
    b = open(p, "rb").read()
    lines = b.split(b"\n")
    print("## %s  %s" % (doc, spec["file"]))
    print("   bytes=%d lines_lf_split=%d sha256=%s" % (len(b), len(lines), hashlib.sha256(b).hexdigest()))
    for s in spec["spans"]:
        got = lines[s["line"] - 1].decode("utf-8", "replace")
        ok = got.startswith(s["startswith"])
        bad += 0 if ok else 1
        print("   %-6s L%-6d %-26s %s" % (s["id"], s["line"], s["kind"], "OK" if ok else "MISMATCH"))
        print("          %s" % got[:110])
        if not ok:
            print("          wanted startswith: %s" % s["startswith"][:110])
    print()

print("anchors checked =", sum(len(d["spans"]) for d in A["docs"].values()), " mismatches =", bad)
sys.exit(1 if bad else 0)
