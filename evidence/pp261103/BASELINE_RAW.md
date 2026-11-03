# CT-00 BASELINE - TPM pre-repair acceptance round

- generated_at: `2026-11-03T09:42:09+08:00`
- run dir: `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103`
- every value below is the stdout of the command printed with it; every command is numbered and repeatable


## Identity chain

1. SOURCE: sbl-tpm-sp-0.3.0-rc.2-private.zip sha256 3a9da65561ab19cad90a6d7cbfb2eae0abf59b87ba565a118790bce5612326a8, 173 members (173 files, 0 dir entries), 14 SKILL.md, top dir sbl-tpm-sp, plugin.json version 0.3.0-rc.2
2. INSTALLED: C:\Projects\Agent_Workspace\_run_sbl_tpm_sp_20261102\RUN-20261102-GJ02-01\shadow\codex-home\plugins\cache\sbl-pre-primary-local\sbl-tpm-sp\0.3.0-rc.2 (plugin sbl-tpm-sp@sbl-pre-primary-local, version 0.3.0-rc.2, plugin.json sha256 48d704bcb0a175baf718aa12f3332cb29a09299d39532469c74c7f953729a281, 14 SKILL.md)
3. ENABLED: config.toml [plugins."sbl-tpm-sp@sbl-pre-primary-local"] enabled = true; install/remove/restore receipts in raw/ (host_final_add, host_reinstall, host_remove, plugin_list_installed|removed|final)
4. LOADED/USED: NOT ESTABLISHED for 0.3.0-rc.2 - requires a fresh codex host run; none exists and none was produced by this round
5. BUILD INPUTS: PIPD worktree fix/cli-docstring-count @ 75fe7de25f with 13 CLI subparsers and 19 schema families; ZIP and installed plugin.json are byte-identical (48d704bcb0a1...)

## 1. rc.2 ZIP

| field | value |
|---|---|
| path | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip` |
| sha256 | `3a9da65561ab19cad90a6d7cbfb2eae0abf59b87ba565a118790bce5612326a8` |
| member_count | `173` |
| file_count | `173` |
| directory_entries | `0` |
| duplicate_member_names | `0` |
| skill_md_count | `14` |
| plugin_json_version | `0.3.0-rc.2` |
| plugin_json_sha256 | `48d704bcb0a175baf718aa12f3332cb29a09299d39532469c74c7f953729a281` |
| top_level_dir | `sbl-tpm-sp` |

skills inside the archive:
- `sbl-tpm-sp/skills/pipd-assurance-tqaep/SKILL.md`
- `sbl-tpm-sp/skills/pipd-authority-source/SKILL.md`
- `sbl-tpm-sp/skills/pipd-execution-contract/SKILL.md`
- `sbl-tpm-sp/skills/pipd-package-project/SKILL.md`
- `sbl-tpm-sp/skills/pipd-pd-bind/SKILL.md`
- `sbl-tpm-sp/skills/pipd-pi-compile/SKILL.md`
- `sbl-tpm-sp/skills/pipd-profile-tailor/SKILL.md`
- `sbl-tpm-sp/skills/pipd-route-intake/SKILL.md`
- `sbl-tpm-sp/skills/tpm-handoff/SKILL.md`
- `sbl-tpm-sp/skills/tpm-product-plan/SKILL.md`
- `sbl-tpm-sp/skills/tpm-program-plan/SKILL.md`
- `sbl-tpm-sp/skills/tpm-setup/SKILL.md`
- `sbl-tpm-sp/skills/tpm-sp/SKILL.md`
- `sbl-tpm-sp/skills/tpm-system-plan/SKILL.md`

## 2. Installed copy (isolated CODEX_HOME)

| field | value |
|---|---|
| host | `codex-cli 0.164.0` |
| codex_home | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home` |
| cache_path | `C:\Projects\Agent_Workspace\_run_sbl_tpm_sp_20261102\RUN-20261102-GJ02-01\shadow\codex-home\plugins\cache\sbl-pre-primary-local\sbl-tpm-sp\0.3.0-rc.2` |
| plugin_ref | `sbl-tpm-sp@sbl-pre-primary-local` |
| plugin_json_version | `0.3.0-rc.2` |
| plugin_json_sha256 | `48d704bcb0a175baf718aa12f3332cb29a09299d39532469c74c7f953729a281` |
| plugin_json_matches_zip | `True` |
| skill_md_count | `14` |
| identity_level | `INSTALLED + ENABLED (recorded host action); LOADED/USED NOT ESTABLISHED` |

