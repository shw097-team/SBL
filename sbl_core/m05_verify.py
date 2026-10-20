"""SBLM05 - Evidence Verification.

Two governance properties are enforced here and both were open findings in the first
independent challenge:

* the claim ceiling belongs to the instance (the build declares ``LOCAL``); a caller may ask
  for a *lower* ceiling but can never raise it (SEC-02);
* a verdict is bound to recorded evidence for the same gate, and only a small declared set of
  real statuses may back a verdict -- proxy statuses are refused after normalisation, so
  ``file_exists`` / ``FILE_EXISTS `` cannot slip through (SEC-03).
"""

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

#: The ceiling this build may ever claim. Release/production needs a separate human/native gate.
BUILD_CEILING = "LOCAL"

PROXY_STATUSES = frozenset({"FILE_EXISTS", "SYMBOL_EXISTS", "SUMMARY_ONLY", "DOCUMENTED"})

REAL_STATUSES = frozenset({"PASS", "FAIL", "BLOCKED_HITL", "BLOCKED_EXTERNAL"})


def _norm_status(status: object) -> str:
    return str(status).strip().upper()


class EvidenceVerification:
    """Records evidence and issues non-self-signed, ceiling-bounded verdicts."""

    def __init__(self, ceiling: str = BUILD_CEILING) -> None:
        if str(ceiling) not in CLAIM_RANKS:
            raise SBLError("SBL_E_BAD_STATE", "unknown build ceiling", {"ceiling": str(ceiling)})
        self.ceiling = str(ceiling)
        self._evidence: dict[str, EvidenceItem] = {}

    # -- evidence ---------------------------------------------------------
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
        item = EvidenceItem(
            gate_id=str(gate_id),
            command=str(command),
            exit_code=int(exit_code),
            stdout_sha256=digest,
            denominator=denominator,
        )
        self._evidence[str(gate_id)] = item
        return item

    def evidence_for(self, gate_id: str) -> EvidenceItem:
        try:
            return self._evidence[str(gate_id)]
        except KeyError:
            raise SBLError(
                "SBL_E_BAD_STATE",
                "no recorded evidence for this gate",
                {"reason": "no_recorded_evidence", "gate_id": str(gate_id)},
            ) from None

    # -- verdict ----------------------------------------------------------
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

        normalised = _norm_status(status)
        if normalised in PROXY_STATUSES:
            raise SBLError(
                "SBL_E_BAD_STATE",
                f"status {status!r} is a proxy status and cannot back a verdict",
                {"gate_id": gate_id, "status": status, "proxy_statuses": sorted(PROXY_STATUSES)},
            )
        if normalised not in REAL_STATUSES:
            raise SBLError(
                "SBL_E_BAD_STATE",
                "status is not one of the declared real statuses",
                {"gate_id": gate_id, "status": status, "allowed": sorted(REAL_STATUSES)},
            )

        evidence = self.evidence_for(gate_id)
        if evidence.exit_code != 0:
            raise SBLError(
                "SBL_E_BAD_STATE",
                "recorded evidence for this gate did not exit zero",
                {
                    "reason": "evidence_exit_nonzero",
                    "gate_id": str(gate_id),
                    "exit_code": evidence.exit_code,
                },
            )

        requested_rank = CLAIM_RANKS.get(str(claim_ceiling))
        claim_rank = CLAIM_RANKS.get(str(claim))
        if requested_rank is None or claim_rank is None:
            raise SBLError(
                "SBL_E_BAD_STATE",
                "unknown claim level",
                {"claim_ceiling": claim_ceiling, "claim": claim},
            )
        ceiling_rank = CLAIM_RANKS[self.ceiling]
        if requested_rank > ceiling_rank:
            raise SBLError(
                "SBL_E_CLAIM_CEILING_EXCEEDED",
                f"ceiling {claim_ceiling} exceeds the build ceiling {self.ceiling}",
                {"requested": str(claim_ceiling), "build_ceiling": self.ceiling},
            )
        if claim_rank > requested_rank:
            raise SBLError(
                "SBL_E_CLAIM_CEILING_EXCEEDED",
                f"claim {claim} exceeds ceiling {claim_ceiling}",
                {"claim": claim, "ceiling": claim_ceiling},
            )
        return Verdict(
            gate_id=str(gate_id),
            maker=str(maker),
            checker=str(checker),
            status=normalised,
            claim_level=str(claim),
        )
