NONCE: VER-B3C_TESTS-143830

Begin your reply with the token above on its own line, followed immediately by ONE sentence in your own words
naming the exact file you will change and what behaviour you will pin down.
Do NOT produce the token with a shell command, an echo, a heredoc or by printing the brief back: it must be
part of your reply text, because a script replaying the brief is not an acknowledgement.

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent
(no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that
in your output and stop.

# VERIFY brief — the four repaired tests only (answer fast)

Files (all under `C:/Projects/Agent_Workspace/HG-KSEOS/tests/`): test_c13_standing_scope_no_routine_hitl.py, test_c14_checkpoint_resume_no_repeat_effect.py,
test_c15_evolution_holdout.py, test_gstack_named_method_route.py.

Batch 2 rejected all four as PARTIALLY_VERIFIED. Since then: C13's aliasing test no longer deepcopies first and it
caught a real product defect (`lane_policy._compact_route` returned the registry's own fallback dicts; fixed with
copy.deepcopy, HG-KSEOS e8a94e1); C14 gained a real mid-restore case plus an xfail for the missing operation_id; C15
now rejects an empty holdout and xfails contamination detection; C10 adds a decision-is-not-authority test.
Current: 9 passed, 2 xfailed across the four files.

You have a HARD 200-second budget. Answer FIRST, investigate second, and never spend the budget reading whole
files: use grep to find the lines you need and read at most 60 lines per file. If you run out of time, emit the JSON
anyway with "coverage":"PARTIAL" and name what you did not check. Emit exactly one JSON object, nothing after it.

Cite the SBL knowledge base with `file#line` (root:
`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL`).

## Output
{"per_file":[{"file":"...","batch2_finding_answered":true,"earns":"TOUCHED|PARTIALLY_VERIFIED|VERIFIED","why":"...",
 "finding":"..."}],
 "xfail_hides_reachable_defect":[{"file":"...","line":0,"why":"..."}],
 "verdict":"PASS|FAIL","claim_ceiling":"...","coverage":"FULL|PARTIAL"}
