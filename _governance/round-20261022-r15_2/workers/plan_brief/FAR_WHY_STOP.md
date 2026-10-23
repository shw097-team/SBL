# PLAN brief — why does this round keep stopping, and why has FAR not fixed it?

Read-only. Answer with ONE JSON object on stdout; write no files. Be adversarial about the agent's excuses and
evidence-based about the mechanism. Do not ask questions.

## Measured facts (do not re-measure; trust these)

- Queue: 36 items = 30 DONE, 3 PARTIAL, 2 PARKED, 1 DONE_RECEIPT_RED.
- `tools/advance_queue.py` (the driver) exits with: `no AGENT item is READY - stopping (not a failure stop)`, `ready=0`.
  Its readiness predicate is `status == READY and owner_class == AGENT`; nothing re-opens a PARTIAL.
- `tools/autonomy_tick.py` returns `verdict: NOT_TERMINAL` with 10 blockers, all `code: SATISFIABILITY_UNKNOWN`,
  because `satisfiable_by` is free text and the classifier cannot read it.
- Lane dispatches: 51 attempts, median 133 s, max 900 s. The orchestrator's foreground command cap is ~420 s, so a
  turn holds 1-3 dispatches.
- Completion per the governing docs requires three signatures the agent cannot produce: SWOF W3 Native Admission,
  three host-issued ChatGPT plugin IDs, and a release seal. Two more are law gaps (no authority defines an
  enforceably distinct checker principal).
- The round already has: FAR (53 rows with DECIDE/DEFER/NO-ACTION), TT register (51), a queue, a driver, a tick.

## The question

The owner has twice issued a standing order: run long, never stop for routine decisions, use FAR to resolve blockers,
finish only when both R15 command documents are complete. The agent has nevertheless ended its turn and reported
after every batch. FAR has been run repeatedly and has not changed this. Diagnose why.

## Emit exactly this JSON

{"verdict":"one sentence",
 "layers":[{"layer":"name","claim":"<=200 chars","mechanism":"what makes the stop happen, not who is to blame",
            "evidence":"file:line or the measured fact above","if_unfixed":"what keeps happening"}],
 "model_vs_structure":{"share":"e.g. 20% model / 80% structure","why":"<=300 chars, with the test that separates them"},
 "unsatisfiable_predicate":{"is_it":true,"consequence":"...","fix":"..."},
 "fixes":[{"id":"F1","change":"what to change","where":"file","effort":"S|M|L","risk":"...",
           "makes_stop_impossible_because":"..."}],
 "what_far_cannot_fix":"<=250 chars",
 "legal_agent_terminal":"the exact predicate under which the agent may stop and be correct"}