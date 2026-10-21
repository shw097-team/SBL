# FAR round r12 — claims alignment and control-package landing

## Why

The external acceptance report (R8) recorded a `CONFIRMED_DEFECT`: `main` still described the product as
`CANDIDATE_ONLY` / `Not released` / "installs one console script, `sbl-todo`" while two releases exist and
`pyproject.toml` installs three console scripts. The same report recommended a scoped merge of
`candidate/r9-20261021-ctrlpkg` (WO-01) which had not been merged.

A FAR deviation study (`_governance/round-20261021-r12-far/FAR_DEVIATION_STUDY.md`) reconciled every open
item against `SBL_PIPD-LS-PKG` DOC-00..13 and classified them into: merge now, fix now (docs), owner
decision, HGK work order, or defer with a trigger. This change lands the first two classes.

## What changes

- README status/claim section tells the truth about the released pre-release line (`v0.1.0-foundation-preview`,
  `v0.1.1rc1`) and lists the three console scripts that actually exist.
- `docs/RUN_CONFORMANCE.md` records the one command that actually runs the conformance suite on this host,
  together with its prerequisites and the rule that a count is only valid with its tree state.
- `_governance/round-20261021-r12-far/` records the FAR study and its adjudication.
- (merged separately, PR #5) the control-package pin and its three negative controls.

## Non-goals

- No change to `sbl_core/`, `sbl_sp/`, `sbl_cli/`, `contracts/` or `tests/`.
- No new claim of native effect, host installation, independent acceptance, or full-contract completion.
- No completion percentage: the semantic denominator stays `UNKNOWN` until an owner signs one.
- No vendoring of the external compiler/challenge bundles; their digests stay in the round ledger.

## Claim ceiling after this change

`SBL_FULL_PRODUCT` remains OPEN. The control package is pinned by identity; the public claim now matches
the published artefacts; the native chain (WorkOrder → ONE ECP → Permit → writer → isolated checker) is
still not established, and that is the next single blocker.
