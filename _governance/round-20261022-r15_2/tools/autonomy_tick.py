"""One autonomy tick: heartbeat, advance the queue, apply the close predicate, report only if something moved.

Designed to run from the scheduler with no agent in the loop. Empty stdout means "nothing to say" — the watchdog
pattern, so the chat is not spammed every interval.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
PY = sys.executable
STATE = os.path.join(R, "receipts", "tick_state.json")


def run(script: str, *args: str, timeout: int = 900) -> tuple[int, str]:
    p = subprocess.run([PY, os.path.join(R, "tools", script), *args], capture_output=True, text=True,
                       timeout=timeout, cwd=r"C:/Projects/Agent_Workspace/_r152_ev")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def counts() -> dict:
    q = json.load(open(os.path.join(R, "QUEUE_R15_2.json"), encoding="utf-8"))
    out = {s: sum(1 for i in q["items"] if i["status"] == s) for s in ("READY", "RUNNING", "DONE", "PARKED")}
    out["runs"] = len(q.get("runs") or [])
    return out


def main() -> int:
    before = counts()
    run("heartbeat.py", "tick")
    rc_adv, out_adv = run("advance_queue.py", "--max-steps", "3")
    after = counts()
    rc_guard, out_guard = run("continuation_guard.py")

    verdict = "TERMINAL" if rc_guard == 0 else "NOT_TERMINAL"
    blockers = []
    try:
        blockers = json.loads(out_guard).get("blockers", [])
    except Exception:
        pass
    moved = after != before or after["runs"] != before["runs"]

    prev = {}
    if os.path.exists(STATE):
        try:
            prev = json.load(open(STATE, encoding="utf-8"))
        except Exception:
            prev = {}
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump({"counts": after, "verdict": verdict, "blockers": blockers},
              open(STATE, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)

    changed = moved or prev.get("verdict") != verdict or prev.get("blockers") != blockers
    if changed:
        print(f"SBL R15.2 tick: {after} verdict={verdict} "
              f"blockers={[b.get('code') for b in blockers]} advance_rc={rc_adv}")
        for b in blockers:
            print(f"  {b.get('code')}: {b.get('ids') or b.get('id') or b.get('age_minutes')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
