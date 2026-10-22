"""lane_admission.py — HG-KSEOS lane-shaped admission record model + receipt writer (CANDIDATE).

# HGK-LANE-ADMISSION-ANCHOR: admission records for lane-shaped probes.

A lane is ADMITTED only when a *lane-shaped* exercise of the arm actually completed through the
real lane engine. A bare direct completion (an HTTP 200 with usable content) is recorded
separately and can NEVER, by itself, set ADMITTED. This module provides the record model, the
status policy, and the receipt writer used by scripts/probe-hgk-lane.py and by the pre-dispatch
gate.

Status policy (fail closed):
  ADMITTED  — lane-shaped exercise completed: >=1 completed model call AND >=1 completed tool
              round-trip AND a served identity that matches the requested arm.
  REFUSED   — the exercise ran and definitively failed (timeout, protocol error, identity
              mismatch, malformed tool path). A direct completion does not rescue REFUSED.
  UNPROVEN  — default. Nothing was measured, or only a direct completion was measured.

Standard library only.
"""
from __future__ import annotations

import json
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

__all__ = [
    "ADMITTED",
    "REFUSED",
    "UNPROVEN",
    "LaneAdmission",
    "record_direct_completion",
    "decide_status",
    "write_receipt",
    "load_receipt",
    "admission_key",
    "DEFAULT_TTL_SECONDS",
]

ADMITTED = "ADMITTED"
REFUSED = "REFUSED"
UNPROVEN = "UNPROVEN"

DEFAULT_TTL_SECONDS = 30 * 60
_VALID = {ADMITTED, REFUSED, UNPROVEN}


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def admission_key(*, lane: str, arm: dict[str, Any]) -> str:
    """A validated, path-safe key identifying one arm of one lane.

    Kept deterministic and filesystem-safe (no separators that escape an output root).
    """
    def _safe(value: str) -> str:
        cleaned = "".join(ch if (ch.isalnum() or ch in "-._") else "-" for ch in str(value))
        return cleaned.strip("-.") or "unknown"

    return f"{_safe(lane)}__{_safe(arm.get('provider', 'unknown'))}__{_safe(arm.get('model', 'unknown'))}__{_safe(arm.get('engine', 'unknown'))}"


class LaneAdmission:
    """Admission record for one lane-shaped probe of one arm."""

    def __init__(
        self,
        *,
        lane: str,
        arm: dict[str, Any],
        policy_epoch: int | None = None,
        request_profile: dict[str, Any] | None = None,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        self.lane = lane
        self.arm = {
            "provider": arm.get("provider"),
            "model": arm.get("model"),
            "engine": arm.get("engine"),
        }
        self.policy_epoch = policy_epoch
        self.request_profile = dict(request_profile or {})
        self.probe_id = f"probe-{secrets.token_hex(8)}"
        self.status = UNPROVEN
        self.failure_code: str | None = None
        self.direct_completion: dict[str, Any] | None = None
        self.lane_exercise: dict[str, Any] | None = None
        self.served: dict[str, Any] = {"provider": None, "model": None, "engine": None}
        self.started_utc: str | None = None
        self.finished_utc: str | None = None
        self.expires_utc: str | None = None
        self._ttl_seconds = int(ttl_seconds)

    # -- recording ---------------------------------------------------------------------------
    def record_start(self) -> None:
        self.started_utc = _now()

    def record_direct_completion(self, *, ok: bool, http_status: int | None = None,
                                 latency_s: float | None = None, detail: str | None = None,
                                 content_present: bool = False) -> None:
        """Record a bare direct-completion result. NEVER sufficient for ADMITTED."""
        self.direct_completion = {
            "ok": bool(ok),
            "http_status": http_status,
            "latency_s": latency_s,
            "content_present": bool(content_present),
            "detail": detail,
            "sufficient_for_admission": False,
        }

    def record_lane_exercise(
        self,
        *,
        completed_model_calls: int,
        completed_tools: int,
        served_provider: str | None,
        served_model: str | None,
        served_engine: str | None,
        session_id: str | None = None,
        elapsed_s: float | None = None,
        evidence_ref: str | None = None,
    ) -> None:
        self.lane_exercise = {
            "completed_model_calls": int(completed_model_calls),
            "completed_tools": int(completed_tools),
            "session_id": session_id,
            "elapsed_s": elapsed_s,
            "evidence_ref": evidence_ref,
        }
        self.served = {
            "provider": served_provider,
            "model": served_model,
            "engine": served_engine,
        }

    def set_failure(self, code: str) -> None:
        self.failure_code = code

    # -- decision ----------------------------------------------------------------------------
    def decide(self) -> str:
        self.status = decide_status(self)
        self.finished_utc = self.finished_utc or _now()
        expires = datetime.now(UTC) + timedelta(seconds=self._ttl_seconds)
        self.expires_utc = expires.isoformat().replace("+00:00", "Z")
        return self.status

    # -- serialization -----------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "HGK-LANE-ADMISSION/1",
            "claim_ceiling": "CANDIDATE_ONLY",
            "probe_id": self.probe_id,
            "lane": self.lane,
            "arm": dict(self.arm),
            "status": self.status,
            "policy_epoch": self.policy_epoch,
            "request_profile": dict(self.request_profile),
            "started_utc": self.started_utc,
            "finished_utc": self.finished_utc,
            "expires_utc": self.expires_utc,
            "direct_completion": self.direct_completion,
            "lane_exercise": self.lane_exercise,
            "served": dict(self.served),
            "failure_code": self.failure_code,
            "admission_key": admission_key(lane=self.lane, arm=self.arm),
            "status_policy": {
                "ADMITTED": "lane-shaped exercise completed (>=1 model call, >=1 tool) and served identity matches the requested arm",
                "REFUSED": "lane-shaped exercise ran and definitively failed",
                "UNPROVEN": "nothing measured, or only a direct completion measured — never sufficient",
            },
        }


