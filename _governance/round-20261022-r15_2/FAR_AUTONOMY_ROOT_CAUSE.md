# FAR, architecture level: continuation has no owner

The previous FAR found that the round's artefacts described state and carried no executable next action. That was
true, and fixing it produced a queue and a driver. It did not stop the round from stopping, because the queue is still
**pulled by the conversation**. This document is about that second layer.

## 1. Evidence

| observation | value | what it means |
|---|---|---|
| rounds that ended with work still READY | 12 | the loop's termination point was a *turn*, not a state |
| queue created at | stop #12 | the mechanism that prevents stopping was built after eleven stops |
| scheduled jobs that ran the driver | **0** | nothing outside the conversation could resume the round |
| parked items with an owner action | 0 before the FAR pack | a parked item had no next actor, so parking looked like ending |
| stop reason recorded in a governed object | **none** | no control-plane record distinguishes "done" from "out of turn" |

## 2. Root cause, stated architecturally

**Continuation is owned by the conversational turn.** Three components are missing, and each one is a component, not a
habit:

1. **No lease.** Nothing in SBL or HG-KSEOS records "this round is still in flight, with these remaining items, until
   this time". Without a lease there is no fact of the matter about whether the round is running or abandoned — so a
   turn boundary is indistinguishable from a completion.
2. **No close guard.** Any principal can declare a round finished. There is no predicate that must hold before a
   closure is even expressible: no requirement that the ready set is empty, that every parked item carries a typed
   reason and a named next actor, and that a terminal proof exists.
3. **No watchdog.** The driver exists but nothing invokes it except a human turn. A loop whose only scheduler is the
   thing it is supposed to outlive is not autonomous; it is manual with good bookkeeping.

The `DELIVERY_READY` finding this round is the same defect in miniature: the state name asserts readiness while the
predicate that would justify the name is not checked. **State names without predicates are how both systems lie.**

## 3. Repair

### 3.1 Runtime side (implemented here)

- `ROUND_LEASE.json` — `round_id`, `subject_sha`, `denominator_ref`, `ready_set_ref`, `driver_cmd`,
  `stop_conditions[4]`, `heartbeat_utc`, `ttl_minutes`, `terminal_proof`. Written by the driver on every step; its
  heartbeat is the evidence that the round is alive.
- `tools/heartbeat.py` — stamps the lease and records the queue digest, so a stale lease is detectable.
- `tools/continuation_guard.py` — the close predicate. A round may be declared terminal only when: no `AGENT` item is
  READY; every PARKED item has `parked_reason` **and** `owner_action`; and the lease heartbeat is fresh or a terminal
  proof exists. Otherwise it exits non-zero and prints the blocking ids. This is what makes "we are done" a claim that
  can fail.
- **A scheduled job** runs `advance_queue.py` + `continuation_guard.py` on an interval, so the loop advances with no
  conversation at all. This is the piece that actually changes the outcome.

### 3.2 Control-plane side (candidate diff, same shape as W15)

HG-KSEOS should own the lease, not the round tree: a `continuation_leases` table with
`(round_id, subject_sha, denominator_ref, heartbeat_utc, ttl_minutes, terminal_proof, closed_by)` plus a
`continuation-guard` refusal in `project advance` when a project claims a terminal state without a guard proof. A
candidate diff and its tests are produced; applying it is an HGK owner action, exactly like the `DELIVERY_READY` guard.

### 3.3 Why not "more resolve"

Instructions decay with context; a cron entry and a predicate do not. The test of this repair is not whether the round
runs longer in one turn — it is whether a *new* session, with no memory of this one, can resume the round from files
alone and be **refused** when it tries to close prematurely.
