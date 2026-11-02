---
name: pipd-profile-tailor
description: Use when a requested profile and axis set must be resolved into an effective
  ProfileBinding through the safety veto before compilation.
version: 1
owner: PIPD
triggers:
- tailor the profile
- compute the profile
- profile binding
- select the axes
schemas:
- schemas/input.schema.json
- schemas/output.schema.json
references:
- references/contract.md
- references/examples.md
tests:
- tests/cases.yaml
---

# pipd-profile-tailor

## Contract (imperative)

1. Accept only the LITE / STANDARD / ASSURED profiles and the nine canonical axes.
2. Refuse unknown profiles, unknown axes, and duplicated axes.
3. Run the safety veto: it may only ESCALATE artifact depth, never reduce it.
4. Escalate LITE to STANDARD when provider-off parity is required, and any profile to ASSURED past its axis ceiling (LITE 3, STANDARD 6, ASSURED 10).
5. Emit a ProfileBinding with the effective profile, vetoes, artifact_depth and assurance set.
6. Keep one canonical truth across all three profiles; never fork truth per profile.

## Boundaries

- **Owner:** PIPD
- **Consumers:** Skills/JIT/HGK
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
