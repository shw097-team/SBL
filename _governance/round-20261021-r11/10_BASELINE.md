# 10 · Baseline（fresh readback, 2026-10-21T23:20+08:00）

全部數值為本輪直測，非引用 R8/R9/R10 敘述。`UNKNOWN` 表未取得。

## 1. Host / runtime

| 項目 | 值 |
|---|---|
| OS / shell | Windows 11 / MSYS bash（Hermes terminal） |
| 時間 | 2026-10-21T23:20+08:00 (Asia/Taipei) |
| HERMES_HOME | `C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes` |
| Hermes skills/sbl | 5 目錄：`commander-sp`, `external-challenge-sp`, `hgk-governed-runtime`, `sbl-stack`, `tpm-sp` |
| SBL console scripts | `sbl-stack`, `sbl-harness`, `sbl-todo`（皆在 hermes-agent venv `Scripts/`） |
| session model（互動平面） | `deepseek-v4.1-flash` @ `opencode-go` — **不是** PLAN 車道綁定 |

## 2. Git（local + remote，`ls-remote` 公開讀取）

| repo | local HEAD / branch | remote | dirty |
|---|---|---|---|
| `HG-KSEOS` | `b22706ebbdff9248f851767c010befc8e807d463`（`lanes(r10): PLAN and EXECUTE swap under the handover mandate`） | 無 remote（本地原生 repo） | **7 modified + 291 untracked**（含 `_sbl_harness_adapter/`、`HGK/`、`SQS-THC/` 等；未 stage、未 reset） |
| `shw097-team/SBL` | worktree `C:\Projects\Agent_Workspace\SBL` @ `2dde2d84a2a6d95ccc6acb9356570bed68ab2f05`（= remote `evidence/r7-20261021-c7`；untracked `contracts/SBL_C0_C9_CONTRACT-R9.json`, `contracts/compiled-r9/`） | `main=345b9477cef9917cfb15c162db80ccda09eaebc5`；`tag v0.1.0-foundation-preview→bedc1195…`；`tag v0.1.1rc1→345b9477…`；`candidate/r9-20261021-ctrlpkg=32d971d9…` | 主樹只有 2 個 untracked 契約產物 |
| `shw097-team/Fabric` | `d62635626d5d2e54fe5bba22a500a17423c85719`（branch `pub/far-minimax-mandate-20261021`） | `main=bcd91043b89b69c9d2f08309e46e31898ac87d89` | 只讀 |
| `shw097-team/PIPD-LS-SP` | 未取本地 HEAD（本輪只讀遠端） | `main=e95942abcb6aa07e69304607ab8afc22a74fc67d` | — |
| `shw097-team/SWOF` | 未取本地 HEAD | `main=acdbfaadd19d12927eb5bd542b09ed230bbc481e` | — |

## 3. HGK conformance（`R11-CHK06` / `R10-CONFORM` 重測）

| 項目 | 值 |
|---|---|
| 指令 | `PYTHONPATH=C:/Projects/Agent_Workspace/HG-KSEOS/src ./.venv/Scripts/python.exe -m pytest tests -q -p no:cacheprovider --tb=no -rf` |
| HEAD | `b22706e`（**dirty tree**，包含 9 個他人 untracked 測試模組 + 1 個 modified 測試） |
| 首輪結果 | **18 failed / 578 passed / 90 subtests passed / 142.14s** |
| 原始日誌 | `hgk_conformance.log`（本目錄，含 `-rf` 失敗清單） |
| 與 R10 差異 | R10 記 `580 passed / 16 failed`；**分母不同、不可互比**（O-R11-001） |
| 照抄指令的失敗 | `--timeout=900` → `pytest: error: unrecognized arguments: --timeout=900`（pytest-timeout 未安裝，O-R11-002） |
| 模組可 import 性 | `.venv` 無 `hg_kseos`（`ModuleNotFoundError`），必須 `PYTHONPATH=src` 或 `pip install -e .`（O-R11-003） |

