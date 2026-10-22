"""Two-sided guard for a bounded writer: snapshot the round tree and the governed repos.

Usage: python tools/guard_write.py before|after <out.json>
"""
import hashlib
import json
import os
import subprocess
import sys

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
GOVERNED = {
    "HG_KSEOS": r"C:/Projects/Agent_Workspace/HG-KSEOS",
    "FABRIC": r"C:/Projects/Agent_Workspace/Fabric",
    "SBL_MAIN": r"C:/Projects/Agent_Workspace/SBL",
    "EVIDENCE_WORKTREE": r"C:/Projects/Agent_Workspace/_r152_ev",
}
EXCLUDE_PREFIX = ("receipts/dispatch/",)


def tree(root):
    out = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for f in fn:
            fp = os.path.join(dp, f)
            rel = os.path.relpath(fp, root).replace("\\", "/")
            if rel.startswith(EXCLUDE_PREFIX):
                continue
            out[rel] = hashlib.sha256(open(fp, "rb").read()).hexdigest()
    return out


def git_status(path):
    r = subprocess.run(["git", "-C", path, "status", "--porcelain=v1", "-uall"],
                       capture_output=True, text=True)
    head = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True, text=True)
    return {"head": head.stdout.strip(), "dirty_count": len([l for l in r.stdout.splitlines() if l.strip()]),
            "dirty_sample": [l for l in r.stdout.splitlines() if l.strip()][:10]}


phase = sys.argv[1]
out_path = sys.argv[2]
snap = {"phase": phase, "round_tree": tree(R), "repos": {k: git_status(v) for k, v in GOVERNED.items()}}
os.makedirs(os.path.dirname(out_path), exist_ok=True)
open(out_path, "w", encoding="utf-8", newline="\n").write(json.dumps(snap, ensure_ascii=False, indent=2) + "\n")

if phase == "after":
    before_path = out_path.replace("_after.json", "_before.json")
    before = json.load(open(before_path, encoding="utf-8"))
    b, a = before["round_tree"], snap["round_tree"]
    added = sorted(set(a) - set(b))
    removed = sorted(set(b) - set(a))
    modified = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    print(json.dumps({"added": len(added), "removed": len(removed), "modified": len(modified),
                      "added_sample": added[:12], "modified_sample": modified[:12],
                      "removed_sample": removed[:6],
                      "outside_worker_writeset": [p for p in added + modified
                                                  if not p.startswith("workers/codex_exec/")][:12],
                      "repos": {k: v["dirty_count"] for k, v in snap["repos"].items()}}, ensure_ascii=False))
else:
    print(json.dumps({"phase": "before", "files": len(snap["round_tree"]),
                      "repos": {k: v["dirty_count"] for k, v in snap["repos"].items()}}, ensure_ascii=False))
