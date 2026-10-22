NONCE: EXEC-R152-Q1B-NONCE-7D24F0B9

Begin your reply with exactly this token on its own line: EXEC-R152-Q1B-NONCE-7D24F0B9

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# EXECUTE brief Q1b: finish the kind matrix, minimum output only

Role: SBL-EXECUTE & Codex bounded writer (`opencode-go/deepseek-v4.1-flash`).
Write-set: **`workers/candidate_proposals/w06_kinds2/**` only.** Do not touch HG-KSEOS. No lane dispatch. No polling.

## Context

A previous run in this same directory already wrote `m03_routing.candidate.py` (173 lines, parses, covers all ten kind
names, contains DEFERRED/UNSUPPORTED). It ran out of time before writing anything else. **Do not rewrite that file** —
read it and build on it.

## Produce exactly four files, then stop

1. `kind_matrix.json` — one row per canonical kind: `{kind, disposition: SUPPORTED|DEFERRED|UNSUPPORTED, reason, code_ref}`.
   Value the dispositions from `m03_routing.candidate.py`, not from opinion.
2. `proposal.diff` — `git diff`-style unified patch from the round tree's `sbl_core/m03_routing.py` to
   `m03_routing.candidate.py` (use `git diff --no-index`, then rewrite the paths to `a/sbl_core/m03_routing.py` and
   `b/sbl_core/m03_routing.py`).
3. `test_kind_matrix.py` — pytest tests: every canonical kind has a disposition; a DEFERRED/UNSUPPORTED kind fails
   closed when routed; a SUPPORTED kind still routes as before.
4. `TEST_OUTPUT.txt` — the real output of running those tests.

Skip everything else: no analysis prose, no extra modules, no refactor of unrelated code.

## Hard rules

- Four files, then stop. If a step is impossible, write what you have and say so in one line.
- Begin your reply with the nonce, then at most 5 lines: files written, tests run, pass/fail counts, anything not done.
