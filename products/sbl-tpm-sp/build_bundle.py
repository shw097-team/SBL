#!/usr/bin/env python3
"""Derive the sbl-tpm-sp skills bundle from the single PIPD skill source.

The eight PIPD skills exist once, in ``integrations/pipd/skills/``. This script copies them into
the plugin bundle and writes a manifest that binds every file to a sha256 — so the bundle is a
build product, not a second hand-maintained copy. It never copies the compiler: a bundle that
contains ``pipd_ls_sp`` source would be the second compiler this migration exists to prevent, and
the script fails closed on that.

Usage:
    python build_bundle.py --source ../../integrations/pipd/skills --out dist/sbl-tpm-sp-skills
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

BUNDLE_ID = "sbl-tpm-sp/skills-bundle@1"
EXPECTED_SKILLS = 8
FORBIDDEN_NAMES = {"pipd_ls_sp", "src", "pipeline.py", "cli.py"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _frontmatter_name(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise SystemExit(f"SKILL_MISSING_FRONTMATTER: {skill_md}")
    for line in text.splitlines()[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    raise SystemExit(f"SKILL_MISSING_NAME: {skill_md}")


def build(source: Path, out: Path) -> dict:
    if not source.is_dir():
        raise SystemExit(f"SKILL_SOURCE_MISSING: {source}")
    packs = sorted(p for p in source.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
    if len(packs) != EXPECTED_SKILLS:
        raise SystemExit(f"SKILL_COUNT_MISMATCH: expected {EXPECTED_SKILLS}, found {len(packs)}")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    entries, seen = [], set()
    for pack in packs:
        name = _frontmatter_name(pack / "SKILL.md")
        if name in seen:
            raise SystemExit(f"SKILL_NAME_DUPLICATE: {name}")
        seen.add(name)
        target = out / "skills" / name
        shutil.copytree(pack, target)
        for f in sorted(target.rglob("*")):
            if f.is_file():
                rel = f.relative_to(out).as_posix()
                entries.append({"path": rel, "sha256": _sha256(f), "bytes": f.stat().st_size})

    # Fail closed on a compiler copy: the bundle must stay a skills bundle.
    for entry in entries:
        parts = set(Path(entry["path"]).parts)
        if parts & FORBIDDEN_NAMES or entry["path"].endswith(("pipeline.py", "cli.py")):
            raise SystemExit(f"BUNDLE_CONTAINS_COMPILER: {entry['path']}")

    manifest = {
        "schema": BUNDLE_ID,
        "source": source.as_posix(),
        "skill_count": len(seen),
        "skills": sorted(seen),
        "files": entries,
        "bundle_sha256": hashlib.sha256(
            "".join(e["path"] + e["sha256"] for e in entries).encode()).hexdigest(),
    }
    (out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                                       encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path,
                    default=Path(__file__).resolve().parents[2] / "integrations" / "pipd" / "skills")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "dist" / "sbl-tpm-sp-skills")
    args = ap.parse_args(argv)
    manifest = build(args.source.resolve(), args.out.resolve())
    print(json.dumps({"ok": True, "out": args.out.as_posix(),
                      "skill_count": manifest["skill_count"],
                      "bundle_sha256": manifest["bundle_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
