# FHS Engineering Entry (Fabric-hosted, GitHub navigation deployed)

**NAVIGATION_ONLY · NOT OWNER RATIFIED · NOT AN ISSUER · NOT A COMPILER · NOT A CHECKER.**

## State, stated precisely

| layer | state | what it means |
|---|---|---|
| **GitHub navigation** | `GITHUB_NAV_DEPLOYED / FHS-NAV/v2` | this page and `repository-map.json` are versioned on Fabric `main`, reachable from the Fabric front page, and readable by an external engineer without a private workspace path |
| **Assisted navigation use (L1)** | `NAV_ASSISTED_USE_APPROVED` | Hermes / engineering AI may use this entry as a **read-only** starting point: task-classification proposal, original-source location, affected-domain identification, and candidate planning or drafting. The static route is a suggestion — the original domain reader decides, and an unknown or mismatched task holds only the affected write. See [the L1 decision](DEPLOYMENT-AND-OWNER-DECISIONS.md#7-l1-assisted-navigation-use--nav_assisted_use_approved). `effect_permission=NONE` is unchanged. |
| **Original domain / native** | `ORIGINAL_DOMAIN / NATIVE_NOT_RATIFIED` | every route below is a **pointer**; no original owner has ratified it as a native reader, no native admission, host load, permit or acceptance has been obtained, and no write authority is granted |

`source_state` remains `PROPOSED_NOT_OWNER_RATIFIED` in `repository-map.json`. `FHS-NAV/v2` changed route
targets only: it retired PIPD-LS-SP from the active set and pointed `pipd_canonical` at the SBL-hosted
compiler. It did not add a route, a state or a permission, and did not change `INTEGRATION/MANIFEST.json`.
`effect_permission` stays `NONE`, `unknown_route` stays `HOLD_AFFECTED_WRITE_ONLY`.

This directory is a single non-authoritative engineering index. It has no repository or native write permissions. The existing Fabric `INTEGRATION/MANIFEST.json` governs the mirror and must not be silently expanded.

| Task class | Public source pointer | Original reader and next action | Affected repositories |
|---|---|---|---|
| `sbl_product` | [SBL TPM Skill](https://github.com/shw097-team/SBL/blob/main/sbl_sp/plugins/tpm_sp/SKILL.md) | SBL Product Reader; verify the SBL-hosted canonical compiler binding before handoff | Fabric |
| `fabric_policy` | [Fabric source projection](https://github.com/shw097-team/Fabric/blob/main/INTEGRATION/SOURCE-PROJECTION.md) | This is a **mirror**, not the authoritative Policy Reader. Ask original Fabric Policy Owner and HGK consumer | HGK |
| `hgk_admission` | [HGK source export](https://github.com/shw097-team/HG-KSEOS/blob/main/README.md) | Original HGK Native Issuer / permit / consumer readback is REQUIRED; GitHub is insufficient | Fabric, SBL |
| `pipd_canonical` | [SBL canonical compiler pipeline](https://github.com/shw097-team/SBL/blob/main/integrations/pipd/src/pipd_ls_sp/pipeline.py) | SBL canonical source reader; the PIPD ABI (13 commands, 19 contract families) is now maintained in `integrations/pipd/` and must be re-checked there, not in the retired repository | Fabric |
| `cross_repo` | Each affected original repository | Make separately scoped PR candidates. Shared ChangeSet ID is not HGK WorkID | SBL, Fabric, HGK |
| `hermes_runtime` | **MISSING: original host source link must be resolved** | Fresh profile / PID / loaded / invoked / ActualServed from original Host Reader, not GitHub | HGK, Fabric |

An unknown task class is not guessed: `repository-map.json` declares
`unknown_route=HOLD_AFFECTED_WRITE_ONLY`, so the affected write is held while permitted source reads and
local drafts continue.

## Historical repository (not an active route target)

`shw097-team/PIPD-LS-SP` is listed under `historical_repositories`, not under `repositories`:

| field | value |
|---|---|
| role | `HISTORICAL_CANONICAL_MOVED_TO_SBL` |
| archived | `true` — archived on GitHub on 2026-11-03 and read back from the API (`shw097-team/PIPD-LS-SP`); it stays public and readable, and its tags and assets are unchanged |
| write authority | `NONE` — no route may target it, and it is never HEAD-polled |

It keeps its tags, preview assets and licence as the release record of the pre-cutover line. The canonical
compiler moved to SBL in the U04 cutover; the control record is SBL
[`docs/pipd-migration/U04-CUTOVER.md`](https://github.com/shw097-team/SBL/blob/main/docs/pipd-migration/U04-CUTOVER.md).

To statically validate from the Fabric repository root:

```bash
python3 INTEGRATION/FHS/validate_entry.py
python3 INTEGRATION/FHS/validate_entry.py --route pipd_canonical
python3 -m unittest discover -s INTEGRATION/FHS/tests -v
```

`STATIC_VALID_ONLY` does **not** mean GitHub merge, native acceptance, actual host load, release, or cross-repository write authority. Online HEAD comparison requires an external, operator-provided fresh expected-head snapshot (three repositories in v2 — a snapshot carrying `pipd` is refused) and is still only GitHub-source observation.

If the index is missing or stale, read each repository's original README/AGENTS or approved Source Reader. HOLD only the affected write; permitted source reads and local drafts may continue. PIPD-LS-SP is the historical line; new compiler work belongs to SBL.

The deployment and the owner-decision record behind it — including the L1 assisted-use approval — are in
[`DEPLOYMENT-AND-OWNER-DECISIONS.md`](DEPLOYMENT-AND-OWNER-DECISIONS.md).
