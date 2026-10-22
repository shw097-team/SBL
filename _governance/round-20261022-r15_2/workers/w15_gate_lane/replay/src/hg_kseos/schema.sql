PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT OR REPLACE INTO schema_meta(key, value) VALUES ('schema_version', '3');

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    product_root TEXT NOT NULL CHECK(product_root = 'HG-KSEOS'),
    state TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    path TEXT NOT NULL UNIQUE,
    mode TEXT NOT NULL CHECK(mode IN (
        'READ_ONLY_SOURCE',
        'WRITABLE_MAKER',
        'ISOLATED_WORKTREE',
        'WRITABLE_CANONICAL_WITH_FROZEN_INPUT_SUBTREES'
    )),
    identity_digest TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS requirements (
    requirement_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    source_locator TEXT NOT NULL,
    wording TEXT NOT NULL,
    priority TEXT NOT NULL,
    state TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 0,
    acceptance_id TEXT NOT NULL,
    rollback_pointer TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS acceptances (
    acceptance_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL REFERENCES requirements(requirement_id),
    oracle TEXT NOT NULL,
    threshold TEXT NOT NULL,
    negative_fixture TEXT NOT NULL,
    verdict TEXT NOT NULL DEFAULT 'NOT_RUN',
    evidence_ref TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY(requirement_id, acceptance_id)
);

CREATE TABLE IF NOT EXISTS artifact_contracts (
    artifact_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    owner TEXT NOT NULL,
    producer TEXT NOT NULL,
    consumer TEXT NOT NULL,
    schema_ref TEXT NOT NULL,
    state TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 0,
    rollback_pointer TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS taskspecs (
    taskspec_id TEXT PRIMARY KEY,
    requirement_id TEXT NOT NULL REFERENCES requirements(requirement_id),
    objective TEXT NOT NULL,
    owner TEXT NOT NULL,
    writable_root TEXT NOT NULL,
    permissions_json TEXT NOT NULL,
    tests_json TEXT NOT NULL,
    rollback_pointer TEXT NOT NULL,
    evidence_plan TEXT NOT NULL,
    state TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workorders (
    workorder_id TEXT PRIMARY KEY,
    taskspec_id TEXT NOT NULL REFERENCES taskspecs(taskspec_id),
    writer TEXT NOT NULL,
    worktree TEXT NOT NULL,
    base_head TEXT NOT NULL,
    state TEXT NOT NULL,
    result_json TEXT,
    rollback_pointer TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS leases (
    resource_id TEXT PRIMARY KEY,
    holder TEXT NOT NULL,
    token_hash TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical_events (
    event_id TEXT PRIMARY KEY,
    idempotency_key TEXT NOT NULL UNIQUE,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    from_state TEXT,
    to_state TEXT NOT NULL,
    actor TEXT NOT NULL,
    expected_version INTEGER NOT NULL,
    resulting_version INTEGER NOT NULL,
    payload_json TEXT NOT NULL,
    evidence_ref TEXT NOT NULL,
    rollback_pointer TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_refs (
    evidence_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    locator TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    producer TEXT NOT NULL,
    checker TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    wave TEXT NOT NULL,
    state_digest TEXT NOT NULL,
    source_digest TEXT NOT NULL,
    repo_head TEXT NOT NULL,
    rollback_pointer TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rollback_records (
    rollback_id TEXT PRIMARY KEY,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    pre_state_digest TEXT NOT NULL,
    post_state_digest TEXT,
    status TEXT NOT NULL,
    evidence_ref TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tt_records (
    tt_id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    owner TEXT NOT NULL,
    blocking INTEGER NOT NULL CHECK(blocking IN (0,1)),
    close_criteria TEXT NOT NULL,
    status TEXT NOT NULL,
    evidence_ref TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    canonical_path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    authority_rank TEXT NOT NULL,
    status TEXT NOT NULL,
    withdrawn_at TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(canonical_path, sha256)
);

CREATE TABLE IF NOT EXISTS source_units (
    unit_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    anchor TEXT NOT NULL,
    content TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    sanitation_status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(source_id, anchor)
);

CREATE TABLE IF NOT EXISTS candidates (
    candidate_id TEXT PRIMARY KEY,
    source_unit_id TEXT NOT NULL REFERENCES source_units(unit_id),
    kind TEXT NOT NULL,
    body TEXT NOT NULL,
    state TEXT NOT NULL,
    verifier TEXT,
    promotion_evidence TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledge_docs (
    doc_id TEXT PRIMARY KEY,
    source_unit_id TEXT NOT NULL REFERENCES source_units(unit_id),
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    citation TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
    doc_id UNINDEXED,
    title,
    body,
    citation UNINDEXED,
    tokenize = 'unicode61'
);

CREATE TABLE IF NOT EXISTS kg_edges (
    edge_id TEXT PRIMARY KEY,
    source_doc_id TEXT NOT NULL REFERENCES knowledge_docs(doc_id),
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kg_assertions (
    edge_id TEXT PRIMARY KEY,
    source_doc_id TEXT NOT NULL REFERENCES knowledge_docs(doc_id),
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_records (
    memory_id TEXT PRIMARY KEY,
    scope TEXT NOT NULL,
    body TEXT NOT NULL,
    provenance TEXT NOT NULL,
    expires_at TEXT,
    revoked_at TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS provider_bindings (
    provider_id TEXT PRIMARY KEY,
    slot TEXT NOT NULL,
    xor_group TEXT,
    disposition TEXT NOT NULL,
    pin TEXT,
    state TEXT NOT NULL,
    doctor_evidence TEXT,
    rollback_pointer TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS one_active_provider_per_xor
ON provider_bindings(xor_group)
WHERE state = 'ENABLED' AND xor_group IS NOT NULL;

CREATE TABLE IF NOT EXISTS release_decisions (
    decision_id TEXT PRIMARY KEY,
    candidate_digest TEXT NOT NULL,
    reducer_version TEXT NOT NULL,
    verdict TEXT NOT NULL,
    reasons_json TEXT NOT NULL,
    independent_checker TEXT,
    evidence_envelope TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- task-011: Autonomous Project Lifecycle (v3 forward-only)
CREATE TABLE IF NOT EXISTS project_lifecycles (
    project_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    state TEXT NOT NULL,
    goal_hash TEXT NOT NULL,
    source_count INTEGER NOT NULL DEFAULT 0,
    authority_order_json TEXT NOT NULL DEFAULT '[]',
    conflicts_json TEXT NOT NULL DEFAULT '[]',
    blocking_missing_json TEXT NOT NULL DEFAULT '[]',
    non_blocking_missing_json TEXT NOT NULL DEFAULT '[]',
    intent_json TEXT NOT NULL DEFAULT '{}',
    non_goals_json TEXT NOT NULL DEFAULT '[]',
    current_workorder TEXT,
    last_checkpoint_id TEXT,
    attempt_budget INTEGER NOT NULL DEFAULT 3,
    attempts_used INTEGER NOT NULL DEFAULT 0,
    repair_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS project_transitions (
    transition_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES project_lifecycles(project_id),
    run_id TEXT NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    trigger TEXT NOT NULL,
    authority_refs_json TEXT NOT NULL DEFAULT '[]',
    workorder_refs_json TEXT NOT NULL DEFAULT '[]',
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    checkpoint_id TEXT,
    rollback_pointer TEXT NOT NULL,
    attempt INTEGER NOT NULL DEFAULT 0,
    budget_remaining INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evolution_signals (
    signal_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    source_evidence_json TEXT NOT NULL DEFAULT '[]',
    recurrence_key TEXT NOT NULL,
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    candidate_worthy INTEGER NOT NULL DEFAULT 0,
    authority_impact TEXT NOT NULL DEFAULT 'NONE',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS improvement_candidates (
    candidate_id TEXT PRIMARY KEY,
    gap_id TEXT NOT NULL,
    candidate_type TEXT NOT NULL,
    source_signals_json TEXT NOT NULL DEFAULT '[]',
    problem_statement TEXT NOT NULL,
    proposed_change TEXT NOT NULL,
    expected_gain TEXT NOT NULL,
    risk_class TEXT NOT NULL,
    allowed_write_set_json TEXT NOT NULL DEFAULT '[]',
    forbidden_write_set_json TEXT NOT NULL DEFAULT '[]',
    state TEXT NOT NULL DEFAULT 'CANDIDATE',
    sandbox_path TEXT,
    baseline_metrics_json TEXT NOT NULL DEFAULT '{}',
    evaluation_plan_json TEXT NOT NULL DEFAULT '{}',
    rollback TEXT NOT NULL,
    authority_gate TEXT NOT NULL,
    independent_verdict TEXT,
    promotion_state TEXT NOT NULL DEFAULT 'NOT_PROMOTED',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
