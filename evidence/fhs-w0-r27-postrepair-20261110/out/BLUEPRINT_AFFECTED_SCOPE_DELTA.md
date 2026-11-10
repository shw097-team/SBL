# 七份藍圖的受影範圍差額（r27）— 全部 `PROPOSED_FOR_RATIFICATION`

> 本檔是**提案**，不是修訂。七份文件全部維持現行 bytes 不變；每一份的修訂都是「在釘住的錨點行插入一段帶 `<!-- R27-APPEND:<DOC> -->` 的追加文字」，原文一個字都不改。

> 產出來源：`evidence/L7/blueprint_measure.json`（實測 bytes/lines/sha256）＋ `evidence/L7/anchors.json`（12 個錨點，`pin_anchors.py` 12/12 OK，log `evidence/L7/m10_anchor_pins.log`）。

> 負例：`evidence/L7/run_amendment_negatives.py` 對七份文件實跑 29 個案例（7 個接受 ＋ 22 個拒絕），全部命中預期拒絕碼，log `evidence/L7/m07_amendment_negatives.log`。


## 0. 七份文件現值（實測）

| doc | 檔案 | bytes | lines(LF split) | sha256 | 錨點數 |
|---|---|---|---|---|---|
| `L0` | `FHS_總藍圖_r4.md` | 291351 | 2043 | `7befcac3570caf9e1ade2ed231bd04de6a561f9b3038fef89597233f3566b75d` | 4 |
| `L1` | `FHS_PIPD-LS-PKG_藍圖_r4.md` | 6224679 | 28005 | `cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b` | 3 |
| `L2` | `FHS_PIPD-LS-PKG_全波次藍圖_r4.md` | 874793 | 2060 | `bb970a439fe31faf23e86c054f6282e538d369b84841d778e3b35b69ce5d4d37` | 1 |
| `W1` | `FHS_PIPD-LS-PKG_W1_藍圖_skeleton_2026-11-04_r5.md` | 588819 | 3132 | `6b60f9f64cfb8589ae4a572cce724be07f57a2a8eca0996e0ad66ebf80ee86fb` | 1 |
| `W2` | `FHS_PIPD-LS-PKG_W2_藍圖_skeleton_2026-11-04_r5.md` | 250300 | 1460 | `7c99e29d00df2da2860965488c0994c435baa0b8cbbc5937934f1a73aba136ec` | 1 |
| `W3` | `FHS_PIPD-LS-PKG_W3_藍圖_skeleton_2026-11-04_r5.md` | 1544950 | 3034 | `47e75d3f808538d0ccce44b412440e418c50e9721d7836b0159dc90bae3da5cd` | 1 |
| `W4` | `FHS_PIPD-LS-PKG_W4_藍圖_skeleton_2026-11-04_r5.md` | 209294 | 1362 | `704260c23f2f19a76614af63d97f0a8108c94f350f144e2918a69480e23f14b1` | 1 |

## 1. 逐份提案

### L0 — 《FHS_總藍圖》r4

- **狀態**：`PROPOSED_FOR_RATIFICATION`（未生效）
- **檔案**：`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖/FHS_總藍圖_r4.md`
- **現值**：291351 bytes／2043 lines／`7befcac3570caf9e1ade2ed231bd04de6a561f9b3038fef89597233f3566b75d`
- **要補的洞**：模型多樣性可選＋受保護身份邊界（EC-R26-012）、單一 Owner／單一 Issuer、證據升格否決權
- **必須 ratify 的原 consumer**：原 OWNER（唯一 Human Owner）簽核；下游 consumer = 原 HGK PLAN／Fabric Policy Reader 與 Protected Checker／Publisher
- **不得動到的東西**：不改 §00.3 既有四條硬邊界任一字元；不新增第五條硬邊界；不重編 §00–§13 章號

#### 錨點 `L0-S4`（第 50 行，`insert_row_after`）

原文（逐字，不動）：

```
| PUBLICATION | 原 Publisher 對同 Candidate／Scope／Epoch 的發行與讀回 | `/ship`、PR 綠燈、壓縮包 Seal、文件完成 |
```

