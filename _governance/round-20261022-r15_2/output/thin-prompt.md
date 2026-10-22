# EXECUTABLE THIN CONSTRUCTION & ACCEPTANCE PROMPT

## 0. Machine Header
task_id: SBL-R15.2-CONTINUATION-20261022
contract_schema: CAPC-PROMPT-CONTRACT/1
compiler_state: PROMPT_COMPILE_PASS

## 1. Mission / ChangeSet
Mission: Land, execute, check, accept and deliver the SBL_PIPD-LS-PKG upper control package under the Fabric governor, with HG-KSEOS as the only native issuer and Hermes as the governed runtime.
Expected outcome: SBL is the single product engineering front door and HG-KSEOS remains the only native authority for admission, state and acceptance.
ChangeSet: CONTINUATION
Affected domains: SBL, HG-KSEOS, Fabric, PIPD, Hermes

## 2. Authority / Files-first order
Read and hash the exact sources below in order. Use their owned controls directly; do not restate or replace them.
- COMPILER_BUNDLE C:\Projects\Agent_Workspace\知識庫\工程基座\construction-acceptance-prompt-compiler\construction-acceptance-prompt-compiler\construction-acceptance-prompt-compiler_SKILL.md SOURCE_FREEZE.json#family=CAPC_OFFICIAL_BUNDLE role=NORMATIVE
- CHECKER_BUNDLE C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\參考工程資料庫\SKILLS_PLUGIN\challenge-review-SKILL.md SOURCE_FREEZE.json#family=CHALLENGE_REVIEW_SKILL role=NORMATIVE
- POLICY_SOURCE C:/Projects/Agent_Workspace/Fabric/FABRIC/control/ACCEPTANCE_POLICY.yaml SOURCE_FREEZE.json#family=FABRIC_ACTIVE_POLICY role=STATE_EVIDENCE
- RUNTIME_PLANE C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/hermes-agent/hermes_cli/main.py SOURCE_FREEZE.json#family=HERMES_RUNTIME_AND_KANBAN role=STATE_EVIDENCE
- NATIVE_CONTROL_PLANE C:/Projects/Agent_Workspace/HG-KSEOS/AGENTS.md SOURCE_FREEZE.json#family=HGK_NATIVE_CONTROL_PLANE role=STATE_EVIDENCE
- LIFECYCLE_STANDARD C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\PIPD\PIPD_LS\PIPD_LS_DOC-00_2026-10-07_r2_HIGH_RETENTION_FULL_REPAIR_FULL_SUBSTANTIVE_BODY.md SOURCE_FREEZE.json#family=PIPD_LS_DOC-00..09 role=NORMATIVE
- STATE_EVIDENCE git -C C:/Projects/Agent_Workspace/SBL rev-parse evidence/r14-20261022-native SOURCE_FREEZE.json#family=R14_NATIVE_LEDGER_AND_CHECKPOINT role=STATE_EVIDENCE
- SUBORDINATE_CONTRACT C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\attachments\SBL_HGK_FABRIC_PIPD_LS_PKG_R15_1_FULL_SUBSTANTIVE_INTEGRATED_REPAIR_REPLACEMENT_2026-10-22.md SOURCE_FREEZE.json#family=R15.1_SUBSTANTIVE_CONTRACT role=NORMATIVE
- TASK_COMMAND C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\attachments\SBL_HERMES_HGK_FABRIC_R15_2_THIN_CONSTRUCTION_ACCEPTANCE_COMMAND_2026-10-22.md SOURCE_FREEZE.json#family=R15.2_ROUTEOUT_COMMAND role=NORMATIVE
- PRODUCT_DESIGN_CANDIDATE C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-00.md SOURCE_FREEZE.json#family=SBL_PIPD-LS-PKG_DOC-00..13 role=NORMATIVE
Equal-rank conflict => quarantine, TT, and stop the affected work.

## 3. Intent / Non-goals / Claim ceiling
Expected experience: A long autonomous round that never fabricates a PASS, reports blockers as typed first-fails, and returns independently checkable evidence.
Constraints:
- product_front_door: SBL_ONLY
- native_issuer_and_state_acceptance: HG_KSEOS_ONLY
- runtime_orchestrator: CURRENT_CANONICAL_HERMES
- final_gate: FAIL_CLOSED
- no second issuer, reducer, RBWI or control plane
Non-goals:
- rewriting the governing documents
- claiming PROMPT_COMPILE_PASS as RUNTIME_READY
- signing permits or releases inside chat
Authorized mutations:
- write inside the evidence worktree only
- create candidate and evidence branches
Forbidden mutations:
- git add -A
- reset --hard
- force push
- overwriting foreign dirty or untracked files
- SWOF mutation without W3
- editing oracles to turn tests green
Claim ceiling: LOCAL

