"""Wait for the model transport to accept a credential, then drain the parked dispatches.

Why this exists: on 2026-10-23 the shared relay began answering 401 Invalid credential to both OPENCODEGO keys on
disk, so every EXECUTE/VERIFY dispatch died in ~12 s. Minting a credential is not mine to do, and re-typing the same
dispatch on a timer is a human loop. So this watcher probes the transport, and the moment it accepts a request it runs
the queued briefs through the mandated lanes and writes a receipt for each.

It never invents a pass: a probe is only a gate, and every dispatch still has to earn its own receipt.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

ROUND = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
WORKTREE = r"C:/Projects/Agent_Workspace/_r152_ev"
KEY = r"C:/Projects/Agent_Workspace/API KEY/shw0968_OPENCODEGO_KEY.txt"
RELAY = "http://127.0.0.1:10101/v1"
OUT = os.path.join(ROUND, "receipts", "lane_watch.json")
POLL_S = 300
MAX_WAIT_S = 6 * 3600

QUEUE = [
    {"role": "EXECUTE", "brief": "workers/codex_exec/W08_D1.md", "timeout": 200},
    {"role": "EXECUTE", "brief": "workers/codex_exec/W08_D2.md", "timeout": 200},
]


def probe() -> tuple[bool, str]:
    key = open(KEY, encoding="utf-8").read().strip()
    body = json.dumps({"model": "deepseek-v4.1-flash", "messages": [{"role": "user", "content": "ping"}],
                       "max_tokens": 1})
    p = subprocess.run(["curl", "-s", "-m", "10", "-o", "/dev/null", "-w", "%{http_code}",
                        "-X", "POST", RELAY + "/v1/chat/completions",
                        "-H", "Content-Type: application/json", "-H", "Authorization: Bearer " + key,
                        "-d", body], capture_output=True, text=True, timeout=30)
    code = (p.stdout or "").strip()
    return code == "200", code


def dispatch(item: dict) -> dict:
    env = dict(os.environ, HGK_LANE_RELAY_BASE=RELAY, HGK_LANE_CODEX_ARGS="-c|features.responses_websocket=false")
    nonce = "WATCH-%s-%d" % (os.path.basename(item["brief"]).replace(".md", ""), int(time.time()))
    cmd = [sys.executable, os.path.join(ROUND, "tools", "run_lane.py"), "--role", item["role"],
           "--brief", item["brief"], "--nonce", nonce, "--timeout", str(item["timeout"])]
    p = subprocess.run(cmd, cwd=WORKTREE, capture_output=True, text=True, timeout=item["timeout"] + 120, env=env)
    tail = ((p.stdout or "") + (p.stderr or "")).strip().splitlines()[-1:]
    return {"brief": item["brief"], "role": item["role"], "rc": p.returncode, "tail": tail}


def main() -> int:
    started = time.time()
    log = {"schema": "SBL-LANE-WATCH/1", "started_utc": time.strftime("%FT%TZ", time.gmtime()),
           "relay": RELAY, "probes": [], "dispatches": []}
    while time.time() - started < MAX_WAIT_S:
        ok, code = probe()
        log["probes"].append({"at": time.strftime("%FT%TZ", time.gmtime()), "http": code})
        json.dump(log, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
        print("probe", code, flush=True)
        if ok:
            for item in QUEUE:
                log["dispatches"].append(dispatch(item))
                json.dump(log, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
                print(json.dumps(log["dispatches"][-1], ensure_ascii=False), flush=True)
            log["outcome"] = "TRANSPORT_RESTORED_AND_QUEUE_DRAINED"
            json.dump(log, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
            return 0
        time.sleep(POLL_S)
    log["outcome"] = "TIMED_OUT_WAITING_FOR_CREDENTIAL"
    json.dump(log, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