插入文字（帶 `<!-- R27-APPEND:L0 -->` 標記）：

```markdown
| PROMOTION VETO | 某層證據只能在其原 Consumer、同 Subject／Scope、帶該層自己的 Raw 之下被上一層引用；跨層引用需具名 join | 以上一層的**存在**替下一層背書（例：CI 綠＝RELEASE、PR 綠燈＝Publisher 已發行、文件完成＝Native 已載入） |
```

#### 錨點 `L0-S2`（第 68 行，`insert_bullet_after`）

原文（逐字，不動）：

```
- **唯一 Human Owner ≠ 單一技術 Principal**：人可以是同一位，但 Maker、HGK Issuer、Protected Checker、Publisher 的 OS／Credential／Trust 不能折疊；Profile 名稱不等於 Windows SID 或 ACL。
```

插入文字（帶 `<!-- R27-APPEND:L0 -->` 標記）：

```markdown
  - **本條不因模型選擇而變**：車道可共用同一模型或同一 provider（`model_diversity_optional = true`），但 Maker、Issuer、Checker、Publisher 的 OS／Credential／Trust 仍不得折疊；credential 分離不因「合格模型只有一個」而降級。
```

#### 錨點 `L0-S1`（第 466 行，`insert_subsection_before`）

原文（逐字，不動）：

```
### 06.3 Windows／多 Profile 已知風險的局部修補
```

插入文字（帶 `<!-- R27-APPEND:L0 -->` 標記）：

```markdown
#### 06.2B｜模型多樣性可選、受保護身份不變（r27 追加，PROPOSED_FOR_RATIFICATION）

`model_diversity_optional = true`：任何車道不得因「與另一車道共用同一模型或同一 provider」被拒絕；`same_arm_lanes` 只記錄，永不作為失敗條件。

`protected_identity_permissions = UNCHANGED`：Maker ≠ Issuer／Checker／Publisher（**credential 軸**）；Writer 不得自簽 protected pass；一個通用目的 token 不得升格為 Publisher key。

兩個軸互不推導：模型自由度變大，不會讓 credential 分離變鬆。任何要移除 credential 分離的提案，都是另一件治理修訂，須逐效果另行裁決。

POS：九個槽由少於三個模型服務時，路由仍成立。NEG：以「模型已多樣化」推定 SoD 已滿足 → 拒收；以同一 token 產生並批准受保護通過 → 拒收。
```

#### 錨點 `L0-S3`（第 521 行，`insert_item_after`）

原文（逐字，不動）：

```
4. **所有五來源集合 485**：`Native20=20; Default30=30; Donor24=24; Method25=25; TECH386=386`，是有來源身份的 **485 個原功能/決策槽位**，並非 485 份獨立下載／強制安裝。每筆保留 `OriginalID,Name,OriginalDisposition,MandatoryFlag,OriginalOwner,Consumer,POS,NEG,Host,Effect,License,Pin,Exit`；同 Occupant 可服務多原 Slot，但逐 Slot 的功能與 NEG 不能消掉。
```

插入文字（帶 `<!-- R27-APPEND:L0 -->` 標記）：

```markdown
5. **單一 OWNER／單一 Issuer 不因車道模型可選而變**：OWNER 仍為唯一 Human Owner；Issuer 仍是原 HG-KSEOS 唯一 Issuer；Fabric 仍只做 Policy／FAR，SBL 仍只做產品與 SBL-hosted PIPD。本節不新增第二 Issuer、第二 Policy DB、第二 Release Writer。
```

**負例（本輪實跑）**：
- `POS` → exit 0，`AMENDMENT_APPLIED`（輸入 `L0_pos.md`，sha256 `4ebc8e5ed706ddd0…`）
- `NEG_PREFIX@1000` → exit 1，`AMENDMENT_PREFIX_MISMATCH`（輸入 `L0_neg_prefix.md`，sha256 `8c1b7c7dd237ed0e…`）
- `NEG_ANCHOR` → exit 3，`AMENDMENT_ANCHOR_MISSING`（輸入 `L0_neg_anchor.md`，sha256 `57f7580afc930154…`）
- `NEG_MARKER` → exit 5，`MARKER_MISSING`（輸入 `L0_neg_marker.md`，sha256 `03cb42c89ec874dd…`）
- **尚欠原 consumer 端執行的語義負例**：以本節推定「credential 分離已滿足」的引用，必須被原 Protected Checker 拒收（consumer 端執行，本輪未執行）

