NONCE: EXECUTE-R152-Q3E2E2-NONCE-ce747836

Begin your reply with exactly this token on its own line: EXECUTE-R152-Q3E2E2-NONCE-ce747836

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# EXECUTE brief — Q3 / M2 isolated E2E, re-run for a green receipt (unique brief name, nothing else)

Bounded writer. The product tree is **read-only** for you: no edits to `sbl_core/`, `sbl_stack/`, `sbl_cli/`,
`tests/`. All your writes go under `C:/Users/user/AppData/Local/Temp/q3b/` and
`_governance/round-20261022-r15_2/workers/q3_e2e/`.

This is a re-run: the same chain already succeeded once in this round, but that lane hit its cap and wrote no nonce,
so the item carries a red receipt. You are producing the receipt, not a new product change.

## The task to build (non-prebuilt, ordinary language)

> Read JSONL work orders, print the open ones grouped by owner, newest file wins when the same id appears twice.

Pipeline: SBL-M01 intake → SBL-M02 spec (≥4 atoms) → SBL-M03 routing (must route to `CLI_TOOL`) → SBL-M04 governed
build bridge writes a real file **inside the declared writeset** into `C:/Users/user/AppData/Local/Temp/q3b/generated/`.

## Chain to execute and measure

1. PIPELINE — drive the four modules through their real entry points; record every stage's class/verdict and the
   writeset you passed. Write `PIPELINE_TRACE.json`.
2. BASELINE — write a test for the generated tool under the scratch dir; `python -m pytest -q -p no:cacheprovider
   <tests>` → record counts.
3. MUTATION — apply exactly one semantic mutation to the **generated** file (not the source):
   `sorted(paths, key=os.path.getmtime)` → add `reverse=True` (inverts newest-wins). Save `MUTATION.diff`.
4. MUTANT — rerun the tests: the duplicate-id test must FAIL with an assertion (an import error or a crash is NOT a
   mutant detection). Record counts + the failing test id.
5. REPAIR — restore the generated file to its **pre-mutation bytes**; prove it by sha256 equality, not by rewriting
   the logic; rerun → counts.
6. REGRESSION — `python -m pytest -q -p no:cacheprovider tests/test_core_modules.py tests/test_kind_matrix.py`
   in the product tree. Do **not** run the whole suite.
7. CLEANUP — `python -m sbl_stack.cli uninstall --root <scratch>/stack` (rc 0) and then
   `python -m sbl_stack.cli doctor --root <scratch>/stack` (must refuse: rc ≠ 0 with a typed problem). Delete the
   scratch `generated/` directory and show the directory listing afterwards.
8. Write `workers/q3_e2e/Q3_RESULT.json` with `predicate` booleans
   (`baseline_pass / mutant_fails_expected_assertion / repaired_pass / affected_regressions_pass /
   outside_scope_unchanged / cleanup_verified`), the counts, the sha256 pairs, and `claim_ceiling` =
   "locally verified single task; not independently accepted".

Set `TMPDIR`/`TEMP`/`TMP` to a directory **outside every git repo** for every child process (a temp dir inside a repo
makes `test_bind_repo_context_negative_not_a_repo` fail for a reason that has nothing to do with your change), and
`PYTHONDONTWRITEBYTECODE=1`.

Final message: the six predicate booleans, the pytest counts for baseline/mutant/repaired, the sha256 pair, and the
uninstall/doctor rcs. If the mutation cannot be made to fail an assertion, say so — do not simulate a failure.
