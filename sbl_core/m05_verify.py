"""SBLM05 - Evidence Verification."""

from __future__ import annotations

from hashlib import sha256

from .dto import EvidenceItem, Verdict
from .errors import SBLError

CLAIM_RANKS: dict[str, int] = {
    "LOCAL": 0,
    "PACKAGE": 1,
    "EXTERNAL_ACCEPTANCE": 2,
    "PRODUCTION": 3,
}

PROXY_STATUSES = frozenset({"FILE_EXISTS", "SYMBOL_EXISTS", "SUMMARY_ONLY", "DOCUMENTED"})


class EvidenceVerification:
    """Records evidence and issues non-self-signed, ceiling-bounded verdicts."""

    def record(
        self,
        gate_id: str,
        command: str,
        exit_code: int,
        stdout: str,
        denominator: int,
    ) -> EvidenceItem:
        if not isinstance(denominator, int) or isinstance(denominator, bool):
            raise SBLError(
                "SBL_E_BAD_STATE",
                "denominator must be an integer",
                {"gate_id": gate_id, "denominator": str(denominator)},
            )
        if denominator <= 0:
            raise SBLError(
                "SBL_E_BAD_STATE",
                "denominator must be greater than zero",
                {"gate_id": gate_id, "denominator": denominator},
            )
        digest = sha256(str(stdout).encode("utf-8")).hexdigest()
        return EvidenceItem(
            gate_id=str(gate_id),
            command=str(command),
            exit_code=int(exit_code),
            stdout_sha256=digest,
            denominator=denominator,
        )

    def verdict(
        self,
        gate_id: str,
        maker: str,
        checker: str,
        status: str,
        claim_ceiling: str,
        claim: str,
    ) -> Verdict:
        if str(maker).strip().lower() == str(checker).strip().lower():
            raise SBLError(
                "SBL_E_SELF_CHECK_FORBIDDEN",
                "a maker may not verify its own work",
                {"gate_id": gate_id, "maker": maker},
            )
        if str(status) in PROXY_STATUSES:
            raise SBLError(
                "SBL_E_BAD_STATE",
                f"status {status!r} is a proxy status and cannot back a verdict",
                {"gate_id": gate_id, "status": status, "proxy_statuses": sorted(PROXY_STATUSES)},
            )
        ceiling_rank = CLAIM_RANKS.get(str(claim_ceiling))
        claim_rank = CLAIM_RANKS.get(str(claim))
        if ceiling_rank is None or claim_rank is None:
            raise SBLError(
                "SBL_E_BAD_STATE",
                "unknown claim level",
                {"claim_ceiling": claim_ceiling, "claim": claim},
            )
        if claim_rank > ceiling_rank:
            raise SBLError(
                "SBL_E_CLAIM_CEILING_EXCEEDED",
                f"claim {claim} exceeds ceiling {claim_ceiling}",
                {"claim": claim, "ceiling": claim_ceiling},
            )
        return Verdict(
            gate_id=str(gate_id),
            maker=str(maker),
            checker=str(checker),
            status=str(status),
            claim_level=str(claim),
        )
