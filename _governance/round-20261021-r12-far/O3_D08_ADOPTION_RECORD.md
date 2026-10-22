# D-08 / O-3 收編紀錄 — 九個他人 untracked 測試模組（2026-10-23）

**權威**：FAR R12（`FAR_DEVIATION_STUDY.md` §2 D-08、§3 O-3）——owner 決策 **收編**（選項：收編／隔離／丟棄）。
**執行**：Kanban swarm `t_c1b4d403` 之 worker `t_aea902e3`（本檔為該決策的獨立收編 commit，非名義 stage）。
**量測基準 commit**：`9c36a77`（收編時 HEAD，2026-10-23 00:51 由同期 session 併入）；收編本體於 `7d9b64b`／`9fa79dd`（2026-10-22 08:47／09:03，author `HGK R14 WO`）落板。

---

## 1. 收編清單（9 個測試模組 — 逐檔可讀回）

R11 baseline（`evidence/r11-20261021-intake` round-20261021-r11 `00_ROUND_PLAN.md` TS08，2026-10-21T23:20+08:00，HEAD `b22706e`，dirty tree）具名列出的 9 個 untracked 測試模組，現皆為 tracked，逐檔 sha256 前綴如下：

| # | 模組 | 首次收編 commit | sha256 (前 16) |
|---|---|---|---|
| 1 | `tests/test_execute_luna_route.py` | `9fa79dd` | `2a290c5844547d67` |
| 2 | `tests/test_far_lane_fix_20261015.py` | `9fa79dd` | `5371cf8b3ab8741d` |
| 3 | `tests/test_governed_runtime_controller.py` | `9fa79dd` | `fdf1dbc251eee5e7` |
| 4 | `tests/test_lane_effort_enforcement.py` | `9fa79dd` | `18742bf07b4055ae` |
| 5 | `tests/test_lane_guard.py` | `9fa79dd` | `d50ad8c94edfb383` |
| 6 | `tests/test_mandatory_tool_guard.py` | `9fa79dd` | `4b69e576573e6f02` |
| 7 | `tests/test_matrix_d_full.py` | `7d9b64b` | `e544ab36c30ea3fa` |
| 8 | `tests/test_role_binding_enforcement.py` | `9fa79dd` | `abb2e5007f346f97` |
| 9 | `tests/test_source_repoint.py` | `9fa79dd` | `608a3382be31b3e9` |

## 2. 同批髒樹項目 disposition（D-08 觀測的其餘部分）

| 項 | R12 觀測 | 現況 | 證據 |
|---|---|---|---|
| `tests/w3_solution/`（7 test + support） | untracked | **tracked** @ `9fa79dd` | `git show 9fa79dd --name-status` |
| 2–3 個測試 `.bak`（TS08 named：`test_governed_runtime_controller.py.bak`、`test_lane_guard.py.bak`、`test_lane_policy.py.bak…`） | dirty tree | **隔離保留** @ `var/quarantine/bak-20261022/tests/`（3 檔齊全，mtime 保留 10-07／10-15／10-16；quarantine 動作 2026-10-22 08:46）——符合 FAR §5「`.bak` 保留」 | `ls var/quarantine/bak-20261022/tests/` |
| 1 modified 測試 `tests/test_task014_named_method_closure.py` | modified | **原樣保留、未 review** @ `db68ee4`（`chore(repo): preserve the six inherited working-tree diffs as they stand, unreviewed`） | `git show db68ee4 --name-status` |

## 3. 作者／授權（misattribution 關閉）

- R8 拒絕 stage 的理由（`round-20261021-r8/R8_ROUND_REPORT.md` L75）：「adding ~800 lines of another party's uncommitted test code under this commit would misattribute authorship」。R11 TS08 同樣記「作者／授權未知，未 stage」。
- **授權鏈**：FAR R12 §3 O-3 owner 決策 = **收編**；本收編在該決策下執行。收編動作為 lane WO commits（`7d9b64b`／`9fa79dd`，author `HGK R14 WO`）+ 本獨立紀錄 commit。
- **作者歸屬**：9 個模組為既有 lane/round session 的產出；repo 歷史中只存在單一收編 commit，**無法**由 git 歷史還原逐檔原作者。本紀錄**不宣稱**作者身分、**不**將收編 commit 的 author 視為測試內容作者。

