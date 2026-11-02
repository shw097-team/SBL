# pipd-profile-tailor — SkillContract

- **Owner:** PIPD
- **Consumers:** Skills/JIT/HGK

## Typed IO

**Input** — `schemas/input.schema.json` (`urn:pipd:skill:pipd-profile-tailor:input:1`): requested profile + axes + provider-off flag

- `profile` — LITE | STANDARD | ASSURED — requested profile
- `axes[]` — the nine canonical axes, unique — axis set driving the veto
- `provider_off_required` — boolean — provider-off parity requirement

**Output** — `schemas/output.schema.json` (`urn:pipd:skill:pipd-profile-tailor:output:1`): ProfileBinding (S0 family 04)

- `profile` — LITE | STANDARD | ASSURED — effective profile after the veto
- `escalated` — boolean — true when the veto raised the depth
- `artifact_depth` — L1 | L3 | L4 — depth floor for downstream artifacts

## Trigger

Use when a requested profile and axis set must be resolved into an effective ProfileBinding through the safety veto before compilation.

Routing phrases (deterministic, case-insensitive): `tailor the profile`, `compute the profile`, `profile binding`, `select the axes`.

## Non-trigger

- Do NOT use when capturing an unbound goal at intake — route to `pipd-route-intake` instead.
- Do NOT use when compiling the PI package — route to `pipd-pi-compile` instead.

## Permission

- May read the axis set and provider-off flag only.
- May write only the ProfileBinding record.
- Must never weaken a veto, and must never accept an axis outside the canonical nine.

## Failure / degrade behaviour

- `PROFILE_VETO` — unknown profile name -> refuse; no binding is minted
- `UNSUPPORTED_SURFACE` — unknown or duplicated axis -> refuse; degrade to asking for a canonical axis set

## First-fail invariant

`input.enum:profile` — PROFILE_VETO fires before any depth computation; see references/contract.md
