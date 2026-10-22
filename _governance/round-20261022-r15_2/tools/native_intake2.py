"""Re-run the native source intake with BOTH corpora so WO-01's objective is actually met.

Adds the 10 PIPD_LS_DOC sources alongside the 14 SBL_PIPD-LS-PKG documents.
"""
import json
import os
import sys
from pathlib import Path

HGK = r"C:/Projects/Agent_Workspace/HG-KSEOS"
sys.path.insert(0, os.path.join(HGK, "src"))
from hg_kseos.spine import SharedSpine                      # noqa: E402
from hg_kseos.lifecycle import ProjectLifecycleController, ProjectRequest  # noqa: E402

PID = "sbl-r152-continuation-20261022"
DOCS = r"C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL"
SBL = os.path.join(DOCS, "SBL_PIPD-LS-PKG")
PIPD = os.path.join(DOCS, "PIPD_LS_PKG")

spine = SharedSpine(Path(os.path.join(HGK, "var", "shared-spine", "hg-kseos.db")))
ctl = ProjectLifecycleController(spine)

req = ProjectRequest(
    goal=("SBL 產品工程施工與驗收交付：依 SBL_PIPD-LS-PKG 上位控制包完成實作、測試、驗收與交付，"
          "並以知識文檔與研究作為來源准入"),
    source_paths=[SBL, PIPD],
    constraints=["candidate-only", "no self-acceptance", "fail-closed"],
    non_goals=["no release", "no host install", "no SWOF write"],
    target_root=r"C:/Projects/Agent_Workspace/_r152_ev",
)

out = {}
for label, path in (("sbl_pkg", SBL), ("pipd_pkg", PIPD)):
    out[label] = {"path": path, "exists": os.path.isdir(path),
                  "md_files": sorted(f for f in os.listdir(path) if f.endswith(".md")) if os.path.isdir(path) else []}

try:
    out["intake"] = ctl.intake(PID, req)
    out["intake_ok"] = True
except Exception as exc:  # noqa: BLE001
    out["intake_error"] = f"{type(exc).__name__}: {exc}"
    out["intake_ok"] = False

st = ctl.status(PID)
out["state"] = st.get("state")
out["source_count_after"] = st.get("source_count")
print(json.dumps(out, ensure_ascii=False, indent=2))
