# L2 — FHS-3L&M 綁定硬入口修補（r27）

**判定：PASS**（`selftest_fhs_3lm.py` 25 個案例全部相符，exit 0）

## 修補內容（tools/fhs_3lm.py，原地修補，未新增第二個 router／registry）

- 控制平面不再硬編碼：`--hgk-root` → `HGK_ROOT` → 工具旁 `config/hgk-root.txt` → `ERR_HGK_ROOT_UNRESOLVED`（exit 8）；根目錄缺 `config/lane-routing-registry.yaml` 或 pool → `ERR_HGK_ROOT_INVALID`（exit 8）。每次綁定記下 `hgk_root` 與 `discovery_source`。
- epoch 取 registry 頂層 `epoch:` 並轉為整數（`policy_epoch`，並記 `epoch_status`、`contract_epoch`）；缺失或非數字 → `ERR_EPOCH_UNRESOLVED`（exit 7）。
- 綁定改為 session-unique 且不覆寫：`lanes/bindings/<run_id>/<lane>_<slot>_<nonce>.json`，以 `O_CREAT|O_EXCL` 建立；同一 run+session+lane+slot 重複 → `BINDING_ALREADY_EXISTS`（exit 10）。
- 雙重摘要：`binding_id` = 正規化 body 的 SHA-256（手改可得 `BINDING_TAMPERED`），另記 `registry_sha256` / `pool_sha256` / `retired_ledger_sha256`（平面移動可得 `EPOCH_DRIFT` / `POOL_DIGEST_DRIFT`）。
- 退役帳同時讀 pool 與 registry 的 `retired_arms:`；兩者不一致、或退役臂仍留在任一 lane pool → `HOLD_REGISTRY_POOL_DRIFT`（exit 7，非 pass）。

## 使用的控制平面（本輪固定）

| 項 | 值 |
|---|---|
| root | `C:/Projects/Agent_Workspace/FHS/HG-KSEOS`（branch `config/plan-mimo-flash-20261109` @ `86f40ec`） |
| `lane-routing-registry.yaml` | `811bf1a5eea4304c057dfc95974e31b4b7655a588091f674db2cf57dbb3055c3` |
| `lane-route-slots.candidate.json` | `628e7db6c0062fa64da07e7356d8f943f7a9ce0e9e4800f06095c19fa142c577` |
| epoch | `41`（int）、`status: IN_FORCE`、`contract_epoch: 34` |
| epoch-33 對照 bytes | `git show origin/main:` @ `acd9196f`：registry `970b925b8a5f5d18b4c47df94d24be1210b4af9f2815d401daf098feb5160b27`、pool `3e632ca41b66250b44bbfef913762fe2bb397e1c21b150c50ecbe036d689ac78` |

`hgk-bridge` 工作樹在本 lane 進行期間由 epoch 33 被 L4 換成 epoch 41（尚未 commit），因此 epoch-33 一律取
`origin/main` 的 bytes，不取該工作樹。

## 修補前缺陷重現

`python <rollback>/fhs_3lm.py.pre-repair --menu` → **exit 1**，`FileNotFoundError: ...HG-KSEOS\config\lane-route-slots.candidate.json`
（`logs/PRE_repair_menu.log`，sha256 `dd3025c1ccaf0b7960f9745ab8f3195cd5e1ceb4e269b3ad627cb6445bd5c23d`）。

## 案例（全部由 `selftest_run.log` 產生，未手寫結果）

