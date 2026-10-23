NONCE: PLAN-CMD-154014

Begin your reply with the token above on its own line, followed immediately by ONE sentence in your own words
naming the exact file you will change and what behaviour you will pin down.
Do NOT produce the token with a shell command, an echo, a heredoc or by printing the brief back: it must be
part of your reply text, because a script replaying the brief is not an acknowledgement.

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent
(no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that
in your output and stop.

# PLAN brief — COMMANDER DECISION: build or withdraw, per artefact (C10/C13/C14/C15)

You are the SBL Commander lane. The independent checker (same model family, different lane) refused to lift four
artefacts past PARTIALLY_VERIFIED and gave, for each, either a minimal product change or a withdrawal argument.
Your job is a decision, not a rewrite of their reasons.

## Inputs (read these; you have ~200 s)
- `C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/FAR_TRANSPORT_R153.json`
- the B4 answer, embedded below (verbatim)
- `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lane_policy.py` around line 197
- `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/recovery.py` around line 37

B4 FINDINGS (verbatim):
- C10 SCOPE_MISMATCH: add a fail-closed permission resolver at lane_policy.py:197 backed by authoritative declared scope;
  a routing assertion cannot authorize an effect. If not built: withdraw the authorization claim, keep routing-only.
- C13 PRODUCT_SURFACE_ABSENT: needs a per-effect Native admission boundary validating subject hash, repo, path, action
  class, risk, expiry, token nonce, lease against trusted standing authorization; the xfail at
  test_c13_standing_scope_no_routine_hitl.py:196 is signature-discovery, not a boundary test.
- C14 PRODUCT_SURFACE_ABSENT: bind restore attempts to operation_id + backup digest + target, reconcile readback;
  recovery.py has neither operation identity nor step counters.
- C15: holdout initialised empty in product; test installs it by SQL and xfails the whole test, absorbing unrelated
  assertion failures.

## The decision you must make
For each id: BUILD_NOW / BUILD_LATER / WITHDRAW, with (a) why, (b) the smallest implementable slice that fits one lane
dispatch of <=200 s, (c) what claim ceiling the round may state while that slice is missing. Prefer WITHDRAW over a
permanent xfail when the check cannot become verifiable without a subsystem this round does not own.

## Output — JSON only
```json
{"decisions":[{"id":"C10","verdict":"BUILD_NOW|BUILD_LATER|WITHDRAW",
  "why":"one sentence","slice":"file:line + behaviour, or null","claim_ceiling_until_then":"..."}],
 "round_ceiling_after":"one sentence",
 "answer_this":"does anything in the four justify keeping the round open past today? yes/no + one line"}
```
