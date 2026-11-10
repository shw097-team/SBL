## CH27 — r27 append-only correction (2026-11-10)

> **性質**：append-only 追加章，不是改版重寫。r26 全文（raw 668,540 bytes，sha256
> `0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f`；LF 運送形 667,205 bytes，
> sha256 `09c666dad4f31099f862c12cc5d3758620c46c70bc5f410af727c465bbb6f0f7`）**逐位元保留為本章前綴**。
> 本章不改寫任何一個 r26 位元；凡被本章推翻的舊敘述，一律以「在本章宣告 `superseded`」的方式退役，
> 舊行原地保留、可稽、可反查。這是本輪唯一的退役機制（見 `../../out/BLUEPRINT_AFFECTED_SCOPE_DELTA.json`
> 的 `append_only_rule`）。
>
> **本輪可主張**：`R27_APPEND_ONLY_CORRECTION_RECORDED`。邊界見 CH27.8。

### 表 27-A｜本章取代哪些行（機械索引）

| finding | 舊位置（r26） | 舊文（節錄） | 處置 | 新值／新位置 |
|---|---|---|---|---|
| `EC-R26-010` | L4548 | `config/plan-mimo-flash-20261109` @ `52c9c21c9f83` | `superseded` | `86f40ec114f19bbd35314e376da4d0bed9805b22`（CH27.1） |
| `EC-R26-004` | L4549／L4553 | 「領先 **327** 個 commit」、「把 327 個 commit 併進 `main`」 | `superseded` | 兩血緣 DISJOINT，`90 / 328`（CH27.6） |
| `EC-R26-004` | `evidence/FHS_ORIGINAL_ACK.json` → `subject_scope.source_contract.l1.bytes` | `"bytes": 111331` | `superseded` | `6224679`；`lines = 28005`（CH27.2） |
| `EC-R26-011` | `…→ subject_scope.unaffected_proof.measured` | 「the four receipts' 32-4=28 properties…」 | `superseded` | `76`（19 clauses × 4）（CH27.3） |
| `EC-R26-009` | `evidence/EVIDENCE_SCOPE.json` → `profiles.full.excluded` | `{"G11,G13,G16a,G16b,G19,G26": …}` | `superseded` | `excluded = {}` ＋ `not_runnable_in_CI`（CH27.4） |
| `EC-R26-002`／`EC-R26-003` | `…/tools/fhs_3lm.py`、`…/tools/verify_quorum.py` | 拒絕碼集合不完整（見 CH27.5 表） | `superseded` | 十個具名拒絕碼（CH27.5） |
| `EC-R26-005`／`EC-R26-006` | L4549 | `main_is_ancestor=true` 的隱含前提 | `retracted` | DISJOINT；改用 main 衍生橋接（CH27.6） |
| `EC-R26-012` | `…→ model_sharing_exception.statement` | 「the owner forbade mandating SoD or model type」 | `clarified`（不撤回） | 兩軸分離（CH27.7） |

**讀法**：表 27-A 是索引，效力在 CH27.1–27.8 各節。任何引用 r26 舊行的下游，必須同時引用本章對應小節；
只引用舊行而沒有引用本章者，其結論在本章之後不成立。

---

### CH27.1 (EC-R26-010) — HGK 分支 head：`52c9c21` 是前任，不是 head

**舊文（r26 L4548，逐字）**

```
| HG-KSEOS 分支 | **已推送** | `config/plan-mimo-flash-20261109` @ `52c9c21c9f83` |
```

**為什麼錯**：這一行是在 `52c9c21` 上寫的，寫完之後**同一條分支又前進了一個 commit**。r26 因此把一個
中間 commit 記成「分支 head」。錯的不是推送這件事（推送為真），而是把「我推送時的那個 commit」
升格成「分支現在的 head」——這是兩種不同的主張，前者是歷史事實，後者會隨下一次推送改變。

**新值（本輪實測）**

