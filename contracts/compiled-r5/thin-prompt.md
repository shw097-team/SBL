# EXECUTABLE THIN CONSTRUCTION & ACCEPTANCE PROMPT

## 0. Machine Header
task_id: SBL-FULL-DOC00-13-R5-20261021
contract_schema: CAPC-PROMPT-CONTRACT/1
compiler_state: PROMPT_COMPILE_PASS

## 1. Mission / ChangeSet
Mission: Continue SBL / SpecBuild Loop v0.1 from the frozen candidate fb7af87 without reopening product code: close the last defect the independent checker raised (a gate-tooling defect in the secret scanner), obtain a fresh independent receipt for the frozen SHA, and publish a scrubbed, reproducible candidate plus evidence commit with both exact SHAs re-read from the remote, so an external assessor can re-run the gates unaided.
Expected outcome: A working product tree with reproducible raw evidence and a public candidate an external checker can re-verify from bytes.
ChangeSet: CONTINUATION
Affected domains: sbl_harness, tests, governance_evidence, contracts

## 2. Authority / Files-first order
Read and hash the exact sources below in order. Use their owned controls directly; do not restate or replace them.
- R1 C:/Projects/Agent_Workspace/_sbl_src_mirror/SBL_PIPD-LS-PKG SBL_PIPD-LS-PKG_DOC-00.md .. SBL_PIPD-LS-PKG_DOC-13.md role=NORMATIVE
- R1 C:/Projects/Agent_Workspace/HG-KSEOS/AGENTS.md AGENTS.md control-plane rules role=NORMATIVE
- R2 C:/Projects/Agent_Workspace/HG-KSEOS/config/lane-routing-registry.yaml config/lane-routing-registry.yaml role=STATE_EVIDENCE
- R1 attachments/SBL／HERMES／HG-KSEOS／Fabric 完整指揮薄 PROMPT v2-3.md commander prompt v2-3 machine header + TS00..TS19 role=NORMATIVE
- R3 C:/Projects/Agent_Workspace/Fabric/FABRIC/AGENTS.md Fabric governance and assurance contract surface role=SUPPORT
- R1 C:/Projects/Agent_Workspace/知識庫/實作相關DOC/HG-KSEOS/construction-acceptance-prompt-compiler/construction-acceptance-prompt-compiler/scripts/prompt_contract_compiler.py scripts/prompt_contract_compiler.py + references/prompt-contract.schema.json role=NORMATIVE
Equal-rank conflict => quarantine, TT, and stop the affected work.

## 3. Intent / Non-goals / Claim ceiling
Expected experience: Run each golden journey end to end from the CLI without reading internal design documents; every failure is typed and recoverable.
Constraints:
- HG-KSEOS remains the only control plane; no second orchestrator, task DB or evidence authority
- maker != checker and the checker lane is read-only
- PLAN/VERIFY = openai-codex/gpt-6.1-sol medium; EXECUTE = opencode-go/deepseek-v4.1-flash through the Codex CLI lane
- candidate-only; no self-acceptance, no RELEASED, no PRODUCTION claim
- PREW3_SHADOW must produce NoEffect; SWOF_CONNECTED stays blocked without a native ACK/Permit
- no private corpus text and no credential value may enter the public repository
- SBL_MASTER_v2.0r1 and the PIPD native P4 package are absent from the mounted corpus; the absence is carried as TT and is not substituted by same-named material from another subject
- claim ceiling is LOCAL: only raw receipts from this host lift it, and only an external checker can grant acceptance
Non-goals:
- install all 386 donor technologies
- modify sealed HG-KSEOS or Fabric policy
- claim a SWOF world connection
- claim independent acceptance from the maker side
- publish private corpus content or credential material
Authorized mutations:
- C:/Projects/Agent_Workspace/SBL (full tree)
- github.com/shw097-team/SBL candidate branches and scrubbed evidence
- HG-KSEOS Shared Spine records scoped to this project
Forbidden mutations:
- HG-KSEOS and Fabric sealed policy
- the read-only source corpus root
- other repositories
- credential stores
- Oracles, RBWI and reducers
Claim ceiling: LOCAL