**Installed/Loaded wording.** This is the Installed + Enabled identity only. **Loaded/Used requires a host run** - an actual codex session that loads the plugin, shows 14 skills, fires an explicit trigger plus a nontrigger and returns ActualServed. No such receipt exists for 0.3.0-rc.2; the only loaded evidence in `HOST_ACTUAL_USED.json` is explicitly carried from 0.3.0-rc.1 and must not be read as rc.2 qualification.

Prior-run receipts read (not re-executed):

- install_receipt: `Added plugin `sbl-tpm-sp` from marketplace `sbl-pre-primary-local`.`
- reinstall_receipt: `Added plugin `sbl-tpm-sp` from marketplace `sbl-pre-primary-local`.`
- remove_receipt: `Removed plugin `sbl-tpm-sp` from marketplace `sbl-pre-primary-local`.`
- list_installed: `5:sbl-tpm-sp@sbl-pre-primary-local  installed, enabled  0.3.0-rc.2  C:\Projects\Agent_Workspace\_run_sbl_tpm_sp_20261102\RUN-20261102-GJ02-01\shadow\codex-case\plugins\sbl-tpm-sp`
- list_after_remove: `5:sbl-tpm-sp@sbl-pre-primary-local  not installed           C:\Projects\Agent_Workspace\_run_sbl_tpm_sp_20261102\RUN-20261102-GJ02-01\shadow\codex-case\plugins\sbl-tpm-sp`
- list_final: `5:sbl-tpm-sp@sbl-pre-primary-local  installed, enabled  0.3.0-rc.2  C:\Projects\Agent_Workspace\_run_sbl_tpm_sp_20261102\RUN-20261102-GJ02-01\shadow\codex-case\plugins\sbl-tpm-sp`

Second cache copy under the same CODEX_HOME:

- path: `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home/plugins/cache/created-by-me-remote/sbl-tpm-sp/0.3.0-rc.2`
- remote_plugin_id: `Plugin_e787f67d86548191ae484c9ab4eb78ab`
- SKILL.md: 14; plugin.json sha256 `48d704bcb0a175baf718aa12f3332cb29a09299d39532469c74c7f953729a281`; referenced in config.toml: False

## 3. PIPD

