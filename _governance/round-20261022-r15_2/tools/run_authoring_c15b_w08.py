"""Two narrowed dispatches, unattended: C15 retry (2 tests) then W08 supersession.

Sequential on purpose - one lane dispatch at a time. Writes its own JSON so the round queue can record the
verdict from evidence rather than from a claim.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time

ROUND = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
WORKTREE = r"C:/Projects/Agent_Workspace/_r152_ev"
HGK = r"C:/Projects/Agent_Workspace/HG-KSEOS"
OUT = os.path.join(ROUND, "workers", "codex_exec", "RUN_C15B_W08.json")

JOBS = [
    {"item": "DEN-C15", "brief": "workers/codex_exec/DEN-C15_narrow2.md",
     "artefact": HGK + "/tests/test_c15_evolution_holdout.py",
     "accept_cwd": HGK, "accept": [sys.executable, "-m", "pytest", "tests/test_c15_evolution_holdout.py", "-q"],
     "env": {"PYTHONPATH": HGK + "/src"}},
    {"item": "DEN-W08", "brief": "workers/codex_exec/DEN-W08_narrow.md",
     "artefact": WORKTREE + "/tests/test_lane_consistency_supersession.py",
     "accept_cwd": WORKTREE, "accept": [sys.executable, "-m", "pytest", "tests/test_lane_consistency_supersession.py", "-q"],
     "env": {}},
]


def sh(args, cwd, timeout, env=None):
    t0 = time.time()
    e = dict(os.environ, **(env or {}))
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=e)
        return p.returncode, (p.stdout or "") + (p.stderr or ""), round(time.time() - t0, 2)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT", round(time.time() - t0, 2)


def main() -> int:
    runs = []
    for j in JOBS:
        rec = {"item": j["item"], "brief": j["brief"], "artefact": j["artefact"]}
        nonce = "%s-A2-%d" % (j["item"].replace("-", "_"), int(time.time()))
        rc, out, secs = sh([sys.executable, os.path.join(ROUND, "tools", "run_lane.py"), "--role", "EXECUTE",
                            "--brief", j["brief"], "--nonce", nonce, "--timeout", "290"], WORKTREE, 380)
        rec["dispatch"] = {"rc": rc, "secs": secs, "tail": out.strip().splitlines()[-2:]}
        rec["artefact_present"] = os.path.exists(j["artefact"])
        if rec["artefact_present"]:
            rec["artefact_sha256"] = hashlib.sha256(open(j["artefact"], "rb").read()).hexdigest()
            arc, aout, asecs = sh(j["accept"], j["accept_cwd"], 300, j["env"])
            rec["accept"] = {"rc": arc, "secs": asecs, "tail": aout.strip().splitlines()[-3:]}
        runs.append(rec)
        json.dump({"schema": "SBL-AUTHORING-RUN/1", "runs": runs}, open(OUT, "w", encoding="utf-8", newline="\n"),
                  ensure_ascii=False, indent=2)
        print(json.dumps(rec, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
