#!/usr/bin/env python3
"""check_blueprint_amendment.py — append-only amendment check for the seven FHS
blueprints proposed in out/BLUEPRINT_AFFECTED_SCOPE_DELTA.md.

The governed rule is "never rewrite a governed byte; append, and mark the old
text superseded in place". This harness is the negative test for that rule: it
refuses an amendment that changed a single byte of the original document, moved
or rewrote an anchor line, or perturbed the L1 DesignID denominator.

Read-only: it never writes to the knowledge base (only the optional report).

Exit codes / refusal codes
  0  AMENDMENT_APPLIED            prefix byte-identical, anchor intact, marker present once
  1  AMENDMENT_PREFIX_MISMATCH    the "after" file does not start with the pinned "before" bytes
  3  AMENDMENT_ANCHOR_MISSING     the pinned anchor line is absent, moved, or rewritten
  4  DESIGNID_COUNT_DRIFT         the DesignID denominator changed (L1: 60 FHS-DR + 24 INT = 84)
  5  MARKER_MISSING               the marker is absent from the appended tail, or not exactly once
"""
import argparse
import hashlib
import json
import re
import sys


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def designids(text):
    dr = set(re.findall(r"FHS-DR-\d{3}", text))
    it = set(re.findall(r"INT-\d{2}\b", text))
    return {"fhs_dr": len(dr), "int": len(it), "total": len(dr) + len(it)}


def check(a):
    before = open(a.before, "rb").read()
    after = open(a.after, "rb").read()
    rep = {
        "doc_id": a.doc_id,
        "before": {"path": a.before, "bytes": len(before), "sha256": sha256(before)},
        "after": {"path": a.after, "bytes": len(after), "sha256": sha256(after)},
    }

    if not after.startswith(before):
        n, m = 0, min(len(before), len(after))
        while n < m and before[n] == after[n]:
            n += 1
        rep.update(code="AMENDMENT_PREFIX_MISMATCH", first_diff_offset=n,
                   detail="the amended file diverges from the pinned original at byte %d" % n)
        return 1, rep

    rep["prefix_identical"] = True
    rep["prefix_bytes"] = len(before)
    tail = after[len(before):]

    anchor = None
    if a.anchor_json:
        anchor = json.load(open(a.anchor_json, encoding="utf-8"))
    elif a.anchor_line:
        anchor = {"line": a.anchor_line, "startswith": a.anchor_text}

    if anchor:
        lines = before.split(b"\n")
        ln = anchor["line"]
        if ln > len(lines):
            rep.update(code="AMENDMENT_ANCHOR_MISSING",
                       detail="anchor line %d beyond the %d-line original" % (ln, len(lines)))
            return 3, rep
        got = lines[ln - 1].decode("utf-8", "replace")
        want = anchor["startswith"]
        if not got.startswith(want):
            rep.update(code="AMENDMENT_ANCHOR_MISSING",
                       detail="line %d reads %r, expected it to start with %r" % (ln, got[:120], want[:120]))
            return 3, rep
        rep["anchor"] = {"line": ln, "startswith": want, "intact": True}

    if a.require_designids:
        d = designids(before.decode("utf-8", "replace"))
        d2 = designids(after.decode("utf-8", "replace"))
        rep["designids_before"] = d
        rep["designids_after"] = d2
        if d["total"] != a.require_designids or d2["total"] != d["total"]:
            rep.update(code="DESIGNID_COUNT_DRIFT",
                       detail="expected %d DesignIDs; before=%d after=%d"
                              % (a.require_designids, d["total"], d2["total"]))
            return 4, rep

    n_marker = tail.count(a.marker.encode())
    if n_marker != 1:
        rep.update(code="MARKER_MISSING",
                   detail="marker %r occurs %d time(s) in the appended tail (want exactly 1)"
                          % (a.marker, n_marker))
        return 5, rep

    rep.update(code="AMENDMENT_APPLIED", status="ACCEPT",
               appended_bytes=len(tail), marker=a.marker)
    return 0, rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc-id", required=True)
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--marker", default="R27-APPEND")
    ap.add_argument("--anchor-line", type=int, default=0)
    ap.add_argument("--anchor-text", default="")
    ap.add_argument("--anchor-json", default="")
    ap.add_argument("--require-designids", type=int, default=0)
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    rc, rep = check(a)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    if a.json:
        open(a.json, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
