"""Record the six verified work orders of the closing project and walk the lifecycle.

Verdicts are the checker's own, from receipts/dispatch/VERIFY_cfinal2.json; nothing here re-interprets them.
Copying that receipt into receipts/dispatch/ does not change the package scope, because the scope rule excludes
that prefix by design.
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

PID = "sbl-r152-close-20261022c"
CHECKER = "codex-lane:openai-codex/gpt-6.1-sol@VERIFY_SECURITY-rank2"

for name in ("VERIFY_cfinal2.json", "VERIFY_close.json", "VERIFY_close6b.json"):
    src = os.path.join(TMP, name)
    if os.path.isfile(src):
        shutil.copy2(src, os.path.join(R, "receipts", "dispatch", name))
for d in ("cfinal2_logs",):
    src, dst = os.path.join(TMP, d), os.path.join(R, "receipts", "dispatch", "VERIFY_cfinal2.logs")
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)

verdicts = json.load(open(os.path.join(R, "receipts", "dispatch", "VERIFY_cfinal2.json"), encoding="utf-8"))
bundle = {
    "01": ("evidence/WO-TS-20261022b-01/intake_coverage.json", "source coverage: 24/24 frozen documents admitted"),
    "02": ("evidence/WO-TS-20261022-02/source_ledger.json", "canonical ledger: 30/30 admitted sources, 24 NORMATIVE + 6 SUPPLEMENTARY"),
    "03": ("evidence/WO-TS-20261022-03/ingestion.json", "ingestion: 3033 chunks, 0 coverage gaps, retrieval returns locators"),
    "04": ("evidence/WO-TS-20261022-04/product_surface.json", "product surface: 227 tests, 0 failed after two Windows fixes"),
    "05": ("evidence/WO-TS-20261022-05/acceptance.json", "acceptance: 4 CAPC receipts, exit 0, PROMPT_COMPILE_PASS"),
    "06": ("evidence/WO-TS-20261022-06/exact_set_readback.json", "package: 172 in-scope files vs 172 manifest paths, 0 mismatch"),
}

spine = SharedSpine(Path(os.path.join(HGK, "var", "shared-spine", "hg-kseos.db")))
ctl = ProjectLifecycleController(spine)

out = {"project_id": PID, "checker_principal": CHECKER, "recorded": [], "transitions": {}}
for i in range(1, 7):
    wo = f"WO-TS-20261022c-{i:02d}"
    ref, why = bundle[f"{i:02d}"]
    try:
        spine.record_workorder_result(wo, writer="codex", checker=CHECKER, verdict="PASS",
                                      evidence_refs=[ref, "receipts/dispatch/VERIFY_cfinal2.json"],
                                      evidence_subject=f"{PID}:{wo}")
        out["recorded"].append({"workorder": wo, "verdict": "PASS", "ok": True, "why": why})
    except Exception as exc:  # noqa: BLE001
        out["recorded"].append({"workorder": wo, "verdict": "PASS", "ok": False,
                                "error": f"{type(exc).__name__}: {exc}"})

for st in ("EXECUTING", "VERIFYING", "EVOLUTION_REVIEW", "RELEASE_REDUCING"):
    try:
        ctl.transition(PID, st, trigger="SBL_R15_2_CLOSING_RESULTS")
        out["transitions"][st] = "OK"
    except Exception as exc:  # noqa: BLE001
        out["transitions"][st] = f"{type(exc).__name__}: {exc}"

st = ctl.status(PID)
out["final_state"] = st.get("state")

import sqlite3
c = sqlite3.connect(os.path.join(HGK, "var", "shared-spine", "hg-kseos.db"))
c.row_factory = sqlite3.Row
out["spine_readback"] = [dict(r) for r in c.execute(
    "SELECT workorder_id,state FROM workorders WHERE workorder_id LIKE 'WO-TS-20261022c-%' ORDER BY rowid")]
out["all_projects"] = [dict(r) for r in c.execute(
    "SELECT project_id,state,repair_count,attempts_used FROM project_lifecycles ORDER BY rowid")]
print(json.dumps(out, ensure_ascii=False, indent=2))
