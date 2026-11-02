# pipd-route-intake — SkillContract

- **Owner:** PIPD-EC (deterministic compiler)
- **Consumers:** pipd-authority-source, pipd-pi-compile

## Typed IO

**Input** — `schemas/input.schema.json` (`urn:pipd:skill:pipd-route-intake:input:1`): goal + source locators + optional constraints/non_goals

- `goal` — string, non-blank — the unbound objective
- `sources[].rel` — string, no '..' traversal — resolvable source locators, at least one
- `constraints[]` — strings — admitted constraints
- `non_goals[]` — strings — explicit non-goals

**Output** — `schemas/output.schema.json` (`urn:pipd:skill:pipd-route-intake:output:1`): IntentCard (schema_version IntentCard@1)

- `subject_id` — INTENT-<16 hex> — content-derived identity
- `content_hash` — 64 hex — hash of the intake body
- `atoms[]` — req_id x axis — requirement atoms, at least one

## Trigger

Use when an unbound goal with source locators arrives at the intake gate and must be captured as a typed IntentCard with requirement atoms before any compilation begins.

Routing phrases (deterministic, case-insensitive): `route the intake`, `intake request`, `intent card`, `capture the goal`.

## Non-trigger

- Do NOT use when compiling the PI package from an existing IntentCard — route to `pipd-pi-compile` instead.
- Do NOT use when freezing source families or authority bindings — route to `pipd-authority-source` instead.

## Permission

- May read admitted source locators to confirm they resolve.
- May write only the IntentCard record it emits.
- Must never write into the sources it names, and must never invent a source locator.

## Failure / degrade behaviour

- `INTAKE_INVALID` — empty/blank goal, or zero requirement atoms derivable -> refuse the intake; no IntentCard is emitted
- `AUTHORITY_UNKNOWN` — a source locator does not resolve on disk -> refuse the intake; degrade to asking for a resolvable locator, never to a guessed path

## First-fail invariant

`input.required:goal` — the intake gate raises INTAKE_INVALID before any atom derivation; see references/contract.md
