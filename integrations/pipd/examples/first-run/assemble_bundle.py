#!/usr/bin/env python3
"""Assemble the four compiler artefacts into the one bundle `validate` reads.

The 13-command CLI has no `assemble` verb, so this tiny helper does exactly what the
documented `validate --bundle` step expects: it reads the four JSON artefacts a reader
produced with the real verbs and writes `{"PI-PKG", "PD-PKG", "ECP", "TQAEP"}` to stdout.
It adds and removes nothing - it re-serialises the artefacts verbatim.

    python assemble_bundle.py pi.json pd.json ecp.json tqaep.json > bundle.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 5:
        print(__doc__, file=sys.stderr)
        return 2
    pi, pd, ecp, tqaep = (json.loads(Path(p).read_text(encoding="utf-8")) for p in argv[1:])
    bundle = {"PI-PKG": pi, "PD-PKG": pd, "ECP": ecp, "TQAEP": tqaep}
    print(json.dumps(bundle, ensure_ascii=False, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