| 項 | 值 |
|---|---|
| 分支 head | `86f40ec114f19bbd35314e376da4d0bed9805b22` |
| head commit 時間／訊息 | `2026-11-09 20:07:26 +0800`／`the retirement moved the arm but left two pinned projections pointing at the old one` |
| 前任（保留為歷史，不是 head） | `52c9c21c9f8330132183c553571446fb1792948b`（`2026-11-09 20:00:17 +0800`，`OWNER ORDER 2026-11-09: admit opencode-go/mimo-v2.6-flash to the PLAN pool, retire opencode-go/mimo-v2.6-pro everywhere`） |
| 兩者關係 | `merge-base --is-ancestor 52c9c21 86f40ec` → exit 0（前任是 head 的祖先）；`rev-list --count 52c9c21..86f40ec` → `1` |
| 遠端包含 | `git branch -r --contains 86f40ec` → `origin/config/plan-mimo-flash-20261109` |

**處置**：L4548 標 `superseded`（本節為其替代）。`52c9c21` **不刪**，它是「推送當時的 head」的證據，
也是 CH26.2–26.4 那批量測實際跑在哪個 commit 上的定位點。

**可重現指令（本輪執行，見 `evidence/L7/m02_hgk_head_chain.log`）**

```
$ git -C C:/Projects/Agent_Workspace/FHS/HG-KSEOS rev-parse 86f40ec
86f40ec114f19bbd35314e376da4d0bed9805b22                                   # exit 0
$ git -C C:/Projects/Agent_Workspace/FHS/HG-KSEOS merge-base --is-ancestor 52c9c21 86f40ec
                                                                            # exit 0
$ git -C C:/Projects/Agent_Workspace/FHS/HG-KSEOS rev-list --count 52c9c21..86f40ec
1                                                                           # exit 0
```

---

### CH27.2 (EC-R26-004) — L1 的 `bytes` 是 6,224,679，不是 111,331；111,331 是 31 冊的「行數」

**舊文（r26 近似，逐字）**

```
"l1": {"sha256": "cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b", "bytes": 111331}
```

同一份 ACK 的 `what_it_does_not_cover` 欄還寫著：「the gate's 111,331 is the total line count across the
31 source volumes; L1 alone is counted in `l1.lines` and its size in `l1.bytes`」。也就是說，**檔案自己
已經知道 111,331 是行數**，卻把它放進 `bytes` 欄，而且 `l1.lines` 根本不存在。

**新值（本輪實測，L1 藍圖實檔）**

| 欄 | 舊值 | 實測值 |
|---|---|---|
| `l1.bytes` | `111331` | **`6224679`** |
| `l1.lines` | （缺欄） | **`28005`**（LF split；newline 數 28,004，檔尾有換行） |
| `l1.sha256` | `cbdd75fd…` | `cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b`（**原值正確，不動**） |
| `source_inventory.total_lines` | （缺欄） | **`111331`**（31 冊來源清冊的總行數，唯一該放這個數字的地方） |

**為什麼重要**：`bytes = 111331` 讓一個 XML/JSON 級別的數字檢查永遠不可能通過，也讓「L1 有 6.2 MB」
這個事實從此消失在機器可讀層。下游任何用 `l1.bytes` 驗大小的 gate 都會拿一個小 56 倍的數字去比對。
**這不是筆誤，是欄位語義被壓平**——正是 L0 §00.1 禁止的那種偷換：把「31 冊的行數」穿成「L1 的大小」。

**量測指令（本輪執行，`evidence/L7/measure_l7.py` → `evidence/L7/measure_l7.log`）**

```
$ python evidence/L7/measure_l7.py blueprint_measure.json
L1_PIPD-LS-PKG_藍圖_r4  bytes=6224679 lines_lf_split=28005 sha256=cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b
```

來源檔 sha256：`cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b`
（`…/藍圖/FHS_PIPD-LS-PKG_藍圖_r4.md`）。這個值與 r26 ACK 自己宣告的 `l1.sha256` **一字不差**——錯的
從來不是 digest，是它旁邊那個 `bytes`。

