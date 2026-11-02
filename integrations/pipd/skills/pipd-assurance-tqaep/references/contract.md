# pipd-assurance-tqaep — SkillContract

- **Owner:** PIPD/TQAEP semantics
- **Consumers:** Independent checker/release

## Typed IO

**Input** — `schemas/input.schema.json` (`urn:pipd:skill:pipd-assurance-tqaep:input:1`): PI-PKG (traced) + ECP + maker/checker identities + checker receipt

- `pi.trace[]` — at least one link — assurance requires trace
- `maker` — identity string — the bounded writer
- `checker` — identity string, distinct from maker — the independent checker
- `checker_execution_receipt` — string, never SELF_ATTESTED — evidence of independence

**Output** — `schemas/output.schema.json` (`urn:pipd:skill:pipd-assurance-tqaep:output:1`): TQAEP (S0 family 13)

- `tests[]` — test_id + oracle + positive_fixture + negative_fixture — one per atom
- `acceptance[]` — INDEPENDENT_CASE_PASS with distinct=true — SoD evidence
- `requalification` — const affected-only — narrow re-qualification scope

## Trigger

Use when a PI-PKG and ECP must be assured through a TQAEP with an independent checker, per-atom oracles and positive/negative fixtures.

Routing phrases (deterministic, case-insensitive): `tqaep`, `assurance plan`, `independent checker`, `quality assurance plan`.

## Non-trigger

- Do NOT use when emitting the ConstructionContract and ECP — route to `pipd-execution-contract` instead.
- Do NOT use when closing the package with claim ceiling and evidence — route to `pipd-package-project` instead.

## Permission

- May read the PI-PKG trace and the ECP.
- May write only the TQAEP record.
- Must never accept a self-attested receipt and must never mark maker and checker distinct when they are not.

## Failure / degrade behaviour

- `TQ_SOD` — maker == checker, aliased or self-attested -> refuse; degrade to a genuinely independent checker, never to self-acceptance
- `TQ_TRACE` — PI without trace links -> refuse until the PI carries trace
- `TQ_ORACLE` — a test without an oracle -> refuse; an oracle-less test is not evidence

## First-fail invariant

`semantic.distinct:maker,checker` — TQ_SOD fires before any test row is minted; see references/contract.md
