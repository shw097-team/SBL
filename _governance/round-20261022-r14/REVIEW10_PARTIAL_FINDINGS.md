# 第十輪 TS23 審查 — 被暫停時的部分發現（必須在恢復後先處理）

**狀態** `interrupted`（owner 關機要求），38 次 API 呼叫、745.88 秒，**沒有最終 verdict**。
**逐字 transcript** `raw/review10_partial/transcript.log`（28,062 B，已入證據分支；原本放在會被 prune 的 cache 目錄）

這一輪不是空的。它已經在跑的過程中產生四個訊號，恢復後**第一件事**就是把它們坐實或推翻。

## 訊號 1（最重要）：`ts23_review` 有一筆變異 SURVIVED

transcript 第 52 列：

```json
{"kind": "SIMPLE_AGENT", "disposition": "SURVIVED", "applied": true, "caught": false,
 "mutant_crashed": false, "crash_not_evidence": false, "mutant_ran_and_answered": true,
 "test_exit": ...}
```

- `mutant_ran_and_answered: true` → **不是崩潰**，程式活著並回答了錯的答案。
- `caught: false` → 我的 36/0 宣告在這位審查者新增的變異下**不成立**。
- 要做的：從 transcript 找出該變異的 `original`／`mutant` 兩段文字，確認它落在 SCOPE 的哪一條，然後**先補測試、再修程式**（順序不可顛倒）。

## 訊號 2：`no_op_control_detected: False`

transcript 第 50 列（RC 1）：

```
all_caught: True · no_false_reds: True · all_mutations_are_real_changes: True
no_op_control_detected: False
```

審查者把 CONTROL 那一筆的處置從 `NOT_A_CHANGE` 變成非 `NOT_A_CHANGE`。可能原因有兩種，**必須分辨**：

1. 他改的是 `MUTATIONS` 內容（新增 rev10 條目時動到控制項）→ 我的旗標計算太依賴「清單裡剛好有那一筆」，屬於**旗標脆弱**；
2. 他真的讓 no-op 通過了檢查 → 那是 `NOT_A_CHANGE` 判定的**真缺陷**。

判別方法：拿他的 mutation 清單跑我的 harness，看 CONTROL 那筆的 `original`／`mutant` 是否仍相等。**不要假設是 (1)。**

## 訊號 3（好消息，已驗）：崩潰不再被算成抓到

第 50 列：刪掉 `except UnicodeError` 的變異 → `AGENT_SKILL CAUGHT`，而 `no_crash_counted: True`。
第 96 列：另一筆 `narrowed_handler` → `mutant_crashed: true, crash_not_evidence: true, false_red: true`，**沒有**被算成 catch。
→ remediation9 的儀器修正有效。

## 訊號 4（好消息，已驗）：`SHADOWED_IMPORT` 擋得住

第 60 列：審查者**自己製造** `PYTHONPATH` 遮蔽，harness 把全部條目判成 `SHADOWED_IMPORT`，沒有冒充 survivor。
→ `TT-R14-051` 的修正有效。

## 恢復後的正確順序

1. 讀 `raw/review10_partial/transcript.log` 第 45–100 列，把訊號 1 的變異原文抄出來。
2. 用 `ts23_mutation_check.py` 重跑該變異，確認 `test_exit` 與 `assertion_message`。
3. 若確為未覆蓋 → 先加契約測試（RED），再修 `ts23_src/*`（GREEN），最後加進 `MUTATIONS` 當回歸。
4. 修 `no_op_control_detected` 的判定：改成「CONTROL 條目必須存在且其 `original == mutant`」再檢查處置，而不是只看處置。
5. 之後才重派第十一輪審查。**不要在訊號 1 未坐實前宣稱 M2 有進展。**
