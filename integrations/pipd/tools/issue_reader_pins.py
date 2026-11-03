#!/usr/bin/env python3
"""Emit the reader pin set that a plugin candidate must carry.

The plugin's bridge (`scripts/pre_v2.py::OriginalPipd`) refuses to invoke the
original writer unless its pin set equals exactly the reader's files and every
digest matches. That pin set must therefore come from the reader side, describing
a committed tree — never from the candidate that wants to pass.

Scope mirrors the bridge exactly: `<reader_root>/src/pipd_ls_sp/**/*.py` plus
`<reader_root>/schemas/**/*.json`, with keys relative to `reader_root`.

Exit codes: 0 emitted, 2 refused (dirty tree, drifted blob, empty set).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

SCHEMA = "SBL.ORIGINAL_READER_PINS@1"
FOLDERS = (("src/pipd_ls_sp", "*.py"), ("schemas", "*.json"))


class Refusal(Exception):
    pass


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=60)
    if proc.returncode != 0:
        raise Refusal("GIT_FAILED:" + (proc.stderr.decode("utf-8", "replace").strip()[:160] or "unknown"))
    return proc.stdout.decode("utf-8", "strict").strip()


def collect(reader_root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for folder, pattern in FOLDERS:
        base = reader_root / folder
        if not base.is_dir():
            raise Refusal(f"READER_FOLDER_MISSING:{folder}")
        for path in sorted(base.rglob(pattern)):
            if "__pycache__" in path.parts:
                continue
            files[path.relative_to(reader_root).as_posix()] = sha256(path.read_bytes())
    if not files:
        raise Refusal("PIN_SET_EMPTY")
    return files


def pin_set_sha(files: dict[str, str]) -> str:
    payload = "".join(f"{name}\0{digest}\n" for name, digest in sorted(files.items())).encode("utf-8")
    return sha256(payload)


def build(reader_root: Path) -> dict:
    reader_root = reader_root.resolve(strict=True)
    repo = Path(git(reader_root, "rev-parse", "--show-toplevel"))
    status = git(repo, "status", "--porcelain", "--", str(reader_root.relative_to(repo)))
    if status:
        # A pin set describes a committed state; a dirty tree would pin bytes that do
        # not exist at HEAD and silently drift on the next checkout.
        raise Refusal("READER_TREE_DIRTY:" + ";".join(status.splitlines()[:3]))
    files = collect(reader_root)
    head = git(repo, "rev-parse", "HEAD")
    for name, digest in files.items():
        blob = subprocess.run(["git", "-C", str(repo), "cat-file", "blob", f"HEAD:{reader_root.relative_to(repo).as_posix()}/{name}"],
                              capture_output=True, timeout=60)
        if blob.returncode != 0:
            raise Refusal("NOT_COMMITTED:" + name)
        if sha256(blob.stdout) != digest:
            raise Refusal("BLOB_MISMATCH:" + name)
    return {
        "schema": SCHEMA,
        "reader_root": reader_root.relative_to(repo).as_posix(),
        "git_head": head,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "git_dirty": False,
        "file_count": len(files),
        "files": {name: files[name] for name in sorted(files)},
        "pin_set_sha256": pin_set_sha(files),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit the reader pin set for a plugin candidate")
    parser.add_argument("--reader-root", type=Path,
                        default=Path(__file__).resolve().parents[1],
                        help="reader package root (default: the integrations/pipd tree containing this tool)")
    parser.add_argument("--out", type=Path, help="write JSON here instead of stdout")
    args = parser.parse_args(argv)
    try:
        body = build(args.reader_root)
    except Refusal as exc:
        print(json.dumps({"emitted": False, "code": str(exc)}, ensure_ascii=False))
        return 2
    text = json.dumps(body, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8", newline="\n")
        print(json.dumps({"emitted": True, "out": str(args.out), "file_count": body["file_count"],
                          "pin_set_sha256": body["pin_set_sha256"], "git_head": body["git_head"]},
                         ensure_ascii=False))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
