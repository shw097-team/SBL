from __future__ import annotations

import csv
import json
from pathlib import Path

from .errors import InvariantViolation
from .spine import SharedSpine
from .util import utc_now


LIFECYCLE = [
    "DISCOVERED",
    "IDENTIFIED",
    "PINNED",
    "INSTALLED",
    "CONFIGURED",
    "DOCTOR_PASS",
    "PILOT_PASS",
    "CERTIFIED",
    "ENABLED",
]


class ProviderRegistry:
    def __init__(self, spine: SharedSpine) -> None:
        self.spine = spine

    def import_protected_ledger(self, path: Path) -> int:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if len(rows) != 78:
            raise InvariantViolation(f"ERR_PROTECTED_IDENTITY_DENOMINATOR:{len(rows)}")
        with self.spine.transaction() as connection:
            for row in rows:
                connection.execute(
                    """INSERT INTO provider_bindings
                       (provider_id,slot,xor_group,disposition,pin,state,rollback_pointer,updated_at)
                       VALUES(?,?,?,?,?,'DISCOVERED',?,?)
                       ON CONFLICT(provider_id) DO UPDATE SET slot=excluded.slot,
                         disposition=excluded.disposition,updated_at=excluded.updated_at""",
                    (
                        row["id"],
                        row["name"],
                        _xor_group(row["name"]),
                        row["disposition"],
                        None,
                        f"RB-{row['id']}",
                        utc_now(),
                    ),
                )
        return len(rows)

    def add_internal_fts5(self, pin: str) -> None:
        with self.spine.transaction() as connection:
            connection.execute(
                """INSERT OR REPLACE INTO provider_bindings
                   (provider_id,slot,xor_group,disposition,pin,state,doctor_evidence,rollback_pointer,updated_at)
                   VALUES('HGK-PROVIDER-FTS5','semantic-retrieval','XOR-RETRIEVAL','PREFERRED_DEFAULT',?,
                          'ENABLED','builtin SQLite FTS5 probe','RB-FTS5',?)""",
                (pin, utc_now()),
            )

    def advance(self, provider_id: str, to_state: str, evidence_ref: str | None = None, pin: str | None = None) -> None:
        with self.spine.transaction() as connection:
            row = connection.execute(
                "SELECT state FROM provider_bindings WHERE provider_id=?", (provider_id,)
            ).fetchone()
            if not row:
                raise InvariantViolation(f"ERR_PROVIDER_UNKNOWN:{provider_id}")
            current_index = LIFECYCLE.index(row["state"])
            target_index = LIFECYCLE.index(to_state)
            if target_index != current_index + 1:
                raise InvariantViolation(f"ERR_PROVIDER_LIFECYCLE_SKIP:{row['state']}->{to_state}")
            if to_state == "PINNED" and not pin:
                raise InvariantViolation("ERR_PROVIDER_PIN_REQUIRED")
            if to_state in {"DOCTOR_PASS", "PILOT_PASS", "CERTIFIED", "ENABLED"} and not evidence_ref:
                raise InvariantViolation(f"ERR_PROVIDER_EVIDENCE_REQUIRED:{to_state}")
            connection.execute(
                """UPDATE provider_bindings SET state=?,pin=COALESCE(?,pin),
                   doctor_evidence=COALESCE(?,doctor_evidence),updated_at=? WHERE provider_id=?""",
                (to_state, pin, evidence_ref, utc_now(), provider_id),
            )


def _xor_group(name: str) -> str | None:
    lowered = name.casefold()
    if any(item in lowered for item in ("qdrant", "chroma", "pgvector", "milvus", "fts5")):
        return "XOR-RETRIEVAL"
    if any(item in lowered for item in ("codex", "opencode")):
        return "XOR-CODING-PROVIDER"
    return None


def qualify_hermes_core(project_root: Path) -> dict[str, object]:
    project_root = project_root.resolve(strict=True)
    config = json.loads((project_root / "config" / "hermes.json").read_text(encoding="utf-8"))
    install = json.loads(
        (project_root / "evidence" / "wave-06" / "HERMES_INSTALL_RECEIPT.json").read_text(
            encoding="utf-8"
        )
    )
    runtime = json.loads(
        (project_root / "evidence" / "wave-06" / "HERMES_RUNTIME_VALIDATION.json").read_text(
            encoding="utf-8"
        )
    )
    expected_commit = config["release"]["commit"]
    if install["release"]["commit"] != expected_commit:
        raise InvariantViolation("ERR_HERMES_INSTALL_COMMIT_MISMATCH")
    if install["result"] != "PASS_LOCAL_CORE_NO_PROVIDER":
        raise InvariantViolation("ERR_HERMES_INSTALL_RECEIPT_NOT_PASS")
    if config["provider_credentials_configured"] is not False:
        raise InvariantViolation("ERR_HERMES_CORE_QUALIFICATION_CREDENTIAL_SCOPE")
    tests = runtime["official_security_rollback_tests"]
    if (tests["tests"], tests["passed"], tests["failures"]) != (57, 50, 7):
        raise InvariantViolation("ERR_HERMES_SECURITY_DENOMINATOR")
    if not tests["all_observed_failures_are_windows_symlink_privilege_blocks"]:
        raise InvariantViolation("ERR_HERMES_SECURITY_FAILURE_UNCLASSIFIED")
    if not runtime["negative_provider_pilot"]["passed"]:
        raise InvariantViolation("ERR_HERMES_NEGATIVE_PILOT")
    if not runtime["rollback_dry_run"]["passed"]:
        raise InvariantViolation("ERR_HERMES_ROLLBACK_DRY_RUN")
    if not runtime["doctor"]["local_core_checks_passed"]:
        raise InvariantViolation("ERR_HERMES_DOCTOR_LOCAL")

    project_config = json.loads((project_root / "config" / "project.json").read_text(encoding="utf-8"))
    spine = SharedSpine(project_root / project_config["canonical_database"])
    provider_id = "P0-TOOL-001"
    evidence = "evidence/wave-06/HERMES_RUNTIME_VALIDATION.json"
    target = LIFECYCLE.index("DOCTOR_PASS")
    advanced: list[str] = []
    registry = ProviderRegistry(spine)
    while True:
        with spine.connect() as connection:
            row = connection.execute(
                "SELECT state,pin FROM provider_bindings WHERE provider_id=?", (provider_id,)
            ).fetchone()
        if not row:
            raise InvariantViolation("ERR_HERMES_PROVIDER_ROW_MISSING")
        current = LIFECYCLE.index(row["state"])
        if current >= target:
            return {
                "status": "HERMES_CORE_QUALIFICATION_PASS",
                "provider_id": provider_id,
                "state": row["state"],
                "pin": row["pin"],
                "advanced": advanced,
                "claim_ceiling": "DOCTOR_PASS; provider-bound PILOT_PASS and higher states remain prohibited",
            }
        next_state = LIFECYCLE[current + 1]
        registry.advance(
            provider_id,
            next_state,
            evidence_ref=evidence,
            pin=expected_commit if next_state == "PINNED" else None,
        )
        advanced.append(next_state)
