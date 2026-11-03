# 十 P0 裁決表 — `sbl-tpm-sp 0.3.0-rc.2` 前置修補最終驗收（r2）

**裁決：`PRE_V2_CLOSEOUT=NO`**
**Run**：`_run_sbl_tpm_pre_v2_final_20261103`　**日期**：2026-11-03　**Owner 授權範圍**：READ／隔離 DRAFT／受影測試／PR

> 本表為**十個共享證據視圖**，不是十個批准程序。每列只引一次有效 Raw；`HOLD` 一律附具名解除條件。

## 一、身份基線（CT-00 實讀）

| 層 | 實讀值 |
|---|---|
| SOURCE | `sbl-tpm-sp-0.3.0-rc.2-private.zip` sha256 `3a9da655…26a8`；173 成員、**14** SKILL.md、頂層 `sbl-tpm-sp/`、plugin.json `0.3.0-rc.2`（`48d704bc…a281`） |
| INSTALLED | 隔離 `CODEX_HOME/plugins/cache/sbl-pre-primary-local/sbl-tpm-sp/0.3.0-rc.2`；plugin.json 與 ZIP **位元組相同**、14 SKILL.md、`enabled=true`；另有 `created-by-me-remote` 同版副本 |
| LOADED / USED | **未成立**：`HOST_ACTUAL_USED.json` 記 rc.2 的 installed/loaded 為 `NOT_RUN`；其 loaded 證據載自 **0.3.0-rc.1**。本輪未能產生新的 Host 呼叫 |
| 原 Reader | **SBL `b7445b0`**、`integrations/pipd`、`pipd-ls-sp 0.1.1a5`（PIPD-LS-SP 已 `archived=true`、`write_authority=NONE`）；13 verbs／19 families 實測 |
| Host | codex-cli `0.164.0`、Python `3.14.9`、git `2.53.0`；沙盒 shell 解析為 `%LOCALAPPDATA%\Microsoft\WindowsApps\pwsh.exe`（Store 版 7.6.9 alias） |

## 二、十 P0

| # | P0 | 判定 | 有效 Raw | 說明／解除條件 |
|---|---|---|---|---|
| 1 | `P0_SOURCE_BASELINE` | **HOLD** | `00_baseline/00_BASELINE.json`（95 命令）、ZIP/Installed 雜湊比對 | Source→Installed 位元組一致；**Loaded/Used 缺**，`source_authority=ORIGINAL_OWNER_UNVERIFIED`。解除：一次真 Host 載入並回讀 |
| 2 | `P0_LIFECYCLE` | **PASS（設計級）** | `raw/plugin_list_installed.txt` → `removed.txt` → `final.txt`；M2 假 Qualified 拒收 | Planned 無 Live Receipt 可成立；假 grant／假 Qualified 必拒。注意：收據無 exit code 存檔 |
| 3 | `P0_PI_ID` | **PASS** | 原 writer PI：`REQ-1fc8f618…`、`REQ-bf8f22cb…`、兩個 ORACLE id、subject `PI-974a4204962f5dc8` | 原名稱與 Original ID 由原 writer 產生；host 標籤 `SUBJ-GJ02-BILLING-ROUNDING` **未**冒原 ID。caveat：fuo/case id 屬作者派生 |
| 4 | `P0_PD_REALITY` | **PASS（降級）** | `c2/pd.json` 綁 `70757870ef49…`（與隔離 repo 實值相同） | 真 probe 成立；`dirty=true`、`writable_scope.verified=false` 照實記。偽 HEAD 負例由 gate 拒 |
| 5 | `P0_ECP_TYPED` | **HOLD** | `c1/REGISTRY_RECON.md`、`bundle_r2/registry/operation_registry.json`（作者派生） | **`EFFECT_REGISTRY_UNBOUND`**：四庫 0 hits、19 family 0 enum；路徑猜 Effect 不合格。解除：PIPD Contract Owner＋HG-KSOS Issuer 批准 `operation-registry` 並登錄 family |
| 6 | `P0_TQAEP_FUO` | **HOLD** | `bundle_r2/PlannedTQAEP.json`（`RUNNER_UNBOUND`）、`tqaep_noReceipt.out`=`TQ_SOD`、c2 `TQAEP_DESIGNED/NOT_GRANTED` | Plan 合法、Live 無收據。解除：真 protected checker 執行收據（同 subject/candidate/host/scope/epoch） |
| 7 | `P0_COMPATIBILITY` | **PASS** | 新樹 `samples/validate_sbl_0111a5.out`、`c2/validate_pos.out`／`validate_neg.out` | 13 verbs／19 families；四件 `--require-four`→`PASS checked 4 complete=true exit 0`；錯 schema ECP→`exit 1`。限制：只驗原 writer→原 reader 單向，host `@2` 物件仍被拒 |
| 8 | `P0_AUTHOR_TESTS` | **PASS（部分）** | `samples/EVIDENCE_MAP.md` 內 5 個命名負例實跑 `5 passed exit 0` | 安全負例零退化。**更正**：先前「664 passed / 20 skipped」無存檔 log、本輪未重現，不作為本輪證據 |
| 9 | `P0_HOST_INVOKE` | **HOLD（NO EVIDENCE）** | gate 輸出 `host_invoked=NOT_RUN`、`native_e2e=NOT_RUN`；`03_native_receipt_refs.json` `world_effect.state=NOT_RUN` | **rc.2 從未有過 Host 執行**；先前印象中的「安裝並載入」實為 0.3.0-rc.1。`HOST-124` 未修，`danger-full-access` 不作資格 |
| 10 | `P0_ROLLBACK` | **HOLD** | `02_HOST_ROLLBACK.md`（本輪真跑 `git checkout -- .`，HEAD `70757870` 不變、缺陷復現：`1 failed, 1 passed`） | Repo 級回退**已實際執行**；plugin 級卸載／重裝有收據；**缺**舊版在真 Host 重新 Loaded 的證據 |

