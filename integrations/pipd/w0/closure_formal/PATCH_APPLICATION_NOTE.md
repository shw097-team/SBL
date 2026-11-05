# 父層套用註記 — F2 patch 03（2026-11-05 run 1040）

## 為什麼有這份註記

`lanes/f2/out/PATCH_MINIMALITY.json` 的 `reference_gate_unmodified.holds=true` 說的是
**lane 內部**：F2 只把 patch 03 套在自己 materialise 的副本 `gate_patched/supply_chain_gate.py`，
沒有動到它當成唯讀輸入的 `lanes/wp19/supply_chain_gate.py`。這句話在 lane 範圍內為真。

但**父層其後把 patch 03 套進了要交付的候選分支**：SBL `integrations/pipd/w0/lanes/wp19/supply_chain_gate.py`
（commit `cd4b2eb`），並另外加了 2 條測試。若不說明，讀者同時看 PR 與本包會得到矛盾印象。

## 實際套用內容

| 項 | 值 |
|---|---|
| 套用位置 | `integrations/pipd/w0/lanes/wp19/supply_chain_gate.py`（SBL 候選分支） |
| 套用方式 | `git apply -p1 --directory=integrations/pipd/w0/lanes/wp19 03_supply_chain_gate_runtime_scope.patch` |
| 與 lane 副本的關係 | **LF 正規化後 byte-identical**（`71fbedc62b9047c6…`，40,544 bytes）；原始 sha 差異僅為 CRLF↔LF，repo 對該檔強制 `eol=lf` |
| 額外新增 | `tests/test_supply_chain_gate.py` 兩條：extras 不參與判定；runtime 缺件回 `SBOM_COMPONENT_MISSING_RUNTIME` |
| 套用後行為 | 對 `origin/main` `004e8891` 的 `integrations/pipd` 實跑：**PASS 6／FAIL 1／HOLD 0**，exit 1，唯一 FAIL 為 `UNDECLARED_DEPENDENCY` — 與 `out/WP19_AFTER_REPAIR_RAW.json` 一致 |
| gate 自身測試 | 31 tests OK（29 原有＋2 新增） |

## 這不是放寬

`no_check_code_removed`、`no_check_downgraded` 兩項斷言仍成立：七項檢查一項沒少，`SBOM_COMPONENT_RECONCILE`
的判定面從「runtime ＋ extras」縮到「runtime」，而 extras 仍逐筆列在 `counts.optional_not_listed`；
runtime 缺件改由更精確的 `SBOM_COMPONENT_MISSING_RUNTIME` 回報（原本會誤報成 `SBOM_COMPONENT_MISMATCH`）。
新增的兩條測試把「extras 不判定」與「runtime 缺件必須 FAIL」同時釘住，避免縮面被靜默擴大。

## 邊界

本註記不改變 `WP19_DONE=false`、`original_ci_reader_ack=NOT_OBSERVED`、`claim_ceiling=AUTHOR_SUPPLY_CHAIN_LOCAL`。
