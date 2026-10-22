"""Re-execute the 32 RUNTIME_QUALIFIED cells instead of trusting their recorded receipts.

The v2 matrix proved the receipts existed and their digests matched, but it never re-ran the commands: the earlier attempt
built them with `bash -c "$cmd"` and was refused by the approval gate. This script takes the recorded command apart
(environment assignments, executable, arguments), runs it with shell=False, and compares three things per cell: the exit
code, the fresh sha256 of the evidence file, and whether the evidence file changed at all.

A cell is RE_EXECUTED only if its command ran and its exit code agrees with the record. It is REPRODUCED only if the
evidence digest also matches. Anything else is reported as DRIFT or NOT_REEXECUTED with the reason - never rounded up.
"""
import hashlib
import json
import os
import subprocess
from pathlib import Path

RAW = Path(__file__).resolve().parent
MATRIX = RAW / "ts17_matrix_v2.json"
OUT = RAW / "ts17_reexec_v3.json"
ENV_MARKERS = ("PYTHONPATH=", "PYTHONDONTWRITEBYTECODE=", "PYTHONIOENCODING=", "TMPDIR=", "TEMP=", "TMP=")


def split_command(command: str):
    """Return (env, argv) for a command written as 'A=1 B=2 exe arg arg'. No shell is involved."""
    env, argv = {}, []
    for token in command.split():
        if not argv and any(token.startswith(m) for m in ENV_MARKERS):
            key, _, value = token.partition("=")
            env[key] = value
            continue
        argv.append(token)
    return env, argv


def main() -> int:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    cells = [c for c in matrix["cells"] if c.get("state") == "RUNTIME_QUALIFIED"]
    results = []
    for cell in cells:
        env_extra, argv = split_command(cell["command"])
        cwd = cell.get("cwd") or str(RAW)
        # Windows will not resolve a relative executable for CreateProcess, so anchor it against the recorded cwd.
        if argv and not Path(argv[0]).is_absolute():
            argv[0] = str((Path(cwd) / argv[0]).resolve())
        evidence = Path(cell["evidence_path"]) if cell.get("evidence_path") else None
        before = hashlib.sha256(evidence.read_bytes()).hexdigest() if evidence and evidence.is_file() else None
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)          # a stray PYTHONPATH once made a measurement import a stale package
        env.update(env_extra)
        record = {"skill": cell["skill"], "test_class": cell["test_class"],
                  "oracle_type": cell["oracle_type"], "command": cell["command"],
                  "recorded_exit": cell.get("exit_code"), "recorded_sha256": cell.get("evidence_sha256")}
        try:
            proc = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=300)
        except Exception as exc:                                  # noqa: BLE001 - the reason is the result
            record.update({"state": "NOT_REEXECUTED", "reason": f"{type(exc).__name__}: {exc}"})
            results.append(record)
            continue
        after = hashlib.sha256(evidence.read_bytes()).hexdigest() if evidence and evidence.is_file() else None
        record.update({"observed_exit": proc.returncode, "stderr_tail": (proc.stderr or "")[-300:],
                       "evidence_before": before, "evidence_after": after,
                       "evidence_rewritten": bool(before and after and before != after)})
        if proc.returncode != cell.get("exit_code"):
            record["state"] = "DRIFT_EXIT"
            record["reason"] = f"recorded exit {cell.get('exit_code')}, observed {proc.returncode}"
        elif cell.get("evidence_sha256") and after != cell["evidence_sha256"]:
            record["state"] = "DRIFT_EVIDENCE"
            record["reason"] = "the command ran, but the evidence bytes differ from the recorded digest"
        else:
            record["state"] = "REPRODUCED" if after == cell.get("evidence_sha256") else "RE_EXECUTED"
            record["reason"] = ("command re-ran and the evidence digest is unchanged"
                               if record["state"] == "REPRODUCED" else
                               "command re-ran with the recorded exit code; no evidence digest was recorded")
        results.append(record)

    counts = {}
    for r in results:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
    doc = {
        "schema": "SBL-R14-TS17-REEXEC/1",
        "answers": "the v2 matrix verified receipts statically; this re-runs them without a shell",
        "method": ("the recorded command is split into environment assignments and argv, then executed with shell=False; "
                   "PYTHONPATH is cleared first, because a stray value once made a measurement import a stale package"),
        "cells": len(results), "counts": counts,
        "claim_ceiling": ("32 real executions still say nothing about the 736 DECLARED_ONLY cells, and nothing about "
                          "functional-native DOC-08 qualification, which remains 0."),
        "results": results,
    }
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"cells": len(results), "counts": counts}, ensure_ascii=False))
    for r in results:
        if r["state"] not in ("REPRODUCED", "RE_EXECUTED"):
            print(" ", r["state"], r["skill"], r["test_class"], r.get("reason", "")[:120])
    return 0 if all(r["state"] in ("REPRODUCED", "RE_EXECUTED") for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
