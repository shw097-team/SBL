#!/usr/bin/env python3
"""Emit the three installable specialised-principal packages and their provenance table.

    python tools/build_sp_plugins.py --out-dir dist/plugins

This produces ZIPs, not installations. The tool prints the same ceiling the packages carry
(``HOST_PENDING``); a host-side human turns a ZIP into an effective load, and only the host can
issue a plugin id.

Every package is re-opened from its own bytes after the ZIP is closed and validated against the
vendored portable schema before the tool reports success. A package that fails validation makes this
tool exit non-zero: the earlier build emitted ``"schema": "SBL-AGENT-PLUGIN/1"`` with no ``$schema``
at all, which looked fine to ``json.loads`` and was not a portable plugin manifest.
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

from sbl_sp.plugins import (  # noqa: E402
    CLAIM_CEILING,
    PLUGIN_SCHEMA_URI,
    build_all,
    inspect_package,
)
from sbl_sp.plugins import portable  # noqa: E402

SCHEMA_FILE = portable.SCHEMA_PATH


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="build the three SBL specialised-principal packages")
    parser.add_argument("--out-dir", default="dist/plugins")
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args(argv)

    packages = build_all(args.out_dir)

    verifications = []
    for package in packages:
        report = inspect_package(package["path"])
        verifications.append(report)
        if report["schema_violations"] or report["skill_violations"]:
            payload = {"ok": False, "package": package["plugin_name"], "report": report}
            print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
            return 2
        if report["plugin_schema"] != PLUGIN_SCHEMA_URI:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "package": package["plugin_name"],
                        "reason": "plugin.json does not declare the portable $schema",
                        "found": report["plugin_schema"],
                    },
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return 2
        if report["sha256"] != package["sha256"]:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "package": package["plugin_name"],
                        "reason": "sha256 changed between build and readback",
                    },
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return 2

    payload = {
        "schema": "SBL-SP-PLUGIN-SET/2",
        "claim_ceiling": CLAIM_CEILING,
        "portable_schema": PLUGIN_SCHEMA_URI,
        "portable_schema_sha256": hashlib.sha256(SCHEMA_FILE.read_bytes()).hexdigest(),
        "packages": packages,
        "verification": [
            {
                "plugin_name": report["plugin_name"],
                "sha256": report["sha256"],
                "entries": report["entries"],
                "schema_violations": report["schema_violations"],
                "skill_violations": report["skill_violations"],
            }
            for report in verifications
        ],
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
