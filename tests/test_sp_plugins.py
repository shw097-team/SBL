"""The three specialised principals must package as three distinct, non-interchangeable identities.

A passing test here proves the packaging is honest about what it is: a set of ZIPs that a host may
or may not load. It cannot prove an installation, so the tests assert the ceiling rather than
claiming past it.
"""

from __future__ import annotations

import json
import zipfile

import pytest

from sbl_core.errors import SBLError
from sbl_sp import plugins
from sbl_sp.sp import load_manifest


def test_the_three_packages_have_distinct_identities(tmp_path):
    packages = plugins.build_all(tmp_path)
    names = [package["plugin_name"] for package in packages]
    assert len(names) == 3
    assert len(set(names)) == 3, names
    assert set(names) == {"sbl-tpm-sp", "sbl-commander-sp", "sbl-external-challenge-sp"}


def test_the_plugin_manifest_is_derived_from_the_principal_manifest():
    for sp_id in plugins.SP_IDS:
        principal = load_manifest(sp_id)
        manifest = plugins.plugin_manifest(sp_id)
        assert manifest["schema"] == plugins.PLUGIN_SCHEMA
        assert manifest["identity"]["sp_id"] == sp_id
        assert manifest["identity"]["role"] == principal["role"]
        assert manifest["identity"]["read_only"] is bool(principal["read_only"])
        assert manifest["permissions"] == list(principal["permissions"])
        assert manifest["forbidden"] == list(principal["forbidden"])


def test_a_package_carries_one_skill_a_manifest_and_a_readme(tmp_path):
    package = plugins.build_package("tpm_sp", tmp_path)
    with zipfile.ZipFile(package["path"]) as archive:
        names = sorted(archive.namelist())
        manifest = json.loads(archive.read("plugin.json").decode("utf-8"))
        skill = archive.read("skills/sbl-tpm-sp/SKILL.md").decode("utf-8")
    assert names == ["README.md", "plugin.json", "skills/sbl-tpm-sp/SKILL.md"]
    assert [entry["name"] for entry in manifest["skills"]] == ["sbl-tpm-sp"]
    assert skill.startswith("---\nname: tpm-sp"), skill[:40]


def test_the_build_is_byte_deterministic(tmp_path):
    first = plugins.build_package("commander_sp", tmp_path / "a")
    second = plugins.build_package("commander_sp", tmp_path / "b")
    assert first["sha256"] == second["sha256"], (first["sha256"], second["sha256"])
    assert first["bytes"] == second["bytes"]


def test_the_claim_ceiling_cannot_be_raised_by_the_caller(tmp_path):
    """A package must not be able to claim it is installed; the ceiling is not a parameter."""

    package = plugins.build_package("external_challenge_sp", tmp_path)
    manifest = plugins.plugin_manifest("external_challenge_sp")
    assert manifest["claim_ceiling"] == "HOST_PENDING"
    assert manifest["host_install_state"] == "NOT_INSTALLED"
    assert package["claim_ceiling"] == "HOST_PENDING"
    assert package["host_install_state"] == "NOT_INSTALLED"
    with pytest.raises(TypeError):
        plugins.build_package("external_challenge_sp", tmp_path, claim_ceiling="INSTALLED")


def test_an_unknown_principal_cannot_be_packaged(tmp_path):
    with pytest.raises(SBLError) as caught:
        plugins.build_package("made_up_sp", tmp_path)
    assert caught.value.code == "SBL_E_UNKNOWN_SP"
    assert not list(tmp_path.glob("*.zip"))


def test_the_challenge_package_stays_read_only_and_unsigned(tmp_path):
    manifest = plugins.plugin_manifest("external_challenge_sp")
    assert manifest["identity"]["read_only"] is True
    assert "product.write" in manifest["forbidden"]
    assert "verdict.sign" not in manifest["permissions"]


def test_no_package_smuggles_corpus_or_private_material(tmp_path):
    for sp_id in plugins.SP_IDS:
        package = plugins.build_package(sp_id, tmp_path)
        for entry in package["entries"]:
            assert entry.endswith((".md", ".json")), entry
            assert "DOC-" not in entry and "KP" not in entry, entry
