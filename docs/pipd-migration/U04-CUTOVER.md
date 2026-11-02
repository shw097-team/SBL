# U04 canonical cutover record

**Record ID:** `U04-CUTOVER-2026-11-02-r1`
**Single control record** for the SBL/PIPD consolidation. Fabric FHS and the PIPD README point here; they do not
keep a second ledger.

**Current state:** **`D1_GO_EFFECTIVE`** — the single canonical writer is SBL `main`
(`c308317818f794602f32945b0cfaa94a7f4fb65e`); `D2` is `CONDITIONALLY_PREAUTHORIZED / AFTER_D1` and is
recorded in §11 as it is executed.
**Writer that was in force before this record:** `PIPD-LS-SP@aeb0d479` (13 CLI), which is now the
historical source and is **not** deleted, rewritten or archived at this point.

## 1. Decisions

| decision | status | who | what is needed |
|---|---|---|---|
| **D0** — canonical baseline | **`APPROVED`** | SBL/PIPD owner (this round's instruction `SBL-PIPD-U04-HERMES-THIN-2026-11-03-r2` §0) | `PIPD-LS-SP@aeb0d479` is the U04 baseline: 13 CLI / 19 families / 8 skills, `pipd_ls_sp` import and `pipd` CLI preserved. The R21 `compile-cc` is **not** part of this ABI. |
| **D1** — cutover Go/No-Go | **`D1_GO_EFFECTIVE`** (2026-11-03 00:40 +0800, merge `c3083178…`) | same owner | activated only after §2 G1–G4 passed on head `441e6d8`: three CI checks green, adapter flow + skills bundle real, independent wheel install proven |
| **D2** — maintenance exit / archive | **`CONDITIONALLY_PREAUTHORIZED / AFTER_D1`** | same owner, then a GitHub admin with real rights | freeze the old compiler's feature line after D1; archive only when the independent distribution, open-PR disposition and security responsibility are settled and `archived=true` reads back |

The authorisation is recorded from the commission itself; no personal signature, independent checker
or other-domain owner signature is claimed. Where a domain's owner authority is not established,
that domain stays `OWNER_AUTHORITY_HOLD` and does not block the rest. `D0` approves **the baseline**,
not a cutover; `D1` stays inert until its gate is measured.

## 2. Phases

| phase | status | evidence |
|---|---|---|
| **C0** source freeze & decision material | **PASS** (D0 pending) | `docs/pipd-migration/BASELINE.md`; SBL `e166d67c`, PIPD `aeb0d479`, Fabric `59bb783d`, HGK `0143b503` |
| **C1** SBL absorption candidate | **PASS (candidate)** | `integrations/pipd/` — 318 files, verbatim from `PIPD-LS-SP@aeb0d479`; one modifiable `pipd_ls_sp` tree; Apache-2.0 `LICENSE` + `NOTICE` carried; 8 script/helper files excluded by SBL's no-shipped-scripts invariant (`integrations/pipd/MIGRATION-NOTES.md`) |
| **C2** compatibility / independent use | **PASS (candidate scope)** | TPM adapter + 9 POS/NEG tests; 8-skill bundle builder; built wheel `pipd_ls_sp-0.1.1a4-py3-none-any.whl` (287 844 B, sha256 `47b58d72…`); clean-venv install with no SBL package; 13 CLI, 19 families, `doctor` reports `INSTALLED` schema source; product test subset result in §4 |
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
| T01 baseline identified | `PIPD-LS-SP@aeb0d479`, 13 CLI, 19 families, 8 skills — recorded in `BASELINE.md` |
| T02 package / independent install | wheel builds; installs into a venv **without** `sbl-v01`; `import sbl_core` fails there by design (U04.2 POS) |
| T03 19 schema families | `registry.EXPECTED_FAMILIES == 19`; `pipd doctor` → `families: 19`, `schema_source.mode = INSTALLED` |
| T04 CLI contract | `pipd --help` lists exactly the 13 commands of `main`; the 14th (`compile-cc`) exists only on the unmerged candidate |
| T05 skills | 8 `SKILL.md` present in `integrations/pipd/skills/`; packaging tools unchanged |
| T06 narrow compiler flow (POS) | `sbl_sp/pipd_adapter.py` compiles a real TPM hand-off through IntentCard → PI-PKG → PD-PKG → ConstructionContract → ECP → TQAEP against a git repository; bundle validates `PASS` with trace closure, PD `PREDEV_READY`, TQAEP `independent_acceptance = NOT_GRANTED` (9 tests, `tests/test_pipd_adapter.py`) |
| T06 negative cases | maker==checker, missing receipt and `SELF_ATTESTED` → `SBL_E_SELF_CHECK_FORBIDDEN`; stale `currentness_epoch` → `SBL_E_STALE_HEAD`; `writable_scope=dist/**` → `SBL_E_WRITE_OUTSIDE_WRITESET`; missing source locator → `SBL_E_UNLOCATED_REQUIREMENT` |
| 8-skill single-source bundle | `products/sbl-tpm-sp/build_bundle.py` derives 8 packs from `integrations/pipd/skills/` and binds every file to a sha256; builder refuses a ninth pack and refuses a compiler copy (`tests/test_sbl_tpm_sp_bundle.py`) |
| skill pack contract | `python tools/skill_pack_check.py --all` in `integrations/pipd`: 8/8 packs, POS/NEG/EDGE/SEC cases all pass, routes verified |
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
| head and CI | this file ships inside the pull request, so the PR head and its Checks tab are the current pair; the run that verified the code above was `test (ubuntu)`, `test (windows)` and `pipd-compat`, all success |
| this line is not a SHA | a committed SHA inside the same PR is stale by definition; cite the PR, not a snapshot of it |
| merge | none — `D1` not recorded, so the writer stays with `PIPD-LS-SP` |
| PIPD side | no change: `main` `aeb0d479`, 4 releases, `archived=false` |
| FHS side | no change: `CANONICAL_COMPILER_PRE_CUTOVER`, `effect_permission=NONE` |

## 8. D1 gate and the fields it needs

`D1` was `CONDITIONALLY_PREAUTHORIZED`; it is now **`D1_GO_EFFECTIVE`** because every row below is a
measurement, not a plan.

| D1 field | value |
|---|---|
| SBL candidate | PR [#17](https://github.com/shw097-team/SBL/pull/17), head recorded in the PR |
| merge | `c308317818f794602f32945b0cfaa94a7f4fb65e` (squash of PR #17 into SBL `main`) |
| PIPD baseline | `PIPD-LS-SP@aeb0d479`, Apache-2.0, 13 CLI |
| ABI | unchanged: `pipd_ls_sp` import, `pipd` CLI with the 13 commands of `main`; no `compile-cc` |
| distribution | first SBL-built wheel proposed as `pipd-ls-sp 0.1.1a5` — the bytes differ from `a4`, so the version must too; `0.1.1a4` release assets stay immutable |
| affected consumers | SBL `sbl-v01` (adapter `sbl_sp/pipd_adapter.py`), `sbl-tpm-sp` skills bundle, any user installing `pipd-ls-sp` |
| effective moment | `2026-11-03 00:40 +0800` — SBL `main` carries the compiler, the adapter runs against the built distribution in CI, and PIPD `main` is unchanged read-only history |
| rollback | revert the SBL merge; `PIPD-LS-SP` `main` was never altered, so it resumes as writer without a restore decision |

`D1_HOLD` applies instead if any of G1–G4 fails, if the independent distribution is not actually
obtainable, or if the original-domain authority for the writer move cannot be shown. Merging and
"canonical effective" are two different facts and are recorded separately.

## 9. Delta against the open PIPD pull requests (measured, not merged)

| PR | what it changes | classification | reason |
|---|---|---|---|
| [#20](https://github.com/shw097-team/PIPD-LS-SP/pull/20) | 3 files: `oracle_compat.py`, `pipeline.py` (+62/−20), `test_oracle_compat.py` | **`DEFERRED_TO_SBL`** | additive DOC-07 / legacy DOC-03 oracle compatibility API; the 13-CLI chain compiles and validates without it |
| [#22](https://github.com/shw097-team/PIPD-LS-SP/pull/22) | 484 files: 30 under `src/` (+981/−1085) incl. `abi.py`, slot contracts, `compile-cc`; the rest is round evidence | **`DEFERRED_TO_SBL`** (src/ABI) / **`HISTORICAL_ONLY`** (evidence) | `mergeable=false`; it stacks on #20 and is a broad semantics refactor plus a 14th command that D0 did not admit. No blocking defect was found in today's chain |
| — | — | **`REQUIRED_PRE_CUTOVER`: none** | G3 runs the real chain (PI → PD → ConstructionContract → ECP → TQAEP) against the absorbed tree |

If the owner later wants R21, it is a versioned ABI change with its own amendment, not a silent
inclusion in this baseline.

## 10. Authorisation record for this round

- Source: `SBL-PIPD-U04-HERMES-THIN-2026-11-03-r2` §0, issued by the requester acting as OWNER.
- `D0` approved the baseline; `D1`/`D2` are conditional on the gates in §2 and §8.
- Not claimed: any independent checker signature, any other-domain owner signature, HGK issuer or
  native effect, Fabric policy effect, Hermes host load, release or store publication.
- The write authority for this PR remains the engineering commission and the repository's existing
  GitHub permissions.

## 11. D2 execution log

| item | state |
|---|---|
| canonical writer | **SBL `main`** `c3083178…`; the compiler package, 19 families and 8 skills are maintained in `integrations/pipd/` |
| PIPD `main` | unchanged `aeb0d479` — no rewrite, no force-push, no release overwritten |
| PIPD releases | 4 preview releases + `b1-promote-20261028` tag untouched |
| independent distribution | wheel builds from SBL `main` and is exercised in CI on every push; **no public download entry point has been published yet** → `CUTOVER_DELIVERY_HOLD` for that sub-item only |
| maintenance | feature work on the old compiler stops; the announcement PR carries `MAINTENANCE_EXIT / CANONICAL_MOVED_TO_SBL` |
| archive | not requested: open PRs #26/#22/#20/#19/#15 need disposition first, and archiving requires real admin rights |
