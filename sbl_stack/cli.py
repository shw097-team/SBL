"""``sbl-stack`` — the operator entry point for the installable SBL stack.

Every subcommand prints one JSON object and exits non-zero when the operation did not succeed, so a
caller never has to parse prose to find out what happened.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import describe, doctor, install, invoke, load, rollback, selftest, status, uninstall, upgrade
from sbl_core.errors import SBLError


def _emit(payload: dict, ok: bool) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if ok else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sbl-stack", description="installable SBL stack")
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install", help="install the stack into a directory")
    p_install.add_argument("--root", required=True)

    p_doctor = sub.add_parser("doctor", help="verify an installed stack")
    p_doctor.add_argument("--root", required=True)

    p_status = sub.add_parser("status", help="describe an installed stack")
    p_status.add_argument("--root", required=True)

    p_uninstall = sub.add_parser("uninstall", help="remove an installed stack")
    p_uninstall.add_argument("--root", required=True)

    p_selftest = sub.add_parser("selftest", help="run the ordinary journey and two refusals")
    p_selftest.add_argument("--workdir", default=None)

    p_load = sub.add_parser("load", help="import every component the manifest names, after checking digests")
    p_load.add_argument("--root", required=True)

    p_invoke = sub.add_parser("invoke", help="exercise the installed mode gate")
    p_invoke.add_argument("--root", required=True)
    p_invoke.add_argument("--mode", default=None)

    p_upgrade = sub.add_parser("upgrade", help="replace the recorded manifest with a different one")
    p_upgrade.add_argument("--root", required=True)
    p_upgrade.add_argument("--manifest", required=True)

    p_rollback = sub.add_parser("rollback", help="restore the most recent preimage byte for byte")
    p_rollback.add_argument("--root", required=True)

    sub.add_parser("describe", help="print the stack surface")

    args = parser.parse_args(argv)

    try:
        if args.command == "install":
            result = install(args.root)
            return _emit(result, result["ok"])
        if args.command == "doctor":
            result = doctor(args.root)
            return _emit(result, result["ok"])
        if args.command == "status":
            result = status(args.root)
            return _emit(result, result["installed"])
        if args.command == "uninstall":
            result = uninstall(args.root)
            return _emit(result, result["ok"])
        if args.command == "selftest":
            result = selftest(args.workdir)
            return _emit(result, result["ok"])
        if args.command == "load":
            result = load(args.root)
            return _emit(result, result["ok"])
        if args.command == "invoke":
            result = invoke(args.root, args.mode)
            return _emit(result, result["ok"])
        if args.command == "upgrade":
            result = upgrade(args.root, args.manifest)
            return _emit(result, result["ok"])
        if args.command == "rollback":
            result = rollback(args.root)
            return _emit(result, result["ok"])
        if args.command == "describe":
            return _emit(describe(), True)
    except SBLError as exc:
        return _emit(exc.as_dict(), False)
    return _emit({"ok": False, "error": "unhandled command"}, False)


if __name__ == "__main__":
    sys.exit(main())
