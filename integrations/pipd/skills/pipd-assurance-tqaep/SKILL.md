---
name: pipd-assurance-tqaep
description: Use when a PI-PKG and ECP must be assured through a TQAEP with an independent checker, per-atom oracles and positive/negative fixtures.
version: 1
owner: PIPD/TQAEP semantics
triggers:
  - tqaep
  - assurance plan
  - independent checker
  - quality assurance plan
schemas:
  - schemas/input.schema.json
  - schemas/output.schema.json
references:
  - references/contract.md
  - references/examples.md
tests:
  - tests/cases.yaml
---

# pipd-assurance-tqaep

## Contract (imperative)

1. Require the PI-PKG (with trace links), the ECP, a maker identity and a distinct checker identity.
2. Refuse maker == checker (case- and whitespace-insensitive); the maker can never self-accept.
3. Refuse a missing or SELF_ATTESTED checker_execution_receipt; independence is evidenced, not asserted.
4. Refuse a PI without trace links; assurance without trace is not assurance.
5. Emit one test per requirement atom, each with an oracle, a positive fixture, a negative fixture and an evidence expectation.
6. Record acceptance as INDEPENDENT_CASE_PASS with both identities and the receipt; keep requalification affected-only.

## Boundaries

- **Owner:** PIPD/TQAEP semantics
- **Consumers:** Independent checker/release
- **Typed IO:** `schemas/input.schema.json` -> `schemas/output.schema.json`
- **Full contract:** `references/contract.md`
- **Worked examples:** `references/examples.md`
- **Cases:** `tests/cases.yaml` (POS / NEG / EDGE / SEC, each naming its expected first-fail)
