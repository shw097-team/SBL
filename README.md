# SBL — SpecBuild Loop

SBL turns a guided specification into a governed build, verifies it with raw evidence, and repairs it in a
bounded cone. It runs as the product of the `SBL_PIPD-LS-PKG` control package (DOC-00..DOC-13), under
**HG-KSEOS** as the sole normative control plane, with **Hermes** as the governed runtime/orchestration
plane and **Codex CLI** as the bounded writer.

> Status: **CANDIDATE — NOT INDEPENDENTLY ACCEPTED.** Nothing in this repository is a release, a production
> claim, or an independent acceptance. See `_governance/round-20261020/` for the round's scope, task list,
> detection list and claim ceiling.

## What is here

| Path | Contents |
|---|---|
| `_governance/round-20261020/` | North star, execution SPEC, task list (TS00..TS19), detection list (CHK00..CHK17), round manifest |
| `openspec/` | OpenSpec change record `sbl-v01-candidate-build` (validated with `openspec validate --strict`) |
| `sbl_core/` | Shared Core, six logical modules `SBLM01..SBLM06` (being landed) |
| `sbl_sp/` | Three responsibility-separated SPs: `TPM-SP`, `Commander-SP`, `External Challenge-SP` |
| `sbl_cli/` | `sbl-todo` CLI tool — the first real FUO (`GJ01`) |
| `tests/` | Unit, contract, host and end-to-end tests (`GJ01..GJ03`) |
| `evidence/` | Scrubbed evidence manifests, per-test raw logs, SBOM/licence inventory |

## Product shape (v0.1 scope)

- One **Shared Core**; six modules: `SBLM01` Goal Intake, `SBLM02` Guided Specification, `SBLM03` Governed
  Routing, `SBLM04` Governed Build Bridge, `SBLM05` Evidence Verification, `SBLM06` Bounded Repair/Evolution.
- Three modes: `STANDALONE` (default), `PREW3_SHADOW` (read-only, `NO_EFFECT`), `SWOF_CONNECTED`
  (blocked until a native receiver ACK + Permit exists — not claimed connected).
- Golden journeys: `GJ01` CLI tool lifecycle, `GJ02` brownfield scoped patch with rollback, `GJ03`
  agent-skill / minimal-agent host bridge.

## Governance invariants

1. **Maker ≠ checker.** The writer lane and the independent checker lane are separate processes with
   separate model pins; the checker is read-only and cannot be the maker.
2. **Evidence first.** Every claim names its command, exit code, denominator, raw log digest and candidate SHA.
3. **No self-promotion.** A candidate becomes accepted only through an independent checker and, for release,
   a human/native gate.
4. **No second control plane.** Routing, task state and evidence authority live in HG-KSEOS.

## Licence

Pending an owner ruling (`TX-LICENSE-OWNER-RULING`). Do not assume a licence until one is committed.

## Tests

Test layout and commands are recorded per task in `openspec/changes/sbl-v01-candidate-build/tasks.md`.
A green CI run is not a substitute for a host-level effective-load receipt.
