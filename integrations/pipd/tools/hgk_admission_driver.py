#!/usr/bin/env python3
"""Drive the HG-KSEOS normal lifecycle admission chain for PIPD-LS-SP.

Uses ONLY the typed Lifecycle controller / SharedSpine API (no raw SQL writes).
Records every canonical event id it causes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hgk-root", required=True, type=Path)
    ap.add_argument("--project-id", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--step", required=True,
                    choices=["start", "intake", "plan", "admit", "status", "checkpoint"])
    args = ap.parse_args()

    sys.path.insert(0, str(args.hgk_root / "src"))
    from hg_kseos.spine import SharedSpine
    from hg_kseos.lifecycle import ProjectLifecycleController, ProjectRequest

    spine = SharedSpine(args.hgk_root / "var/shared-spine/hg-kseos.db",
                        args.hgk_root / "src/hg_kseos/schema.sql")
    lc = ProjectLifecycleController(spine)
    args.out.mkdir(parents=True, exist_ok=True)
    PID = args.project_id
    KB = "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/PIPD"
    REQ = ProjectRequest(
        goal=("以 HG-KSEOS 治理控制平面實作 PIPD-LS-SP 知識驅動的 Pre-Implementation & Pre-Dev "
              "Lifecycle Skills Plugin：完成規格包編譯、系統建置、工具與 CLI 實作、測試驗收、"
              "證據封存與公開交付。"),
        source_paths=[f"{KB}/PIPD_LS", f"{KB}/PIPD-LS-SP_PIPD-PKG", f"{KB}/SKILLS_PLUGIN",
                      f"{KB}/PIPD-LS-SP_藍圖",
                      "C:/Projects/Agent_Workspace/知識庫/工程基座/GRP_PORTABLE_DISTRIBUTION_SET_13",
                      "C:/Projects/Agent_Workspace/HG-KSEOS/AGENTS.md"],
        constraints=["HG-KSEOS is the sole normative control plane",
                     "product writes are confined to the PIPD target root",
                     "no secret values in stdout, argv or evidence"],
        non_goals=["no second control plane / scheduler / reducer",
                   "no production deployment or Stage-3 escalation",
                   "no self-issued INDEPENDENT_PASS"],
        target_root="C:/Projects/Agent_Workspace/PIPD",
    )
    result: dict = {"step": args.step, "project_id": PID}
    if args.step == "start":
        result["start"] = lc.start(REQ, project_id=PID)
    elif args.step == "intake":
        result["intake"] = lc.intake(PID, REQ)
    elif args.step == "plan":
        result["plan"] = lc.plan(PID)
    elif args.step == "admit":
        result["admit"] = lc.admit_workorders(PID)
    elif args.step == "status":
        result["status"] = lc.status(PID)
    elif args.step == "checkpoint":
        result["checkpoint"] = lc.checkpoint(PID)

    (args.out / f"admission_{args.step}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1, default=str), encoding="utf-8", newline="")
    summary = json.dumps(result, ensure_ascii=False, default=str)
    print(summary[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
