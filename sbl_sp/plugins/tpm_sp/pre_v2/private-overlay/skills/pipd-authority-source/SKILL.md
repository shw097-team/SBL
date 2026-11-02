---
name: pipd-authority-source
description: Use when source families must be frozen into a SourceFreezeManifest with
  AuthorityBinding records before any compiler reads them.
version: 1
owner: PIPD
triggers:
- freeze the authority
- authority binding
- source freeze
- bind the source family
schemas:
- schemas/input.schema.json
- schemas/output.schema.json
references:
- references/contract.md
- references/examples.md
tests:
- tests/cases.yaml
---

# pipd-authority-source

## Contract (imperative)

1. Require every source family to carry a sha256 manifest digest and at least one file locator.
2. Refuse a family with a missing or non-sha256 digest, an empty file list, or an unresolved locator.
3. Reject any locator that traverses out of the admitted root.
4. Rank families deterministically: F1/F2/F3/F5/F6 are R1 authority, the rest R2.
5. Emit one AuthorityBinding per family plus a SourceFreezeManifest over their digests.
6. Refuse to proceed on conflict: conflict_state stays NONE and supersession CURRENT or the freeze is refused.

## Boundaries

- **Owner:** PIPD
- **Consumers:** all compilers/adapters
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
