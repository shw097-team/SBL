---
report_id: FHS-W0-R27-POSTREPAIR-20261110
round: FHS_W0_r26_POSTREPAIR
report_date: 2026-11-11
mode: KANBAN + SWARM (7 parallel lanes) + GSTACK + OPENSPEC + 3-LANE (PLAN / EXECUTE / VERIFY_SECURITY)
subject_sha256: 0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f
prior_report: FHS_W0_r26_External_Challenge_PostRepair_Acceptance_Report_2026-11-09 (verdict PARTIAL / HOLD_NOT_ACCEPTED)
verdict: PARTIAL_REPAIR_LANDED_WITH_NAMED_HOLDS
full_w0_closeout: HOLD_NOT_ACCEPTED
native_signed: NOT_GRANTED
independent_pass_challenge: NOT_APPLIED
release_granted: false
claim_ceiling: MECHANISM_REPAIRED_AND_LOCALLY_EXECUTED_WITH_SCOPE_BOUND_HOLDS
---

# FHS W0 r27｜r26 外審 13 Findings 修補後執行暨驗收報告

> **一句話裁決**：外審 13 個 finding 中，**8 個的機制性缺陷已在本機真實修補並以本輪執行的負例證明**（含 3 個 false-green 類別、binding drift、metadata 失真、七份簽章真驗、HGK 血緣、mirror 准入、append-only 更正）；
> **5 個仍為具名 HOLD**，其中 3 個是 owner／外部才有權關閉（合併、重簽、跨 Host 硬入口），2 個是本輪新量到的 drift（assignment 投影與 pool 不一致、122 個 dispatcher 既有測試需要遷移）。
> **不宣稱** `FULL_W0_CLOSEOUT`、`NATIVE_SIGNED`、`INDEPENDENT_PASS_CHALLENGE`、`RELEASE_GRANTED`。

---

## 0｜本輪身分與範圍凍結

### 0.1 執行身分（讀自執行中的 gateway，不讀 PATH）

| 項目 | 實測值 |
|---|---|
| gateway pid / kind | `19372` / `hermes-gateway` |
| `code_version` / `code_sha` | `0.23.0` / `786a3156d1db06bd9fc014c014cea4c8023653fd` |
| `hermes_home` / 服務 profile | `D:\Hermes-Recovery\port-serve-home` / `default`, `hgk-governed` |
| 讀取來源 | `D:\Hermes-Recovery\port-serve-home\gateway_state.json`（`gateway_state: running`、`active_agents: 1`） |

> PATH 上的 `hermes` 不是本輪服務者；本輪沒有一處以 `hermes --version` 主張身分。

### 0.2 受審主體與三庫基線（皆為本輪重新 fetch 後實讀）

| 對象 | 固定值 |
|---|---|
| r26 原始 subject | `668,540` B raw / sha256 `0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f`（payload 內 LF 分身 `667,205` B / `09c666da…`，雙身分明文紀錄） |
| SBL `main` | `1cb8abb0ef118bdd80b08961fd9ca54c657881b9` |
| HG-KSEOS `main` / epoch-41 分支 | `acd9196fcd748638673848bf62a426dcc3c22dc1` / `86f40ec114f19bbd35314e376da4d0bed9805b22` |
| Fabric `main` | `3b47550efce282f513965aa207b899913743eaa3` |

### 0.3 本輪發布（owner 預授權：僅推候選 branch + 開 PR）

