# L5 — FHS 硬入口（EC-R26-001 / R26-03）結果

**狀態：PASS**（機制已證；blast radius 誠實列出）

## 一句話
`scripts/hgk-lane-dispatch.py` 現在在**任何子行程存在之前**驗 SessionBinding 並消耗一次性 capability：
沒有 binding → `FHS_ENTRY_ASSERT_REQUIRED` exit 20、零 spawn；有 binding 但沒有/已用過的 token →
`FHS_ENTRY_TOKEN_REQUIRED` exit 28 / `FHS_ENTRY_TOKEN_CONSUMED` exit 29。

## 已執行（canonical: epoch-41 副本 `FHS_R26_WT/hgk-bridge`，registry `5c7ce9de…c4b6`）

| 個案 | 期望 code | 實測 | exit |
|---|---|---|---|
| `E01_FRESH_PROCESS_BYPASS` | `FHS_ENTRY_ASSERT_REQUIRED` | 同 | **20** |
| `POS_E01B_BOUND_CONTROL` | 過閘、下一階段失敗 | `ERR_LANE_ALL_ROUTES_EXHAUSTED`，attempts=1，token spent=true | **3** |
| `E02_TOKEN_REPLAY` | `FHS_ENTRY_TOKEN_CONSUMED` | 同 | **29** |
| `E03_EPOCH_DRIFT` | `FHS_ENTRY_EPOCH_DRIFT` | 同 | **22** |
| `E04_RETIRED_ARM` | `FHS_ENTRY_RETIRED_ARM` | 同（replacement `opencode-go/mimo-v2.6-flash`；reader `--assert-arm` exit 9） | **24** |
| `E05_NO_CAPABILITY` | `FHS_ENTRY_TOKEN_REQUIRED` | 同 | **28** |

`selftest_bridge.out` = `18775fd668d946751b71f5fceec5177c6df0d2eeb8e80a8eedccb4d5785a032b`（exit 0, 6/6）。
真 clone `FHS/HG-KSEOS`（registry `811bf1a5…055c3`）同樣 6/6：`selftest_hgkclone.out`。

**零 spawn 的量測方式**：子行程 sentinel（stub 子行程會寫 `$HGK_STUB_PROMPT_OUT`）。E01/E02/E05 該檔不存在；
POS 該檔存在且 `attempts=1` —— 同一支儀器分辨「沒 spawn」與「spawn 了」。

## wrapper 鏈（`sh scripts/hgk-lane-run.sh`）
- W0（未設 `FHS_BINDING`）→ exit **2**，`HGK-LANE-RUN REFUSED: FHS_BINDING is not set`
- W1（有效 binding，bridge epoch 41）→ exit **4**，**過入口閘門**後在下一階段被拒：`ERR_LANE_PIN_IDENTITY_INVALID`（宣告的 codex pin 不在本機；零 spawn、零 model call）
- W2（同一 binding 再跑）→ exit **29**，`FHS_ENTRY_TOKEN_CONSUMED`

## 測試
- `pytest tests/test_fhs_entry_guard.py -q` → **21 passed**（exit 0）
- `scripts/selftest_fhs_entry_guard.py` → **6/6 PASS**（exit 0）
- 11 個既有 dispatcher 測試檔 → **122 failed / 127 passed / 1 xfailed**

## Blast radius（不隱藏）
122 個失敗**全部**是同一個 code：`FHS_ENTRY_ASSERT_REQUIRED`（`grep -oE 'FHS_ENTRY_[A-Z_]+'` 只出現這一個，311 次）。
它們就是「未綁定的直接 dispatch」，正是 finding 說必須被拒的東西。遷移前提（resume predicate）：
把 dispatcher 測試套件改到 bound-entry fixture（session 級 binding + 每次呼叫一個 capability）。目前**卡在治理決定**——
其中一批測試刻意 dispatch **合成臂**（控制平面不放行的臂），這類臂無法由合法 issuer 簽出 binding，
在測試 harness 裡自簽就會變成「第二個 issuer」。

## 不宣稱（not claimed）
- 只證明**本 repo dispatcher** 內的攔截；desktop app session / 其他 host 必須自行採用同一 ABI，這裡無法代為強制。
- 122 個既有測試未遷移（套件目前紅）。
- dispatcher 自己的 pool（本 repo epoch）未與 HGK 控制平面 pool 對帳（那是 L4 的 port）；實際載重的是「binding 的 arm == 即將 spawn 的 arm」。
- capability 授權的是**入口**（lane + 第一個 arm），不是每次 retry 都重新發一次。
- 全程無網路、無 model call。

## 控制平面 / reader 身分（逐字）
- bridge registry `5c7ce9de2c7602258bca7f0ce8b2dc1e295eca547b39ac75d10a21f2cf31c4b6`（epoch 41, `IN_FORCE`）
- HG-KSEOS registry `811bf1a5eea4304c057dfc95974e31b4b7655a588091f674db2cf57dbb3055c3`（epoch 41）
- SBL reader `fhs_3lm.py` `49a1eea688a40649767ee08a11e8d87f83cc6efe38245f61abb91e36400f4afb`（L2 commit `5402fe3`, schema `FHS.3LM.Binding/2`）

完整 artifact 索引與每個 log 的 sha256：`evidence/L5/L5_EVIDENCE.md`。
