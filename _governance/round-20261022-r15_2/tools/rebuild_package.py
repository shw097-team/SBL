"""Rebuild only the package manifest and its exact-set readback, under the converged scope rule.

Scope: the round tree minus `receipts/dispatch/` (harness output), minus ROUND_MANIFEST.json, minus
evidence/WO_EVIDENCE_INDEX.json, minus the readback file itself. Run this after any evidence edit so the package
describes the tree that actually exists.
"""
import hashlib
import json
import os
import subprocess

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
EXCLUDE = {"ROUND_MANIFEST.json", "evidence/WO_EVIDENCE_INDEX.json",
           "evidence/WO-TS-20261022-06/exact_set_readback.json"}
EXCLUDE_PREFIX = ("receipts/dispatch/",)


def utc():
    return subprocess.run(["date", "-u", "+%FT%TZ"], capture_output=True, text=True).stdout.strip()


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def walk():
    out = []
    for root, dirs, files in os.walk(R):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in sorted(files):
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, R).replace("\\", "/")
            if rel in EXCLUDE or rel.startswith(EXCLUDE_PREFIX):
                continue
            out.append({"path": rel, "bytes": os.path.getsize(fp), "sha256": sha(fp)})
    out.sort(key=lambda r: r["path"])
    return out


rows = walk()
mp = os.path.join(R, "ROUND_MANIFEST.json")
mf = json.load(open(mp, encoding="utf-8"))
mf["file_count"] = len(rows)
mf["files"] = rows
mf["scope_rule"] = ("round tree minus receipts/dispatch/ minus ROUND_MANIFEST.json minus "
                    "evidence/WO_EVIDENCE_INDEX.json minus the readback itself")
mf["generated_utc"] = utc()
open(mp, "w", encoding="utf-8", newline="\n").write(json.dumps(mf, ensure_ascii=False, indent=2) + "\n")

declared = {r["path"] for r in rows}
disk = {r["path"] for r in walk()}
readback = {
    "workorder": "WO-TS-20261022-06",
    "objective": "Produce package, exact-set readback and delivery readiness evidence",
    "scope_rule": mf["scope_rule"],
    "files_on_disk": len(disk),
    "files_declared_in_manifest": len(declared),
    "missing_from_disk": sorted(declared - disk),
    "undeclared_on_disk": sorted(disk - declared),
    "exact_set_equal": declared == disk,
    "hash_mismatches": [r["path"] for r in rows if sha(os.path.join(R, r["path"])) != r["sha256"]],
    "delivery_readiness": "READY_FOR_EXTERNAL_REVIEW" if declared == disk else "NOT_READY",
    "generated_utc": utc(),
}
rp = os.path.join(R, "evidence", "WO-TS-20261022-06", "exact_set_readback.json")
open(rp, "w", encoding="utf-8", newline="\n").write(json.dumps(readback, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: readback[k] for k in ("files_on_disk", "files_declared_in_manifest",
                                           "exact_set_equal", "delivery_readiness")}, ensure_ascii=False))