### L1 — 《FHS_PIPD-LS-PKG_藍圖》r4

- **狀態**：`PROPOSED_FOR_RATIFICATION`（未生效）
- **檔案**：`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖/FHS_PIPD-LS-PKG_藍圖_r4.md`
- **現值**：6224679 bytes／28005 lines／`cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b`
- **要補的洞**：單一 FHS-3L&M ABI／九槽、Registry／Pool／Session／ActualServed 四型契約、quorum 真票約束
- **必須 ratify 的原 consumer**：Original PIPD Intake／Authority／Profile Reader；CH-19 段另需 Hermes Host/PID ＋ HGK Lane Reader（`H-LANE-06`）；CH-43 quorum 段另需原 Protected Checker／Challenge Consumer
- **不得動到的東西**：**不得改動 84 個 DesignID**（本輪實測：60 個 `FHS-DR-###` ＋ 24 個 `INT-##` = 84）；不新增 CH-50 之後的一級章；不重述 CH-03／CH-16 已定義的共用 envelope 欄位

#### 錨點 `L1-S1`（第 1830 行，`insert_subsection_after`）

原文（逐字，不動）：

```
<!-- R4-END:CH-19 -->
```

插入文字（帶 `<!-- R27-APPEND:L1 -->` 標記）：

```markdown
## r27｜`FHS-3L&M` 單一 ABI 與九槽（PROPOSED_FOR_RATIFICATION）

- 本文件只承認**一個** `FHS-3L&M` ABI：三車道 × 三槽 = **九槽**，唯讀自原 HGK `lane-routing-registry.yaml` 與 `lane-route-slots.candidate.json`；不得另建第二 router／registry／pool。
- 每車道 pool 的臂數以 registry 為準（本輪實測 PLAN 6、EXECUTE 4、VERIFY_SECURITY 5）；候選臂不得超出 pool。
- 每次派工須有 run-scoped binding：`run_id, session_id, work_id, lane, slot, provider, model, pool_rank, policy_epoch(int), registry_sha256, pool_sha256, retired_ledger_sha256, nonce, bound_at, expires_at`；以 `O_CREAT|O_EXCL` 建立，碰撞即拒，不得覆寫。
- `same_arm_lanes` 一律記錄，永不作為拒絕理由（見 L0 §06.2B）。

NEG：同一 binding 被兩個 session 覆寫；以 `Selected` 冒充 `ActualServed`；以字串型號當 `policy_epoch`。
```

#### 錨點 `L1-S2`（第 1630 行，`insert_subsection_after`）

原文（逐字，不動）：

```
<!-- R3-END:CH-16 -->
```

插入文字（帶 `<!-- R27-APPEND:L1 -->` 標記）：

```markdown
## r27｜Registry／Pool／Session／ActualServed 四型契約（PROPOSED_FOR_RATIFICATION）

| 型 | 必要欄 | 拒收條件 |
|---|---|---|
| `Registry` | `epoch`(int)、`status`(IN_FORCE¦CANDIDATE)、`retired_arms{}`、自身 sha256 | epoch 非整數；退役臂仍在任一 live 位置 |
| `Pool` | 逐車道 `arms[]`（`rank`, `provider/model`）、自身 sha256 | 臂不在該車道 pool；rank 重複 |
| `Session` | `run_id, session_id, process_id`(fresh PID)、`lane, slot, binding_id, expires_at` | 同 `(lane,slot)` 覆寫；過期；body digest ≠ `binding_id` |
| `ActualServed` | `request_id, response_id, provider, api_mode, profile_sha, host_pid, model_usage_raw` | 只有 Selected／只有 HTTP 200／只有 UI 顯示 |

`Selected ≠ ActualServed`；缺 `ActualServed` raw 一律 `NOT_OBSERVED`，不得以字串型號推斷。
registry 的退役段與 pool 的 `retired_arms` 不一致時 → `HOLD`（不得擇一採用）。
```