| field | value |
|---|---|
| source_path | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` |
| worktree_gitdir | `gitdir: C:/Projects/Agent_Workspace/PIPD/.git/worktrees/pipd-wt` |
| branch | `fix/cli-docstring-count` |
| head | `75fe7de25ff3d40544080ce94c4ef05be7dc335e` |
| head_subject | `75fe7de 2026-11-03 00:58:19 +0800 docs(cli): the registry has 13 commands, not 14` |
| dirty_count | `1` |
| package_version | `0.1.1a4` |
| cli_subparser_count | `13` |
| add_parser_source_count | `13` |
| schema_registry_id | `PIPD-S0-CONTRACT-REGISTRY/1` |
| schema_family_count | `19` |
| schema_registry_sha256 | `85100a8e5ba6320f6648d33a14099fb999b2c452a94aff1652854d2550065e9d` |

subcommands: `bind-pd compile-ecp compile-pi compile-tqaep diff doctor export init intake profile project repair validate`

schema families: `ArtifactIdentity AuthorityBinding RequirementAtom ProfileBinding TechnologyAdmission PI-PKG PD-PKG TraceLink TaskSpecSeed ConstructionContract WorkOrderCandidate ECP TQAEP ExecutionHandoff EvidenceExpectation ClaimCeiling SurfaceProjectionManifest GENIEProjectionRef ExecutionBindingRef`

## 3b. Writer drift: canonical PIPD is now inside SBL main

A sibling task dropped `DRIFT_NOTE.md` beside this file during the round. Its claims were re-measured here:

| field | value |
|---|---|
| sbl_local_main_ref | `bedc11957d4fc2474b249b69d200829272c118ef` |
| sbl_origin_main_ref | `b7445b0abb5d0f07f7d46d6bc11a9f165bf599d8` |
| sbl_origin_main_subject | `b7445b0 2026-11-03 09:15:27 +0800 U04: close C4 — the archive happened, and FHS now says so (#24)` |
| sbl_main_worktree | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main` |
| sbl_main_worktree_head | `b7445b0abb5d0f07f7d46d6bc11a9f165bf599d8` |
| sbl_main_worktree_ref | `HEAD` |
| sbl_main_worktree_dirty | `0` |
| sbl_main_pipd_version | `version = "0.1.1a5"` |
| sbl_main_pipd_cli_verbs | `13` |
| sbl_main_pipd_expected_families | `19` |
| sbl_main_pipd_registry_families | `19 PIPD-S0-CONTRACT-REGISTRY/1` |
| sbl_main_pipd_schema_files | `20` |

Reading: the packaged candidate (this round's ZIP) was built from the legacy PIPD worktree, but the canonical writer tree now is SBL origin/main `b7445b0abb` → `integrations/pipd` at `version = "0.1.1a5"`. That tree independently reproduces 13 CLI verbs and 19 expected schema families, so the 13/19 expectations survive the drift.

## 4. Four repos

| repo | toplevel | branch | HEAD | dirty |
|---|---|---|---|---|
| SBL | `C:/Projects/Agent_Workspace/SBL` | `candidate/r14-ts15-kinds` | `826ca066a1c2df2976c0d402018b79e1c79a444f` | 47 (`4  M;     43 ??;`) |
| PIPD | `C:/Projects/Agent_Workspace/PIPD` | `candidate/r21-far-20261101` | `3b48c262f4174217cb35391c6da22bc53f068755` | 239 (`3  M;    236 ??;`) |
| Fabric | `C:/Projects/Agent_Workspace/Fabric` | `far/far-031-fhs-msc-all-pass-20261031` | `765df6289cfb7730aa56efbd522d76df6ec9809a` | 6 (`2  M;      4 ??;`) |
| HG-KSEOS | `C:/Projects/Agent_Workspace/HG-KSEOS` | `candidate/r18-fhs-skeleton-spine-20261029` | `f5474257aa7d2005937867340f4cd01b39751129` | 2 (`2 ??;`) |

## 5. Host

| field | value |
|---|---|
| codex | `codex-cli 0.164.0` |
| python | `Python 3.14.9` |
| git | `git version 2.53.0.windows.1` |
| pwsh_on_path | `C:\Users\user\AppData\Local\Microsoft\WindowsApps\pwsh.exe` |
| pwsh_version | `7.6.9` |
| pwsh_resolved_by_codex_sandbox | `C:\Users\user\AppData\Local\Microsoft\WindowsApps\pwsh.exe` |
| os | `Microsoft Windows [版本 10.0.26200.9711]` |
| nproc | `12` |

## Expectation check

- all stated expectations matched: sha256 `3a9da65561ab19ca...`, 14 SKILL.md in both ZIP and installed copy, top dir `sbl-tpm-sp`, plugin.json `0.3.0-rc.2`, 13 CLI subparsers, 19 schema families

## Discrepancies worth a decision

- DUPLICATE INSTALLED COPY: two copies of sbl-tpm-sp/0.3.0-rc.2 sit under the isolated CODEX_HOME - sbl-pre-primary-local (enabled in config.toml, cited by the install receipts, 14 SKILL.md) and created-by-me-remote (Plugin_e787f67d86548191ae484c9ab4eb78ab, 14 SKILL.md, 0 references in config.toml). The sbl-pre-primary-local copy is used as the Installed identity; both plugin.json files hash to 48d704bcb0a1...
- RECORD CONFLICT: output/HOST_ACTUAL_USED.json records codex installed/loaded = NOT_RUN for rc.2 (marketplace manifest rejected), while the GJ02 receipts of 2026-11-02 23:11 (later) record a successful marketplace add and 'installed, enabled'. The receipts are cited as install evidence; neither record supports a Loaded claim for rc.2.
- PIPD SPLIT: the packaged source is the worktree patch/pipd-wt (fix/cli-docstring-count @ 75fe7de25f), not the canonical clone C:/Projects/Agent_Workspace/PIPD (candidate/r21-far-20261101 @ 3b48c262f4, 239 dirty entries); the worktree is registered under that clone's .git/worktrees.
- WRITER DRIFT: per the sibling DRIFT_NOTE.md and re-measured here, the canonical PIPD writer now lives in SBL origin/main b7445b0abb at integrations/pipd (version = "0.1.1a5"); that tree still yields 13 CLI verbs and 19 expected schema families. The SBL clone's local `main` ref is stale at bedc11957d while origin/main is b7445b0abb - quote origin/main, never the local ref, for SBL identity.
- NAME: the task says 'HG-KEOS'; the only git repo is C:/Projects/Agent_Workspace/HG-KSEOS (KSEOS). Check output: ls: cannot access 'C:/Projects/HG-KEOS': No such file or directory
- PRIOR-RUN VALUES: the sandbox pwsh path comes from the earlier run's raw/codex_stderr.txt via _extract_pwsh.py, not from a fresh sandbox probe in this round; only `where pwsh` and `pwsh --version` are fresh measurements.

## Notes

- Installed/Loaded: INSTALLED + ENABLED is a recorded host action; LOADED/USED requires a host run (load, 14 skills, explicit trigger, nontrigger, ActualServed) that does not exist for 0.3.0-rc.2 and was not performed here.
- The ZIP carries no directory entries - all 173 members are files, so member count and file count coincide; duplicate member names: 0.
- SBL packaging worktree patch/sbl-wt is on repair/sbl-tpm-sp-rc2 @ dadeb91eb9, distinct from the canonical SBL clone; recorded for ZIP traceability.
- PIPD CLI imports from the worktree source (C:\Projects\Agent_Workspace\_candidate_sbl_tpm_sp_20261102\patch\pipd-wt\src\pipd_ls_sp\__init__.py), so the runtime subparser count measures the packaged code.

## Command log

| # | what | command | cwd | exit | value |
|---|---|---|---|---|---|
| 1 | zip_sha256 | `sha256sum 'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip'` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | 3a9da65561ab19cad90a6d7cbfb2eae0abf59b87ba565a118790bce5612326a8 *C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip |
| 2 | zip_member_count | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import zipfile;n=zipfile.ZipFile(r'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip').namelist();print(len(n))"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | 173 |
| 3 | zip_directory_entries | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import zipfile;n=zipfile.ZipFile(r'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip').namelist();print(len([x for x in n if x.endswith('/')]))"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | 0 |
| 4 | zip_file_count | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import zipfile;n=zipfile.ZipFile(r'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip').namelist();print(len([x for x in n if not x.endswith('/')]))"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | 173 |
| 5 | zip_skillmd_count | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import zipfile;n=zipfile.ZipFile(r'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip').namelist();print(len([x for x in n if x.split('/')[-1]=='SKILL.md']))"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | 14 |
| 6 | zip_skillmd_paths | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import zipfile;n=zipfile.ZipFile(r'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip').namelist();[print(x) for x in n if x.split('/')[-1]=='SKILL.md']"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | sbl-tpm-sp/skills/pipd-assurance-tqaep/SKILL.md<br>sbl-tpm-sp/skills/pipd-authority-source/SKILL.md<br>sbl-tpm-sp/skills/pipd-execution-contract/SKILL.md<br>sbl-tpm-sp/skills/pipd-package-project/SKILL.md<br>sbl-tpm-sp/skills/pipd-pd-bind/SKILL.md<br>sbl-tpm-s ...(truncated; full value in 00_BASELINE.json) |
| 7 | zip_top_level_dir | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import zipfile;n=zipfile.ZipFile(r'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip').namelist();print(','.join(sorted({x.split('/')[0] for x in n})))"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | sbl-tpm-sp |
| 8 | zip_plugin_json_version | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import zipfile,json;print(json.loads(zipfile.ZipFile(r'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip').read('sbl-tpm-sp/plugin.json').decode('utf-8'))['version'])"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | 0.3.0-rc.2 |
| 9 | zip_plugin_json_sha256 | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import zipfile,hashlib;print(hashlib.sha256(zipfile.ZipFile(r'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip').read('sbl-tpm-sp/plugin.json')).hexdigest())"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | 48d704bcb0a175baf718aa12f3332cb29a09299d39532469c74c7f953729a281 |
| 10 | zip_member_tail | `unzip -l 'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip' \| tail -3` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | 10333  2026-10-28 00:00   sbl-tpm-sp/tests/test_pre_v2_controls.py<br>---------                     -------<br> 28060299                     173 files |
| 11 | zip_duplicate_member_names | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import zipfile;n=zipfile.ZipFile(r'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip').namelist();print(len(n)-len(set(n)))"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | 0 |
| 12 | installed_cache_path_receipt | `grep -o 'Installed plugin root: .*' raw/host_reinstall.txt \| sed 's/Installed plugin root: //'` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01` | 0 | C:\Projects\Agent_Workspace\_run_sbl_tpm_sp_20261102\RUN-20261102-GJ02-01\shadow\codex-home\plugins\cache\sbl-pre-primary-local\sbl-tpm-sp\0.3.0-rc.2 |
| 13 | installed_receipt_add_line | `head -1 raw/host_final_add.txt` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01` | 0 | Added plugin `sbl-tpm-sp` from marketplace `sbl-pre-primary-local`. |
| 14 | installed_receipt_reinstall_line | `head -1 raw/host_reinstall.txt` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01` | 0 | Added plugin `sbl-tpm-sp` from marketplace `sbl-pre-primary-local`. |
| 15 | installed_receipt_remove_line | `head -1 raw/host_remove.txt` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01` | 0 | Removed plugin `sbl-tpm-sp` from marketplace `sbl-pre-primary-local`. |
| 16 | installed_plugin_json_version | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import json;print(json.load(open(r'plugins/cache/sbl-pre-primary-local/sbl-tpm-sp/0.3.0-rc.2/plugin.json',encoding='utf-8'))['version'])"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home` | 0 | 0.3.0-rc.2 |
| 17 | installed_plugin_json_sha256 | `sha256sum plugins/cache/sbl-pre-primary-local/sbl-tpm-sp/0.3.0-rc.2/plugin.json` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home` | 0 | 48d704bcb0a175baf718aa12f3332cb29a09299d39532469c74c7f953729a281 *plugins/cache/sbl-pre-primary-local/sbl-tpm-sp/0.3.0-rc.2/plugin.json |
| 18 | installed_skillmd_count | `find plugins/cache/sbl-pre-primary-local/sbl-tpm-sp/0.3.0-rc.2 -name SKILL.md \| wc -l` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home` | 0 | 14 |
| 19 | installed_skills_dir_entries | `ls plugins/cache/sbl-pre-primary-local/sbl-tpm-sp/0.3.0-rc.2/skills \| wc -l` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home` | 0 | 14 |
| 20 | installed_config_enable_block | `grep -n -A1 'plugins."sbl-tpm-sp@sbl-pre-primary-local"' config.toml` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home` | 0 | 22:[plugins."sbl-tpm-sp@sbl-pre-primary-local"]<br>23-enabled = true |
| 21 | installed_marketplace_block | `grep -n -A2 'marketplaces.sbl-pre-primary-local' config.toml` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home` | 0 | 12:[marketplaces.sbl-pre-primary-local]<br>13-source_type = "local"<br>14-source = '\\?\C:\Projects\Agent_Workspace\_run_sbl_tpm_sp_20261102\RUN-20261102-GJ02-01\shadow\codex-case' |
| 22 | plugin_list_installed_line | `grep -n 'sbl-tpm-sp' raw/plugin_list_installed.txt \| head -1` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01` | 0 | 5:sbl-tpm-sp@sbl-pre-primary-local  installed, enabled  0.3.0-rc.2  C:\Projects\Agent_Workspace\_run_sbl_tpm_sp_20261102\RUN-20261102-GJ02-01\shadow\codex-case\plugins\sbl-tpm-sp |
| 23 | plugin_list_final_line | `grep -n 'sbl-tpm-sp' raw/plugin_list_final.txt \| head -1` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01` | 0 | 5:sbl-tpm-sp@sbl-pre-primary-local  installed, enabled  0.3.0-rc.2  C:\Projects\Agent_Workspace\_run_sbl_tpm_sp_20261102\RUN-20261102-GJ02-01\shadow\codex-case\plugins\sbl-tpm-sp |
| 24 | plugin_list_removed_line | `grep -n 'sbl-tpm-sp' raw/plugin_list_removed.txt \| head -1` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01` | 0 | 5:sbl-tpm-sp@sbl-pre-primary-local  not installed           C:\Projects\Agent_Workspace\_run_sbl_tpm_sp_20261102\RUN-20261102-GJ02-01\shadow\codex-case\plugins\sbl-tpm-sp |
| 25 | duplicate_copy_remote_plugin_id | `grep -o '"remote_plugin_id": "[^"]*"' plugins/cache/created-by-me-remote/sbl-tpm-sp/.codex-remote-plugin-install.json` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home` | 0 | "remote_plugin_id": "Plugin_e787f67d86548191ae484c9ab4eb78ab" |
| 26 | duplicate_copy_skillmd_count | `find plugins/cache/created-by-me-remote/sbl-tpm-sp/0.3.0-rc.2 -name SKILL.md \| wc -l` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home` | 0 | 14 |
| 27 | duplicate_copy_plugin_json_sha256 | `sha256sum plugins/cache/created-by-me-remote/sbl-tpm-sp/0.3.0-rc.2/plugin.json` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home` | 0 | 48d704bcb0a175baf718aa12f3332cb29a09299d39532469c74c7f953729a281 *plugins/cache/created-by-me-remote/sbl-tpm-sp/0.3.0-rc.2/plugin.json |
| 28 | duplicate_copy_in_config | `grep -c 'created-by-me-remote' config.toml` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home` | 1 | 0 |
| 29 | loaded_receipt_claim_in_output | `grep -o '"claim": "[^"]*"' output/HOST_ACTUAL_USED.json` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102` | 0 | "claim": "NO_FRESH_HOST_QUALIFICATION_FOR_THIS_VERSION" |
| 30 | loaded_receipt_installed_step | `grep -o '"installed": "[^"]*"' output/HOST_ACTUAL_USED.json` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102` | 0 | "installed": "NOT_RUN"<br>"installed": "NOT_RUN" |
| 31 | loaded_receipt_carry_forward | `grep -o '"carried_forward_not_revalidated"' -A2 output/HOST_ACTUAL_USED.json \| tail -2` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102` | 0 | "carried_forward_not_revalidated" |
| 32 | pipd_source_path | `git rev-parse --show-toplevel` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt |
| 33 | pipd_worktree_gitdir | `cat .git` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | gitdir: C:/Projects/Agent_Workspace/PIPD/.git/worktrees/pipd-wt |
| 34 | pipd_branch | `git rev-parse --abbrev-ref HEAD` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | fix/cli-docstring-count |
| 35 | pipd_head | `git rev-parse HEAD` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | 75fe7de25ff3d40544080ce94c4ef05be7dc335e |
| 36 | pipd_head_subject | `git log -1 --format='%h %ad %s' --date=iso` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | 75fe7de 2026-11-03 00:58:19 +0800 docs(cli): the registry has 13 commands, not 14 |
| 37 | pipd_dirty_count | `git status --porcelain \| wc -l` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | 1 |
| 38 | pipd_dirty_files | `git status --porcelain` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | ?? src/pipd_ls_sp.egg-info/ |
| 39 | pipd_version_attr | `'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/.venv-pipd/Scripts/python.exe' -c "import pipd_ls_sp;print(pipd_ls_sp.__version__)"` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | 0.1.1a4 |
| 40 | pipd_cli_subparser_count | `'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/.venv-pipd/Scripts/python.exe' -c "from pipd_ls_sp.cli import build_parser;s=[a for a in build_parser()._actions if type(a).__name__=='_SubParsersAction'][0];print(len(s.choices))"` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | 13 |
| 41 | pipd_cli_subcommands | `'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/.venv-pipd/Scripts/python.exe' -c "from pipd_ls_sp.cli import build_parser;s=[a for a in build_parser()._actions if type(a).__name__=='_SubParsersAction'][0];print(' '.join(sorted(s.choices)))"` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | bind-pd compile-ecp compile-pi compile-tqaep diff doctor export init intake profile project repair validate |
| 42 | pipd_add_parser_grep_count | `grep -c 'add_parser(' src/pipd_ls_sp/cli.py` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | 13 |
| 43 | pipd_schema_family_count | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import json;d=json.load(open('schemas/registry.json',encoding='utf-8'));print(len(d['families']))"` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | 19 |
| 44 | pipd_schema_registry_id | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import json;d=json.load(open('schemas/registry.json',encoding='utf-8'));print(d['schema'])"` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | PIPD-S0-CONTRACT-REGISTRY/1 |
| 45 | pipd_schema_family_names | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import json;d=json.load(open('schemas/registry.json',encoding='utf-8'));print(' '.join(f['contract'] for f in d['families']))"` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | ArtifactIdentity AuthorityBinding RequirementAtom ProfileBinding TechnologyAdmission PI-PKG PD-PKG TraceLink TaskSpecSeed ConstructionContract WorkOrderCandidate ECP TQAEP ExecutionHandoff EvidenceExpectation ClaimCeiling SurfaceProjectionManifest GENIEProject ...(truncated; full value in 00_BASELINE.json) |
| 46 | pipd_schema_registry_sha256 | `sha256sum schemas/registry.json` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | 85100a8e5ba6320f6648d33a14099fb999b2c452a94aff1652854d2550065e9d *schemas/registry.json |
| 47 | pipd_imported_package_path | `'C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/.venv-pipd/Scripts/python.exe' -c "import pipd_ls_sp;print(pipd_ls_sp.__file__)"` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt` | 0 | C:\Projects\Agent_Workspace\_candidate_sbl_tpm_sp_20261102\patch\pipd-wt\src\pipd_ls_sp\__init__.py |
| 48 | repo_SBL_toplevel | `git rev-parse --show-toplevel` | `C:/Projects/Agent_Workspace/SBL` | 0 | C:/Projects/Agent_Workspace/SBL |
| 49 | repo_SBL_branch | `git rev-parse --abbrev-ref HEAD` | `C:/Projects/Agent_Workspace/SBL` | 0 | candidate/r14-ts15-kinds |
| 50 | repo_SBL_head | `git rev-parse HEAD` | `C:/Projects/Agent_Workspace/SBL` | 0 | 826ca066a1c2df2976c0d402018b79e1c79a444f |
| 51 | repo_SBL_head_subject | `git log -1 --format='%h %ad %s' --date=iso` | `C:/Projects/Agent_Workspace/SBL` | 0 | 826ca06 2026-10-27 11:52:29 +0800 SBL: land PR13 atomic save with O_EXCL staging (B1 r9) |
| 52 | repo_SBL_dirty_count | `git status --porcelain \| wc -l` | `C:/Projects/Agent_Workspace/SBL` | 0 | 47 |
| 53 | repo_SBL_dirty_breakdown | `git status --porcelain \| cut -c1-2 \| sort \| uniq -c \| tr '\n' ';'` | `C:/Projects/Agent_Workspace/SBL` | 0 | 4  M;     43 ??; |
| 54 | repo_PIPD_toplevel | `git rev-parse --show-toplevel` | `C:/Projects/Agent_Workspace/PIPD` | 0 | C:/Projects/Agent_Workspace/PIPD |
| 55 | repo_PIPD_branch | `git rev-parse --abbrev-ref HEAD` | `C:/Projects/Agent_Workspace/PIPD` | 0 | candidate/r21-far-20261101 |
| 56 | repo_PIPD_head | `git rev-parse HEAD` | `C:/Projects/Agent_Workspace/PIPD` | 0 | 3b48c262f4174217cb35391c6da22bc53f068755 |
| 57 | repo_PIPD_head_subject | `git log -1 --format='%h %ad %s' --date=iso` | `C:/Projects/Agent_Workspace/PIPD` | 0 | 3b48c26 2026-11-01 19:22:36 +0800 R21 closure: layer audit, full evidence preservation, signed rulings, handover state |
| 58 | repo_PIPD_dirty_count | `git status --porcelain \| wc -l` | `C:/Projects/Agent_Workspace/PIPD` | 0 | 239 |
| 59 | repo_PIPD_dirty_breakdown | `git status --porcelain \| cut -c1-2 \| sort \| uniq -c \| tr '\n' ';'` | `C:/Projects/Agent_Workspace/PIPD` | 0 | 3  M;    236 ??; |
| 60 | repo_Fabric_toplevel | `git rev-parse --show-toplevel` | `C:/Projects/Agent_Workspace/Fabric` | 0 | C:/Projects/Agent_Workspace/Fabric |
| 61 | repo_Fabric_branch | `git rev-parse --abbrev-ref HEAD` | `C:/Projects/Agent_Workspace/Fabric` | 0 | far/far-031-fhs-msc-all-pass-20261031 |
| 62 | repo_Fabric_head | `git rev-parse HEAD` | `C:/Projects/Agent_Workspace/Fabric` | 0 | 765df6289cfb7730aa56efbd522d76df6ec9809a |
| 63 | repo_Fabric_head_subject | `git log -1 --format='%h %ad %s' --date=iso` | `C:/Projects/Agent_Workspace/Fabric` | 0 | 765df62 2026-11-01 12:35:34 +0800 FAR-054/055/056: three lanes each, and the two defects the VERIFY lane found in the harness |
| 64 | repo_Fabric_dirty_count | `git status --porcelain \| wc -l` | `C:/Projects/Agent_Workspace/Fabric` | 0 | 6 |
| 65 | repo_Fabric_dirty_breakdown | `git status --porcelain \| cut -c1-2 \| sort \| uniq -c \| tr '\n' ';'` | `C:/Projects/Agent_Workspace/Fabric` | 0 | 2  M;      4 ??; |
| 66 | repo_HG-KSEOS_toplevel | `git rev-parse --show-toplevel` | `C:/Projects/Agent_Workspace/HG-KSEOS` | 0 | C:/Projects/Agent_Workspace/HG-KSEOS |
| 67 | repo_HG-KSEOS_branch | `git rev-parse --abbrev-ref HEAD` | `C:/Projects/Agent_Workspace/HG-KSEOS` | 0 | candidate/r18-fhs-skeleton-spine-20261029 |
| 68 | repo_HG-KSEOS_head | `git rev-parse HEAD` | `C:/Projects/Agent_Workspace/HG-KSEOS` | 0 | f5474257aa7d2005937867340f4cd01b39751129 |
| 69 | repo_HG-KSEOS_head_subject | `git log -1 --format='%h %ad %s' --date=iso` | `C:/Projects/Agent_Workspace/HG-KSEOS` | 0 | f547425 2026-11-01 12:38:43 +0800 re-index after the report amendment: a stale digest in an evidence index is worse than no digest |
| 70 | repo_HG-KSEOS_dirty_count | `git status --porcelain \| wc -l` | `C:/Projects/Agent_Workspace/HG-KSEOS` | 0 | 2 |
| 71 | repo_HG-KSEOS_dirty_breakdown | `git status --porcelain \| cut -c1-2 \| sort \| uniq -c \| tr '\n' ';'` | `C:/Projects/Agent_Workspace/HG-KSEOS` | 0 | 2 ??; |
| 72 | repo_named_HG-KEOS_check | `ls -d 'C:/Projects/HG-KEOS' 2>&1; git -C 'C:/Projects/HG-KEOS' rev-parse --show-toplevel 2>&1 \| head -1` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | ls: cannot access 'C:/Projects/HG-KEOS': No such file or directory |
| 73 | repo_sbl_packaging_worktree_branch | `git rev-parse --abbrev-ref HEAD` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/sbl-wt` | 0 | repair/sbl-tpm-sp-rc2 |
| 74 | repo_sbl_packaging_worktree_head | `git rev-parse HEAD` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/sbl-wt` | 0 | dadeb91eb937b020ce0f385e85579fbfee2b8072 |
| 75 | host_codex_version | `codex --version` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | codex-cli 0.164.0 |
| 76 | host_python_version | `python --version` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | Python 3.14.9 |
| 77 | host_git_version | `git --version` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | git version 2.53.0.windows.1 |
| 78 | host_where_pwsh | `where pwsh` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | C:\Users\user\AppData\Local\Microsoft\WindowsApps\pwsh.exe |
| 79 | host_pwsh_version | `pwsh -NoProfile -Command '$PSVersionTable.PSVersion.ToString()'` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | 7.6.9 |
| 80 | host_sandbox_pwsh_earlier_run | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' 'C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline/_extract_pwsh.py' raw/codex_stderr.txt raw/m3_stderr.txt raw/ds_stderr.txt` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01` | 0 | C:\Users\user\AppData\Local\Microsoft\WindowsApps\pwsh.exe<br>SOURCE=raw/codex_stderr.txt |
| 81 | host_codex_version_earlier_record | `grep -o '"version": "[^"]*"' output/HOST_ACTUAL_USED.json \| head -2` | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102` | 0 | "version": "0.164.0"<br>"version": "v0.22.5 (2026.9.24) local bf0203a794a0" |
| 82 | host_os | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import subprocess;b=subprocess.run(['cmd','/c','ver'],capture_output=True).stdout;print(b.decode('cp950','replace').strip())"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | Microsoft Windows [版本 10.0.26200.9711] |
| 83 | host_cpu | `nproc` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | 12 |
| 84 | sbl_local_main_ref | `git -C C:/Projects/Agent_Workspace/SBL rev-parse main` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | bedc11957d4fc2474b249b69d200829272c118ef |
| 85 | sbl_origin_main_ref | `git -C C:/Projects/Agent_Workspace/SBL rev-parse origin/main` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | b7445b0abb5d0f07f7d46d6bc11a9f165bf599d8 |
| 86 | sbl_origin_main_subject | `git -C C:/Projects/Agent_Workspace/SBL log -1 --format='%h %ad %s' --date=iso origin/main` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | b7445b0 2026-11-03 09:15:27 +0800 U04: close C4 — the archive happened, and FHS now says so (#24) |
| 87 | sbl_main_worktree_head | `git rev-parse HEAD` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main` | 0 | b7445b0abb5d0f07f7d46d6bc11a9f165bf599d8 |
| 88 | sbl_main_worktree_ref | `git rev-parse --abbrev-ref HEAD` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main` | 0 | HEAD |
| 89 | sbl_main_worktree_dirty | `git status --porcelain \| wc -l` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main` | 0 | 0 |
| 90 | sbl_main_pipd_version | `grep -m1 '^version' integrations/pipd/pyproject.toml` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main` | 0 | version = "0.1.1a5" |
| 91 | sbl_main_pipd_cli_verbs | `PYTHONPATH='C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main/integrations/pipd/src' 'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "from pipd_ls_sp.cli import build_parser;s=[a for a in build_parser()._actions if type(a).__name__=='_SubParsersAction'][0];print(len(s.choices))"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main` | 0 | 13 |
| 92 | sbl_main_pipd_expected_families | `PYTHONPATH='C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main/integrations/pipd/src' 'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "from pipd_ls_sp import registry;print(registry.EXPECTED_FAMILIES)"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main` | 0 | 19 |
| 93 | sbl_main_pipd_registry_families | `'D:/Hermes-Recovery/live22/installs/3b763fa5cf79ba4a/environments/fef3df20083a4a92a5d98969b736e5a5/venv/Scripts/python.exe' -c "import json;d=json.load(open('integrations/pipd/schemas/registry.json',encoding='utf-8'));print(len(d['families']), d['schema'])"` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main` | 0 | 19 PIPD-S0-CONTRACT-REGISTRY/1 |
| 94 | sbl_main_pipd_schema_files | `ls integrations/pipd/schemas/*.json \| wc -l` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main` | 0 | 20 |
| 95 | drift_note_present | `head -1 C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline/DRIFT_NOTE.md` | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/00_baseline` | 0 | # 關鍵漂移：原 PIPD Writer 已在 ARCHIVE 後移轉到 SBL（本輪必讀） |
