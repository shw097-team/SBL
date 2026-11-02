# Host Capability Inventory

- Date: 2026-11-02 (Asia/Taipei)
- Scope: `gj02-repo` plus the `sbl-tpm-sp` plugin currently visible to this Codex Host.
- Inventory method: followed the `sbl-tpm-sp:tpm-setup` skill instructions, then probed the actual local Host, plugin cache, corpus reader, Git context and Python test entry. No capability was accepted merely because a manifest declared it.

## Claim Ceiling

**Overall Host readiness: `HOST_PENDING`.** The package declares `claim_ceiling: HOST_PENDING` and `host_install_state: NOT_INSTALLED`; this session observed a local cache and loaded skills, but found no Host receipt or native qualification. Under the skill rule, no Host receipt means `HOST_PENDING`.

Other ceilings apply independently:

| Area | Ceiling | Meaning |
|---|---|---|
| Host/skill readiness | `HOST_PENDING` | Local execution was observed, but formal Host qualification was not performed. |
| Corpus | `PHYSICAL_INTEGRITY_ONLY` | All 24 files matched the manifest SHA under an extended Windows path. Source authority/ratification is still unverified. |
| Target SPECs | `AUTHOR_DESIGN_ONLY` | Product, Architecture and Program drafts are design candidates, not canonical or accepted artifacts. |
| Original PIPD compiler/reader | `EXECUTOR_UNBOUND` | No original compiler/reader, protected checker or receiver was bound in this Host. |
| Release/native acceptance | Not claimed | No Publisher release, Native W0-W3 run, independent acceptance or Mission Complete claim. |

## Host Summary

- Codex CLI: `0.164.0` (`<HOME>\AppData\Roaming\npm\codex.ps1`).
- Configured model: `deepseek-v4.1-flash`; provider: `opencode_go`.
- OS/shell: Windows `10.0.26200.0`; PowerShell `7.6.9`.
- Python: `3.14.9` at `D:\Hermes-Recovery\live22\installs\3b763fa5cf79ba4a\environments\fef3df20083a4a92a5d98969b736e5a5\venv\Scripts\python.exe`.
- Git: `2.53.0.windows.1`.
- Filesystem/process capability: unrestricted filesystem access, approval policy `never`, shell execution available.
- Repository trust: `trust_level = "trusted"` for this repo in `CODEX_HOME/config.toml`.

## Plugin Inventory

| Item | Observed value |
|---|---|
| Plugin name/version | `sbl-tpm-sp` `0.3.0-rc.2` |
| Marketplace | `sbl-pre-primary-local` (local source) |
| Enablement | `[plugins."sbl-tpm-sp@sbl-pre-primary-local"] enabled = true` |
| Cache path | `CODEX_HOME/plugins/cache/sbl-pre-primary-local/sbl-tpm-sp/0.3.0-rc.2` |
| Skills present | 14 directories with `SKILL.md` |
| Stage contracts | 18 total: 6 PM, 6 SE, 6 TPgM |
| Target plugin identity | `Plugin_e787f67d86548191ae484c9ab4eb78ab` |
| Observed account release | `pluginrel_6ae839cbc3c88191a906f64d31f0e449`, version `0.3.0-rc.1` |
| `0.3.0-rc.2` publication | Not published; official same-plugin update unavailable |

Source/cache key-file hashes match exactly:

| File | SHA-256 | Source = Cache |
|---|---|---|
| `plugin.json` | `48D704BCB0A175BAF718AA12F3332CB29A09299D39532469C74C7F953729A281` | Yes |
| `.codex-plugin/plugin.json` | `E4E2B3EFC53AE89723C2AAD08FA1336549F2ACB946273C9E0185FE684B38875E` | Yes |
| `references/corpus/SourceManifest.json` | `D2B5BFBD3489771DDF90897255CC416A0048FC6109E47BE4C6E658F2CB3AB761` | Yes |
| `PRE_V2_STATUS.json` | `73B450B768B31E4E732570901400F2C9C4C3CF4E646A1D2C2B08F0C750374FF0` | Yes |

## Capability State Matrix

States are recorded separately as required: `SELECTED`, `INSTALLED`, `BOUND`, `INVOKED`, `VERIFIED`.

