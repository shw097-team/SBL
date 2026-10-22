"""Do the tests catch a wrong answer for the RIGHT reason?

Four earlier versions of this file were wrong in ways reviewers had to point out:
  v1 replaced main() with a body referencing undefined names, so "caught" meant NameError.
  v2 mutated real source but counted any AssertionError as a catch - a crashing mutant makes the returncode guard raise.
  v3-v6 kept improving, and each round reviewers found another shape the fixtures did not contain.
  v7 (this file) supersedes the string-patched versions: the three implementations now live in ts23_src/, so the snippets
  below are plain substrings of real files rather than escapes inside a generator.

Rules that make a "caught" honest:
  - the mutation is one textual substitution in the INSTALLED module, so the mutant stays self-contained;
  - the mutated program is probed for EVERY invocation the tests use, and must still exit 0 with JSON, otherwise the
    mutation is recorded as crash_not_evidence, never as a catch;
  - the failing test must report an AssertionError whose message carries no exception class;
  - __pycache__ is purged before and after, with a failure to purge raising rather than being ignored;
  - the script exits non-zero unless every flag holds, so a failing receipt cannot look like a passing one.
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
FIXTURE = TESTS / "headings.md"
QUEUE = SB / "workspace_queue.json"
EMPTY_QUEUE = SB / "ts23_empty_queue.json"

BS = "\\"
TERM = 'terminators = data.count(b"' + BS + 'n") + data.count(b"' + BS + 'r") - data.count(b"' + BS + 'r' + BS + 'n")'
HEADING = 'HEADING = re.compile(r"^(#{1,6})[ ' + BS + 't]+(.*)$")'
CLOSING = 'CLOSING = re.compile(r"[ ' + BS + 't]+#+$")'
BODY = '        body = CLOSING.sub("", match.group(2)).strip()'
ERR = '        sys.stderr.write("ERR_INPUT: " + str(exc) + "' + BS + 'n")'
NOT_LIST = ('        if not isinstance(queue, list):\n'
            '            raise ValueError("queue must be a JSON array of paths")\n')

# (kind, module, test file, original, mutant, description, provenance)
MUTATIONS = [
    ("CLI_TOOL", "ts23_newline", "test_cli.py", "data = path.read_bytes()",
     'data = Path(path).read_text(encoding="utf-8").encode("utf-8")',
     "binary input is decoded as UTF-8", "review 7 (N01)"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py", ERR + "\n        return 2",
     ERR + "\n        return 7", "an input error exits 7 instead of 2", "review 7 (N02)"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py", "    except OSError as exc:\n" + ERR,
     "    except OSError as exc:\n        print('partial')\n" + ERR,
     "an input error also writes to stdout", "review 7 (N03)"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py", '"bytes": len(data)', '"bytes": 0',
     "census reports bytes=0 for a non-empty file", "review 2 (G1)"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py", 'hashlib.sha256(data).hexdigest()', "'0' * 64",
     "census reports a fake digest", "maker"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py", TERM, 'terminators = data.count(b"' + BS + 'n")',
     "a lone CR is not counted as a terminator", "review 5 (LONE_CR)"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py", TERM,
     TERM + ' + (0 if data.endswith((b"' + BS + 'n", b"' + BS + 'r")) else 1)',
     "an unterminated final line is counted", "review 5 (UNTERMINATED)"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py", TERM, TERM + ' - data.count(b"' + BS + 'n' + BS + 'r")',
     "an LF+CR pair is merged into one terminator", "review 6 (LFCR)"),
    ("CLI_TOOL", "ts23_newline", "test_cli.py", TERM,
     'terminators = 0',
     "a file of only terminators reports zero", "review 6 (TERMINATORS_ONLY)"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", HEADING, HEADING.replace("[ " + BS + "t]+", " +"),
     "only a space separates the hashes from the text", "review 7 (N04)"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", HEADING,
     'HEADING = re.compile(r"^(#{1,5})[ ' + BS + 't]+(.*)$")',
     "level-six headings are dropped", "review 4 (LEVEL6)"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", BODY,
     '        body = " ".join(CLOSING.sub("", match.group(2)).split())',
     "internal whitespace is collapsed", "review 7 (N07)"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", BODY,
     '        body = __import__("unicodedata").normalize("NFKD", CLOSING.sub("", match.group(2)).strip())',
     "heading text is NFKD-normalised", "review 7 (N19)"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", BODY,
     '        body = re.sub(r"#+$", "", match.group(2)).strip()',
     "a trailing hash is stripped without a closing sequence", "review 6 (CONTENT_HASH)"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", "        if not body:\n            continue\n",
     "", "an empty heading text is accepted", "review 7 (G07)"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", 'str(args.path.resolve())', '"wrong"',
     "headings come with a wrong path", "review 3 (N3)"),
    ("AGENT_SKILL", "ts23_headings", "test_skill.py", "    headings = []",
     "    headings = []\n    return [{'line': 1, 'level': 1, 'text': 'One'}]",
     "headings are constants regardless of the document", "review 1"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py", '"bytes": len(data)', '"bytes": 0',
     "agent reports bytes=0 per file", "review 2 (G1)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py", 'hashlib.sha256(data).hexdigest()', "'0' * 64",
     "agent reports fake digests", "maker"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py", '"path": str(path),', '"path": "wrong",',
     "a wrong path in the review entry", "review 3 (N4)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py", '"remaining": len(fixed) - len(reviewed)',
     '"remaining": 0', "remaining is always zero", "maker"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py", '"remaining": len(fixed) - len(reviewed)',
     '"remaining": 999', "remaining is 999", "review 3 (N7)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py", "    budget_hit = len(reviewed) < len(fixed)",
     "    budget_hit = True", "a non-empty exhausted queue reports BUDGET", "review 7 (N14)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py", "    budget_hit = len(reviewed) < len(fixed)",
     "    budget_hit = False", "a budget-limited run reports QUEUE_EXHAUSTED", "maker"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py",
     'queue = json.loads(args.queue.read_text(encoding="utf-8"))', 'queue = json.loads("[]")',
     "the queue file is ignored and an empty list is used", "review 7 (N16)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py", "        data = Path(path).read_bytes()",
     "        try:\n            data = Path(path).read_bytes()\n        except OSError:\n            continue",
     "an unreadable entry is silently skipped", "review 7 (N15)"),
    ("SIMPLE_AGENT", "ts23_review", "test_agent.py", ERR + "\n        return 2",
     ERR + "\n        return 7", "a queue input error exits 7", "review 7 (N17)"),
]

MODULE_FOR_TEST = {"test_cli.py": "ts23_newline", "test_skill.py": "ts23_headings", "test_agent.py": "ts23_review"}
PROBE_ARGS = {
    "ts23_newline": [[str(FIXTURE)]],
    "ts23_headings": [[str(FIXTURE)]],
    "ts23_review": [[str(QUEUE)], [str(QUEUE), "--max-steps", "1"], [str(EMPTY_QUEUE)]],
}


def purge(module: str) -> None:
    import shutil
    for cache in (SP / module).rglob("__pycache__"):
        shutil.rmtree(cache)
    leftovers = list((SP / module).rglob("__pycache__"))
    assert not leftovers, f"bytecode cache could not be removed: {leftovers}"


def env() -> dict:
    e = dict(os.environ)
    e.update({"TS23_FIXTURE": str(FIXTURE), "TS23_QUEUE": str(QUEUE), "PYTHONDONTWRITEBYTECODE": "1"})
    return e


def probe(module: str) -> dict:
    e = env()
    e["TS23_MODULE"] = module
    runs = []
    for args in PROBE_ARGS[module]:
        proc = subprocess.run([str(VENV), "-m", module, *args], capture_output=True, text=True,
                              encoding="utf-8", env=e, cwd=str(SB))
        try:
            json.loads(proc.stdout)
            answered = True
        except Exception:
            answered = False
        runs.append({"args": args, "exit": proc.returncode, "answered": answered,
                     "tail": (proc.stderr or "")[-160:]})
    return {"runs": runs, "ok": all(r["exit"] == 0 and r["answered"] for r in runs)}


def run_test(test: str) -> dict:
    e = env()
    e["TS23_MODULE"] = MODULE_FOR_TEST[test]
    proc = subprocess.run([str(VENV), str(TESTS / test)], capture_output=True, text=True,
                          encoding="utf-8", env=e, cwd=str(SB))
    text = (proc.stderr or "") + (proc.stdout or "")
    match = re.search(r"AssertionError: (.+)", text)
    return {"exit": proc.returncode, "assertion": "AssertionError" in text,
            "message": match.group(1).strip()[:200] if match else "", "tail": text[-300:]}


def main() -> int:
    results = []
    for kind, module, test, original, mutant, description, provenance in MUTATIONS:
        target = SP / module / "__init__.py"
        if not target.exists():
            results.append({"kind": kind, "mutation": description, "provenance": provenance,
                            "applied": False, "caught": False, "note": "module not installed"})
            continue
        base = target.read_bytes()
        digest = hashlib.sha256(base).hexdigest()
        text = base.decode("utf-8")
        if original not in text:
            results.append({"kind": kind, "mutation": description, "provenance": provenance,
                            "applied": False, "caught": False, "note": "snippet absent from the installed source"})
            continue
        purge(module)
        try:
            target.write_text(text.replace(original, mutant, 1), encoding="utf-8")
            probed = probe(module)
            outcome = run_test(test)
        finally:
            target.write_bytes(base)
            purge(module)
        message = outcome["message"]
        crash_shaped = bool(re.search(r"(Traceback \(most recent call last\)|\w*Error|\w*Exception)", message))
        caught = bool(probed["ok"] and outcome["exit"] != 0 and outcome["assertion"] and not crash_shaped)
        results.append({"kind": kind, "mutation": description, "provenance": provenance, "applied": True,
                        "mutant_ran_and_answered": probed["ok"], "probe": probed,
                        "test_exit": outcome["exit"], "assertion_message": message,
                        "caught": caught,
                        "crash_not_evidence": not probed["ok"],
                        "false_red": (not probed["ok"]) and outcome["exit"] != 0,
                        "restored_byte_identical": hashlib.sha256(target.read_bytes()).hexdigest() == digest})
    baseline = {test: run_test(test) for test in MODULE_FOR_TEST}
    flags = {"all_caught": all(r.get("caught") for r in results if r.get("applied")),
             "no_false_reds": all(not r.get("false_red") for r in results if r.get("applied")),
             "all_applied": all(r.get("applied") for r in results),
             "all_restored": all(r.get("restored_byte_identical") for r in results if r.get("applied")),
             "baseline_all_pass": all(v["exit"] == 0 for v in baseline.values())}
    doc = {"schema": "SBL-R14-TS23-MUTATION-CHECK/7",
           "answers_review": "ts23_review7.json - 14 in-scope survivors, C03/C04 false catches, G06 coverage overclaim",
           "method": "one textual substitution in the INSTALLED module; probe every invocation; cache purged; crash never counts",
           "results": results, "unmutated_baseline": baseline, "flags": flags,
           "exit_code_policy": "non-zero unless every flag is true"}
    (RAW / "ts23_test_strength.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    for r in results:
        state = "CAUGHT" if r.get("caught") else ("absent" if not r.get("applied") else "SURVIVED")
        print(f"{r['kind']:12} {state:9} restored={r.get('restored_byte_identical','-')} {r['mutation']}  [{r['provenance']}]")
    for name, value in flags.items():
        print(f"  {name}: {value}")
    return 0 if all(flags.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