#### 錨點 `L1-S3`（第 27367 行，`insert_subsection_after`）

原文（逐字，不動）：

```
<!-- R4-END:CH-43 -->
```

插入文字（帶 `<!-- R27-APPEND:L1 -->` 標記）：

```markdown
## r27｜quorum 真票約束（PROPOSED_FOR_RATIFICATION）

- 一個 `DECIDED` preservation property 需 ≥2 張**有效**票，且票來自互異的 lane 身份、同 candidate、同 span。
- 有效票必要欄（缺一不計票）：`lane_id, candidate_sha256, source_sha256, clause_id, property, raw_path, raw_sha256, timestamp, session_id, process_id`。
- 票值必須 `type(v) is bool`；JSON 整數 `1`、字串 `"true"` 不是票。
- raw 必須可重算：`sha256(bytes(raw_path)) == raw_sha256`；不可解析或不等即不計票。
- 同一 `lane_id` 或同一 `(session_id, process_id)` 的重複票只算一票（不是兩張）。

NEG：以 dict 形狀 `{"A": true}` 取代具名票；以 `"00"*32` 假 digest 過關；把兩張同 process 的票算成 quorum。
```

**負例（本輪實跑）**：
- `POS` → exit 0，`AMENDMENT_APPLIED`（輸入 `L1_pos.md`，sha256 `8ca0d1ac0779dcc5…`）
- `NEG_PREFIX@1000` → exit 1，`AMENDMENT_PREFIX_MISMATCH`（輸入 `L1_neg_prefix.md`，sha256 `b425c583bc01e386…`）
- `NEG_ANCHOR` → exit 3，`AMENDMENT_ANCHOR_MISSING`（輸入 `L1_neg_anchor.md`，sha256 `9b736ef21af863e8…`）
- `NEG_MARKER` → exit 5，`MARKER_MISSING`（輸入 `L1_neg_marker.md`，sha256 `614e9cf2344f7ecf…`）
- `NEG_DESIGNID` → exit 4，`DESIGNID_COUNT_DRIFT`（輸入 `L1_neg_designid.md`，sha256 `44f08b0a3767c4c6…`）
- **尚欠原 consumer 端執行的語義負例**：把九槽寫成「三個模型」，或新增第二個 registry／router，必須被原 HGK Lane Reader 拒收（consumer 端執行，本輪未執行）

### L2 — 《FHS_PIPD-LS-PKG_全波次藍圖》r4

- **狀態**：`PROPOSED_FOR_RATIFICATION`（未生效）
- **檔案**：`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖/FHS_PIPD-LS-PKG_全波次藍圖_r4.md`
- **現值**：874793 bytes／2060 lines／`bb970a439fe31faf23e86c054f6282e538d369b84841d778e3b35b69ce5d4d37`
- **要補的洞**：W0-A／W1／W2／W3／W4 的責任切分與 resume predicate
- **必須 ratify 的原 consumer**：原 TPM Program／PLAN Reader
- **不得動到的東西**：**不新增 WP #23**；**不新增 DAG 邊 #37**；不改 22 WP／36 邊的既有身份與方向

#### 錨點 `L2-S1`（第 601 行，`insert_subsection_before`）

原文（逐字，不動）：

```
## 5.0｜W0／`FHS_PKG_WAVE_000`：先確定來源/Authority 與 W0-A 首個可用三 SPEC，不等待 OPS
```

插入文字（帶 `<!-- R27-APPEND:L2 -->` 標記）：

