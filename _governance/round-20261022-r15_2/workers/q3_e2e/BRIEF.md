# EXECUTE brief — Q3 / M2: one non-prebuilt CLI_TOOL through the real six-module pipeline, with mutation → FirstFail → bounded repair → regression → cleanup

You are the bounded writer. All outputs go under
`C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/workers/q3_e2e/` and under a
scratch root `C:/Users/user/AppData/Local/Temp/q3_e2e/`. You may **not** modify any file in the SBL product
tree (`sbl_core/`, `sbl_sp/`, `sbl_cli/`, `sbl_stack/`, `tests/`, `tools/`). No commits, no lane dispatch,
no sub-agents.

## What must be true at the end (the predicate)

`baseline_pass && mutant_fails_expected_assertion && repaired_pass && affected_regressions_pass
 && outside_scope_unchanged && cleanup_verified`

## The task (non-prebuilt: it exists in no fixture in this repo)

Plain-language request: *"a CLI tool that reads a JSONL file of work orders and prints how many open work
orders each owner has, newest file wins on duplicates by (id)"*. Output is a new file
`<scratch>/generated/owner_load.py`, produced **through the product's own pipeline**, not hand-written
straight into place.

## Steps

1. **Fresh environment.** `python -m sbl_stack.cli install --root <scratch>/stack`, then
   `python -m sbl_stack.cli doctor --root <scratch>/stack` (expect rc 0, 14 components, 39 mode-gate cells).
   Record both.
2. **A scratch git repo as the governed write target.** `git init <scratch>/target`, one initial commit, so
   `sbl_core.m04_bridge.bind_repo_context(<scratch>/target)` and `GovernedBuildBridge.prepare/apply` have a
   real repo context and a real WriteSet boundary. Read `tests/test_core_modules.py` and
   `tests/e2e/test_gj01_cli.py` first for the actual constructor arguments — use them, do not invent them.
3. **Drive the pipeline.** `GoalIntake.intake(...)` → `GuidedSpecification.derive(goal, clauses)` →
   `Routing.route(atom, "CLI_TOOL")` → `GovernedBuildBridge.prepare/apply` (writes only inside the WriteSet)
   → `EvidenceVerification.record/verdict`. Persist the trace as
   `workers/q3_e2e/PIPELINE_TRACE.json` (one row per module: input id, output id, decision, code ref).
4. **Baseline pass.** Write `<scratch>/generated/test_owner_load.py` with 3 cases (normal, duplicate id,
   malformed line) and run `python -m pytest -q <scratch>/generated/test_owner_load.py`. All 3 pass.
5. **Controlled mutation.** Change exactly one behavioural line of `owner_load.py` (e.g. count by status
   instead of owner, or ignore the duplicate rule). Record the diff line in `MUTATION.diff`. Run the same
   test file: it must **FAIL** with the specific assertion you name in advance, and the failure must come
   from a real test assertion (non-zero exit with a failing test), not from an import error or a crash.
6. **Bounded repair.** Call `sbl_core.m06_repair.BoundedRepair.plan(first_fail, scope, attempts)` with the
   real first-fail string; apply the minimal repair to `owner_load.py`; rerun the 3 tests: pass.
7. **Regression (affected scope only).** Run `python -m pytest -q -p no:cacheprovider tests/test_core_modules.py tests/e2e tests/test_modes.py`
   — these are the modules the task touches. Report the exact counts. Do **not** run the whole `tests/` tree: the
   orchestrator owns the full-suite run and a second concurrent run would interleave with it.
8. **Outside scope unchanged.** `git -C <SBL tree> status --porcelain` before and after; the only delta may be
   the files you added under `workers/q3_e2e/`. Record both snapshots.
9. **Cleanup + readback.** `python -m sbl_stack.cli uninstall --root <scratch>/stack`, then
   `python -m sbl_stack.cli doctor --root <scratch>/stack` must refuse (rc != 0). Remove `<scratch>/target`
   and `<scratch>/generated`; record that both are gone.
10. Write `workers/q3_e2e/Q3_RESULT.json`:
    `{"predicate": {"baseline_pass": bool, "mutant_fails_expected_assertion": bool, "repaired_pass": bool,
      "affected_regressions_pass": bool, "outside_scope_unchanged": bool, "cleanup_verified": bool},
      "counts": {"baseline_tests": 3, "regression_passed": N, "regression_skipped": N},
      "first_fail": "<the verbatim assertion line>", "mutation_line": "...", "repair_line": "...",
      "raw_logs": ["<relative paths>"], "claim_ceiling": "one task on one host through the real modules; \
not a product acceptance, not an independent verification"}`

## Rules

- If any module cannot be driven as described (wrong signature, missing prerequisite), write the exact error
  into `Q3_RESULT.json` under `"blocked"` and stop at that step. Do **not** hand-write the generated tool and
  call it pipeline output.
- Every boolean in the predicate must be backed by a command and its exit code that you ran this turn.
- Cap your own output: put raw logs in files, keep your final message to the predicate table + the file list.
