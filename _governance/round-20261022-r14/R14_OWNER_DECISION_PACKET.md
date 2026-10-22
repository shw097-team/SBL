# R14 — 需要 owner 出手的五件事（其餘 26 筆已可由本回合機器推進）

**回合** `SBL-R14-FULL-DOC-POST-R13-20261022` · **產出時間** 2026-10-22 · **狀態** 21 DONE / 5 PARTIAL / 4 BLOCKED / 1 BLOCKED_SOFT（31）

本檔案只列「**我沒有權限自己做，也不能代簽**」的項目。每一項都附：卡在哪、已備好的東西是什麼、需要您做的**一個動作**、以及做完之後會鬆開什麼。任何一項都不需要您重讀整份契約。

---

## 1. `TS27` — PIPD 語義分母簽名（M4 的前置）

| | |
|---|---|
| 卡在 | `D_clause_semantic = UNRESOLVED`。沒有 Source Owner 簽名的分母，任何「語義完成度 %」都不成立 |
| 已備好 | `_r14_packet/raw/ts27_denominator_proposal.md`（含完整度量指令、逐 DOC 的 sha256、packet/heading/bytes 實測值）＋ `ts27_denominator.json` ＋ `ts27_measure.py` |
| 需要您 | 在提案上簽名，或回一個 typed 的拒絕與理由 |
| 鬆開什麼 | `TS27` 可關；`TS30`（M4）才有分母可比 |
| 我不會做的 | 自己挑一組數字當分母。那正是把 TS27 做壞的方式 |

**關鍵一句**（提案原文）：measured packet 總數是「review workload」，**不是** `D_clause_semantic`；簽 parser 的計數並不等於解決 TS27。

---

## 2. `TS12` — 三個私人 ChatGPT Plugin 的 schema/host 授權（BLOCKED_SOFT）

| | |
|---|---|
| 卡在 | 三個 surface 皆 `HOST_PENDING`；DOC-06 禁止 Draft 上架，且 plugin 的 schema/host 權威不在我手上 |
| 已備好 | `_r14_packet/raw/ts10_12_PLAN.md`；三 surface 的資格清單與缺項 |
| 需要您 | 出一張 CR 授予 plugin schema/host 權威，或明確裁決「本輪不做，維持 HOST_PENDING」 |
| 鬆開什麼 | `TS12` 可進 M4 的 E06 證據列 |

---

## 3. `TS25` / `TS26` — SWOF W3 permit（M3 的唯一入口）

| | |
|---|---|
| 卡在 | 沒有任何 W3 permit（`TS24` 已量測：0 permit），而受治理的 SWOF 變更**在沒有 permit 時不存在**——不是「先做再說」 |
| 已備好 | `_r14_packet/raw/ts24_w3_route_out.json`：SWOF repo `HEAD 417f1157`、worktree 讀寫狀態、W2 凍結讀集樣本、route-out 的完整欄位 |
| 需要您 | SWOF Native Owner 發 W3 permit，**或**回 typed NACK |
| 鬆開什麼 | `TS25`（第一次真正受治理 SWOF 變更）→ `TS26`（M3 正式接續）→ `TS30`（M4） |
| 我不會做的 | 繞過 permit 在 SWOF 裡寫東西。`TS24` 的 route-out 就是為了證明這件事沒有被偷偷做掉 |

---

## 4. `TS23` — M2 的接受判決（第九輪進行中）

| | |
|---|---|
| 卡在 | **八輪獨立審查全 FAIL**，每輪都找到真缺陷；第九輪正由 checker 車道（`opencode-go/deepseek-v4.1-flash`）執行 |
| 已備好 | `ts23_SCOPE.md`（書面契約 + 明列 out-of-scope）、三個實作正本 `ts23_src/*.py`、三份契約測試、`ts23_remediation{,2..8}.json`、`ts23_review{,2..8}.json`、變異 harness（32 變異全抓、0 假紅、32/32 還原） |
| 需要您 | **不需要動作**（這一項是我自己的責任，不是您的簽名）。列在這裡是因為 M2 未通過是 `TS30` 的硬前置 |
| 誠實上限 | M2 = `NOT_PASSED`。我不會因為「已經審了九輪」而收線 |

---

## 5. `TS30` — M4（受前三項阻擋）

| | |
|---|---|
| 卡在 | M2 未通過、M3 BLOCKED，M4 依定義不可通過 |
| 已備好 | `ts30_m4_verdict.json` / `.md`（ledger 驅動，非人工填寫） |
| 需要您 | 前四項鬆動後**重新發裁決**即可，無需另外簽名 |
| 目前判決 | `BLOCKED`，counts `{BLOCKED:3, BLOCKED_SOFT:1, DONE:17, OPEN:1, PARTIAL:9}` |

---

## 附：本回合已自行關閉的（不需要您）

`TS10` 產品層四動詞（load/invoke/upgrade/rollback，7 tests、八動詞生命週期每步 exit 0）· `TS11` 第三方式 SBOM＋68 advisories 全部落在交付物依賴閉包外（三 SP 宣告 0 依賴、MIT）· `TS13` oracle 接上發證路徑（5 tests，含順序守衛）· `TS28` 三支分支遠端讀回 1116 個相同 blob · `TS17` DOC-08 軸線矩陣 768 格（32 runtime-qualified、7 個 OracleType 無執行器）· `TS29/D-19` canonical 清單**從控制包導出**（14 份、17,473,442 bytes，與已在量的總量一致；仍待簽名）

全套件：**646 passed / 90 subtests / exit 0**（`PYTHONPATH=src`）。車道：epoch 32，PLAN/VERIFY = `opencode-go/deepseek-v4.1-flash`、EXECUTE = `opencode-go/minimax-m3.1-flash-free`，`SOD006-C6` 已宣告 PLAN 與 VERIFY 同模型（只剩流程/車道/證據路徑分離）。
