from __future__ import annotations

import json
from dataclasses import dataclass, field, MISSING
from typing import Any

from .spine import SharedSpine
from .util import canonical_json, new_id, sha256_text, utc_now


@dataclass(frozen=True)
class EvidenceEnvelope:
    requirements_total: int
    requirements_passed: int
    blocking_tests_passed: bool
    security_critical: int
    rollback_passed: bool
    restore_passed: bool
    independent_passed: bool
    provider_lifecycle_closed: bool
    user_guide_complete: bool
    raw_evidence_complete: bool
    open_blocking_tt: int
    checker: str
    artifacts: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "EvidenceEnvelope":
        required = {field.name for field in cls.__dataclass_fields__.values()}
        missing = required - value.keys()
        if missing:
            raise ValueError(f"ERR_EVIDENCE_ENVELOPE_MISSING:{sorted(missing)}")
        value = dict(value)
        value["artifacts"] = tuple(value["artifacts"])
        return cls(**{key: value[key] for key in required})


class ReleaseReducer:
    VERSION = "1"

    def __init__(self, spine: SharedSpine) -> None:
        self.spine = spine

    def reduce(self, envelope: EvidenceEnvelope) -> dict[str, Any]:
        reasons: list[str] = []
        if envelope.requirements_total <= 0 or envelope.requirements_passed != envelope.requirements_total:
            reasons.append("REQUIREMENT_COVERAGE_INCOMPLETE")
        if not envelope.blocking_tests_passed:
            reasons.append("BLOCKING_TEST_FAILURE")
        if envelope.security_critical:
            reasons.append("SECURITY_CRITICAL_NONZERO")
        if not envelope.rollback_passed or not envelope.restore_passed:
            reasons.append("RECOVERY_NOT_PROVEN")
        if not envelope.independent_passed or not envelope.checker:
            reasons.append("INDEPENDENT_ACCEPTANCE_MISSING")
        if not envelope.provider_lifecycle_closed:
            reasons.append("PROVIDER_LIFECYCLE_OPEN")
        if not envelope.user_guide_complete:
            reasons.append("USER_GUIDE_INCOMPLETE")
        if not envelope.raw_evidence_complete or not envelope.artifacts:
            reasons.append("RAW_EVIDENCE_INCOMPLETE")
        if envelope.open_blocking_tt:
            reasons.append("RELEASE_BLOCKING_TT_OPEN")
        verdict = "HG-KSEOS_LOCAL_DELIVERY_PASS" if not reasons else "FAIL_CLOSED"
        envelope_json = canonical_json(envelope.__dict__)
        decision = {
            "decision_id": new_id("REL"),
            "candidate_digest": sha256_text(envelope_json),
            "reducer_version": self.VERSION,
            "verdict": verdict,
            "reasons": reasons,
            "checker": envelope.checker,
            "created_at": utc_now(),
        }
        with self.spine.transaction() as connection:
            connection.execute(
                """INSERT INTO release_decisions
                   (decision_id,candidate_digest,reducer_version,verdict,reasons_json,
                    independent_checker,evidence_envelope,created_at)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (
                    decision["decision_id"],
                    decision["candidate_digest"],
                    self.VERSION,
                    verdict,
                    json.dumps(reasons),
                    envelope.checker,
                    envelope_json,
                    decision["created_at"],
                ),
            )
        return decision


# Terminal statuses acceptable for a coverage domain (指令-4 §11 / §13).
TERMINAL_STATUSES = {
    "RUNTIME_PASS",
    "DEFERRED_SOURCE_BACKED",
    "NOT_APPLICABLE_SOURCE_BACKED",
    "PROHIBITED_SOURCE_BACKED",
}
FORBIDDEN_DOMAIN_STATUSES = {
    "UNKNOWN",
    "MISSING",
    "DESIGN_ONLY_WHEN_RUNTIME_REQUIRED",
    "STATIC_ONLY_WHEN_RUNTIME_REQUIRED",
    "OPEN_BLOCKING_TT",
}


@dataclass(frozen=True)
class CoverageEnvelope:
    """Coverage-complete final gate input (指令-4 §13 schema)."""

    coverage_domains_total: int
    coverage_domains_terminal: int
    subcapabilities_total: int
    subcapabilities_terminal: int
    canonical_requirements_total: int
    requirements_reconciled: bool
    requirements_domain_mapped: int
    requirements_source_bound: int
    requirement_owner_matches_domain_owner: int
    requirement_owner_source_validated: int
    unsupported_disposition_count: int
    orphan_requirements: int
    unowned_mandatory_assets: int
    runtime_pass_missing_evidence: int
    active_deferred_contradiction: int
    missing_evidence_refs: int
    tst_total: int
    tst_independent_pass: int
    semantic_depth_calibrated: bool
    runtime_required_static_only_count: int
    current_executor_missing: int
    raw_receipt_missing: int
    domains: dict[str, str]
    knowledge_security_negative: str
    domain_blocking_gaps: int
    hermes_provider: str
    hermes_model: str
    codex_cli_primary_executor: bool
    opencodex_transport: bool
    openai_model_fallback: bool
    protected_identities_78_disposition_complete: bool
    mandatory_default_active_providers_certified: bool
    tst_054: str
    tst_092: str
    product_tests_all_pass: bool
    hlpe_tests_all_pass: bool
    security_blockers: int
    blocking_tt: int
    backup_restore_pass: bool
    rollback_pass: bool
    sbom_current: bool
    user_guide_exists: bool
    user_guide_runtime_consistent: bool
    user_guide_sha256_verified: bool
    package_exact_readback: bool
    final_head_independently_checked: bool
    final_evidence_md_exists: bool
    final_evidence_md_readback_verified: bool
    checker: str
    artifacts: tuple[str, ...]
    # ── Task-014 named-method activation invariants (all default 0 = PASS) ──
    canonical_flow_named_method_without_runtime_or_certified_substitute: int = 0
    active_named_method_missing_identity: int = 0
    active_named_method_missing_pin: int = 0
    active_named_method_missing_install: int = 0
    active_named_method_missing_binding: int = 0
    active_named_method_missing_doctor: int = 0
    active_named_method_missing_pilot: int = 0
    active_named_method_missing_independent_cert: int = 0
    active_named_method_silent_fallback: int = 0
    named_method_fake_invocation: int = 0
    named_method_silent_fallback: int = 0
    dual_spec_owner: int = 0
    second_orchestrator: int = 0
    release_authority_escape: int = 0

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CoverageEnvelope":
        required = {field.name for field in cls.__dataclass_fields__.values()
                    if field.default is MISSING and field.default_factory is MISSING}
        missing = required - value.keys()
        if missing:
            raise ValueError(f"ERR_COVERAGE_ENVELOPE_MISSING:{sorted(missing)}")
        value = dict(value)
        value["artifacts"] = tuple(value["artifacts"])
        value["domains"] = dict(value["domains"])

        def _default(f: Any) -> Any:
            if f.default is not MISSING:
                return f.default
            if f.default_factory is not MISSING:
                return f.default_factory()
            return None

        return cls(**{key: value[key] if key in value else _default(cls.__dataclass_fields__[key])
                      for key in cls.__dataclass_fields__})


class CoverageReducer:
    """Coverage-complete deterministic final gate (reducer v2, 指令-4 §13/§17).

    Any domain with UNKNOWN / MISSING / DESIGN_ONLY_WHEN_RUNTIME_REQUIRED /
    STATIC_ONLY_WHEN_RUNTIME_REQUIRED / OPEN_BLOCKING_TT status, or any
    required runtime flag false, forces exit 1 (FAIL_CLOSED).
    """

    VERSION = "2"

    def __init__(self, spine: SharedSpine) -> None:
        self.spine = spine

    def reduce(self, envelope: CoverageEnvelope) -> dict[str, Any]:
        reasons: list[str] = []

        # authority / denominator
        if envelope.coverage_domains_total < 1 or envelope.coverage_domains_terminal != envelope.coverage_domains_total:
            reasons.append("DOMAIN_COVERAGE_INCOMPLETE")
        if envelope.subcapabilities_total < 0 or envelope.subcapabilities_terminal != envelope.subcapabilities_total:
            reasons.append("SUBCAPABILITY_COVERAGE_INCOMPLETE")
        if not envelope.requirements_reconciled or envelope.orphan_requirements or envelope.unowned_mandatory_assets:
            reasons.append("REQUIREMENT_RECONCILIATION_INCOMPLETE")
        if envelope.canonical_requirements_total < 1:
            reasons.append("REQUIREMENT_DENOMINATOR_EMPTY")
        if envelope.requirements_domain_mapped != envelope.canonical_requirements_total:
            reasons.append("REQUIREMENT_DOMAIN_MAPPING_INCOMPLETE")
        if envelope.requirements_source_bound != envelope.canonical_requirements_total:
            reasons.append("REQUIREMENT_SOURCE_BINDING_INCOMPLETE")
        if envelope.requirement_owner_matches_domain_owner != envelope.canonical_requirements_total:
            reasons.append("REQUIREMENT_OWNER_MISMATCH")
        if envelope.requirement_owner_source_validated != envelope.canonical_requirements_total:
            reasons.append("REQUIREMENT_OWNER_NOT_SOURCE_VALIDATED")
        if envelope.unsupported_disposition_count:
            reasons.append("UNSUPPORTED_DISPOSITION_NONZERO")
        if envelope.runtime_pass_missing_evidence:
            reasons.append("RUNTIME_PASS_MISSING_EVIDENCE")
        if envelope.active_deferred_contradiction:
            reasons.append("ACTIVE_DEFERRED_CONTRADICTION")
        if envelope.missing_evidence_refs:
            reasons.append("MISSING_EVIDENCE_REFS")
        # acceptance depth
        if envelope.tst_total < 1 or envelope.tst_independent_pass != envelope.tst_total:
            reasons.append("ACCEPTANCE_NOT_INDEPENDENT_FULL")
        if not envelope.semantic_depth_calibrated or envelope.runtime_required_static_only_count:
            reasons.append("SEMANTIC_DEPTH_NOT_CALIBRATED")
        if envelope.current_executor_missing or envelope.raw_receipt_missing:
            reasons.append("ACCEPTANCE_TRACE_BINDING_INCOMPLETE")
        # domains: every status terminal source-backed
        for domain, status in envelope.domains.items():
            if status in FORBIDDEN_DOMAIN_STATUSES:
                reasons.append(f"DOMAIN_STATUS_FORBIDDEN:{domain}:{status}")
            elif status not in TERMINAL_STATUSES:
                reasons.append(f"DOMAIN_STATUS_NONTERMINAL:{domain}:{status}")
        if envelope.domain_blocking_gaps:
            reasons.append("DOMAIN_BLOCKING_GAPS_NONZERO")
        # runtime/provider routing (fail closed: no OpenAI fallback)
        if envelope.hermes_provider != "opencode-go" or envelope.hermes_model != "deepseek-v4-flash":
            reasons.append("HERMES_ROUTE_MISMATCH")
        if not envelope.codex_cli_primary_executor or not envelope.opencodex_transport:
            reasons.append("CODEX_ROUTE_INCOMPLETE")
        if envelope.openai_model_fallback:
            reasons.append("OPENAI_MODEL_FALLBACK_ENABLED")
        if not envelope.protected_identities_78_disposition_complete:
            reasons.append("PROTECTED_IDENTITIES_INCOMPLETE")
        if not envelope.mandatory_default_active_providers_certified:
            reasons.append("PROVIDER_CERTIFICATION_INCOMPLETE")
        # tests / security / tt
        if not envelope.product_tests_all_pass or not envelope.hlpe_tests_all_pass:
            reasons.append("TEST_SUITE_NOT_ALL_PASS")
        if envelope.security_blockers:
            reasons.append("SECURITY_BLOCKERS_NONZERO")
        if envelope.blocking_tt:
            reasons.append("BLOCKING_TT_OPEN")
        if envelope.knowledge_security_negative != "PASS":
            reasons.append("KNOWLEDGE_SECURITY_NEGATIVE_NOT_PASS")
        # recovery / package / evidence
        if not envelope.backup_restore_pass or not envelope.rollback_pass:
            reasons.append("RECOVERY_NOT_PROVEN")
        if not envelope.sbom_current:
            reasons.append("SBOM_NOT_CURRENT")
        if not envelope.user_guide_exists or not envelope.user_guide_runtime_consistent or not envelope.user_guide_sha256_verified:
            reasons.append("USER_GUIDE_NOT_VERIFIED")
        if not envelope.package_exact_readback or not envelope.final_head_independently_checked:
            reasons.append("PACKAGE_OR_HEAD_NOT_CHECKED")
        if not envelope.final_evidence_md_exists or not envelope.final_evidence_md_readback_verified:
            reasons.append("FINAL_EVIDENCE_MD_NOT_VERIFIED")
        if envelope.tst_054 != "INDEPENDENT_CASE_PASS" or envelope.tst_092 != "INDEPENDENT_CASE_PASS":
            reasons.append("TST_054_092_NOT_INDEPENDENT_PASS")
        # ── Task-014 named-method activation invariants (fail closed) ──
        for key in (
            "canonical_flow_named_method_without_runtime_or_certified_substitute",
            "active_named_method_missing_identity",
            "active_named_method_missing_pin",
            "active_named_method_missing_install",
            "active_named_method_missing_binding",
            "active_named_method_missing_doctor",
            "active_named_method_missing_pilot",
            "active_named_method_missing_independent_cert",
            "active_named_method_silent_fallback",
            "named_method_fake_invocation",
            "named_method_silent_fallback",
            "dual_spec_owner",
            "second_orchestrator",
            "release_authority_escape",
        ):
            if getattr(envelope, key) != 0:
                reasons.append(f"{key.upper()}_NONZERO")

        verdict = "HG-KSEOS_LOCAL_DELIVERY_PASS" if not reasons else "FAIL_CLOSED"
        envelope_json = canonical_json(envelope.__dict__)
        decision = {
            "decision_id": new_id("REL"),
            "candidate_digest": sha256_text(envelope_json),
            "reducer_version": self.VERSION,
            "verdict": verdict,
            "reasons": reasons,
            "checker": envelope.checker,
            "created_at": utc_now(),
        }
        with self.spine.transaction() as connection:
            connection.execute(
                """INSERT INTO release_decisions
                   (decision_id,candidate_digest,reducer_version,verdict,reasons_json,
                    independent_checker,evidence_envelope,created_at)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (
                    decision["decision_id"],
                    decision["candidate_digest"],
                    self.VERSION,
                    verdict,
                    json.dumps(reasons),
                    envelope.checker,
                    envelope_json,
                    decision["created_at"],
                ),
            )
        return decision




