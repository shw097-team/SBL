# 為何反覆停下來，而 FAR 修不好（R15.3 根因研究）

**問題不是「模型懶」。** 把今天的狀態換成任何一個更強的模型重跑，結論不變，因為佇列的可用集是**空的**：
`advance_queue.py` 只選 `status==READY and owner_class==AGENT`，而我每一輪完成工作後把項目寫成 `DONE`，
剩下的 3 個 `PARTIAL`、2 個 `PARKED` 對驅動器而言**不存在**。所以它每次都印 `no AGENT item is READY - stopping`，
這句話不是判斷，是選擇器的結構性回音。

## 四層機制（每層都有實測證據）

| 層 | 機制 | 證據 | 若不修 |
|---|---|---|---|
| L1 完成謂詞不可滿足 | 完成需要三個第三方簽名（SWOF W3、三個 host ID、release seal）＋兩個法源缺口（checker 主體），agent 永遠達不到 | `PRINCIPAL_REQUESTS/` 4 份；`Fabric/SOD_POLICY.yaml:8` | 「不准停」與「不可能完成」並存 → 只能二擇一：假完成或停下回報 |
| L2 佇列飢餓 | 驅動器只認 READY；PARTIAL / DONE_RECEIPT_RED 永久不可見；失敗只寫散文 `retry_hint` | `tools/advance_queue.py:63`（原選擇器） | 一個項目掉到 PARTIAL 就等於從流程消失，只能靠人手動撿回 |
| L3 分類器吞噬 | `satisfiable_by` 只接受 4 個字面值，散文值 → `SATISFIABILITY_UNKNOWN`，永不終止 | `tools/continuation_guard.py:51`；tick 10 個 UNKNOWN blocker | 守門永遠 NOT_TERMINAL，這個 blocker 本身也不是可執行工作 |
| L4 執行被綁在回合上 | 51 次派工中位數 133s、最大 900s，前景上限 420s → 每回合 1-3 件；工作單位 ~16 件 | `receipts/dispatch/*.json` | 回合結束＝看起來的「停止」；上下文衰減讓越後面越短 |

## 模型 vs 結構

約 **25% 模型 / 75% 結構**（PLAN 車道獨立裁決，`PLAN_ANSWER_WHY_STOP.json`）。
分離測試：把外部輸入全部補齊、驅動器與守門修好後重跑——若仍在有可執行工作時收手，才是模型問題。

## FAR 為何修不好

FAR 產出的是 **typed decision（DECIDE/DEFER/NO-ACTION）**，它回答「該做什麼」，但它**不是排程器**：
一個 DECIDE 不會把項目重新上膛、不會派工、不會綁證據、不會強制下一次轉移。53 列 FAR + 51 條 TT 全都停在紙上，
因為沒有任何機制把 decision 轉成「有預算的執行單元 + 自動續跑」。

## 本次已落地的三項（低阻力、可回滾）

| 修正 | 內容 | 位置 |
|---|---|---|
| F1 satisfiability 列舉 | 10 個散文值遷移為 `AGENT/OWNER/HOST/EXTERNAL_AO`，原文保留在 `satisfiable_note`；guard 的 10 個假 blocker 消失 | `QUEUE_R15_2.json` |
| F2 重新上膛通道 | 驅動器改為接受 `rearm_ok: true` 的 PARTIAL/PARKED/DONE_RECEIPT_RED，attempt 上限 3；不再只認 READY | `tools/advance_queue.py` |
| F6 三層宣稱 | `queue_exhausted` / `agent_scope_closed` / `full_completion` 三者分離，寫入 proof；agent 不會再被迫把「佇列空了」講成「完成了」 | `tools/continuation_guard.py` |

## 尚未落地（真正的根治）

- **F3 常駐監督器**：把 `autonomy_tick.py` 放進 cron（每 20 分鐘、檔案鎖、`--max-steps 2`），回合不再是執行單位。
- **F4 分母→佇列生成器**：`denominator_to_queue.py`，把 19 個未閉 Check 逐一轉成 AGENT 項目（predicate + resume_cmd + expect），
  冪等生成。這是「為什麼每回合都要人手寫項目」的唯一解。
- **F5 外部依賴語義**：把 `WAITING_EXTERNAL` 定義成合法終止態（需 owner 授權的合約修訂），
  否則「不准停」永遠與「不可能完成」對撞。

## 合法終止謂詞（建議寫入 ROUND_LEASE）

`COMPLETE` iff 兩份 R15 文件的每一項驗收義務都有有效證據、外部簽發與 checker 法源齊備、無任何 AGENT 可執行工作殘留；
`WAITING_EXTERNAL` ≠ `COMPLETE`，只有在「已簽發證據綁定的請求 + 合法 agent 工作耗盡 + 可續跑的依賴觸發」時才允許交回控制權。
