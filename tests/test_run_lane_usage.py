"""run_lane must fail as a usage error, not as a stack trace, when the role key is wrong.

Measured: `--role VERIFY_SECURITY` raised KeyError('VERIFY_SECURITY') because the mandate key is `VERIFY` while the
lane it dispatches to is named VERIFY_SECURITY. That reads like a broken lane and cost a dispatch cycle.

Also measured: DEN-C13_narrow and DEN-C14_narrow emitted the nonce only inside an item.completed/command_execution
event - the model echoed it in a shell command - so the strict detector (correctly) refused the receipt. The
instruction, not the detector, needed fixing: an echo replaying the brief proves nothing.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import os

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
TOOL = os.path.join(R, "tools", "run_lane.py")


def _mod():
    spec = importlib.util.spec_from_file_location("run_lane", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_header_forbids_an_echo_and_demands_a_sentence():
    head = _mod().stamp_header("EXEC-TEST-123")
    assert head.startswith("NONCE: EXEC-TEST-123")
    low = head.lower()
    assert "do not produce the token with a shell command" in low
    assert "echo" in low and "heredoc" in low
    assert "one sentence in your own words" in low
    assert "naming the exact file" in low


def test_the_header_keeps_the_no_subagent_rule():
    low = _mod().stamp_header("X").lower()
    assert "do not dispatch, spawn or poll another lane or agent" in low


def _run(args):
    return subprocess.run([sys.executable, TOOL] + args, cwd=R, capture_output=True, text=True, timeout=120)


def test_the_lane_name_is_not_a_accepted_role_key():
    p = _run(["--role", "VERIFY_SECURITY", "--brief", "workers/challenge_brief/CHALLENGE_R153_BATCH2.md"])
    assert p.returncode == 2, "a wrong role must be a usage error, not a dispatch attempt"
    assert "UNKNOWN_ROLE" in p.stdout
    assert "VERIFY" in p.stdout, "the message must name the role keys that do exist"
    assert "Traceback" not in (p.stdout + p.stderr)


def test_missing_brief_is_reported_before_any_dispatch():
    p = _run(["--role", "VERIFY", "--brief", "workers/challenge_brief/does_not_exist.md"])
    assert p.returncode == 2 and "BRIEF_MISSING" in p.stdout
    assert "Traceback" not in (p.stdout + p.stderr)
