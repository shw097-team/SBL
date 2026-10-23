NONCE: PLAN-R153-FIXSPEC-113355

Begin your reply with exactly this token on its own line: PLAN-R153-FIXSPEC-113355

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# PLAN brief — minimal complete fix for the stop-loop (design only, JSON out)

Read-only. Emit ONE JSON object on stdout. No file writes. The owner has pre-authorised whatever you rule, so
design for *implementation today*, not for a future programme. Reject anything that is not strictly needed.

## Established root causes (measured; do not re-derive)

L1 completion is unsatisfiable by the agent (SWOF W3, three host IDs, release seal, two checker-law gaps), while the
   standing order says never stop. There is no legal agent terminal, so every stop is either a violation or a lie.
L2 `advance_queue.py` selected only READY; PARTIAL / DONE_RECEIPT_RED were invisible for ever.
L3 `continuation_guard.py` accepted only 4 literal satisfiable_by values; prose -> SATISFIABILITY_UNKNOWN for ever.
L4 work is bound to a chat turn: 51 dispatches, median 133 s, foreground cap ~420 s, ~16 work units left.
L5 newly measured: the EXECUTE lane cannot run a test (its sandbox refuses process spawn), so every
   test-driven repair lands in the orchestrator session and trips the lane_bypassed blocker.

Already landed and verified today: satisfiability enum migration; driver re-arm gate on `rearm_ok` with attempt cap;
three separated claims (queue_exhausted / agent_scope_closed / full_completion) in the guard and its proof.

## What to design

1. The **legal terminal** the agent may stop on, expressed as a predicate over queue + requests, and named as a
   verdict the guard can emit (so stopping stops being a violation).
2. The **smallest mechanism that keeps work available between turns** — prefer one file plus one scheduler entry
   over a service. Say exactly what it runs, its lock, its budget, and what makes it exit.
3. The **smallest mechanism that stops items being hand-written each turn** (denominator -> queue), and how it stays
   idempotent and does not resurrect DONE items.
4. A **rule for the test-driven repair class** that satisfies maker/checker separation without a 350 s round trip per
   repair. State the exact discrimination: which writes must go to EXECUTE, which may be orchestrator, and what
   evidence each leaves.

## Output (exactly this JSON)

{"terminal_predicate":{"verdict":"name","predicate":"booleans over queue+requests","why_stop_becomes_legal":"..."},
 "items":[{"id":"A1","file":"tools/x.py","what":"<=160 chars","lines_of_code":"S|M","test":"the one test that proves it",
           "risk":"...","needed_because":"which L it closes","reject_if":"..."}],
 "repair_class_rule":{"execute_required":"...","orchestrator_allowed":"...","evidence":"..."},
 "scheduler":{"how":"cron|loop|both","command":"...","lock":"...","budget":"...","exit_when":"..."},
 "what_not_to_build":["over-engineered things to refuse"],
 "definition_of_done":"the predicate under which the owner may be told the stop-loop is fixed"}