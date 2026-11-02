"""Canonical machine-contract registry (exact 19/19, 總藍圖 §7.3)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .errors import ValidationFail

EXPECTED_FAMILIES = 19

# Fallback exact-set in source order; schemas/registry.json is authoritative when present.
SOURCE_ORDER = [
    "ArtifactIdentity", "AuthorityBinding", "RequirementAtom", "ProfileBinding",
    "TechnologyAdmission", "PI-PKG", "PD-PKG", "TraceLink", "TaskSpecSeed",
    "ConstructionContract", "WorkOrderCandidate", "ECP", "TQAEP",
    "ExecutionHandoff", "EvidenceExpectation", "ClaimCeiling",
    "SurfaceProjectionManifest", "GENIEProjectionRef", "ExecutionBindingRef",
]
SEAM_ONLY = {"GENIEProjectionRef": "SCHEMA_SEAM_ONLY_UNTIL_S6",
             "ExecutionBindingRef": "SCHEMA_SEAM_ONLY_UNTIL_S5"}


def _repo_schemas_dir() -> Path:
    """Source-tree fallback: <repo_root>/schemas (keeps in-tree tests/tools working)."""
    return Path(__file__).resolve().parents[2] / "schemas"


def _packaged_schemas_dir() -> Path | None:
    """The schemas/ tree shipped INSIDE the installed package.

    Uses `importlib.resources.files("pipd_ls_sp") / "schemas"`. For a normal
    filesystem (unzipped wheel / editable) install `Path(...)` yields the real
    directory. For a zipped/re-homed install the resource is not a filesystem
    path, so it is materialised with `as_file` and copied to a persistent cache
    (the `as_file` temp dir is removed when its context exits). Returns the
    directory only when it actually contains `registry.json`; never assumes a
    filesystem path exists without checking it.
    """
    try:
        from importlib.resources import as_file, files
    except Exception:  # pragma: no cover - importlib.resources is stdlib on >=3.9
        return None
    try:
        resource = files("pipd_ls_sp") / "schemas"
    except Exception:  # pragma: no cover - package not importable as a resource
        return None
    try:
        direct = Path(resource)
    except TypeError:
        direct = None
    if direct is not None and (direct / "registry.json").is_file():
        return direct
    try:
        with as_file(resource) as materialized:
            mpath = Path(materialized)
            if not (mpath / "registry.json").is_file():
                return None
            return _persist_tree(mpath)
    except Exception:  # pragma: no cover - unreadable/zipped edge
        return None


_PERSISTED: Path | None = None


def _persist_tree(src: Path) -> Path:
    """Copy a materialised (possibly ephemeral) schemas tree to a stable cache."""
    global _PERSISTED
    if _PERSISTED is not None and (_PERSISTED / "registry.json").is_file():
        return _PERSISTED
    import shutil
    import tempfile

    dst = Path(tempfile.mkdtemp(prefix="pipd-schemas-")) / "schemas"
    shutil.copytree(src, dst)
    _PERSISTED = dst
    return dst


def _candidate_schemas_dirs_with_mode() -> list[tuple[str, Path]]:
    """Strict resolution order, tagged with the surface each candidate came from.

    ``OVERRIDE`` = ``$PIPD_SCHEMAS_DIR``; ``INSTALLED`` = the copy packaged inside the
    installed wheel; ``SOURCE`` = the ``<repo>/schemas`` source-tree fallback. This is the
    single owner of the order ``_resolve_schemas_dir`` consumes; it must never be reordered
    (``describe_schemas_source`` reports the SAME order to the operator).
    """
    candidates: list[tuple[str, Path]] = []
    override = os.environ.get("PIPD_SCHEMAS_DIR")
    if override:
        candidates.append(("OVERRIDE", Path(override)))
    packaged = _packaged_schemas_dir()
    if packaged is not None:
        candidates.append(("INSTALLED", packaged))
    candidates.append(("SOURCE", _repo_schemas_dir()))
    return candidates


def _candidate_schemas_dirs() -> list[Path]:
    """Strict resolution order: explicit override, packaged copy, source tree."""
    return [path for _, path in _candidate_schemas_dirs_with_mode()]


def _resolve_schemas_dir_and_mode() -> tuple[Path | None, str, list[str]]:
    """First candidate that contains registry.json, tagged with its surface mode."""
    tried: list[str] = []
    seen: set[str] = set()
    for mode, cand in _candidate_schemas_dirs_with_mode():
        key = str(cand)
        if key in seen:
            continue
        seen.add(key)
        tried.append(key)
        if (cand / "registry.json").is_file():
            return cand, mode, tried
    return None, "NONE", tried


def _resolve_schemas_dir() -> Path:
    """First location that contains registry.json, else typed ValidationFail."""
    resolved, _mode, tried = _resolve_schemas_dir_and_mode()
    if resolved is None:
        raise ValidationFail(
            "no schemas directory containing registry.json; tried: " + "; ".join(tried))
    return resolved


def describe_schemas_source() -> dict[str, Any]:
    """Public report of the schemas surface ``_resolve_schemas_dir`` actually selects.

    ``{"mode": "OVERRIDE"|"INSTALLED"|"SOURCE"|"NONE", "path": str, "tried": [str, ...]}``.
    ``OVERRIDE`` when ``$PIPD_SCHEMAS_DIR`` was selected, ``INSTALLED`` when the packaged
    copy was selected, ``SOURCE`` when the source-tree fallback was selected, and ``NONE``
    when nothing resolved (``path`` is then ``""``). ``tried`` lists the candidates in the
    order they were probed, so a caller can see exactly which surface a verdict came from
    instead of assuming a workspace-local ``schemas/`` convention. This never silently
    falls back to a different copy; it reports what the resolver will consume.
    """
    resolved, mode, tried = _resolve_schemas_dir_and_mode()
    return {"mode": mode, "path": str(resolved) if resolved is not None else "", "tried": tried}


def resolve_for_validate(root: "Path | str") -> tuple[Path | None, str, list[str]]:
    """Resolve the schemas surface ``validate`` consumes, tagged with its mode.

    ``validate`` used to read ``<root>/schemas`` unconditionally, so a cwd without a
    ``schemas/`` tree (e.g. an installed wheel) failed while ``doctor`` succeeded. This
    reuses the EXACT ``OVERRIDE -> INSTALLED -> SOURCE`` order ``_candidate_schemas_dirs_with_mode``
    owns - no second ordering scheme - but lets a workspace-local ``<root>/schemas`` win
    ONLY when it actually contains ``registry.json`` (reported as ``WORKSPACE``), inserted
    ahead of the shared chain. A ``<root>/schemas`` without a ``registry.json`` is skipped
    just like every other candidate; it never displaces a real copy. Returns the same
    ``(path, mode, tried)`` shape as ``_resolve_schemas_dir_and_mode``.
    """
    tried: list[str] = []
    seen: set[str] = set()
    local = Path(root) / "schemas"
    local_key = str(local)
    seen.add(local_key)
    tried.append(local_key)
    if (local / "registry.json").is_file():
        return local, "WORKSPACE", tried
    for mode, cand in _candidate_schemas_dirs_with_mode():
        key = str(cand)
        if key in seen:
            continue
        seen.add(key)
        tried.append(key)
        if (cand / "registry.json").is_file():
            return cand, mode, tried
    return None, "NONE", tried


def load_registry(schemas_dir: Path | None = None) -> dict[str, Any]:
    d = schemas_dir or _resolve_schemas_dir()
    reg_path = d / "registry.json"
    if not reg_path.is_file():
        raise ValidationFail(f"registry missing: {reg_path}")
    data = json.loads(reg_path.read_text(encoding="utf-8"))
    fams = data.get("families") or []
    if len(fams) != EXPECTED_FAMILIES:
        raise ValidationFail(f"registry family count {len(fams)} != {EXPECTED_FAMILIES}")
    names = [f["contract"] for f in fams]
    if names != SOURCE_ORDER:
        raise ValidationFail("registry family order/name diverges from §7.3 exact set")
    for f in fams:
        if not (d / f"{f['contract']}.schema.json").is_file():
            raise ValidationFail(f"schema file missing for {f['contract']}")
        if not f.get("required_fields"):
            raise ValidationFail(f"{f['contract']} has no required_fields")
    return data


def load_schema(contract: str, schemas_dir: Path | None = None) -> dict[str, Any]:
    d = schemas_dir or _resolve_schemas_dir()
    return json.loads((d / f"{contract}.schema.json").read_text(encoding="utf-8"))
