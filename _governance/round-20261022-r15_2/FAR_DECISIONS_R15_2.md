# FAR decisions for the five parked queue items

Every parked item has an owner class, a recommendation, the exact one-line action the owner can take, and what the
agent will do the moment that action lands. Nothing here is signed by the agent.

---

## W02 — Fabric active policy disposition (`OWNER_DECISION`)

**Observed.** The round consumes Fabric as `FABRIC_CURRENT_ACTIVE_VIA_HGK_CONSUMER`, but no artefact names *which*
policy version is active, and `TT-R15.2-FRONTDOOR-SANCTIONED-DRIFT` shows the front door disagreeing with the declaring
config (`10100` hard-codes `deepseek-v4.1-flash`; `config/hermes-codex-lane.json` declares `minimax-m3.1-flash-free`).

**Root cause.** Two configs claim authority over the same decision, and neither is marked active. The disagreement is
structural, not a typo: a front door with a hard-coded model cannot follow a config that is meant to change.

**Recommendation (cheapest correct fix).** Declare the active policy digest in one place (`config/active-policy.json`
with `policy_digest`, `declared_by`, `declared_at`) and make the front door *read* it instead of hard-coding a model.
Until that exists, the sanctioned drift is the honest state.

**Owner action (one line).** Name the active policy digest, or authorise the agent to treat `hermes-codex-lane.json` as
active and retire the hard-coded front door.

**Agent on landing.** Bind the digest, re-run doctor, and re-measure the front door's declared-vs-served model.

---

## W12 — SWOF W3 admission (`OWNER_DECISION`)

**Observed.** `SWOF_CONNECTED` exists in `MODES` with disposition `BLOCKED_EXTERNAL`; `E08`/`E09` (first real SWOF) are
NOT_RUN. Execution is limited to `STANDALONE` and `PREW3_SHADOW`.

**Root cause.** The product already models the three modes and the blocked disposition correctly. What is missing is an
external Domain Owner issuing a Native Admission for W3 — an authority an agent cannot substitute for without turning
a governance gate into a formality.

**Recommendation.** Keep `SWOF_CONNECTED` blocked. Prepare the connected-mode dry run against a stub so that W3 is a
configuration change on the day the admission lands, not a build.

**Owner action.** Issue the W3 Domain Owner Native Admission, or authorise a shadow-only connected dry run.

**Agent on landing.** Run the connected mode against the admission, capture the external receipt, and re-measure E08/E09.

---

## W13 — five tools / three ZIPs / three private hosts (`HOST_PENDING`)

**Observed.** `GSTACK_ABSENT` (23 probes); no host-issued IDs; no private-plugin schema in hand. E06 is NOT_RUN.

**Root cause.** Three of the artefacts this work package needs can only be produced *by* the host that will consume
them: tool IDs, reproducible ZIP install receipts, and private-host load receipts. An agent can build the tool, but it
cannot be the host that accepts it.

**Recommendation.** Split the work package: the agent builds the five tools locally and proves reproducibility by
building each ZIP twice and comparing digests; only the host-load step stays `HOST_PENDING`. That converts "not started"
into "built, awaiting load", which is a materially different state.

**Owner action.** Provide host IDs (or delegate to the host owner) and the private-plugin schema, or accept the local-build-with-double-digest
evidence as the interim ceiling.

**Agent on landing.** Load into each host, capture the load receipts, re-measure E06/C22.

---

## W15 — release control bundle (`OWNER_DECISION`)

**Observed.** `release: BLOCKED`; the control plane reaches `DELIVERY_READY` but the round refuses `DELIVERED`
(`TT-R15.2-DELIVERY-GATE-IGNORES-FAILED` — the gate does not block on FAILED work orders).

**Root cause.** The release needs two owner-side artefacts: a seal and a host-load receipt. Separately, HG-KSEOS's
delivery transition ignores FAILED work orders, so "DELIVERY_READY" is not evidence of readiness. Both facts point the
same way: the transition is a status flip, not a gate.

**Recommendation.** Do not fix the gate by refusing to advance — fix it by making the transition *require* a
zero-FAILED predicate. That is a control-plane change (HG-KSEOS), and it is the highest-value defect in this list
because every future round inherits it.

**Owner action.** Approve the HG-KSEOS change (delivery gate must reject any FAILED work order) and issue the release
seal separately.

**Agent on landing.** Re-run the closing cycle and expect the transition to refuse while a FAILED order exists.

---

## W16 — B0/B1/B2 performance baselines (`OWNER_DECISION`)

**Observed.** No baseline artefact exists; `E0x` performance rows are NOT_RUN.

**Root cause.** A baseline needs an owner-chosen reference workload and an owner-accepted threshold. An agent that
invents both is setting its own exam.

**Recommendation.** Measure first, threshold later: publish B0/B1/B2 as *observed* numbers with the workload and host
described, explicitly unratified. That is useful immediately and cannot be mistaken for an accepted baseline.

**Owner action.** Name the reference workload and accept or reject the observed thresholds.

**Agent on landing.** Measure against the accepted workload, publish deltas, and re-measure C16.

---

## Cross-cutting

Three of the five blocker classes are the same shape: **the agent can produce the artefact but not the authority that
accepts it.** The repair is not more effort — it is splitting each work package into a buildable part and an acceptance
part, and reporting them separately. That split is what turns `NOT_RUN` into `BUILT_AWAITING_ACCEPTANCE`, which is a
true statement, instead of `NOT_RUN`, which reads as "did nothing".
