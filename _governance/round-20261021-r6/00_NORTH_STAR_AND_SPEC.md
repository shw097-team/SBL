# SBL-R6｜核心大目標 / 任務執行 SPEC / 任務執行清單 / 檢測清單

> Round: `SBL-R6-DOC00-13-CONTINUATION`；order_id 與 R6 指揮檔一致。
> 本檔為本 SESSION 防飄移主控。裁決依據：R6 報告主文（附錄舊 merge 文字依 `TT-R6-APPENDIX-STALE-MERGE-001` 隔離）。
> 所有上位依據 = `SBL_PIPD-LS-PKG_DOC-00..13`（46/46 hash 已核，見 `10_PREFLIGHT/SSOT_FACTS.json`）。

## 0. 車道 vs 會話（兩個平面，防混淆）

| 平面 | 本輪 binding | 依據 |
|---|---|---|
| 車道 PLAN | Codex CLI `openai-codex/gpt-6.1-sol`（medium, OAuth；pool rank 2，以 `--force-rank 2` 釘選） | 用戶 2026-10-20 更新；非 session 互動模型（當前 glm-5.3-flash），不得把 session pin 當 PLAN 綁定 |
| 車道 EXECUTE | Codex CLI `opencode-go/deepseek-v4.1-flash`（pool rank 1） | 同上；registry epoch22 寫 glm → 已宣告 drift，逐輪以 role mandate 覆蓋 |
| 車道 VERIFY/SECURITY | Codex CLI `openai-codex/gpt-6.1-sol`（medium；`--force-rank 2` 釘選） | 用戶 mandate；R5 三輪 VERIFY 同此 |
| 會話互動模型 | glm-5.3-flash（Hermes desktop） | 僅 orchestrator/會話用，不作為任何車道綁定依據 |

R5-PREFLIGHT 回執證明此 dispatch 路徑可用（`HG-KSEOS/var/R5-PREFLIGHT/plan_probe.json`：`required_arm==served_arm=openai-codex/gpt-6.1-sol`）。

## 1. 核心大目標（North Star，不變）

`SBL_FULL_PRODUCT`：完成 DOC-00..13 全契約。R6 既有裁決不改：
- 全案 `FAIL_FULL_CONTRACT / PARTIAL_CHALLENGE`（除非所有 active 需求閉合）。
- PR #2（`a6bcdd0`）`RECOMMEND_MERGE_SCOPED_NOW`；merge 動作屬 Owner。
- 三 ChatGPT 私人 Plugin `0/3 HOST_ACCEPTED`；Host-issued ID 缺即 fail-closed，不得偽造。
- 本 session 合法推進的是：trace 骨架（TS07）、非 fixture 真 E2E（TS15/16）、packaging（TS06 後段）、441/38 對帳（TS24/25）、evidence 回傳（TS28）。

## 2. 任務執行 SPEC（本 session 邊界）

- WriteSet（candidate branch）：`sbl_harness/`、`sbl_stack/`、`sbl_core/`、`tests/`、`contracts/`、`_governance/round-20261021-r6/`、`pyproject.toml`、`openspec/`、`docs/`、`README.md`。
- 禁區：`知識庫/**`（唯讀 SSOT）、`API KEY/**`（credential broker only）、HGK root、Fabric root、其他 repo、frozen DOC/Oracle。
- 模型方案無法使用時（車道 probe 失敗）：暫停該 TS，改 TEMP_CLOSED + checkpoint，不降級不假造。
- Native effect（merge/release/Host install/Permit）：NOT_GRANTED，僅 Owner。
- 每輪產出：candidate commit SHA + evidence branch + raw receipts + checker verdict + readback。

## 3. 任務執行清單（本 session 實際排程）

| # | TS | 內容 | 狀態 |
|---|---|---|---|
| 1 | R6-TS00 | 機器/遠端新鮮狀態（SSOT_FACTS.json） | DONE（46/46 + 3 SHA 對齊） |
| 2 | R6-TS01 | 來源 intake 46 冊 hash 核對 | DONE（併 TS00） |
| 3 | R6-TS02 | C0–C9 contract 編譯（R6 版 contract，繼承 R5 形狀） | 本 session 主工 |
| 4 | R6-TS05 | `a6bcdd0` scoped proof readback（不重修） | 本 session 主工 |
| 5 | R6-TS06 | PR #2 狀態 fresh check + packaging 準備（merge=Owner） | 本 session 主工 |
| 6 | R6-TS07 | 50 Parent + 149 Child trace 骨架（ChildOutcome ledger，OPEN 不假造） | 本 session 主工 |
| 7 | R6-TS24/25 | 38 Surface + 441 ledger 現況對帳（METHOD-09 drift 修正） | 本 session 主工 |
| 8 | R6-TS28 | evidence branch + push GitHub | 本 session 主工 |
| 9 | R6-TS29 | 隔離 checker（VERIFY 車道，model-axis 不同 principal） | 本 session 主工 |
| 10 | R6-TS15/16 | 非 fixture 真 E2E（CLI_TOOL / AGENT_SKILL / MINIMAL_AGENT） | 視 round 預算啟動；至少產出 bounded TaskSpec |
| 11 | R6-TS21 | ChatGPT 3/3 Host UAT | BLOCKED（需 Host-issued ID，Owner/HITL） |
| 12 | R6-TS12/13 | PIPD Native Writer / HGK Native effect | BLOCKED（NOT_GRANTED） |

## 4. 檢測清單（對應 R6-CHK）

- CHK00 ✓（SSOT_FACTS）；CHK01 ✓（46/46）
- CHK02：compiler 四階段 exit 0 + receipt verdict
- CHK05：a6bcdd0 POS/NEG 重跑 + 同 SHA CI 確認
- CHK06：PR #2 head/base/CI fresh readback（不執行 merge）
- CHK07：149/50 ledger 0 orphan，全部 OPEN 標註
- CHK24/25：38/441 逐列現況欄位（frozen vs current execution 分離）
- CHK28：candidate SHA ≠ evidence SHA；secret scan clean；remote readback
- CHK29：checker verdict 檔（model-axis 獨立；非 signed PASS_CHALLENGE——challenge bundle 需 Owner 補）
- CHK30：全案維持 FAIL_FULL_CONTRACT（誠實結案）

## 5. TT/CR register（本 session 新增/承繼）

| ID | 狀態 |
|---|---|
| TT-R6-APPENDIX-STALE-MERGE-001 | OPEN（R6 主文優先） |
| TT-METHOD09-LEDGER-DRIFT | 本輪以 current_execution 欄修正 |
| CR-PLUGIN-SCHEMA-AUTHORITY | OPEN_CR（B1 建議，未裁定） |
| TT-CHALLENGE-BUNDLE-MISSING | OPEN（references/assets/scripts 未隨單檔上傳） |
| 其餘承繼 R5 closeout §4 | 不變 |
