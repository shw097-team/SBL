# pipd-pi-compile — SkillContract

- **Owner:** PIPD
- **Consumers:** PD binder

## Typed IO

**Input** — `schemas/input.schema.json` (`urn:pipd:skill:pipd-pi-compile:input:1`): IntentCard reference + profile + requirement atoms

- `intent.subject_id` — INTENT-<16 hex> — frozen intent identity
- `profile` — LITE | STANDARD | ASSURED — effective profile
- `atoms[]` — req_id + source_clause + owner + acceptance_cue + risk_guard — atoms, at least one

**Output** — `schemas/output.schema.json` (`urn:pipd:skill:pipd-pi-compile:output:1`): PI-PKG (S0 family 06) with stable_semantic_contract, acceptance, trace

- `stable_semantic_contract` — contract=stable + profile_binding + atoms — the semantic contract
- `acceptance.mode` — const bound — bound acceptance, oracle DOC-03
- `trace[]` — PI-PKG -> RequirementAtom links — one link per atom

## Trigger

Use when a frozen IntentCard and an effective ProfileBinding must be compiled into a PI-PKG with a stable semantic contract and trace links.

Routing phrases (deterministic, case-insensitive): `compile the pi`, `pi package`, `pi-pkg`, `compile pi`.

## Non-trigger

- Do NOT use when capturing the goal at intake — route to `pipd-route-intake` instead.
- Do NOT use when late-binding the PI to a repository context — route to `pipd-pd-bind` instead.

## Permission

- May read the frozen IntentCard and the ProfileBinding.
- May write only the PI-PKG and its trace links.
- Must never consult an LLM on this path and must never invent an atom.

## Failure / degrade behaviour

- `PI_SEMANTIC` — compiled zero atoms, or acceptance cannot be bound -> refuse; degrade to requesting a corrected atom set, never to a prose-only contract
- `PI_SCHEMA` — atom missing a required field -> refuse with the field named

## First-fail invariant

`input.minItems:atoms` — PI_SEMANTIC fires before any trace is minted; see references/contract.md