**落地狀態（本輪實測，`evidence/L7/logs/14_landing_status.log`）**：`sbl-meta` 車道 branch
`r27/metadata-hygiene` @ `8353ae6` 的 `FHS_ORIGINAL_ACK.json` 已改為
`"l1": {path, sha256, bytes: 6224679, lines: 28005, declared_sha256_in_r26_doc, sha_agrees_with_r26_doc: true}`
——與本章的數值一致。本章因此**不再只是契約**：這個修法已有一個可 `git grep` 的落地點。

---

### CH27.3 (EC-R26-011) — `unaffected_proof` 的分母：19 clauses → 76 properties，不是 `32-4=28`

**舊文（逐字）**

```
"measured": "the four receipts' 32-4=28 properties still pass tools/verify_quorum.py unchanged; their envelope bytes are identical to r24"
```

**為什麼錯**：`32-4=28` 算的是**條款**（clauses），卻被寫成 **properties**。receipts 的結構是每條 clause
帶 4 個 preservation 欄位（key set 完全一致），所以 4 個不受影響的 WP 是 19 條 clause、76 個 property。
`28` 這個數字在 receipts 裡沒有任何對應的量。

**逐 WP 算術（可自行重算）**

| WP | clauses | properties（×4） |
|---|---|---|
| `WP-FHS-15` | 12 | 48 |
| `WP-FHS-16` | 4 | 16 |
| `WP-FHS-19` | 2 | 8 |
| `WP-FHS-21` | 1 | 4 |
| **合計** | **19** | **76** |

全輪分母是 32 clauses／128 properties（`WP-FHS-00` 8/32、`WP-FHS-01` 5/20 亦各 ×4），因此「不受影響」
的正確說法是 **76 / 128 properties**，而不是「28 個 properties」。r26 的 G29 gate 自報
`128 preservation properties across 10 signed envelope(s)`，與此一致：128 存在，28 不存在。

**量測**：`evidence/L7/measure_l7.py`（`## C. preservation denominators`）與 sbl-meta 車道的獨立重算
（`evidence/L3/count_preservation_properties.log`）得到同一個 12/4/2/1 → 19 → 76。

**處置**：`unaffected_proof.measured` 該行標 `superseded`；修好的文字必須同時保留 ACK 自己那條正確的
警語 `not_a_prefix_argument`（「byte-exact prefix 不是語義未變的證據」），本節不推翻它。

---

### CH27.4 (EC-R26-009) — 「不在 full profile」與「CI 跑不了」是兩件事

**舊文（逐字，`evidence/EVIDENCE_SCOPE.json`）**

```
"full": {"checks": 22, "where": "this host, author run", "command": "python tools/gate_r20.py --round .",
         "excluded": {"G11,G13,G16a,G16b,G19,G26": "need the 31 local source volumes; not runnable in CI"}}
```

**為什麼這是自我矛盾**：`checks: 22` 說 full profile 有 22 個 gate；`excluded` 又說其中 6 個不在
full profile 裡。同一個物件同時主張「22 個都跑」與「6 個不跑」。而 payload profile 是 `checks: 16`，
16 = 22 − 6：**被排除的 6 個屬於 payload（CI），不屬於 full**。實測的 payload 16/16 清單正好是
`G10,G12,G14,G15,G16c,G17,G18,G20,G21,G22,G23,G24,G25,G27,G28,G29`——也就是那 22 減 6。原因欄寫的
「not runnable in CI」本身是對的，錯的是把它放進 `profiles.full.excluded`。

**兩個不同的事實**

| 說法 | 意思 | 對這 6 個 gate 是否成立 |
|---|---|---|
| 「excluded from the full profile」 | full profile 根本不執行它 | **不成立**（full 的 22 個含它們） |
| 「not runnable in CI」 | full profile 執行它，但 CI job 的環境跑不動（需 31 冊本地來源） | **成立** |

**修法（本節即規範）**

