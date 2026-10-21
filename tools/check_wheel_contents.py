#!/usr/bin/env python3
"""Build the wheel and assert the data files a runtime needs are actually inside it.

Why this exists: ``pip install -e .`` — which is what CI used to run — resolves every import and every
data file straight out of the source tree, so a missing ``[tool.setuptools.package-data]`` entry is
invisible to the whole test suite. It is not invisible to a user: the installed wheel shipped without
``sbl_sp/manifests/*.json``, so every ``load_manifest`` call in an installed package raised
``SBL_E_UNKNOWN_SP`` while the source tree was green (found in the round-4 Docker sandbox).

    python tools/check_wheel_contents.py

Exit 0 only when the built wheel carries every required member.
"""

from __future__ import annotations

import os
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUIRED_PREFIXES = (
    "sbl_core/",
    "sbl_sp/manifests/",
    "sbl_sp/plugins/schema/",
    "sbl_cli/",
    "sbl_stack/",
    "sbl_harness/",
)
REQUIRED_EXACT = (
    "sbl_sp/manifests/tpm_sp.json",
    "sbl_sp/manifests/commander_sp.json",
    "sbl_sp/manifests/external_challenge_sp.json",
    "sbl_sp/plugins/schema/plugin.schema.json",
    "sbl_sp/plugins/tpm_sp/SKILL.md",
    "sbl_sp/plugins/commander_sp/SKILL.md",
    "sbl_sp/plugins/external_challenge_sp/SKILL.md",
    "sbl_stack/SKILL.md",
)


def build_wheel(out_dir: Path) -> Path:
    import setuptools.build_meta as build_meta

    previous = Path.cwd()
    os.chdir(ROOT)
    try:
        name = build_meta.build_wheel(str(out_dir))
    finally:
        os.chdir(previous)
    return out_dir / name


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        wheel = build_wheel(Path(tmp))
        with zipfile.ZipFile(wheel) as archive:
            members = archive.namelist()
        missing_exact = [name for name in REQUIRED_EXACT if name not in members]
        missing_prefix = [
            prefix for prefix in REQUIRED_PREFIXES if not any(m.startswith(prefix) for m in members)
        ]
        problems = missing_exact + [f"no member under {prefix}" for prefix in missing_prefix]
        print(f"wheel={wheel.name} members={len(members)}")
        for name in REQUIRED_EXACT:
            print(("  OK   " if name in members else "  MISS ") + name)
        if problems:
            print("FAIL: the wheel is missing runtime data", file=sys.stderr)
            for problem in problems:
                print("  - " + problem, file=sys.stderr)
            return 2
    print("wheel contents OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
