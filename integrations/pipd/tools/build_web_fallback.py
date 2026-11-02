#!/usr/bin/env python3
"""S4POST Stage B: project one frozen Web mount pack into ONE bounded fallback document.

There is no public directory listing for the plugin yet, so the current Web route is a single
markdown document a reader can attach to a conversation or a Knowledge base. This tool builds that
document from a *frozen mount pack* (a directory carrying ``MANIFEST.sha256``) and is fail-closed:
it REFUSES (typed reason, non-zero exit) rather than warn on

  * ``MANIFEST_DIGEST_MISMATCH``  a member's bytes no longer match ``MANIFEST.sha256``
  * ``MEMBER_SYMLINK``            a symlinked member (or pack) is present
  * ``PATH_ESCAPE``               a manifest path escapes the pack root
  * ``UNEXPECTED_EXTRA_FILE``     a file exists in the pack that the manifest does not list
  * ``RELEASE_STAMP_MISSING``     a member document does not stamp the pinned release id AND the
                                  pinned commit (a member naming only one of the two is stale)
  * ``MEMBER_NOT_TEXT``           a member is not UTF-8 text (it could not be embedded verbatim)
  * ``SIZE_CAP_EXCEEDED``         the composed document would exceed the cap (NEVER truncated)
  * ``DESTINATION_EXISTS`` / ``DESTINATION_SYMLINK``  the output file already exists

The document is written with ``O_EXCL`` and stamps ``DOC_MOUNT_ONLY`` plus the member inventory. No
timestamp is embedded, so two builds are byte-identical.

CLI
---
``--mount-pack DIR``      unpacked frozen mount pack (contains MANIFEST.sha256)
``--release-id TEXT``     e.g. v0.1.1-preview.3 (informational stamp)
``--release-commit HEX40`` the commit the members must stamp
``--size-cap BYTES``      hard cap for the composed document (default 524288)
``--out FILE``            destination markdown file (must not exist)
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

MANIFEST_NAME = "MANIFEST.sha256"
FALLBACK_SCHEMA = "PIPD-WEB-FALLBACK/1"
DEFAULT_SIZE_CAP = 524288
HEX40 = re.compile(r"^[0-9a-f]{40}$")


class Refusal(Exception):
    """A fail-closed refusal. ``code`` is the machine-checkable typed reason."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"REFUSED {code}: {detail}")
        self.code = code
        self.detail = detail


