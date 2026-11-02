# pipd-package-project — SkillContract

- **Owner:** PIPD
- **Consumers:** all planes

## Typed IO

**Input** — `schemas/input.schema.json` (`urn:pipd:skill:pipd-package-project:input:1`): artifact bundle + allowed claims + producer (+ approval for LOCAL_QUALIFIED+)

- `bundle.artifacts[]` — name + subject_id + content_hash — the artifacts being closed
- `allowed_claims[]` — rungs of the claim ladder — the ceiling being requested
- `approval` — required only at LOCAL_QUALIFIED+ — checker identity + approval receipt

**Output** — `schemas/output.schema.json` (`urn:pipd:skill:pipd-package-project:output:1`): ClaimCeiling (S0 family 16) + EvidenceExpectation[] + TraceClosureReport

- `forbidden_escalation[]` — ladder rungs above the ceiling — explicitly forbidden
- `evidence[]` — RAW_RECEIPT, LOCAL claim effect — evidence expectations
- `trace_closure.verdict` — PASS | FAIL — closure verdict over the bundle

## Trigger

Use when the artifact bundle must be closed into a ClaimCeiling with EvidenceExpectation records and a TraceClosureReport before handoff.

Routing phrases (deterministic, case-insensitive): `package the project`, `claim ceiling`, `evidence expectation`, `trace closure`.

## Non-trigger

- Do NOT use when compiling the TQAEP assurance plan — route to `pipd-assurance-tqaep` instead.
- Do NOT use when tailoring the profile binding — route to `pipd-profile-tailor` instead.

## Permission

- May read the artifact bundle and its trace edges.
- May write only the ClaimCeiling, EvidenceExpectation and TraceClosureReport records.
- Must never raise a claim above the evidenced ceiling, and must never self-approve a claim gate.

## Failure / degrade behaviour

- `PI_SEMANTIC` — unknown claim rung -> refuse the ceiling
- `EVIDENCE_GAP` — claim above LOCAL_QUALIFIED without approval evidence -> refuse; degrade to the evidenced ceiling, never to an unevidenced claim
- `DENOMINATOR` — empty artifact bundle -> refuse; an empty bundle can never pass

## First-fail invariant

`semantic.claim_gate` — EVIDENCE_GAP fires before the ceiling is minted; see references/contract.md
