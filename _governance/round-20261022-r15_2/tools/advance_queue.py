"""Drive the R15.2 queue: run every ready AGENT item, park what fails, keep going.

Stop policy (the only legal stops): destructive action, missing credential, mandated lane unavailable, owner-only
decision. Anything else is parked with a typed reason and the driver continues. The driver exits when no AGENT item is
READY — never because a single step failed.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
Q = os.path.join(R, "QUEUE_R15_2.json")
# A step that fails is worth exactly one automatic re-arm; beyond that the failure is a diagnosis, not a retry.
ATTEMPT_CAP = 3
REARMABLE = ("STEP_FAILED",)
LOG = os.path.join(R, "receipts", "queue_runner.log")
WORKTREE = r"C:/Projects/Agent_Workspace/_r152_ev"


def load() -> dict:
    return json.load(open(Q, encoding="utf-8"))


def save(q: dict) -> None:
    json.dump(q, open(Q, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    open(Q, "a", encoding="utf-8", newline="\n").write("\n")


def log(line: str) -> None:
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(line.rstrip("\n") + "\n")
    print(line)


def run(item: dict) -> tuple[bool, str]:
    cmd = item["resume_cmd"]
    timeout = int(item.get("timeout_s", 240))
    t0 = time.time()
    try:
        p = subprocess.run(cmd, shell=True, cwd=item.get("cwd") or WORKTREE, capture_output=True, text=True,
                        timeout=timeout)
        out, rc = (p.stdout or "") + (p.stderr or ""), p.returncode
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {timeout}s"
    secs = round(time.time() - t0, 2)
    expect = item.get("expect")
    ok = rc == 0 and (re.search(expect, out) is not None if expect else True)
    if rc == 0 and not ok:
        out = "EXPECT_MISS (rc=0)\n" + out
    tail = out.strip().splitlines()[-6:]
    return ok, f"rc={rc} secs={secs} expect={'hit' if ok else 'miss'}\n    " + "\n    ".join(tail)


def main() -> int:
    max_steps = int(sys.argv[sys.argv.index("--max-steps") + 1]) if "--max-steps" in sys.argv else 6
    q = load()
    steps = 0
    log(f"=== advance_queue start {time.strftime('%FT%T')} max_steps={max_steps} ===")
    while steps < max_steps:
        # A READY-only predicate starved this queue: 3 PARTIAL and 1 DONE_RECEIPT_RED item were invisible to the
        # driver forever, and a failed step became PARKED with a prose retry hint nobody read. Selection now also
        # re-arms unfinished agent work, bounded by an attempt cap so a broken item cannot spin.
        ready = [
            i for i in q["items"]
            if i["owner_class"] == "AGENT"
            and i.get("satisfiable_by", "AGENT") == "AGENT"
            and int(i.get("attempts", 0)) < ATTEMPT_CAP
            and (i["status"] == "READY"
                 or (i.get("rearm_ok") is True
                     and i["status"] in ("PARTIAL", "PARKED", "DONE_RECEIPT_RED")))
        ]
        if not ready:
            log("no AGENT item is READY — stopping (not a failure stop)")
            break
        item = ready[0]
        steps += 1
        item["status"] = "RUNNING"
        save(q)
        log(f"[{steps}] {item['id']} :: {item['next_action']}")
        try:
            subprocess.run([sys.executable, os.path.join(R, "tools", "heartbeat.py"), item["id"]],
                           capture_output=True, text=True, timeout=60)
        except Exception:
            pass
        ok, detail = run(item)
        item["attempts"] = int(item.get("attempts", 0)) + 1
        item["last_result"] = detail
        item["last_run_utc"] = time.strftime("%FT%TZ", time.gmtime())
        if ok:
            item["status"] = "DONE"
            log(f"    DONE {item['id']}")
        else:
            item["status"] = "PARKED"
            item["parked_reason"] = "STEP_FAILED"
            item["retry_hint"] = ("ladder: 1) narrow the command 2) raise timeout_s 3) switch arm; the item stays "
                                  "PARKED until a human or a later pass re-arms it")
            log(f"    PARKED {item['id']} — continuing with the next ready item")
        save(q)
    q.setdefault("runs", []).append({
        "at": time.strftime("%FT%TZ", time.gmtime()), "steps": steps,
        "done": sum(1 for i in q["items"] if i["status"] == "DONE"),
        "parked": sum(1 for i in q["items"] if i["status"] == "PARKED"),
        "owner": sum(1 for i in q["items"] if i["owner_class"] == "OWNER"),
        "host": sum(1 for i in q["items"] if i["owner_class"] == "HOST"),
        "ready": sum(1 for i in q["items"] if i["status"] == "READY")})
    save(q)
    log(f"=== advance_queue end: {json.dumps(q['runs'][-1], ensure_ascii=False)} ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