def _path_is_symlink(path) -> bool:
    """Seam for tests: a single predicate the destination gate consults."""
    return os.path.islink(path)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_bytes(data: bytes) -> bytes:
    if b"\x00" in data:
        return data
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _is_text_member(data: bytes) -> bool:
    """A member is embeddable verbatim only if it is UTF-8 text with no NUL byte.

    The fallback document is markdown, so a non-text member could only be embedded through a lossy
    ``decode(..., "replace")`` that silently corrupts the source bytes. Fail closed instead.
    """
    if b"\x00" in data:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _parse_manifest(text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        if "  " not in line:
            raise Refusal("MANIFEST_INVALID", f"line has no two-space separator: {line!r}")
        digest, rel = line.split("  ", 1)
        digest, rel = digest.strip(), rel.strip()
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise Refusal("MANIFEST_INVALID", f"digest is not 64 hex chars: {digest!r}")
        entries.append((digest, rel))
    if not entries:
        raise Refusal("MANIFEST_INVALID", "MANIFEST.sha256 lists no members")
    return entries


def _escapes(rel: str) -> bool:
    parts = rel.replace("\\", "/").split("/")
    return (rel.startswith("/") or "\\" in rel or ":" in rel or ".." in parts
            or any(part == "" for part in parts) or parts[0] in (".", ""))


def load_and_verify_pack(mount_pack: Path, release_commit: str,
                         release_id: str | None = None) -> list[tuple[str, str, bytes]]:
    """Return [(rel, sha256, bytes), ...] for a verified, exactly-listed pack."""
    mount_pack = Path(mount_pack)
    if _path_is_symlink(mount_pack):
        raise Refusal("MEMBER_SYMLINK", f"mount pack {mount_pack} is a symlink")
    if not mount_pack.is_dir():
        raise Refusal("MOUNT_PACK_MISSING", f"mount pack is not a directory: {mount_pack}")
    manifest_path = mount_pack / MANIFEST_NAME
    if _path_is_symlink(manifest_path):
        raise Refusal("MEMBER_SYMLINK", f"{manifest_path} is a symlink")
    if not manifest_path.is_file():
        raise Refusal("MANIFEST_MISSING", f"{manifest_path} is absent")
    entries = _parse_manifest(manifest_path.read_text(encoding="utf-8"))

    listed: list[tuple[str, str, bytes]] = []
    listed_paths: set[str] = set()
    for digest, rel in entries:
        if _escapes(rel):
            raise Refusal("PATH_ESCAPE", f"manifest path escapes the pack root: {rel!r}")
        member = mount_pack / rel
        if _path_is_symlink(member):
            raise Refusal("MEMBER_SYMLINK", f"{member} is a symlink")
        if not member.is_file():
            raise Refusal("MANIFEST_MEMBER_MISSING", f"manifest lists {rel} but it is absent")
        data = member.read_bytes()
        actual = _sha256(_canonical_bytes(data))
        if actual != digest:
            raise Refusal("MANIFEST_DIGEST_MISMATCH",
                          f"{rel}: copied digest {digest} != computed {actual}")
        if not _is_text_member(data):
            raise Refusal("MEMBER_NOT_TEXT",
                          f"{rel} is not UTF-8 text; refusing to embed it in a markdown document")
        listed_paths.add(rel)
        listed.append((rel, digest, data))

    on_disk: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(mount_pack, followlinks=False):
        dirnames.sort()
        filenames.sort()
        for d in dirnames:
            if _path_is_symlink(Path(dirpath) / d):
                raise Refusal("MEMBER_SYMLINK", str(Path(dirpath) / d))
        for f in filenames:
            p = Path(dirpath) / f
            if _path_is_symlink(p):
                raise Refusal("MEMBER_SYMLINK", str(p))
            rel = p.relative_to(mount_pack).as_posix()
            if rel == MANIFEST_NAME:
                continue
            on_disk.add(rel)
    extra = sorted(on_disk - listed_paths)
    if extra:
        raise Refusal("UNEXPECTED_EXTRA_FILE", f"pack carries unlisted file(s): {extra}")

    for rel, _digest, data in listed:
        if not rel.endswith(".md"):
            continue
        text = data.decode("utf-8")
        if release_commit not in text:
            raise Refusal("RELEASE_STAMP_MISSING",
                          f"{rel} does not stamp the pinned release commit {release_commit}")
        if release_id and release_id not in text:
            raise Refusal("RELEASE_STAMP_MISSING",
                          f"{rel} does not stamp the release id {release_id}; a member that names "
                          "the pinned commit but not the release is a stale release stamp")
    return listed


def compose_document(release_id: str, release_commit: str,
                     members: list[tuple[str, str, bytes]], size_cap: int) -> bytes:
    """Compose the single bounded markdown document (no truncation anywhere)."""
    lines: list[str] = [
        f"<!-- {FALLBACK_SCHEMA} DOC_MOUNT_ONLY -->",
        "# PIPD-LS-SP S4 Web fallback — single-document mount (DOC_MOUNT_ONLY)",
        "",
        f"- release_id: {release_id}",
        f"- release_commit: {release_commit}",
        "- doc_mount_only: true",
        f"- member_count: {len(members)}",
        f"- size_cap_bytes: {size_cap}",
        "",
        "> DOC_MOUNT_ONLY: this is a document drop, not an installed plugin, not a host-registered",
        "> skill and not a public directory listing (none exists yet). It executes nothing. Verify a",
        "> member against the inventory below before you rely on it.",
        "",
        "## Member inventory",
        "",
        "| member | sha256 |",
        "| --- | --- |",
    ]
    for rel, digest, _data in members:
        lines.append(f"| {rel} | {digest} |")
    for rel, _digest, data in members:
        lines += ["", f"## Member: {rel}", "", f"<!-- BEGIN MEMBER {rel} -->"]
        lines.append(data.decode("utf-8", "replace"))
        lines.append(f"<!-- END MEMBER {rel} -->")
    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    return text.encode("utf-8")


def write_exclusive(out_path: Path, data: bytes) -> None:
    out_path = Path(out_path)
    if _path_is_symlink(out_path):
        raise Refusal("DESTINATION_SYMLINK", f"destination {out_path} is a symlink")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(out_path, flags, 0o644)
    except FileExistsError as exc:
        raise Refusal("DESTINATION_EXISTS",
                      f"destination {out_path} already exists; refusing to overwrite") from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
    except BaseException:
        if out_path.exists() and not _path_is_symlink(out_path):
            out_path.unlink()
        raise


def build_fallback(*, mount_pack: Path, release_id: str, release_commit: str, out_path: Path,
                   size_cap: int = DEFAULT_SIZE_CAP) -> dict:
    if not HEX40.match(str(release_commit)):
        raise Refusal("RELEASE_COMMIT_INVALID",
                      f"release commit is not 40 hex chars: {release_commit!r}")
    if size_cap <= 0:
        raise Refusal("SIZE_CAP_INVALID", f"size cap must be positive: {size_cap!r}")
    members = load_and_verify_pack(mount_pack, release_commit, release_id)
    document = compose_document(release_id, release_commit, members, size_cap)
    if len(document) > size_cap:
        raise Refusal("SIZE_CAP_EXCEEDED",
                      f"composed document is {len(document)} bytes > cap {size_cap}; "
                      "refusing to truncate")
    write_exclusive(Path(out_path), document)
    return {
        "verdict": "BUILT",
        "out": str(out_path),
        "bytes": len(document),
        "sha256": _sha256(document),
        "member_count": len(members),
        "doc_mount_only": True,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mount-pack", required=True)
    ap.add_argument("--release-id", required=True)
    ap.add_argument("--release-commit", required=True)
    ap.add_argument("--size-cap", type=int, default=DEFAULT_SIZE_CAP)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    try:
        report = build_fallback(
            mount_pack=Path(args.mount_pack),
            release_id=args.release_id,
            release_commit=args.release_commit,
            out_path=Path(args.out),
            size_cap=args.size_cap,
        )
    except Refusal as exc:
        print(str(exc))
        return 2
    print(f"BUILT {report['out']} bytes={report['bytes']} sha256={report['sha256']} "
          f"members={report['member_count']} DOC_MOUNT_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
