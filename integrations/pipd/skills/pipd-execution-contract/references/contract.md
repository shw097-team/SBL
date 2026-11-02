# pipd-execution-contract — SkillContract

- **Owner:** PIPD (ConstructionContract) / PIPD-ECP semantics (ECP)
- **Consumers:** HGK adapter, TQAEP

## Typed IO

**Input** — `schemas/input.schema.json` (`urn:pipd:skill:pipd-execution-contract:input:1`): PD-PKG reference + PI-PKG reference

- `pd.subject_id` — PD-<16 hex> — bound PD identity
- `pi.subject_id` — PI-<16 hex> — its PI identity

**Output** — `schemas/output.schema.json` (`urn:pipd:skill:pipd-execution-contract:output:1`): ConstructionContract (S0 family 10) + ECP (S0 family 12)

- `construction_contract.writable_scope[]` — non-empty, no '..', never '**' — the only write scope
- `ecp.permission.token_required` — const true — token-gated effect
- `ecp.rollback.required` — const true — rollback is mandatory

## Trigger

Use when a bound PD-PKG must become a ConstructionContract plus an ECP that fixes effect, permission, retries, idempotency, readback and rollback.

Routing phrases (deterministic, case-insensitive): `execution contract`, `construction contract`, `compile the ecp`, `emit the ecp`.

## Non-trigger

- Do NOT use when binding the PD package to a repository context — route to `pipd-pd-bind` instead.
- Do NOT use when compiling the TQAEP assurance plan — route to `pipd-assurance-tqaep` instead.

## Permission

- May read the PD-PKG and PI-PKG references.
- May write only the ConstructionContract and ECP records.
- Must never widen the PD writable_scope, and must never emit an effect without a rollback pointer.

## Failure / degrade behaviour

- `EFFECT_UNKNOWN` — empty or unbounded writable scope -> refuse; no ECP is emitted
- `ECP_PERMISSION` — permission without a token, or rollback not required -> refuse; degrade to a token-gated plan, never to an unguarded effect

## First-fail invariant

`output.required:ecp.permission` — ECP_PERMISSION fires before the contract is sealed; see references/contract.md
