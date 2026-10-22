# TS17 DOC-08-shaped runtime measurement

- 768 cells = 8 skills × 12 TestClasses × 8 OracleTypes.
- Local contract-oracle execution: **32 RUNTIME_QUALIFIED / 736 DECLARED_ONLY**; 32 isolated commands.
- Scope: DETERMINISTIC schema/semantic-contract checks only. **Full DOC-08 functional/native qualification: 0**. POS fixture output validation does not invoke a skill; NEG/SEC do not establish runtime-world state or egress. These limits are explicit in the JSON, not acceptance claims.
- The two schema-accepted negatives remain schema-accepted. Actual HGK semantic.distinct and semantic.claim_gate predicates are executed to refuse them; neither is a SEMANTIC_JUDGE.
- No state propagated to other OracleTypes, no invented fixtures or output generation, no ledger or PIPD edits. No independent checker/acceptance issued by this measurement.
- Repository commit: `f4646e8f04831b2996265d0d27d69c2af286d9d6`.
- Every cell, normative predicate and source rule is in `ts17_matrix_v2.json`; qualified cells carry exact command, cwd, exit, evidence path and SHA-256. Evidence files contain full stdout/stderr and raw expected/observed values.

## Unqualified OracleTypes

- STATE_READBACK: No skill/class-bound native pre/post state transition runner and digests executed; schema rejection is not state readback.
- PROPERTY: No skill/class-bound generated cases, invariant and seed runner executed; ordinary parametrization is not property coverage.
- REFERENCE_OUTPUT: No skill/class-bound pinned reference comparison executed; stored fixture outputs and hashes alone are not pinned_reference_eq.
- STATISTICAL: No skill/class-bound dataset/calibration/confidence/threshold benchmark executed.
- SEMANTIC_JUDGE: No skill/class-bound pinned judge, rubric and human calibration executed. semantic.distinct/claim_gate are deterministic predicates, not calibrated judges.
- HUMAN: No skill/class-bound signed human decision, rubric, principal and consent/basis executed/read back.
- COMPOSITE: No skill/class-bound ordered component oracle runner, failure policy and raw component receipts executed; checking input/output schemas together is not DOC-08 COMPOSITE.

## Per OracleType

| OracleType | RUNTIME_QUALIFIED | DECLARED_ONLY |
| --- | ---: | ---: |
| DETERMINISTIC | 32 | 64 |
| STATE_READBACK | 0 | 96 |
| PROPERTY | 0 | 96 |
| REFERENCE_OUTPUT | 0 | 96 |
| STATISTICAL | 0 | 96 |
| SEMANTIC_JUDGE | 0 | 96 |
| HUMAN | 0 | 96 |
| COMPOSITE | 0 | 96 |
