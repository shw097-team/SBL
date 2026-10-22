# R14-TS16 — measured bounded fix / recovery dry-run

**Verdict: PARTIAL.** Real sandbox defect, red→green, byte-equal copy-back rollback and zero newly failing test IDs proved. The full copied suite remains red; native autonomous engine/recovery is NOT qualified.

## Scope / subject

- Original: `C:\Projects\Agent_Workspace\HG-KSEOS` (read-only). Copy-time HEAD: `3dfaebc5c1d2ffe7d1782f3027bd25b54a557f2b`.
- Disposable copy: `C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/cache/scratch/ts16-sandbox`.
- Copy constructed using independent `git clone --no-hardlinks`, then every 744 tracked regular file overwritten with exact original working-tree bytes; equality asserted. Genuine ignored `evidence/` copied for full-suite inputs. No links back into original.
- Python 3.12.14 / pytest 9.1.1 from original venv executable, with `-B`, `PYTHONDONTWRITEBYTECODE=1`, sandbox `PYTHONPATH`, sandbox CWD. Only venv launchers/config copied for legacy CLI tests.
- Runtime-only relocation of legacy test ROOT globals and `tempfile.mkdtemp(...ROOT.parent/TEST_RESULTS)` into sandbox; test bytes and assertions unchanged. Full raw command/cwd/exit in each `ts16_*_run.json`. W3 scratch overridden into disposable copy.

## FirstFail / minimal RepairCone

- Earliest violated invariant: an unexpired lease must not be taken by another holder. FirstFail is the holder comparison in `src/hg_kseos/spine.py:122`, not merely the later pytest error.
- Injected `!=` → `==` in `SharedSpine.acquire_lease`; live lease holder A is then overwritten by holder B. Existing production test catches the missing LeaseConflict (`tests/test_spine.py:46–49`). No fabricated tests or responses.
- Repair: restore precisely that operator. One source line / one character differs. No test, schema, policy, registry, source document, or unrelated module changed. `ts16_injected.diff` preserves injection.
- Causal alternatives: missing DB/schema would error in setup (not observed); wrong module/cache would leave baseline test green (explicit sandbox import and `-B`); wrong invariant would produce a different exception. Red reproduces only the injected guard failure.
- Impact closure: lease acquisition → competing-holder rejection / requirement mutations using leases; focused test plus complete copied `tests/` suite. Excluded from write cone: all tests, other spine functions, lifecycle, registry, original repo. Full-suite run retains all global safety tests.

## Real pytest output (verbatim lines)

### baseline_target

```text
tests/test_spine.py::SharedSpineTests::test_dual_writer_is_rejected PASSED [100%]
============================== 1 passed in 0.37s ==============================
```
Exit: `0`. Raw: `ts16_baseline_target.log`, `ts16_baseline_target.xml`.

### baseline_full

```text
tests/test_spine.py::SharedSpineTests::test_dual_writer_is_rejected PASSED [ 79%]
== 25 failed, 581 passed, 1 skipped, 90 subtests passed in 157.91s (0:02:37) ==
```
Exit: `1`. Raw: `ts16_baseline_full.log`, `ts16_baseline_full.xml`.

### red

```text
tests/test_spine.py::SharedSpineTests::test_dual_writer_is_rejected FAILED [100%]
________________ SharedSpineTests.test_dual_writer_is_rejected ________________
FAILED tests/test_spine.py::SharedSpineTests::test_dual_writer_is_rejected - AssertionError: LeaseConflict not raised
============================== 1 failed in 0.50s ==============================
```
Exit: `1`. Raw: `ts16_red.log`, `ts16_red.xml`.

### green

```text
tests/test_spine.py::SharedSpineTests::test_dual_writer_is_rejected PASSED [100%]
============================== 1 passed in 0.41s ==============================
```
Exit: `0`. Raw: `ts16_green.log`, `ts16_green.xml`.

### rollback_red

```text
tests/test_spine.py::SharedSpineTests::test_dual_writer_is_rejected FAILED [100%]
________________ SharedSpineTests.test_dual_writer_is_rejected ________________
FAILED tests/test_spine.py::SharedSpineTests::test_dual_writer_is_rejected - AssertionError: LeaseConflict not raised
============================== 1 failed in 0.53s ==============================
```
Exit: `1`. Raw: `ts16_rollback_red.log`, `ts16_rollback_red.xml`.

### replay_green

