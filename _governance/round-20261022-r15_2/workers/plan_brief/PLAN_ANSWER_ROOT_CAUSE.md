I’ll read `ROOT_CAUSE.md` and check for applicable repository instructions.

---

The files distinguish premature stopping from legitimate authority waits. I’ll check whether the exhaustion proof covers all required work.

---

## 1. Ranked attribution

Ranked by explanatory power for the **remaining recurrence after the repairs**, not the original twelve stops.

| Rank | Layer | Mechanism and evidence |
|---|---|---|
| **1** | **Other: incomplete end-to-end governance protocol** | Continuity, authority, and completion are treated as one problem, but require different predicates. The queue proves exhaustion of its selected tasks—not coverage of every unfinished obligation. Its proof explicitly disclaims completion, while the denominator still contains implementation, measurement, and acceptance gaps. `QUEUE_EXHAUSTION_PROOF.json:3`; `DENOMINATOR_R15_2.json:326`; `DENOMINATOR_R15_2.json:435`. |
| **2** | **SBL** | Round-local continuation controls lack a demonstrated, denominator-complete contract connecting every obligation to an executable action or a genuine external dependency. W11 even records the standing grant as missing, despite the brief’s pre-authorization premise: conversational authorization has not demonstrably become a recognized governance artefact. `DENOMINATOR_R15_2.json:146`; `FAR_ROOT_CAUSE_AUTHORITY.md:19`. |
| **3** | **Fabric** | Principal-specific admissions and seals genuinely prevent agent-only completion; effort authorization does not confer another principal’s identity. This explains legitimate waiting, **not** abandonment or omitted agent work. Five requests name the required principals and satisfying actions. `PRINCIPAL_REQUESTS/INDEX.json:6`. |
| **4** | **HG-KSEOS** | `DELIVERY_READY` overstates its enforced predicate, allowing failed work orders beneath a reassuring state name. This confuses progress with readiness; the correction confirms that `DELIVERED` already guards failed orders. `DENOMINATOR_R15_2.json:210`. |
| **5** | **Hermes runtime** | Conversation-driven execution without a scheduler explains the original post-push stops. The queue now records a scheduler check, weakening “missing scheduler” as the explanation for the remaining authority boundary—but job existence alone does not establish sustained execution or receipt-triggered resumption. `FAR_ROOT_CAUSE_AUTHORITY.md:17`; `QUEUE_R15_2.json:292`. |
| **6** | **Model/session** | Re-deriving next actions from prose and choosing a report as the turn-ending action amplified premature stopping. Persistent commands reduce that failure mode; no supplied evidence shows that a different model could legitimately supply the missing admissions, host receipts, or independent acceptance. `FAR_STOP_LOOP_ROOT_CAUSE.md:24`; `FAR_ROOT_CAUSE_AUTHORITY.md:18`. |

## 2. Root cause

**The system lacks a demonstrated, complete protocol from standing mandate to governed completion.** Early FARs repaired execution liveness—remembering work, dispatching it, surviving failures, and scheduling continuation—whereas later barriers concern principal authority and unfinished product evidence. Repeated FAR cannot manufacture those inputs. However, “only owner signatures remain” is also too strong: five parked queue items do not establish that the entire denominator is externally blocked. Three declared kinds remain unimplemented, M2 lacks its isolated E2E/mutation evidence, and M4 lacks a measured semantic denominator; signatures cannot substitute for these. Principal requests are already issued, so issuing them again is not the next architectural repair. The missing guarantee is that **every unfinished obligation is represented, classified correctly, and connected either to executable work or to an authenticated external-response path**. See `DENOMINATOR_R15_2.json:326`, `DENOMINATOR_R15_2.json:435`, and `DENOMINATOR_R15_2.json:451`.

## 3. Single highest-leverage repair

**Promote the queue into a denominator-complete, authority-aware obligation ledger enforced by the control plane.**

Its mechanically checked waiting predicate should be:

```text
WAITING_FOR_PRINCIPAL iff
  every required denominator obligation is represented
  AND every unfinished obligation has a validated dependency path
  AND no legally executable agent action remains
  AND every dependency leaf is an issued request to an authorized principal
  AND receipt ingestion and automatic resumption are configured and tested
```

For each obligation, record the exact satisfaction predicate, permitted principal or scoped grant, dependency edges, executable next action, evidence verifier, and—when external—the request identity and response-validation/resumption rule. **Unknown classification must fail closed, not become OWNER by default.**

Keep completion separate: required evidence must verify, required orders must pass, semantic coverage must be measured, and admissions, independent acceptance, and release authorization must be valid. A request file is not acceptance; a lease heartbeat is not progress; `13 × 3` gates is not full semantic coverage.

This extends the existing exhaustion predicate rather than repeating it: `QUEUE_EXHAUSTION_PROOF.json:9` checks queue state, but does not establish denominator-wide coverage or response-driven resumption.

## 4. What would falsify this diagnosis?

- **A complete obligation mapping already exists**, with tested authenticated receipt ingestion and automatic resumption. That would falsify the proposed protocol gap.
- **Ready, authorized work is dispatched but execution repeatedly ends after a push.** That would move Hermes/model liveness back to the top.
- **A valid scoped grant already authorizes the disputed action**, yet the system still demands a fresh owner decision. That would indicate grant-recognition or enforcement failure, not missing authority.
- **All required external inputs arrive, yet no downstream work resumes.** Authority would no longer explain the stall; dispatch or dependency handling would.
- **All five requests are satisfied but M2, missing kinds, or semantic measurement remain unfinished.** That would directly falsify the narrower claim that “only owner signatures remain.”

Analysis only; no repository changes.