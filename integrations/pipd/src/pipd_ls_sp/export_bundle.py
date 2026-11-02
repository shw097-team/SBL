"""Portable export bundle: deterministic ``<name>.tar.gz`` + manifest + checksums.

總藍圖 §5.9.3 defines ``pipd export`` as a *portable export*: it must deliver an
archive, a manifest and checksums.  This module is the bounded, dependency-free
implementation of that bundle.

The bundle is built entirely in memory first (so a refused export writes nothing
anywhere), staged into a sibling directory on the same volume, independently
verified by re-opening the archive and recomputing every member digest, and only
then published atomically through the R5-WO1 publisher shared with the surface
projector.  The destination is resolved by the caller with the existing
``projection.resolve_output_destination`` *before* this module touches disk.
"""
from __future__ import annotations

import gzip
import io
import json
import os
import shutil
import tarfile
from pathlib import Path
from typing import Any

from . import projection
from .errors import (ExportMemberUnsafe, ExportSecretFound,
                     ExportVerificationFailed)
from .util import canonical_json, sha256_bytes, sha256_file, sha256_text, utc_now
from .workspace import secret_scan

BUNDLE_SCHEMA = "PIPD-EXPORT-BUNDLE/1"
MANIFEST_NAME = "export_manifest.json"
SUMS_NAME = "SHA256SUMS"
DEFAULT_INCLUDE = ["schemas", "src", "tests", "docs", "pyproject.toml"]

# Frozen per-member attributes so the archive is byte-deterministic across runs
# and hosts.  No wall-clock, no user/group, no execute bits.
_MEMBER_MTIME = 0
_MEMBER_MODE = 0o644


def _validate_rel(rel: str, root: Path) -> str:
    """Refuse any member path that is absolute, contains ``..`` or escapes root."""
    if not rel:
        raise ExportMemberUnsafe("empty member path in the export set")
    norm = rel.replace("\\", "/")
    if norm.startswith("/") or os.path.isabs(rel) or (len(norm) > 1 and norm[1] == ":"):
        raise ExportMemberUnsafe(f"absolute member path refused: {rel!r}")
    parts = [p for p in norm.split("/") if p not in ("", ".")]
    if ".." in parts:
        raise ExportMemberUnsafe(f"member path contains '..': {rel!r}")
    # Belt-and-braces containment: the real path must stay inside the source root.
    root_key = os.path.normcase(os.path.abspath(str(root)))
    real_key = os.path.normcase(os.path.abspath(os.path.join(str(root), norm)))
    if real_key != root_key and not real_key.startswith(root_key.rstrip("\\/") + os.sep):
        raise ExportMemberUnsafe(f"member path escapes the source root: {rel!r}")
    return "/".join(parts)


def collect_source_files(root: Path, include: list[str] | None = None) -> list[tuple[str, Path]]:
    """The manifest file set, sorted by relative path, with per-member path safety."""
    root = Path(root)
    found: list[tuple[str, Path]] = []
    for rel in include or DEFAULT_INCLUDE:
        target = root / rel
        if target.is_file():
            found.append((rel.replace("\\", "/"), target))
        elif target.is_dir():
            for x in sorted(target.rglob("*")):
                if not x.is_file():
                    continue
                if "__pycache__" in x.parts or ".git" in x.parts:
                    continue
                found.append((str(x.relative_to(root)).replace("\\", "/"), x))
    rows = sorted({rel: p for rel, p in found}.items(), key=lambda kv: kv[0])
    return [(_validate_rel(rel, root), p) for rel, p in rows]


def file_rows(members: list[tuple[str, Path]]) -> list[dict[str, Any]]:
    rows = [{"rel": rel, "size": p.stat().st_size, "sha256": sha256_file(p)}
            for rel, p in members]
    rows.sort(key=lambda r: r["rel"])
    return rows


def manifest_files_digest(rows: list[dict[str, Any]]) -> str:
    return sha256_text(canonical_json([[r["rel"], r["size"], r["sha256"]] for r in rows]))


def _canonical_archive_name(target: Path) -> str:
    name = target.name or "export"
    return f"{name}.tar.gz"


def _build_archive(members: list[tuple[str, Path]]) -> bytes:
    """A deterministic gzip-compressed tar of the member bytes.

    Members are added sorted by rel path, each carrying a fixed mtime/uid/gid/mode,
    and the gzip layer fixes its own header mtime to 0 — so an identical source
    state yields a byte-identical archive.
    """
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.GNU_FORMAT) as tar:
        for rel, path in members:
            data = path.read_bytes()
            info = tarfile.TarInfo(name=rel)
            info.size = len(data)
            info.mtime = _MEMBER_MTIME
            info.mode = _MEMBER_MODE
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.type = tarfile.REGTYPE
            tar.addfile(info, io.BytesIO(data))
    return gzip.compress(raw.getvalue(), mtime=0)


