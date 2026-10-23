# R15.3 治理式自演化記錄

## 這一輪改的是「為什麼會停」的機制，不是再寫一份裁決

PLAN 車道（openai-codex/gpt-6.1-sol, rank 2, 156.92s, nonce ✓）給出的設計只允許五項，並明列拒絕清單：
不建服務、不建第二驅動器、不建自然語言任務生成器。落地結果：

| 控制 | 檔案 | 狀態 |
|---|---|---|
| A1 合法終止 | `tools/continuation_guard.py`、`AGENT_QUIESCENCE_PROOF.json` | 已落地，目前未達成 |
| A2 排程器 + 鎖 | `tools/autonomy_tick.py`、cron `e539df5f39a4`（15m, no_agent） | 已落地 |
| A3 分母覆蓋同步 | `tools/sync_denominator_queue.py` | 已落地，重播 15→0 |
| A4 每步預算/原子檢查點 | `advance_queue.py` 的 attempt cap + `--max-steps` | **部分**：無 wall-clock 預算 |
| A5 修補類別規則 | `MANDATE_R15_2.json: repair_class_rule` | 已落地 |

## 觀測（同一批工具，改前 vs 改後）

- 改前：`advance_queue` 每次都回「no AGENT item is READY」；PARTIAL 永久隱形。
- 改前：guard 有 10 個 `SATISFIABILITY_UNKNOWN`，永不終止，且不是可執行工作。
- 改後：`sync_denominator_queue` 第一次補 15 列、第二次 0（冪等），DONE 列未被觸碰。
- 改後：guard 終止語義分四層，並列出 15 個 `NEEDS_RECIPE` 的 AGENT 項目＝真正剩下的工作。
- `mandate_gate audit` = `AUDIT_CLEAN (53)`；本輪新增 17 張卡（Q18/Q19 + 15 列 DEN）。

## 學到的（已提升為技能）

`round-continuation-controls`（software-development）：診斷三量測、五控制、四宣稱、四坑。
核心一句：**「不准停」與「不可能完成」並存時，任何模型只能選違規或說謊；先造出合法終止，再談自動化。**

## 尚未完成（不得美化）

- 15 列 `NEEDS_RECIPE` 需要逐列寫出 chk predicate + resume_cmd；這是真工作，不是設定。
- Q9（OpenSpec delta 兩段）與 Q12（ci.yml 一步）仍為真 bypass，依 A5 必須由 EXECUTE 重寫；
  Q17/Q18/Q19 依 A5 屬 plumbing，已記錄未洗白。
- A4 的 wall-clock 預算未做：目前靠 attempt cap 與 max-steps，長跑仍可能卡在單一 lane 呼叫。
- 因此 `agent_quiescent` 仍為 false；本輪宣稱上限 `LOCALLY_VERIFIED_PARTIAL`。

## 下一步（已可見、可續跑）

每 15 分鐘的 tick 會保持一致觀測；下一個回合從 `DEN-C08/C09/C10/C13/C14/C15/W08/W17/E02/E03/E05/E08/E09`
逐列補 recipe，Q12/Q17 由 EXECUTE 重寫，直到 guard 回 `AGENT_QUIESCENT_AWAITING_PRINCIPALS`。
