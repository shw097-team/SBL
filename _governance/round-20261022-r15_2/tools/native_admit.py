"""Native HG-KSEOS admission for the SBL R15.2 subject.

Creates a project, walks the lifecycle to DESIGN_READY, then calls the controller's own
`admit_workorders()` so HG-KSEOS (not this script) derives TaskSpecs and issues WorkOrders.
Every id printed here is produced by the native control plane.
"""
import json
import os
import sys
from pathlib import Path

HGK = r"C:/Projects/Agent_Workspace/HG-KSEOS"
sys.path.insert(0, os.path.join(HGK, "src"))

from hg_kseos.spine import SharedSpine                     # noqa: E402
from hg_kseos.lifecycle import ProjectLifecycleController, ProjectRequest  # noqa: E402

DB = os.path.join(HGK, "var", "shared-spine", "hg-kseos.db")
PID = "sbl-r152-continuation-20261022"

spine = SharedSpine(Path(DB))
ctl = ProjectLifecycleController(spine)

req = ProjectRequest(
    goal=("SBL 產品工程施工與驗收交付：依 SBL_PIPD-LS-PKG 上位控制包完成實作、測試、驗收與交付，"
          "並以知識文檔與研究作為來源准入"),
    source_paths=[r"C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG"],
    constraints=["candidate-only", "no self-acceptance", "fail-closed"],
    non_goals=["no release", "no host install", "no SWOF write"],
    target_root=r"C:/Projects/Agent_Workspace/_r152_ev",
)

out = {}
try:
    out["start"] = ctl.start(req, project_id=PID)
except Exception as exc:  # noqa: BLE001
    out["start_error"] = f"{type(exc).__name__}: {exc}"

def adv(state):
    try:
        ctl.transition(PID, state, trigger="SBL_R15_2_CONTINUATION")
        return "OK"
    except Exception as exc:  # noqa: BLE001
        return f"{type(exc).__name__}: {exc}"

# intake binds the source envelope (source_count), then walk forward to DESIGN_READY
try:
    out["intake"] = ctl.intake(PID, req) if hasattr(ctl, "intake") else "NO_INTAKE_METHOD"
except Exception as exc:  # noqa: BLE001
    out["intake_error"] = f"{type(exc).__name__}: {exc}"

for st in ("SOURCE_DISCOVERY", "SOURCE_ADMISSION", "INTENT_BOUND",
           "REQUIREMENTS_READY", "DESIGN_READY", "PLAN_READY"):
    out.setdefault("advance", {})[st] = adv(st)

out["state_before_admit"] = ctl.status(PID).get("state")

try:
    out["admission"] = ctl.admit_workorders(PID)
except Exception as exc:  # noqa: BLE001
    out["admission_error"] = f"{type(exc).__name__}: {exc}"

out["state_after_admit"] = ctl.status(PID).get("state")

# read back what the spine actually holds for this project
import sqlite3
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
req_id = f"REQ-{PID}-PLAN"
rows = c.execute(
    "SELECT w.workorder_id, w.taskspec_id, w.state, w.writer, t.objective, t.owner "
    "FROM workorders w JOIN taskspecs t ON t.taskspec_id = w.taskspec_id "
    "WHERE t.requirement_id = ? ORDER BY w.rowid", (req_id,)).fetchall()
out["workorders_readback"] = [dict(r) for r in rows]
out["requirement_id"] = req_id

print(json.dumps(out, ensure_ascii=False, indent=2))