```markdown
### 4.r27-SP｜W0-A／W1／W2／W3／W4 責任切分與 resume predicate（PROPOSED_FOR_RATIFICATION）

| 相位 | 允許的效果 | 唯一 WriteSet | 不得做的事 | resume predicate |
|---|---|---|---|---|
| `W0-A` | `SOURCE_READ` ＋ `LOCAL_DRAFT_WRITE` | 隔離 output root | 不 mint Permit、不寫任何 repo | 31 冊 snapshot manifest ＋ 三 SPEC 草稿 ＋ W0 cursor |
| `W1` | 路由／registry／issuer／host 的**讀回** | 無（唯讀） | 不寫 repo、不發任何世界效果 | 九槽可 bind、`--assert` 全綠、retired ledger 可讀 |
| `W2` | 受保護、可逆的寫入 | 具名 repo 的 allowed-writeset | 跨 Scope、自簽 Checker、無 Permit 先寫 | Permit＋epoch＋preimage＋rollback commit raw |
| `W3` | UX／Host 矩陣／normal mode | 文件與規格 | 新增世界效果、以 UI 顯示當 served | fresh PID 之三 Lane `ActualServed` raw |
| `W4` | Release／Retire **候選** | release artifact | 把 CI 綠當 Release | `GHP-02` ＋ 發行後 readback |

resume predicate 的共同形狀：`last_good + first_fail + next_legal_action`，且必須指名原 Reader；沒有原 Reader 的讀回，就不是 resume，是重新開始。

**邊界**：本節不新增 WP、不新增 DAG 邊；任何超出 22 WP／36 邊的提案，都在 L2 之外處理。
```

**負例（本輪實跑）**：
- `POS` → exit 0，`AMENDMENT_APPLIED`（輸入 `L2_pos.md`，sha256 `6037774c56207867…`）
- `NEG_PREFIX@1000` → exit 1，`AMENDMENT_PREFIX_MISMATCH`（輸入 `L2_neg_prefix.md`，sha256 `b7aa9700453da595…`）
- `NEG_ANCHOR` → exit 3，`AMENDMENT_ANCHOR_MISSING`（輸入 `L2_neg_anchor.md`，sha256 `b12b8c8e0a5a7675…`）
- `NEG_MARKER` → exit 5，`MARKER_MISSING`（輸入 `L2_neg_marker.md`，sha256 `1ab15dd6c1db6cf3…`）
- **尚欠原 consumer 端執行的語義負例**：任何引入 WP #23 或 DAG 邊 #37 的提案，必須被原 Program Reader 拒收（consumer 端執行，本輪未執行）

### W1 — 《FHS_PIPD-LS-PKG_W1_藍圖&skeleton》r5

- **狀態**：`PROPOSED_FOR_RATIFICATION`（未生效）
- **檔案**：`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖/各W藍圖&skeleton/FHS_PIPD-LS-PKG_W1_藍圖_skeleton_2026-11-04_r5.md`
- **現值**：588819 bytes／3132 lines／`6b60f9f64cfb8589ae4a572cce724be07f57a2a8eca0996e0ad66ebf80ee86fb`
- **要補的洞**：native startup／discovery hook、Codex CLI 的 lane-bound dispatch、單一 issuer／pool／registry 綁定
- **必須 ratify 的原 consumer**：SBL-hosted PIPD 原 Writer／Receiver ＋ 原 HGK Registry／Issuer
- **不得動到的東西**：不新增 launcher；不改 24 張 L2 Design Obligation 的身份；不把 W1 寫成會寫 repo 的相位

#### 錨點 `W1-S1`（第 110 行，`insert_section_before`）

原文（逐字，不動）：

```
## W1-r5｜角色、產品規格與三庫工程入口
```

插入文字（帶 `<!-- R27-APPEND:W1 -->` 標記）：

```markdown
## W1-r27｜native startup／discovery hook 與 lane-bound dispatch（PROPOSED_FOR_RATIFICATION）

- 組態發現只走原生 startup 路徑（profiles／gateway state／`hgk-lane-dispatch.py`），不得另造第二個 launcher 或第二套 discovery。
- Codex CLI 的每一次派工必須綁定 `(lane, slot, arm, policy_epoch, binding_id)`；未綁定即**不得 spawn**，且拒絕必須發生在建立子程序之前。
- 一個 Issuer、一個 pool、一個 registry：W1 只讀，不寫、不投影、不複製成第二份；`registry_sha256` 與 `pool_sha256` 記進每一次讀回。

NEG：以 `AGENTS.md` 的一行提示取代機械攔截；以 Selected 臂直接 spawn；在 W1 內寫回 registry。
```

