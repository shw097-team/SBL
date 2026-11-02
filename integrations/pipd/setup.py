#!/usr/bin/env python3
"""Build hook for the ONE canonical ``schemas/`` tree (S4R3-F006, P0).

Why this file exists
--------------------
The whole packaging configuration stays declarative in ``pyproject.toml`` -- except for one thing it
cannot express: the canonical ``schemas/`` tree (``registry.json`` + 19 ``*.schema.json``) lives at
the repository ROOT, outside the import package (``src/pipd_ls_sp/``), and setuptools'
``[tool.setuptools.package-data]`` can only reach data that is already inside a package directory.
So a backend-driven build (``python -m build``) shipped a wheel with NO ``pipd_ls_sp/schemas/``:
installed into a clean venv, ``pipd doctor`` reported ``mode=NONE`` / ``verdict=FAIL`` and exited 1.
The hand-built wheel from ``tools/build_dist.py`` never had this defect because it maps the tree
explicitly; this hook restores that behaviour for the standard build.

Self-contained on purpose
-------------------------
The build-time logic lives HERE and imports nothing from ``tools/``: an sdist does not carry
``tools/``, so a helper imported from there would break the normal sdist -> wheel path. ``MANIFEST.in``
carries ``schemas/*.json`` in the sdist for the same reason.

Fail-closed contract
--------------------
The mirror refuses (``SchemaMirrorRefusal``) rather than shipping a wheel whose registry cannot be
resolved: registry missing or unparseable, a family without ``schema_file``, a declared schema that is
absent, an undeclared ``*.json`` present (the registry is authoritative), or a file that did not land
byte-identical. Nothing is ever copied into the source tree; the mirror is written into the build
directory only.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

ROOT = Path(__file__).resolve().parent
PACKAGE = "pipd_ls_sp"
REGISTRY = "registry.json"


class SchemaMirrorRefusal(Exception):
    """The schemas tree and its registry disagree; the build must not continue."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def declared_schema_files(schemas_dir: "Path | str") -> list[str]:
    """Basenames of the schema files ``registry.json`` names, in registry order."""
    schemas = Path(schemas_dir)
    registry_path = schemas / REGISTRY
    if not registry_path.is_file():
        raise SchemaMirrorRefusal(f"{registry_path} is missing: the registry is the source of truth")
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SchemaMirrorRefusal(f"{registry_path} is not readable JSON: {exc}") from exc
    families = registry.get("families") if isinstance(registry, dict) else None
    if not isinstance(families, list) or not families:
        raise SchemaMirrorRefusal(f"{registry_path} declares no `families` list")
    names: list[str] = []
    for index, family in enumerate(families):
        if not isinstance(family, dict) or not isinstance(family.get("schema_file"), str):
            raise SchemaMirrorRefusal(f"family #{index} in {registry_path} has no `schema_file`")
        names.append(Path(family["schema_file"]).name)
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise SchemaMirrorRefusal(f"{registry_path} names the same schema twice: {duplicates}")
    return names


def assert_schemas_are_consistent(schemas_dir: "Path | str") -> dict:
    """Refuse if the on-disk ``*.json`` set and the registry disagree. Returns a digest ledger."""
    schemas = Path(schemas_dir)
    required = declared_schema_files(schemas)
    missing = [n for n in required if not (schemas / n).is_file()]
    if missing:
        raise SchemaMirrorRefusal(f"registry names schemas absent from {schemas}: {missing}")
    on_disk = sorted(p.name for p in schemas.glob("*.json"))
    undeclared = sorted(set(on_disk) - set(required) - {REGISTRY})
    if undeclared:
        raise SchemaMirrorRefusal(
            f"undeclared json in {schemas} (the registry is authoritative): {undeclared}")
    ledger = {REGISTRY: _sha256((schemas / REGISTRY).read_bytes())}
    for name in required:
        ledger[name] = _sha256((schemas / name).read_bytes())
    return {"files": [REGISTRY, *required], "sha256": ledger}


def mirror_schemas(schemas_dir: "Path | str", target_dir: "Path | str") -> dict:
    """Copy ``registry.json`` + every declared schema into ``target_dir`` (a package directory).

    Returns a ledger of what was written so a caller can ASSERT the mirror instead of trusting that a
    copy "should" have happened.
    """
    schemas = Path(schemas_dir)
    target = Path(target_dir)
    ledger = assert_schemas_are_consistent(schemas)
    target.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, expected in ledger["sha256"].items():
        source = schemas / name
        destination = target / name
        shutil.copyfile(source, destination)
        actual = _sha256(destination.read_bytes())
        if actual != expected:
            raise SchemaMirrorRefusal(
                f"{destination} is not byte-identical to {source} ({actual} != {expected})")
        written.append(name)
    still_missing = [n for n in ledger["files"] if n not in written]
    if still_missing:
        raise SchemaMirrorRefusal(f"schemas did not reach {target}: {still_missing}")
    return {"target": str(target), "written": written, "sha256": ledger["sha256"]}


class build_py(_build_py):
    """Stock ``build_py`` plus the registry mirror, asserted after the copy."""

    def run(self) -> None:
        super().run()
        result = mirror_schemas(ROOT / "schemas", Path(self.build_lib) / PACKAGE / "schemas")
        self.announce(
            f"mirrored {len(result['written'])} contract files into "
            f"{PACKAGE}/schemas ({result['target']})", level=2)


if __name__ == "__main__":
    # setuptools.build_meta execs this file with __name__ == "__main__"; importing it (as the test
    # suite does, to exercise the very same functions the build actually runs) must NOT build.
    setup(cmdclass={"build_py": build_py})