```text
tests/test_spine.py::SharedSpineTests::test_dual_writer_is_rejected PASSED [100%]
============================== 1 passed in 0.34s ==============================
```
Exit: `0`. Raw: `ts16_replay_green.log`, `ts16_replay_green.xml`.

### green_full

```text
tests/test_spine.py::SharedSpineTests::test_dual_writer_is_rejected PASSED [ 79%]
== 25 failed, 581 passed, 1 skipped, 90 subtests passed in 204.43s (0:03:24) ==
```
Exit: `1`. Raw: `ts16_green_full.log`, `ts16_green_full.xml`.

## Regression comparison

- Comparable full baseline: 581 passed / 25 failed / 1 skipped, 90 subtests passed.
- Final full suite: 581 passed / 25 failed / 1 skipped, 90 subtests passed.
- Failed-ID set difference `final − baseline = []`; equal sets: `True`. **Zero new failures is not all-green.** IDs parsed from actual JUnit XML, not counts inferred from summaries. All retained in JSON.
- Initial apparatus miss retained in `ts16_baseline_initial.*`: 76 failed / 530 passed / 1 skipped. Missing genuine ignored evidence and nonexistent sibling TEST_RESULTS prompted a new baseline, before defect injection. The successful comparison uses only the same corrected setup.

### Full-suite failures retained (same before/after)

- `tests.test_autonomy_evolution.CliEntrypointTests::test_evolution_status_cli`
- `tests.test_autonomy_evolution.CliEntrypointTests::test_project_start_cli`
- `tests.test_autonomy_evolution.LifecycleIntegrationTests::test_checkpoint_resume_idempotent`
- `tests.test_autonomy_evolution.LifecycleIntegrationTests::test_workorders_admitted_via_spine`
- `tests.test_autonomy_evolution.LifecycleStateMachineTests::test_full_forward_path`
- `tests.test_autonomy_evolution.LifecycleStateMachineTests::test_repair_loop`
- `tests.test_c2_case_run.CaseRunCliTests::test_r4_only_allowed_files_changed`
- `tests.test_cs_a_gate_repair.D2ProjectScopedRequirementTests::test_existing_req_001_collision_avoided`
- `tests.test_cs_a_gate_repair.D2ProjectScopedRequirementTests::test_requirement_id_is_project_scoped`
- `tests.test_cs_a_gate_repair.D4PendingWorkCannotDeliverTests::test_delivered_allowed_when_workorders_terminal`
- `tests.test_cs_a_gate_repair.D4PendingWorkCannotDeliverTests::test_delivered_rejected_when_workorders_open`
- `tests.test_cs_a_gate_repair.D5OrdinaryUserFlowTests::test_start_to_admit_no_spine_workaround`
- `tests.test_cs_a_gate_repair.D6DenominatorTests::test_denominator_materializes_full_project`
- `tests.test_far_lane_fix_20261015.TestP0PinAssert::test_current_pin_verifies`
- `tests.test_far_lane_fix_20261015.TestP0PinAssert::test_digest_mismatch_is_typed_not_a_spawn`
- `tests.test_far_lane_fix_20261015.TestP1MandateConsumer::test_owner_order_mandate_resolves`
- `tests.test_far_lane_fix_20261015.TestP1MandateConsumer::test_verify_security_mandate_resolves`
- `tests.test_far_lane_fix_20261015.TestP1MandateConsumer::test_wrong_model_in_pool_refuses`
- `tests.test_final_md_section_u_semantics.FinalMdSectionUSemanticTests::test_fixture_a_end_to_end_against_real_validator`
- `tests.w3_solution.test_code_page_independence::test_invalid_utf8_child_bytes_do_not_change_preflight_classification`
- `tests.w3_solution.test_mandatory_defects::test_preflight_cleanup_failure_changes_return_code_and_is_recorded`
- `tests.w3_solution.test_receipt_schema::test_preflight_receipt_carries_all_additive_fields`
- `tests.w3_solution.test_receipt_schema::test_served_model_is_null_when_no_turn_is_served`
- `tests.w3_solution.test_served_vs_declared_identity::test_primary_acceptance_long_lane_mismatch_fails_closed_with_receipt`
- `tests.w3_solution.test_served_vs_declared_identity::test_vacuous_pass_control_unreadable_banner_fails_closed`

## Rollback / replay / digests

