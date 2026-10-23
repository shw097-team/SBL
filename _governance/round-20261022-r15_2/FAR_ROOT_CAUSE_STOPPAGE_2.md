# 為什麼又停了（第二輪）：佇列沒有可執行單位，不是模型罷工

FAR `PLAN__FAR_WHY_STOP_4`（PLAN 車道 rank 2 `gpt-6.1-sol`、199.58s、nonce ✓、KB 引用 12 條）裁決：
**REPRESENTATION 支配**，不是模型、不是排程器。

## 量測到的事實

```
cron tick 每 15 分鐘仍在跑：advance_queue start ... no AGENT item is READY - stopping
                             steps=0 done=33 parked=4 owner=4 host=1 ready=0
queue: DONE 33 | PARKED 4 | PARTIAL 3 | DONE_RECEIPT_RED 1 | NEEDS_RECIPE 12
READY 且帶 resume_cmd 的項目：0
```

監督器活著、每 15 分鐘醒一次、每次都判定「沒有可執行項」後乾淨退出。十二條待辦**被計數、被顯示、但沒有命令**，
所以對驅動器而言與「沒事可做」無法區分。上一輪修的是 `PARTIAL` 不在選擇集；這一輪我把同一批工作改叫
`NEEDS_RECIPE`——同樣不在選擇集。同一個缺陷換了名字。

## 已修的（可重算，不靠宣稱）

1. `tools/materialize_authoring.py`：每個無命令的 authoring 義務 → 一份有界 brief ＋ 既有的 EXECUTE 派工命令
   （`--role EXECUTE --brief … --nonce …`）、`expect_artefact`、`accept_cmd`。冪等，不碰 DONE，不碰 OWNER/HOST。
2. `advance_queue.py`：新增 `classify_dispatch()`，把三個事實分開判——派工結果、產物是否存在、驗收是否通過：
   派工逾時但產物在 → `PARTIAL` 轉 TEST 階段（不得重寫，那是被禁止的盲目重試）；派工綠但產物不在 → `PARKED`；
   派工綠且驗收綠 → `DONE`。零選取時印出未解數量與原因分類，不再宣稱「沒事了」。
3. `tests/test_authoring_materialisation.py`：8 tests，釘住材化、冪等、OWNER/HOST 不被材化、三事實分類。

## 實測（含失敗）

| 派工 | brief 形態 | 結果 |
|---|---|---|
| `EXECUTE__DEN-C08` | 通用（「寫測試」） | 300s 逾時、`dispatch_exit=3`、**零產物** |
| `EXECUTE__DEN-C10_narrow` | 指名單一 surface 檔 ＋ 4 條行為 | **93.66s、ok、nonce、產物 4,671 bytes** |
| 驗收 | `pytest tests/test_gstack_named_method_route.py` | **4 passed**（HG-KSEOS） |

結論不是「EXECUTE 車道不行」，而是**通才 brief 不行**：車道花 300 秒探索一個它從沒見過的 repo。
brief 指名 `src/hg_kseos/named_methods.py` 與四條斷言後，同一個車道 94 秒交件。

## 尚未解決（誠實列出）

- 其餘 11 條仍是 `NEEDS_RECIPE`，但已附上 surface 三角定位（`surface_triage`：檔在 `_r152_ev` 還是 `HG-KSEOS`）
  與 `lesson_ref`，下一步是按 C10 的形狀逐條窄化，而不是再發通才 brief。
- C08/C09 的 kanban/swarm 實作不在 `HG-KSEOS/scripts`，在 `.hgk/checker-upgrade-20261009/tools/`（快照目錄）；
  要測哪一個是**範圍問題**，不是寫測試問題——已記在 triage 裡，不假裝已解。
- 宣稱上限不變：`LOCALLY_VERIFIED_PARTIAL`。C10 是 `LANE_AUTHORED + TESTS_PASS`，仍無獨立驗收。
