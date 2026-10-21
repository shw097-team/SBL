"""The HGK adapter must be installable on its own, honest about an unusable root, and removable.

Two of these tests build a *synthetic* HGK root so the suite runs anywhere (including a container
with no HGK present); one probes the real root and skips where it is absent. A synthetic root only
proves the probe logic — it is never evidence that the native control plane is reachable.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sbl_core.errors import SBLError
from sbl_harness import (
    CLAIM_CEILING,
    HGK_PIN,
    HARNESS_ABI,
    doctor,
    install,
    plugin_manifest,
    probe,
    uninstall,
)
from sbl_sp.plugins import portable


def _fake_root(tmp_path: Path, version: str = "0.1.0") -> Path:
    root = tmp_path / "fake-hgk"
    (root / "src" / "hg_kseos").mkdir(parents=True)
    (root / "src" / "hg_kseos" / "__init__.py").write_text(
        f'__version__ = "{version}"\n', encoding="utf-8"
    )
    (root / "var" / "shared-spine").mkdir(parents=True)
    (root / "var" / "shared-spine" / "hg-kseos.db").write_bytes(b"")
    (root / "config").mkdir()
    (root / "config" / "lane-route-slots.candidate.json").write_text("{}", encoding="utf-8")
    (root / "scripts").mkdir()
    (root / "scripts" / "hgk-lane-dispatch.py").write_text("", encoding="utf-8")
    return root


def test_a_missing_root_is_a_typed_refusal_not_an_exception(tmp_path):
    result = probe(tmp_path / "does-not-exist")
    assert result["status"] == "REFUSED_ROOT_UNUSABLE"
    assert result["native_effect"] == "NOT_GRANTED"
    assert any(not check["ok"] for check in result["checks"])


def test_a_synthetic_root_satisfies_the_probe(tmp_path):
    result = probe(_fake_root(tmp_path))
    assert result["status"] == "ROOT_READY", result["checks"]
    assert result["observed_version"] == HGK_PIN["version"]
    assert result["abi"]["name"] == HARNESS_ABI["name"]


def test_a_version_mismatch_is_refused(tmp_path):
    result = probe(_fake_root(tmp_path, version="0.2.0"))
    assert result["status"] == "REFUSED_VERSION_MISMATCH"


def test_install_refuses_when_the_root_is_unusable_and_writes_nothing(tmp_path):
    target = tmp_path / "adapter"
    with pytest.raises(SBLError) as caught:
        install(target, tmp_path / "nope")
    assert caught.value.code == "SBL_E_BAD_STATE"
    assert not target.exists()


def test_the_adapter_manifest_is_a_valid_portable_plugin(tmp_path):
    manifest = plugin_manifest(probe(_fake_root(tmp_path)))
    assert manifest["$schema"] == portable.CANONICAL_SCHEMA_URI
    assert portable.validate_manifest(manifest) == []
    assert manifest["extensions"]["org.sbl.harness"]["native_effect"] == "NOT_GRANTED"


def test_install_doctor_and_uninstall_round_trip(tmp_path):
    root = _fake_root(tmp_path)
    target = tmp_path / "adapter"
    receipt = install(target, root)
    assert receipt["ok"] is True
    assert receipt["claim_ceiling"] == CLAIM_CEILING
    assert (target / "plugin.json").is_file()
    assert (target / "skills" / "hgk-governed-runtime" / "SKILL.md").is_file()
    adapter = json.loads((target / "adapter.json").read_text(encoding="utf-8"))
    assert adapter["hgk_root"] == str(root)
    assert adapter["native_effect"] == "NOT_GRANTED"

    report = doctor(target)
    assert report["ok"] is True, report["problems"]

    removed = uninstall(target)
    assert removed["ok"] is True
    assert not target.exists()


def test_doctor_detects_a_changed_file(tmp_path):
    target = tmp_path / "adapter"
    install(target, _fake_root(tmp_path))
    plugin = target / "plugin.json"
    payload = json.loads(plugin.read_text(encoding="utf-8"))
    payload["version"] = "9.9.9"
    plugin.write_text(json.dumps(payload), encoding="utf-8")
    report = doctor(target)
    assert report["ok"] is False
    assert any("digest changed" in problem for problem in report["problems"])


def test_doctor_detects_the_root_going_away(tmp_path):
    root = _fake_root(tmp_path)
    target = tmp_path / "adapter"
    install(target, root)
    (root / "src" / "hg_kseos" / "__init__.py").unlink()
    report = doctor(target)
    assert report["ok"] is False
    assert any("probe is" in problem for problem in report["problems"])


def test_uninstall_refuses_a_directory_with_foreign_files(tmp_path):
    target = tmp_path / "adapter"
    install(target, _fake_root(tmp_path))
    (target / "extra.txt").write_text("x", encoding="utf-8")
    with pytest.raises(SBLError) as caught:
        uninstall(target)
    assert caught.value.code == "SBL_E_FOREIGN_FILES"


def test_uninstall_refuses_a_directory_it_did_not_install(tmp_path):
    target = tmp_path / "not-ours"
    target.mkdir()
    (target / "plugin.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SBLError) as caught:
        uninstall(target)
    assert caught.value.code == "SBL_E_FOREIGN_FILES"


def test_the_real_hgk_root_probes_ready_when_present():
    root = Path(HGK_PIN["default_root"])
    if not root.is_dir():
        pytest.skip("no HGK root on this host")
    result = probe(root)
    assert result["status"] == "ROOT_READY", result["checks"]
    assert result["observed_version"] == HGK_PIN["version"]
