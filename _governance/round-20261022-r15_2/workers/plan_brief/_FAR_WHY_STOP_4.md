NONCE: PLAN-R153-STOP4-130347

Begin your reply with exactly this token on its own line: PLAN-R153-STOP4-130347

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# PLAN brief — it stopped again, with the supervisor alive. Why, and what is the smallest fix?

Read-only. One JSON object on stdout. Ground every ruling in the SBL KB and cite `file#line`:
`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL`
(SBL_PIPD-LS-PKG_DOC-00..13.md, 藍圖資料庫/, 參考工程資料庫/). If the KB does not speak to a question, say so.

## What is measured right now (not an opinion)

```
cron tick, every 15 min, no_agent:  advance_queue start ... max_steps=3
                                   no AGENT item is READY - stopping (not a failure stop)
                                   steps=0 done=33 parked=4 owner=4 host=1 ready=0
queue: DONE 33 | PARKED 4 | PARTIAL 3 | DONE_RECEIPT_RED 1 | NEEDS_RECIPE 12
READY items with a resume_cmd: 0
```

So the earlier fix worked and then re-broke in a new shape. Round 1 the driver starved on `PARTIAL` because its
selector accepted only `READY`; the fix admitted `READY` plus re-armable states. Round 2 the remaining work was
re-expressed as `NEEDS_RECIPE`, a state the selector still does not admit, and the twelve items are invisible again.
The supervisor runs, finds nothing it is allowed to execute, and exits cleanly. The agent then reports and the turn
ends. Nobody lied; the loop simply has no executable unit left.

## The questions

Q1 Is the recurring stop a model property, a scheduler property, or a queue-representation property? Separate the
   three with the evidence above, and name which one dominates. If the KB has a doctrine on work-item states or on
   who may hold a work item, cite it.
Q2 The twelve items are *authoring* work (write a test for kanban transitions, for swarm fan-in, for a checkpoint
   resume, ...). Authoring has no command in the queue, so the driver cannot run it. What is the smallest
   representation that makes authoring executable - one brief file plus a lane dispatch per item, or something
   simpler? Do not propose a service, a second queue, or an agent framework.
Q3 What must the selector accept, and what must it refuse, so that this class cannot silently reappear a third time?
   State the invariant, not the patch.
Q4 The EXECUTE lane hits a 330 s cap and often writes the big file but dies before its test, leaving a NOT_GREEN
   receipt over real work. What is the low-friction unit size and the right receipt semantics for that case?
Q5 Does the KB put any obligation on the round to keep a human-visible trail when work is driven unattended every
   15 minutes? Cite it or say the KB is silent.

## Output

{"q1":{"dominant_cause":"MODEL|SCHEDULER|REPRESENTATION","why":"...","citations":["path#line"]},
 "q2":{"unit":"...","files":["..."],"why_minimal":"...","reject":["..."]},
 "q3":{"selector_invariant":"...","must_accept":["..."],"must_refuse":["..."]},
 "q4":{"unit_size":"...","receipt_semantics":"..."},
 "q5":{"kb_says":"...","citations":["..."]},
 "implement_today":[{"n":1,"file":"...","what":"<=140 chars","test":"..."}],
 "claim_ceiling":"..."}