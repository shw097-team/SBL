NONCE: EXECUTE-R152-Q1APPLY-NONCE-dcadc8f1

Begin your reply with exactly this token on its own line: EXECUTE-R152-Q1APPLY-NONCE-dcadc8f1

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# EXECUTE brief — apply the verified eight-kind routing candidate (one file group, nothing else)

Bounded writer. Change only `sbl_core/m03_routing.py` and create `tests/test_kind_matrix.py`.
Do **not** run the full test suite (the orchestrator runs it after you). Do not commit, dispatch or spawn.

1. `git apply --check` then `git apply` `workers/candidate_proposals/w06_kinds2/proposal.diff`.
   Record both exit codes. If it does not apply cleanly, copy the semantics from
   `workers/candidate_proposals/w06_kinds2/m03_routing.candidate.py` by hand and say so.
2. `cp workers/candidate_proposals/w06_kinds2/test_kind_matrix.py tests/test_kind_matrix.py` (adjust imports only if
   needed), then run **only**:
   `python -m pytest -q -p no:cacheprovider tests/test_kind_matrix.py`
3. Assert the dispositions: `CLI_TOOL`/`AGENT_SKILL` SUPPORTED route to a build/skill target; `SIMPLE_AGENT`,
   `PLUGIN`, `PROFILE` DEFERRED; `AGENT_OS`, `AI_SYSTEM`, `GENIE/GENIE.md` UNSUPPORTED and produce **no** target.
   If a DEFERRED/UNSUPPORTED kind produces a target, that is a finding: record it, do not invent an API.
4. Write `workers/candidate_proposals/w06_kinds2/APPLIED.json`:
   `{"apply_rc":0,"method":"git apply|manual","kind_tests":{"passed":N,"failed":0},
     "dispositions":{"SUPPORTED":[...],"DEFERRED":[...],"UNSUPPORTED":[...]},
     "no_target_for_deferred_or_unsupported": true, "before_sha256":"...","after_sha256":"...",
     "claim_ceiling":"candidate applied on the evidence branch; not promoted, not accepted"}`
5. Stop there. Final message: apply rc, kind test counts, the three disposition lists, and the sha256 pair.

If a single step fails, stop at that step, write the error into APPLIED.json under `"blocked"`, and say which line.
