---
name: pipd-pi-compile
description: Use when a frozen IntentCard and an effective ProfileBinding must be compiled into a PI-PKG with a stable semantic contract and trace links.
version: 1
owner: PIPD
triggers:
  - compile the pi
  - pi package
  - pi-pkg
  - compile pi
schemas:
  - schemas/input.schema.json
  - schemas/output.schema.json
references:
  - references/contract.md
  - references/examples.md
tests:
  - tests/cases.yaml
---

# pipd-pi-compile

## Contract (imperative)

1. Require the frozen IntentCard reference, the effective profile, and at least one requirement atom.
2. Refuse zero-atom compilations; a PI without atoms has no semantic contract.
3. Require every atom to carry source_clause, owner, acceptance_cue and risk_guard.
4. Bind acceptance in 'bound' mode with oracle_source DOC-03 DOMAIN_ORACLES; never leave acceptance open.
5. Emit TraceLinks from the PI-PKG to every atom and recompute identity over the final body.
6. Reject undeclared sidecar keys such as _profile_meta on the input; sidecars are stripped, not trusted.

## Boundaries

- **Owner:** PIPD
- **Consumers:** PD binder
- **Typed IO:** `schemas/input.schema.json` -> `schemas/output.schema.json`
- **Full contract:** `references/contract.md`
- **Worked examples:** `references/examples.md`
- **Cases:** `tests/cases.yaml` (POS / NEG / EDGE / SEC, each naming its expected first-fail)