- Repair preimage (defective) SHA-256: `453855d7aaf3257610fa86dcda973799e24161373bf4e7920d8c256301733430`.
- Copy-back undo of repair SHA-256: `453855d7aaf3257610fa86dcda973799e24161373bf4e7920d8c256301733430`. Byte equality asserted; targeted test returns red again.
- Healthy original preimage SHA-256: `024a3068fc37444bd5b1750947f2bce3e3d58c592dd6d15832fdc6dbaf1215d1`.
- Final whole-experiment restore SHA-256: `024a3068fc37444bd5b1750947f2bce3e3d58c592dd6d15832fdc6dbaf1215d1`. Exact bytes compared; targeted replay returns green; full suite run follows.
- Preimages preserved as `ts16_spine_preimage.bin` and `ts16_spine_defect_preimage.bin`; readback `ts16_rollback.json`. Replaying here means deterministic local restoration/retest, not reissuing an unknown external effect.

## Attempt / lease / checkpoint limits

- File repair attempts: `1` / cap `1`. Real `sbl_core.m06_repair.BoundedRepair.plan` returns `STOP_ESCALATE` for the next attempt; no second repair file write performed. Rollback/replay are separately recorded recovery actions, not retries of an unknown effect.
- Repair executed under SharedSpine lease assertion in an isolated SQLite DB; elapsed `0.078000` seconds / TTL `60` seconds; lease explicitly released. This is a local dry-run guard, not a newly minted Native Permit.
- Real negative lease assertions: {"released": "ERR_LEASE_REQUIRED:TS16-SPINE-FILE", "expired": "ERR_LEASE_EXPIRED:TS16-EXPIRED", "foreign": "ERR_LEASE_REQUIRED:TS16-FOREIGN"}. No file writes on those probes.
- Native `begin_repair` gap reproduced independently: budget=1 yet attempts_used=2 after second call. This probe writes only sandbox lifecycle rows and never a second source patch. Native attempt enforcement therefore **fails**; planner STOP is not proof the native executor enforces limits.
- Real checkpoint/resume recorded in `ts16_loop.json`: state REPAIRING is retained, but first_unfinished incorrectly projects PROJECT_CREATED. Code `lifecycle.py:391–439` also replaces intent_json with checkpoint sidecar and checks project ID rather than recomputing state_digest. Do not promote to robust restart/recovery PASS.
- `HarnessAction.attempt` / `timeout_seconds` are fields (`harness.py:31–32`); `Harness.run` (`68–85`) does not itself enforce attempt or wall-clock timeout. Required follow-up: owner-scoped atomic budget reservation before effect, expiry/subject/scope guards at write seam, subprocess timeout + status readback, digest-verified non-destructive checkpoint, distinct checker.

## Original integrity / blockers

```json
{
  "head_before": "3dfaebc5c1d2ffe7d1782f3027bd25b54a557f2b",
  "head_after": "3dfaebc5c1d2ffe7d1782f3027bd25b54a557f2b",
  "head_unchanged": true,
  "status_porcelain": "",
  "tracked_file_count": 744,
  "tracked_bytes_unchanged": true,
  "changed_paths": [],
  "initial_preflight_head": "3dab083a92032153750b04f805e410f748a407a2",
  "freshness_note": "HEAD changed between initial inspection and copy; no original writes performed by this worker. Copy-time HEAD is measured baseline."
}
```

- Snapshot comparison proves tracked original bytes. Git status and HEAD are separately read back; ignored/live original runtime state is not certified by a tracked-file manifest.
- The early preflight HEAD changed before copying; this worker performed no original write. Copy-time HEAD, not stale initial inspection, binds this experiment.
- No original repo changes were attempted to repair baseline failures. No push/merge/release, no SWOF effect, no alternate control plane. No independent acceptance is claimed.
- Governance mapping: DOC-11/C30 distinguishes STANDALONE from Shadow/Connected; DOC-13/C46.1a and C46.3 require preserved FirstFail/evidence, minimal cone, effect idempotency, bounded repair, affected+global regression and byte-level recovery. This dry-run supplies local observations only; TS16 full product gate remains OPEN.

## Scope incident (not hidden)

- Initial copied `tests/w3_solution/conftest.py:pytest_configure` created the sibling `C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/cache/scratch/scratch-w3/pytest` at 2026-10-22T02:05:15Z, outside the exact allowed sandbox. This violates the narrow write scope, although the original repo remained unchanged. The directory is empty; it was left untouched rather than silently deleted outside scope. Corrected baseline/final runs set `HGK_SOLUTION_SCRATCH` inside the disposable copy. This incident prevents a clean scope-compliance PASS.
