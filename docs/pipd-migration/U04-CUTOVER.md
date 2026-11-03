# U04 canonical cutover record

**Record ID:** `U04-CUTOVER-2026-11-02-r1` (revised at C4)
**Single control record** for the SBL/PIPD consolidation. Fabric FHS and the PIPD README point here; they do not
keep a second ledger.

**Current state:** `C0–C3 = CLOSED_SCOPED`; **`C4 = CLOSED_SCOPED`** — the source moved, the distribution is
published, the old repository is frozen **and archived** (`archived=true`, read back from GitHub), and Fabric FHS
shows three active repositories plus one historical one.
**Canonical writer:** SBL `main` (`25a4c13c`), package `pipd-ls-sp 0.1.1a5` built from `integrations/pipd/`.
**Historical repository:** `PIPD-LS-SP@221dc61c`, **`archived=true`** (read back 2026-11-03), `MAINTENANCE_FROZEN` —
kept, not deleted, its tags and assets untouched.

## 1. Decisions

| decision | status | who | what it means |
|---|---|---|---|
| **D0** — canonical baseline | **`APPROVED`** | SBL/PIPD owner (`SBL-PIPD-U04-HERMES-THIN-2026-11-03-r2` §0) | `PIPD-LS-SP@aeb0d479` was the baseline: 13 CLI / 19 families / 8 skills, `pipd_ls_sp` import and `pipd` CLI preserved. `compile-cc` is **not** part of this ABI. |
| **D1** — cutover Go/No-Go | **`D1_GO_EFFECTIVE`** (2026-11-03 00:40 +0800, merge `c3083178…`) | same owner | activated after G1–G4 passed on head `441e6d8` (three CI checks green, adapter flow and skills bundle real, independent wheel install proven) |
| **D2** — maintenance exit / archive | **`DONE`** — frozen, announced, and archived (`archived=true` read back 2026-11-03) | same owner, executed by a repository admin | the old compiler's feature line is stopped and announced; the archive was completed by an administrator with the Administration scope after the token-scoped attempt returned 403 (§11.1, §11.2) |

The authorisation is recorded from the commission itself; no personal signature, independent checker
or other-domain owner signature is claimed. Where a domain's owner authority is not established,
that domain stays `OWNER_AUTHORITY_HOLD` and does not block the rest.

## 2. Phases

