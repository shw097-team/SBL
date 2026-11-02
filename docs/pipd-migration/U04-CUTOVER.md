# U04 canonical cutover record

**Record ID:** `U04-CUTOVER-2026-11-02-r1`
**Single control record** for the SBL/PIPD consolidation. Fabric FHS and the PIPD README point here; they do not
keep a second ledger.

**Current state:** `U04_CANDIDATE_READY / CUTOVER_PENDING_OWNER`
**Writer in force today:** `PIPD-LS-SP@main` (`8a0c852…`). This record does **not** move it.

## 1. Decisions

| decision | status | who | what is needed |
|---|---|---|---|
| **D0** — canonical baseline | `PENDING_OWNER` | SBL/PIPD owner | confirm `PIPD-LS-SP@8a0c852` (13 CLI) as the absorbed baseline, or name `candidate/r21-far-20261101` (14 CLI, `compile-cc`) and approve that ABI amendment |
| **D1** — cutover Go/No-Go | `NOT_REQUESTED` | same owner | after C2, approve the writer move with SBL candidate SHA, PIPD original SHA, version/ABI, effective time, affected consumers, rollback |
| **D2** — maintenance exit / archive | `NOT_REQUESTED` | same owner, then GitHub admin | stop compact; archive only after the independent distribution path is verified |

Nothing in this PR presumes any of the three. `D0` is a recommendation with a measured rationale
(`BASELINE.md` §4); it is not a signature.

## 2. Phases

| phase | status | evidence |
|---|---|---|
| **C0** source freeze & decision material | **PASS** (D0 pending) | `docs/pipd-migration/BASELINE.md`; SBL `e166d67c`, PIPD `8a0c852`, Fabric `59bb783d`, HGK `0143b503` |
| **C1** SBL absorption candidate | **PASS (candidate)** | `integrations/pipd/` — 318 files, verbatim from `PIPD-LS-SP@8a0c852`; one modifiable `pipd_ls_sp` tree; Apache-2.0 `LICENSE` + `NOTICE` carried; 8 script/helper files excluded by SBL's no-shipped-scripts invariant (`integrations/pipd/MIGRATION-NOTES.md`) |
| **C2** compatibility / independent use | **PASS (candidate scope)** | built wheel `pipd_ls_sp-0.1.1a4-py3-none-any.whl` (287 844 B, sha256 `47b58d72…`); clean-venv install with no SBL package; 13 CLI, 19 families, `doctor` reports `INSTALLED` schema source; product test subset result in §4 |
| **C3** canonical cutover | **NOT_STARTED** | requires D1; the SBL PR stays a candidate until then |
| **C4** maintenance exit / archive | **NOT_STARTED** | requires D2; PIPD `archived=false`, unchanged |

## 3. What deliberately does not change

- `PIPD-LS-SP` remains the canonical writer: `main` untouched, no release rewritten, 4 preview releases and the
  `b1-promote-20261028` tag unchanged, no forced push, no archive.
- Fabric FHS: `INTEGRATION/FHS/repository-map.json` still says `CANONICAL_COMPILER_PRE_CUTOVER` for PIPD, `source_state`
  still `PROPOSED_NOT_OWNER_RATIFIED`, `effect_permission=NONE`. The route only moves after D1 (C3).
- SBL `sbl-v01`: package name, version, dependency list and console scripts unchanged; its own CI must stay green.
- HG-KSEOS, Fabric policy, Hermes runtime: untouched.

## 4. Verification log

| test | result |
|---|---|
| T01 baseline identified | `PIPD-LS-SP@8a0c852`, 13 CLI, 19 families, 8 skills — recorded in `BASELINE.md` |
| T02 package / independent install | wheel builds; installs into a venv **without** `sbl-v01`; `import sbl_core` fails there by design (U04.2 POS) |
| T03 19 schema families | `registry.EXPECTED_FAMILIES == 19`; `pipd doctor` → `families: 19`, `schema_source.mode = INSTALLED` |
| T04 CLI contract | `pipd --help` lists exactly the 13 commands of `main`; the 14th (`compile-cc`) exists only on the unmerged candidate |
| T05 skills | 8 `SKILL.md` present in `integrations/pipd/skills/`; packaging tools unchanged |
| T06 narrow compiler flow | not run in this candidate; requires D0 owner choice and the SBL adapter, scheduled with C3 |
| T07 workspace-local doctor | `pipd init` creates the workspace; `doctor` correctly reports a missing local `schemas/registry.json` in a fresh workspace (consumes the installed registry instead) |
| T08 provenance | wheel built from the absorbed tree; `tools/build_dist.py` emits digest and licence metadata |
| T09 FHS route | **not applicable** (C3) |
| T10 maintenance exit | **not applicable** (C4) |
| absorbed product tests | **494 tests, 0 failed, 0 errors, 19 skipped** on the 37 product modules; the 12 repository-state modules and 2 governance-input modules are excluded with their reason in `BASELINE.md` §7 |

## 5. Rollback

Deleting this branch/postponing the PR returns the repositories to their current state; no writer, release, route
or archive was changed. If the PR is merged and later withdrawn, revert its merge commit; PIPD `main` was never
altered, so it remains the canonical writer without a restore decision.

## 6. Claim ceiling

`U04_CANDIDATE_READY` only. Not claimed: canonical cutover, three-active-repo consolidation, PIPD maintenance exit
or archive, native acceptance, HGK admission, policy effect, release, or an independent checker verdict.

## 7. Round record

| item | value |
|---|---|
| pull request | [#17](https://github.com/shw097-team/SBL/pull/17) — **draft**; it must not be merged before D1 |
| head at this record | `7cc0576` |
| CI | [run 41472781614](https://github.com/shw097-team/SBL/actions/runs/41472781614) — `test (ubuntu)`, `test (windows)`, `pipd-compat` all success |
| merge | none — `D1` not recorded, so the writer stays with `PIPD-LS-SP` |
| PIPD side | no change: `main` `8a0c852`, 4 releases, `archived=false` |
| FHS side | no change: `CANONICAL_COMPILER_PRE_CUTOVER`, `effect_permission=NONE` |
