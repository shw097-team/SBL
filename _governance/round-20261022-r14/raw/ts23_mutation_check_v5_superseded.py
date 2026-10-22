"""Do the tests catch a wrong answer for the RIGHT reason - and does this harness say so honestly?

Version history, because each version was wrong in a way a reviewer had to point out:
  v1  replaced main() with a body referencing undefined names, so "caught" meant NameError. False red. (review 2, G2)
  v2  mutated real source but still classified any AssertionError as caught - a crashing mutant makes the test's
      "returncode == 0" guard fail with an AssertionError, so a crash still read as behavioural detection.
      It also always exited 0, so a failing receipt could not fail a pipeline. (review 3, G2)
  v3  (this file) probes the mutated program FIRST: if it crashes or emits no JSON, the mutation is recorded as CRASH,
      never as caught. `caught` now requires the program to run and answer, the test to fail, and the failure to be an
      AssertionError. The script exits non-zero whenever any flag is false.

It also carries every mutation the three reviewers used, including the five that survived review 3 (N3, N4, N5, N7, N8),
so the survivors cannot quietly come back.
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
FIXTURE = SB / "SBL" / "ts23_tests" / "headings.md"
QUEUE = SB / "workspace_queue.json"

MUTATIONS = [
    # (kind, module, test, original, mutant, description, reviewer who used it)
    ("CLI_TOOL", "ts23_newline", "test_cli.py", "'bytes':len(data)", "'bytes':0",
     "census reports bytes=0 for a non-empty file", "review 2 (survived), review 3 (G1)"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py",
     "'sha256':hashlib.sha256(data).hexdigest()", "'sha256':'0'*64",
     "census reports a fake 64-character digest", "maker"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", "return headings",
     "return [{'line':1,'level':1,'text':'One'},{'line':3,'level':2,'text':'Two'},{'line':4,'level':3,'text':'Three'}]",
     "headings are fixture constants regardless of the document", "review 1"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", "'path':str(args.path.resolve())", "'path':'wrong'",
     "correct headings but a wrong path", "review 3 (N3)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py", "'bytes':len(data)", "'bytes':0",
     "agent reports bytes=0 per file", "review 2 (survived)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py",
     "'remaining':len(fixed)-len(reviews)", "'remaining':0",
     "agent reports remaining=0 while a file is still queued", "maker"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py", "'path':path", "'path':'wrong'",
     "correct byte counts but a wrong path in the one-step run", "review 3 (N4)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py",
     "'sha256':hashlib.sha256(data).hexdigest()", "'sha256':'0'*64",
     "one-step run reports a fake digest", "review 3 (N5)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py",
     "'remaining':len(fixed)-len(reviews)", "'remaining':999",
     "one-step run reports remaining=999", "review 3 (N7)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py",
     "'halt_reason':'BUDGET' if len(reviews)<len(fixed) else 'QUEUE_EXHAUSTED'",
     "'halt_reason':'QUEUE_EXHAUSTED'",
     "one-step run claims the queue is exhausted", "review 3 (N8)"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", "(#{1,6})", "(#{1,5})",
     "level-six headings are silently dropped", "review 4 (LEVEL6_COVERAGE)"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py", "data.count(b'\\n')", "data.count(b'\\n')+data.count(b'\\r')",
     "CRLF is counted twice", "review 4 (CRLF_COVERAGE)"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py", "data.count(b'\\n')+data.count(b'\\r')-data.count(b'\\r\\n')", "data.count(b'\\n')",
     "a lone CR is not counted as a line terminator", "review 5 (LONE_CR_IGNORED_BY_SUITE)"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py", "data.count(b'\\n')+data.count(b'\\r')-data.count(b'\\r\\n')", "data.count(b'\\n')+data.count(b'\\r')-data.count(b'\\r\\n')+(0 if data.endswith((b'\\n',b'\\r')) else 1)",
     "an unterminated final line is counted as a newline", "review 5 (UNTERMINATED_LINE_COUNTED_AS_NEWLINE)"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", "re.sub(r'[ \t]+#+$','',match[2]).strip()", 'match[2]',
     "the ATX closing sequence stays in the heading text", "review 5 (ATX_CLOSING_SEQUENCE_UNSPECIFIED)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py",
     "'halt_reason':'BUDGET' if len(reviews)<len(fixed) else 'QUEUE_EXHAUSTED'", "'halt_reason':'BUDGET'",
     "an empty queue is reported as budget-limited", "review 5 (EMPTY_QUEUE_REPORTS_BUDGET)"),
]

MODULE_FOR_TEST = {"test_cli.py": "ts23_newline", "test_skill.py": "ts23_headings", "test_agent.py": "ts23_review"}
PROBE_ARGS = {"ts23_newline": [str(FIXTURE)], "ts23_headings": [str(FIXTURE)], "ts23_review": [str(QUEUE)]}


def _purge_cache(module: str) -> None:
    """A same-size edit within one mtime tick can be masked by a stale .pyc. Round 4 (CACHE_BINDING) showed it."""
    import shutil
    for cache in (SP / module).rglob("__pycache__"):
        shutil.rmtree(cache)          # no ignore_errors: a failed purge must be visible
    leftovers = list((SP / module).rglob("__pycache__"))
    assert not leftovers, f"bytecode cache could not be removed: {leftovers}"


def _env() -> dict:
    env = dict(os.environ)
    env.update({"TS23_FIXTURE": str(FIXTURE), "TS23_QUEUE": str(QUEUE),
                "PYTHONDONTWRITEBYTECODE": "1"})
    return env


def probe(module: str) -> dict:
    """Run the mutated program directly: did it run and answer at all?"""
    env = _env()
    env["TS23_MODULE"] = module
    proc = subprocess.run([str(VENV), "-m", module, *PROBE_ARGS[module]],
                          capture_output=True, text=True, encoding="utf-8", env=env,
                          cwd=str(SB))
    try:
        json.loads(proc.stdout)
        answered = True
    except Exception:
        answered = False
    return {"exit": proc.returncode, "answered_with_json": answered, "tail": (proc.stderr or "")[-200:]}


def run_test(test: str) -> dict:
    env = _env()
    env["TS23_MODULE"] = MODULE_FOR_TEST[test]
    proc = subprocess.run([str(VENV), str(TESTS / test)], capture_output=True, text=True, encoding="utf-8",
                          env=env, cwd=str(SB))
    text = (proc.stderr or "") + (proc.stdout or "")
    match = re.search(r"AssertionError: (.+)", text)
    return {"exit": proc.returncode, "has_assertion": "AssertionError" in text,
            "assertion_message": match.group(1).strip()[:160] if match else "", "tail": text[-320:]}


def main() -> int:
    results = []
    for kind, module, test, original_snippet, mutant_snippet, description, provenance in MUTATIONS:
        target = SP / module / "__init__.py"
        original = target.read_bytes()
        digest = hashlib.sha256(original).hexdigest()
        text = original.decode("utf-8")
        if original_snippet not in text:
            results.append({"kind": kind, "mutation": description, "provenance": provenance,
                            "applied": False, "caught": False, "note": "snippet absent; not applied"})
            continue
        _purge_cache(module)
        try:
            target.write_text(text.replace(original_snippet, mutant_snippet, 1), encoding="utf-8")
            probe_result = probe(module)
            test_result = run_test(test)
        finally:
            target.write_bytes(original)
            _purge_cache(module)
        restored = hashlib.sha256(target.read_bytes()).hexdigest() == digest
        ran_and_answered = probe_result["exit"] == 0 and probe_result["answered_with_json"]
        message = test_result["assertion_message"]
        crash_shaped = bool(re.search(r"(Traceback \(most recent call last\)|\w*Error|\w*Exception)", message))
        caught = (ran_and_answered and test_result["exit"] != 0
                  and test_result["has_assertion"] and not crash_shaped)
        results.append({
            "kind": kind, "mutation": description, "provenance": provenance, "applied": True,
            "mutant_ran_and_answered": ran_and_answered, "probe": probe_result,
            "test_exit": test_result["exit"], "assertion_message": test_result["assertion_message"],
            "caught": caught, "crash_shaped_assertion": crash_shaped,
            "false_red": (not ran_and_answered) and test_result["exit"] != 0,
            "crash_not_evidence": (not ran_and_answered),
            "restored_byte_identical": restored, "tail": test_result["tail"]})
    baseline = {test: run_test(test) for test in MODULE_FOR_TEST}
    flags = {
        "all_caught": all(r.get("caught") for r in results),
        "no_false_reds": all(not r.get("false_red") for r in results),
        "all_restored": all(r.get("restored_byte_identical") for r in results),
        "baseline_all_pass": all(v["exit"] == 0 for v in baseline.values()),
    }
    doc = {"schema": "SBL-R14-TS23-MUTATION-CHECK/3",
           "answers_review": "ts23_review3.json - survivors N3/N4/N5/N7/N8, G2 crash-read-as-caught, exit 0 on failure",
           "method": ("one textual substitution in the INSTALLED module; the mutant is probed directly first, and a "
                      "mutant that crashes or emits no JSON is recorded as crash_not_evidence rather than as a catch"),
           "results": results, "unmutated_baseline": baseline, "flags": flags,
           "exit_code_policy": "non-zero unless every flag is true"}
    (RAW / "ts23_test_strength.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    for r in results:
        print(f"{r['kind']:12} caught={str(r.get('caught')):5} ran={str(r.get('mutant_ran_and_answered')):5} "
              f"restored={r.get('restored_byte_identical','-')} {r['mutation']}")
    for name, value in flags.items():
        print(f"  {name}: {value}")
    return 0 if all(flags.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
