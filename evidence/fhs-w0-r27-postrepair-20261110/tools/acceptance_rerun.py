#!/usr/bin/env python3
"""acceptance_rerun — the commander's independent re-execution of every decisive negative.

Why a separate runner: the lane that wrote a check must not be the only process that ever ran it.
This script spawns a FRESH process per check, with stdout/stderr captured to its own evidence path,
and records the exit code it actually got. It never imports the code under test.

Exit 0 only when every row matches its expectation.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys

WT = pathlib.Path("C:/Projects/Agent_Workspace/FHS_R26_WT")
OUT = pathlib.Path("C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110/evidence/ACCEPTANCE_RERUN")
PY311 = "C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe"
PYCRYPTO = "D:/Hermes-Recovery/port-serve-home/installs/b102548ee4f8e4a3/environments/3a3e2a5d77634dac9b1464274b872271/venv/Scripts/python.exe"

SBL_ROUND = "evidence/fhs-w0-r26-repair-20261109"


def rows() -> list[dict]:
    q = WT / "sbl-quorum" / SBL_ROUND / "tools"
    l = WT / "sbl-3lm" / SBL_ROUND / "tools"
    m = WT / "sbl-meta" / SBL_ROUND / "tools"
    b = WT / "hgk-bridge"
    f = WT / "fabric-mirror"
    h = WT / "hgk-hook"
    return [
        # --- L1 quorum -------------------------------------------------------------
        {"id": "L1.selftest", "cmd": [PY311, str(q / "verify_quorum.py"), "--selftest"], "expect": 0, "cwd": str(WT / "sbl-quorum")},
        {"id": "L1.r25-scan", "cmd": [PY311, str(q / "verify_quorum.py"),
                                      "--root", str(WT / "sbl-quorum" / SBL_ROUND)], "expect": 0, "cwd": str(WT / "sbl-quorum")},
        # --- L2 binding ------------------------------------------------------------
        {"id": "L2.selftest",
         "cmd": [PY311, str(l / "selftest_fhs_3lm.py"), "--tool", str(l / "fhs_3lm.py"),
                 "--hgk-root", str(b),
                 "--epoch33-root", "C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110/evidence/L2/probe/epoch33",
                 "--workdir", "C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110/evidence/ACCEPTANCE_RERUN/l2scratch",
                 "--logdir", "C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110/evidence/ACCEPTANCE_RERUN/l2logs",
                 "--json-out", "C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110/evidence/ACCEPTANCE_RERUN/l2selftest.json"],
         "expect": 0, "cwd": str(WT / "sbl-3lm")},
        {"id": "L2.menu-epoch41", "cmd": [PY311, str(l / "fhs_3lm.py"), "--menu", "--hgk-root", str(b)],
         "expect": 0, "cwd": str(WT / "sbl-3lm")},
        {"id": "L2.retired-arm", "cmd": [PY311, str(l / "fhs_3lm.py"), "--assert-arm", "opencode-go/mimo-v2.6-pro",
                                         "--hgk-root", str(b)], "expect": 9, "cwd": str(WT / "sbl-3lm")},
        # --- L3 metadata + crypto --------------------------------------------------
        {"id": "L3.gate-payload", "cmd": [PY311, str(m / "gate_r20.py"), "--round", str(WT / "sbl-meta" / SBL_ROUND),
                                          "--profile", "payload", "--scope", "payload", "--skip-hygiene"],
         "expect": 0, "cwd": str(WT / "sbl-meta" / SBL_ROUND)},
        {"id": "L3.ed25519", "cmd": [PYCRYPTO, str(m / "verify_public_bundle.py")], "expect": 0,
         "cwd": str(WT / "sbl-meta" / SBL_ROUND)},
        {"id": "L3.ed25519-selftest", "cmd": [PYCRYPTO, str(m / "verify_public_bundle.py"), "--selftest"], "expect": 0,
         "cwd": str(WT / "sbl-meta" / SBL_ROUND)},
        # --- L4 epoch bridge -------------------------------------------------------
        {"id": "L4.validate-pos", "cmd": [PY311, str(b / "scripts" / "lane_epoch_validate.py"),
                                          "--root", str(b)], "expect": 0, "cwd": str(b)},
        {"id": "L4.pytest", "cmd": [PY311, "-m", "pytest", "-q", "tests/test_lane_epoch_validate.py"], "expect": 0, "cwd": str(b)},
        # --- L6 fabric admission ---------------------------------------------------
        {"id": "L6.pytest", "cmd": [PY311, "-m", "pytest", "-q", "INTEGRATION/FHS/tests/test_manifest_admission.py"],
         "expect": 0, "cwd": str(f)},
        {"id": "L6.validate", "cmd": [PY311, str(f / "INTEGRATION/FHS/tools/validate_manifest_admission.py"),
                                      "--repo", str(f)], "expect": 0, "cwd": str(f)},
        # --- L5 hard entry ---------------------------------------------------------
        {"id": "L5.selftest", "cmd": [PY311, str(h / "scripts" / "selftest_fhs_entry_guard.py")], "expect": 0, "cwd": str(h)},
        {"id": "L5.pytest", "cmd": [PY311, "-m", "pytest", "-q", "tests/test_fhs_entry_guard.py"], "expect": 0, "cwd": str(h)},
    ]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    res, bad = [], 0
    for r in rows():
        log = OUT / (r["id"].replace(".", "_") + ".log")
        argv = [str(x) for x in r["cmd"]]
        try:
            p = subprocess.run(argv, cwd=r["cwd"], capture_output=True, text=True, timeout=900,
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            out = (p.stdout or "") + ("\n[stderr]\n" + p.stderr if p.stderr else "")
            code = p.returncode
        except subprocess.TimeoutExpired:
            out, code = "TIMEOUT after 900s", 124
        except FileNotFoundError as e:
            out, code = f"ERR_FILE_NOT_FOUND {e}", 127
        log.write_text(f"$ {' '.join(argv)}\ncwd={r['cwd']}\nexit={code}\n\n{out}", encoding="utf-8")
        ok = code == r["expect"]
        bad += 0 if ok else 1
        res.append({"id": r["id"], "expect_exit": r["expect"], "observed_exit": code, "ok": ok,
                    "log": log.relative_to(OUT.parent.parent).as_posix(),
                    "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()})
        print(f"{'PASS' if ok else 'FAIL'}  {r['id']:<22} expect={r['expect']} got={code}")
    report = {"schema": "FHS.R27.AcceptanceRerun/1", "checks": len(res), "failed": bad, "rows": res,
              "OK": bad == 0}
    (OUT / "ACCEPTANCE_RERUN.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(res), "failed": bad}, ensure_ascii=False))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
