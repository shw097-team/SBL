#!/usr/bin/env python3
"""Build a repinned `sbl-tpm-sp` candidate from a base tree.

The first 0.3.1-rc.1 was assembled by hand in a session directory: unzip the previous
candidate, bump two manifests, drop in the reader's pin set, clean caches, zip. That is a
reproducible *procedure* but it lived nowhere durable, so nobody could re-derive or verify
the artifact later. This tool is that procedure, with the same output.

Two rules it encodes:

* **The pins are an input, not something this tool invents.** They come from
  `integrations/pipd/tools/issue_reader_pins.py`, which reads the reader at a named commit.
  A build tool that generated its own pin set would make the bridge's check circular.
* **Byte identity depends on file timestamps** unless `--normalise-timestamps` is passed.
  The published `0.3.1-rc.1` (`f00c5792…`) preserved the tree's mtimes; normalising produces a
  different, equally valid digest. The flag exists so a future build can be timestamp-independent
  on purpose rather than by accident.

Usage:

    python tools/build_tpm_sp_candidate.py \
        --tree /path/to/extracted/sbl-tpm-sp \
        --version 0.3.1-rc.1 \
        --pins READER_PINS.json --signature READER_PINS.owner.sig.json \
        --out sbl-tpm-sp-0.3.1-rc.1-private.zip
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

MANIFESTS = ("plugin.json", ".codex-plugin/plugin.json")
PINS_DIR = "references/reader-pins"
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".git"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


class BuildError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildError("MANIFEST_UNREADABLE", f"{path}: {exc}") from exc


def set_version(tree: Path, version: str) -> list[str]:
    """Write `version` into every manifest that exists. Refuses a tree with none."""
    touched = []
    for rel in MANIFESTS:
        path = tree / rel
        if not path.is_file():
            continue
        data = _read_json(path)
        if data.get("name") != "sbl-tpm-sp":
            raise BuildError("MANIFEST_NAME_MISMATCH", f"{path}: {data.get('name')!r}")
        data["version"] = version
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        touched.append(rel)
    if not touched:
        raise BuildError("NO_MANIFEST", f"{tree} has none of {MANIFESTS}")
    return touched


def install_pins(tree: Path, pins: Path, signature: Path | None) -> dict:
    payload = _read_json(pins)
    if payload.get("schema") != "SBL.ORIGINAL_READER_PINS@1":
        raise BuildError("PINS_SCHEMA_UNEXPECTED", str(payload.get("schema")))
    digest = payload.get("pin_set_sha256")
    if not digest or len(digest) != 64:
        raise BuildError("PINS_DIGEST_MISSING", str(digest))
    if int(payload.get("file_count", 0)) != len(payload.get("files") or {}):
        raise BuildError("PINS_COUNT_MISMATCH", f"file_count={payload.get('file_count')} listed={len(payload.get('files') or {})}")

    dest = tree / PINS_DIR
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pins, dest / "READER_PINS.json")
    if signature is not None:
        sig = _read_json(signature)
        if sig.get("pin_set_sha256") and sig["pin_set_sha256"] != digest:
            raise BuildError("SIGNATURE_DIGEST_MISMATCH", "signature covers a different pin set")
        shutil.copy2(signature, dest / "READER_PINS.owner.sig.json")
    return {"file_count": payload["file_count"], "pin_set_sha256": digest, "git_head": payload.get("git_head")}


def clean(tree: Path) -> int:
    removed = 0
    for path in sorted(tree.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and path.name in SKIP_DIRS:
            shutil.rmtree(path, ignore_errors=True)
            removed += 1
        elif path.is_file() and path.suffix in SKIP_SUFFIXES:
            path.unlink(missing_ok=True)
            removed += 1
    return removed


def members(tree: Path) -> list[Path]:
    out = []
    for path in tree.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in SKIP_SUFFIXES:
            continue
        out.append(path)
    return sorted(out, key=lambda p: p.relative_to(tree.parent).as_posix())


def zip_tree(tree: Path, out: Path, normalise: bool = False) -> dict:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    files = members(tree)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            info = zipfile.ZipInfo.from_file(path, path.relative_to(tree.parent).as_posix())
            if normalise:
                info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(path, "rb") as fh:
                zf.writestr(info, fh.read())
    blob = out.read_bytes()
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    return {
        "path": str(out),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "bytes": len(blob),
        "members": len(names),
        "skills": sum(1 for n in names if n.endswith("SKILL.md")),
        "bytecode": sum(1 for n in names if n.endswith((".pyc", ".pyo")) or "__pycache__" in n),
    }


def build(tree: Path, version: str, pins: Path, signature: Path | None, out: Path,
          normalise: bool = False) -> dict:
    tree = tree.resolve()
    if not (tree / "plugin.json").is_file() and not (tree / ".codex-plugin" / "plugin.json").is_file():
        raise BuildError("NOT_A_PLUGIN_TREE", str(tree))
    manifests = set_version(tree, version)
    pin_info = install_pins(tree, pins, signature)
    cleaned = clean(tree)
    report = zip_tree(tree, out, normalise=normalise)
    report.update({"version": version, "manifests": manifests, "cleaned": cleaned,
                   "pins": pin_info, "normalised": normalise})
    if report["bytecode"]:
        raise BuildError("BYTECODE_IN_ARTIFACT", f"{report['bytecode']} files")
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build a repinned sbl-tpm-sp candidate.")
    ap.add_argument("--tree", required=True, type=Path, help="extracted plugin directory (contains plugin.json)")
    ap.add_argument("--version", required=True)
    ap.add_argument("--pins", required=True, type=Path)
    ap.add_argument("--signature", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--normalise-timestamps", action="store_true",
                    help="fixed 1980 timestamps, so the digest does not depend on mtimes")
    args = ap.parse_args(argv)
    try:
        report = build(args.tree, args.version, args.pins, args.signature, args.out,
                       normalise=args.normalise_timestamps)
    except BuildError as exc:
        # Same shape as issue_reader_pins.py: a refusal is JSON with a code, exit 2.
        print(json.dumps({"code": exc.code, "detail": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