```
profiles.full.excluded = {}                       # 空物件，不是 null
profiles.full.not_runnable_in_CI = [
  {"gate": "G11",  "reason": "needs the 31 local source volumes"},
  {"gate": "G13",  "reason": "needs the 31 local source volumes"},
  {"gate": "G16a", "reason": "needs the 31 local source volumes"},
  {"gate": "G16b", "reason": "needs the 31 local source volumes"},
  {"gate": "G19",  "reason": "needs the 31 local source volumes"},
  {"gate": "G26",  "reason": "needs the 31 local source volumes"}
]
```

`profiles.payload.excluded` 保留那 6 個（payload 的 16 個 gate 本來就不含它們），語義上不變。
任何綁定 `EVIDENCE_SCOPE` 的 digest／manifest 必須重算，並把新舊 sha 一起記錄（舊：
`dad2d715d40e35814c38ed801d59ea4e575b9a28937032fb03a5808d1e99120c`，711 bytes）。

**落地狀態（本輪實測，`evidence/L7/logs/14_landing_status.log`）**：`sbl-meta` 車道 branch
`r27/metadata-hygiene` @ `8353ae6` 的 `EVIDENCE_SCOPE.json` 已是 schema **`FHS.W0.EvidenceScope/2`**，
`profiles.full.excluded = {}`，並有六項 `not_runnable_in_CI`（`G11,G13,G16a,G16b,G19,G26`，各附一句
理由）；typed check `SOURCE_CONTRACT_BYTES_MISMATCH` 已出現在 `tools/gate_r20.py` 與 ACK。也就是說，
本章描述的修法不是提案，而是一個已落地、可反查的狀態。

---

### CH27.5 (EC-R26-002 / EC-R26-003) — 修好的 verifier 與 binding 契約（按名引用）

本節**不重述程式碼**，只把契約名與所在位置寫死，讓下游可以按名對帳。代碼名逐字如下。

| 代碼（逐字） | 觸發條件 | 擁有者檔案 | 本輪落點 |
|---|---|---|---|
| `VOTE_TYPE_INVALID` | 票值不是 `bool`（JSON 整數 `1`、字串 `"true"` 皆拒） | `evidence/fhs-w0-r26-repair-20261109/tools/verify_quorum.py` | L1 `r27/quorum-g29` |
| `MISSING_CANDIDATE_BINDING` | 修復票缺 `candidate_sha256` 等十個必要綁定欄之一 | 同上 | L1 |
| `RAW_DIGEST_MISMATCH` | `raw_path` 可解析但 `sha256(bytes) != raw_sha256` | 同上 | L1 |
| `PROCESS_ID_DUPLICATE` | 兩票同 `(session_id, process_id)` | 同上 | L1 |
| `POOL_DIGEST_DRIFT` | `--assert` 時 pool sha256 與 binding 不符 | `…/tools/fhs_3lm.py` | L2 `r27/fhs3lm-binding` |
| `RETIRED_ARM` | 選到退役帳中的臂（exit 9） | 同上 | L2 |
| `BINDING_EXPIRED` | `expires_at` 已過 | 同上 | L2 |
| `BINDING_TAMPERED` | binding body 的 digest 不等於 `binding_id` | 同上 | L2 |
| `HOLD_REGISTRY_POOL_DRIFT` | registry 退役段與 pool `retired_arms` 不一致 | 同上 | L2 |
| `FHS_ENTRY_*` | 原生 pre-dispatch 硬入口的一族（以下七個＋token 兩個） | `scripts/fhs_entry_guard.py`（新）＋ `scripts/hgk-lane-dispatch.py`（單一鉤點） | L5 `r27/fhs-entry-hook` |

`FHS_ENTRY_*` 逐字展開：`FHS_ENTRY_ASSERT_REQUIRED`(exit 20)、`FHS_ENTRY_BINDING_INVALID`(21)、
`FHS_ENTRY_EPOCH_DRIFT`(22)、`FHS_ENTRY_POOL_DRIFT`(23)、`FHS_ENTRY_RETIRED_ARM`(24)、
`FHS_ENTRY_ARM_MISMATCH`(25)、`FHS_ENTRY_BINDING_EXPIRED`(26)、`FHS_ENTRY_GUARD_UNRESOLVED`(27)、
`FHS_ENTRY_TOKEN_REQUIRED`(28)、`FHS_ENTRY_TOKEN_CONSUMED`(29)。