| phase | status | evidence |
|---|---|---|
| **C0** source freeze & decision material | **PASS** | `docs/pipd-migration/BASELINE.md`; SBL `e166d67c`, PIPD `aeb0d479`, Fabric `59bb783d`, HGK `0143b503` |
| **C1** SBL absorption | **PASS** | `integrations/pipd/` — 318 files absorbed from `PIPD-LS-SP@aeb0d479`; one modifiable `pipd_ls_sp` tree; Apache-2.0 `LICENSE` + `NOTICE`; 8 script/helper files excluded by SBL's no-shipped-scripts invariant (`integrations/pipd/MIGRATION-NOTES.md`) |
| **C2** compatibility / independent use | **PASS** | TPM adapter + 9 POS/NEG tests; 8-skill bundle builder; wheel built from the tree; clean-venv install with no SBL package; 13 CLI, 19 families, `doctor` reports `INSTALLED` schema source |
| **C3** canonical cutover | **PASS** | SBL `main` `c3083178` (merge of [#17](https://github.com/shw097-team/SBL/pull/17)); Fabric `main` `2436e440` (FHS-NAV/v2, [#25](https://github.com/shw097-team/Fabric/pull/25)); PIPD announcement [#27](https://github.com/shw097-team/PIPD-LS-SP/pull/27) |
| **C4** maintenance exit / archive | **CLOSED_SCOPED** | frozen and announced (§11); 5 open PRs dispositioned (§12); **archived** — `archived=true` read back from the GitHub API and mirrored into Fabric FHS as `FHS-NAV/v2` (§11.2, §15) |

## 3. What changed at C3, and what still does not change

- `PIPD-LS-SP` is **no longer** the canonical writer. Its `main` advanced after the cutover only by the two PRs
  the owner had already merged there (#26 `7073fe2d`, #28 `a25fb569`); no new compiler feature work is accepted.
- Fabric FHS `FHS-NAV/v2`: `pipd_canonical` → `sbl`, PIPD listed under `historical_repositories`
  (`role=HISTORICAL_CANONICAL_MOVED_TO_SBL`, `archived=true`, `write_authority=NONE`), `effect_permission=NONE`,
  `source_state=PROPOSED_NOT_OWNER_RATIFIED` unchanged.
- SBL `sbl-v01`: package name, version, dependency list and console scripts unchanged; its own CI stays green.
- HG-KSEOS, Fabric policy, Hermes runtime: untouched.

## 4. Verification log

| test | result |
|---|---|
| T01 baseline identified | `PIPD-LS-SP@aeb0d479`, 13 CLI, 19 families, 8 skills — `BASELINE.md` |
| T02 package / independent install | wheel builds; installs into a venv **without** `sbl-v01`; `import sbl_core` fails there by design (U04.2 POS) |
| T03 19 schema families | `registry.EXPECTED_FAMILIES == 19`; `pipd doctor` → `families: 19`, `schema_source.mode = INSTALLED` |
| T04 CLI contract | 13 verbs before and after the C4 drift port; the 14th (`compile-cc`) is not in this ABI |
| T05 skills | 8 `SKILL.md`; `tools/skill_pack_check.py --all` → 8/8 packs, POS/NEG/EDGE/SEC cases pass |
| T06 narrow compiler flow (POS) | `sbl_sp/pipd_adapter.py` compiles IntentCard → PI → PD → ConstructionContract → ECP → TQAEP on a real git repo; bundle `PASS` with trace closure; TQAEP `independent_acceptance = NOT_GRANTED` |
| T06 negative cases | maker==checker / no receipt / `SELF_ATTESTED` → `SBL_E_SELF_CHECK_FORBIDDEN`; stale epoch → `SBL_E_STALE_HEAD`; `dist/**` scope → `SBL_E_WRITE_OUTSIDE_WRITESET`; missing locator → `SBL_E_UNLOCATED_REQUIREMENT` |
| T09 FHS route | **PASS** — `FHS-NAV/v2` merged as Fabric `2436e440`; `fhs-nav-static` success on the PR and on the `main` push |
| T10 maintenance exit | **PASS** — announcement merged (PIPD `a25fb569`); archive read back `archived=true`; Fabric map mirrors it |
| absorbed product tests | **536 tests, 0 failed, 0 errors, 28 skipped** at C4 (was 494); the 12 repository-state modules and 2 governance-input modules stay excluded with their reason in `BASELINE.md` §7 |

## 5. Rollback

Reverting the SBL merge commit returns SBL to the pre-cutover tree; it does **not** by itself restore PIPD as the
canonical writer. Restoring the old writer is a separate owner decision (D-level), and it must move the FHS route
and the published distribution back in the same decision — two live writers are forbidden. PIPD `main` was never
rewritten, so its history remains intact either way.

## 6. Claim ceiling

`U04_CANONICAL_CUTOVER_DONE` for the product source and repository consolidation. Not claimed: native acceptance,
HGK admission, policy effect, Hermes host load, published-store release, independent checker verdict, or
`archived=true` (which is not true).

## 7. Round record

| item | value |
|---|---|
| pull request | [#17](https://github.com/shw097-team/SBL/pull/17) → merged `c3083178` |
| D1 record | [#19](https://github.com/shw097-team/SBL/pull/19) → merged `67c29be6` |
| C3 route | Fabric [#25](https://github.com/shw097-team/Fabric/pull/25) → merged `2436e440` |
| PIPD announcement | [#27](https://github.com/shw097-team/PIPD-LS-SP/pull/27) → merged `a25fb569` |
| PIPD side | `main` `221dc61c`, 4 preview releases untouched, `archived=true` |
| FHS side | `FHS-NAV/v2`, three active repositories, PIPD historical |

## 8. D1 fields (as measured at activation)

| D1 field | value |
|---|---|
| SBL candidate | PR [#17](https://github.com/shw097-team/SBL/pull/17), head `441e6d8` |
| merge | `c308317818f794602f32945b0cfaa94a7f4fb65e` |
| PIPD baseline | `PIPD-LS-SP@aeb0d479`, Apache-2.0, 13 CLI |
| ABI | unchanged: `pipd_ls_sp` import, `pipd` CLI with 13 commands; no `compile-cc` |
| distribution | `pipd-ls-sp 0.1.1a5`, built from SBL `integrations/pipd`; `0.1.1a4` and the preview assets stay immutable |
| affected consumers | `sbl-v01` adapter, `sbl-tpm-sp` skills bundle, users installing `pipd-ls-sp` |
| effective moment | 2026-11-03 00:40 +0800 |
| rollback | see §5 — revert restores the tree, not the writer |

## 9. Delta against the remaining open PIPD pull requests

| PR | what it changes | classification | reason |
|---|---|---|---|
| [#20](https://github.com/shw097-team/PIPD-LS-SP/pull/20) | 3 files: `oracle_compat.py`, `pipeline.py` (+62/−20), `test_oracle_compat.py` | **`DEFERRED_TO_SBL`** | additive DOC-07 / legacy DOC-03 compatibility API; the 13-verb chain compiles without it |
| [#22](https://github.com/shw097-team/PIPD-LS-SP/pull/22) | 484 files (460 evidence); 30 under `src/` incl. `abi.py`, slot contracts, `compile-cc` | **`HISTORICAL_ONLY`** | `mergeable=false`; adds a 14th command outside the approved ABI |

## 10. Authorisation record

- Source: `SBL-PIPD-U04-HERMES-THIN-2026-11-03-r2` §0 (D0/D1 activation) and
  `SBL-PIPD-U04-HERMES-C4-CLOSEOUT-2026-11-03-r3` §0 (C4 scope, W1–W6, one-time A1–A7 approval).
- Not claimed: any independent checker signature, other-domain owner signature, HGK issuer or native effect,
  Fabric policy effect, Hermes host load, store publication.
- Write authority for these changes remains the engineering commission and the repository's GitHub permissions.

## 11. D2 execution log

| item | state |
|---|---|
| canonical writer | **SBL `main`** (`25a4c13c` at this record); compiler, 19 families and 8 skills in `integrations/pipd/` |
| PIPD `main` | `221dc61c`; advanced only by the two owner-merged PRs (#26, #28) and the documentation pointer (#29); no rewrite, no force-push |
| PIPD releases | 4 preview releases + `b1-promote-20261028` tag untouched |
| independent distribution | **published**: `pipd-ls-sp 0.1.1a5` release on SBL with wheel + `SHA256SUMS` + 8-skill bundle (§14) |
| maintenance | `MAINTENANCE_EXIT / CANONICAL_MOVED_TO_SBL` merged in the PIPD README |
| archive | **done** — `archived=true` was read back on 2026-11-03 (§11.2); the earlier `ARCHIVE_ADMIN_HOLD` and its 403 are kept below as the measurement that preceded it |

### 11.1 Archive attempt — measured, not assumed

| step | result |
|---|---|
| capability | `GET /repos/shw097-team/PIPD-LS-SP` reports `permissions.admin = true`, but that is the *effective* permission of the account, not the scope of the token |
| no-op probe | `PATCH {"archived": false}` (a value the repository already holds, so the write changes nothing) → **403** `Resource not accessible by personal access token`, `documentation_url: /rest/repos/repos#update-a-repository` |
| real attempt | `PATCH {"archived": true}` → the same **403**; not retried |
| readback | `archived = false`, `pushed_at = 2026-11-03T00:25:31Z`, 5 open PRs still open |
| verdict at the time | **`ARCHIVE_ADMIN_HOLD`** — the credential lacks the repository-administration scope. No other credential was used and no archived state was claimed **at that measurement**; §11.2 records how it was resolved |

**Manual action for an admin:** Settings → General → Danger zone → *Archive this repository*, or a token with
**Administration: write** on this repository, then `PATCH /repos/shw097-team/PIPD-LS-SP {"archived": true}`.
After that single change, Fabric `INTEGRATION/FHS/repository-map.json` `historical_repositories.pipd.archived`
flips to `true` in a bounded PR — it stays `false` until the readback says otherwise.

### 11.2 Resolution (2026-11-03)

| step | result |
|---|---|
| action | the repository was archived by an administrator with the **Administration** scope — the same manual action named in §11.1 |
| readback | `GET /repos/shw097-team/PIPD-LS-SP` → `"archived": true`; tags, preview assets, `LICENSE` and `NOTICE` remain readable, and the 5 dispositioned pull requests remain open as history |
| Fabric | `INTEGRATION/FHS/repository-map.json` `historical_repositories.pipd.archived` `false` → `true`, `FHS-NAV/v2` not bumped; `validate_entry.py` now refuses `archived=false` (`HISTORICAL_ACTIVE_pipd`) and still refuses a non-bool; 30 FHS tests pass; PR [#26](https://github.com/shw097-team/Fabric/pull/26) merged as `f4f2ad7c…` with `fhs-nav-static` success |
| verdict | `ARCHIVE_ADMIN_HOLD` **released**; the 403 row above stays as the historical measurement, not as the current state |

## 12. Open PIPD pull requests — disposition (current)

| PR | disposition | evidence | next action |
|---|---|---|---|
| [#26](https://github.com/shw097-team/PIPD-LS-SP/pull/26) pre-v2 adapters | **merged in PIPD `7073fe2d`; ported to SBL** | its one real contract fix (`validate_bundle` must not call a 3-object bundle "complete") is now in SBL with 29 tests; the rest (design-only adapter, additive flags, four versioned sidecars) is ported; its "14 commands" docstring hunk was **dropped** | none — closed by the port (§13) |
| [#28](https://github.com/shw097-team/PIPD-LS-SP/pull/28) 13-commands docstring | **merged; nothing to port** | SBL's own docstring already states 13 verbs exactly; #28 only undoes #26's 14-command wording | none |
| [#20](https://github.com/shw097-team/PIPD-LS-SP/pull/20) oracle compatibility | **`TRANSFER_TO_SBL`** | 3 files; applies cleanly; its 12 tests pass on the absorbed tree | open against SBL when wanted |
| [#19](https://github.com/shw097-team/PIPD-LS-SP/pull/19) front-page limits | **`TRANSFER_TO_SBL`** | README-only; the claims it corrects are carried into `integrations/pipd/README.md` | re-apply in SBL |
| [#15](https://github.com/shw097-team/PIPD-LS-SP/pull/15) validator hardening | **resolved by §13** | the recorded gaps were real; both are now closed in SBL with POS/NEG tests | none; keep the PR as the round's evidence |
| [#22](https://github.com/shw097-team/PIPD-LS-SP/pull/22) R21 FAR | **`HISTORICAL_ONLY`** | 484 files, `mergeable=false`, adds `compile-cc` | no merge |

## 13. C4 source drift and validator hardening

**Drift from the two post-cutover PIPD merges.** #26's diff applies cleanly to `integrations/pipd` and was ported
except for its `cli.py` docstring hunk, which claimed 14 commands. The one substantive contract defect it fixed is
reproduced and closed: `validate_bundle` returned `{verdict: PASS, checked: 3, closure: FULL}` for a bundle with
TQAEP missing; it now returns `scope: PARTIAL_BUNDLE, missing: [TQAEP], complete: false` and `--require-four` fails
closed. Four additive sidecar schemas live under the private `urn:sbl:pre-v2-active:*:2` namespace and are **not** in
`registry.json`, so the 19-family ABI and the 13 verbs are unchanged.

**#15 hardening (both gaps were real).**

| gap | before | after |
|---|---|---|
| digest binding | the recompute-and-compare was gated to the five release-bound families; an edited `RequirementAtom`, `EvidenceExpectation` or `ClaimCeiling` validated clean and `validate_bundle` said PASS | the digest is verified for every family that carries one; the same edits are refused |
| oracle polarity | no invariant compared `risk_guard.oracle.expected` or `acceptance_cue` with `risk_guard.polarity`; `MUST` + `expected="forbidden"` was accepted, as were undeclared tokens (`MAY`, `must`, `''`, `None`) | `MUST` must be evidenced by `expected="required"`, `MUST NOT` by `"forbidden"`, the cue must state its own polarity, and the check also runs on atoms nested in a PI |

Tests: `tests/test_validate_hardening.py` (13 tests, POS 3 / NEG 10) plus the four-object suite
(`tests/test_validate_four_objects.py`, 4 tests) and the ported pre-v2 suites (25 tests). Six synthetic fixtures
that carried placeholder hashes (`"a"*64`) were re-sealed with their real body hash — the fixtures were wrong,
not the check.

## 14. Published distribution

| artefact | value |
|---|---|
| release | SBL `pipd-ls-sp-v0.1.1a5` |
| wheel | `pipd_ls_sp-0.1.1a5-py3-none-any.whl` — 325 619 B, sha256 `ff3d0f69a509df36d301d6ab631ecc723c3a2594ceaf656e42582f7359050418` |
| skills bundle | `sbl-tpm-sp-skills-0.1.1a5.zip` — 57 045 B, sha256 `418c33f3397ac9564fa881b2a747a4bedf97dc2510c2c301bca3b6c7924a4a95`, 8 skills derived from `integrations/pipd/skills` |
| install verification | a clean Python 3.11 venv created outside the repository installs the wheel **from the release URL**, imports `pipd_ls_sp`, lists 13 commands, reports 19 families, and cannot import `sbl_core` |

## 15. Final closeout

| item | value |
|---|---|
| SBL canonical source | `main` `2560970` → this document's PR; compiler, 19 families, 8 skills under `integrations/pipd/` |
| distribution | [`pipd-ls-sp-v0.1.1a5`](https://github.com/shw097-team/SBL/releases/tag/pipd-ls-sp-v0.1.1a5) — wheel `ff3d0f69…`, 8-skill bundle `418c33f3…`, installed and exercised from the public URL |
| PIPD | `archived=true` (read back 2026-11-03); maintenance frozen; nothing deleted or rewritten |
| Fabric FHS | `FHS-NAV/v2`; PR [#26](https://github.com/shw097-team/Fabric/pull/26) merged as `f4f2ad7cbed97074cc2d78b401734fc47633cc20`; `fhs-nav-static` success; three active repositories + one historical (`archived=true`, `write_authority=NONE`) |
| FHS invariants kept | six task classes, `pipd_canonical` → `sbl`, `unknown_route=HOLD_AFFECTED_WRITE_ONLY`, `effect_permission=NONE`, `source_state=PROPOSED_NOT_OWNER_RATIFIED`, historical repository never a route target, affected repository or HEAD sample |
| claim ceiling | `U04_FULL_PROGRAM = CLOSED_SCOPED` for the product source and repository consolidation. **Not claimed:** HGK Permit / Native Admission, Fabric Policy Effect, Hermes Host Loaded, Production or store release, Independent Acceptance, and any revival of the PIPD writer |
