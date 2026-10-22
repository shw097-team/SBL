"""Bounded HG-KSEOS-side semantic oracle; does not replace PIPD schema authority.

Call after source-owned schema validation and before emitting an artifact. A
VIOLATED result is a refusal, not an exception. SATISFIED covers only the named
predicate; NOT_APPLICABLE is not permission to bypass schema validation.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, TypedDict

Verdict = Literal["SATISFIED", "VIOLATED", "NOT_APPLICABLE"]
Predicate = Literal["semantic.distinct", "semantic.claim_gate"]


class SemanticResult(TypedDict):
    predicate: Predicate
    verdict: Verdict
    reasons: list[str]
    evidence: dict[str, object]


def _identity(value: object) -> str:
    return "".join(value.split()).casefold() if isinstance(value, str) else ""


def _result(predicate: Predicate, verdict: Verdict, reasons: list[str],
            evidence: dict[str, object]) -> SemanticResult:
    return {"predicate": predicate, "verdict": verdict, "reasons": reasons, "evidence": evidence}


def check_distinct(payload: Mapping[str, object],
                   output: Mapping[str, object] | None = None) -> SemanticResult:
    """Enforce maker/checker separation, NOT generic item novelty or reordering.

    PIPD assurance NEG-001 says "maker aliased as checker fails the SoD rule
    (TQ_SOD) even though the shape is valid": Maker-A vs ' maker-a '. Infer
    case/whitespace-insensitive identity inequality, corroborated by SKILL.md
    rule 2. Inspect input roles and optional emitted acceptance roles. Missing
    or blank roles violate an applicable pair; no roles means NOT_APPLICABLE.
    This detects textual aliases only, not concealed real-world shared actors.
    """
    pairs = []
    if "maker" in payload or "checker" in payload:
        pairs.append(("input", payload.get("maker"), payload.get("checker")))
    acceptance = output.get("acceptance", []) if output is not None else []
    if isinstance(acceptance, list):
        for index, row in enumerate(acceptance):
            if isinstance(row, Mapping):
                pairs.append((f"output.acceptance[{index}]", row.get("maker_identity"),
                              row.get("checker_identity")))
    evidence: dict[str, object] = {"identity_pairs": [
        {"location": location, "maker": maker, "checker": checker,
         "normalized": [_identity(maker), _identity(checker)]}
        for location, maker, checker in pairs
    ]}
    if not pairs:
        return _result("semantic.distinct", "NOT_APPLICABLE", ["No maker/checker roles."], evidence)
    reasons = [f"{location}: blank identities or maker aliases checker (TQ_SOD)."
               for location, maker, checker in pairs
               if not _identity(maker) or not _identity(checker)
               or _identity(maker) == _identity(checker)]
    return _result("semantic.distinct", "VIOLATED" if reasons else "SATISFIED",
                   reasons or ["Maker and checker identities are distinct in every supplied pair."],
                   evidence)


GATED_CLAIMS = frozenset({"LOCAL_QUALIFIED", "INDEPENDENT_PASS", "PUBLICATION_APPROVED",
                          "RELEASED", "PRODUCTION_VERIFIED"})


def check_claim_gate(payload: Mapping[str, object],
                     output: Mapping[str, object] | None = None) -> SemanticResult:
    """Require nonblank approval receipt and independent checker for gated claims.

    PIPD package NEG-001 says "LOCAL_QUALIFIED without a bound approval receipt
    and checker identity is refused". POS-001 supplies approval.checker_identity
    and approval.approval_receipt; POS-002 explicitly needs no approval below
    LOCAL_QUALIFIED. SKILL.md rule 4 extends the gate through the higher rungs.
    Gate both requested and optionally emitted claims, using input approval;
    evidence expectations in an output are not actual approval receipts.
    Nonblank receipt presence is checkable here; authenticity, candidate-hash
    binding and real-world independence require an external receipt verifier.
    """
    claims: list[str] = []
    for record in (payload, output):
        candidate = record.get("allowed_claims") if record is not None else None
        if isinstance(candidate, list):
            claims.extend(claim for claim in candidate if isinstance(claim, str))
    gated = sorted(set(claims) & GATED_CLAIMS)
    evidence: dict[str, object] = {"claims": claims, "gated_claims": gated}
    if not gated:
        return _result("semantic.claim_gate", "NOT_APPLICABLE",
                       ["No LOCAL_QUALIFIED-or-higher claim; schema checks remain required."], evidence)
    approval = payload.get("approval")
    approval = approval if isinstance(approval, Mapping) else {}
    missing = [f"approval.{field}" for field in ("checker_identity", "approval_receipt")
               if not isinstance(approval.get(field), str) or not str(approval[field]).strip()]
    evidence.update({"approval": dict(approval), "missing_fields": missing,
                     "producer": payload.get("producer")})
    reasons = [f"Missing or empty required evidence: {field} (EVIDENCE_GAP)." for field in missing]
    if _identity(approval.get("checker_identity")) == _identity(payload.get("producer")):
        reasons.append("Approval checker aliases the producer; self-approval is refused.")
    return _result("semantic.claim_gate", "VIOLATED" if reasons else "SATISFIED",
                   reasons or ["Gated claims have a nonblank receipt and distinct checker identity."],
                   evidence)