> 判讀：這是「目前 dirty 工作樹上的 conformance 分母」，**不是**乾淨 checkout 的 regression verdict；R11 指揮稿要求「不可把舊 580/16 當新實測」，本檔即其替代。

## 4. Source pin（`R11-TS01` / `CHK01`）

| 項目 | 值 |
|---|---|
| 14 DOC | 14/14 SHA-256 相符，bytes 合計 `17,473,442` |
| rollup | `01b972c80341e1b87db4fa6f20f61723564c609f0ff12282f9205679a4f9cf9d` **MATCH** |
| canonical ↔ mirror | `知識庫/…/SBL/SBL_PIPD-LS-PKG` 與 `_sbl_src_mirror/SBL_PIPD-LS-PKG` 逐檔 byte-equal |
| 20 KP | 20/20 檔存在，bytes 與 R11 §8.3 表一致；`00_KNOW_INDEX` `5b42abab…`、`19_KP_INDEX_CROSSWALK` `b0cd7729…` 全 SHA 相符 |
| 2 Skill | `challenge-review-SKILL.md` `9ecd2366…`、`construction-acceptance-prompt-compiler_SKILL.md` `214c7f04…`（皆相符） |
| 10 design vols | vol-01..10 全數 SHA 相符（`_sbl_src_mirror/參考工程資料庫/GPTs_GENIEMAKER_設計實作/_01.._10/`） |
| R9 三負例 | detached `32d971d` worktree 跑 `tests/test_control_package_manifest.py` → **6 passed**，跑後 worktree clean |

## 5. Compiler bundle（`R11-TS04` 前置）

| 項目 | 值 |
|---|---|
| bundle 路徑 | `知識庫/工程基座/construction-acceptance-prompt-compiler/construction-acceptance-prompt-compiler` |
| 內容 | `references/`(7 含 `prompt-contract.schema.json`)、`scripts/prompt_contract_compiler.py`、`tests/`、`assets/`、`agents/`、`SKILL.md` |
| 控制執行 | 對 `SBL/contracts/SBL_C0_C9_CONTRACT-R9.json`：`lint`/`activation`/`acceptance`/`compile` **全 rc0 / PROMPT_COMPILE_PASS** |
| 收據 | `compile_control/compiler-receipt.json`：`contract_sha256=dd200277ca1b9352d751a178fb51b8a5a5d857d0a472f11119fcc56f0471d55d`、`compiler_sha256=2c282ad6539a465c3b1d751868cab98437a8f35e9728be686117e364a70857d9`、`independent_claim=NOT_EVALUATED`、`production_claim=NOT_CLAIMED` |
| 邊界 | 只證 bundle 完整與指令形狀；**不是 R11 契約的 PASS**，也不是任何驗收 |

## 6. Host install readback（`R11-TS14` 片段）

| 面 | 讀回 |
|---|---|
| `sbl-stack status --root SBL-install/stack` | `installed=true`, `schema=SBL-STACK/1`, `version=0.1.0`, `components=14`, principals `[commander_sp, external_challenge_sp, tpm_sp]`, `claim_ceiling=STANDALONE_ONLY`, `host_install_state=NOT_INSTALLED` |
| `sbl-harness doctor --target SBL-install/hgk-adapter` | `ok=true`, `abi=hgk-harness-abi/1`, `claim_ceiling=HOST_PENDING`, `native_effect=NOT_GRANTED`（dispatcher present + `import hg_kseos` 兩項 check 皆 true） |
| 未讀回 | 五工具逐名 effective-load / restart / no-trigger / uninstall / residue；ChatGPT Host 0/3 |

## 7. Native / authority 狀態

| 項目 | 值 |
|---|---|
| HGK WorkOrder / ONE ECP / Permit / ExecutionBinding | **NONE**（本輪未取得；不得由提示詞自簽） |
| Fabric F0 六步 consumer trace | 未跑 |
| R9-02 checker scratch | 未授權 |
| SWOF W3 ACK | 無 ⇒ NO_EFFECT |
