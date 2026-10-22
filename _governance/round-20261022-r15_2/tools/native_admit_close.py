"""Final native admission: both corpora in one intake, then HG-KSEOS admits the work orders.

Fixes the WO-01 coverage gap (the earlier project's intake saw only the 14 SBL documents) by binding
both source roots before admission, which is the only point where intake is accepted.
"""
import json
import os
import sys
from pathlib import Path

HGK = r"C:/Projects/Agent_Workspace/HG-KSEOS"
sys.path.insert(0, os.path.join(HGK, "src"))
from hg_kseos.spine import SharedSpine                          # noqa: E402
from hg_kseos.lifecycle import ProjectLifecycleController, ProjectRequest  # noqa: E402

PID = "sbl-r152-close-20261022c"
KNOW = r"C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric"
SBL_PKG = os.path.join(KNOW, "SBL", "SBL_PIPD-LS-PKG")
PIPD_DIR = os.path.join(KNOW, "PIPD", "PIPD_LS")

spine = SharedSpine(Path(os.path.join(HGK, "var", "shared-spine", "hg-kseos.db")))
ctl = ProjectLifecycleController(spine)

req = ProjectRequest(
    goal=("SBL 產品工程施工與驗收交付：依 SBL_PIPD-LS-PKG 上位控制包完成實作、測試、驗收與交付，"
          "並以知識文檔與研究作為來源准入"),
    source_paths=[SBL_PKG, PIPD_DIR],
    constraints=["candidate-only", "no self-acceptance", "fail-closed"],
    non_goals=["no release", "no host install", "no SWOF write"],
    target_root=r"C:/Projects/Agent_Workspace/_r152_ev",
)

out = {"roots": {
    "sbl_pkg": {"path": SBL_PKG, "exists": os.path.isdir(SBL_PKG),
                "md": len([f for f in os.listdir(SBL_PKG) if f.endswith(".md")]) if os.path.isdir(SBL_PKG) else 0},
    "pipd_dir": {"path": PIPD_DIR, "exists": os.path.isdir(PIPD_DIR),
                 "md": len([f for f in os.listdir(PIPD_DIR) if f.endswith(".md")]) if os.path.isdir(PIPD_DIR) else 0},
}}

try:
    out["start"] = ctl.start(req, project_id=PID)
except Exception as exc:  # noqa: BLE001
    out["start_error"] = f"{type(exc).__name__}: {exc}"

try:
    out["intake"] = ctl.intake(PID, req)
    out["source_count"] = out["intake"].get("source_count")
except Exception as exc:  # noqa: BLE001
    out["intake_error"] = f"{type(exc).__name__}: {exc}"

for st in ("SOURCE_DISCOVERY", "SOURCE_ADMISSION", "INTENT_BOUND",
           "REQUIREMENTS_READY", "DESIGN_READY", "PLAN_READY"):
    try:
        ctl.transition(PID, st, trigger="SBL_R15_2_FINAL")
        out.setdefault("advance", {})[st] = "OK"
    except Exception as exc:  # noqa: BLE001
        out.setdefault("advance", {})[st] = f"{type(exc).__name__}: {exc}"

try:
    out["admission"] = ctl.admit_workorders(PID)
except Exception as exc:  # noqa: BLE001
    out["admission_error"] = f"{type(exc).__name__}: {exc}"

st = ctl.status(PID)
out["state"] = st.get("state")
out["source_count_status"] = st.get("source_count")
print(json.dumps(out, ensure_ascii=False, indent=2))
