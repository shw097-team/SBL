"""Gate runner for SBL v0.1: executes every locally runnable contract gate and freezes raw receipts.

This is an EVIDENCE GENERATOR, not an acceptance: it records command, exit code, raw stdout/stderr,
their sha256 and the parsed pytest denominator. The verdict of each gate is read from the exit code;
no gate is marked PASS here on any other basis.

Usage: python tools/run_gates.py [--root .] [--json-out evidence/gates/GATES_RAW.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Every "<n> <outcome>" pair on pytest's summary line counts. The old pattern was anchored at the
# start of a line, so "1 failed, 31 passed" recorded a denominator of 1 (VERIFY-02).
PYTEST_LINE = re.compile(r"(\d+) (passed|failed|error|errors|skipped)\b")

# gate_id -> argv (relative paths resolved against the root)
GATES: list[tuple[str, list[str]]] = [
    ("G-CORE-MODULES", ["-m", "pytest", "tests/test_core_modules.py"]),
    ("G-MODES-NOEFFECT", ["-m", "pytest", "tests/test_modes.py"]),
    ("G-KNOW", ["-m", "pytest", "tests/test_gknow.py"]),
    ("G-SP-ISOLATION", ["-m", "pytest", "tests/test_sp_isolation.py"]),
    ("G-GJ03-BRIDGE", ["-m", "pytest", "tests/test_gj03_bridge.py"]),
    ("G-GJ01-CLI", ["-m", "pytest", "tests/e2e/test_gj01_cli.py"]),
    ("G-GJ02-PATCH", ["-m", "pytest", "tests/e2e/test_gj02_patch.py"]),
    ("G-ROLLBACK", ["-m", "pytest", "tests/e2e/test_rollback.py"]),
    ("G-SOURCE-FREEZE", ["tools/verify_source.py", "--verify"]),
    ("G-SEC-SCAN", ["tools/secret_scan.py", "--root", ".", "--json-out", "evidence/security/SECRET_SCAN.json"]),
    ("G-SUITE-FULL", ["-m", "pytest"]),
]


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(root: Path, out_dir: Path, gate_id: str, argv: list[str]) -> dict:
    started = time.time()
    proc = subprocess.run([sys.executable, *argv], cwd=str(root), capture_output=True)
    elapsed = round(time.time() - started, 3)
    out_path = out_dir / f"{gate_id}.stdout.txt"
    err_path = out_dir / f"{gate_id}.stderr.txt"
    out_path.write_bytes(proc.stdout)
    err_path.write_bytes(proc.stderr)
    text = proc.stdout.decode("utf-8", "replace") + proc.stderr.decode("utf-8", "replace")
    counts = {}
    for value, word in PYTEST_LINE.findall(text):
        counts[word] = counts.get(word, 0) + int(value)
    denominator = sum(counts.get(k, 0) for k in ("passed", "failed", "error", "errors"))
    return {
        "gate_id": gate_id,
        "command": " ".join([sys.executable, *argv]),
        "exit": proc.returncode,
        "seconds": elapsed,
        "stdout_sha256": sha_bytes(proc.stdout),
        "stderr_sha256": sha_bytes(proc.stderr),
        "stdout_path": str(out_path),
        "stderr_path": str(err_path),
        "test_counts": counts,
        "failed": counts.get("failed", 0) + counts.get("error", 0) + counts.get("errors", 0),
        "denominator": denominator,
        "tail": "\n".join(text.strip().splitlines()[-6:]),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--json-out", default="evidence/gates/GATES_RAW.json")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    out_dir = root / "evidence" / "gates"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = [run(root, out_dir, gate_id, argv) for gate_id, argv in GATES]
    payload = {
        "schema": "SBL-GATES-RAW/1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "python": sys.executable,
        "gates": rows,
        "summary": {
            "gates": len(rows),
            "exit_zero": sum(1 for r in rows if r["exit"] == 0),
            "failed": [r["gate_id"] for r in rows if r["exit"] != 0],
            "total_tests": sum(r["denominator"] for r in rows),
        },
        "claim_ceiling": "LOCAL_RAW_RECEIPT_ONLY",
    }
    out = root / args.json_out
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=1))
    for row in rows:
        print(f'{row["gate_id"]:18s} exit={row["exit"]} denom={row["denominator"]:3d} {row["tail"].splitlines()[-1][:110] if row["tail"] else ""}')
    # A pytest gate that reports no denominator measured nothing: fail it explicitly.
    zero = [r["gate_id"] for r in rows if "pytest" in r["command"] and r["denominator"] == 0]
    if zero:
        print("ZERO_DENOMINATOR: " + ", ".join(zero))
    return 0 if not payload["summary"]["failed"] and not zero else 1


if __name__ == "__main__":
    raise SystemExit(main())
