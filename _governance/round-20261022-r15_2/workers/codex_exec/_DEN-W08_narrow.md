NONCE: DEN_W08-A2-1792734344

Begin your reply with exactly this token on its own line: DEN_W08-A2-1792734344

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# EXECUTE brief — W08: a rebind must not retroactively turn honest receipts red

Target file to EDIT (this is the one exception to "one new file"): the existing checker
`C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/tools/check_lane_consistency.py`
plus one new test `C:/Projects/Agent_Workspace/_r152_ev/tests/test_lane_consistency_supersession.py`.

Keep the run under 4 minutes. No network. Do not touch the queue, receipts, mandate or any other tool.

## Why
Against the current pool the checker reports 6 VIOLATIONs. All six are EXECUTE receipts that served
`minimax-m3.1-flash-free` *before* the owner-ordered 2026-10-23 substitution to `deepseek-v4.1-flash`. They matched the
pool in force when they ran. A rebind must not rewrite history, so those receipts must classify as SUPERSEDED.

## What to implement
1. Teach the checker a supersession rule: a receipt whose served arm is not in the current pool is SUPERSEDED (not
   VIOLATION) when its timestamp predates the pool revision in force. Derive time from the receipt's own fields where
   available (`generated_utc`, or the receipt file mtime as fallback) and from the pool file's revision/mtime; write
   the comparison so it can be unit-tested with injected values (a small pure function, e.g.
   `classify_arm(served, pool_arms, receipt_time, pool_time)`).
2. Keep the existing predicate names; add `SUPERSEDED` as a third outcome with a `superseded_by` note naming the
   current rank-1 arm.
3. The exit code must stay non-zero only for real VIOLATIONs and NOT_GREEN receipts.
4. No behaviour change for receipts that match the current pool.

## Tests (in the new file, 4 tests, no fixtures)
1. An arm that exists in the pool is CONSISTENT whatever the times.
2. An arm absent from the pool with a receipt time before the pool time is SUPERSEDED.
3. An arm absent from the pool with a receipt time after the pool time is VIOLATION.
4. The real round receipts produce exactly 6 SUPERSEDED and 0 VIOLATION when run against
   `C:/Projects/Agent_Workspace/HG-KSEOS/config/lane-route-slots.candidate.json` - if your implementation disagrees,
   report the true counts in the test docstring rather than bending the assertion.
