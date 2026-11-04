#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run all six W0 implementation lanes against a given r4c source package.

    python reproduce.py --source-root /path/to/FHS_PIPD-LS-PKG_W0_R4C

Every step writes its own log under runs/<timestamp>/; the first non-zero exit stops the run
and is reported. Nothing is installed and no network is used.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANES = HERE / "lanes"


def run(cmd, log_path, cwd, extra_env=None):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    if extra_env:
        env.update(extra_env)
    with open(log_path, "w", encoding="utf-8", newline="\n") as fh:
        p = subprocess.run(cmd, cwd=str(cwd), stdout=fh, stderr=subprocess.STDOUT, env=env)
    return {"cmd": cmd, "cwd": str(cwd), "exit": p.returncode,
            "seconds": round(time.time() - t0, 2), "log": str(log_path)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--zip", default=None)
    ap.add_argument("--body", default=None)
    ap.add_argument("--wp19-tree", default=None,
                    help="tree the supply-chain gate scans (default: the PIPD package root when it has a LICENSE, else the source root)")
    a = ap.parse_args()
    S = Path(a.source_root).resolve()
    if not S.is_dir():
        print("source root not found: %s" % S)
        return 2
    zip_path = Path(a.zip) if a.zip else S.parent / (S.name + ".zip")
    body = Path(a.body) if a.body else next(iter(sorted(S.glob("*_實質正文.md"))), None)
    if body is None:
        print("no substantive body md found under %s" % S)
        return 2
    run_root = HERE / "runs" / time.strftime("%Y%m%d_%H%M%S")
    heads = HERE / "docs" / "REMOTE_HEADS.json"
    pkg_root = HERE.parent
    wp19_tree = Path(a.wp19_tree) if a.wp19_tree else (pkg_root if (pkg_root / "LICENSE").exists() else S)
    # wp19 is a gate: exit 1 means "the gate found something", which is a reportable outcome,
    # not a harness crash. Any other code is a harness failure.
    steps = [
        ("wp00", [sys.executable, "source_probe.py", "--zip", str(zip_path), "--source-root", str(S), "--out", "out",
                  "--heads", str(heads)]),
        ("wp01", [sys.executable, "authority_router.py", "--source-root", str(S), "--out", "out"]),
        ("wp15", [sys.executable, "spec_pipeline.py", "--body", str(body), "--source-root", str(S), "--out", "out",
                  "--goal", "讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證且可回讀的三份 SPEC"]),
        ("wp16", [sys.executable, "need_occupant.py", "--source-root", str(S), "--out", "out"]),
        ("wp19", [sys.executable, "supply_chain_gate.py", "--tree", str(wp19_tree), "--out", "out/SUPPLY_CHAIN_RAW.json", "--mode", "author"]),
        ("wp21", [sys.executable, "trace_runner.py", "--source-root", str(S), "--out", "out"]),
    ]
    results, failed, findings = [], None, []
    # A gate may legitimately exit non-zero to mean "sealed but with findings/holds":
    # wp19 exit 1 = at least one FAIL check; wp21 exit 3 = structurally sealed with holds.
    allowed = {"wp19": {0, 1}, "wp21": {0, 3}}
    for name, cmd in steps:
        r = run(cmd, run_root / (name + "_tool.log"), LANES / name)
        r["findings_exit"] = r["exit"] != 0 and r["exit"] in allowed.get(name, {0})
        if r["findings_exit"]:
            findings.append(name)
        results.append({"step": name + "_tool", **r})
        if r["exit"] != 0 and not r["findings_exit"]:
            failed = name + "_tool"
            break
    if failed is None:
        for name in ("wp00", "wp01", "wp15", "wp16", "wp19", "wp21"):
            r = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
                    run_root / (name + "_tests.log"), LANES / name,
                    extra_env={"FHS_R4C_SOURCE_ROOT": str(S)})
            results.append({"step": name + "_tests", **r})
            if r["exit"] != 0:
                failed = name + "_tests"
                break
    rec = {"schema": "FHS_W0_IMPL/REPRODUCE/v1", "source_root": str(S), "zip": str(zip_path),
           "body": str(body), "input_body_sha256": __import__("hashlib").sha256(body.read_bytes()).hexdigest(),
           "wp19_tree": str(wp19_tree),
           "steps": results, "first_fail": failed, "findings_exit_steps": findings,
           "verdict": ("FAIL" if failed else
                       ("PASS_AUTHOR_LOCAL_WITH_FINDINGS" if findings else "PASS_AUTHOR_LOCAL"))}
    (run_root / "REPRODUCE.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n",
                                             encoding="utf-8", newline="\n")
    print(json.dumps({"run_root": str(run_root), "steps": len(results), "first_fail": failed,
                      "verdict": rec["verdict"]}, ensure_ascii=False))
    return 0 if failed is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
