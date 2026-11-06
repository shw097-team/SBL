"""Negative tests for the security boundary of the case runner binding.

These exist because the first version of `case_runner` accepted:
  * absolute / drive / UNC / `..` / symlinked paths outside the subject root,
  * a runner that printed junk and then a `GREEN` (last-line parsing),
  * a `GREEN` from a process that exited non-zero,
  * a restore whose backup no longer held the pre-image.

Each test below is a boundary that must refuse, not warn. The positive controls at the end exist
so that the refusals cannot be satisfied by refusing everything.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pipd_ls_sp.case_runner import (  # noqa: E402
    CaseRunnerRefusal, build_entry, restore, run_entry, verify_entry,
)

ORACLE = "def observe(x):\n    return 'RED' if x else 'GREEN'\n"


def _make_subject(tmp_path: Path, runner_body: str) -> Path:
    root = tmp_path / "subject"
    (root / "tests").mkdir(parents=True)
    (root / "oracle.py").write_text(ORACLE, encoding="utf-8")
    (root / "tests" / "runner.py").write_text(runner_body, encoding="utf-8")
    (root / "tests" / "pos.json").write_text('{"input": 1, "expect": "GREEN"}\n', encoding="utf-8")
    (root / "tests" / "neg.json").write_text('{"input": 0, "expect": "RED"}\n', encoding="utf-8")
    return root


def _entry(root: Path, **over):
    kwargs = dict(root=root, case_id="GJ02", original_requirement_id="REQ-GJ02",
                  original_oracle_id="ORACLE-GJ02", clause_id="CH-41", fuo_id="FUO-GJ02",
                  parent_neg="NEG-GJ02-PARENT", oracle="oracle.py", runner="tests/runner.py",
                  positive_fixture="tests/pos.json", negative_fixture="tests/neg.json",
                  raw_schema="SBL.CaseRunner.WorldRaw@1", evidence_expectation="exit+world_state",
                  checker_role="PROTECTED_CHECKER", runner_owner="SBL-PIPD",
                  applicability={"host": "windows", "profile": "hgk-governed",
                                 "kind": "DEV", "mode": "NATIVE"})
    kwargs.update(over)
    return build_entry(**kwargs)


GREEN_RUNNER = "import json,sys\nprint(json.dumps({'verdict':'GREEN'}))\n"
RED_EXIT1 = "import json,sys\nprint(json.dumps({'verdict':'RED'}))\nsys.exit(1)\n"
GREEN_EXIT1 = "import json,sys\nprint(json.dumps({'verdict':'GREEN'}))\nsys.exit(1)\n"
JUNK_THEN_GREEN = ("import json,sys\nprint('log line that is not json')\n"
                   "print(json.dumps({'verdict':'GREEN'}))\n")
NOTHING = "import sys\nsys.exit(0)\n"


def _refusal(fn, code):
    with pytest.raises(CaseRunnerRefusal) as exc:
        fn()
    assert exc.value.code == code, exc.value.code
    return exc.value


# ---------------------------------------------------------------- path containment
def test_absolute_oracle_path_is_refused(tmp_path):
    root = _make_subject(tmp_path, GREEN_RUNNER)
    outside = tmp_path / "outside_oracle.py"
    outside.write_text(ORACLE, encoding="utf-8")
    with pytest.raises(CaseRunnerRefusal) as exc:
        _entry(root, oracle=str(outside))
    assert exc.value.code == "CASE_RUNNER_PATH_ESCAPE"


def test_drive_letter_path_is_refused(tmp_path):
    root = _make_subject(tmp_path, GREEN_RUNNER)
    with pytest.raises(CaseRunnerRefusal) as exc:
        _entry(root, runner="C:/Windows/System32/drivers/etc/hosts")
    assert exc.value.code == "CASE_RUNNER_PATH_ESCAPE"


def test_unc_path_is_refused(tmp_path):
    root = _make_subject(tmp_path, GREEN_RUNNER)
    with pytest.raises(CaseRunnerRefusal) as exc:
        _entry(root, oracle="//server/share/oracle.py")
    assert exc.value.code == "CASE_RUNNER_PATH_ESCAPE"


def test_parent_traversal_is_refused(tmp_path):
    root = _make_subject(tmp_path, GREEN_RUNNER)
    (tmp_path / "escape.py").write_text(ORACLE, encoding="utf-8")
    with pytest.raises(CaseRunnerRefusal) as exc:
        _entry(root, oracle="../escape.py")
    assert exc.value.code == "CASE_RUNNER_PATH_ESCAPE"


def test_symlink_escape_is_refused(tmp_path):
    root = _make_subject(tmp_path, GREEN_RUNNER)
    outside = tmp_path / "outside.py"
    outside.write_text(ORACLE, encoding="utf-8")
    link = root / "linked.py"
    try:
        os.symlink(outside, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted on this host")
    with pytest.raises(CaseRunnerRefusal) as exc:
        _entry(root, oracle="linked.py")
    assert exc.value.code == "CASE_RUNNER_PATH_ESCAPE"


# ---------------------------------------------------------------- verdict integrity
def test_junk_then_green_is_refused(tmp_path):
    root = _make_subject(tmp_path, JUNK_THEN_GREEN)
    entry = _entry(root)
    _refusal(lambda: run_entry(entry, subject_root=root),
             "CASE_RUNNER_OUTPUT_NOT_SINGLE_JSON")


def test_green_with_nonzero_exit_is_refused(tmp_path):
    root = _make_subject(tmp_path, GREEN_EXIT1)
    entry = _entry(root)
    _refusal(lambda: run_entry(entry, subject_root=root), "CASE_RUNNER_EXIT_VERDICT_CONFLICT")


def test_no_output_is_refused(tmp_path):
    root = _make_subject(tmp_path, NOTHING)
    entry = _entry(root)
    _refusal(lambda: run_entry(entry, subject_root=root), "CASE_RUNNER_EXEC_FAILED")


def test_green_with_zero_exit_is_accepted(tmp_path):
    root = _make_subject(tmp_path, GREEN_RUNNER)
    out = run_entry(_entry(root), subject_root=root)
    assert out["world_state"] == "GREEN" and out["runner"]["exit"] == 0


def test_red_with_nonzero_exit_is_accepted(tmp_path):
    """RED is a legitimate observation, so a non-zero exit must not be treated as GREEN."""
    root = _make_subject(tmp_path, RED_EXIT1)
    out = run_entry(_entry(root), subject_root=root)
    assert out["world_state"] == "RED" and out["runner"]["exit"] == 1


# ---------------------------------------------------------------- restore confinement
def test_restore_with_drifted_backup_is_refused(tmp_path):
    root = _make_subject(tmp_path, GREEN_RUNNER)
    backup = tmp_path / "backup"
    (backup / "tests").mkdir(parents=True)
    (backup / "tests" / "pos.json").write_text('{"input": 9}\n', encoding="utf-8")
    want = hashlib.sha256((root / "tests" / "pos.json").read_bytes()).hexdigest()
    _refusal(lambda: restore(root, {"tests/pos.json": want}, backup), "CASE_RUNNER_BACKUP_DRIFT")


def test_restore_with_traversal_key_is_refused(tmp_path):
    root = _make_subject(tmp_path, GREEN_RUNNER)
    backup = tmp_path / "backup"
    backup.mkdir()
    want = hashlib.sha256(b"x").hexdigest()
    _refusal(lambda: restore(root, {"../escape.json": want}, backup), "CASE_RUNNER_PATH_ESCAPE")


def test_restore_happy_path_is_exact(tmp_path):
    root = _make_subject(tmp_path, GREEN_RUNNER)
    backup = tmp_path / "backup"
    (backup / "tests").mkdir(parents=True)
    original = (root / "tests" / "pos.json").read_bytes()
    (backup / "tests" / "pos.json").write_bytes(original)
    want = hashlib.sha256(original).hexdigest()
    (root / "tests" / "pos.json").write_text('{"input": 7}\n', encoding="utf-8")
    out = restore(root, {"tests/pos.json": want}, backup)
    assert out["exact"] is True
    assert (root / "tests" / "pos.json").read_bytes() == original


# ---------------------------------------------------------------- entry integrity unchanged
def test_verify_still_detects_drift(tmp_path):
    root = _make_subject(tmp_path, GREEN_RUNNER)
    entry = _entry(root)
    (root / "oracle.py").write_text(ORACLE + "# drift\n", encoding="utf-8")
    _refusal(lambda: verify_entry(entry, root), "CASE_RUNNER_ENTRY_DRIFT")