## 4. Active / Deferred / Forbidden scope
Active:
- SBL_SHARED_CORE: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- SBLM01_GOAL_INTAKE: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- SBLM02_GUIDED_SPECIFICATION: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- SBLM03_GOVERNED_ROUTING: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- SBLM04_GOVERNED_BUILD_BRIDGE: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- SBLM05_EVIDENCE_VERIFICATION: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- SBLM06_BOUNDED_REPAIR: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- TPM_SP: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- COMMANDER_SP: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- EXTERNAL_CHALLENGE_SP: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- MODE_STANDALONE: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- MODE_PREW3_SHADOW: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- GJ01_CLI_TOOL: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- GJ02_BROWNFIELD_PATCH: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- GJ03_SKILL_AGENT_BRIDGE: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- GKNOW_RETRIEVAL: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- PUBLIC_CANDIDATE_PUBLICATION: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- SP_PLUGIN_PACKAGE_TPM: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- SP_PLUGIN_PACKAGE_COMMANDER: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- SP_PLUGIN_PACKAGE_CHALLENGE: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
- SP_HOST_INSTALL_REQUEST: ACTIVE_REQUIRED; action=INSTALL; runtime_required=true
Non-active:
- MODE_SWOFCON: DEFERRED_SOURCE_BACKED; action=DEFER
Do not install, enable, or qualify a non-active capability.

## 5. Baseline / Reuse / Do-not-redo
Baseline: required=true; verified=true; reuse_prior_pass=true
Do not reopen:
- foundation main merge
- foundation prerelease v0.1.0-foundation-preview
- M4-LITE owner procedural receipt
- 441/149/38 frozen ledgers
- c3-v2 plugin schema / package-data / stack / wheel work
- sbl_core m01..m06 module logic
Verify source and candidate bindings before reuse. A tracked mutation invalidates the affected seal.

