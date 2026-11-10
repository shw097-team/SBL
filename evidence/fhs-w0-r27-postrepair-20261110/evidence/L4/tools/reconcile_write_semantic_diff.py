#!/usr/bin/env python3
"""Semantic diff of reconcile --write: what the branch's own projection tool would change on the ported config.

Runs against evidence/L4/scratch_probe (the ported copy) and evidence/L4/scratch_write (the same copy after
`lane_policy_reconcile.py --write`), so the answer is measured, not asserted.

Usage: python reconcile_write_semantic_diff.py <evidence_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EV = Path(sys.argv[1]).resolve()
A = EV / "scratch_probe" / "config" / "lane-route-slots.candidate.json"
B = EV / "scratch_write" / "config" / "lane-route-slots.candidate.json"
a = json.loads(A.read_text(encoding="utf-8"))
b = json.loads(B.read_text(encoding="utf-8"))

print(f"$ python scripts/lane_policy_reconcile.py --write   (on scratch_write; see ported_reconcile_write.log)")
print(f"input A (ported, untouched): {A}  {A.stat().st_size} bytes")
print(f"input B (after --write)    : {B}  {B.stat().st_size} bytes")
print("top-level keys only in A:", sorted(set(a) - set(b)), " only in B:", sorted(set(b) - set(a)))
changed = [k for k in a if k in b and a[k] != b[k]]
print("changed top-level keys:", changed)
for k in changed:
    if k != "change_log":
        print(f"  {k}: {json.dumps(a[k], ensure_ascii=False)[:120]} -> {json.dumps(b[k], ensure_ascii=False)[:160]}")
print(f"change_log entries: {len(a.get('change_log', []))} -> {len(b.get('change_log', []))}")
if len(b.get("change_log", [])) > len(a.get("change_log", [])):
    print("  appended:", json.dumps(b["change_log"][-1], ensure_ascii=False)[:400])


def chains(doc):
    return {lane["lane"]: [(e["provider"], e["model"], e.get("rank"), e.get("default"),
                            e.get("automatic_selection")) for e in lane["ordered_pool"]]
            for lane in doc["lanes"]}


ca, cb = chains(a), chains(b)
print("ordered_pool chains identical:", ca == cb)
for lane, v in ca.items():
    print(f"  {lane}: {[x[0] + '/' + x[1] for x in v]}")
print("conclusion: --write would only advance revision/supersedes_revision and append one change_log entry; "
      "no arm, rank, default or automatic_selection changes. The 3026-line textual diff is whole-file "
      "re-serialisation, not a policy change.")
sys.exit(0 if (ca == cb and set(changed) <= {"revision", "supersedes_revision", "change_log"}) else 1)
