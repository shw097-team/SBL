# POST_STATE — R13 原生鏈讀回（實測）

**時間**：2026-10-21 · 執行者：Hermes（受治理 Runtime 面）· 控制平面：HG-KSEOS spine `var/shared-spine/hg-kseos.db`

## 1. 車道（三 probe 全 served，逐輪 mandate）

| lane | required | served | rank | usage |
|---|---|---|---|---|
| PLAN | `openai-codex/gpt-6.1-sol` | 同左 | 2（rank1 為 minimax） | 200 |
| EXECUTE | `opencode-go/minimax-m3.1-flash-free` | 同左 | 2（rank1 為 deepseek） | 200 |
| VERIFY_SECURITY | `openai-codex/gpt-6.1-sol` | 同左 | 1 | 200 |

證據：`raw/PLAN.json`、`raw/EXECUTE.json`、`raw/VERIFY_SECURITY.json`。

## 2. 原生鏈（不是示意）

| 階段 | 實際 | 證據 |
|---|---|---|
| project 建立（RED） | `HGKR13-RED`，target=HGK，**CWD 非 repo** → admission 失敗 | `raw/stage_red.json`：`InvariantViolation: ERR_WORKORDER_CRITICAL_FIELD_MISSING` |
| project 建立（WO） | `HGKR13-WO` → `WO-TS-WO-01/02`，`base_head=b22706ebbdff…` | `raw/stage_wo.json` |
| ExecutionBinding | `taskspecs.permissions_json.role_binding`（`HGK-ROLE-BINDING/1`，scope 2 路徑、expiry +6h、EXECUTE/VERIFY arm） | `raw/binding.json` |
| Permit/lease | `spine.acquire_lease("file:src/hg_kseos/lifecycle.py", "hermes-r13-writer", ttl=7200)` | `raw/stage_wo.json.lease` |
| bounded writer | EXECUTE 車道（minimax）套 patch，只動 `lifecycle.py` | `raw/EXECUTE_write.json`、`raw/candidate.diff` |
| RED | patch 前：**2 failed**（`base_head` 取到 CWD repo；非 repo target 未拋錯） | `raw/RED_test_output.txt` |
| GREEN | patch 後：**2 passed** | `raw/GREEN_test_output.txt` |
| 獨立 checker | VERIFY 車道（gpt-6.1-sol）唯讀複核；`a/b/c/d=true`，`verdict=PASS`，自述「Tests not run（static review）」 | `raw/VERIFY_check.json` |
| 結果落帳 | `record_workorder_result` → **`WO-TS-WO-01` = VERIFIED**，`role_binding_digest=7111d08c…` | `raw/role_evidence.json` + spine `workorders.result_json` |
| project 前進 | `WORKORDERS_ADMITTED → EXECUTING → VERIFYING → EVOLUTION_REVIEW` + checkpoint | `raw/stage_finalize.json` |
| 修復後正向 | `HGKR13-GREEN`：**同一非 repo CWD** 下 admission 成功，`base_head=b22706e…` | `raw/stage_green.json` |

## 3. 三個 typed 負控（全部 deny）

| 負控 | 結果 |
|---|---|
| maker 自審（writer==checker） | `InvariantViolation: ERR_WORKORDER_SELF_REVIEW` |
| 已 VERIFIED 的 WO 重放 | `InvariantViolation: ERR_WORKORDER_RESULT_STATE` |
| binding 過期 | `BindingError: ERR_ROLE_BINDING_EXPIRED` |

## 4. 落地狀態

- HGK commit **`49f48ae`**（只 stage `src/hg_kseos/lifecycle.py` + `tests/test_r13_repo_head_cwd.py`）。
- 同工作樹其他人的 7 個 modified + `.hgk/` untracked **未被 stage、未被 reset**。
- 檢查者隔離（O-2）：候選**唯讀**；checker 產物落在 `var/checker-scratch/round-20261021-r13/`（非 repo 路徑），以 sha 記帳。

## 5. 未閉合（不掩蓋）

| 項 | 狀態 |
|---|---|
| D-06 SP 身份（Commander/Challenge 真 invoke） | **OPEN** —— 本回合是**車道**執行（`LANE_ONLY`），不是 SP 身份；不因 WO VERIFIED 而降級宣稱 |
| O-4 三 Plugin | `HOST_PENDING`（見 `CR-PLUGIN-SCHEMA-AUTHORITY.md`） |
| 語義分母 | `UNKNOWN` |
| `SBL_FULL_PRODUCT` | **OPEN** |

## 6. 新觀察 `O-R13-001`

writer 車道再次以 `ERR_NO_ARM_EMITTED_NONCE` 收尾（`usage` 仍 200、patch 已套用）——與 R12 的 `O-R12-001` 同一模式，第二次獨立重現。**`--require-arm` 不能作為 writer 回合的唯一寫入憑證**；寫入必須以 `git diff` + digest 驗收。此為車道設計缺陷，建議 dispatcher 對 writer 回合改以 diff digest 為 gate。

## 7. 第二切片（自修補）與完整分母

第一個候選用 patch 後只跑了新測試（2 passed），**未跑全量**；全量後發現 5 個 G0 控制測試由
`target_root` 空值的舊行為繼承 CWD，fail-closed 後全數失敗 —— 這是本回合自己造成的回歸，如實記在此。

處理：切出第二個 WO（`WO-TS-WO-02`，主體 `tests/test_g0_wave3_controls.py`），只讓 fixture 明確宣告
target，不動任何斷言；由 VERIFY 車道第二次獨立複核（`a/b/c=true`，明言「no tests weakened, skipped or deleted」）
後才落帳 VERIFIED（`role_binding_digest d53b2238`）。

| 指標 | 回合前 | 兩切片後 |
|---|---|---|
| HGK 全量 | 18 failed / 578 passed / 90 subtests / 143.58s | **18 failed / 580 passed / 90 subtests / 146.94s** |
| 新增失敗 | — | **0**（`raw/before_failed.txt` vs `raw/final_failed.txt` 集合相同） |
| 新增通過 | — | +2（`tests/test_r13_repo_head_cwd.py`） |

HGK commits：`49f48ae`（slice 1）、`5119c97`（slice 2）。工作樹中其他作者的 7 個 modified 仍未 stage。
