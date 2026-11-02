#!/usr/bin/env python3
"""Assert that an INSTALLED wheel resolved its OWN packaged contract registry (S4R3-F006).

Why this is a tool and not an inline CI heredoc: the first version of this gate lived only inside
`.github/workflows/ci.yml`, so it was never executed locally and its type error (it asserted that the
doctor's `families` was a dict, when `workspace.doctor` reports the family COUNT as an int) first
surfaced as a red hosted run. A gate that cannot be run locally cannot be falsified locally. This file
is the single implementation; CI calls it and the unit tests in
`tests/test_standard_wheel_schemas.py` call it with mutated inputs.

Exit code 0 means the claim holds. Any other exit code means it does not, with a typed line on stderr.

Usage:
    verify_installed_wheel_registry.py wheel-doctor.log [--expect-families 19]
                                                       [--deny-prefix <path>]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


def _fail(code: str, detail: str) -> int:
    print(f"{code}: {detail}", file=sys.stderr)
    return 1


def _resolved_path_inside(doc: dict[str, Any]) -> str | None:
    source = doc.get("schema_source")
    if not isinstance(source, dict):
        return None
    path = source.get("path")
    return path if isinstance(path, str) and path.strip() else None


def check(doc: Any, expect_families: int, deny_prefix: str | None) -> tuple[int, str]:
    """Return (exit_code, summary). Pure function so the tests can call it directly."""
    if not isinstance(doc, dict):
        return 1, "DOCTOR_NOT_AN_OBJECT: the doctor output must be a JSON object"

    verdict = doc.get("verdict")
    if verdict != "PASS":
        return 1, f"DOCTOR_VERDICT: doctor did not PASS (verdict={verdict!r}, findings={doc.get('findings')!r})"

    source = doc.get("schema_source")
    if not isinstance(source, dict):
        return 1, f"DOCTOR_SCHEMA_SOURCE: no schema_source object in the doctor output ({source!r})"
    mode = source.get("mode")
    if mode != "INSTALLED":
        return 1, ("DOCTOR_SCHEMA_MODE: the installed wheel did not resolve its own packaged registry "
                   f"(mode={mode!r}); it must ship schemas/ (S4R3-F006)")

    families = doc.get("families")
    # `workspace.doctor` reports the family COUNT here, not the family list. Assert the type as well as
    # the value: a bare `!= expect` on `{'a': 1}` would be a comparison against a dict, which is how the
    # original gate failed.
    if not isinstance(families, int) or isinstance(families, bool):
        return 1, (f"DOCTOR_FAMILIES_TYPE: expected the family count as an int, got {type(families).__name__} "
                   f"({families!r})")
    if families != expect_families:
        return 1, f"DOCTOR_FAMILIES: expected {expect_families} declared families, got {families}"

    resolved = _resolved_path_inside(doc)
    if resolved is None:
        return 1, "DOCTOR_SCHEMA_PATH: the doctor reported no resolved schemas path"

    if deny_prefix:
        try:
            rp = pathlib.Path(resolved).resolve()
            dp = pathlib.Path(deny_prefix).resolve()
        except OSError as exc:
            return 1, f"DOCTOR_SCHEMA_PATH_UNRESOLVABLE: {exc}"
        # `rp.parents` excludes rp itself: a resolution that IS the checkout root is equally wrong.
        if rp == dp or dp in rp.parents:
            return 1, (f"DOCTOR_SCHEMA_PATH_IN_CHECKOUT: the wheel resolved schemas from the checkout "
                       f"({rp}), not from the installed package; mode=INSTALLED alone does not prove "
                       f"the schemas came from the wheel")

    return 0, f"installed-wheel contract registry: mode={mode} families={families} path={resolved}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Assert that an INSTALLED wheel resolved its OWN packaged contract registry (S4R3-F006).")
    ap.add_argument("doctor_json", help="path to the JSON written by `pipd doctor --json`")
    ap.add_argument("--expect-families", type=int, default=19,
                    help="declared contract family count (default: 19)")
    ap.add_argument("--deny-prefix", default=None,
                    help="a directory the resolved schemas path must NOT be inside (e.g. $GITHUB_WORKSPACE)")
    args = ap.parse_args(argv)

    path = pathlib.Path(args.doctor_json)
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _fail("DOCTOR_JSON_MISSING", f"{path} does not exist")
    except (OSError, json.JSONDecodeError) as exc:
        return _fail("DOCTOR_JSON_UNREADABLE", f"{path}: {exc}")

    code, summary = check(doc, args.expect_families, args.deny_prefix)
    if code != 0:
        print(summary, file=sys.stderr)
        return code
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
