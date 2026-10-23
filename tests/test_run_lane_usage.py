"""run_lane must fail as a usage error, not as a stack trace, when the role key is wrong.

Measured: `--role VERIFY_SECURITY` raised KeyError('VERIFY_SECURITY') because the mandate key is `VERIFY` while the
lane it dispatches to is named VERIFY_SECURITY. That reads like a broken lane and cost a dispatch cycle.
"""
from __future__ import annotations

import subprocess
import sys
import os

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
TOOL = os.path.join(R, "tools", "run_lane.py")


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
