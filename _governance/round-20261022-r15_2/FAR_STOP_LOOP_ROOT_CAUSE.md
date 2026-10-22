# FAR: why the SBL × HG-KSEOS round keeps stopping

## 1. Observed stops

Twelve rounds ended immediately after a commit/push or after a measurement was written. In every case the work was
verifiable, the tree was clean, and nothing external was blocking *at that moment*. The stop was not caused by a
blocker; the blocker was found only after resuming.

## 2. Measurements that locate the cause

| measurement | value | what it rules out |
|---|---|---|
| TT entries | 20 | — |
| TT with a prose `next_legal_step` | 20 | the round does record intent |
| TT with an executable `resume_cmd` | **0** | intent is never machine-runnable |
| Denominator items | 56 (18 W + 25 C + 9 E + 4 M) | — |
| Denominator items with `next_action` | **0** | the register measures state, it cannot drive work |
| Kanban tasks | 18 | — |
| Kanban `task_runs` | 6 | the board was never used as a dispatch queue |
| Kanban cards still `blocked` with reason `initial_status` | 12 | blocked-by-default reads as "nothing to do" |

## 3. Root cause

**The round's artefacts describe state; none of them carries an executable next action.** At a turn boundary the agent
re-derives "what now" from prose, and prose does not survive context compression. So the loop terminates not because
the work is finished but because the *only available move* is to report.

This is a system defect, and it has three components:

1. **No executable queue.** Status registers, TT registers and the kanban board all answer "where are we"; none answers
   "what do I run next, with which command, and what proves it worked".
2. **Blocked reads as stopped.** 12 of 18 cards were blocked with `initial_status`, a state that carries no reason and
   no next action — so a reader cannot distinguish "waiting on an owner" from "not started".
3. **No retry ladder.** The first EXECUTE dispatch died at 300 s and the round reported instead of re-scoping the task.
   The same task later succeeded in 344 s once re-scoped; the failure was survivable and was treated as terminal.

## 4. Repair, chosen for leverage

**A queue whose items are commands, plus a driver that parks blockers and keeps going.**

- `QUEUE_R15_2.json`: every item carries `id`, `status`, `owner_class` (`AGENT` / `OWNER` / `HOST`), `next_action`,
  and for agent items a literal `resume_cmd` with a `expect` condition.
- `tools/advance_queue.py`: runs ready `AGENT` items one at a time, records the observed output, marks `DONE` on the
  expectation, and on failure **parks** the item with a typed reason and continues to the next one.
- Stop policy, now explicit and the only legal stops: destructive action, missing credential, mandated lane
  unavailable, or an owner-only decision. Everything else parks and the driver continues.

Design note: the driver deliberately does not try to be a scheduler. It is a resume pointer with a retry ladder; the
state it needs is a file, so it survives context compression, a new session, and a reboot.

## 5. Why this is better than "try harder"

A resolve-to-continue instruction fails exactly when context is compressed, which is when the work is longest. A queue
file plus a driver moves the memory from the conversation into the repository, so "continue" becomes a command rather
than a recollection. It is also auditable: the queue records what ran, what it printed, and what was parked.