## 6. Implementation and qualification gates
Use Manifest → owner WP/RBWI → TaskSpec/WorkOrder → active AGENTS/SKILLS → Harness/Loop.
Runtime closure:
- SBL_SHARED_CORE: verdict=NOT_READY; work=materialize SBL_SHARED_CORE runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- SBLM01_GOAL_INTAKE: verdict=NOT_READY; work=materialize SBLM01_GOAL_INTAKE runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- SBLM02_GUIDED_SPECIFICATION: verdict=NOT_READY; work=materialize SBLM02_GUIDED_SPECIFICATION runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- SBLM03_GOVERNED_ROUTING: verdict=NOT_READY; work=materialize SBLM03_GOVERNED_ROUTING runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- SBLM04_GOVERNED_BUILD_BRIDGE: verdict=NOT_READY; work=materialize SBLM04_GOVERNED_BUILD_BRIDGE runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- SBLM05_EVIDENCE_VERIFICATION: verdict=NOT_READY; work=materialize SBLM05_EVIDENCE_VERIFICATION runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- SBLM06_BOUNDED_REPAIR: verdict=NOT_READY; work=materialize SBLM06_BOUNDED_REPAIR runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- TPM_SP: verdict=NOT_READY; work=materialize TPM_SP runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- COMMANDER_SP: verdict=NOT_READY; work=materialize COMMANDER_SP runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- EXTERNAL_CHALLENGE_SP: verdict=NOT_READY; work=materialize EXTERNAL_CHALLENGE_SP runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- MODE_STANDALONE: verdict=NOT_READY; work=materialize MODE_STANDALONE runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- MODE_PREW3_SHADOW: verdict=NOT_READY; work=materialize MODE_PREW3_SHADOW runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- GJ01_CLI_TOOL: verdict=NOT_READY; work=materialize GJ01_CLI_TOOL runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- GJ02_BROWNFIELD_PATCH: verdict=NOT_READY; work=materialize GJ02_BROWNFIELD_PATCH runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- GJ03_SKILL_AGENT_BRIDGE: verdict=NOT_READY; work=materialize GJ03_SKILL_AGENT_BRIDGE runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- GKNOW_RETRIEVAL: verdict=NOT_READY; work=materialize GKNOW_RETRIEVAL runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- PUBLIC_CANDIDATE_PUBLICATION: verdict=NOT_READY; work=materialize PUBLIC_CANDIDATE_PUBLICATION runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- SP_PLUGIN_PACKAGE_TPM: verdict=NOT_READY; work=materialize SBL_SHARED_CORE runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- SP_PLUGIN_PACKAGE_COMMANDER: verdict=NOT_READY; work=materialize SBL_SHARED_CORE runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- SP_PLUGIN_PACKAGE_CHALLENGE: verdict=NOT_READY; work=materialize SBL_SHARED_CORE runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
- SP_HOST_INSTALL_REQUEST: verdict=NOT_READY; work=materialize SBL_SHARED_CORE runtime closure with typed errors; positive + negative + security fixtures executed for real; raw receipt plus a distinct-model independent checker verdict
Required user journeys:
- GJ01_CLI_TOOL: Install a small CLI tool, add one item, and read it back after restarting → add prints an id; list --json shows the same id/title/status after restart; uninstall leaves nothing behind
- GJ02_BROWNFIELD_PATCH: Have a scoped defect patched inside an existing repository without touching unrelated code → diff limited to the declared write-set; failing test turns green; affected regression clean; rollback restores the exact baseline
- GJ03_SKILL_AGENT_BRIDGE: Use an agent skill that is discoverable, effectively loaded and refuses out-of-scope effects → skill is discovered and triggers on its intent, does not trigger on unrelated intents, and refuses unauthorised effects
Acceptance predicates:
- ACC-SBL_SHARED_CORE subject=SBL_SHARED_CORE depth=L3_INTEGRATION_RUNTIME
- ACC-SBLM01_GOAL_INTAKE subject=SBLM01_GOAL_INTAKE depth=L3_INTEGRATION_RUNTIME
- ACC-SBLM02_GUIDED_SPECIFICATION subject=SBLM02_GUIDED_SPECIFICATION depth=L3_INTEGRATION_RUNTIME
- ACC-SBLM03_GOVERNED_ROUTING subject=SBLM03_GOVERNED_ROUTING depth=L3_INTEGRATION_RUNTIME
- ACC-SBLM04_GOVERNED_BUILD_BRIDGE subject=SBLM04_GOVERNED_BUILD_BRIDGE depth=L3_INTEGRATION_RUNTIME
- ACC-SBLM05_EVIDENCE_VERIFICATION subject=SBLM05_EVIDENCE_VERIFICATION depth=L3_INTEGRATION_RUNTIME
- ACC-SBLM06_BOUNDED_REPAIR subject=SBLM06_BOUNDED_REPAIR depth=L3_INTEGRATION_RUNTIME
- ACC-TPM_SP subject=TPM_SP depth=L3_INTEGRATION_RUNTIME
- ACC-COMMANDER_SP subject=COMMANDER_SP depth=L3_INTEGRATION_RUNTIME
- ACC-EXTERNAL_CHALLENGE_SP subject=EXTERNAL_CHALLENGE_SP depth=L3_INTEGRATION_RUNTIME
- ACC-MODE_STANDALONE subject=MODE_STANDALONE depth=L3_INTEGRATION_RUNTIME
- ACC-MODE_PREW3_SHADOW subject=MODE_PREW3_SHADOW depth=L3_INTEGRATION_RUNTIME
- ACC-GJ01_CLI_TOOL subject=GJ01_CLI_TOOL depth=L3_INTEGRATION_RUNTIME
- ACC-GJ02_BROWNFIELD_PATCH subject=GJ02_BROWNFIELD_PATCH depth=L3_INTEGRATION_RUNTIME
- ACC-GJ03_SKILL_AGENT_BRIDGE subject=GJ03_SKILL_AGENT_BRIDGE depth=L3_INTEGRATION_RUNTIME
- ACC-GKNOW_RETRIEVAL subject=GKNOW_RETRIEVAL depth=L3_INTEGRATION_RUNTIME
- ACC-PUBLIC_CANDIDATE_PUBLICATION subject=PUBLIC_CANDIDATE_PUBLICATION depth=L3_INTEGRATION_RUNTIME
- ACC-MODE_SWOFCON subject=MODE_SWOFCON depth=L1_SCHEMA_CONTRACT
- ACC-DELIV_PRODUCT_TREE subject=DELIV_PRODUCT_TREE depth=L3_INTEGRATION_RUNTIME
- ACC-DELIV_PUBLIC_CANDIDATE subject=DELIV_PUBLIC_CANDIDATE depth=L3_INTEGRATION_RUNTIME
- ACC-DELIV_HANDOVER_BUNDLE subject=DELIV_HANDOVER_BUNDLE depth=L3_INTEGRATION_RUNTIME
- ACC-SP_PLUGIN_PACKAGE_TPM subject=SP_PLUGIN_PACKAGE_TPM depth=L3_INTEGRATION_RUNTIME
- ACC-SP_PLUGIN_PACKAGE_COMMANDER subject=SP_PLUGIN_PACKAGE_COMMANDER depth=L3_INTEGRATION_RUNTIME
- ACC-SP_PLUGIN_PACKAGE_CHALLENGE subject=SP_PLUGIN_PACKAGE_CHALLENGE depth=L3_INTEGRATION_RUNTIME
- ACC-SP_HOST_INSTALL_REQUEST subject=SP_HOST_INSTALL_REQUEST depth=L3_INTEGRATION_RUNTIME
- ACC-TOOL_TPM_SP subject=TOOL_TPM_SP depth=L3_INTEGRATION_RUNTIME
- ACC-TOOL_COMMANDER_SP subject=TOOL_COMMANDER_SP depth=L3_INTEGRATION_RUNTIME
- ACC-TOOL_CHALLENGE_SP subject=TOOL_CHALLENGE_SP depth=L3_INTEGRATION_RUNTIME
- ACC-TOOL_HGK_UPGRADE subject=TOOL_HGK_UPGRADE depth=L3_INTEGRATION_RUNTIME
- ACC-TOOL_SBL_STACK subject=TOOL_SBL_STACK depth=L3_INTEGRATION_RUNTIME
- ACC-R5_UNINSTALL_BOUNDARY subject=SBL_HARNESS_UNINSTALL_BOUNDARY depth=L3_INTEGRATION_RUNTIME
Proxy, static, maker, shared, file-presence, or summary evidence cannot close runtime behavior.

## 7. Failure / HITL / Repair / Resume
Use the smallest affected repair, focused tests, affected regression, independent recheck, and a new checkpoint.
Require HITL for: scope expansion, credential or permission change, release promotion, owner ruling on a TT/CR.
No silent fallback. Use only a certified explicit substitute; otherwise return BLOCKED_EXTERNAL or BLOCKED_HITL.

## 8. Evidence / Independent acceptance / Candidate binding
Return case-specific raw receipts, command or probe, stdout/stderr/exit, producer, independent checker, source hashes, candidate head/package hash, invalidation, rollback, and residue readback.
Maker output is an evidence candidate, not a final verdict.

## 9. Termination / Final output
Terminal states: COMPLETED_ACCEPTED.
Nonterminal pauses: PAUSED_REMEDIABLE, BLOCKED, STOP_ESCALATE, TEMP_CLOSED, BLOCKED_EXTERNAL, BLOCKED_HITL.
Iteration or session pause requires a checkpoint and is not completion.
Return no claim above LOCAL.
