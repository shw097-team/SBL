# EXECUTE brief: Q1 — canonical kind routing matrix and explicit dispositions

Role: SBL-EXECUTE & Codex bounded writer (`opencode-go/deepseek-v4.1-flash`).
Write-set: **`workers/candidate_proposals/w06_kinds2/**` only.** Do not touch HG-KSEOS. Do not dispatch any lane.

## Task

1. Read `sbl_core/m03_routing.py` (`DEFAULT_POLICY`, 5 implemented kinds: `CLI_TOOL`, `BROWN_PATCH`, `SKILL`,
   `AGENT_OS`, `AI_SYSTEM`) and the canonical 8-kind list in the package docs under this round tree.
2. Reconcile the naming: the canonical kind is `AGENT_SKILL`; the code says `SKILL`. Decide by reading which name the
   rest of the code and tests use, and make the code consistent either way — do not leave two names for one kind.
3. For every canonical kind, emit a machine-readable disposition: `SUPPORTED` (runnable lifecycle today) or
   `DEFERRED` / `UNSUPPORTED` (with a one-line reason). A recognition entry is not a success claim.
4. Write `kind_matrix.json` (8 rows: kind, disposition, reason, code_ref) and `proposal.diff` — a unified diff against
   the round tree that implements steps 2–3.
5. Write `test_kind_matrix.py` with tests that assert: every canonical kind has a disposition; DEFERRED/UNSUPPORTED
   kinds cannot be dispatched (attempting to route them fails closed); SUPPORTED kinds still route as before.
6. Run your tests. Put the raw output in `TEST_OUTPUT.txt`.

## Hard rules

- Only files under `workers/candidate_proposals/w06_kinds2/`.
- No lane dispatch, no sub-agent, no polling loop.
- Do not claim closure: this is a candidate diff plus tests, nothing is applied.
- Begin your reply with the nonce, then a 5-line summary: files written, tests run, pass/fail counts, what you did NOT do.
