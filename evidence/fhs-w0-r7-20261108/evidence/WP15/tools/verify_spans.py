#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WP-FHS-15 span verifier.

Re-reads every cited file from disk, re-slices [byte_start:byte_end), and asserts
the slice equals quoted_text. Also re-hashes the whole file and compares it with
the recorded file_sha256, so a drifted source fails loudly instead of silently.

Exit codes: 0 = all PASS, 1 = at least one FAIL, 2 = no refs found.

Usage:
  python tools/verify_spans.py [--root <evidence/WP15>]
"""
import argparse
import hashlib
import json
import os
import sys

SOURCES = r"C:\Projects\Agent_Workspace\FHS_W1_Work_Final\FHS_W1_Work_Final\sources"
W0_DIR = r"C:\Projects\Agent_Workspace\FHS_W0W2_R4_20261107\writeback\W0"
REQUIRED = ("file", "file_sha256", "byte_start", "byte_end", "quoted_text")


def resolve(name, roots):
    for r in roots:
        p = os.path.join(r, name)
        if os.path.isfile(p):
            return p
    return None


def walk_refs(node, trail, acc):
    if isinstance(node, dict):
        if all(k in node for k in REQUIRED):
            acc.append((trail, node))
            return
        for k, v in node.items():
            walk_refs(v, trail + "/" + str(k), acc)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk_refs(v, trail + "[%d]" % i, acc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    a = ap.parse_args()
    root = a.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    roots = [SOURCES, W0_DIR, root]

    files = []
    for sub in ("specs", "stages", "evidence"):
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.lower().endswith(".json"):
                files.append(os.path.join(d, fn))
    if not files:
        print("NO JSON INPUTS under", root)
        return 2

    refs = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            doc = json.load(fh)
        rel = os.path.relpath(f, root)
        walk_refs(doc, rel, refs)

    cache = {}
    ok = bad = 0
    failed = []
    for trail, r in refs:
        name = r["file"]
        p = resolve(name, roots)
        if p is None:
            bad += 1
            failed.append((trail, "FILE_NOT_FOUND " + name))
            print("FAIL  %-72s file not found: %s" % (trail, name))
            continue
        if p not in cache:
            with open(p, "rb") as fh:
                cache[p] = fh.read()
        data = cache[p]
        problems = []
        h = hashlib.sha256(data).hexdigest()
        if h != r["file_sha256"]:
            problems.append("file_sha256 drift (recorded %s…, observed %s…)"
                            % (r["file_sha256"][:12], h[:12]))
        bs, be = int(r["byte_start"]), int(r["byte_end"])
        if not (0 <= bs < be <= len(data)):
            problems.append("span out of range [%d,%d) vs %d bytes" % (bs, be, len(data)))
        else:
            try:
                got = data[bs:be].decode("utf-8")
            except UnicodeDecodeError as e:
                got = None
                problems.append("slice is not valid UTF-8: %s" % e)
            if got is not None and got != r["quoted_text"]:
                problems.append("slice != quoted_text (slice %d chars, quote %d chars)"
                                % (len(got), len(r["quoted_text"])))
        if problems:
            bad += 1
            failed.append((trail, "; ".join(problems)))
            print("FAIL  %-72s %s" % (trail, "; ".join(problems)))
        else:
            ok += 1
            print("PASS  %-72s %s[%d:%d] %d bytes"
                  % (trail, os.path.basename(name), bs, be, be - bs))

    total = ok + bad
    print("-" * 100)
    print("TOTAL %d/%d PASS, %d FAIL, %d files scanned, %d refs"
          % (ok, total, bad, len(files), total))
    if bad:
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
