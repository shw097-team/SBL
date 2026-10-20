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
        "SBL_E_REPAIR_WITHOUT_EVIDENCE",
        "SBL_E_FOREIGN_FILES",
        "SBL_E_BAD_STATE",
        "SBL_E_UNKNOWN_MODE",
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
