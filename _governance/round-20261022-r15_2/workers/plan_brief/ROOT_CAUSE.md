# PLAN brief: root cause of "still blocked" after repeated FAR

You are the PLAN lane (SBL-Commander & PLAN). Answer one question with reasoning and, where possible, evidence from the
files listed below. Do not write to the repository; return analysis only.

## Question

A governed round was given a standing, pre-authorized long-task mandate: "do not stop, use FAR on every blocker, and
execute your own FAR recommendations". It was FAR-reviewed seven times and repaired four times (queue with executable
resume commands, a driver that parks instead of stopping, a lease with heartbeat, a close predicate with non-zero exit,
a scheduler with no agent in the loop). It nevertheless keeps ending on the same sentence: *these items need an owner
signature, which an agent may not provide*.

Why does this keep happening? Is the root cause (a) the model, (b) SBL, (c) Fabric, (d) HG-KSEOS, (e) Hermes runtime,
or (f) something else? Give a ranked attribution with the mechanism for each, then the single highest-leverage
architectural repair.

## Measured facts you may rely on

- 12 stops, every one immediately after a `git push`; 0 scheduler jobs existed before this round.
- Queue: 20 items, 15 DONE, 5 PARKED, 0 ready. All 5 parked items now carry an issued principal request.
- HG-KSEOS `lifecycle.py:172` refuses the `DELIVERED` transition while required work orders are open or FAILED, but
  `DELIVERY_READY` has no such guard, so a project with 2 FAILED orders sits in a state whose name reads as "ready".
- `sbl_core/modes.py`: `MODES = ("STANDALONE", "PREW3_SHADOW", "SWOF_CONNECTED")`, disposition of `SWOF_CONNECTED` is
  `BLOCKED_EXTERNAL`; `GATE_IDS` = 13 ids, so "39 mode gates" = 13 x 3.
- `sbl_core/m03_routing.py` `DEFAULT_POLICY` implements 5 of a declared 8 kinds.
- R14 TS27 records `semantic_total_state: UNMEASURED` (20 units, 1,743 structural packets), so "DOC full semantics" has
  no denominator and M4 is unclaimable.
- Release is `BLOCKED`; `independent_acceptance` is `NOT_RUN`; the checker and maker share a host, so only lane-level
  separation exists.

## Files you may read (read-only)

- `FAR_STOP_LOOP_ROOT_CAUSE.md`, `FAR_ROOT_CAUSE_AUTHORITY.md`, `FAR_DECISIONS_R15_2.md`
- `QUEUE_R15_2.json`, `QUEUE_EXHAUSTION_PROOF.json`, `ROUND_LEASE.json`
- `PRINCIPAL_REQUESTS/INDEX.json`
- `DENOMINATOR_R15_2.json`

## Required output shape

1. Ranked attribution (model / SBL / Fabric / HGK / Hermes / other) with a one-line mechanism each and the evidence you
   used.
2. The root cause in one paragraph that would survive a reader who disagrees with the ranking.
3. The single highest-leverage repair, stated as an artefact or predicate that can be checked mechanically.
4. What would falsify your diagnosis.