## 4. 驗證（clean checkout 可重現性 — R9-05 close condition）

方法：`pytest tests -q -p no:cacheprovider --tb=no -rf`，venv `HG-KSEOS/.venv`（Python 3.12.13），`PYTHONPATH=<checkout>/src`，`PIPD_ROOT=C:/Projects/Agent_Workspace/PIPD`，Windows scratch。log 於 kanban task workspace `evidence/`。

| run | checkout | HEAD | 結果 | log sha256 (前16) |
|---|---|---|---|---|
| A（基準側） | 主 checkout（含同期 session WIP：`scripts/hgk-lane-dispatch.py` +100、3 個 untracked 檔） | `9c36a77`+WIP | **10F / 653P / 1 skip / 90 subtests** | `afd7914a192a735` |
| B（受驗側） | depth-1 乾淨 clone `_d08_repro` | `9c36a77` 淨 | **20F / 625P / 1 skip / 90 subtests** | `ae8a1ab37206f34` |

- **收編生效證明**：乾淨 checkout 完整 collect 9 個模組共 **113 個測試項目**（`--collect-only` 比對）。
- 失敗集合對比：**共同 5**（`test_matrix_d_full` 3、`test_role_binding_enforcement` 1、`test_lane_policy` 1 → 於 HEAD 上兩側皆紅，屬既有失敗，非收編範圍）、**clone-only 15**（`test_autonomy_evolution` 5、`test_cs_a_gate_repair` 5、`test_far_lane_fix_20261015` 5）、**main-only 5**（`w3_solution` 4、`test_c2_case_run` 1，與同期 WIP 時序重疊）。
- clone-only 15 的根因已抽樣定名：(a) `ERR_LANE_TOOLCHAIN_DECLARATION_MISSING`（本機 lane toolchain 宣告不存在於乾淨 checkout）；(b) `ERR_REPO_HEAD:worktrees` —— `worktrees/` 為 gitignore 目錄，主機 checkout 有、乾淨 clone 無。即：**局部失敗類別 = 對 gitignored 本機狀態（`worktrees/`、`var/`、machine lane 宣告）的耦合**，非收編遺漏。
- 排除項：一次嵌套於 `HG-KSEOS/var/d08-repro` 的 run（80F/565P）因 `parents[2]` 路徑解析到錯位置而失效，**不採計**為可重現性證據；其 diagnose 僅用於修正跑法。

## 5. 主張上限（claim ceiling）

- **可宣稱**：D-08 的所有權／可追溯缺陷**已關閉**——9 模組 tracked、`.bak` 隔離保留、modified 測試原樣留檔、收編以獨立 commit 成文；乾淨 checkout 能 collect 全部 9 模組。
- **不可宣稱**：R9-05 的完整 close condition（乾淨 checkout 重現同樣 conformance 計數）**尚未達成**——共同 5 紅 + clone-only 15 紅；上述為既有本機狀態耦合與既有失敗，屬後續 checker／修復回合範圍。本紀錄非驗收、無完成百分比（D-04 ceiling）、不變更任何 DOC 條款。

## 6. 本回合側效（2026-10-22 23:30–2026-10-23 01:05 +08:00）

- 寫入：本檔（`docs/ADOPTION-D08-O3-UNTRACKED-TESTS-20261023.md`）單檔、單 commit、`git commit --only`（不同步任何他人 WIP）。
- scratch：`var/d08-repro/`（嵌套 clone，已判失效）、`var/d08-tmp/`、`C:/Projects/Agent_Workspace/_d08_repro/`（depth-1 clone）、task workspace `evidence/*.log`（4 份）。
- 未做：push、merge、stage 他人檔案、改任何產品程式碼／DOC／registry。
- Rollback：`git rm docs/ADOPTION-D08-O3-UNTRACKED-TESTS-20261023.md`；scratch 三處可直接刪除。
