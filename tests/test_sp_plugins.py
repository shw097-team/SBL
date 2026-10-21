"""The three specialised principals must package as three distinct, non-interchangeable identities,
and each package must be a valid portable Agent Plugin rather than merely valid JSON.

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
from sbl_sp.plugins import portable
from sbl_sp.sp import load_manifest


def test_the_three_packages_have_distinct_identities(tmp_path):
    packages = plugins.build_all(tmp_path)
    names = [package["plugin_name"] for package in packages]
    skills = [package["skill_name"] for package in packages]
    assert len(names) == 3
    assert len(set(names)) == 3, names
    assert len(set(skills)) == 3, skills
    assert set(names) == {"sbl-tpm-sp", "sbl-commander-sp", "sbl-external-challenge-sp"}
    assert set(skills) == {"tpm-sp", "commander-sp", "external-challenge-sp"}


def test_the_plugin_manifest_is_derived_from_the_principal_manifest():
    for sp_id in plugins.SP_IDS:
        principal = load_manifest(sp_id)
        manifest = plugins.plugin_manifest(sp_id)
        record = manifest["extensions"][plugins.EXTENSION_NAMESPACE]
        assert record["sp_id"] == sp_id
        assert record["role"] == principal["role"]
        assert record["read_only"] is bool(principal["read_only"])
        assert record["permissions"] == list(principal["permissions"])
        assert record["forbidden"] == list(principal["forbidden"])


def test_the_manifest_is_a_valid_portable_plugin_manifest():
    """The defect this round repairs: no `$schema`, and internal keys at the top level."""

    for sp_id in plugins.SP_IDS:
        manifest = plugins.plugin_manifest(sp_id)
        assert manifest["$schema"] == portable.CANONICAL_SCHEMA_URI
        assert portable.validate_manifest(manifest) == [], (sp_id, manifest)
        # The old shape must be gone, not merely supplemented.
        assert "schema" not in manifest
        for internal in ("identity", "permissions", "forbidden", "claim_ceiling", "skills"):
            assert internal not in manifest, (sp_id, internal)


def test_the_vendored_schema_is_the_published_one():
    schema = portable.load_schema()
    assert schema["$id"] == portable.CANONICAL_SCHEMA_URI
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {"$schema", "name"}
    assert portable.ALLOWED_TOP_LEVEL == set(schema["properties"])


def test_the_validator_rejects_each_shape_it_claims_to_catch():
    """Non-vacuity: every one of these must be refused, and none is a JSON syntax error."""

    good = plugins.plugin_manifest("tpm_sp")

    missing_schema = {k: v for k, v in good.items() if k != "$schema"}
    assert portable.validate_manifest(missing_schema), "missing $schema was accepted"

    wrong_schema = dict(good, **{"$schema": "https://example.invalid/plugin.schema.json"})
    assert portable.validate_manifest(wrong_schema), "a foreign $schema was accepted"

    extra_top_level = dict(good, permissions=["product.write"])
    assert portable.validate_manifest(extra_top_level), "an extra top-level key was accepted"

    legacy_shape = dict(good)
    legacy_shape["schema"] = plugins.PLUGIN_SCHEMA
    assert portable.validate_manifest(legacy_shape), "the legacy 'schema' key was accepted"

    bad_name = dict(good, name="SBL TPM SP")
    assert portable.validate_manifest(bad_name), "an illegal name pattern was accepted"

    double_dash = dict(good, name="sbl--tpm-sp")
    assert portable.validate_manifest(double_dash), "a '--' name was accepted"

    bad_extensions = dict(good, extensions={"org.sbl.principal": ["not", "an", "object"]})
    assert portable.validate_manifest(bad_extensions), "a non-object extension was accepted"

    bad_author = dict(good, author={"name": "x", "role": "y"})
    assert portable.validate_manifest(bad_author), "an unknown author key was accepted"


def test_a_package_carries_one_skill_a_manifest_and_a_readme(tmp_path):
    package = plugins.build_package("tpm_sp", tmp_path)
    with zipfile.ZipFile(package["path"]) as archive:
        names = sorted(archive.namelist())
        manifest = json.loads(archive.read("plugin.json").decode("utf-8"))
        skill = archive.read("skills/tpm-sp/SKILL.md").decode("utf-8")
    assert names == ["README.md", "plugin.json", "skills/tpm-sp/SKILL.md"]
    assert manifest["name"] == "sbl-tpm-sp"
    assert skill.startswith("---\nname: tpm-sp"), skill[:40]


def test_every_skill_directory_matches_its_frontmatter_name(tmp_path):
    for sp_id in plugins.SP_IDS:
        package = plugins.build_package(sp_id, tmp_path)
        report = plugins.inspect_package(package["path"])
        assert report["skill_violations"] == [], (sp_id, report["skill_violations"])
        assert report["skill_paths"] == ["skills/" + package["skill_name"] + "/SKILL.md"]


def test_the_build_is_byte_deterministic(tmp_path):
    first = plugins.build_package("commander_sp", tmp_path / "a")
    second = plugins.build_package("commander_sp", tmp_path / "b")
    assert first["sha256"] == second["sha256"], (first["sha256"], second["sha256"])
    assert first["bytes"] == second["bytes"]


def test_the_claim_ceiling_cannot_be_raised_by_the_caller(tmp_path):
    """A package must not be able to claim it is installed; the ceiling is not a parameter."""

    package = plugins.build_package("external_challenge_sp", tmp_path)
    record = plugins.principal_record("external_challenge_sp")
    assert record["claim_ceiling"] == "HOST_PENDING"
    assert record["host_install_state"] == "NOT_INSTALLED"
    assert package["claim_ceiling"] == "HOST_PENDING"
    assert package["host_install_state"] == "NOT_INSTALLED"
    with pytest.raises(TypeError):
        plugins.build_package("external_challenge_sp", tmp_path, claim_ceiling="INSTALLED")


def test_an_unknown_principal_cannot_be_packaged(tmp_path):
    with pytest.raises(SBLError) as caught:
        plugins.build_package("made_up_sp", tmp_path)
    assert caught.value.code == "SBL_E_UNKNOWN_SP"
    assert not list(tmp_path.glob("*.zip"))


def test_a_skill_that_does_not_match_its_directory_is_refused():
    problems = plugins.validate_skill("---\nname: something-else\ndescription: x\n---\n", "tpm-sp")
    assert problems and "must equal the skill directory" in problems[0]
    assert plugins.validate_skill("# no frontmatter\n", "tpm-sp")


def test_the_challenge_package_stays_read_only_and_unsigned():
    record = plugins.principal_record("external_challenge_sp")
    assert record["read_only"] is True
    assert "product.write" in record["forbidden"]
    assert "verdict.sign" not in record["permissions"]


def test_no_package_smuggles_corpus_or_private_material(tmp_path):
    for sp_id in plugins.SP_IDS:
        package = plugins.build_package(sp_id, tmp_path)
        for entry in package["entries"]:
            assert entry.endswith((".md", ".json")), entry
            assert "DOC-" not in entry and "KP" not in entry, entry


def test_inspect_package_catches_a_tampered_manifest(tmp_path):
    package = plugins.build_package("tpm_sp", tmp_path)
    source = tmp_path / "tampered.zip"
    with zipfile.ZipFile(package["path"]) as original, zipfile.ZipFile(source, "w") as target:
        for name in original.namelist():
            payload = original.read(name)
            if name == "plugin.json":
                manifest = json.loads(payload.decode("utf-8"))
                manifest["claim_ceiling"] = "INSTALLED"
                payload = json.dumps(manifest, indent=2).encode("utf-8")
            target.writestr(name, payload)
    report = plugins.inspect_package(source)
    assert report["schema_violations"], "a tampered top-level key slipped through"


def test_the_manifest_also_validates_under_the_real_jsonschema_engine():
    """Cross-check the hand-written validator against a general engine when one is installed."""

    jsonschema = pytest.importorskip("jsonschema")
    schema = portable.load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    for sp_id in plugins.SP_IDS:
        manifest = plugins.plugin_manifest(sp_id)
        assert list(validator.iter_errors(manifest)) == [], sp_id
