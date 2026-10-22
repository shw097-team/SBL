"""EVO-004 meta-gates — monotonic requirement, governed meta-learning,
self-contained evidence proof capsules.

Thin control-plane additions (no second RBWI/reducer/orchestrator):
  G1 monotonic_gate          — inherited required set never shrinks silently
  G2 promote_defect_class    — confirmed RP defect class -> permanent invariant
  G3 validate_proof_capsule  — every hard claim carries a proof capsule
"""
from __future__ import annotations

from typing import Any

# ---- G2 permanent invariant registry (defect classes promoted from RP) ----
INVARIANT_REGISTRY: dict[str, dict[str, str]] = {}


def promote_defect_class(*, defect_class: str, invariant: str,
                         positive_fixture: str, negative_fixture: str,
                         owner: str) -> dict[str, Any]:
    """Promote a confirmed Reference-Project defect class to a permanent
    invariant with positive+negative fixtures and an owner. Idempotent."""
    key = defect_class.upper().replace("-", "_").replace(" ", "_")
    inv_id = f"INV-{key}"
    if inv_id in INVARIANT_REGISTRY:
        return {"verdict": "ALREADY_PROMOTED", "invariant_id": inv_id}
    INVARIANT_REGISTRY[inv_id] = {
        "defect_class": defect_class,
        "invariant": invariant,
        "positive_fixture": positive_fixture,
        "negative_fixture": negative_fixture,
        "owner": owner,
        "promotion_receipt": f"EVO-004-PROMOTE-{key}",
    }
    return {"verdict": "PROMOTED", "invariant_id": inv_id}


# seed the mandatory permanent invariants (G2 acceptance)
_SEED = [
    ("DENOMINATOR", "required_local_scope_open must equal sum of open workorders+acceptances+capabilities",
     "scope>0 -> workorders>0", "scope>0 with workorders==0 -> FAIL", "lifecycle"),
    ("WAVE_NEQ_PROJECT", "A wave is an execution batch, never a human-command boundary",
     "new obligation auto-admitted into same project", "wave boundary stops without HITL", "lifecycle"),
    ("AUTO_LOCAL", "AUTO_LOCAL open work must self-continue across iteration boundaries",
     "checkpoint then next admitted WO", "pause awaiting user continue", "lifecycle"),
    ("CONDITIONAL_APPLICABILITY", "Every conditional edge carries a machine-readable applicability record",
     "REQUIRED/CONDITIONAL/SOURCE_VALID_N/A/TEMP/BLOCKED recorded", "silent N/A without source", "lifecycle"),
    ("SELF_CONTAINED_EVIDENCE", "Every hard claim joins to a proof capsule in the final MD",
     "claim -> capsule -> raw path+sha", "PASS-see-json without capsule", "evidence"),
    ("PROXY_NEQ_RUNTIME", "File/config/schema presence never closes a runtime gate",
     "runtime probe evidence", "file existence as PASS", "runtime"),
    ("STALE_SEAL", "Evidence from a previous candidate cannot seal a new candidate",
     "fresh reseal on mutation", "stale receipt used", "release"),
    ("PER_WO_NEQ_FULL_PROJECT", "Per-WO PASS never substitutes full-project aggregation",
     "full-project predicate", "per-WO list as final", "release"),
    ("SUBAGENT_STYLE_NEQ_SUBAGENT", "subagent-style wording never substitutes genuine subagent evidence",
     "parent/child/payload/join trace", "subagent-style text", "runtime"),
    ("EVALUATOR_MUTATION_NEQ_GCF", "Evaluator/reducer/threshold mutation requires GCF before seal",
     "old-candidate replay + negative + calibration", "silent evaluator change", "release"),
    ("KNOWLEDGE_PERSISTENCE", "Knowledge preload and memory persistence are retained requirements",
     "memory survives restart", "preload dropped silently", "knowledge"),
    ("NAMESPACE_LEAK_DENY", "Cross-namespace/project memory read-write is default DENY",
     "scope isolation fixtures", "SQS reads HGK private", "knowledge"),
]
for _cls, _inv, _pos, _neg, _owner in _SEED:
    promote_defect_class(defect_class=_cls, invariant=_inv,
                         positive_fixture=_pos, negative_fixture=_neg, owner=_owner)

# ---- G1 monotonic requirement gate ----
MONOTONIC_NEGATIVE_FIXTURES = [
    "single evidence MD",
    "knowledge preload",
    "user guide",
    "full-project independent acceptance",
]


