# pipd-pd-bind — SkillContract

- **Owner:** PIPD
- **Consumers:** execution handoff

## Typed IO

**Input** — `schemas/input.schema.json` (`urn:pipd:skill:pipd-pd-bind:input:1`): PI-PKG reference + RepoContext

- `pi.subject_id` — PI-<16 hex> — compiled PI identity
- `repo_context.root` — string, non-empty — repository root that must resolve
- `repo_context.currentness` — FRESH | STALE — observed currentness
- `repo_context.writable_scope` — string, no '..', not '**' — the only write scope

**Output** — `schemas/output.schema.json` (`urn:pipd:skill:pipd-pd-bind:output:1`): PD-PKG (S0 family 07)

- `RepoContext` — root + head + tracked_files — the bound context
- `currentness` — FRESH | STALE — recorded, never inferred
- `late_bound_construction_binding` — bound_at PD, affected_only — late binding record

## Trigger

Use when a compiled PI-PKG must be late-bound to a real RepoContext into a PD-PKG before any construction is planned.

Routing phrases (deterministic, case-insensitive): `bind the pd`, `pd package`, `repo context`, `late-bind the pd`.

## Non-trigger

- Do NOT use when compiling the PI package from an IntentCard — route to `pipd-pi-compile` instead.
- Do NOT use when emitting the construction contract and ECP — route to `pipd-execution-contract` instead.

## Permission

- May read the repository root to confirm it resolves and count tracked files.
- May write only the PD-PKG record.
- Must never write into the repository during binding, and must never widen writable_scope.

## Failure / degrade behaviour

- `REPO_CONTEXT_MISSING` — no RepoContext, or the root does not exist -> fail closed; degrade to requesting the real RepoContext, never to a synthetic one
- `REPAIR_SCOPE` — writable_scope escapes the root or is '**' -> refuse outright; no partial binding is emitted

## First-fail invariant

`input.required:repo_context` — REPO_CONTEXT_MISSING fires before any binding is sealed; see references/contract.md
