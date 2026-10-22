# EXECUTE brief — `load` must refuse a tampered manifest with a typed code (same discipline as `doctor`)

Bounded writer. Change only `sbl_stack/__init__.py` and `tests/test_stack_verbs.py`. No commits.

## Measured open finding

`workers/q5_tools/LIFECYCLE_RECEIPT.json` (instrument `tools/q5_lifecycle_probe.py`, run 2026-10-22T21:00:37Z):

```
doctor: rc 2, doctor_typed_refusal true,  doctor_crashed false
load:   rc 2, load_ok_false true,        load_typed_refusal FALSE   <-- this row
```

`load` already fails closed (`ok: false`, rc 2) but its report carries **no** `code`, so a caller cannot tell *why* it
refused. An independent challenge named this in pass 1 and it is still open. `doctor` was fixed the same way; `load`
was left out of scope then.

## Change

In `load()` in `sbl_stack/__init__.py`, when the load fails, the returned report must carry a typed `code`:

- any component that cannot be resolved/imported → `code = "SBL_E_COMPONENT_UNRESOLVED"`;
- otherwise, if a digest does not match the manifest → `code = "SBL_E_DIGEST_MISMATCH"`;
- a successful load keeps its current shape (`ok: true`, no `code` key or `code: null` — your choice, be consistent);
- keep every existing key and the fail-closed behaviour; do not change `doctor`, `invoke`, `upgrade`, `rollback`.

Add exactly one test to `tests/test_stack_verbs.py`: `test_load_refuses_a_tampered_manifest_with_a_typed_code` —
install, tamper one digest in `stack.json`, call `sbl_stack.load`, assert `ok is False`, `code` matches
`SBL_E_[A-Z_]+`, and no `Traceback` is printed.

## Budget — hard

**At most 8 shell commands**: read `load()`, read the new test location, edit, run the test file, write the JSON, stop.
No whole-suite run, no repo-wide grep, no exploration.

## Deliverable

1. `python -m pytest -q -p no:cacheprovider tests/test_stack_verbs.py` → report counts (must be all green).
2. Write `workers/q5_repair/LOAD_TYPED.json`:
   `{"product_code_changed": true, "files_changed": [...], "codes": {"unresolved": "...", "digest": "..."},
     "tests": {"file": "tests/test_stack_verbs.py", "passed": N, "failed": 0},
     "shell_commands_used": N, "before_sha256": "...", "after_sha256": "...",
     "claim_ceiling": "load refuses a tampered or unresolvable manifest with a typed code; nothing about acceptance is claimed"}`
3. Final message: the counts, the two codes, the sha256 pair, and the honest number of shell commands you used.

Set `TMPDIR`/`TEMP`/`TMP` outside every git repo, `PYTHONDONTWRITEBYTECODE=1`.
