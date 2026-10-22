from __future__ import annotations

import json
import platform
import sqlite3
import sys
from pathlib import Path

from .hlpe import qualify_hlpe
from .security import network_is_disabled
from .spine import SharedSpine
from .util import sha256_file, utc_now


def doctor(project_root: Path) -> dict[str, object]:
    project_root = project_root.resolve(strict=True)
    config_path = project_root / "config" / "project.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    checks: dict[str, object] = {}
    checks["product_root"] = config.get("product_root") == "HG-KSEOS"
    checks["python"] = platform.python_version()
    checks["python_supported"] = sys.version_info >= (3, 12)
    checks["sqlite"] = sqlite3.sqlite_version
    connection = sqlite3.connect(":memory:")
    try:
        options = {row[0] for row in connection.execute("PRAGMA compile_options")}
        connection.execute("CREATE VIRTUAL TABLE probe USING fts5(body)")
        checks["fts5"] = True
        checks["sqlite_compile_options"] = sorted(options)
    finally:
        connection.close()
    database = project_root / config["canonical_database"]
    checks["database_exists"] = database.is_file()
    if database.is_file():
        spine = SharedSpine(database)
        checks["spine"] = spine.snapshot()
        with spine.connect() as connection:
            checks["integrity"] = connection.execute("PRAGMA integrity_check").fetchone()[0]
    inventory = project_root / "evidence" / "wave-00" / "SOURCE_INVENTORY.csv"
    checks["inventory_sha256"] = sha256_file(inventory)
    checks["inventory_frozen"] = checks["inventory_sha256"] == "c79213f6ae9dcfa6dab7718dff013c9ae33e7a563117bdec39d2518ffc469c5e"
    checks["network_disabled"] = network_is_disabled()
    try:
        checks["hlpe"] = qualify_hlpe(
            Path(config["hlpe"]["integrated_target"]), config["hlpe"]["expected_head"]
        )
    except Exception as exc:
        checks["hlpe"] = {"status": "FAIL", "error": f"{type(exc).__name__}:{exc}"}
    blocking = [
        name
        for name in ("product_root", "python_supported", "fts5", "database_exists", "inventory_frozen")
        if checks.get(name) is not True
    ]
    if isinstance(checks["hlpe"], dict) and checks["hlpe"].get("status") == "FAIL":
        blocking.append("hlpe")
    return {"captured_at": utc_now(), "checks": checks, "blocking": blocking, "verdict": "PASS" if not blocking else "FAIL"}
