#!/usr/bin/env python3
"""Round manifest: digest every artefact as GIT BLOBS so CRLF normalisation cannot skew a readback.

Files are staged first (`git add --intent-to-add` is not enough; the real blob is needed), then each
digest is computed over `git cat-file blob` output. The manifest excludes itself and the remote
readback, which is written after publication.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(r"C:\Projects\Agent_Workspace\SBL")
ROUND = ROOT / "_governance" / "round-20261021-r5"
OUT = ROUND / "ROUND_MANIFEST.json"
EXCLUDE = {"ROUND_MANIFEST.json", "90_EVIDENCE/REMOTE_READBACK.json"}


def main() -> int:
    subprocess.run(["git", "add", "-A", "_governance/round-20261021-r5"], cwd=str(ROOT), check=True)
    rows = []
    for path in sorted(ROUND.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROUND).as_posix()
        if rel in EXCLUDE:
            continue
        sha1 = subprocess.run(
            ["git", "hash-object", str(path)], cwd=str(ROOT), capture_output=True, text=True, check=True
        ).stdout.strip()
        blob = subprocess.run(
            ["git", "cat-file", "blob", sha1], cwd=str(ROOT), capture_output=True, check=True
        ).stdout
        rows.append({"path": rel, "bytes": len(blob), "blob_sha256": hashlib.sha256(blob).hexdigest()})
    bad = [r["path"] for r in rows if not r["blob_sha256"]]
    OUT.write_text(
        json.dumps(
            {
                "round": "SBL-R5-20261021-C5",
                "digest_basis": "sha256 of the git blob (post-normalisation bytes)",
                "count": len(rows),
                "bad": bad,
                "files": rows,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"count": len(rows), "bad": bad, "sample": rows[0] if rows else None}, ensure_ascii=False))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
