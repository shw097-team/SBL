# EXECUTABLE THIN CONSTRUCTION & ACCEPTANCE PROMPT

## 0. Machine Header
task_id: SBL-R17-S2-07-HOST-HOTPATH-POSTSESSION-CONTAINMENT
contract_schema: CAPC-PROMPT-CONTRACT/1
compiler_state: PROMPT_COMPILE_PASS

## 1. Mission / ChangeSet
Mission: prove or refuse post-turn host dispatch, bind the real host hot path, keep the containment per-card, and stop mistaking a relay-served lane turn for owner OAuth
Expected outcome: one measurable continuation claim with its ceiling, a per-card release list, and every remaining blocker named with its owner action
ChangeSet: CONTINUATION
Affected domains: host cron hot path, queue containment, lane payer attribution, os sandbox qualification

## 2. Authority / Files-first order
Read and hash the exact sources below in order. Use their owned controls directly; do not restate or replace them.
- R1 R17 S2-02 command attachments/R17 S2-02｜既有 HGK 車道複用、Codex 執行前隔離修復、持久任務接續與全產品 Native 驗收指揮令.md#0-9 role=NORMATIVE
- R2 HG-KSEOS/scripts/hgk-lane-dispatch.py :104-108,1190,2038-2117,2439 role=NORMATIVE
- R3 var/R17-20261023/receipts/FAR_S2_N9.json whole file role=SUPPORT
- 2 attachments/SBL × HG-KSEOS × Fabric × PIPD｜R17 S2-07 真 Host 熱路徑核驗・跨 Session 收據回讀・全量 Native 持久續工指揮令.md #0 role=NORMATIVE
Equal-rank conflict => quarantine, TT, and stop the affected work.

## 3. Intent / Non-goals / Claim ceiling
Expected experience: the report states what was measured, by whom, and what was refused
Constraints:
- no bulk release of deferred cards
- no owner credential handled by the agent
- no second scheduler or ledger
- relay-served turns are never reported as owner OAuth
- writer hold survives until an OS positive control exists
Non-goals:
- closing the mission
- declaring FULL_PRODUCT_ACCEPTED
- relaxing an assertion to make a card green
Authorized mutations:
- additive receipts under var/R17-20261023
- candidate patches under candidate_diffs
Forbidden mutations:
- SBL/HG-KSEOS/Fabric/PIPD tracked files
- another actor's untracked or dirty files
- force push
- editing a test oracle
Claim ceiling: LOCAL

## 4. Active / Deferred / Forbidden scope
Active:
- CAPC_OFFICIAL_COMPILE: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- EXECUTE_PREEXEC_SANDBOX_GUARD: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- EXECUTE_SANDBOX_MODE_ENFORCING: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- HGK_LANE_MODEL_ATTRIBUTION: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- HOST_SUPERVISOR_CONTINUATION: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- PLAN_OAUTH_PROVISIONING: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- POST_TURN_HOST_DISPATCH: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- HOTPATH_RUNTIME_BINDING: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- CONTAINMENT_PER_CARD_RELEASE: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- LANE_PAYER_ATTRIBUTION: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
- OS_SANDBOX_POSITIVE_CONTROL: ACTIVE_REQUIRED; action=QUALIFY; runtime_required=true
Non-active:
- PIPD_CANONICAL_PROMOTION: DEFERRED_SOURCE_BACKED; action=DEFER
- GITHUB_SBL_DRAFT_PUBLISH: DEFERRED_SOURCE_BACKED; action=DEFER
- VERIFY_DISTINCT_CHECKER: DEFERRED_SOURCE_BACKED; action=DEFER
Do not install, enable, or qualify a non-active capability.

## 5. Baseline / Reuse / Do-not-redo
Baseline: required=true; verified=true; reuse_prior_pass=false
Do not reopen:
- S2-04 compiled contract bytes
- frozen PI/PD
- the 145 obligation denominator
- another actor's dirty files
Verify source and candidate bindings before reuse. A tracked mutation invalidates the affected seal.

