"""The HGK adapter must be installable on its own, honest about an unusable root, and removable.

Two of these tests build a *synthetic* HGK root so the suite runs anywhere (including a container
with no HGK present); one probes the real root and skips where it is absent. A synthetic root only
proves the probe logic — it is never evidence that the native control plane is reachable.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
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


def _manifest(target: Path) -> dict:
    return json.loads((target / "MANIFEST.json").read_text(encoding="utf-8"))


def _write_manifest(target: Path, payload: dict) -> None:
    (target / "MANIFEST.json").write_text(json.dumps(payload), encoding="utf-8")


def _sentinel(tmp_path: Path) -> tuple[Path, bytes]:
    outside = tmp_path / "outside.txt"
    payload = b"SENTINEL-CONTENT-MUST-SURVIVE\n"
    outside.write_bytes(payload)
    return outside, payload


def test_uninstall_refuses_a_parent_escape_key_and_leaves_the_outside_file_untouched(tmp_path):
    """F-R5-HARNESS-UNINSTALL-TRAVERSAL-001: the exact escape the R5 review constructed."""

    target = tmp_path / "adapter"
    install(target, _fake_root(tmp_path))
    outside, payload = _sentinel(tmp_path)
    manifest = _manifest(target)
    manifest["files"]["../outside.txt"] = "0" * 64
    _write_manifest(target, manifest)

    with pytest.raises(SBLError) as caught:
        uninstall(target)

    assert caught.value.code == "SBL_E_MANIFEST_UNTRUSTED"
    assert outside.read_bytes() == payload
    assert (target / "plugin.json").is_file()
    assert (target / "MANIFEST.json").is_file()


def test_uninstall_refuses_an_absolute_manifest_key(tmp_path):
    target = tmp_path / "adapter"
    install(target, _fake_root(tmp_path))
    outside, payload = _sentinel(tmp_path)
    manifest = _manifest(target)
    manifest["files"][str(outside)] = "0" * 64
    _write_manifest(target, manifest)

    with pytest.raises(SBLError) as caught:
        uninstall(target)

    assert caught.value.code == "SBL_E_MANIFEST_UNTRUSTED"
    assert outside.read_bytes() == payload


def test_uninstall_refuses_a_key_outside_the_installer_allowlist(tmp_path):
    target = tmp_path / "adapter"
    install(target, _fake_root(tmp_path))
    (target / "stray.txt").write_text("stray", encoding="utf-8")
    manifest = _manifest(target)
    manifest["files"]["stray.txt"] = "0" * 64
    _write_manifest(target, manifest)

    with pytest.raises(SBLError) as caught:
        uninstall(target)

    assert caught.value.code == "SBL_E_MANIFEST_UNTRUSTED"
    assert (target / "stray.txt").is_file()


def test_uninstall_refuses_when_a_file_changed_since_install(tmp_path):
    target = tmp_path / "adapter"
    install(target, _fake_root(tmp_path))
    plugin = target / "plugin.json"
    plugin.write_text(plugin.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(SBLError) as caught:
        uninstall(target)

    assert caught.value.code == "SBL_E_MANIFEST_UNTRUSTED"
    assert plugin.is_file()


def test_uninstall_refuses_a_malformed_files_object(tmp_path):
    target = tmp_path / "adapter"
    install(target, _fake_root(tmp_path))
    _write_manifest(target, {"files": ["plugin.json"]})

    with pytest.raises(SBLError) as caught:
        uninstall(target)

    assert caught.value.code == "SBL_E_MANIFEST_UNTRUSTED"
    assert (target / "plugin.json").is_file()


def test_uninstall_refuses_a_symlinked_file_even_inside_the_allowlist(tmp_path):
    target = tmp_path / "adapter"
    install(target, _fake_root(tmp_path))
    outside, payload = _sentinel(tmp_path)
    plugin = target / "plugin.json"
    plugin.unlink()
    try:
        plugin.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("this host cannot create symlinks without elevation")
    manifest = _manifest(target)
    manifest["files"]["plugin.json"] = "0" * 64
    _write_manifest(target, manifest)

    with pytest.raises(SBLError) as caught:
        uninstall(target)

    assert caught.value.code == "SBL_E_MANIFEST_UNTRUSTED"
    assert outside.read_bytes() == payload


def test_uninstall_refuses_a_symlinked_manifest(tmp_path):
    target = tmp_path / "adapter"
    install(target, _fake_root(tmp_path))
    elsewhere = tmp_path / "elsewhere" / "MANIFEST.json"
    elsewhere.parent.mkdir()
    elsewhere.write_bytes((target / "MANIFEST.json").read_bytes())
    (target / "MANIFEST.json").unlink()
    try:
        (target / "MANIFEST.json").symlink_to(elsewhere)
    except (OSError, NotImplementedError):
        pytest.skip("this host cannot create symlinks without elevation")

    with pytest.raises(SBLError) as caught:
        uninstall(target)

    assert caught.value.code == "SBL_E_MANIFEST_UNTRUSTED"
    assert elsewhere.is_file()


def test_uninstall_removes_exactly_the_installed_paths(tmp_path):
    target = tmp_path / "adapter"
    install(target, _fake_root(tmp_path))

    receipt = uninstall(target)

    assert receipt["removed"] == [
        "MANIFEST.json",
        "adapter.json",
        "plugin.json",
        "skills/hgk-governed-runtime/SKILL.md",
    ]
    assert not target.exists()


def test_uninstall_refuses_a_junction_parent_that_leaves_the_root(tmp_path):
    """A directory junction needs no elevation on Windows, so this is the reversible link case."""

    if os.name != "nt":
        pytest.skip("junctions are a Windows reparse-point feature")

    target = tmp_path / "adapter"
    install(target, _fake_root(tmp_path))
    outside = tmp_path / "outside-skills"
    (outside / "hgk-governed-runtime").mkdir(parents=True)
    body = outside / "hgk-governed-runtime" / "SKILL.md"
    body.write_bytes(b"OUTSIDE-SKILL-MUST-SURVIVE\n")
    shutil.rmtree(target / "skills")
    proc = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(target / "skills"), str(outside)],
        capture_output=True,
        text=True,
        errors="replace",
    )
    if proc.returncode != 0:
        pytest.skip(f"mklink /J unavailable here: {proc.stdout or proc.stderr}".strip())
    assert (target / "skills").exists()

    with pytest.raises(SBLError) as caught:
        uninstall(target)

    assert caught.value.code == "SBL_E_MANIFEST_UNTRUSTED"
    assert body.read_bytes() == b"OUTSIDE-SKILL-MUST-SURVIVE\n"
    assert (target / "plugin.json").is_file()


def test_the_real_hgk_root_probes_ready_when_present():
    root = Path(HGK_PIN["default_root"])
    if not root.is_dir():
        pytest.skip("no HGK root on this host")
    result = probe(root)
    assert result["status"] == "ROOT_READY", result["checks"]
    assert result["observed_version"] == HGK_PIN["version"]
