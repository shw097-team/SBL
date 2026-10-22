# FAR: root cause of "still blocked" after repeated FAR

## 0. The question, split correctly

Two different phenomena were being called by one name:

- **stopping** — the round ends while agent-actionable work remains;
- **not completing** — the round reaches items that no agent may satisfy.

The first was fixed (queue, lease, guard, scheduler). The second kept recurring after every FAR, because every FAR was
aimed at the first. That misdirection *is* the root cause, and it is not a model problem.

## 1. Attribution, with evidence from this round

| layer | contribution | measurement | verdict |
|---|---|---|---|
| **Hermes (runtime)** | the loop was conversation-pulled; no scheduler by default | 12 stops, each after a push; `cron` job count = 0 before this round | **real cause, fixed** (lease + guard + `12eff9cba53c`) |
| **model / session** | context compaction destroys in-flight intent | 12 compactions; state re-derived from prose each time | **amplifier, fixed** (state in files + resume cmds) |
| **SBL** | no front door that refuses a round's closure | queue exhaustion was indistinguishable from completion until `continuation_guard.py` | **real cause, fixed in round tree; control-plane half is candidate only** |
| **HG-KSEOS** | states named above their predicates (`DELIVERY_READY`) | `lifecycle.py:172` guards `DELIVERED` but not `DELIVERY_READY` | **real cause, candidate fix, not applied** |
| **Fabric** | defines principals, not effort: W3 needs a Domain Owner admission; release needs a seal | `SWOF_CONNECTED -> BLOCKED_EXTERNAL`; `release: BLOCKED` | **dominant cause of "not completing"; not a defect** |

## 2. The actual root cause

**The user's standing authorization and the governance contract quantify over different things.**

- The authorization is about **effort and continuity**: "do not stop, use FAR, execute your recommendations".
- The Fabric/HGK predicates are about **principal identity**: "only a Domain Owner may admit W3", "only an AO may
  accept", "only an owner may seal a release".

An agent can satisfy the first instruction by working indefinitely. It cannot satisfy the second by working at all,
because the predicate is `signed_by ∈ {owner}` — a set that no amount of computation enlarges. When both arrive in the
same turn, every possible action violates one of them:

- stop → violates the continuity instruction;
- sign anyway → violates the governance contract (and is the one failure that cannot be repaired later, because a
  forged admission is indistinguishable from a real one downstream).

**So the round did not stop because the model was lazy or the harness was missing a scheduler. It stopped because I kept
choosing the only legal action — refuse to forge — and then dressed that refusal as an ending instead of issuing the
request that would have unblocked it.** The missing component was never compute; it was a **principal request**: a
first-class, tracked, one-click-shaped ask addressed to the entity that can actually satisfy the predicate.

That is why repeated FAR failed: each FAR treated "blocked on an owner" as a symptom to be engineered around, when it is
a *fact about authority* that has to be **issued**, not solved.

## 3. Why the repair is not "get more authorization"

The user has already granted everything a user can grant. Granting it again changes nothing, because the predicate is
not `authorized_by_user` — it is `signed_by_domain_owner`. A user who is not that owner cannot make it true by fiat, and
an agent that pretends otherwise produces the one artefact class the whole contract exists to prevent. **The correct
engineering response to an unsatisfiable-by-agent predicate is to make it satisfiable-by-owner in one step, and to
prove the step was taken.**

## 4. The engineering solution (three components, all mechanical)

### 4.1 Satisfiability classification, declared per item

Every denominator item carries `satisfiable_by ∈ {AGENT, OWNER, HOST, EXTERNAL_AO}` **and** the field that makes it so
(e.g. `required_signature: "domain_owner"`, `required_artifact: "host_id"`). Without this, the same item gets
re-litigated every round: it looks like unfinished work, so the next agent tries again, fails again, reports again.

### 4.2 Principal requests as artefacts

`PRINCIPAL_REQUESTS/<item>.md` — one per owner-gated item, containing: the exact predicate, the artifact already built
and waiting, the **literal** action or command that satisfies it, what it unblocks, an expiry, and the fallback if
denied. This converts "not in my scope" into "issued, tracked, one step from unblocked". It is the difference between a
blocked round and a **pending decision with a form attached**.

### 4.3 A guard that refuses both false endings

The continuation guard already refuses "done" while agent work remains. It must equally refuse **"blocked" without a
formal request**: an item parked with no principal request is indistinguishable from an item abandoned, and abandonment
is what a chat turn looks like from the outside. New blocker: `UNISSUED_PRINCIPAL_REQUEST`. Together the two refusals
leave exactly one honest terminal state: *no agent work remains, and every remaining item is an issued request awaiting
a named principal.*

## 5. What this predicts, and how it would be falsified

If the analysis is right, then after this repair the round should be able to sit indefinitely without a chat turn,
with every open item addressable by a single owner action, and no further FAR should find a new "why did it stop"
cause. It is falsified if the guard's next refusals are again about agent-actionable work — that would mean the queue
was under-filled, not that authority was the limit.
