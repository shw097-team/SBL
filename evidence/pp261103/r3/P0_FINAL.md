# `P0_FINAL` — 十項 P0 最終裁決（r3，2026-11-03）

**裁決：`PRE_V2_CLOSEOUT=NO`**
唯一原因：**Host 面兩項（`P0_HOST_INVOKE`、`P0_ROLLBACK`）在受限模式下無法取得真執行證據**；其餘八項已有可信讀回。
本輪**未**生成 `FHS_PIPD-LS-PKG_v2` 主產包、未跑 22 WP／W0–W3、未簽 Grant、未切換主用路由。

## 一、計數規則（依 r3 §5 末端）

`PASS(部分)` 一律計為 `HOLD`；設計降級（`PD_UNBOUND`／`RUNNER_UNBOUND`）若原條款允許且來源契約成立，可 `PASS` 並注明 `claim_ceiling=DESIGN_ONLY`。**缺 Live Checker 不自動判 FAIL。**

## 二、十項裁決

| # | P0 | 判定 | 有效 RawRef | 殘餘 |
|---|---|---|---|---|
| 1 | `P0_SOURCE_BASELINE` | **PASS** | `evidence/pp261103/00_BASELINE.json`（95 命令）；ZIP `3a9da65…` 173 檔／**14** SKILL；Installed `plugin.json` 與 ZIP **位元組相同** `48d704bc…`；canonical reader = SBL `integrations/pipd` 13 verbs／19 families | Host 載入歸第 9 項，不重複扣點 |
| 2 | `P0_LIFECYCLE` | **PASS** | `tests/test_pre_v2_planned_reader.py`、`test_claim_ceiling_shape.py`（本輪 53 passed 內）；假 grant／假收據／nested checker 皆拒 | 無 |
| 3 | `P0_PI_ID` | **PASS** | 原 writer PI：`REQ-1fc8f618…`、`REQ-bf8f22cb…`、subject `PI-974a4204…`、polarity NEG | Host 標籤不冒原 ID（已證） |
| 4 | `P0_PD_REALITY` | **PASS（設計降級）** | 真 HEAD `70757870ef49…`（與隔離 repo 實值相同）、dirty 照記；`writable_scope.verified=false` 明示 | `claim_ceiling=DESIGN_ONLY` |
| 5 | `P0_ECP_TYPED` | **PASS（設計級，Grant 仍 NOT_GRANTED）** | 契約 `integrations/pipd/contracts/operation-registry.pre-v2-r3.json` sha256 `bedf8754…f7a631`（PR #27 → main `7aab3c82`）；loader `operation_registry.py`；`test_operation_registry_r3.py` 11 passed | 效果值集仍未 owner-ratified；`RATIFIED` 故意不可達 |
| 6 | `P0_TQAEP_FUO` | **HOLD** | `bundle_r2/PlannedTQAEP.json`（`runner_binding=RUNNER_UNBOUND`）、`tqaep_noReceipt.out`=`TQ_SOD` | **基於來源**：本 Slice 無原 Case／Oracle registry，現有 case 為 `AUTHOR_DERIVED` |
| 7 | `P0_COMPATIBILITY` | **PASS** | 新 canonical 樹 `--require-four`→`PASS/checked 4/complete true/exit 0`；錯 Schema→`exit 1`；CT-03 後 13 verbs／19 families 未變；受影 53 passed | 不稱 Native Qualified |
| 8 | `P0_AUTHOR_TESTS` | **PASS（slice 範圍）** | `samples/T01_T24_MAP.md`：15 `PASS_REUSED`＋5 `SUPPLEMENTED`（五具名 NEG `5 passed`）；**T12 本輪由 CT-03 補齊**（路徑不變性 4 斷言）；T08 由 adapter `CATEGORY_AS_ID` 拒收覆蓋 | T06（949 全分母）、T20（282 Case 分母）為產品級分母，本 Slice 標 `NOT_APPLICABLE_SLICE_SCOPE` |
| 9 | `P0_HOST_INVOKE` | **HOLD** | `host/host_probe*.jsonl`：`exec_command … rejected: blocked by policy`（workspace-write、read-only、含 cmd.exe 皆同） | 受限模式**無法產生任何 Host 執行**；`danger-full-access` 不作資格 |
| 10 | `P0_ROLLBACK` | **HOLD** | Repo 級回退**已真跑**（`git checkout -- .` → HEAD `70757870` 不變、缺陷復現 `1 failed, 1 passed`）；plugin 卸／裝收據在案 | 缺**舊版在真 Host 重新 Loaded**（同第 9 項阻塞） |

**統計：PASS 7（含 1 設計降級、1 受限設計級）／HOLD 3／FAIL 0**

## 三、本輪新解決的阻斷

| 阻斷 | 狀態 |
|---|---|
| CT-03 「原 Effect Authority 不存在」 | **已解（設計級）**：效果改由 canonical repo 內唯一契約決定，不再由呼叫者自帶 JSON＋自帶 sha 自證；未知／重複／越界／被改／未追蹤一律拒收；`RATIFIED` 非資料可翻轉 |
| `HOST-124` 的 shell 解析層 | **已解並證**：`codex sandbox` 直接執行完整非-WindowsApps 的 pwsh 7.6.9 成功（`7.6.9` / `14`）；MSIX alias 被拒的原因確認為路徑含 `\windowsapps\` |
| `HOST-124` 的程序建立層 | **未解**：`codex exec` 在 `workspace-write` 與 `read-only` 下，任何 `exec_command`（含 `cmd.exe`）皆 `blocked by policy` — 與 shell 選擇無關 |

## 四、薄治理

`RepeatQuestions=0`、`FalseBlockCount=0`、0 次人類批准（兩個相依設計步驟）；gate 兩跑位元組相同（候選 `9338793684eab1b0`）；必要安全拒收全過；成本 A/B `AB_CAUSAL_SAVING_UNVERIFIED`。

## 五、未做

未生成 FHS v2 主包／22 WP／W0–W3；未跑 949／282 全量；未取得 Live Checker／Issuer／Publisher；未改現役 `~/.codex`、plugin cache、原 WorkID。
