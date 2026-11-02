---
name: pipd-pd-bind
description: Use when a compiled PI-PKG must be late-bound to a real RepoContext into
  a PD-PKG before any construction is planned.
version: 1
owner: PIPD
triggers:
- bind the pd
- pd package
- repo context
- late-bind the pd
schemas:
- schemas/input.schema.json
- schemas/output.schema.json
references:
- references/contract.md
- references/examples.md
tests:
- tests/cases.yaml
---

# pipd-pd-bind

## Contract (imperative)

1. Obtain a real Git root/HEAD/branch, dirty+untracked state, process ACL, exact writable scope, timestamp and preimages through a live probe.
2. A missing Repo yields RepoBindingRequest/UNBOUND_CANDIDATE only. A plain directory is not a proven Git binding.
3. Caller --head is a claim. Compare the actual original PD context with a current probe and preserve original scope checks.
4. Reject path escapes, scope widening, fake HEAD, stale preimages or policy changes; re-probe before original world-write admission.
5. When the original CLI/Reader cannot bind the affected scope, retain UNBOUND and name the original scope owner. Never launder STALE into FRESH.

## Boundaries

- **Owner:** PIPD
- **Consumers:** execution handoff
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
