"""Slice B1: the skill bridge stays inside its manifest."""

from __future__ import annotations

from pathlib import Path

import pytest

from sbl_core.errors import SBLError
from sbl_sp.bridge import SkillBridge

SKILL_MANIFEST = (
    Path(__file__).resolve().parents[1] / "skills" / "sbl_todo" / "skill.json"
)


def _bridge() -> SkillBridge:
    return SkillBridge(str(SKILL_MANIFEST))


def test_missing_manifest_is_refused(tmp_path: Path) -> None:
    with pytest.raises(SBLError) as excinfo:
        SkillBridge(str(tmp_path / "absent.json"))
    assert excinfo.value.code == "SBL_E_BAD_STATE"


def test_discover_reports_surface() -> None:
    found = _bridge().discover()

    assert found == {
        "schema": "SBL-SKILL-DISCOVER/1",
        "skill": "sbl-todo",
        "triggers": ["todo", "task list", "待辦"],
        "permissions": ["todo.read", "todo.write"],
    }


def test_match_is_case_insensitive() -> None:
    bridge = _bridge()

    assert bridge.match("Please add a TODO for the review") is True
    assert bridge.match("show my TASK LIST") is True
    assert bridge.match("整理待辦事項") is True
    assert bridge.match("deploy the release") is False


def test_effective_load_requires_provider() -> None:
    bridge = _bridge()

    with pytest.raises(SBLError) as excinfo:
        bridge.effective_load({"name": "codex", "provider_on": False})
    assert excinfo.value.code == "SBL_E_PROVIDER_OFF"

    loaded = bridge.effective_load({"name": "codex", "provider_on": True})
    assert loaded["schema"] == "SBL-SKILL-LOAD/1"
    assert loaded["skill"] == "sbl-todo"
    assert loaded["loaded"] is True
    assert loaded["host"] == "codex"
    assert loaded["trace_id"].startswith("L-")
    assert len(loaded["trace_id"]) == 2 + 12


def test_invoke_refuses_forbidden_and_out_of_scope_actions() -> None:
    bridge = _bridge()

    for action in ("repo.write", "net.call", "todo.delete"):
        with pytest.raises(SBLError) as excinfo:
            bridge.invoke(action, provider_on=True)
        assert excinfo.value.code == "SBL_E_PERMISSION_DENIED"

    with pytest.raises(SBLError) as excinfo:
        bridge.invoke("todo.read", provider_on=False)
    assert excinfo.value.code == "SBL_E_PROVIDER_OFF"


def test_invoke_permitted_action_succeeds() -> None:
    assert _bridge().invoke("todo.write", provider_on=True) == {
        "ok": True,
        "skill": "sbl-todo",
        "action": "todo.write",
    }


def test_unload_leaves_no_residue() -> None:
    assert _bridge().unload() == {
        "schema": "SBL-SKILL-UNLOAD/1",
        "unloaded": True,
        "residue": [],
    }
