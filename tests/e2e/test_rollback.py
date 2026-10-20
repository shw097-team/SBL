"""Rollback and refusal invariants across the CLI and the governed bridge."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

import pytest

from sbl_core.dto import WriteSet
from sbl_core.errors import SBLError
from sbl_core.m04_bridge import GovernedBuildBridge, bind_repo_context
from sbl_core.m05_verify import EvidenceVerification

REPO = Path(__file__).resolve().parents[2]
from tests.conftest import scratch_root

_SCRATCH = Path(scratch_root())
TMP_ROOT = _SCRATCH / "rollback"
GJ02_ROOT = _SCRATCH / "gj02"

BASELINE = "def add(a, b):\n    return a - b\n"
FIXED = "def add(a, b):\n    return a + b\n"


def run(args: list[str]) -> tuple[subprocess.CompletedProcess[str], dict]:
    completed = subprocess.run(
        [sys.executable, "-m", "sbl_cli.sbl_todo", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    return completed, json.loads(completed.stdout)


GIT_ENV = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
GIT_ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"})


def _git(root: Path, *args: str) -> str:
    # A hostile inherited environment (GIT_DIR, a broken global config, a read-only HOME) must not
    # be able to break the fixture: otherwise a red result says nothing about the product
    # (independent challenge round 2, ENV-01).
    env = dict(GIT_ENV)
    env["HOME"] = str(root.parent)
    env["USERPROFILE"] = str(root.parent)
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


def _digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    return sha256(path.read_bytes()).hexdigest()


def _purge(path: Path) -> None:
    # ``ignore_errors=True`` instead of ``onexc=``: the latter is 3.12-only while pyproject
    # declares 3.11 as the floor, so the suite has to run on both (VERIFY-03).
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture()
def data_dir(request: pytest.FixtureRequest) -> Path:
    case = request.node.name.replace("test_", "").replace("_", "-")
    path = TMP_ROOT / case
    _purge(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_cli_uninstall_then_reinit_is_empty(data_dir: Path) -> None:
    prefix = ["--data-dir", str(data_dir)]
    run(prefix + ["add", "--title", "unique-rollback-31ab"])
    completed, removed = run(prefix + ["uninstall", "--yes"])
    assert completed.returncode == 0
    assert removed["uninstalled"] is True
    assert not data_dir.exists()

    completed, initialized = run(prefix + ["init"])
    assert completed.returncode == 0
    assert initialized["ok"] is True

    completed, listed = run(prefix + ["list", "--json"])
    assert completed.returncode == 0
    assert listed["count"] == 0


def test_patch_rollback_leaves_no_residue() -> None:
    root = GJ02_ROOT
    _purge(root)
    root.mkdir(parents=True, exist_ok=True)
    try:
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "mode.agent@example.com")
        _git(root, "config", "user.name", "Mode Agent")
        _git(root, "config", "core.autocrlf", "false")
    except AssertionError as exc:  # pragma: no cover - depends on the host, not the code
        pytest.skip(f"ENV: git cannot create a repository in this sandbox: {exc}")
    (root / "calc.py").write_text(BASELINE, encoding="utf-8", newline="\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "baseline")
    baseline_head = _git(root, "rev-parse", "HEAD")

    ctx = bind_repo_context(str(root))
    bridge = GovernedBuildBridge()
    order = bridge.prepare(ctx, WriteSet(["calc.py"]))
    bridge.apply(order, "calc.py", FIXED)
    _git(root, "checkout", "--", "calc.py")

    assert _git(root, "status", "--porcelain") == ""
    assert _git(root, "rev-parse", "HEAD") == baseline_head


def test_refusal_as_dict_is_json_serialisable() -> None:
    verifier = EvidenceVerification()
    verifier.record("G-test", "pytest -q", 0, "1 passed\n", 1)

    with pytest.raises(SBLError) as excinfo:
        verifier.verdict(
            gate_id="G-test",
            maker="mode-a",
            checker="mode-b",
            status="PASS",
            claim_ceiling="LOCAL",
            claim="PRODUCTION",
        )

    payload = excinfo.value.as_dict()
    assert payload["code"] == "SBL_E_CLAIM_CEILING_EXCEEDED"
    assert json.loads(json.dumps(payload))["code"] == payload["code"]


def test_refused_cli_call_does_not_touch_state(data_dir: Path) -> None:
    prefix = ["--data-dir", str(data_dir)]
    completed, _ = run(prefix + ["add", "--title", "unique-guard-77cd"])
    assert completed.returncode == 0
    state = data_dir / "data.json"
    before = _digest(state)
    assert before is not None

    completed, refused = run(prefix + ["add", "--title", "  "])
    assert completed.returncode == 2
    assert refused["code"] == "SBL_E_EMPTY_TITLE"

    completed, refused = run(prefix + ["remove", "--id", "T-missing"])
    assert completed.returncode == 4
    assert refused["code"] == "SBL_E_BAD_STATE"

    assert _digest(state) == before