| Capability | Selected | Installed | Bound | Invoked | Verified | Evidence / limit |
|---|---|---|---|---|---|---|
| `tpm-setup` skill | Yes | Yes, local cache | Yes, current session/repo | Yes | Session-only | `SKILL.md` was read and applied; no formal Host receipt. |
| Plugin package | Yes | Local cache present and enabled | Yes | Yes | Partial | Source/cache key hashes match; package itself still declares `NOT_INSTALLED`/`HOST_PENDING`. |
| Corpus SHA verifier | Yes | Yes | Yes, with `\\?\` root | Yes | Yes | `verify_corpus.py`: `PASS`, `core_docs: 24`, `PHYSICAL_INTEGRITY_ONLY`. |
| Corpus clause reader | Yes | Yes | Yes, with `\\?\` root | Yes | Yes, sample | `SBL-04` lines 466-475 returned the pinned SHA and `DESIGN_SOURCE_RATIFICATION_UNVERIFIED`. |
| Python runtime | Yes | Yes | Yes | Yes | Yes | `Python 3.14.9`; `jsonschema` is importable. |
| Git/repo probe | Yes | Yes | Yes, `master` | Yes | Yes | HEAD `70757870ef495b0c3c7193fbf35df1223f8a6566`; dirty state recorded below. |
| `pytest` runner | No | No | No | Attempted | No | `python -m pytest` fails: `No module named pytest`. |
| `PyYAML` dependency | Required by tests | No | No | Import attempted | No | `import yaml` fails; one author-test module cannot load. |
| Author test suite | Yes | Yes | Yes | Yes | Partial | 83 discovered: 82 passed, 1 import error, 0 failures; full 186-case claim not revalidated. |
| Original PIPD reader/compiler | N/A | Not proven | `UNBOUND` | No | No | No original compiler/reader or receiver available; formal transitions remain HOLD. |
| Host/native qualification | N/A | N/A | `UNVERIFIED` | No | No | No Host qualification, receipt, native W0-W3 or independent checker run. |
| ChatGPT executor | N/A | Not applicable here | `EXECUTOR_UNBOUND` | No | No | No ChatGPT Host/executor test in this run. |

## Corpus Inventory

- Manifest: `SBL.CorpusManifest@1`.
- Required/observed count: 24 = 10 PIPD (`PIPD-00` … `PIPD-09`) + 14 SBL (`SBL-00` … `SBL-13`).
- Unique source SHA values: 24.
- Total declared bytes: `21,510,675`.
- Clause index: `3,308` JSONL entries.
- All entries: `required = true`; `baseline_match = true`.
- Authority state for every entry: `DESIGN_SOURCE_RATIFICATION_UNVERIFIED`.
- Distribution for every entry: `OWNER_PRIVATE_CANDIDATE_ONLY`.
- Manifest authority state: `PHYSICAL_COPY_ONLY`.

The physical verification is valid only after using the Windows extended-path root. The normal path to `PIPD-02` is 271 characters and fails with `FileNotFoundError`; the file is present and its SHA matches when accessed through `\\?\C:\...`.

## Target Repository Snapshot

- Root: `C:\Projects\Agent_Workspace\_run_sbl_tpm_sp_20261102\RUN-20261102-GJ02-01\shadow\gj02-repo`.
- Branch/HEAD: `master` / `70757870ef495b0c3c7193fbf35df1223f8a6566`.
- Working tree: dirty. `src/demo/billing.py` is modified; `specs/` and Python bytecode caches are untracked.
- Non-cache files: `src/demo/billing.py`, `tests/test_billing.py`, and three SPECs.
- `AGENTS.md`: absent.
- SPEC status: all three are `DESIGN_CANDIDATE`, with `claim_ceiling: AUTHOR_DESIGN_ONLY`.
- Repo tests: two pytest-style test functions pass when invoked directly; the configured `pytest` runner is unavailable.

## Unverified Items and Holds

1. **No Host receipt:** this was an actual Codex session, but no signed or owner-ratified Host qualification exists for `0.3.0-rc.2`. Host evidence in `PRE_V2_STATUS.json` belongs to `0.3.0-rc.1` only.
2. **Versions are split:** local cache and manifests are `0.3.0-rc.2`; the observed account release is `0.3.0-rc.1`; `0.3.0-rc.2` is not published.
3. **SETUP contract gap:** `stage-contracts.json` contains no `role: SETUP` entries; it has only PM/SE/TPgM contracts. The skill instruction to read SETUP entries could not be satisfied from that file, so only the skill body, pre-v2 routing and delivery status were used.
4. **Corpus authority is unratified:** all 24 sources are private candidate copies; their origin paths are stale/not found and no source owner ratified them. A SHA pass is not a source-authority or normative-content verdict.
5. **Windows long-path limitation:** default Python path handling cannot open the 271-character `PIPD-02` path; `\\?\` works. This workaround was not part of a Host qualification.
6. **Incomplete dependency set:** `PyYAML` is required but absent; `pytest` is absent. The author-test entry therefore does not prove the full advertised suite.
7. **Original execution chain unbound:** original PIPD compiler/reader, protected checker, receiver, effect registry and Native W0-W3 remain unavailable or unrun.
8. **Source volatility:** the repository is dirty at inventory time, so the snapshot is not a clean release boundary. Any later HEAD or working-tree change requires rebinding.
9. **No release claim:** local corpus integrity, SPEC drafts, a package seal or this inventory cannot be promoted to Granted, Qualified, published, accepted or Mission Complete.
