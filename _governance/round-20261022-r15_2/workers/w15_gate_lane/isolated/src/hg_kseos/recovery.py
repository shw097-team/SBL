from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

from .errors import InvariantViolation
from .util import sha256_file, utc_now


def backup_database(database: Path, backup_root: Path) -> dict[str, str]:
    database = database.resolve(strict=True)
    backup_root.mkdir(parents=True, exist_ok=True)
    stamp = utc_now().replace(":", "").replace("-", "")
    target = backup_root / f"hg-kseos-{stamp}.db"
    source_connection = sqlite3.connect(database)
    target_connection = sqlite3.connect(target)
    try:
        source_connection.backup(target_connection)
    finally:
        target_connection.close()
        source_connection.close()
    target_hash = sha256_file(target)
    manifest = {
        "created_at": utc_now(),
        "source": str(database),
        "backup": str(target),
        "sha256": target_hash,
        "status": "BACKUP_READBACK_PASS",
    }
    manifest_path = target.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest | {"manifest": str(manifest_path)}


def restore_database(backup: Path, expected_sha256: str, restore_target: Path) -> dict[str, str]:
    backup = backup.resolve(strict=True)
    if sha256_file(backup) != expected_sha256.lower():
        raise InvariantViolation("ERR_BACKUP_DIGEST_MISMATCH")
    if restore_target.exists():
        raise InvariantViolation("ERR_RESTORE_TARGET_EXISTS")
    restore_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup, restore_target)
    connection = sqlite3.connect(restore_target)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        connection.close()
    if integrity != "ok":
        restore_target.unlink(missing_ok=True)
        raise InvariantViolation(f"ERR_RESTORE_INTEGRITY:{integrity}")
    return {
        "backup": str(backup),
        "restored": str(restore_target),
        "sha256": sha256_file(restore_target),
        "status": "RESTORE_READBACK_PASS",
    }

