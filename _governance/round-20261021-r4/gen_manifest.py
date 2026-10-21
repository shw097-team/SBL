#!/usr/bin/env python3
"""Round manifest with digests taken from the Git blob, not the working tree.

Rationale: this host has core.autocrlf on, so the working-tree bytes of a text file are CRLF while
the repository stores LF. A digest of the working tree is therefore unreproducible anywhere else and
silently disagrees with `git show HEAD:path | sha256sum`. Every entry here is reproducible with that
last command.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(r"C:\Projects\Agent_Workspace\SBL")
OUT = REPO / "_governance" / "round-20261021-r4" / "ROUND_MANIFEST.json"
PREFIXES = ("_governance/round-20261021-r4/", "contracts/SBL_C0_C9_CONTRACT-R4.json", "contracts/compiled-r4/")


def blob(path: str) -> bytes:
    proc = subprocess.run(
        ["git", "cat-file", "blob", f"HEAD:{path}"], cwd=str(REPO), capture_output=True
    )
    if proc.returncode != 0:
        raise SystemExit(f"no blob for {path}: {proc.stderr.decode()[:200]}")
    return proc.stdout


def main() -> int:
    listing = subprocess.run(
        ["git", "ls-files", "-z"], cwd=str(REPO), capture_output=True, text=True
    ).stdout.split("\0")
    entries = []
    for path in sorted(p for p in listing if p and p.startswith(PREFIXES)):
        if path.endswith("ROUND_MANIFEST.json"):
            continue
        data = blob(path)
        entries.append({"path": path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    payload = {
        "schema": "SBL-ROUND-MANIFEST/2",
        "round": "round-20261021-r4",
        "digest_basis": "git blob bytes at HEAD (git show HEAD:<path> | sha256sum), never working-tree bytes",
        "count": len(entries),
        "total_bytes": sum(e["bytes"] for e in entries),
        "entries": entries,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(entries), "total_bytes": payload["total_bytes"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
