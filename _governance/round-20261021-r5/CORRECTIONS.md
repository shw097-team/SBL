# R5 — 自致缺陷與修正（CORRECTIONS）

每條都是本輪自己造成、自己發現並修正的缺陷，與 `F-R5-HARNESS-UNINSTALL-TRAVERSAL-001`（既有缺
陷）分開記帳。

## 1. `check_sources.py` 長路徑漏判 — `MISSING` 而非 `MATCH`

三個 KP 檔路徑超過 260 字元，`Path.is_file()` 在 Windows 回 False，被記成 `MISSING`，導致 46 項來源
驗證出現 3 個假缺件。修正：以 `\\?\` 延長路徑前綴存取；修正後 46/46 `MATCH`。

## 2. `gen_negative_matrix.py` 用 node id 當 `-k` 模式 — rc=4 而非 0

把未完全匹配的測試名當 `tests/...::name` 傳入，pytest 直接 usage error（rc=4），而腳本當時只看
`rc != 0` 就把該案例記為失敗，造成「矩陣全紅」的假訊息。修正：改用 `-k` 子字串匹配；並另外記錄
`skipped`，避免把 skip 當 PASS。

## 3. `sbl_harness/__init__.py` 一次 patch 引入語法錯誤

`path unlink_guard = None`（字詞錯置）寫入後 lint 失敗；同回合內發現並移除，未進入任何 commit。

## 4. 獨立 VERIFY 車道（gpt-6.1-sol）找到的三個真缺陷（maker 自己沒看出來）

這不是自致缺陷，但記在同一份紀律裡：獨立檢查的價值就是抓到 maker 的盲點。

| # | 缺陷 | 修法 | commit |
|---|---|---|---|
| a | 刪除後的 `rglob("*")` + `rmdir` 清掃會跟隨 Windows junction，刪到 root 外的空目錄 | 改為固定清單 `skills/<name>`、`skills`，逐個檢查 link + resolve 內含 | `ab9a354` |
| b | 逃生測試宣告零 digest，digest 比對可能才是拒絕原因，掩蓋壞掉的路徑守衛 | 測試宣告 sentinel 的**真實** digest，只有路徑守衛能拒絕 | `ab9a354`、`a6bcdd0` |
| c | manifest 鍵用反斜線時 `files[key]` KeyError（驗證正規化、查表用原鍵） | deletable 保存 (原鍵, 正規化, 解析路徑) 三元組 | `ab9a354` |

## 5. 流程遵守

- 閘門（secret scan）與 commit 分開呼叫，不在同一條 `&&` 鏈（R4 #6 教訓）。
- 每個 commit 前先跑 `tools/run_gates.py`（11/11 exit 0）。
- 注入對照（injection control）先於宣稱：四個逃生案例在 pre-repair bytes 上確認會 FAIL，才寫
  `finding_closed_locally`。
