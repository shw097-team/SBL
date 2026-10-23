NONCE: EXEC-W08B-140843

Begin your reply with the token above on its own line, followed immediately by ONE sentence in your own words
naming the exact file you will change and what behaviour you will pin down.
Do NOT produce the token with a shell command, an echo, a heredoc or by printing the brief back: it must be
part of your reply text, because a script replaying the brief is not an acknowledgement.

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent
(no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that
in your output and stop.

# EXECUTE brief — W08 step B of 2: the tests for classify_arm (small, do only this)

Target: create ONE new file `C:/Projects/Agent_Workspace/_r152_ev/tests/test_lane_consistency_supersession.py`. Do not edit the checker.
Keep the run under 3 minutes: 4 tests, no fixtures, no network, no temp files outside tmp_path.

The checker at `C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/tools/check_lane_consistency.py` now exposes `classify_arm(served, pool_arms, receipt_time, pool_time)` returning
"CONSISTENT" | "SUPERSEDED" | "VIOLATION". Import it with importlib from that exact path.

## Four tests
1. A served arm present in the pool is CONSISTENT regardless of the times.
2. An arm absent from the pool with receipt_time before pool_time is SUPERSEDED.
3. An arm absent from the pool with receipt_time after pool_time is VIOLATION.
4. An unknown (None) receipt time is VIOLATION, never SUPERSEDED.
