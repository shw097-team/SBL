# L5 — FHS 硬入口（EC-R26-001 / R26-03）evidence index

所有數字都讀自本目錄下的捕獲檔；沒有任何值是被「打進」產出器的（`make_result.py` 讀不到檔案就 `exit`）。

## 1. 交付物（worktree `C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-hook`，branch `r27/fhs-entry-hook`）

| 檔案 | 內容 |
|---|---|
| `scripts/fhs_entry_guard.py`（新，stdlib only） | 機械閘門：`assert-entry`（binding 重驗 + `--guard-token` 一次性能力）與 `consume-token`；十個 fail-closed code，各自 exit 20–29 |
| `scripts/hgk-lane-run.sh`（新） | 唯一入口：binding → mint capability → `exec` dispatcher（`--fhs-entry-token` 用同一個 `run_id`） |
| `scripts/selftest_fhs_entry_guard.py`（新） | 獨立跑 E01 / POS / E02 / E03 / E04 / E05，六案有任一不符即非零退出 |
| `tests/test_fhs_entry_guard.py`（新） | pytest 21 案（單元 18 + 真子程序 3） |
| `scripts/hgk-lane-dispatch.py`（+96/−4） | 五個 entry flag、by-path import、`fhs_entry_precheck()`、spawn 邊界前一個 hook、receipt 一個 `fhs_entry` 欄位、`emit_refusal(exit_code=)` |
| `AGENTS.md`（+11） | 非權威註記，指名兩支腳本 |

## 2. 主執行（canonical，對 brief 指定的 epoch-41 副本 `FHS_R26_WT/hgk-bridge`）

```
python scripts/selftest_fhs_entry_guard.py \
  --hgk-root C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-bridge \
  --workdir  .../evidence/L5/selftest_bridge          # exit 0, 6/6 PASS
```

| 個案 | 期望 | 實測 | exit | log (sha256) |
|---|---|---|---|---|
| `E01_FRESH_PROCESS_BYPASS` | `FHS_ENTRY_ASSERT_REQUIRED` | `FHS_ENTRY_ASSERT_REQUIRED` | 20 | `selftest_bridge/E01_FRESH_PROCESS_BYPASS/run.log` `b529430d…e520f` |
| `POS_E01B_BOUND_CONTROL` | 通過閘門、在下一個階段失敗 | `ERR_LANE_ALL_ROUTES_EXHAUSTED`（attempts=1，sentinel 已寫入，token spent=true） | 3 | `selftest_bridge/POS_E01B_BOUND_CONTROL/run.log` `0e8c13c0…a862a` |
| `E02_TOKEN_REPLAY` | `FHS_ENTRY_TOKEN_CONSUMED` | `FHS_ENTRY_TOKEN_CONSUMED` | 29 | `…/E02_TOKEN_REPLAY/run.log` `89ca84ad…a64173` |
| `E03_EPOCH_DRIFT` | `FHS_ENTRY_EPOCH_DRIFT` | `FHS_ENTRY_EPOCH_DRIFT` | 22 | `…/E03_EPOCH_DRIFT/run.log` `d5f29d8f…1d28c3` |
| `E04_RETIRED_ARM` | `FHS_ENTRY_RETIRED_ARM` | `FHS_ENTRY_RETIRED_ARM`（replacement `opencode-go/mimo-v2.6-flash`；reader `--assert-arm` 同案 exit 9） | 24 | `…/E04_RETIRED_ARM/run.log` `2e41118b…e998060` |
| `E05_NO_CAPABILITY` | `FHS_ENTRY_TOKEN_REQUIRED` | `FHS_ENTRY_TOKEN_REQUIRED` | 28 | `…/E05_NO_CAPABILITY/run.log` `cc325695…ac9c0c` |

總表：`selftest_bridge.out` `18775fd6…785a032b`、`selftest_bridge/SELFTEST_RESULT.json` `a0981d02…ca1c3d3`。

第二個控制平面（真 clone `C:/Projects/Agent_Workspace/FHS/HG-KSEOS`，epoch 41，registry `811bf1a5…055c3`）同樣 6/6：`selftest_hgkclone.out`。

## 3. wrapper 鏈（`sh scripts/hgk-lane-run.sh`）