**負例（本輪實跑）**：
- `POS` → exit 0，`AMENDMENT_APPLIED`（輸入 `W1_pos.md`，sha256 `f534f7da04f03a61…`）
- `NEG_PREFIX@1000` → exit 1，`AMENDMENT_PREFIX_MISMATCH`（輸入 `W1_neg_prefix.md`，sha256 `a35b612566032351…`）
- `NEG_ANCHOR` → exit 3，`AMENDMENT_ANCHOR_MISSING`（輸入 `W1_neg_anchor.md`，sha256 `5475941c6063a49d…`）
- `NEG_MARKER` → exit 5，`MARKER_MISSING`（輸入 `W1_neg_marker.md`，sha256 `efdcbad62ce67d34…`）
- **尚欠原 consumer 端執行的語義負例**：以 prompt 一行取代 lane binding 的派工，必須被 dispatch guard 以 `FHS_ENTRY_ASSERT_REQUIRED` 拒（由 L5 車道執行；本文件不宣稱）

### W2 — 《FHS_PIPD-LS-PKG_W2_藍圖&skeleton》r5

- **狀態**：`PROPOSED_FOR_RATIFICATION`（未生效）
- **檔案**：`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖/各W藍圖&skeleton/FHS_PIPD-LS-PKG_W2_藍圖_skeleton_2026-11-04_r5.md`
- **現值**：250300 bytes／1460 lines／`7c99e29d00df2da2860965488c0994c435baa0b8cbbc5937934f1a73aba136ec`
- **要補的洞**：真寫入前的 Permit／epoch／preimage／allowed-writeset 四件套；source-read ACL 不變
- **必須 ratify 的原 consumer**：原 DEV Repo Reader ＋ 原 HGK Issuer ＋ WorldRaw Consumer
- **不得動到的東西**：不放寬 `SOURCE_READ` ACL；不改 W2 四主 WP 的身份；不新增依賴邊

#### 錨點 `W2-S1`（第 91 行，`insert_subsection_before`）

原文（逐字，不動）：

```
### 最少充分交付與法位分離
```

插入文字（帶 `<!-- R27-APPEND:W2 -->` 標記）：

```markdown
### W2-r27｜真寫入前的四件套：Permit／epoch／preimage／allowed-writeset（PROPOSED_FOR_RATIFICATION）

- 任何 `REPO_DEV_WRITE` 生效前，必須同時具備：①原 HGK Permit（同 Subject／Scope）②有效的 numeric policy epoch ③目標寫入集的 preimage digest ④具名的 allowed-writeset。缺一即拒，且在寫入前拒。
- 四件齊備才可寫；寫後必須留下 rollback commit 與世界讀回（world diff ＋ Raw）。
- **`SOURCE_READ` 的 ACL 完全不變**：本節不放寬任何讀取權限，也不允許寫入路徑借用讀取 ACL 或反向借用。

NEG：以 Candidate ECP 充當 Permit；以字串 epoch 充當有效 epoch；寫入範圍超出 allowed-writeset 仍宣稱完成。
```

**負例（本輪實跑）**：
- `POS` → exit 0，`AMENDMENT_APPLIED`（輸入 `W2_pos.md`，sha256 `5e26392ec99556d9…`）
- `NEG_PREFIX@1000` → exit 1，`AMENDMENT_PREFIX_MISMATCH`（輸入 `W2_neg_prefix.md`，sha256 `9f5a838e9feb5425…`）
- `NEG_ANCHOR` → exit 3，`AMENDMENT_ANCHOR_MISSING`（輸入 `W2_neg_anchor.md`，sha256 `f26a4de86e112a5c…`）
- `NEG_MARKER` → exit 5，`MARKER_MISSING`（輸入 `W2_neg_marker.md`，sha256 `052e4eac2f02fc16…`）
- **尚欠原 consumer 端執行的語義負例**：缺 Permit 仍寫入的情形，必須被原 HGK Issuer 拒（consumer 端執行，本輪未執行）

