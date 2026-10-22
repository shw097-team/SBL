# R14-TS23 — Third independent review

**Verdict: FAIL**

## Results

- **G1: closed.** Reporting zero bytes for non-empty files fails at `test_agent.py:12`: `AssertionError: Lists differ: [0, 0] != [5765, 5776]`.
- A separate mutation corrupting **only** `--max-steps 1` fails at line 18: `AssertionError: Lists differ: [0] != [5765]`. The default two-step output remains correct in this experiment.
- **G2: not closed as a harness guarantee.** All five shipped mutation cases reproduce genuine output-value assertions, and the re-run receipt matches the maker receipt on `failure_kind`, `false_red`, `restored_byte_identical`, `caught`, `applied`, test exit, assertion text and aggregate flags. Timing text differs naturally.
- However, `run_test()` labels any output containing `AssertionError` as `ASSERTION`. A real process raising `NameError('AssertionError: decoy, not an assertion')` is misclassified. More importantly, replacing the agent byte expression with an undefined name causes a genuine child `NameError`; the test's return-code assertion wraps it, and the harness records **caught=true, false_red=false**, with **restored_byte_identical=true, baseline_all_pass=true**. No output-value assertion was reached. Restoration and baseline flags cannot establish detection quality.
- `main()` always returns zero (line 116), even when receipt flags indicate failure. The remediation's statement that false reds make the run fail is not enforced by process exit.

## New mutations

| ID | Mutation | Unchanged test outcome |
|---|---|---|
| N1 | CLI: correct bytes/digest, wrong path | Caught as AssertionError |
| N2 | Skill: correct heading text/levels, line number +1 | Caught as AssertionError |
| N3 | Skill: correct headings, `path=WRONG_PATH` | **SURVIVED**, exit 0 |
| N4 | Agent, one-step only: correct bytes, wrong path | **SURVIVED**, exit 0 |
| N5 | Agent, one-step only: correct bytes/path, zero-filled digest | **SURVIVED**, exit 0 |
| N6 | Agent: map each digest to the next file | Caught as AssertionError |
| N7 | Agent, one-step only: `remaining=999` | **SURVIVED**, exit 0 |
| N8 | Agent, one-step only: `halt_reason=QUEUE_EXHAUSTED` while two remain | **SURVIVED**, exit 0 |

Each survivor was additionally invoked directly: the wrong field is present in valid JSON and the program exits zero. The skill tests never assert the emitted path. The limited-agent branch asserts only `steps` and exact byte counts, leaving its path, digest, remaining count and halt reason unchecked. The default-agent branch does catch wrong digest mapping.

## Regression controls

All three unmodified installed programs pass their own tests, including ordinary installed `-m` dispatch. All three importable no-output stubs fail with `AssertionError: '' is not true : program produced no output`, not import errors. `pyvenv.cfg` declares `include-system-site-packages = false`; all three modules resolve inside the sandbox venv. This confirms the requested venv properties, not full environment sanitization: inherited external PYTHONPATH entries remain visible.

## Scope and evidence

Only `ts23_review3.json` and this Markdown report were written. Mutation source, test-created fixture writes, and the harness receipt write were intercepted in memory because modifying the sandbox or receipts was prohibited. The actual harness source, original mutation list and `main()` ran with this overlay; its generated receipt was read back from that overlay. Tests and programs ran in real venv child processes, with bytecode writes disabled. This is a disclosed write-free adapted rerun, **not** an on-disk harness rerun; source restoration was tested in the overlay rather than by rewriting installed files. The JSON embeds the runner, exact substitutions, receipt, observations, direct survivor outputs and source SHA-256 bindings. All 3,049 sandbox files retained the same SHA-256 inventory and the maker receipt remained unchanged.

**Claim ceiling:** G1 and the regression controls pass; five maker mutations genuinely detect output errors. G2 still allows false behavioral-detection credit, and five new mutations survive. No overall acceptance is supported.
