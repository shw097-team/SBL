#!/usr/bin/env python3
"""R5 TS05 — produce the uninstall-boundary negative matrix from REAL pytest runs.

Two halves, both required:

* the positive/negative cases, run in the candidate worktree;
* the **injection control**: the same negative cases run against the pre-repair implementation
  (`68c276d`, i.e. the bytes the R5 reviewer flagged) in a throwaway copy. If the old bytes also
  passed those cases the tests would be vacuous, so this half is what makes the matrix evidence
  rather than a claim.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WORKTREE = Path(r"C:\Projects\_sbl_r4\c3v2")
BASE_SHA = "68c276d354dae2b1bc2baef290f89e539fb34751"
OUT = Path(__file__).with_name("NEGATIVE_MATRIX.json")
PY = sys.executable

CASES = [
    ("parent_escape_dotdot", "test_uninstall_refuses_a_parent_escape_key"),
    ("absolute_path_key", "test_uninstall_refuses_an_absolute_manifest_key"),
    ("key_outside_allowlist", "test_uninstall_refuses_a_key_outside_the_installer_allowlist"),
    ("digest_changed_since_install", "test_uninstall_refuses_when_a_file_changed_since_install"),
    ("malformed_files_object", "test_uninstall_refuses_a_malformed_files_object"),
    ("symlinked_file_in_allowlist", "test_uninstall_refuses_a_symlinked_file"),
    ("symlinked_manifest", "test_uninstall_refuses_a_symlinked_manifest"),
    ("junction_parent_escape", "test_uninstall_refuses_a_junction_parent"),
    ("junction_cleanup_escape", "test_uninstall_never_prunes_empty_directories"),
    ("backslash_key_normalisation", "test_uninstall_accepts_a_backslash_manifest_key"),
    ("legit_roundtrip_removes_exactly", "test_uninstall_removes_exactly_the_installed_paths"),
    ("legit_roundtrip_install_doctor_uninstall", "test_install_doctor_and_uninstall_round_trip"),
    ("foreign_files_still_refused", "test_uninstall_refuses_a_directory_with_foreign_files"),
]


def pytest(cwd: Path, expr: str) -> dict:
    proc = subprocess.run(
        [PY, "-m", "pytest", "tests/test_sbl_harness.py", "-q", "--no-header", "-p", "no:cacheprovider", "-rs", "-k", expr],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        errors="replace",
    )
    tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
    skipped = "SKIPPED" in (proc.stdout or "")
    return {"rc": proc.returncode, "summary": tail[0][:200], "skipped": skipped}


def main() -> int:
    matrix: dict = {
        "round": "SBL-R5-20261021-C5",
        "task": "TS05",
        "finding": "F-R5-HARNESS-UNINSTALL-TRAVERSAL-001",
        "candidate_worktree": str(WORKTREE),
        "pre_repair_sha": BASE_SHA,
        "positive_and_negative": [],
        "injection_control": [],
    }

    for case_id, expr in CASES:
        result = pytest(WORKTREE, expr)
        matrix["positive_and_negative"].append({"case": case_id, "test": expr, **result})

    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "pre_repair"
        shutil.copytree(
            WORKTREE,
            copy,
            ignore=shutil.ignore_patterns(".git", "dist", "build", "*.egg-info", "__pycache__", ".pytest_cache"),
        )
        old = subprocess.run(
            ["git", "show", f"{BASE_SHA}:sbl_harness/__init__.py"],
            cwd=str(WORKTREE),
            capture_output=True,
            text=True,
            errors="replace",
        )
        if old.returncode != 0:
            matrix["injection_control"].append({"error": "could not read the pre-repair blob", "detail": old.stderr[:300]})
        else:
            (copy / "sbl_harness" / "__init__.py").write_text(old.stdout, encoding="utf-8")
            for case_id in ("parent_escape_dotdot", "absolute_path_key", "junction_cleanup_escape", "key_outside_allowlist"):
                expr = dict(CASES)[case_id]
                matrix["injection_control"].append({"case": case_id, "test": expr, **pytest(copy, expr)})

    pos_ok = all(row["rc"] == 0 for row in matrix["positive_and_negative"])
    skipped = [row["case"] for row in matrix["positive_and_negative"] if row["skipped"]]
    # The control MUST fail on the pre-repair bytes; a green control means the tests prove nothing.
    inj_ok = bool(matrix["injection_control"]) and all(row.get("rc") == 1 for row in matrix["injection_control"])
    matrix["verdict"] = {
        "all_cases_green": pos_ok,
        "skipped_on_this_host": skipped,
        "pre_repair_bytes_fail_the_escapes": inj_ok,
        "finding_closed_locally": pos_ok and inj_ok,
        "note": (
            "a skipped case is not a PASS: the two symlink cases cannot run on a Windows host "
            "without Developer Mode and are expected to run on the ubuntu CI leg"
            if skipped
            else "no case skipped"
        ),
    }
    OUT.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(matrix["verdict"], indent=2))
    return 0 if pos_ok and inj_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