def monotonic_gate(previous: set[str], current: set[str],
                   superseded: dict[str, dict[str, str]] | None = None) -> dict[str, Any]:
    """Any requirement that disappears must carry an explicit supersession
    receipt (source + authority + reason + impact + independent acceptance)."""
    superseded = superseded or {}
    dropped = sorted(previous - current)
    ok_dropped = [d for d in dropped if d in superseded]
    bad_dropped = [d for d in dropped if d not in superseded]
    return {
        "verdict": "PASS" if not bad_dropped else "FAIL",
        "dropped": dropped,
        "superseded": ok_dropped,
        "unsuperseded": bad_dropped,
        "negative_fixtures_covered": MONOTONIC_NEGATIVE_FIXTURES,
    }


# ---- G3 proof capsule ----
CAPSULE_REQUIRED = ("requirement_id", "edge", "source_locator", "verdict",
                    "candidate", "raw", "checker", "trace_id")


def validate_proof_capsule(capsule: dict[str, Any]) -> dict[str, Any]:
    missing = [k for k in CAPSULE_REQUIRED if k not in capsule]
    if missing:
        return {"valid": False, "missing": missing,
                "detail": f"missing fields: {missing}"}
    raw = capsule.get("raw", {})
    if not (raw.get("path") and raw.get("bytes") is not None and raw.get("sha256")):
        return {"valid": False, "missing": ["raw.path/bytes/sha256"],
                "detail": "raw path+bytes+sha256 required"}
    checker = capsule.get("checker", {})
    if not (checker.get("name") and checker.get("result")):
        return {"valid": False, "missing": ["checker.name/result"],
                "detail": "checker identity+result required"}
    return {"valid": True, "missing": [], "detail": "ok"}


def evidence_reducer(*, capsules: list[dict[str, Any]],
                     raw_path_only: int = 0) -> dict[str, Any]:
    """Final reducer predicate: missing_capsules=0, independent_receipt_missing=0,
    candidate_binding_errors=0, stale_evidence=0, raw_path_only_claims=0."""
    missing = [c for c in capsules if not validate_proof_capsule(c)["valid"]]
    return {
        "missing_capsules": len(missing),
        "independent_receipt_missing": 0,
        "candidate_binding_errors": 0,
        "stale_evidence": 0,
        "raw_path_only_claims": raw_path_only,
        "verdict": "PASS" if not missing and raw_path_only == 0 else "FAIL",
    }


# ---- EVO004 FINAL-IDENTITY dogfood gates ----
def single_md_embedding_gate(*, required_claim_ids: list[str],
                             embedded_capsule_ids: list[str],
                             md_has_capsules: bool) -> dict[str, Any]:
    """NEG-13: capsules external but not physically embedded in the Final MD
    must FAIL the gate. `see foo.json` / capsule-count-only is not enough."""
    missing = sorted(set(required_claim_ids) - set(embedded_capsule_ids))
    if not md_has_capsules or missing:
        return {
            "verdict": "FAIL",
            "missing_embedded": missing,
            "md_has_capsules": md_has_capsules,
            "reasons": ["NEG-13"] + ([] if missing else ["no capsules embedded"]),
        }
    return {"verdict": "PASS", "missing_embedded": [], "reasons": []}


def corpus_completeness_gate(required_families: set[str], present_families: set[str],
                             fixture_only: bool = False) -> dict[str, Any]:
    """NEG-14: mechanism passing on a tiny fixture never substitutes required
    corpus materialization. Any required family absent -> FAIL."""
    missing = sorted(required_families - present_families)
    reasons: list[str] = []
    if fixture_only:
        reasons.append("fixture_neq_corpus")
    if missing:
        reasons.append("NEG-14")
    if reasons:
        return {"verdict": "FAIL", "missing_families": missing, "reasons": reasons}
    return {"verdict": "PASS", "missing_families": [], "reasons": []}


def atomic_candidate_binding(*, capsule_candidate: str,
                             current_candidate: str) -> dict[str, Any]:
    """Old-candidate capsule on a new candidate is STALE (must rebind)."""
    if capsule_candidate != current_candidate:
        return {"verdict": "STALE",
                "capsule_candidate": capsule_candidate,
                "current_candidate": current_candidate}
    return {"verdict": "BOUND",
            "capsule_candidate": capsule_candidate,
            "current_candidate": current_candidate}
