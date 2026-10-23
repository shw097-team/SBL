NONCE: EXEC-C13_fix-141258

Begin your reply with the token above on its own line, followed immediately by ONE sentence in your own words
naming the exact file you will change and what behaviour you will pin down.
Do NOT produce the token with a shell command, an echo, a heredoc or by printing the brief back: it must be
part of your reply text, because a script replaying the brief is not an acknowledgement.

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent
(no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that
in your output and stop.

# EXECUTE brief — repair C13's one unsound test (small)

File to EDIT: `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c13_standing_scope_no_routine_hitl.py`
Surface for reference: `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lane_policy.py`

## The challenge that must be answered
`test_standing_scope_is_stable_across_repeated_resolution` (around lines 248-255) deepcopies the projection BEFORE
mutating it, so an implementation that returns aliases into its registry still passes. That is not a test of the
defensive-copy boundary.

## Change exactly one test
Rewrite it so aliasing is actually detectable:
1. Take two independent projections of the same role, `a = project(...)` and `b = project(...)`, without any deepcopy
   in the test.
2. Snapshot `b` (a plain dict/set copy of its permissions is fine - this is the expected value, not a mutation target).
3. Mutate `a` destructively (clear or add to its permission container).
4. Assert `b` still equals the snapshot AND a THIRD fresh projection equals the snapshot too.
5. If the implementation does return aliases, this test fails - that is the point; report it in the docstring rather
   than reverting.

Also add ONE test that pins the gap the checker named: per-effect Native admission checks (citation
`SBL_HGK_FABRIC_PIPD_LS_PKG_R15_1_FULL_SUBSTANTIVE_INTEGRATED_REPAIR_REPLACEMENT_2026-10-22.md#1400`: subject hash,
repository, path, action class, risk, expiry, token nonce, lease, current policy). Write it as `xfail(strict=True)` with
that citation if the product exposes no such per-effect check - which it does not today.

Do not edit any other file, the queue, the receipts or the mandate. Do not run pytest. No network, no fixtures.
Where the product genuinely lacks the rule, mark the test `@pytest.mark.xfail(strict=True, reason="<citation> <rule>")`
so the gap stays VISIBLE - never weaken an assertion to manufacture green.
