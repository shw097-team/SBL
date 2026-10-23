NONCE: EXEC-W08D-144156

Begin your reply with the token above on its own line, followed immediately by ONE sentence in your own words
naming the exact file you will change and what behaviour you will pin down.
Do NOT produce the token with a shell command, an echo, a heredoc or by printing the brief back: it must be
part of your reply text, because a script replaying the brief is not an acknowledgement.

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent
(no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that
in your output and stop.

# EXECUTE brief — the checker must not invent time (small, one file + one test file)

File to EDIT: `C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/tools/check_lane_consistency.py`
File to CREATE: `C:/Projects/Agent_Workspace/_r152_ev/tests/test_lane_consistency_time_sources.py`
Under 4 minutes. Do not touch anything else. The RETIRED_ARMS narrowing already in the file must stay.

## Three holes a checker reproduced in the current tool
1. `#372`-ish: when a receipt has no `generated_utc`, the reader falls back to the receipt FILE's mtime. An old file
   therefore buys SUPERSEDED with no receipt timestamp at all.
2. `#689`-ish: the declaration's mtime is used as the revision's effective time, so touching the pool file later excuses
   receipts issued after the policy actually changed.
3. Only the CURRENT pool is consulted: an arm authorised in revision A but barred in B is still excused when judged
   against a later revision C.

## The change
1. Receipt time: read ONLY from the receipt (`generated_utc`, then `useconds`/`generated_at` style fields if present).
   If none parses, the time is UNKNOWN. Never substitute the file mtime. UNKNOWN never buys SUPERSEDED.
2. Pool effective time: read from the pool's own revision record (`history[].at_utc`/`at` for the current `revision`,
   or a top-level `effective_at` if present). Fall back to the file mtime ONLY if a result records
   `pool_time_source: "file_mtime"` so the weakness is visible; when the source is file_mtime, a SUPERSEDED verdict must
   carry `superseded_confidence: "LOW"`.
3. Revision membership: accept an optional `prior_arms_by_revision` mapping {revision: [arms]}; SUPERSEDED requires the
   arm to be in the revision in force at receipt time. If that mapping is unavailable, keep RETIRED_ARMS as the floor and
   record `revision_membership: "UNAVAILABLE"` on every SUPERSEDED verdict.
4. Keep all existing keys and verdicts; do not weaken any current test.

## The tests (new file, four tests, no fixtures)
1. A receipt with no timestamp and an older file mtime is VIOLATION, not SUPERSEDED.
2. A receipt older than the pool's EFFECTIVE time (taken from the revision record, not the file) is SUPERSEDED when the
   arm is retired, and VIOLATION when it is not.
3. When the pool time came from the file mtime, the SUPERSEDED verdict records `superseded_confidence: LOW`.
4. With `prior_arms_by_revision` supplied, an arm authorised in A but absent in B is VIOLATION for a receipt issued
   during B.
