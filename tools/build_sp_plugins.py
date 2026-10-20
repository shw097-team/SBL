#!/usr/bin/env python3
"""Emit the three installable specialised-principal packages and their provenance table.

    python tools/build_sp_plugins.py --out-dir dist/plugins

This produces ZIPs, not installations. The tool prints the same ceiling the packages carry
(``HOST_PENDING``); a host-side human turns a ZIP into an effective load, and only the host can
issue a plugin id.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sbl_sp.plugins import CLAIM_CEILING, build_all  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="build the three SBL specialised-principal packages")
    parser.add_argument("--out-dir", default="dist/plugins")
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args(argv)
    packages = build_all(args.out_dir)
    payload = {
        "schema": "SBL-SP-PLUGIN-SET/1",
        "claim_ceiling": CLAIM_CEILING,
        "packages": packages,
        "note": "a package is not an installation; plugin ids are issued by the host",
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        Path(args.json_out).write_text(text, encoding="utf-8")
    print(text, end="")
    print(f"set_sha256 {hashlib.sha256(text.encode('utf-8')).hexdigest()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
