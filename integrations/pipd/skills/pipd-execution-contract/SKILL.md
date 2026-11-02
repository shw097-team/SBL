---
name: pipd-execution-contract
description: Use when a bound PD-PKG must become a ConstructionContract plus an ECP that fixes effect, permission, retries, idempotency, readback and rollback.
version: 1
owner: PIPD (ConstructionContract) / PIPD-ECP semantics (ECP)
triggers:
  - execution contract
  - construction contract
  - compile the ecp
  - emit the ecp
schemas:
  - schemas/input.schema.json
  - schemas/output.schema.json
references:
  - references/contract.md
  - references/examples.md
tests:
  - tests/cases.yaml
---

# pipd-execution-contract

## Contract (imperative)

1. Require the bound PD-PKG reference and its PI-PKG reference.
2. Derive writable_scope from the PD late binding; refuse an empty scope and refuse '**' or escaping scopes.
3. State expected_changes, tests, rollback and evidence_expectations explicitly in the ConstructionContract.
4. Compile the ECP with effect_intent, token-required permission, at-most-once idempotency, residue-scan readback and a mandatory rollback pointer.
5. Fix retries at max 1 with backoff none; never silently retry a governed effect.
6. Refuse to emit an ECP whose permission lacks a token or whose rollback is not required.

## Boundaries

- **Owner:** PIPD (ConstructionContract) / PIPD-ECP semantics (ECP)
- **Consumers:** HGK adapter, TQAEP
- **Typed IO:** `schemas/input.schema.json` -> `schemas/output.schema.json`
- **Full contract:** `references/contract.md`
- **Worked examples:** `references/examples.md`
- **Cases:** `tests/cases.yaml` (POS / NEG / EDGE / SEC, each naming its expected first-fail)