### W3 — 《FHS_PIPD-LS-PKG_W3_藍圖&skeleton》r5

- **狀態**：`PROPOSED_FOR_RATIFICATION`（未生效）
- **檔案**：`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖/各W藍圖&skeleton/FHS_PIPD-LS-PKG_W3_藍圖_skeleton_2026-11-04_r5.md`
- **現值**：1544950 bytes／3034 lines／`47e75d3f808538d0ccce44b412440e418c50e9721d7836b0159dc90bae3da5cd`
- **要補的洞**：可選的三車道九槽 UI、跨 host loader／ActualServed 讀回、fallback 邊界、fresh-PID 驗收
- **必須 ratify 的原 consumer**：Hermes original Runtime／Launcher／Provider Raw Reader → HGK Lane／Journal Consumer
- **不得動到的東西**：不把 UI 顯示升格為 served；不新增第六個工程波次；不改 W18 的 E33–E42 身份

#### 錨點 `W3-S1`（第 131 行，`insert_subsection_before`）

原文（逐字，不動）：

```
## 0.5｜原技術五集合：需要的功能預設必備，實例要真資格化
```

插入文字（帶 `<!-- R27-APPEND:W3 -->` 標記）：

```markdown
## 0.4B｜三車道九槽 UI、跨 host loader／ActualServed 讀回與 fallback 邊界（PROPOSED_FOR_RATIFICATION）

- UI 的三車道九槽是**可選呈現**：未顯示不等於未服務，顯示也不等於 served。一切以 `ActualServed` raw 為準。
- 跨 host 讀回必須帶 loader 身分（`profile_sha, host_pid, process_origin`）與 `request_id → response_id → actual_served` 的因果鏈；跨 host 借收據一律拒。
- fallback 只在原 Policy 已批准的集合內成立，且有界（次數／成本／該 lane 的效果）；越界即 PARK 該 lane 的受影工作，不動全域 `model.default`。
- fresh-PID 驗收：新 process、普通 Goal、零 B1 專用 prompt，三 Lane 各自可讀回；缺一即 `LANE_ACTUALSERVE_HOLD`。

NEG：以 UI 綠燈或 200 回應宣稱 served；以舊 B1 主機的 Raw 冒充 normal-mode 驗收。
```

**負例（本輪實跑）**：
- `POS` → exit 0，`AMENDMENT_APPLIED`（輸入 `W3_pos.md`，sha256 `70be088e2ebbd62a…`）
- `NEG_PREFIX@1000` → exit 1，`AMENDMENT_PREFIX_MISMATCH`（輸入 `W3_neg_prefix.md`，sha256 `02858014de21441a…`）
- `NEG_ANCHOR` → exit 3，`AMENDMENT_ANCHOR_MISSING`（輸入 `W3_neg_anchor.md`，sha256 `5a9078e498259635…`）
- `NEG_MARKER` → exit 5，`MARKER_MISSING`（輸入 `W3_neg_marker.md`，sha256 `832919fc3a44cb72…`）
- **尚欠原 consumer 端執行的語義負例**：以 UI 顯示或 200 當 served 的引用，必須以既有 `LANE_ACTUALSERVE_HOLD` 拒（consumer 端執行，本輪未執行）

### W4 — 《FHS_PIPD-LS-PKG_W4_藍圖&skeleton》r5

- **狀態**：`PROPOSED_FOR_RATIFICATION`（未生效）
- **檔案**：`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖/各W藍圖&skeleton/FHS_PIPD-LS-PKG_W4_藍圖_skeleton_2026-11-04_r5.md`
- **現值**：209294 bytes／1362 lines／`704260c23f2f19a76614af63d97f0a8108c94f350f144e2918a69480e23f14b1`
- **要補的洞**：CI 綠 ≠ Release、供應鏈／授權／SBOM／rollback、受保護 Publisher 閘
- **必須 ratify 的原 consumer**：原 Protected Checker ＋ 原 Publisher（`GHP-02`）
- **不得動到的東西**：不改 `E-FULL-01..08` 的原 ID 與完成門檻；不改 `W4-01..12` 的身份；不新增依賴邊