**落地狀態必須與契約分開陳述**，因此分兩次量測：

| 時點 | 量測 | 結果 |
|---|---|---|
| 寫本章第 1 版時（sibling 車道尚未 commit） | `evidence/L7/m06_contract_codes.log` | 於 HEAD `1cb8abb` 只有 `RETIRED_ARM` 存在；其餘皆 `ABSENT_AT_HEAD` |
| 本章定稿前（sibling 車道已 commit） | `evidence/L7/logs/14_landing_status.log` | 見下表 |

| 代碼 | 落地的 branch @ HEAD | 檔案 |
|---|---|---|
| `VOTE_TYPE_INVALID`／`MISSING_CANDIDATE_BINDING`／`RAW_DIGEST_MISMATCH`／`PROCESS_ID_DUPLICATE` | `r27/quorum-g29` @ `3099dec` | `…/tools/verify_quorum.py` |
| `POOL_DIGEST_DRIFT`／`RETIRED_ARM`／`BINDING_EXPIRED`／`BINDING_TAMPERED`／`HOLD_REGISTRY_POOL_DRIFT`／`BINDING_ALREADY_EXISTS`／`ERR_HGK_ROOT_UNRESOLVED`／`ERR_EPOCH_UNRESOLVED` | `r27/fhs3lm-binding` @ `5402fe3` | `…/tools/fhs_3lm.py`（＋`selftest_fhs_3lm.py`） |
| `FHS_ENTRY_*`（十個） | **尚未落地**（`r27/fhs-entry-hook` 仍停在 `acd9196`） | — |

注意兩件事。其一，上表是**字串存在性**（`git grep` 可證），**不是**「會拒絕」的證明；可執行性由各車道
自己的 selftest log 主張，本章不代為主張。其二，`hgk-hook` 的 `BINDING_EXPIRED` 命中屬於 HG-KSEOS
既有的 `src/hg_kseos/role_binding.py`，那是另一個模組的同名概念，**不是**本契約的實作，不能拿來充數。

因此本章主張的是「契約已命名、位置已指定、多數已有落地點、`FHS_ENTRY_*` 仍欠」；
**不主張**「二十個拒絕碼都已可執行」。

**為什麼要按名寫死**：EC-R26-002／003 的原始形狀不是「驗證器壞了」，而是「驗證器會對不該接受的東西
回 `ACCEPTABLE_FOR_FHS_READER_SCOPE`」。修這種缺陷，唯一可稽核的成果形式是**具名拒絕碼 + 非零 exit**
——不是「已修好」這句話。

---

### CH27.6 (EC-R26-005 / EC-R26-006) — HGK 兩血緣 DISJOINT；`327` 撤回；改走 main 衍生橋接

**舊文（r26 L4549、L4553，逐字節錄）**

```
… `main` = `acd9196fcd74`，其 registry 仍是 **epoch 33**；本地 in-force 血緣是 epoch 40 → 41，領先 **327** 個 commit
本輪不把 327 個 commit 併進 `main`
```

**實測（`evidence/L4/h0_*.log`，本輪重跑）**

| 量測 | 輸出 | exit |
|---|---|---|
| `git merge-base acd9196f 86f40ec` | （無輸出） | **1** |
| `git rev-list --max-parents=0 acd9196f` | `a2389c138cf51641c95494c3fa551c249a6c0058` | 0 |
| `git rev-list --max-parents=0 86f40ec` | `ec58a0be385b2b387bb7fb336aceef90259e7a1a` | 0 |
| `git rev-list --left-right --count acd9196f...86f40ec` | `90	328` | 0 |
| `git merge-base --is-ancestor acd9196f 86f40ec` | （無輸出） | **1** |
| `git rev-parse --is-shallow-repository` | `false` | 0 |