## 6. Implementation and qualification gates
Use Manifest → owner WP/RBWI → TaskSpec/WorkOrder → active AGENTS/SKILLS → Harness/Loop.
Runtime closure:
- CAPC_OFFICIAL_COMPILE: verdict=NOT_READY; work=close the open stages for CAPC_OFFICIAL_COMPILE
- EXECUTE_PREEXEC_SANDBOX_GUARD: verdict=NOT_READY; work=close the open stages for EXECUTE_PREEXEC_SANDBOX_GUARD
- EXECUTE_SANDBOX_MODE_ENFORCING: verdict=NOT_READY; work=close the open stages for EXECUTE_SANDBOX_MODE_ENFORCING
- HGK_LANE_MODEL_ATTRIBUTION: verdict=NOT_READY; work=close the open stages for HGK_LANE_MODEL_ATTRIBUTION
- HOST_SUPERVISOR_CONTINUATION: verdict=NOT_READY; work=close the open stages for HOST_SUPERVISOR_CONTINUATION
- PLAN_OAUTH_PROVISIONING: verdict=NOT_READY; work=close the open stages for PLAN_OAUTH_PROVISIONING
- POST_TURN_HOST_DISPATCH: verdict=RUNTIME_READY; work=keep the arm marker; read each new fire from the scheduler ledger
- HOTPATH_RUNTIME_BINDING: verdict=RUNTIME_READY; work=keep the binding receipt; re-measure after any tool edit
- CONTAINMENT_PER_CARD_RELEASE: verdict=NOT_READY; work=one admission receipt per card before release
- LANE_PAYER_ATTRIBUTION: verdict=NOT_READY; work=owner interactive sign-in in the sealed home
- OS_SANDBOX_POSITIVE_CONTROL: verdict=NOT_READY; work=a sandbox mode that executes a child AND denies an outside write
Required user journeys:
- J01_SAFE_RESUME: resume R17 without weakening the N9 hold → a checkpoint plus an explicit list of legal next work
- J02_NO_UNCONFINED_WRITE: no writer can reach a path outside its write-set → a denied write with a raw canary hash before and after
- J03_HOST_CONTINUATION: the mission continues without asking the user to say continue → a second workunit receipt appears after an interim report
- J04_POST_TURN_WAKE: work moves while nobody is chatting → a dispatched card with a fire time outside every agent turn
- J05_CONTAINMENT_RELEASE: deferred cards return one by one, with a reason each → a per-card admission record
Acceptance predicates:
- ACC-CAPC_OFFICIAL_COMPILE subject=CAPC_OFFICIAL_COMPILE depth=L3_INTEGRATION_RUNTIME
- ACC-EXECUTE_PREEXEC_SANDBOX_GUARD subject=EXECUTE_PREEXEC_SANDBOX_GUARD depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-EXECUTE_SANDBOX_MODE_ENFORCING subject=EXECUTE_SANDBOX_MODE_ENFORCING depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-HGK_LANE_MODEL_ATTRIBUTION subject=HGK_LANE_MODEL_ATTRIBUTION depth=L4_FAILURE_RECOVERY
- ACC-J01_SAFE_RESUME subject=J01_SAFE_RESUME depth=L4_FAILURE_RECOVERY
- ACC-J02_NO_UNCONFINED_WRITE subject=J02_NO_UNCONFINED_WRITE depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-REQ-N9-CONTAIN subject=REQ-N9-CONTAIN depth=L4_FAILURE_RECOVERY
- ACC-REQ-CAPC-COMPILE subject=REQ-CAPC-COMPILE depth=L3_INTEGRATION_RUNTIME
- ACC-DEL-CAPC-CONTRACT subject=DEL-CAPC-CONTRACT depth=L3_INTEGRATION_RUNTIME
- ACC-HOST_SUPERVISOR_CONTINUATION subject=HOST_SUPERVISOR_CONTINUATION depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-PLAN_OAUTH_PROVISIONING subject=PLAN_OAUTH_PROVISIONING depth=L4_FAILURE_RECOVERY
- ACC-J03_HOST_CONTINUATION subject=J03_HOST_CONTINUATION depth=L5_REAL_LIFECYCLE_SIDE_EFFECT
- ACC-REQ-HOST-CONTINUATION subject=REQ-HOST-CONTINUATION depth=L4_FAILURE_RECOVERY
- ACC-REQ-PLAN-OAUTH subject=REQ-PLAN-OAUTH depth=L4_FAILURE_RECOVERY
- ACC-DEL-S204-READBACK subject=DEL-S204-READBACK depth=L3_INTEGRATION_RUNTIME
- ACC-POST-TURN-DISPATCH subject=POST_TURN_HOST_DISPATCH depth=L3_INTEGRATION_RUNTIME
- ACC-HOTPATH-BIND subject=HOTPATH_RUNTIME_BINDING depth=L3_INTEGRATION_RUNTIME
- ACC-CONTAINMENT-PER-CARD subject=CONTAINMENT_PER_CARD_RELEASE depth=L3_INTEGRATION_RUNTIME
- ACC-LANE-PAYER-ATTRIBUTION subject=LANE_PAYER_ATTRIBUTION depth=L3_INTEGRATION_RUNTIME
- ACC-SANDBOX-POS-NEG subject=OS_SANDBOX_POSITIVE_CONTROL depth=L3_INTEGRATION_RUNTIME
- ACC-REQ-POST-TURN-DISPATCH subject=REQ-POST-TURN-DISPATCH depth=L3_INTEGRATION_RUNTIME
- ACC-REQ-HOTPATH-BIND subject=REQ-HOTPATH-BIND depth=L3_INTEGRATION_RUNTIME
- ACC-REQ-CONTAINMENT-PER-CARD subject=REQ-CONTAINMENT-PER-CARD depth=L3_INTEGRATION_RUNTIME
- ACC-REQ-LANE-PAYER-ATTRIBUTION subject=REQ-LANE-PAYER-ATTRIBUTION depth=L3_INTEGRATION_RUNTIME
- ACC-REQ-SANDBOX-POSITIVE-CONTROL subject=REQ-SANDBOX-POSITIVE-CONTROL depth=L3_INTEGRATION_RUNTIME
- ACC-J04_POST_TURN_WAKE subject=J04_POST_TURN_WAKE depth=L3_INTEGRATION_RUNTIME
- ACC-J05_CONTAINMENT_RELEASE subject=J05_CONTAINMENT_RELEASE depth=L3_INTEGRATION_RUNTIME
Proxy, static, maker, shared, file-presence, or summary evidence cannot close runtime behavior.

## 7. Failure / HITL / Repair / Resume
Use the smallest affected repair, focused tests, affected regression, independent recheck, and a new checkpoint.
Require HITL for: host owner sandbox provisioning, fabric policy designation, credential rotation.
No silent fallback. Use only a certified explicit substitute; otherwise return BLOCKED_EXTERNAL or BLOCKED_HITL.

## 8. Evidence / Independent acceptance / Candidate binding
Return case-specific raw receipts, command or probe, stdout/stderr/exit, producer, independent checker, source hashes, candidate head/package hash, invalidation, rollback, and residue readback.
Maker output is an evidence candidate, not a final verdict.

## 9. Termination / Final output
Terminal states: FULL_PRODUCT_ACCEPTED, CANCELLED_BY_OWNER.
Nonterminal pauses: ACTIVE_BUILD, CONTAINMENT_HELD_PER_CARD, DURABLE_WAIT_EXTERNAL, POST_TURN_DISPATCH_UNVERIFIED, SAFETY_HOLD_AFFECTED, SESSION_CHECKPOINTED_NOT_AUTONOMOUS.
Iteration or session pause requires a checkpoint and is not completion.
Return no claim above LOCAL.
