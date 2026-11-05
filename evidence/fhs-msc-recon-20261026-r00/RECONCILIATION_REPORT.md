# FHS-MSC R00 reconciliation candidate

Task: `FHS-MSC-CODEX-R00-RECON-PUBLISH/2026-10-26-r1`  
Observed: 2026-10-26T10:49:32+08:00 (Asia/Taipei); collection began approximately 10:36 and ended at this timestamp.  
Ceiling: **DESIGN_BASELINE_EVIDENCE_CANDIDATE**. No Native acceptance, SourceFreeze, independent AO, runtime repair or Release is issued.

Gate A: PARTIAL. All four specified roots have honest results; readable Git identities and four complete remote main Trees are verified. Private/long-path enumeration and active runtime readback remain incomplete.  
Gate B: PUBLICATION_REVIEW_PASS applies only to these four newly derived files, subject to the recorded final scanner/guard result in the caller session. Other source/host material remains excluded.  
Gate C: PREPUBLICATION_SNAPSHOT. This immutable file predates push; actual publication commit, remote byte verification and Draft PR are returned separately in the caller session. It does not attest to its own later publication.

## LOCAL_REMOTE_INVENTORY

Local roots were checked with Test-Path/Get-Item and git rev-parse, with optional locks disabled. All three found roots are true Git worktrees with ordinary root/ancestor directories, separate .git directories and no superproject reported. The fourth specified path is MISSING. No source fetch/pull/checkout/reset/clean/add/commit/install/build was performed.

| Local root alias | HEAD | tracked | modified | staged | untracked observed | ignored observed |
|---|---|---:|---:|---:|---:|---:|
| HG-KSEOS | `086a9402189a2bb0ac3b198a7a9805b3dcbe38d8` | 785 | 2 | 0 | 1 | 187846 |
| Fabric | `bb06b7a6c17c45c777a636e9dae3196e21eb77b9` | 4264 | 1 | 0 | 51 | 9 |
| SBL | `10d510f7b052e6139fd4eb536f970c0245002e17` | 456 | 0 | 0 | 55369 | 17818 |
| PIPD-LS-SP | `MISSING` | - | - | - | - | - |

All three found worktrees are dirty when untracked entries count. HGK branch `codex/hgk-final-closure-002` has no remote or upstream; Fabric branch `pub/far-minimax-mandate-20261021` has sanitized origin matching the intended Fabric repository, cached upstream ahead 2/behind 0; SBL branch `candidate/r14-ts15-kinds` has intended SBL origin and no upstream. HGK/Fabric/SBL observed nested repositories: at least 107/3/224; traversal did not follow reparse directories or enumerate secret-shaped directories. HGK had 17 reparse directories and 983 traversal errors. SBL long-path queries still emitted 60 untracked and 65 ignored warning lines. Counts with warnings are lower bounds, not a complete private denominator. Earlier default-path observations (SBL untracked 52115, ignored 17770) used a narrower traversal; they must not be interpreted as new files created by this task.

Root aliases mean the user-designated source roots. Exact machine paths remain in the private caller session. No new persistent private inventory registry was created. The public matrix uses exact safe repository-relative locators and aggregates quarantined untracked/private sets; per-item private provenance is NOT_VERIFIED.

| Remote (all default main) | current full HEAD | current Tree | entries (trees included) |
|---|---|---|---:|
| Fabric | `bcd91043b89b69c9d2f08309e46e31898ac87d89` | `83b65a65207e4c14bed9a49ea6f755eebd0ca433` | 4774 |
| SBL | `dc5428f23d15f0ec56cbc3d25b22f5381fce8771` | `3f95125c5fe1d5436e1b0a112753d91f5a7e2af7` | 278 |
| PIPD-LS-SP | `e95942abcb6aa07e69304607ab8afc22a74fc67d` | `1a929d1b7c609fc0e9e70df0edb3bddaaee214c1` | 2389 |
| SWOF | `acdbfaadd19d12927eb5bd542b09ed230bbc481e` | `438dce18cdae6e2bb6a9543b8f4643562655ff10` | 18 |