**結論**：兩個 commit 沒有共同祖先（root 不同、`merge-base` exit 1、`is-ancestor` exit 1、repo 不是
shallow）。因此：

1. `main_is_ancestor=true` 是**錯的**，撤回；
2. `327` 這個數字**沒有指涉物**——兩條血緣既然 disjoint，「領先幾個 commit」不是一個可定義的量。
   可定義的是 `90 / 328`（各自獨有的 commit 數），而 `90 + 328 = 418` 也不是「合併後新增的 commit 數」；
3. 「把 327 個 commit 併進 main」這個選項不存在，因此「本輪不做」這個陳述本身也要換成「本輪改用
   **main 衍生的橋接 PR**」：從 `origin/main`（`acd9196f`，epoch 33）切出 `r27/epoch41-bridge`，
   只做 `config/` 的**內容移植**（content port），不 cherry-pick 歷史、不 merge、不用
   `--allow-unrelated-histories`。移植後仍須過該庫自己的 CI 與 OWNER 的合併決定，**不是**自動生效。

**處置**：L4549、L4553 就 `327` 與 `main_is_ancestor` 兩點標 `superseded`；`acd9196f`／epoch 33 這兩
個事實不變（仍為真），不撤回。

---

### CH27.7 (EC-R26-012) — 治理分裂：模型多樣性可選，受保護身份不變

這一節是本文件最容易被讀錯的一段，因此分成兩個獨立軸陳述，任何把兩軸合併的讀法都錯。

**軸一：`model_diversity_optional = true`**

- 任何車道**不得**因為「與另一車道共用同一個模型或同一個 provider」而被拒絕。
- `same_arm_lanes`（同一臂同時服務多個車道）**要被記錄**，永遠不是失敗條件；它是一條事實欄位，不是
  一個 verdict。
- 這一軸改變的是「要求三個不同模型」這類強制條件：它被明示為**非必要**。OWNER 2026-11-09 的裁決
  （r26 `model_sharing_exception`）已表達同一意思，本節把它升為規範語句，而不是例外註記。

**軸二：`protected_identity_permissions = UNCHANGED`**

- **Maker ≠ Issuer／Checker／Publisher，在 credential 軸上。** 這一條**沒有**被軸一放寬，也沒有被
  「車道之間可以共用模型」觸及。
- Writer **不得**自簽一個 protected pass；一件受保護的通過，其簽章必須來自與產出者不同的 credential。
- 一個通用目的 token **不得**被升格成 Publisher key。
- L0 §00.3 那句「**唯一 Human Owner ≠ 單一技術 Principal**」維持原文，一個字不改；本節是它的**讀法
  澄清**，不是它的修訂。

**為什麼這是兩軸，而不是一個折衷**：模型自由解決的是「這台主機只有一個合格供應商／一個合格模型」的
現實；credential 分離解決的是「同一支 token 不能既產生又批准」。前者放寬不會讓後者變鬆——把
`model_diversity_optional = true` 讀成「SoD 可以少一層」是**誤讀**，且會直接抵觸 L0 的四個硬邊界。
任何要移除 credential 分離的提案，都是**另一件治理修訂**，必須逐效果、逐風險、由 OWNER 另行裁決，
不能用本節當依據。

**落地範圍**：本節是文件層的規範陳述。`FHS_ORIGINAL_ACK.json` 的 `separation_level` 現值
`PROCESS_LANE_EVIDENCE_SEPARATION_ONLY` 與 `model_sharing_exception` 的文字**不需要也不應該**被改寫；
兩者談的是車道分離與模型共用，不是 credential 軸。

---

### CH27.8 (E12 / claim ceiling) — 本章不授權什麼

```json
"claim_ceiling": {
  "granted": "R27_APPEND_ONLY_CORRECTION_RECORDED",
  "not_licensed": [
    "FULL_W0_CLOSEOUT",
    "NATIVE_SIGNED",
    "PASS_CHALLENGE",
    "RELEASE",
    "CROSS_SESSION_HARD_ENTRY"
  ]
}
```

