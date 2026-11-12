#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WP-FHS-21 oracle plan checker (author side, SOURCE_READ only).

What it proves: the plan in tables/*.json is source-bound and internally
consistent.  What it does NOT prove: that any oracle was executed, that the
original protected runner/checker accepted anything, or that the plan is
correct with respect to the world.  See REPORT.json claim_ceiling.

Checks
  C1  every source_ref's quoted_text equals the bytes at [byte_start, byte_end)
  C2  every source_ref's quoted_text occurs exactly once in the source
  C3  id uniqueness within each table
  C4  every record has a non-empty firstfail_code and a non-empty consumer
  C5  POS observation != NEG observation for every record (discriminating oracle)
  C6  each table's measured count equals the count declared in REPORT.json
  C7  the primary source sha256 equals the pinned FHS-BODY-07 sha256
  C8  structural: 96 = 12 TestClass x 8 OracleType, complete cross product,
      corrupt tokens contiguous __CORRUPT__001..096
  C9  structural: AC15 = E01..E15 contiguous with 15 distinct sender->receiver
      pairs; H4 = 01..12 contiguous; SEAM = 01..11 contiguous

Usage
  python tools/oracle_plan_check.py              # full run, prints per-check results
  python tools/oracle_plan_check.py --cell ID    # single-row replay for an oracle owner
Exit code 0 = all checks passed, 1 = at least one failure.
"""
import argparse
import hashlib
import json
import os
import re
import sys

WP = "WP-FHS-21"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES = os.path.join(ROOT, "tables")
REPORT = os.path.join(ROOT, "REPORT.json")

BODY07_SHA = "81a8c2f1cc4629f59829f11f87aebd14cd57f7c4dd0970d672880e90e2899741"
SOURCE_BASENAME = "07_ACCEPTANCE_CHALLENGE(4).md"
SOURCE_CANDIDATES = [
    os.path.join(ROOT, "sources", SOURCE_BASENAME),
    r"C:\Projects\Agent_Workspace\FHS_W1_Work_Final\FHS_W1_Work_Final\sources\%s" % SOURCE_BASENAME,
]

TABLE_FILES = [("AC15", "AC15.json", "ac_id"), ("ORACLE96", "ORACLE96.json", "cell_id"),
               ("H4", "H4.json", "cell_id"), ("SEAM", "SEAM.json", "cell_id")]
REPORT_KEYS = {"AC15": "ac15", "ORACLE96": "oracle96", "H4": "h4", "SEAM": "seam"}

RESULTS = []          # (check_id, ok, detail)


def ok(cid, detail):
    RESULTS.append((cid, True, detail))


def bad(cid, detail):
    RESULTS.append((cid, False, detail))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def resolve_source():
    for p in SOURCE_CANDIDATES:
        if os.path.isfile(p):
            return p
    return None


def load_tables():
    out = {}
    for name, fn, idkey in TABLE_FILES:
        path = os.path.join(TABLES, fn)
        if not os.path.isfile(path):
            bad("C0:%s" % name, "table missing: %s" % path)
            continue
        doc = json.load(open(path, encoding="utf-8"))
        out[name] = doc
        if not isinstance(doc.get("records"), list) or not doc["records"]:
            bad("C0:%s" % name, "records empty or not a list")
    return out


# --------------------------------------------------------------------- checks
def check_source(tables, src_path, src_bytes):
    got = sha(src_bytes)
    if got == BODY07_SHA:
        ok("C7:source_sha256", "%s sha256=%s matches pinned FHS-BODY-07 sha" % (SOURCE_BASENAME, got))
    else:
        bad("C7:source_sha256", "sha256 drift: got %s expected %s" % (got, BODY07_SHA))

    for name, doc in tables.items():
        for r in doc["records"]:
            ref = r.get("source_ref") or {}
            rid = r.get("ac_id") or r.get("cell_id")
            try:
                a, b = int(ref["byte_start"]), int(ref["byte_end"])
            except (KeyError, TypeError, ValueError):
                bad("C1:%s:%s" % (name, rid), "source_ref missing byte_start/byte_end")
                continue
            if not (0 <= a < b <= len(src_bytes)):
                bad("C1:%s:%s" % (name, rid), "span out of range [%d,%d) file=%d" % (a, b, len(src_bytes)))
                continue
            got_q = src_bytes[a:b]
            want_q = ref.get("quoted_text", "")
            if got_q != want_q.encode("utf-8"):
                bad("C1:%s:%s" % (name, rid), "quoted_text != bytes at [%d,%d)" % (a, b))
                continue
            n = src_bytes.count(want_q.encode("utf-8"))
            if n != 1:
                bad("C2:%s:%s" % (name, rid), "quoted_text occurs %d times (need 1)" % n)
            else:
                ok("C1+C2:%s:%s" % (name, rid), "bytes [%d,%d) exact, unique, %d bytes" % (a, b, b - a))


def check_uniqueness(tables):
    for name, doc in tables.items():
        idkey = dict((n, k) for n, _f, k in TABLE_FILES)[name]
        ids = [r[idkey] for r in doc["records"]]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            bad("C3:%s" % name, "duplicate ids: %s" % dupes)
        else:
            ok("C3:%s" % name, "%d ids unique (%s .. %s)" % (len(ids), ids[0], ids[-1]))


def check_fields(tables):
    for name, doc in tables.items():
        bads = []
        for r in doc["records"]:
            rid = r.get("ac_id") or r.get("cell_id")
            if not str(r.get("firstfail_code", "")).strip():
                bads.append("%s:empty firstfail_code" % rid)
            if not str(r.get("consumer", "")).strip():
                bads.append("%s:empty consumer" % rid)
        if bads:
            bad("C4:%s" % name, "; ".join(bads[:8]))
        else:
            ok("C4:%s" % name, "%d/%d records have firstfail_code+consumer" % (len(doc["records"]), len(doc["records"])))


def check_discriminating(tables):
    for name, doc in tables.items():
        same, empty = [], []
        for r in doc["records"]:
            rid = r.get("ac_id") or r.get("cell_id")
            pos = str(r.get("pos", r.get("expected_observation", ""))).strip()
            neg = str(r.get("neg", r.get("neg_observation", ""))).strip()
            if not pos or not neg:
                empty.append(rid)
            elif pos == neg:
                same.append(rid)
        if same or empty:
            bad("C5:%s" % name, "identical POS/NEG: %s ; empty: %s" % (same[:6], empty[:6]))
        else:
            ok("C5:%s" % name, "%d/%d records have POS != NEG (non-degenerate oracle)"
               % (len(doc["records"]), len(doc["records"])))


def check_counts(tables):
    if not os.path.isfile(REPORT):
        bad("C6:REPORT", "REPORT.json missing, cannot reconcile counts")
        return
    rep = json.load(open(REPORT, encoding="utf-8"))
    declared = rep.get("counts", {})
    for name, doc in tables.items():
        key = REPORT_KEYS[name]
        if key not in declared:
            bad("C6:%s" % name, "REPORT.json has no counts.%s" % key)
            continue
        d = declared[key]
        m = len(doc["records"])
        if not isinstance(d, int):
            bad("C6:%s" % name, "declared count not an int: %r" % (d,))
        elif d != m:
            bad("C6:%s" % name, "declared=%d measured=%d delta=%+d" % (d, m, m - d))
        else:
            ok("C6:%s" % name, "declared=%d measured=%d reconcile" % (d, m))


def check_structure(tables):
    o = tables.get("ORACLE96", {}).get("records", [])
    classes = sorted({r["test_class"] for r in o})
    kinds = sorted({r["oracle_kind"] for r in o})
    cross = {(r["test_class"], r["oracle_kind"]) for r in o}
    idx = sorted(int(re.sub(r"\D", "", r["corrupt_token"])) for r in o if r.get("corrupt_token"))
    cond = (len(o) == 96, len(classes) == 12, len(kinds) == 8,
            len(cross) == 96, idx == list(range(1, 97)))
    if all(cond):
        ok("C8:ORACLE96", "96 = %dx%d complete cross product; __CORRUPT__001..096 contiguous 1:1 with cells"
           % (len(classes), len(kinds)))
    else:
        bad("C8:ORACLE96", "count=%d classes=%d kinds=%d cross=%d corrupt_contiguous=%s"
            % (len(o), len(classes), len(kinds), len(cross), idx == list(range(1, 97))))

    a = tables.get("AC15", {}).get("records", [])
    aids = [r["ac_id"] for r in a]
    pairs = {(r["sender"], r["receiver"]) for r in a}
    if aids == ["AC-E%02d" % i for i in range(1, 16)] and len(pairs) == 15:
        ok("C9:AC15", "AC-E01..E15 contiguous; 15 distinct sender->receiver pairs; payload types: %s"
           % ",".join(sorted({r["payload_kind"] for r in a})))
    else:
        bad("C9:AC15", "ids=%s distinct_pairs=%d" % (aids, len(pairs)))

    h = [r["cell_id"] for r in tables.get("H4", {}).get("records", [])]
    if h == ["H4-%02d" % i for i in range(1, 13)]:
        ok("C9:H4", "H4-01..H4-12 contiguous; %d distinct firstfail codes"
           % len({r["firstfail_code"] for r in tables["H4"]["records"]}))
    else:
        bad("C9:H4", "ids=%s" % h)

    s = [r["cell_id"] for r in tables.get("SEAM", {}).get("records", [])]
    if s == ["SEAM-%02d" % i for i in range(1, 12)]:
        ok("C9:SEAM", "SEAM-01..SEAM-11 contiguous; %d distinct firstfail codes"
           % len({r["firstfail_code"] for r in tables["SEAM"]["records"]}))
    else:
        bad("C9:SEAM", "ids=%s" % s)


# ----------------------------------------------------------------- single cell
def replay_cell(cid, tables, src_path, src_bytes):
    hit = None
    for name, doc in tables.items():
        for r in doc["records"]:
            if r.get("ac_id") == cid or r.get("cell_id") == cid:
                hit = (name, r)
                break
        if hit:
            break
    if not hit:
        print("NOT_FOUND %s" % cid)
        return 1
    name, r = hit
    ref = r["source_ref"]
    span = src_bytes[int(ref["byte_start"]):int(ref["byte_end"])]
    good = span == ref["quoted_text"].encode("utf-8")
    print("== %s / %s ==" % (name, cid))
    print("source      : %s" % src_path)
    print("span        : [%d,%d) line %s  (byte-exact: %s)"
          % (ref["byte_start"], ref["byte_end"], ref.get("line"), "YES" if good else "NO"))
    print("quoted_text : %s" % ref["quoted_text"].replace("\n", "\\n"))
    for f in ("test_class", "oracle_kind", "payload_kind", "sender", "receiver", "criterion",
              "applicability", "expected_observation", "neg_observation", "pos", "neg",
              "corrupt_token", "firstfail_code", "consumer", "requirement", "runner_state"):
        if f in r:
            print("%-12s: %s" % (f, r[f]))
    if "source_ref" in r and not good:
        print("VERDICT: SOURCE_SPAN_MISMATCH (row must not be used)")
        return 1
    print("VERDICT: ROW_SOURCE_BOUND (plan row is replayable; oracle itself NOT_EXECUTED)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", help="print one row and re-verify its source span")
    args = ap.parse_args()

    src_path = resolve_source()
    if not src_path:
        print("FATAL: source %s not found in: %s" % (SOURCE_BASENAME, SOURCE_CANDIDATES))
        return 1
    src_bytes = open(src_path, "rb").read()
    tables = load_tables()

    if args.cell:
        return replay_cell(args.cell, tables, src_path, src_bytes)

    print("WP-FHS-21 oracle plan checker")
    print("root        : %s" % ROOT)
    print("source      : %s (%d bytes)" % (src_path, len(src_bytes)))
    print("")

    check_source(tables, src_path, src_bytes)
    check_uniqueness(tables)
    check_fields(tables)
    check_discriminating(tables)
    check_counts(tables)
    check_structure(tables)

    fails = 0
    for cid, good, detail in RESULTS:
        if not good:
            fails += 1
        print("[%s] %-28s %s" % ("PASS" if good else "FAIL", cid, detail))

    total = len(RESULTS)
    print("")
    print("checks=%d pass=%d fail=%d" % (total, total - fails, fails))
    print("counts: AC15=%d ORACLE96=%d H4=%d SEAM=%d"
          % tuple(len(tables[k]["records"]) for k in ("AC15", "ORACLE96", "H4", "SEAM")))
    print("verdict: %s" % ("AUTHOR_SIDE_PLAN_CONSISTENT (NOT a protected-checker verdict)"
                           if fails == 0 else "PLAN_INCONSISTENT"))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
