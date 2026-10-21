"""``sbl-harness`` — install/doctor/uninstall the HGK adapter.

Same contract as ``sbl-stack``: one JSON object per command, non-zero exit when the operation did not
succeed. ``probe`` is read-only and is the command to run before believing anything else.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import doctor, install, probe, uninstall
from sbl_core.errors import SBLError


def _emit(payload: dict, ok: bool) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if ok else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sbl-harness", description="HGK harness adapter")
    sub = parser.add_subparsers(dest="command", required=True)

    p_probe = sub.add_parser("probe", help="read-only probe of an HGK root")
    p_probe.add_argument("--root", default=None)

    p_install = sub.add_parser("install", help="install the adapter into a directory")
    p_install.add_argument("--target", required=True)
    p_install.add_argument("--hgk-root", default=None)

    p_doctor = sub.add_parser("doctor", help="verify an installed adapter")
    p_doctor.add_argument("--target", required=True)

    p_uninstall = sub.add_parser("uninstall", help="remove an installed adapter")
    p_uninstall.add_argument("--target", required=True)

    args = parser.parse_args(argv)

    try:
        if args.command == "probe":
            result = probe(args.root)
            return _emit(result, result["status"] == "ROOT_READY")
        if args.command == "install":
            result = install(args.target, args.hgk_root)
            return _emit(result, result["ok"])
        if args.command == "doctor":
            result = doctor(args.target)
            return _emit(result, result["ok"])
        if args.command == "uninstall":
            result = uninstall(args.target)
            return _emit(result, result["ok"])
    except SBLError as exc:
        return _emit(exc.as_dict(), False)
    return _emit({"ok": False, "error": "unhandled command"}, False)


if __name__ == "__main__":
    sys.exit(main())
