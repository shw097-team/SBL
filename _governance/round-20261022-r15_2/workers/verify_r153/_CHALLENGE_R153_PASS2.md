NONCE: VERIFY-R153-P2-102133

Begin your reply with exactly this token on its own line: VERIFY-R153-P2-102133

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# VERIFY brief — challenge pass 2 (after repair)

You are the VERIFY_SECURITY checker again. Read-only: do not edit the candidate, do not dispatch or spawn any lane.

**Your first line of output must be the nonce token, alone.** Then the JSON.

Pass 1 returned `FAIL` with 7 findings. The maker has since repaired some of them. Your job in pass 2 is to test the
**repairs**, not to re-litigate what did not change, and to look for defects the repairs introduced.

## Repairs claimed since pass 1

| # | Pass-1 finding | Claimed repair | Test it by |
|---|---|---|---|
| R1 | `check_active_policy` returned ABSENT for a missing designation (bypass by deleting one file) and ignored `policy_path` | now refuses `ERR_EXEC_FRONTDOOR_ACTIVE_POLICY_ABSENT` unless `--allow-absent-active-policy`; refuses `ERR_EXEC_FRONTDOOR_ACTIVE_POLICY_MISMATCH` when `policy_path` is not the loaded declaration | `HG-KSEOS/scripts/hgk-exec-model-frontdoor.py:252`, `HG-KSEOS/tests/test_frontdoor_active_policy.py` (7 tests), and a live start attempt with a missing designation |
| R2 | the OpenSpec delta added two obligations the sources do not state (mandatory revision/dirty-path fields; a blanket ban on reporting a tree-caused difference as a regression) | both clauses rewritten to what `proposal.md` / `tasks.md` support | read `openspec/changes/far-r12-20261021/specs/sbl-release-claims/spec.md` against both sources; re-run `openspec validate --all --strict` |
| R3 | 24 rows were classed `CLOSE_NOW_AGENT` while their action was only a read | a scripted correction (`class_correction` block) moved them to `READY_FOR_EXECUTE`, keeping the original class in `class_before_correction` | read `FAR_DECISIONS_R15_3.json`; confirm no row's class still overstates its action |
| R4 | the advisory evidence-scan step in CI used `continue-on-error`, contradicting the repo's own `tests/test_ci_contract.py::test_ci_does_not_swallow_failures` | the step is removed; the evidence-surface scan stays a round-local measurement recorded as a TT | run `pytest tests/test_ci_contract.py tests/test_secret_scan_exclude.py` |
| R5 | `EXECUTE_RECEIPT.json` claimed C11/C22 closed and recorded a stale `ci.yml` size; `EXECUTE_RECEIPT_2.json` was absent | the denominator was re-measured from the orchestrator's own runs; the lane receipt was left untouched as evidence and the discrepancy is registered | compare `DENOMINATOR_R15_2.json` C11/C22/W02/C02 statuses against the files and commands they cite |

## Also test

- Whether any **new** defect appeared: the CI now has two new steps and no `continue-on-error`; the front door has a
  new flag; the delta changed. Look for unearned greens the repair could have created.
- Whether the `class_correction` block is honest: sample three corrected rows and check that the action really does not
  close the row.
- Whether `BENCH_DISPOSITION_R15_3.json` binds a digest that resolves.

## Output

Nonce line first, then exactly this JSON:

{"schema":"SBL_CHALLENGE_R15_3_PASS2/1","verdict":"PASS|PARTIAL|FAIL",
 "repaired":[{"id":"R1..R5","status":"PASS|PARTIAL|FAIL","observation":"<=300 chars","evidence":"file:line or command"}],
 "new_findings":[{"category":"...","text":"..."}],
 "first_fail":"...", "independent_acceptance":"ESTABLISHED|NOT_ESTABLISHED",
 "ceiling":"what may not be claimed after this review"}
