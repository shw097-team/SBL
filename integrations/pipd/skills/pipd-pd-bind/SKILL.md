---
name: pipd-pd-bind
description: Use when a compiled PI-PKG must be late-bound to a real RepoContext into a PD-PKG before any construction is planned.
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

1. Require the PI-PKG reference and a RepoContext with root, head, tracked_files, currentness and writable_scope.
2. Refuse to bind without a RepoContext; never bind against an assumed repository.
3. Refuse an unresolved root, a negative tracked-file count, or an empty writable scope.
4. Refuse any writable_scope that escapes the repository root or equals '**'.
5. Record currentness exactly as observed (FRESH or STALE); never launder STALE into FRESH.
6. Emit the PD-PKG with late_bound_construction_binding bound_at PD and binding_scope affected_only.

## Boundaries

- **Owner:** PIPD
- **Consumers:** execution handoff
- **Typed IO:** `schemas/input.schema.json` -> `schemas/output.schema.json`
- **Full contract:** `references/contract.md`
- **Worked examples:** `references/examples.md`
- **Cases:** `tests/cases.yaml` (POS / NEG / EDGE / SEC, each naming its expected first-fail)
