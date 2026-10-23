NONCE: DEN-C09-AUTHOR-00cfd812

Begin your reply with exactly this token on its own line: DEN-C09-AUTHOR-00cfd812

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# EXECUTE brief — DEN-C09

You are the bounded writer on the EXECUTE lane. One artefact, one run, no sub-agents.

## Obligation
DEN-C09 (?). recipe_hint: author a fan-in checker: N dispatched workers, assert len(returned)==N with per-worker receipt digests, and that a missing worker makes the fan-in verdict PARTIAL not PASS

## Write exactly this
`tests/test_den_c09.py`

- A pytest module. No fixture may write outside the repo; no `tmp_path` under a system temp root; no network.
- One behaviour per test, at most 8 tests. Each test asserts a real product rule, not that a function exists.
- Keep the module under ~200 lines so the run finishes inside the lane's 330 s cap.
- Do not edit any other file. Do not edit the queue, the mandate or the receipts.

## Acceptance commands (run them yourself before you finish)
```
cd C:/Projects/Agent_Workspace/_r152_ev
python -m pytest tests/test_den_c09.py -q
```
If a test cannot pass because the product lacks the rule, write the test to assert what the governing document
actually requires and mark it `xfail(strict=True, reason="<the missing rule>")` - never weaken an assertion to make
it green.

## Refuse
Claiming the check is done, writing a placeholder test, touching DONE items, or reporting acceptance.
