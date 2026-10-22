# EXECUTE brief — apply the verified eight-kind routing candidate to the product, with tests

You are the bounded writer. You may edit only:
- `sbl_core/m03_routing.py`
- `tests/test_kind_matrix.py` (may be created; if `workers/candidate_proposals/w06_kinds2/test_kind_matrix.py`
  already exists, copy it in and adjust imports only)

No other file. No commits. No lane dispatch. No sub-agents.

## Input

`workers/candidate_proposals/w06_kinds2/proposal.diff` (already `git apply --check` rc=0 against this tree) and
`workers/candidate_proposals/w06_kinds2/m03_routing.candidate.py`, plus `kind_matrix.json` (the eight canonical
kinds with dispositions: `CLI_TOOL` and `AGENT_SKILL` SUPPORTED; `SIMPLE_AGENT`, `PLUGIN`, `PROFILE` DEFERRED;
`AGENT_OS`, `AI_SYSTEM`, `GENIE/GENIE.md` UNSUPPORTED).

## Steps

1. `git apply --check` the diff, then `git apply` it. Record both exit codes.
2. If the diff does not apply cleanly (whitespace drift), apply the candidate file's semantics by hand to
   `sbl_core/m03_routing.py` and say so in RESULT.json — never leave the module half-edited.
3. Run:
   `python -m pytest -q -p no:cacheprovider tests/test_kind_matrix.py` → must be green.
4. Run the full suite: `python -m pytest -q -p no:cacheprovider tests` → must stay green
   (baseline 227 passed / 4 skipped; if the count changes because you added tests, report the new exact count).
5. Negative control: assert that a DEFERRED kind (`SIMPLE_AGENT`) and an UNSUPPORTED kind (`AGENT_OS`) both
   route to a refusal with a typed reason and **no** build target. If the module has no such refusal path,
   that is a finding — record it, do not invent an API.
6. Write `workers/candidate_proposals/w06_kinds2/APPLIED.json`:
   `{"apply_rc": 0, "method": "git apply|manual", "files": [...],
     "kind_tests": {"passed": N, "failed": 0}, "full_suite": {"passed": N, "failed": 0, "skipped": N},
     "negative_control": {"SIMPLE_AGENT": "refused|NOT_IMPLEMENTED", "AGENT_OS": "refused|NOT_IMPLEMENTED"},
     "before_sha256": "...", "after_sha256": "...",
     "claim_ceiling": "candidate applied on the evidence branch; not promoted, not accepted"}`
7. `git -C C:/Projects/Agent_Workspace/_r152_ev diff --stat` and paste it into RESULT.

## Rules

- If applying the candidate would break an existing test in a way you cannot fix inside the two allowed files,
  revert your edit (`git checkout -- sbl_core/m03_routing.py`) and write `"blocked"` + the failing test name.
- Do not touch `tests/` other than `test_kind_matrix.py`.
- Final message: apply rc, kind test counts, full suite counts, and the diff-stat line.
