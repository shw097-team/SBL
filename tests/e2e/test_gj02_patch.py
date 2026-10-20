"""GJ02: a brownfield patch stays inside its writeset and rolls back cleanly."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from sbl_core.dto import WriteSet
from sbl_core.errors import SBLError
from sbl_core.m04_bridge import GovernedBuildBridge, bind_repo_context

REPO = Path(__file__).resolve().parents[2]
from tests.conftest import scratch_root

FIXTURE_ROOT = Path(scratch_root()) / "gj02"

BASELINE = "def add(a, b):\n    return a - b\n"
FIXED = "def add(a, b):\n    return a + b\n"


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


def run_tests(root: Path) -> bool:
    shutil.rmtree(root / "__pycache__", ignore_errors=True)
    completed = subprocess.run(
        [sys.executable, "-B", "-c", "import calc; assert calc.add(2, 3) == 5"],
        cwd=root,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )
    return completed.returncode == 0


def _purge(path: Path) -> None:
    # ``ignore_errors=True`` instead of ``onexc=``: the latter is 3.12-only while pyproject
    # declares 3.11 as the floor, so the suite has to run on both (VERIFY-03).
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = FIXTURE_ROOT
    _purge(root)
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "mode.agent@example.com")
    _git(root, "config", "user.name", "Mode Agent")
    _git(root, "config", "core.autocrlf", "false")
    (root / "calc.py").write_text(BASELINE, encoding="utf-8", newline="\n")
    (root / "tests_local.py").write_text(
        "def run_tests():\n"
        "    import calc\n"
        "    assert calc.add(2, 3) == 5\n",
        encoding="utf-8",
        newline="\n",
    )
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "baseline")
    return root


def test_bind_repo_context_reads_clean_head(repo: Path) -> None:
    ctx = bind_repo_context(str(repo))

    assert len(ctx.head) == 40
    assert all(ch in "0123456789abcdef" for ch in ctx.head)
    assert ctx.dirty is False
    assert ctx.root == str(repo.resolve())


def test_prepare_issues_order_id(repo: Path) -> None:
    ctx = bind_repo_context(str(repo))

    order = GovernedBuildBridge().prepare(ctx, WriteSet(["calc.py"]))

    assert order.order_id.startswith("O-")
    assert order.head == ctx.head


def test_baseline_is_red(repo: Path) -> None:
    assert run_tests(repo) is False


def test_apply_turns_check_green(repo: Path) -> None:
    ctx = bind_repo_context(str(repo))
    bridge = GovernedBuildBridge()
    order = bridge.prepare(ctx, WriteSet(["calc.py"]))

    bridge.apply(order, "calc.py", FIXED)

    assert (repo / "calc.py").read_text(encoding="utf-8") == FIXED
    assert run_tests(repo) is True


def test_apply_outside_writeset_is_refused(repo: Path) -> None:
    ctx = bind_repo_context(str(repo))
    bridge = GovernedBuildBridge()
    order = bridge.prepare(ctx, WriteSet(["calc.py"]))

    with pytest.raises(SBLError) as excinfo:
        bridge.apply(order, "other.py", "x = 1\n")

    assert excinfo.value.code == "SBL_E_WRITE_OUTSIDE_WRITESET"
    assert not (repo / "other.py").exists()


def test_apply_after_new_commit_is_stale(repo: Path) -> None:
    ctx = bind_repo_context(str(repo))
    bridge = GovernedBuildBridge()
    order = bridge.prepare(ctx, WriteSet(["calc.py"]))

    (repo / "notes.txt").write_text("later work\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "later")

    with pytest.raises(SBLError) as excinfo:
        bridge.apply(order, "calc.py", FIXED)

    assert excinfo.value.code == "SBL_E_STALE_HEAD"


def test_rollback_restores_baseline(repo: Path) -> None:
    baseline_head = _git(repo, "rev-parse", "HEAD")
    ctx = bind_repo_context(str(repo))
    bridge = GovernedBuildBridge()
    order = bridge.prepare(ctx, WriteSet(["calc.py"]))
    bridge.apply(order, "calc.py", FIXED)
    assert run_tests(repo) is True

    _git(repo, "checkout", "--", "calc.py")

    assert (repo / "calc.py").read_bytes() == BASELINE.encode("utf-8")
    assert run_tests(repo) is False
    assert _git(repo, "rev-parse", "HEAD") == baseline_head
