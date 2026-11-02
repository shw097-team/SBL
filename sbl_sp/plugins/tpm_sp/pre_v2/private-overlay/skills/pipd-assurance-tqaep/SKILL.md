---
name: pipd-assurance-tqaep
description: Use when a PI-PKG and ECP must be assured through a TQAEP with an independent
  checker, per-atom oracles and positive/negative fixtures.
version: 1
owner: PIPD/TQAEP semantics
triggers:
- tqaep
- assurance plan
- independent checker
- quality assurance plan
schemas:
- schemas/input.schema.json
- schemas/output.schema.json
references:
- references/contract.md
- references/examples.md
tests:
- tests/cases.yaml
---

# pipd-assurance-tqaep

## Contract (imperative)

1. Plan without any live checker receipt. Require nonempty traced canonical PI plus ECP intent and a pinned original Case registry.
2. Bind every applicable Case to original RequirementID, Clause/SourceSHA, Oracle and FUO; pin both POS and NEG bytes, raw schema, expected WorldRaw, Host/Profile/Kind/Mode, checker role and affected requalification.
3. Missing original runner is RUNNER_UNBOUND with its named owner. PLAN_VALID is design consistency only.
4. A nested fake receipt, signed verdict, grant, empty evidence, wrong Host or false Qualified claim is refused. A maker cannot certify independence.
5. The unchanged original compile-tqaep may return TQ_SOD without a live receipt. Record ORIGINAL_TQAEP_EXPORT_HOLD; never fabricate a receipt. Original protected Checker alone can qualify the same Subject/Candidate/Scope/Host/PolicyEpoch/FUO; Publisher owns release.

## Boundaries

- **Owner:** PIPD/TQAEP semantics
- **Consumers:** Independent checker/release
- **Typed IO:** `schemas/input.schema.json` -> `schemas/output.schema.json`
- **Full contract:** `references/contract.md`
- **Worked examples:** `references/examples.md`
- **Cases:** `tests/cases.yaml` (POS / NEG / EDGE / SEC, each naming its expected first-fail)


## PRE-V2 active route (@2)

For current planning use `../../scripts/pre_v2.py` and
`../../references/contracts/pre-v2-routing.md`. Existing v1 schemas keep their
original `$id` and are compatibility replay inputs; their fixture receipts and
approval-shaped strings provide no live authority. Read original bytes and pin
the current original Reader. Missing original Reader means EXECUTOR_UNBOUND.
Produce design artifacts with AUTHOR_DESIGN_ONLY; receipt-free planning is legal.
Use only the original PIPD Writer for canonical PI/PD/ECP/TQAEP. Keep @2 sidecars
separate from canonical JSON and validate actual bodies, not just schema syntax.
Never turn a Sidecar, package seal or author test into a Grant, Qualified verdict,
Host qualification or release. Scope/Host/PolicyEpoch changes invalidate only the
affected binding. Reuse the owner's already-scoped authorization and known answers.