## 4. Active / Deferred / Forbidden scope
Active:
- SBL_PRODUCT_FRONT_DOOR: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- HGK_NATIVE_ISSUER: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- FABRIC_ACTIVE_POLICY_CONSUMER: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- PIPD_8_SKILLS: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- PIPD_19_CONTRACT_FAMILIES: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- PIPD_13_CLI_VERBS: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- TPM_SP: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- COMMANDER_SP: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- EXTERNAL_CHALLENGE_SP: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- ONE_CORE_SIX_MODULES: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- FIVE_PRODUCT_TOOLS: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- EIGHT_KINDS_THREE_MODES: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- HERMES_KANBAN_SWARM: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- OPENSPEC_STRICT_METHOD: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
Non-active:
- GSTACK_METHOD: DONOR_ONLY; action=DEFER
- SWOF_W3_CONNECTED: DEFERRED_SOURCE_BACKED; action=DEFER
- CHATGPT_PRIVATE_PLUGINS: DEFERRED_SOURCE_BACKED; action=DEFER
- AGENT_OS_KIND: PROHIBITED; action=PROHIBIT
- AI_SYSTEM_KIND: PROHIBITED; action=PROHIBIT
- GENIE_NATIVE_WRITE: DEFERRED_SOURCE_BACKED; action=DEFER
- PLUGIN_PROFILE_KINDS: DEFERRED_SOURCE_BACKED; action=DEFER
Do not install, enable, or qualify a non-active capability.

## 5. Baseline / Reuse / Do-not-redo
Baseline: required=true; verified=true; reuse_prior_pass=true
Do not reopen:
- R14 items independently accepted on the same exact subject
- SBL DOC-00..13 normative text
Verify source and candidate bindings before reuse. A tracked mutation invalidates the affected seal.

