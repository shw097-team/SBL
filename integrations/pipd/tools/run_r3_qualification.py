#!/usr/bin/env python3
"""FW-09 (audit finding R-AUD-010): re-qualify the pilots and the 13-command CLI.

This runner is a MEASUREMENT harness, not a judge: it executes the fresh suite, the
13-command surface, the golden pilots and the replay/rollback probes, captures each
raw stdout/stderr/exit verbatim, and binds them to one candidate tuple. It never
computes a PASS by itself, never merges the 22/47/57 denominators, and never
substitutes a historical receipt for a fresh run.

Usage:
  python tools/run_r3_qualification.py --out .hgk/rounds/R3-20261009-audit-repair/FW-09
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TZ = timezone(timedelta(hours=8))
CLI13 = ["init", "intake", "profile", "compile-pi", "bind-pd", "compile-ecp", "compile-tqaep",
         "validate", "doctor", "project", "export", "diff", "repair"]


def run(cmd: list[str], log: Path, cwd: Path = ROOT) -> dict:
    log.parent.mkdir(parents=True, exist_ok=True)
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, env=env)
    log.write_text(f"$ {' '.join(cmd)}\nexit={p.returncode}\n--- stdout ---\n{p.stdout}\n"
                   f"--- stderr ---\n{p.stderr}\n", encoding="utf-8", newline="")
    return {"cmd": " ".join(cmd), "exit": p.returncode, "raw_log": log.name,
            "stdout_bytes": len(p.stdout.encode()), "stderr_bytes": len(p.stderr.encode())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    raw = out / "raw"
    out.mkdir(parents=True, exist_ok=True)

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()
    tree = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()
    status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=str(ROOT),
                            capture_output=True, text=True).stdout

    commands: list[dict] = []
    # 1) fresh unit suite (the R3 denominator, captured separately from the historical 22/47/57)
    commands.append(run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
                        raw / "unittest_r3.txt"))
    # 2) the 13-command surface, invoked through the module entry point
    commands.append(run([sys.executable, "-B", "-m", "pipd_ls_sp.cli", "--help"], raw / "cli_help.txt"))
    for name in CLI13:
        commands.append(run([sys.executable, "-B", "-m", "pipd_ls_sp.cli", name, "--help"],
                            raw / f"cli_{name}.txt"))
    # 3) golden pilots + replay + performance, when the tools are present
    for tool, extra in (("run_golden_pilots.py", ["--all", "--raw"]),
                        ("replay_check.py", []),
                        ("perf_budget.py", []),
                        ("edge_selfcheck.py", [])):
        p = ROOT / "tools" / tool
        if p.exists():
            commands.append(run([sys.executable, "-B", str(p), *extra], raw / f"{tool}.txt"))
        else:
            commands.append({"cmd": f"python tools/{tool}", "exit": None,
                             "raw_log": None, "note": "TOOL_ABSENT"})

    receipt = {
        "schema": "PIPD-R3-FW09-QUALIFICATION/1",
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "candidate": {"repo_commit_sha": head, "repo_tree_sha": tree,
                      "worktree_dirty_lines": len([l for l in status.splitlines() if l.strip()]),
                      "runner": f"{sys.version.split()[0]} unittest"},
        "denominator_policy": ("22/47/57 style denominators are NOT merged; this run records its own "
                               "fresh discovery count and never replaces it with a historical PASS."),
        "commands": commands,
        "honesty": {"passes_computed_by_this_runner": 0,
                    "note": "measurement only; qualification verdicts belong to the gate rows."},
    }
    (out / "FW-09_QUALIFICATION.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=1) + "\n",
                                                 encoding="utf-8", newline="")
    print(json.dumps({"out": str(out / "FW-09_QUALIFICATION.json"),
                      "head": head, "commands": len(commands),
                      "nonzero_exit": [c["cmd"] for c in commands if c.get("exit") not in (0, None)]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
