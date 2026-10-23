"""Drive the three narrowed authoring dispatches, then run their acceptance, unattended.

One item at a time: EXECUTE lane dispatch (bounded), artefact existence check, then pytest in HG-KSEOS.
Nothing is marked DONE here; the round queue records the verdict from the JSON this writes.
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
OUT = os.path.join(ROUND, "workers", "codex_exec", "RUN_C13_C14_C15.json")

ITEMS = [
    ("DEN-C13", "workers/codex_exec/DEN-C13_narrow.md", "C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c13_standing_scope_no_routine_hitl.py"),
    ("DEN-C14", "workers/codex_exec/DEN-C14_narrow.md", "C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c14_checkpoint_resume_no_repeat_effect.py"),
    ("DEN-C15", "workers/codex_exec/DEN-C15_narrow.md", "C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c15_evolution_sandbox_holdout_promotion.py"),
]


def sh(args, cwd, timeout):
    t0 = time.time()
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, shell=isinstance(args, str))
        return p.returncode, (p.stdout or "") + (p.stderr or ""), round(time.time() - t0, 2)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT", round(time.time() - t0, 2)


def main() -> int:
    results = []
    for item, brief, art in ITEMS:
        rec = {"item": item, "brief": brief, "artefact": art}
        nonce = "%s-AUTHOR-%d" % (item.replace("-", "_"), int(time.time()))
        cmd = [sys.executable, os.path.join(ROUND, "tools", "run_lane.py"), "--role", "EXECUTE",
               "--brief", brief, "--nonce", nonce, "--timeout", "300"]
        rc, out, secs = sh(cmd, WORKTREE, 400)
        rec["dispatch"] = {"rc": rc, "secs": secs, "tail": out.strip().splitlines()[-2:]}
        rec["artefact_present"] = os.path.exists(art)
        if rec["artefact_present"]:
            rec["artefact_sha256"] = hashlib.sha256(open(art, "rb").read()).hexdigest()
            env = dict(os.environ, PYTHONPATH=os.path.join(HGK, "src"))
            arc, aout, asecs = sh([sys.executable, "-m", "pytest", art, "-q"], HGK, 300)
            rec["accept"] = {"rc": arc, "secs": asecs, "tail": aout.strip().splitlines()[-3:]}
        json.dump({"schema": "SBL-AUTHORING-RUN/1", "runs": results + [rec]}, open(OUT, "w", encoding="utf-8", newline="\n"),
                  ensure_ascii=False, indent=2)
        results.append(rec)
        print(json.dumps(rec, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
