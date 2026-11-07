"""Single source of truth for SBL typed refusals."""

from __future__ import annotations

from typing import Any

ERROR_CODES = frozenset(
    {
        "SBL_E_EMPTY_TITLE",
        "SBL_E_DUPLICATE_TITLE",
        "SBL_E_UNLOCATED_REQUIREMENT",
        "SBL_E_UNKNOWN_KIND",
        "SBL_E_PROHIBITED_KIND",
        "SBL_E_WRITE_OUTSIDE_WRITESET",
        "SBL_E_STALE_HEAD",
        "SBL_E_SELF_CHECK_FORBIDDEN",
        "SBL_E_CLAIM_CEILING_EXCEEDED",
        "SBL_E_UNKNOWN_SP",
        "SBL_E_PERMISSION_DENIED",
        "SBL_E_KNOWLEDGE_NO_ANSWER",
        "SBL_E_KNOWLEDGE_COVERAGE_GAP",
        "SBL_E_PROVIDER_OFF",
        "SBL_E_REQUIRES_NATIVE_ACK",
        # D-18: the native gate's own bound refusals. Distinct codes, because each one names a
        # different thing the issuer has to fix; none of them is reachable by an unauthenticated ACK.
        "SBL_E_ACK_MISSING_FIELD",
        "SBL_E_ACK_MALFORMED_FIELD",
        "SBL_E_ACK_EXPIRED",
        "SBL_E_ACK_NOT_YET_VALID",
        "SBL_E_ACK_SUBJECT_MISMATCH",
        "SBL_E_ACK_SCOPE_MISMATCH",
        "SBL_E_ACK_PERMIT_UNKNOWN",
        "SBL_E_ACK_PERMIT_MISMATCH",
        "SBL_E_ACK_ECP_MISSING",
        "SBL_E_REPAIR_WITHOUT_EVIDENCE",
        "SBL_E_FOREIGN_FILES",
        "SBL_E_BAD_STATE",
        "SBL_E_UNKNOWN_MODE",
        "SBL_E_PLUGIN_SCHEMA",
        "SBL_E_MANIFEST_UNTRUSTED",
    }
)


class SBLError(Exception):
    """A typed, JSON-serialisable SBL refusal.

    Every refusal in product code is one of these: bare ``Exception`` and
    silent ``None`` returns are not part of the contract.
    """

    def __init__(
        self, code: str, message: str, detail: dict[str, Any] | None = None
    ) -> None:
        if not isinstance(code, str) or not code.strip():
            raise TypeError("SBLError code must be a non-empty string")
        self.code: str = code.strip()
        self.message: str = str(message)
        self.detail: dict[str, Any] = dict(detail) if detail else {}
        super().__init__(self.code, self.message, self.detail)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": False,
            "code": self.code,
            "message": self.message,
            "detail": dict(self.detail),
        }

    def to_dict(self) -> dict[str, Any]:
        return self.as_dict()

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"
