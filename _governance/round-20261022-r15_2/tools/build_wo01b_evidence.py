"""Evidence for WO-TS-20261022b-01: prove the native intake now covers every frozen document."""
import hashlib
import json
import os
import subprocess

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
EV = os.path.join(R, "evidence", "WO-TS-20261022b-01")
os.makedirs(EV, exist_ok=True)

freeze = json.load(open(os.path.join(R, "SOURCE_FREEZE.json"), encoding="utf-8"))
admit = json.load(open(os.path.join(R, "receipts", "admission", "native_admit_final2.json"), encoding="utf-8"))

frozen = {d["name"]: (d.get("observed") or {}).get("sha256") for d in freeze["documents"]}
frozen_hashes = {h for h in frozen.values() if h}
intake = admit["intake"]["inventory"]
intake_hashes = {s["sha256"] for s in intake}
intake_names = {os.path.basename(s["path"]) for s in intake}

covered = sorted(h for h in frozen_hashes if h in intake_hashes)
uncovered = sorted(h for h in frozen_hashes if h not in intake_hashes)

obj = {
    "workorder": "WO-TS-20261022b-01",
    "objective": "Inventory, hash and admit the provided source corpus",
    "native_intake_source_count": admit["intake"]["source_count"],
    "frozen_documents": len(frozen),
    "frozen_distinct_hashes": len(frozen_hashes),
    "intake_distinct_hashes": len(intake_hashes),
    "frozen_documents_covered_by_native_intake": len(covered),
    "frozen_documents_not_covered": uncovered,
    "coverage_complete": not uncovered,
    "intake_roots": {k: v for k, v in admit.get("roots", {}).items()},
    "method": ("cross-match the sha256 of every SOURCE_FREEZE document against the sha256 set the native "
               "intake recorded; a document counts as admitted only when its hash is present"),
    "note": ("the earlier project sbl-r152-continuation-20261022 admitted only the 14 SBL documents because its "
             "intake predated the PIPD root binding; this project bound both roots before admission, which is "
             "the only point at which intake is accepted (ERR_INTAKE_STATE otherwise)"),
    "generated_utc": subprocess.run(["date", "-u", "+%FT%TZ"], capture_output=True, text=True).stdout.strip(),
}
p = os.path.join(EV, "intake_coverage.json")
txt = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
open(p, "w", encoding="utf-8", newline="\n").write(txt)
print(json.dumps({k: obj[k] for k in ("frozen_documents", "frozen_distinct_hashes", "intake_distinct_hashes",
                                      "frozen_documents_covered_by_native_intake", "coverage_complete",
                                      "frozen_documents_not_covered")}, ensure_ascii=False, indent=2))
