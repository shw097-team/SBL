# EXECUTE brief — author the `doctor` typed-refusal repair under a green receipt (product code changes HERE)

Bounded writer. Change only `sbl_stack/__init__.py`. Do not touch tests, do not touch any other module, no commits.

## Why this lane exists

The same repair was once made by a lane whose receipt was red, so an independent challenge refused to count it: the
behaviour was evidenced, the **authorship** was not. The repair has been **reverted** for you. You are authoring it, so
`product_code_changed` must be `true` in your report.

## Measured red (this is your first fail, already reproduced)

```
cd C:/Projects/Agent_Workspace/_r152_ev
python -m pytest -q -p no:cacheprovider tests/test_stack_verbs.py
```

```
FAILED  tests/test_stack_verbs.py::StackVerbTests::test_doctor_refuses_a_manifest_naming_a_nonexistent_component
SUBFAILED(shape='digest-edited')  ...::test_doctor_refuses_a_tampered_manifest_with_a_typed_code_and_no_traceback
SUBFAILED(shape='entry-removed')  ...::test_doctor_refuses_a_tampered_manifest_with_a_typed_code_and_no_traceback
tests/test_stack_verbs.py:112: KeyError
```

The two tests are existing committed oracles — read them (lines 40–120) and satisfy them; **do not edit them**.

## What to change

In `doctor()` inside `sbl_stack/__init__.py`:

1. a component named in `stack.json` whose module cannot be resolved must become a **problem**, not a `KeyError` /
   traceback;
2. the report must carry a **typed** `code` (`SBL_E_COMPONENT_UNRESOLVED`) when any component is unresolved, while
   `ok` stays `false` and the existing keys (`problems`, `target`, `components`, `claim_ceiling`,
   `host_install_state`) keep their shape;
3. `doctor` must still exit non-zero through the CLI for these cases with **no `Traceback`** in stdout/stderr.

Minimal change only. `load`, `invoke`, `upgrade`, `rollback` are out of scope.

## Budget — hard

**At most 10 shell commands.** Read the test file once, read `doctor()` once, edit, run the test file, write the JSON,
stop. No whole-suite run, no repo-wide grep, no exploration. If something surprises you, record it instead of chasing it.

## Deliverable

1. `python -m pytest -q -p no:cacheprovider tests/test_stack_verbs.py` → all green (report the counts).
2. Write `workers/q5_repair/DOCTOR_REPAIR2.json`:
   `{"product_code_changed": true, "files_changed": ["sbl_stack/__init__.py"], "typed_code": "SBL_E_COMPONENT_UNRESOLVED",
     "tests": {"file": "tests/test_stack_verbs.py", "passed": N, "failed": 0, "skipped": N},
     "shell_commands_used": N, "before_sha256": "...", "after_sha256": "...",
     "claim_ceiling": "doctor refuses an unresolvable or tampered component with a typed code; nothing about release, installation or acceptance is claimed"}`
3. Final message: the test counts, the sha256 pair, and **the honest number of shell commands you used** — an
   understated count is worse than a large one (a previous lane claimed 8 while its log showed 16, and the challenge
   caught it).

Set `TMPDIR`/`TEMP`/`TMP` outside every git repo, and `PYTHONDONTWRITEBYTECODE=1`.