- **`FULL_W0_CLOSEOUT`**：不授權。22 個 full gate 中仍有 6 個只能在具備 31 冊本地來源的主機上跑；
  本輪沒有任何一次 full-profile 22/22 的執行記錄。
- **`NATIVE_SIGNED`**：不授權。本輪沒有動用任何 owner 金鑰、沒有開簽章窗、沒有 mint 任何簽章。
- **`PASS_CHALLENGE`**：不授權。r26 的 external challenge 是**被回應的對象**，不是被推翻的對象；
  本章只更正它指出的缺陷，不宣稱它已被獨立 reviewer 判定通過。
- **`RELEASE`**：不授權。`RELEASE_GRANTED` 只能由原 Publisher 在 `GHP-02` 與發行後讀回之後給出；
  本輪沒有任何一次發行。
- **`CROSS_SESSION_HARD_ENTRY`**（跨 session 硬入口）：**只**在「hook 被安裝且被量測的那一台主機、
  那一個 dispatcher」上成立；對其他 host、desktop app session 或另一個 repo 的 spawn 點，本章
  **不主張**任何攔截能力。任何把單機證據外推成全域硬入口的引用，都是 claim-ceiling 越界。

**這一章的邊界**：本章更正文字與數字，不改任何控制平面、不改任何簽章、不改任何 repo 的 `main`、
不改任何藍圖（藍圖修訂是 `out/BLUEPRINT_AFFECTED_SCOPE_DELTA.md` 裡的**提案**，須逐份由原 consumer
ratify，ratify 之前不生效）。

---

### CH27.V — append-only 與量測的可重現證明

```
# 1. 兩個 r26 身分（同一份文件的兩種位元形式）
$ sha256sum evidence/fhs-w0-r26-repair-20261109/doc/FHS_PIPD-LS-PKG_W0_r26.md
09c666dad4f31099f862c12cc5d3758620c46c70bc5f410af727c465bbb6f0f7   667205 bytes  (LF, git blob 9b3d0119)
$ sha256sum "…/知識庫/…/實作/W0/FHS_PIPD-LS-PKG_W0_r26.md"
0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f   668540 bytes  (raw, 1,335 CRLF 行)

# 2. 兩者只差行尾：raw 去掉 CR 後與 LF 形逐位元相等（1,335 行、無其他差異、首差 offset 481255）
$ python evidence/L7/pin_r26_identity.py
raw.replace(b"\r\n", b"\n") == lf  ->  True

# 3. r27 的前 667,205 bytes 與 r26 LF 形完全相同
$ python evidence/L7/check_append_only.py --r26 <r26> --r27 <r27>
prefix_identical: True   prefix_bytes: 667205   r26_bytes: 667205   r27_bytes: <r27>   appended_bytes: <本章>
r26 sha256          = 09c666dad4f31099f862c12cc5d3758620c46c70bc5f410af727c465bbb6f0f7  (667205 bytes)
r27 prefix sha256   = 09c666dad4f31099f862c12cc5d3758620c46c70bc5f410af727c465bbb6f0f7
$ head -c 667205 <r27> | cmp - <r26> ; echo $?
0

# 4. 反向：把前綴動一個 byte，同一個檢查器必須拒絕
$ python evidence/L7/check_append_only.py --r26 <r26> --r27 <prefix-mutated-copy>
PREFIX_NOT_IDENTICAL   first_diff_offset=1000   exit 1
```

第 3、4 兩條一起才構成證明：一個永遠回 `true` 的檢查器不是證據。這兩條的實跑輸出在
`evidence/L7/m08_prefix_identity.log` 與 `evidence/L7/m09_append_only_negative.log`。

本檔依 r26 的同一慣例**不記錄自身 digest**（避免自我指涉）；r27 的 bytes 與 sha256、以及本輪全部
log 的 sha256，記在 `out/L7_RESULT.json`。
