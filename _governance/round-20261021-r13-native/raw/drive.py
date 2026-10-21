"""R13 native-chain driver: project -> taskspec -> workorder under the real HGK spine.

Stages (run one at a time):
  red    admission from a NON-repo CWD -> expect the CWD bug to fail the admission
  wo     admission from the HGK root  -> create the workorder, embed the role binding, take a lease
  green  admission from a NON-repo CWD again, after the patch -> expect success + HGK HEAD
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

HGK = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS")
sys.path.insert(0, str(HGK / "src"))

from hg_kseos.lifecycle import ProjectLifecycleController, ProjectRequest  # noqa: E402
from hg_kseos.spine import SharedSpine  # noqa: E402

SPINE = HGK / "var" / "shared-spine" / "hg-kseos.db"
NONREPO = Path(r"C:/Projects/Agent_Workspace/_r13_cwd")   # not a git repo, on purpose
OUT = HGK / "var" / "R13-NATIVE-20261021"
GOAL = (
    "Repair the HGK lifecycle repo-head resolution (R9-06): base_head must come from the project "
    "target_root, not the process CWD, and a failed git call must raise instead of returning empty."
)
SOURCES = [
    r"C:/Projects/Agent_Workspace/_r12_far/subagent/R9-06_repo_head_report.md",
    r"C:/Projects/Agent_Workspace/_r12_docs/_governance/round-20261021-r12-far/FAR_DEVIATION_STUDY.md",
]


def h(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def make_request() -> ProjectRequest:
    fields = getattr(ProjectRequest, "__dataclass_fields__", {})
    kw = {"goal": GOAL, "target_root": str(HGK), "constraints": ["bounded write: src/hg_kseos/lifecycle.py"],
          "non_goals": ["no change to lane routing", "no change to the readiness contract"]}
    for name, alt in (("source_paths", "sources"), ("sources", "source_paths")):
        if name in fields:
            kw[name] = SOURCES
            break
    return ProjectRequest(**{k: v for k, v in kw.items() if k in fields})


def to_design_ready(c, pid):
    order = ["SOURCE_DISCOVERY", "SOURCE_ADMISSION", "INTENT_BOUND", "REQUIREMENTS_READY", "DESIGN_READY"]
    cur = c.status(pid)["state"]
    start = order.index(cur) + 1 if cur in order else 0
    for st in order[start:]:
        c.transition(pid, st, trigger=f"R13_{st}")
    return c.status(pid)["state"]


def run(stage: str) -> dict:
    spine = SharedSpine(SPINE)
    c = ProjectLifecycleController(spine)
    req = make_request()
    rec: dict = {"stage": stage, "cwd": os.getcwd(), "hgk_head": None}

    if stage in ("red", "green"):
        pid = f"HGKR13-{stage.upper()}"
        os.chdir(NONREPO)
        try:
            c.start(req, project_id=pid)
        except Exception as exc:  # already started on a retry
            rec["start"] = f"{type(exc).__name__}: {exc}"
        c.intake(pid, req)
        rec["state_after_intake"] = to_design_ready(c, pid)
        rec["plan"] = len(c.plan(pid)["plan"])
        try:
            rec["admitted"] = c.admit_workorders(pid)
        except Exception as exc:
            rec["admit_error"] = f"{type(exc).__name__}: {exc}"
        rec["state_final"] = c.status(pid)["state"]
    else:  # wo
        pid = "HGKR13-WO"
        os.chdir(HGK)          # admission resolves HEAD from here (the pre-patch behaviour)
        try:
            c.start(req, project_id=pid)
        except Exception as exc:
            rec["start"] = f"{type(exc).__name__}: {exc}"
        c.intake(pid, req)
        rec["state_after_intake"] = to_design_ready(c, pid)
        rec["plan"] = len(c.plan(pid)["plan"])
        rec["admitted"] = c.admit_workorders(pid)
        # ---- embed the execution binding into the admitted TaskSpec, then take a lease ----
        wo = rec["admitted"]["workorders"][0]
        with spine.connect() as conn:
            row = conn.execute(
                "SELECT w.base_head,t.taskspec_id,t.permissions_json FROM workorders w "
                "JOIN taskspecs t ON t.taskspec_id=w.taskspec_id WHERE w.workorder_id=?", (wo,)).fetchone()
        base_head, ts_id, perms = row["base_head"], row["taskspec_id"], json.loads(row["permissions_json"])
        mandate = ("OWNER MANDATE R13: PLAN=openai-codex/gpt-6.1-sol; EXECUTE=opencode-go/minimax-m3.1-flash-free; "
                   "VERIFY_SECURITY=openai-codex/gpt-6.1-sol")
        binding = {
            "schema": "HGK-ROLE-BINDING/1",
            "round": "round-20261021-r13",
            "session": "r13-native-20261021",
            "workorder": wo,
            "base_head": base_head,
            "subject": "src/hg_kseos/lifecycle.py",
            "scope": ["src/hg_kseos/lifecycle.py", "tests/test_r13_repo_head_cwd.py"],
            "expiry": (datetime.now(UTC) + timedelta(hours=6)).isoformat(),
            "mandate_digest": "sha256:" + hashlib.sha256(mandate.encode()).hexdigest(),
            "roles": {
                "EXECUTE": {"provider": "opencode-go", "model": "minimax-m3.1-flash-free",
                            "surface": "codex-cli", "rank": 2, "reasoning_effort": "medium"},
                "VERIFY_SECURITY": {"provider": "openai-codex", "model": "gpt-6.1-sol",
                                    "surface": "codex-cli", "rank": 1, "reasoning_effort": "medium"},
            },
        }
        perms["role_binding"] = binding
        with spine.transaction() as conn:
            conn.execute("UPDATE taskspecs SET permissions_json=?,updated_at=datetime('now') WHERE taskspec_id=?",
                         (json.dumps(perms, ensure_ascii=False), ts_id))
        lease_res = "file:src/hg_kseos/lifecycle.py"
        spine.acquire_lease(lease_res, "hermes-r13-writer", "TK-R13-WRITE", ttl_seconds=7200)
        rec["binding"] = binding
        rec["lease"] = {"resource": lease_res, "holder": "hermes-r13-writer", "ttl": 7200}
        (OUT / "binding.json").write_text(json.dumps(binding, indent=2), encoding="utf-8")

    with spine.connect() as conn:
        rec["workorders"] = [
            dict(r) for r in conn.execute(
                "SELECT workorder_id,state,base_head,worktree FROM workorders ORDER BY created_at DESC LIMIT 3")
        ]
        rec["project"] = dict(conn.execute(
            "SELECT project_id,state,intent_json FROM project_lifecycles WHERE project_id=?", (pid,)).fetchone())
    rec["project"]["intent_json"] = json.loads(rec["project"]["intent_json"])
    return rec


if __name__ == "__main__":
    stage = sys.argv[1]
    res = run(stage)
    res["head_now"] = __import__("subprocess").run(
        ["git", "-C", str(HGK), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"stage_{stage}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False)[:2200])
