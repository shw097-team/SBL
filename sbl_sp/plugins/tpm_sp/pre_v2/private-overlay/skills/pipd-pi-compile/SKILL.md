---
name: pipd-pi-compile
description: Use when a frozen IntentCard and an effective ProfileBinding must be
  compiled into a PI-PKG with a stable semantic contract and trace links.
version: 1
owner: PIPD
triggers:
- compile the pi
- pi package
- pi-pkg
- compile pi
schemas:
- schemas/input.schema.json
- schemas/output.schema.json
references:
- references/contract.md
- references/examples.md
tests:
- tests/cases.yaml
---

# pipd-pi-compile

## Contract (imperative)

1. Invoke the pinned original PIPD Compiler and rederive its PI from original source bytes; skills are not a second canonical Writer.
2. Keep each original RequirementID, Clause/SourceSHA/span, POS/NEG polarity, parent/child and original Oracle/FUO mapping in SBL.PI.Crosswalk@2.
3. Five taxonomy codes are advisory classifications and cannot replace original identities. Refuse empty PI, false source/oracle, subject mismatch or polarity alteration.
4. Validate the selected affected Scope. Preserve the 949/149/50/39/96/192/282 original denominators and per-ID applicability ledger; a bounded first useful result does not require all-product Native tests.

## Boundaries

- **Owner:** PIPD
- **Consumers:** PD binder
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
