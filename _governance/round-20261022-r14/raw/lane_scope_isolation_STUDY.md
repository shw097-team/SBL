# 車道模型保真度：先把四個平面分開，再談對錯

**結論先講：這不是「車道綁錯」，而是兩個不同性質的東西被併在一起比。**

1. **平面混淆**：先前那份稽核把「會話（session）的互動模型」與「車道（lane）的綁定」放進同一張表比。你指出的情況成立——本機同時有多個 root session 各自用不同模型跑，那些值是 S 平面的，不是車道漂移。
2. **一個真正的版本落差（不是異常，是時序）**：`lane-routing-registry.yaml` 已到 **epoch 30**，而 `model-lane-assignment.json` 仍自稱 **`registry_epoch: 29`**。這一個落差就解釋了全部 10 個值層面的不一致——registry 前進了，投影沒有重算。
3. **歷史殘留（有出處、有日期）**：PLAN 的 `transport_model` 仍是 `opencode-go/minimax-m3.1-flash-free`，來源 commit 是 **`a1bd583`「FAR-MINIMAX-MANDATE-20261021: bind all three lanes to MiniMax M3.1 Flash (epoch 25)」**——那是 2026-10-21 一輪 owner 把三條車道全綁 MiniMax 的決策，之後 `f4a2ec4`／`b22706e`／`924af95` 只還原了「宣告的 model」，沒有還原 `transport_model`。**這是一個合法的回合級決策留下的殘值，不是誰把線接錯。**

---

## 四個平面（不可互比）

| 平面 | 權威來源 | 內容 | 可以被誰改 |
|---|---|---|---|
| **L 車道** | `config/lane-routing-registry.yaml`（`epoch`、每角色 `selection_authority`） | 車道 → provider/model 的正式綁定 | 只有該回合的 owner order，經 rebind |
| **R 回合** | 每回合 `role_mandate.json`，由 `scripts/runtime_role_binding_assert.py`（P1-A）在派工前消費 | 該回合把某車道指向哪一臂；**允許與 L 不同** | 該回合的 owner；P1-A 於派工前 fail-closed 檢查 |
| **S 會話** | Hermes `state.db` 的 `sessions.model` / `model_config` | 某個對話實際跑哪個模型 | 使用者/該 session；**永遠不是車道綁定** |
| **V 實際服務** | `session_model_usage` 收據 | 那一次呼叫真的由誰回答 | 無（事後事實） |

**不可互比規則**：S 的值不得寫入 L 的宣告欄位，也不得拿來判 L 對錯；R 與 L 不同是常態，只要 P1-A 在派工前擋住就行；只有 L↔投影（assignment）之間的差異才是「管線衛生」問題。

---

## 本次量測（可重跑）

`scripts/lane_scope_isolation.py` 只比 L↔投影，並為每個差異找出**引進該值的 commit**：

| 分類 | 筆數 | 說明 |
|---|---|---|
| `SUPERSEDED_ROUND_RESIDUE` | **3** | 值可追到 `a1bd583`（MINIMAX-MANDATE，epoch 25 的三車道 MiniMax 決策），後續只部分還原 |
| `CURRENT_ROUND_NOT_DERIVED` | **7** | 值來自更早的 commit，本回合沒有依 registry 重算 |
| 合計 | **10** | 與 `registry_epoch` 29 vs 30 的落差一致 |

**S 平面觀察（並行 session，全部非車道漂移）**：

| session | 模型 | 開始（UTC+8） | 訊息數 |
|---|---|---|---|
| `20261022_100010_67dad4` | deepseek-v4.1-flash | 2026-10-22 10:07 | 239 |
| `20261022_091710_18a854` | deepseek-v4.1-flash | 2026-10-22 09:28 | 160 |
| `20261021_224136_53890b`（本回合） | deepseek-v4.1-flash | 2026-10-21 23:08 | 327 |
| 另有 4 個 10-20/10-21 的 root session | minimax / deepseek / glm | — | 184–245 |

也就是說：**同一時間確實有多個 session 在跑不同模型**。把它們算進「車道不一致」是把平面的錯誤當成系統的錯誤。

---

## 隔離機制（已落地，不是文件而已）

| 檔案 | 作用 |
|---|---|
| `scripts/lane_scope_isolation.py` | 只比 L↔投影；用 `git log -S` 為每個差異找出來源 commit 並分類；輸出 `var/R14-LANE-SCOPE-20261022/isolation.json` |
| `config/lane_scope_exceptions.json` | 把已知殘留**逐筆登記**（角色/index/欄位/L 值/投影值/分類/來源 commit/日期），另記 `epoch_skew` = registry 30 vs assignment 29 與其原因 |
| `tests/test_lane_scope_isolation.py` | 四條守則：①**新的**漂移沒有登記就紅；②每筆例外必須有出處（布林值例外，因 `git -S` 無法歸屬，測試明說）；③session 用的模型不得成為車道的宣告臂（且 transport 必為裸 id 或 `provider/id`）；④assignment 必須標明它投影自哪個 epoch，**只有已登記的那個落差可以存在** |

`4 passed`。這代表：殘留看得見、有出處、有日期；而任何**新的**漂移會立刻紅。

---

## 對先前 TT 的更正

| 編號 | 原判 | 更正後 |
|---|---|---|
| `TT-R14-034` | 「車道 assignment 宣告與實際不符，屬接線錯誤」 | **改判**：①`registry_epoch` 29 vs registry 30 的**版本落差**（唯一根因）；②`a1bd583` 的**回合級決策殘留**（有出處）。**不是錯誤接線，也不是異常行為。** |
| `TT-R14-035` | 「漂移檢測器看不到漂移」 | **保留但改述**：`check_drift()` 比的是「上一版同一份檔案」的值，因此無法區分 L／R／S 三個平面；它需要的不是更嚴，而是**先有平面**。 |
| `TT-R14-036` | 「收據比對接受被改的 `resolvedModel`」 | **不變**（這是 V 平面自身的完整性問題，與平面混淆無關）。 |

---

## 正確的修法（下一步，尚未執行）

把 assignment 從 **registry epoch 30** 重新投影，且必須**同一批**完成：assignment revision 30→31、10 個衍生欄位、87 個 projection、drift baseline。我上一輪嘗試只改 assignment，結果 8 個車道測試轉紅——因為 baseline 把殘值釘成期望值。**半套 rebind 比登記缺陷更糟**，所以本回合只登記、不改綁定；`scripts/lane_assignment_resync.py` 已備好，等同一批變更一起做。

## 宣稱上限

本回合證明的是：**平面已經分開、殘留有出處、新漂移會被抓到**。沒有證明的是：投影已正確（它仍是 epoch 29）、runtime 綁定已變更（沒有動）、以及任何「車道保真度已達成」——PLAN 的實際服務歸屬仍缺逐呼叫歸因（`TT-R14-036` 未修）。
