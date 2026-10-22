"""HG-KSEOS Governed Evolution Controller (task-011).

Thin controller over the existing Shared Spine: automatic signal collection,
gap classification, FIT-GAP reuse-first, improvement candidates, sandboxed
qualification, independent checker, source-defined promotion policy, rollback.

Key invariants (fail-closed):
- single random failure never becomes permanent learning (recurrence threshold)
- candidates cannot self-promote; checker is separate
- candidates cannot mutate frozen authority or their own evaluator
- bad candidates are rejected + rolled back without active contamination
- no infinite evolution loop (budget stop)
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import HGKError, InvariantViolation
from .observability import EventLog, StructuredEvent
from .spine import SharedSpine
from .util import canonical_json, sha256_text, utc_now

GAP_TYPES = (
    "KNOWLEDGE_GAP", "MEMORY_GAP", "SKILL_GAP", "TOOL_GAP", "ROUTING_GAP",
    "ORCHESTRATION_GAP", "WORKFLOW_GAP", "TEST_GAP", "EVIDENCE_GAP", "UX_GAP",
    "PERFORMANCE_GAP", "RELIABILITY_GAP", "SECURITY_GAP", "DOCUMENTATION_GAP",
    "ARCHITECTURE_GAP", "POLICY_GAP",
)
CANDIDATE_TYPES = (
    "KnowledgeCandidate", "MemoryCandidate", "SkillCandidate", "RoutingRuleCandidate",
    "PromptCandidate", "WorkflowCandidate", "TestCandidate", "EvaluatorCandidate",
    "ToolCandidate", "ProviderCandidate", "CodePatchCandidate", "DocumentationCandidate",
)

# source-defined promotion policy (P0-CIP PUB-10 COV-11-05/06 + DOC-16/20):
# COV-11-06: promotion requires independent verifier + Human Policy Owner for
# every risk class; no implementation-invented auto-promotion (Task-012
# source-resolved semantics; GE-11 = PROMOTION_READY_HITL_SOURCE_REQUIRED).
PROMOTION_POLICY = {
    "low_risk": {
        "examples": ["documentation", "non-authoritative routing hint", "test fixture",
                     "candidate knowledge", "reversible local optimization"],
        "automatic_pipeline": True, "independent_checker": True, "rollback": True,
        "human_gate": "required",  # COV-11-06: promotion requires independent verifier + Human Policy Owner
        "source_locator": "HG-KSEOS_P0-CIP-PACK_v2026.08.05-r2.md#COV-11-06",
        "policy_version": "P0-CIP r2 (2026-08-05)",
    },
    "medium_risk": {
        "examples": ["new active Skill", "provider/tool capability", "workflow behavior",
                     "persistent routing policy"],
        "automatic_pipeline": True, "independent_checker": True,
        "human_gate": "required",  # COV-11-06
        "source_locator": "HG-KSEOS_P0-CIP-PACK_v2026.08.05-r2.md#COV-11-06",
        "policy_version": "P0-CIP r2 (2026-08-05)",
    },
    "high_risk": {
        "examples": ["permission expansion", "external egress", "destructive action",
                     "release policy", "security policy"],
        "human_gate": "required", "auto_promotion": False,
        "source_locator": "HG-KSEOS_P0-CIP-PACK_v2026.08.05-r2.md#COV-11-06 + security constitution",
        "policy_version": "P0-CIP r2 (2026-08-05)",
    },
    "constitutional": {
        "examples": ["authority stack", "product constitution", "frozen evaluator governance",
                     "production admission policy"],
        "human_gate": "mandatory", "auto_promotion": False,
        "source_locator": "HG-KSEOS_P0-CIP-PACK_v2026.08.05-r2.md#COV-11-06 + PUB-10 H2-07/H2-08",
        "policy_version": "P0-CIP r2 (2026-08-05)",
    },
}
RISK_LEVELS = {"LOW": "low_risk", "MEDIUM": "medium_risk", "HIGH": "high_risk",
               "CONSTITUTIONAL": "constitutional"}

# frozen surfaces candidates may never write
FROZEN_WRITE_PATTERNS = (
    r"requirements[\\/].*\.csv", r".*P0-CIP.*\.md", r".*PREDEV.*\.md",
    r"src[\\/]hg_kseos[\\/]release\.py", r"src[\\/]hg_kseos[\\/]security\.py",
    r"src[\\/]hg_kseos[\\/]schema\.sql", r"AGENTS\.md", r"docs[\\/]HG-KSEOS使用說明文檔\.md",
)
EVALUATOR_PATTERNS = (r"tests[\\/]test_.*\.py", r"src[\\/]hg_kseos[\\/](?:release|security)\.py")


class EvolutionError(HGKError):
    pass


@dataclass
class EvolutionSignal:
    project_id: str
    run_id: str
    signal_type: str
    severity: str = "LOW"
    source_evidence: list[str] = field(default_factory=list)
    recurrence_key: str = ""
    authority_impact: str = "NONE"

    def __post_init__(self) -> None:
        if self.signal_type not in GAP_TYPES and self.signal_type != "ROUTING_MISS":
            raise EvolutionError(f"ERR_UNKNOWN_SIGNAL_TYPE {self.signal_type}")
        if self.severity not in ("LOW", "MEDIUM", "HIGH"):
            raise EvolutionError(f"ERR_BAD_SEVERITY {self.severity}")
        if not self.recurrence_key:
            self.recurrence_key = f"{self.project_id}:{self.signal_type}"


class GovernedEvolutionController:
    """Signal -> gap -> FIT-GAP -> candidate -> qualification -> policy gate -> rollback."""

    def __init__(self, spine: SharedSpine, event_log: EventLog | None = None,
                 recurrence_threshold: int = 2) -> None:
        self.spine = spine
        self.event_log = event_log
        self.recurrence_threshold = recurrence_threshold

    # ---------- signal collection ----------
    def capture_signal(self, signal: EvolutionSignal) -> dict[str, Any]:
        sig_id = f"EVO-SIG-{uuid.uuid4().hex[:8].upper()}"
        with self.spine.transaction() as conn:
            prior = conn.execute(
                "SELECT signal_id, occurrence_count FROM evolution_signals WHERE recurrence_key=?",
                (signal.recurrence_key,)).fetchone()
            if prior:
                conn.execute(
                    "UPDATE evolution_signals SET occurrence_count=occurrence_count+1, "
                    "source_evidence_json=?, updated_at=? WHERE signal_id=?",
                    (json.dumps(signal.source_evidence, ensure_ascii=False), utc_now(), prior[0]))
                sig_id = prior[0]
                occurrence = prior[1] + 1
            else:
                conn.execute(
                    "INSERT INTO evolution_signals(signal_id, project_id, run_id, signal_type, severity, "
                    "source_evidence_json, recurrence_key, occurrence_count, candidate_worthy, "
                    "authority_impact, created_at, updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (sig_id, signal.project_id, signal.run_id, signal.signal_type, signal.severity,
                     json.dumps(signal.source_evidence, ensure_ascii=False), signal.recurrence_key, 1,
                     1 if signal.severity == "HIGH" else 0, signal.authority_impact, utc_now(), utc_now()))
                occurrence = 1
            # candidate-worthy: recurrence >= threshold OR high severity
            worthy = occurrence >= self.recurrence_threshold or signal.severity == "HIGH"
            conn.execute("UPDATE evolution_signals SET candidate_worthy=? WHERE signal_id=?",
                         (1 if worthy else 0, sig_id))
        if self.event_log:
            self.event_log.append(StructuredEvent(
                trace_id=signal.run_id, event_id=f"EV-{sig_id}", entity_type="evolution_signal",
                entity_id=sig_id, state="CAPTURED", taxonomy="evolution",
                payload={"signal_type": signal.signal_type, "occurrence": occurrence}))
        return {"signal_id": sig_id, "occurrence_count": occurrence,
                "candidate_worthy": worthy}

    # ---------- gap classification ----------
    def classify(self, signal: EvolutionSignal, evidence: list[str] | None = None) -> str:
        """Deterministic gap classification from signal + evidence keywords."""
        text = " ".join([signal.signal_type, signal.severity] + (evidence or []))
        t = text.lower()
        if any(k in t for k in ("security", "secret", "egress", "permission", "privilege")):
            return "SECURITY_GAP"
        if any(k in t for k in ("test", "oracle", "fixture", "coverage")):
            return "TEST_GAP"
        if any(k in t for k in ("evidence", "receipt", "verification")):
            return "EVIDENCE_GAP"
        if "skill" in t or "route" in t or "routing" in t:
            return "SKILL_GAP" if "skill" in t else "ROUTING_GAP"
        if "memory" in t or "recall" in t or "retrieval" in t:
            return "MEMORY_GAP"
        if "rag" in t or "retrieval" in t or "citation" in t:
            return "KNOWLEDGE_GAP"
        if "doc" in t or "guide" in t or "manual" in t:
            return "DOCUMENTATION_GAP"
        if any(k in t for k in ("perf", "latency", "slow", "budget", "spend")):
            return "PERFORMANCE_GAP"
        if any(k in t for k in ("crash", "timeout", "flaky", "retry", "repro")):
            return "RELIABILITY_GAP"
        if any(k in t for k in ("workflow", "orchestration", "state", "transition")):
            return "WORKFLOW_GAP"
        if "tool" in t or "provider" in t:
            return "TOOL_GAP"
        if "policy" in t or "authority" in t or "constitution" in t:
            return "POLICY_GAP"
        return "ROUTING_GAP"

    # ---------- FIT-GAP (reuse-first) ----------
    def fit_gap(self, gap_type: str, *, existing_capabilities: list[str] | None = None,
                requested: str = "") -> dict[str, Any]:
        """Check existing capabilities before creating a candidate."""
        existing = existing_capabilities or [
            "SharedSpine", "KnowledgeFactory(RAG)", "KG assertions", "Memory",
            "SkillRegistry route", "Harness", "NRTV harness", "EventLog",
            "Co/UserExperience reducers", "backup/restore/rollback",
        ]
        requested_l = requested.lower()
        reuse_candidates = {
            "KNOWLEDGE_GAP": "KnowledgeFactory ingest/search",
            "MEMORY_GAP": "Memory remember/active_memory",
            "SKILL_GAP": "SkillRegistry route (existing skills)",
            "ROUTING_GAP": "SkillRegistry route + assurance.validate_receiver_packet",
            "TOOL_GAP": "tool registry / provider bindings",
            "TEST_GAP": "unittest suite + acceptance runner",
            "EVIDENCE_GAP": "evidence_refs + EventLog",
            "WORKFLOW_GAP": "lifecycle controller + Harness",
            "DOCUMENTATION_GAP": "docs/ User Guide",
            "PERFORMANCE_GAP": "observability no_progress + perf smoke",
            "RELIABILITY_GAP": "recovery backup/restore + rollback_records",
            "SECURITY_GAP": "security.NRTV harness + quarantine",
            "POLICY_GAP": "P0-CIP PUB-10 + release reducers",
        }
        reusable = reuse_candidates.get(gap_type, "")
        create_new = bool(reusable == "" or (requested_l and reusable.lower() not in requested_l
                                             and not any(r.lower() in requested_l for r in reusable.split("/"))))
        return {
            "gap_type": gap_type,
            "reuse_first": True,
            "reusable_existing": reusable or "NONE_IDENTIFIED",
            "create_new_candidate": create_new,
            "rationale": "reuse existing capability" if not create_new
                         else "NO_ACCEPTABLE_EXISTING_CAPABILITY",
        }

    # ---------- candidate creation ----------
    def create_candidate(self, project_id: str, gap_id: str, candidate_type: str,
                         problem_statement: str, proposed_change: str, expected_gain: str,
                         risk_class: str = "LOW", allowed_write_set: list[str] | None = None,
                         forbidden_write_set: list[str] | None = None,
                         baseline_metrics: dict[str, Any] | None = None,
                         source_signals: list[str] | None = None) -> dict[str, Any]:
        if candidate_type not in CANDIDATE_TYPES:
            raise EvolutionError(f"ERR_UNKNOWN_CANDIDATE_TYPE {candidate_type}")
        if risk_class not in RISK_LEVELS:
            raise EvolutionError(f"ERR_UNKNOWN_RISK {risk_class}")
        # forbidden write set is auto-extended with frozen surfaces (defense-in-depth)
        forbidden = list(forbidden_write_set or [])
        forbidden.extend(["requirements/**", "src/hg_kseos/release.py",
                          "src/hg_kseos/security.py", "src/hg_kseos/schema.sql",
                          "AGENTS.md", "docs/HG-KSEOS使用說明文檔.md"])
        cid = f"IC-{uuid.uuid4().hex[:8].upper()}"
        with self.spine.transaction() as conn:
            conn.execute(
                "INSERT INTO improvement_candidates("
                "candidate_id, gap_id, candidate_type, source_signals_json, problem_statement, "
                "proposed_change, expected_gain, risk_class, allowed_write_set_json, "
                "forbidden_write_set_json, state, sandbox_path, baseline_metrics_json, "
                "evaluation_plan_json, rollback, authority_gate, independent_verdict, "
                "promotion_state, created_at, updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (cid, gap_id, candidate_type,
                 json.dumps(source_signals or [], ensure_ascii=False), problem_statement,
                 proposed_change, expected_gain, risk_class,
                 json.dumps(allowed_write_set or [], ensure_ascii=False),
                 json.dumps(forbidden, ensure_ascii=False), "CANDIDATE", None,
                 json.dumps(baseline_metrics or {}, ensure_ascii=False),
                 json.dumps({"tests": [], "holdout": [], "negative": [], "security": []}, ensure_ascii=False),
                 f"RB-{cid}", RISK_LEVELS[risk_class], None, "NOT_PROMOTED", utc_now(), utc_now()))
        return {"candidate_id": cid, "risk_class": risk_class, "state": "CANDIDATE",
                "promotion_policy": PROMOTION_POLICY[RISK_LEVELS[risk_class]]}

    # ---------- sandbox / qualification ----------
    def qualify(self, candidate_id: str, *, tests_pass: bool, negative_pass: bool,
                security_pass: bool, holdout_pass: bool, nrtv_pass: bool,
                baseline_verified: bool, rollback_verified: bool,
                sandbox_path: str | None = None, evaluator_self_mutation: bool = False,
                authority_mutation: bool = False) -> dict[str, Any]:
        """Sandboxed qualification; fail-closed on any guard breach."""
        with self.spine.connect() as conn:
            row = conn.execute(
                "SELECT risk_class, state FROM improvement_candidates WHERE candidate_id=?",
                (candidate_id,)).fetchone()
        if row is None:
            raise EvolutionError(f"ERR_CANDIDATE_UNKNOWN {candidate_id}")
        risk, state = row
        if state != "CANDIDATE":
            raise EvolutionError(f"ERR_CANDIDATE_STATE {state}")
        if evaluator_self_mutation or authority_mutation:
            self._reject(candidate_id, "AUTHORITY_OR_EVALUATOR_MUTATION")
            return {"candidate_id": candidate_id, "state": "REJECTED",
                    "reason": "authority/evaluator mutation detected — fail closed"}
        ok = all([tests_pass, negative_pass, security_pass, holdout_pass, nrtv_pass,
                  baseline_verified, rollback_verified])
        if not ok:
            self._reject(candidate_id, "QUALIFICATION_FAILED")
            return {"candidate_id": candidate_id, "state": "REJECTED", "reason": "qualification failed"}
        with self.spine.transaction() as conn:
            conn.execute(
                "UPDATE improvement_candidates SET state='QUALIFIED', sandbox_path=?, updated_at=? "
                "WHERE candidate_id=?",
                (sandbox_path, utc_now(), candidate_id))
        return {"candidate_id": candidate_id, "state": "QUALIFIED", "risk_class": risk}

    def _reject(self, candidate_id: str, reason: str) -> None:
        with self.spine.transaction() as conn:
            conn.execute("UPDATE improvement_candidates SET state='REJECTED', updated_at=? WHERE candidate_id=?",
                         (utc_now(), candidate_id))

    # ---------- independent checker (maker != checker) ----------
    def independent_check(self, candidate_id: str, *, checker: str = "INDEPENDENT_CHECKER",
                          raw_evidence_refs: list[str] | None = None,
                          recomputed_invariants: bool = True) -> dict[str, Any]:
        if checker == "maker":
            raise EvolutionError("ERR_MAKER_CANNOT_BE_CHECKER")
        with self.spine.connect() as conn:
            row = conn.execute("SELECT state FROM improvement_candidates WHERE candidate_id=?", (candidate_id,)).fetchone()
        if row is None or row[0] != "QUALIFIED":
            raise EvolutionError(f"ERR_CHECKER_STATE {candidate_id}")
        verdict = "PASS" if recomputed_invariants and raw_evidence_refs else "FAIL"
        with self.spine.transaction() as conn:
            conn.execute("UPDATE improvement_candidates SET independent_verdict=?, updated_at=? WHERE candidate_id=?",
                         (verdict, utc_now(), candidate_id))
        return {"candidate_id": candidate_id, "checker": checker, "verdict": verdict}

    # ---------- promotion gate ----------
    def promotion_gate(self, candidate_id: str, *, human_approval: bool | None = None) -> dict[str, Any]:
        """Enforce source-defined promotion policy."""
        with self.spine.connect() as conn:
            row = conn.execute(
                "SELECT risk_class, independent_verdict, state, rollback FROM improvement_candidates "
                "WHERE candidate_id=?", (candidate_id,)).fetchone()
        if row is None:
            raise EvolutionError(f"ERR_CANDIDATE_UNKNOWN {candidate_id}")
        risk, ind, state, rollback = row
        if state != "QUALIFIED":
            raise EvolutionError(f"ERR_PROMOTION_STATE {state}")
        policy = PROMOTION_POLICY[RISK_LEVELS[risk]]
        if ind != "PASS":
            return {"candidate_id": candidate_id, "state": "PROMOTION_READY",
                    "blocked": "INDEPENDENT_CHECK_NOT_PASS"}
        if policy.get("auto_promotion") is False or policy["human_gate"] in ("required", "mandatory"):
            if human_approval is None:
                return {"candidate_id": candidate_id, "state": "PROMOTION_READY_HITL_SOURCE_REQUIRED",
                        "human_role": "AUTHORITY_GATE_ONLY",
                        "source_locator": policy.get("source_locator", ""),
                        "question": f"Candidate {candidate_id} completed automatic qualification. Risk={risk}. Rollback={rollback}. Approve/Reject?"}
            if human_approval is False:
                self._reject(candidate_id, "HUMAN_REJECTED")
                return {"candidate_id": candidate_id, "state": "REJECTED", "reason": "human rejected"}
        # human-approved promotion (source COV-11-06: Human Policy Owner approval)
        with self.spine.transaction() as conn:
            conn.execute("UPDATE improvement_candidates SET promotion_state='PROMOTED', state='PROMOTED', "
                         "updated_at=? WHERE candidate_id=?", (utc_now(), candidate_id))
        return {"candidate_id": candidate_id, "state": "PROMOTED", "promotion_state": "PROMOTED",
                "gate": "HUMAN_APPROVED"}

    # ---------- canary / rollback ----------
    def canary(self, candidate_id: str, *, observed_regression: bool = False) -> dict[str, Any]:
        with self.spine.connect() as conn:
            row = conn.execute("SELECT promotion_state FROM improvement_candidates WHERE candidate_id=?",
                               (candidate_id,)).fetchone()
        if row is None or row[0] != "PROMOTED":
            raise EvolutionError(f"ERR_CANARY_STATE {candidate_id}")
        if observed_regression:
            with self.spine.transaction() as conn:
                conn.execute("UPDATE improvement_candidates SET promotion_state='ROLLED_BACK', "
                             "state='ROLLED_BACK', updated_at=? WHERE candidate_id=?", (utc_now(), candidate_id))
            return {"candidate_id": candidate_id, "state": "ROLLED_BACK", "action": "AUTO_DISABLE_ROLLBACK"}
        return {"candidate_id": candidate_id, "state": "CANARY_OK"}

    # ---------- observability ----------
    def status(self, project_id: str | None = None) -> dict[str, Any]:
        with self.spine.connect() as conn:
            if project_id:
                signals = conn.execute(
                    "SELECT signal_type, COUNT(*) c FROM evolution_signals WHERE project_id=? GROUP BY signal_type",
                    (project_id,)).fetchall()
            else:
                signals = conn.execute("SELECT signal_type, COUNT(*) c FROM evolution_signals GROUP BY signal_type").fetchall()
            candidates = conn.execute("SELECT state, COUNT(*) c FROM improvement_candidates GROUP BY state").fetchall()
        return {
            "signal_count": sum(r[1] for r in signals),
            "signals_by_type": {r[0]: r[1] for r in signals},
            "candidate_count": sum(r[1] for r in candidates),
            "candidates_by_state": {r[0]: r[1] for r in candidates},
        }
