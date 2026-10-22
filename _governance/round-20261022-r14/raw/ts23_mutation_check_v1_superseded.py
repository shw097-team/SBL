"""Do the strengthened tests actually catch a broken implementation?

The independent reviewer's check 2 failed because the original tests also passed against deliberately broken code. This
script re-runs that experiment on the strengthened suite: for each program it mutates the INSTALLED module in place,
runs the installed behavioural test, records whether the test failed, and restores the file byte-for-byte.

A mutation that survives is a coverage hole, and it is reported as one instead of being quietly skipped.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

RAW = Path(__file__).resolve().parent
SB = RAW / "ts23_sandbox"
VENV = SB / "venv" / "Scripts" / "python.exe"
SP = SB / "venv" / "Lib" / "site-packages"
TESTS = SB / "SBL" / "ts23_tests"

MUTATIONS = [
    ("CLI_TOOL", "ts23_newline", "test_cli.py",
     "return {'path': str(p), 'bytes': 0, 'newlines': 0, 'sha256': hashlib.sha256(b'').hexdigest()}",
     "census reports zero for a non-empty file"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py",
     "return {'path': str(p), 'headings': [{'line':1,'level':1,'text':'One'},{'line':3,'level':2,'text':'Two'},{'line':4,'level':3,'text':'Three'}]}",
     "headings are fixture constants regardless of input"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py",
     "return {'steps': 2, 'remaining': 1, 'halt_reason': 'WRONG', 'reviews': [{'path': str(q), 'bytes': -999, 'sha256': 'x'*64} for q in queue[:2]]}",
     "halt_reason wrong and a negative byte count"),
]


def run(test: str) -> dict:
    env = dict(os.environ)
    env.update({"TS23_MODULE": "", "TS23_FIXTURE": str(RAW / "ts23_sandbox/fixture.md"),
                "TS23_QUEUE": str(SB / "workspace_queue.json")})
    env["TS23_MODULE"] = {"test_cli.py": "ts23_newline", "test_skill.py": "ts23_headings",
                          "test_agent.py": "ts23_review"}[test]
    proc = subprocess.run([str(VENV), str(TESTS / test)], capture_output=True, text=True, encoding="utf-8", env=env)
    return {"exit": proc.returncode, "tail": (proc.stderr or proc.stdout or "")[-400:]}


def main() -> int:
    results = []
    for kind, module, test, mutant_body, description in MUTATIONS:
        target = SP / module / "__init__.py"
        original = target.read_bytes()
        digest = hashlib.sha256(original).hexdigest()
        try:
            text = original.decode("utf-8")
            marker = "def main("
            cut = text.find(marker)
            head = text[:cut] if cut != -1 else text
            mutant = head + "def main(argv=None):\n    " + mutant_body + "\n"
            target.write_text(mutant, encoding="utf-8")
            outcome = run(test)
        finally:
            target.write_bytes(original)
        restored = hashlib.sha256(target.read_bytes()).hexdigest() == digest
        results.append({"kind": kind, "mutation": description, "test": test, "test_exit": outcome["exit"],
                        "caught": outcome["exit"] != 0, "restored_byte_identical": restored,
                        "tail": outcome["tail"]})
    doc = {"schema": "SBL-R14-TS23-MUTATION-CHECK/1",
           "note": ("Each mutation replaces the installed module's main() with a wrong implementation, runs the installed "
                    "behavioural test, then restores the file and verifies the digest. A surviving mutation is a "
                    "coverage hole and is reported as caught=false."),
           "results": results,
           "all_caught": all(r["caught"] for r in results),
           "all_restored": all(r["restored_byte_identical"] for r in results)}
    (RAW / "ts23_test_strength.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    for r in results:
        print(f"{r['kind']:12} caught={r['caught']} exit={r['test_exit']} restored={r['restored_byte_identical']}  {r['mutation']}")
    print("all_caught:", doc["all_caught"], "| all_restored:", doc["all_restored"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
