#!/usr/bin/env python3
"""Create a Hermes rollback point before the owner-authorised local install.

The point of a rollback point is that restoring is one command, not a document. So this writes a
verifiable archive plus a digest manifest of the exact pre-install state, and refuses to overwrite an
earlier rollback point (a re-run must not snapshot a half-installed tree and call it pristine).
"""

from __future__ import annotations

import hashlib
import json
import os
import tarfile
import time
from pathlib import Path

HERMES_HOME = Path(
    os.environ.get(
        "HERMES_HOME",
        r"C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes",
    )
)
OUT = Path(__file__).resolve().parent
SKILLS = HERMES_HOME / "skills"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    # The archive holds the whole pre-install skills tree, which legitimately contains third-party
    # contact addresses. Keeping it inside the published repository would make the secret scan
    # permanently red and would publish those addresses again, so it lives outside the tree and only
    # its digest travels.
    archive = Path(os.environ.get("SBL_ROLLBACK_ARCHIVE_DIR", r"C:\Projects\_sbl_r4")) / "skills-preinstall.tar.gz"
    archive.parent.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "ROLLBACK_MANIFEST.json"
    if archive.exists() or manifest_path.exists():
        raise SystemExit(
            "refusing to overwrite an existing rollback point; move it aside deliberately "
            "before creating a new one"
        )

    files = []
    for path in sorted(SKILLS.rglob("*")):
        if path.is_file():
            files.append(
                {
                    "rel": str(path.relative_to(HERMES_HOME)).replace("\\", "/"),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_of(path),
                }
            )

    with tarfile.open(archive, "w:gz") as tar:
        tar.add(SKILLS, arcname="skills")

    manifest = {
        "schema": "SBL-HERMES-ROLLBACK-POINT/1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hermes_home": str(HERMES_HOME),
        "skills_root": str(SKILLS),
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "archive": {
            "path": archive.name,
            "bytes": archive.stat().st_size,
            "sha256": sha256_of(archive),
        },
        "config_sha256": sha256_of(HERMES_HOME / "config.yaml"),
        "files": files,
        "restore": (
            "tar -xzf skills-preinstall.tar.gz -C <HERMES_HOME> --overwrite, then delete any "
            "skills/sbl directory that postdates this manifest"
        ),
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: manifest[k] for k in ("created_utc", "file_count", "total_bytes")}, indent=2))
    print("archive_sha256", manifest["archive"]["sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
