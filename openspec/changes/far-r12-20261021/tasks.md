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

- [x] O-1 PLAN lane declaration vs owner mandate — DECIDED 2026-10-23 (`DEC-R12-D11-O1-20261023`):
      rebind-on-order is the standing rule for binding changes (already executed as registry epochs
      30/31/32 under WO discipline on 2026-10-22); the per-round mandate chain stays as the
      assertion/evidence layer (`required_arm == served_arm` receipts), not a substitute for the
      declaration. Residual D-11b: rev-32 `sod.*` narrative prose is stale and pinned by projection
      `expected` values — one issuer commit must move prose + pins together.
      Record: `_governance/round-20261021-r12-far/D11_O1_LANE_DECLARATION_DECISION.md`.
- [x] O-2 GRANTED 2026-10-23 (`DEC-R12-D07-O2-20261023`): checker-only scratch round root, candidate
      read-only, subject frozen at origin/main@dc5428f2 (225 files, rollup eb5325d4…), 24h expiry,
      digest guard discriminates. Full SBL suite 218 passed / 2 skipped / 0 failed inside the granted
      scratch; control-package pin CONTROL_PACKAGE_PINNED; subject tree unchanged. R9-02 acceptance
      round itself still OPEN. Record: `_governance/round-20261021-r12-far/O2_D07_CHECKER_SCRATCH_GRANT.md`.
- [x] O-3 untracked test adoption (D-08): ADOPTED 2026-10-23 under the FAR R12 owner decision — all
      9 modules tracked (first tracking commits `7d9b64b`/`9fa79dd`), `.bak` quarantined to
      `var/quarantine/bak-20261022/tests/`, modified test preserved unreviewed at `db68ee4`. R9-05
      clean-checkout parity stays PARTIAL (no percentage, D-04 ceiling). Record:
      HG-KSEOS `docs/ADOPTION-D08-O3-UNTRACKED-TESTS-20261023.md` @ `f380719`, mirrored at
      `_governance/round-20261021-r12-far/O3_D08_ADOPTION_RECORD.md`.
- [x] O-4 plugin schema authority: chosen surface = ChatGPT private GPT (GA, DOC-12 C36.3);
      NOBJ-017 (Agent Plugins 1.0 WD) stays PROHIBITED; C-016..C-018 remain HOST_PENDING.
      See CR-PLUGIN-SCHEMA-AUTHORITY + `_governance/round-20261021-r12-far/O4_NOBJ017_EXCEPTION_RECORD.md`.
- [x] O-5 KP-R04 polarity (D-15): ACKNOWLEDGED 2026-10-23 via CR-GPTB-KP-R04-POLARITY — recorded,
      0 DOC/KP source files modified; 20/20 R04 rows stay quarantined `POLARITY_UNVERIFIED`, DOC is
      the upper authority; KP corpus + `19_KP_INDEX_CROSSWALK` row deferred to Knowledge Owner
      (7 byte-identical corpus copies, canonical not designated). Record:
      `_governance/round-20261021-r12-far/CR-GPTB-KP-R04-POLARITY.md` (origin
      `evidence/r12-20261021-far@72ee999`, mirrored here byte-identical).

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
