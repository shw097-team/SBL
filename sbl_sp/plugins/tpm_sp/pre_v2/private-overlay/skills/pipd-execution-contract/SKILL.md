---
name: pipd-execution-contract
description: Use when a bound PD-PKG must become a ConstructionContract plus an ECP
  that fixes effect, permission, retries, idempotency, readback and rollback.
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

1. Resolve the typed OperationType from the pinned original Effect Registry. Relative, absolute and UNC spelling never determines the effect.
2. Create SBL.ECP.INTENT@2 with exact Scope, Pre/Post, original Consumer/ABI, permission basis, idempotency and effect-specific World Readback/recovery.
3. READ uses source ACL/hash; DRAFT uses sandbox/diff/cleanup; DEV uses a live Repo probe, HEAD, exact pre/postimages and rollback commit.
4. OPS uses HostID/OS principal/receiver ABI and Host recovery, never a generic git revert. USER binds original consent/data scope/compensation. RELEASE names original Publisher, remote scope, approval reference and recovery.
5. UNKNOWN requires original-reader reconcile before any retry. An ECP intent never grants an effect. Missing registry/receiver means EFFECT_UNBOUND.
6. Keep the original compile-ecp output and @2 Sidecar separate. If the original generic Writer cannot express the effect, record ORIGINAL_ECP_EFFECT_HOLD rather than advertise executable readiness.

## Boundaries

- **Owner:** PIPD (ConstructionContract) / PIPD-ECP semantics (ECP)
- **Consumers:** HGK adapter, TQAEP
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