#### 錨點 `W4-S1`（第 254 行，`insert_subsection_before`）

原文（逐字，不動）：

```
### 2.2A｜39 `ModeGateIdentityDisposition`：獨立於 192 Cell 的 W3→W4 收件（F-002）
```

插入文字（帶 `<!-- R27-APPEND:W4 -->` 標記）：

```markdown
### 2.1B｜CI 綠 ≠ Release；供應鏈、授權與 rollback 的受保護 Publisher 閘（PROPOSED_FOR_RATIFICATION）

- CI 綠只證明該 repo 的規則集對該 commit 通過；它不是 Release，也不是任何 Checker verdict。
- Release 前必須具備**同一 BuildDigest** 下的：授權（License）、NOTICE、SBOM、scanner raw、rollback/last-good/dual-read。缺一即 `RELEASE_SUPPLY_CHAIN_EVIDENCE_MISSING`。
- 發行只能由原 Publisher 以 `GHP-02` 對同 Candidate／Scope／Channel 給出，並留下發行後讀回；沒有讀回就沒有 `P2_FULL_PKG_RELEASE_DONE`。
- 通用目的 token 不得升格為 Publisher key；Maker 不得自簽 protected pass（見 L0 §06.2B 與 §00.3）。

NEG：以 CI green 自稱 Release（應得 `RELEASE_NOT_GRANTED`）；缺 SBOM 仍判 E26 通過。
```

**負例（本輪實跑）**：
- `POS` → exit 0，`AMENDMENT_APPLIED`（輸入 `W4_pos.md`，sha256 `c1508def95ef2c35…`）
- `NEG_PREFIX@1000` → exit 1，`AMENDMENT_PREFIX_MISMATCH`（輸入 `W4_neg_prefix.md`，sha256 `1f4ab23a77c20b23…`）
- `NEG_ANCHOR` → exit 3，`AMENDMENT_ANCHOR_MISSING`（輸入 `W4_neg_anchor.md`，sha256 `668f063558cfc575…`）
- `NEG_MARKER` → exit 5，`MARKER_MISSING`（輸入 `W4_neg_marker.md`，sha256 `a7b722749e997f34…`）
- **尚欠原 consumer 端執行的語義負例**：CI 綠即宣告發行的引用，必須以既有 `RELEASE_NOT_GRANTED` 拒（consumer 端執行，本輪未執行）

## 2. 負例工具與它證明什麼

`evidence/L7/check_blueprint_amendment.py` 對「修正後的檔案」要求四件事同時成立：
①前 N bytes 與釘住的原文逐位元相同（`AMENDMENT_PREFIX_MISMATCH`，exit 1）②錨點行仍在原位且未被改寫（`AMENDMENT_ANCHOR_MISSING`，exit 3）③L1 的 84 個 DesignID 分母不變（`DESIGNID_COUNT_DRIFT`，exit 4）④追加段恰好出現一次標記（`MARKER_MISSING`，exit 5）。

這四條合起來的意思：一份「合法修正」只能是**純插入**，而且插入點與分母都不能漂。只驗 prefix 不驗錨點，會漏掉「原文被換掉、但新舊檔前綴剛好相同」以外的所有情況；只驗錨點不驗 prefix，則任何改寫都能過關。

## 3. 明確不在本提案內的主張

- 七份文件**都還沒有被 ratify**，本輪不主張任何一份已修訂。
- 提案文字本身**不是** new authority：它若與 L0／原 Domain Canonical 衝突，以原 Reader 為準。
- L1 的 84 個 DesignID、L2 的 22 WP／36 邊、W4 的 `E-FULL-01..08` 與 `W4-01..12` 都**不新增、不改號**。
- 沒有任何提案會讓 `FULL_W0_CLOSEOUT`／`NATIVE_SIGNED`／`PASS_CHALLENGE`／`RELEASE` 成立。
