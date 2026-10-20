"""Specialised-principal manifests and the challenge-signing gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from sbl_core.errors import SBLError

MANIFEST_DIR = Path(__file__).parent / "manifests"


def _unknown_sp(sp_id: Any) -> SBLError:
    return SBLError(
        "SBL_E_UNKNOWN_SP",
        "specialised principal is not registered",
        {"sp_id": sp_id},
    )


def _safe_sp_id(sp_id: Any) -> str:
    if not isinstance(sp_id, str):
        raise _unknown_sp(sp_id)
    candidate = sp_id.strip()
    lowered = candidate.lower()
    if (
        not candidate
        or candidate != sp_id
        or lowered in (".", "..")
        or ".." in lowered
        or "/" in candidate
        or "\\" in candidate
        or ":" in candidate
    ):
        raise _unknown_sp(sp_id)
    return candidate


def load_manifest(sp_id: str) -> dict:
    """Load the manifest for ``sp_id``; every lookup failure is a refusal."""

    safe_id = _safe_sp_id(sp_id)
    path = MANIFEST_DIR / f"{safe_id}.json"
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise _unknown_sp(sp_id) from exc
    try:
        manifest = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise SBLError(
            "SBL_E_BAD_STATE",
            "manifest is not valid JSON",
            {"sp_id": sp_id, "path": str(path)},
        ) from exc
    if not isinstance(manifest, dict):
        raise SBLError(
            "SBL_E_BAD_STATE",
            "manifest must be a JSON object",
            {"sp_id": sp_id, "path": str(path)},
        )
    return manifest


def assert_permission(sp_id: str, action: str) -> None:
    """Raise unless ``sp_id`` may perform ``action``."""

    manifest = load_manifest(sp_id)
    permissions = set(manifest.get("permissions") or ())
    forbidden = set(manifest.get("forbidden") or ())
    if action in forbidden or action not in permissions:
        raise SBLError(
            "SBL_E_PERMISSION_DENIED",
            "specialised principal is not permitted to perform this action",
            {"sp_id": sp_id, "action": action},
        )


def sign_verdict(principal_id: str, maker_principal: str, verdict: dict) -> dict:
    """Sign an independent challenge verdict; a maker may never sign its own."""

    assert_permission(principal_id, "challenge.sign")
    if principal_id.strip().lower() == maker_principal.strip().lower():
        raise SBLError(
            "SBL_E_SELF_CHECK_FORBIDDEN",
            "a maker may not sign the verdict on its own work",
            {"principal": principal_id, "maker": maker_principal},
        )
    payload = json.dumps([principal_id, verdict], sort_keys=True)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return {
        "schema": "SBL-CHALLENGE-VERDICT/1",
        "principal": principal_id,
        "maker": maker_principal,
        "verdict": verdict,
        "signature": "SIG-" + digest[:16],
    }