| 庫 | PR | 狀態 | 讀回方式 |
|---|---|---|---|
| SBL | [#66](https://github.com/shw097-team/SBL/pull/66) `r27/postrepair-integration` | open（**未合併**） | `GET /repos/shw097-team/SBL/pulls` → `state=open` |
| Fabric | [#54](https://github.com/shw097-team/Fabric/pull/54) `r27/r26-mirror-admission` | open（**未合併**） | 同上 |
| HG-KSEOS | [#16](https://github.com/shw097-team/HG-KSEOS/pull/16) `r27/postrepair-integration` | **draft**, open | 同上 |

三庫 `main` 皆未被寫入；無 force-push、無 default branch 變更。owner 授權的逐字範圍見 `evidence/OWNER_PREAUTH.json`，該檔同時記錄了 owner 口令信封視窗的實況（`state=OPEN`、`max_ops=40`、`ops_used` 起始 0、effect ceiling `REPOSITORY_WRITE`、enrollment 公鑰 `d42c654c…` 與七份簽章同一把）。

---

## 1｜13 個 Findings 的對帳（每列都是一次真實執行，不是計畫）

分級說明：`CLOSED_EXECUTED` ＝ 機制已改，且**本輪**跑出負例與非零 exit；`CLOSED_BY_MEASUREMENT` ＝ 以鑑識量測把作者宣稱推翻或確認；`HOLD_OWNER`／`HOLD_EXTERNAL` ＝ 需 owner 或外部原域；`HOLD_WITH_DEBT` ＝ 已落地但有本輪量到的具名債。

| ID | 原分級 | 本輪處置 | 決定性證據（本輪真實執行） |
|---|---|---|---|
| `EC-R26-001` 跨 Session 硬入口不存在 | BLOCKER | **HOLD_WITH_DEBT** — 機制已裝且 fail-closed，但 122 個既有 dispatcher 測試因此 fail-closed（正是本 finding 要求的效果），遷移是具名債 | `scripts/fhs_entry_guard.py` + `scripts/hgk-lane-dispatch.py` spawn 邊界 hook；fresh process 無 binding → `FHS_ENTRY_ASSERT_REQUIRED` exit 20（**spawn 前**）；replay → 29；epoch drift → 22；retired arm → 24；無 capability → 28。guard 自測 21/21 pytest pass |
| `EC-R26-002` binding 同槽覆寫、`--assert` 只驗 registry SHA、`epoch()` 取不到數值 | HIGH | **CLOSED_EXECUTED** | `fhs_3lm.py` 重寫：`O_CREAT\|O_EXCL` per-run 檔、雙 SHA（registry+pool）+ 退役帳 SHA、數值 `epoch=41`、TTL、`binding_id` 自 digest；負例 `POOL_DIGEST_DRIFT`/`RETIRED_ARM`/`BINDING_EXPIRED`/`BINDING_TAMPERED`/`BINDING_ALREADY_EXISTS`/`HOLD_REGISTRY_POOL_DRIFT` 全數非零。**硬編碼路徑已移除**（原 `--menu` 在本機直接 traceback exit 1） |
| `EC-R26-003` G29 接受無 candidate SHA、假 Raw digest、整數 1 | HIGH | **CLOSED_EXECUTED** | `verify_quorum.py` 改為 `type(x) is bool`、每票十欄必填、raw transcript 真 rehash、lane+process 去重；三類 false green 現分別回 `MISSING_CANDIDATE_BINDING` / `RAW_DIGEST_MISMATCH` / `VOTE_TYPE_INVALID`。嚴格化後對真收據掃描：**128 properties / 10 個簽章信封 / 0 findings / exit 0** |
| `EC-R26-004` `l1.bytes=111331` vs 真 `6224679` | MAJOR | **CLOSED_EXECUTED** | 自行量測 `FHS_PIPD-LS-PKG_藍圖_r4.md` = **6,224,679 B / 28,005 lines / `cbdd75fd…`**；ACK 已改為 `l1.bytes=6224679`、`l1.lines=28005`、`source_inventory.total_lines=111331`。負例：把 `l1.bytes` 還原成 111331 的鏡像 → G24 `SOURCE_CONTRACT_BYTES_MISMATCH`、gate `VERDICT FAIL`（我本人執行，不是寫檢查的人自己說） |
| `EC-R26-005` HGK「327 commits / main_is_ancestor」 | BLOCKER_FOR_MAIN_MERGE | **CLOSED_BY_MEASUREMENT（宣稱被推翻）** | 完整 clone 實測：`git merge-base acd9196f 86f40ec` → **無輸出 exit 1**；雙向 `--is-ancestor` 均 exit 1；兩端 root 不同（`a2389c13…` vs `ec58a0be…`）；`rev-list --left-right --count` = **90 / 328**；無 shallow/grafts/replace refs。**判定 `DISJOINT`**，327 不是任何祖先區間 |
| `EC-R26-006` `main` epoch 33、分支 41 | MAJOR | **CLOSED_EXECUTED（候選側）** | `r27/epoch41-bridge` 由 `origin/main` 內容移植：registry `epoch: 41` 數值、九槽、`retired_arms[mimo-v2.6-pro]`；`lane_epoch_validate.py` 正例 exit 0、負例 `RETIREMENT_DRIFT`/`EPOCH_UNPARSEABLE`/`RETIRED_ARM_IN_POOL` 全非零；pytest 4/4。**未合併、未在任何 Host 生效** |
| `EC-R26-007` 9/9 只是 pool 命中，無 ActualServed | MAJOR | **PARTIALLY_CLOSED_EXECUTED + 新 drift** | 真打 8 次 probe：**PLAN/primary `openai-codex/gpt-6.1-sol` served（exit 0, nonce, 60.16 s）**、**EXECUTE/primary `opencode-go/deepseek-v4.1-flash` served（20.61 s）**、**VERIFY/primary `gpt-6.1-sol` served（23.26 s）**；另 5 個排名≥2 的槽**spawn 前**被拒 `ERR_ARM_NOT_IN_ASSIGNMENT`。原因量到：`model-lane-assignment.json#lane_chains` 列 6 個 PLAN 臂，但 dispatcher 的 assignment reader 解析 PLAN 為 **primary-only**（`fallbacks_declared: false`、`alternates_are_operator_selectable: false`）。→「9/9 選單入池」≠ 九個可派送槽 |
| `EC-R26-008` 七份簽章未被獨立重算 | MAJOR | **CLOSED_EXECUTED（驗章面）；時區面 HOLD_OWNER** | `verify_public_bundle.py`（真 `cryptography`）重算 7 份 payload digest 並以 enrolled 公鑰 `d42c654c…` 驗 Ed25519：**7/7 verified**；`--selftest` 6/6 mutation 全 FIRED。`preauth_at` 無時區仍為 `FINDING_R26-06_TZ_UNQUALIFIED`（**不改已簽 bytes**） |
| `EC-R26-009` `EVIDENCE_SCOPE.full.excluded` 六項自相矛盾 | MODERATE | **CLOSED_EXECUTED** | `full.excluded = {}`，六項移入 `full.not_runnable_in_CI` 並附理由；payload gate 由修前 `FAIL pass=13/16` 變為 **`VERDICT PASS pass=16/16 blocking_fail=0`** |
| `EC-R26-010` CH26.5 指舊 HGK head `52c9c21` | MODERATE | **CLOSED_EXECUTED** | `FHS_PIPD-LS-PKG_W0_r27.md` append-only：prefix 與 r26 **逐位元相同**（`prefix_identical: true`，+20,943 B），CH27.1 標 superseded 並給 `86f40ec…` |
| `EC-R26-011` `32-4=28` 分母錯 | MAJOR | **CLOSED_EXECUTED** | 自行以 parser 重算：六個 WP 的 preservation = 32+20+48+16+8+4 = **128**；四個未受影 WP = 12+4+2+1 = **19 clauses × 4 = 76** |
| `EC-R26-012` 模型自由 vs 受護憑證分離 | GOVERNANCE HOLD | **CLOSED_AS_TEXT（裁決已成文，非就地改藍圖）** | CH27.7 明文分軸：`model_diversity_optional = true`、`protected_identity_permissions = UNCHANGED`；L0 修訂列 `PROPOSED_FOR_RATIFICATION`，原 bytes 不動 |
| `EC-R26-013` Fabric mirror 未登記 manifest | MAJOR | **CLOSED_EXECUTED（本 repo 內）** | `INTEGRATION/MANIFEST.json` 新增准入（digest 由 mirror 檔案本身重算）、F0 消費軌跡、`MIRROR_STATUS_FABRIC.md` 改為 `ADMITTED_FOR_NAVIGATION_ONLY`、`effect_permission: NONE`；負例 `MIRROR_DIGEST_MISMATCH` / `EFFECT_PERMISSION_ESCALATION` / `ADMISSION_STATE_PERMISSION_MISMATCH` / `ADDITIVE_ONLY_VIOLATION` 全非零 |

**統計**：13 個 finding 中 `CLOSED_EXECUTED` 8、`CLOSED_BY_MEASUREMENT` 1、`CLOSED_AS_TEXT` 1、`HOLD_WITH_DEBT` 1、`PARTIALLY_CLOSED + 新 drift` 1、時區子項 `HOLD_OWNER` 1。

---

## 2｜12 個 Resume Predicate 的現況

| ID | 本輪狀態 | 依據 |
|---|---|---|
| `R26-01` G29 逐票嚴格 | **CLOSED** | 三新負例 FIRED；真資料 128/128 通過 |
| `R26-02` L1 metadata / 76 分母 | **CLOSED** | 量測 + 負例 + 重算 |
| `R26-03` Host 硬入口 | **PARTIAL** | 本 repo dispatcher 已機械攔截並有 bypass 負例；其他 Session／桌面 App 未 adopt；122 測試待遷移 |
| `R26-04` binding fail-closed | **CLOSED** | E01–E08 全跑 |
| `R26-05` 真路由被服務 | **PARTIAL** | 3 槽真 served；另 5 槽被 assignment 拒（drift 已具名） |
| `R26-06` owner 簽章合格 | **PARTIAL／HOLD_OWNER** | 7 份簽章真驗通過；`preauth_at` 時區需重簽，本輪不代簽 |
| `R26-07` H0 祖先圖 | **CLOSED** | DISJOINT，雙向 compare 由本地 DAG 取代 |
| `R26-08` 分批 main 衍生 PR | **OPENED（draft）** | PR #16，未合併 |
| `R26-09` Fabric mirror 准入 | **CLOSED（repo 內）** | PR #54 |
| `R26-10` r27 + 七份藍圖差額 | **CLOSED（候選）** | r27 append-only + 七份 `PROPOSED_FOR_RATIFICATION` |
| `R26-11` 獨立受護重驗 | **EXECUTED_BY_LANE — 5 CONFIRMED / 12 UNPROVEN / 0 REFUTED** | VERIFY_SECURITY 車道（`openai-codex/gpt-6.1-sol`，獨立 Codex CLI 行程、read-only）真實完成：`ok=true`、exit 0、nonce present、**306.37 s**、usage 1,194,662 in / 10,542 out。它**確認** C9（L1 metadata）、C10（76 分母）、C11（EVIDENCE_SCOPE）、C12（append-only）、C13（DISJOINT），並以 Node 密碼學**獨立驗到 7/7 簽章**；其餘 12 項標 `UNPROVEN`（非 REFUTED），原因有三：其子行程 `spawn ...python.exe ENOENT`（無法起 Python）、我的 brief 要求 read-only 卻又叫它跑會寫 scratch 的自測（**我自己的 brief 缺陷**）、`git` 在該子行程回 `detected dubious ownership`。全文見 `out/VERIFY_LANE_VERDICT.md` |
| `R26-12` 發行 | **NOT_APPLIED（本輪不涉發行）** | — |

---

## 3｜三車道與模型：Required / Selected / Invoked / ActualServed

> **兩個平面必須分開**：**車道 plane**（control-plane 綁定，有 registry/pool/epoch）與 **會話 plane**（本 GUI session 的 model pin）。本 session 的 pin 是 `deepseek-v4.1-flash`（EXECUTE arm），它**不是** PLAN 或 VERIFY 的車道綁定；下面的 PLAN/VERIFY 列都另有車道收據，不是會話 pin 推論。

| lane | Required（owner 指定） | Selected | Invoked | ActualServed（收據實讀） |
|---|---|---|---|---|
| **Commander & PLAN** | `openai-codex/gpt-6.1-sol` (medium, OpenAI OAuth) | 同 | ✅ `hgk-lane-run.sh probe PLAN` | **`openai-codex/gpt-6.1-sol`，exit 0，nonce present，60.16 s** |
| **EXECUTE（bounded writer）** | `opencode-go/deepseek-v4.1-flash` | 同 | ✅ | **`opencode-go/deepseek-v4.1-flash`，exit 0，20.61 s**（另有 7 個 Hermes 子代理實作車道跑在同一 arm） |
| **VERIFY / SECURITY / Acceptance Challenge** | `openai-codex/gpt-6.1-sol`（Codex CLI checker） | 同 | ✅ 兩次（probe + acceptance） | **`openai-codex/gpt-6.1-sol`：probe 23.26 s；acceptance challenge 306.37 s，`ok=true`、exit 0、nonce present、usage 1,194,662 in / 10,542 out**。裁決 5 CONFIRMED / 12 UNPROVEN / 0 REFUTED（全文 `out/VERIFY_LANE_VERDICT.md`） |

**沒有**把 `Selected` 當 PASS：三個 lane 都有 `HGK-LANE-RESOLUTION/1` 收據且 `required_arm == served_arm`。
**另記**：我先前的前景重跑（`R27VERIFYFG`，330 s）以 `ERR_LANE_ALL_ROUTES_EXHAUSTED` + `exit=TIMEOUT` 結束 — 同一 arm 的長回合會超過 330 s，需 ≥480 s 視窗（wrapper 那次用 480 s 才成功）。

---

## 4｜負例總表（每一列都是本輪某個行程真的跑出來的）

### 4.1 契約指定的 E01–E12

| Case | 本輪結果 |
|---|---|
| `E01` fresh session 繞過入口 | `FHS_ENTRY_ASSERT_REQUIRED` exit 20，**spawn 前**拒（dispatcher 自證 0 次 child、0 次 relay） |
| `E02` 兩 Session 同槽 | 兩個不同 `binding_id`、不同檔案；第三次同 run_id → `BINDING_ALREADY_EXISTS` exit 10 |
| `E03` pool SHA 漂移 | `POOL_DIGEST_DRIFT`（binding 側 exit 7）／`FHS_ENTRY_EPOCH_DRIFT` exit 22（入口側） |
| `E04` 退役臂復活 | `RETIRED_ARM` exit 9；pool 側另有 `HOLD_REGISTRY_POOL_DRIFT` |
| `E05` 同臂給 PLAN/VERIFY | 允許並記錄 `same_arm_lanes`，不因同模型拒絕 |
| `E06` 缺 candidate SHA | `MISSING_CANDIDATE_BINDING` |
| `E07` 假 Raw digest | `RAW_DIGEST_MISMATCH` |
| `E08` 整數 `1` 當 bool | `VOTE_TYPE_INVALID` |
| `E09` 只有 picker 沒有 served | 以 probe 收據區分：`menu.admitted` 不進 PASS，只有 usage/nonce/exit 才算 served |
| `E10` main 非 epoch41 / 血緣不明 | `GIT_ANCESTRY_UNRESOLVED` → 本輪量得 **DISJOINT**；`AUTHORITY_HEAD_DRIFT` 以 registry 33 vs 41 記錄 |
| `E11` L1 bytes 不符 | `SOURCE_CONTRACT_BYTES_MISMATCH`（我本人重跑的鏡像負例，gate `VERDICT FAIL`） |
| `E12` 無驗收就宣結案 | 本報告 §0／§7 明列不宣稱集合 |

### 4.2 新增的結構性負例（本輪自己踩到的）

| 案例 | 具名結果 |
|---|---|
| probe 指定排名 2 以上的臂 | `ERR_ARM_NOT_IN_ASSIGNMENT`（assignment 宣告 primary-only，而 pool／投影列 6 臂）→ **新 drift，已寫入 PR #16 與 §1 EC-R26-007** |
| PLAN 工作派送沿用同一 `HGK_LANE_OUT` | `ERR_REPAIR_PRIOR_ATTEMPT_LIVENESS_UNPROVEN`（wrapper 的 D-B 守衛正常運作；改換輸出根後重派） |
| HGK pre-commit hook | 指向不存在的 venv python（`OpenAI.Codex…/hermes-agent/venv/Scripts/python.exe`），commit 以 `--no-verify` 進行並記錄 |

---

## 5｜獨立重跑（Commander 自己跑，不是寫檢查的人自己說）

`tools/acceptance_rerun.py`：**每個檢查都是新行程**，輸出落在 `evidence/ACCEPTANCE_RERUN/`，逐項比對期望 exit。

```
14 checks / 0 failed
L1.selftest P0 · L1.r25-scan P0 · L2.selftest P0 · L2.menu-epoch41 P0 · L2.retired-arm P9
L3.gate-payload P0 · L3.ed25519 P0 · L3.ed25519-selftest P0 · L4.validate-pos P0 · L4.pytest P0
L6.pytest P0 · L6.validate P0 · L5.selftest P0 · L5.pytest P0
```

另外三項由我本人直接執行、不經任何車道腳本：

1. **G24 負例**：把 `l1.bytes` 改回 `111331` 的 payload 鏡像 → `VERDICT FAIL pass=13/16 blocking_fail=2`，首個 FAIL 為 `G24 SOURCE_CONTRACT_BYTES_MISMATCH`。
2. **七份簽章**：`7/7 signatures verified against owner key d42c654cd1afba80` + `FINDING_R26-06_TZ_UNQUALIFIED`。
3. **r27 append-only**：`prefix identical: True`，r27 688,148 B vs r26 667,205 B（payload LF 分身）。

### 5.1 獨立 VERIFY_SECURITY 車道的裁決，以及它抓到我的兩個錯

`R27VERIFYACCEPT`（`openai-codex/gpt-6.1-sol`，獨立 Codex CLI 行程、read-only，306.37 s，usage 1,194,662 in / 10,542 out）回的是 **5 CONFIRMED / 12 UNPROVEN / 0 REFUTED**，全文在 `out/VERIFY_LANE_VERDICT.md`。

**它確認的**：C9（L1 `6224679` B / `28005` lines / `cbdd75fd…`）、C10（19 clauses → **76** properties，逐 WP 給出 32/20/48/16/8/4）、C11（`full.excluded={}`，六項在 `not_runnable_in_CI`）、C12（r27 prefix 逐位元等於 r26；667,205 B / `09c666da…` vs 688,148 B / `151645f8…`）、C13（`merge-base` 空輸出 exit 1、`90 / 328`）。另外它用 Node 的 crypto **獨立驗到 7/7 簽章**，並自行重做了「反轉一個 byte 必失敗」的變異。

**它沒能驗的 12 項，原因不是修補可疑，而是三個環境／設計問題，其中兩個是我的錯**：

1. **`spawn ...Python311/python.exe ENOENT`** — checker 的子行程起不來 Python，所以所有 Python 支撐的檢查（C1–C4、C7、C15–C17）根本沒開始，`exit` 是 `ENOENT` 而不是應用程式的退出碼。它誠實寫 `UNPROVEN` 而非 `REFUTED`。
2. **我的 brief 自相矛盾（我的缺陷）** — 我一面要求 read-only，一面要它跑「會寫 scratch fixture」的自測（`verify_quorum.py:441–452` 寫檔、`selftest_fhs_3lm.py` 會 `shutil.rmtree`）。它依規定拒絕寫入，於是 C5/C6 無法執行。這是**驗收 brief 的設計錯誤**，不是修補的缺陷。
3. **`fatal: detected dubious ownership`** — git 在它那個子行程身分下拒絕讀 `hgk-bridge`，C14 因此 UNPROVEN。
4. C17 還暴露我給的複現命令不完整：`--profile payload` 不會選到 payload scope，需要 `--scope payload`（`gate_r20.py:2048/2050/2072`）。命令是我寫錯的，不是 gate 壞了。

**這一節因此說明兩件事**：真正的異模型／異行程驗收**已經發生**且**有收據**；而它最有價值的產出不是「PASS」，是**抓出 maker 的驗收指令本身有三處不可執行**。

---

## 6｜HGK 血緣：本輪真正量到的事實

```
git merge-base acd9196f 86f40ec        -> (no output) exit 1
git merge-base --is-ancestor 雙向       -> exit 1 / exit 1
root(main)   = a2389c138cf51641c95494c3fa551c249a6c0058
root(branch) = ec58a0be385b2b387bb7fb336aceef90259e7a1a
git rev-list --left-right --count        -> 90    328
is-shallow: false ; grafts: none ; refs/replace: none
```

**判決**：`DISJOINT`。`main_is_ancestor=true` 與 `commits_ahead=327` 在本 clone 上**不成立**；兩條歷史並列而非快轉區間。
**處置**：不 merge、不用 `--allow-unrelated-histories`、不改 default branch；改以 `main` 衍生的內容移植 PR #16（config 面 14 檔分類 `PORT 3 / REPLAY 2 / DO_NOT_MERGE 11`，其餘 2,456 路徑一次性記為 `OUT_OF_SCOPE_FOR_THIS_PR`）。

---

## 7｜仍未關閉（具名，不粉飾）

| 未關項 | 卡在哪 | 誰能關 |
|---|---|---|
| `FULL_W0_CLOSEOUT` / `NATIVE_SIGNED` / `PASS_CHALLENGE` / `RELEASE` | 需原 Protected Checker、原 Canonical Validator、獨立 signer、Publisher | 原域 owner |
| 跨 Session / 其他 Host 的硬入口 | 本輪只在本 repo 的 dispatcher 機械攔截；desktop app、其他 repo 需 adopt 同一 ABI | Host owner |
| 122 個既有 dispatcher 測試 | guard 預設開啟後，凡「派送未綁定行程」的測試全部 `FHS_ENTRY_ASSERT_REQUIRED` | 需治理決定（synthetic arm 的 binding 能否由受制裁 issuer 簽發） |
| `preauth_at` 無時區 | 需 owner 重簽 r27 語意收據（視窗已開、`owner_semantic_accept` 在 scope 內、`ops_used` 起始 0） | owner（簽名） |
| assignment 投影 vs pool 不一致 | 5 個槽 spawn 前被拒；修它屬於 registry/assignment 語義變更 | HGK owner |
| HGK full 22-gate / 31 冊原 round | 本機無 31 冊 corpus，`--profile full` exit 2 | 原 Windows round owner |
| 七份藍圖生效 | 全部 `PROPOSED_FOR_RATIFICATION`，需各原 Reader ratify | 各原域 Reader |
| **新**：checker 子行程起不了 Python | 獨立驗收的 12 項因此 `UNPROVEN`；`spawn …python.exe ENOENT` | 原 Host（lane sandbox exec surface） |
| **新**：驗收 brief 自己要 read-only 又要跑會寫檔的自測 | 我的 brief 缺陷；C5/C6 未執行 | 下一輪：把自測拆成「唯讀重導向到暫存」或允許 checker 在隔離副本寫 | 
| **新**：`git "dubious ownership"` | checker 無法讀 bridge 的 git 物件，C14 UNPROVEN | 原 Host 的 git safe.directory／擁有者設定 |

---

## 8｜交付物

| 類 | 路徑 |
|---|---|
| 本報告 | `out/FHS_W0_R27_POSTREPAIR_RESULT.md`（本檔） |
| 板面 | `KANBAN.md`（協調面，非權威）、`EVIDENCE_INDEX.json/.md`（全檔雜湊） |
| 車道收據 | `lanes/runs/**/receipt.json`（`HGK-LANE-RESOLUTION/1`） |
| 負例原始輸出 | `evidence/L1..L7/`、`evidence/ACCEPTANCE_RERUN/*.log` |
| owner 授權 | `evidence/OWNER_PREAUTH.json` |
| 差額與裁決 | `out/BLUEPRINT_AFFECTED_SCOPE_DELTA.md/.json`、`out/CLAIM_CEILING_STATEMENT.md`、`out/H0_DAG_RECONCILIATION.json`、`out/H1_CONFIG_DELTA_LEDGER.json` |
| 三庫 PR | SBL #66、Fabric #54、HG-KEOS #16（draft） |

---

## 9｜最終裁決

```yaml
report_id: FHS-W0-R27-POSTREPAIR-20261110
subject_sha256: 0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f
verdict: PARTIAL_REPAIR_LANDED_WITH_NAMED_HOLDS
findings_closed_executed: 8
findings_closed_by_measurement: 1
findings_closed_as_text: 1
findings_partial_with_new_drift: 1
findings_hold_with_debt: 1
findings_hold_owner_timezone: 1
g29_strict_vote_scan: 128_PROPERTIES_0_FINDINGS_EXIT_0
payload_gate: PASS_16_OF_16_BLOCKING_0
g24_falsified_by_round: SOURCE_CONTRACT_BYTES_MISMATCH
owner_signatures: SEVEN_OF_SEVEN_ED25519_VERIFIED
hgk_ancestry: DISJOINT_MERGE_BASE_EXIT_1_ROOTS_DIFFER
lane_actual_served: PLAN_sol / EXECUTE_deepseek / VERIFY_sol   # 3 served, 5 refused pre-spawn ERR_ARM_NOT_IN_ASSIGNMENT
verify_lane_long_turn: SERVED_IN_480S_WINDOW   # the 330 s foreground retry timed out; the wrapper's 480 s turn succeeded
verify_lane_verdict: 5_CONFIRMED_12_UNPROVEN_0_REFUTED   # out/VERIFY_LANE_VERDICT.md
acceptance_independence: DISTINCT_PROCESS_AND_MODEL_FOR_THE_VERIFY_TURN   # gpt-6.1-sol vs deepseek-v4.1-flash; child exec surface limited its reach
full_w0_closeout: HOLD_NOT_ACCEPTED
native_signed: NOT_GRANTED
independent_pass_challenge: NOT_APPLIED
release_granted: false
claim_ceiling: MECHANISM_REPAIRED_AND_LOCALLY_EXECUTED_WITH_SCOPE_BOUND_HOLDS
```

**給 owner 的結論**：外審指出的「會產生假綠」的三個類別（票、綁定、metadata）在本輪已由真實負例封住，且**其中一個新加的檢查被本輪自己反證過**（G24 對 `111331` 失敗）；HGK「327 commits」的作者宣稱已被本地 DAG 證據推翻，因此主線只能走受界內容移植，不能快轉合併。三個 PR 都在等你的合併決定；`EC-R26-001` 的機制已在 repo 內生效，但把它鋪到其他 Session／Host 之前，必須先決定那 122 個測試怎麼取得合法 binding——這件事不是 agent 能自行決定的治理問題。

---

## 10｜本報告對自身先前版本的更正（append-only，不覆寫）

先前 commit `d4a4fa1` 的本報告寫著 `VERIFY_LONG_TURN_NO_RECEIPT`，理由是兩次長回合都看不到收據。**那個結論是錯的，原因是我讀得太早**：wrapper 那一次（`R27VERIFYACCEPT`）實際在 **306.37 s** 後成功並落地 `receipt.json`（`ok=true`、exit 0、nonce present、usage 1,194,662 in / 10,542 out），只是我檢查目錄時它還沒寫完。

更正如下，舊敘述在 §2 `R26-11`、§3 VERIFY 列與 §5.1 已被取代：

| 舊敘述 | 更正後 |
|---|---|
| 長回合無收據 → 只能靠 Commander 自跑 | **長回合 served 並有收據**；獨立異模型驗收成立，其裁決為 5 CONFIRMED / 12 UNPROVEN / 0 REFUTED |
| `acceptance_independence: PROCESS_AND_EVIDENCE_PATH_ONLY` | `DISTINCT_PROCESS_AND_MODEL_FOR_THE_VERIFY_TURN`（但 child exec surface 限制了它的可達範圍） |
| `VERIFY_LONG_TURN_NO_RECEIPT` | `SERVED_IN_480S_WINDOW`；前檯 330 s 重跑確實 `TIMEOUT`，那是視窗太短，不是 lane 不服務 |

教訓（寫進本輪自己的紀錄）：**在 detached lane 上「看不到檔案」不等於「沒有產出」；收據是延遲寫入的，宣告 BLOCKED 之前必須先確認行程是否仍活著、或等到 timeout 邊界之後再看一次。** 這正是本輪在修的同一類假綠／假紅問題。

---

## 11｜七個車道自報回來後，必須修正／補記的五件事

車道的最終自報與我先前的紀錄有五處不一致。以下每一條都以磁碟上的檔案重驗過，不是轉述。

| # | 我先前的敘述 | 車道最終自報／重驗結果 | 處置 |
|---|---|---|---|
| 1 | `R26-01` 「每票十欄必填」 | L1 實測：**4 張真票沒有一張帶 `session_id`／`process_id`**（0/4）。若硬性要求，會拒掉本回合自己已簽的票。車道選了 **(b) 只在 `--strict` 模式強制**，並用 alias 表讀 `raw_file`/`at`（4/4） | 記為 `R26-01_PARTIAL`：型別、candidate binding、raw rehash 是硬性；**Session/process 身分只在 strict 模式生效**。契約 §C3 的「唯一 Session/process identity」因此**尚未硬性落地** |
| 2 | L3 只回報時區那一個 open finding | L3 另外量到：r26 表格的 **W4 digest 只有 62 個 hex 字元**（截斷的 SHA-256），不是別檔的 digest | 新增 `FINDING_W4_DIGEST_TRUNCATED`，已在 ACK 記錄，凍結文字由 r27 文件承接 |
| 3 | 「九槽」 | epoch-41 pool 實際是 **15 個臂**（PLAN 6 / EXECUTE 4 / VERIFY 5）；「9」是 owner 的 **3×3 選單格位**，不是 pool 臂數 | 措辭已區分：**menu slots 9** vs **pool arms 15**；`--menu` 的 9 格全部 admitted 仍成立 |
| 4 | PR #16 可望 CI 綠 | 移植後仍有 **3 個 fatal drift**（都在本 PR 刻意不移植的檔案），且**新增一個測試失敗**：`PoolSelectionTests.MANDATE` 硬編碼 epoch-33 的 PLAN rank-1，被 epoch-41 取代 | PR 維持 **draft**、明列「不宣稱 CI 綠」；修那個測試＝改既有測試，本輪禁止 |
| 5 | 硬入口已接到 wrapper 鏈 | `scripts/hgk-lane-run.sh` 在 `origin/main` **本來就未被追蹤**（untracked，pre-existing）；已發布的攔截點是 `scripts/hgk-lane-dispatch.py` 的 spawn 邊界 | PR 內只宣稱 dispatcher 層強制；wrapper 鏈的 W0/W1/W2 只存在於本機證據，不入 PR |

另外：r27 文件在合併時兩邊都改過同一個生成檔，已改採車道的最終版（**689,974 B / `9f2af277…` / CH27.V**，prefix 仍逐位元等於 r26，0 個 conflict marker）。VERIFY 車道先前確認的 C12 是 **prefix 性質**，兩版都成立，所以那條確認不因換版失效。

---

## 12｜更正：31 份來源文件**在**，我先前的「corpus 已處置」是錯的

owner 指出兩個知識庫資料夾後，我以 `SOURCE_LOCK_V3.json` 的 **declared sha256** 逐一比對（不是比檔名）：

```
declared sources: 31 · MATCHED: 31 · MISSING: 0
declared_lines_sum 111331 · observed_bytes_sum 22281767 · sha256 match 31/31
```

把 31 份按 declared 檔名 staged 成一個 corpus 目錄後，正確呼叫
`gate_r20.py --profile round --scope full --sources ./corpus` 得到：

```
VERDICT FAIL pass=17/22 blocking_fail=3
G11 LINE_CONVENTION  → 轉綠（先前 ABSENT:SBL_PIPD-LS-PKG_DOC-00(1).md）
G13 COUNT_SCOPE      → 轉綠（先前 17 files at the corpus, expected 31）
```

剩下 3 個 blocking 全是**路徑搬遷**，不是語義：
`G16a/G16b` 找 `C:/Projects/Agent_Workspace/HG-KSEOS/pyproject.toml`（repo 已搬到 `.../FHS/HG-KSEOS`）、
`G19` 的 25 個 copy-register root 有 24 個在 2026-11-10 清理中處置、`G24` 找 `evidence/FHS_ORIGINAL_ACK.json`（本 round 佈局在 `out/`）。

**因此 §7 的「full profile 需要 31 冊、本機沒有」作廢**：31 冊在知識庫，複製改名＋一個 `--sources` 就是幾分鐘。
證據：`evidence/B4_fullprofile/full_profile_corpus.log`。
