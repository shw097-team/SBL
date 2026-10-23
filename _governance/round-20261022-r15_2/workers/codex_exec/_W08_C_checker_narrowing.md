NONCE: EXEC-W08C-143743

Begin your reply with the token above on its own line, followed immediately by ONE sentence in your own words
naming the exact file you will change and what behaviour you will pin down.
Do NOT produce the token with a shell command, an echo, a heredoc or by printing the brief back: it must be
part of your reply text, because a script replaying the brief is not an acknowledgement.

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent
(no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that
in your output and stop.

# EXECUTE brief — close the SUPERSEDED hole (small, one file + one test file)

File to EDIT: `C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/tools/check_lane_consistency.py`
File to CREATE: `C:/Projects/Agent_Workspace/_r152_ev/tests/test_lane_consistency_retired_arms.py`
Keep the run under 4 minutes. Do not touch anything else.

## The hole (a checker named it in one line: "supersession accepts an unauthorized model")
`classify_arm(served, pool_arms, receipt_time, pool_time)` returns SUPERSEDED for ANY arm absent from the current pool
whenever the receipt predates the pool. So an arm that was never declared by any revision - a hijacked model, a typo, a
hand-edited receipt - reads as "superseded" instead of "never authorized".

## The narrowing
1. Give `classify_arm` a fourth fact: `prior_arms` (iterable of arm labels that a PRIOR revision really declared).
   SUPERSEDED now requires BOTH: served not in `pool_arms`, served IS in `prior_arms`, and receipt_time < pool_time.
   Absent from both -> VIOLATION with a distinct reason string `UNAUTHORIZED_ARM` (keep the verdict VIOLATION).
   Unknown timestamps still VIOLATION, and an unknown arm with no `prior_arms` argument must never be SUPERSEDED.
2. Load `prior_arms` from `RETIRED_ARMS_R153.json` next to this tool (key `arms[].arm`), and pass it at every call site.
   The file already exists; read it, do not edit it.
3. Keep the existing counts keys; add `UNAUTHORIZED_ARM` as a sub-reason on the VIOLATION results (do not add a new
   top-level verdict).
4. The exit code must stay non-zero when any VIOLATION exists.

## The tests (new file, four tests, no fixtures)
1. An arm in the current pool is CONSISTENT.
2. An arm in `prior_arms` with an older receipt is SUPERSEDED.
3. An arm in neither list is VIOLATION, and its reason is UNAUTHORIZED_ARM - even with a very old receipt.
4. An arm in `prior_arms` but with an unknown receipt time is VIOLATION.
