# pipd-authority-source — SkillContract

- **Owner:** PIPD
- **Consumers:** all compilers/adapters

## Typed IO

**Input** — `schemas/input.schema.json` (`urn:pipd:skill:pipd-authority-source:input:1`): families[] with manifest_sha256 + file locators

- `families[].name` — F<digit>_<A-Z0-9_> — family code
- `families[].manifest_sha256` — 64 hex — manifest digest of the family
- `families[].files[].rel` — string, no '..' — file locators, at least one

**Output** — `schemas/output.schema.json` (`urn:pipd:skill:pipd-authority-source:output:1`): SourceFreezeManifest + AuthorityBinding[] (S0 families 02)

- `bindings[].authority_rank` — R1 | R2 — R1 for F1/F2/F3/F5/F6 families
- `bindings[].locator` — string — the resolved locator that was frozen
- `digests[]` — 64 hex — per-family manifest digests

## Trigger

Use when source families must be frozen into a SourceFreezeManifest with AuthorityBinding records before any compiler reads them.

Routing phrases (deterministic, case-insensitive): `freeze the authority`, `authority binding`, `source freeze`, `bind the source family`.

## Non-trigger

- Do NOT use when capturing a new goal as an IntentCard — route to `pipd-route-intake` instead.
- Do NOT use when computing the profile binding — route to `pipd-profile-tailor` instead.

## Permission

- May read source files named by the locators to confirm they resolve.
- May write only the freeze manifest and its bindings.
- Must never rewrite a source file, and must never accept a digest it did not read.

## Failure / degrade behaviour

- `AUTHORITY_UNKNOWN` — missing/invalid manifest digest, empty family, or unresolved locator -> refuse the freeze; degrade to requesting a corrected manifest, never to a default digest
- `REPAIR_SCOPE` — a locator traverses out of the admitted root -> refuse the freeze outright; no partial freeze is emitted

## First-fail invariant

`input.required:manifest_sha256` — AUTHORITY_UNKNOWN fires before any binding is minted; see references/contract.md
