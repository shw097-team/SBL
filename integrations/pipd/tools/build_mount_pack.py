#!/usr/bin/env python3
"""WO-S4-WEB-02: build and verify the one versioned Web/ChatGPT mount pack.

This tool is the *only* writer for ``dist/mount/**``. It does three determinism-critical things,
and nothing else:

1. It derives ``MANIFEST.sha256`` **from the actual pack files** (relative POSIX paths, sorted,
   ``"<sha256>  <relpath>"`` one per line) and rewrites it into the pack root.
2. It builds the ZIP byte-identically on every run with the same inputs: entries rooted at the pack
   directory name, fixed ``ZipInfo.date_time`` (the 1980 ZIP epoch), fixed permission bits, fixed
   compression. ``MANIFEST.sha256`` is written **last** (the first manifest entry is therefore the
   last archive entry).
3. ``--verify`` recomputes the digest of every manifest-listed member from the ZIP bytes themselves
   and refuses, by name, any mutation, missing member, unmanifested member, or path that escapes the
   pack root. It never writes.

The tool declares no runtime authority: it is a stdlib-only build/verify utility, candidate-only.

CLI
---
``--pack-root DIR --out-zip FILE``   rebuild MANIFEST.sha256, then the ZIP (+ ``.sha256`` sidecar).
``--verify FILE``                    recompute and compare; exit 0 on PASS, non-zero on any refusal.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

MANIFEST_NAME = "MANIFEST.sha256"
# The ZIP epoch. A constant date_time makes the archive reproducible across runs (zips otherwise
# embed the wall-clock mtime of each member).
FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)
COMPRESS_LEVEL = 9


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _member_bytes(path: Path) -> bytes:
    """The CANONICAL bytes of a pack member (EOL-normalised for text).

    S4EXT-R1 (F-S4EXT-008, found while repairing F001): the ZIP published as
    ``v0.1.1-preview.3`` captured CRLF member bytes -- it was built from a CRLF checkout, before
    ``.gitattributes`` pinned ``* text=auto eol=lf`` -- so its 8 members (and the manifest it
    embeds) do not match the same members in the LF-normalised tree, and the published bytes were
    NOT reproducible from the repository. Canonicalising text members to LF here means the
    manifest and the archive members are derived from ONE byte sequence, so a rebuild of the same
    source is byte-identical on any platform. Binary members (NUL byte / non-UTF-8) are never
    rewritten. ``verify_pack`` is deliberately NOT changed: it must keep re-deriving a member's
    digest from the bytes actually inside the ZIP.
    """
    data = path.read_bytes()
    if b"\x00" in data:
        return data
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _content_files(pack_root: Path) -> list[Path]:
    """Every real file under the pack root except the manifest itself, sorted by rela. POSIX path."""
    files = [
        p for p in pack_root.rglob("*")
        if p.is_file() and p.name != MANIFEST_NAME
    ]
    return sorted(files, key=lambda p: p.relative_to(pack_root).as_posix())


def _manifest_text(pack_root: Path, files: list[Path]) -> str:
    lines = [
        f"{_sha256_bytes(_member_bytes(f))}  {f.relative_to(pack_root).as_posix()}"
        for f in files
    ]
    return ("\n".join(lines) + "\n") if lines else ""


def _write_member(zf: zipfile.ZipFile, arcname: str, data: bytes) -> None:
    info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16  # fixed permission bits, no host-specific metadata
    info.create_system = 0            # fixed "creator" so the header bytes are stable
    zf.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=COMPRESS_LEVEL)


def build_pack(pack_root: Path, out_zip: Path) -> dict:
    """Rebuild MANIFEST.sha256 from the pack files, then the ZIP. Returns a small report."""
    pack_root = Path(pack_root).resolve()
    out_zip = Path(out_zip).resolve()
    if not pack_root.is_dir():
        raise FileNotFoundError(f"pack root is not a directory: {pack_root}")

    files = _content_files(pack_root)
    manifest_text = _manifest_text(pack_root, files)
    manifest_bytes = manifest_text.encode("utf-8")
    (pack_root / MANIFEST_NAME).write_bytes(manifest_bytes)

    root_name = pack_root.name
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=COMPRESS_LEVEL) as zf:
        for f in files:
            rel = f.relative_to(pack_root).as_posix()
            _write_member(zf, f"{root_name}/{rel}", _member_bytes(f))
        # MANIFEST.sha256 is the LAST archive entry (its first content line is written last).
        _write_member(zf, f"{root_name}/{MANIFEST_NAME}", manifest_bytes)

    digest = _sha256_bytes(out_zip.read_bytes())
    sidecar = out_zip.with_name(out_zip.name + ".sha256")
    sidecar.write_bytes(f"{digest}  {out_zip.name}\n".encode("utf-8"))
    return {
        "pack_root": str(pack_root),
        "out_zip": str(out_zip),
        "members": len(files) + 1,  # content files + the manifest
        "zip_sha256": digest,
        "sidecar": str(sidecar),
    }


def _parse_manifest(text: str) -> list[tuple[str, str]]:
    """Parse ``"<sha256>  <relpath>"`` lines. Returns [(digest, relpath), ...]."""
    entries: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        if "  " not in line:
            raise ValueError(f"malformed manifest line (no two-space separator): {line!r}")
        digest, rel = line.split("  ", 1)
        entries.append((digest.strip(), rel.strip()))
    return entries


def verify_pack(zip_path: Path) -> tuple[bool, list[str]]:
    """Recompute the manifest from the ZIP bytes. Returns (ok, problems)."""
    zip_path = Path(zip_path).resolve()
    problems: list[str] = []
    if not zip_path.is_file():
        return False, [f"ZIP_NOT_FOUND: {zip_path}"]

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()

        # 1. No member may escape the pack root (no absolute path, no '..', no backslash).
        for name in names:
            parts = name.split("/")
            if (name.startswith("/") or ".." in parts or "\\" in name
                    or parts[0] in ("", ".")):
                problems.append(f"ESCAPES_PACK_ROOT: {name}")

        if not names:
            return False, ["EMPTY_ZIP"]
        root_name = names[0].split("/")[0]
        manifest_arcname = f"{root_name}/{MANIFEST_NAME}"
        if manifest_arcname not in names:
            return False, [f"MANIFEST_MISSING: {MANIFEST_NAME}"]

        # 2. Every member must live under the single pack-root segment.
        for name in names:
            if not name.startswith(root_name + "/"):
                problems.append(f"OUTSIDE_PACK_ROOT: {name}")

        entries = _parse_manifest(zf.read(manifest_arcname).decode("utf-8"))
        if not entries:
            problems.append("MANIFEST_EMPTY")

        manifest_paths = set()
        for digest, rel in entries:
            manifest_paths.add(rel)
            arcname = f"{root_name}/{rel}"
            if arcname not in names:
                problems.append(f"MANIFEST_ENTRY_NOT_IN_ZIP: {rel}")
                continue
            actual = _sha256_bytes(zf.read(arcname))
            if actual != digest:
                problems.append(f"MUTATED_MEMBER: {rel}")

        # 3. Every content member (i.e. everything but the manifest) must be listed.
        for name in names:
            if name == manifest_arcname:
                continue
            rel = name[len(root_name) + 1:]
            if rel not in manifest_paths:
                problems.append(f"UNMANIFESTED_FILE: {rel}")

    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack-root", help="pack authoring directory (its name roots the ZIP)")
    ap.add_argument("--out-zip", help="destination ZIP path when building")
    ap.add_argument("--verify", help="verify an existing ZIP; exit 0 on PASS, non-zero on refusal")
    args = ap.parse_args(argv)

    if args.verify:
        ok, problems = verify_pack(Path(args.verify))
        if ok:
            print(f"VERIFY PASS: {args.verify}")
            return 0
        print(f"VERIFY FAIL: {args.verify}")
        for p in problems:
            print(f"  - {p}")
        return 1

    if not args.pack_root or not args.out_zip:
        ap.error("either --verify FILE, or both --pack-root DIR and --out-zip FILE, are required")
    report = build_pack(Path(args.pack_root), Path(args.out_zip))
    print(
        "BUILD OK: "
        f"pack_root={report['pack_root']} "
        f"out_zip={report['out_zip']} "
        f"members={report['members']} "
        f"zip_sha256={report['zip_sha256']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
