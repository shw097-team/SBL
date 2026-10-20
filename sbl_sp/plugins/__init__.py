"""Installable packaging for the three specialised principals.

A principle here: a package is not an installation. Everything this module produces carries
``claim_ceiling: HOST_PENDING`` and the builder refuses any attempt to raise it, because only a real
host (ChatGPT workspace, Hermes, Codex, Claude Code) can turn a ZIP into an effective load, and this
code has no host present.

Packages are byte-deterministic: fixed zip timestamps, sorted entries, one skill each. That is what
makes the recorded sha256 a usable provenance handle rather than a moving target.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

from sbl_core.errors import SBLError

from ..sp import load_manifest

PLUGIN_SCHEMA = "SBL-AGENT-PLUGIN/1"
VERSION = "0.1.0"
CLAIM_CEILING = "HOST_PENDING"
PLUGIN_ROOT = Path(__file__).parent
SP_IDS: tuple[str, ...] = ("tpm_sp", "commander_sp", "external_challenge_sp")
_ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def _plugin_name(sp_id: str) -> str:
    return "sbl-" + sp_id.replace("_sp", "").replace("_", "-") + "-sp"


def plugin_manifest(sp_id: str) -> dict[str, Any]:
    """Derive the installable manifest from the principal's own manifest, never from a caller's dict."""

    manifest = load_manifest(sp_id)
    skill_name = _plugin_name(sp_id)
    return {
        "schema": PLUGIN_SCHEMA,
        "name": skill_name,
        "display_name": str(manifest.get("name") or sp_id),
        "version": VERSION,
        "description": f"{manifest.get('name')} specialised principal ({manifest.get('role')})",
        "skills": [{"name": skill_name, "path": f"skills/{skill_name}/SKILL.md"}],
        "identity": {
            "sp_id": sp_id,
            "role": manifest.get("role"),
            "read_only": bool(manifest.get("read_only")),
        },
        "permissions": list(manifest.get("permissions") or []),
        "forbidden": list(manifest.get("forbidden") or []),
        "claim_ceiling": CLAIM_CEILING,
        "host_install_state": "NOT_INSTALLED",
        "limits": [
            "This package declares intent; it does not prove a host loaded it.",
            "A plugin id is issued by the host, not by this package.",
            "Skills/paths follow the documented private-plugin layout; schema conformance is NOT_RUN offline.",
        ],
    }


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


def package_files(sp_id: str) -> dict[str, bytes]:
    """The exact bytes that go into the archive, keyed by in-archive path."""

    manifest = plugin_manifest(sp_id)
    skill_name = _plugin_name(sp_id)
    readme = (
        f"# {manifest['display_name']}\n\n"
        f"Private plugin package for the {manifest['display_name']} specialised principal.\n\n"
        f"- claim ceiling: `{CLAIM_CEILING}` (a package is not an installation)\n"
        f"- permissions: {', '.join(manifest['permissions']) or 'none'}\n"
        f"- forbidden: {', '.join(manifest['forbidden']) or 'none'}\n\n"
        "Importing this package into a host is a separate, human, host-side action. Do not report\n"
        "`INSTALLED` on the strength of the ZIP existing.\n"
    )
    return {
        "plugin.json": (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        f"skills/{skill_name}/SKILL.md": skill_text(sp_id).encode("utf-8"),
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
    name = plugin_manifest(sp_id)["name"]
    target = out / f"{name}-{VERSION}.zip"
    files = package_files(sp_id)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for archive_path in sorted(files):
            info = zipfile.ZipInfo(archive_path, date_time=_ZIP_DATE)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, files[archive_path])
    payload = target.read_bytes()
    return {
        "sp_id": sp_id,
        "plugin_name": name,
        "path": str(target),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "entries": sorted(files),
        "claim_ceiling": CLAIM_CEILING,
        "host_install_state": "NOT_INSTALLED",
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
    return packages
