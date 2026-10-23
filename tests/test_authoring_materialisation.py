"""The authoring-obligation fix must be provable without dispatching a lane.

FAR (PLAN__FAR_WHY_STOP_4) named the defect: authoring work stored as NEEDS_RECIPE is counted but has no
command, so a live supervisor reports zero selectable items while twelve obligations remain. These tests pin
the materialisation, its idempotency, and the three-fact classification that replaces "did the shell exit 0".
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os

R = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(R, "tools", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mat = _load("materialize_authoring")
aq = _load("advance_queue")


def _item(**kw):
    base = {"id": "DEN-TEST01", "den_id": "DEN-TEST01", "title": "a test obligation", "status": "NEEDS_RECIPE",
            "owner_class": "AGENT", "satisfiable_by": "AGENT", "recipe_hint": "kanban transitions must be total"}
    base.update(kw)
    return base


def test_a_commandless_obligation_becomes_an_executable_author_action(tmp_path):
    q = {"items": [_item()]}
    changed = mat.materialise(q, {"recipes": {}}, brief_dir=str(tmp_path))
    it = q["items"][0]
    assert changed and it["status"] == "READY" and it["phase"] == "AUTHOR"
    assert it["resume_cmd"].startswith("python _governance/round-20261022-r15_2/tools/run_lane.py --role EXECUTE")
    assert "--brief" in it["resume_cmd"] and "--nonce" in it["resume_cmd"]
    assert it["expect_artefact"].startswith("tests/test_")
    assert it["accept_cmd"].startswith("python -m pytest")
    brief = (tmp_path / os.path.basename(it["author_brief"])).read_text(encoding="utf-8")
    assert "kanban transitions must be total" in brief
    assert it["expect_artefact"] in brief, "the brief must name the exact artefact path"


def test_materialisation_is_idempotent_and_leaves_done_alone(tmp_path):
    q = {"items": [_item(), _item(id="DEN-DONE1", den_id="DEN-DONE1", status="DONE")]}
    first = mat.materialise(q, {}, brief_dir=str(tmp_path))
    snapshot = [json.dumps(i, sort_keys=True) for i in q["items"]]
    second = mat.materialise(q, {}, brief_dir=str(tmp_path))
    assert len(first) == 1 and second == []
    assert [json.dumps(i, sort_keys=True) for i in q["items"]] == snapshot
    assert q["items"][1]["status"] == "DONE"


def test_owner_and_host_items_are_never_materialised(tmp_path):
    q = {"items": [_item(owner_class="OWNER"), _item(id="DEN-H1", den_id="DEN-H1", owner_class="HOST")]}
    assert mat.materialise(q, {}, brief_dir=str(tmp_path)) == []
    assert all(i["status"] == "NEEDS_RECIPE" for i in q["items"])


def test_selector_admits_author_action_and_names_what_stays_unresolved():
    item = _item()
    q = {"items": [item]}
    mat.materialise(q, {}, brief_dir=os.path.join(R, "workers", "codex_exec"))
    sel = [i for i in q["items"] if i["owner_class"] == "AGENT" and i["status"] == "READY" and i.get("resume_cmd")]
    assert len(sel) == 1, "an AUTHOR action must be selectable, or the supervisor idles again"
    stale = _item(id="DEN-X", den_id="DEN-X")
    assert not stale.get("resume_cmd"), "a bare NEEDS_RECIPE item is still invisible - that is the defect being fixed"


def test_dispatch_green_without_artefact_is_not_a_pass():
    it = {"expect_artefact": "tests/test_none.py"}
    assert aq.classify_dispatch(it, True, False, None) == ("PARKED", "DISPATCH_GREEN_BUT_ARTEFACT_MISSING")


def test_timeout_with_artefact_keeps_partial_and_never_re_authors():
    it = {"expect_artefact": "tests/test_x.py"}
    status, reason = aq.classify_dispatch(it, False, True, None)
    assert status == "PARTIAL" and reason == "ARTEFACT_PRESENT_BUT_DISPATCH_NOT_GREEN"


def test_dispatch_and_acceptance_are_separate_facts():
    it = {"expect_artefact": "tests/test_x.py"}
    assert aq.classify_dispatch(it, True, True, False)[0] == "PARTIAL"
    assert aq.classify_dispatch(it, True, True, True) == ("DONE", "ACCEPTED")


def test_plain_command_item_without_artefact_still_completes_on_rc():
    assert aq.classify_dispatch({"id": "Q1"}, True, False, None) == ("DONE", "ACCEPTED")
    assert aq.classify_dispatch({"id": "Q1"}, False, False, None) == ("PARKED", "STEP_FAILED")