統計：**PASS 4（含 2 個降級）／HOLD 6／FAIL 0**

## 三、薄治理（共用同一受界案例，設計級）

| 測項 | 真值 |
|---|---|
| K1 同 Owner/Scope/TTL 不重問 | `RepeatQuestions=0`（兩個相依步驟、0 次人類批准） |
| K2 無 Live Receipt 可 Plan、不可 Qualified | `TQAEP_DESIGNED`／`independent_acceptance=NOT_GRANTED`；假收據拒收 |
| K3 缺 Grant 只 HOLD 受影效果 | `world_effect=NOT_RUN`，合法 READ／DRAFT 照常；`FalseBlockCount=0` |
| K4 路徑表示不改變 EffectClass | **不可驗**（無原 registry；此正是 `P0_ECP_TYPED` HOLD 的原因） |
| K5 UNKNOWN 不盲重試 | 設計級拒收成立（blind-retry 負例 pass）；無真 broker/spine → Native 面 `NOT_RUN` |
| 成本 A/B | `AB_CAUSAL_SAVING_UNVERIFIED`（不宣稱百分比） |

Gate 決定性：同一候選 `9338793684eab1b0` 連跑兩次輸出位元組相同（`raw/m4_gate_run1.json` ≡ `run2.json`）。

## 四、三個 FirstFail

| # | FirstFail | 原 Owner | 已合法候選／降級 |
|---|---|---|---|
| 1 | **`P0_HOST_INVOKE`：rc.2 無任何 Host 執行記錄** | Hermes/Codex Host | 交付已安裝、可列舉、可卸載的 RC；資格保留 `HOLD` |
| 2 | **`P0_ECP_TYPED`：`EFFECT_REGISTRY_UNBOUND`** | PIPD Contract Owner ＋ HG-KSOS Issuer | 泛用 ECP＋`EFFECT_UNBOUND` 標記；不造第二 Registry |
| 3 | **`P0_ROLLBACK`：缺 Host 級舊版重載** | Hermes/Codex Host | Repo 級回退已真跑；plugin 卸／裝收據在案 |

## 五、本輪未做（依指示）

未生成 `FHS_PIPD-LS-PKG_v2` 三 SPEC／22 WP 主包；未跑 W0～W3、949/282 Runner、Native Issuer/Checker/Publisher、ChatGPT 私人 Host；未改現役 `~/.codex`、plugin cache、原 WorkID/Journal；未重建 rc.2 位元組。
