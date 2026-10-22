"""Record the six final work-order results and walk the lifecycle to DELIVERY_READY.

Verdicts come from the checker dispatches:
  * VERIFY_final.json      -> 01 PASS, 02 PASS, 03 FAIL, 04 FAIL, 05 PASS
  * VERIFY_wo6b.json       -> 06 PASS (run with outputs outside the tree so the package stayed stable)
"""
import json
import os
import shutil
import sys
from pathlib import Path

HGK = r"C:/Projects/Agent_Workspace/HG-KSEOS"
R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
TMP = r"C:/Users/user/AppData/Local/Temp/r152"
sys.path.insert(0, os.path.join(HGK, "src"))
from hg_kseos.spine import SharedSpine                      # noqa: E402
from hg_kseos.lifecycle import ProjectLifecycleController   # noqa: E402

PID = "sbl-r152-final2-20261022b"
CHECKER = "codex-lane:openai-codex/gpt-6.1-sol@VERIFY_SECURITY-rank2"

# bring the out-of-tree WO-06 receipt into the evidence branch before recording it
src = os.path.join(TMP, "VERIFY_wo6b.json")
dst = os.path.join(R, "receipts", "dispatch", "VERIFY_wo6b.json")
if os.path.isfile(src):
    shutil.copy2(src, dst)
    logs_src = os.path.join(TMP, "wo6b_logs")
    if os.path.isdir(logs_src):
        shutil.copytree(logs_src, dst + ".logs", dirs_exist_ok=True)

spine = SharedSpine(Path(os.path.join(HGK, "var", "shared-spine", "hg-kseos.db")))
ctl = ProjectLifecycleController(spine)

results = [
    ("WO-TS-20261022b-01", "PASS",
     ["evidence/WO-TS-20261022b-01/intake_coverage.json", "receipts/dispatch/VERIFY_final.json"],
     "checker rehashed all 24 frozen sources and confirmed the native intake covers 24/24 with zero uncovered"),
    ("WO-TS-20261022b-02", "PASS",
     ["evidence/WO-TS-20261022-02/source_ledger.json", "receipts/dispatch/VERIFY_final.json"],
     "24 ledger entries, 24 distinct hashes, all NORMATIVE; checker re-derived the counts"),
    ("WO-TS-20261022b-03", "FAIL",
     ["TT_R15_2_REGISTER.json"],
     "no RAG/KG ingestion exists; the checker found no bundle and marked the objective unevidenced"),
    ("WO-TS-20261022b-04", "FAIL",
     ["TT_R15_2_REGISTER.json", "DECISION_PACK_R15_2.md"],
     "the core product surface needs a product write permit HG-KSEOS has not issued; nothing was written"),
    ("WO-TS-20261022b-05", "PASS",
     ["evidence/WO-TS-20261022-05/acceptance.json", "receipts/dispatch/VERIFY_final.json"],
     "four CAPC receipts with PROMPT_COMPILE_PASS and exit_code 0; checker verified the receipt hashes"),
    ("WO-TS-20261022b-06", "PASS",
     ["evidence/WO-TS-20261022-06/exact_set_readback.json", "receipts/dispatch/VERIFY_wo6b.json"],
     "checker enumerated 214 files against 214 manifest paths, zero undeclared, zero missing"),
]

out = {"project_id": PID, "checker_principal": CHECKER, "results": [], "transitions": {}}
for wo, verdict, refs, reason in results:
    try:
        res = spine.record_workorder_result(wo, writer="codex", checker=CHECKER,
                                            verdict=verdict, evidence_refs=refs,
                                            evidence_subject=f"{PID}:{wo}")
        out["results"].append({"workorder": wo, "verdict": verdict, "ok": True, "reason": reason,
                               "spine": str(res)[:200]})
    except Exception as exc:  # noqa: BLE001
        out["results"].append({"workorder": wo, "verdict": verdict, "ok": False, "reason": reason,
                               "error": f"{type(exc).__name__}: {exc}"})

for st in ("EXECUTING", "VERIFYING", "EVOLUTION_REVIEW", "RELEASE_REDUCING", "DELIVERY_READY"):
    try:
        ctl.transition(PID, st, trigger="SBL_R15_2_FINAL_RESULTS")
        out["transitions"][st] = "OK"
    except Exception as exc:  # noqa: BLE001
        out["transitions"][st] = f"{type(exc).__name__}: {exc}"

st = ctl.status(PID)
out["final_state"] = st.get("state")

import sqlite3
c = sqlite3.connect(os.path.join(HGK, "var", "shared-spine", "hg-kseos.db"))
c.row_factory = sqlite3.Row
out["spine_readback"] = [dict(r) for r in c.execute(
    "SELECT workorder_id,state FROM workorders WHERE workorder_id LIKE 'WO-TS-20261022b-%' ORDER BY rowid")]
out["project_states"] = [dict(r) for r in c.execute(
    "SELECT project_id,state FROM project_lifecycles WHERE project_id LIKE 'sbl-r15%' OR project_id LIKE 'sbl-r152%' ORDER BY rowid")]
print(json.dumps(out, ensure_ascii=False, indent=2))
