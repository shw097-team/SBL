---
name: pipd-package-project
description: Use when the artifact bundle must be closed into a ClaimCeiling with
  EvidenceExpectation records and a TraceClosureReport before handoff.
version: 1
owner: PIPD
triggers:
- package the project
- claim ceiling
- evidence expectation
- trace closure
schemas:
- schemas/input.schema.json
- schemas/output.schema.json
references:
- references/contract.md
- references/examples.md
tests:
- tests/cases.yaml
---

# pipd-package-project

## Contract (imperative)

1. Require nonempty canonical artifact bodies and a nonempty PlannedTQAEP with real POS/NEG pins.
2. Invoke the pinned original Reader and recompute the actual candidate digest and graph joins; counts or success-shaped caller JSON do not prove closure.
3. Missing graph provenance, original Reader or required Case leaves an affected HOLD. Preserve historical failing fixtures as counterexamples.
4. Seal at AUTHOR_DESIGN_ONLY with expected evidence explicitly EXPECTED_NOT_OBSERVED. Do not use an approval receipt string to raise the ceiling.
5. Hand off through original FABRIC policy, HGK Issuer/SharedSpine and SBL receiver; no new queue, Issuer, Checker or Publisher.

## Boundaries

- **Owner:** PIPD
- **Consumers:** all planes
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
