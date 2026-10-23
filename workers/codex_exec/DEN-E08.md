# EXECUTE brief — DEN-E08

You are the bounded writer on the EXECUTE lane. One artefact, one run, no sub-agents.

## Obligation
DEN-E08 (?). recipe_hint: shadow-only dry run per SWOF_SHADOW_AUTHORIZATION_R15_3.json; assert zero writes to the SWOF repo

## Write exactly this
`tests/test_den_e08.py`

- A pytest module. No fixture may write outside the repo; no `tmp_path` under a system temp root; no network.
- One behaviour per test, at most 8 tests. Each test asserts a real product rule, not that a function exists.
- Keep the module under ~200 lines so the run finishes inside the lane's 330 s cap.
- Do not edit any other file. Do not edit the queue, the mandate or the receipts.

## Acceptance commands (run them yourself before you finish)
```
cd C:/Projects/Agent_Workspace/_r152_ev
python -m pytest tests/test_den_e08.py -q
```
If a test cannot pass because the product lacks the rule, write the test to assert what the governing document
actually requires and mark it `xfail(strict=True, reason="<the missing rule>")` - never weaken an assertion to make
it green.

## Refuse
Claiming the check is done, writing a placeholder test, touching DONE items, or reporting acceptance.
