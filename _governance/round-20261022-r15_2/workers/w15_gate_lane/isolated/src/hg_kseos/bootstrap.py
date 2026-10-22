from __future__ import annotations

import csv
import json
from pathlib import Path

from .providers import ProviderRegistry
from .spine import SharedSpine


def clean(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "`":
        return value[1:-1]
    return value


def configured_workspace_bindings(project_root: Path, source_root: Path) -> tuple[tuple[str, str, Path, str], ...]:
    """Return non-conflicting workspace bindings for companion or canonical layouts."""
    project_root = project_root.resolve(strict=True)
    source_root = source_root.resolve(strict=True)
    if project_root == source_root:
        return (
            (
                "WS-CANONICAL",
                "HGK-P0",
                project_root,
                "WRITABLE_CANONICAL_WITH_FROZEN_INPUT_SUBTREES",
            ),
        )
    return (
        ("WS-SOURCE", "HGK-P0", source_root, "READ_ONLY_SOURCE"),
        ("WS-MAKER", "HGK-P0", project_root, "WRITABLE_MAKER"),
    )


def bootstrap(project_root: Path) -> dict[str, object]:
    project_root = project_root.resolve(strict=True)
    config = json.loads((project_root / "config" / "project.json").read_text(encoding="utf-8"))
    database = project_root / config["canonical_database"]
    if database.exists():
        raise RuntimeError(f"ERR_BOOTSTRAP_DATABASE_EXISTS:{database}")
    spine = SharedSpine(database)
    spine.initialize()
    spine.create_project()
    for workspace_id, project_id, path, mode in configured_workspace_bindings(
        project_root, Path(config["source_root"])
    ):
        spine.bind_workspace(workspace_id, project_id, path, mode)

    requirement_count = 0
    with (project_root / "requirements" / "PREDEV_REQUIREMENTS.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            spine.register_requirement(
                clean(row["REQ"]),
                clean(row["direct_source_locator"]),
                clean(row["requirement"]),
                clean(row["ACC"]),
                clean(row["oracle"]),
                clean(row["threshold"]),
                clean(row["rejected_interpretation"]),
                clean(row["priority"]),
            )
            requirement_count += 1
    with (project_root / "requirements" / "P0_REQUIREMENTS.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            spine.register_requirement(
                clean(row["p0_req"]),
                clean(row["original_source_locator"]),
                clean(row["original_wording"]),
                clean(row["new_ACC"]),
                clean(row["original_oracle"]),
                clean(row["original_test_gate"]),
                clean(row["original_rejected_interpretation"]),
                "P0",
            )
            requirement_count += 1
    provider_count = ProviderRegistry(spine).import_protected_ledger(
        project_root / "registries" / "PROTECTED_IDENTITY_CLASS_QUALIFICATION.csv"
    )
    import sqlite3

    ProviderRegistry(spine).add_internal_fts5(sqlite3.sqlite_version)
    with (project_root / "source-freeze" / "TT_LEDGER.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["status"].startswith(("OPEN", "TEMP_CLOSED")):
                spine.open_tt(
                    row["tt_id"],
                    row["subject"],
                    row["owner"],
                    row["blocking"].casefold() == "true",
                    row["close_criteria"],
                )
    return {
        "database": str(database),
        "requirements": requirement_count,
        "protected_identities": provider_count,
        "retrieval_provider": "sqlite-fts5",
        "snapshot": spine.snapshot(),
        "status": "BOOTSTRAP_PASS",
    }


def reconcile_tt(project_root: Path) -> dict[str, object]:
    project_root = project_root.resolve(strict=True)
    config = json.loads((project_root / "config" / "project.json").read_text(encoding="utf-8"))
    spine = SharedSpine(project_root / config["canonical_database"])
    opened = 0
    closed = 0
    with (project_root / "source-freeze" / "TT_LEDGER.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["status"].startswith("CLOSED"):
                with spine.connect() as connection:
                    current = connection.execute("SELECT status FROM tt_records WHERE tt_id=?", (row["tt_id"],)).fetchone()
                if current and current["status"] == "OPEN":
                    evidence = row["status"].split(":", 1)[1] if ":" in row["status"] else "E-TT-CLOSE"
                    spine.close_tt(row["tt_id"], evidence)
                    closed += 1
            elif row["status"].startswith(("OPEN", "TEMP_CLOSED")):
                spine.open_tt(
                    row["tt_id"],
                    row["subject"],
                    row["owner"],
                    row["blocking"].casefold() == "true",
                    row["close_criteria"],
                )
                opened += 1
    return {"status": "TT_RECONCILIATION_PASS", "opened_or_refreshed": opened, "closed": closed, "snapshot": spine.snapshot()}
