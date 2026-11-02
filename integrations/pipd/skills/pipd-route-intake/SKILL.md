---
name: pipd-route-intake
description: Use when an unbound goal with source locators arrives at the intake gate and must be captured as a typed IntentCard with requirement atoms before any compilation begins.
version: 1
owner: PIPD-EC (deterministic compiler)
triggers:
  - route the intake
  - intake request
  - intent card
  - capture the goal
schemas:
  - schemas/input.schema.json
  - schemas/output.schema.json
references:
  - references/contract.md
  - references/examples.md
tests:
  - tests/cases.yaml
---

# pipd-route-intake

## Contract (imperative)

1. Take the unbound goal and its source locators as the only accepted intake shape.
2. Refuse a blank goal and refuse an intake with zero source locators.
3. Reject any source locator that traverses out of the admitted root.
4. Derive one requirement atom per matched axis (intent, knowledge, verification, release, trust_boundary).
5. Emit a content-addressed IntentCard whose subject_id is derived from the intake body.
6. Hand the IntentCard to pipd-pi-compile; never compile directly from prose.

## Boundaries

- **Owner:** PIPD-EC (deterministic compiler)
- **Consumers:** pipd-authority-source, pipd-pi-compile
- **Typed IO:** `schemas/input.schema.json` -> `schemas/output.schema.json`
- **Full contract:** `references/contract.md`
- **Worked examples:** `references/examples.md`
- **Cases:** `tests/cases.yaml` (POS / NEG / EDGE / SEC, each naming its expected first-fail)
