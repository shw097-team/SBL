"""Record the six admitted work orders' results in the native spine, then try to deliver.

Every verdict comes from a real checker dispatch (or from the absence of any implementation, in which
case the verdict is FAIL with the reason recorded). writer='codex' is the value HG-KSEOS itself wrote
when it admitted the work orders; checker is the VERIFY lane principal, which is a distinct value and
therefore satisfies the spine's ERR_WORKORDER_SELF_REVIEW guard.
"""
import json
import os
import sys
from pathlib import Path

HGK = r"C:/Projects/Agent_Workspace/HG-KSEOS"
R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
sys.path.insert(0, os.path.join(HGK, "src"))
from hg_kseos.spine import SharedSpine                      # noqa: E402
from hg_kseos.lifecycle import ProjectLifecycleController   # noqa: E402

PID = "sbl-r152-continuation-20261022"
CHECKER = "codex-lane:openai-codex/gpt-6.1-sol@VERIFY_SECURITY-rank2"
spine = SharedSpine(Path(os.path.join(HGK, "var", "shared-spine", "hg-kseos.db")))
ctl = ProjectLifecycleController(spine)

E = lambda p: f"{p}"  # noqa: E731

results = [
    ("WO-TS-20261022-01", "FAIL",
     ["evidence/WO-TS-20261022-01/source_inventory.json",
      "receipts/dispatch/VERIFY_workorders2.json"],
     "native intake covers 14 of 24 frozen documents; the 10 PIPD_LS documents are absent, so 'admit the provided source corpus' is not established"),
    ("WO-TS-20261022-02", "PASS",
     ["evidence/WO-TS-20261022-02/source_ledger.json",
      "receipts/dispatch/VERIFY_workorders2.json"],
     "24 ledger rows, 24 distinct source ids, 24 distinct sha256; checker re-derived the counts independently"),
    ("WO-TS-20261022-03", "FAIL",
     ["TT_R15_2_REGISTER.json", "DECISION_PACK_R15_2.md"],
     "no RAG/KG ingestion was implemented in this round; the objective is unmet and no evidence bundle exists"),
    ("WO-TS-20261022-04", "FAIL",
     ["TT_R15_2_REGISTER.json", "DECISION_PACK_R15_2.md"],
     "core product surface changes require a product write permit which HG-KSEOS has not issued; nothing was written"),
    ("WO-TS-20261022-05", "PASS",
     ["evidence/WO-TS-20261022-05/acceptance.json",
      "receipts/dispatch/VERIFY_workorders2.json"],
     "all four CAPC receipts carry PROMPT_COMPILE_PASS and exit_code 0; checker parsed the raw receipts"),
    ("WO-TS-20261022-06", "PASS",
     ["evidence/WO-TS-20261022-06/exact_set_readback.json",
      "receipts/dispatch/VERIFY_wo6.json"],
     "independent enumeration: 199 files on disk, 199 manifest paths, zero undeclared, zero missing"),
]

out = {"project_id": PID, "checker_principal": CHECKER, "write_results": [], "transitions": {}}
for wo, verdict, refs, reason in results:
    try:
        res = spine.record_workorder_result(
            wo, writer="codex", checker=CHECKER, verdict=verdict,
            evidence_refs=refs, evidence_subject=f"{PID}:{wo}",
        )
        out["write_results"].append({"workorder": wo, "verdict": verdict, "ok": True,
                                     "reason": reason, "spine_result": str(res)[:300]})
    except Exception as exc:  # noqa: BLE001
        out["write_results"].append({"workorder": wo, "verdict": verdict, "ok": False,
                                     "reason": reason, "error": f"{type(exc).__name__}: {exc}"})

for st in ("EXECUTING", "VERIFYING", "EVOLUTION_REVIEW", "RELEASE_REDUCING", "DELIVERY_READY"):
    try:
        ctl.transition(PID, st, trigger="SBL_R15_2_WORKORDER_RESULTS")
        out["transitions"][st] = "OK"
    except Exception as exc:  # noqa: BLE001
        out["transitions"][st] = f"{type(exc).__name__}: {exc}"
        if "ERR_PENDING_WORK_CANNOT_DELIVER" in str(exc) or "DELIVER" in str(exc):
            break

st = ctl.status(PID)
out["final_state"] = st.get("state")
out["pending_workorders"] = st.get("pending_workorders") if isinstance(st, dict) else None

import sqlite3
c = sqlite3.connect(os.path.join(HGK, "var", "shared-spine", "hg-kseos.db"))
c.row_factory = sqlite3.Row
rows = c.execute("SELECT workorder_id,state,substr(result_json,1,160) AS result FROM workorders "
                 "WHERE workorder_id LIKE 'WO-TS-20261022-%' ORDER BY rowid").fetchall()
out["spine_readback"] = [dict(r) for r in rows]
print(json.dumps(out, ensure_ascii=False, indent=2))
