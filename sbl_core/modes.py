"""SBL 39 ModeGate: 13 gates x 3 modes."""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Any

from .dto import ModeDecision
from .errors import SBLError

MODES: tuple[str, ...] = ("STANDALONE", "PREW3_SHADOW", "SWOF_CONNECTED")
GATE_IDS: tuple[str, ...] = tuple(f"G{i:02d}" for i in range(13))

DISPOSITIONS: dict[str, str] = {
    "STANDALONE": "ACTIVE",
    "PREW3_SHADOW": "SHADOW_NOEFFECT",
    "SWOF_CONNECTED": "BLOCKED_EXTERNAL",
}

_NATIVE_ACK_FIELDS = ("issuer", "permit_id", "subject_id", "signature")
# A native acknowledgement is a claim by an external issuer, so the four non-empty strings a caller can
# type are not evidence of anything. It is accepted only when the issuer is on the configured allowlist
# and the signature is the HMAC of the three identity fields under a key this build was given out of
# band. With no issuer list or no key the gate refuses, because an unverifiable ACK is not an ACK.
_ACK_ISSUERS_ENV = "SBL_SWOF_ACK_ISSUERS"
_ACK_KEY_ENV = "SBL_SWOF_ACK_KEY"


def ack_signature(issuer: str, permit_id: str, subject_id: str, key: str) -> str:
    """The only accepted signature shape for a native acknowledgement."""

    # Length-prefixed, not delimiter-joined: with a bare separator, ("a\x1fB", "C") and ("a", "B\x1fC")
    # produce identical material and therefore interchangeable signatures (V16-MODE-02).
    parts = (str(issuer), str(permit_id), str(subject_id))
    material = "".join(f"{len(part)}:{part}" for part in parts).encode("utf-8")
    return hmac.new(str(key).encode("utf-8"), material, hashlib.sha256).hexdigest()


def _configured_issuers() -> set[str]:
    raw = os.environ.get(_ACK_ISSUERS_ENV, "")
    return {item.strip() for item in raw.split(",") if item.strip()}


def _ack_state(native_ack: Any) -> tuple[bool, str]:
    """Returns (verified, reason). Anything short of a verified ACK is a refusal, never a default allow."""

    if not _complete_ack(native_ack):
        return False, "ACK_INCOMPLETE"
    issuers = _configured_issuers()
    if not issuers:
        return False, f"NO_TRUSTED_ISSUERS_CONFIGURED:{_ACK_ISSUERS_ENV}"
    key = os.environ.get(_ACK_KEY_ENV, "")
    if not key:
        return False, f"NO_VERIFICATION_KEY_CONFIGURED:{_ACK_KEY_ENV}"
    issuer = str(native_ack.get("issuer"))
    if issuer not in issuers:
        return False, "ISSUER_NOT_TRUSTED"
    expected = ack_signature(issuer, str(native_ack.get("permit_id")), str(native_ack.get("subject_id")), key)
    if not hmac.compare_digest(expected, str(native_ack.get("signature")).strip().lower()):
        return False, "SIGNATURE_MISMATCH"
    return True, "NATIVE_ACK_VERIFIED"


def mode_gate_matrix() -> list[dict[str, str]]:
    """Returns 39 unique gate rows: each gate in each of the three modes."""

    rows: list[dict[str, str]] = []
    for mode in MODES:
        for gate in GATE_IDS:
            rows.append(
                {
                    "gate_id": f"SBL-{gate}-{mode}",
                    "mode": mode,
                    "gate": gate,
                    "disposition": DISPOSITIONS[mode],
                }
            )
    return rows


def _complete_ack(native_ack: Any) -> bool:
    if not isinstance(native_ack, dict):
        return False
    for field in _NATIVE_ACK_FIELDS:
        value = native_ack.get(field)
        if not isinstance(value, str) or not value.strip():
            return False
    return True


class ModeGate:
    """Decides whether an effect may occur in the active execution mode."""

    def __init__(self, mode: str, native_ack: dict[str, Any] | None = None) -> None:
        if mode not in MODES:
            raise SBLError(
                "SBL_E_UNKNOWN_MODE",
                f"unknown mode: {mode!r}",
                {"mode": mode, "modes": list(MODES)},
            )
        self.mode = mode
        self.native_ack = dict(native_ack) if isinstance(native_ack, dict) else None

    def decide(self, effect: str) -> ModeDecision:
        effect = str(effect)
        if self.mode == "PREW3_SHADOW":
            return ModeDecision(
                mode=self.mode,
                effect=effect,
                allowed=False,
                no_effect=True,
                reason="SHADOW_READ_ONLY_NO_EFFECT",
            )
        if self.mode == "STANDALONE":
            allowed = effect in {"local.write", "local.read"}
            return ModeDecision(
                mode=self.mode,
                effect=effect,
                allowed=allowed,
                no_effect=not allowed,
                reason="LOCAL_EFFECT_ALLOWED" if allowed else "EFFECT_NOT_ALLOWED",
            )
        verified, ack_reason = _ack_state(self.native_ack)
        if not verified:
            raise SBLError(
                "SBL_E_REQUIRES_NATIVE_ACK",
                "SWOF_CONNECTED requires a verifiable native acknowledgement",
                {"mode": self.mode, "required": list(_NATIVE_ACK_FIELDS), "state": ack_reason},
            )
        return ModeDecision(
            mode=self.mode,
            effect=effect,
            allowed=True,
            no_effect=False,
            reason=ack_reason,
        )
