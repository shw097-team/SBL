# EXECUTE brief — DEN-C08

You are the bounded writer on the EXECUTE lane. One artefact, one run, no sub-agents.

## Obligation
DEN-C08 (?). recipe_hint: author tests/test_kanban_transitions.py: Ready->Claim only by one claimant, a second claim refused with a typed code, lease expiry returns the card to Ready, heartbeat extends the lease once and refuses after expiry

## Write exactly this
`tests/test_den_c08.py`

- A pytest module. No fixture may write outside the repo; no `tmp_path` under a system temp root; no network.
- One behaviour per test, at most 8 tests. Each test asserts a real product rule, not that a function exists.
- Keep the module under ~200 lines so the run finishes inside the lane's 330 s cap.
- Do not edit any other file. Do not edit the queue, the mandate or the receipts.

## Acceptance commands (run them yourself before you finish)
```
cd C:/Projects/Agent_Workspace/_r152_ev
python -m pytest tests/test_den_c08.py -q
```
If a test cannot pass because the product lacks the rule, write the test to assert what the governing document
actually requires and mark it `xfail(strict=True, reason="<the missing rule>")` - never weaken an assertion to make
it green.

## Refuse
Claiming the check is done, writing a placeholder test, touching DONE items, or reporting acceptance.
