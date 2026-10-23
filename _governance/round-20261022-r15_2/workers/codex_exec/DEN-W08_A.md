# EXECUTE brief — W08 step A of 2: teach the checker supersession (small, do only this)

Target: EDIT `C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/tools/check_lane_consistency.py`. Nothing else. No new test file in this dispatch - a second dispatch writes the tests.
Keep the run under 3 minutes: read the file, find the arm comparison, make the change, stop.

## Why
Against `C:/Projects/Agent_Workspace/HG-KSEOS/config/lane-route-slots.candidate.json` the checker reports 6 VIOLATIONs.
All six served `minimax-m3.1-flash-free` before the owner-ordered 2026-10-23 substitution to `deepseek-v4.1-flash`.
They matched the pool in force when they ran, so a rebind must not turn them red.

## Change
1. Add a pure function `classify_arm(served, pool_arms, receipt_time, pool_time)` -> one of
   "CONSISTENT" | "SUPERSEDED" | "VIOLATION":
   served in pool_arms -> CONSISTENT; not in pool and receipt_time < pool_time -> SUPERSEDED; otherwise VIOLATION.
   Accept timestamps as ISO strings or None; None means unknown, which is VIOLATION (never assume supersession).
2. Use it wherever the checker currently decides an arm mismatch. Keep every existing predicate name and its output.
3. Add "SUPERSEDED" to the counts dict and to the per-result verdicts; attach `superseded_by` naming the pool's rank-1 arm.
4. Exit non-zero only for real VIOLATION / NOT_GREEN. A SUPERSEDED receipt must not fail the run by itself, and must
   stay visible in the JSON.
5. Do not change how the pool is loaded or which file is passed in.