@dataclass
class UserExperienceEnvelope:
    """User Expected Capability & Experience (UECX) final gate input (task-006 §16)."""

    uecx_source_expectations: int
    uecx_rows: int
    uecx_orphans: int
    uecx_unknown: int
    p0_required_user_journeys_open: int
    p0_required_user_journeys_static_only: int
    p0_required_user_journeys_maker_only: int
    required_vertical_slices_total: int
    required_vertical_slices_applicable: int
    required_vertical_slices_pass: int
    required_vertical_slices_deferred_source_backed: int
    required_negative_tests_total: int
    required_negative_tests_pass: int
    natural_task_auto_route: str
    skill_auto_select: str
    memory_route_positive: str
    memory_route_negative: str
    rag_auto_route: str
    kg_route_positive: str
    kg_route_negative: str
    unnecessary_hitl: int
    unnecessary_multi_agent: int
    unnecessary_tool_activation: int
    self_promotion: int
    authority_mutation: int
    controlled_learning_scope_resolved: bool
    obsidian_scope_resolved: bool
    all_deferred_items_source_backed: bool
    blocking_user_experience_tt: int
    coverage_reducer_v2_exit: int
    # --- task-007 F5 fail-closed invariants ---
    source_families_required: int
    source_families_reviewed: int
    source_expectations_unmapped: int
    requirement_id_not_in_canonical_ledger: int
    requirement_domain_mismatch: int
    requirement_disposition_mismatch: int
    u0_u1_disposition_conflict: int
    p0_runtime_pass_raw_evidence_missing: int
    p0_runtime_pass_independent_evidence_missing: int
    p0_runtime_pass_fixture_missing: int
    p0_runtime_pass_command_missing: int
    p0_runtime_pass_trace_missing: int
    p0_runtime_pass_hash_missing: int
    classification_terminal_contradiction: int
    named_tool_claim_without_lifecycle_evidence: int
    knowledge_workbench_scope_resolved: bool
    # --- task-007 §26 workbench extension invariants ---
    obsidian_identity_resolved: bool
    obsidian_installed: bool
    obsidian_runtime_qualified: bool
    obsidian_feature_inventory_complete: bool
    obsidian_unknown_features: int
    llm_wiki_identity_resolved: bool
    llm_wiki_single_selected_identity: bool
    llm_wiki_installed: bool
    llm_wiki_runtime_qualified: bool
    llm_wiki_feature_inventory_complete: bool
    llm_wiki_unknown_features: int
    workbench_canonical_authority_violation: int
    tool_claim_without_identity: int
    tool_claim_without_version: int
    tool_claim_without_raw_evidence: int
    tool_claim_without_independent_evidence: int
    obsidian_llmwiki_integration_pass: bool
    withdrawal_consistency_pass: bool
    conflict_fail_closed_pass: bool
    fallback_to_git_markdown_pass: bool
    external_gated_features_all_accounted_for: bool
    blocking_workbench_tt: int
    # task-011 autonomy/evolution hard invariants
    autonomous_project_entrypoint: bool
    external_gpt_not_required: bool
    project_source_auto_admission: bool
    intent_roundtrip: bool
    workorder_auto_admission: bool
    real_hermes_codex_execution: bool
    automatic_repair: bool
    checkpoint_resume: bool
    independent_project_acceptance: bool
    minimal_hitl: bool
    evolution_signal_capture: bool
    gap_classification: bool
    fit_gap_reuse_first: bool
    candidate_sandbox: bool
    holdout_nrtv: bool
    independent_candidate_check: bool
    failed_candidate_rollback: bool
    promotion_policy_enforced: bool
    authority_mutation: int
    evaluator_self_mutation: int
    infinite_evolution_loop: int
    user_guide_current_runtime: bool
    user_guide_no_stale_companion_claim: bool
    user_guide_no_task007_current_wording: bool
    checker: str
    artifacts: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "UserExperienceEnvelope":
        required = {field.name for field in cls.__dataclass_fields__.values()}
        missing = required - value.keys()
        if missing:
            raise ValueError(f"ERR_USER_EXPERIENCE_ENVELOPE_MISSING:{sorted(missing)}")
        value = dict(value)
        value["artifacts"] = tuple(value["artifacts"])
        return cls(**{key: value[key] for key in required})


