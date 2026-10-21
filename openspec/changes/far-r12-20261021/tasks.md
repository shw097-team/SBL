# FAR r12 — tasks

Status legend: `[x]` done and read back · `[ ]` open, owner named · `[!]` blocked on an owner/native decision.

## Landed

- [x] Merge `candidate/r9-20261021-ctrlpkg` into `main` (PR #5, non-force, merge commit `31406ad7`).
      Verified: main is an ancestor of the head; 10 files, +3362/−0; CI ubuntu + windows success on the head SHA.
- [x] README claim section aligned with the two published releases and the three console scripts (D-01).
- [x] `docs/RUN_CONFORMANCE.md`: the runnable conformance command, its prerequisites, and the
      count-needs-tree-state rule (D-10).
- [x] FAR deviation study with per-item adjudication (D-01..D-16).

## Owner decisions requested

- [!] O-1 PLAN lane declaration vs owner mandate: either rebind epoch 30 or accept a per-round mandate chain.
- [!] O-2 grant an isolated writable scratch root to the checker (unblocks R9-02).
- [!] O-3 adopt the nine untracked HGK test modules under their authors' approval (or isolate them under `var/`).
- [!] O-4 plugin schema authority: pick the compliant packaging surface and record the exception to NOBJ-017.
- [!] O-5 record the GPTB KP R04 polarity conflict as a CR; do not edit the KP.

## HGK work orders required (not started)

- [ ] D-05/D-06/D-07 as ONE admitted work order: WorkOrder → ONE ECP → Permit → dispatcher → writer →
      isolated checker → readback, with the Commander-SP and Challenge-SP seams at pre-handoff/pre-spawn.
      Evidence required: `required_arm == served_arm` per lane, SP `invocation_id`, permit scope/lease/nonce,
      POS + NEG (revoked/expired/replay/foreign-scope), and a signed checker bundle.
- [ ] D-09 `_repo_head()` CWD defect: RED test (target ≠ CWD, exception propagation) → minimal patch →
      regression, inside the HGK repo under its own permit.

## Deferred with a trigger

- [ ] D-04 semantic denominator: only after D-05/D-06 are established; owner signs the total. Until then no percentage.
- [ ] D-13 441 / 149 / 38 per-item runtime: same trigger.
- [ ] D-12 three ChatGPT private plugins: trigger = host permission for the plugin creator scope.
- [ ] D-16 SWOF: trigger = native W3 ACK + permit; PREW3_SHADOW stays NO_EFFECT.

## Explicitly not done

- [ ] No branch deletions for the seven superseded candidates (they are ancestors of `main`; annotate, do not rewrite).
