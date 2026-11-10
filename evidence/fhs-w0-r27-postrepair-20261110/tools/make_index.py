#!/usr/bin/env python3
"""make_index — one index over every artifact this round produced, hashes computed from bytes.

Rules this keeps (learned the hard way in earlier rounds):
  * the index never records its own digest, and is never hashed by the script that writes it;
  * a missing file is listed as MISSING, never silently skipped;
  * the count is printed, so a reader can check it against the report.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys

ROOT = pathlib.Path("C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110")
SKIP_DIRS = {"__pycache__", ".git", ".pytest_cache"}


def walk(base: pathlib.Path):
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = pathlib.Path(dirpath) / fn
            if p.name in ("EVIDENCE_INDEX.json", "EVIDENCE_INDEX.md"):
                continue
            yield p


def main() -> int:
    rows = []
    for p in sorted(walk(ROOT)):
        try:
            b = p.read_bytes()
            rows.append({"path": p.relative_to(ROOT).as_posix(), "bytes": len(b),
                         "sha256": hashlib.sha256(b).hexdigest()})
        except OSError as e:
            rows.append({"path": p.relative_to(ROOT).as_posix(), "error": f"{type(e).__name__}: {e}"})
    missing = [r["path"] for r in rows if "error" in r]
    out = {"schema": "FHS.R27.EvidenceIndex/1", "root": str(ROOT), "files": len(rows),
           "unreadable": missing, "rows": rows}
    (ROOT / "EVIDENCE_INDEX.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    lines = ["# EVIDENCE INDEX — FHS W0 r26 post-repair round", "",
             f"files: {len(rows)} — unreadable: {len(missing)}", "",
             "| path | bytes | sha256 |", "|---|---:|---|"]
    for r in rows:
        lines.append(f"| `{r['path']}` | {r.get('bytes','')} | `{r.get('sha256', r.get('error',''))}` |")
    (ROOT / "EVIDENCE_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(rows), "unreadable": missing}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
