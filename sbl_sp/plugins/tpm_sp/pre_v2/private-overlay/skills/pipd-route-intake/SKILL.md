---
name: pipd-route-intake
description: Use when an unbound goal with source locators arrives at the intake gate
  and must be captured as a typed IntentCard with requirement atoms before any compilation
  begins.
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


## PRE-V2 active route (@2)

For current planning use `../../scripts/pre_v2.py` and
`../../references/contracts/pre-v2-routing.md`. Existing v1 schemas keep their
original `$id` and are compatibility replay inputs; their fixture receipts and
approval-shaped strings provide no live authority. Read original bytes and pin
the current original Reader. Missing original Reader means EXECUTOR_UNBOUND.
Produce design artifacts with AUTHOR_DESIGN_ONLY; receipt-free planning is legal.
Use only the original PIPD Writer for canonical PI/PD/ECP/TQAEP. Keep @2 sidecars
separate from canonical JSON and validate actual bodies, not just schema syntax.
Never turn a Sidecar, package seal or author test into a Grant, Qualified verdict,
Host qualification or release. Scope/Host/PolicyEpoch changes invalidate only the
affected binding. Reuse the owner's already-scoped authorization and known answers.
