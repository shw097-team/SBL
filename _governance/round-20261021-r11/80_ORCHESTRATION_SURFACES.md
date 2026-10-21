# 80 · 編排面（KANBAN / SWARM / GSTACK / OPENSPEC）本輪實際狀態

指令要求「啟用 KANBAN、SWARM、GSTACK、OPENSPEC」。這四個是**編排/變更記錄面，不是模型路由器**（啟用它們不會把任何模型放上任何角色；模型由 lane binding 決定，見 `30_MANDATE_CHAIN.md`）。以下逐面記錄本輪的**實際**狀態，不以宣告代替。

| 面 | 本輪狀態 | 證據 | 為什麼停在此處 |
|---|---|---|---|
| **KANBAN** | **ENABLED + USED** | board `sbl-r11-20261021`，DB `<HERMES_HOME>/kanban/boards/sbl-r11-20261021/kanban.db`；7 張卡（1 goal、1 done、5 open），readback 見 `70_KANBAN_BOARD.md` | 已把本輪切片與五個未結義務落成可回讀卡片 |
| **SWARM** | **AVAILABLE / NOT USED** | CLI 具 `kanban swarm`（一次建 root + workers + verifier + synthesizer 的 DAG） | 本輪沒有可平行派工的寫入單元：無 HGK permit、無 checker scratch，量測本身是序列式唯讀。開空 DAG 只會製造假活動。下一個有 WriteSet 的回合應以 `swarm` 一次建圖 |
| **GSTACK** | **NOT AUDITED THIS ROUND** | HGK 內只有 `var/task014_gstack_e2e.py`、`var/task014_gstack_inventory.py` 等評估腳本 | 未對 R11 角色做 named-method 選用回讀（需 `references/gstack-named-method-readback.md` 的選用面），不宣稱已選用或已生效 |
| **OPENSPEC** | **EXISTS / NO NEW CHANGE** | 產品 repo 現有 `openspec/changes/sbl-v01-candidate-build` | 新增 OpenSpec change 會寫入產品 repo，需要 candidate-branch WriteSet 與 permit；本輪無授權，故變更記錄落在本 evidence packet + kanban board，不偽造 change |

## 誠實邊界

- 「啟用」= 有可回讀的 board / CLI 證據；不是「已把模型路由到某角色」。
- 未達成的面一律標示 `NOT USED` / `NOT AUDITED` / `NO NEW CHANGE`，不以空殼充當已啟用。
- 下一回合若取得 permit，建議順序：`kanban swarm`（建 DAG）→ OpenSpec change（記錄）→ bounded writer 派工 → isolated checker。
