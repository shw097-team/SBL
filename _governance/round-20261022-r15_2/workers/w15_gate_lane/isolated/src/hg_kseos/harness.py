from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from .errors import AdmissionDenied
from .security import ensure_within, sanitation_findings
from .util import canonical_json, sha256_text, utc_now


@dataclass(frozen=True)
class HarnessAction:
    action_id: str
    workorder_id: str
    actor: str
    tool: str
    tool_identity: str
    tool_version: str
    input_digest: str
    side_effect_class: str
    filesystem_scope: tuple[str, ...]
    network_scope: tuple[str, ...] = ()
    permission_profile: str = "workspace-write"
    preconditions: tuple[str, ...] = ()
    dry_run: bool = True
    expected_postcondition: str = ""
    rollback: str = ""
    evidence_required: tuple[str, ...] = ()
    timeout_seconds: int = 60
    attempt: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def digest(self) -> str:
        return sha256_text(canonical_json(asdict(self)))


class Harness:
    def __init__(self, maker_root: Path, evidence_log: Path, *, network_enabled: bool = False) -> None:
        self.maker_root = maker_root.resolve(strict=True)
        self.evidence_log = evidence_log
        self.network_enabled = network_enabled

    def preflight(self, action: HarnessAction) -> dict[str, Any]:
        if not action.rollback or not action.expected_postcondition or not action.evidence_required:
            raise AdmissionDenied("ERR_HARNESS_CONTRACT_INCOMPLETE")
        if action.network_scope and not self.network_enabled:
            raise AdmissionDenied("ERR_NETWORK_NOT_ADMITTED")
        if action.permission_profile not in {"read-only", "workspace-write"}:
            raise AdmissionDenied(f"ERR_PERMISSION_ESCALATION:{action.permission_profile}")
        scopes = [ensure_within(Path(item), self.maker_root) for item in action.filesystem_scope]
        findings = sanitation_findings(canonical_json(action.metadata))
        if findings:
            raise AdmissionDenied(f"ERR_UNTRUSTED_ACTION_METADATA:{','.join(findings)}")
        receipt = {
            "action_id": action.action_id,
            "action_digest": action.digest,
            "admitted_at": utc_now(),
            "resolved_scopes": [str(item) for item in scopes],
            "network": list(action.network_scope),
            "verdict": "ADMITTED",
        }
        self._append(receipt)
        return receipt

    def run(self, action: HarnessAction, operation: Callable[[], Any]) -> dict[str, Any]:
        admission = self.preflight(action)
        if action.dry_run:
            return admission | {"verdict": "DRY_RUN_PASS"}
        try:
            result = operation()
        except Exception as exc:
            receipt = admission | {
                "completed_at": utc_now(),
                "verdict": "FAILED_ROLLBACK_REQUIRED",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            self._append(receipt)
            raise
        receipt = admission | {"completed_at": utc_now(), "verdict": "PASS", "result": result}
        self._append(receipt)
        return receipt

    def _append(self, record: dict[str, Any]) -> None:
        self.evidence_log.parent.mkdir(parents=True, exist_ok=True)
        with self.evidence_log.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
