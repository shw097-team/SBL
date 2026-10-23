NONCE: VER-B4c-151541

Begin your reply with the token above on its own line, followed immediately by ONE sentence in your own words
naming the exact file you will change and what behaviour you will pin down.
Do NOT produce the token with a shell command, an echo, a heredoc or by printing the brief back: it must be
part of your reply text, because a script replaying the brief is not an acknowledgement.

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent
(no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that
in your output and stop.

# VERIFY brief - R153-B4: what would it actually take to move each artefact off PARTIALLY_VERIFIED?

You judged C10, C13, C14, C15 PARTIALLY_VERIFIED in batch 2 and again in batch 3. Do not re-judge them. Answer one
question per artefact: **the smallest product change that would make the check verifiable at all**, with `file:line`
and the behaviour to assert.

## Inputs (read, then answer; you have about 150 seconds)
- `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/evolution.py` (C15 - holdout initialised empty, qualification uses
  caller booleans, near line 254 and 279)
- `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lane_policy.py` (C10 - is there any admission/permission resolver,
  or only routing? near the named-method surface)
- `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c15_evolution_holdout.py` and
  `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c10_named_method_route.py` if present
- `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/recovery.py` (C14 - checkpoint resume; is there any operation
  identity, or only step counters?)

## Output - JSON only, no prose outside it
```json
{"coverage":"FULL|PARTIAL",
 "items":[{"id":"C10|C13|C14|C15",
           "blocked_by":"PRODUCT_SURFACE_ABSENT|TEST_SHAPE_ONLY|SCOPE_MISMATCH",
           "minimal_change":"one sentence, file:line, the behaviour to assert",
           "verifiable_after":"what evidence would let you say VERIFIED",
           "if_not_worth_it":"why the check should be withdrawn instead"}]}
```
Rules: if a check cannot become verifiable without building a subsystem, say so and recommend withdrawal - a
withdrawn check is better than a permanent xfail. Do not praise anything. If you cannot read a file, say which.
