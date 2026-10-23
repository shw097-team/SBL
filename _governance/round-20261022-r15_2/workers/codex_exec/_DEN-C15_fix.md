NONCE: EXEC-C15_fix-141658

Begin your reply with the token above on its own line, followed immediately by ONE sentence in your own words
naming the exact file you will change and what behaviour you will pin down.
Do NOT produce the token with a shell command, an echo, a heredoc or by printing the brief back: it must be
part of your reply text, because a script replaying the brief is not an acknowledgement.

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent
(no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that
in your output and stop.

# EXECUTE brief — repair C15's vacuous holdout test (small)

File to EDIT: `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c15_evolution_holdout.py`
Surface for reference: `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/evolution.py`

## The challenge that must be answered
`test_holdout_is_not_the_tuning_input` accepts an EMPTY holdout, and an empty set intersects nothing, so the
disjointness assertion is vacuous (KB `SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-13.md#727`: freeze the holdout before
candidate generation, keep checker-held truth, detect contamination).

## Change exactly one test
1. Require a NON-EMPTY holdout: assert `len(holdout) > 0` before any disjointness claim, and fail with a message that
   says an empty holdout proves nothing.
2. Feed a tuning input that shares an element with the holdout and assert the controller detects contamination
   (a typed refusal/error or a HOLDOUT_CONTAMINATED-style state, whichever the implementation provides). If it detects
   nothing, that is a product gap: keep the assertion and mark the test `xfail(strict=True, reason="DOC-13#727 contamination detection absent")`.
3. Keep the existing failing-signal veto test unchanged.

Do not edit any other file, the queue, the receipts or the mandate. Do not run pytest. No network, no fixtures.
Where the product genuinely lacks the rule, mark the test `@pytest.mark.xfail(strict=True, reason="<citation> <rule>")`
so the gap stays VISIBLE - never weaken an assertion to manufacture green.