def decide_status(record: LaneAdmission) -> str:
    """Pure status decision — the single place ADMITTED can be produced."""
    exercise = record.lane_exercise
    if not exercise:
        # No lane-shaped exercise happened. A direct completion can never upgrade this.
        if record.failure_code:
            return REFUSED
        return UNPROVEN
    if record.failure_code:
        return REFUSED
    model_calls = int(exercise.get("completed_model_calls", 0))
    tools = int(exercise.get("completed_tools", 0))
    served = record.served or {}
    served_model = (served.get("model") or "").strip().lower()
    served_provider = (served.get("provider") or "").strip().lower()
    requested_model = (record.arm.get("model") or "").strip().lower()
    requested_provider = (record.arm.get("provider") or "").strip().lower()
    if model_calls < 1 or tools < 1:
        return REFUSED
    if not served_model or not served_provider:
        return REFUSED
    if normalize_identity(served_model) != normalize_identity(requested_model):
        record.failure_code = record.failure_code or "ERR_LANE_IDENTITY_MODEL_MISMATCH"
        return REFUSED
    if served_provider != requested_provider:
        record.failure_code = record.failure_code or "ERR_LANE_IDENTITY_PROVIDER_MISMATCH"
        return REFUSED
    return ADMITTED


def normalize_identity(model: str) -> str:
    token = str(model).strip().lower()
    if "/" in token:
        token = token.split("/")[-1]
    return token


def record_from_dict(data: dict[str, Any]) -> LaneAdmission:
    record = LaneAdmission(
        lane=data.get("lane", "UNKNOWN"),
        arm=data.get("arm", {}),
        policy_epoch=data.get("policy_epoch"),
        request_profile=data.get("request_profile", {}),
    )
    record.probe_id = data.get("probe_id", record.probe_id)
    record.status = data.get("status", UNPROVEN)
    record.failure_code = data.get("failure_code")
    record.direct_completion = data.get("direct_completion")
    record.lane_exercise = data.get("lane_exercise")
    record.served = data.get("served", {"provider": None, "model": None, "engine": None})
    record.started_utc = data.get("started_utc")
    record.finished_utc = data.get("finished_utc")
    record.expires_utc = data.get("expires_utc")
    return record


def write_receipt(record: LaneAdmission, path: Path) -> Path:
    """Write an admission receipt as deterministic JSON (sorted keys, LF, trailing newline)."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True, indent=2)
    target.write_text(payload + "\n", encoding="utf-8", newline="\n")
    return target


def load_receipt(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
