"""Drive the R15.2 queue: run every ready AGENT item, park what fails, keep going.

Stop policy (the only legal stops): destructive action, missing credential, mandated lane unavailable, owner-only
decision. Anything else is parked with a typed reason and the driver continues. The driver exits when no AGENT item is
READY — never because a single step failed.
"""
from __future__ import annotations

import hashlib
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


def classify_dispatch(item: dict, ok: bool, artefact_exists: bool, accept_ok: bool | None) -> tuple[str, str]:
    """Decide the item's next status from three independent facts, per the FAR ruling.

    The facts are never merged: dispatch outcome, artefact existence, acceptance result. A timed-out lane that
    really wrote the artefact is PARTIAL on the TEST phase (not a pass, not a re-author), because re-authoring
    over an existing artefact is the blind-mutation retry the mandate forbids.
    """
    art = item.get("expect_artefact")
    if not ok and artefact_exists and art:
        return "PARTIAL", "ARTEFACT_PRESENT_BUT_DISPATCH_NOT_GREEN"
    if ok and art and not artefact_exists:
        return "PARKED", "DISPATCH_GREEN_BUT_ARTEFACT_MISSING"
    if not ok:
        return "PARKED", "STEP_FAILED"
    if art:
        if accept_ok is True:
            return "DONE", "ACCEPTED"
        return "PARTIAL", "ARTEFACT_PRESENT_ACCEPT_FAILED"
    return "DONE", "ACCEPTED"


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
            # FAR: zero selected items is not exhaustion while AGENT-satisfiable work is unresolved. Say what remains
            # and why it was not selected, so an idle tick cannot be mistaken for "nothing left to do".
            unresolved = [i for i in q["items"]
                          if i.get("owner_class") == "AGENT" and i["status"] != "DONE"
                          and i.get("satisfiable_by", "AGENT") == "AGENT"]
            why = {}
            for i in unresolved:
                if int(i.get("attempts", 0)) >= ATTEMPT_CAP:
                    why.setdefault("ATTEMPT_CAP_REACHED", []).append(i["id"])
                elif not i.get("resume_cmd"):
                    why.setdefault("NO_EXECUTABLE_ACTION", []).append(i["id"])
                else:
                    why.setdefault("NOT_SELECTED_OTHER", []).append(i["id"])
            log("no AGENT item is selectable — NOT exhaustion, NOT a failure stop")
            log(f"    unresolved AGENT work: {len(unresolved)} " + json.dumps(why, ensure_ascii=False))
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
        art = item.get("expect_artefact")
        art_exists = bool(art) and os.path.exists(os.path.join(WORKTREE, art))
        accept_ok = None
        if ok and art_exists and item.get("accept_cmd"):
            try:
                ap = subprocess.run(item["accept_cmd"], shell=True, cwd=WORKTREE, capture_output=True, text=True,
                                    timeout=int(item.get("accept_timeout_s", 300)))
                accept_ok = ap.returncode == 0
                item["accept_result"] = {"rc": ap.returncode,
                                         "tail": ((ap.stdout or "") + (ap.stderr or "")).strip().splitlines()[-4:]}
            except subprocess.TimeoutExpired:
                accept_ok = False
                item["accept_result"] = {"rc": None, "tail": ["ACCEPT_TIMEOUT"]}
        status, reason = classify_dispatch(item, ok, art_exists, accept_ok)
        if art_exists:
            with open(os.path.join(WORKTREE, art), "rb") as fh:
                item["artefact_sha256"] = hashlib.sha256(fh.read()).hexdigest()
        if status != "DONE" and item.get("phase") == "AUTHOR" and art_exists:
            # the artefact is on disk: the remaining work is TEST, not another authoring dispatch
            item["phase"] = "TEST"
            item["resume_cmd"] = item["accept_cmd"]
            item["expect"] = r"(\d+) passed"
            item["attempts"] = 0
        item["status"] = status
        if status == "DONE":
            item.pop("parked_reason", None)
            log(f"    DONE {item['id']} ({reason})")
        elif status == "PARTIAL":
            item["rearm_ok"] = True
            item.pop("parked_reason", None)
            item["partial_reason"] = reason
            log(f"    PARTIAL {item['id']} — {reason}; continuing")
        else:
            item["parked_reason"] = reason
            item["retry_hint"] = ("ladder: 1) narrow the command 2) raise timeout_s 3) switch arm; the item stays "
                                  "PARKED until a human or a later pass re-arms it")
            log(f"    PARKED {item['id']} — {reason}; continuing with the next ready item")
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