| case | 期望 exit | 實測 exit | code | 結果 | log |
|---|---|---|---|---|---|
| `E00a` | 8 | 8 | `ERR_HGK_ROOT_UNRESOLVED` | PASS | `E00a_root_unresolved.log` |
| `E00b` | 8 | 8 | `ERR_HGK_ROOT_INVALID` | PASS | `E00b_root_invalid.log` |
| `E01` | 0 | 0 | `—` | PASS | `E01_menu_epoch41.log` |
| `E01b` | 0 | 0 | `—` | PASS | `E01b_plane.log` |
| `E02a` | 0 | 0 | `—` | PASS | `E02a_bind_run_a.log` |
| `E02b` | 0 | 0 | `—` | PASS | `E02b_bind_run_b.log` |
| `E02c` | 0 | 0 | `—` | PASS | `E02c_bind_run_a_other_session.log` |
| `E02d` | 10 | 10 | `BINDING_ALREADY_EXISTS` | PASS | `E02d_bind_collision.log` |
| `E03a` | 0 | 0 | `—` | PASS | `E03a_bind_for_pool_drift.log` |
| `E03b` | 0 | 0 | `—` | PASS | `E03b_assert_control_same_binding.log` |
| `E03c` | 7 | 7 | `POOL_DIGEST_DRIFT` | PASS | `E03c_assert_pool_drift.log` |
| `E04a` | 9 | 9 | `RETIRED_ARM` | PASS | `E04a_assert_arm_retired_epoch41.log` |
| `E04b` | 0 | 0 | `—` | PASS | `E04b_assert_arm_epoch33.log` |
| `E04c` | 9 | 9 | `RETIRED_ARM` | PASS | `E04c_assert_arm_registry_only_ledger.log` |
| `E05a` | 0 | 0 | `—` | PASS | `E05a_bind_plan_primary.log` |
| `E05b` | 0 | 0 | `—` | PASS | `E05b_bind_verify_primary_same_arm.log` |
| `E05c` | 0 | 0 | `—` | PASS | `E05c_assert_same_arm_binding.log` |
| `E06a` | 0 | 0 | `—` | PASS | `E06a_bind_ttl0.log` |
| `E06b` | 7 | 7 | `BINDING_EXPIRED` | PASS | `E06b_assert_expired.log` |
| `E07` | 8 | 8 | `BINDING_TAMPERED` | PASS | `E07_assert_tampered_model.log` |
| `E08a` | 7 | 7 | `HOLD_REGISTRY_POOL_DRIFT` | PASS | `E08a_menu_registry_pool_drift.log` |
| `E08b` | 7 | 7 | `HOLD_REGISTRY_POOL_DRIFT` | PASS | `E08b_assert_arm_drift.log` |
| `E09` | 7 | 7 | `EPOCH_DRIFT` | PASS | `E09_assert_epoch_drift.log` |
| `E10` | 7 | 7 | `POOL_DIGEST_DRIFT` | PASS | `E10_assert_arm_removed_from_pool.log` |
| `E11` | 1 | 1 | `BINDING_ALREADY_EXISTS` | PASS | `E11_concurrent_binds.log` |

`selftest_run.log` sha256 `930a114cc9f88e6ef84310f55da99909a80e63dcb6410e05bb3b85239182f353`；工具 sha256 `49a1eea688a40649767ee08a11e8d87f83cc6efe38245f61abb91e36400f4afb`；selftest sha256 `4a5944611d0470a9b8f7ffb3fb8f63980bc3a61578996d60b42e6bf12e4343ea`。

## 未主張

- 沒有呼叫任何模型、也沒有實際服務任何 lane 回合：本輪證明的是路由與拒絕，不是推論能力
- `ARM_LEFT_POOL` 是第二道防線而非第一拒絕：任何把臂移出 pool 的編輯都會同時改變 pool 摘要，因此先以 `POOL_DIGEST_DRIFT` 拒絕（實測 E10）
- epoch-33 平面根本未退役 `opencode-go/mimo-v2.6-pro`（實測 E04b）：退役是 epoch-41 的事實；「只有 registry 退役段也能決定」是以把 pool 退役帳設為 null 的 probe 證明（E04c）
- 不主張 `NATIVE_SIGNED`、`RELEASE_GRANTED`；HGK `main` 仍停在 epoch 33（`acd9196f`）
- 不消費、也不驗證 L4 lane 在 `hgk-bridge` 工作樹裡那份尚未 commit 的 epoch-41 port
- 修補前的覆寫缺陷（E02）是依其程式碼路徑 `BINDING_DIR/{lane}_{slot}.json` 判讀；在本機無法實際執行，因為缺陷 1 會先讓它崩潰

> E11 的兩個數字不是 exit code：`期望 1` = 只允許一個寫入者成功，`實測 1` = 成功的寫入者數；其餘 5 個都是 exit 10
> `BINDING_ALREADY_EXISTS`，且落地的檔案只有一個、其 `binding_id` 可用正規化 body 重算。