def _sums_lines(rows: list[dict[str, Any]], archive: dict[str, Any]) -> str:
    entries = [(r["rel"], r["sha256"]) for r in rows] + [(archive["name"], archive["sha256"])]
    entries.sort(key=lambda kv: kv[0])
    return "".join(f"{sha}  {rel}\n" for rel, sha in entries)


def plan(root: Path, include: list[str] | None = None) -> dict[str, Any]:
    """The read-only plan for a bundle: file count, manifest digest, archive name."""
    root = Path(root)
    members = collect_source_files(root, include)
    rows = file_rows(members)
    return {"file_count": len(rows), "manifest_sha256": manifest_files_digest(rows),
            "files": rows, "source_root": str(root.resolve(strict=False))}


def _verify_members(archive_bytes: bytes, rows: list[dict[str, Any]]) -> None:
    """Re-open the produced archive and recompute every member digest."""
    expected = {r["rel"]: r for r in rows}
    seen: set[str] = set()
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            if member.name not in expected:
                raise ExportVerificationFailed(
                    f"archive member {member.name!r} is not in the manifest")
            data = tar.extractfile(member).read()
            row = expected[member.name]
            if len(data) != row["size"]:
                raise ExportVerificationFailed(
                    f"member {member.name!r} size {len(data)} != manifest {row['size']}")
            digest = sha256_bytes(data)
            if digest != row["sha256"]:
                raise ExportVerificationFailed(
                    f"member {member.name!r} sha256 {digest} != manifest {row['sha256']}")
            seen.add(member.name)
    missing = sorted(set(expected) - seen)
    if missing:
        raise ExportVerificationFailed(f"archive is missing manifest members {missing}")


def write_bundle(root: Path, target: Path, *, include: list[str] | None = None,
                 authorized_roots=None, allow_replace=None) -> dict[str, Any]:
    """Build, verify, stage and atomically publish a portable export bundle.

    ``target`` MUST already have been resolved by
    ``projection.resolve_output_destination`` — that happens before this call and
    therefore before any create/delete.  Nothing is written until the secret scan,
    the member-path safety check and the in-memory build have all succeeded.
    """
    root = Path(root)
    target = Path(target)

    # 1. Secrets: on any hit, write NOTHING anywhere and refuse typed.
    scan = secret_scan(root)
    if scan["verdict"] != "PASS":
        raise ExportSecretFound(f"secret scan found {len(scan['hits'])} hits")

    # 2. Member set + traversal safety (raises before any disk write).
    members = collect_source_files(root, include)
    rows = file_rows(members)
    archive_name = _canonical_archive_name(target)

    archive_bytes = _build_archive(members)
    manifest = {
        "schema": BUNDLE_SCHEMA,
        "generated_at": utc_now(),
        "source_root": str(root.resolve(strict=False)),
        "file_count": len(rows),
        "archive": {"name": archive_name, "size": len(archive_bytes),
                    "sha256": sha256_bytes(archive_bytes)},
        "files": rows,
    }
    digest = manifest_files_digest(rows)
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    sums_text = _sums_lines(rows, manifest["archive"])

    # 3. Independent verification of the in-memory archive before publishing.
    _verify_members(archive_bytes, rows)

    # 4. Stage on the same volume, verify from disk, publish atomically.
    parent = target.parent
    parent.mkdir(parents=True, exist_ok=True)
    stage = parent / f".{target.name}.pipd-stage-{projection.secrets.token_hex(8)}"
    stage.mkdir(parents=True, exist_ok=False)
    try:
        (stage / archive_name).write_bytes(archive_bytes)
        (stage / MANIFEST_NAME).write_text(manifest_text, encoding="utf-8", newline="")
        (stage / SUMS_NAME).write_text(sums_text, encoding="utf-8", newline="")

        # Re-verify from the staged bytes on disk.
        _verify_members((stage / archive_name).read_bytes(), rows)
        staged_sums = (stage / SUMS_NAME).read_text(encoding="utf-8")
        if staged_sums != sums_text:
            raise ExportVerificationFailed("staged SHA256SUMS does not match the manifest")

        # TOCTOU: re-verify containment/authorization immediately before publish.
        projection._verify_destination(Path(root).expanduser().resolve(strict=False), target,
                                       authorized_roots=authorized_roots)
        replaced, rollback = projection._publish_staged(stage, target)
    finally:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)

    return {
        "verdict": "PASS",
        "mode": "PORTABLE_BUNDLE",
        "out": str(target),
        "schema": BUNDLE_SCHEMA,
        "archive": manifest["archive"],
        "file_count": len(rows),
        "manifest_sha256": digest,
        "secret_scan": scan["verdict"],
        "wrote": sorted([archive_name, MANIFEST_NAME, SUMS_NAME]),
        "destination": {
            "resolved": str(target),
            "authorized_roots": [str(Path(a)) for a in authorized_roots]
                                if authorized_roots else [],
            "replaced": replaced,
            "rollback_pointer": rollback,
            "staged": str(stage),
        },
    }
