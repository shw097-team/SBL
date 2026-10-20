"""GJ01: the ``sbl-todo`` CLI keeps state across restarts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[2]
from tests.conftest import scratch_root

TMP_ROOT = Path(scratch_root()) / "gj01"


def run(args: list[str]) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    completed = subprocess.run(
        [sys.executable, "-m", "sbl_cli.sbl_todo", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    return completed, json.loads(completed.stdout)


@pytest.fixture()
def data_dir(request: pytest.FixtureRequest) -> Path:
    case = request.node.name.replace("test_", "").replace("_", "-")
    path = TMP_ROOT / case
    if path.exists():
        for child in sorted(path.rglob("*"), reverse=True):
            child.unlink() if child.is_file() else child.rmdir()
        path.rmdir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _args(data_dir: Path, *rest: str) -> list[str]:
    return ["--data-dir", str(data_dir), *rest]


def test_init_and_add_create_open_item(data_dir: Path) -> None:
    completed, payload = run(_args(data_dir, "init"))
    assert completed.returncode == 0
    assert payload["ok"] is True
    assert Path(payload["data_dir"]) == data_dir.resolve()

    title = "unique-6f1d2c4a"
    completed, payload = run(_args(data_dir, "add", "--title", title))

    assert completed.returncode == 0
    assert payload["ok"] is True
    assert payload["item"]["id"].startswith("T-")
    assert payload["item"]["title"] == title
    assert payload["status"] == "open"


def test_list_reads_back_in_separate_process(data_dir: Path) -> None:
    run(_args(data_dir, "init"))
    title = "unique-restart-7a3e"
    _, added = run(_args(data_dir, "add", "--title", title))

    completed, payload = run(_args(data_dir, "list", "--json"))

    assert completed.returncode == 0
    assert payload["ok"] is True
    assert payload["count"] == 1
    item = payload["items"][0]
    assert item["id"] == added["item"]["id"]
    assert item["title"] == title
    assert item["status"] == "open"


def test_duplicate_title_is_refused(data_dir: Path) -> None:
    title = "unique-dupe-91bc"
    run(_args(data_dir, "add", "--title", title))

    completed, payload = run(_args(data_dir, "add", "--title", title))

    assert completed.returncode == 3
    assert payload["ok"] is False
    assert payload["code"] == "SBL_E_DUPLICATE_TITLE"


def test_blank_title_is_refused(data_dir: Path) -> None:
    completed, payload = run(_args(data_dir, "add", "--title", "   "))

    assert completed.returncode == 2
    assert payload["ok"] is False
    assert payload["code"] == "SBL_E_EMPTY_TITLE"


def test_remove_item_then_unknown_id(data_dir: Path) -> None:
    _, added = run(_args(data_dir, "add", "--title", "unique-remove-2d0f"))
    item_id = added["item"]["id"]

    completed, payload = run(_args(data_dir, "remove", "--id", item_id))

    assert completed.returncode == 0
    assert payload == {"ok": True, "removed": item_id}

    _, listed = run(_args(data_dir, "list", "--json"))
    assert listed["count"] == 0
    assert listed["items"] == []

    completed, payload = run(_args(data_dir, "remove", "--id", "T-nope"))
    assert completed.returncode == 4
    assert payload["code"] == "SBL_E_BAD_STATE"


def test_uninstall_removes_data_dir_and_list_still_works(data_dir: Path) -> None:
    run(_args(data_dir, "add", "--title", "unique-uninstall-4c55"))

    completed, payload = run(_args(data_dir, "uninstall", "--yes"))

    assert completed.returncode == 0
    assert payload == {"ok": True, "uninstalled": True}
    assert not data_dir.exists()

    completed, payload = run(_args(data_dir, "list", "--json"))
    assert completed.returncode == 0
    assert payload["count"] == 0


def test_uninstall_refuses_foreign_files(data_dir: Path) -> None:
    run(_args(data_dir, "add", "--title", "unique-foreign-8e12"))
    (data_dir / "stranger.txt").write_text("keep me\n", encoding="utf-8")

    completed, payload = run(_args(data_dir, "uninstall", "--yes"))

    assert completed.returncode == 5
    assert payload["ok"] is False
    assert payload["code"] == "SBL_E_FOREIGN_FILES"
    assert data_dir.exists()