| 案 | 指令 | exit | 觀察 | log (sha256) |
|---|---|---|---|---|
| W0 | `FHS_BINDING` 未設 | 2 | `HGK-LANE-RUN REFUSED: FHS_BINDING is not set` | `wrap_W0.out` `fb1c4d87…13c33c9` |
| W1 | 有效 binding（bridge，epoch 41） | 4 | **通過入口閘門**，在下一個階段被拒：`ERR_LANE_PIN_IDENTITY_INVALID`（宣告的 codex pin 不存在於本機，零 spawn、零 model call） | `wrap_W1.out` `392dd4df…c0918582` |
| W2 | 同一 binding 再跑一次 | 29 | `FHS_ENTRY_TOKEN_CONSUMED`（capability 一次性） | `wrap_W2.out` `b4645349…8c580148d` |

capability 實體（`spent=true`、`consumer_pid` 已記錄）：`wrapper_capabilities/l5-wrap-bridge-002.json` 與 `.spent`。
binding 記錄（reader 自己簽發）：`bindings/l5-wrap-bridge-002/EXECUTE_primary_5d59a4b7d141932c.json`。

## 4. 測試

| 指令 | exit | 結果 | log (sha256) |
|---|---|---|---|
| `python -m pytest tests/test_fhs_entry_guard.py -q` | 0 | 21 passed | `pytest_fhs_entry_guard.out` `c9accd24…cb9cbebc` |
| 11 個既有 dispatcher 測試檔 | 1 | **122 failed, 127 passed, 1 xfailed** | `pytest_existing_suites.out` `7049b7c1…38bd6fc` |

既有套件 122 個失敗**全部**是同一個 code：`grep -oE 'FHS_ENTRY_[A-Z_]+'` 只出現 `FHS_ENTRY_ASSERT_REQUIRED`（311 次），沒有任何其他 `FHS_ENTRY_*`。原因見 `out/L5_RESULT.md` 的 blast radius 段。

## 5. 控制平面與 reader 身分

| 物件 | sha256 | 備註 |
|---|---|---|
| `hgk-bridge/config/lane-routing-registry.yaml` | `5c7ce9de2c7602258bca7f0ce8b2dc1e295eca547b39ac75d10a21f2cf31c4b6` | epoch 41、`status: IN_FORCE`（L4 的 content port，內容與真 clone 不同 bytes） |
| `hgk-bridge/config/lane-route-slots.candidate.json` | `544564a9a0a19fa0ba2519a85ada7c122b1c6bd899d8a17ede9e0166cbb80fb5` | epoch 41、`retired_arms` 有 `opencode-go/mimo-v2.6-pro` |
| `FHS/HG-KSEOS/config/lane-routing-registry.yaml` | `811bf1a5eea4304c057dfc95974e31b4b7655a588091f674db2cf57dbb3055c3` | 真 clone，第二個控制平面 |
| SBL reader `sbl-3lm/.../tools/fhs_3lm.py` | `49a1eea688a40649767ee08a11e8d87f83cc6efe38245f61abb91e36400f4afb` | L2 的修復版（commit `5402fe3`），schema `FHS.3LM.Binding/2` |

## 6. 副作用與清理（誠實記錄）

* reader 的 `--bind` 只能寫在它自己的 round 樹下（`sbl-3lm/evidence/…/lanes/bindings/<run_id>/`）。本 lane 在測試期間建立了 44 個 `l5-*` 目錄，**執行完已全部刪除**，位元組保留在 `bindings/`，刪除前的 sha 清單是 `bindings_sha256_before_cleanup.txt`；`sbl-3lm` worktree 的 `git status` 已回到 L2 自己的狀態（乾淨）。
* `hgk-hook` worktree 內 `var/fhs-entry/` 是本 lane 執行期產物，未進 commit。
* 全程無網路、無 model call。POS 用 `tests/fixtures/stub_lane_child_echo_prompt.py`；wrapper 控制在 pin gate 就被拒（在任何 spawn 之前）。

## 7. 重跑方式

```
# 六案（任一不符即非零退出）
python scripts/selftest_fhs_entry_guard.py --hgk-root <epoch-41 root> --workdir <dir>

# pytest
python -m pytest tests/test_fhs_entry_guard.py -q

# 重新生成 out/L5_RESULT.json（只讀捕獲檔）
python evidence/L5/make_result.py
```