class UserExperienceReducer:
    """Cross-domain user-journey deterministic gate (UX reducer v1, task-006 §16/§17).

    Guards: source-bound expectation inventory, P0-required journey closure,
    vertical slices, negative operational tests, automatic routing,
    memory/RAG/KG routing, minimal manual intervention, learning/workbench scope.
    """

    VERSION = "1"

    def __init__(self, spine: SharedSpine) -> None:
        self.spine = spine

    def reduce(self, envelope: UserExperienceEnvelope) -> dict[str, Any]:
        reasons: list[str] = []

        if envelope.uecx_source_expectations <= 0:
            reasons.append("UECX_SOURCE_EXPECTATIONS_EMPTY")
        if envelope.uecx_rows <= 0:
            reasons.append("UECX_ROWS_EMPTY")
        if envelope.uecx_orphans:
            reasons.append("UECX_ORPHAN_NONZERO")
        if envelope.uecx_unknown:
            reasons.append("UECX_UNKNOWN_NONZERO")
        if envelope.p0_required_user_journeys_open:
            reasons.append("P0_USER_JOURNEYS_OPEN")
        if envelope.p0_required_user_journeys_static_only:
            reasons.append("P0_USER_JOURNEYS_STATIC_ONLY")
        if envelope.p0_required_user_journeys_maker_only:
            reasons.append("P0_USER_JOURNEYS_MAKER_ONLY")
        if envelope.required_vertical_slices_applicable <= 0:
            reasons.append("VERTICAL_SLICES_NONE_APPLICABLE")
        if envelope.required_vertical_slices_pass < envelope.required_vertical_slices_applicable:
            reasons.append("VERTICAL_SLICES_INCOMPLETE")
        if envelope.required_negative_tests_total <= 0 or envelope.required_negative_tests_pass != envelope.required_negative_tests_total:
            reasons.append("NEGATIVE_OPERATIONAL_TESTS_INCOMPLETE")
        if envelope.natural_task_auto_route != "PASS":
            reasons.append("NATURAL_TASK_AUTO_ROUTE_FAIL")
        if envelope.skill_auto_select != "PASS":
            reasons.append("SKILL_AUTO_SELECT_FAIL")
        if envelope.memory_route_positive != "PASS":
            reasons.append("MEMORY_ROUTE_POSITIVE_FAIL")
        if envelope.memory_route_negative != "PASS":
            reasons.append("MEMORY_ROUTE_NEGATIVE_FAIL")
        if envelope.rag_auto_route != "PASS":
            reasons.append("RAG_AUTO_ROUTE_FAIL")
        if envelope.kg_route_positive != "PASS":
            reasons.append("KG_ROUTE_POSITIVE_FAIL")
        if envelope.kg_route_negative != "PASS":
            reasons.append("KG_ROUTE_NEGATIVE_FAIL")
        if envelope.unnecessary_hitl:
            reasons.append("UNNECESSARY_HITL_NONZERO")
        if envelope.unnecessary_multi_agent:
            reasons.append("UNNECESSARY_MULTI_AGENT_NONZERO")
        if envelope.unnecessary_tool_activation:
            reasons.append("UNNECESSARY_TOOL_ACTIVATION_NONZERO")
        if envelope.self_promotion:
            reasons.append("SELF_PROMOTION_NONZERO")
        if envelope.authority_mutation:
            reasons.append("AUTHORITY_MUTATION_NONZERO")
        if not envelope.controlled_learning_scope_resolved:
            reasons.append("CONTROLLED_LEARNING_SCOPE_UNRESOLVED")
        if not envelope.obsidian_scope_resolved:
            reasons.append("OBSIDIAN_SCOPE_UNRESOLVED")
        if not envelope.all_deferred_items_source_backed:
            reasons.append("DEFERRED_ITEM_NOT_SOURCE_BACKED")
        if envelope.blocking_user_experience_tt:
            reasons.append("BLOCKING_USER_EXPERIENCE_TT_NONZERO")
        if envelope.coverage_reducer_v2_exit != 0:
            reasons.append("COVERAGE_REDUCER_V2_NOT_PASS")

        # ---- task-007 F5 fail-closed invariants ----
        if envelope.source_families_required <= 0 or envelope.source_families_reviewed != envelope.source_families_required:
            reasons.append("SOURCE_FAMILY_SCAN_INCOMPLETE")
        if envelope.source_expectations_unmapped:
            reasons.append("SOURCE_EXPECTATIONS_UNMAPPED")
        if envelope.requirement_id_not_in_canonical_ledger:
            reasons.append("REQUIREMENT_ID_NOT_IN_CANONICAL_LEDGER")
        if envelope.requirement_domain_mismatch:
            reasons.append("REQUIREMENT_DOMAIN_MISMATCH")
        if envelope.requirement_disposition_mismatch:
            reasons.append("REQUIREMENT_DISPOSITION_MISMATCH")
        if envelope.u0_u1_disposition_conflict:
            reasons.append("U0_U1_DISPOSITION_CONFLICT")
        if envelope.p0_runtime_pass_raw_evidence_missing:
            reasons.append("P0_RUNTIME_PASS_RAW_EVIDENCE_MISSING")
        if envelope.p0_runtime_pass_independent_evidence_missing:
            reasons.append("P0_RUNTIME_PASS_INDEPENDENT_EVIDENCE_MISSING")
        if envelope.p0_runtime_pass_fixture_missing:
            reasons.append("P0_RUNTIME_PASS_FIXTURE_MISSING")
        if envelope.p0_runtime_pass_command_missing:
            reasons.append("P0_RUNTIME_PASS_COMMAND_MISSING")
        if envelope.p0_runtime_pass_trace_missing:
            reasons.append("P0_RUNTIME_PASS_TRACE_MISSING")
        if envelope.p0_runtime_pass_hash_missing:
            reasons.append("P0_RUNTIME_PASS_HASH_MISSING")
        if envelope.classification_terminal_contradiction:
            reasons.append("CLASSIFICATION_TERMINAL_CONTRADICTION")
        if envelope.named_tool_claim_without_lifecycle_evidence:
            reasons.append("NAMED_TOOL_CLAIM_WITHOUT_LIFECYCLE_EVIDENCE")
        if not envelope.knowledge_workbench_scope_resolved:
            reasons.append("KNOWLEDGE_WORKBENCH_SCOPE_UNRESOLVED")

        # ---- task-007 §26 workbench extension invariants ----
        if not envelope.obsidian_identity_resolved:
            reasons.append("OBSIDIAN_IDENTITY_UNRESOLVED")
        if not envelope.obsidian_installed:
            reasons.append("OBSIDIAN_NOT_INSTALLED")
        if not envelope.obsidian_runtime_qualified:
            reasons.append("OBSIDIAN_NOT_RUNTIME_QUALIFIED")
        if not envelope.obsidian_feature_inventory_complete:
            reasons.append("OBSIDIAN_FEATURE_INVENTORY_INCOMPLETE")
        if envelope.obsidian_unknown_features:
            reasons.append("OBSIDIAN_UNKNOWN_FEATURES_NONZERO")
        if not envelope.llm_wiki_identity_resolved:
            reasons.append("LLM_WIKI_IDENTITY_UNRESOLVED")
        if not envelope.llm_wiki_single_selected_identity:
            reasons.append("LLM_WIKI_SINGLE_IDENTITY_VIOLATION")
        if not envelope.llm_wiki_installed:
            reasons.append("LLM_WIKI_NOT_INSTALLED")
        if not envelope.llm_wiki_runtime_qualified:
            reasons.append("LLM_WIKI_NOT_RUNTIME_QUALIFIED")
        if not envelope.llm_wiki_feature_inventory_complete:
            reasons.append("LLM_WIKI_FEATURE_INVENTORY_INCOMPLETE")
        if envelope.llm_wiki_unknown_features:
            reasons.append("LLM_WIKI_UNKNOWN_FEATURES_NONZERO")
        if envelope.workbench_canonical_authority_violation:
            reasons.append("WORKBENCH_CANONICAL_AUTHORITY_VIOLATION")
        if envelope.tool_claim_without_identity:
            reasons.append("TOOL_CLAIM_WITHOUT_IDENTITY")
        if envelope.tool_claim_without_version:
            reasons.append("TOOL_CLAIM_WITHOUT_VERSION")
        if envelope.tool_claim_without_raw_evidence:
            reasons.append("TOOL_CLAIM_WITHOUT_RAW_EVIDENCE")
        if envelope.tool_claim_without_independent_evidence:
            reasons.append("TOOL_CLAIM_WITHOUT_INDEPENDENT_EVIDENCE")
        if not envelope.obsidian_llmwiki_integration_pass:
            reasons.append("OBSIDIAN_LLMWIKI_INTEGRATION_FAIL")
        if not envelope.withdrawal_consistency_pass:
            reasons.append("WITHDRAWAL_CONSISTENCY_FAIL")
        if not envelope.conflict_fail_closed_pass:
            reasons.append("CONFLICT_FAIL_CLOSED_FAIL")
        if not envelope.fallback_to_git_markdown_pass:
            reasons.append("FALLBACK_TO_GIT_MARKDOWN_FAIL")
        if not envelope.external_gated_features_all_accounted_for:
            reasons.append("EXTERNAL_GATED_FEATURES_NOT_ACCOUNTED")
        if envelope.blocking_workbench_tt:
            reasons.append("BLOCKING_WORKBENCH_TT_NONZERO")

        # ---- task-011 autonomy/evolution invariants ----
        if not envelope.autonomous_project_entrypoint:
            reasons.append("AUTONOMOUS_PROJECT_ENTRYPOINT_MISSING")
        if not envelope.external_gpt_not_required:
            reasons.append("EXTERNAL_GPT_REQUIRED_FOR_NORMAL_LIFECYCLE")
        if not envelope.project_source_auto_admission:
            reasons.append("SOURCE_AUTO_ADMISSION_FAIL")
        if not envelope.intent_roundtrip:
            reasons.append("INTENT_ROUNDTRIP_FAIL")
        if not envelope.workorder_auto_admission:
            reasons.append("WORKORDER_AUTO_ADMISSION_FAIL")
        if not envelope.real_hermes_codex_execution:
            reasons.append("REAL_HERMES_CODEX_EXECUTION_FAIL")
        if not envelope.automatic_repair:
            reasons.append("AUTOMATIC_REPAIR_FAIL")
        if not envelope.checkpoint_resume:
            reasons.append("CHECKPOINT_RESUME_FAIL")
        if not envelope.independent_project_acceptance:
            reasons.append("INDEPENDENT_PROJECT_ACCEPTANCE_FAIL")
        if not envelope.minimal_hitl:
            reasons.append("MINIMAL_HITL_FAIL")
        if not envelope.evolution_signal_capture:
            reasons.append("EVOLUTION_SIGNAL_CAPTURE_FAIL")
        if not envelope.gap_classification:
            reasons.append("GAP_CLASSIFICATION_FAIL")
        if not envelope.fit_gap_reuse_first:
            reasons.append("FIT_GAP_REUSE_FIRST_FAIL")
        if not envelope.candidate_sandbox:
            reasons.append("CANDIDATE_SANDBOX_FAIL")
        if not envelope.holdout_nrtv:
            reasons.append("HOLDOUT_NRTV_FAIL")
        if not envelope.independent_candidate_check:
            reasons.append("INDEPENDENT_CANDIDATE_CHECK_FAIL")
        if not envelope.failed_candidate_rollback:
            reasons.append("FAILED_CANDIDATE_ROLLBACK_FAIL")
        if not envelope.promotion_policy_enforced:
            reasons.append("PROMOTION_POLICY_NOT_ENFORCED")
        if envelope.authority_mutation:
            reasons.append("AUTHORITY_MUTATION_ATTEMPT_SUCCEEDED")
        if envelope.evaluator_self_mutation:
            reasons.append("EVALUATOR_SELF_MUTATION_SUCCEEDED")
        if envelope.infinite_evolution_loop:
            reasons.append("INFINITE_EVOLUTION_LOOP")
        if not envelope.user_guide_current_runtime:
            reasons.append("USER_GUIDE_STALE")
        if not envelope.user_guide_no_stale_companion_claim:
            reasons.append("USER_GUIDE_STALE_COMPANION_CLAIM")
        if not envelope.user_guide_no_task007_current_wording:
            reasons.append("USER_GUIDE_TASK007_CURRENT_WORDING")

        verdict = "HG-KSEOS_USER_EXPECTED_CAPABILITY_EXPERIENCE_PASS" if not reasons else "FAIL_CLOSED"
        envelope_json = canonical_json(envelope.__dict__)
        decision = {
            "schema": "HGK-USER-EXPERIENCE-REDUCER/1",
            "decision_id": new_id("REL"),
            "candidate_digest": sha256_text(envelope_json),
            "version": self.VERSION,
            "verdict": verdict,
            "reasons": reasons,
            "checker": envelope.checker,
            "created_at": utc_now(),
            "exit_code": 0 if not reasons else 1,
        }
        with self.spine.transaction() as connection:
            connection.execute(
                """INSERT INTO release_decisions
                   (decision_id,candidate_digest,reducer_version,verdict,reasons_json,
                    independent_checker,evidence_envelope,created_at)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (
                    decision["decision_id"],
                    decision["candidate_digest"],
                    f"UX-{self.VERSION}",
                    verdict,
                    json.dumps(reasons),
                    envelope.checker,
                    envelope_json,
                    decision["created_at"],
                ),
            )
        return decision
