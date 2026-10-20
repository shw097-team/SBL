"""SBL 39 ModeGate: 13 gates x 3 modes."""

from __future__ import annotations

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
        if not _complete_ack(self.native_ack):
            raise SBLError(
                "SBL_E_REQUIRES_NATIVE_ACK",
                "SWOF_CONNECTED requires a complete native acknowledgement",
                {"mode": self.mode, "required": list(_NATIVE_ACK_FIELDS)},
            )
        return ModeDecision(
            mode=self.mode,
            effect=effect,
            allowed=True,
            no_effect=False,
            reason="NATIVE_ACK_PRESENT",
        )
