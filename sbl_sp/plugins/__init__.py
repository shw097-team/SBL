"""Installable packaging for the three specialised principals.

A principle here: a package is not an installation. Everything this module produces carries
``claim_ceiling: HOST_PENDING`` and the builder refuses any attempt to raise it, because only a real
host (ChatGPT workspace, Hermes, Codex, Claude Code) can turn a ZIP into an effective load, and this
code has no host present.

Packages are byte-deterministic: fixed zip timestamps, sorted entries, one skill each. That is what
makes the recorded sha256 a usable provenance handle rather than a moving target.

Layout follows the portable Agent Plugins 1.0.0 package shape: a root ``plugin.json`` that validates
against the vendored portable schema, ``skills/<skill-name>/SKILL.md`` where the directory name equals
the skill's own frontmatter ``name``, and a human-facing README. Principal metadata the portable schema
has no field for (identity, permissions, forbidden actions, claim ceiling) rides in
``extensions["org.sbl.principal"]`` — the schema sets ``additionalProperties: false``, so any extra
top-level key makes the package unrecognisable to a conforming host.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

from sbl_core.errors import SBLError

from ..sp import load_manifest
from . import portable

# The internal source-ledger schema id. Kept so records that already cite it stay resolvable, and
# recorded INSIDE the extensions block — never as a top-level key, where the portable schema's
# `additionalProperties: false` would reject it.
PLUGIN_SCHEMA = "SBL-AGENT-PLUGIN/1"
PLUGIN_SCHEMA_URI = portable.CANONICAL_SCHEMA_URI
EXTENSION_NAMESPACE = "org.sbl.principal"
VERSION = "0.1.0"
CLAIM_CEILING = "HOST_PENDING"
PLUGIN_ROOT = Path(__file__).parent
SP_IDS: tuple[str, ...] = ("tpm_sp", "commander_sp", "external_challenge_sp")
_ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def _plugin_name(sp_id: str) -> str:
    return "sbl-" + sp_id.replace("_", "-")


def skill_name(sp_id: str) -> str:
    """The Agent Skill's own name, which must equal its containing directory."""

    return sp_id.replace("_", "-")


def _frontmatter(text: str) -> dict[str, str]:
    """Minimal reader for the leading ``---`` block. No YAML dependency, by design."""

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SBLError(
            "SBL_E_PLUGIN_SCHEMA",
            "SKILL.md must open with a YAML frontmatter block",
            {"first_line": lines[0] if lines else None},
        )
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        fields[key.strip()] = value.strip().strip('"').strip("'")
    raise SBLError(
        "SBL_E_PLUGIN_SCHEMA",
        "SKILL.md frontmatter is not terminated",
        {"sp_id": None},
    )


def plugin_manifest(sp_id: str) -> dict[str, Any]:
    """Derive the installable manifest from the principal's own manifest, never from a caller's dict."""

    manifest = load_manifest(sp_id)
    name = _plugin_name(sp_id)
    skill = skill_name(sp_id)
    return {
        "$schema": PLUGIN_SCHEMA_URI,
        "name": name,
        "version": VERSION,
        "description": (
            f"{manifest.get('name')} specialised principal ({manifest.get('role')}): "
            "one Agent Skill packaged for portable host ingestion"
        ),
        "license": "MIT",
        "keywords": ["sbl", "specbuild-loop", "agent-skill", sp_id.replace("_", "-")],
        "extensions": {
            EXTENSION_NAMESPACE: {
                "sp_id": sp_id,
                "role": manifest.get("role"),
                "read_only": bool(manifest.get("read_only")),
                "permissions": list(manifest.get("permissions") or []),
                "forbidden": list(manifest.get("forbidden") or []),
                "skill": skill,
                "source_ledger_schema": PLUGIN_SCHEMA,
                "claim_ceiling": CLAIM_CEILING,
                "host_install_state": "NOT_INSTALLED",
                "limits": [
                    "This package declares intent; it does not prove a host loaded it.",
                    "A plugin id is issued by the host, not by this package.",
                    "Schema conformance is proven offline against the vendored portable schema; "
                    "host-side ingestion remains a host action.",
                ],
            }
        },
    }


def principal_record(sp_id: str) -> dict[str, Any]:
    """The principal metadata, read back out of the portable manifest's extension block."""

    return dict(plugin_manifest(sp_id)["extensions"][EXTENSION_NAMESPACE])


def skill_text(sp_id: str) -> str:
    path = PLUGIN_ROOT / sp_id / "SKILL.md"
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SBLError(
            "SBL_E_BAD_STATE",
            "skill body is missing for this principal",
            {"sp_id": sp_id, "path": str(path)},
        ) from exc