GitHub metadata IDs: Fabric 1404471533; SBL 1426519274; PIPD-LS-SP 1410587331; SWOF 1401572664. All recursive main Trees returned truncated=false. Independent unauthenticated git ls-remote HEAD agreed for all four. Current rulesets including parents returned empty and main protected=false; this does not replace Native authority. Latest sampled main CI: SBL success run 39630610337; PIPD success run 38929072130; Fabric/SWOF query returned no runs. No product suites were rerun. Tags: Fabric 0, SWOF 0, PIPD 6; SBL 13 including archive tags and preview tags v0.1.0-foundation-preview/v0.1.1rc1; tag presence is not product acceptance.

Open PR snapshot:
- Fabric [#17](https://github.com/shw097-team/Fabric/pull/17): OPEN, draft=false, head `d0bae0a761781a4e77c7ce206369a1998a523b2f`.
- Fabric [#16](https://github.com/shw097-team/Fabric/pull/16): OPEN, draft=false, head `09b11bd235ef72f2d5690e100e1969b6537eecda`.
- Fabric [#15](https://github.com/shw097-team/Fabric/pull/15): OPEN, draft=false, head `a22ad7e17559d787f6220ce07a161105cb32fad2`.
- SBL [#11](https://github.com/shw097-team/SBL/pull/11): OPEN, draft=true, head `bf3cccfe7abd94053eb147b586da4f9f95815921`.
- SBL [#10](https://github.com/shw097-team/SBL/pull/10): OPEN, draft=true, head `dbacbd304564ff52cbffe42fed080e8020e13103`.
- SBL [#9](https://github.com/shw097-team/SBL/pull/9): OPEN, draft=true, head `7b772b3d9a687c164f63b50a6e7f93bc7fb31f2f`.
- PIPD-LS-SP [#19](https://github.com/shw097-team/PIPD-LS-SP/pull/19): OPEN, draft=false, head `3e35c1ceaf07187773ea30a2f9cda48368e6a1f9`.
- PIPD-LS-SP [#15](https://github.com/shw097-team/PIPD-LS-SP/pull/15): OPEN, draft=true, head `eae636d8668027887977a797b20e63899465ad8d`.
- PIPD-LS-SP [#14](https://github.com/shw097-team/PIPD-LS-SP/pull/14): OPEN, draft=true, head `d89e7f33ec14aa6fc14c35f3ad6c6202d7fc0d00`.
- SWOF [#7](https://github.com/shw097-team/SWOF/pull/7): OPEN, draft=true, head `c333e47141393b4f6c39a13f70c96b31190f3c3d`.
- SWOF [#6](https://github.com/shw097-team/SWOF/pull/6): OPEN, draft=true, head `bffe540ffbab683127338a4bd94b2f7d4bb39cce`.
- SWOF [#5](https://github.com/shw097-team/SWOF/pull/5): OPEN, draft=false, head `ca463f1ab3206e4065d424e96e3feebfd371b7a2`.
- SWOF [#4](https://github.com/shw097-team/SWOF/pull/4): OPEN, draft=true, head `7e1f912d863b8c155eb9ae5ae9682b0e185450fc`.
- SWOF [#3](https://github.com/shw097-team/SWOF/pull/3): OPEN, draft=true, head `ed28b784fcae651897fe261120db7840134d0028`.
- SWOF [#2](https://github.com/shw097-team/SWOF/pull/2): OPEN, draft=true, head `8689e583bab5198be11fb31442f5ac95d8490c00`.
- SWOF [#1](https://github.com/shw097-team/SWOF/pull/1): OPEN, draft=true, head `0ddf00be6bd779b375368d5f4e647d8bccf1b81b`.

## DRIFT_MATRIX

`DRIFT_MATRIX.tsv` has 471 safe rows; entry_count aggregates explicitly marked sets. Git HEAD comparisons: Fabric local-only 119, remote-only 0, changed 4, identical 4141 blobs; SBL local-only 273, remote-only 42, changed 18, identical 165 blobs. These compare committed trees, not dirty working bytes. Fabric main-to-local is 0 behind / 14 ahead; local HEAD is not advertised in current heads/tags and GitHub compare returned 404, so exact unpublished commit count remains NOT_VERIFIED. SBL GitHub compare independently returned diverged (46 ahead/26 behind); those 46 are NOT labelled unpushed merely because they differ from main.

Fixed classes all retained: TRACKED_UNPUSHED, UNCOMMITTED_WORK, UNTRACKED_CANDIDATE, REMOTE_ONLY, MIRROR_PROJECTION, LIVE_RUNTIME_ONLY, EVIDENCE_LOCAL_ONLY, SOURCE_DUPLICATE_OR_DRIFT, STALE_CANDIDATE, SECRET_OR_PRIVATE_STATE, UNKNOWN_PROVENANCE. Sensitive-shaped committed-tree differences omitted: {'Fabric': 3}. Subject algorithms are explicit; Git blob SHA-1 is not SHA-256. Configuration dirty subjects have no published digest.

## EFFECTIVE_HOST_AND_CANDIDATE_MAP

Git 2.53.0.windows.1; codex-cli 0.164.0-alpha.11.1 (actual --version). Codex desktop app build NOT_VERIFIED. Get-Command hermes resolved the approved Recovery launcher; where.exe additionally showed the user-local launcher. Launcher ancestors had no reparse points. Static launcher code points to the discovered hermes-agent checkout HEAD `f97608f178d1ffeca59860195ab7da295f7c8e5f`, declaring `__version__=0.21.5`. This is SOURCE_DECLARED_VERSION, not a runtime version result. The HGK AGENTS binding describes older v0.20.0/3c27eb62: SOURCE_DUPLICATE_OR_DRIFT pending Host Owner reconciliation, not automatic supersession.

Hermes main.py lines 24-28 and 55-65 call interrupted-pull/install recovery before ordinary argument handling. Therefore --help/--version were not executed: READONLY_CLI_NOT_ASSURED. Capabilities are STATIC_DECLARATION_ONLY (chat/gateway/setup/status/cron/doctor/update). No named Hermes process/service was visible through the bounded query; Python-hosted activity remains unverified.

Current executable SHA256 `c02538dd297474191546684681344c0ad859580a635047e577947b8bebd559e8`; launcher SHA256 `a9d680b00f163669b7edd9c002df6eda8e34267d6765249fc0b031ce610a487c`; CLI main.py SHA256 `3b89b46e67f35398ba0af6b3441172490469702cd0e4e0381ff7e45ea78b2eef`.

SBL PR11 CANDIDATE_SHA `bf3cccfe7abd94053eb147b586da4f9f95815921`, complete Tree 312 entries. Current exact R17 stage file byte reads matched that Tree's Git blobs:

| stage file | bytes | SHA256 | remote Git blob SHA1 |
|---|---:|---|---|
| runner.py | 33436 | 3522dfa6ff7de7a7eaeccddc5dd5a49764a89161d80619056f033622f4ed7615 | 533d8c8340cd78405fccda97af88c145e3388d6b |
| advance.py | 19396 | 337e67630663f12bdfebcaf4410e5b7f1963ed288a253d0b89070ab161ec8484 | 1636c6e08a36669993d104cf4d3028a52150e48d |

These are file-level STAGE_SHA identities; no whole-stage Git commit identity is asserted. LOADED_SHA=LOADED_UNVERIFIED; ACTIVE_JOB_REF=NOT_VERIFIED. The PR11 entrypoint receipt is dated historical evidence; its job/wrapper/module claims are not current native readback. Stage queue/dispatch ledger paths were identified from source declarations but their raw contents were not read. No secret config/DB/queue/checkpoint was read or service started/stopped.

## AUTHORITY_AND_OWNER_MAP

- User mandate authorizes read-only reconciliation and conditional SBL sanitized evidence publication. Canonical source, governance or runtime mutations remain outside this writeset.
- HGK AGENTS.md (SHA256 ce94f479b6095802dd25c36d2131d20f4c386810d7a89cd9eb496816e1bcb755) governs HGK source; only its readable identity was inspected. Native admission, kanban/swarm/gstack/openspec effects and model lanes were NOT invoked or claimed. No fresh checker/native permit was issued. A governed build remains HOLD_NATIVE_GATE.
- SBL main README and its effect scope retain CANDIDATE_ONLY / STANDALONE_ONLY. No root/evidence AGENTS or CODEOWNERS gate was found in the isolated main tree or designated source evidence chain. Current repository rulesets reveal no extra candidate-branch gate; this is bounded policy discovery, not a grant to modify products.
- Blueprint identity FHS-MSC-BLUEPRINT-2026-10-26-r2-SUBSTANTIVE-COVERAGE-REPAIR, sections 0.1/0.3/2.1/12: B0 before B1, no runtime AO/release, no self-issued Permit/SourceFreeze. Only these targeted clauses were consumed; the knowledge base was not recursively content-indexed.
- SBL DOC-00..13 current local KB bytes were recomputed: 14/14, total 17473442, rollup SHA256 01b972c80341e1b87db4fa6f20f61723564c609f0ff12282f9205679a4f9cf9d; all per-document values match current SBL main contracts/CONTROL_PACKAGE_MANIFEST.json. Identity match does not ratify source authority. No upstream DOC text was copied.
- PIPD Canonical DOC-00..09 authority, profiles/GRP and CR-ORACLE-001 require PIPD Source Owner disposition. No PIPD compilation was run. Fabric projections retain their separate Owners; HGK source HEAD tree d45e9ab8f48a1ea1df140180b9a49e6ed6ede50d differs from the Fabric/HG-KSEOS projection tree bdd55c16e7800980fb5dff2a80eb470d263bf58c.
- SWOF Owner retains W2 acceptance/merge and PRE-W3 gates: main remains W0 and W2 PR6/7 are open Draft candidates. No W3 readiness is asserted.

## PUBLICATION_DISPOSITION

Only the four new derived files under this bounded evidence subtree are SBL_PUBLIC_CANDIDATE. Exact machine/user paths, credentials, secret material, private KB text, raw runtime state and original host logs/configs are excluded by construction. Original source code, canonical DOCs and licensed governance material are OWNER_APPROVAL_REQUIRED; only safe locators/digests/gaps are included here. Dirty, nested, stale and unproven sets remain UNBOUND / QUARANTINE. Excluded file total is NOT_CENSUSED; do not treat zero scanner findings as rights approval.

The existing SBL main secret scanner will run on the actual four-file candidate and the publication guard will check the staged tree. Its digest and results are carried in final caller readback; no scanner result is Native acceptance. PUBLICATION_MANIFEST.tsv covers three other artifacts and excludes its own digest by construction. READBACK.json is a prepublication remote-baseline snapshot, not a fabricated post-push receipt. Final all-four bytes/Git blob/SHA256 verification is performed externally after push, avoiding a self-referential manifest or a second commit.

## OPEN_TT_AND_REPAIR_PLAN

1. PIPD_ROOT_MISSING / SOURCE_AUTHORITY_UNBOUND: PIPD Owner provides authoritative actual root and current DOC/GRP/Profile binding; decide CR-ORACLE-001. No compilation until authority holds are resolved.
2. LOADED_UNVERIFIED / READONLY_CLI_NOT_ASSURED: Hermes/HGK Host Owner supplies permitted current module/binary/job/lease readback. Do not trigger CLI recovery merely to learn a version.
3. DIVERGED_LOCAL_CANDIDATE / REMOTE_REACHABILITY_UNVERIFIED: SBL/Fabric Owners select intended product baseline, classify local-only/dirty/untracked evidence, and authorize any subsequent bounded source repair separately.
4. PRIVATE_INVENTORY_INCOMPLETE: Host Owner provides a specifically approved private Evidence Store and resolves inaccessible/long-path/reparse categories if a full private denominator is needed. This report does not invent that store or publish its contents.
5. HOLD_NATIVE_GATE: HGK Issuer and independent Checker remain unbound for effects. Commander may prepare a NEXT_WORK_REQUEST for authority/readback gaps; this report is not a runtime repair order or PI/PD/ECP/TQAEP completion.

Preserved denominators: R17 145-ID product obligations remain open (R17 vol05 lines 101-103; Fabric canary separate); R15.1 sections 2-16 / blueprint section 11 retain the 949 atoms, 42 audit findings, 3 SP, 6 modules, 3 Golden Journeys, four Host x three SP and R13 18 reds. Historical R17 vols01-05 and original SBL/PIPD DOC denominators are retained by locator, NOT_EXECUTED/NOT_REQUALIFIED. No 949/42/full R17 suite was rerun and no completion fraction is claimed.

Rollback for this evidence-only publication: leave the unmerged branch unconsumed; an Owner may close the Draft PR. No automatic branch deletion, merge, release, source restore or runtime rollback is performed.
