"""Project the round queue onto a real Hermes kanban board.

Why: this round drove its own JSON queue while KANBAN was available, which is a governance deviation - the board is the
authority for task state and it survives sessions. Each queue item becomes one card, keyed by its id so a re-run is
idempotent. Mapping is one-way and lossless in meaning: DONE -> completed, HOLD/PARKED -> blocked, the rest -> todo.

Read-only against the queue; writes only to the kanban board. Prints a JSON summary.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROUND = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
QUEUE = os.path.join(ROUND, "QUEUE_R15_2.json")
HH = r"C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/hermes-agent"
BOARD = "r15-2-evidence-20261022"
RECEIPT = os.path.join(ROUND, "KANBAN_PROJECTION_R153.json")


def kc(*args: str) -> tuple[int, str]:
    env = dict(os.environ, PYTHONPATH=HH, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-B", "-m", "hermes_cli.main", "kanban", "--board", BOARD, *args],
                       cwd=HH, capture_output=True, text=True, timeout=120, env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    apply = "--apply" in sys.argv
    q = json.load(open(QUEUE, encoding="utf-8"))
    plan = []
    for i in q["items"]:
        st = i["status"]
        target = {"DONE": "COMPLETED", "HOLD": "BLOCKED", "PARKED": "BLOCKED"}.get(st, "TODO")
        plan.append({"id": i["id"], "status": st, "kanban": target,
                     "title": ("%s | %s" % (i["id"], (i.get("title") or i.get("next_action") or st)))[:120],
                     "den_id": i.get("den_id"), "owner_class": i.get("owner_class")})
    summary = {"board": BOARD, "apply": apply, "cards": len(plan),
               "by_target": {t: sum(1 for p in plan if p["kanban"] == t) for t in ("COMPLETED", "BLOCKED", "TODO")}}
    if apply:
        rc, out = kc("boards", "create", BOARD, "--name", "R15.2 evidence + repair")
        summary["board_create"] = {"rc": rc, "out": out.strip().splitlines()[-1:]}
        created, failed = 0, []
        for p in plan:
            args = ["create", p["title"], "--body", "queue %s | den %s | owner %s | mapped %s -> %s"
                    % (p["status"], p["den_id"], p["owner_class"], p["status"], p["kanban"]),
                    "--idempotency-key", "r152:" + p["id"]]
            if p["kanban"] == "BLOCKED":
                args += ["--initial-status", "blocked"]
            rc, out = kc(*args)
            if rc != 0:
                failed.append({"id": p["id"], "out": out.strip().splitlines()[-1:]})
                continue
            created += 1
            if p["kanban"] == "COMPLETED":
                tid = ""
                for line in out.splitlines():
                    if line.strip().startswith("t_"):
                        tid = line.strip().split()[0]
                if tid:
                    rcc, outc = kc("complete", tid)
                    if rcc != 0:
                        failed.append({"id": p["id"], "complete": outc.strip().splitlines()[-1:]})
        summary["created"] = created
        summary["failed"] = failed
        rc, out = kc("stats")
        summary["stats"] = out.strip().splitlines()[-8:]
    json.dump(summary, open(RECEIPT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != "cards"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
