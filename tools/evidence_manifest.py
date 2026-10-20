"""Build or verify a sorted evidence manifest (relative path, bytes, sha256).

The manifest never contains its own digest; the caller records `manifest_sha256` separately.
`--verify` recomputes every entry and the declared count, and reports mismatches.

Usage:
  python tools/evidence_manifest.py --root . --include evidence contracts _governance --out evidence/EVIDENCE_MANIFEST.json
  python tools/evidence_manifest.py --root . --verify evidence/EVIDENCE_MANIFEST.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".pytest_tmp", ".venv", "venv", ".sbl-tests"}
SKIP_NAMES = {"EVIDENCE_MANIFEST.json"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(root: Path, includes: list[str]) -> list[Path]:
    files: list[Path] = []
    for inc in includes:
        base = root / inc
        if base.is_file():
            files.append(base)
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                if name in SKIP_NAMES:
                    continue
                files.append(Path(dirpath) / name)
    return sorted(set(files))


def build(root: Path, includes: list[str]) -> dict:
    entries = []
    for path in walk(root, includes):
        rel = path.relative_to(root).as_posix()
        entries.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    entries.sort(key=lambda row: row["path"])
    return {
        "schema": "SBL-EVIDENCE-MANIFEST/1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "root": ".",
        "includes": includes,
        "count": len(entries),
        "total_bytes": sum(row["bytes"] for row in entries),
        "entries": entries,
        "note": "The manifest excludes itself; its own digest must be recorded by the caller.",
    }


def verify(root: Path, manifest_path: Path) -> dict:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    mismatches, missing = [], []
    for row in data.get("entries", []):
        path = root / row["path"]
        if not path.is_file():
            missing.append(row["path"])
            continue
        digest = sha256_file(path)
        if digest != row["sha256"] or path.stat().st_size != row["bytes"]:
            mismatches.append({"path": row["path"], "recorded": row["sha256"], "actual": digest})
    declared = data.get("count")
    return {
        "ok": not mismatches and not missing and declared == len(data.get("entries", [])),
        "declared_count": declared,
        "entries": len(data.get("entries", [])),
        "mismatches": mismatches,
        "missing": missing,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--include", nargs="*", default=["evidence", "contracts", "_governance"])
    ap.add_argument("--out", default="evidence/EVIDENCE_MANIFEST.json")
    ap.add_argument("--verify", default="")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if args.verify:
        result = verify(root, root / args.verify)
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 0 if result["ok"] else 1
    payload = build(root, args.include)
    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"manifest": str(out), "count": payload["count"], "total_bytes": payload["total_bytes"],
                      "manifest_sha256": sha256_file(out)}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
