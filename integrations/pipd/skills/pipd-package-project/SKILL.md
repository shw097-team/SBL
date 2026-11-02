---
name: pipd-package-project
description: Use when the artifact bundle must be closed into a ClaimCeiling with EvidenceExpectation records and a TraceClosureReport before handoff.
version: 1
owner: PIPD
triggers:
  - package the project
  - claim ceiling
  - evidence expectation
  - trace closure
schemas:
  - schemas/input.schema.json
  - schemas/output.schema.json
references:
  - references/contract.md
  - references/examples.md
tests:
  - tests/cases.yaml
---

# pipd-package-project

## Contract (imperative)

1. Require a non-empty artifact bundle, the allowed claims and the producer identity.
2. Refuse an empty bundle: an empty denominator never passes.
3. Refuse any claim outside the eight-rung ladder; claims only move up the ladder, never sideways.
4. Gate LOCAL_QUALIFIED and above on a bound approval receipt plus an independent checker identity; without them, refuse the claim.
5. Emit one EvidenceExpectation per test: RAW_RECEIPT, same_candidate_hash freshness, LOCAL claim effect.
6. Recompute trace closure over the bundle and refuse the package on orphan or hash-mismatched edges.

## Boundaries

- **Owner:** PIPD
- **Consumers:** all planes
- **Typed IO:** `schemas/input.schema.json` -> `schemas/output.schema.json`
- **Full contract:** `references/contract.md`
- **Worked examples:** `references/examples.md`
- **Cases:** `tests/cases.yaml` (POS / NEG / EDGE / SEC, each naming its expected first-fail)
