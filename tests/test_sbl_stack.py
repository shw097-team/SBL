"""The stack surface must install, verify itself honestly, and refuse what it does not own."""

from __future__ import annotations

import json

import pytest

from sbl_core.errors import SBLError
from sbl_stack import (
    CLAIM_CEILING,
    COMPONENT_MODULES,
    MANIFEST_NAME,
    describe,
    doctor,
    install,
    selftest,
    status,
    uninstall,
)


def test_install_writes_an_integrity_manifest_covering_every_component(tmp_path):
    target = tmp_path / "stack"
    receipt = install(target)
    assert receipt["ok"] is True
    assert receipt["components"] == len(COMPONENT_MODULES)
    assert receipt["claim_ceiling"] == CLAIM_CEILING
    payload = json.loads((target / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert set(payload["components"]) == set(COMPONENT_MODULES)
    assert sorted(payload["extras"]["principals"]) == [
        "commander_sp",
        "external_challenge_sp",
        "tpm_sp",
    ]
    assert payload["extras"]["mode_gate_cells"] == 39


def test_a_fresh_install_passes_its_own_doctor(tmp_path):
    target = tmp_path / "stack"
    install(target)
    report = doctor(target)
    assert report["ok"] is True, report["problems"]
    assert report["components"] == len(COMPONENT_MODULES)


def test_doctor_fails_on_a_tampered_manifest_digest(tmp_path):
    """NEG: a manifest claiming the wrong bytes must not be reported healthy."""

    target = tmp_path / "stack"
    install(target)
    manifest_path = target / MANIFEST_NAME
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["components"]["sbl_core.m03_routing"] = "0" * 64
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    report = doctor(target)
    assert report["ok"] is False
    assert any("digest changed" in problem for problem in report["problems"])


def test_doctor_refuses_a_directory_that_is_not_an_installed_stack(tmp_path):
    report = doctor(tmp_path)
    assert report["ok"] is False
    assert "not an installed stack" in report["problems"][0]


def test_install_refuses_a_non_empty_foreign_directory(tmp_path):
    target = tmp_path / "stack"
    target.mkdir()
    (target / "someone-elses-file.txt").write_text("x", encoding="utf-8")
    with pytest.raises(SBLError) as caught:
        install(target)
    assert caught.value.code == "SBL_E_FOREIGN_FILES"


def test_uninstall_removes_the_stack_and_refuses_foreign_files(tmp_path):
    target = tmp_path / "stack"
    install(target)
    receipt = uninstall(target)
    assert receipt["ok"] is True
    assert receipt["empty"] is True
    assert not target.exists()

    again = tmp_path / "stack2"
    install(again)
    (again / "left-behind.txt").write_text("x", encoding="utf-8")
    with pytest.raises(SBLError) as caught:
        uninstall(again)
    assert caught.value.code == "SBL_E_FOREIGN_FILES"


def test_status_reports_the_ceiling_not_an_installation_claim(tmp_path):
    target = tmp_path / "stack"
    install(target)
    report = status(target)
    assert report["installed"] is True
    assert report["claim_ceiling"] == CLAIM_CEILING
    assert report["host_install_state"] == "NOT_INSTALLED"
    assert status(tmp_path / "nowhere")["installed"] is False


def test_describe_lists_the_six_modules_and_three_principals():
    surface = describe()
    assert surface["modules"] == ["SBLM01", "SBLM02", "SBLM03", "SBLM04", "SBLM05", "SBLM06"]
    assert len(surface["principals"]) == 3


def test_selftest_runs_the_journey_and_both_refusals(tmp_path):
    report = selftest(tmp_path)
    steps = {item["step"]: item for item in report["steps"]}
    assert report["ok"] is True, report
    for required in (
        "core.doctor",
        "m01.intake",
        "m02.derive",
        "m03.route.CLI_TOOL",
        "NEG.unlocated-clause",
        "NEG.prohibited-kind",
        "sp.manifests",
        "modes.matrix",
        "plugins.build",
    ):
        assert steps[required]["ok"] is True, (required, steps[required])
    assert report["denominator"].split("/")[0] == report["denominator"].split("/")[1]
