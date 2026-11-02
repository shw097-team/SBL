#!/usr/bin/env python3
"""Write requirements.lock - the resolved runtime closure of this project, pinned exactly.

Walks the declared requirements of each installed distribution starting from the single runtime
dependency declared in pyproject.toml, and records the exact versions found. See the header emitted
into the lock file for what this does and does not pin (it is NOT hash-pinned; see the honest limits).

Usage:
    python tools/build_requirements_lock.py            # write requirements.lock
    python tools/build_requirements_lock.py --check     # exit 1 if the file is stale

Read-only with respect to everything else: it inspects installed metadata and writes exactly one file.
"""

from __future__ import annotations

import argparse
import importlib.metadata as md
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEADER = """# requirements.lock - the RESOLVED runtime closure of pipd-ls-sp, pinned exactly.
#
# WHY THIS FILE EXISTS: `pyproject.toml` declares the runtime requirement as the open range
# `jsonschema>=4.0`, which permits any future 4.x or 5.x. That is a declaration, not a reproduction
# recipe: two installs months apart can resolve to different bytes. This file records the closure that
# was actually present and exercised when the published wheel was verified, so an install can be
# reproduced rather than merely re-resolved.
#
# WHAT IT PINS: exact versions of the transitive closure of `jsonschema`, enumerated by walking the
# declared requirements of each installed distribution (markers with an `extra` are excluded, since no
# extras are requested). Verified on Windows CPython 3.11.9.
#
# HONEST LIMITS - read these before treating this as a supply-chain control:
#   1. NOT HASH-PINNED. Artifact hashes (sha256 of each wheel/sdist) are NOT recorded, because the
#      build environment for this release was network-off and the artifacts could not be fetched to
#      hash them. `pip install --require-hashes` will therefore NOT work against this file. Version
#      pinning narrows the window; it does not close it.
#   2. This is the closure as INSTALLED and TESTED, not a resolution performed by a resolver. It
#      states what was exercised, not what is optimal.
#   3. `rpds-py` and `typing-extensions` arrive through `referencing`; they are listed because they are
#      in the closure, not because this project imports them directly.
#
# Regenerate with: tools/build_requirements_lock.py  (writes this file; see that script for the walk)

"""


def _req_name(spec: str) -> str | None:
    m = re.match(r"^([A-Za-z0-9_.\-]+)", spec.split(";")[0].strip())
    return m.group(1) if m else None


def _declared_runtime_deps() -> list[str]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    names = []
    for spec in data.get("project", {}).get("dependencies", []):
        name = _req_name(spec)
        if name:
            names.append(name)
    return names


def closure() -> list[tuple[str, str]]:
    """Return (name, version) for the transitive closure, deterministically ordered."""
    seen: dict[str, str | None] = {}
    todo = _declared_runtime_deps()
    while todo:
        name = todo.pop(0)
        key = name.lower().replace("_", "-")
        if key in seen:
            continue
        try:
            dist = md.distribution(name)
        except md.PackageNotFoundError:
            seen[key] = None
            continue
        seen[key] = dist.version
        for spec in dist.requires or []:
            req = _req_name(spec)
            if not req:
                continue
            marker = spec.split(";", 1)[1].strip() if ";" in spec else ""
            if marker and "extra" in marker:
                continue
            todo.append(req)
    pinned = [(k, v) for k, v in sorted(seen.items()) if v]
    return pinned


def render() -> str:
    lines = [HEADER, "\n".join("%s==%s" % (n, v) for n, v in closure()), "\n"]
    return "".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="exit 1 if requirements.lock is stale")
    args = ap.parse_args(argv)

    target = ROOT / "requirements.lock"
    want = render()
    if args.check:
        have = target.read_text(encoding="utf-8") if target.exists() else ""
        if have != want:
            print("STALE: requirements.lock does not match the installed closure", file=sys.stderr)
            return 1
        print("OK: requirements.lock matches the installed closure (%d pins)" % len(closure()))
        return 0
    target.write_text(want, encoding="utf-8", newline="\n")
    print("wrote %s (%d pins)" % (target.name, len(closure())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
