#!/usr/bin/env python3
"""RG04 post-session continuity fixture card.

Dispatched by the EXISTING host job `3602bce285e8` (cron -> hermes/scripts/r17_queue_runner.py ->
tools/runner.py -> tools/advance.py --run -> bash -lc -> this file). It is deliberately boring and
strictly no-effect on every governed repo:

  * reads the canonical queue and reports its own row counts (a real measurement, not a sleep),
  * writes exactly one receipt under var/R17-20261023/runner/rg04/,
  * records its ancestor process chain so a successor can prove which host path drove it,
  * prints one JSON object and exits 0 (a non-zero exit would park the card and stop the cycle).

Usage:  python var/R17-20261023/tools/rg04_probe.py --tag A
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

R17 = r"C:\Projects\Agent_Workspace\var\R17-20261023"
OUT = os.path.join(R17, "runner", "rg04")


def ancestors(limit: int = 6) -> list:
    """Best-effort process ancestry: proves whether a cron wrapper (r17_queue_runner.py) is upstream."""
    chain, pid = [], os.getpid()
    try:
        for _ in range(limit):
            ps = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}') | "
                 "Select-Object -ExpandProperty ParentProcessId"],
                capture_output=True, text=True, timeout=20).stdout.strip()
            if not ps.isdigit():
                break
            ppid = int(ps)
            cmd = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"(Get-CimInstance Win32_Process -Filter 'ProcessId={ppid}') | "
                 "Select-Object -ExpandProperty CommandLine"],
                capture_output=True, text=True, timeout=20).stdout.strip()
            chain.append({"pid": ppid, "cmd": cmd[:300]})
            if ppid <= 4 or ppid == pid:
                break
            pid = ppid
    except Exception as exc:
        chain.append({"error": type(exc).__name__})
    return chain


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, choices=["A0", "A", "B", "C", "D", "E", "F", "G", "H"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    counts = {}
    try:
        q = json.load(open(os.path.join(R17, "WORK_QUEUE_R17.json"), encoding="utf-8"))
        rows = q.get("rows") or []
        counts = {"rows": len(rows), "ids_unique": len({r.get("id") for r in rows})}
    except Exception as exc:
        counts = {"error": type(exc).__name__}

    payload = {
        "schema": "SBL_R17_RG04_CARD/1",
        "tag": a.tag,
        "nonce": f"RG04-{a.tag}-{os.getpid()}-{int(datetime.datetime.now().timestamp())}",
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "local": datetime.datetime.now().astimezone().isoformat(),
        "pid": os.getpid(),
        "argv": sys.argv[1:],
        "ppid": os.getppid(),
        "ancestors": ancestors(),
        "queue": counts,
        "effect_on_governed_repos": "NONE_CLAIMED_MEASURED_BY_RUNNER_ENVELOPE",
    }
    body = json.dumps(payload, ensure_ascii=False, indent=1)
    dest = os.path.join(OUT, f"RG04_{a.tag}.json")
    with open(dest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    payload["receipt"] = dest
    payload["receipt_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