## 6. Implementation and qualification gates
Use Manifest → owner WP/RBWI → TaskSpec/WorkOrder → active AGENTS/SKILLS → Harness/Loop.
Runtime closure:
- SBL_PRODUCT_FRONT_DOOR: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering SBL_PRODUCT_FRONT_DOOR; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- HGK_NATIVE_ISSUER: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering HGK_NATIVE_ISSUER; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- FABRIC_ACTIVE_POLICY_CONSUMER: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering FABRIC_ACTIVE_POLICY_CONSUMER; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- PIPD_8_SKILLS: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering PIPD_8_SKILLS; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- PIPD_19_CONTRACT_FAMILIES: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering PIPD_19_CONTRACT_FAMILIES; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- PIPD_13_CLI_VERBS: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering PIPD_13_CLI_VERBS; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- TPM_SP: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering TPM_SP; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- COMMANDER_SP: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering COMMANDER_SP; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- EXTERNAL_CHALLENGE_SP: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering EXTERNAL_CHALLENGE_SP; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- ONE_CORE_SIX_MODULES: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering ONE_CORE_SIX_MODULES; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- FIVE_PRODUCT_TOOLS: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering FIVE_PRODUCT_TOOLS; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- EIGHT_KINDS_THREE_MODES: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering EIGHT_KINDS_THREE_MODES; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- HERMES_KANBAN_SWARM: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering HERMES_KANBAN_SWARM; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
- OPENSPEC_STRICT_METHOD: verdict=NOT_READY; work=obtain the HGK native WorkOrder and Permit covering OPENSPEC_STRICT_METHOD; execute the real lifecycle probe and persist stdout/stderr/exit with sha256; independent checker, distinct principal, re-execution on the same candidate sha
Required user journeys:
- GJ01: describe a new CLI tool in ordinary language and receive a working installable CLI → built wheel, --help, JSON output, persistence and clean uninstall
- GJ02: repair one failing test in an existing repository inside an exact write set → minimal diff, red to green evidence, foreign files untouched
- GJ03: install an agent skill and a simple agent, then verify refusal of forbidden tools → host-discovered trigger, denial receipt, uninstall without residue
Acceptance predicates:
- ACC-SBL_PRODUCT_FRONT_DOOR-01 subject=SBL_PRODUCT_FRONT_DOOR depth=L3_INTEGRATION_RUNTIME
- ACC-HGK_NATIVE_ISSUER-01 subject=HGK_NATIVE_ISSUER depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-FABRIC_ACTIVE_POLICY_CONSUMER-01 subject=FABRIC_ACTIVE_POLICY_CONSUMER depth=L3_INTEGRATION_RUNTIME
- ACC-PIPD_8_SKILLS-01 subject=PIPD_8_SKILLS depth=L3_INTEGRATION_RUNTIME
- ACC-PIPD_19_CONTRACT_FAMILIES-01 subject=PIPD_19_CONTRACT_FAMILIES depth=L2_UNIT_BEHAVIOR
- ACC-PIPD_13_CLI_VERBS-01 subject=PIPD_13_CLI_VERBS depth=L2_UNIT_BEHAVIOR
- ACC-TPM_SP-01 subject=TPM_SP depth=L3_INTEGRATION_RUNTIME
- ACC-COMMANDER_SP-01 subject=COMMANDER_SP depth=L3_INTEGRATION_RUNTIME
- ACC-EXTERNAL_CHALLENGE_SP-01 subject=EXTERNAL_CHALLENGE_SP depth=L3_INTEGRATION_RUNTIME
- ACC-ONE_CORE_SIX_MODULES-01 subject=ONE_CORE_SIX_MODULES depth=L3_INTEGRATION_RUNTIME
- ACC-FIVE_PRODUCT_TOOLS-01 subject=FIVE_PRODUCT_TOOLS depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-EIGHT_KINDS_THREE_MODES-01 subject=EIGHT_KINDS_THREE_MODES depth=L3_INTEGRATION_RUNTIME
- ACC-HERMES_KANBAN_SWARM-01 subject=HERMES_KANBAN_SWARM depth=L3_INTEGRATION_RUNTIME
- ACC-OPENSPEC_STRICT_METHOD-01 subject=OPENSPEC_STRICT_METHOD depth=L2_UNIT_BEHAVIOR
- ACC-W00-01 subject=W00 depth=L3_INTEGRATION_RUNTIME
- ACC-W01-01 subject=W01 depth=L3_INTEGRATION_RUNTIME
- ACC-W02-01 subject=W02 depth=L3_INTEGRATION_RUNTIME
- ACC-W03-01 subject=W03 depth=L3_INTEGRATION_RUNTIME
- ACC-W04-01 subject=W04 depth=L3_INTEGRATION_RUNTIME
- ACC-W05-01 subject=W05 depth=L3_INTEGRATION_RUNTIME
- ACC-W06-01 subject=W06 depth=L3_INTEGRATION_RUNTIME
- ACC-W07-01 subject=W07 depth=L3_INTEGRATION_RUNTIME
- ACC-W08-01 subject=W08 depth=L3_INTEGRATION_RUNTIME
- ACC-W09-01 subject=W09 depth=L3_INTEGRATION_RUNTIME
- ACC-W10-01 subject=W10 depth=L3_INTEGRATION_RUNTIME
- ACC-W11-01 subject=W11 depth=L3_INTEGRATION_RUNTIME
- ACC-W12-01 subject=W12 depth=L3_INTEGRATION_RUNTIME
- ACC-W13-01 subject=W13 depth=L3_INTEGRATION_RUNTIME
- ACC-W14-01 subject=W14 depth=L3_INTEGRATION_RUNTIME
- ACC-W15-01 subject=W15 depth=L3_INTEGRATION_RUNTIME
- ACC-W16-01 subject=W16 depth=L3_INTEGRATION_RUNTIME
- ACC-W17-01 subject=W17 depth=L3_INTEGRATION_RUNTIME
- ACC-C00-01 subject=C00 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C01-01 subject=C01 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C02-01 subject=C02 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C03-01 subject=C03 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C04-01 subject=C04 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C05-01 subject=C05 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C06-01 subject=C06 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C07-01 subject=C07 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C08-01 subject=C08 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C09-01 subject=C09 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C10-01 subject=C10 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C11-01 subject=C11 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C12-01 subject=C12 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C13-01 subject=C13 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C14-01 subject=C14 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C15-01 subject=C15 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C16-01 subject=C16 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C17-01 subject=C17 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C18-01 subject=C18 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C19-01 subject=C19 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C20-01 subject=C20 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C21-01 subject=C21 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C22-01 subject=C22 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C23-01 subject=C23 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-C24-01 subject=C24 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-TS00-01 subject=R14-TS00 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS01-01 subject=R14-TS01 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS02-01 subject=R14-TS02 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS03-01 subject=R14-TS03 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS04-01 subject=R14-TS04 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS05-01 subject=R14-TS05 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS06-01 subject=R14-TS06 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS07-01 subject=R14-TS07 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS08-01 subject=R14-TS08 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS09-01 subject=R14-TS09 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS10-01 subject=R14-TS10 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS11-01 subject=R14-TS11 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS12-01 subject=R14-TS12 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS13-01 subject=R14-TS13 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS14-01 subject=R14-TS14 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS15-01 subject=R14-TS15 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS16-01 subject=R14-TS16 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS17-01 subject=R14-TS17 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS18-01 subject=R14-TS18 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS19-01 subject=R14-TS19 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS20-01 subject=R14-TS20 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS21-01 subject=R14-TS21 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS22-01 subject=R14-TS22 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS23-01 subject=R14-TS23 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS24-01 subject=R14-TS24 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS25-01 subject=R14-TS25 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS26-01 subject=R14-TS26 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS27-01 subject=R14-TS27 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS28-01 subject=R14-TS28 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS29-01 subject=R14-TS29 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-TS30-01 subject=R14-TS30 depth=L3_INTEGRATION_RUNTIME
- ACC-R14-CHK00-01 subject=R14-CHK00 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK01-01 subject=R14-CHK01 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK02-01 subject=R14-CHK02 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK03-01 subject=R14-CHK03 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK04-01 subject=R14-CHK04 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK05-01 subject=R14-CHK05 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK06-01 subject=R14-CHK06 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK07-01 subject=R14-CHK07 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK08-01 subject=R14-CHK08 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK09-01 subject=R14-CHK09 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK10-01 subject=R14-CHK10 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK11-01 subject=R14-CHK11 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK12-01 subject=R14-CHK12 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK13-01 subject=R14-CHK13 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK14-01 subject=R14-CHK14 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK15-01 subject=R14-CHK15 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK16-01 subject=R14-CHK16 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK17-01 subject=R14-CHK17 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK18-01 subject=R14-CHK18 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK19-01 subject=R14-CHK19 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK20-01 subject=R14-CHK20 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK21-01 subject=R14-CHK21 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK22-01 subject=R14-CHK22 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK23-01 subject=R14-CHK23 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK24-01 subject=R14-CHK24 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK25-01 subject=R14-CHK25 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK26-01 subject=R14-CHK26 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK27-01 subject=R14-CHK27 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK28-01 subject=R14-CHK28 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK29-01 subject=R14-CHK29 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-R14-CHK30-01 subject=R14-CHK30 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-E01-01 subject=E01 depth=L3_INTEGRATION_RUNTIME
- ACC-E02-01 subject=E02 depth=L3_INTEGRATION_RUNTIME
- ACC-E03-01 subject=E03 depth=L3_INTEGRATION_RUNTIME
- ACC-E04-01 subject=E04 depth=L3_INTEGRATION_RUNTIME
- ACC-E05-01 subject=E05 depth=L3_INTEGRATION_RUNTIME
- ACC-E06-01 subject=E06 depth=L3_INTEGRATION_RUNTIME
- ACC-E07-01 subject=E07 depth=L3_INTEGRATION_RUNTIME
- ACC-E08-01 subject=E08 depth=L3_INTEGRATION_RUNTIME
- ACC-E09-01 subject=E09 depth=L3_INTEGRATION_RUNTIME
- ACC-M1-01 subject=M1 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-M2-01 subject=M2 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-M3-01 subject=M3 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-M4-01 subject=M4 depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-DLV-d6106d42 subject=18 work packages depth=L3_INTEGRATION_RUNTIME
- ACC-DLV-9877c311 subject=25 check runs depth=L3_INTEGRATION_RUNTIME
- ACC-DLV-6f194bdb subject=31 R14 tasks and 31 R14 checks depth=L3_INTEGRATION_RUNTIME
- ACC-DLV-b9e60416 subject=E01..E09 depth=L3_INTEGRATION_RUNTIME
- ACC-DLV-5c762c92 subject=M1..M4 depth=L3_INTEGRATION_RUNTIME
- ACC-DLV-230ed618 subject=raw evidence manifest depth=L3_INTEGRATION_RUNTIME
- ACC-DLV-dc45853a subject=independent acceptance package depth=L3_INTEGRATION_RUNTIME
- ACC-GJ01 subject=GJ01 depth=L3_INTEGRATION_RUNTIME
- ACC-GJ02 subject=GJ02 depth=L3_INTEGRATION_RUNTIME
- ACC-GJ03 subject=GJ03 depth=L3_INTEGRATION_RUNTIME
Proxy, static, maker, shared, file-presence, or summary evidence cannot close runtime behavior.

## 7. Failure / HITL / Repair / Resume
Use the smallest affected repair, focused tests, affected regression, independent recheck, and a new checkpoint.
Require HITL for: NEW_SCOPE, IRREVERSIBLE, HIGH_RISK_EXCEPTION, PRODUCTION_RELEASE, SECRET_PERMISSION_ESCALATION.
No silent fallback. Use only a certified explicit substitute; otherwise return BLOCKED_EXTERNAL or BLOCKED_HITL.

## 8. Evidence / Independent acceptance / Candidate binding
Return case-specific raw receipts, command or probe, stdout/stderr/exit, producer, independent checker, source hashes, candidate head/package hash, invalidation, rollback, and residue readback.
Maker output is an evidence candidate, not a final verdict.

## 9. Termination / Final output
Terminal states: PASS, PARTIAL, FAIL, TEMP_CLOSED, NO_LEGAL_PROGRESS.
Nonterminal pauses: BLOCKED_HITL, BLOCKED_EXTERNAL, UNKNOWN_EFFECT.
Iteration or session pause requires a checkpoint and is not completion.
Return no claim above LOCAL.
