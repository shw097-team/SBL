# EXECUTE brief — `sbl-stack doctor` must refuse a tampered manifest with a typed code (green receipt, narrow)

Bounded writer. Change only `sbl_stack/__init__.py` and `tests/test_stack_verbs.py`. Nothing else; no commits.

## Why

An earlier EXECUTE lane produced this repair, but its receipt is **RED** (900 s timeout, no nonce), so an independent
challenge refused to count it: a product change with a red receipt is not mandate-compliant completion. This is the
same change, re-earned with a receipt that names it.

## Required behaviour

When a stack directory carries a `stack.json` whose component manifest has been tampered with (an entry edited so its
recorded digest no longer matches the installed bytes, or an entry removed), `python -m sbl_stack.cli doctor --root
<root>` must

- exit non-zero,
- print JSON with `"ok": false` and a **typed** problem code from the `SBL_E_*` family (the current repair emits
  `SBL_E_COMPONENT_UNRESOLVED`),
- and must **not** raise an unhandled exception (`Traceback` must not appear).

A crash is not a refusal. `load` may keep its current behaviour; do not expand scope to it.

## Hard budget (this is the third attempt; two lanes burned their caps exploring)

**At most 8 shell commands. No repository exploration, no reading of unrelated files, no test discovery.** Run the
four steps below in order, then write the JSON and stop. If a step's output is not what you expect, record that fact in
the JSON instead of investigating: an honest "unexpected" is worth more than a green number.

Step 1 (one command): `python -m sbl_stack.cli install --root "$TMP/q5d/stack"` — capture rc.
Step 2 (one command, python inline): edit exactly one `sha256` field inside `"$TMP/q5d/stack/stack.json"` and print the
old and new value.
Step 3 (one command): `python -m sbl_stack.cli doctor --root "$TMP/q5d/stack"` — capture rc, stdout, stderr.
Step 4 (one command): `python -m pytest -q -p no:cacheprovider tests/test_stack_verbs.py` — capture counts.
Then: write `workers/q5_repair/DOCTOR_REPAIR.json` and finish.

## Steps

1. Confirm the current behaviour and record it:
   `python -m sbl_stack.cli install --root "$TMP/q5d/stack"` then tamper one digest inside `stack.json`, then
   `python -m sbl_stack.cli doctor --root "$TMP/q5d/stack"` — capture rc, stdout, stderr.
2. If the typed refusal is already correct, **do not touch the product code**; say so and go to step 4.
   If it is missing or it crashes, make the minimal change in `sbl_stack/__init__.py` so the tampered case returns the
   typed code, and add exactly one test to `tests/test_stack_verbs.py` asserting rc != 0, a code matching
   `SBL_E_[A-Z_]+`, and no `Traceback` in the output.
3. Run only `python -m pytest -q -p no:cacheprovider tests/test_stack_verbs.py` — record the counts.
4. Write `workers/q5_repair/DOCTOR_REPAIR.json`:
   `{"product_code_changed": true|false, "typed_code": "SBL_E_...", "doctor_rc": N, "traceback_present": false,
     "tests": {"file": "tests/test_stack_verbs.py", "passed": N, "failed": 0},
     "before_sha256": "...", "after_sha256": "...",
     "claim_ceiling": "doctor refuses a tampered manifest with a typed code; nothing about release or installation is claimed"}`

Set `TMPDIR`/`TEMP`/`TMP` **outside every git repo** for child processes, and `PYTHONDONTWRITEBYTECODE=1`.

Final message: whether you changed the product code, the typed code observed, the doctor rc, the test counts, and the
sha256 pair.
