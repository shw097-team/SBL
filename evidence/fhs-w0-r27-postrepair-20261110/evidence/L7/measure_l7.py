#!/usr/bin/env python3
"""L7 measurement: L1 blueprint byte/line truth, seven-blueprint digests,
and the r26 ACK claims that CH27 supersedes. Read-only."""
import hashlib, json, os, sys

KB = "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖"
SK = KB + "/各W藍圖&skeleton"
ROUND = "C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-docs/evidence/fhs-w0-r26-repair-20261109"

DOCS = [
    ("L0_總藍圖_r4",              KB + "/FHS_總藍圖_r4.md"),
    ("L1_PIPD-LS-PKG_藍圖_r4",     KB + "/FHS_PIPD-LS-PKG_藍圖_r4.md"),
    ("L2_全波次藍圖_r4",           KB + "/FHS_PIPD-LS-PKG_全波次藍圖_r4.md"),
    ("W1_skeleton_r5",            SK + "/FHS_PIPD-LS-PKG_W1_藍圖_skeleton_2026-11-04_r5.md"),
    ("W2_skeleton_r5",            SK + "/FHS_PIPD-LS-PKG_W2_藍圖_skeleton_2026-11-04_r5.md"),
    ("W3_skeleton_r5",            SK + "/FHS_PIPD-LS-PKG_W3_藍圖_skeleton_2026-11-04_r5.md"),
    ("W4_skeleton_r5",            SK + "/FHS_PIPD-LS-PKG_W4_藍圖_skeleton_2026-11-04_r5.md"),
]


def measure(p):
    b = open(p, "rb").read()
    return {
        "path": p,
        "bytes": os.stat(p).st_size,
        "len_bytes": len(b),
        "lines_lf_split": len(b.split(b"\n")),
        "lines_newline": b.count(b"\n"),
        "sha256": hashlib.sha256(b).hexdigest(),
        "ends_with_newline": b.endswith(b"\n"),
    }


print("## A. seven blueprint digests (measured from the real files)")
out = []
for name, p in DOCS:
    if not os.path.exists(p):
        print("MISSING", name, p); sys.exit(3)
    m = measure(p); m["doc"] = name
    out.append(m)
    print("%-26s bytes=%8d lines_lf_split=%6d sha256=%s"
          % (name, m["bytes"], m["lines_lf_split"], m["sha256"]))
json.dump({"measured": out}, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)

L1 = [m for m in out if m["doc"].startswith("L1_")][0]
print("\n## B. L1 truth vs the r26 ACK declaration")
print("measured L1 bytes            =", L1["bytes"])
print("measured L1 lines_lf_split   =", L1["lines_lf_split"])
print("measured L1 sha256           =", L1["sha256"])
print("ACK declared l1.bytes        = 111331   (BRIEF/ACK claim under review)")

print("\n## C. preservation denominators (4 unaffected WPs)")
per_wp = {"WP-FHS-15": 12, "WP-FHS-16": 4, "WP-FHS-19": 2, "WP-FHS-21": 1}
props_per_clause = 4
tot_clauses = sum(per_wp.values())
for k, v in per_wp.items():
    print("  %-11s clauses=%2d  properties=%2d" % (k, v, v * props_per_clause))
print("  unaffected clauses total =", tot_clauses,
      "-> 19 x 4 =", tot_clauses * props_per_clause)
print("  ACK claimed '32-4=28'      =", 32 - 4, " (refuted: 28 is a clause count, not 76 properties)")

print("\n## D. r26 round metadata claims (as declared, for the supersede record)")
ack = os.path.join(ROUND, "evidence", "FHS_ORIGINAL_ACK.json")
if os.path.exists(ack):
    raw = open(ack, "rb").read()
    print("ACK file bytes=", len(raw), "sha256=", hashlib.sha256(raw).hexdigest())
    j = json.loads(raw.decode("utf-8"))
    sc = j.get("subject_scope", {}).get("source_contract", {})
    print("ACK l1 =", json.dumps(sc.get("l1"), ensure_ascii=False))
    inv = sc.get("source_inventory") or j.get("source_inventory")
    print("ACK source_inventory =", json.dumps(inv, ensure_ascii=False)[:300])
    up = j.get("unaffected_proof")
    print("ACK unaffected_proof =", json.dumps(up, ensure_ascii=False)[:600])
else:
    print("ACK NOT FOUND at", ack)

print("\n## E. EVIDENCE_SCOPE")
es = os.path.join(ROUND, "evidence", "EVIDENCE_SCOPE.json")
if os.path.exists(es):
    raw = open(es, "rb").read()
    print("EVIDENCE_SCOPE bytes=", len(raw), "sha256=", hashlib.sha256(raw).hexdigest())
    j = json.loads(raw.decode("utf-8"))
    full = j.get("profiles", {}).get("full", {})
    print("profiles.full.excluded =", json.dumps(full.get("excluded"), ensure_ascii=False))
    print("profiles.full keys     =", list(full.keys()))
else:
    print("EVIDENCE_SCOPE NOT FOUND at", es)
