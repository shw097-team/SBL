"""Run a mandated lane in one command, so using the lane is cheaper than bypassing it.

    python tools/run_lane.py --role PLAN    --brief workers/plan_brief/ROOT_CAUSE.md
    python tools/run_lane.py --role EXECUTE --brief workers/codex_exec/BRIEF.md
    python tools/run_lane.py --role VERIFY  --brief workers/verify/CHECK.md

Lane, provider/model and rank come from MANDATE_R15_2.json. A receipt lands in receipts/dispatch/ regardless of outcome,
so the gate can audit it afterwards.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
HGK = r"C:/Projects/Agent_Workspace/HG-KSEOS"
MANDATE = os.path.join(R, "MANDATE_R15_2.json")


def main() -> int:
    if "--role" not in sys.argv or "--brief" not in sys.argv:
        print("usage: run_lane.py --role PLAN|EXECUTE|VERIFY --brief <file> [--nonce N] [--timeout 560]")
        return 2
    role = sys.argv[sys.argv.index("--role") + 1]
    brief = sys.argv[sys.argv.index("--brief") + 1]
    if not os.path.isabs(brief):
        brief = os.path.join(R, brief)
    if not os.path.exists(brief):
        print(f"BRIEF_MISSING {brief}")
        return 2
    m = json.load(open(MANDATE, encoding="utf-8"))["roles"][role]
    nonce = (sys.argv[sys.argv.index("--nonce") + 1] if "--nonce" in sys.argv
             else f"{m['lane']}-R152-{time.strftime('%H%M%S')}-{abs(hash(brief)) % 9999:04d}")
    tmo = int(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 560
    out = os.path.join(R, "receipts", "dispatch", f"{m['lane']}_{os.path.basename(brief).replace('.md', '')}.json")
    cmd = [sys.executable, "scripts/hgk-lane-dispatch.py", "--lane", m["lane"], "--prompt", brief,
           "--nonce", nonce, "--require-arm", m["provider_model"], "--force-rank", str(m["required_rank"]),
           "--pool", "config/lane-route-slots.candidate.json", "--cwd", R, "--timeout", str(tmo),
           "--json-out", out]
    env = dict(os.environ, PYTHONPATH="src")
    p = subprocess.run(cmd, cwd=HGK, capture_output=True, text=True, timeout=tmo + 90, env=env)
    tail = ((p.stdout or "") + (p.stderr or "")).strip().splitlines()[-2:]
    print("dispatch_exit=", p.returncode)
    print("\n".join(tail))
    try:
        d = json.load(open(out, encoding="utf-8"))
        a = (d.get("attempts") or [{}])[0]
        print(json.dumps({"lane": d.get("lane"), "ok": d.get("ok"), "secs": a.get("seconds"),
                          "nonce": a.get("nonce_present"), "model": d.get("used_transport_model"),
                          "rank": d.get("used_rank"), "receipt": out}, ensure_ascii=False))
        return 0 if d.get("ok") else 1
    except Exception as exc:
        print(f"RECEIPT_UNREADABLE {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