def validate_skill(text: str, expected_name: str) -> list[str]:
    """Return violations of the skill-packaging rules this project can prove offline."""

    errors: list[str] = []
    try:
        fields = _frontmatter(text)
    except SBLError as exc:
        return ["frontmatter unreadable: " + str(exc.message)]
    if not fields.get("name"):
        errors.append("frontmatter is missing 'name'")
    elif fields["name"] != expected_name:
        errors.append(
            "frontmatter name " + repr(fields["name"]) + " must equal the skill directory "
            + repr(expected_name)
        )
    if not fields.get("description"):
        errors.append("frontmatter is missing 'description'")
    return errors


def package_files(sp_id: str) -> dict[str, bytes]:
    """The exact bytes that go into the archive, keyed by in-archive path."""

    manifest = plugin_manifest(sp_id)
    portable.assert_valid(manifest, where=_plugin_name(sp_id) + "/plugin.json")
    name = manifest["name"]
    skill = skill_name(sp_id)
    body = skill_text(sp_id)
    problems = validate_skill(body, skill)
    if problems:
        raise SBLError(
            "SBL_E_PLUGIN_SCHEMA",
            "the packaged skill does not satisfy the Agent Skill layout rules",
            {"sp_id": sp_id, "violations": problems},
        )
    record = manifest["extensions"][EXTENSION_NAMESPACE]
    readme = (
        "# " + name + "\n\n"
        "Portable Agent Plugin package for the SBL specialised principal `" + str(record["sp_id"])
        + "` (" + str(record["role"]) + ").\n\n"
        "- portable manifest: `plugin.json` (`" + PLUGIN_SCHEMA_URI + "`)\n"
        "- skill: `skills/" + skill + "/SKILL.md`\n"
        "- claim ceiling: `" + CLAIM_CEILING + "` (a package is not an installation)\n"
        "- permissions: " + (", ".join(record["permissions"]) or "none") + "\n"
        "- forbidden: " + (", ".join(record["forbidden"]) or "none") + "\n\n"
        "Importing this package into a host is a separate, human, host-side action. Do not report\n"
        "`INSTALLED` on the strength of the ZIP existing.\n"
    )
    return {
        "plugin.json": (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        "skills/" + skill + "/SKILL.md": body.encode("utf-8"),
        "README.md": readme.encode("utf-8"),
    }


def build_package(sp_id: str, out_dir: str | Path) -> dict[str, Any]:
    if sp_id not in SP_IDS:
        raise SBLError(
            "SBL_E_UNKNOWN_SP",
            "only the three registered principals can be packaged",
            {"sp_id": sp_id, "known": list(SP_IDS)},
        )
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest = plugin_manifest(sp_id)
    name = manifest["name"]
    target = out / (name + "-" + VERSION + ".zip")
    files = package_files(sp_id)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for archive_path in sorted(files):
            info = zipfile.ZipInfo(archive_path, date_time=_ZIP_DATE)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, files[archive_path])
    payload = target.read_bytes()
    record = manifest["extensions"][EXTENSION_NAMESPACE]
    return {
        "sp_id": sp_id,
        "plugin_name": name,
        "skill_name": skill_name(sp_id),
        "path": str(target),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "entries": sorted(files),
        "plugin_schema": PLUGIN_SCHEMA_URI,
        "plugin_schema_valid": True,
        "claim_ceiling": CLAIM_CEILING,
        "host_install_state": "NOT_INSTALLED",
        "identity": {
            "sp_id": sp_id,
            "role": record["role"],
            "read_only": record["read_only"],
        },
    }


def inspect_package(path: str | Path) -> dict[str, Any]:
    """Re-validate a built archive from its bytes alone. Used by the tools and the tests."""

    archive_path = Path(path)
    with zipfile.ZipFile(archive_path) as archive:
        names = sorted(archive.namelist())
        manifest = json.loads(archive.read("plugin.json").decode("utf-8"))
        skill_paths = [n for n in names if n.startswith("skills/") and n.endswith("/SKILL.md")]
        skill_errors: list[str] = []
        for skill_path in skill_paths:
            parts = skill_path.split("/")
            expected = parts[1] if len(parts) == 3 else ""
            skill_errors.extend(
                validate_skill(archive.read(skill_path).decode("utf-8"), expected)
            )
    payload = archive_path.read_bytes()
    return {
        "path": str(archive_path),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "entries": names,
        "schema_violations": portable.validate_manifest(manifest),
        "skill_violations": skill_errors,
        "skill_paths": skill_paths,
        "plugin_name": manifest.get("name"),
        "plugin_schema": manifest.get("$schema"),
    }


def build_all(out_dir: str | Path) -> list[dict[str, Any]]:
    packages = [build_package(sp_id, out_dir) for sp_id in SP_IDS]
    names = [package["plugin_name"] for package in packages]
    if len(set(names)) != len(SP_IDS):
        raise SBLError(
            "SBL_E_SP_IDENTITY_COLLISION",
            "the three principals must not share a package identity",
            {"names": names},
        )
    skills = [package["skill_name"] for package in packages]
    if len(set(skills)) != len(SP_IDS):
        raise SBLError(
            "SBL_E_SP_IDENTITY_COLLISION",
            "the three principals must not share a skill identity",
            {"skills": skills},
        )
    return packages
