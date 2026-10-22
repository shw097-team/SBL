"""Negative control for the continuation guard: remove a request reference and prove the guard refuses.

A predicate nobody has seen fail is an assumption. This test mutates the queue for the duration of one guard run and
restores it in a finally block, so a crash cannot leave the round in the mutated state.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
Q = os.path.join(R, "QUEUE_R15_2.json")
GUARD = os.path.join(R, "tools", "continuation_guard.py")


def run_guard() -> tuple[int, dict]:
    p = subprocess.run([sys.executable, GUARD], capture_output=True, text=True, timeout=180)
    try:
        return p.returncode, json.loads(p.stdout)
    except Exception:
        return p.returncode, {"raw": (p.stdout or "") + (p.stderr or "")}


def main() -> int:
    backup = Q + ".bak"
    shutil.copy2(Q, backup)
    try:
        q = json.load(open(Q, encoding="utf-8"))
        victim = next(i for i in q["items"] if i["status"] == "PARKED")
        victim.pop("principal_request_ref", None)
        json.dump(q, open(Q, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
        rc, doc = run_guard()
        codes = [b.get("code") for b in doc.get("blockers", [])]
        ok = rc != 0 and "UNISSUED_PRINCIPAL_REQUEST" in codes
        print(json.dumps({"victim": victim["id"], "rc": rc, "codes": codes, "refused": ok}, ensure_ascii=False))
        if not ok:
            print("NEGATIVE_CONTROL_FAILED")
            return 1
        # satisfiability control
        q = json.load(open(backup, encoding="utf-8"))
        q["items"][0]["satisfiable_by"] = "NOBODY"
        json.dump(q, open(Q, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
        rc2, doc2 = run_guard()
        codes2 = [b.get("code") for b in doc2.get("blockers", [])]
        ok2 = rc2 != 0 and "SATISFIABILITY_UNKNOWN" in codes2
        print(json.dumps({"satisfiability_rc": rc2, "codes": codes2, "refused": ok2}, ensure_ascii=False))
        if not ok2:
            print("NEGATIVE_CONTROL_FAILED")
            return 1
        print("NEGATIVE_CONTROL_OK")
        return 0
    finally:
        shutil.move(backup, Q)


if __name__ == "__main__":
    raise SystemExit(main())
