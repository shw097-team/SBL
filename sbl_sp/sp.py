"""Specialised-principal manifests and the challenge-signing gate.

The signing gate is credential-bound: naming a principal in an argument is not authority. A
caller must also present the HMAC digest that only the holder of that principal's key can
produce, so a maker cannot impersonate the external checker by passing a string (SEC-01), and a
verdict whose status is a proxy can never be signed (SEC-03).

``keys.json`` is a local DEMO keyring with deterministic placeholder keys -- it is deliberately
public and is not a secret. Its only job is to make "naming a principal" insufficient.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any

from sbl_core.errors import SBLError

MANIFEST_DIR = Path(__file__).parent / "manifests"

#: Signing keys are NEVER stored in the repository. The operator provisions one per principal in
#: the environment of the process that is allowed to sign; a fresh checkout therefore cannot mint
#: a challenger credential (independent challenge round 2, NEW-02).
KEY_ENV_PREFIX = "SBL_SP_KEY_"
MIN_KEY_CHARS = 32

REAL_STATUSES = frozenset({"PASS", "FAIL", "BLOCKED_HITL", "BLOCKED_EXTERNAL"})
PROXY_STATUSES = frozenset({"FILE_EXISTS", "SYMBOL_EXISTS", "SUMMARY_ONLY", "DOCUMENTED"})


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


def load_key(sp_id: str) -> str:
    """Return the operator-provisioned signing key for ``sp_id``.

    The key comes from the environment, never from the repository, and is never logged or echoed
    in a refusal detail.
    """

    safe_id = _safe_sp_id(sp_id)
    key = os.environ.get(KEY_ENV_PREFIX + safe_id.upper(), "")
    if not isinstance(key, str) or len(key) < MIN_KEY_CHARS:
        raise SBLError(
            "SBL_E_PERMISSION_DENIED",
            "no signing key is provisioned for this principal",
            {
                "reason": "no_key_provisioned",
                "principal": safe_id,
                "expected_env": KEY_ENV_PREFIX + safe_id.upper(),
            },
        )
    return key


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


def expected_signature(principal_id: str, verdict: dict) -> str:
    """The digest a genuine holder of ``principal_id``'s key would present."""

    payload = json.dumps([principal_id, verdict], sort_keys=True, default=str)
    return hmac.new(
        load_key(principal_id).encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def sign_verdict(
    principal_id: str,
    maker_principal: str,
    verdict: dict,
    credential: str | None = None,
) -> dict:
    """Sign an independent challenge verdict; a maker may never sign its own."""

    assert_permission(principal_id, "challenge.sign")
    if principal_id.strip().lower() == maker_principal.strip().lower():
        raise SBLError(
            "SBL_E_SELF_CHECK_FORBIDDEN",
            "a maker may not sign the verdict on its own work",
            {"principal": principal_id, "maker": maker_principal},
        )

    status = str(verdict.get("status", "")).strip().upper()
    if status in PROXY_STATUSES or status not in REAL_STATUSES:
        raise SBLError(
            "SBL_E_BAD_STATE",
            "verdict status cannot back a signature",
            {
                "principal": principal_id,
                "status": verdict.get("status"),
                "allowed": sorted(REAL_STATUSES),
                "proxy_statuses": sorted(PROXY_STATUSES),
            },
        )

    if not isinstance(credential, str) or not credential:
        raise SBLError(
            "SBL_E_PERMISSION_DENIED",
            "signing requires the principal credential",
            {"reason": "credential_missing_or_invalid", "principal": principal_id},
        )
    if not hmac.compare_digest(credential, expected_signature(principal_id, verdict)):
        raise SBLError(
            "SBL_E_PERMISSION_DENIED",
            "signing requires the principal credential",
            {"reason": "credential_missing_or_invalid", "principal": principal_id},
        )

    return {
        "schema": "SBL-CHALLENGE-VERDICT/1",
        "principal": principal_id,
        "maker": maker_principal,
        "verdict": verdict,
        "signature": credential,
    }
