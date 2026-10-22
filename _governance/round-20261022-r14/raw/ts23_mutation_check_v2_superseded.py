"""Do the strengthened tests catch a wrong answer for the RIGHT reason?

The first version of this script was itself wrong: it replaced main() with a body that referenced names that did not
exist, so the "caught" results were NameError / missing-fixture failures rather than assertions about output. An
independent reviewer caught that (finding G2), and it was right.

This version mutates the REAL installed source by a single textual substitution, so the mutant stays self-contained and
wrong in exactly one respect, and it records WHICH failure fired. A mutation counts as caught only when the test exits
non-zero AND the failure is an AssertionError. Anything else - an import error, a NameError, a missing file - is recorded
as a false red, which is a defect of the harness, not evidence.

The reviewer's surviving mutation (the agent reporting bytes=0 for non-empty files) is present as case D: it survived
because the test only required a non-negative int. The test now compares exact byte counts for both the two-step and the
--max-steps 1 run, so it must die here.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

RAW = Path(__file__).resolve().parent
SB = RAW / "ts23_sandbox"
VENV = SB / "venv" / "Scripts" / "python.exe"
SP = SB / "venv" / "Lib" / "site-packages"
TESTS = SB / "SBL" / "ts23_tests"

MUTATIONS = [
    ("CLI_TOOL", "ts23_newline", "test_cli.py",
     "'bytes':len(data)", "'bytes':0",
     "census reports bytes=0 for a non-empty file"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py",
     "'sha256':hashlib.sha256(data).hexdigest()", "'sha256':'0'*64",
     "census reports a fake 64-character digest"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py",
     "return headings",
     "return [{'line':1,'level':1,'text':'One'},{'line':3,'level':2,'text':'Two'},{'line':4,'level':3,'text':'Three'}]",
     "headings are fixture constants regardless of the document"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py",
     "'bytes':len(data)", "'bytes':0",
     "agent reports bytes=0 per file (the mutation that survived the first review)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py",
     "'remaining':len(fixed)-len(reviews)", "'remaining':0",
     "agent reports remaining=0 while a file is still queued"),
]

MODULE_FOR_TEST = {"test_cli.py": "ts23_newline", "test_skill.py": "ts23_headings", "test_agent.py": "ts23_review"}


def run_test(test: str) -> dict:
    env = dict(os.environ)
    env.update({"TS23_MODULE": MODULE_FOR_TEST[test],
                "TS23_FIXTURE": str(SB / "SBL" / "ts23_tests" / "headings.md"),
                "TS23_QUEUE": str(SB / "workspace_queue.json")})
    proc = subprocess.run([str(VENV), str(TESTS / test)], capture_output=True, text=True, encoding="utf-8", env=env)
    text = (proc.stderr or "") + (proc.stdout or "")
    if "AssertionError" in text:
        kind = "ASSERTION"
    elif "ModuleNotFoundError" in text or "No module named" in text:
        kind = "IMPORT_ERROR"
    elif "NameError" in text:
        kind = "NAME_ERROR"
    elif "FileNotFoundError" in text:
        kind = "FILE_ERROR"
    else:
        kind = "OTHER_ERROR" if proc.returncode != 0 else "PASSED"
    match = re.search(r"AssertionError: (.+)", text)
    return {"exit": proc.returncode, "failure_kind": kind,
            "assertion_message": match.group(1).strip()[:160] if match else "",
            "tail": text[-320:]}


def main() -> int:
    results = []
    for kind, module, test, original_snippet, mutant_snippet, description in MUTATIONS:
        target = SP / module / "__init__.py"
        original = target.read_bytes()
        digest = hashlib.sha256(original).hexdigest()
        text = original.decode("utf-8")
        if original_snippet not in text:
            results.append({"kind": kind, "mutation": description, "applied": False, "caught": False,
                            "note": "snippet not present; mutation not applied"})
            continue
        try:
            target.write_text(text.replace(original_snippet, mutant_snippet, 1), encoding="utf-8")
            outcome = run_test(test)
        finally:
            target.write_bytes(original)
        restored = hashlib.sha256(target.read_bytes()).hexdigest() == digest
        caught = outcome["exit"] != 0 and outcome["failure_kind"] == "ASSERTION"
        results.append({"kind": kind, "mutation": description, "applied": True,
                        "test_exit": outcome["exit"], "failure_kind": outcome["failure_kind"],
                        "assertion_message": outcome["assertion_message"], "caught": caught,
                        "false_red": outcome["exit"] != 0 and outcome["failure_kind"] != "ASSERTION",
                        "restored_byte_identical": restored, "tail": outcome["tail"]})
    baseline = {test: run_test(test) for test in MODULE_FOR_TEST}
    doc = {"schema": "SBL-R14-TS23-MUTATION-CHECK/2",
           "answers_review": "ts23_review2.json G2 - the first harness produced false reds",
           "method": ("one textual substitution in the INSTALLED module, so the mutant stays self-contained and wrong in "
                      "exactly one respect; caught requires a non-zero exit AND an AssertionError"),
           "results": results,
           "unmutated_baseline": baseline,
           "all_caught": all(r.get("caught") for r in results),
           "no_false_reds": all(not r.get("false_red") for r in results),
           "all_restored": all(r.get("restored_byte_identical") for r in results),
           "baseline_all_pass": all(v["exit"] == 0 for v in baseline.values())}
    (RAW / "ts23_test_strength.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    for r in results:
        print(f"{r['kind']:12} caught={str(r.get('caught')):5} kind={r.get('failure_kind','-'):12} "
              f"restored={r.get('restored_byte_identical','-')} {r['mutation']}")
    print("all_caught:", doc["all_caught"], "| no_false_reds:", doc["no_false_reds"],
          "| all_restored:", doc["all_restored"], "| baseline_all_pass:", doc["baseline_all_pass"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
