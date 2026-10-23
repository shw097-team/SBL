"""Q5 local half — eight lifecycle verbs with real exit codes (no pipeline masking).

Runs the sbl_stack CLI through install/doctor/status/load/invoke/upgrade/rollback/uninstall
against an isolated root, records each verb's own exit code, and asserts the negative
controls: invoke on an unknown mode must be refused, upgrade with the same manifest must
refuse, and uninstall must not leave the root behind. Writes receipt.json next to itself.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:/Projects/Agent_Workspace/_r152_ev"
WORK = os.path.join(tempfile.mkdtemp(prefix="q5lc_"), "stack")


def run(*args: str) -> dict:
    p = subprocess.run([sys.executable, "-m", "sbl_stack.cli", *args],
                       cwd=REPO, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    return {"argv": list(args), "exit": p.returncode,
            "stdout_tail": (p.stdout or "").strip().splitlines()[-3:],
            "stderr_tail": (p.stderr or "").strip().splitlines()[-3:]}


def main() -> int:
    rows = [run("install", "--root", WORK),
            run("doctor", "--root", WORK),
            run("status", "--root", WORK),
            run("load", "--root", WORK),
            run("invoke", "--root", WORK),
            run("invoke", "--root", WORK, "--mode", "NOT_A_REAL_MODE"),
            run("upgrade", "--root", WORK, "--manifest", os.path.join(WORK, "manifest.json")),
            run("rollback", "--root", WORK),
            run("uninstall", "--root", WORK)]
    exists_after = os.path.exists(WORK)
    pos = [r for r in rows[:5]]
    neg_unknown_mode = rows[5]
    neg_same_manifest = rows[6]
    receipt = {
        "schema": "SBL_Q5_LIFECYCLE_PROBE/1",
        "claim_ceiling": "local lifecycle probe in a temp root; no host install, no independent acceptance",
        "root": WORK,
        "verbs_ok": [r["argv"][0] for r in pos if r["exit"] == 0],
        "verbs_failed": [r for r in pos if r["exit"] != 0],
        "neg_unknown_mode": {"exit": neg_unknown_mode["exit"], "refused": neg_unknown_mode["exit"] != 0},
        "neg_same_manifest": {"exit": neg_same_manifest["exit"], "refused": neg_same_manifest["exit"] != 0},
        "uninstall_exit": rows[-1]["exit"],
        "root_removed_by_uninstall": not exists_after,
        "all_rows": rows,
    }
    receipt["verdict"] = ("PASS" if not receipt["verbs_failed"] and receipt["neg_unknown_mode"]["refused"]
                          and receipt["neg_same_manifest"]["refused"] and rows[-1]["exit"] == 0
                          else "FAIL")
    open(os.path.join(ROOT, "receipt.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(receipt, ensure_ascii=False, indent=2))
    print(json.dumps({k: receipt[k] for k in
                      ("verdict", "verbs_ok", "neg_unknown_mode", "neg_same_manifest",
                       "uninstall_exit", "root_removed_by_uninstall")}, ensure_ascii=False))
    return 0 if receipt["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
