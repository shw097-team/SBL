---
artifact_id: FHS-PIPD-LS-PKG-W0-OWNER-AUTHORIZED-FINAL
artifact_version: 2026-11-05_r4-final-c7a91e
candidate_id: FHS-W0-OWNER-AUTHORIZED-FINAL-r4-final-c7a91e
candidate_round: OWNER_AUTHORIZED_FINAL
generation: 3
parent_candidate_body_sha256: 44a55d6d4af26fd51f36fdb1bdfaf511bfcface6f379b4afc9232b949c18439c
historical_parent_r3_body_sha256: 0e4f1ed002f024bc9030fe50937e53ddeb1fcd921c1d015f3b0d51165166b328
supersedes_author_draft_r2_sha256: e313d4d49dec9094a840052c9dc25092c3383019cbf58cd878aad90649a7fd66
upper_l0_sha256: 7befcac3570caf9e1ade2ed231bd04de6a561f9b3038fef89597233f3566b75d
upper_l1_sha256: cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b
upper_l2_sha256: bb970a439fe31faf23e86c054f6282e538d369b84841d778e3b35b69ce5d4d37
upper_w0_sha256: 4f8d67fd9978f6ce67014736991b88cec2c90d9ba31229475f6556db5114622a
version_currency: OWNER_AUTHORIZED_USABLE_FINAL
r3_status: HISTORICAL_PARENT_ONLY_NOT_CURRENT
original_owner_ratification: NOT_OBSERVED
claim_ceiling: OWNER_AUTHORIZED_DESIGN_FINAL_NOT_NATIVE_PERMIT
document_status: 定案（Owner 授權可用定案）
owner_authorization_basis: USER_EXPLICIT_APPROVAL_THIS_TURN
approval_provenance: CHAT_DIRECTIVE_NOT_CRYPTOGRAPHIC_SIGNATURE
previous_generation_draft_sha256: 56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a
revision_round: FHS-W0W2-BASELINE-RECON-20261106
revision_of_file: FHS_PIPD-LS-PKG_W0_r4.md
supersedes_sha256: 0fed31f593fd132ba4f1f2d18df89a03e22e3fbdb6a75ded8bb479f86db884b4
revision_version: r5
changed_scope: ["WP-FHS-19", "WP-FHS-00", "WP-FHS-01", "D-W0-IDENTITY", "D-W0-CLOSEOUT"]
rollback_ref: ORIGINAL_BYTES_SHA_0fed31f593fd
revision_claim_ceiling: AUTHOR_SIDE_RECONCILED_WITH_SCOPED_HOLDS
revision_writer: original_W0_design_curator
original_writer_transferred: false
source_snapshot_round: FHS-W0W2-BASELINE-RECON-20261106
---

> **〔R1-2026-11-06 更正〕本文件為 Owner 授權之作者端可用定案（`2026-11-05_r4-final-c7a91e`，generation 3），相對 generation 2 草案只改身份，全部條款、OriginalID、50 個 `CH` H1 與 22 WP／36 Edge 一字未動。更正：此「可用」僅指作者端設計閱讀，不代表缺口已清；2026-11-06 重算之 68 筆 HOLD 全部 OPEN，SBL #41 仍 OPEN 且 dirty，故對外 claim ceiling 降為 `AUTHOR_SIDE_RECONCILED_WITH_SCOPED_HOLDS`；不是密碼學簽章、不是 U4 原 Owner 語義核簽、不是 HGK Permit、不是 Protected Checker 判決、不是 Native、不是 Release。。**
> 相對 generation 2 草案（`56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a`）**只改身份**：檔名、frontmatter、標題與自述字樣；全部條款、OriginalID、50 個 `CH` H1 與 22 WP／36 Edge 一字未動。
> 授權依據＝本次 Owner 直接指令，`approval_provenance=CHAT_DIRECTIVE_NOT_CRYPTOGRAPHIC_SIGNATURE`；**不是**密碼學簽章、**不是** U4 原 Owner 語義核簽、**不是** HGK Permit、**不是** Protected Checker 判決、**不是** Release。
> 文中「W0 草案增補」「W0 草案路由確認」等章節標籤是**條款來源 provenance**（哪些內容在草案期補入），不代表本文件仍處草案階段；`W0_藍圖&skeleton → W0_草案 → W0_定案` 為章節流程字串，一律保留。

<!-- r2 metadata retained as lineage only
---
artifact_id: FHS-PIPD-LS-PKG-L3-W0-DRAFT-20261104-r2-HIGH-RETENTION-AUDIT-REPAIRED
artifact_type: L3_W0_FULL_SUBSTANTIVE_DRAFT
wave_id: FHS_PKG_WAVE_000
version: 2026-11-05_r3_SOURCE_BOUND_DELTA_REPAIR_AUTHOR_DRAFT_SOURCE_BOUND
supersedes_author_draft: FHS-PIPD-LS-PKG-L3-W0-DRAFT-20261104-r1
superseded_complete_zip_sha256: 2e7ace8530ce5ad9c885dd7d9a6a8e337e052df2cdbc6c98cf1b8da810297d0c
repair_audit: AUDIT-FHS-W0-DRAFT-COMPLETE-20261104-R1
repair_audit_sha256: e971ce3cb307351f285e3b4fa47505e451fc793b98746fa60b4cacf09b649e79
repair_scope: AUD-W0-P0-001..003/P1-004..009/P2-010..012
active_author_reader: THIS_R2_BODY_ONLY
language: zh-TW
source_basis: L0_r4>L1_r4>L2_r4>W0_skeleton_r4
upper_l0_sha256: 7befcac3570caf9e1ade2ed231bd04de6a561f9b3038fef89597233f3566b75d
upper_l1_sha256: cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b
upper_l2_sha256: bb970a439fe31faf23e86c054f6282e538d369b84841d778e3b35b69ce5d4d37
w0_skeleton_r4_sha256: 4f8d67fd9978f6ce67014736991b88cec2c90d9ba31229475f6556db5114622a
semantic_plan_sha256: c8cf1087255ebd811a0f7902403bc1ef4615f0be25c6fb732c6db3739cc213db
plugin_used: sbl-tpm-sp_SKILL_CONTRACTS_READ_ONLY
original_pipd_compiler: NOT_RUN
original_domain_owner_ack: NOT_OBSERVED
original_domain_writer: UNCHANGED
native_host_e2e: NOT_RUN
protected_checker: NOT_RUN
release: NOT_GRANTED
claim_ceiling: AUTHOR_DESIGN_ONLY_WITH_STATIC_READBACK_AND_AFFECTED_HOLDS
---
-->


**《FHS_PIPD-LS-PKG_W0_定案》｜2026-11-05 r3 高保留差額修補，50 CH 單一作者端工作版本**

> 本定案以 W0 r4 原正文的 50 個 CH 作**逐章高保留基線**，各章後標示「W0 草案增補」的段落為本輪作者端收斂內容。並非另一套有效 Original Canonical；W0 r4 原章文字中的「當期」僅指其**來源作者端 r4 時點**，不因被引入本草案取得新的 Native/Owner 權限。所有新決策與資料均為 `AUTHOR_DESIGN_ONLY`，受影缺項在 HOLD 表留原 Owner 與解除條件。

## 當期最高優先有效差額（承 r3 差額範圍；r3 為歷史父版本、非當期）

本定案（generation 3）承接 r3 在作者端《W0 草案》已受影 Scope 的整合、覆蓋與 r1 錯誤語義取代；r3 僅為歷史父版本，不再具當期效力；保留 r1 合法 50 H1/31 原 Source/84 Card/22 WP/36 DAG/485 正交資產/949+192+B1+AC/50+149 原身份。不另增 SBL 原 Canonical、HGK Issuer、Hermes Queue、Protected Checker/Publisher。`WP-FHS-19` 已由 r2 恢復且 r3 保留原 CI/SupplyChain 職責（不作 TraceClosure）；96 原 Oracle 個案 source-bound；25 張卡 Wave 欄分層；Default30 具名策略與 E16 歷史來源可讀。本版本單一作者端現行正文；前版 r1 **歷史/回歸用**，不存在兩套當期可生效命令。

**E16 歷史證據閉包**：所有正文中提及的「歷史 `E16`」均解至本 ZIP 內 `W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md` 的 `## E16`；原 W0 r4 非規範性附錄 SHA `7970d241cde21e9327e60d1877a7b50bdf409f403c827109c4d524a31396eb1b`，精確摘錄段 SHA `b20189badd4d69312c4cf475c6f494d814b88f8f7c7fdd35a8bdbd36018a9856`。注意 Program DAG 的 `E16: WP21→WP09` 是**另一類 OriginalEdgeID**，不得混淆為歷史附錄 E16。上游原附錄 `paired_body_bytes:960436` 與原 W0 r4 Body 真 bytes=391123 不符，SHA 配對一致，故列 `UPSTREAM_BYTE_FIELD_STALE`，不修改原 W0 r4 證物。

## 一頁入口：定案成品、法位與最小工作鏈

- **W0-A（SOURCE_READ／隔離草案）**：WP00→WP01→WP15；來源31物理 SHA、Question/Decision Ledger、Product/Architecture/Program 三 SPEC、可觀察 FUO。WP16 的技術 Need/Original Disposition 台帳可同期進行。
- **W0-B（連接而不施工）**：WP15／WP21／W0-DOC-HANDOFF-01 建 Source→Requirement→Spec→Case→Evidence→Deliver 雙向 Join，WP19 僅原 CI/License/NOTICE/SBOM SourceRead、96 Oracle PlannableCase、S1–S5 Walking Skeleton 的 Effect/原 Receiver/Raw/NEG/stop-resume，最後送 W1 原 Reader 接收。
- **波次分離**：本波六個 `WP-FHS-00/01/15/16/19/21`；真正 GJ02/WP-FHS-06 屬 W2，W18 是 B1 後常態 UAT，不是新 W5。
- **五層真值**：`AUTHOR_DESIGN` ≠ `ORIGINAL_READER_ACK` ≠ `HOST_LOADED` ≠ `NATIVE_WORLD_EFFECT` ≠ `INDEPENDENT_PASS/RELEASE`。GitHub/FHS-NAV、來源 SHA、ZIP、外掛技能都沒有相互升格的能力。
- **下游入口**：〔R1-2026-11-06 更正〕下游入口原指 `INDEX_AND_MANIFEST_r4-candidate-b41d2e.md` → 本正文 50 CH → 配對非規範性附錄 → 三份逐 ID Trace → 原 SBL PIPD／Fabric/HGK Reader，按生效 Scope 確認。更正：現行封存身份為 `2026-11-05_r4-final-c7a91e`（sha256 `0fed31f593fd132ba4f1f2d18df89a03e22e3fbdb6a75ded8bb479f86db884b4`，2254 行；定案/ZIP 內為 `W0_FINAL_定案_COMPLETE_r4-final-c7a91e.zip`）；`r4-candidate-b41d2e` 之 Index／Manifest 降為歷史父索引，只作 lineage 對照，不得再作為現行交付清單或下游入口。 → 配對非規範性附錄 → 三份逐 ID Trace → 原 SBL PIPD／Fabric/HGK Reader，按生效 Scope 確認。

## 資料與技術來源基線

| Source | 實體 SHA-256 | 本輪用法 |
|---|---|---|
| L0 | `FHS_總藍圖_2026-11-04_r4_HIGH_RETENTION_AUDIT_REPAIRED_實質正文(1).md` | `7befcac3570caf9e1ade2ed231bd04de6a561f9b3038fef89597233f3566b75d` |
| L1 | `FHS_PIPD-LS-PKG_藍圖_2026-11-04_r4_HIGH_RETENTION_AUDIT_REPAIRED_實質正文(1).md` | `cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b` |
| L2 | `FHS_PIPD-LS-PKG_全波次藍圖_2026-11-04_r4_實質正文(1).md` | `bb970a439fe31faf23e86c054f6282e538d369b84841d778e3b35b69ce5d4d37` |
| W0 | `FHS_PIPD-LS-PKG_W0_藍圖_skeleton_2026-11-04_r4_HIGH_RETENTION_FULL_DESTRUCTIVE_AUDIT_REPAIR_實質正文.md` | `4f8d67fd9978f6ce67014736991b88cec2c90d9ba31229475f6556db5114622a` |
| W1 | `FHS_PIPD-LS-PKG_W1_藍圖_skeleton_2026-11-04_r5_實質正文.md` | `6b60f9f64cfb8589ae4a572cce724be07f57a2a8eca0996e0ad66ebf80ee86fb` |
| W2 | `FHS_PIPD-LS-PKG_W2_藍圖_skeleton_2026-11-04_r5_HIGH_RETENTION_FULL_DESTRUCTIVE_AUDIT_REPAIR_實質正文.md` | `7c99e29d00df2da2860965488c0994c435baa0b8cbbc5937934f1a73aba136ec` |
| W3 | `FHS_PIPD-LS-PKG_W3_藍圖_skeleton_2026-11-04_r5_HIGH_RETENTION_AUDIT_REPAIRED_實質正文.md` | `47e75d3f808538d0ccce44b412440e418c50e9721d7836b0159dc90bae3da5cd` |
| W4 | `FHS_PIPD-LS-PKG_W4_藍圖_skeleton_2026-11-04_r5_HIGH_RETENTION_FULL_SUBSTANTIVE_AUDIT_REPAIR_實質正文.md` | `704260c23f2f19a76614af63d97f0a8108c94f350f144e2918a69480e23f14b1` |
| SC | `UNIFIED_SBL14_FHS17_SEMANTIC_CONSERVATION_PLAN_r4.md` | `c8cf1087255ebd811a0f7902403bc1ef4615f0be25c6fb732c6db3739cc213db` |
| ROLE | `FHS_專業角色動態掛載總表_2026-11-03_r1.md` | `0b0e1fde1568d394e7fb7609546567137159672ee77c98997a3bd62d2d94a3b5` |
| H1 | `FHS_不可降級_不可壓平_一級章節_2026-11-04_r2_HIGH_RETENTION_FULL_SUBSTANTIVE_AUDIT_REPAIR.md` | `ba9b64ec19e5c7e92ddfdbdf46fe38945d81d837c7c550d1689f1ec17083d0c1` |
| PROMPT | `GPT6_CHAT_FHS_PIPD-LS-PKG_W0_DRAFT_THIN_PROMPT_2026-11-04_r1.md` | `a0b410f13548eefd92b645bae1d1d963d0497dbc079cdace6d8bbcaa227b3b80` |

## Plugin 契約使用紀錄（作者端）

本輪使用已掛載 `$sbl-tpm-sp` 中 `tpm-sp`、`tpm-setup`、`tpm-product-plan`、`tpm-system-plan`、`tpm-program-plan`、`tpm-handoff` 及八個 PIPD 技能文檔協定。`tpm-sp` 要求 JTBD/FUO、POS/NEG、來源 Locator；PM/SE/TPgM 各輸出獨立 SPEC。`pipd-route-intake` 只有 Goal+源 locator 才可提 Intent；`pipd-authority-source` 必有未衝突來源 digest；`pipd-profile-tailor` 安全 veto 只能提升；PI/PD/ECP/TQAEP 都須原 Writer/Repo/Effect/Runner 綁定。這是**設計期路由**；沒有實際運行原 PIPD `@2` Compiler/Reader，也沒有直接用外掛輸出正式 Canonical。

## 外部研究的當期保守選擇

- Hermes：2026-11-04 所見官方最新 v0.22.7（2026-11-03）；本工程**維持 v0.22.5 pinned**，新版只記 HotSwap 候選。
- OpenSpec：W0 r2 選定官方 `v1.16.0`（2026-10-30），與 r1 `v1.15.0` 的設計釘選差額見 CH-23／W0_R3_TECH_CHOICE_AND_TRANSLATION.md。npm 路徑 Node >=22.12.0；Windows 預設評估 standalone；Host 實際安裝／Loader SHA 尚未觀測。
- gstack：MIT，Codex experimental／Hermes instruction-only 支援等級須保留；W0 選 review/QA 方法，Windows 真安裝/調用由後波測，不派「全功能已載入」聲稱。


## R1｜2026-11-06 受界基準同步修訂（W0，作者端）

> 插入位置：W0 定案正文前言之後、`# CH-00` 之前。只更正受影響敘述；原句保留可見，更正置於其後。

### 1. 法位與上限

本節是**作者端修訂**（`AUTHOR_SIDE`），把 2026-11-05 定案（generation 3、`2026-11-05_r4-final-c7a91e`、sha256 `0fed31f593fd132ba4f1f2d18df89a03e22e3fbdb6a75ded8bb479f86db884b4`、2254 行）中已被 2026-11-06 Repo／PR／重算事實推翻的敘述，降回可程式核對的層級。

本節**不是**原域 Ratification、**不是** Native World Effect、**不是** Protected Checker 判決、**不是** Publisher Release、**不是** HGK Permit、**不是** 密碼學簽章、**不是** U4 原 Owner 語義核簽。原 ZIP 與歷史正文不覆寫：以 `supersedes` 串接，`rollback_ref` 指回 `0fed31f5…84b4`。

對外 claim ceiling 一律 `AUTHOR_SIDE_RECONCILED_WITH_SCOPED_HOLDS`。凡出現 `NATIVE`／`INDEPENDENT`／`PUBLISHED`／`已驗收`／`已清零`／`已解除` 而未附同 Subject／Scope 原 Reader Raw 與 Checker 判決者，即判 `CLAIM_CEILING_VIOLATION`。作者端結果、已合併 PR、sandbox 綠燈三者皆無互相升格或升格為原域完成的能力。

### 2. 受影範圍與未受影聲明

**受影**：frontmatter 的 `claim_ceiling`／`document_status`；前言「可用定案」；下游入口對 `r4-candidate-b41d2e` 的現行指標；`CH-37`／`CH-44` 段「唯一現行正文是本候選（generation 2）」；`CH-48` `H-E16` 條目同型敘述。

**未受影**：50 個 `CH` H1、22 個 `WP-FHS-*`、36 條 DAG Edge（含 `E26`）、六個 W0 Primary WP（`00/01/15/16/19/21`）及其 CH 條款、OriginalID、DesignID 卡、既有 HOLD ID 與 NEG 代碼。本輪以本檔 bytes 重算：H1 50 條、`WP-FHS-*` 22 個、Edge 列 36 條，與 `ROUND_FACTS.structural_invariants_expected` 一致。本修訂**不新增第 37 條 Edge、不新增第 23 個 WP、不刪任何 CH、不改 Primary Wave 指派**。

### 3. 逐項差額表（before → after，含出處）

| # | 受影項 | before（原文） | after（本節） | 出處（ROUND_FACTS 鍵路徑） |
|---|---|---|---|---|
| 1 | `claim_ceiling` | `OWNER_AUTHORIZED_DESIGN_FINAL_NOT_NATIVE_PERMIT` | `AUTHOR_SIDE_RECONCILED_WITH_SCOPED_HOLDS` | `non_negotiables`；`verified_local_measurements.w0_r4c_closeout` |
| 2 | `document_status` | 定案（Owner 授權可用定案） | 作者端受界同步修訂（非新定案／Native／Release） | 同上 |
| 3 | 前言「可用定案」 | 本文件為 Owner 授權之可用定案 | 作者端可用、缺口受界列管 | `verified_local_measurements.w0_r4c_closeout` |
| 4 | 現行正文身分 | generation 2、`2026-11-05_r4-candidate-b41d2e` | generation 3、`r4-final-c7a91e`（2254 行） | `sources.W0.sha256`、`sources.W0.lines` |
| 5 | 下游入口 | `INDEX_AND_MANIFEST_r4-candidate-b41d2e.md` | 以 c7a91e 封存為入口；b41d2e 降歷史父索引 | `declared_but_different_local_files.files[3]` |
| 6 | `H-E16` 條目 | 當期正文為本候選（generation 2） | 當期正文為 generation 3／c7a91e | `sources.W0.sha256` |
| 7 | SBL PR 疊層（原文無記載） | — | #41 OPEN／`dirty`／203 files／head `d10362d7`；#46 合併 `393316e2c5`；#47 合併 `8f5161a3` | `pr_states_2026_11_06_1945.SBL` |
| 8 | HOLD 帳（原文無記載） | — | R4C 封存 68 筆全 OPEN（carried 64／new 4） | `verified_local_measurements.w0_r4c_closeout` |
| 9 | 71 筆帳（原文無記載） | — | `REPORTED_BY_W1_R2_NOT_INDEPENDENTLY_REVERIFIED`；不得與 68 互抵或相加 | `verified_local_measurements.w0_final_1203_71` |

第 7～9 列是**新增事實列**，非改寫原句：W0 正文全篇無 `#41`、`#46`、`#27`、`#11`、`pyproject`、`SBOM.cdx`、`cherry`（grep 命中 0），亦無 68／71 兩本帳的筆數陳述。故只登記事實，不虛構原句。

### 4. 與四個衝突項的裁決

**D-W0-IDENTITY（自述 vs 實際 bytes）**：以 sha256 `0fed31f5…84b4`／2254 行為唯一身份。`b41d2e`（generation 2）與 r3 全部降為歷史父版本，只作 lineage；凡以 b41d2e 為「現行正文」或「現行交付清單」者一律 superseded，不得再用其 Index/Manifest 當下游入口。

**D-W0-CLOSEOUT（「可用定案」vs 68 筆 OPEN）**：不承認 closeout 已清零。本輪自原封存 `HOLD_LEDGER_CLOSEOUT.json` 重讀 68 筆、`state` 全 `OPEN`（carried 64／new 4），與宣告值一致。「可用」只解為「作者端可讀、可用於設計閱讀」；本節**不解除任何具名 HOLD**，亦不得以升版、改名或重封裝達成解除。

**D-W0-WP19（作者端 7 PASS／0 FAIL vs 原 CI ACK）**：作者端自報計數（上游轉述 7 PASS／0 FAIL）只記 `AUTHOR_SIDE`，**不是**原 CI ACK，**不是** Checker 判決；本輪未取得原始 run 輸出，標 `REPORTED_NOT_REVERIFIED`。`WP19_DONE` 維持 `HOLD`，`E26`（`WP-FHS-19→WP-FHS-14`）不放行；`E26` 只影響 W4 `WP-FHS-14` 的 Release-ready 宣告，不阻 W0 的 `SOURCE_READ`／隔離草案與其餘五個 Primary WP。

**D-W0-PR41（#41 可合併／已含入主線）**：不成立。#41 於 2026-11-06 19:45 仍 `open`、`merged=false`、`mergeable_state=dirty`、203 files、head `d10362d7`，並與已合併 #46（`393316e2c5`）在 `integrations/pipd/pyproject.toml` 與 `SBOM.cdx.json` 重疊，故不可直接合併、不可 cherry-pick。#47（`8f5161a3`）才是 SBL main 尖端；其 note 明示「合併不等於原 CaseRunner 已接收」，故 #41 日後縱合併，也不得寫成 WP19 驗收或 Native 完成。

### 5. 驗證狀態

**可重算（本輪已實作）**：本檔 sha256 與 2254 行；CH 50／WP 22／Edge 36（以本檔 bytes 重算，與預期一致）；R4C 封存 68 筆 HOLD 與 `all_open`（讀原封存 JSON，非引用舊報告）；三庫 PR 狀態、head 與 merge commit（2026-11-06 19:45 readback）。

**NOT_RUN**：原 Native E2E；Protected Checker 判決；原 Domain Reader ACK；原 CI/SupplyChain 的 `CI/License/NOTICE/SBOM` Raw readback；#41 rebase 後衝突重算與 merge；71 筆原封存（未取得原件）；W2 G2／G3／G4 native 鏈（現值 `HOLD_CANDIDATE_SOURCE_MERGED`、`SOURCE_PRESENT_NATIVE_CHAIN_NOT_QUALIFIED`、`STATIC_OWNER_ISSUER_SOD_PRESERVED_PERMIT_NOT_RUN`）。

**本節自身**：未改 code、未 commit、未 push、未開 PR、未 merge、未重封裝 ZIP。

### 6. HOLD 與 ResumePredicate（具名 Owner）

> facts 未記載人員姓名，Owner 以原 Reader／Owner **角色**具名；不得自行填入人名或冒充該角色。

| HOLD_ID | 受阻範圍 | Owner（角色） | ResumePredicate |
|---|---|---|---|
| `H-R1-IDENTITY` | b41d2e 指標與「generation 2」自述 | W0:DesignCurator＋原 L3 Pack Reader | 入口、Manifest、封存清單改指 c7a91e；`supersedes_sha256`＝`rollback_ref`＝`0fed31f5…84b4`；舊清單標 `HISTORICAL_PARENT_ONLY` |
| `H-R1-CLOSEOUT` | 68 筆 OPEN | W0:DesignCurator＋各筆原 Owner/Reader | 逐筆 `resume_predicate` 各自滿足並留 Raw；**不得整批解除** |
| `H-R1-PR41` | #41 與 #46 在 `pyproject.toml`／`SBOM.cdx.json` 重疊 | SBL PIPD 原 Repo Owner＋原 CI/SupplyChain Reader | rebase 後 `mergeable_state` 非 `dirty`；兩檔無衝突且可回退；原 CI Raw 同 CandidateSHA |
| `H-R1-WP19-CI` | WP19 原 CI ACK／`E26` 放行 | 原 CI/SupplyChain Reader → 原 release-readiness Reader | 同 CandidateSHA 之 CI receipt＋LICENSE／NOTICE／SBOM bytes/SHA＋issue_disposition |
| `H-R1-NATIVE` | Native／Independent／Release | 原 Protected Checker、原 Publisher（非本 GPT 角色） | 同 Subject／Candidate／Scope／Host／PolicyEpoch 之獨立 Verdict＋Publisher Admission |

### 7. 未宣稱清單

- 未宣稱 #41、#27、#11 已合併或含入主線：三者均 `open`（head 各 `d10362d7`、`8fb0b6e0`、`8da3cb3c`）。
- 未宣稱 #46 之後 `pyproject.toml`／`SBOM.cdx.json` 已穩定，或 #41 可 cherry-pick：兩檔正是重疊點，且 #41 現為 `dirty`。
- 未宣稱 WP19 作者端結果＝原 CI ACK，或 `E26` 可解除：`WP19_DONE=HOLD`。
- 未宣稱 68 與 71 互抵、相加或清零：68 為本輪重算且全 OPEN；71 僅 `REPORTED_BY_W1_R2`。
- 未宣稱 WP16 的 license／HostFit 欠件已解或已安裝：Default30 仍停在 `SELECTED_DESIGN`，後四段全 `NOT_OBSERVED`。
- 未宣稱任何 Native、Independent、Published、Release 或原 PIPD Compiler／HGK Issuer／Protected Checker 的新權限。

# CH-00｜正式入口、主體法位、不可降級 H1 規則

<a id="ch-00"></a>

## r4 當期 L3 合法正文｜`CH-00`：主波 W0（L2 r4 §6）
**W0 主責：單一設計閱讀入口。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：User 的 W0 文件編製命令→固定 R2 Native-first 原意、L0/L1/L2 r4 的真 bytes digest、單一 Human Owner 與本輪只允許 author-design 的 WriteSet→產 W0 L3 正文與審計附錄；受影原 Writer/Reader 不被作者層取代。
**原 Writer／Reader／Consumer／責任界線**：FHS-R00／W0 WaveCurator 唯一寫新 W0 L3 檔；原 Domain Owner/Reader 只評估各自 Scope。
**Acceptance POS**：POS：所交 L3 回鏈 L0、L1、L2 r4，50 章保持 H1 並界定作者端上限。
**Acceptance NEG／FirstFail**：NEG：以 W0 文件「定案」稱作原 PI / HGK Permit / Full Release；FirstFail=CLAIM_CEILING_VIOLATION。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-11` `L1-r4:L779` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader、Fabric FHS Navigation/Policy/FAR Reader → Original Consumer | 有權原 Writer/Owner 決定有效版本、比對 Same Scope | README／作者文件 SHA 當 Original Effective Canonical；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-001` `L1-r4:L798` | W3 | SBL Product/Kind/Host Original Consumer | 使用者可明白一個 FHS 與原三庫分工 | 舊 149 Child 直接刪除或假稱已 supersede；`DESIGN_OBLIGATION_MISSING`（若失卡） |
### 50 CH 唯一主波與讀取順序（實際 L2 r4 §6 原 50 列）
| CH | 不可降級章義 | 唯一主波 | Original Consumer/明確跨波約束 |
|---|---|---|---|
| `CH-00` | 正式入口、主體法位、不可降級 H1 規則 | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；L3 Pack Curator；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-01` | FHS 產品定位、Owner／JTBD／FUO 和非目標 | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；SBL Product/Owner；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-02` | 七大痛點、原始動機與逐產品旅程 | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；SBL Product/Owner；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-03` | 功能需求、OriginalID、強弱語義及完整不變量 | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；Original Requirement Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-04` | 31 冊 SourceFreeze、AuthorityBinding、Currentness、版本衝突 | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；Original Source Authority Reader；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-05` | U0 全位元組內容盤點：表格、負條件、Code、原版附錄 | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；Original Corpus Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-06` | U1 子要求逐義拆解：各有／分別／對應／若／不得 | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；Original Requirement Atom Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-07` | U2–U4 Crosswalk、版本去向、Owner 語義核簽與反例 | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；Original Domain Owner + Trace Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-08` | SBL SharedCore 六模組與三 SP 的完整產品鏈 | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；SBL Product/三 SP；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-09` | 八 Kind、三 Mode、四 Host、16 Moments、38 Delivery Surfaces | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Original Kind/Mode/Host Product Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-10` | 已知答案、Source-bound 檢索、FAR／知識服務 | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；FAR/G-KNOW Consumer；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-11` | TPM 三 SPEC：Product、Architecture、Program 與 18 Stage | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；SBL TPM/PIPD Intake；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-12` | PIPD 13 CLI／19 Contract Families／8 Skills 與唯一 Writer | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；Original PIPD Registry/Compiler；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-13` | Authority SourceFreeze／Profile Tailoring／原 PI 的 18 領域 | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；Original PIPD Authority/Profile/PI Writer；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-14` | PD-01..10、RepoContext Currentness、Scope 與晚綁 | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；Original PD / RepoContext Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-15` | ConstructionContract／ECP：DEV、OPS、USER、RELEASE 不混用 | **W2** | `W2_藍圖&skeleton → W2_草案 → W2_定案`；Original ECP Writer / HGK effect receiver；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-16` | 跨庫 Typed ABI、Producer→Consumer、Same Subject 交接 | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；Original ABI Consumer；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-17` | Fabric Policy／FAR／治理鏡像與 FHS 工程入口 | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；Fabric Policy Owner/Consumer；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-18` | HG-KSEOS 唯一 Native Issuer／SharedSpine／WorkID／許可 | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；HGK Original Issuer/SharedSpine；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-19` | Hermes 三 Lane、模型路由、Profiles、ActualServed | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；Hermes Original Host / Lane Reader；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-20` | Hermes Native Kanban／Delegation／Swarm／長任務編排 | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；Hermes Kanban/Delegation Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-21` | Windows Host／CLI／Plugin／Skill：安裝與實際載入三段驗收 | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Original Host Install/Loader Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-22` | Native20：現役唯一原生核心與維護權 | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；Native Owner/Registry；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-23` | Default30：默認能力、可配置佔用與 NoFit | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Default Capability/Host Owner；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-24` | Donor24：可借用外部輪子與授權條件 | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Donor License/Host Owner；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-25` | Method25：演算法／流程工具方法的原用途 | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Method Consumer；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-26` | TECH386：逐原 ID 技術功能與非降級 Disposition | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Tech Need/License/Host Owner；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-27` | SBL 50 Parent／149 Child：原生產品分母專章 | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；SBL Product Parent/Child Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-28` | R15 949 原產品原子與 B1 66／254／629 映射 | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；SBL Full Product R15 Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-29` | Kind×Mode×Host×LegacyToken 192 Cell 的原始逐格行為 | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Original Host Cell Reader；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-30` | Original 96 Oracle：Test Class×Oracle 的型別與逐格準則 | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Original Assurance Oracle Reader；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-31` | Acceptance Challenge 15 條異構 Sender→Receiver Edge | **W2** | `W2_藍圖&skeleton → W2_草案 → W2_定案`；Original Challenge/Protected Checker；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-32` | B1 120 Parent／124 Child／38 Node＝282 Case 的獨立驗收 | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Original B1 CaseRunner Reader；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-33` | B1 原 27 PI→31 PD Slot：拓撲與 Effect ECP | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Original PI/PD Slot Reader；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-34` | Portable Commander Guide A／B／C 與原 Native PLAN | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；Original Native PLAN Producer；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-35` | FHS-EXECUTE：Lease、Journal、UNKNOWN、World Reconcile | **W2** | `W2_藍圖&skeleton → W2_草案 → W2_定案`；Original HGK reducer/world reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-36` | B1 自舉與 W18：Fresh PID 普通 Goal 的第一成果 | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Hermes normal-mode Host Consumer；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-37` | Program SPEC：W0～W3、原 22 WP／36 DAG 邊及 W0-A/B | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；Original Program/WP Reader；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-38` | 最小 Native E2E、GJ01–03、Golden/V2-T 與停止規則 | **W2** | `W2_藍圖&skeleton → W2_草案 → W2_定案`；Original E2E/Golden Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-39` | 安全：SoD、Process ACL、秘鑰、原授權、Consent/Privacy | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；Original Security/Consent Owner；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-40` | 三 SPEC／PI／PD／ECP／TQAEP 對原 Reader 的交接矩陣 | **W1** | `W1_藍圖&skeleton → W1_草案 → W1_定案`；Original PIPD + affected Host Receiver；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-41` | TQAEP：POS／NEG／FirstFail／獨立 Oracle 的可執行計畫 | **W2** | `W2_藍圖&skeleton → W2_草案 → W2_定案`；Original Oracle/Protected Checker；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-42` | 來源／要求／Case／Evidence／Delivery LEDGER：一筆一真值 | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；Original Evidence Ledger/Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-43` | ClaimCeiling、測量層、Producer/Checker/Publisher 的不同責任 | **W4** | `W4_藍圖&skeleton → W4_草案 → W4_定案`；Original ClaimCeiling Owner；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-44` | CI、供應鏈、部署、Cutover、Rollback 的原服務區分 | **W4** | `W4_藍圖&skeleton → W4_草案 → W4_定案`；Original Publisher/SupplyChain Owner；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |
| `CH-45` | L0–L3 文件包、DELIVER、原 Consumer ACK 與長期可維護性 | **W4** | `W4_藍圖&skeleton → W4_草案 → W4_定案`；FHS L3 Curator + Original Domain Owner；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-46` | 成本／FinOps／KnownAnswer 復用及三種 Dogfood Loop | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Product FinOps/Dogfood Owner；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-47` | OpenSpec、gstack、Hermes 外部研究與 Build-or-Use 准入 | **W3** | `W3_藍圖&skeleton → W3_草案 → W3_定案`；Original Tech/License/Host Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-48` | 受界 ChangeSet、風險／具名 HOLD、Stop-Resume 與決策閉環 | **W0** | `W0_藍圖&skeleton → W0_草案 → W0_定案`；Affected Original Owner/FirstFail Reader；不可從該章文字直接提升原 Canonical 或 Native PASS；跨波只保留 read-only locator/受影 Consumer ACK |
| `CH-49` | 逐章正式驗收標準、H1 防壓平測試與裁決 | **W4** | `W4_藍圖&skeleton → W4_草案 → W4_定案`；Original Checker/Publisher (as affected)；當期原 Reader/Host/Checker 未 ACK 只能具名 HOLD，不能借其他波/Case 認證 |

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：Owner 啟動 W0 L3 修補後閱讀。
- **獨立輸入**：同版 L0/L1/L2 三 SHA、原 Domain Reader scope 與 W0 作者 WriteSet。
- **原有能力導向操作**：先驗版本有效性及命中 Scope；僅本 W0 Curator 寫修補正文／審計附錄。
- **可觀察輸出／First Useful Outcome**：W0 前置可重算入口與受影 Reader/HOLD。
- **原 Reader／Consumer**：W0 DraftMaker、Original Domain Owner。
- **正反驗收與 FirstFail**：POS 三 SHA+50 CH+同 W0 修補版；NEG 作者文件當原 Owner 正式批准 → CLAIM_CEILING_VIOLATION。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-00](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-00)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### W0 草案決策卡｜L3 草案的唯一法位

- **受領**：單一 Human Owner 交付「W0 草案」；分析角色 R00/R04/R27/R28 及 TPM Product/System/Program 依需求輪用，不新增 Native Principal。
- **使用順序**：R2 Native-first 設計原意 → `L0 r4` Product/Architecture/Program → `L1 r4` 50 原義章 → `L2 r4` 22 WP/36 DAG/五波 → `W0 r4` 原位條文 → 本次僅限 W0 `DraftMaker` 增補；每一條與原 Domain Effective Reader 衝突，以其所屬 Scope 的 original Reader/Owner 決定並對受影操作 `HOLD`。
- **唯一 Writer**：本草案屬 `W0:DraftMaker / AUTHOR_DESIGN_ONLY`；W0:WaveCurator 和 W0:DesignCurator 分別對應上游 skeleton 與未來定案，兩者不能由草案越權取代。SBL/PIPD/Fabric/HGK Canonical Writers、原 HGK Issuer、Protected Checker、Publisher 全部不移轉。
- **立即可合法產物**：來源唯讀清冊、隔離 Product/Architecture/Program SPEC 草案、84 張卡的追溯索引、最小的 W0-B 假設與測試設計、受影 HOLD；**不得**將其中任何物件標記成 PIPD 原編譯的 `PI-PKG/PD-PKG/ECP/TQAEP`。
- **阻斷分流**：缺 SBL 最新原 Reader → 只 HOLD 原正式升格；缺 Host ACL/Policy Epoch → 僅 HOLD 相關 world effect；SOURCE_READ 或已允許的隔離本地草稿可在權限內繼續。

**本章 POS/NEG/FirstFail**：POS 可從本草案 OriginalID 追查 31 冊 SHA、唯一主波與 Original Consumer；NEG 把作者 SHA 或 Fabric FHS-NAV/v2 當原 Owner 的 permit → `AUTHOR_AUTHORITY_ESCALATION_DENY`。Consumer：W0 DesignCurator、原 SBL Product/PIPD/Fabric/HGK 原域 Reader。Evidence：本包 Manifest/Trace；Original Owner ACK=`NOT_OBSERVED`。

# CH-01｜FHS 產品定位、Owner／JTBD／FUO 和非目標

<a id="ch-01"></a>

## r4 當期 L3 合法正文｜`CH-01`：主波 W0（L2 r4 §6）
**W0 主責：單人 Owner 的直接產品價值。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：普通 Goal「對齊來源後產三份受界 SPEC 草案」→一次取 Subject/Scope/QuestionLedger、來源 SHA→Product/Architecture/Program 三份不同 Draft；可讓 Owner 閱讀、批註、修訂，所有 Native 效果仍在受影波。
**原 Writer／Reader／Consumer／責任界線**：SBL Product/TPM 原 Reader；TPM-SP(Product/System/Program) 為作者協作，非原 Issuer。
**Acceptance POS**：POS：三 SPEC 均同 Subject、各有可取用 FUO、Owner 可逐項讀回正/負例。
**Acceptance NEG／FirstFail**：NEG：將完成三檔當最終產品 Native 閉環；FirstFail=FUO_NOT_OBSERVABLE。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-01` `L1-r4:L769` | W0 | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) | 以 Subject+Scope+SourceSHA 鍵重用 KnownAnswer/QuestionLedger，只有差額重問 | 沿用相同 SourceSHA 卻重問同一已知答案；或混同一個 Human Owner 與技術 Checker 身分；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-02` `L1-r4:L770` | W3 | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) | 保留 8 Kind/3 Mode/4 Host/3 SP/6 Module/16 Moment/GJ/OriginalID | 用 FHS 新名稱刪掉 SBL 原 Kind/Mode/Host/Moment/Child；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-03` `L1-r4:L771` | W0 | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) | 短 Goal 可產直接有用答案／SPEC，寫入則需實際 Diff/Host | 只交文件數量、沒有使用者可取用之 FUO，或冒稱 Host 已執行；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-001` `L1-r4:L798` | W3 | SBL Product/Kind/Host Original Consumer | 使用者可明白一個 FHS 與原三庫分工 | 舊 149 Child 直接刪除或假稱已 supersede；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-002` `L1-r4:L799` | W0 | Original Domain Owner/Reader (scope binding pending) | 新 PID 可取得可追溯答案 | 沒有實質效果仍建立 22WP/3 Lane；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-003` `L1-r4:L800` | W0 | Original Domain Owner/Reader (scope binding pending) | 三 SPEC 各自有 ACC/NEG/NonGoals | 三份同文換標題、自稱 PI 由 GPT 正式發布；`DESIGN_OBLIGATION_MISSING`（若失卡） |

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：普通 Goal 輸入／唯一 Human Owner。
- **獨立輸入**：goal, subject, scope, KnownAnswer, P01–P07 original trace。
- **原有能力導向操作**：PM 產 ProductSPEC、有界 FUO；SE 產 ArchitectureSPEC；TPgM 產 ProgramSPEC；不得把人類 Owner 合併為一組 OS issuer/checker credential。
- **可觀察輸出／First Useful Outcome**：三份彼此不同且可編修的 SPEC+DecisionDelta。
- **原 Reader／Consumer**：SBL Product Owner／原 PIPD Intake。
- **正反驗收與 FirstFail**：POS Owner 能逐項審 Source+ACC±；NEG 同文換標題或自簽核 → SPEC_TRACE_BROKEN。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-01](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-01)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### W0 Product SPEC｜受界第一有用結果（P.W0.PROD.001～007，作者端 ID）

| 類型 | W0 草案實質規格 | 可量測 POS | 排除 NEG／FirstFail |
|---|---|---|---|
| Persona | 唯一 Human Owner，單人本機、日常普通 Goal；模型/工具原生 Worker 是執行角色，非新的 Owner/Issuer | 不必先填完整 PIPD schema 即可取用可追溯答案或 SPEC | 要求所有短問答先開 22 WP → `FUO_BURIED_BY_PROCESS` |
| JTBD | 將普通 Goal 與已許可來源轉成可用的 source-bound SpecDelta，只有受保護世界效果才提升 Gate | `goal, affected_scope, source_refs, user_value, acceptance±` 全有 | 只輸出「已建立 30 個文件」→ `NO_USER_VALUE` |
| FUO-A | 讀取已上傳來源後，直接交付需求／風險／可行更改的帶來源回答 | 選定一段原需求能回溯 SourceSHA、Parent、NEG、Consumer | grep-only 當語義通過 → `SEMANTIC_HOLD` |
| FUO-B | 需改程式時先交 Product、Architecture、Program 三份不同 SPEC 的**草案**與最小原接收請求 | 三份互相對齊、各有 1 個對應 Original Consumer、各有 POS/NEG | 以草稿自稱 native PI 編譯完成 → `CANONICAL_WRITER_BOUNDARY` |
| MVP | W0-A 完成問題/已知答案/源索引和三 SPEC；W0-B 交付五 Seam 的預期 Input/Output、原 Receiver 和最短可測 fixture | 無 Host Raw 也能作合法 W1 文檔交接；未觀測項在 HOLD | 要求 W0 執行 GJ02 的 REPO_WRITE → `FUTURE_RECEIPT_DEPENDENCY` |
| 非目標 | 不建第二 HGK 控制層、Compiler、Queue、Independent Checker、Release Gate；不重新分配 SBL 領域正本 | 無新 SSOT/Writer/Issuer/Publisher | 任務設計到處重造周邊輪子 → `DUPLICATE_NATIVE_CAPABILITY` |
| 使用者驗收 | 使用者拿到一份能指示 W1 真接收與受影阻斷的 SPEC、下一步與退出條件 | 三 SPEC／Source index／HOLD 不互相指代成空包 | 任務僅留下一堆抽象標題 → `SPEC_NOT_ACTIONABLE` |

**輸入**：`ordinary_goal`, `source_refs[]`, `Subject/Scope`, `known_answers`, `read_acl`。**操作**：重用 QuestionLedger，以最小模式排程 source-read → product outcome → applicable cases。**輸出**：`W0_Product_SPEC_Draft`＋`SpecDelta`＋`ACC/NEG`。**消費**：原 SBL Product Reader→原 PIPD Intake (W1)，缺 original ack 則作者草案保持可讀、`ORIGINAL_SOURCE_READER_ACK_HOLD`。

# CH-02｜七大痛點、原始動機與逐產品旅程

<a id="ch-02"></a>

## r4 當期 L3 合法正文｜`CH-02`：主波 W0（L2 r4 §6）
**W0 主責：七痛點逐條產品旅程。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：保持 P01～P07 原 ID，不以「治理太重」統一壓成抽象需求；每一痛點在 ProductSPEC 對應 user action/input→原模組操作→可見 Output→原 Consumer，保留被禁止的替代行為與 FirstFail。
**原 Writer／Reader／Consumer／責任界線**：SBL Product Owner +各 Kind/Host Consumer；W3 負責全量 Kind/Moment UAT。
**Acceptance POS**：POS：可逆查七項原痛點各自的 user journey 和一項專屬負例。
**Acceptance NEG／FirstFail**：NEG：以一個「Kanban Done」證明七項獨立產品成果；FirstFail=PRODUCT_REQUIREMENT_COLLAPSE。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-002` `L1-r4:L799` | W0 | Original Domain Owner/Reader (scope binding pending) | 新 PID 可取得可追溯答案 | 沒有實質效果仍建立 22WP/3 Lane；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-004` `L1-r4:L801` | W3 | SBL Product/Kind/Host Original Consumer | 七痛點各有一個真正 UAT | 把一個 Kanban Done 當七項 PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：七個原痛點分別觸發。
- **獨立輸入**：P01 選型、P02 ABI、P03 KnownAnswer、P04 Writer、P05 Oracle、P06 Host、P07 FUO。
- **原有能力導向操作**：逐 Pxx 以原來源/同一 Subject 記 action→原 Consumer→可用輸出／專屬 NEG；同類不合併。
- **可觀察輸出／First Useful Outcome**：七張 PainCase，各自 POS+NEG+FirstFail。
- **原 Reader／Consumer**：SBL Product/Kind/Host 原 Consumer。
- **正反驗收與 FirstFail**：POS P03 同 Scope 已知答案不重問；NEG 一個 Kanban Done 宣告七痛點全 PASS → PRODUCT_REQUIREMENT_COLLAPSE。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-02](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-02)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### W0 七痛點的使用者旅程落地欄

不刪原 `P01～P07`；逐痛點必保留 `OriginalPainID/原句/來源位置/使用者場景/必要功能/禁止條件/Owner/目標波`。對 W0 直接受影者：啟動繁重→普通 Goal 直入／短答；已知答案重問→`subject+scope+sourceSHA` 命中重用；文檔生成過度→按 Effect 最小充分證據；來源失真→U0～U4 原義與 NEG 有明確未核簽狀態；無真世界閉環→先寫 W0-B 接線，不冒稱已測世界。其他痛點交至 W1～W4 主波，不在 W0 偷換驗收責任。

**原 Reader/Consumer**：SBL Product/Persona，原 Hermes Launcher／HGK Host。POS 每痛點保留針對性 FUO/Case；NEG 七個痛點全部用同一「符合需求」句子 → `PAIN_IDENTITY_FLATTENED`；證據期待 `EXPECTED_NOT_OBSERVED`。

# CH-03｜功能需求、OriginalID、強弱語義及完整不變量

<a id="ch-03"></a>

## r4 當期 L3 合法正文｜`CH-03`：主波 W0（L2 r4 §6）
**W0 主責：原身份與否定作用域。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：每條 OriginalID 僅是來源身份，不能從重名 enum 直接推相同 Parent/Child。將 Requirement 原全文／Parent／否定詞／例外／適用 Host/Mode 搭 SourceSHA、byte-span、Original Reader、原 Outcome/Oracle 記 Crosswalk；未核位置用 SOURCE_SPAN_HOLD。
**原 Writer／Reader／Consumer／責任界線**：31 冊原 Domain Writer/Reader，各失配保持 affected-scope HOLD；W0 Curator 僅登記。
**Acceptance POS**：POS：任一 OriginalID 可追到一份實體原文與專屬 Consumer 或具名 HOLD。
**Acceptance NEG／FirstFail**：NEG：將 Provider OFF token 倒轉或省略「不得」；FirstFail=NEG_SCOPE_LOSS。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-10` `L1-r4:L778` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader、Corpus Extractor + Original Domain Semantic Owner (U0–U4) | 31 冊兩 Scope、U0–U4、四表、Parent/NEG preserved | 只計 949 筆字串，漏掉 Parent NEG/例外仍宣全義接受；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-015` `L1-r4:L812` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader | 每個原 ID 有候選或具名 HOLD | 原字串關鍵字命中代 SOURCE_TRACE_PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：提取 OriginalID／來源子義。
- **獨立輸入**：SBL14/FHS17 的 original SHA, real byte span, Parent/Child/NEG/Exception/Applicability。
- **原有能力導向操作**：原文 Parent 作用域下逐 verb/Host/Mode/Condition 解多項；在原 Reader 未核之前保留候選／受影 HOLD。
- **可觀察輸出／First Useful Outcome**：`OriginalID→SpecClauseID→CaseID` trace row，所有條位有原 Consumer。
- **原 Reader／Consumer**：Original Requirement / Semantic Reader。
- **正反驗收與 FirstFail**：POS 反查 Parent+NEG；NEG 用 keyword 命中代完整 clause 或反轉 Provider OFF → ORIGINAL_ID_OR_NEG_SCOPE_LOSS。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-03](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-03)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### RequirementAtom 的不減損資料契約

每個子義務採作者側 `RequirementRef = {OriginalID, SourceID, SHA256, ByteSpan, ParentID, ChildID?, Polarity(POS|NEG), NegationScope, Condition, Exception, Applicability, OriginalConsumer, Owner, PrimaryWave, AffectedScope}`。`原句` 與 `作者歸納` 分欄；SourceSHA 必從真 source bytes 取得；缺 byte span 只允 `LOCATOR_PENDING`，不得合成假 offset。

**驗證順序**：先 `OriginalID/SourceSHA/Span` → Parent/NEG/Exception → Original Consumer → Wave/Scope → SpecClause → Case/Oracle → Expected evidence。POS 同一 Parent 下若干子條件各自能反查；NEG 拿「支援所有模式」取代各自有例外子義 → `COMPOSITE_NEGATION_LOST`。W0 只記作者候選 Identity Ledger，原 Domain Reader 的正式採納為獨立 Gate。

# CH-04｜31 冊 SourceFreeze、AuthorityBinding、Currentness、版本衝突

<a id="ch-04"></a>

## r4 當期 L3 合法正文｜`CH-04`：主波 W0（L2 r4 §6）
**W0 主責：31 原來源與當期 Effective 分離。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：對 SBL14+FHS17 各檔讀 bytes、SHA、lines；保存固定來源 snapshot manifest，另列 Currentness/原 Canonical Reader ACK、版本 supersession、SBL-hosted Writer 所在位置；只憑 SHA 不產 SourceFreezeManifest。
**原 Writer／Reader／Consumer／責任界線**：原 SBL/PIPD/Fabric/HGK Source Reader；Fabric Repo 先導航至 SBL/HGK。
**Acceptance POS**：POS：31/31 位元可重算且每件有來源檔、唯一 ID、SHA、line。
**Acceptance NEG／FirstFail**：NEG：source SHA 一致就宣稱原 Owner ratified；FirstFail=SOURCE_CURRENTNESS_HOLD。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-11` `L1-r4:L779` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader、Fabric FHS Navigation/Policy/FAR Reader → Original Consumer | 有權原 Writer/Owner 決定有效版本、比對 Same Scope | README／作者文件 SHA 當 Original Effective Canonical；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-014` `L1-r4:L811` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader | 31/31 bytes/sha 檔案映射可重算 | 只看標題/文件數就稱全部語義完成；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-020` `L1-r4:L817` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader | 新舊版本衝突不會被靜默覆蓋 | 作者端 SHA 自封 OWNER_CURRENT_CONFIRMED；`DESIGN_OBLIGATION_MISSING`（若失卡） |
### 31 冊物理 Snapshot Manifest（真實 bytes/SHA；Currentness 另外待原 Reader）
| SourceID | 原始快照檔 | Bytes | Lines | SHA-256 |
|---|---|---:|---:|---|
| `SBL-DOC-00` | `SBL_PIPD-LS-PKG_DOC-00(1).md` | 465363 | 1591 | `bd9c1a85ea0cae68fa8cde617e5592fca6123f72b4caf1a9d2894167d9a82e01` |
| `SBL-DOC-01` | `SBL_PIPD-LS-PKG_DOC-01(1).md` | 1041962 | 4938 | `43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f` |
| `SBL-DOC-02` | `SBL_PIPD-LS-PKG_DOC-02(1).md` | 1148207 | 11084 | `4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035` |
| `SBL-DOC-03` | `SBL_PIPD-LS-PKG_DOC-03(1).md` | 1704253 | 4851 | `ea69e1d3718ed86aecd74a3ebcc933960eacc30b586ab80fcb9f733037e33476` |
| `SBL-DOC-04` | `SBL_PIPD-LS-PKG_DOC-04(1).md` | 618110 | 3036 | `ee90cb1c86f6f7350c11c9c962233a89b035ca41ff82c8968f7968608fc6f6e0` |
| `SBL-DOC-05` | `SBL_PIPD-LS-PKG_DOC-05(1).md` | 2382349 | 7888 | `3b47a0b6224b1984a4047cf53aac5ac50615c93a560fea46e1b43d079a5d9f27` |
| `SBL-DOC-06` | `SBL_PIPD-LS-PKG_DOC-06(1).md` | 1554880 | 2858 | `64ea4977dab3093301f82dc7469413cc754998fc53946467842e06d83645102b` |
| `SBL-DOC-07` | `SBL_PIPD-LS-PKG_DOC-07(1).md` | 1265128 | 3620 | `a366d3783c82089c5593ffabb0704d8507632cce45622684f7a0186f2ae310f8` |
| `SBL-DOC-08` | `SBL_PIPD-LS-PKG_DOC-08(1).md` | 925526 | 11139 | `c7029c1ff07abe3135d33d3abf858a5fecedd911b494cd69c16eb1ddb8158288` |
| `SBL-DOC-09` | `SBL_PIPD-LS-PKG_DOC-09(1).md` | 904598 | 3978 | `6450f7c15915ec8b304f4e5fd4093ea707434db8bae9d2bb6e66c30ab6eed2e1` |
| `SBL-DOC-10` | `SBL_PIPD-LS-PKG_DOC-10(1).md` | 1397936 | 3888 | `a64aa21c977334dd74d660a86377ee10c4d329aa5fde0dae25ff81a3e69e8d8f` |
| `SBL-DOC-11` | `SBL_PIPD-LS-PKG_DOC-11(1).md` | 1831131 | 5005 | `12f8705d780b76f264457c194a6ff359da8d74b5d6d8c83fa245b74d2a37508e` |
| `SBL-DOC-12` | `SBL_PIPD-LS-PKG_DOC-12(1).md` | 982931 | 7940 | `d1e470d82ca14319582cb8947aa52007927aa38e726249b1430804cfe8c8ca56` |
| `SBL-DOC-13` | `SBL_PIPD-LS-PKG_DOC-13(1).md` | 1251068 | 3814 | `7cc0c8b17311130c875910b2548b93c28bd4e1c8ee04d300f85fc33d4c09beb1` |
| `FHS-BODY-00` | `00_INDEX_AND_DECISION(4).md` | 8236 | 83 | `cb4727d5b0c190aba40559f72b6989964659923eed6c27504ab62acfdc3b2635` |
| `FHS-BODY-01` | `01_PRODUCT_AUTHORITY_SPINE(4).md` | 17661 | 145 | `e257dfcd01f2e8afeda1dd88fdd33b4ef7346bf224572e60935bf9834d25b02c` |
| `FHS-BODY-02` | `02_PIPD_LIFECYCLE_AND_TPM(4).md` | 73292 | 858 | `c336d3d9d702834e84bc2e45037e21e6ac56fb99c7abcb3adea372d901824ea2` |
| `FHS-BODY-03` | `03_ARCHITECTURE_ABI_AND_EFFECT(4).md` | 12144 | 106 | `58628861e63956ae31b1ac17404c093533226688f975f5fa11b9b82adecd1284` |
| `FHS-BODY-04` | `04_FABRIC_HGK_CONTROL(4).md` | 16794 | 120 | `a7d54bdeb9129e7e1979bbc1af1944189b1054760e76424f8ffd8547a682eb1f` |
| `FHS-BODY-05` | `05_COMMANDER_GUIDE_AND_NATIVE_PLAN(3).md` | 6726 | 59 | `ee47e07455767c063fd0700440b46d27592caea4638c39407b9af1309a2b44d5` |
| `FHS-BODY-06` | `06_FHS_EXECUTE_HERMES_RUNTIME(4).md` | 16807 | 117 | `6bc5de0d26c8d13f4227ac9b48a66b808af0eb1108dc3012941e9c0c1ee362d5` |
| `FHS-BODY-07` | `07_ACCEPTANCE_CHALLENGE(4).md` | 211405 | 1370 | `81a8c2f1cc4629f59829f11f87aebd14cd57f7c4dd0970d672880e90e2899741` |
| `FHS-BODY-08` | `08_TECHNOLOGY_DEFAULT_HOTSWAP(4).md` | 1128554 | 5900 | `1df04680319796aa253256c5da9c8adea47a5601abfe17086f3598d4f0470f8d` |
| `FHS-BODY-09` | `09_SBL_DOC00_13_FULL_UPGRADE(4).md` | 300559 | 2198 | `1a0fcbdd77998bc9beed039407b96a1163c634052583813a98193f4d49769185` |
| `FHS-BODY-09A` | `09A_R15_949_ORIGINAL_ATOMS(4).md` | 1855910 | 12639 | `ce14d5d45ef76ded7cd60e4faec34119749c29fee31d9b6e1b78738179612410` |
| `FHS-BODY-09B` | `09B_KIND_MODE_HOST_192(4).md` | 474159 | 3050 | `aed2234821768307d81991aa56d5ff3a98fc9b884ff79e2930f2b9c4ae8e441d` |
| `FHS-BODY-10` | `10_B1_W18_SELF_BOOTSTRAP(4).md` | 7761 | 76 | `13b0764732bc1501e7c823b12be0d0be3a54afdaec5f77a5e90111c1947fa70a` |
| `FHS-BODY-10A` | `10A_B1_TQAEP_120_124_38(4).md` | 572218 | 8042 | `39ffde0115cdf894806a4d3bf270046b68f8786956507480db47b2a154a8c4e1` |
| `FHS-BODY-10B` | `10B_B1_PI27_PD31(4).md` | 44264 | 405 | `7c33e2472a6510a6c15b5b8eee2fca6dd9e4865c7ad3beb8c19d1e4618886f64` |
| `FHS-BODY-11` | `11_WORKPACKAGES_AND_DAG(4).md` | 46467 | 380 | `6c526c991b5996c2d4f862f153fbf580d456f78b45d2a714abe11bcb9a9cc811` |
| `FHS-BODY-12` | `12_VERIFICATION_AND_DELIVERY(4).md` | 15368 | 153 | `e4f7512a27ecbec1ce6a4569654ce33c4bf3265361a5ec141418a313fd25dd45` |

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：31 冊來源最新性判讀。
- **獨立輸入**：31 個實體 UTF-8 bytes/SHA、來源檔／Original Owner 的 Currentness probe。
- **原有能力導向操作**：作者凍結可重算 Snapshot，不代原 SourceFreeze；僅原 Reader 可判 EffectiveRevision/Supersession/PolicyEpoch。
- **可觀察輸出／First Useful Outcome**：31 份 SourceSnapshot + 需要 Reader ACK 的 Currentness Ledger。
- **原 Reader／Consumer**：原 Source/Authority Reader。
- **正反驗收與 FirstFail**：POS 31/31 本地 hash 一致；NEG 自封 SourceFreeze 或 SHA=Owner ratification → ORIGINAL_AUTHORITY_READER_UNBOUND。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-04](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-04)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### W0-A SourceManifest／AuthorityBinding 設計與原 Currentness 分離

**觸發**：需要對本機上傳版 31 冊建立可重算快照。**輸入**：每檔 `SourceID, actual bytes, SHA256, line_count, scope, original Reader locator`。**操作**：計算 SHA、檢出重複身份與版本衝突；用 `snapshot_valid` 與 `owner_currentness` 兩獨立欄位保存，`original_owner_confirmed` 預設 `NOT_OBSERVED`。**輸出**：作者端 `SourceSnapshotLedger@W0`、`AuthorityConflictLedger`、受影 `SourceFreezeRequest`；只有原 Authority Source Reader 可核定 formal freeze。

**FIRST FAIL**：快照 bytes 不吻合 → `SOURCE_SHA_MISMATCH`；當期原 Owner Reader 不可得 → `H-SRC-01` 僅 PARK scope 下游 Canonical 投影；原 Domain Reader 與 W0 作者資料衝突 → `OWNER_CURRENTNESS_HOLD`，留 both digests + supersession candidate，不用日期猜勝者。**POS**：31/31 在附錄可按同檔 byte/hash 重算；**NEG**：`sha_match==true` 就輸出正式 SourceFreezeManifest → `FREEZE_AUTHORITY_LAUNDERING`。原 Consumer：Original PIPD Source/Authority Reader／各 SBL/Fabric/HGK Domain Owner。

# CH-05｜U0 全位元組內容盤點：表格、負條件、Code、原版附錄

<a id="ch-05"></a>

## r4 當期 L3 合法正文｜`CH-05`：主波 W0（L2 r4 §6）
**W0 主責：U0 全文結構與位元邊界。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：對每個文件按 byte offset 分割 H1～H6、表列、code fence、附錄、否定、空行和原始段落；保存區間覆蓋/相鄰/不重疊不遺失斷言；目錄索引絕非已完成 U0。
**原 Writer／Reader／Consumer／責任界線**：原 Corpus Extraction 設計 Reader；Original Owner 的語義接受另行完成。
**Acceptance POS**：POS：來源 byte ranges 可覆蓋原檔且保留 SourceSpan。
**Acceptance NEG／FirstFail**：NEG：只抽 heading lines 宣稱完整 U0；FirstFail=U0_BYTE_PARTITION_INCOMPLETE。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-10` `L1-r4:L778` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader、Corpus Extractor + Original Domain Semantic Owner (U0–U4) | 31 冊兩 Scope、U0–U4、四表、Parent/NEG preserved | 只計 949 筆字串，漏掉 Parent NEG/例外仍宣全義接受；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-054` `L1-r4:L851` | W0 | Corpus Extractor + Original Domain Semantic Owner (U0–U4) | 所有非空片段有處置或 HOLD | grep/counter/SHA 當 100% 原義；`DESIGN_OBLIGATION_MISSING`（若失卡） |

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：原語義保護的 U0 位元掃描。
- **獨立輸入**：每 Source 的 raw bytes／Code/table/fence/empty/appendix/negative clause。
- **原有能力導向操作**：作者端先產 line-byte exhaustive partition，要求原 Corpus Reader 對 semantic unit 再建立 U0 parser interval coverage；不能把逐行 partition 當語義分割。
- **可觀察輸出／First Useful Outcome**：line-byte proof/expected parser records，原 Reader 未執行標 U0 SEMANTIC HOLD。
- **原 Reader／Consumer**：Original Corpus Reader。
- **正反驗收與 FirstFail**：POS raw line bytes 串回原 SHA；NEG 缺 table cell 或以 Heading 索引冒完備 → U0_SEMANTIC_PARTITION_HOLD。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-05](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-05)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### U0 位元組分割與未解析 token 的失敗封套

U0 處理「可稽內容區間」而不僅統計行數：對每份 UTF-8 檔保存 `[byte_start,byte_end)`、換行型別、檔案 SHA、表格列/程式碼區/fence/註解/歷史段狀態，原文先不改寫；每一非空內容區段必歸入 `normative_current | historical | fixture | commentary | unresolved` 之一。確認區段連續、非重疊、無未歸屬 bytes；`unresolved` 不可自動解讀為非規範。

**操作序列**：Read raw→ decode with strict UTF-8→ byte offsets→ Markdown structural map→ SourceLocator/Scope→ Parent/NEG token→ crosscheck against current original Reader→ Hash/readback。**POS**：同一 fixture 回放時無丟 byte 或改極性；**NEG**：只複製 31 檔 H1 索引便宣 U0 完整 → `U0_PARTITION_NOT_PROVEN`。W0 此輪的已實測僅 physical 31 SHA，不宣 `U0_PARTITION_CLOSED`；原 Parser/Owner 尚待正式抽取/核簽。

# CH-06｜U1 子要求逐義拆解：各有／分別／對應／若／不得

<a id="ch-06"></a>

## r4 當期 L3 合法正文｜`CH-06`：主波 W0（L2 r4 §6）
**W0 主責：U1 子義非壓平。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：對「各有／分別／對應／若／不得」按具名 subject/condition 將 Parent 句拆成原子子義；原否定/前置/例外都保留；未能確認抽取器是否正確則 SourceContextFragment HOLD。
**原 Writer／Reader／Consumer／責任界線**：原 Corpus/Requirement Writer + 各 Original Owner；W0 只製作受界提案。
**Acceptance POS**：POS：一條含正負兩條件的 Parent 可反查兩個子 claim 及共同 Parent。
**Acceptance NEG／FirstFail**：NEG：把「ON/OFF」直接轉為 provider_off Boolean 且無原 Owner ACK；FirstFail=PROVIDER_OFF_MAPPING_HOLD。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-10` `L1-r4:L778` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader、Corpus Extractor + Original Domain Semantic Owner (U0–U4) | 31 冊兩 Scope、U0–U4、四表、Parent/NEG preserved | 只計 949 筆字串，漏掉 Parent NEG/例外仍宣全義接受；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-019` `L1-r4:L816` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader | 該 Parent 子 claim 的 POS+NEG 個別讀回 | 一條統稱「支援多 Host」替代 N 條；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-054` `L1-r4:L851` | W0 | Corpus Extractor + Original Domain Semantic Owner (U0–U4) | 所有非空片段有處置或 HOLD | grep/counter/SHA 當 100% 原義；`DESIGN_OBLIGATION_MISSING`（若失卡） |

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：Parent 複合語句含各有／分別／對應／若／不得。
- **獨立輸入**：每 sentence 的 SourceSpan/ParentID, raw ON/OFF, Host/Mode/Provider, Exception。
- **原有能力導向操作**：為每個適用 Condition×Host×Operation 分立 SubclaimCandidate；負句 scope 不外溢，Original Cell Owner 未確認不把 ON/OFF 作 boolean。
- **可觀察輸出／First Useful Outcome**：可反向回 Parent 的逐子義備選＋受影 Source Hold。
- **原 Reader／Consumer**：Original Requirement Reader / Host Cell Owner。
- **正反驗收與 FirstFail**：POS 各有/分別不同 Consumer 的負例不共用；NEG 把 raw OFF 翻成 true 當正式 → PROVIDER_OFF_MAPPING_HOLD。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-06](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-06)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### U1 拆解規則與逐子義反例

遇「各有」建立每 `Kind×Host` 子義；「分別」保持獨立 Producer/Consumer；「對應」生成有向依存；「若」先存 predicate，再存 consequent；「不得」獨立 NEG 與作用域；「至少」保留 threshold 和適用 context。每個 `child` 承接父原句 source/span，不取代 Parent 的例外、版本範圍。若來源 `provider=ON/OFF` 字面與推定布林相反，保留 raw literal，進入 `H-CELL-03`；不得默改反向意思。

**POS**：同 Parent 的條件差異產生各自 TestCase/NEG；**NEG**：一條 `all_modes=true` 合併六個不同 Host 原句 → `U1_CHILD_COLLAPSE`。原 Reader：Original SBL Requirement/Kind Reader；W0 輸出是 `SubclaimLedger` 及差額，未標正式編譯器結果。

# CH-07｜U2–U4 Crosswalk、版本去向、Owner 語義核簽與反例

<a id="ch-07"></a>

## r4 當期 L3 合法正文｜`CH-07`：主波 W0（L2 r4 §6）
**W0 主責：U2–U4 雙向追蹤閉包。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：U2 原句→DesignID/CH/WP→新位置，U3 產品/架構/程式差額，U4 反向每個新規格查原 RequirementID、Parent+NEG、Original Consumer。84 筆 L2 r4 強制設計 obligation 是獨立分母，必逐項保留，不以 949/485 的數目取代。
**原 Writer／Reader／Consumer／責任界線**：原 Requirement/Design Reader 與受影 Domain Owner；W0 波次接收 84 中 W0 主責卡。
**Acceptance POS**：POS：任何 INT/FHS-DR 可由 L1-r4 原行定位、主波、專屬 POS/NEG、Consumer 到 L3。
**Acceptance NEG／FirstFail**：NEG：刪除 INT-24 或 DR-060，仍聲稱完整；FirstFail=DESIGN_OBLIGATION_MISSING。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-10` `L1-r4:L778` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader、Corpus Extractor + Original Domain Semantic Owner (U0–U4) | 31 冊兩 Scope、U0–U4、四表、Parent/NEG preserved | 只計 949 筆字串，漏掉 Parent NEG/例外仍宣全義接受；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-019` `L1-r4:L816` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader | 該 Parent 子 claim 的 POS+NEG 個別讀回 | 一條統稱「支援多 Host」替代 N 條；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-054` `L1-r4:L851` | W0 | Corpus Extractor + Original Domain Semantic Owner (U0–U4) | 所有非空片段有處置或 HOLD | grep/counter/SHA 當 100% 原義；`DESIGN_OBLIGATION_MISSING`（若失卡） |
### 84 項 L2 r4 MANDATORY_SPEC 設計卡：逐 ID 原位接線（非全量原需求替代）
| DesignID／L1 r4 實行 | 本波處置 | 原主波/WP | 不可壓平原義/受影 CH | Original Consumer | POS | NEG/FirstFail |
|---|---|---|---|---|---|---|
| `INT-01` `L1-r4:L769` | `W0_REQUIRED` | W0/`WP-FHS-15` | 單一擁有者、最少打擾；以 Subject+Scope+SourceSHA 鍵重用 KnownAnswer/QuestionLedger，只有差額重問；[CH-01](#ch-01)/[CH-10](#ch-10) | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) | 以 Subject+Scope+SourceSHA 鍵重用 KnownAnswer/QuestionLedger，只有差額重問 | 沿用相同 SourceSHA 卻重問同一已知答案；或混同一個 Human Owner 與技術 Checker 身分；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-02` `L1-r4:L770` | `W1-W4_HANDOFF` | W3/`WP-FHS-20` | 保住 SBL 獨立產品身份；保留 8 Kind/3 Mode/4 Host/3 SP/6 Module/16 Moment/GJ/OriginalID；[CH-01](#ch-01)/[CH-08](#ch-08)/[CH-09](#ch-09) | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) | 保留 8 Kind/3 Mode/4 Host/3 SP/6 Module/16 Moment/GJ/OriginalID | 用 FHS 新名稱刪掉 SBL 原 Kind/Mode/Host/Moment/Child；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-03` `L1-r4:L771` | `W0_REQUIRED` | W0/`WP-FHS-15` | 真正可用的第一成果；短 Goal 可產直接有用答案／SPEC，寫入則需實際 Diff/Host；[CH-01](#ch-01)/[CH-38](#ch-38) | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) | 短 Goal 可產直接有用答案／SPEC，寫入則需實際 Diff/Host | 只交文件數量、沒有使用者可取用之 FUO，或冒稱 Host 已執行；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-04` `L1-r4:L772` | `W0_REQUIRED` | W0/`WP-FHS-15` | 產品／Native 正交 AND；A 全量產品語義守恆；B 最短合法 Effect 路徑；[CH-15](#ch-15)/[CH-18](#ch-18)/[CH-38](#ch-38) | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、HGK Original Issuer/SharedSpine/Protected Checker Reader、Effect-specific original | A 全量產品語義守恆；B 最短合法 Effect 路徑 | 把 A 全量需求全作每次 B READ 的前置 OPS Permit；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-05` `L1-r4:L773` | `W1-W4_HANDOFF` | W1/`WP-FHS-03` | 一個 HGK 控制平面；沿用 HGK 原 WorkID/Issuer/CAS/SharedSpine/World；[CH-18](#ch-18) | HGK Original Issuer/SharedSpine/Protected Checker Reader | 沿用 HGK 原 WorkID/Issuer/CAS/SharedSpine/World | 生成第二 HGK Issuer／Queue／SharedSpine；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-06` `L1-r4:L774` | `W1-W4_HANDOFF` | W1/`WP-FHS-05` | 一個現役 PIPD Compiler Writer；SBL integrations/pipd 13 CLI／19 families／8 skills，薄 Adapter；[CH-12](#ch-12)/[CH-13](#ch-13) | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | SBL integrations/pipd 13 CLI／19 families／8 skills，薄 Adapter | 將歷史 PIPD-LS-SP 當現役唯一 Writer，或技能自行簽 PI；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-07` `L1-r4:L775` | `W1-W4_HANDOFF` | W1/`WP-FHS-04` | 低阻力優先既有輪子；Hermes Direct/Delegation/Kanban/Swarm 按複雜度選擇，NoFit 才補；[CH-20](#ch-20)/[CH-23](#ch-23)/[CH-47](#ch-47) | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer、Original Tech/License/Host/Method Owner → Capability Consumer | Hermes Direct/Delegation/Kanban/Swarm 按複雜度選擇，NoFit 才補 | 沒查現有 Hermes 能力便重造 Scheduler/Router；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-08` `L1-r4:L776` | `W1-W4_HANDOFF` | W2/`WP-FHS-08` | 可恢復長任務；原 Kanban 狀態+WorkID/TaskID 對應+checkpoint、受影 Reconcile；[CH-35](#ch-35)/[CH-36](#ch-36) | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 原 Kanban 狀態+WorkID/TaskID 對應+checkpoint、受影 Reconcile | 重啟後遺失 WorkID/Journal，要求 Owner 重新交代長任務；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-09` `L1-r4:L777` | `W1-W4_HANDOFF` | W2/`WP-FHS-08` | 確定性世界效果；原 HGK 應用權限與 World Reader reconcile before retry；[CH-15](#ch-15)/[CH-35](#ch-35) | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer、E | 原 HGK 應用權限與 World Reader reconcile before retry | UNKNOWN 未 World Reconcile 即同 OperationID 盲重試；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-10` `L1-r4:L778` | `W0_REQUIRED` | W0/`WP-FHS-01` | 來源／契約語義無聲漏失為零；31 冊兩 Scope、U0–U4、四表、Parent/NEG preserved；[CH-03](#ch-03)/[CH-05](#ch-05)/[CH-06](#ch-06)/[CH-07](#ch-07) | SBL Original Source/Requirement/Corpus Semantic Reader、Corpus Extractor + Original Domain Semantic Owner (U0–U4) | 31 冊兩 Scope、U0–U4、四表、Parent/NEG preserved | 只計 949 筆字串，漏掉 Parent NEG/例外仍宣全義接受；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-11` `L1-r4:L779` | `W0_REQUIRED` | W0/`WP-FHS-00` | Owner/Reader／權威逐域維持；有權原 Writer/Owner 決定有效版本、比對 Same Scope；[CH-00](#ch-00)/[CH-04](#ch-04)/[CH-17](#ch-17) | SBL Original Source/Requirement/Corpus Semantic Reader、Fabric FHS Navigation/Policy/FAR Reader → Original Consumer | 有權原 Writer/Owner 決定有效版本、比對 Same Scope | README／作者文件 SHA 當 Original Effective Canonical；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-12` `L1-r4:L780` | `W0_REQUIRED` | W0/`WP-FHS-15` | 三 SPEC 具體可操作；PM JTBD/FUO；SE ADR/ABI；TPgM DAG/Exit；[CH-11](#ch-11) | Original Domain Owner/Reader (scope binding pending) | PM JTBD/FUO；SE ADR/ABI；TPgM DAG/Exit | 三 SPEC 同文換標題或沒有不同 Consumer/ACC；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-13` `L1-r4:L781` | `W1-W4_HANDOFF` | W1/`WP-FHS-05` | PIPD PI/PD/ECP/TQAEP 分層；PI source-bound，PD 晚綁 Repo，ECP 非 Admission，TQAEP 依 Original Oracle；[CH-12](#ch-12)/[CH-13](#ch-13)/[CH-14](#ch-14)/[CH-15](#ch-15)/[CH-41](#ch-41) | SBL RepoContext/PD Reader → HGK Original Issuer → Repo World Reader、SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、Original Domai | PI source-bound，PD 晚綁 Repo，ECP 非 Admission，TQAEP 依 Original Oracle | ECP intent 冒 Issuer Permit；PD 未 live RepoContext 即號稱已綁；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-14` `L1-r4:L782` | `W1-W4_HANDOFF` | W1/`WP-FHS-11` | 四 Host 正交可用；各 Host 按本地能力與 Loader 獨立 Install/Invoke/Uninstall；[CH-09](#ch-09)/[CH-21](#ch-21)/[CH-29](#ch-29) | SBL Product/Kind/Host Original Consumer、SBL Product Owner → CLI Host Consumer、SBL Product Owner → Original Skill/Agent Host Registry Consumer、SBL Orig | 各 Host 按本地能力與 Loader 獨立 Install/Invoke/Uninstall | 一個 Host 的 CLI PASS 當四 Host Skill/Agent 都已 Qualify；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-15` `L1-r4:L783` | `W1-W4_HANDOFF` | W2/`WP-FHS-09` | 可防虛假 PASS；POS/NEG/Case/Raw/SourceSHA，符合原 Principal 差異；[CH-38](#ch-38)/[CH-41](#ch-41)/[CH-43](#ch-43) | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer、Original Oracle/Protected Checker Reader | POS/NEG/Case/Raw/SourceSHA，符合原 Principal 差異 | Maker 自簽 Independent、沒有實際 Runner Raw 卻宣 PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-16` `L1-r4:L784` | `W1-W4_HANDOFF` | W3/`WP-FHS-13` | 選型不丟給 Owner；Need→Occupant→Qualified EffectiveLoad→Consumer→Retire；[CH-22](#ch-22)/[CH-23](#ch-23)/[CH-24](#ch-24)/[CH-25](#ch-25)/[CH-26](#ch-26)/[CH-47](#ch-47) | SBL Original Source/Requirement/Corpus Semantic Reader、Original Tech/License/Host/Method Owner → Capability Consumer | Need→Occupant→Qualified EffectiveLoad→Consumer→Retire | 只讀 485 身份卡便強制安裝 485 件或把必備 Default 改 OPTIONAL；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-17` `L1-r4:L785` | `W1-W4_HANDOFF` | W3/`WP-FHS-20` | 有用且可逆的 CLI/Skill/Plugin；GJ01 clean CLI、GJ02 bounded patch、GJ03 live skill invoke；[CH-09](#ch-09)/[CH-21](#ch-21)/[CH-38](#ch-38) | SBL Product/Kind/Host Original Consumer、SBL Product Owner → CLI Host Consumer、SBL Product Owner → Original Skill/Agent Host Registry Consumer | GJ01 clean CLI、GJ02 bounded patch、GJ03 live skill invoke | GJ01 只有 SPEC、GJ02 缺 Repo Diff、GJ03 只有 Resume；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-18` `L1-r4:L786` | `W0_REQUIRED` | W0/`WP-FHS-15` | 恰好安全，非全面發行治理；六類 Effect 對應最低充分原 Evidence；[CH-15](#ch-15)/[CH-39](#ch-39)/[CH-43](#ch-43) | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、HGK Original Issuer/SharedSpine/Protected Checker Reader、Effect-specific original | 六類 Effect 對應最低充分原 Evidence | 缺 OPS/RELEASE Permission 使合法 READ/DRAFT 全域停工；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-19` `L1-r4:L787` | `W1-W4_HANDOFF` | W2/`WP-FHS-18` | 研究可導入但有原消費者；FAR Typed Envelope／R8 Consumer ACK/NACK；[CH-10](#ch-10)/[CH-17](#ch-17)/[CH-40](#ch-40) | Fabric FHS Navigation/Policy/FAR Reader → Original Consumer、Original Program/DAG/Delivery Consumer | FAR Typed Envelope／R8 Consumer ACK/NACK | 研究文章／FAR Finding 無原 R8 Consumer ACK 卻宣 policy 已落地；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-20` `L1-r4:L788` | `W1-W4_HANDOFF` | W3/`WP-FHS-13` | 升級可退場且舊有效功能不回歸；Callgraph 等價+Consumer 轉交+受影 POS/NEG+Rollback；[CH-23](#ch-23)/[CH-24](#ch-24)/[CH-44](#ch-44) | Original Tech/License/Host/Method Owner → Capability Consumer、Original Program/DAG/Delivery Consumer | Callgraph 等價+Consumer 轉交+受影 POS/NEG+Rollback | 未驗 Caller/Consumer 等價便刪舊技術，HotSwap 後不可回退；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-21` `L1-r4:L789` | `W1-W4_HANDOFF` | W2/`WP-FHS-04` | 真正模型服務與政策吻合；Requested/Required/Selected/Spawn/Protocol/ActualServed/Usage；[CH-19](#ch-19) | Original Domain Owner/Reader (scope binding pending)、Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | Requested/Required/Selected/Spawn/Protocol/ActualServed/Usage | Selected model 存在但沒有 Request/Transport/ActualServed Raw 即宣 Served；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-22` `L1-r4:L790` | `W1-W4_HANDOFF` | W3/`WP-FHS-12` | W18 普通 Goal 無長 Prompt 綁架；Fresh PID 正常 Goal/Task/E33–E42/合法退出；[CH-36](#ch-36)/[CH-38](#ch-38) | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | Fresh PID 正常 Goal/Task/E33–E42/合法退出 | W18 用 B1 長 Prompt 或測試專用 Profile 冒真普通 Goal；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-23` `L1-r4:L791` | `W0_REQUIRED` | W0/`WP-FHS-00` | 所有工作包不因重分波改身份；保留 WP-FHS-00..21；WP15 先讀草稿，WP06 受護後做；[CH-37](#ch-37) | Original FHS BODY-11 Program/DAG Reader → L2 Planner | 保留 WP-FHS-00..21；WP15 先讀草稿，WP06 受護後做 | 改動依賴邊或 Scheduled 當 Done，WP17↔WP06 造成環；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-24` `L1-r4:L792` | `W1-W4_HANDOFF` | W1/`WP-FHS-16` | OpenSpec/gstack 是方法而非再一套法定流程；OpenSpec proposal/validate；gstack review/QA 轉原 Consumer；[CH-47](#ch-47) | Original Tech/License/Host/Method Owner → Capability Consumer | OpenSpec proposal/validate；gstack review/QA 轉原 Consumer | OpenSpec/gstack 自發 Canonical PI/Independent Verdict/Publisher Release；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-001` `L1-r4:L798` | `W1-W4_HANDOFF` | W3/`WP-FHS-20` | 產品與身份／A＋B；維持 FHS 是整合性產品；SBL 原產品不被廢棄；FHS-MSC 是工程歷史；讀原 Domain Effective Writer 與 FHS Source Identity；所有新名稱只作別名；[CH-01](#ch-01)/[CH-00](#ch-00) | SBL Product/Kind/Host Original Consumer | 使用者可明白一個 FHS 與原三庫分工 | 舊 149 Child 直接刪除或假稱已 supersede；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-002` `L1-r4:L799` | `W0_REQUIRED` | W0/`WP-FHS-15` | 使用者入口／B/READ；Goal 不需先選九個 MissionOptions 或填完整 PIPD Schema；直接 Hermes Session/SOURCE_READ 或合法短答；[CH-01](#ch-01)/[CH-02](#ch-02) | Original Domain Owner/Reader (scope binding pending) | 新 PID 可取得可追溯答案 | 沒有實質效果仍建立 22WP/3 Lane；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-003` `L1-r4:L800` | `W0_REQUIRED` | W0/`WP-FHS-15` | 使用者入口／B/SPEC；模糊 Goal 可以進三 SPEC，來源缺件只保留受影 Need；TPM product/system/program 用 Source+KnownAnswer 產三份不同規格；[CH-11](#ch-11)/[CH-01](#ch-01) | Original Domain Owner/Reader (scope binding pending) | 三 SPEC 各自有 ACC/NEG/NonGoals | 三份同文換標題、自稱 PI 由 GPT 正式發布；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-004` `L1-r4:L801` | `W1-W4_HANDOFF` | W3/`WP-FHS-20` | 產品／A；全部原七痛點的使用者結果個別可反證；P01–P07 每個需 source-bound 工作流/Consumer/NEG；[CH-02](#ch-02) | SBL Product/Kind/Host Original Consumer | 七痛點各有一個真正 UAT | 把一個 Kanban Done 當七項 PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-005` `L1-r4:L802` | `W1-W4_HANDOFF` | W3/`WP-FHS-20` | 產品／A；保留八 Kind 原義，不強制八種同時開啟；按 Kind→Host→Effect 能力分別產可用 Artifact 或 NoFit；[CH-09](#ch-09) | SBL Product/Kind/Host Original Consumer | 至少受影 Kind 真能被原 Host 消費 | 以 CLI 例子驗收 PLUGIN/AI_SYSTEM；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-006` `L1-r4:L803` | `W1-W4_HANDOFF` | W3/`WP-FHS-20` | 產品／A＋B；三 Mode 的效果權限保持正交；STANDALONE/PREW3_SHADOW/SWOF_CONNECTED 的 Gate 分別查核；[CH-09](#ch-09)/[CH-15](#ch-15) | SBL Product/Kind/Host Original Consumer | 合法本地效果可做、Shadow無Effect、Connected要真ACK | 字串 Mode 覆蓋原 HGK 許可；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-007` `L1-r4:L804` | `W1-W4_HANDOFF` | W1/`WP-FHS-11` | 產品／A；四 Host 各有獨立 Loader/Capabilities/NEG；Hermes/Codex/Claude/ChatGPT 原 Host 原 Process/Tool 查 readback；[CH-09](#ch-09)/[CH-21](#ch-21) | SBL Product/Kind/Host Original Consumer | 不同 Host 的實際 Trigger/Uninstall | 把在 ChatGPT 生成草稿稱 Windows 已完成；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-008` `L1-r4:L805` | `W1-W4_HANDOFF` | W1/`WP-FHS-07` | 產品／A；三 SP 均保留 Portable/Native 對照而不混權限；TPM/Commander/Challenge 各自讀合法原 Consumer；[CH-08](#ch-08)/[CH-11](#ch-11)/[CH-34](#ch-34) | SBL Product/Kind/Host Original Consumer | 同 WorkID/Source/Case 的適用讀回 | 任一 Portable Skill 自行發 Grant/Checker；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-009` `L1-r4:L806` | `W1-W4_HANDOFF` | W3/`WP-FHS-20` | 產品／A；六個 Shared Core Modules 的原功能與拒絕碼不能無聲遺失；Goal→Spec→Route→Bridge→Verify→Repair 原模組 map；[CH-08](#ch-08) | SBL Product/Kind/Host Original Consumer | 真原 ProductKind 得到受界成果 | 改成自造 FHS 全域 AgentOS 取代 SBL Core；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-010` `L1-r4:L807` | `W1-W4_HANDOFF` | W3/`WP-FHS-20` | 產品／A；16 User Moments 仍是原產品體驗選項與累進契約；M00–M15 逐項保存 Trigger/Output/Original Oracle；[CH-09](#ch-09) | SBL Product/Kind/Host Original Consumer | 受影 Moment 各有 FirstFail/exit | 將 16 Moment 視為每個 B Goal 全部必經；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-011` `L1-r4:L808` | `W1-W4_HANDOFF` | W3/`WP-FHS-20` | 產品／A＋B；GJ01 CLI 的 clean install/use/uninstall 可在真 Host 驗證；CLI 有 entrypoint/help/JSON/nonzero、foreign data 免疫；[CH-21](#ch-21)/[CH-38](#ch-38) | SBL Product Owner → CLI Host Consumer | 實際 clean Host 操作與退出 | README-only/假退出碼/錯誤清除外來檔；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-012` `L1-r4:L809` | `W1-W4_HANDOFF` | W2/`WP-FHS-06` | 產品／A/W0-B；GJ02 Brownfield patch 受限 WriteSet/Preimage/HEAD；真 RepoContext/PD/DEV ECP/原 HGK Grant 之後才 mutate；[CH-14](#ch-14)/[CH-15](#ch-15)/[CH-38](#ch-38) | SBL RepoContext/PD Reader → HGK Original Issuer → Repo World Reader | 原 Repo Raw/小 diff/test/revert | stale HEAD/skip preimage/wildcard WriteSet；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-013` `L1-r4:L810` | `W1-W4_HANDOFF` | W3/`WP-FHS-11` | 產品／A；GJ03 Portable Skill/Agent 遵循有效載入/觸發/卸載；Host skill loader pin、trigger/nontrigger tests；[CH-21](#ch-21)/[CH-38](#ch-38) | SBL Product Owner → Original Skill/Agent Host Registry Consumer | Host 真 Invoked + Unloaded | 單 ZIP 存在即宣稱已用；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-014` `L1-r4:L811` | `W0_REQUIRED` | W0/`WP-FHS-00` | 資料與來源／A；31 冊原位身份與 31 snapshot sha 不丟失；兩 Scope SBL14/FHS17，4表 U0–U4；[CH-04](#ch-04) | SBL Original Source/Requirement/Corpus Semantic Reader | 31/31 bytes/sha 檔案映射可重算 | 只看標題/文件數就稱全部語義完成；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-015` `L1-r4:L812` | `W0_REQUIRED` | W0/`WP-FHS-01` | 資料與來源／A；每個原 Parent/Child/NEG/Exception/Applicability 必保存；Source span/Parent Context/OriginalID/OriginalOwner/Consumer Crosswalk；[CH-03](#ch-03)/[CH-27](#ch-27) | SBL Original Source/Requirement/Corpus Semantic Reader | 每個原 ID 有候選或具名 HOLD | 原字串關鍵字命中代 SOURCE_TRACE_PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-016` `L1-r4:L813` | `W1-W4_HANDOFF` | W3/`WP-FHS-10` | 資料與來源／A；949 R15 原子不因 B1 受影集而消失；原 66/254/629 B1 投影與 949 Full Product 各自保留；[CH-28](#ch-28) | SBL Original Source/Requirement/Corpus Semantic Reader | Full Product 949 身分另帳清晰 | 把 B1 PASS 宣稱 949 全驗收；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-017` `L1-r4:L814` | `W1-W4_HANDOFF` | W3/`WP-FHS-20` | 資料與來源／A；192 Kind×Mode×Host×legacy token 逐 Cell 適用性；每 Cell 原 ON/OFF 文字原值不擅自推 ProviderOff；[CH-29](#ch-29) | SBL Original Source/Requirement/Corpus Semantic Reader | 每 Cell 適用/NoFit/原 Reader | 把 Legacy OFF 簡單等同 Provider disabled；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-018` `L1-r4:L815` | `W1-W4_HANDOFF` | W3/`WP-FHS-16` | 資料與來源／A；485 來源資產槽保留五正交集合並去 Occupant 重複；Native20+Default30+Donor24+Method25+TECH386；[CH-22](#ch-22)/[CH-23](#ch-23)/[CH-24](#ch-24)/[CH-25](#ch-25)/[CH-26](#ch-26) | SBL Original Source/Requirement/Corpus Semantic Reader | 原 Slot 的 OriginalDisposition/NoFit 皆可讀 | 建立 485 安裝任務；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-019` `L1-r4:L816` | `W0_REQUIRED` | W0/`WP-FHS-01` | 資料與來源／A；複合「各有/分別/對應」依原作用域拆需求；每個 actor/Host/Effect/Consumer 出候選 subclaim，Parent 保留；[CH-06](#ch-06)/[CH-07](#ch-07) | SBL Original Source/Requirement/Corpus Semantic Reader | 該 Parent 子 claim 的 POS+NEG 個別讀回 | 一條統稱「支援多 Host」替代 N 條；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-020` `L1-r4:L817` | `W0_REQUIRED` | W0/`WP-FHS-00` | 資料與來源／A；來源 Currentness 由原有權 Reader 讀回；SourceBytesSHA≠Owner EffectiveRevision；unknown→affected HOLD；[CH-04](#ch-04) | SBL Original Source/Requirement/Corpus Semantic Reader | 新舊版本衝突不會被靜默覆蓋 | 作者端 SHA 自封 OWNER_CURRENT_CONFIRMED；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-021` `L1-r4:L818` | `W0_REQUIRED` | W0/`WP-FHS-15` | PIPD/TPM／A＋B/SPEC；Portable TPM 能以 PM/SE/TPgM 產三獨立 SPEC；JTBD/FUO；ADR/ABI；DAG/Exit/Resume；[CH-11](#ch-11) | Original Domain Owner/Reader (scope binding pending) | 各 SPEC 有原來源和非目標 | 三職能被當三個獨立 Principal；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-022` `L1-r4:L819` | `W0_REQUIRED` | W0/`WP-FHS-15` | PIPD/TPM／A；18 Stage/K0–K3 及原問題去重仍遵守；Reader只按受影 Stage 取得 source/QuestionLedger；[CH-11](#ch-11) | Original Domain Owner/Reader (scope binding pending) | 當次階段結果可原位交下游 | 把階段文章當出現已完成事件；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-023` `L1-r4:L820` | `W1-W4_HANDOFF` | W1/`WP-FHS-01` | PIPD/TPM／A；SourceFreeze 由原 PIPD/Source Reader 綁定；source family sha/locator/authority/conflict；[CH-13](#ch-13) | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | 不合格來源受影 HOLD | 用 MD metadata 的 approved 字樣繞 Reader；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-024` `L1-r4:L821` | `W1-W4_HANDOFF` | W1/`WP-FHS-05` | PIPD/TPM／A；PI 保留 OriginalID/ClauseSHA/Parent/POS/NEG/Oracle/FUO；由 SBL integrations/pipd 正式 Writer 編譯；[CH-13](#ch-13) | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | 原 PIPD Reader 實收／錯誤有型別 | GPT 生成 JSON 假裝正式 PI；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-025` `L1-r4:L822` | `W1-W4_HANDOFF` | W1/`WP-FHS-05` | PIPD/TPM／A/W0-B；PD 是來源穩定 PI 對真 RepoContext 的 late binding；Repo HEAD/index/untracked/Preimage/WriteSet 與 Scope；[CH-14](#ch-14) | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | Repo drift 只重綁受影部分 | 未知 Repo 強行出有權 PD；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-026` `L1-r4:L823` | `W1-W4_HANDOFF` | W1/`WP-FHS-05` | PIPD/TPM／A/W0-B；DEV/OPS/USER 等 Effect-specific ECP 不可充 Permit；ConstructionContract/ECP 計畫／受權 Gateway 分離；[CH-15](#ch-15) | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | 有界許可後讀真 World/Repo | 無 Effect Authorization 自行 Apply；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-027` `L1-r4:L824` | `W1-W4_HANDOFF` | W1/`WP-FHS-05` | PIPD/TPM／A；TQAEP/19 Schema/13 CLI/8 Skill 原 ABI 不私改；以實際 Canonical Pipeline 與 installed Reader 判斷；[CH-12](#ch-12)/[CH-41](#ch-41) | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | Case 有正負例和待原 Checker 收據 | 不核 ABI 就加 compile-cc 14th verb；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-028` `L1-r4:L825` | `W1-W4_HANDOFF` | W1/`WP-FHS-10` | PIPD/TPM／A；B1 PI27→PD31 是分裂映射，不能一比一湊數；逐 31 edge 保留來源與適用 Effect；[CH-33](#ch-33) | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | 原 Reader 能追每條細分 PD | 只記 27 PI ID 便宣稱全 PD 完成；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-029` `L1-r4:L826` | `W1-W4_HANDOFF` | W1/`WP-FHS-00` | 治理／A＋B；Fabric FHS-NAV/v2 是唯一跨庫導航入口且唯讀；先 Fabric FHS README/map，再 SBL/HGK 原域 Reader；[CH-17](#ch-17) | Fabric FHS Navigation/Policy/FAR Reader → Original Consumer | 三庫各自 bounded PR/source fact | 導航 metadata 被當授權來源；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-030` `L1-r4:L827` | `W1-W4_HANDOFF` | W1/`WP-FHS-02` | 治理／A＋B；Fabric Policy/FAR 原 Reader/Consumer 可實際回讀；PolicyEpoch/RequiredSet/Producer/Original R8 Consumer ACK；[CH-17](#ch-17)/[CH-40](#ch-40) | Fabric FHS Navigation/Policy/FAR Reader → Original Consumer | R8 真 ACK 不被研究文件代替 | 工具回應被視為 Policy Applied；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-031` `L1-r4:L828` | `W1-W4_HANDOFF` | W1/`WP-FHS-03` | 治理／B/PROTECTED；HGK 是唯一 Work/Issuer/SharedSpine/World 權威；原 WorkID/Scope/TTL/Nonce/CAS 與有效 OS ACL；[CH-18](#ch-18) | HGK Original Issuer/SharedSpine/Protected Checker Reader | 真原 Issuer admission + world state | Human Owner 只有一人→普通 Agent 有 admin Token；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-032` `L1-r4:L829` | `W1-W4_HANDOFF` | W1/`WP-FHS-03` | 治理／B/PROTECTED；不同技術 Principal 不能被 GPT persona 假造；runtime user SID 與維護 Token 實際隔離；[CH-18](#ch-18)/[CH-39](#ch-39) | HGK Original Issuer/SharedSpine/Protected Checker Reader | 直接修改 HGK 的一般 Profile 被拒 | 兩個 Hermes Profile 名稱即宣稱 OS 隔離；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-033` `L1-r4:L830` | `W1-W4_HANDOFF` | W2/`WP-FHS-09` | 治理／A＋B；Maker 不能受保護地自驗收或自發行；Original Oracle/Raw/Same Subject＋different Checker principal；[CH-39](#ch-39)/[CH-43](#ch-43) | HGK Original Issuer/SharedSpine/Protected Checker Reader | 獨立驗收只有相應原授權主體可出 | 雙 GPT review 冒 Independent；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-034` `L1-r4:L831` | `W1-W4_HANDOFF` | W1/`WP-FHS-00` | 治理／A；三庫更改各自 branch→PR/verified original HEAD；不可跨 Repo 一個隱形 Commit；[CH-14](#ch-14)/[CH-44](#ch-44) | Original Domain Owner/Reader (scope binding pending) | 相應 PR 有真變更與可回退提交 | 憑本檔直接覆寫 main/force push；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-035` `L1-r4:L832` | `W1-W4_HANDOFF` | W1/`WP-FHS-04` | Runtime／B/LONG；Hermes v0.22.5 原能力優先使用；Direct→Delegate→Kanban→Swarm 依複雜度決定；[CH-19](#ch-19)/[CH-20](#ch-20) | Original Domain Owner/Reader (scope binding pending) | 真 task result 有再續工 | 簡單 Read 任務硬套多 Agent Queue；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-036` `L1-r4:L833` | `W1-W4_HANDOFF` | W1/`WP-FHS-04` | Runtime／A＋B；3 正式 Lane 的模型 RequiredSet/Served 分開；PLAN/EXECUTE/VERIFY_SECURITY 受原有效 Policy 選模；[CH-19](#ch-19) | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 同 Subject 每 Lane 真 Request/Served/Usage | 只選到 Picker 便宣稱 Protected Lane Served；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-037` `L1-r4:L834` | `W1-W4_HANDOFF` | W2/`WP-FHS-08` | Runtime／B/LONG；Kanban Worker 結果必看 Prompt delivery/LLM request；worker_bound/pid/module origin/API Mode/actual result 分層；[CH-20](#ch-20) | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 有 Prompt Delivered 和模型實際請求 | Windows issue #146955 型 worker bound/no prompt 仍 Done；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-038` `L1-r4:L835` | `W1-W4_HANDOFF` | W2/`WP-FHS-08` | Runtime／B/LONG；Managed Worker frozen Profile boundary 不可繞；跨 Profile delegate 不許則改原生分卡；[CH-19](#ch-19)/[CH-20](#ch-20) | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 用合法卡路由完成分工 | 直接讀另一 Profile secrets 破壞 snapshot；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-039` `L1-r4:L836` | `W1-W4_HANDOFF` | W2/`WP-FHS-08` | Runtime／B/LONG；未知世界效果先原 World reconcile，禁止盲 retry；OperationID/lease fence/World Reader/next safe step；[CH-35](#ch-35) | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | no double settlement+有效 replay cap | 同 nonce/未知外部作用重播；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-040` `L1-r4:L837` | `W1-W4_HANDOFF` | W2/`WP-FHS-08` | Runtime／B/LONG；無人值守長任務須有 stop-loss/budget/resume；owner scope、timeout、budget、retry cap、cursor；[CH-20](#ch-20)/[CH-35](#ch-35)/[CH-46](#ch-46) | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 任務能 Crash 恢復且有界停損 | 無限回圈/4h 乾等/無 FirstFail；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-041` `L1-r4:L838` | `W1-W4_HANDOFF` | W3/`WP-FHS-12` | Runtime／A/W18；普通 Goal Fresh PID 不依賴 B1 長 Prompt；W18/E33–E42 自然入口；[CH-36](#ch-36) | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 不貼 B1 指令也能執行合法任務 | B1 mock 主機結果當 W18 normal pass；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-042` `L1-r4:L839` | `W1-W4_HANDOFF` | W1/`WP-FHS-13` | 工具／A＋B；Need→Existing Capability→Occupant→Loaded/Used→Consumer；OriginalDisposition/License/Pin/NoFit/Backout 各槽；[CH-22](#ch-22)/[CH-23](#ch-23)/[CH-47](#ch-47) | Original Tech/License/Host/Method Owner → Capability Consumer | 需求由已合格工具解決 | 用外部宣傳文即自稱 loaded；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-043` `L1-r4:L840` | `W1-W4_HANDOFF` | W1/`WP-FHS-16` | 工具／B/SPEC；OpenSpec 只作 Brownfield SpecDelta/Proposal/Validate 方法；避免第二 PIPD compiler/strict $id；[CH-47](#ch-47) | Original Tech/License/Host/Method Owner → Capability Consumer | 規格差額轉原 SBL/PIPD Reader | OpenSpec archive 即原 Owner Ratified；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-044` `L1-r4:L841` | `W1-W4_HANDOFF` | W1/`WP-FHS-16` | 工具／B/VERIFY；gstack Review/QA/Investigate 只作可追 advisory；Windows minimal support 認清，Host probe first；[CH-31](#ch-31)/[CH-47](#ch-47) | Original Tech/License/Host/Method Owner → Capability Consumer | 原 Runner 能重現 QA Finding | gstack /ship 被當原 Publisher / Independent；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-045` `L1-r4:L842` | `W1-W4_HANDOFF` | W3/`WP-FHS-13` | 工具／A；技術退場須 Callgraph 同等功能/原 Consumer/NEG/rollback；先視證後保守處置與 restore；[CH-24](#ch-24)/[CH-44](#ch-44) | Original Tech/License/Host/Method Owner → Capability Consumer | 旧有效功能不能回歸 | 未測就刪 HGK 已用控制面；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-046` `L1-r4:L843` | `W0_REQUIRED` | W0/`WP-FHS-00` | 效力／驗收／B/READ；SOURCE_READ 只需合法來源/ACL/Locator/SourceSHA；合法 answer + Source readback；[CH-15](#ch-15) | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 短 READ 有用結果 | 因缺 OPS/RELEASE 全系統停工；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-047` `L1-r4:L844` | `W0_REQUIRED` | W0/`WP-FHS-15` | 效力／驗收／B/DRAFT；LOCAL_DRAFT_WRITE 需隔離 output root/原文未修改；只產候選、可重算/刪除；[CH-15](#ch-15) | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 真檔案來源/字元編碼/Readback | Draft 檔案冒 Canonical Product；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-048` `L1-r4:L845` | `W1-W4_HANDOFF` | W2/`WP-FHS-06` | 效力／驗收／B/DEV；REPO_WRITE/DEV 必有完整 Repo/WriteSet/DEV ECP/原 Permit；真 Diff/Test/Rollback Raw；[CH-14](#ch-14)/[CH-15](#ch-15) | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 可逆最小 Patch | 自造 universal write permission；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-049` `L1-r4:L846` | `W1-W4_HANDOFF` | W2/`WP-FHS-17` | 效力／驗收／B/OPS；HOST_OPERATION 要有真 Host SID/Trust/OPS ECP/World Reader；Host state before/after；[CH-15](#ch-15)/[CH-21](#ch-21) | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 適用 Host 操作真的生效 | Git rollback 冒 Host 世界回復；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-050` `L1-r4:L847` | `W1-W4_HANDOFF` | W2/`WP-FHS-08` | 效力／驗收／B/EXTERNAL；USER/EXTERNAL 需 Consent、Scope、external receipt、補償；有界外部效果可查；[CH-15](#ch-15)/[CH-39](#ch-39) | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 原 Consumer/合法使用者授權 | 對陌生帳號自動操作/未知結果重試；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-051` `L1-r4:L848` | `W1-W4_HANDOFF` | W2/`WP-FHS-09` | 效力／驗收／A/W3；INDEPENDENT/RELEASE 僅在真正需要時啟動原 Checker/Publisher；同 CandidateSHA Case/Raw 原 Keeper；[CH-41](#ch-41)/[CH-43](#ch-43)/[CH-44](#ch-44) | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 原受權發行收據 | PR Green/Markdown signed 誤宣 RELEASE；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-052` `L1-r4:L849` | `W1-W4_HANDOFF` | W2/`WP-FHS-21` | 效力／驗收／A；15 Acceptance Edge/96 Oracle/282 B1 Case 各自有原 Case 身份；POS/NEG/EDGE/SEC 真受影 Reviewer；[CH-30](#ch-30)/[CH-31](#ch-31)/[CH-32](#ch-32) | Original Domain Owner/Reader (scope binding pending) | 完整分母逐項可回原 Domain | 一套 generic fixture 宣稱全 282 PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-053` `L1-r4:L850` | `W0_REQUIRED` | W0/`WP-FHS-00` | Program／A；22WP/36 Depends-on 邊逐 ID 原樣保留；W0-A WP15；W0-B WP06；W1–W3/受影依賴；[CH-37](#ch-37) | Original FHS BODY-11 Program/DAG Reader → L2 Planner | 首有用 SPEC 在受保護 Effect 前 | 以縮工改原 DAG edge、加新 W4 代方案；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-054` `L1-r4:L851` | `W0_REQUIRED` | W0/`WP-FHS-01` | Program／A；r4 U0–U4 全量語義保存，四 JSONL 是候選事實表；byte partition/obligation/crosswalk/decision delta/3 SpecDelta；[CH-05](#ch-05)/[CH-06](#ch-06)/[CH-07](#ch-07) | Corpus Extractor + Original Domain Semantic Owner (U0–U4) | 所有非空片段有處置或 HOLD | grep/counter/SHA 當 100% 原義；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-055` `L1-r4:L852` | `W0_REQUIRED` | W0/`WP-FHS-15` | Program／A；L0/L1/L2/L3 是文檔視圖，非四套 Canonical；Master+Global Semantic；PIPD Blueprint；Waves；WP Slice；[CH-45](#ch-45) | Original Program/DAG/Delivery Consumer | 逐層交 downstream 不改原 Writer | L2 Wave Plan 冒 Native WorkOrder；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-056` `L1-r4:L853` | `W0_REQUIRED` | W0/`WP-FHS-15` | Program／A＋B；缺一處原 Reader 只停受影部分；FirstFail/AffectedScope/ResumePredicate/ClaimCeiling；[CH-48](#ch-48) | Original Program/DAG/Delivery Consumer | 其他合法來源和 Goal 可繼續 | 因一個 Host/Oracle HOLD 而所有 READ 停工；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-057` `L1-r4:L854` | `W1-W4_HANDOFF` | W4/`WP-FHS-19` | Delivery／A；單次發布/供應鏈 CI 只因受影 Release 啟動；Original Publisher/License/NOTICE/SBOM/Case RAW；[CH-44](#ch-44) | Original Program/DAG/Delivery Consumer | Publisher 有效 Receipt | 全產品 README 每次必建 SBOM/attestation；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-058` `L1-r4:L855` | `W1-W4_HANDOFF` | W4/`WP-FHS-14` | Delivery／A；FHS_PIPD-LS-PKG 須可移交原 PIPD/Native 且明確上限；L0-L3+3 SPEC+U4+PI/PD/ECP/TQAEP/原 Consumer；[CH-40](#ch-40)/[CH-45](#ch-45) | Original Program/DAG/Delivery Consumer | Subject/OriginalID/SourceSHA/Effect/Claim 全接線 | 產出本 MD 就宣稱全量正式 PKG 生成；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-059` `L1-r4:L856` | `W1-W4_HANDOFF` | W4/`WP-FHS-19` | Quality／A＋B；Repo 成功遵守 repo-specific AGENTS 及所需規範；GitHub branch/PR、Original Reader、逐規範 Negative；[CH-14](#ch-14)/[CH-44](#ch-44) | Original Oracle/Protected Checker Reader | 功能與 repo process 都符合 | 測試綠但觸犯禁止直接 main 寫；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-060` `L1-r4:L857` | `W1-W4_HANDOFF` | W2/`WP-FHS-09` | Quality／A＋B；測試由 Original Oracle/Neg/Mutant 反證，不只 LLM 自產綠燈；真 Case identity/Runner/Raw/Checker；[CH-41](#ch-41)/[CH-49](#ch-49) | Original Oracle/Protected Checker Reader | 原適用變體能抓回歸 | 測試空泛，全部 88% tests pass 仍漏 mutants；`DESIGN_OBLIGATION_MISSING`（若失卡） |

**U0–U4 本輪真值**：31 bytes/sha、84 卡及 crosswalk 表已做靜態來源盤點；正式 Original Reader 的 U0 byte partition、U1 全部子義、U2/3/4 語義與 Owner ACK **未執行**；不能以此索引宣稱全量 31 原文 semantic closure。

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：W0 24 alias／84 DesignID 與上位交叉。
- **獨立輸入**：原 source SHA/span、parent/neg、L1 INT/FHS-DR、CH/WP/SpecClause。
- **原有能力導向操作**：按 U2 正逆映射、U3 SpecDelta、U4 inverse readback 分別記錄；原 Reader 欠件不冒正式閉包。
- **可觀察輸出／First Useful Outcome**：W0 Crosswalk + TraceClosureReport AUTHOR-CANDIDATE／HOLD。
- **原 Reader／Consumer**：原 Semantic Owner + 原 Product/Architecture/Program Consumer。
- **正反驗收與 FirstFail**：POS 所有 W0-required 映射到來源或 scoped HOLD；NEG 遺失上位 INT/DR 任一條仍宣全量 → DESIGN_OBLIGATION_MISSING。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-07](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-07)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### U2／U3／U4 完整雙向閉包規劃

| 階段 | 逐原物輸入 | W0 操作 | 最低可收成果 | 必拒收 NEG |
|---|---|---|---|---|
| U2 | `OriginalRequirementID+SourceSHA+Parent/NEG+Consumer` | `OriginalID ↔ L1 CH ↔ L2 PrimaryWP ↔ W0/後波 SpecClause` 雙向 Join | `CrosswalkLedger`、一個唯一主波與回查位置 | 刪任何 `INT-01..24`／`FHS-DR-001..060` 而仍全通過 |
| U3 | Current/Proposed 原文，三 SPEC | 分 Product Delta、ABI/Authority Delta、Program/DAG Delta；每 delta 保留 POS/NEG 和適用 Scope | `SpecDeltaLedger` 的 `NO_CHANGE / CHANGED / CONFLICT / HOLD` | 以新章字串出現等同無產品功能退化 |
| U4 | U2/U3 的雙向檔案與原 Reader | 反向從 `Deliver→Case→SPEC→OriginalID→Original SourceSpan`，原 Domain Owner 逐受影 ID 確認/否認 | `SemanticClosureRequest`（候選），未核准保留 owner/status | 用 `31/31 SHA`、`485 count`、或單一 Checker 自證語義守恆 |

W0 中 `84=24 INT+60 FHS-DR` 是設計義務，不替代 `949 R15`、`149 Child` 或 `96 Oracle` 的原義分母。本文的追蹤表來源同一 L1 r4 原行號；附錄提供逐 ID 完整表。**POS**：任選 `INT-24`、`FHS-DR-060` 回查其 Parent/NEG/主波/Consumer；**NEG**：只有 ID 數或來源摘要 → `DESIGN_OBLIGATION_MISSING`。原 Corpus/Owner Semantic Reader 在 U0～U4 真核簽前仍 `H-U0U4-02`。

# CH-08｜SBL SharedCore 六模組與三 SP 的完整產品鏈

<a id="ch-08"></a>

## r4 當期 L3 合法正文｜`CH-08`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-08` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：SBL SharedCore 六模組與三 SP 的完整產品鏈。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：SBL Product/三 SP。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-02` `L1-r4:L770` | W3 | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) | 保留 8 Kind/3 Mode/4 Host/3 SP/6 Module/16 Moment/GJ/OriginalID | 用 FHS 新名稱刪掉 SBL 原 Kind/Mode/Host/Moment/Child；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-008` `L1-r4:L805` | W1 | SBL Product/Kind/Host Original Consumer | 同 WorkID/Source/Case 的適用讀回 | 任一 Portable Skill 自行發 Grant/Checker；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-009` `L1-r4:L806` | W3 | SBL Product/Kind/Host Original Consumer | 真原 ProductKind 得到受界成果 | 改成自造 FHS 全域 AgentOS 取代 SBL Core；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-08` Primary=`W1`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-09｜八 Kind、三 Mode、四 Host、16 Moments、38 Delivery Surfaces

<a id="ch-09"></a>

## r4 當期 L3 合法正文｜`CH-09`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-09` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：八 Kind、三 Mode、四 Host、16 Moments、38 Delivery Surfaces。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Original Kind/Mode/Host Product Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-02` `L1-r4:L770` | W3 | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) | 保留 8 Kind/3 Mode/4 Host/3 SP/6 Module/16 Moment/GJ/OriginalID | 用 FHS 新名稱刪掉 SBL 原 Kind/Mode/Host/Moment/Child；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-14` `L1-r4:L782` | W1 | SBL Product/Kind/Host Original Consumer、SBL Product Owner → CLI Host Consumer、SBL Product Owner → Original Skill/Agent Host Registry Co | 各 Host 按本地能力與 Loader 獨立 Install/Invoke/Uninstall | 一個 Host 的 CLI PASS 當四 Host Skill/Agent 都已 Qualify；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-17` `L1-r4:L785` | W3 | SBL Product/Kind/Host Original Consumer、SBL Product Owner → CLI Host Consumer、SBL Product Owner → Original Skill/Agent Host Registry Co | GJ01 clean CLI、GJ02 bounded patch、GJ03 live skill invoke | GJ01 只有 SPEC、GJ02 缺 Repo Diff、GJ03 只有 Resume；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-005` `L1-r4:L802` | W3 | SBL Product/Kind/Host Original Consumer | 至少受影 Kind 真能被原 Host 消費 | 以 CLI 例子驗收 PLUGIN/AI_SYSTEM；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-006` `L1-r4:L803` | W3 | SBL Product/Kind/Host Original Consumer | 合法本地效果可做、Shadow無Effect、Connected要真ACK | 字串 Mode 覆蓋原 HGK 許可；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-007` `L1-r4:L804` | W1 | SBL Product/Kind/Host Original Consumer | 不同 Host 的實際 Trigger/Uninstall | 把在 ChatGPT 生成草稿稱 Windows 已完成；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-010` `L1-r4:L807` | W3 | SBL Product/Kind/Host Original Consumer | 受影 Moment 各有 FirstFail/exit | 將 16 Moment 視為每個 B Goal 全部必經；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-09` Primary=`W3`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-10｜已知答案、Source-bound 檢索、FAR／知識服務

<a id="ch-10"></a>

## r4 當期 L3 合法正文｜`CH-10`：主波 W0（L2 r4 §6）
**W0 主責：一次性 GHP-01 與 KnownAnswer。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：新普通 Goal→以 Subject+SourceManifestSHA+Scope 查原 QuestionLedger；相同已回答資料重用，必要缺口才按 Risk 對指定 Scope 問一次；GHP-01 未讀到則記 GHP01_READER_UNBOUND，不阻合法 READ/DRAFT。
**原 Writer／Reader／Consumer／責任界線**：原 SBL TPM Knowledge Reader、原 GHP-01 Decision Reader；GHP-02 僅真正 Release。
**Acceptance POS**：POS：對相同 Scope 的第二輪 Goal 不重問已知答案且可顯示原回答來源。
**Acceptance NEG／FirstFail**：NEG：為所有普通 Goal 加 OPS 或 Publisher Gate；FirstFail=QUESTION_LEDGER_SCOPE_COLLISION。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-01` `L1-r4:L769` | W0 | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) | 以 Subject+Scope+SourceSHA 鍵重用 KnownAnswer/QuestionLedger，只有差額重問 | 沿用相同 SourceSHA 卻重問同一已知答案；或混同一個 Human Owner 與技術 Checker 身分；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-19` `L1-r4:L787` | W2 | Fabric FHS Navigation/Policy/FAR Reader → Original Consumer、Original Program/DAG/Delivery Consumer | FAR Typed Envelope／R8 Consumer ACK/NACK | 研究文章／FAR Finding 無原 R8 Consumer ACK 卻宣 policy 已落地；`DESIGN_OBLIGATION_MISSING`（若失卡） |

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：相同 Subject 重複來源查詢。
- **獨立輸入**：subject+scope+source_sha+QuestionLedger+KnownAnswerRef。
- **原有能力導向操作**：依唯一原 FAR/Knowledge Reader 查來源；已知答案同有效邊界復用、僅 scope/source drift 重問。
- **可觀察輸出／First Useful Outcome**：具證據差額回答與 SourceRef/QuestionUpdate 候選。
- **原 Reader／Consumer**：FAR/G-KNOW／Original Product Reader。
- **正反驗收與 FirstFail**：POS 同 SHA 同 Scope 不反覆詢問；NEG 舊答案在變更 Scope 後依舊作 grant → KNOWN_ANSWER_STALE。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-10](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-10)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### KnownAnswer／QuestionLedger 的可重用鍵與零重問政策

每筆 `QuestionLedgerEntry` 必有 `subject_id, affected_scope, source_sha, question_id, last_answer_hash, verified_by, applicability, updated_at, invalidation_condition`。相同 `subject+scope+sourceSHA` 命中既有有效答案就重用，只有 SourceSHA/Scope/Reader 變更才重問受影問題；不得用單純標題相似度把不同人／不同專案答案併用。`GHP-01` 可在 W0 作者端規劃一次；`UNDECIDED/DEFERRED` 只凍結受影外部操作，不阻合法 SOURCE_READ/LOCAL_DRAFT_WRITE。`GHP-02` 只由原 Publisher 在需要遠端發布時檢查。

**POS**：一個已知 SourceSHA 的短 Goal 不會多問不影響 FUO 的十題；**NEG**：把前一次不同 scope 的 Owner 批准借用 → `KNOWN_ANSWER_SCOPE_MISMATCH`。Consumer：SBL TPM 原 Product Reader，W0 DraftMaker；未授權的秘密不能寫 Ledger。

# CH-11｜TPM 三 SPEC：Product、Architecture、Program 與 18 Stage

<a id="ch-11"></a>

## r4 當期 L3 合法正文｜`CH-11`：主波 W0（L2 r4 §6）
**W0 主責：三 SPEC 與 18 Stage。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：ProductSPEC 有 Persona/JTBD/FUO/ACC±，ArchitectureSPEC 有五 Seam/ADR/單 Writer/ABI/Effect NEG，ProgramSPEC 有 22WP/36 DAG/5 波/Stop-Resume；三者同 Subject 但角色與 Consumer 分開，依原 Stage contract 編制，不自造 PI。
**原 Writer／Reader／Consumer／責任界線**：`tpm-product-plan`→Original SBL Product Reader；`tpm-system-plan`→Original Architecture Reader；`tpm-program-plan`→Original Program/PIPD Intake。
**Acceptance POS**：POS：三 SPECDraft 在隔離目錄可讀，原 PIPD Intake 得到正確 source locators，或回具名 NACK。
**Acceptance NEG／FirstFail**：NEG：把 3 SPEC 合併成一段 prose 便冒已編 PI；FirstFail=SPEC_NOT_SOURCE_BOUND。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-12` `L1-r4:L780` | W0 | Original Domain Owner/Reader (scope binding pending) | PM JTBD/FUO；SE ADR/ABI；TPgM DAG/Exit | 三 SPEC 同文換標題或沒有不同 Consumer/ACC；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-003` `L1-r4:L800` | W0 | Original Domain Owner/Reader (scope binding pending) | 三 SPEC 各自有 ACC/NEG/NonGoals | 三份同文換標題、自稱 PI 由 GPT 正式發布；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-008` `L1-r4:L805` | W1 | SBL Product/Kind/Host Original Consumer | 同 WorkID/Source/Case 的適用讀回 | 任一 Portable Skill 自行發 Grant/Checker；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-021` `L1-r4:L818` | W0 | Original Domain Owner/Reader (scope binding pending) | 各 SPEC 有原來源和非目標 | 三職能被當三個獨立 Principal；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-022` `L1-r4:L819` | W0 | Original Domain Owner/Reader (scope binding pending) | 當次階段結果可原位交下游 | 把階段文章當出現已完成事件；`DESIGN_OBLIGATION_MISSING`（若失卡） |
### W0-A 三份可用的 source-bound SPEC（同 Subject，三個獨立 Consumer）

**實際作者示例的 User Goal**：「從既有 SBL14/FHS17 來源為普通變更需求產生可審閱的三份變更規格；不得改 Repo、不得部署」。**Subject 以使用者 Goal＋本地 Source Manifest 的 digest 真實綁定**，無原 PIPD 原件簽名時只作 `W0_EXAMPLE`，不能偽稱既有 canonical SubjectID。

| SPEC | 設計輸入／動作 | 直接可用的 FUO／輸出 | 原 Consumer/Owner | 正向／否向 Oracle |
|---|---|---|---|---|
| Product SPEC | 普通 Goal + P01–P07 + 原 RequirementID/SHA + QuestionLedger → PM 綁 persona、MVP、non-goals | `SpecDelta` 包含 goal、使用者實際看得到的差額建議、七痛點適用性、ACC(POS/NEG) 各至少一項 | SBL Product Owner/Original PIPD Intake | POS：Owner 能直接逐條接受/拒絕差額；NEG：只有生成檔案數而沒有 FUO → `FUO_NOT_OBSERVABLE` |
| Architecture SPEC | Product SPEC 同 Subject + 五 Typed Seam + 原現役三庫/ABI/Effect Registry → SE 給 ADR | 五 Seam 各有原 Producer/Reader/Consumer、原單 Writer、風險、Positive/Negative、No-Second-Issuer | SBL Architecture/HGK/Fabric Domain Reader | POS：正確區分 READ/DRAFT/DEV/OPS；NEG：把 GitHub HEAD 或 staging 當 Host Active → `HOST_READBACK_HOLD` |
| Program SPEC | Product＋Architecture + 22 WP/36 DAG + Scope/受影效果 → TPgM 排五波 | 每 WP 指定原身份、唯一 Primary Wave、前置／Stop/Resume、第一 FUO、具名 HOLD、需求證據 | Original Program/Reader、後續 PIPD Intake/Receiver | POS：首 W0 Draft 不等待未來 W2 Receipt；NEG：WP06 被列 W0 已完成 → `FUTURE_RECEIPT_DEPENDENCY` |

**三份 Spec 最低必填欄位**：`artifact_id,version,goal,subject_ref,source_refs[{OriginalID,file_sha256,span}],scope,persona_or_owner,jtbd,fuo,non_goals,assumptions,decisions,acceptance[{POS,NEG,oracle,consumer,firstfail}],open_questions,affected_holds,original_reader,claim_ceiling`。相同已答 QuestionLedger 不重問；風險／未知造成 Critical 深度，而不是所有情況強迫 L4 全發行。

**TaskSpecSeed** 是可供原 PIPD Reader 接收／NACK 的候選，不含 Grant、Receipt、Release；若原 Intake 無可用 Reader，維持 `ORIGINAL_PIPD_PRE_V2_ROUTING_HOLD` 而保留 W0 三 SPEC 草稿供 Owner 審。

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：W0-A 產三份 SPEC。
- **獨立輸入**：Goal/Source/OriginalID、七痛點、五 seam、22WP/36Edge。
- **原有能力導向操作**：PM 独立 Product/FUO/ACC±；SE independent ADR/ABI/SoD；TPgM independent DAG/Exit/Stop-Resume；同 Subject、三原 Consumer 不同。
- **可觀察輸出／First Useful Outcome**：三份 content-addressed SPEC Draft+TaskSpecSeed candidate。
- **原 Reader／Consumer**：SBL TPM 原三角色／PIPD 原 Intake。
- **正反驗收與 FirstFail**：POS 三種業務字段可見不相同；NEG 以 Seed JSON 自稱 PI 編譯/Grant → SPEC_NOT_SOURCE_BOUND。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-11](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-11)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### 三份不同 SPEC 的完整作者端輸出契約（不等同原 PI）

**Product SPEC — `W0/PM/ProductSPEC-DRAFT`**：`persona=single human owner`, `goal=ordinary_goal_to_source_bound_fuo`, `JTBD=取用可落地需求與可回溯增量`, `FUO=A:answer|B:SpecDelta`, `MVP=W0-A`, `scope=SBL14/FHS17 affected`, `non_goals=[new_issuer,new_compiler,force_full_release_gate]`, `source_refs`, `ACC±`, `known_answers`。輸入普通 Goal 與來源；輸出具名產品需求條位。Consumer：原 SBL Product/PIPD Intake；POS 任何需求有可觀察價值；NEG 用文件數替代 FUO → `PRODUCT_SPEC_FUO_MISSING`。

**Architecture SPEC — `W0/SE/ArchitectureSPEC-DRAFT`**：`system_context=Fabric→SBL(PIPD)→HGK→Hermes`, `original_writers`, `seams=S1..S5`, `effect_matrix`, `ABI_version_candidate`, `ADR-001..`, `security_SO_D`, `sourceSHA`, `NEG wrongScope/PolicyEpoch/Writer`, `recovery=WorldRaw reconciliation before retry`。輸入 Product SPEC；輸出五 Seam/ADR/ABI 接線草案和受影拒收。Consumer：原 SBL/PIPD/Fabric/HGK 原 Registry；POS 每 seam 有唯一責任與原 Consumer；NEG 同一新服務同時簽 Permit/Checker → `ARCH_SOD_BREACH`。

**Program SPEC — `W0/TPgM/ProgramSPEC-DRAFT`**：`milestone=W0-A/W0-B`, `WP_original=00..21`, `edges_original=36`, `primary_wave_per_WP`, `done_predicate`, `stop_resume`, `evidence_expectation`, `handoff=[W1,W2,W3,W4]`, `hold_owner`。輸入前兩 SPEC/原 DAG；輸出具名可驗 WorkPackage 交接與依賴。Consumer：Original Program/Native PLAN Reader；POS 22/36 保持 DAG 無環；NEG W0 把 WP06 宣告已執行 → `PROGRAM_WAVE_MISMATCH`。

三 SPEC 的 `SpecClauseID` 是**本草案作者端標記**，非原 `PIPD` schema `$id`。生成時只寫本輪隔離工作區；若交原 PIPD 編譯須由 W1 Original Compiler rederive、驗 Reader ACK、Original Source/Authority；任何 T4/T5 Transition 當期映射未確認時維持 `CR-DOC04-STATE-MAP HOLD`。



### r3 當期條款（保留 r2 正確修補並補差額）｜同一普通 Goal 三份相異的 SPEC Instance（AUD-W0-P1-008）

採用 `SubjectID=FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001`，Product SPEC `SPEC-Product-W0-r3`（Persona/JTBD/FUO/ACC±）、Architecture SPEC `SPEC-Architecture-W0-r3`（ADR/Single Writer/ABI/Effect/SoD NEG）、Program SPEC `SPEC-Program-W0-r3`（22 WP/36 DAG/Stop-Resume/WP19 E26 NEG）。三份是**不同欄位的作者端 Source-bound SPEC 實例**，非原 PIPD Canonical PI/PD；具名 Trigger/Input/Output/原 Consumer、POS/NEG 見 `W0_R3_WALKING_SKELETON_SPEC_SEAMS_TRACE.md`，不可只用模板存在宣布功能完成。Original Source/U0-U4 語義核簽仍 `NOT_OBSERVED`。

# CH-12｜PIPD 13 CLI／19 Contract Families／8 Skills 與唯一 Writer

<a id="ch-12"></a>

## r4 當期 L3 合法正文｜`CH-12`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-12` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：PIPD 13 CLI／19 Contract Families／8 Skills 與唯一 Writer。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：Original PIPD Registry/Compiler。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-06` `L1-r4:L774` | W1 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | SBL integrations/pipd 13 CLI／19 families／8 skills，薄 Adapter | 將歷史 PIPD-LS-SP 當現役唯一 Writer，或技能自行簽 PI；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-13` `L1-r4:L781` | W1 | SBL RepoContext/PD Reader → HGK Original Issuer → Repo World Reader、SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | PI source-bound，PD 晚綁 Repo，ECP 非 Admission，TQAEP 依 Original Oracle | ECP intent 冒 Issuer Permit；PD 未 live RepoContext 即號稱已綁；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-027` `L1-r4:L824` | W1 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | Case 有正負例和待原 Checker 收據 | 不核 ABI 就加 compile-cc 14th verb；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-12` Primary=`W1`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-13｜Authority SourceFreeze／Profile Tailoring／原 PI 的 18 領域

<a id="ch-13"></a>

## r4 當期 L3 合法正文｜`CH-13`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-13` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：Authority SourceFreeze／Profile Tailoring／原 PI 的 18 領域。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：Original PIPD Authority/Profile/PI Writer。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-06` `L1-r4:L774` | W1 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | SBL integrations/pipd 13 CLI／19 families／8 skills，薄 Adapter | 將歷史 PIPD-LS-SP 當現役唯一 Writer，或技能自行簽 PI；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-13` `L1-r4:L781` | W1 | SBL RepoContext/PD Reader → HGK Original Issuer → Repo World Reader、SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | PI source-bound，PD 晚綁 Repo，ECP 非 Admission，TQAEP 依 Original Oracle | ECP intent 冒 Issuer Permit；PD 未 live RepoContext 即號稱已綁；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-023` `L1-r4:L820` | W1 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | 不合格來源受影 HOLD | 用 MD metadata 的 approved 字樣繞 Reader；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-024` `L1-r4:L821` | W1 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | 原 PIPD Reader 實收／錯誤有型別 | GPT 生成 JSON 假裝正式 PI；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-13` Primary=`W1`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-14｜PD-01..10、RepoContext Currentness、Scope 與晚綁

<a id="ch-14"></a>

## r4 當期 L3 合法正文｜`CH-14`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-14` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：PD-01..10、RepoContext Currentness、Scope 與晚綁。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：Original PD / RepoContext Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-13` `L1-r4:L781` | W1 | SBL RepoContext/PD Reader → HGK Original Issuer → Repo World Reader、SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | PI source-bound，PD 晚綁 Repo，ECP 非 Admission，TQAEP 依 Original Oracle | ECP intent 冒 Issuer Permit；PD 未 live RepoContext 即號稱已綁；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-012` `L1-r4:L809` | W2 | SBL RepoContext/PD Reader → HGK Original Issuer → Repo World Reader | 原 Repo Raw/小 diff/test/revert | stale HEAD/skip preimage/wildcard WriteSet；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-025` `L1-r4:L822` | W1 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | Repo drift 只重綁受影部分 | 未知 Repo 強行出有權 PD；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-034` `L1-r4:L831` | W1 | Original Domain Owner/Reader (scope binding pending) | 相應 PR 有真變更與可回退提交 | 憑本檔直接覆寫 main/force push；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-048` `L1-r4:L845` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 可逆最小 Patch | 自造 universal write permission；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-059` `L1-r4:L856` | W4 | Original Oracle/Protected Checker Reader | 功能與 repo process 都符合 | 測試綠但觸犯禁止直接 main 寫；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-14` Primary=`W1`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-15｜ConstructionContract／ECP：DEV、OPS、USER、RELEASE 不混用

<a id="ch-15"></a>

## r4 當期 L3 合法正文｜`CH-15`：主波 W2（L2 r4 §6）
**W0 非主責，唯一主波是 W2。** `CH-15` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W2 專屬規格與 Native 權威。

**原產品主題／受影接收**：ConstructionContract／ECP：DEV、OPS、USER、RELEASE 不混用。主波 L3 收件 `W2_藍圖&skeleton → W2_草案 → W2_定案`；原 Consumer：Original ECP Writer / HGK effect receiver。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W2 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W2_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-04` `L1-r4:L772` | W0 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、HGK Original Issuer/SharedSpine/Protected Checker Reader、Effect-spe | A 全量產品語義守恆；B 最短合法 Effect 路徑 | 把 A 全量需求全作每次 B READ 的前置 OPS Permit；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-09` `L1-r4:L777` | W2 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Jou | 原 HGK 應用權限與 World Reader reconcile before retry | UNKNOWN 未 World Reconcile 即同 OperationID 盲重試；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-13` `L1-r4:L781` | W1 | SBL RepoContext/PD Reader → HGK Original Issuer → Repo World Reader、SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | PI source-bound，PD 晚綁 Repo，ECP 非 Admission，TQAEP 依 Original Oracle | ECP intent 冒 Issuer Permit；PD 未 live RepoContext 即號稱已綁；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-18` `L1-r4:L786` | W0 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、HGK Original Issuer/SharedSpine/Protected Checker Reader、Effect-spe | 六類 Effect 對應最低充分原 Evidence | 缺 OPS/RELEASE Permission 使合法 READ/DRAFT 全域停工；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-006` `L1-r4:L803` | W3 | SBL Product/Kind/Host Original Consumer | 合法本地效果可做、Shadow無Effect、Connected要真ACK | 字串 Mode 覆蓋原 HGK 許可；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-012` `L1-r4:L809` | W2 | SBL RepoContext/PD Reader → HGK Original Issuer → Repo World Reader | 原 Repo Raw/小 diff/test/revert | stale HEAD/skip preimage/wildcard WriteSet；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-026` `L1-r4:L823` | W1 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | 有界許可後讀真 World/Repo | 無 Effect Authorization 自行 Apply；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-046` `L1-r4:L843` | W0 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 短 READ 有用結果 | 因缺 OPS/RELEASE 全系統停工；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-047` `L1-r4:L844` | W0 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 真檔案來源/字元編碼/Readback | Draft 檔案冒 Canonical Product；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-048` `L1-r4:L845` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 可逆最小 Patch | 自造 universal write permission；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-049` `L1-r4:L846` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 適用 Host 操作真的生效 | Git rollback 冒 Host 世界回復；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-050` `L1-r4:L847` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 原 Consumer/合法使用者授權 | 對陌生帳號自動操作/未知結果重試；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案增補｜跨波原責任保留與准入規劃
### W0-A 僅規劃 Effect 互斥門檻（主波 W1）

`SOURCE_READ`=原 ACL+hash；`LOCAL_DRAFT_WRITE`=授權隔離 output root+cleanup；`REPO_WRITE`=W2 exact RepoContext/HEAD/preimages/DEV ECP/Issuer；`HOST_OP`=原 Host SID/PolicyEpoch/TTL/OPS ECP；`RELEASE`=原 Publisher/GHP-02+Protected Checker。W0 不核發 Permit，原 ABI/OperationType 未綁標 `EFFECT_UNBOUND`。POS 同一段原 source read 不受未授權 HOST_OP 阻斷；NEG 把所有操作歸一律 OPS → `EFFECT_CLASS_COLLAPSED`。此處只作 W1/W2 handoff，不改寫 CH15 原 Writer。

# CH-16｜跨庫 Typed ABI、Producer→Consumer、Same Subject 交接

<a id="ch-16"></a>

## r4 當期 L3 合法正文｜`CH-16`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-16` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：跨庫 Typed ABI、Producer→Consumer、Same Subject 交接。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：Original ABI Consumer。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。


### W0 草案路由確認｜非本波主責
`CH-16` Primary=`W1`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-17｜Fabric Policy／FAR／治理鏡像與 FHS 工程入口

<a id="ch-17"></a>

## r4 當期 L3 合法正文｜`CH-17`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-17` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：Fabric Policy／FAR／治理鏡像與 FHS 工程入口。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：Fabric Policy Owner/Consumer。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-11` `L1-r4:L779` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader、Fabric FHS Navigation/Policy/FAR Reader → Original Consumer | 有權原 Writer/Owner 決定有效版本、比對 Same Scope | README／作者文件 SHA 當 Original Effective Canonical；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-19` `L1-r4:L787` | W2 | Fabric FHS Navigation/Policy/FAR Reader → Original Consumer、Original Program/DAG/Delivery Consumer | FAR Typed Envelope／R8 Consumer ACK/NACK | 研究文章／FAR Finding 無原 R8 Consumer ACK 卻宣 policy 已落地；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-029` `L1-r4:L826` | W1 | Fabric FHS Navigation/Policy/FAR Reader → Original Consumer | 三庫各自 bounded PR/source fact | 導航 metadata 被當授權來源；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-030` `L1-r4:L827` | W1 | Fabric FHS Navigation/Policy/FAR Reader → Original Consumer | R8 真 ACK 不被研究文件代替 | 工具回應被視為 Policy Applied；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-17` Primary=`W1`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-18｜HG-KSEOS 唯一 Native Issuer／SharedSpine／WorkID／許可

<a id="ch-18"></a>

## r4 當期 L3 合法正文｜`CH-18`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-18` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：HG-KSEOS 唯一 Native Issuer／SharedSpine／WorkID／許可。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：HGK Original Issuer/SharedSpine。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-04` `L1-r4:L772` | W0 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、HGK Original Issuer/SharedSpine/Protected Checker Reader、Effect-spe | A 全量產品語義守恆；B 最短合法 Effect 路徑 | 把 A 全量需求全作每次 B READ 的前置 OPS Permit；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-05` `L1-r4:L773` | W1 | HGK Original Issuer/SharedSpine/Protected Checker Reader | 沿用 HGK 原 WorkID/Issuer/CAS/SharedSpine/World | 生成第二 HGK Issuer／Queue／SharedSpine；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-031` `L1-r4:L828` | W1 | HGK Original Issuer/SharedSpine/Protected Checker Reader | 真原 Issuer admission + world state | Human Owner 只有一人→普通 Agent 有 admin Token；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-032` `L1-r4:L829` | W1 | HGK Original Issuer/SharedSpine/Protected Checker Reader | 直接修改 HGK 的一般 Profile 被拒 | 兩個 Hermes Profile 名稱即宣稱 OS 隔離；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-18` Primary=`W1`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-19｜Hermes 三 Lane、模型路由、Profiles、ActualServed

<a id="ch-19"></a>

## r4 當期 L3 合法正文｜`CH-19`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-19` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：Hermes 三 Lane、模型路由、Profiles、ActualServed。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：Hermes Original Host / Lane Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-21` `L1-r4:L789` | W2 | Original Domain Owner/Reader (scope binding pending)、Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | Requested/Required/Selected/Spawn/Protocol/ActualServed/Usage | Selected model 存在但沒有 Request/Transport/ActualServed Raw 即宣 Served；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-035` `L1-r4:L832` | W1 | Original Domain Owner/Reader (scope binding pending) | 真 task result 有再續工 | 簡單 Read 任務硬套多 Agent Queue；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-036` `L1-r4:L833` | W1 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 同 Subject 每 Lane 真 Request/Served/Usage | 只選到 Picker 便宣稱 Protected Lane Served；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-038` `L1-r4:L835` | W2 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 用合法卡路由完成分工 | 直接讀另一 Profile secrets 破壞 snapshot；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-19` Primary=`W1`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-20｜Hermes Native Kanban／Delegation／Swarm／長任務編排

<a id="ch-20"></a>

## r4 當期 L3 合法正文｜`CH-20`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-20` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：Hermes Native Kanban／Delegation／Swarm／長任務編排。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：Hermes Kanban/Delegation Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-07` `L1-r4:L775` | W1 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer、Original Tech/License/Host/Method Owner → Capability C | Hermes Direct/Delegation/Kanban/Swarm 按複雜度選擇，NoFit 才補 | 沒查現有 Hermes 能力便重造 Scheduler/Router；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-035` `L1-r4:L832` | W1 | Original Domain Owner/Reader (scope binding pending) | 真 task result 有再續工 | 簡單 Read 任務硬套多 Agent Queue；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-037` `L1-r4:L834` | W2 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 有 Prompt Delivered 和模型實際請求 | Windows issue #146955 型 worker bound/no prompt 仍 Done；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-038` `L1-r4:L835` | W2 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 用合法卡路由完成分工 | 直接讀另一 Profile secrets 破壞 snapshot；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-040` `L1-r4:L837` | W2 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 任務能 Crash 恢復且有界停損 | 無限回圈/4h 乾等/無 FirstFail；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-20` Primary=`W1`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-21｜Windows Host／CLI／Plugin／Skill：安裝與實際載入三段驗收

<a id="ch-21"></a>

## r4 當期 L3 合法正文｜`CH-21`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-21` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：Windows Host／CLI／Plugin／Skill：安裝與實際載入三段驗收。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Original Host Install/Loader Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-14` `L1-r4:L782` | W1 | SBL Product/Kind/Host Original Consumer、SBL Product Owner → CLI Host Consumer、SBL Product Owner → Original Skill/Agent Host Registry Co | 各 Host 按本地能力與 Loader 獨立 Install/Invoke/Uninstall | 一個 Host 的 CLI PASS 當四 Host Skill/Agent 都已 Qualify；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-17` `L1-r4:L785` | W3 | SBL Product/Kind/Host Original Consumer、SBL Product Owner → CLI Host Consumer、SBL Product Owner → Original Skill/Agent Host Registry Co | GJ01 clean CLI、GJ02 bounded patch、GJ03 live skill invoke | GJ01 只有 SPEC、GJ02 缺 Repo Diff、GJ03 只有 Resume；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-007` `L1-r4:L804` | W1 | SBL Product/Kind/Host Original Consumer | 不同 Host 的實際 Trigger/Uninstall | 把在 ChatGPT 生成草稿稱 Windows 已完成；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-011` `L1-r4:L808` | W3 | SBL Product Owner → CLI Host Consumer | 實際 clean Host 操作與退出 | README-only/假退出碼/錯誤清除外來檔；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-013` `L1-r4:L810` | W3 | SBL Product Owner → Original Skill/Agent Host Registry Consumer | Host 真 Invoked + Unloaded | 單 ZIP 存在即宣稱已用；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-049` `L1-r4:L846` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 適用 Host 操作真的生效 | Git rollback 冒 Host 世界回復；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案增補｜跨波原責任保留與准入規劃
### W0 技術准入的安裝／載入分層驗證計畫（主波 W1）

對各 Host 留 `SELECTED→INSTALL_PLANNED→INSTALLED→LOADED→INVOKED→VERIFIED` 彼此獨立的證據欄：版本/commit/SHA/License、Windows Host 依賴、命令實際 exit/Source、Host loader 認得的 capability、真正 trigger 和 nontrigger、原 Consumer ActualServed/WorldRaw、卸載殘留。未觀測一律 `NOT_OBSERVED`，不是 `NOFIT` 或 `OPTIONAL_FOREVER`。只有後波原 Host Reader 確認過的狀態可以推進。POS 未安裝的 Method-only 仍合法有原功能 trace；NEG 只看 GitHub checkout 就標 VERIFIED → `HOST_LOAD_LAUNDERING`。

# CH-22｜Native20：現役唯一原生核心與維護權

<a id="ch-22"></a>

## r4 當期 L3 合法正文｜`CH-22`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-22` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：Native20：現役唯一原生核心與維護權。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：Native Owner/Registry。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-16` `L1-r4:L784` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader、Original Tech/License/Host/Method Owner → Capability Consumer | Need→Occupant→Qualified EffectiveLoad→Consumer→Retire | 只讀 485 身份卡便強制安裝 485 件或把必備 Default 改 OPTIONAL；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-018` `L1-r4:L815` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader | 原 Slot 的 OriginalDisposition/NoFit 皆可讀 | 建立 485 安裝任務；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-042` `L1-r4:L839` | W1 | Original Tech/License/Host/Method Owner → Capability Consumer | 需求由已合格工具解決 | 用外部宣傳文即自稱 loaded；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案增補｜跨波原責任保留與准入規劃
### W0 技術來源映射（主波 W3，非新 Build 工單）

`Native20` 分為原 SINGLETON/ROLE_WORKER/METHOD_FORMAT/OWNER_COMPONENT，不等於 20 個待安裝可執行程式。W0 建 `OriginalID+SourceLocator+OriginalDisposition+Need+Owner+Consumer+POS/NEG+future_wave`，保留 `CORE.FABRIC_POLICY`,`CORE.HGK_NATIVE`,`CORE.SHAREDSPINE`,`RUNTIME.HERMES` 等原身份。這些在原域保持單一 Writer，W1/W3 Host Fit/Loaded 不可由本草案假定。反例：以 20 core 條位增建 20 套服務 → `SECOND_CONTROL_PLANE_DENY`。

# CH-23｜Default30：默認能力、可配置佔用與 NoFit

<a id="ch-23"></a>

## r4 當期 L3 合法正文｜`CH-23`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-23` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：Default30：默認能力、可配置佔用與 NoFit。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Default Capability/Host Owner。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-07` `L1-r4:L775` | W1 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer、Original Tech/License/Host/Method Owner → Capability C | Hermes Direct/Delegation/Kanban/Swarm 按複雜度選擇，NoFit 才補 | 沒查現有 Hermes 能力便重造 Scheduler/Router；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-16` `L1-r4:L784` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader、Original Tech/License/Host/Method Owner → Capability Consumer | Need→Occupant→Qualified EffectiveLoad→Consumer→Retire | 只讀 485 身份卡便強制安裝 485 件或把必備 Default 改 OPTIONAL；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-20` `L1-r4:L788` | W3 | Original Tech/License/Host/Method Owner → Capability Consumer、Original Program/DAG/Delivery Consumer | Callgraph 等價+Consumer 轉交+受影 POS/NEG+Rollback | 未驗 Caller/Consumer 等價便刪舊技術，HotSwap 後不可回退；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-018` `L1-r4:L815` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader | 原 Slot 的 OriginalDisposition/NoFit 皆可讀 | 建立 485 安裝任務；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-042` `L1-r4:L839` | W1 | Original Tech/License/Host/Method Owner → Capability Consumer | 需求由已合格工具解決 | 用外部宣傳文即自稱 loaded；`DESIGN_OBLIGATION_MISSING`（若失卡） |
### 30 個 DESIGN_DEFAULT_REQUIRED 原槽位的 r4 只讀接收與真正資格現況分離
原 Mandatory 不可改成 Optional。以下保留當期 L2 r4 §7.r4-DEFAULT 的逐筆名與 Source；僅為跨波讀取索引，主要適用與 Host 資格由 W3 原 Tech/Host Reader 判定。對未安裝或未 Loaded 不可填 `ACTIVE`。
| Default 原 ID / L1-r4 | 原指定 Occupant 與 OriginalDisposition | 後波 Host Fit／Rollback | W0 處置 |
|---|---|---|---|
| `Default30:P0-TOOL-001` `L1-r4:L2395` | **Hermes Agent**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：NATIVE_OWNER_COMPONENT。。；原業務 POS/NEG P0-TOOL-001 Hermes Agent \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；DIRECT_CORE；成果：governed durable task dispatch \/ Host/Pack：RUNTIME.HERMES→HGK SharedSpine→canonical Hermes executable/PID；Owner candidate=HGK Native Control Owner + Hermes Runtime Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS… | `Need=Default30:P0-TOOL-001`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`NATIVE_OWNER_COMPONENT`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-002` `L1-r4:L2405` | **SDLC_PRW**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：NATIVE_OWNER_COMPONENT。。；原業務 POS/NEG P0-TOOL-002 SDLC_PRW \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；DIRECT_CORE；成果：phase/source bound lifecycle mapping \/ Host/Pack：CORE.SDLC_PRW→PIPD phase compiler→HGK SharedSpine schema reader；Owner candidate=PIPD Lifecycle Writer + HGK SharedSpine Consumer Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；… | `Need=Default30:P0-TOOL-002`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`NATIVE_OWNER_COMPONENT`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-003` `L1-r4:L2415` | **SRU Kernel**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：LIBRARY。。；原業務 POS/NEG P0-TOOL-003 SRU Kernel \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；DIRECT_CORE；成果：safe reusable execution kernel \/ Host/Pack：CORE.SRU_KERNEL→HGK Native Registry/SourceReuse scoped resolver；Owner candidate=HGK SRU Kernel / Native Registry Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用觸發時… | `Need=Default30:P0-TOOL-003`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`LIBRARY`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-004` `L1-r4:L2425` | **DocETL**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：LIBRARY。。；原業務 POS/NEG P0-TOOL-004 DocETL \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SHARED_CAPABILITY；成果：document ingest with provenance \/ Host/Pack：KNOWLEDGE.DOCETL→SBL/PIPD Document Reader + known file/source parser；Owner candidate=PIPD Document Reader Owner + SBL Knowledge Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；In… | `Need=Default30:P0-TOOL-004`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`LIBRARY`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-005` `L1-r4:L2435` | **Codex**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：CLI。。；原業務 POS/NEG P0-TOOL-005 Codex \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；DIRECT_CORE；成果：bounded primary code worker \/ Host/Pack：RUNTIME.CODE_WORKER_PRIMARY→Hermes delegated Codex CLI via HGK executor registry；Owner candidate=HGK/Hermes Bounded Executor Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適… | `Need=Default30:P0-TOOL-005`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`CLI`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-006` `L1-r4:L2445` | **OpenCode**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：CLI。。；原業務 POS/NEG P0-TOOL-006 OpenCode \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；DIRECT_CORE；成果：bounded code worker alternative \/ Host/Pack：RUNTIME.CODE_WORKER_ALTERNATE→Hermes approved OpenCode/OpenCode Go provider adapter；Owner candidate=HGK Model Policy Owner + Hermes Provider Router Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_… | `Need=Default30:P0-TOOL-006`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`CLI`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-008` `L1-r4:L2455` | **LLM Wiki**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：LIBRARY。。；原業務 POS/NEG P0-TOOL-008 LLM Wiki \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SHARED_CAPABILITY；成果：source bound wiki projection \/ Host/Pack：KNOWLEDGE.LLM_WIKI→SBL Knowledge K09 wiki compiler/validated local reader；Owner candidate=SBL Knowledge/Wiki Compiler Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NE… | `Need=Default30:P0-TOOL-008`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`LIBRARY`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-010` `L1-r4:L2465` | **Spec Kit**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：SKILL。。；原業務 POS/NEG P0-TOOL-010 Spec Kit \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SHARED_CAPABILITY；成果：greenfield specification method \/ Host/Pack：SPEC.GREENFIELD_SPEC_KIT→SBL TPM/spec HostAdapter, optional official Spec Kit；Owner candidate=SBL SPEC/TPM Owner + PIPD Canonical Reader Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=D… | `Need=Default30:P0-TOOL-010`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`SKILL`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-011` `L1-r4:L2475` | **OpenSpec**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：SKILL。。；原業務 POS/NEG P0-TOOL-011 OpenSpec \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SHARED_CAPABILITY；成果：brownfield spec change workflow \/ Host/Pack：SPEC.BROWNFIELD_OPENSPEC→SBL proposal adapter+OpenSpec allowed Host skill；Owner candidate=SBL Spec/Change Owner + HGK Proposal Consumer Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DI… | `Need=Default30:P0-TOOL-011`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`SKILL`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-016` `L1-r4:L2485` | **mattpocock-skills v1.1**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：SKILL。。；原業務 POS/NEG P0-TOOL-016 mattpocock-skills v1.1 \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SHARED_CAPABILITY；成果：document-led structured interview \/ Host/Pack：METHOD.MATTPOCOCK_SKILLS→TPM Skill loader+approved original v1.1 method contract；Owner candidate=SBL TPM Skill/Host Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOV… | `Need=Default30:P0-TOOL-016`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`SKILL`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-017` `L1-r4:L2495` | **Grill Me**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：SKILL。。；原業務 POS/NEG P0-TOOL-017 Grill Me \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SHARED_CAPABILITY；成果：Grill Me discovery interaction \/ Host/Pack：METHOD.GRILL_ME→TPM Document/QuestionLedger Skill Host；Owner candidate=SBL TPM Intake/QuestionLedger Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用觸發時真 asked … | `Need=Default30:P0-TOOL-017`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`SKILL`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-020` `L1-r4:L2505` | **Superpowers**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：SKILL。。；原業務 POS/NEG P0-TOOL-020 Superpowers \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SHARED_CAPABILITY；成果：TDD/Debug/Review method \/ Host/Pack：METHOD.SUPERPOWERS→SBL bounded code-repair method slot via Host Skill；Owner candidate=SBL Bounded Repair/Skill Host Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用… | `Need=Default30:P0-TOOL-020`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`SKILL`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-024` `L1-r4:L2515` | **Agent Skills**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：SKILL。。；原業務 POS/NEG P0-TOOL-024 Agent Skills \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SHARED_CAPABILITY；成果：portable SKILL.md contract \/ Host/Pack：FORMAT.AGENT_SKILLS→SBL skills/ HostAdapter + Skill Loader；Owner candidate=SBL Host Adapter/Plugin Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用觸發時真 fresh ho… | `Need=Default30:P0-TOOL-024`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`SKILL`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-025` `L1-r4:L2525` | **Model Context Protocol**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：FORMAT。。；原業務 POS/NEG P0-TOOL-025 Model Context Protocol \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SHARED_CAPABILITY；成果：typed tool gateway protocol \/ Host/Pack：PROTO.MCP→HGK Tool/Method registry and approved host MCP adapter；Owner candidate=HGK Tool Registry + Host MCP Adapter Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；… | `Need=Default30:P0-TOOL-025`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`FORMAT`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-026` `L1-r4:L2535` | **AGENTS.md**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：FORMAT。。；原業務 POS/NEG P0-TOOL-026 AGENTS.md \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SHARED_CAPABILITY；成果：pinned repo instruction context \/ Host/Pack：SOURCE.AGENTS_MD→Git repo AGENTS.md parser read-only；Owner candidate=Subject Repository Owner + HGK Instruction Reader Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/P… | `Need=Default30:P0-TOOL-026`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`FORMAT`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-028` `L1-r4:L2545` | **DESIGN.md**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：FORMAT。。；原業務 POS/NEG P0-TOOL-028 DESIGN.md \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SHARED_CAPABILITY；成果：design view fidelity \/ Host/Pack：SOURCE.DESIGN_MD→SBL TPM design reader for versioned DESIGN.md；Owner candidate=SBL TPM Source/Design Reader Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用觸發時真 input→ou… | `Need=Default30:P0-TOOL-028`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`FORMAT`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-030` `L1-r4:L2555` | **Loop Engineering**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：METHOD_ONLY。。；原業務 POS/NEG P0-TOOL-030 Loop Engineering \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；DIRECT_CORE；成果：bounded loop state transitions \/ Host/Pack：CORE.LOOP_ENGINEERING→HGK SharedSpine/Hermes reducer/Checkpoint；Owner candidate=HGK SharedSpine Reducer Owner + Hermes Runtime Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；… | `Need=Default30:P0-TOOL-030`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`METHOD_ONLY`；OriginalMethodOutput+trigger/nontrigger+Consumer readback; binary_install=NOT_APPLICABLE；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-031` `L1-r4:L2565` | **Harness Engineering**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：METHOD_ONLY。。；原業務 POS/NEG P0-TOOL-031 Harness Engineering \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；DIRECT_CORE；成果：agent harness contract and qualification \/ Host/Pack：CORE.HARNESS_ENGINEERING→HGK native harness + Runner/Tool registry；Owner candidate=HGK Harness/Runner Registry Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Inv… | `Need=Default30:P0-TOOL-031`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`METHOD_ONLY`；OriginalMethodOutput+trigger/nontrigger+Consumer readback; binary_install=NOT_APPLICABLE；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-032` `L1-r4:L2575` | **Multi-Agent**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：METHOD_ONLY。。；原業務 POS/NEG P0-TOOL-032 Multi-Agent \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；DIRECT_CORE；成果：bounded multi-agent delegation \/ Host/Pack：RUNTIME.MULTI_AGENT→Hermes SWARM/Worker pool via HGK admission；Owner candidate=HGK Task Admission Owner + Hermes SWARM Pool Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/P… | `Need=Default30:P0-TOOL-032`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`METHOD_ONLY`；OriginalMethodOutput+trigger/nontrigger+Consumer readback; binary_install=NOT_APPLICABLE；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-034` `L1-r4:L2585` | **Sub-Agent**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：METHOD_ONLY。。；原業務 POS/NEG P0-TOOL-034 Sub-Agent \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；DIRECT_CORE；成果：sub-agent bounded task handoff \/ Host/Pack：RUNTIME.SUB_AGENT→HGK lease-bound Hermes child worker；Owner candidate=HGK Task Admission Owner + Hermes Sub-Agent Worker Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NE… | `Need=Default30:P0-TOOL-034`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`METHOD_ONLY`；OriginalMethodOutput+trigger/nontrigger+Consumer readback; binary_install=NOT_APPLICABLE；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-053` `L1-r4:L2595` | **OpenTelemetry**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：LIBRARY。。；原業務 POS/NEG P0-TOOL-053 OpenTelemetry \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SUPPLY_CHAIN_DEPENDENCY；成果：tracing and diagnostics \/ Host/Pack：OBS.OTEL→Host telemetry exporter via approved OpenTelemetry adapter；Owner candidate=Hermes Observability/Operations Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/PO… | `Need=Default30:P0-TOOL-053`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`LIBRARY`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-059` `L1-r4:L2605` | **Semgrep**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：CLI。。；原業務 POS/NEG P0-TOOL-059 Semgrep \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SUPPLY_CHAIN_DEPENDENCY；成果：Semgrep SAST \/ Host/Pack：SEC.SEMGREP→Security CI runner Semgrep pinned ruleset；Owner candidate=SBL/PIPD Security CI Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用觸發時真 ruleset digest + run/exit/fin… | `Need=Default30:P0-TOOL-059`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`CLI`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-060` `L1-r4:L2615` | **CodeQL**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：CLI。。；原業務 POS/NEG P0-TOOL-060 CodeQL \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SUPPLY_CHAIN_DEPENDENCY；成果：CodeQL code query analysis \/ Host/Pack：SEC.CODEQL→Security CI or GitHub Actions CodeQL required workflow；Owner candidate=SBL/PIPD Security CI Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用觸發時真 Code… | `Need=Default30:P0-TOOL-060`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`CLI`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-061` `L1-r4:L2625` | **Trivy**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：CLI。。；原業務 POS/NEG P0-TOOL-061 Trivy \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SUPPLY_CHAIN_DEPENDENCY；成果：Trivy vulnerability scanning \/ Host/Pack：SEC.TRIVY→Security CI Trivy binary runner；Owner candidate=SBL/PIPD Security CI Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用觸發時真 SBOM/image ref pinned plus … | `Need=Default30:P0-TOOL-061`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`CLI`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-062` `L1-r4:L2635` | **GitHub Actions**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：FORMAT。。；原業務 POS/NEG P0-TOOL-062 GitHub Actions \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SUPPLY_CHAIN_DEPENDENCY；成果：GitHub Actions CI runtime \/ Host/Pack：SUPPLY.CI_GITHUB_ACTIONS→SBL/PIPD repository workflow caller；Owner candidate=SBL/PIPD Repository CI Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用觸發時真 … | `Need=Default30:P0-TOOL-062`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`FORMAT`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-063` `L1-r4:L2645` | **OpenSSF Scorecard**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：CLI。。；原業務 POS/NEG P0-TOOL-063 OpenSSF Scorecard \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SUPPLY_CHAIN_DEPENDENCY；成果：OpenSSF Scorecard posture \/ Host/Pack：SUPPLY.OSSF_SCORECARD→Security Owner Scorecard workflow；Owner candidate=Security/Supply-Chain Assurance Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：… | `Need=Default30:P0-TOOL-063`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`CLI`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-064` `L1-r4:L2655` | **SBOM**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：FORMAT。。；原業務 POS/NEG P0-TOOL-064 SBOM \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SUPPLY_CHAIN_DEPENDENCY；成果：software bill of materials \/ Host/Pack：SUPPLY.SBOM→Release Owner SBOM generator/output registry；Owner candidate=Release/Supply-Chain SBOM Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用觸發時真 SBOM per a… | `Need=Default30:P0-TOOL-064`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`FORMAT`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-065` `L1-r4:L2665` | **Artifact Attestation**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：FORMAT。。；原業務 POS/NEG P0-TOOL-065 Artifact Attestation \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SUPPLY_CHAIN_DEPENDENCY；成果：artifact provenance attestation \/ Host/Pack：SUPPLY.ARTIFACT_ATTESTATION→Release Owner GitHub Attestation/Cosign binding；Owner candidate=Release/Attestation Signing Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=… | `Need=Default30:P0-TOOL-065`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`FORMAT`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-068` `L1-r4:L2675` | **OSV**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：CLI。。；原業務 POS/NEG P0-TOOL-068 OSV \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；SUPPLY_CHAIN_DEPENDENCY；成果：OSV vulnerability knowledge \/ Host/Pack：SEC.OSV→Security/vuln feed Reader or pinned approved OSV API；Owner candidate=Security Vulnerability Intelligence Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用觸… | `Need=Default30:P0-TOOL-068`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`CLI`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |
| `Default30:P0-TOOL-072` `L1-r4:L2685` | **SQLite**；原處置 DEFAULT_ENABLED_AFTER_QUALIFICATION；product_decision：MANDATED_DEFAULT；AssetType候選：LIBRARY。。；原業務 POS/NEG P0-TOOL-072 SQLite \/ DEFAULT_ENABLED_AFTER_QUALIFICATION 原選用；原決策 DEFAULT_ENABLED_AFTER_QUALIFICATION；DIRECT_CORE；成果：SQLite durable state store \/ Host/Pack：CORE.SQLITE→HGK existing src/hg_kseos/spine.py / DB actual host discovery；Owner candidate=HGK SharedSpine State/Schema Owner（正式 principal 仍須 registry/Owner 確認），PIN/LICENSE/LOADER_SHA=DISCOVERY；Invoke/POS/NEG：適用觸發時真 … | `Need=Default30:P0-TOOL-072`／原 Slot Owner/Original Consumer，W1設計→W3適用 Host 真測；type=`LIBRARY`；exact source/release/commit+License/Host fit→original installer/loader→Invoked→ConsumerRaw；Preferred=該原卡名稱（待 pin）；ActualQualified=**NOT_OBSERVED**；Fallback=原 LastGood 若同 Scope Qualified，否則 `CAPABILITY_GAP_HOLD`；Rollback=原 Owner 受影退出 | `W1-W4_HANDOFF` (W3 primary; W0 on-demand qualified reuse only) |


### W0 草案增補｜跨波原責任保留與准入規劃
### W0 Default30 的一版選型卡（主波 W3，強制預設不降級）

對原 `DEFAULT_ENABLED_AFTER_QUALIFICATION` 的 30 項逐一保留目標 `MANDATED_DEFAULT`，不因欠 Windows Raw/License 將其改成 Optional。W0 `SELECTED` 設計佔用：`P0-TOOL-001` Hermes v0.22.5 原 Runtime；`P0-TOOL-005` Codex 原 bounded Diff/Test；`P0-TOOL-011` OpenSpec v1.16.0 **method design pin（r2 當期）**；其他 `P0-TOOL-*` 依原表和需要保留。各版本/License/Host/Owner/Consumer 在 Trace 技術表逐 ID 回讀。完整安裝/載入/呼叫/測試/HotSwap 交 W1/W3，不把本卡誤當 30 已 qualification。POS Need/Occupant/Owner 一一可對；NEG 未裝就永久降成不需要 → `DEFAULT_DOWNGRADE_DENY`。



### r3 當期條款｜Default30 具名設計決策與 pin 缺口（AUD-W0-P1-004）

30 個原 Mandatory Need 均保留 DESIGN_DEFAULT_REQUIRED，逐筆 `DEFAULT30_CHOICES.json` 綁 L1 原 card SHA/實體行、原功能、Original Consumer、POS/NEG、exit/rollback。Hermes 保留 v0.22.5 設計基準（v0.22.7 已查官方但不默升）；OpenSpec 採 v1.16.0 設計基準（npm Node≥22.12 或原官方 Windows standalone，未安裝）。官方版本／License 實際讀回及日期見 EXTERNAL_RESEARCH_READBACK.json。

不能解析到具體發行 artifact 的項明記 OCCUPANT_PIN_HOLD，不能把 ORIGINAL_COMPONENT_OF_RECORD 字串當已具唯一可執行 binary。每 Need 由其原 Technology/License/Host Reader 補 immutable artifact+hash、license/NOTICE、Windows fit/ACL/loader、功能 POS/NEG、Consumer ACK 才解除受影安裝。SELECTED_DESIGN、INSTALLED、BOUND、INVOKED、VERIFIED 分開；本輪後四項 NOT_OBSERVED。Required 不降 Optional；單 Need HOLD 不阻 SOURCE_READ/隔離草案。

### r4-candidate｜Default30 pin 分類與狀態升格禁令（AUD-W0-P1-004 收斂）

30 個 Mandatory Need 的設計佔用分兩類，**不得混用**；分類以 `DEFAULT30_CHOICES.json` 的 `hold` 欄位為唯一來源：

- **`OCCUPANT_PIN_HOLD`（28 項）**：Need 已能定位到具名 Occupant 候選，但缺 immutable artifact hash／License／NOTICE／Windows fit／loader 之一。此類保留 `DESIGN_DEFAULT_REQUIRED` 與 `SELECTED_DESIGN`，`required` 不降、Need 不刪。
- **`HOST_PIN_HOLD`（2 項）**：`P0-TOOL-001` Hermes Agent（設計基準 `v0.22.5`；官方 `v0.22.7` 已查但不默升）與 `P0-TOOL-011` OpenSpec（`v1.16.0` 設計基準，未安裝）。兩者的 pin 缺口在 **Host 本體**而不在 Occupant 選型，因此「已寫出版本號」不等於「Host 已載入」，不得以 release 頁或 changelog 反推 `INSTALLED`。

**狀態機（單向，不得跳段）**：`REQUIRED → SELECTED_DESIGN → INSTALLED → BOUND → INVOKED → VERIFIED`。本輪只到 `SELECTED_DESIGN`，後四段全部 `NOT_OBSERVED`。

**FirstFail 兩碼分義**：Required 改 Optional 或刪 Need＝`DEFAULT_DOWNGRADE_DENY`；`SELECTED_DESIGN`、`OCCUPANT_PIN_HOLD` 或 `HOST_PIN_HOLD` 被直接寫成 `INSTALLED`／`BOUND`／`INVOKED`／`VERIFIED`＝`CAPABILITY_STATE_ESCALATION`。兩碼皆為本版 vetted 代碼字彙（別名表見 `CH-43` §r4-candidate）。

單一 Need 的 pin HOLD 不阻 `SOURCE_READ` 與隔離草案，也不使同批其他 Need 失效；28+2 的分類缺口只 HOLD 該 Need 的 host 升格，不 HOLD 其設計條文。

# CH-24｜Donor24：可借用外部輪子與授權條件

<a id="ch-24"></a>

## r4 當期 L3 合法正文｜`CH-24`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-24` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：Donor24：可借用外部輪子與授權條件。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Donor License/Host Owner。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-16` `L1-r4:L784` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader、Original Tech/License/Host/Method Owner → Capability Consumer | Need→Occupant→Qualified EffectiveLoad→Consumer→Retire | 只讀 485 身份卡便強制安裝 485 件或把必備 Default 改 OPTIONAL；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-20` `L1-r4:L788` | W3 | Original Tech/License/Host/Method Owner → Capability Consumer、Original Program/DAG/Delivery Consumer | Callgraph 等價+Consumer 轉交+受影 POS/NEG+Rollback | 未驗 Caller/Consumer 等價便刪舊技術，HotSwap 後不可回退；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-018` `L1-r4:L815` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader | 原 Slot 的 OriginalDisposition/NoFit 皆可讀 | 建立 485 安裝任務；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-045` `L1-r4:L842` | W3 | Original Tech/License/Host/Method Owner → Capability Consumer | 旧有效功能不能回歸 | 未測就刪 HGK 已用控制面；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案增補｜跨波原責任保留與准入規劃
### W0 Donor24 資產採納／拒絕的最少欄位（主波 W3）

只對受影 Need 選具名 donor 的 pinned commit/License/Host/ABI/Version，用 `BUILD_OR_USE=REUSE|THIN_ADAPTER|NOFIT|REFERENCE_ONLY|REJECT` 分離結果。方法槽不等於下載/安裝；原 Native 已可滿足 Need 就不用借第二輪子。HotSwap 預先規劃 callgraph+原 Consumer parity＋NEG＋rollback/uninstall residue。POS 不增第二 Compiler；NEG 24 donor 全部預設 must-install → `DONOR_SET_FLATTENED`。



### r3 當期條款（保留 r2 正確修補並補差額）｜WP16 Donor24 原 Slot 機械翻譯（AUD-W0-P1-006）

保持原 24 個 Donor SourceID、Disposition、Trigger/Output；`SLOT-OS-01..04` 選用 OpenSpec `v1.16.0` 的 Explore/SpecDelta/Validate/Archive **方法型**功能，輸入為 `SourceSHA+SpecDelta+Scope`，輸出為供 SBL Product/PIPD Reader 審閱的差額規格，原 Canonical 仍由 SBL Compiler 生成。`SLOT-GT-01..04` 依原 `REFERENCE/EVAL_ONLY` 僅以 gstack review/QA checklist 當補助方法，不轉成已安裝 Hermes Plugin，也不得出 Protected AO 簽章。`SLOT-GS-01..04` 為 Archived Reference；其餘 MP/SK/SP 檢查原 License 和 Host，再視原 Need 逐項翻譯，不預先安裝。每 Slot 的 `Input→Translate→ExpectedOutput→OriginalConsumer→POS/NEG/FirstFail` 在 `W0_R3_TECH_CHOICE_AND_TRANSLATION.md` 具名表列；無原 Reader ACK 的寫效果止於作者端草案。

### r3 WP16 逐 Slot 可消費轉譯

WP16 原 24 Donor/25 Method 責任保留。每個原 ID 的 source-bound Trigger/Input→獨特 Translation/Output→Original Consumer、原 NEG/FirstFail、License/Host/ACL、rollback 在 WP16_TRANSLATION49.json 與 W0_R3_TECH_CHOICE_AND_TRANSLATION.md；所有 W0 review-required 項保留，非採用者依原 REFERENCE_ONLY/DEFER/NO_SOURCE_EVIDENCE，不形成 installer。方法只交原 MethodOutput；有真效果的 OS03/Archive 仍需原 ECP/Closure，不能借 W0 文檔取得許可。

# CH-25｜Method25：演算法／流程工具方法的原用途

<a id="ch-25"></a>

## r4 當期 L3 合法正文｜`CH-25`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-25` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：Method25：演算法／流程工具方法的原用途。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Method Consumer。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-16` `L1-r4:L784` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader、Original Tech/License/Host/Method Owner → Capability Consumer | Need→Occupant→Qualified EffectiveLoad→Consumer→Retire | 只讀 485 身份卡便強制安裝 485 件或把必備 Default 改 OPTIONAL；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-018` `L1-r4:L815` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader | 原 Slot 的 OriginalDisposition/NoFit 皆可讀 | 建立 485 安裝任務；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案增補｜跨波原責任保留與准入規劃
### W0 Method25 的原用途維持（主波 W3）

`METHOD_ONLY` 可用於 Product Interview、OpenSpec change proposal、gstack review/QA 流程設計，不構成原生 Worker 或獨立證據。只有必要的 `Need` 才派真正 Host 安裝，未被呼叫保持 `SELECTED / INVOKED_NOT_OBSERVED`。NEG 單一方法名稱被拿來替代 HGK `Native PLAN` 或 Original Checker → `METHOD_AS_AUTHORITY_DENY`。



### r3 當期條款（保留 r2 正確修補並補差額）｜WP16 Method25 原方法與 Skill／Installer 區隔

`METHOD-01..25` 的 `METHOD_ONLY/PROTOCOL_ONLY/SUPPORT_ONLY/CANDIDATE/REFERENCE` 不得變成 25 件必安裝。W0 對 `METHOD-06 OpenSpec` 產 `SourceSHA+SpecDelta→OpenSpec v1.16.0 change+validate report` 候選，對 `METHOD-23 FAR/FDA` 僅產原 Fabric/HGK FAR/FirstFail repair-cone；對 `METHOD-10 MCP` 只讀協定、不新建現役 Host。若把方法/參考當已 Loaded，先失 `METHOD_AS_INSTALL_DENY`；若未有具名輸入/輸出/Consumer 卻稱成功壓製，先失 `METHOD_TRANSLATION_MISSING`。逐 OriginalID 轉譯保留在 `W0_R3_TECH_CHOICE_AND_TRANSLATION.md`；W1/W3 原 Host/License Reader 確認後始可啟用。

# CH-26｜TECH386：逐原 ID 技術功能與非降級 Disposition

<a id="ch-26"></a>

## r4 當期 L3 合法正文｜`CH-26`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-26` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：TECH386：逐原 ID 技術功能與非降級 Disposition。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Tech Need/License/Host Owner。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-16` `L1-r4:L784` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader、Original Tech/License/Host/Method Owner → Capability Consumer | Need→Occupant→Qualified EffectiveLoad→Consumer→Retire | 只讀 485 身份卡便強制安裝 485 件或把必備 Default 改 OPTIONAL；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-018` `L1-r4:L815` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader | 原 Slot 的 OriginalDisposition/NoFit 皆可讀 | 建立 485 安裝任務；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案增補｜跨波原責任保留與准入規劃
### W0 TECH386 不進入「386 件必安裝」陷阱（主波 W3）

386 原 ID 逐行保留原 `Disposition`、SourceLocator、NEG、License/Host/Consumer；`REJECTED/REFERENCE_ONLY/METHOD_ONLY/DEFERRED_BY_EVIDENCE` 原義不能由作者重新判為 `MUST_INSTALL`。W0 交付具名選型台帳與受影 NoFit 原 Owner，後續 W3 只重測需更換 Occupant 的局部 Scope。NEG 看到缺工具就自動新增第二 Queue → `TECH_DISPOSITION_LAUNDERING`。

# CH-27｜SBL 50 Parent／149 Child：原生產品分母專章

<a id="ch-27"></a>

## r4 當期 L3 合法正文｜`CH-27`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-27` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：SBL 50 Parent／149 Child：原生產品分母專章。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：SBL Product Parent/Child Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-015` `L1-r4:L812` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader | 每個原 ID 有候選或具名 HOLD | 原字串關鍵字命中代 SOURCE_TRACE_PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-27` Primary=`W3`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-28｜R15 949 原產品原子與 B1 66／254／629 映射

<a id="ch-28"></a>

## r4 當期 L3 合法正文｜`CH-28`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-28` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：R15 949 原產品原子與 B1 66／254／629 映射。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：SBL Full Product R15 Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-016` `L1-r4:L813` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader | Full Product 949 身分另帳清晰 | 把 B1 PASS 宣稱 949 全驗收；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-28` Primary=`W3`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-29｜Kind×Mode×Host×LegacyToken 192 Cell 的原始逐格行為

<a id="ch-29"></a>

## r4 當期 L3 合法正文｜`CH-29`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-29` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：Kind×Mode×Host×LegacyToken 192 Cell 的原始逐格行為。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Original Host Cell Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-14` `L1-r4:L782` | W1 | SBL Product/Kind/Host Original Consumer、SBL Product Owner → CLI Host Consumer、SBL Product Owner → Original Skill/Agent Host Registry Co | 各 Host 按本地能力與 Loader 獨立 Install/Invoke/Uninstall | 一個 Host 的 CLI PASS 當四 Host Skill/Agent 都已 Qualify；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-017` `L1-r4:L814` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader | 每 Cell 適用/NoFit/原 Reader | 把 Legacy OFF 簡單等同 Provider disabled；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-29` Primary=`W3`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-30｜Original 96 Oracle：Test Class×Oracle 的型別與逐格準則

<a id="ch-30"></a>

## r4 當期 L3 合法正文｜`CH-30`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-30` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：Original 96 Oracle：Test Class×Oracle 的型別與逐格準則。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Original Assurance Oracle Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-052` `L1-r4:L849` | W2 | Original Domain Owner/Reader (scope binding pending) | 完整分母逐項可回原 Domain | 一套 generic fixture 宣稱全 282 PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-30` Primary=`W3`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。



### r3 當期條款｜96 Oracle typed POS/NEG（AUD-W0-P0-002）

WP21 的 96 原 CaseID/Class/Oracle/applicability/Parent/NEG/FirstFail 以 FHS-BODY-07 真 SHA `81a8c2f1cc4629f59829f11f87aebd14cd57f7c4dd0970d672880e90e2899741` 及 SBL-DOC-08 C39 物理行逐案釘選。`ORACLE96_CONTRACTS.json` 與 `W0_R3_ORACLE96_PER_CASE_CONTRACTS.md` 指向每案真 POS、domain-NEG、oracle-NEG bytes/SHA；檢測先驗同 Type/Scope/Parent/Source，然後 Class predicate，再驗該 Oracle payload/predicate。每 Class 兩對異 Type swap 必拒；只換 ID 或 `__CORRUPT__` 不構成具體負例。DETERMINISTIC 的 exact equality、STATE_READBACK pre/post、PROPERTY seed/invariant、REFERENCE_OUTPUT pin、STATISTICAL dataset/calibration/confidence、SEMANTIC_JUDGE calibrated rubric/hard veto、HUMAN consent/scope/signed-decision expectation、COMPOSITE hard AND 互不借 schema。

所有 fixtures 皆 AUTHOR synthetic 設計測例；HUMAN 簽章、Judge 校準、WorldRaw 都 EXPECTED_NOT_OBSERVED。原 Protected Reader/Runner/Host `RUNNER_UNBOUND`，作者 detector 的 STATIC_PASS 不代表原 96 Native Case PASS。Native ALL/安全 veto 的先合取規則不變。B1 282／AC15 保留原身份與分波，具名 NEXT_READER_ACTION 見 CASE393_REGISTRY.json，W0 不執行 393 個世界案例。


# CH-31｜Acceptance Challenge 15 條異構 Sender→Receiver Edge

<a id="ch-31"></a>

## r4 當期 L3 合法正文｜`CH-31`：主波 W2（L2 r4 §6）
**W0 非主責，唯一主波是 W2。** `CH-31` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W2 專屬規格與 Native 權威。

**原產品主題／受影接收**：Acceptance Challenge 15 條異構 Sender→Receiver Edge。主波 L3 收件 `W2_藍圖&skeleton → W2_草案 → W2_定案`；原 Consumer：Original Challenge/Protected Checker。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W2 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W2_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-044` `L1-r4:L841` | W1 | Original Tech/License/Host/Method Owner → Capability Consumer | 原 Runner 能重現 QA Finding | gstack /ship 被當原 Publisher / Independent；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-052` `L1-r4:L849` | W2 | Original Domain Owner/Reader (scope binding pending) | 完整分母逐項可回原 Domain | 一套 generic fixture 宣稱全 282 PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-31` Primary=`W2`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-32｜B1 120 Parent／124 Child／38 Node＝282 Case 的獨立驗收

<a id="ch-32"></a>

## r4 當期 L3 合法正文｜`CH-32`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-32` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：B1 120 Parent／124 Child／38 Node＝282 Case 的獨立驗收。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Original B1 CaseRunner Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-052` `L1-r4:L849` | W2 | Original Domain Owner/Reader (scope binding pending) | 完整分母逐項可回原 Domain | 一套 generic fixture 宣稱全 282 PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-32` Primary=`W3`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-33｜B1 原 27 PI→31 PD Slot：拓撲與 Effect ECP

<a id="ch-33"></a>

## r4 當期 L3 合法正文｜`CH-33`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-33` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：B1 原 27 PI→31 PD Slot：拓撲與 Effect ECP。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Original PI/PD Slot Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-028` `L1-r4:L825` | W1 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | 原 Reader 能追每條細分 PD | 只記 27 PI ID 便宣稱全 PD 完成；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-33` Primary=`W3`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-34｜Portable Commander Guide A／B／C 與原 Native PLAN

<a id="ch-34"></a>

## r4 當期 L3 合法正文｜`CH-34`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-34` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：Portable Commander Guide A／B／C 與原 Native PLAN。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：Original Native PLAN Producer。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-008` `L1-r4:L805` | W1 | SBL Product/Kind/Host Original Consumer | 同 WorkID/Source/Case 的適用讀回 | 任一 Portable Skill 自行發 Grant/Checker；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-34` Primary=`W1`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-35｜FHS-EXECUTE：Lease、Journal、UNKNOWN、World Reconcile

<a id="ch-35"></a>

## r4 當期 L3 合法正文｜`CH-35`：主波 W2（L2 r4 §6）
**W0 非主責，唯一主波是 W2。** `CH-35` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W2 專屬規格與 Native 權威。

**原產品主題／受影接收**：FHS-EXECUTE：Lease、Journal、UNKNOWN、World Reconcile。主波 L3 收件 `W2_藍圖&skeleton → W2_草案 → W2_定案`；原 Consumer：Original HGK reducer/world reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W2 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W2_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-08` `L1-r4:L776` | W2 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 原 Kanban 狀態+WorkID/TaskID 對應+checkpoint、受影 Reconcile | 重啟後遺失 WorkID/Journal，要求 Owner 重新交代長任務；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-09` `L1-r4:L777` | W2 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Jou | 原 HGK 應用權限與 World Reader reconcile before retry | UNKNOWN 未 World Reconcile 即同 OperationID 盲重試；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-039` `L1-r4:L836` | W2 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | no double settlement+有效 replay cap | 同 nonce/未知外部作用重播；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-040` `L1-r4:L837` | W2 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 任務能 Crash 恢復且有界停損 | 無限回圈/4h 乾等/無 FirstFail；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-35` Primary=`W2`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-36｜B1 自舉與 W18：Fresh PID 普通 Goal 的第一成果

<a id="ch-36"></a>

## r4 當期 L3 合法正文｜`CH-36`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-36` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：B1 自舉與 W18：Fresh PID 普通 Goal 的第一成果。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Hermes normal-mode Host Consumer。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-08` `L1-r4:L776` | W2 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 原 Kanban 狀態+WorkID/TaskID 對應+checkpoint、受影 Reconcile | 重啟後遺失 WorkID/Journal，要求 Owner 重新交代長任務；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-22` `L1-r4:L790` | W3 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | Fresh PID 正常 Goal/Task/E33–E42/合法退出 | W18 用 B1 長 Prompt 或測試專用 Profile 冒真普通 Goal；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-041` `L1-r4:L838` | W3 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 不貼 B1 指令也能執行合法任務 | B1 mock 主機結果當 W18 normal pass；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-36` Primary=`W3`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-37｜Program SPEC：W0～W3、原 22 WP／36 DAG 邊及 W0-A/B

<a id="ch-37"></a>

## r4 當期 L3 合法正文｜`CH-37`：主波 W0（L2 r4 §6）
**W0 主責：22 WP、36 DAG 與 W0-A/B。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：W0 的 00/01/15/16/19/21 只做 Read/隔離 Draft/最小證據；工程 W0-B 的 WP06/GJ02 仍隸 W2，必在 W1 綁原 PIPD RepoContext、ECP、HGK Policy/Issuer、Hermes 能力後才可試，W0 不可跨波提前取 future receipt。
**原 Writer／Reader／Consumer／責任界線**：原 Program Reader、HGK Original WorkOrder；W0 Curator 只寫 L3 設計候選，不建 shadow queue。
**Acceptance POS**：POS：22/36 原資料有向無環；每原 WP 只有一主波，受影 effect 需真 ACK。
**Acceptance NEG／FirstFail**：NEG：WP06 被誤作本輪已過可逆世界效果；FirstFail=FUTURE_RECEIPT_DEPENDENCY。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-23` `L1-r4:L791` | W0 | Original FHS BODY-11 Program/DAG Reader → L2 Planner | 保留 WP-FHS-00..21；WP15 先讀草稿，WP06 受護後做 | 改動依賴邊或 Scheduled 當 Done，WP17↔WP06 造成環；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-053` `L1-r4:L850` | W0 | Original FHS BODY-11 Program/DAG Reader → L2 Planner | 首有用 SPEC 在受保護 Effect 前 | 以縮工改原 DAG edge、加新 W4 代方案；`DESIGN_OBLIGATION_MISSING`（若失卡） |
### 完整 22 個 Original WP、唯一 Primary Wave 與 Effect（L2 r4 §4.1）
| Original WP／功能 | 原輸出 | 原依賴 | Primary Wave | 原 Effect/Consumer |
|---|---|---|---|---|
| `WP-FHS-00` Source/Host Discovery | SourceManifest+RepoContext。 | `ROOT` | **W0** | \`SOURCE_READ\`；原唯讀 ACL/read scope。；原 SourceReader/RepoProbe → \`SourceManifest + RepoContext readback\` → 原 TPM/PIPD Source Reader。 |
| `WP-FHS-01` Authority/Oracle/Profile | AuthorityConflictLedger+Oracle/ProfileBinding。 | `WP-FHS-00` | **W0** | \`SOURCE_READ\`；原唯讀 ACL/read scope。；原 Authority/Profile Owner → \`AuthorityBinding/ProfileBinding 原 19-schema Registry\` → PIPD compile-pi。 |
| `WP-FHS-02` Fabric Policy Consumer | PolicyLoadedConsumerACK。 | `WP-FHS-01` | **W1** | \`HOST_OP\`；OPS ECP + Host Owner/Issuer + nonce/TTL/epoch。；Fabric Policy Owner → \`FABRIC/fabric/consumers/hgk_policy_consumer.py 原 Consumer ABI\` → HGK policy consumer。 |
| `WP-FHS-03` HGK Registry/Issuer | IssuerReceiverBinding。 | `WP-FHS-01` | **W1** | \`HOST_OP\`；OPS ECP + Host Owner/Issuer + nonce/TTL/epoch。；HGK 原 Registry/Resolver/Issuer → \`原 HGK WorkOrder/ExecutionBinding/Permit ABI\` → 原 HGK Receiver。 |
| `WP-FHS-04` Hermes Durable Runtime | WakeLeaseRuntimeBinding。 | `WP-FHS-00` | **W1** | \`HOST_OP\`；OPS ECP + Host Owner/Issuer + nonce/TTL/epoch。；Hermes 原 runtime/journal Owner → \`原 WorkID/Queue/Lease/Journal ABI\` → 原 bounded Worker。 |
| `WP-FHS-05` PIPD Native Compiler | PI/PD/DEV-OPS候選。 | `WP-FHS-01` | **W1** | \`LOCAL_DRAFT_WRITE\`；明列隔離 output root 的使用者授權。；PIPD 原 Intake/PI/PD/ECP Compiler → \`PIPD schemas/registry.json 原 19 families\` → HGK construction/OPS adapters。 |
| `WP-FHS-06` Legal First Reversible Slice | 最小可逆Repo diff+Raw。 | `WP-FHS-02, WP-FHS-03, WP-FHS-04, WP-FHS-05, WP-FHS-17` | **W2** | \`REPO_WRITE\`；DEV ECP + exact WriteSet + 原 HGK admission。；已受權 Codex bounded Writer → \`ConstructionContract + DEV ECP + 原 HGK admission\` → 原 Repo Reader/Checker。 |
| `WP-FHS-07` Native PLAN Commander A/B/C | PlanRevisionProposal+CAS ACK。 | `WP-FHS-01, WP-FHS-15` | **W1** | \`LOCAL_DRAFT_WRITE\`；明列隔離 output root 的使用者授權。；原 SBL TPM/Commander PLAN Reader → \`PlanRevisionProposal + 原 PLAN CAS ABI\` → 原 HGK PLAN Reader。 |
| `WP-FHS-08` FHS Execute Worker | WorkerEffectRaw+JournalCursor。 | `WP-FHS-06, WP-FHS-07` | **W2** | \`HOST_OP\`；OPS ECP + Host Owner/Issuer + nonce/TTL/epoch。；原 Hermes Dispatcher + bounded Worker → \`原 ExecutionBinding/lease fence/EffectRaw ABI\` → 原 WorldRaw Collector。 |
| `WP-FHS-09` Challenge/Protected AO | ProtectedCheckerRequest/Receipt（需另一主體）。 | `WP-FHS-08, WP-FHS-21` | **W2** | \`SOURCE_READ\`；原唯讀 ACL/read scope。；原 WorldRaw Producer → \`原 TQAEP/Protected Checker Request ABI\` → 不同 Principal 的原 Protected Checker。 |
| `WP-FHS-10` B1 3 GWO & G-A/G-B | 三GWO各自Raw+G-A/G-B。 | `WP-FHS-09, WP-FHS-20` | **W3** | \`HOST_OP\`；OPS ECP + Host Owner/Issuer + nonce/TTL/epoch。；Fabric/HGK/SBL 三個原 GWO Owner → \`B1 原 PI27→PD31→TQAEP ABI\` → 三 GWO 各自原 Receiver。 |
| `WP-FHS-11` Portable Host Dogfood | 三SP逐Host loaded/invoked raw。 | `WP-FHS-05, WP-FHS-16` | **W1** | \`HOST_OP\`；OPS ECP + Host Owner/Issuer + nonce/TTL/epoch。；原 Portable SP packager/Host Loader → \`原各 Host install/load/invoke/remove manifest\` → 各 Host 原 Skill Reader。 |
| `WP-FHS-12` W18 Normal Mode | 新PID普通Goal E33-E42 Raw。 | `WP-FHS-10, WP-FHS-11` | **W3** | \`HOST_OP\`；OPS ECP + Host Owner/Issuer + nonce/TTL/epoch。；原 Hermes normal-entry Owner → \`W18 ordinary Goal/E33–E42 原 ABI\` → 原 normal Profile/ToolAutoSelect Reader。 |
| `WP-FHS-13` CAP On-Demand + HotSwap | CAP gap/HotSwap parity+readback。 | `WP-FHS-16, WP-FHS-17` | **W3** | \`HOST_OP\`；OPS ECP + Host Owner/Issuer + nonce/TTL/epoch。；原 TechnologyAdmission/Host capability Owner → \`原 Need/Occupant/HotSwap admission ABI\` → 原有 Consumer 與 Host Loader。 |
| `WP-FHS-14` Release/Retire Candidate | ReleaseCandidate+原Publisher receipt。 | `WP-FHS-09, WP-FHS-19` | **W4** | \`RELEASE\`；原 Publisher/GHP-02 + 受保護 Checker。；原 Publisher → \`原 Release/Retire + GHP-02 ABI\` → 原發行 channel Reader。 |
| `WP-FHS-15` TPM Corpus & SPEC 18Stage | 原三SPECDraft、來源readback、FUO十欄；三份受界 SPECDraft／`TaskSpecSeed CANDIDATE`；歷史來源曾記 24 功能 Atom／PI/PD 設計意圖，但本輪未見同 Scope 原 PIPD Reader 真 ACK，`H-WP15-HISTORICAL-ACK-UNVERIFIED`。 | `WP-FHS-00` | **W0** | \`LOCAL_DRAFT_WRITE\`；明列隔離 output root 的使用者授權。；原 TPM Corpus Reader/PM/SE/TPgM → \`SBL 三 SPECDraft + source-bound Stage contracts\` → 原 PIPD Intake。 |
| `WP-FHS-16` Donor/Method Slot Translation | 24slot/25method壓製候選。 | `WP-FHS-00` | **W0** | \`LOCAL_DRAFT_WRITE\`；明列隔離 output root 的使用者授權。；原 SBL DOC06 TechnologyAdmission Owner → \`原 24 Donor Slot/25 Method Reader projection\` → 原 TPM/PIPD/HGK 各受影 Consumer。 |
| `WP-FHS-17` CAP-BOOT Native Occupants | needed能力最小HostOccupant+loaded ACK。 | `WP-FHS-00, WP-FHS-02, WP-FHS-03` | **W1** | \`HOST_OP\`；OPS ECP + Host Owner/Issuer + nonce/TTL/epoch。；原 Host Installer + HGK 原 Issuer → \`CAP-BOOT 原 Host admission + manifest ABI\` → 原 Host capability Registry/Consumer。 |
| `WP-FHS-18` FAR Bounded Repair & Incident | BoundedRepairDiff+RedGreen+residue。 | `WP-FHS-08` | **W2** | \`REPO_WRITE\`；DEV ECP + exact WriteSet + 原 HGK admission。；原 FAR/incident Reader + bounded Writer → \`原 FirstFail/RepairCone + DEV ECP ABI\` → 原 affected rechallenge/Checker。 |
| `WP-FHS-19` CI/Supply Chain & Requal | CI/License/NOTICE/SBOM掃描Raw。 | `WP-FHS-00` | **W0** | \`SOURCE_READ\`；原唯讀 ACL/read scope。；原 CI/supply-chain Reader → \`原 license/NOTICE/SBOM/dependency evidence ABI\` → 原 release-readiness Reader。 |
| `WP-FHS-20` CLI/Agent/Host Kind Matrix | 192Cell適用/NoFit/Host Raw。 | `WP-FHS-05, WP-FHS-16` | **W1** | \`HOST_OP\`；OPS ECP + Host Owner/Issuer + nonce/TTL/epoch。；原 Product/Host matrix Owner → \`原八 Kind×三 Mode×四 Host×Provider token Cell ABI\` → 每個原 Cell 的原 Host Reader。 |
| `WP-FHS-21` Challenge 96/H4/SEAM Coverage | 96Cell/H4/SEAM原Oracle計畫。 | `WP-FHS-01` | **W0** | \`SOURCE_READ\`；原唯讀 ACL/read scope。；原 Acceptance/Oracle Owner → \`原 AC15/Oracle96/H4/SEAM Reader ABI\` → 原 Protected AO Request Reader。 |

### 原 36 邊 DAG（L2 r4 §4.2，原 Reader 判定 consumption 時 Hard/Soft）
| EdgeID | 原前置→後件 | 跨波方向 | Hard/Soft 原域條件 |
|---|---|---|---|
| E01 | `WP-FHS-00 → WP-FHS-01` | `W0→W0` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E02 | `WP-FHS-01 → WP-FHS-02` | `W0→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E03 | `WP-FHS-01 → WP-FHS-03` | `W0→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E04 | `WP-FHS-00 → WP-FHS-04` | `W0→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E05 | `WP-FHS-01 → WP-FHS-05` | `W0→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E06 | `WP-FHS-02 → WP-FHS-06` | `W1→W2` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E07 | `WP-FHS-03 → WP-FHS-06` | `W1→W2` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E08 | `WP-FHS-04 → WP-FHS-06` | `W1→W2` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E09 | `WP-FHS-05 → WP-FHS-06` | `W1→W2` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E10 | `WP-FHS-17 → WP-FHS-06` | `W1→W2` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E11 | `WP-FHS-01 → WP-FHS-07` | `W0→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E12 | `WP-FHS-15 → WP-FHS-07` | `W0→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E13 | `WP-FHS-06 → WP-FHS-08` | `W2→W2` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E14 | `WP-FHS-07 → WP-FHS-08` | `W1→W2` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E15 | `WP-FHS-08 → WP-FHS-09` | `W2→W2` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E16 | `WP-FHS-21 → WP-FHS-09` | `W0→W2` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E17 | `WP-FHS-09 → WP-FHS-10` | `W2→W3` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E18 | `WP-FHS-20 → WP-FHS-10` | `W1→W3` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E19 | `WP-FHS-05 → WP-FHS-11` | `W1→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E20 | `WP-FHS-16 → WP-FHS-11` | `W0→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E21 | `WP-FHS-10 → WP-FHS-12` | `W3→W3` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E22 | `WP-FHS-11 → WP-FHS-12` | `W1→W3` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E23 | `WP-FHS-16 → WP-FHS-13` | `W0→W3` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E24 | `WP-FHS-17 → WP-FHS-13` | `W1→W3` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E25 | `WP-FHS-09 → WP-FHS-14` | `W2→W4` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E26 | `WP-FHS-19 → WP-FHS-14` | `W0→W4` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E27 | `WP-FHS-00 → WP-FHS-15` | `W0→W0` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E28 | `WP-FHS-00 → WP-FHS-16` | `W0→W0` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E29 | `WP-FHS-00 → WP-FHS-17` | `W0→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E30 | `WP-FHS-02 → WP-FHS-17` | `W1→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E31 | `WP-FHS-03 → WP-FHS-17` | `W1→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E32 | `WP-FHS-08 → WP-FHS-18` | `W2→W2` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E33 | `WP-FHS-00 → WP-FHS-19` | `W0→W0` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E34 | `WP-FHS-05 → WP-FHS-20` | `W1→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E35 | `WP-FHS-16 → WP-FHS-20` | `W0→W1` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |
| E36 | `WP-FHS-01 → WP-FHS-21` | `W0→W0` | 原結構邊保持；操作消耗前置 Raw/ACK 時為 **Hard**，僅可同波合法並行讀取的為 **Soft**；需要原 Reader 核定具體 operation |

### W0-A 六 WP 具體执行順序與 W0-B 接線證據

| Step／WP | 原真正操作 | 輸入 → 具名 Output | 可見驗證、NEG／FirstFail | 停止/恢復 |
|---|---|---|---|---|
| 1／WP00 | 唯讀 31 source + Fabric→SBL→HGK Git remote 和原持有權限 | Root+SourceRefs → SHA Manifest/RemoteHeadRecord | 31/31 bit check；NEG 以 remote HEAD 冒 local HEAD → `LOCAL_REPO_CONTEXT_HOLD` | 差異 Scope PARK；其他讀取繼續 |
| 2／WP01 | 原 Authority/Oracle/Profile 之**設計候選** | SourceManifest/QuestionLedger → SourceConflict+ProfileBinding Request | POS 來源衝突列明；NEG 自發 SourceFreeze → `SOURCE_CURRENTNESS_HOLD` | 待 Original Reader ACK，不阻 Draft |
| 3／WP15 | TPM Product/System/Program 18 Stage 有界編製 | Goal + KnownAnswer + OriginalID → 三不同 SPECDraft + TaskSpecSeed candidate | POS 三 SPEC各具 ACC±/相同 Subject；NEG 三合一→`SPEC_NOT_SOURCE_BOUND` | 隔離 Draft 快照、重用已知答案 |
| 4／WP16 | 24 Donor＋25 Method 原處置分流 | OriginalSlotID+Need+Host → `BuildOrUseRecipe@design` | POS 逐 ID 原處置和負例；NEG `REFERENCE_ONLY` 當已安裝→`CAPABILITY_GAP_HOLD` | 只受影 Tool 綁定 PARK |
| 5／WP19 | 唯讀 License/NOTICE/SBOM/secret baseline | Repo snapshot, manifest → `ScanExpectation`+原 Stdout/exit placeholders | POS 真 License 表、未見就 HOLD；NEG 空檔充 PASS→`SUPPLY_CHAIN_RAW_MISSING` | 後波原 CI/Publisher 使用實際 Run Raw |
| 6／WP21 | 96 Original Oracle/H4/SEAM 計畫 | Original CaseID+Reader+NEG → `PlannedCaseFixture`、RunnerBindingRequest | POS 96 case identity 可重算；NEG 無 Runner 就報 Independent PASS→`ORACLE_RUNNER_BIND_HOLD` | 保持 `PLAN_NOT_RUN`，交 W2/W3 原 Checker |

**W0-B `WP-FHS-06` Walking Skeleton**：本波只提供下表之預期接線，**實作 primary=W2**。過 W1 `WP02/03/04/05/17` 的真正 same-Subject Original Reader/Receiver 授權後，由 W2 Codex bounded Worker 在 exact RepoContext 做可逆 DEV diff；原 Hermes Queue/Lease/Journal 記 WorkID，WorldRaw 交 Protected Checker，不使用本 MD 虛構受保護事件。若原操作已 admitted，同 WorkID Resume 高於新包啟動。
| Phase | 必要原 Producer／Writer | 真 ABI/Reader／Consumer | 受影輸入與預期 Output | POS / NEG / FirstFail / Reversible Exit |
|---|---|---|---|---|
| S1 W0 | SBL TPM PM/SE/TPgM | Original SBL Product/Program/PIPD Intake Reader | Ordinary Goal+SBL14/FHS17 SourceRefs→3 SPECDraft | POS 具 FUO+ACC±；NEG 雙轉 Canonical PI→SPEC_NOT_SOURCE_BOUND；可刪隔離 Draft |
| S2 W1 | Original PIPD Intake/PI Writer | Current original PIPD DOC02 Compiler+Authority/Profile Reader | IntentCard+SourceFreeze ACK+ProfileBinding→PI candidate and real original Consumer ACK | POS 原 5 namespace/Parent/NEG intact；NEG `_profile_meta` schema → PI_SCHEMA_NACK；無 ACK 則不 promotion |
| S3 W1 | Original PD/ECP Writer | Original RepoContext/Effect Registry/ECP Reader | Live Git root/HEAD/ACL/exact preimages+PI→PD/ECP/ConstructionContract | POS real Repo bind；NEG stale HEAD/out-of-scope→REPO_BIND_HOLD；不寫世界 |
| S4 W1→W2 | Fabric Policy Owner + HGK Original Issuer | ActiveEpoch/LoadedDigest+HGK Registry/SharedSpine/Issuer | Scoped OPS/DEV intent→original Admission/WorkID/Lease/Journal | POS exact token/cas；NEG source/epoch mismatch→ADMISSION_NACK；無 permit 先 park |
| S5 W2 | Original Hermes bounded Worker/World Receiver | Original WorldRaw + Protected Checker/Publisher | Scoped reversible GJ02 effect+RunRaw→independent Verdict/repair loop | POS world diff/rollback/negative tested；NEG fake raw/signer→INDEPENDENCE_NACK；UNKNOWN先 reconcile |

### L3 五波三稿唯一 WriteSet 與交接

| 波 | `藍圖&skeleton` 唯一 Writer | `草案` 唯一 Writer | `定案` 唯一 Writer | 接收條件／HOLD |
|---|---|---|---|---|
| W0 | W0:WaveCurator | W0:DraftMaker | W0:DesignCurator | 31 Source+三 SPEC+22/36+POS/NEG、`AUTHOR_FINAL_SCOPED`≠正式 Reader ACK |
| W1 | W1:WaveCurator | W1:DraftMaker | W1:DesignCurator | 原 PI/PD/Policy/HGK/Host 受影 Registry/Reader；缺 original ACK park effect |
| W2 | W2:WaveCurator | W2:DraftMaker | W2:DesignCurator | 合法最小 GJ02 world effect/WorldRaw/independent qualification |
| W3 | W3:WaveCurator | W3:DraftMaker | W3:DesignCurator | 949/192/282/485 等全量分母應用分流、Fresh PID W18 UAT、NoFit 專案範圍 |
| W4 | W4:WaveCurator | W4:DraftMaker | W4:DesignCurator | Original Consumer、Protected Checker、Publisher 的正式 Cutover/rollback，不靠文件完成 |

### r3 精簡 Envelope 已由 r4 L2 §8.2 完整交接型態取代


### r4 受影 L3→W1 完整文件 Handoff Envelope（依 L2 r4 §8.2，不擅改 Original JSON）

下列可機器解析 YAML 是 **作者端設計交接投影**。SHA 是實體 bytes；`design_candidate_id` 由非自我引用的來源+scope seed 計算（可重算），非原 PIPD `subject_id`；`OriginalID` 如原 Reader 尚未核出則明確 `HOLD`，禁止虛構。多個候選 SpecClauseID 是作者端明示，不會作新 Canonical `$id`。原受影 Consumer 讀回或回具名 NACK 後才可 promotion。

```yaml
artifact_class: L3_WAVE_DESIGN_ONLY
wave_id: FHS_PKG_WAVE_000
artifact_id: FHS-PIPD-LS-PKG-L3-W0-20261104-R4-FULL-DESTRUCTIVE-AUDIT-REPAIRED
version: 2026-11-04_r4_HIGH_RETENTION_FULL_DESTRUCTIVE_AUDIT_REPAIR
source:
  upper_l0_effective: {artifact_id: FHS-MASTER-BLUEPRINT-2026-11-04-R4-DESTRUCTIVE-AUDIT-REPAIRED, version: r4, sha256: "7befcac3570caf9e1ade2ed231bd04de6a561f9b3038fef89597233f3566b75d"}
  upper_l1_effective: {artifact_id: FHS-PIPD-LS-PKG-L1-2026-11-04-r4-AUDIT-REPAIRED, version: r4, sha256: "cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b"}
  this_l2_effective: {artifact_id: FHS-PIPD-LS-PKG-ALL-WAVES-BLUEPRINT-2026-11-04-r4, version: r4, sha256: "bb970a439fe31faf23e86c054f6282e538d369b84841d778e3b35b69ce5d4d37"}
  original_source_manifest_sha: "bb2fce3e593c189d236cf8c353b8d149356ca294398fdf6ad407a3c4fe6399f4"
  original_requirement_refs:
    - {source_id: SBL-DOC-01, source_sha: "43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f", byte_start: 106437, byte_end: 106823, original_id: SOURCE_CONTEXT_ORIGINAL_ID_OWNER_HOLD, parent_neg_scope: ORIGINAL_READER_PENDING, applicability: AUTHOR_READ_DRAFT_ONLY}
  design_obligation_refs:
    - {id: INT-01, source: L1-r4:L769, positive: KnownAnswer_same_scope_reuse, negative: stale_or_repeat_question, original_consumer: SBL_Product_Reader}
    - {id: FHS-DR-003, source: L1-r4:L800, positive: three_distinct_SPECs, negative: same_body_three_titles, original_consumer: Original_TPM_SPEC_Reader}
    - {id: FHS-DR-054, source: L1-r4:L851, positive: semantic_source_or_scoped_HOLD, negative: keyword_hit_as_full_U1, original_consumer: Original_Semantic_Reader}
  original_reader_ack_or_affected_hold: ORIGINAL_READER_ACK_UNOBSERVED
  historical_lineage: {r3_body_sha256: "de49af389b2806bc6137b9f070605a11cafac565e61b7825e23710af70f6e4fd", r3_appendix_sha256: "ec2eef481473d654f91512c041e497d451f8a48f3d546e4ccf4da682ca6f76aa"}
identity:
  subject_id: AUTHOR_W0_DEMO_SUBJECT__ORIGINAL_PIPD_UNBOUND
  design_candidate_id: "9f6a506cb9f8b2bb64a5973d5ddf680c612966bf7d1c77180d5332bc2eeeb7b7"
  original_writer: {product: SBL_Product, pi_pd_ecp_tqaep: SBL_integrations_pipd, native_admission: HGK_Original}
  author_writer: FHS_W0_L3_WAVE_CURATOR
  affected_scope: {effects: [SOURCE_READ, LOCAL_DRAFT_WRITE], write_set: ISOLATED_W0_AUTHOR_DESIGN_ONLY, world_write: NOT_ADMITTED}
program:
  wp_refs: ["WP-FHS-00", "WP-FHS-01", "WP-FHS-15", "WP-FHS-16", "WP-FHS-19", "WP-FHS-21"]
  original_dep_edge_refs: ["E01", "E02", "E03", "E04", "E05", "E11", "E12", "E16", "E20", "E23", "E26", "E27", "E28", "E29", "E33", "E35", "E36"]
  primary_fuo: Owner_reads_and_edits_three_distinct_source_bound_SPEC_drafts
  expected_effects: [SOURCE_READ, LOCAL_DRAFT_WRITE]
  future_effects_not_admitted_here: [DEV_REPO_WRITE, HOST_OPS, USER_EFFECT, RELEASE_EFFECT]
  acceptance:
    positive: [three_distinct_SPECDraft_bytes, original_source_span_or_typed_HOLD, inverse_OriginalID_SpecClauseID_Case_trace]
    negative: [no_unobserved_OriginalWriter_ACK, no_WP06_world_effect_claim, no_generic_96_Oracle_PASS]
    firstfail: [SPEC_TRACE_BROKEN, ORIGINAL_READER_ACK_UNOBSERVED, EDGE_EFFECT_READER_UNBOUND]
    reader: Original_SBL_TPM_and_PIPD_Intake_Reader__HOST_PENDING
  artifact_claim_ceiling: AUTHOR_DESIGN_ONLY
  native_receipt: EXPECTED_NOT_OBSERVED
  checker_receipt: NOT_RUN
  release: NOT_GRANTED
  holds:
    - {id: ORIGINAL_READER_ACK_UNOBSERVED, scope: Original_Source_Currentness, owner: Original_Domain_SourceReader, unblock_predicate: same_scope_original_reader_readback}
    - {id: U0_U4_SEMANTIC_OWNER_HOLD, scope: original_requirement_refs, owner: Original_Semantic_Owner, unblock_predicate: parent_neg_exception_source_span_ack}
    - {id: W1_HOST_BIND_HOLD, scope: PI_PD_Repo_HGK, owner: Original_PIPD_HGK_Host, unblock_predicate: actual_original_host_reader_and_repo_context}
  resume: {same_work_id_if_admitted: true, admitted_work_id: NOT_OBSERVED, first_fail: ORIGINAL_READER_ACK_UNOBSERVED, last_good_source_sha: "bb2fce3e593c189d236cf8c353b8d149356ca294398fdf6ad407a3c4fe6399f4", affected_cone_only: true}
```

**Consumer 讀回拒收契約**：原 W1 Reader 發現 `sha256` 不是 64 hex、`design_obligation_refs` 空、`SpecClauseID` 不可追 `OriginalID` 或具名 HOLD、`reader` 只是推測、波次把 W2 WP06 當 W0 Done、或用 `PINNED_R4` 假 SHA，均回 `L3_HANDOFF_SCHEMA_OR_TRACE_NACK`；保存 LastGoodSourceSHA/ReadSet，局部修補。不存在以本 YAML 自封 Original PIPD PI/PD/ECP 或 Host Permit 的路徑。

### r4 E01～E36 Operation-level Readiness Overlay（F-009；不改原 DAG／不成第二排程器）
下表是原 36 條結構邊逐邊的**候選操作級接收指引**：只有原 Operator/Effect Registry/Consumer Reader 才能將具體某次 operation 決定為 `HARD_EFFECT_READBACK` 或 `SOFT_READ_ONLY`。當來源是合法 READ/DRAFT 且只依源檔可用即可執行時，不依賴未來 Native Receipt；任何消耗真效果的邊必在原 Consumer ACK 前 `EDGE_EFFECT_READER_UNBOUND`。
| Edge | 原結構 Producer→Consumer | 主波 | no-ACK ready_when | hard_effect_when (original) | soft_when／FirstFail／resume |
|---|---|---|---|---|---|
| E01 | `WP-FHS-00`→`WP-FHS-01` | W0→W0 | 讀 `WP-FHS-00` 的 SourceSHA/已授權隔離 Draft／作者版 SpecClauseRef；不要求未來 WorldRaw | 當 `WP-FHS-01` 對 `WP-FHS-00` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-01` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E01` 與 LastGood，受影 cone 恢復 |
| E02 | `WP-FHS-01`→`WP-FHS-02` | W0→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-01` 的未來效果當已完成 | 當 `WP-FHS-02` 對 `WP-FHS-01` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-02` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E02` 與 LastGood，受影 cone 恢復 |
| E03 | `WP-FHS-01`→`WP-FHS-03` | W0→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-01` 的未來效果當已完成 | 當 `WP-FHS-03` 對 `WP-FHS-01` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-03` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E03` 與 LastGood，受影 cone 恢復 |
| E04 | `WP-FHS-00`→`WP-FHS-04` | W0→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-00` 的未來效果當已完成 | 當 `WP-FHS-04` 對 `WP-FHS-00` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-04` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E04` 與 LastGood，受影 cone 恢復 |
| E05 | `WP-FHS-01`→`WP-FHS-05` | W0→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-01` 的未來效果當已完成 | 當 `WP-FHS-05` 對 `WP-FHS-01` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-05` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E05` 與 LastGood，受影 cone 恢復 |
| E06 | `WP-FHS-02`→`WP-FHS-06` | W1→W2 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-02` 的未來效果當已完成 | 當 `WP-FHS-06` 對 `WP-FHS-02` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK；`WP-FHS-06` DEV effect 需 W1 原 PI/PD/RepoContext/Permit/原 Receiver 層級完整，W2 實作前不得READY | 對受影 `WP-FHS-06` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E06` 與 LastGood，受影 cone 恢復 |
| E07 | `WP-FHS-03`→`WP-FHS-06` | W1→W2 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-03` 的未來效果當已完成 | 當 `WP-FHS-06` 對 `WP-FHS-03` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK；`WP-FHS-06` DEV effect 需 W1 原 PI/PD/RepoContext/Permit/原 Receiver 層級完整，W2 實作前不得READY | 對受影 `WP-FHS-06` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E07` 與 LastGood，受影 cone 恢復 |
| E08 | `WP-FHS-04`→`WP-FHS-06` | W1→W2 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-04` 的未來效果當已完成 | 當 `WP-FHS-06` 對 `WP-FHS-04` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK；`WP-FHS-06` DEV effect 需 W1 原 PI/PD/RepoContext/Permit/原 Receiver 層級完整，W2 實作前不得READY | 對受影 `WP-FHS-06` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E08` 與 LastGood，受影 cone 恢復 |
| E09 | `WP-FHS-05`→`WP-FHS-06` | W1→W2 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-05` 的未來效果當已完成 | 當 `WP-FHS-06` 對 `WP-FHS-05` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK；`WP-FHS-06` DEV effect 需 W1 原 PI/PD/RepoContext/Permit/原 Receiver 層級完整，W2 實作前不得READY | 對受影 `WP-FHS-06` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E09` 與 LastGood，受影 cone 恢復 |
| E10 | `WP-FHS-17`→`WP-FHS-06` | W1→W2 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-17` 的未來效果當已完成 | 當 `WP-FHS-06` 對 `WP-FHS-17` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK；`WP-FHS-06` DEV effect 需 W1 原 PI/PD/RepoContext/Permit/原 Receiver 層級完整，W2 實作前不得READY；WP17 Host 安裝由原 OPS/Installer 決定，不可反向依賴 WP06 的未來 Receipt | 對受影 `WP-FHS-06` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E10` 與 LastGood，受影 cone 恢復 |
| E11 | `WP-FHS-01`→`WP-FHS-07` | W0→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-01` 的未來效果當已完成 | 當 `WP-FHS-07` 對 `WP-FHS-01` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-07` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E11` 與 LastGood，受影 cone 恢復 |
| E12 | `WP-FHS-15`→`WP-FHS-07` | W0→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-15` 的未來效果當已完成 | 當 `WP-FHS-07` 對 `WP-FHS-15` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-07` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E12` 與 LastGood，受影 cone 恢復 |
| E13 | `WP-FHS-06`→`WP-FHS-08` | W2→W2 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-06` 的未來效果當已完成 | 當 `WP-FHS-08` 對 `WP-FHS-06` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK；`WP-FHS-06` DEV effect 需 W1 原 PI/PD/RepoContext/Permit/原 Receiver 層級完整，W2 實作前不得READY | 對受影 `WP-FHS-08` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E13` 與 LastGood，受影 cone 恢復 |
| E14 | `WP-FHS-07`→`WP-FHS-08` | W1→W2 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-07` 的未來效果當已完成 | 當 `WP-FHS-08` 對 `WP-FHS-07` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-08` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E14` 與 LastGood，受影 cone 恢復 |
| E15 | `WP-FHS-08`→`WP-FHS-09` | W2→W2 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-08` 的未來效果當已完成 | 當 `WP-FHS-09` 對 `WP-FHS-08` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-09` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E15` 與 LastGood，受影 cone 恢復 |
| E16 | `WP-FHS-21`→`WP-FHS-09` | W0→W2 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-21` 的未來效果當已完成 | 當 `WP-FHS-09` 對 `WP-FHS-21` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-09` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E16` 與 LastGood，受影 cone 恢復 |
| E17 | `WP-FHS-09`→`WP-FHS-10` | W2→W3 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-09` 的未來效果當已完成 | 當 `WP-FHS-10` 對 `WP-FHS-09` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-10` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E17` 與 LastGood，受影 cone 恢復 |
| E18 | `WP-FHS-20`→`WP-FHS-10` | W1→W3 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-20` 的未來效果當已完成 | 當 `WP-FHS-10` 對 `WP-FHS-20` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-10` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E18` 與 LastGood，受影 cone 恢復 |
| E19 | `WP-FHS-05`→`WP-FHS-11` | W1→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-05` 的未來效果當已完成 | 當 `WP-FHS-11` 對 `WP-FHS-05` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-11` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E19` 與 LastGood，受影 cone 恢復 |
| E20 | `WP-FHS-16`→`WP-FHS-11` | W0→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-16` 的未來效果當已完成 | 當 `WP-FHS-11` 對 `WP-FHS-16` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-11` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E20` 與 LastGood，受影 cone 恢復 |
| E21 | `WP-FHS-10`→`WP-FHS-12` | W3→W3 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-10` 的未來效果當已完成 | 當 `WP-FHS-12` 對 `WP-FHS-10` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-12` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E21` 與 LastGood，受影 cone 恢復 |
| E22 | `WP-FHS-11`→`WP-FHS-12` | W1→W3 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-11` 的未來效果當已完成 | 當 `WP-FHS-12` 對 `WP-FHS-11` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-12` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E22` 與 LastGood，受影 cone 恢復 |
| E23 | `WP-FHS-16`→`WP-FHS-13` | W0→W3 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-16` 的未來效果當已完成 | 當 `WP-FHS-13` 對 `WP-FHS-16` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-13` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E23` 與 LastGood，受影 cone 恢復 |
| E24 | `WP-FHS-17`→`WP-FHS-13` | W1→W3 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-17` 的未來效果當已完成 | 當 `WP-FHS-13` 對 `WP-FHS-17` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK；WP17 Host 安裝由原 OPS/Installer 決定，不可反向依賴 WP06 的未來 Receipt | 對受影 `WP-FHS-13` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E24` 與 LastGood，受影 cone 恢復 |
| E25 | `WP-FHS-09`→`WP-FHS-14` | W2→W4 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-09` 的未來效果當已完成 | 當 `WP-FHS-14` 對 `WP-FHS-09` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-14` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E25` 與 LastGood，受影 cone 恢復 |
| E26 | `WP-FHS-19`→`WP-FHS-14` | W0→W4 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-19` 的未來效果當已完成 | 當 `WP-FHS-14` 對 `WP-FHS-19` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-14` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E26` 與 LastGood，受影 cone 恢復 |
| E27 | `WP-FHS-00`→`WP-FHS-15` | W0→W0 | 讀 `WP-FHS-00` 的 SourceSHA/已授權隔離 Draft／作者版 SpecClauseRef；不要求未來 WorldRaw | 當 `WP-FHS-15` 對 `WP-FHS-00` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-15` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E27` 與 LastGood，受影 cone 恢復 |
| E28 | `WP-FHS-00`→`WP-FHS-16` | W0→W0 | 讀 `WP-FHS-00` 的 SourceSHA/已授權隔離 Draft／作者版 SpecClauseRef；不要求未來 WorldRaw | 當 `WP-FHS-16` 對 `WP-FHS-00` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-16` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E28` 與 LastGood，受影 cone 恢復 |
| E29 | `WP-FHS-00`→`WP-FHS-17` | W0→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-00` 的未來效果當已完成 | 當 `WP-FHS-17` 對 `WP-FHS-00` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK；WP17 Host 安裝由原 OPS/Installer 決定，不可反向依賴 WP06 的未來 Receipt | 對受影 `WP-FHS-17` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E29` 與 LastGood，受影 cone 恢復 |
| E30 | `WP-FHS-02`→`WP-FHS-17` | W1→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-02` 的未來效果當已完成 | 當 `WP-FHS-17` 對 `WP-FHS-02` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK；WP17 Host 安裝由原 OPS/Installer 決定，不可反向依賴 WP06 的未來 Receipt | 對受影 `WP-FHS-17` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E30` 與 LastGood，受影 cone 恢復 |
| E31 | `WP-FHS-03`→`WP-FHS-17` | W1→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-03` 的未來效果當已完成 | 當 `WP-FHS-17` 對 `WP-FHS-03` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK；WP17 Host 安裝由原 OPS/Installer 決定，不可反向依賴 WP06 的未來 Receipt | 對受影 `WP-FHS-17` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E31` 與 LastGood，受影 cone 恢復 |
| E32 | `WP-FHS-08`→`WP-FHS-18` | W2→W2 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-08` 的未來效果當已完成 | 當 `WP-FHS-18` 對 `WP-FHS-08` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-18` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E32` 與 LastGood，受影 cone 恢復 |
| E33 | `WP-FHS-00`→`WP-FHS-19` | W0→W0 | 讀 `WP-FHS-00` 的 SourceSHA/已授權隔離 Draft／作者版 SpecClauseRef；不要求未來 WorldRaw | 當 `WP-FHS-19` 對 `WP-FHS-00` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-19` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E33` 與 LastGood，受影 cone 恢復 |
| E34 | `WP-FHS-05`→`WP-FHS-20` | W1→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-05` 的未來效果當已完成 | 當 `WP-FHS-20` 對 `WP-FHS-05` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-20` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E34` 與 LastGood，受影 cone 恢復 |
| E35 | `WP-FHS-16`→`WP-FHS-20` | W0→W1 | 可獨立做已准的 SOURCE_READ/LOCAL_DRAFT_WRITE；不得藉 `WP-FHS-16` 的未來效果當已完成 | 當 `WP-FHS-20` 對 `WP-FHS-16` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-20` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E35` 與 LastGood，受影 cone 恢復 |
| E36 | `WP-FHS-01`→`WP-FHS-21` | W0→W0 | 讀 `WP-FHS-01` 的 SourceSHA/已授權隔離 Draft／作者版 SpecClauseRef；不要求未來 WorldRaw | 當 `WP-FHS-21` 對 `WP-FHS-01` 的 original output/HostLoaded/RepoContext/WorldRaw/ACK 真實依賴，必原 Reader 綁定並有同 Subject/Scope receipt；否則 PARK | 對受影 `WP-FHS-21` 子 operation 逐欄查 required Consumer、source SHA、expected readback；SOFT 僅合法獨立 READ；UNKNOWN→World Reconcile；`EDGE_EFFECT_READER_UNBOUND`，保留 `E36` 與 LastGood，受影 cone 恢復 |

**反循環**：`WP-FHS-15` W0 三 SPEC 可在 W2 WP06 世界 Receipt 缺席時完成；WP06 W2 受影前置不滿則只 PARK；`WP-FHS-17` 原 Host install 不藉 WP06 假收據反向滿足。變更 original edge identity/PrimaryWave 即 `ORIGINAL_DAG_EDGE_MISMATCH`，不得自建 scheduler。

### r4-candidate｜E26 與六個 W0 主責 WP 的逐操作綁定（D1 收斂；機器投影 `PROGRAM_WP22_DAG36.json` → `operation_binding`）

r3 的 `PROGRAM_WP22_DAG36.json` 36 條邊只有**單一** `type_rule` 字串，`expected_source_raw`／`original_consumer`／`firstfail` 出現 0 次；機器讀者因此無法驗證 E26 的「接 WP19 原 Raw、不接 TraceClosure」。本節把上表投影成機器可讀的 `operation_binding`，**原 22 WP／36 Edge ID 與波次完全不動**，也不新增第二排程器或第二 Queue。

- `binding_state` 只有兩種：`AUTHOR_STATIC_READY`（本波可靜態驗的操作敘述）與 `ABI_BIND_HOLD`（需原 Operator/Effect Registry/Consumer Reader 才可核定的 operation）。
- **本表不代替原 ACK**：每列的 `original_reader_ack` 一律 `NOT_OBSERVED`，除非未來由原 Reader 以同 Subject/Scope 真 Raw 回填。
- `E26` 的三個拒收點：只交 TraceClosure＝`WP19_ORIGINAL_OUTPUT_MISSING`；刪除 E26 邊＝`ORIGINAL_DAG_EDGE_MISSING`；把 `WP-FHS-19.primary_wave` 改成 W4 以配合交付波＝`WAVE_PRIMARY_CONFLATION`。

| Edge | Producer→Consumer | 主波 | operation（作者端敘述） | expected_source_raw | original_consumer | blocking_rule（Hard 條件） | soft_safe_condition | firstfail | next_reader |
|---|---|---|---|---|---|---|---|---|---|
| E01 | `WP-FHS-00`→`WP-FHS-01` | W0→W0 | 以 `SourceManifest`（31 Source＋22 Upper 的 path/SHA/bytes）與 `RepoContext` readback 餵 AuthorityBinding 綁定 | `SourceManifest` 逐檔 SHA/bytes；`RepoContext` 的 root／HEAD／dirty／ACL 實讀值 | 原 TPM/PIPD Source Reader（Source 冊＋Authority 冊） | Hard 僅當 WP-FHS-01 實質消費 WP-FHS-00 的 Host／ACL 事實；純結構傳遞為 Soft | 同波合法並行 SOURCE_READ，不要求未來 WorldRaw | `EDGE_EFFECT_READER_UNBOUND` | 原 原 TPM/PIPD Source Reader（Source 冊＋Authority 冊） 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E04 | `WP-FHS-00`→`WP-FHS-04` | W0→W1 | 以 SourceFreeze 清冊餵 31 冊 Currentness／AuthorityBinding 章節 | `SOURCE31_PHYSICAL_IDENTITY.json` 31 筆的 path/SHA/bytes，逐筆可開 | 原 SBL/FHS 31 冊 Source Reader | Hard 當章節主張 currentness 需要原 Source Reader 回讀；僅引用 locator 為 Soft | 可先用已驗 SHA 做索引，不宣 currentness PASS | `EDGE_EFFECT_READER_UNBOUND` | 原 原 SBL/FHS 31 冊 Source Reader 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E11 | `WP-FHS-01`→`WP-FHS-07` | W0→W1 | AuthorityBinding／ProfileBinding 餵 U2–U4 crosswalk 與 Owner 語義核簽章 | 原 19-schema Registry 的 binding 原 bytes；`UPPER22_PHYSICAL_IDENTITY` 對應冊 | 原 Authority/Profile Owner → 原 PIPD `compile-pi` Reader | Hard：U4 核簽欄位必須由原 Owner 回，不得由作者文件自填 | U0–U3 的檔案身份可先驗，U4 保持 NOT_OBSERVED | `EDGE_EFFECT_READER_UNBOUND` | 原 原 Authority/Profile Owner → 原 PIPD `compile-pi` Reader 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E12 | `WP-FHS-15`→`WP-FHS-07` | W0→W1 | 三份異質 SPEC（Product/Architecture/Program）條款餵 crosswalk 的 U 級對映 | 三份 SPEC 的 same-Subject 鍵、FUO/ACC±／ABI/SoD／DAG 各自欄位 bytes | 原 SBL TPM Producer/Owner 閱讀三 SPEC | Hard 當 crosswalk 主張某 U 級已由原義支撐 | 三 SPEC 同 Subject 但不同欄位，可靜態驗 | `EDGE_EFFECT_READER_UNBOUND` | 原 原 SBL TPM Producer/Owner 閱讀三 SPEC 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E16 | `WP-FHS-21`→`WP-FHS-09` | W0→W2 | Oracle96／H4／SEAM 原計畫餵 Case↔Oracle 對映（96 typed） | `ORACLE96_CONTRACTS.json` 96 筆 Class/Oracle/Parent/NEG/typed fixture；原 CaseRegistry 分波 Handoff | 原 Acceptance/Oracle Owner → 原 Protected AO Request Reader | Hard：任何 Case 進 PASS 需原 Runner Raw；W0 只給作者端計畫 | 96 typed 契約可靜態辨識，Runner 未綁記 RUNNER_UNBOUND | `EDGE_EFFECT_READER_UNBOUND` | 原 原 Acceptance/Oracle Owner → 原 Protected AO Request Reader 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E20 | `WP-FHS-16`→`WP-FHS-11` | W0→W1 | Donor24／Method25 的 49 recipe 翻譯餵 Build-or-Use／版本准入章 | `WP16_TRANSLATION49.json` 49 筆原身份、License、Consumer、translation | 原 SBL DOC06 TechnologyAdmission Owner → 各受影 Consumer | Hard：Method 不得當可安裝 Skill；未知 Host/License 局部 HOLD | 49 recipe 原身份可讀，Selected 才展開 | `EDGE_EFFECT_READER_UNBOUND` | 原 原 SBL DOC06 TechnologyAdmission Owner → 各受影 Consumer 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E23 | `WP-FHS-16`→`WP-FHS-13` | W0→W3 | 49 recipe 的原 Consumer/License 投影餵 Profile Tailoring 與晚綁 | 同上 49 筆；Profile 側的原 slot/role 對映 | 原 Profile Tailoring Owner／原 TPM-PIPD Reader | Hard：晚綁不得越過 RepoContext 原 Reader | 未受影 recipe 可冷保留 locator | `EDGE_EFFECT_READER_UNBOUND` | 原 原 Profile Tailoring Owner／原 TPM-PIPD Reader 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E26 | `WP-FHS-19`→`WP-FHS-14` | W0→W4 | **WP19 的 CI／License／NOTICE／SBOM 原掃描 Raw 作為 WP14 Release 候選的供應鏈前置**；W0 只出設計契約與 typed 期望值，不產生也不替代該 Raw | 原 CI run receipt、License／NOTICE 檔、SBOM（CycloneDX／SPDX）原 bytes＋SHA；**作者端 TraceClosure 不在可接受清單內** | 原 CI/SupplyChain Reader → 原 release-readiness Reader → 原 Publisher/受保護 Checker | Hard：WP14 的 `RELEASE` effect 必須有同 Subject／Scope 的原 CI Raw 與原 Publisher 收據；只交 TraceClosure 即標 WP19 DONE 為拒收 | W0 可 `SOURCE_READ` 讀既有 CI Raw、可寫隔離設計草案；不得把 W0 Trace 當供應鏈 PASS | `EDGE_EFFECT_READER_UNBOUND` | 原 原 CI/SupplyChain Reader → 原 release-readiness Reader → 原 Publisher/受保護 Checker 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E27 | `WP-FHS-00`→`WP-FHS-15` | W0→W0 | SourceManifest 餵 TPM corpus 與三 SPEC 18-Stage 契約 | WP-FHS-00 的 SourceSHA 與已授權隔離 Draft／作者版 SpecClauseRef | 原 TPM Corpus Reader/PM/SE/TPgM → 原 PIPD Intake | Hard 當三 SPEC 主張引用原 Source 語義；僅引用 SHA 為 Soft | 同波可並行，不需未來 WorldRaw | `EDGE_EFFECT_READER_UNBOUND` | 原 原 TPM Corpus Reader/PM/SE/TPgM → 原 PIPD Intake 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E28 | `WP-FHS-00`→`WP-FHS-16` | W0→W0 | SourceManifest 餵 24 Donor Slot／25 Method 的原始 slot 定位 | WP-FHS-00 的 SourceSHA＋原 DOC06 slot 清冊 locator | 原 SBL DOC06 TechnologyAdmission Owner | Hard 當 slot 翻譯主張原 slot 語義；索引層為 Soft | unknown Host/License 局部 HOLD | `EDGE_EFFECT_READER_UNBOUND` | 原 原 SBL DOC06 TechnologyAdmission Owner 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E29 | `WP-FHS-00`→`WP-FHS-17` | W0→W1 | SourceManifest 餵 Host／CLI／Plugin 三段驗收的設計輸入 | WP-FHS-00 的 RepoContext／Host 事實；**GitHub remote main 不可是本地 HEAD 的替代** | 原 Host/Installer Reader（原 OPS 面） | Hard：Host 安裝由原 OPS/Installer 決定，不可反向依賴 WP06 未來 Receipt | 設計層可先行，Host Loaded 保持 NOT_OBSERVED | `EDGE_EFFECT_READER_UNBOUND` | 原 原 Host/Installer Reader（原 OPS 面） 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E33 | `WP-FHS-00`→`WP-FHS-19` | W0→W0 | SourceManifest 餵 CI/Supply-Chain 掃描的輸入清冊 | WP-FHS-00 的 SourceSHA；CI 側需原 pipeline 定義與 raw run id | 原 CI/supply-chain Reader | Hard 當掃描主張覆蓋率或結論；清冊傳遞為 Soft | 無原 CI Raw 時只 HOLD 供應鏈結論 | `EDGE_EFFECT_READER_UNBOUND` | 原 原 CI/supply-chain Reader 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E35 | `WP-FHS-16`→`WP-FHS-20` | W0→W1 | 49 recipe 的技術選型餵 Native Kanban/Delegation 編排章 | `WP16_TRANSLATION49.json` 的 Selected recipe 與其 Consumer | 原 Hermes Host/Profile Reader | Hard 當編排主張某 recipe 已在 Host 生效 | 編排設計可先行，Loaded 保持 NOT_OBSERVED | `EDGE_EFFECT_READER_UNBOUND` | 原 原 Hermes Host/Profile Reader 回同 Subject/Scope 的 ACK 或 scoped HOLD |
| E36 | `WP-FHS-01`→`WP-FHS-21` | W0→W0 | Authority/Oracle/Profile binding 餵 96 Oracle 與 H4 的 Case 綁定 | WP-FHS-01 的 `Oracle/ProfileBinding` 原 bytes 與 96 案的 Class/Oracle 對映 | 原 Acceptance/Oracle Owner | Hard：Oracle 型別不得由作者端改寫；綁定需原 Reader 核 | 同波可並行，96 typed 契約靜態可驗 | `EDGE_EFFECT_READER_UNBOUND` | 原 原 Acceptance/Oracle Owner 回同 Subject/Scope 的 ACK 或 scoped HOLD |

**W0 主責六 WP 的 operation 邊界**：`WP-FHS-00`（Source/Host Discovery）、`WP-FHS-01`（Authority/Oracle/Profile）、`WP-FHS-15`（TPM Corpus & SPEC 18Stage）、`WP-FHS-16`（Donor/Method Slot Translation）、`WP-FHS-19`（CI/Supply Chain & Requal）、`WP-FHS-21`（Challenge 96/H4/SEAM Coverage）。六者的 `primary_wave` 一律 `W0`，不得因交付波在後而改主波；`WP-FHS-06` 主波仍 `W2`、`WP-FHS-19` 的原輸出仍是 CI/License/NOTICE/SBOM 四件，TraceClosure 由 `WP-FHS-15`／`WP-FHS-21` 合法承接。

### r4 正交資產類型：具名 Need／Qualified Occupant／退出規範（F-001/F-008）

各 `OriginalAssetID` 的完整原處置、原卡 Owner/NEG 與 immutable SourceLocator 在附錄 `E07` 修復後 **485/485 四欄**可重算表。`Default30` 原 `MANDATED_DEFAULT` 設計義務不可選擇性歸零；`Preferred` 未經原 License/Host Reader 確認只屬候選，`SELECTED→INSTALLED→BOUND→INVOKED→VERIFIED` 必逐層查 Raw，缺者 `CAPABILITY_GAP_HOLD`，不因 W0 作者有已寫名字而自動 installed。

| 原資產型別 | 原 Need→佔位／採納方法 | Host/原 Consumer 真驗證 | 不可做／退出、NEG |
|---|---|---|---|
| CLI / bounded worker | 指定 release digest/License/Host，再由原有 installer install→`--version`/exit→實際 sample invoke | 原 HGK/Hermes Worker Registry、命令輸出、工作時限；僅原受授 Scope | 沒有 CLI 真執行不得 `INVOKED`；撤除原適用安裝並清除隔離狀態，不動其他 Worker |
| LIBRARY | 透過原 dependency manager 釘 commit/lock→import/use→原 Consumer sample | 原 Module Origin／功能結果／SBOM 僅適用需要時 | 禁止當可執行檔假 install；不適用 Host 時 `NOFIT`，按 lock 回退 |
| METHOD_ONLY | 文件/流程轉譯→受權 Skill trigger／步驟輸出→原消費者 | 原方法結果、NEG、Source/Scope trace | 禁止加新 daemon 或要求 binary uninstall；退出為停用候選方法映射／恢復 PreviousRecipe |
| FORMAT / schema | 原 Producer 生成 bytes→版本化 parser/schema→原 Consumer ACK/NACK | 需實體 parse 結果與負例；Schema `$id` 原 Writer 不變 | GitHub Actions workflow、JSON Format 不應一律執行「工具 installer」；輸出不兼容即回退 mapping |
| SKILL / prompt | 原 Skills/Host Loader install 或引用→Host 真 triggered→output/Consumer | 原 Skill Trigger/Invocation/Host Loaded；Prompt 字串不當 Permission | 僅列插件／README 不等於 Loaded；retire 原 Host 注册並 readback |
| GOVERNED_RUNTIME | 使用釘選 Hermes `v0.22.5` 原 launcher/profile／原 Lane Registry | fresh PID、LoadedProfile、actual model served、WorkID/Lease/Journal、Resume | 不建立 shadow Queue，版本不擅自升級，拒絕 test-only profile 冒正式 Runtime |
| NATIVE_SINGLETON / ORIGINAL_OWNER_COMPONENT | 只由原 Domain Owner 的既有 Authority/Registry/Writer 路線變更 | Fabric active epoch、HGK issuer/SharedSpine、SBL/PIPD Canonical Reader | 禁止一般 HotSwap 取代 Issuer、Compiler、Queue、Checker；變更失敗只能交原 Owner rollback |

**四個決策結果**：`QUALIFIED_SAME_SCOPE` 可使用；`QUALIFIED_FALLBACK_SAME_SCOPE` 可依原 Owner/License/Scope 切換；`NOFIT` 只停其 Need／Consumer；`UNKNOWN`/缺 License/Host/Raw 記 `CAPABILITY_GAP_HOLD`。不合格變更只重驗受影 Need/Host/OriginalConsumer，而非重跑 485 件。`REJECT/REFERENCE_ONLY/METHOD_ONLY` 的原處置絕不被「推薦」偷換成必裝。

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：W0-A 與 W0-B 不混波。
- **獨立輸入**：22 原 WP、36 原 Edge、W0 主責 00/01/15/16/19/21、W2 主責 WP06。
- **原有能力導向操作**：W0 合法來源/隔離草稿先達 FUO；36 Edge 逐 operation 投影 ready/no-ACK/Hard-if-effect/Resume；未來 WorldRaw 不列當下前置。
- **可觀察輸出／First Useful Outcome**：ProgramSPEC＋operation readiness overlay＋下一波 typed handoff。
- **原 Reader／Consumer**：Original Program/DAG Reader、W1/W2 WaveCurator。
- **正反驗收與 FirstFail**：POS WP15 不等待 W2 receipt；NEG WP06 缺 W1 Repo/Issuer 仍進 effect → FUTURE_RECEIPT_DEPENDENCY。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-37](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-37)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### W0 Program SPEC｜完整波次、唯一主責與六 WP 可施工工作卡

**不改依賴身份**：以下 W0 六張卡的 `Dependency` 僅引用原 `WP-FHS`，不創建新的 `WP` 編號；36 邊詳附錄。每張的 `Done` 僅指作者可重算的草案完成，不代表 Host effect。

| 原 WP／階段 | Trigger／Input | W0 操作與 Output/FUO | 原 Producer→Consumer | POS／NEG／FirstFail | Stop／Resume |
|---|---|---|---|---|---|
| `WP-FHS-00` W0-A | 普通 Goal、31 Snapshot/三庫導航 | 用唯讀 ACL 掃描 SourceSHA/版本/Host link，輸出 SourceSnapshotLedger+RepoContext **Request** | 原 Source Reader→TPM/PIPD Original Source Reader | POS 31/31；NEG remote Git HEAD 假本機 Git/ACL → `REPO_CONTEXT_UNBOUND` | 未見 Host probe，保留 request，不停 source scan |
| `WP-FHS-01` W0-A | WP00 來源、Authority/Oracle/Profile 資料 | AuthorityConflictLedger、Profile/Oracle **候選**、QuestionLedger | 原 Authority/Profile/Oracle Owner→原 PIPD Compiler W1 | POS Unknown 原 Reader 具名 HOLD；NEG 作者自簽 freeze → `AUTHORITY_PROMOTION_DENY` | Source SHA 變更只重算受影 family |
| `WP-FHS-15` W0-A | Ordinary Goal + Product pain/known answers | 三 SPEC 独立草案、FUO、可重用 Decision Ledger | TPM PM/SE/TPgM 作者→原 SBL Product/PIPD Intake Reader | POS 具原 Consumer/ACC±；NEG YAML 假 canonical PI → `SPEC_AS_CANONICAL_DENY` | 草稿可持續，送原 Reader 待 W1 ACK |
| `WP-FHS-16` W0-A/B | Asset Need/OriginalDisposition、Host/License 需求 | 485 技術身份分流；原 24slot/25method 壓製候選＋選定 Needed Need/Host Qualification Plan；不縮成 485 身份分類 | 原 Tech/License/Host Owner→W1/W3 原 capability consumer | POS 30 default required 不降級；NEG 485 全部標 must-install → `ASSET_CLASS_CONFLATION` | 無 fit 時只 Hold Need、保留 fallback |
| `WP-FHS-19` W0-B | 原 CI/SupplyChain Reader、同 CandidateSHA 的 dependency manifest／License/NOTICE/SBOM source | **僅原 `CI/License/NOTICE/SBOM 掃描Raw` 與其 source-bound Requalification Request**；不得由 Spec/Handoff 假代 | 原 CI/SupplyChain Reader → 原 release-readiness Reader；`E26:WP19→WP14` | POS 真同 CandidateSHA Reader 原 Raw 含 LICENSE/NOTICE/SBOM/dependency scope；NEG 只交 TraceClosure 便宣 WP19 Done → `WP19_ORIGINAL_OUTPUT_MISSING` | 不具原 CI readback 時 `WP19_DONE=HOLD`，只阻 E26/WP14；合法 W0 Spec/READ 繼續 |
| `WP-FHS-21` W0-B | FHS-BODY-07 96 Oracle、六 Ledger | per-case POS/NEG/FirstFail、CasePlan/ExpectedEvidence；不觸發 Protected Checker | Original Case/Oracle Reader→W1/W2 protected checker planner | POS 96 個原 Case 的 Class×Oracle typed precondition/POS/NEG/FirstFail 各異並具原 SourceLine；NEG 交換 HUMAN 與 DETERMINISTIC 的 fixture → `CASE_TYPE_OR_SCOPE_MISMATCH`；缺原 Runner/Raw 仍 `RUNNER_BIND_HOLD` | 未綁 Runner/Raw => `PLAN_NOT_RUN` |

**W0-A 退出**：SRC31 physical verified、Issue/Question Ledger、三 SPEC 的各自 POS/NEG/Consumer、84 card 主波路由及局部 HOLD；可向 W0-B 接線。**W0-B 退出**：S1..S5 Input/Original ABI/Effect/Owner/Expected Raw/NEG/rollback、W1 Typed Envelope、CasePlan；不聲稱任何 protected effect 或 W18 qualified。

**唯一主波**：`W0=WP00/01/15/16/19/21`；`WP06=W2`；依原 DAG `WP06←WP02,03,04,05,17` 待 W1 true binding 及 admit。`W18` 屬 W3 B1 後普通 Goal UAT，不建 W5。已取得原 WorkID 的 admitted work 先以原 Lease/Journal cursor 恢復，禁止草案生成第二 Queue。



### r3 當期條款（保留 r2 正確修補並補差額）｜Original WP19／E26 不改派 + 25 個 Wave Join 語義拆離（AUD-W0-P0-001/003）

**唯一 WP19 原契約**：Trigger=原 `WP00` Source Discovery 並具 `CandidateSHA`；Input=原 CI/License/NOTICE/SBOM/dependency source；Process=原供應鏈 Reader `SOURCE_READ` 確認 license、notice、SBOM、依賴與再資格化差額；Output=`CI/License/NOTICE/SBOM掃描Raw`；Consumer=原 release-readiness Reader；POS=與 E26 交付的 Candidate/SourceSHA 同 Scope 且四類 Raw 可讀；NEG=只有作者 TraceClosure 或三 SPEC 卻填 `WP19 Done=true`，`FirstFail=WP19_ORIGINAL_OUTPUT_MISSING`。無原真 Raw ⇒ `WP19_DONE=HOLD`，只使 `E26 (WP19→WP14)` / W4 Release-ready 受影停工；**W0 Source Read／Draft 不被封鎖**。原 DAG 的 E26 不刪、不重編、不由 W0 Draft 代簽。

**文件交接另外處理**：`W0-DOC-HANDOFF-01` 是**作者端本包內部交付 Task，不是新 WP / Native Queue**；由 WP15 供三 SPEC/Source、WP21 供 CasePlan，再以 S1～S5 接線給 W1 Original Reader；Never credit to WP19.Done/E26。

**84 卡的波次**：E04 `Card.Wave=requirement_delivery_wave`；E06 `WP.primary_wave=wp_primary_wave`；`consumer_verification_wave` 尚未由原 Reader 綁定；25 個不同的 `Card.Wave` 與其 WP 主波只是 `JOIN_AMBIGUOUS`，不可自動改原 22 WP primary wave。見 `W0_R2_DESIGN84_WAVE_JOIN_NORMALIZED.md` 逐 84 卡分欄與 25 個受影 Hold，NEG 將 `FHS-DR-057 W4` 改 `WP19.primary_wave=W4` 即 `WAVE_PRIMARY_CONFLATION`。

### r3 WP19 原 Raw 形狀與 84/25 重驗

WP19 所需的 author ExpectedRaw shape：candidate_sha、source_version、scope、原 CI/license/NOTICE/SBOM/dependency 各 raw_ref+sha256、Original Reader identity、issue_disposition、原 CI/Program Reader ACK；這只是期待，不是本輪生產掃描。只有 TraceClosureRequest 或跨 candidate Raw 即 WP19_ORIGINAL_OUTPUT_MISSING；WP19_DONE=HOLD，E26 WP19→WP14 不放行。WP15/21 承接文檔交接，不新造 WP。DESIGN84_WAVE_JOIN.json 指向原 L1 SHA/物理行，原 r2 normalized 表四 wave/ACK 欄已正確，原 bytes 保留；25 異義由 Original Program Reader 後續 ACK，不改 22 WP 主波。

# CH-38｜最小 Native E2E、GJ01–03、Golden/V2-T 與停止規則

<a id="ch-38"></a>

## r4 當期 L3 合法正文｜`CH-38`：主波 W2（L2 r4 §6）
**W0 非主責，唯一主波是 W2。** `CH-38` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W2 專屬規格與 Native 權威。

**原產品主題／受影接收**：最小 Native E2E、GJ01–03、Golden/V2-T 與停止規則。主波 L3 收件 `W2_藍圖&skeleton → W2_草案 → W2_定案`；原 Consumer：Original E2E/Golden Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W2 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W2_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-03` `L1-r4:L771` | W0 | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) | 短 Goal 可產直接有用答案／SPEC，寫入則需實際 Diff/Host | 只交文件數量、沒有使用者可取用之 FUO，或冒稱 Host 已執行；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-04` `L1-r4:L772` | W0 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、HGK Original Issuer/SharedSpine/Protected Checker Reader、Effect-spe | A 全量產品語義守恆；B 最短合法 Effect 路徑 | 把 A 全量需求全作每次 B READ 的前置 OPS Permit；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-15` `L1-r4:L783` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer、Original Oracle/Protected Checker Reader | POS/NEG/Case/Raw/SourceSHA，符合原 Principal 差異 | Maker 自簽 Independent、沒有實際 Runner Raw 卻宣 PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-17` `L1-r4:L785` | W3 | SBL Product/Kind/Host Original Consumer、SBL Product Owner → CLI Host Consumer、SBL Product Owner → Original Skill/Agent Host Registry Co | GJ01 clean CLI、GJ02 bounded patch、GJ03 live skill invoke | GJ01 只有 SPEC、GJ02 缺 Repo Diff、GJ03 只有 Resume；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-22` `L1-r4:L790` | W3 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | Fresh PID 正常 Goal/Task/E33–E42/合法退出 | W18 用 B1 長 Prompt 或測試專用 Profile 冒真普通 Goal；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-011` `L1-r4:L808` | W3 | SBL Product Owner → CLI Host Consumer | 實際 clean Host 操作與退出 | README-only/假退出碼/錯誤清除外來檔；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-012` `L1-r4:L809` | W2 | SBL RepoContext/PD Reader → HGK Original Issuer → Repo World Reader | 原 Repo Raw/小 diff/test/revert | stale HEAD/skip preimage/wildcard WriteSet；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-013` `L1-r4:L810` | W3 | SBL Product Owner → Original Skill/Agent Host Registry Consumer | Host 真 Invoked + Unloaded | 單 ZIP 存在即宣稱已用；`DESIGN_OBLIGATION_MISSING`（若失卡） |
### W0-B 最短可逆 GJ02：計畫與世界實測的分界
GJ01/W0-A 可以只讀起點；GJ02 的受影可逆世界 WriteSet 只有在 W1 真 RepoContext、PD/DEV ECP、Fabric/HGK original Admission、Hermes 受准入 WorkOrder 具備後進 W2；GJ03/Release 仍各自歸後波原 Consumer。任何示例 diff 不可當受原 Issuer 許可的世界變更。


### W0 草案增補｜跨波原責任保留與准入規劃
### W0-B Walking Skeleton 測試設計（主波 W2，**不得在 W0 執行 GJ02**）

`GJ01` READ-only 原 source/probe，W0 可規劃並在允許範圍測物理讀回；`GJ02` 真實可逆 REPO_WRITE 僅 W2，在 W1 原 PI/PD/RepoContext+DEV ECP、Fabric Active/Loaded、HGK Issuer admit 後執行；`GJ03` live Skill/Plugin invoked 由實際 Host 原 Reader 測。W0 本輪只列 Request/Raw Schema、negative fixture、回滾、原 Consumer、FirstFail。POS 五 Seam 文件每段都明確所需 Receiver；NEG 假 Raw `PASS` 或 `W18` 當施工波 → `NATIVE_RECEIPT_LAUNDERING`。



### r3 當期條款（保留 r2 正確修補並補差額）｜S1～S5 同 Subject 最小 Fixture 與 NEG（AUD-W0-P1-007）

同 Subject `FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001` 的合法**計畫**：`S1` 普通 Goal+31 SourceSHA→三 SPEC；`S2` 原 SBL PIPD Intake/Authority/Profile→PI（`EXECUTOR_UNBOUND`）；`S3` 真 RepoContext HEAD/ACL/Preimage→PD/ECP（`REPO_CONTEXT_UNBOUND`）；`S4` Fabric ActiveEpoch/LoadedDigest→HGK Issuer WorkID（`HOST_PENDING`）；`S5` Hermes bounded Worker→同 Operation WorldRaw→原 Protected Checker（`NATIVE_NOT_RUN`）。逐 Seam 的 sample input、Writer/Reader、expected raw keys、POS/NEG/FirstFail、Effect/Owner/Resume 和 typed handoff JSON 由 `W0_R3_WALKING_SKELETON_SPEC_SEAMS_TRACE.md` 提供。上述預期並未創造原 19 family 的新 Schema，也不能以作者端 fixture 代稱實測 GJ02。NEG 假 Head→`HOST_REPOCONTEXT_UNBOUND`、假 Original PI→`CANONICAL_WRITER_BOUNDARY`，都只阻受影效果。

### r3 五 Seam 原 Reader pin 與 fixture 實物

SEAM_CONTRACTS.json、seam_fixtures/ 與 SEAMS_AND_REPO_READBACK.md 為 S1–S5 的 request/ExpectedRaw/negative bytes/SHA。原 CLI/schema/Registry 原始碼使用三庫 remote immutable Commit+file SHA pin；本地 Repo HEAD/dirty/untracked 分開記錄，沒有把遠端 readback 當本地有效 RepoContext/ACL。S2–S5 runtime binding/ACK/Loaded policy/WorldRaw 未觀測即 EXECUTOR_UNBOUND/HOST_PENDING，Owner 補 same Subject/Candidate/Scope/Host/Epoch 才恢復；W0 不呼叫原 Compile/Issuer 或執行世界 effect。

# CH-39｜安全：SoD、Process ACL、秘鑰、原授權、Consent/Privacy

<a id="ch-39"></a>

## r4 當期 L3 合法正文｜`CH-39`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-39` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：安全：SoD、Process ACL、秘鑰、原授權、Consent/Privacy。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：Original Security/Consent Owner。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-18` `L1-r4:L786` | W0 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、HGK Original Issuer/SharedSpine/Protected Checker Reader、Effect-spe | 六類 Effect 對應最低充分原 Evidence | 缺 OPS/RELEASE Permission 使合法 READ/DRAFT 全域停工；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-032` `L1-r4:L829` | W1 | HGK Original Issuer/SharedSpine/Protected Checker Reader | 直接修改 HGK 的一般 Profile 被拒 | 兩個 Hermes Profile 名稱即宣稱 OS 隔離；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-033` `L1-r4:L830` | W2 | HGK Original Issuer/SharedSpine/Protected Checker Reader | 獨立驗收只有相應原授權主體可出 | 雙 GPT review 冒 Independent；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-050` `L1-r4:L847` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 原 Consumer/合法使用者授權 | 對陌生帳號自動操作/未知結果重試；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案增補｜跨波原責任保留與准入規劃
### W0 權限敏感度與 SoD 最小決策（主波 W1）

唯一 Human Owner 可跨產品簽其被授權的 Owner 決策，但不等於軟體 Principal 同身份獲得所有技術權限。作者角色不能冒充 HGK Issuer/Protected Checker；同模型下不同 Profile 不自動形成技術獨立。OS SID/ACL 原始測量缺失時，對受保護 world effect `H-OS-08`，不阻已許可的來源讀取。任何秘密不寫 ZIP/QuestionLedger/Repo。

# CH-40｜三 SPEC／PI／PD／ECP／TQAEP 對原 Reader 的交接矩陣

<a id="ch-40"></a>

## r4 當期 L3 合法正文｜`CH-40`：主波 W1（L2 r4 §6）
**W0 非主責，唯一主波是 W1。** `CH-40` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W1 專屬規格與 Native 權威。

**原產品主題／受影接收**：三 SPEC／PI／PD／ECP／TQAEP 對原 Reader 的交接矩陣。主波 L3 收件 `W1_藍圖&skeleton → W1_草案 → W1_定案`；原 Consumer：Original PIPD + affected Host Receiver。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W1 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W1_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-19` `L1-r4:L787` | W2 | Fabric FHS Navigation/Policy/FAR Reader → Original Consumer、Original Program/DAG/Delivery Consumer | FAR Typed Envelope／R8 Consumer ACK/NACK | 研究文章／FAR Finding 無原 R8 Consumer ACK 卻宣 policy 已落地；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-030` `L1-r4:L827` | W1 | Fabric FHS Navigation/Policy/FAR Reader → Original Consumer | R8 真 ACK 不被研究文件代替 | 工具回應被視為 Policy Applied；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-058` `L1-r4:L855` | W4 | Original Program/DAG/Delivery Consumer | Subject/OriginalID/SourceSHA/Effect/Claim 全接線 | 產出本 MD 就宣稱全量正式 PKG 生成；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案增補｜跨波原責任保留與准入規劃
### W0→W1 Typed Handoff 一版欄位（主波 W1）

`{design_candidate_sha, subject, affected_scope, SourceManifestSHA, ProductSpecRef, ArchitectureSpecRef, ProgramSpecRef, OriginalIDs, original_consumer, expected_ABI, effect_class, POS/NEG, first_fail, holds[], last_good_checkpoint, resume_predicate}`。當期原 `PIPD` schema 未確認，不新增 `$id` 或寄送 canonical JSON。第一 Consumer 原 SBL Product/PIPD Intake Reader，NACK 要帶具名失敗字段；無 ACK 只為 `W1_REVIEW_REQUEST`，不得投 HGK Issuer。

# CH-41｜TQAEP：POS／NEG／FirstFail／獨立 Oracle 的可執行計畫

<a id="ch-41"></a>

## r4 當期 L3 合法正文｜`CH-41`：主波 W2（L2 r4 §6）
**W0 非主責，唯一主波是 W2。** `CH-41` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W2 專屬規格與 Native 權威。

**原產品主題／受影接收**：TQAEP：POS／NEG／FirstFail／獨立 Oracle 的可執行計畫。主波 L3 收件 `W2_藍圖&skeleton → W2_草案 → W2_定案`；原 Consumer：Original Oracle/Protected Checker。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W2 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W2_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-13` `L1-r4:L781` | W1 | SBL RepoContext/PD Reader → HGK Original Issuer → Repo World Reader、SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | PI source-bound，PD 晚綁 Repo，ECP 非 Admission，TQAEP 依 Original Oracle | ECP intent 冒 Issuer Permit；PD 未 live RepoContext 即號稱已綁；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-15` `L1-r4:L783` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer、Original Oracle/Protected Checker Reader | POS/NEG/Case/Raw/SourceSHA，符合原 Principal 差異 | Maker 自簽 Independent、沒有實際 Runner Raw 卻宣 PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-027` `L1-r4:L824` | W1 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader | Case 有正負例和待原 Checker 收據 | 不核 ABI 就加 compile-cc 14th verb；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-051` `L1-r4:L848` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 原受權發行收據 | PR Green/Markdown signed 誤宣 RELEASE；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-060` `L1-r4:L857` | W2 | Original Oracle/Protected Checker Reader | 原適用變體能抓回歸 | 測試空泛，全部 88% tests pass 仍漏 mutants；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案增補｜跨波原責任保留與准入規劃
### W0 96 Oracle 計畫 vs 實驗測量（主波 W2）

`TestClass(12)×OracleType(8)` 是原 Case Registry 的 96 真設計身份；W0 各保存 input schema、applicability、POS bytes、NEG bytes、OriginalCaseID、Host/Profile/Subject、Original Runner、Expected WorldRaw、FirstFail。若 Runner 未綁則 `PLAN_NOT_RUN/H-CASES-09`，單一 generic pass 不可代替 96 專屬 oracle。原 Protected Checker 才能產獨立資格收據；Maker 只能送計畫。

# CH-42｜來源／要求／Case／Evidence／Delivery LEDGER：一筆一真值

<a id="ch-42"></a>

## r4 當期 L3 合法正文｜`CH-42`：主波 W0（L2 r4 §6）
**W0 主責：原 Oracle 96 與六 Ledger。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：W0 的 WP21 逐 `AC-C39-*` 96 案保留原 test class×Oracle，POS/NEG/Raw schema/RunnerOwner/FirstFail 準備；Source/Requirement/SPEC/Case/EvidenceExpectation/Deliver 六 Ledger 由原 Writer 寫，W0 只存 references；無 Runner/Raw 就 CaseStatus=PLAN_NOT_RUN。
**原 Writer／Reader／Consumer／責任界線**：原 AC Oracle/Protected AO Request Reader；真獨立 Checker W2/W3，Maker 不簽。
**Acceptance POS**：POS：96 原 ID 每項有獨立 input/output/NEG 或可指向原來源；現場未測一律 NOT_RUN。
**Acceptance NEG／FirstFail**：NEG：通用 fixture 給 96 項直接 Pass；FirstFail=ORACLE_RUNNER_BIND_HOLD。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### r4 六 Ledger｜不可遺漏的 `SPEC_LEDGER` 與雙向 Join（F-002 已修補）
六者是原 Registry/Source/Spec/Case/Evidence/Deliver 的 **read-model 投影**；W0 只寫隔離作者端索引，不新增資料庫、第二 Canonical、Issuer 或 Registry。`Source→Requirement→SPEC→Case→Evidence→Deliver` 六段必保留原 Reader 規格和受影負例。
| 六原 Ledger ID | 最低主鍵／必備映射 | 原 Writer／Reader | 下游 Consumer | POS / 必要正向 Join | NEG / FirstFail |
|---|---|---|---|---|---|
| SOURCE_LEDGER | `SourceID+Revision+SourceSHA+SourceSpan` | 原 Source/Authority Reader | REQUIREMENT_LEDGER | 真 bytes / Currentness Reader ACK，若僅 snapshot 則標候選 | 來源 SHA mismatch／`SOURCE_IDENTITY_HOLD` |
| REQUIREMENT_LEDGER | `OriginalRequirementID+ParentID+ChildID+Polarity+Context+NEGScope+Applicability` | 原 SBL/PIPD Requirement/Domain Reader | SPEC_LEDGER | 逐 OriginalID 保留否定/例外/Condition/Owner | Parent/NEG 不可反查／`REQUIREMENT_PARENT_NEG_HOLD` |
| SPEC_LEDGER | `OriginalRequirementID+SpecClauseID+SpecKind+SubjectID+SourceRef` | SBL TPM PM/SE/TPgM 作者候選→原 SPEC/PIPD Reader | CASE_LEDGER | Product FUO/ACC、Architecture ADR/ABI、Program DAG 三不同條位與原 Requirement 逐一 Join | 缺 SpecClauseID／三份同文／`SPEC_TRACE_BROKEN` |
| CASE_LEDGER | `OriginalCaseID+Variant+Scope+OriginalOracleID+SpecClauseID+PositiveRef+NegativeRef` | 原 Case/Oracle Registry Reader | EVIDENCE_EXPECTATION_LEDGER | 每個受影 Case 同 Source/Scope、POS/NEG/FirstFail/Runner 類型 | ORACLE 型別誤用／`CASE_JOIN_OR_ORACLE_HOLD` |
| EVIDENCE_EXPECTATION_LEDGER | `SourceID+CaseID+EffectClass+HostID+PolicyEpoch+EvidenceExpectationID+ExpectedWorldRawSchema` | 原 Evidence/TQAEP Reader 與未來 Protected Checker | DELIVER_LEDGER | 設計期 `EXPECTED_NOT_OBSERVED`；觀測收據由原 Host/Checker 才能綁 | Maker 虛構 Raw/PASS／`EVIDENCE_LAUNDERING_DENY` |
| DELIVER_LEDGER | `ArtifactID+CandidateSHA+OriginalConsumer+DeliverID+EvidenceExpectationID+ReceiptStatus` | 原 Delivery/Consumer/Publisher Reader | 原受影 Consumer | 每交付項回指 Case→SpecClause→OriginalID→Source bytes；正式 effect 依原 Publisher | 跳過原 Consumer 或用 ZIP 取代 Release／`DELIVER_CHAIN_BROKEN` |

**雙向 Join 驗證**：對 W0 `SpecClauseID=P.W0.PROD.001`（作者候選，非 OriginalID），其來源必是 `SBL-DOC-01` 真 `SourceSHA+Span` 與對應 `OriginalRequirementID/Parent/NEG`（尚未經原 Reader 核定時為 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`）；CaseID `W0.CASE.P.001` 再指向 POS+NEG expectation，證據期望 `EXPECTED_NOT_OBSERVED`，Deliver 指向原 PIPD Intake/Owner。反向從 Deliver 返回原 Source 若任何 Join 不同 Subject/Scope／原 identity，必 `SPEC_TRACE_BROKEN`。
**三種 SPEC 的分離**：Product→FUO／User ACC±；Architecture→ADR／Versioned ABI／Effect/SoD NEG；Program→22WP/36Edge／Stop–Resume。不能把相同正文換三個檔名充 `SPEC_LEDGER`；遺失任何一種 SpecClause 的負例或 Consumer 必拒收。本範例鍵 `P.W0.PROD.001` 等僅是作者端 seeded ID，非 PIPD 正式 schema `$id`。

### r4 96 Oracle｜逐案 typed 來源／原專屬正負條款（F-003 已修補）
以下為 `FHS-BODY-07` 原實質條文物理位元組切片的作者端**測試計畫**，不是模擬 Raw、原 Runner 或 Protected Checker 的 PASS。`TestClass×OracleType` 為 12×8 原型別，個別 POS/NEG 與來源區間不可互代。SourceByteSpan 為半開 `[start,end)`，來源 SHA 見表頭；若原 Case Registry 原 Reader 當期性未綁，一律 `PLAN_NOT_RUN / ORACLE_RUNNER_BIND_HOLD`。
**原文件**：`07_ACCEPTANCE_CHALLENGE(4).md`，SHA-256 `81a8c2f1cc4629f59829f11f87aebd14cd57f7c4dd0970d672880e90e2899741`。原受保護 Checker 仍是唯一獨立判定者。
| Original CaseID | TestClass | OracleType | SourceByteSpan／原行 | 真觸發與原域／型別判定（原條文） | 專屬 NEG 及預期 FirstFail | 原 Consumer／執行上限 |
|---|---|---|---|---|---|---|
| `AC-C39-POS-DETERMINISTIC` | POS | DETERMINISTIC | `16215:18072` / `FHS-BODY-07:L172-183` | Input: 本TestClass domain=POS，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 功能被要求且已宣告acceptance predicate；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L445，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `feature_invoked and acceptance_predicate_declared && DETERMINISTIC_inputs_bound`；requires feature invoked + acceptance predicate; consumer output and real raw; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: 去掉必要輸出或接受錯誤輸出；observed_value改成非expected; mutation: `/outcome/pos/deterministic := __CORRUPT__001` → `MISSING_POS_FUNCTION`；`AC-C39-POS-DETERMINISTIC`; FirstFail=`MISSING_POS_FUNCTION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-POS-STATE_READBACK` | POS | STATE_READBACK | `18072:20002` / `FHS-BODY-07:L184-195` | Input: 本TestClass domain=POS，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 功能被要求且已宣告acceptance predicate；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L446，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `feature_invoked and acceptance_predicate_declared && STATE_READBACK_inputs_bound`；requires feature invoked + acceptance predicate; consumer output and real raw; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: 去掉必要輸出或接受錯誤輸出；actual_post_state不同或foreign world Reader; mutation: `/outcome/pos/state_readback := __CORRUPT__002` → `MISSING_POS_FUNCTION`；`AC-C39-POS-STATE_READBACK`; FirstFail=`MISSING_POS_FUNCTION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-POS-PROPERTY` | POS | PROPERTY | `20002:21863` / `FHS-BODY-07:L196-207` | Input: 本TestClass domain=POS，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 功能被要求且已宣告acceptance predicate；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L447，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `feature_invoked and acceptance_predicate_declared && PROPERTY_inputs_bound`；requires feature invoked + acceptance predicate; consumer output and real raw; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: 去掉必要輸出或接受錯誤輸出；至少一generated case破invariant; mutation: `/outcome/pos/property := __CORRUPT__003` → `MISSING_POS_FUNCTION`；`AC-C39-POS-PROPERTY`; FirstFail=`MISSING_POS_FUNCTION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-POS-REFERENCE_OUTPUT` | POS | REFERENCE_OUTPUT | `21863:23772` / `FHS-BODY-07:L208-219` | Input: 本TestClass domain=POS，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 功能被要求且已宣告acceptance predicate；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L448，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `feature_invoked and acceptance_predicate_declared && REFERENCE_OUTPUT_inputs_bound`；requires feature invoked + acceptance predicate; consumer output and real raw; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: 去掉必要輸出或接受錯誤輸出；更換reference或輸出差異; mutation: `/outcome/pos/reference_output := __CORRUPT__004` → `MISSING_POS_FUNCTION`；`AC-C39-POS-REFERENCE_OUTPUT`; FirstFail=`MISSING_POS_FUNCTION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-POS-STATISTICAL` | POS | STATISTICAL | `23772:25664` / `FHS-BODY-07:L220-231` | Input: 本TestClass domain=POS，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 功能被要求且已宣告acceptance predicate；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L449，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `feature_invoked and acceptance_predicate_declared && STATISTICAL_inputs_bound`；requires feature invoked + acceptance predicate; consumer output and real raw; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: 去掉必要輸出或接受錯誤輸出；刪dataset/改confidence/樣本不達界; mutation: `/outcome/pos/statistical := __CORRUPT__005` → `MISSING_POS_FUNCTION`；`AC-C39-POS-STATISTICAL`; FirstFail=`MISSING_POS_FUNCTION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-POS-SEMANTIC_JUDGE` | POS | SEMANTIC_JUDGE | `25664:27598` / `FHS-BODY-07:L232-243` | Input: 本TestClass domain=POS，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 功能被要求且已宣告acceptance predicate；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L450，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `feature_invoked and acceptance_predicate_declared && SEMANTIC_JUDGE_inputs_bound`；requires feature invoked + acceptance predicate; consumer output and real raw; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: 去掉必要輸出或接受錯誤輸出；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/pos/semantic_judge := __CORRUPT__006` → `MISSING_POS_FUNCTION`；`AC-C39-POS-SEMANTIC_JUDGE`; FirstFail=`MISSING_POS_FUNCTION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-POS-HUMAN` | POS | HUMAN | `27598:29438` / `FHS-BODY-07:L244-255` | Input: 本TestClass domain=POS，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 功能被要求且已宣告acceptance predicate；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L451，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `feature_invoked and acceptance_predicate_declared && HUMAN_inputs_bound`；requires feature invoked + acceptance predicate; consumer output and real raw; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: 去掉必要輸出或接受錯誤輸出；Maker冒Human或決議是另一scope; mutation: `/outcome/pos/human := __CORRUPT__007` → `MISSING_POS_FUNCTION`；`AC-C39-POS-HUMAN`; FirstFail=`MISSING_POS_FUNCTION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-POS-COMPOSITE` | POS | COMPOSITE | `29438:31304` / `FHS-BODY-07:L256-267` | Input: 本TestClass domain=POS，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 功能被要求且已宣告acceptance predicate；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L452，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `feature_invoked and acceptance_predicate_declared && COMPOSITE_inputs_bound`；requires feature invoked + acceptance predicate; consumer output and real raw; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: 去掉必要輸出或接受錯誤輸出；刪hard component或soft分數蓋hard fail; mutation: `/outcome/pos/composite := __CORRUPT__008` → `MISSING_POS_FUNCTION`；`AC-C39-POS-COMPOSITE`; FirstFail=`MISSING_POS_FUNCTION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-NEG-DETERMINISTIC` | NEG | DETERMINISTIC | `31304:33104` / `FHS-BODY-07:L268-279` | Input: 本TestClass domain=NEG，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=['CLI-NEG-DUPLICATE']；無Raw不可假裝已跑Native。; Applicability: 來源禁止行為或非法輸入可構造；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L453，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `invalid_input_contract or forbidden_action_declared && DETERMINISTIC_inputs_bound`；requires forbidden action or invalid input; deny with world no diff; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: 將拒收轉成功或寫入禁止state；observed_value改成非expected; mutation: `/outcome/neg/deterministic := __CORRUPT__009` → `NEGATIVE_ACCEPTED`；`AC-C39-NEG-DETERMINISTIC`; FirstFail=`NEGATIVE_ACCEPTED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-NEG-STATE_READBACK` | NEG | STATE_READBACK | `33104:34977` / `FHS-BODY-07:L280-291` | Input: 本TestClass domain=NEG，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=['CLI-NEG-DUPLICATE']；無Raw不可假裝已跑Native。; Applicability: 來源禁止行為或非法輸入可構造；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L454，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `invalid_input_contract or forbidden_action_declared && STATE_READBACK_inputs_bound`；requires forbidden action or invalid input; deny with world no diff; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: 將拒收轉成功或寫入禁止state；actual_post_state不同或foreign world Reader; mutation: `/outcome/neg/state_readback := __CORRUPT__010` → `NEGATIVE_ACCEPTED`；`AC-C39-NEG-STATE_READBACK`; FirstFail=`NEGATIVE_ACCEPTED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-NEG-PROPERTY` | NEG | PROPERTY | `34977:36781` / `FHS-BODY-07:L292-303` | Input: 本TestClass domain=NEG，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=['CLI-NEG-DUPLICATE']；無Raw不可假裝已跑Native。; Applicability: 來源禁止行為或非法輸入可構造；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L455，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `invalid_input_contract or forbidden_action_declared && PROPERTY_inputs_bound`；requires forbidden action or invalid input; deny with world no diff; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: 將拒收轉成功或寫入禁止state；至少一generated case破invariant; mutation: `/outcome/neg/property := __CORRUPT__011` → `NEGATIVE_ACCEPTED`；`AC-C39-NEG-PROPERTY`; FirstFail=`NEGATIVE_ACCEPTED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-NEG-REFERENCE_OUTPUT` | NEG | REFERENCE_OUTPUT | `36781:38633` / `FHS-BODY-07:L304-315` | Input: 本TestClass domain=NEG，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=['CLI-NEG-DUPLICATE']；無Raw不可假裝已跑Native。; Applicability: 來源禁止行為或非法輸入可構造；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L456，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `invalid_input_contract or forbidden_action_declared && REFERENCE_OUTPUT_inputs_bound`；requires forbidden action or invalid input; deny with world no diff; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: 將拒收轉成功或寫入禁止state；更換reference或輸出差異; mutation: `/outcome/neg/reference_output := __CORRUPT__012` → `NEGATIVE_ACCEPTED`；`AC-C39-NEG-REFERENCE_OUTPUT`; FirstFail=`NEGATIVE_ACCEPTED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-NEG-STATISTICAL` | NEG | STATISTICAL | `38633:40469` / `FHS-BODY-07:L316-327` | Input: 本TestClass domain=NEG，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=['CLI-NEG-DUPLICATE']；無Raw不可假裝已跑Native。; Applicability: 來源禁止行為或非法輸入可構造；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L457，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `invalid_input_contract or forbidden_action_declared && STATISTICAL_inputs_bound`；requires forbidden action or invalid input; deny with world no diff; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: 將拒收轉成功或寫入禁止state；刪dataset/改confidence/樣本不達界; mutation: `/outcome/neg/statistical := __CORRUPT__013` → `NEGATIVE_ACCEPTED`；`AC-C39-NEG-STATISTICAL`; FirstFail=`NEGATIVE_ACCEPTED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-NEG-SEMANTIC_JUDGE` | NEG | SEMANTIC_JUDGE | `40469:42347` / `FHS-BODY-07:L328-339` | Input: 本TestClass domain=NEG，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-NEG-DUPLICATE']；無Raw不可假裝已跑Native。; Applicability: 來源禁止行為或非法輸入可構造；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L458，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `invalid_input_contract or forbidden_action_declared && SEMANTIC_JUDGE_inputs_bound`；requires forbidden action or invalid input; deny with world no diff; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: 將拒收轉成功或寫入禁止state；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/neg/semantic_judge := __CORRUPT__014` → `NEGATIVE_ACCEPTED`；`AC-C39-NEG-SEMANTIC_JUDGE`; FirstFail=`NEGATIVE_ACCEPTED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-NEG-HUMAN` | NEG | HUMAN | `42347:44131` / `FHS-BODY-07:L340-351` | Input: 本TestClass domain=NEG，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=['CLI-NEG-DUPLICATE']；無Raw不可假裝已跑Native。; Applicability: 來源禁止行為或非法輸入可構造；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L459，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `invalid_input_contract or forbidden_action_declared && HUMAN_inputs_bound`；requires forbidden action or invalid input; deny with world no diff; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: 將拒收轉成功或寫入禁止state；Maker冒Human或決議是另一scope; mutation: `/outcome/neg/human := __CORRUPT__015` → `NEGATIVE_ACCEPTED`；`AC-C39-NEG-HUMAN`; FirstFail=`NEGATIVE_ACCEPTED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-NEG-COMPOSITE` | NEG | COMPOSITE | `44131:45941` / `FHS-BODY-07:L352-363` | Input: 本TestClass domain=NEG，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-NEG-DUPLICATE']；無Raw不可假裝已跑Native。; Applicability: 來源禁止行為或非法輸入可構造；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L460，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `invalid_input_contract or forbidden_action_declared && COMPOSITE_inputs_bound`；requires forbidden action or invalid input; deny with world no diff; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: 將拒收轉成功或寫入禁止state；刪hard component或soft分數蓋hard fail; mutation: `/outcome/neg/composite := __CORRUPT__016` → `NEGATIVE_ACCEPTED`；`AC-C39-NEG-COMPOSITE`; FirstFail=`NEGATIVE_ACCEPTED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-EDGE-DETERMINISTIC` | EDGE | DETERMINISTIC | `45941:47726` / `FHS-BODY-07:L364-375` | Input: 本TestClass domain=EDGE，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=['CLI-EDGE-EMPTY-TITLE']；無Raw不可假裝已跑Native。; Applicability: 來源boundary/empty/limit適用；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L461，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `input_boundary_or_resource_limit_declared && DETERMINISTIC_inputs_bound`；requires input bound or resource limit; one-past boundary rejection; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: off-by-one接受越界值；observed_value改成非expected; mutation: `/outcome/edge/deterministic := __CORRUPT__017` → `EDGE_BOUND_VIOLATION`；`AC-C39-EDGE-DETERMINISTIC`; FirstFail=`EDGE_BOUND_VIOLATION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-EDGE-STATE_READBACK` | EDGE | STATE_READBACK | `47726:49584` / `FHS-BODY-07:L376-387` | Input: 本TestClass domain=EDGE，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=['CLI-EDGE-EMPTY-TITLE']；無Raw不可假裝已跑Native。; Applicability: 來源boundary/empty/limit適用；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L462，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `input_boundary_or_resource_limit_declared && STATE_READBACK_inputs_bound`；requires input bound or resource limit; one-past boundary rejection; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: off-by-one接受越界值；actual_post_state不同或foreign world Reader; mutation: `/outcome/edge/state_readback := __CORRUPT__018` → `EDGE_BOUND_VIOLATION`；`AC-C39-EDGE-STATE_READBACK`; FirstFail=`EDGE_BOUND_VIOLATION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-EDGE-PROPERTY` | EDGE | PROPERTY | `49584:51373` / `FHS-BODY-07:L388-399` | Input: 本TestClass domain=EDGE，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=['CLI-EDGE-EMPTY-TITLE']；無Raw不可假裝已跑Native。; Applicability: 來源boundary/empty/limit適用；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L463，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `input_boundary_or_resource_limit_declared && PROPERTY_inputs_bound`；requires input bound or resource limit; one-past boundary rejection; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: off-by-one接受越界值；至少一generated case破invariant; mutation: `/outcome/edge/property := __CORRUPT__019` → `EDGE_BOUND_VIOLATION`；`AC-C39-EDGE-PROPERTY`; FirstFail=`EDGE_BOUND_VIOLATION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-EDGE-REFERENCE_OUTPUT` | EDGE | REFERENCE_OUTPUT | `51373:53210` / `FHS-BODY-07:L400-411` | Input: 本TestClass domain=EDGE，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=['CLI-EDGE-EMPTY-TITLE']；無Raw不可假裝已跑Native。; Applicability: 來源boundary/empty/limit適用；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L464，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `input_boundary_or_resource_limit_declared && REFERENCE_OUTPUT_inputs_bound`；requires input bound or resource limit; one-past boundary rejection; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: off-by-one接受越界值；更換reference或輸出差異; mutation: `/outcome/edge/reference_output := __CORRUPT__020` → `EDGE_BOUND_VIOLATION`；`AC-C39-EDGE-REFERENCE_OUTPUT`; FirstFail=`EDGE_BOUND_VIOLATION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-EDGE-STATISTICAL` | EDGE | STATISTICAL | `53210:55030` / `FHS-BODY-07:L412-423` | Input: 本TestClass domain=EDGE，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=['CLI-EDGE-EMPTY-TITLE']；無Raw不可假裝已跑Native。; Applicability: 來源boundary/empty/limit適用；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L465，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `input_boundary_or_resource_limit_declared && STATISTICAL_inputs_bound`；requires input bound or resource limit; one-past boundary rejection; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: off-by-one接受越界值；刪dataset/改confidence/樣本不達界; mutation: `/outcome/edge/statistical := __CORRUPT__021` → `EDGE_BOUND_VIOLATION`；`AC-C39-EDGE-STATISTICAL`; FirstFail=`EDGE_BOUND_VIOLATION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-EDGE-SEMANTIC_JUDGE` | EDGE | SEMANTIC_JUDGE | `55030:56892` / `FHS-BODY-07:L424-435` | Input: 本TestClass domain=EDGE，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-EDGE-EMPTY-TITLE']；無Raw不可假裝已跑Native。; Applicability: 來源boundary/empty/limit適用；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L466，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `input_boundary_or_resource_limit_declared && SEMANTIC_JUDGE_inputs_bound`；requires input bound or resource limit; one-past boundary rejection; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: off-by-one接受越界值；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/edge/semantic_judge := __CORRUPT__022` → `EDGE_BOUND_VIOLATION`；`AC-C39-EDGE-SEMANTIC_JUDGE`; FirstFail=`EDGE_BOUND_VIOLATION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-EDGE-HUMAN` | EDGE | HUMAN | `56892:58660` / `FHS-BODY-07:L436-447` | Input: 本TestClass domain=EDGE，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=['CLI-EDGE-EMPTY-TITLE']；無Raw不可假裝已跑Native。; Applicability: 來源boundary/empty/limit適用；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L467，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `input_boundary_or_resource_limit_declared && HUMAN_inputs_bound`；requires input bound or resource limit; one-past boundary rejection; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: off-by-one接受越界值；Maker冒Human或決議是另一scope; mutation: `/outcome/edge/human := __CORRUPT__023` → `EDGE_BOUND_VIOLATION`；`AC-C39-EDGE-HUMAN`; FirstFail=`EDGE_BOUND_VIOLATION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-EDGE-COMPOSITE` | EDGE | COMPOSITE | `58660:60454` / `FHS-BODY-07:L448-459` | Input: 本TestClass domain=EDGE，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-EDGE-EMPTY-TITLE']；無Raw不可假裝已跑Native。; Applicability: 來源boundary/empty/limit適用；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L468，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `input_boundary_or_resource_limit_declared && COMPOSITE_inputs_bound`；requires input bound or resource limit; one-past boundary rejection; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: off-by-one接受越界值；刪hard component或soft分數蓋hard fail; mutation: `/outcome/edge/composite := __CORRUPT__024` → `EDGE_BOUND_VIOLATION`；`AC-C39-EDGE-COMPOSITE`; FirstFail=`EDGE_BOUND_VIOLATION` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-SEC-DETERMINISTIC` | SEC | DETERMINISTIC | `60454:62301` / `FHS-BODY-07:L460-471` | Input: 本TestClass domain=SEC，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: trust boundary/credential/source受影；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L469，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `trust_boundary or secrets or untrusted_source or permission_effect && DETERMINISTIC_inputs_bound`；requires trust/secrets/untrusted source/permission effect; rights stay bounded; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: 越域payload或自簽verdict被接受；observed_value改成非expected; mutation: `/outcome/sec/deterministic := __CORRUPT__025` → `SECURITY_BOUNDARY_BREACH`；`AC-C39-SEC-DETERMINISTIC`; FirstFail=`SECURITY_BOUNDARY_BREACH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-SEC-STATE_READBACK` | SEC | STATE_READBACK | `62301:64221` / `FHS-BODY-07:L472-483` | Input: 本TestClass domain=SEC，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: trust boundary/credential/source受影；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L470，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `trust_boundary or secrets or untrusted_source or permission_effect && STATE_READBACK_inputs_bound`；requires trust/secrets/untrusted source/permission effect; rights stay bounded; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: 越域payload或自簽verdict被接受；actual_post_state不同或foreign world Reader; mutation: `/outcome/sec/state_readback := __CORRUPT__026` → `SECURITY_BOUNDARY_BREACH`；`AC-C39-SEC-STATE_READBACK`; FirstFail=`SECURITY_BOUNDARY_BREACH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-SEC-PROPERTY` | SEC | PROPERTY | `64221:66072` / `FHS-BODY-07:L484-495` | Input: 本TestClass domain=SEC，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: trust boundary/credential/source受影；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L471，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `trust_boundary or secrets or untrusted_source or permission_effect && PROPERTY_inputs_bound`；requires trust/secrets/untrusted source/permission effect; rights stay bounded; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: 越域payload或自簽verdict被接受；至少一generated case破invariant; mutation: `/outcome/sec/property := __CORRUPT__027` → `SECURITY_BOUNDARY_BREACH`；`AC-C39-SEC-PROPERTY`; FirstFail=`SECURITY_BOUNDARY_BREACH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-SEC-REFERENCE_OUTPUT` | SEC | REFERENCE_OUTPUT | `66072:67971` / `FHS-BODY-07:L496-507` | Input: 本TestClass domain=SEC，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: trust boundary/credential/source受影；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L472，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `trust_boundary or secrets or untrusted_source or permission_effect && REFERENCE_OUTPUT_inputs_bound`；requires trust/secrets/untrusted source/permission effect; rights stay bounded; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: 越域payload或自簽verdict被接受；更換reference或輸出差異; mutation: `/outcome/sec/reference_output := __CORRUPT__028` → `SECURITY_BOUNDARY_BREACH`；`AC-C39-SEC-REFERENCE_OUTPUT`; FirstFail=`SECURITY_BOUNDARY_BREACH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-SEC-STATISTICAL` | SEC | STATISTICAL | `67971:69854` / `FHS-BODY-07:L508-519` | Input: 本TestClass domain=SEC，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: trust boundary/credential/source受影；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L473，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `trust_boundary or secrets or untrusted_source or permission_effect && STATISTICAL_inputs_bound`；requires trust/secrets/untrusted source/permission effect; rights stay bounded; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: 越域payload或自簽verdict被接受；刪dataset/改confidence/樣本不達界; mutation: `/outcome/sec/statistical := __CORRUPT__029` → `SECURITY_BOUNDARY_BREACH`；`AC-C39-SEC-STATISTICAL`; FirstFail=`SECURITY_BOUNDARY_BREACH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-SEC-SEMANTIC_JUDGE` | SEC | SEMANTIC_JUDGE | `69854:71779` / `FHS-BODY-07:L520-531` | Input: 本TestClass domain=SEC，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: trust boundary/credential/source受影；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L474，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `trust_boundary or secrets or untrusted_source or permission_effect && SEMANTIC_JUDGE_inputs_bound`；requires trust/secrets/untrusted source/permission effect; rights stay bounded; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: 越域payload或自簽verdict被接受；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/sec/semantic_judge := __CORRUPT__030` → `SECURITY_BOUNDARY_BREACH`；`AC-C39-SEC-SEMANTIC_JUDGE`; FirstFail=`SECURITY_BOUNDARY_BREACH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-SEC-HUMAN` | SEC | HUMAN | `71779:73610` / `FHS-BODY-07:L532-543` | Input: 本TestClass domain=SEC，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: trust boundary/credential/source受影；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L475，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `trust_boundary or secrets or untrusted_source or permission_effect && HUMAN_inputs_bound`；requires trust/secrets/untrusted source/permission effect; rights stay bounded; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: 越域payload或自簽verdict被接受；Maker冒Human或決議是另一scope; mutation: `/outcome/sec/human := __CORRUPT__031` → `SECURITY_BOUNDARY_BREACH`；`AC-C39-SEC-HUMAN`; FirstFail=`SECURITY_BOUNDARY_BREACH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-SEC-COMPOSITE` | SEC | COMPOSITE | `73610:75466` / `FHS-BODY-07:L544-555` | Input: 本TestClass domain=SEC，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: trust boundary/credential/source受影；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L476，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `trust_boundary or secrets or untrusted_source or permission_effect && COMPOSITE_inputs_bound`；requires trust/secrets/untrusted source/permission effect; rights stay bounded; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: 越域payload或自簽verdict被接受；刪hard component或soft分數蓋hard fail; mutation: `/outcome/sec/composite := __CORRUPT__032` → `SECURITY_BOUNDARY_BREACH`；`AC-C39-SEC-COMPOSITE`; FirstFail=`SECURITY_BOUNDARY_BREACH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PERF-DETERMINISTIC` | PERF | DETERMINISTIC | `75466:77706` / `FHS-BODY-07:L556-567` | Input: 本TestClass domain=PERF，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=['CLI-PERF-LIST-00', 'CLI-PERF-LIST-01', 'CLI-PERF-LIST-02', 'CLI-PERF-LIST-03', 'CLI-PERF-LIST-04', 'CLI-PERF-LIST-05', 'CLI-PERF-LIST-06', 'CLI-PERF-LIST-07', 'CLI-PERF-LIST-08', 'CLI-PERF-LIST-09', 'CLI-PERF-LIST-10', 'CLI-PERF-LIST-11']；無Raw不可假裝已跑Native。; Applicability: 有來源校準dataset/metric/budget；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L477，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `nfr_sli_slo_id and benchmark_dataset_pin and metric_threshold && DETERMINISTIC_inputs_bound`；requires actual SLI/SLO + pinned benchmark; do not proxy latency; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: 改校準或把漏測樣本去除；observed_value改成非expected; mutation: `/outcome/perf/deterministic := __CORRUPT__033` → `PERF_SLO_EXCEEDED`；`AC-C39-PERF-DETERMINISTIC`; FirstFail=`PERF_SLO_EXCEEDED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PERF-STATE_READBACK` | PERF | STATE_READBACK | `77706:80019` / `FHS-BODY-07:L568-579` | Input: 本TestClass domain=PERF，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=['CLI-PERF-LIST-00', 'CLI-PERF-LIST-01', 'CLI-PERF-LIST-02', 'CLI-PERF-LIST-03', 'CLI-PERF-LIST-04', 'CLI-PERF-LIST-05', 'CLI-PERF-LIST-06', 'CLI-PERF-LIST-07', 'CLI-PERF-LIST-08', 'CLI-PERF-LIST-09', 'CLI-PERF-LIST-10', 'CLI-PERF-LIST-11']；無Raw不可假裝已跑Native。; Applicability: 有來源校準dataset/metric/budget；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L478，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `nfr_sli_slo_id and benchmark_dataset_pin and metric_threshold && STATE_READBACK_inputs_bound`；requires actual SLI/SLO + pinned benchmark; do not proxy latency; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: 改校準或把漏測樣本去除；actual_post_state不同或foreign world Reader; mutation: `/outcome/perf/state_readback := __CORRUPT__034` → `PERF_SLO_EXCEEDED`；`AC-C39-PERF-STATE_READBACK`; FirstFail=`PERF_SLO_EXCEEDED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PERF-PROPERTY` | PERF | PROPERTY | `80019:82263` / `FHS-BODY-07:L580-591` | Input: 本TestClass domain=PERF，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=['CLI-PERF-LIST-00', 'CLI-PERF-LIST-01', 'CLI-PERF-LIST-02', 'CLI-PERF-LIST-03', 'CLI-PERF-LIST-04', 'CLI-PERF-LIST-05', 'CLI-PERF-LIST-06', 'CLI-PERF-LIST-07', 'CLI-PERF-LIST-08', 'CLI-PERF-LIST-09', 'CLI-PERF-LIST-10', 'CLI-PERF-LIST-11']；無Raw不可假裝已跑Native。; Applicability: 有來源校準dataset/metric/budget；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L479，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `nfr_sli_slo_id and benchmark_dataset_pin and metric_threshold && PROPERTY_inputs_bound`；requires actual SLI/SLO + pinned benchmark; do not proxy latency; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: 改校準或把漏測樣本去除；至少一generated case破invariant; mutation: `/outcome/perf/property := __CORRUPT__035` → `PERF_SLO_EXCEEDED`；`AC-C39-PERF-PROPERTY`; FirstFail=`PERF_SLO_EXCEEDED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PERF-REFERENCE_OUTPUT` | PERF | REFERENCE_OUTPUT | `82263:84555` / `FHS-BODY-07:L592-603` | Input: 本TestClass domain=PERF，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=['CLI-PERF-LIST-00', 'CLI-PERF-LIST-01', 'CLI-PERF-LIST-02', 'CLI-PERF-LIST-03', 'CLI-PERF-LIST-04', 'CLI-PERF-LIST-05', 'CLI-PERF-LIST-06', 'CLI-PERF-LIST-07', 'CLI-PERF-LIST-08', 'CLI-PERF-LIST-09', 'CLI-PERF-LIST-10', 'CLI-PERF-LIST-11']；無Raw不可假裝已跑Native。; Applicability: 有來源校準dataset/metric/budget；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L480，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `nfr_sli_slo_id and benchmark_dataset_pin and metric_threshold && REFERENCE_OUTPUT_inputs_bound`；requires actual SLI/SLO + pinned benchmark; do not proxy latency; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: 改校準或把漏測樣本去除；更換reference或輸出差異; mutation: `/outcome/perf/reference_output := __CORRUPT__036` → `PERF_SLO_EXCEEDED`；`AC-C39-PERF-REFERENCE_OUTPUT`; FirstFail=`PERF_SLO_EXCEEDED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PERF-STATISTICAL` | PERF | STATISTICAL | `84555:86833` / `FHS-BODY-07:L604-615` | Input: 本TestClass domain=PERF，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=['CLI-PERF-LIST-00', 'CLI-PERF-LIST-01', 'CLI-PERF-LIST-02', 'CLI-PERF-LIST-03', 'CLI-PERF-LIST-04', 'CLI-PERF-LIST-05', 'CLI-PERF-LIST-06', 'CLI-PERF-LIST-07', 'CLI-PERF-LIST-08', 'CLI-PERF-LIST-09', 'CLI-PERF-LIST-10', 'CLI-PERF-LIST-11']；無Raw不可假裝已跑Native。; Applicability: 有來源校準dataset/metric/budget；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L481，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `nfr_sli_slo_id and benchmark_dataset_pin and metric_threshold && STATISTICAL_inputs_bound`；requires actual SLI/SLO + pinned benchmark; do not proxy latency; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: 改校準或把漏測樣本去除；刪dataset/改confidence/樣本不達界; mutation: `/outcome/perf/statistical := __CORRUPT__037` → `PERF_SLO_EXCEEDED`；`AC-C39-PERF-STATISTICAL`; FirstFail=`PERF_SLO_EXCEEDED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PERF-SEMANTIC_JUDGE` | PERF | SEMANTIC_JUDGE | `86833:89153` / `FHS-BODY-07:L616-627` | Input: 本TestClass domain=PERF，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-PERF-LIST-00', 'CLI-PERF-LIST-01', 'CLI-PERF-LIST-02', 'CLI-PERF-LIST-03', 'CLI-PERF-LIST-04', 'CLI-PERF-LIST-05', 'CLI-PERF-LIST-06', 'CLI-PERF-LIST-07', 'CLI-PERF-LIST-08', 'CLI-PERF-LIST-09', 'CLI-PERF-LIST-10', 'CLI-PERF-LIST-11']；無Raw不可假裝已跑Native。; Applicability: 有來源校準dataset/metric/budget；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L482，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `nfr_sli_slo_id and benchmark_dataset_pin and metric_threshold && SEMANTIC_JUDGE_inputs_bound`；requires actual SLI/SLO + pinned benchmark; do not proxy latency; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: 改校準或把漏測樣本去除；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/perf/semantic_judge := __CORRUPT__038` → `PERF_SLO_EXCEEDED`；`AC-C39-PERF-SEMANTIC_JUDGE`; FirstFail=`PERF_SLO_EXCEEDED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PERF-HUMAN` | PERF | HUMAN | `89153:91379` / `FHS-BODY-07:L628-639` | Input: 本TestClass domain=PERF，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=['CLI-PERF-LIST-00', 'CLI-PERF-LIST-01', 'CLI-PERF-LIST-02', 'CLI-PERF-LIST-03', 'CLI-PERF-LIST-04', 'CLI-PERF-LIST-05', 'CLI-PERF-LIST-06', 'CLI-PERF-LIST-07', 'CLI-PERF-LIST-08', 'CLI-PERF-LIST-09', 'CLI-PERF-LIST-10', 'CLI-PERF-LIST-11']；無Raw不可假裝已跑Native。; Applicability: 有來源校準dataset/metric/budget；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L483，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `nfr_sli_slo_id and benchmark_dataset_pin and metric_threshold && HUMAN_inputs_bound`；requires actual SLI/SLO + pinned benchmark; do not proxy latency; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: 改校準或把漏測樣本去除；Maker冒Human或決議是另一scope; mutation: `/outcome/perf/human := __CORRUPT__039` → `PERF_SLO_EXCEEDED`；`AC-C39-PERF-HUMAN`; FirstFail=`PERF_SLO_EXCEEDED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PERF-COMPOSITE` | PERF | COMPOSITE | `91379:93628` / `FHS-BODY-07:L640-651` | Input: 本TestClass domain=PERF，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-PERF-LIST-00', 'CLI-PERF-LIST-01', 'CLI-PERF-LIST-02', 'CLI-PERF-LIST-03', 'CLI-PERF-LIST-04', 'CLI-PERF-LIST-05', 'CLI-PERF-LIST-06', 'CLI-PERF-LIST-07', 'CLI-PERF-LIST-08', 'CLI-PERF-LIST-09', 'CLI-PERF-LIST-10', 'CLI-PERF-LIST-11']；無Raw不可假裝已跑Native。; Applicability: 有來源校準dataset/metric/budget；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L484，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `nfr_sli_slo_id and benchmark_dataset_pin and metric_threshold && COMPOSITE_inputs_bound`；requires actual SLI/SLO + pinned benchmark; do not proxy latency; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: 改校準或把漏測樣本去除；刪hard component或soft分數蓋hard fail; mutation: `/outcome/perf/composite := __CORRUPT__040` → `PERF_SLO_EXCEEDED`；`AC-C39-PERF-COMPOSITE`; FirstFail=`PERF_SLO_EXCEEDED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PARITY-DETERMINISTIC` | PARITY | DETERMINISTIC | `93628:95532` / `FHS-BODY-07:L652-663` | Input: 本TestClass domain=PARITY，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID', 'CLI-PARITY-SECOND-ENTRYPOINT']；無Raw不可假裝已跑Native。; Applicability: 替代Provider/Host/mode需原Parity；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L485，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `provider_off_required and provider_off_profile_id and fallback_contract && DETERMINISTIC_inputs_bound`；requires provider-off profile + fallback; no network egress; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: 只測一Host借其他HostPASS；observed_value改成非expected; mutation: `/outcome/parity/deterministic := __CORRUPT__041` → `PARITY_PROVIDER_OFF_FAIL`；`AC-C39-PARITY-DETERMINISTIC`; FirstFail=`PARITY_PROVIDER_OFF_FAIL` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PARITY-STATE_READBACK` | PARITY | STATE_READBACK | `95532:97509` / `FHS-BODY-07:L664-675` | Input: 本TestClass domain=PARITY，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID', 'CLI-PARITY-SECOND-ENTRYPOINT']；無Raw不可假裝已跑Native。; Applicability: 替代Provider/Host/mode需原Parity；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L486，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `provider_off_required and provider_off_profile_id and fallback_contract && STATE_READBACK_inputs_bound`；requires provider-off profile + fallback; no network egress; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: 只測一Host借其他HostPASS；actual_post_state不同或foreign world Reader; mutation: `/outcome/parity/state_readback := __CORRUPT__042` → `PARITY_PROVIDER_OFF_FAIL`；`AC-C39-PARITY-STATE_READBACK`; FirstFail=`PARITY_PROVIDER_OFF_FAIL` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PARITY-PROPERTY` | PARITY | PROPERTY | `97509:99417` / `FHS-BODY-07:L676-687` | Input: 本TestClass domain=PARITY，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID', 'CLI-PARITY-SECOND-ENTRYPOINT']；無Raw不可假裝已跑Native。; Applicability: 替代Provider/Host/mode需原Parity；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L487，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `provider_off_required and provider_off_profile_id and fallback_contract && PROPERTY_inputs_bound`；requires provider-off profile + fallback; no network egress; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: 只測一Host借其他HostPASS；至少一generated case破invariant; mutation: `/outcome/parity/property := __CORRUPT__043` → `PARITY_PROVIDER_OFF_FAIL`；`AC-C39-PARITY-PROPERTY`; FirstFail=`PARITY_PROVIDER_OFF_FAIL` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PARITY-REFERENCE_OUTPUT` | PARITY | REFERENCE_OUTPUT | `99417:101373` / `FHS-BODY-07:L688-699` | Input: 本TestClass domain=PARITY，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID', 'CLI-PARITY-SECOND-ENTRYPOINT']；無Raw不可假裝已跑Native。; Applicability: 替代Provider/Host/mode需原Parity；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L488，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `provider_off_required and provider_off_profile_id and fallback_contract && REFERENCE_OUTPUT_inputs_bound`；requires provider-off profile + fallback; no network egress; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: 只測一Host借其他HostPASS；更換reference或輸出差異; mutation: `/outcome/parity/reference_output := __CORRUPT__044` → `PARITY_PROVIDER_OFF_FAIL`；`AC-C39-PARITY-REFERENCE_OUTPUT`; FirstFail=`PARITY_PROVIDER_OFF_FAIL` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PARITY-STATISTICAL` | PARITY | STATISTICAL | `101373:103312` / `FHS-BODY-07:L700-711` | Input: 本TestClass domain=PARITY，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID', 'CLI-PARITY-SECOND-ENTRYPOINT']；無Raw不可假裝已跑Native。; Applicability: 替代Provider/Host/mode需原Parity；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L489，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `provider_off_required and provider_off_profile_id and fallback_contract && STATISTICAL_inputs_bound`；requires provider-off profile + fallback; no network egress; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: 只測一Host借其他HostPASS；刪dataset/改confidence/樣本不達界; mutation: `/outcome/parity/statistical := __CORRUPT__045` → `PARITY_PROVIDER_OFF_FAIL`；`AC-C39-PARITY-STATISTICAL`; FirstFail=`PARITY_PROVIDER_OFF_FAIL` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PARITY-SEMANTIC_JUDGE` | PARITY | SEMANTIC_JUDGE | `103312:105293` / `FHS-BODY-07:L712-723` | Input: 本TestClass domain=PARITY，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID', 'CLI-PARITY-SECOND-ENTRYPOINT']；無Raw不可假裝已跑Native。; Applicability: 替代Provider/Host/mode需原Parity；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L490，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `provider_off_required and provider_off_profile_id and fallback_contract && SEMANTIC_JUDGE_inputs_bound`；requires provider-off profile + fallback; no network egress; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: 只測一Host借其他HostPASS；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/parity/semantic_judge := __CORRUPT__046` → `PARITY_PROVIDER_OFF_FAIL`；`AC-C39-PARITY-SEMANTIC_JUDGE`; FirstFail=`PARITY_PROVIDER_OFF_FAIL` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PARITY-HUMAN` | PARITY | HUMAN | `105293:107180` / `FHS-BODY-07:L724-735` | Input: 本TestClass domain=PARITY，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID', 'CLI-PARITY-SECOND-ENTRYPOINT']；無Raw不可假裝已跑Native。; Applicability: 替代Provider/Host/mode需原Parity；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L491，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `provider_off_required and provider_off_profile_id and fallback_contract && HUMAN_inputs_bound`；requires provider-off profile + fallback; no network egress; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: 只測一Host借其他HostPASS；Maker冒Human或決議是另一scope; mutation: `/outcome/parity/human := __CORRUPT__047` → `PARITY_PROVIDER_OFF_FAIL`；`AC-C39-PARITY-HUMAN`; FirstFail=`PARITY_PROVIDER_OFF_FAIL` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-PARITY-COMPOSITE` | PARITY | COMPOSITE | `107180:109093` / `FHS-BODY-07:L736-747` | Input: 本TestClass domain=PARITY，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID', 'CLI-PARITY-SECOND-ENTRYPOINT']；無Raw不可假裝已跑Native。; Applicability: 替代Provider/Host/mode需原Parity；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L492，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `provider_off_required and provider_off_profile_id and fallback_contract && COMPOSITE_inputs_bound`；requires provider-off profile + fallback; no network egress; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: 只測一Host借其他HostPASS；刪hard component或soft分數蓋hard fail; mutation: `/outcome/parity/composite := __CORRUPT__048` → `PARITY_PROVIDER_OFF_FAIL`；`AC-C39-PARITY-COMPOSITE`; FirstFail=`PARITY_PROVIDER_OFF_FAIL` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-RECOVERY-DETERMINISTIC` | RECOVERY | DETERMINISTIC | `109093:110975` / `FHS-BODY-07:L748-759` | Input: 本TestClass domain=RECOVERY，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 存在restart/timeout/checkpoint情境；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L493，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `effect_or_failure_recovery_required and rollback_ref && DETERMINISTIC_inputs_bound`；requires failure recovery + rollback ref; pre/post and no residue; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: 同nonce盲重播或skip未完成工作；observed_value改成非expected; mutation: `/outcome/recovery/deterministic := __CORRUPT__049` → `RECOVERY_STATE_MISMATCH`；`AC-C39-RECOVERY-DETERMINISTIC`; FirstFail=`RECOVERY_STATE_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-RECOVERY-STATE_READBACK` | RECOVERY | STATE_READBACK | `110975:112930` / `FHS-BODY-07:L760-771` | Input: 本TestClass domain=RECOVERY，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 存在restart/timeout/checkpoint情境；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L494，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `effect_or_failure_recovery_required and rollback_ref && STATE_READBACK_inputs_bound`；requires failure recovery + rollback ref; pre/post and no residue; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: 同nonce盲重播或skip未完成工作；actual_post_state不同或foreign world Reader; mutation: `/outcome/recovery/state_readback := __CORRUPT__050` → `RECOVERY_STATE_MISMATCH`；`AC-C39-RECOVERY-STATE_READBACK`; FirstFail=`RECOVERY_STATE_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-RECOVERY-PROPERTY` | RECOVERY | PROPERTY | `112930:114816` / `FHS-BODY-07:L772-783` | Input: 本TestClass domain=RECOVERY，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 存在restart/timeout/checkpoint情境；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L495，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `effect_or_failure_recovery_required and rollback_ref && PROPERTY_inputs_bound`；requires failure recovery + rollback ref; pre/post and no residue; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: 同nonce盲重播或skip未完成工作；至少一generated case破invariant; mutation: `/outcome/recovery/property := __CORRUPT__051` → `RECOVERY_STATE_MISMATCH`；`AC-C39-RECOVERY-PROPERTY`; FirstFail=`RECOVERY_STATE_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-RECOVERY-REFERENCE_OUTPUT` | RECOVERY | REFERENCE_OUTPUT | `114816:116750` / `FHS-BODY-07:L784-795` | Input: 本TestClass domain=RECOVERY，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 存在restart/timeout/checkpoint情境；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L496，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `effect_or_failure_recovery_required and rollback_ref && REFERENCE_OUTPUT_inputs_bound`；requires failure recovery + rollback ref; pre/post and no residue; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: 同nonce盲重播或skip未完成工作；更換reference或輸出差異; mutation: `/outcome/recovery/reference_output := __CORRUPT__052` → `RECOVERY_STATE_MISMATCH`；`AC-C39-RECOVERY-REFERENCE_OUTPUT`; FirstFail=`RECOVERY_STATE_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-RECOVERY-STATISTICAL` | RECOVERY | STATISTICAL | `116750:118668` / `FHS-BODY-07:L796-807` | Input: 本TestClass domain=RECOVERY，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 存在restart/timeout/checkpoint情境；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L497，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `effect_or_failure_recovery_required and rollback_ref && STATISTICAL_inputs_bound`；requires failure recovery + rollback ref; pre/post and no residue; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: 同nonce盲重播或skip未完成工作；刪dataset/改confidence/樣本不達界; mutation: `/outcome/recovery/statistical := __CORRUPT__053` → `RECOVERY_STATE_MISMATCH`；`AC-C39-RECOVERY-STATISTICAL`; FirstFail=`RECOVERY_STATE_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-RECOVERY-SEMANTIC_JUDGE` | RECOVERY | SEMANTIC_JUDGE | `118668:120628` / `FHS-BODY-07:L808-819` | Input: 本TestClass domain=RECOVERY，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 存在restart/timeout/checkpoint情境；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L498，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `effect_or_failure_recovery_required and rollback_ref && SEMANTIC_JUDGE_inputs_bound`；requires failure recovery + rollback ref; pre/post and no residue; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: 同nonce盲重播或skip未完成工作；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/recovery/semantic_judge := __CORRUPT__054` → `RECOVERY_STATE_MISMATCH`；`AC-C39-RECOVERY-SEMANTIC_JUDGE`; FirstFail=`RECOVERY_STATE_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-RECOVERY-HUMAN` | RECOVERY | HUMAN | `120628:122494` / `FHS-BODY-07:L820-831` | Input: 本TestClass domain=RECOVERY，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 存在restart/timeout/checkpoint情境；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L499，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `effect_or_failure_recovery_required and rollback_ref && HUMAN_inputs_bound`；requires failure recovery + rollback ref; pre/post and no residue; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: 同nonce盲重播或skip未完成工作；Maker冒Human或決議是另一scope; mutation: `/outcome/recovery/human := __CORRUPT__055` → `RECOVERY_STATE_MISMATCH`；`AC-C39-RECOVERY-HUMAN`; FirstFail=`RECOVERY_STATE_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-RECOVERY-COMPOSITE` | RECOVERY | COMPOSITE | `122494:124385` / `FHS-BODY-07:L832-843` | Input: 本TestClass domain=RECOVERY，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 存在restart/timeout/checkpoint情境；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L500，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `effect_or_failure_recovery_required and rollback_ref && COMPOSITE_inputs_bound`；requires failure recovery + rollback ref; pre/post and no residue; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: 同nonce盲重播或skip未完成工作；刪hard component或soft分數蓋hard fail; mutation: `/outcome/recovery/composite := __CORRUPT__056` → `RECOVERY_STATE_MISMATCH`；`AC-C39-RECOVERY-COMPOSITE`; FirstFail=`RECOVERY_STATE_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UPGRADE-DETERMINISTIC` | UPGRADE | DETERMINISTIC | `124385:126171` / `FHS-BODY-07:L844-855` | Input: 本TestClass domain=UPGRADE，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=[]；無Raw不可假裝已跑Native。; Applicability: 同asset有來源定義版本migration；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L501，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `upgrade_path_declared and from_version and to_version && DETERMINISTIC_inputs_bound`；requires from/to migration invariant + schema versions; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: 靜默丟欄或拿舊receipt當新版；observed_value改成非expected; mutation: `/outcome/upgrade/deterministic := __CORRUPT__057` → `UPGRADE_VERSION_MISMATCH`；`AC-C39-UPGRADE-DETERMINISTIC`; FirstFail=`UPGRADE_VERSION_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UPGRADE-STATE_READBACK` | UPGRADE | STATE_READBACK | `126171:128030` / `FHS-BODY-07:L856-867` | Input: 本TestClass domain=UPGRADE，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=[]；無Raw不可假裝已跑Native。; Applicability: 同asset有來源定義版本migration；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L502，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `upgrade_path_declared and from_version and to_version && STATE_READBACK_inputs_bound`；requires from/to migration invariant + schema versions; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: 靜默丟欄或拿舊receipt當新版；actual_post_state不同或foreign world Reader; mutation: `/outcome/upgrade/state_readback := __CORRUPT__058` → `UPGRADE_VERSION_MISMATCH`；`AC-C39-UPGRADE-STATE_READBACK`; FirstFail=`UPGRADE_VERSION_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UPGRADE-PROPERTY` | UPGRADE | PROPERTY | `128030:129820` / `FHS-BODY-07:L868-879` | Input: 本TestClass domain=UPGRADE，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=[]；無Raw不可假裝已跑Native。; Applicability: 同asset有來源定義版本migration；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L503，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `upgrade_path_declared and from_version and to_version && PROPERTY_inputs_bound`；requires from/to migration invariant + schema versions; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: 靜默丟欄或拿舊receipt當新版；至少一generated case破invariant; mutation: `/outcome/upgrade/property := __CORRUPT__059` → `UPGRADE_VERSION_MISMATCH`；`AC-C39-UPGRADE-PROPERTY`; FirstFail=`UPGRADE_VERSION_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UPGRADE-REFERENCE_OUTPUT` | UPGRADE | REFERENCE_OUTPUT | `129820:131658` / `FHS-BODY-07:L880-891` | Input: 本TestClass domain=UPGRADE，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=[]；無Raw不可假裝已跑Native。; Applicability: 同asset有來源定義版本migration；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L504，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `upgrade_path_declared and from_version and to_version && REFERENCE_OUTPUT_inputs_bound`；requires from/to migration invariant + schema versions; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: 靜默丟欄或拿舊receipt當新版；更換reference或輸出差異; mutation: `/outcome/upgrade/reference_output := __CORRUPT__060` → `UPGRADE_VERSION_MISMATCH`；`AC-C39-UPGRADE-REFERENCE_OUTPUT`; FirstFail=`UPGRADE_VERSION_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UPGRADE-STATISTICAL` | UPGRADE | STATISTICAL | `131658:133479` / `FHS-BODY-07:L892-903` | Input: 本TestClass domain=UPGRADE，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=[]；無Raw不可假裝已跑Native。; Applicability: 同asset有來源定義版本migration；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L505，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `upgrade_path_declared and from_version and to_version && STATISTICAL_inputs_bound`；requires from/to migration invariant + schema versions; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: 靜默丟欄或拿舊receipt當新版；刪dataset/改confidence/樣本不達界; mutation: `/outcome/upgrade/statistical := __CORRUPT__061` → `UPGRADE_VERSION_MISMATCH`；`AC-C39-UPGRADE-STATISTICAL`; FirstFail=`UPGRADE_VERSION_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UPGRADE-SEMANTIC_JUDGE` | UPGRADE | SEMANTIC_JUDGE | `133479:135342` / `FHS-BODY-07:L904-915` | Input: 本TestClass domain=UPGRADE，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=[]；無Raw不可假裝已跑Native。; Applicability: 同asset有來源定義版本migration；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L506，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `upgrade_path_declared and from_version and to_version && SEMANTIC_JUDGE_inputs_bound`；requires from/to migration invariant + schema versions; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: 靜默丟欄或拿舊receipt當新版；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/upgrade/semantic_judge := __CORRUPT__062` → `UPGRADE_VERSION_MISMATCH`；`AC-C39-UPGRADE-SEMANTIC_JUDGE`; FirstFail=`UPGRADE_VERSION_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UPGRADE-HUMAN` | UPGRADE | HUMAN | `135342:137111` / `FHS-BODY-07:L916-927` | Input: 本TestClass domain=UPGRADE，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=[]；無Raw不可假裝已跑Native。; Applicability: 同asset有來源定義版本migration；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L507，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `upgrade_path_declared and from_version and to_version && HUMAN_inputs_bound`；requires from/to migration invariant + schema versions; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: 靜默丟欄或拿舊receipt當新版；Maker冒Human或決議是另一scope; mutation: `/outcome/upgrade/human := __CORRUPT__063` → `UPGRADE_VERSION_MISMATCH`；`AC-C39-UPGRADE-HUMAN`; FirstFail=`UPGRADE_VERSION_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UPGRADE-COMPOSITE` | UPGRADE | COMPOSITE | `137111:138906` / `FHS-BODY-07:L928-939` | Input: 本TestClass domain=UPGRADE，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=[]；無Raw不可假裝已跑Native。; Applicability: 同asset有來源定義版本migration；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L508，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `upgrade_path_declared and from_version and to_version && COMPOSITE_inputs_bound`；requires from/to migration invariant + schema versions; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: 靜默丟欄或拿舊receipt當新版；刪hard component或soft分數蓋hard fail; mutation: `/outcome/upgrade/composite := __CORRUPT__064` → `UPGRADE_VERSION_MISMATCH`；`AC-C39-UPGRADE-COMPOSITE`; FirstFail=`UPGRADE_VERSION_MISMATCH` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-ROLLBACK-DETERMINISTIC` | ROLLBACK | DETERMINISTIC | `138906:140823` / `FHS-BODY-07:L940-951` | Input: 本TestClass domain=ROLLBACK，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 本effect可回復或需補償；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L509，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `mutating_effect and rollback_ref and preimage_digest && DETERMINISTIC_inputs_bound`；requires mutating effect + preimage; exact state restore; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: 只刪log卻稱回復世界；observed_value改成非expected; mutation: `/outcome/rollback/deterministic := __CORRUPT__065` → `ROLLBACK_PREIMAGE_MISSING`；`AC-C39-ROLLBACK-DETERMINISTIC`; FirstFail=`ROLLBACK_PREIMAGE_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-ROLLBACK-STATE_READBACK` | ROLLBACK | STATE_READBACK | `140823:142813` / `FHS-BODY-07:L952-963` | Input: 本TestClass domain=ROLLBACK，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 本effect可回復或需補償；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L510，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `mutating_effect and rollback_ref and preimage_digest && STATE_READBACK_inputs_bound`；requires mutating effect + preimage; exact state restore; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: 只刪log卻稱回復世界；actual_post_state不同或foreign world Reader; mutation: `/outcome/rollback/state_readback := __CORRUPT__066` → `ROLLBACK_PREIMAGE_MISSING`；`AC-C39-ROLLBACK-STATE_READBACK`; FirstFail=`ROLLBACK_PREIMAGE_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-ROLLBACK-PROPERTY` | ROLLBACK | PROPERTY | `142813:144734` / `FHS-BODY-07:L964-975` | Input: 本TestClass domain=ROLLBACK，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 本effect可回復或需補償；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L511，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `mutating_effect and rollback_ref and preimage_digest && PROPERTY_inputs_bound`；requires mutating effect + preimage; exact state restore; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: 只刪log卻稱回復世界；至少一generated case破invariant; mutation: `/outcome/rollback/property := __CORRUPT__067` → `ROLLBACK_PREIMAGE_MISSING`；`AC-C39-ROLLBACK-PROPERTY`; FirstFail=`ROLLBACK_PREIMAGE_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-ROLLBACK-REFERENCE_OUTPUT` | ROLLBACK | REFERENCE_OUTPUT | `144734:146703` / `FHS-BODY-07:L976-987` | Input: 本TestClass domain=ROLLBACK，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 本effect可回復或需補償；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L512，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `mutating_effect and rollback_ref and preimage_digest && REFERENCE_OUTPUT_inputs_bound`；requires mutating effect + preimage; exact state restore; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: 只刪log卻稱回復世界；更換reference或輸出差異; mutation: `/outcome/rollback/reference_output := __CORRUPT__068` → `ROLLBACK_PREIMAGE_MISSING`；`AC-C39-ROLLBACK-REFERENCE_OUTPUT`; FirstFail=`ROLLBACK_PREIMAGE_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-ROLLBACK-STATISTICAL` | ROLLBACK | STATISTICAL | `146703:148656` / `FHS-BODY-07:L988-999` | Input: 本TestClass domain=ROLLBACK，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 本effect可回復或需補償；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L513，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `mutating_effect and rollback_ref and preimage_digest && STATISTICAL_inputs_bound`；requires mutating effect + preimage; exact state restore; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: 只刪log卻稱回復世界；刪dataset/改confidence/樣本不達界; mutation: `/outcome/rollback/statistical := __CORRUPT__069` → `ROLLBACK_PREIMAGE_MISSING`；`AC-C39-ROLLBACK-STATISTICAL`; FirstFail=`ROLLBACK_PREIMAGE_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-ROLLBACK-SEMANTIC_JUDGE` | ROLLBACK | SEMANTIC_JUDGE | `148656:150651` / `FHS-BODY-07:L1000-1011` | Input: 本TestClass domain=ROLLBACK，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 本effect可回復或需補償；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L514，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `mutating_effect and rollback_ref and preimage_digest && SEMANTIC_JUDGE_inputs_bound`；requires mutating effect + preimage; exact state restore; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: 只刪log卻稱回復世界；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/rollback/semantic_judge := __CORRUPT__070` → `ROLLBACK_PREIMAGE_MISSING`；`AC-C39-ROLLBACK-SEMANTIC_JUDGE`; FirstFail=`ROLLBACK_PREIMAGE_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-ROLLBACK-HUMAN` | ROLLBACK | HUMAN | `150651:152552` / `FHS-BODY-07:L1012-1023` | Input: 本TestClass domain=ROLLBACK，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 本effect可回復或需補償；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L515，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `mutating_effect and rollback_ref and preimage_digest && HUMAN_inputs_bound`；requires mutating effect + preimage; exact state restore; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: 只刪log卻稱回復世界；Maker冒Human或決議是另一scope; mutation: `/outcome/rollback/human := __CORRUPT__071` → `ROLLBACK_PREIMAGE_MISSING`；`AC-C39-ROLLBACK-HUMAN`; FirstFail=`ROLLBACK_PREIMAGE_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-ROLLBACK-COMPOSITE` | ROLLBACK | COMPOSITE | `152552:154478` / `FHS-BODY-07:L1024-1035` | Input: 本TestClass domain=ROLLBACK，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 本effect可回復或需補償；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L516，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `mutating_effect and rollback_ref and preimage_digest && COMPOSITE_inputs_bound`；requires mutating effect + preimage; exact state restore; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: 只刪log卻稱回復世界；刪hard component或soft分數蓋hard fail; mutation: `/outcome/rollback/composite := __CORRUPT__072` → `ROLLBACK_PREIMAGE_MISSING`；`AC-C39-ROLLBACK-COMPOSITE`; FirstFail=`ROLLBACK_PREIMAGE_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UNINSTALL-DETERMINISTIC` | UNINSTALL | DETERMINISTIC | `154478:156370` / `FHS-BODY-07:L1036-1047` | Input: 本TestClass domain=UNINSTALL，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-OWNED-REMOVE', 'CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: 該asset有Host安裝/loaded effect；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L517，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `installation_workpackage and retention_policy && DETERMINISTIC_inputs_bound`；requires installed workpackage + retention; no stale hooks; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: copy刪除但Host仍loaded；observed_value改成非expected; mutation: `/outcome/uninstall/deterministic := __CORRUPT__073` → `UNINSTALL_RESIDUE`；`AC-C39-UNINSTALL-DETERMINISTIC`; FirstFail=`UNINSTALL_RESIDUE` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UNINSTALL-STATE_READBACK` | UNINSTALL | STATE_READBACK | `156370:158335` / `FHS-BODY-07:L1048-1059` | Input: 本TestClass domain=UNINSTALL，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-OWNED-REMOVE', 'CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: 該asset有Host安裝/loaded effect；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L518，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `installation_workpackage and retention_policy && STATE_READBACK_inputs_bound`；requires installed workpackage + retention; no stale hooks; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: copy刪除但Host仍loaded；actual_post_state不同或foreign world Reader; mutation: `/outcome/uninstall/state_readback := __CORRUPT__074` → `UNINSTALL_RESIDUE`；`AC-C39-UNINSTALL-STATE_READBACK`; FirstFail=`UNINSTALL_RESIDUE` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UNINSTALL-PROPERTY` | UNINSTALL | PROPERTY | `158335:160231` / `FHS-BODY-07:L1060-1071` | Input: 本TestClass domain=UNINSTALL，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-OWNED-REMOVE', 'CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: 該asset有Host安裝/loaded effect；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L519，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `installation_workpackage and retention_policy && PROPERTY_inputs_bound`；requires installed workpackage + retention; no stale hooks; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: copy刪除但Host仍loaded；至少一generated case破invariant; mutation: `/outcome/uninstall/property := __CORRUPT__075` → `UNINSTALL_RESIDUE`；`AC-C39-UNINSTALL-PROPERTY`; FirstFail=`UNINSTALL_RESIDUE` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UNINSTALL-REFERENCE_OUTPUT` | UNINSTALL | REFERENCE_OUTPUT | `160231:162175` / `FHS-BODY-07:L1072-1083` | Input: 本TestClass domain=UNINSTALL，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-OWNED-REMOVE', 'CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: 該asset有Host安裝/loaded effect；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L520，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `installation_workpackage and retention_policy && REFERENCE_OUTPUT_inputs_bound`；requires installed workpackage + retention; no stale hooks; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: copy刪除但Host仍loaded；更換reference或輸出差異; mutation: `/outcome/uninstall/reference_output := __CORRUPT__076` → `UNINSTALL_RESIDUE`；`AC-C39-UNINSTALL-REFERENCE_OUTPUT`; FirstFail=`UNINSTALL_RESIDUE` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UNINSTALL-STATISTICAL` | UNINSTALL | STATISTICAL | `162175:164103` / `FHS-BODY-07:L1084-1095` | Input: 本TestClass domain=UNINSTALL，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-OWNED-REMOVE', 'CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: 該asset有Host安裝/loaded effect；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L521，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `installation_workpackage and retention_policy && STATISTICAL_inputs_bound`；requires installed workpackage + retention; no stale hooks; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: copy刪除但Host仍loaded；刪dataset/改confidence/樣本不達界; mutation: `/outcome/uninstall/statistical := __CORRUPT__077` → `UNINSTALL_RESIDUE`；`AC-C39-UNINSTALL-STATISTICAL`; FirstFail=`UNINSTALL_RESIDUE` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UNINSTALL-SEMANTIC_JUDGE` | UNINSTALL | SEMANTIC_JUDGE | `164103:166073` / `FHS-BODY-07:L1096-1107` | Input: 本TestClass domain=UNINSTALL，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-OWNED-REMOVE', 'CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: 該asset有Host安裝/loaded effect；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L522，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `installation_workpackage and retention_policy && SEMANTIC_JUDGE_inputs_bound`；requires installed workpackage + retention; no stale hooks; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: copy刪除但Host仍loaded；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/uninstall/semantic_judge := __CORRUPT__078` → `UNINSTALL_RESIDUE`；`AC-C39-UNINSTALL-SEMANTIC_JUDGE`; FirstFail=`UNINSTALL_RESIDUE` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UNINSTALL-HUMAN` | UNINSTALL | HUMAN | `166073:167949` / `FHS-BODY-07:L1108-1119` | Input: 本TestClass domain=UNINSTALL，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-OWNED-REMOVE', 'CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: 該asset有Host安裝/loaded effect；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L523，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `installation_workpackage and retention_policy && HUMAN_inputs_bound`；requires installed workpackage + retention; no stale hooks; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: copy刪除但Host仍loaded；Maker冒Human或決議是另一scope; mutation: `/outcome/uninstall/human := __CORRUPT__079` → `UNINSTALL_RESIDUE`；`AC-C39-UNINSTALL-HUMAN`; FirstFail=`UNINSTALL_RESIDUE` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-UNINSTALL-COMPOSITE` | UNINSTALL | COMPOSITE | `167949:169850` / `FHS-BODY-07:L1120-1131` | Input: 本TestClass domain=UNINSTALL，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-UNINSTALL-OWNED-REMOVE', 'CLI-UNINSTALL-FOREIGN-DENY']；無Raw不可假裝已跑Native。; Applicability: 該asset有Host安裝/loaded effect；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L524，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `installation_workpackage and retention_policy && COMPOSITE_inputs_bound`；requires installed workpackage + retention; no stale hooks; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: copy刪除但Host仍loaded；刪hard component或soft分數蓋hard fail; mutation: `/outcome/uninstall/composite := __CORRUPT__080` → `UNINSTALL_RESIDUE`；`AC-C39-UNINSTALL-COMPOSITE`; FirstFail=`UNINSTALL_RESIDUE` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-MUT-DETERMINISTIC` | MUT | DETERMINISTIC | `169850:171640` / `FHS-BODY-07:L1132-1143` | Input: 本TestClass domain=MUT，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 本domain可構造破壞性mutation；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L525，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `testable_predicate and mutation_operator and fixed_seed && DETERMINISTIC_inputs_bound`；requires testable predicate + operator + fixed seed; mutant killed; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: oracle忽略被mutate欄位；observed_value改成非expected; mutation: `/outcome/mut/deterministic := __CORRUPT__081` → `MUTANT_SURVIVED`；`AC-C39-MUT-DETERMINISTIC`; FirstFail=`MUTANT_SURVIVED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-MUT-STATE_READBACK` | MUT | STATE_READBACK | `171640:173503` / `FHS-BODY-07:L1144-1155` | Input: 本TestClass domain=MUT，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 本domain可構造破壞性mutation；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L526，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `testable_predicate and mutation_operator and fixed_seed && STATE_READBACK_inputs_bound`；requires testable predicate + operator + fixed seed; mutant killed; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: oracle忽略被mutate欄位；actual_post_state不同或foreign world Reader; mutation: `/outcome/mut/state_readback := __CORRUPT__082` → `MUTANT_SURVIVED`；`AC-C39-MUT-STATE_READBACK`; FirstFail=`MUTANT_SURVIVED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-MUT-PROPERTY` | MUT | PROPERTY | `173503:175297` / `FHS-BODY-07:L1156-1167` | Input: 本TestClass domain=MUT，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 本domain可構造破壞性mutation；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L527，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `testable_predicate and mutation_operator and fixed_seed && PROPERTY_inputs_bound`；requires testable predicate + operator + fixed seed; mutant killed; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: oracle忽略被mutate欄位；至少一generated case破invariant; mutation: `/outcome/mut/property := __CORRUPT__083` → `MUTANT_SURVIVED`；`AC-C39-MUT-PROPERTY`; FirstFail=`MUTANT_SURVIVED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-MUT-REFERENCE_OUTPUT` | MUT | REFERENCE_OUTPUT | `175297:177139` / `FHS-BODY-07:L1168-1179` | Input: 本TestClass domain=MUT，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 本domain可構造破壞性mutation；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L528，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `testable_predicate and mutation_operator and fixed_seed && REFERENCE_OUTPUT_inputs_bound`；requires testable predicate + operator + fixed seed; mutant killed; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: oracle忽略被mutate欄位；更換reference或輸出差異; mutation: `/outcome/mut/reference_output := __CORRUPT__084` → `MUTANT_SURVIVED`；`AC-C39-MUT-REFERENCE_OUTPUT`; FirstFail=`MUTANT_SURVIVED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-MUT-STATISTICAL` | MUT | STATISTICAL | `177139:178968` / `FHS-BODY-07:L1180-1191` | Input: 本TestClass domain=MUT，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 本domain可構造破壞性mutation；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L529，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `testable_predicate and mutation_operator and fixed_seed && STATISTICAL_inputs_bound`；requires testable predicate + operator + fixed seed; mutant killed; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: oracle忽略被mutate欄位；刪dataset/改confidence/樣本不達界; mutation: `/outcome/mut/statistical := __CORRUPT__085` → `MUTANT_SURVIVED`；`AC-C39-MUT-STATISTICAL`; FirstFail=`MUTANT_SURVIVED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-MUT-SEMANTIC_JUDGE` | MUT | SEMANTIC_JUDGE | `178968:180839` / `FHS-BODY-07:L1192-1203` | Input: 本TestClass domain=MUT，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 本domain可構造破壞性mutation；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L530，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `testable_predicate and mutation_operator and fixed_seed && SEMANTIC_JUDGE_inputs_bound`；requires testable predicate + operator + fixed seed; mutant killed; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: oracle忽略被mutate欄位；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/mut/semantic_judge := __CORRUPT__086` → `MUTANT_SURVIVED`；`AC-C39-MUT-SEMANTIC_JUDGE`; FirstFail=`MUTANT_SURVIVED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-MUT-HUMAN` | MUT | HUMAN | `180839:182616` / `FHS-BODY-07:L1204-1215` | Input: 本TestClass domain=MUT，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 本domain可構造破壞性mutation；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L531，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `testable_predicate and mutation_operator and fixed_seed && HUMAN_inputs_bound`；requires testable predicate + operator + fixed seed; mutant killed; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: oracle忽略被mutate欄位；Maker冒Human或決議是另一scope; mutation: `/outcome/mut/human := __CORRUPT__087` → `MUTANT_SURVIVED`；`AC-C39-MUT-HUMAN`; FirstFail=`MUTANT_SURVIVED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-MUT-COMPOSITE` | MUT | COMPOSITE | `182616:184415` / `FHS-BODY-07:L1216-1227` | Input: 本TestClass domain=MUT，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-LIST-FRESH-PID']；無Raw不可假裝已跑Native。; Applicability: 本domain可構造破壞性mutation；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L532，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `testable_predicate and mutation_operator and fixed_seed && COMPOSITE_inputs_bound`；requires testable predicate + operator + fixed seed; mutant killed; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: oracle忽略被mutate欄位；刪hard component或soft分數蓋hard fail; mutation: `/outcome/mut/composite := __CORRUPT__088` → `MUTANT_SURVIVED`；`AC-C39-MUT-COMPOSITE`; FirstFail=`MUTANT_SURVIVED` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-JOURNEY-DETERMINISTIC` | JOURNEY | DETERMINISTIC | `184415:186459` / `FHS-BODY-07:L1228-1239` | Input: 本TestClass domain=JOURNEY，Oracle=DETERMINISTIC；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 原使用者Goal/FUO跨邊鏈已定義；DETERMINISTIC的required inputs全綁且原source適用；原SRC-L-001:L533，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `consumer_entrypoint and user_outcome_defined and supported_kind && DETERMINISTIC_inputs_bound`；requires consumer entrypoint/outcome and product-kind; real end-user result; Oracle mechanism: `expected_value` → `observed_value`；`exact_eq / observed must equal source-bound expected` | NEG: 只有零件測試沒有使用者成果；observed_value改成非expected; mutation: `/outcome/journey/deterministic := __CORRUPT__089` → `FUNCTIONAL_CONSUMER_MISSING`；`AC-C39-JOURNEY-DETERMINISTIC`; FirstFail=`FUNCTIONAL_CONSUMER_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-JOURNEY-STATE_READBACK` | JOURNEY | STATE_READBACK | `186459:188576` / `FHS-BODY-07:L1240-1251` | Input: 本TestClass domain=JOURNEY，Oracle=STATE_READBACK；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 原使用者Goal/FUO跨邊鏈已定義；STATE_READBACK的required inputs全綁且原source適用；原SRC-L-001:L534，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `consumer_entrypoint and user_outcome_defined and supported_kind && STATE_READBACK_inputs_bound`；requires consumer entrypoint/outcome and product-kind; real end-user result; Oracle mechanism: `pre_digest+expected_post_digest` → `native_world_pre+native_world_post`；`state_transition / pre+post digest from real world` | NEG: 只有零件測試沒有使用者成果；actual_post_state不同或foreign world Reader; mutation: `/outcome/journey/state_readback := __CORRUPT__090` → `FUNCTIONAL_CONSUMER_MISSING`；`AC-C39-JOURNEY-STATE_READBACK`; FirstFail=`FUNCTIONAL_CONSUMER_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-JOURNEY-PROPERTY` | JOURNEY | PROPERTY | `188576:190624` / `FHS-BODY-07:L1252-1263` | Input: 本TestClass domain=JOURNEY，Oracle=PROPERTY；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 原使用者Goal/FUO跨邊鏈已定義；PROPERTY的required inputs全綁且原source適用；原SRC-L-001:L535，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `consumer_entrypoint and user_outcome_defined and supported_kind && PROPERTY_inputs_bound`；requires consumer entrypoint/outcome and product-kind; real end-user result; Oracle mechanism: `invariant+seed` → `generated_cases+minimal_counterexample`；`all_invariant / seeded generated cases + shrunk counterexample` | NEG: 只有零件測試沒有使用者成果；至少一generated case破invariant; mutation: `/outcome/journey/property := __CORRUPT__091` → `FUNCTIONAL_CONSUMER_MISSING`；`AC-C39-JOURNEY-PROPERTY`; FirstFail=`FUNCTIONAL_CONSUMER_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-JOURNEY-REFERENCE_OUTPUT` | JOURNEY | REFERENCE_OUTPUT | `190624:192720` / `FHS-BODY-07:L1264-1275` | Input: 本TestClass domain=JOURNEY，Oracle=REFERENCE_OUTPUT；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 原使用者Goal/FUO跨邊鏈已定義；REFERENCE_OUTPUT的required inputs全綁且原source適用；原SRC-L-001:L536，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `consumer_entrypoint and user_outcome_defined and supported_kind && REFERENCE_OUTPUT_inputs_bound`；requires consumer entrypoint/outcome and product-kind; real end-user result; Oracle mechanism: `reference_sha+canonical_output` → `observed_output`；`pinned_reference_eq / reference SHA pinned` | NEG: 只有零件測試沒有使用者成果；更換reference或輸出差異; mutation: `/outcome/journey/reference_output := __CORRUPT__092` → `FUNCTIONAL_CONSUMER_MISSING`；`AC-C39-JOURNEY-REFERENCE_OUTPUT`; FirstFail=`FUNCTIONAL_CONSUMER_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-JOURNEY-STATISTICAL` | JOURNEY | STATISTICAL | `192720:194799` / `FHS-BODY-07:L1276-1287` | Input: 本TestClass domain=JOURNEY，Oracle=STATISTICAL；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 原使用者Goal/FUO跨邊鏈已定義；STATISTICAL的required inputs全綁且原source適用；原SRC-L-001:L537，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `consumer_entrypoint and user_outcome_defined and supported_kind && STATISTICAL_inputs_bound`；requires consumer entrypoint/outcome and product-kind; real end-user result; Oracle mechanism: `dataset_sha+calibration_sha+confidence+threshold` → `sample_metrics`；`bound_confidence / dataset+calibration+threshold` | NEG: 只有零件測試沒有使用者成果；刪dataset/改confidence/樣本不達界; mutation: `/outcome/journey/statistical := __CORRUPT__093` → `FUNCTIONAL_CONSUMER_MISSING`；`AC-C39-JOURNEY-STATISTICAL`; FirstFail=`FUNCTIONAL_CONSUMER_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-JOURNEY-SEMANTIC_JUDGE` | JOURNEY | SEMANTIC_JUDGE | `194799:196920` / `FHS-BODY-07:L1288-1299` | Input: 本TestClass domain=JOURNEY，Oracle=SEMANTIC_JUDGE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 原使用者Goal/FUO跨邊鏈已定義；SEMANTIC_JUDGE的required inputs全綁且原source適用；原SRC-L-001:L538，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `consumer_entrypoint and user_outcome_defined and supported_kind && SEMANTIC_JUDGE_inputs_bound`；requires consumer entrypoint/outcome and product-kind; real end-user result; Oracle mechanism: `rubric_sha+judge_model_pin+human_calibration` → `scores+disagreements`；`calibrated_rubric / model+human calibration+disagreement` | NEG: 只有零件測試沒有使用者成果；judge未校準/不同rubric卻聲稱一致; mutation: `/outcome/journey/semantic_judge := __CORRUPT__094` → `FUNCTIONAL_CONSUMER_MISSING`；`AC-C39-JOURNEY-SEMANTIC_JUDGE`; FirstFail=`FUNCTIONAL_CONSUMER_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-JOURNEY-HUMAN` | JOURNEY | HUMAN | `196920:198947` / `FHS-BODY-07:L1300-1311` | Input: 本TestClass domain=JOURNEY，Oracle=HUMAN；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 原使用者Goal/FUO跨邊鏈已定義；HUMAN的required inputs全綁且原source適用；原SRC-L-001:L539，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `consumer_entrypoint and user_outcome_defined and supported_kind && HUMAN_inputs_bound`；requires consumer entrypoint/outcome and product-kind; real end-user result; Oracle mechanism: `rubric+principal+consent_or_basis` → `signed_human_decision`；`rights_veto / real authorized principal, consent and signed decision` | NEG: 只有零件測試沒有使用者成果；Maker冒Human或決議是另一scope; mutation: `/outcome/journey/human := __CORRUPT__095` → `FUNCTIONAL_CONSUMER_MISSING`；`AC-C39-JOURNEY-HUMAN`; FirstFail=`FUNCTIONAL_CONSUMER_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |
| `AC-C39-JOURNEY-COMPOSITE` | JOURNEY | COMPOSITE | `198947:200967` / `FHS-BODY-07:L1312-1328` | Input: 本TestClass domain=JOURNEY，Oracle=COMPOSITE；同Subject/scope/source。實際私有CLI Raw refs=['CLI-POS-EMPTY-LIST', 'CLI-POS-ADD', 'CLI-POS-LIST-FRESH-PID', 'CLI-ROLLBACK-REMOVE', 'CLI-JOURNEY-FINAL-EMPTY']；無Raw不可假裝已跑Native。; Applicability: 原使用者Goal/FUO跨邊鏈已定義；COMPOSITE的required inputs全綁且原source適用；原SRC-L-001:L540，SHA `0af1fd914a2bbb1f3221c4959facc6d0bbb4b43d4a6d385ed57f9cde8f8eab99`。; Source predicate: `consumer_entrypoint and user_outcome_defined and supported_kind && COMPOSITE_inputs_bound`；requires consumer entrypoint/outcome and product-kind; real end-user result; Oracle mechanism: `components+ordering+failure_policy` → `component_raw_receipts`；`all_hard_and / ordered hard component receipts` | NEG: 只有零件測試沒有使用者成果；刪hard component或soft分數蓋hard fail; mutation: `/outcome/journey/composite := __CORRUPT__096` → `FUNCTIONAL_CONSUMER_MISSING`；`AC-C39-JOURNEY-COMPOSITE`; FirstFail=`FUNCTIONAL_CONSUMER_MISSING` | Original Case/Oracle Reader→Protected Checker；Runner/Raw=`NOT_OBSERVED`；`ORACLE_RUNNER_BIND_HOLD` |

**異構拒收示例**：`DETERMINISTIC` 檢測原 `expected_value/observed_value`；`STATE_READBACK` 必驗原世界 `pre/post_digest` 而不是只比 JSON；`STATISTICAL` 必由原校準 Reader 提供樣本與門檻；`SEMANTIC_JUDGE`、`HUMAN`、`COMPOSITE` 不得用 Maker 字串替代受保護評議。對任何同名 Case 的 Host/Profile/SourceSHA/Subject／原 Registry 失配，只影響其 Case cone，FirstFail=`ORACLE_TYPE_OR_SCOPE_MISMATCH`。

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：W0 WP21 規劃 96 Oracle、六帳。
- **獨立輸入**：BODY-07 96 source clauses+TQAEP Original TestClass×OracleType、六 Ledger join。
- **原有能力導向操作**：逐 TestClass/OracleType 以原條文 POS/NEG/WorldRaw schema／Checker Reader 建 PlannableCase；SPEC_LEDGER 作 Requirement/Case 中間 Join。
- **可觀察輸出／First Useful Outcome**：96 TypedCasePlan+六 Ledger 字典+原 Checker scoped HOLD。
- **原 Reader／Consumer**：Original Case/Spec/Checker Reader。
- **正反驗收與 FirstFail**：POS Case 各有實質來源 span+專屬 NEG；NEG 96 generic ORACLE/同一 fixture → ORACLE_TYPE_OR_SCOPE_MISMATCH。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-42](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-42)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### W0 六 Ledger 的可計算 Join Gate 與 96 Oracle 等級

六帳 `SOURCE_LEDGER → REQUIREMENT_LEDGER → SPEC_LEDGER → CASE_LEDGER → EVIDENCE_EXPECTATION_LEDGER → DELIVER_LEDGER` 的最低契約見本 CH r4 原表；在 W0 只建立**隔離唯讀投影**。每個 Case 必能反向回 `OriginalID→SourceSHA→ByteSpan→Parent/NEG`，`SpecClauseID` 不得取代 OriginalID。`OriginalCaseID=AC-C39-<TestClass>-<OracleType>` 有獨立 POS/NEG/FirstFail，12 TestClass×8 OracleType=96 原型別；本輪 status 一律 `PLANNED_NOT_RUN`，`ExpectedWorldRawSchema` 只可寫 `EXPECTED_NOT_OBSERVED`。

| Gate | 可讀回條件 | 受影負例／FirstFail | 原 Reader/Owner |
|---|---|---|---|
| E1 Source | 31 SourceID hash 與當期版本分欄 | 來源不在 snapshot；`SOURCE_IDENTITY_HOLD` | Original Source Reader |
| E2 Requirement | 原 Parent/Child/NEG/例外雙向完整 | Child 找不到原 Parent；`REQUIREMENT_PARENT_NEG_HOLD` | SBL Product/Requirement Reader |
| E3 SPEC | 每 Product/Architecture/Program 條位的不同 Consumer 和 ACC± | 三 SPEC 純換標題；`SPEC_TRACE_BROKEN` | SBL TPM／PIPD Intake Reader |
| E4 Case | 96 CaseID 的 OracleType、輸入、POS、NEG、FirstFail 可定位 | 96 共用單一 fake fixture；`CASE_JOIN_OR_ORACLE_HOLD` | AC Original Registry |
| E5 Evidence | Host/Effect/WorldRaw schema 與 observed 分離 | 字串 PASS 無 Raw；`EVIDENCE_LAUNDERING_DENY` | Original TQAEP/Protected Checker |
| E6 Delivery | DeliverID 回追 Case/Spec/Source，同 Scope Reader 受領 | ZIP 完成就稱 Release；`DELIVER_CHAIN_BROKEN` | Original Delivery/Publisher |

**結果**：`SIX_LEDGER_JOIN_PLAN`，不產正式 `Qualified Verdict`。缺 Original Runner / Checker credential 只 Hold 受影 Case；其他合法 W0 讀取、草案和不需要 Host 的負例靜態檢查仍可完成。



### r3 當期條款｜W0_REQUIRED22 六帳雙向實體 join（AUD-W0-P1-008/009）

每一列以 L1 r4 真 SHA/物理 row 及原 Parent/NEG/condition，連到同 Subject 但不同 Product/Architecture/Program SpecClause，再接獨立作者 Case fixture、EvidenceExpectation、DeliverID、原 WP/需求波/施工主波、Original Consumer。W0_REQUIRED22_TRACE.json、TRACE_GRAPH.json、trace_fixtures/ 是具體可回讀工件；任一 source→requirement→spec→case→evidence→deliver 邊被移除首失 TRACE_JOIN_NOT_MATERIALIZED，反向邊也必由實際節點重算。

本 22 列完成的是作者端 scoped-row trace；U0=指定 row bytes pin、U1=本列義務/NEG 分離、U2=author雙向join、U3=SpecDelta候選、U4=ORIGINAL_OWNER_ACK_NOT_OBSERVED。31 冊完整 byte partition、逐義 Parent/exception/Original Owner semantic closure 未由數量驗證取得。三份獨立實物 SPEC_Product_r3.md、SPEC_Architecture_r3.md、SPEC_Program_r3.md 給不同 Reader，禁止同文換標題或 SHA→U4 升格。


# CH-43｜ClaimCeiling、測量層、Producer/Checker/Publisher 的不同責任

<a id="ch-43"></a>

## r4 當期 L3 合法正文｜`CH-43`：主波 W4（L2 r4 §6）
**W0 非主責，唯一主波是 W4。** `CH-43` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W4 專屬規格與 Native 權威。

**原產品主題／受影接收**：ClaimCeiling、測量層、Producer/Checker/Publisher 的不同責任。主波 L3 收件 `W4_藍圖&skeleton → W4_草案 → W4_定案`；原 Consumer：Original ClaimCeiling Owner。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W4 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W4_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-15` `L1-r4:L783` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer、Original Oracle/Protected Checker Reader | POS/NEG/Case/Raw/SourceSHA，符合原 Principal 差異 | Maker 自簽 Independent、沒有實際 Runner Raw 卻宣 PASS；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-18` `L1-r4:L786` | W0 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、HGK Original Issuer/SharedSpine/Protected Checker Reader、Effect-spe | 六類 Effect 對應最低充分原 Evidence | 缺 OPS/RELEASE Permission 使合法 READ/DRAFT 全域停工；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-033` `L1-r4:L830` | W2 | HGK Original Issuer/SharedSpine/Protected Checker Reader | 獨立驗收只有相應原授權主體可出 | 雙 GPT review 冒 Independent；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-051` `L1-r4:L848` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 原受權發行收據 | PR Green/Markdown signed 誤宣 RELEASE；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案增補｜跨波原責任保留與准入規劃
### 五層證據與本草案 ClaimCeiling（主波 W4）

`SNAPSHOT_SHA_VERIFIED → AUTHOR_DRAFT_STATIC_READBACK → ORIGINAL_READER_ACK → NATIVE_WORLD_RAW → PROTECTED_CHECKER_VERDICT/PUBLISHER_RELEASE` 是不同的證據類別，不是一步自動提升狀態。本包僅到第二層，不在 W0 要求全部 Release/Independent 收據；日後若原 Reader 不受領，HOLD 其受影子圖，保留合法來源讀取和作者草案成果。
### r4-candidate｜作者端靜態重播的唯一入口與 NEG 代碼字彙對齊（D2 收斂）

**（1）入口事實與修補**。r3 的 `REPRODUCE_AUTHOR_STATIC.md` 記載 `python work/static_checker.py work/candidate_r3`，但套件實體根只有 `AUTHOR_STATIC_CHECKER.py`，`work/`、`static_checker.py`、`candidate_r3` 三者皆不存在；且該檢測器只讀 `sys.argv[1]` 當 ROOT，遇到既有 `STATIC_BASELINE_INITIAL.json` 立即 `SystemExit('Baseline already frozen...')`（exit 1），沒有 flag 可繞，因此記載的命令**不可重播**。本版提供三件事，使命令與實體一致：

1. `work/static_checker.py` 薄 shim（內容等同 `AUTHOR_STATIC_CHECKER.py`，SHA 記錄於 `INDEX_AND_MANIFEST_r4-candidate-b41d2e.json`）；
2. 三個顯式參數 `--root`、`--baseline-out`、`--allow-rebaseline`：baseline 一律寫到 runner 目錄，永不寫回 r3 原根；
3. 唯一合法命令（隔離 runner，不變更原根）：
   `python AUTHOR_STATIC_CHECKER.py --root <candidate_root> --baseline-out <runner>/STATIC_BASELINE_r4c.json`

**（2）代碼字彙對齊**。25 個 NEG first-fail 碼中 13 個在 r3 正文出現 0 次，protected checker 若以碼比對會落空。以下為唯一 canonical 別名表；每碼必須同時滿足「正文出現」與「對應禁止行為」兩項，否則不得作為拒收碼。

| Canonical code | 禁止行為 | 本版正文錨點 | 對應 Finding／Seam |
|---|---|---|---|
| `CAPABILITY_STATE_ESCALATION` | `SELECTED_DESIGN`／pin HOLD 直寫 `INSTALLED`／`BOUND`／`INVOKED`／`VERIFIED` | CH-23 §r4-candidate 狀態機 | AUD-W0-P1-004 |
| `CASE_GENERIC_ORACLE_LAUNDERING` | 通用 Case 只換 ID、`HUMAN↔DETERMINISTIC` fixture 互換 | CH-30 `ORACLE_TYPE_OR_SCOPE_MISMATCH` 同義 | AUD-W0-P0-002 |
| `DELIVERY_ARTIFACT_NOT_MATERIALIZED` | Index／Manifest 宣稱某包存在，磁碟無檔 | CH-43 本節（配對與交付） | AUD-W0-P2-011 |
| `H1_PROTECTED_CHAPTER_MISSING` | `CH-00..49` 任一 H1 被降級／合併／刪除 | CH-00 H1 不可降級規則 | 結構不變量 |
| `HISTORICAL_E16_RESOLUTION_MISSING` | 以舊 17 分母宣「全部驗證」，或補造 4 條歷史引用 | CH-07／E16 當期 13 條款 | AUD-W0-P1-005 |
| `HOST_POLICY_EFFECTIVE_LOAD_HOLD` | GitHub／Fabric 導航文件當 ActivePolicy／Permit | CH-17／S4 接縫 | S4 |
| `INDEPENDENT_SOD_FAIL` | Maker 自我檢測冒充獨立判決 | CH-39 SoD 條款 | S5 |
| `ORIGINAL_DAG_EDGE_MISSING` | 刪除或重編 E26 等原 36 邊之一 | CH-37 本節 E26 列 | AUD-W0-P0-001 |
| `PAIRED_BODY_BYTES_MISMATCH` | 附錄 `paired_body_sha256`／`bytes` 與實際正文不符 | 附錄配對條款（正文落盤後重算） | AUD-W0-P2-010 |
| `SEMANTIC_RATIFICATION_LAUNDERING` | 以 31/31 SHA 或 GitHub 索引升格為 U4 原 Owner 核簽 | CH-07 U0/U4 分層 | AUD-W0-P1-008 |
| `SPEC_IDENTITY_OR_SOURCE_MISMATCH` | 三 SPEC 同模板換標題，或 SourceSHA 錯置 | CH-11 三 SPEC 異質要求 | S1 |
| `UNKNOWN_RECONCILE_REQUIRED` | `UNKNOWN` 未經 World Reconcile 直接盲重試 | CH-35 UNKNOWN 條款 | S5 |
| `W18_SCOPE_OR_RECEIPT_FRAUD` | 把 W18 改名 W5、提前認證或偽造 Fresh PID 收據 | CH-36 W18 條款 | W18 |

其餘 12 碼（`CANONICAL_WRITER_BOUNDARY`、`CASE_TYPE_OR_SCOPE_MISMATCH`、`DEFAULT_DOWNGRADE_DENY`、`FUTURE_RECEIPT_DEPENDENCY`、`HOST_REPOCONTEXT_UNBOUND`、`METHOD_AS_INSTALL_DENY`、`REQUIREMENT_PARENT_NEG_HOLD`、`SECOND_CONTROL_PLANE_DENY`、`SOURCE_SHA_MISMATCH`、`TRACE_JOIN_NOT_MATERIALIZED`、`WAVE_PRIMARY_CONFLATION`、`WP19_ORIGINAL_OUTPUT_MISSING`）在 r3 正文已出現，維持原文不改。

# CH-44｜CI、供應鏈、部署、Cutover、Rollback 的原服務區分

<a id="ch-44"></a>

## r4 當期 L3 合法正文｜`CH-44`：主波 W4（L2 r4 §6）
**W0 非主責，唯一主波是 W4。** `CH-44` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W4 專屬規格與 Native 權威。

**原產品主題／受影接收**：CI、供應鏈、部署、Cutover、Rollback 的原服務區分。主波 L3 收件 `W4_藍圖&skeleton → W4_草案 → W4_定案`；原 Consumer：Original Publisher/SupplyChain Owner。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W4 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W4_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-20` `L1-r4:L788` | W3 | Original Tech/License/Host/Method Owner → Capability Consumer、Original Program/DAG/Delivery Consumer | Callgraph 等價+Consumer 轉交+受影 POS/NEG+Rollback | 未驗 Caller/Consumer 等價便刪舊技術，HotSwap 後不可回退；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-034` `L1-r4:L831` | W1 | Original Domain Owner/Reader (scope binding pending) | 相應 PR 有真變更與可回退提交 | 憑本檔直接覆寫 main/force push；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-045` `L1-r4:L842` | W3 | Original Tech/License/Host/Method Owner → Capability Consumer | 旧有效功能不能回歸 | 未測就刪 HGK 已用控制面；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-051` `L1-r4:L848` | W2 | Effect-specific original ACL/Repo/Host/Consent/Publisher Consumer | 原受權發行收據 | PR Green/Markdown signed 誤宣 RELEASE；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-057` `L1-r4:L854` | W4 | Original Program/DAG/Delivery Consumer | Publisher 有效 Receipt | 全產品 README 每次必建 SBOM/attestation；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-059` `L1-r4:L856` | W4 | Original Oracle/Protected Checker Reader | 功能與 repo process 都符合 | 測試綠但觸犯禁止直接 main 寫；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-44` Primary=`W4`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。



### r3 當期條款（保留 r2 正確修補並補差額）｜WP19 SupplyChain 條件不等於完整 Release Gate

原 WP19 是 W0 `SOURCE_READ` 規格與必要原資料讀取，要求 CI/License/NOTICE/SBOM/依賴 Manifest 與 `CandidateSHA` 同範圍的 `raw_ref`；缺原 `CI/SupplyChain Reader` readback 的條目只輸出 `W0-CI-READBACK-REQUEST`，不得 `Done=true`，不得稱已跑完整產品級 CI。E26 接原 WP19 Raw，不接作者端的 TraceClosure；W4 `WP14` Release 必以原 Publisher/Checker 的獨立 Gate 為準。

### r3 交付讀表與主張

〔R1-2026-11-06 更正〕原句「唯一現行正文是本候選（generation 2、`artifact_version: 2026-11-05_r4-candidate-b41d2e`）；r3 為歷史父版本」更正為：唯一現行正文是本檔（generation 3、`artifact_version: 2026-11-05_r4-final-c7a91e`、sha256 `0fed31f593fd132ba4f1f2d18df89a03e22e3fbdb6a75ded8bb479f86db884b4`、2254 行）；generation 2（b41d2e）與 r3 均為歷史父版本，只作 lineage。附錄不規範；封存與交付之 ZIP／CRC／SHA 以 c7a91e 封存為準，b41d2e 期之 `INDEX_AND_MANIFEST_r4-candidate-b41d2e.md` 不再代表現行交付。；r3 為歷史父版本。附錄不規範。`INDEX_AND_MANIFEST_r4-candidate-b41d2e.md` 指出實物用途、SHA/bytes/lines/dependencies；`INDEX_AND_MANIFEST_r3.md` 已列為歷史（見 `HISTORICAL_R3_INDEX.json`）。BODY/EVIDENCE/COMPLETE 三真 ZIP 各 reopen/CRC/Manifest 回讀；COMPLETE 含當期正文、非規範附錄、所有必要證據及 E16 當期 13 個 CH 明確歷史 links（控制包舊版17引用數另列 SOURCE_HOLD，不虛造4處）。上位來源與 r2 原物不修改。最終逐 Finding 與必要 Gate 由真 static raw 決定，不能沿用 r2 自報 27/27 或 16/16。

# CH-45｜L0–L3 文件包、DELIVER、原 Consumer ACK 與長期可維護性

<a id="ch-45"></a>

## r4 當期 L3 合法正文｜`CH-45`：主波 W4（L2 r4 §6）
**W0 非主責，唯一主波是 W4。** `CH-45` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W4 專屬規格與 Native 權威。

**原產品主題／受影接收**：L0–L3 文件包、DELIVER、原 Consumer ACK 與長期可維護性。主波 L3 收件 `W4_藍圖&skeleton → W4_草案 → W4_定案`；原 Consumer：FHS L3 Curator + Original Domain Owner。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W4 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W4_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-055` `L1-r4:L852` | W0 | Original Program/DAG/Delivery Consumer | 逐層交 downstream 不改原 Writer | L2 Wave Plan 冒 Native WorkOrder；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-058` `L1-r4:L855` | W4 | Original Program/DAG/Delivery Consumer | Subject/OriginalID/SourceSHA/Effect/Claim 全接線 | 產出本 MD 就宣稱全量正式 PKG 生成；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-45` Primary=`W4`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-46｜成本／FinOps／KnownAnswer 復用及三種 Dogfood Loop

<a id="ch-46"></a>

## r4 當期 L3 合法正文｜`CH-46`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-46` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：成本／FinOps／KnownAnswer 復用及三種 Dogfood Loop。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Product FinOps/Dogfood Owner。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-040` `L1-r4:L837` | W2 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer | 任務能 Crash 恢復且有界停損 | 無限回圈/4h 乾等/無 FirstFail；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-46` Primary=`W3`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

# CH-47｜OpenSpec、gstack、Hermes 外部研究與 Build-or-Use 准入

<a id="ch-47"></a>

## r4 當期 L3 合法正文｜`CH-47`：主波 W3（L2 r4 §6）
**W0 非主責，唯一主波是 W3。** `CH-47` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W3 專屬規格與 Native 權威。

**原產品主題／受影接收**：OpenSpec、gstack、Hermes 外部研究與 Build-or-Use 准入。主波 L3 收件 `W3_藍圖&skeleton → W3_草案 → W3_定案`；原 Consumer：Original Tech/License/Host Reader。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W3 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W3_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `INT-07` `L1-r4:L775` | W1 | Hermes original Runtime/Launcher/Provider Raw Reader → HGK Lane/Journal Consumer、Original Tech/License/Host/Method Owner → Capability C | Hermes Direct/Delegation/Kanban/Swarm 按複雜度選擇，NoFit 才補 | 沒查現有 Hermes 能力便重造 Scheduler/Router；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-16` `L1-r4:L784` | W3 | SBL Original Source/Requirement/Corpus Semantic Reader、Original Tech/License/Host/Method Owner → Capability Consumer | Need→Occupant→Qualified EffectiveLoad→Consumer→Retire | 只讀 485 身份卡便強制安裝 485 件或把必備 Default 改 OPTIONAL；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `INT-24` `L1-r4:L792` | W1 | Original Tech/License/Host/Method Owner → Capability Consumer | OpenSpec proposal/validate；gstack review/QA 轉原 Consumer | OpenSpec/gstack 自發 Canonical PI/Independent Verdict/Publisher Release；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-042` `L1-r4:L839` | W1 | Original Tech/License/Host/Method Owner → Capability Consumer | 需求由已合格工具解決 | 用外部宣傳文即自稱 loaded；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-043` `L1-r4:L840` | W1 | Original Tech/License/Host/Method Owner → Capability Consumer | 規格差額轉原 SBL/PIPD Reader | OpenSpec archive 即原 Owner Ratified；`DESIGN_OBLIGATION_MISSING`（若失卡） |
| `FHS-DR-044` `L1-r4:L841` | W1 | Original Tech/License/Host/Method Owner → Capability Consumer | 原 Runner 能重現 QA Finding | gstack /ship 被當原 Publisher / Independent；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案增補｜跨波原責任保留與准入規劃
### W0 2026-11-04 外部輪子准入裁決（主波 W3，只是 W0 選型提案）

| 能力 | 官方/資料讀回 | 本草案 `SELECTED` 目的 | 版本與實機分離 | 採納、移轉與退場 |
|---|---|---|---|---|
| Hermes | 官方 GitHub v0.22.7 已於 2026-11-03 發布；本專案 **仍釘 v0.22.5** | 原 Profiles/Delegation/Kanban/Swarm/Runtime；依 Need 優先 Native | `v0.22.5 PINNED`；Windows PID/ProfileSHA/ActualServed 未觀測 | 在 W1 真 Host probing + backward/negative parity 後才評估 HotSwap；不得以新 release 自動升級 |
| OpenSpec | Fission-AI 官方 v1.16.0（2026-10-30），MIT；Windows standalone candidate；npm requires Node >=22.12.0，須用官方資產 checksum/原 Host Reader 綁定 | 需求與變更 proposal/validate 的輔助方法 | Windows `openspec --version`, command trigger, exit, spec/change outputs 未觀測 | W1/W3 若原 Consumer 認可且 POS/NEG 有證，才 `INSTALLED→LOADED→INVOKED`；不得變 PIPD Compiler |
| gstack | 官方 README MIT，Host: Claude full、Codex experimental、Hermes instruction-only；團隊 stable channel 以 tag 發行 | `/review`/`/qa`/安全評估作方法；Codex 受界 worker | Windows Bun/Node/Git/Toolchain 和真 skill invocation 未觀測 | 對 Windows Hermes 不可宣稱 fully native；NoFit 只保持該使用點 HOLD，必要時採 Codex 路線或現役工具替代 |
| Codex/FAR | 原 SBL/Fabric Reader 和既有受限 Worker/Research | Diff/test/proposal/來源探查（按 Effect） | 真 CLI/Provider/Policy/ACL/FAR Receiver ACK 未觀測 | 不自建替代對等執行器；無 Raw 原 Consumer 不標 Verified |

**類型**：本章的官方更新是外部研究，不能覆寫本源的 SourceSHA 與原 Domain Owner。工具軌跡須有 `SELECTED / INSTALL_PLANNED / INSTALLED / LOADED / INVOKED / VERIFIED / RETIRED` 加證據，不可把任一階段混寫。Tool-chain 採用前查原 License/SBOM/hash/OS fit；Need 被 `REJECT/REFERENCE_ONLY/METHOD_ONLY/NOFIT` 命中時仍遵原處置。

# CH-48｜受界 ChangeSet、風險／具名 HOLD、Stop-Resume 與決策閉環

<a id="ch-48"></a>

## r4 當期 L3 合法正文｜`CH-48`：主波 W0（L2 r4 §6）
**W0 主責：具名 HOLD 與差額 Resume。** 章義不壓平。引用 L1 r4 同 CH 原生章；L2 r4 §5.0/§6 與本版 SourceManifest。

**User Trigger → 輸入 → 操作 → 輸出／可見結果**：每個 HOLD 包含 OriginalID、affected Scope、Owner、原 Reader、FirstFail、必要 Raw、unblock predicate；先恢復同 Subject/WorkID/Queue cursor；未觸發受保護 Effect 時不要求 OPS Permit，已 admitted WorkID 可續工，Scope/Host/Epoch 變更僅 invalidate 受影依賴。
**原 Writer／Reader／Consumer／責任界線**：Original Scope Owner／HGK Registry/Reader；W0 只提供停/續工提案，無新 EventWriter。
**Acceptance POS**：POS：缺 Host 的 W1 子操作 PARK，但相同來源 W0 草稿照常可完成。
**Acceptance NEG／FirstFail**：NEG：遇一個 License Hold 就停止 31 冊全部讀取；FirstFail=UNBOUNDED_GLOBAL_HOLD。
**W0 最小證據與退出**：來源定位、原 ID/Parent/NEG、同 Subject+Scope 的 Draft/Case ref、受影具名 HOLD、Owner 可讀回；沒有 original Reader ACK 時只完成 AUTHOR_DESIGN。下游若涉及世界效果，以原 `WP-FHS-xx`、原 Receiver/Effect Registry 及適用 W1/W2/W3 交接，不假造 Receipt。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-056` `L1-r4:L853` | W0 | Original Program/DAG/Delivery Consumer | 其他合法來源和 Goal 可繼續 | 因一個 Host/Oracle HOLD 而所有 READ 停工；`DESIGN_OBLIGATION_MISSING`（若失卡） |
### L2 r4 的原 12 HOLD 與受影新增 HOLD（最短解封 Reader，原效力分離）
| 原 HOLD / Question | 未解除的精確原因 | 原負責 Reader／Owner | 所需真證據／解除條件 | 只受阻的 Scope |
|---|---|---|---|---|
| `H-SRC-01` Q02/Q03/Q10 | 31 冊上傳快照與當期 original Effective Canonical/currentness 未齊 | SBL Product Reader、PIPD Original Source/Authority Reader、FHS17 各 Domain Owner | active SourceSHA/version/supersession + OriginalOwner scope ACK；衝突解成同 subject/scope 有效快照 | 需提升為正式規範的 OriginalID，不阻隔離讀取 |
| `H-U0U4-02` Q03/Q10 | `UNIFIED r4` 仍是 extraction PLAN，31 冊全面 U0–U4 未跑 | 後續 Corpus Extractor + 各 Original Owner Semantic Reader | U0 byte partition closure、U1 subclaims/Parent/NEG、U2 original→target join、U3 三 SpecDelta、U4 non-sampled reverse closure 及每筆 Owner ACK/HOLD | 正式語義合併與高保留完成聲明 |
| `H-CELL-03` Q03/Q05 | 192 Cell `legacy=ON/OFF` 的 provider_off 真映射有衝突 | 原 ProductKind/Host/Provider Owner，Cell Table Reader | Original label/domain enum mapping + 相同 Cell 的 ProviderOff POS/NEG；raw token 及原版本必保留 | 受影 Cell 模型調用/ProviderOff Effect |
| `H-PIPD-04` Q02/Q04/Q10 | SBL U04 scoped cutover 不等於實機 original PIPD Reader/Compiler Loaded | SBL PIPD U04 Writer/CLI/Distribution Reader | 同時點原 CLI/19 schema/8 skills、pipd source version、真 Reader reparse；PD 需 live RepoContext/ACL/HEAD | 正式 PI/PD/ECP/TQAEP compile/bind，不阻三 SPEC 草稿 |
| `H-ABI-05` Q04/Q08 | HGK reducer enum、OperationType、S3–S5 Receiver/Writer ABI 未綁 | HGK Original Registry/Native Issuer、Fabric Active Policy Reader、原 Consumer | versioned schema `$id`, original enum, operation scope, `ActivePolicyEpoch+LoadedDigest+ConsumerACK`，WrongSchema/Scope NEG | 受保護 DEV/OPS/Checker 交接 |
| `H-LANE-06` Q05/Q09 | Desired/Selected/ActualServed 與 0.22.5 Kanban `api_mode`/multi-profile 當期實際行為 | HGK Lane RequiredSet Reader、Hermes Host/PID/Provider Raw Reader | Fresh PID、ProfileSHA、TaskPrompt/Request/Transport/API Mode/Response/Error Raw、WorkID 和 RequestID；per-lane negative & fallback | 受影的 PLAN/EXECUTE/VERIFY Worker/Lane |
| `H-TOOLS-07` Q06 | OpenSpec/gstack 選定 release 到本機的 license/Host Fit 不明 | 原 Tech/License/Host Owner、安裝有效載入 Reader | 官方 tag/asset digest/License/SBOM、Node/Bun/Windows、installed/enabled/invoked、trigger/nontrigger、撤銷殘留 | 只停要採用的 ToolMethod；不強制替代已有適用能力 |
| `H-OS-08` Q07/Q08 | 低權限 Runtime / 短命維護 OS token 與技術 Checker 真 SoD 未證 | Windows Host SID/ACL Reader、HGK Trust/Issuer Reader、Protected Checker Credential Reader | OS SID/ACL deny tests、approved token TTL/quota/revocation、Credential/Reader ACK；如有法定雙人條件由原制度 Owner 判 | Policy/Keys/Registry/外部受保護效果，非普通 READ |
| `H-CASES-09` Q08/Q09 | B1 282 Case 與 AC 96 Oracle 的 original Runner/Raw/Checker 實際連結未齊 | Original CaseRegistry/Oracle Owner、Protected Checker | 每受影 Case original `runner_entry,signature,input/output_schema_SHA,oracle_impl,POS_NEG_Raw,subject_scope,checker credential` | 受影 Case 的獨立驗收聲明 |
| `H-W18-10` Q09 | W18 E33–E42、Fresh PID、NormalMode/Resume 未由本輪真測 | Hermes original Launcher/Default Profile/Journal、HGK SharedSpine Reader | 新 PID 啟動、普通 Goal、不貼 B1 長 Prompt、KnownAnswer 復用、三 Lane Served、Unknown world reconcile、GJ real output | `NORMAL_MODE_QUALIFIED` 宣稱，不封鎖已授權舊 WorkID 續工 |
| `H-H1-11` Q10 | **HISTORICAL wording**：50章與 L0–L3 尚未實際編製；當期材料化差額以 §10.3 為準 | L0/L1 後續作者 + Original PIPD Domain Reader / Product Owner | 真 50 H1 各有獨立正文/trace/NEG/Consumer；原 CLI/Reader 真 ACK、T4/T5 原狀態映射 | 正式高保留 L1 完成聲明、PIPD promotion |
| `H-REL-12` Q07/Q08/Q10 | Independent Checker/Publisher/Production 的原收據未取得 | Protected Checker/Original Publisher（不是本 GPT 角色） | Frozen Raw、same Subject/Candidate/Scope/Host/PolicyEpoch 的不同技術 Principal Verdict、Publisher Admission + Release readback | 相應 Release；不阻許可的開發和閱讀 |

**W0-A 不受全面授權缺口牽連**：SOURCE_READ/隔離 Draft 只需對應 read ACL 與用戶授權 root。若待原 `CR-ORACLE-001`、SBL PIPD @2 原 Writer、OS Principal、Policy Epoch，僅阻真受影效應；留下 original id, Subject/Scope, raw needed, firstfail, last_good/checkpoint 和 resume。

### r4 F-005～F-013 Affected HOLD 與撤回／啟用規則

| 修補事項 | 本輪可宣告 | 仍需原 Reader 的受影 HOLD | 受影退出 |
|---|---|---|---|
| F-001 E07 485 Asset 解析 | 485 列四欄與原 ID/Disposition 靜態一致 | 原 License/Host Need→Qualified Occupant | 缺當期 Host fit 時只停該 Need |
| F-002 六 Ledger | 各 Unique ID + 兩方向 Join author read-model | 原 Spec/Requirement/Case Reader 同 Scope ACK | SpecClause 斷鏈只退該 Case |
| F-003 96 Typed Oracle | 96 個 BODY07 真 bytes span/專屬 NEG 設計 | Original Runner/Raw/Protected Checker verdict | 同 Case Runner 未綁只停該 Case |
| F-004 50 當期錨 | current #ch-XX 全在 r4 H1 下 | 不涉及 Native 權限 | 任何 current/history 交錯即回退本文版位 |
| F-005 原始語義 | 31 raw source 保全、U0 行段 bytes proof、24 alias trace | Formal U0–U4、Original Owner negative scope ratification | 受影 source/span NACK 退 W0 Draft；未受影 READ 繼續 |
| F-007/009 L3 Readiness | 完整 §8.2 Envelope／36 operation overlay | 真 Original Consumer/Effect Registry、RepoContext | UNKNOWN 世界效果先 Reconcile，不盲 retry |
| F-008 AssetType | 七類有獨立採納、調用與退出規則 | 真 Host version/license/load/invoke | 沒有真證據不得升級 VERIFIED |
| F-010/012/013 包封 | 修復版兩 MD + ZIP、CRC/SHA + current links | 原域 Release/Owner ACK 不由 ZIP 提供 | ZIP mismatch 禁用修補版 Reader；回 r3 regression baseline |

**User activation**：依本次明確授權，修補 r4 可以取代 r3 作為 **W0 作者端設計閱讀**。遇上游同 Scope Original Effective Reader 異議先以原 Reader 處理、保持 affected `HOLD`；此授權不授與 OS Principal、原 PIPD Compiler、HGK Issuer、Protected Checker、Publisher 的新權限。

### r4 修補後 W0 Primary CH 具體運行/驗收契約（F-005/F-006；保留原義不覆蓋 Canonical）
- **觸發／目標**：受影第一失敗與局部恢復。
- **獨立輸入**：subject/work_id/affected_scope/first_fail/last_good_sha/permission/effect。
- **原有能力導向操作**：只停第一個失敗 cone，READ/DRAFT 繼續；UNKNOWN 必原 World Reconcile、不以 maker 文字自發 retry。
- **可觀察輸出／First Useful Outcome**：HOLD register＋ResumePredicate＋bounded stop/rollback instruction。
- **原 Reader／Consumer**：Original Domain Owner/HGK Reader／W0 DraftMaker。
- **正反驗收與 FirstFail**：POS 未受影子圖不重跑；NEG OPS HOLD 全球阻止來源檢索／UNKNOWN 盲重試 → LOCAL_SCOPE_PARK_VIOLATION。
- **源及效力處理**：原 `OriginalRequirementID+SourceSHA+byte-span+Parent/NEG/Exception+OriginalConsumer` 不能由同名 alias、原需求數目或 keyword 推論；下游原 Reader 缺件則 `SOURCE_SPAN_OR_SEMANTIC_OWNER_HOLD`，W0 隔離 SPECDraft/SourceRead 可繼續，受保護 effect 不促進。歷史 r2 完整保全與該 CH 的 SourceSHA/段落位置見非規範性附錄 `E16`。 明確歷史 Reader：[HISTORICAL_E16.CH-48](W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md#history-r2-ch-48)，file SHA `20add30f98e02a6dbd62f73c7b2adc809ff7a9e5349f96ce67cef5341392d6e3`。


### W0 草案增補｜本波主責實質施工接線
### W0 Stop–Resume 的最小完整記錄

每個受影條目使用 `{HOLD_ID, OriginalID, affected_scope, failed_gate, first_fail, original_reader, owner, required_raw, last_good_sha, dependent_WP, unaffected_siblings, resume_predicate, expiration}`，不得只列 `待處理`。Resume 先核 `Subject+Scope+SourceSHA+PolicyEpoch+HostID` 與原 Reader/WorkID 一致；UNKNOWN 效果先 WorldReadback/Journal Reconcile，禁止盲 retry。任何 scope/版本異動只使受影 cone 失效。

**常見局部 HOLD**：`H-SRC-01` 原 Canonical currentness；`H-U0U4-02` 未真正完成全部語義；`H-CELL-03` 192 provider polarity；`H-PIPD-04` 原 compiler/RepoContext；`H-ABI-05` HGK Registry/Policy；`H-LANE-06` Hermes ActualServed；`H-TOOLS-07` Host/License/Load；`H-OS-08` SID/ACL/SoD；`H-CASES-09` Runner/Checker；`H-W18-10` Fresh PID UAT；`H-H1-11` 原 50 CH/Reader 法位；`H-REL-12` Protected Checker/Publisher。每項在附錄保留原 Owner 和受影停止界線。

**POS**：`H-TOOLS-07` 只 PARK 某 Donor/Need，SOURCE_READ 正常；**NEG**：一個 OPS grant 缺件阻止 31 檔所有讀取，或 UNKNOWN 直接 replay world write → `LOCAL_SCOPE_PARK_VIOLATION`。W0 草案只建立恢復規劃，未觀測同 WorkID Native 讀回。



### r2 差額裁決與受影 HOLD（可繼續合法開發）

- `H-WP19-E26`：原 CI/SupplyChain Reader/Original Program Reader 確認 CandidateSHA、License/NOTICE/SBOM 原 Raw；只阻 E26/W4 WP14 的相應 Release-ready 宣告。
- `H-ORACLE-RAW96`：原 DOC07/Acceptance Case Registry/Runner/Protected Checker；96 個個案已 source-bound 規劃，但無 Host 真 Runner/Fixture bytes，**不報 Native PASS**。
- `H-WAVE-25`：原 Program Reader 核定 25 卡需求波／WP 主波及 consumer_verification_wave，其他 59 不受阻。
- `H-CAPABILITY-N`：原 Technology/License/Windows Host Reader 提供 exact binary digest、OS/ACL、Installed/Loaded/Invoked、NoFit，所涉 Needed Slot 限定受影 HOLD。
- `H-E16`：歷史 `E16` 原文封在 `W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md` 且具原附錄 SHA，〔R1-2026-11-06 更正〕`H-E16`：歷史 `E16` 原文仍封在 `W0_R2_E16_HISTORICAL_SOURCE_RETENTION.md` 且具原附錄 SHA，其歷史來源引用可讀，但不提升語義權威。原句「當期正文為本候選（generation 2）；r3 僅歷史父版本」更正為：當期正文為 generation 3／`2026-11-05_r4-final-c7a91e`（sha256 `0fed31f593fd132ba4f1f2d18df89a03e22e3fbdb6a75ded8bb479f86db884b4`）；generation 2 與 r3 僅歷史父版本。此為身份更正，不改 E16 歷史封存 SHA，亦不解除任何 HOLD。；其歷史來源引用已可讀，但不提升語義權威。
- `H-U0U4`：Original Owner currentness／逐義核簽缺件；僅阻受影正式 SourceFreeze/全量語義 closure，不阻 W0-A 合法 SOURCE_READ 與隔離草案。
- `H-NATIVE`：原 SBL PIPD Writer、Fabric Policy/HGK issuer/Hermes Host/Independent Checker/Publisher 尚未出真 Raw；後波有界解封，W0 只交 Proposal。

上述受影差額與原 AUDIT P0/P1/P2 對應：`W0_R2_AUDIT_REPAIR_LEDGER_AND_TESTS.md`。任何作者端本包 SHA、靜態 POS/NEG 不能升格成 Canonical、Host qualification、Release。

# CH-49｜逐章正式驗收標準、H1 防壓平測試與裁決

<a id="ch-49"></a>

## r4 當期 L3 合法正文｜`CH-49`：主波 W4（L2 r4 §6）
**W0 非主責，唯一主波是 W4。** `CH-49` 在本版保留獨立 H1 及原義不可折疊，只記原來源定位／跨波 Needed Input、Consumer、受影 NEG；本輪不改寫該 W4 專屬規格與 Native 權威。

**原產品主題／受影接收**：逐章正式驗收標準、H1 防壓平測試與裁決。主波 L3 收件 `W4_藍圖&skeleton → W4_草案 → W4_定案`；原 Consumer：Original Checker/Publisher (as affected)。

**POS**：W0 的索引可由 L1 r4 原章 SourceSHA/OriginalID 回查，且目的波唯一；**NEG**：重複生成該章的第二套規範／將 W4 原 Host/Effect 消費借 W0 作為已驗收；FirstFail=`CROSS_WAVE_SCOPE_CONFLICT`。

**Handoff**：`W0_SOURCE_INDEX → W4_L3_WAVE_CURATOR`；Original Reader/Owner/Protected Checker 不因本映射被移轉，未見原 ACK 則 `ORIGINAL_READER_ACK_UNOBSERVED`。
### 受影 r4 設計卡（DesignID；來源仍以 L1 r4 §7 卡為準）
| DesignID／原定位 | Primary W | 原 Producer/Consumer | POS | NEG／FirstFail |
|---|---|---|---|---|
| `FHS-DR-060` `L1-r4:L857` | W2 | Original Oracle/Protected Checker Reader | 原適用變體能抓回歸 | 測試空泛，全部 88% tests pass 仍漏 mutants；`DESIGN_OBLIGATION_MISSING`（若失卡） |


### W0 草案路由確認｜非本波主責
`CH-49` Primary=`W4`；沿用上方 r4 原位定位、OriginalID／NEG／Consumer，不移轉下游唯一 Writer。本波只交 SourceIndex/SpecDelta/CaseExpectation（適用才交）；POS 可反向追 L1 CH 與目的波；NEG 跨波先自建第二 Normative → `CROSS_WAVE_SCOPE_CONFLICT`。無原 Reader ACK 的受影效應維持 `ORIGINAL_READER_ACK_UNOBSERVED`。

---

## 實作後回寫（As-Built）— W0 r6

> **ArtifactID**：`FHS_PIPD-LS-PKG_W0_r6_ASBUILT@2026-11-07`  
> **Parent／Supersedes**：`FHS_PIPD-LS-PKG_W0_r5.md` @ `60b0c36e1bde6d0be1127461aa87a6bbb91dd69d6a31875d216ad8ddc88dbf0b`（475,265 bytes）  
> **本版 SHA256**：見同目錄 `*_REVISION_MANIFEST.json`（本檔不記錄自身 digest，避免自我指涉）  
> **產生時間**：2026-11-07T23:41:56+0800  
> **性質**：As-Built 追加章節。母本正文逐位元保留，未改寫、未摘要、未刪除任何 OriginalID／NEG／SourceSHA／Reader；本章只補本輪**實作與驗收差額**。  
> **ClaimCeiling**：`DOCUMENT_RECONCILIATION_COMPLETE_WITH_SCOPED_HOLDS`。本章不授權任何世界效果，也不代表原域 Reader ACK。

### A.1 狀態詞彙（本章只用這七個，避免「完成」一詞混用）

| 詞 | 含義 |
|---|---|
| `IMPLEMENTED` | 程式已在受權分支或已合併 main 落地，但未取得原域 ACK |
| `TESTED` | 有可重算的 Raw（含指令、exit code、digest），層級限於其所測對象 |
| `ORIGINAL_ACK` | 原域 Reader 對其 DonePredicate 出具收據（本輪**無任何**一項達到） |
| `NATIVE_WORLDRAW` | 真世界效果 Raw（本輪**無**） |
| `INDEPENDENT` | 不同技術 SID 的 Protected Checker 判決（本輪**無**） |
| `NOT_RUN` | 未執行 |
| `HOLD` | 前置未成立，已具名 ResumePredicate |

### A.2 本波受影 WP 對帳

| OriginalWP | 狀態 | 本輪實際發生什麼 | 尚未成立的部分 |
|---|---|---|---|
| `WP-FHS-00` | `TESTED` | source lock re-verified on this machine: control doc 5739a682 (70,517 B), W0 r5 60b0c36e (475,265 B), W1 r3 936a8bcb (868,138 B), W2 r5 647ee559 (430,128 B), CURRENT_READER_MAP d6a8fe98 (2,339 B) - all five match the control table | L0/L1/L2 are not present under the knowledge-base path used here, so those three are NOT_OBSERVED, not verified |
| `WP-FHS-01` | `NOT_RUN` | no new measurement this session; the nine-context profile and the independent twelve-risk sidecar remain author-side | no AuthorityConflictLedger / QuestionLedger decision was taken |
| `WP-FHS-15` | `NOT_RUN` | the three SPECs were not re-issued; nothing this session changes their source binding | TPM/PIPD intake not exercised |
| `WP-FHS-16` | `NOT_RUN` | Donor24/Method25 unchanged | no host-fit consumption happened |
| `WP-FHS-19` | `TESTED` | SBL main CI was already green (4 jobs) and PR #48/#49 were merged into it; the supply-chain layer is unchanged by this round | merging a PR is not a re-run of the supply-chain job; the layer stays APPLICABLE_DONE_AT_CI_LAYER |
| `WP-FHS-21` | `TESTED` | the declared GJ02 runner separates a defective checkout from a fixed one on identical oracle bytes (RED observed 0.03 forbidden / exit 1; GREEN observed 0.02 expect / exit 0; runner c4e447ba, oracle 33170cc1) | this is oracle discrimination, not a DEV effect, and the RED is not yet bound to a WorkID/ExactWriteSet |

### A.3 證據指標（可重算；路徑相對於本回合根目錄）

| EvidenceRef | sha256 | 證明了什麼 |
|---|---|---|
| `out/REPO_WIRING_R4.json` | `098020c935a963d3…` | the four merges (Fabric #32/#33, SBL #48, HG-KSEOS #15) with merge shas and reader runs on the merged code |
| `out/D24_SCOPED_PR.json` | `bdd082666253d1ad…` | Fabric #34 scope, before/after matrix, refusal codes and honest limits |
| `out/D24_INTEGRATION.json` | `0546c6d232fd700e…` | the two D-24 lanes and their merge |
| `out/GJ02_ORACLE_RED_GREEN.json` | `6bddca21543be99c…` | the same runner separating RED from GREEN with identical oracle bytes |
| `out/FIRSTFAIL_GJ02_CASE_SOURCE.json` | `9c8a6d3e58db4687…` | why DEV ECP cannot be produced (no clause-bound GJ02 case source) |
| `out/P3_MAINTENANCE_WINDOW.json` | `3799177b77d47ba5…` | deploy 0001-0007, additive migration, schema-99 refusal, rollback drill |
| `out/P3_POST_RESTART_ACCEPTANCE.json` | `63e61382fc1841fb…` | new gateway PID, loaded-tree proof, cross-restart data integrity |
| `out/T1_CHILDWORKITEMS.json` | `deb374ed94f9e59e…` | two child work items dispatched and collected with reader-level results |
| `out/R5_RULING_AND_WIRING.json` | `72344550853e3520…` | T2 reclassification, scheduler defects, SBL RepoContext POS/NEG |
| `out/R1_PRERUN_CHECKS.json` | `129933cf5a322580…` | R1 preflight 7/7, ceremony pin, signing-capability challenge |
| `out/OWNER_RULING_D24.json` | `0a780c56b6885a63…` | scope map for the D-24 lanes and the Host Load receipt acceptance |

### A.4 Scoped Holds（具名 ResumePredicate）

- **H-W0-1** L0/L1/L2 source lock — 原因：the three upper documents are not present under the knowledge-base path used in this session；恢復條件：supply L0/L1/L2 by path, then re-run the source lock check and compare with the control table

### A.5 本輪明確**不**主張的事

- 不主張任何 WP 達到 `ORIGINAL_ACK`：18 個原主責 WP 的原域 Reader 收據數為 **0**。
- 不主張 `W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE=true`；該查詢值仍為 `false`。
- 不主張 Fabric policy 生效：`BOUND` 只表示 artifact 被打開並重算，`FABRIC_ACTIVE_EPOCH@1` 尚無 Policy Owner 簽章，Host 亦未載入。
- 不主張 Issuer 恢復：registry 仍為 rev 13（`3254714b…`），rev 14 須由唯一 OWNER 在受保護終端執行。
- 不主張 T2：唯一觀測到的喚醒來自 maker 自造的到期項，依裁決不得作為 T2 證據。
- 不主張 DEV：本輪**未對任何世界寫入**；WP06 的 RED 是既存 checkout 上的正當缺陷，不是受權效果。

### A.6 母本保全聲明

本檔 = `FHS_PIPD-LS-PKG_W0_r5.md` 全文（475,265 bytes, sha256 `60b0c36e1bde6d0be1127461aa87a6bbb91dd69d6a31875d216ad8ddc88dbf0b`）＋本章。母本的所有章節、OriginalID、ParentNEG、SourceSHA、Writer/Reader、POS/NEG/SEC、FirstFail、Rollback、HOLD 與 Handoff 均逐字保留；本章不得被引用為對母本條款的修改。


## 實作後回寫（As-Built）— W0 r7

> **ArtifactID**：`FHS_PIPD-LS-PKG_W0_r7_ASBUILT@2026-11-08`
> **Parent／Supersedes**：`FHS_PIPD-LS-PKG_W0_r6.md` @ `69a08e7fae0404d7fc33842d66c28a21684a6d13caa6ac40ba7a269411db28d5`（481,212 bytes）
> **本版 SHA256**：見同目錄 `*_REVISION_MANIFEST.json`（本檔不記錄自身 digest，避免自我指涉）
> **產生時間**：2026-11-08T00:00:00+0800（章節內容以本輪 GSTACK 判決時間為準）
> **性質**：As-Built 追加章節。r6 母本正文逐位元保留（前 481,212 bytes 與 r6 完全相同，已由 appender 以位元比對證明），本章只補**實測**與其邊界。
> **ClaimCeiling**：`W0_SIX_WP_MEASURED_WITH_SCOPED_HOLDS`。本章不授權任何世界效果，也不代表原域 Reader ACK。

### B.0 本版相對 r6 的唯一差別

r6 的三個 WP（`WP-FHS-01/15/16`）停在 `NOT_RUN`，另外三個（`00/19/21`）的證據薄於各自的 DonePredicate。本版把**六個 WP 全部實際執行**，並把「執行到哪裡、在哪一層成立、什麼仍然沒有」逐項寫死。

**這一版改變的是量測，不是權限。** 六個 WP 全部屬於 `SOURCE_READ` 或 `LOCAL_DRAFT_WRITE`；本輪沒有動用任何 owner 金鑰、沒有開簽章窗、沒有 mint Permit、沒有碰 registry、沒有對任何 repo 的 `main` 寫入。owner 簽章需求是**量測值 0**，不是假設（`out/OWNER_SIGNING_DEMAND_W0.json`：live registry rev 13、31 列全 `INSTALLED` 且全列已簽、root `owner_signature` 在場；既然沒有新增列、沒有改列、沒有改 root，ceremony 沒有東西可簽）。

### B.1 逐 WP 對帳（唯一有效版本；覆蓋 r6 §A.2）

| OriginalWP | DonePredicate | r6 | **r7 實測** | 層級 |
|---|---|---|---|---|
| `WP-FHS-00` | SourceManifest + RepoContext readback | `TESTED`（31 冊本地 hash，L0/L1/L2 `NOT_OBSERVED`） | **`MEASURED`**：31/31 源檔 bytes+lines+sha256 全等；**L0/L1/L2/W0-skeleton/r6/r5-parent 六份上層文件 digest 全數 MATCH**；三庫 HEAD/branch/dirty 讀回成基線 | `SOURCE_READ` |
| `WP-FHS-01` | AuthorityConflictLedger + Oracle/ProfileBinding | `NOT_RUN` | **`MEASURED`**：31 檔 22,281,767 bytes 之 byte-exact 分割 **111,331 段**，31/31 檔「無縫、無重疊、全覆蓋」；U1 子義候選 6,524 條／6,248 個父句；U2 交叉表 84 個 DesignID（24 `INT` ＋ 60 `FHS-DR`）；U3 22 個 `W0_REQUIRED` 全有 CH 錨；`ProfileBinding` **19/19 對到真實 schema 檔**；`AuthorityConflictLedger` 17 筆同名不同 digest | `SOURCE_READ` |
| `WP-FHS-15` | 原三 SPECDraft + 來源 readback + FUO 十欄 | `NOT_RUN`（Architecture 470 chars、Program 385 chars，實為 stub） | **`MEASURED`**：三份**實質相異** SPEC（Product 9,116 B／Architecture 9,267 B／Program 9,691 B），每份最低欄位齊備、FUO 十欄全填、15 條驗收（6 POS／9 NEG）；**52/52** span 回切等於引文；三份兩兩相似度句級 shingle 上限 **0.0755**、字元 5-gram 上限 **0.2134**（門檻 0.85），consumer 與 NEG 集合互斥；18 條 Stage 契約 | `LOCAL_DRAFT_WRITE` |
| `WP-FHS-16` | 24 slot／25 method 壓製候選 | `NOT_RUN`（目錄為空） | **`MEASURED`**：Donor **24/24**、Method **25/25**（合計 49，零 padding、零丟棄）；`ADOPT_CANDIDATE` 8、`DEFER` 21、`NOFIT` 1、`HOLD` **19**；13/13 驗證檢查 | `LOCAL_DRAFT_WRITE` |
| `WP-FHS-19` | CI/License/NOTICE/SBOM 掃描 Raw | `TESTED`（理由僅為「main CI 本來就綠、兩個 PR 已併」） | **`MEASURED`**：三庫逐庫授權／NOTICE／SBOM／依賴／workflow 盤點，並以 token 回讀 live CI。**Fabric：LICENSE/NOTICE/SBOM 全缺席**、1 個 workflow（`fhs-nav-static`，無 supply-chain job）；**SBL：MIT＋NOTICE＋CycloneDX 1.5（8 components、未簽章）**、`supply-chain` job 在 run `42361088797` 綠；**HG-KSEOS：LICENSE/NOTICE 全缺席、SBOM 非 CycloneDX、`CI_SERVICE_ABSENT`** | `SOURCE_READ` |
| `WP-FHS-21` | 96 Cell／H4／SEAM 原 Oracle 計畫 | `TESTED`（只有一個 runner 分辨 RED/GREEN） | **`MEASURED`**：AC15 **15/15**、Oracle96 **96/96**（12 TestClass × 8 OracleType 完整交叉乘積，`__CORRUPT__001..096` 連續）、H4 **12**、SEAM **11**，合計 134 列，四個分母 delta 全為 0；檢查器 **155/155**；負控注入 5 類缺陷 **5/5 被抓**；單列鑑別示範 POS 通過／NEG 失敗，並含一個 laundering probe | `SOURCE_READ` |

### B.2 `H-W0-1` 結案：不是「文件不存在」，是「上一輪的路徑沒找到」

r6 把 L0/L1/L2 記為 `NOT_OBSERVED`，理由是「不在本 session 使用的知識庫路徑下」。本輪在同一台機器上按 frontmatter 宣告的 digest 逐一解析：

| 文件 | 解析路徑 | 宣告 digest | 實測 |
|---|---|---|---|
| L0 | `藍圖/FHS_總藍圖_r4.md` | `7befcac3…` | **MATCH** |
| L1 | `藍圖/FHS_PIPD-LS-PKG_藍圖_r4.md` | `cbdd75fd…` | **MATCH** |
| L2 | `藍圖/FHS_PIPD-LS-PKG_全波次藍圖_r4.md` | `bb970a43…` | **MATCH** |
| W0 skeleton | `藍圖&skeleton/…_W0_…_r4.md` | `4f8d67fd…` | **MATCH** |
| W0 r6 | `writeback/W0/FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7f…` | **MATCH** |
| W0 r5 parent | `evidence/E_docs/FHS_PIPD-LS-PKG_W0_r5.md` | `60b0c36e…` | **MATCH** |

**結案方式**：`H-W0-1` 由 `DOC_ABSENT` 改判為 `DOC_PRESENT_DIGEST_MATCH`。這仍然**不是** `SourceFreeze`，也**不是** `OWNER_CURRENTNESS_CONFIRMED`：digest 相符只證明「我讀到的位元就是被綁定的位元」，不證明「原 Owner 說這是有效版本」。此區別寫在 `WP01/AUTHORITY_CONFLICT_LEDGER.json` 的 `SOURCE_CURRENTNESS_UNOWNED`（31/31）。

### B.3 本輪新發現的真實缺陷（不是進度落後，是文件與流程的洞）

| # | 缺陷 | 實測 | 影響 | 誰能修 |
|---|---|---|---|---|
| `D-W0-R7-01` | **17 組同名原稿在知識庫內有多個不同 digest** | 掃 282 個候選副本；`00_INDEX_AND_DECISION.md` 有 5 個不同 digest，僅 1 個等於 source digest（其餘為 `HANDOFF-PATCH-v1`／`STATIC-REPAIR-v1`／`INPUT_R2_VERBATIM`／`DELIVERY_R2` 各線） | 任何以「檔名」而非 digest 取源的下游，都可能讀到非本輪綁定的那一份 | 原 Domain Owner 指名權威副本 |
| `D-W0-R7-02` | **W0 CH-11 只宣告「18 Stage」這個數字，列舉 0 列** | `grep` 在 W0 r6 全檔對 18 stage 的列舉命中 0；18 條契約實際只存在於來源 `02_PIPD_LIFECYCLE_AND_TPM(4).md` 第 38–55 行 | 只讀 W0 章節的實作者會做不出 stage 契約 | W0 章節 Curator／原 TPM Reader |
| `D-W0-R7-03` | **W0 r6 完全未列舉 H4 與 SEAM** | 對 `H4-`／`SEAM-` 的列舉命中數為 0；12＋11 列僅由 `07_ACCEPTANCE_CHALLENGE(4).md` 的 `R2-07-H4-SEAM`（byte 201,749..210,204）支撐 | WP-21 的分母在控制稿內不可見 | W0 章節 Curator／原 Oracle Owner |
| `D-W0-R7-04` | **CH-24／CH-25 對 49 個 slot 只列舉 7 個具名 ID** | CH-24 只給 `SLOT-OS-01`、`SLOT-GT-01`、`SLOT-GS-01` 與三個區間；CH-25 只給 `METHOD-01/06/10/23`；其餘靠 `WP16_TRANSLATION49.json` 指標 | 逐章實作者會以為只有 3＋4 個 slot | W0 章節 Curator |
| `D-W0-R7-05` | **49 個 slot 中 41 個沒有任何授權陳述** | 只有 8 個（`mattpocock/skills` 系）在 DOC-04 研究表有 `MIT`，且該 MIT 屬 `UNVERIFIED_RESEARCH_OBSERVATION`、未讀上游 LICENSE digest | 任何以原意圖（`SELECTIVE_NATIVE_REUSE` 等）直接 adopt 的做法都是無授權採用 | 原 TechnologyAdmission Owner |
| `D-W0-R7-06` | **Fabric 與 HG-KSEOS 根層沒有 LICENSE／NOTICE** | Fabric：root 無授權檔、GitHub license API 回 `null`，僅 5 個 vendored 深層授權；HG-KSEOS：全樹無授權檔 | 對外散佈前授權未定；Fabric `INTEGRATION/MANIFEST.json` 的 `pending` 本來就列著 `licence choice (owner)` | OWNER |
| `D-W0-R7-07` | **HG-KSEOS 沒有 CI** | workflow 檔 0、workflow run `total_count=0`、check-run `total_count=0` | 「HG-KSEOS CI 綠」不是可成立的句子；WP-19 在該庫只能記 `CI_SERVICE_ABSENT` | OWNER（決定是否建 CI） |
| `D-W0-R7-08` | **Fabric 唯一的 CI job 不掃供應鏈** | `fhs-nav-static` 只跑 `validate_entry.py` 與 unittest | Fabric 的綠燈與 license／SBOM／dependency 無關，不可引用為供應鏈證據 | Fabric 維護者 |
| `D-W0-R7-09` | **`WP16` 車道的 `head` 預覽以 bytes 截斷** | 1,045 個抽樣預覽中 91 個尾端切成 U+FFFD（多位元組中文字被切半） | 純顯示瑕疵：偏移與覆蓋完全正確（31/31 檔位元全覆蓋），但預覽字串不可直接引用 | 本輪已記錄，未改寫車道產物 |

### B.4 GSTACK 不變量閘（本輪新增，且已證明會咬）

`tools/gstack_w0.py` 不信任何車道的自報判決：它自己重算每個 artifact 的 digest、自己把每個 `source_ref` 從原始 bytes 重新切片、自己把每個宣告的計數與表格實際列數對帳。

| 判決 | 事實 |
|---|---|
| 空回合目錄 | `exit 2`（`FAIL_CLOSED_PRECONDITION`）— 在還有東西可檢查之前就能失敗，這是非空轉的第一個證明 |
| 真實樹 | **15/15 PASS，`exit 0`**：116 個宣告 artifact 全數重雜湊、350 個 source ref 全數重切、0 個問題 |
| 注入違規 | `exit 1`，四族檢查同時咬住：`G2` digest 漂移、`G5b` 裸聲稱、`G6` span 不符、`G7` 計數謊報 |
| 還原後 | 三個被改檔的 digest 恢復為原值（`ae17b9fa…`／`cf21cd62…`／`a823b6bc…`），閘回到 15/15 PASS |

另有 `G8`：以 WP-00 的基線比對三庫 HEAD 與 dirty 數，本輪 **0 drift**——「沒有動 repo」因此是可比較的事實，不是聲明。

### B.5 本輪明確**不**主張的事（逐項對照 r6 §A.5）

- 不主張任何 WP 達到 `ORIGINAL_ACK`：六個 WP 的原域 Reader 收據數仍為 **0**。maker 端的量測不是 domain acceptance。
- 不主張 `W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE=true`；該查詢值仍為 `false`。
- 不主張 Fabric policy 生效：`FABRIC_ACTIVE_EPOCH@1` 仍無 Policy Owner 簽章。
- 不主張 Issuer 恢復：registry 仍為 rev 13（`3254714b…`）；rev 14 須由唯一 OWNER 在受保護終端執行。
- 不主張 T2、不主張 DEV、不主張任何世界效果：本輪對世界寫入為 **0**。
- 不主張三份 SPEC 是原 PIPD schema `$id`，也不主張 Owner SourceFreeze。
- 不主張 49 個 slot 的任何一個已被 TechnologyAdmission 核可；8 個 `ADOPT_CANDIDATE` 只是「授權已陳述、可供下游審」的候選。
- 不主張 134 列 oracle 已被保護檢查者判定；它們是**計畫**，每列狀態 `NOT_EXECUTED / RUNNER_UNBOUND`。

### B.6 母本保全聲明

本檔 = `FHS_PIPD-LS-PKG_W0_r6.md` 全文（481,212 bytes, sha256 `69a08e7fae0404d7fc33842d66c28a21684a6d13caa6ac40ba7a269411db28d5`）＋本章。母本的所有章節、OriginalID、ParentNEG、SourceSHA、Writer/Reader、POS/NEG/SEC、FirstFail、Rollback、HOLD 與 Handoff 均逐字保留；本章不得被引用為對母本條款的修改。

---

## 驗收後回寫（Verification Round）— W0 r7 獨立重驗與作者端修補

> **ArtifactID**：`FHS_PIPD-LS-PKG_W0_r8_VERIFY@2026-11-08`
> **Parent／Supersedes**：`FHS_PIPD-LS-PKG_W0_r7.md` @ `264787b065fbca6a8e728054fd3abdb6133883bbeb87710ddf5e880071f61845`（492,290 bytes）
> **本版 SHA256**：見同目錄 `W0_REVISION_MANIFEST.json`（本檔不記錄自身 digest，避免自我指涉）
> **產生時間**：2026-11-08T03:20:00+0800
> **性質**：追加章節。父本 492,290 bytes 逐位元保留為本檔前綴（可機械驗證），本章只補「對 r6 草案本地實作的獨立重驗結果、措辭級錯誤更正、列舉修補與一個新增閘檢項」。
> **ClaimCeiling**：`DOCUMENT_RECONCILIATION_COMPLETE_WITH_SCOPED_HOLDS`。本章不授權任何世界效果，不代表任何原域 Reader ACK。

### C.0 這一輪的結論（一句）

把 `FHS_PIPD-LS-PKG_W0_r6` 當草案、對其本地實作做六個 W0 WP 的**獨立重驗**：**六個 WP 的頭條數字全部重現**，但過程中量到**七個措辭級或中繼資料級缺陷**（其中一個讓 15 項閘全綠卻仍出貨），並修好一個真實的閘缺口。**原域 Reader 收據仍是 0**；本輪沒有改變這件事，也不打算用任何措辭讓它看起來改變了。

| 項目 | 本輪值 |
|---|---|
| 六個 W0 WP 的頭條宣稱 | 6 / 6 重現（其中 2 項屬「規則相依」，見 C.3） |
| 重驗後仍然成立的 `ORIGINAL_ACK` | **0** |
| 新量到的缺陷 | 7（V-01…V-07；皆為文件或中繼資料層，無一是世界效果） |
| 新增閘檢項 | 1（`G10-DOC-PARENT-CLAIM`），在 r7 上紅、在 r8 上綠 |
| 本輪對三庫的寫入 | 0（`G8` 以 WP-00 基線比對，0 drift） |
| Owner 簽章需求 | 0（見 `OWNER_SIGNING_DEMAND_W0R7.json`）；具名 OWNER 待辦合併為 1 份 5 項 |

### C.1 怎麼驗的：三方獨立，互不採信

這一輪刻意不採信任何一方的自報判決。三條證據線各自獨立產生，最後只有**互相吻合的部分**才寫進本章：

| 線 | 角色 | 它能主張什麼 | 它不能主張什麼 |
|---|---|---|---|
| L1 母代理 | 以自寫程式直接從 31 個原始 bytes 重算 31 檔 digest、U0 覆蓋、84 卡與 22 個 `W0_REQUIRED`、96 Oracle 的 12×8 完備性 | `AUTHOR_SIDE_MEASURED` | 不是原域 Reader，不能給 ACK |
| L2 四條子代理（SWARM，各寫自己的目錄、無憑證） | 獨立重導 WP00/01、WP15/16、WP19/21，並抽出列舉缺口所需的來源座標 | `AUTHOR_SIDE_INDEPENDENT_REDERIVATION` | 不能 push、不能 merge、不能自簽獨立判決 |
| L3 閘（`GSTACK`） | 不信任何車道自報：自己重算每個 artifact digest、自己從原始 bytes 重切每個 `source_ref`、自己對帳計數 | `GATE_VERDICT` | 綠燈不是驗收 |

**反偽造的做法**（本輪實際執行）：

- 子代理的 `quote` 不信，母代理隨機抽 12 條自行把 `bytes[start:end]` 切出來比對：**12/12 逐位元相同**。
- 子代理產的 18/12/11/24/25 五組列舉，母代理再抽 10 條比對來源檔 sha256 與切片長度：**10/10 相符**。
- 子代理報「重現」的每一條，母代理都另外用一條**不同寫法**再算一次（例：`AC-C39-*` 用正則取 id 集合與 12×8 笛卡兒積雙向比對）。
- 閘的負控不是「宣告它會咬」，而是**真的注入三種違規**並要求它紅在指定的三層（見 C.5）。

### C.2 六個 WP 的逐項對帳

| WP | r6 頭條宣稱 | 本輪獨立量測 | 判決 |
|---|---|---|---|
| `WP-FHS-00` | 31/31 源檔 bytes+lines+sha256；上層 6 份 digest；三庫 HEAD 基線 | 31/31 bytes 與 sha256 相符、0 缺檔、0 多檔；行數以 `count("\n")` 為 111,331（lock 自身用另一慣例得 111,362，見 V-07）；6/6 上層 MATCH；三庫 0 drift | **REPRODUCED**（行數慣例見 V-07） |
| `WP-FHS-01` | 111,331 段／22,281,767 bytes 全覆蓋；84 DesignID；22 `W0_REQUIRED`；19 schema family；17 筆同名不同 digest | bytes 22,281,767 完全一致且 31/31 檔位元全覆蓋；84（24 INT＋60 DR）；22；19；**同名碰撞在 31 源集內為 0** | **REPRODUCED**（U0 段數與「17 筆」屬規則／措辭相依，見 V-03／V-04） |
| `WP-FHS-15` | 3 份實質相異 SPEC；52/52 span；15 條 ACC（6 POS／9 NEG）；18 Stage | 3 份相異；52/52 EXACT；15（6/9）；18 | **REPRODUCED**（相似度數值引用錯誤，見 V-02） |
| `WP-FHS-16` | 24 donor／25 method；8 ADOPT／21 DEFER／1 NOFIT／19 HOLD；8/49 具名授權 | 24/25 無填充無重複；8/21/1/19 合計 49；8/49；49/49 來源座標 EXACT | **REPRODUCED** |
| `WP-FHS-19` | 三庫授權／NOTICE／SBOM／依賴／CI 盤點，含 3 處缺席 | SBL：LICENSE＋NOTICE＋`ci.yml`（供應鏈 job 綠）；Fabric：根層無授權檔、**深度 5 個**授權／NOTICE（2 個 vendored MIT）、唯一 workflow 不掃供應鏈；HG-KSEOS：根層無、**完全無 CI** | **REPRODUCED**（「無授權」僅在根層成立，見 V-06） |
| `WP-FHS-21` | AC15 15／Oracle96 96／H4 12／SEAM 11；檢查器 155/155；負控 5/5 | 15（`AC-E01`…`AC-E15`）；96（12×8 完備、0 缺格、0 重複）；12；11；檢查器重跑 155/155；負控重跑 5/5 | **REPRODUCED** |

**母代理另行獨立確認的四個數字**（不經任何車道）：`AC-C39-*` 去重 96、類別 12、型別 8；L1 卡 24 `INT` ＋ 60 `FHS-DR`；W0 84 列表 `W0_REQUIRED` 22／`W1-W4_HANDOFF` 62；r6 回合自帶 `SHA256SUMS` 162 條全部通過 `sha256sum -c`。

### C.3 本輪新量到的七個缺陷（全部是文件或中繼資料層）

> 這一節是本章的主要產出。七個都不是「進度落後」，而是**讀者會照著做卻會得到不同答案**的地方。

| ID | 缺陷 | 量測（可重算） | 處置 |
|---|---|---|---|
| `V-01` | **同一份 r6 文件存在兩個位元不同、長度相同的副本**；r7 宣告的父本 digest 指向回合內的副本，知識庫路徑上服務的是另一份 | 兩份皆 481,212 bytes；僅 4 個 byte 不同（附錄 `產生時間` 23:10:08 vs 23:41:56）；`9f9eb261…`（KB 回寫路徑）vs `69a08e7f…`（`FHS_W0W2_R4_20261107/writeback/W0`） | 本章 C.7 同時列舉兩份副本與各自 digest；**哪一份是 canonical 由原 Owner 決定**（`OWNER-W0R7-01`／`AUTHORITY-17-COLLISIONS`） |
| `V-02` | 「相似度上限 0.0755」既不是上限，也**未能重現** | 同一份 `WP15/REPORT.json` 的 `distinctness.pairs[].max` 欄為 0.2134／0.2102／0.2113，0.0755 只出現在 `sentence_shingle` 子欄；本輪以 6 種方法族重算，primary（token-3gram）上限 0.1208、全方法族上限 0.2063，而 0.0755 在任一族都未重現（本輪 sentence-2gram 為 0.0497／0.0370／0.0355） | 本章以分方法並列取代單一數字；判決方向不變（全部遠低於 0.85 門檻），但「0.0755」不得再被引用為上限 |
| `V-03` | 「17 筆同名不同 digest」的**作用域寫錯** | 31 源集內：31 個相異 basename、**0 組同名碰撞**。真正成立的是：**17 個源檔在知識庫他處存在同名副本且 digest 不同**（例：`00_INDEX_AND_DECISION.md` 13 份外部副本，12 份不同） | 本章改寫為「17 個源檔存在 digest 相異的同名外部副本」；權威副本選擇仍屬原 Owner |
| `V-04` | 「111,331 段」= **行數**，不是語意區塊數 | 同一 22,281,767 bytes：per-line 規則 111,331 段；block 規則（heading／表格／code fence／空行／text）**24,003 段**。兩者都完整覆蓋、無縫無疊 | 標為 `REPRODUCED_WITH_DEFINITION_DRIFT`；本章明示「111,331 是 line-byte 證明的行數，不是 U0 語意分割數」 |
| `V-05` | **發佈鏡像的 11 筆 digest 不對應它所指的 bytes** | SBL 端 `MANIFEST.json` 82 筆中 71 筆在其 payload 內完全對帳；**11 筆屬 Fabric 鏡像**，其宣告 digest 與鏡像實際 bytes 不同（例：r7 文件宣告 492,208 bytes／LF 正規化 digest，鏡像實為 492,290 bytes 原樣 `264787b0…`） | 本章附 `CORRECTIONS.json` 逐筆列出「宣告值 vs 實測值」；r7 已發佈的 manifest **不改寫**（它是已量測的歷史），更正以疊加方式給出 |
| `V-07` | WP00 的 source lock **自己量到 31/31 檔行數不符，判決卻寫 MATCH** | lock 的 `observed.lines` 採 `text.split("\n")` 慣例，每檔多算 1 行（31 檔合計 111,362）；宣告值與 `wc -l`／`count("\n")` 皆為 **111,331**。`lines_match` 31 筆全 false，`verdict` 仍為 `MATCH`（只看 bytes＋sha） | 本章把「31/31 相符」明確限定為 **bytes 與 sha256**；行數以 `count("\n")` 為準並記為 111,331；lock 本身不改寫（已量測歷史），差異記於 `CORRECTIONS.json` |
| `V-06` | 「Fabric／HG-KSEOS 無授權檔」只在**根層**成立 | Fabric 根層 0，但深度 5 個授權／NOTICE（2 個 vendored MIT）；HG-KSEOS 根層 0 且 depth 亦為 0；SBL 根層 LICENSE＋NOTICE | 本章把宣稱改為「根層無授權檔」，並保留深度實測；是否補授權仍是 OWNER 決定 |

**本輪自身的錯誤（公開）**：`E-V01`—我最初只用知識庫單一路徑探測 r7 的父本 digest，得到「無法解析」，並已準備把它寫成 `V-01 UNRESOLVED`。在寫入前搜尋同名副本，才發現 digest 其實指向回合內另一份 r6；正確分類是 `COPY_AMBIGUITY`，不是「digest 不存在」。**教訓**：一個 digest 不解析，先問「是不是還有同名副本」，再問「是不是打錯」。這條錯誤與更正同時留在 `out/SELF_ERRORS.md`。

### C.4 列舉修補：`D-02`／`D-03`／`D-04`

> 這三項是 r6/r7 的**文件缺口**（只宣告數字，不列舉），不是量測缺口。以下片段全部由原始 bytes 切片產生，`座標` 為來源檔絕對 byte offset；母代理已隨機抽驗 12/12 逐位元相同。

### D-02｜CH-11：TPM 18 Stage 具名列舉

> **來源**：`02_PIPD_LIFECYCLE_AND_TPM(4).md`；sha256 `c336d3d9d702834e84bc2e45037e21e6ac56fb99c7abcb3adea372d901824ea2`
> **區段**：§2 `STATIC-v1 三角色 18 Stage：按插件原 Clause Reader 的實際契約` 表（L36–L55；byte 4371–9518）。
> 同檔 `R2-02-STAGE：K0–K3 與原18-stage投影`（L451–L470）為同 18 列之鏡像投影，id 與順序逐列相同（已比對）。
> **插入位置**：`CH-11` 主體 `**W0 主責：三 SPEC 與 18 Stage。**` 段之後、`### 受影 r4 設計卡` 之前。
> **18 列＝PM 6＋SE 6＋TPgM 6**；此為 Stage 契約 draft，不是 StateEnum，也不代表該階段已執行。

| # | Stage | 名稱（操作，逐字） | 用途（一子句：輸出／Consumer） | Guard／FirstFail／退出 | 座標 |
|--:|---|---|---|---|---|
| 1 | `PM:T0` | segregate facts from user guesses; detect unanswered JTBD | ProductKnownState@1(goal_sha,missing_questions) / ProductOwner/PIPD Reader | GoalCard+known_answer_refs; source_sha present；KNOWN_ANSWER_REASK；ASK_NEW_ONLY；`T1` | 02:L38｜4371–4656 |
| 2 | `PM:T1` | rank questions by user information gain | QuestionPriority@1(qid,impact,source_ref) / ProductOwner/PIPD Reader | Persona+PainLedger+JTBD; source_sha present；JTBD_UNBOUND；FUO_PATH_BOUND；`T2` | 02:L39｜4657–4909 |
| 3 | `PM:T2` | define observable CLI/add,list,delete or brownfield user result | ProductSuccess@1(FUO,exit_code,negative_cases) / ProductOwner/PIPD Reader | FUO+UserOutcome+variants; source_sha present；FUO_UNTESTABLE；USER_VALUE_MEASURABLE；`T3` | 02:L40｜4910–5202 |
| 4 | `PM:T3` | compile ProductSPEC draft and acceptance cues | ProductSPECDraft@1(journey_id,kind,acceptance_sha) / ProductOwner/PIPD Reader | ProductSuccess+PrimaryKind; source_sha present；KIND_ID_DRIFT；OWNER_REVIEW_REQUESTED；`T4` | 02:L41｜5203–5484 |
| 5 | `PM:T4` | issue user-facing POS/NEG proposal, not Native verdict | ProductAcceptanceProposal@1(pos,neg,raw_expect) / ProductOwner/PIPD Reader | ProductSPECDraft+ACC_NEG; source_sha present；ACC_NOT_BOUND；PIPD_ACC_REF_AVAILABLE；`T5` | 02:L42｜5485–5768 |
| 6 | `PM:T5` | compare observable use vs claimed outcome; create repair request | ProductReviewRequest@1(gap,affected_journeys) / ProductOwner/PIPD Reader | FUO_raw_refs+feedback; source_sha present；FUO_RAW_MISSING；REVIEW_WITH_RAW_OR_HOLD；`T5 final review or affected T3/T4 rework` | 02:L43｜5769–6095 |
| 7 | `SE:T0` | enumerate source/destination trust seams | SystemReadset@1(owners,sha,scope) / ArchitectureOwner/HostReader | RepoBoundaries+SourceIndex; source_sha present；SYSTEM_SOURCE_GAP；SOURCE_BOUND；`T1` | 02:L44｜6096–6353 |
| 8 | `SE:T1` | assign every seam to exactly one writer | OwnershipSeamMap@1(writer,reader,forbidden_effect) / ArchitectureOwner/HostReader | SystemReadset+ADRRefs; source_sha present；SEAM_OWNER_CONFLICT；ONE_WRITER_PER_SEAM；`T2` | 02:L45｜6354–6626 |
| 9 | `SE:T2` | trade off typed ABI and provider-off reliability | ADRSet@1(option,tradeoff,security_guard) / ArchitectureOwner/HostReader | RiskInventory+HostCaps; source_sha present；ARCHITECTURE_RISK_OPEN；ADR_OWNER_REVIEW；`T3` | 02:L46｜6627–6900 |
| 10 | `SE:T3` | bind schemas and compatibility version | ArchitectureSPEC@1(abi,compat,host_matrix) / ArchitectureOwner/HostReader | ADRSet+C4+ComponentCards; source_sha present；ABI_SCHEMA_MISMATCH；SCHEMA_READER_BOUND；`T4` | 02:L47｜6901–7171 |
| 11 | `SE:T4` | test scope/token/provider-off/thin adapter semantics | ArchitectureNEGRequest@1(neg,oracle_source) / ArchitectureOwner/HostReader | ArchitectureSPEC+BoundaryNEG; source_sha present；PERMISSION_NEG_MISSING；NEG_PROPOSAL_READY；`T5` | 02:L48｜7172–7466 |
| 12 | `SE:T5` | re-evaluate actual host ABI and raw results | ArchitectureReview@1(findings,repair_cone) / ArchitectureOwner/HostReader | NativeRawRefs+IntegrationRisks; source_sha present；HOST_RAW_MISSING；RAW_OR_HOLD；`T5 final review or affected T3/T4 rework` | 02:L49｜7467–7780 |
| 13 | `TPgM:T0` | identify budget milestones without claiming approval | ProgramIntent@1(milestone,owner,risk) / ProgramOwner/NativeRouter | OwnerRoster+CostTime; source_sha present；MILESTONE_OWNER_MISSING；OWNER_ROSTER_COMPLETE；`T1` | 02:L50｜7781–8056 |
| 14 | `TPgM:T1` | record sequencing constraints and blocking decisions | SchedulingAssumptions@1(edges,confidence) / ProgramOwner/NativeRouter | UnknownDependencies+ResourceCaps; source_sha present；UNBOUNDED_WORK；DEPENDENCY_DISCLOSED；`T2` | 02:L51｜8057–8350 |
| 15 | `TPgM:T2` | toposort bounded DAG and cycle check | ProgramDAG@1(topo,locks,no_fit) / ProgramOwner/NativeRouter | OwnerGates+DependencyEdges; source_sha present；DAG_CYCLE；ACYCLIC_AND_SCOPED；`T3` | 02:L52｜8351–8599 |
| 16 | `TPgM:T3` | package work with traceable scope and approver | ProgramSPEC@1(wp,effort,owner,stop) / ProgramOwner/NativeRouter | ProgramDAG+ProductSPEC+ArchitectureSPEC; source_sha present；WP_SCOPE_UNKNOWN；WORK_PACKAGE_OWNER_REVIEW；`T4` | 02:L53｜8600–8903 |
| 17 | `TPgM:T4` | route to correct Native ECP/Oracle Owner | HandoffReferral@1(expected_grants,oracle_conflict) / ProgramOwner/NativeRouter | PI_PD_refs+VerifierReferral; source_sha present；CR_ORACLE_001；NATIVE_REF_NOT_SYNTHESIZED；`T5` | 02:L54｜8904–9189 |
| 18 | `TPgM:T5` | review schedule with evidence status; refreeze affected only | ProgramReview@1(blocked_waves,replan_cone) / ProgramOwner/NativeRouter | MilestoneRaw+IssueLedger; source_sha present；STALE_MILESTONE_EVIDENCE；REVIEW_OR_HOLD；`T5 final review or affected T3/T4 rework` | 02:L55｜9190–9518 |

**回切結果**：18/18 列 slice 與來源 bytes 逐位元相同；`PM:T0…TPgM:T5` 無缺號、無重複。

### D-03｜H4（12）與 SEAM（11）具名列舉

> **來源**：`07_ACCEPTANCE_CHALLENGE(4).md`；sha256 `81a8c2f1cc4629f59829f11f87aebd14cd57f7c4dd0970d672880e90e2899741`
> **區段**：`## R2-07-H4-SEAM：12 H4與11 SEAM保持原Oracle`（L1336–L1362；byte 201871–210202）。
> **插入位置**：`CH-42` 之後新增 `CH-42A`（或併入 CH-42 的 Oracle 族說明）：H4 為 12 列驗收 Case，SEAM 為 11 列故障面；兩者與 96 Oracle 是不同的分母，不可互抵。
> **註**：下表 `POS／NEG／退出` 欄省略了每列完全相同的尾句（H4：`；FirstFail 受影 H4 停止，原 Checker Owner 證明退出／重測，不影響無關案。`；SEAM：`；FirstFail 停受影 Receiver；原 Owner 更正/驗原 Raw 後才可重入。`）。

#### D-03a H4（宣告 12；實測 12）

| ID | 標題 | 斷言什麼（原業務契約，逐字） | POS／NEG／退出（尾句省略） | 座標 |
|---|---|---|---|---|
| `H4-01` | Fresh Context | 原 checker_principal, loaded_history_ids, write_cap → fresh-context-proof；Consumer/Owner Checker Registry；換真獨立 context／re-run；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS checker≠maker、無重疊私有歷史、無受審檔寫權；NEG 看過 Maker private notes 或可寫候選 → CHECKER_CONTEXT_TAINTED | 07:L1340｜201871–202363 |
| `H4-02` | Frozen Binding | 原 subject sha, source manifest, raw refs → exact-hash-binding；Consumer/Owner Source Owner；重凍結後重測；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 每個 SourceLocator 可讀且 sha 與 frozen 一致；NEG source[3] 漂移 → FROZEN_BINDING_MISMATCH | 07:L1341｜202364–202797 |
| `H4-03` | A∪B∪C | 原 stable A/B/C IDs, waiver → attack union ledger；Consumer/Owner Challenge Owner；補原攻擊而非改分母；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS A={x,y}, B={y,z}, C={w} 得唯一 4 件且都有 disposition；NEG count=3 或藏未測 → ATTACK_DENOMINATOR_UNDERCOUNT | 07:L1342｜202798–203243 |
| `H4-04` | Anti-Correlation | 原 high-risk flags, challenge origin/principal → independence matrix；Consumer/Owner Protected Checker；獨立再生案例；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 高風險有至少一條非 Maker 派生的攻擊與新 context；NEG tests 全取同一 Maker Memo → CORRELATED_BLIND_SPOT | 07:L1343｜203244–203712 |
| `H4-05` | 11 Seams | 原 seam_case_ids[11]，tamper fields → SeamTestLedger；Consumer/Owner Security/Native Owners；逐 Seam 真測；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 11 個不同故障面各一正一負且對應不同 FirstFail；NEG 11 個僅改標題、未實測 → SEAM_UNTESTED | 07:L1344｜203713–204151 |
| `H4-06` | Next-Wave | 原 current+next-wave consumer, policy → under-enforcement check；Consumer/Owner Policy Owner；保持拒收；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 當前沒消費但 next-wave 仍必拒過期權；NEG no current reader 竟豁免 → NEXT_WAVE_UNDERENFORCED | 07:L1345｜204152–204581 |
| `H4-07` | Regression Retention | 原 previous F IDs, new SHA, change cone → regression matrix；Consumer/Owner Regression Owner；舊判決保留；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 過往 F17 仍在新 SHA 重測集，除非受權變更；NEG 靜默刪 prior rejection → REGRESSION_SILENT_DROP | 07:L1346｜204582–205030 |
| `H4-08` | Two-Pass Blind | 原 PassA seal time/SHA, PassB open time → order proof；Consumer/Owner Checker Owner；新 Session 重新盲審；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS A immutable frozen 後才開 B，能重算 timestamp；NEG B 先開或封印被改 → BLIND_REVIEW_INVALID | 07:L1347｜205031–205466 |
| `H4-09` | Dual Axis | 原 candidate truth, reviewer process qualified → two-axis result；Consumer/Owner AO；分軸判斷不可平均；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS candidate=FAIL、process=PASS 時全案仍 HOLD；NEG reviewer 合格便宣稱 candidate PASS → DUAL_AXIS_COLLAPSE | 07:L1348｜205467–205906 |
| `H4-10` | Native Receipt | 原 issuer/subject/raw digest/sig → trusted binding；Consumer/Owner HGK Native Owner；驗真 key/ACL；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS sig+scope+raw 同 Subject 有效；NEG S2 收據重播給 S1 → NATIVE_RECEIPT_SUBJECT_MISMATCH | 07:L1349｜205907–206321 |
| `H4-11` | RepairCone | 原 first failing invariant, DAG, legal writeset → minimal repair cone；Consumer/Owner Maker/Repair Owner；用受限 L2 ECP；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 只修依賴受影最小集合，重測對應案；NEG 擴寫無關 Source/Oracle → REPAIR_SCOPE_OVERREACH | 07:L1350｜206322–206767 |
| `H4-12` | PRE-W3 | 原 first W3 packet, SWOF Gate, dispatch raw → non-dispatch proof；Consumer/Owner SWOF Owner；正式 Gate 前只 shadow；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 沒正式 Gate 時 NOT_DISPATCHED 可驗；NEG 無 Gate 卻寫 W3 → PREW3_GATE_BYPASS | 07:L1351｜206768–207184 |

**回切結果**：12/12 列 slice 逐位元相同；`H4-01…H4-12` 連續。

#### D-03b SEAM（宣告 11；實測 11）

| ID | 標題 | 斷言什麼（原契約，逐字） | POS／NEG／退出（尾句省略） | 座標 |
|---|---|---|---|---|
| `SEAM-01` | Activation | host_loader.trigger_route 必註冊；受影 Domain Reader=Host Operator。 | 合法 Skill 真觸發；不存在 route 卻稱 Active → HOST_NOT_EFFECTIVE | 07:L1352｜207185–207459 |
| `SEAM-02` | Pre-gate bypass | gate.receipt_ref 在 dispatch 前驗；受影 Domain Reader=HGK Issuer/Receiver。 | 有權 Gate 先於 effect；dispatch_at<admit_at → PRE_GATE_BYPASS | 07:L1353｜207460–207737 |
| `SEAM-03` | Input downgrade | schema_version/security attributes 不降；受影 Domain Reader=Schema/PIPD Owner。 | 不變欄被保留；v1 threat fields 被刪成 v0 → SCHEMA_DOWNGRADE_DENIED | 07:L1354｜207738–208028 |
| `SEAM-04` | Internal Oracle | oracle.principal_id != maker；受影 Domain Reader=Oracle/Checker Owners。 | 有權 Checker 真分離；Maker 上白名單 → TQ_SOD | 07:L1355｜208029–208288 |
| `SEAM-05` | Canonical Owner | pi.writer_namespace 唯 PIPD；受影 Domain Reader=PIPD Owner。 | 正式 PI Writer 正確；SBL 假 PI → SECOND_CANONICAL_WRITER | 07:L1356｜208289–208545 |
| `SEAM-06` | Fallback compatibility | provider-off 必保持 Required FUO；受影 Domain Reader=Product/Host Owner。 | fallback 有同等 FUO；缺 delete 仍稱 parity → PROVIDER_OFF_FUO_LOSS | 07:L1357｜208546–208835 |
| `SEAM-07` | Alternate route | 每條 route 保持 issuer authority；受影 Domain Reader=HGK/SWOF Owners。 | 本地與連線 Route 不換權威；secondary local grant → WRONG_AUTHORITY_GRANT | 07:L1358｜208836–209125 |
| `SEAM-08` | Post-gate effect | Dispatch 實時 nonce/expiry valid；受影 Domain Reader=HGK Receiver。 | 當下可驗效期；plan 後過期仍動手 → POST_GATE_PERMISSION_EXPIRED | 07:L1359｜209126–209404 |
| `SEAM-09` | Replay/stale | nonce/op_id at-most-once；受影 Domain Reader=Hermes/Issuer。 | Unknown 先 readback；timeout blind retry → EFFECT_REPLAY_DENIED | 07:L1360｜209405–209660 |
| `SEAM-10` | TOCTOU | repo_context.head_sha 鎖 preimage；受影 Domain Reader=L2 Repo Owner。 | 写前 HEAD 同凍結版；中途漂移 → TOCTOU_REPO_HEAD | 07:L1361｜209661–209913 |
| `SEAM-11` | Exact evidence | raw_receipt.subject_sha 同候選；受影 Domain Reader=Evidence/Checker Owner。 | candidate/raw/manifest exact match；舊 SHA Raw 冒用 → RAW_SUBJECT_MISMATCH | 07:L1362｜209914–210202 |

**回切結果**：11/11 列 slice 逐位元相同；`SEAM-01…SEAM-11` 連續。

### D-04｜CH-24 Donor24（24）與 CH-25 Method25（25）具名列舉

> **來源**：`08_TECHNOLOGY_DEFAULT_HOTSWAP(4).md`；sha256 `1df04680319796aa253256c5da9c8adea47a5601abfe17086f3598d4f0470f8d`
> **區段**：§5.3 `Donor24：24 個原身份逐項功能與處置`（byte 158197–242138）與 §5.4 `Method25：25 個原身份逐項功能與處置`（byte 244859–324412）。
> **插入位置**：`CH-24` 主體 `**原產品主題／受影接收**` 段之後（在受影 r4 設計卡之前）；`CH-25` 同位置。
> **邊界**：列舉只還原「原身份／原功能／原處置」，**不構成 TechnologyAdmission 核可**，也不把任何 `原處置` 升為安裝同意。

#### D-04a Donor24：24 個 slot（宣告 24；實測 24）

| Slot ID | Donor | Need（原功能，逐字） | Output／Consumer | 原處置 | 座標 |
|---|---|---|---|---|---|
| `SLOT-OS-01` | OpenSpec | OS-01: if unclear→Explore; if conflict→TT | Trigger = Explore when ambiguous 有效且符合原 disposition → DecisionLedger+QuestionDelta；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1076] | `SELECTIVE_NATIVE_REUSE` | 08:L761｜158197–159165 |
| `SLOT-OS-02` | OpenSpec | OS-02: diff current spec to requested behavior | Trigger = CurrentHEAD+desired scope bounded diff 有效且符合原 disposition → SpecDelta+ChangeProposal；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1077] | `SELECTIVE_NATIVE_REUSE` | 08:L779｜161785–162788 |
| `SLOT-OS-03` | OpenSpec | OS-03: apply only legal write paths then verify | Trigger = Approved Change+WriteSet+Native ECP 有效且符合原 disposition → ChangeSet+ApplyReadback；Reader=WP-FHS-16 受影原 PIPD/SBL/HGK Consumer，effect REPOSITORY_WRITE_ONLY_WITH_NATIVE_DEV_ECP，不可越權；[SRC-MASTER:L1078] | `SELECTIVE_NATIVE_REUSE` | 08:L797｜165461–166488 |
| `SLOT-OS-04` | OpenSpec | OS-04: archive only when truth & trace settled | Trigger = Verified change + trace closed archive 有效且符合原 disposition → ArchiveRecord+Supersession；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1079] | `SELECTIVE_NATIVE_REUSE` | 08:L815｜169162–170174 |
| `SLOT-SK-01` | Spec Kit | SK-01: carry precedence into all downstream artifacts | Trigger = Product kind + Constitution + non-goals 有效且符合原 disposition → ConstitutionBinding；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1080] | `OPTIONAL_GREENFIELD` | 08:L833｜172858–173851 |
| `SLOT-SK-02` | Spec Kit | SK-02: clarify only new high-value unknowns | Trigger = Unknown requirement + value of information 有效且符合原 disposition → RequirementAtom+ACCSeed；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1081] | `OPTIONAL_GREENFIELD` | 08:L851｜176510–177498 |
| `SLOT-SK-03` | Spec Kit | SK-03: topologically sort task nodes after dependencies | Trigger = Bounded task nodes + dependency and owner 有效且符合原 disposition → TaskDAG+TopoOrder；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1082] | `OPTIONAL_GREENFIELD` | 08:L869｜180158–181127 |
| `SLOT-SK-04` | Spec Kit | SK-04: compose only admitted modules | Trigger = Approved workflow manifests with versions 有效且符合原 disposition → WorkflowComposition；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1083] | `OPTIONAL_GREENFIELD` | 08:L887｜183762–184748 |
| `SLOT-MP-01` | mattpocock/skills | MP-01: route domain need, not donor brand | Trigger = Goal+intent type+host capability 有效且符合原 disposition → SkillRouteDecision；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1084] | `METHOD_REUSE` | 08:L905｜187402–188357 |
| `SLOT-MP-02` | mattpocock/skills | MP-02: maximize information gain / known answers never reask | Trigger = Document context+known answers+uncertainty 有效且符合原 disposition → QuestionLedger；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1085] | `METHOD_REUSE` | 08:L923｜190955–191939 |
| `SLOT-MP-03` | mattpocock/skills | MP-03: normalize glossary before ADR | Trigger = Glossary terms+boundary+events 有效且符合原 disposition → DomainModel+Glossary+ADR；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1086] | `METHOD_REUSE` | 08:L941｜194578–195553 |
| `SLOT-MP-04` | mattpocock/skills | MP-04: atom→task seed and acceptance ref | Trigger = Approved SpecCandidate+ACC+task owner 有效且符合原 disposition → TaskSpecSeed+TicketCandidate；Reader=WP-FHS-15 受影原 PIPD/SBL/HGK Consumer，effect LOCAL_DRAFT_NOT_REMOTE_PUBLISH，不可越權；[SRC-MASTER:L1087] | `METHOD_REUSE` | 08:L959｜198179–199188 |
| `SLOT-GS-01` | GSD | GS-01: partition immutable refs and task context | Trigger = SourceHash+Goal+Phase context 有效且符合原 disposition → CheckpointManifest；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1088] | `REFERENCE_ONLY/ARCHIVED_LINEAGE_CHECK` | 08:L977｜201852–202851 |
| `SLOT-GS-02` | GSD | GS-02: gate previous phase before next | Trigger = Milestone DAG + gate prerequisites 有效且符合原 disposition → MilestoneGateDecision；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1089] | `REFERENCE_ONLY/ARCHIVED_LINEAGE_CHECK` | 08:L995｜205402–206423 |
| `SLOT-GS-03` | GSD | GS-03: resume after readback and nonce proof | Trigger = Saved Checkpoint+nonce+effect result 有效且符合原 disposition → ResumeDecision+EffectReadback；Reader=WP-FHS-08 受影原 PIPD/SBL/HGK Consumer，effect RECONCILE_FIRST_NO_REPLAY，不可越權；[SRC-MASTER:L1090] | `REFERENCE_ONLY/ARCHIVED_LINEAGE_CHECK` | 08:L1013｜209012–210058 |
| `SLOT-GS-04` | GSD | GS-04: bind release input sha to test sha | Trigger = Build SubjectSHA+verification+release rights 有效且符合原 disposition → ReleaseReadinessReport；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1091] | `REFERENCE_ONLY/ARCHIVED_LINEAGE_CHECK` | 08:L1031｜212679–213691 |
| `SLOT-GT-01` | gstack | GT-01: role review product value with concrete alternatives | Trigger = ProductKind+JTBD/FUO target 有效且符合原 disposition → ProductReviewFindings；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1092] | `REFERENCE/EVAL_ONLY` | 08:L1049｜216283–217265 |
| `SLOT-GT-02` | gstack | GT-02: review usability,NFR,error paths | Trigger = Arch+NFR+UX baseline 有效且符合原 disposition → EngineeringUXFindings；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1093] | `REFERENCE/EVAL_ONLY` | 08:L1067｜219798–220736 |
| `SLOT-GT-03` | gstack | GT-03: independent review/QA on exact source | Trigger = Test plan+candidate hash+independent checker 有效且符合原 disposition → QAReviewFindings+CheckerRequest；Reader=WP-FHS-09 受影原 PIPD/SBL/HGK Consumer，effect ADVISORY_ONLY_UNTIL_TRUE_CHECKER，不可越權；[SRC-MASTER:L1094] | `REFERENCE/EVAL_ONLY` | 08:L1085｜223211–224214 |
| `SLOT-GT-04` | gstack | GT-04: check ship gate and log retro without modifying Oracle | Trigger = Status checks+user value+release evidence 有效且符合原 disposition → ShipReadinessFindings；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1095] | `REFERENCE/EVAL_ONLY` | 08:L1103｜226793–227781 |
| `SLOT-SP-01` | Superpowers | SP-01: freeze key ADR before effect | Trigger = Design options+source-risk-ADR 有效且符合原 disposition → ArchitectureADR+WriteIntentCandidate；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1096] | `METHOD_REUSE` | 08:L1121｜230342–231296 |
| `SLOT-SP-02` | Superpowers | SP-02: run Red on old HEAD → modify → Green on new HEAD | Trigger = Failing test OldHEAD+exact code scope 有效且符合原 disposition → RedGreenTrace+RunnerRawLog；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1097] | `METHOD_REUSE` | 08:L1139｜233921–234913 |
| `SLOT-SP-03` | Superpowers | SP-03: identify invariant then smallest affected cone | Trigger = Observed failure+repro+root cause 有效且符合原 disposition → RootCauseRecord+RepairCone；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1098] | `METHOD_REUSE` | 08:L1157｜237573–238535 |
| `SLOT-SP-04` | Superpowers | SP-04: bounded plan/test/independent review | Trigger = Plan+independent evidence+review request 有效且符合原 disposition → CompletionGateCandidate；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1099] | `METHOD_REUSE` | 08:L1175｜241161–242138 |

**回切結果**：24/24 個 slot 的 block slice 逐位元相同；分組為 OS 4／SK 4／MP 4／GS 4／GT 4／SP 4＝24，無缺號。

#### D-04b Method25：25 個 method（宣告 25；實測 25）

| Method ID | 名稱 | 用途（Trigger→Output／Consumer，逐字） | 原處置 | 座標 |
|---|---|---|---|---|
| `METHOD-01` | BMAD-METHOD | 只有原適用 Trigger/來源條款支持時 BMAD bounded requirements map + human decisions → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `METHOD_ONLY (not installed claim)` | 08:L1194｜244859–245926 |
| `METHOD-02` | mattpocock/skills:grill-with-docs | 只有原適用 Trigger/來源條款支持時 deduplicated QuestionLedger → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `METHOD_ONLY (not installed claim)` | 08:L1211｜248255–249305 |
| `METHOD-03` | mattpocock/skills:domain-modeling | 只有原適用 Trigger/來源條款支持時 DomainModel + Glossary + ADR conflict → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `METHOD_ONLY (not installed claim)` | 08:L1228｜251595–252655 |
| `METHOD-04` | mattpocock/skills:to-spec | 只有原適用 Trigger/來源條款支持時 SpecCandidate{atoms,ACC,source_refs} → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `METHOD_ONLY (not installed claim)` | 08:L1245｜254955–256005 |
| `METHOD-05` | mattpocock/skills:to-tickets | 只有原適用 Trigger/來源條款支持時 TaskSpecSeed+TicketCandidate local JSON → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `METHOD_ONLY (not installed claim)` | 08:L1262｜258303–259379 |
| `METHOD-06` | OpenSpec | 只有原適用 Trigger/來源條款支持時 ChangeDraft→SpecDelta→bounded patch/ref+archive candidate → WP-FHS-16 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE_TRANSLATE (not installed claim)` | 08:L1279｜261700–262775 |
| `METHOD-07` | Spec Kit | 只有原適用 Trigger/來源條款支持時 ConstBinding/Spec/Plan/TaskDAG → WP-FHS-16 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE_WRAP (not installed claim)` | 08:L1296｜265107–266107 |
| `METHOD-08` | Superpowers | 只有原適用 Trigger/來源條款支持時 DesignDecision/RedGreenTrace/RootCause/ReviewGate → WP-FHS-18 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE_TRANSLATE (not installed claim)` | 08:L1313｜268369–269421 |
| `METHOD-09` | GitHub Actions | 只有原適用 Trigger/來源條款支持時 CI status checks/readback expectations → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE_WRAP (not installed claim)` | 08:L1330｜271727–272763 |
| `METHOD-10` | MCP | 只有原適用 Trigger/來源條款支持時 TypedToolDescriptor/transport mapping → WP-FHS-17 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `PROTOCOL_ONLY (not installed claim)` | 08:L1347｜274959–275980 |
| `METHOD-11` | ACP | 只有原適用 Trigger/來源條款支持時 AgentMessageCandidate → WP-FHS-17 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `PROTOCOL_ONLY (not installed claim)` | 08:L1364｜278170–279142 |
| `METHOD-12` | OpenSSF Scorecard | 只有原適用 Trigger/來源條款支持時 ScorecardSignals and PolicyReview → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `SUPPORT_ONLY (not installed claim)` | 08:L1381｜281283–282327 |
| `METHOD-13` | SLSA | 只有原適用 Trigger/來源條款支持時 SLSA ProvenanceExpectation → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `SUPPORT_ONLY (not installed claim)` | 08:L1398｜284610–285620 |
| `METHOD-14` | OWASP | 只有原適用 Trigger/來源條款支持時 negative fixtures and guarded failure expectations → WP-FHS-09 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `SUPPORT_ONLY (not installed claim)` | 08:L1415｜287799–288822 |
| `METHOD-15` | CodeQL | 只有原適用 Trigger/來源條款支持時 SARIF findings+query provenance → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE (not installed claim)` | 08:L1432｜291012–291989 |
| `METHOD-16` | Semgrep | 只有原適用 Trigger/來源條款支持時 Rule ID/path/priority findings → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE (not installed claim)` | 08:L1449｜294218–295204 |
| `METHOD-17` | Renovate | 只有原適用 Trigger/來源條款支持時 Renovate update proposal PR candidate → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `DEFER (not installed claim)` | 08:L1466｜297441–298455 |
| `METHOD-18` | Dependabot | 只有原適用 Trigger/來源條款支持時 Dependabot update proposal (source-specific owner TT) → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `NO_SOURCE_EVIDENCE (not installed claim)` | 08:L1483｜300640–301711 |
| `METHOD-19` | Cosign | 只有原適用 Trigger/來源條款支持時 Signature verification report → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE (not installed claim)` | 08:L1500｜303938–304934 |
| `METHOD-20` | Syft | 只有原適用 Trigger/來源條款支持時 Syft SBOM (SPDX/CycloneDX) → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE (not installed claim)` | 08:L1517｜307099–308064 |
| `METHOD-21` | Trivy | 只有原適用 Trigger/來源條款支持時 Trivy scanner result+policy outcome → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE (not installed claim)` | 08:L1534｜310203–311176 |
| `METHOD-22` | SQLite/FTS5 | 只有原適用 Trigger/來源條款支持時 SQLite schema/FTS5 index and query evidence → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `LOCAL_FIRST_OPTION (not installed claim)` | 08:L1551｜313402–314450 |
| `METHOD-23` | FAR/FDA | 只有原適用 Trigger/來源條款支持時 Native owned FAR/FDA reference only → WP-FHS-18 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `HGK_FABRIC_EXISTING_ONLY (not installed claim)` | 08:L1568｜316720–317780 |
| `METHOD-24` | OpenAI Agents SDK | 只有原適用 Trigger/來源條款支持時 HITL pause/resume donor pattern → WP-FHS-17 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `SUPPORT_QUARANTINE (not installed claim)` | 08:L1585｜319993–321058 |
| `METHOD-25` | Agent Skills specification | 只有原適用 Trigger/來源條款支持時 SKILL.md format and dependency validation → WP-FHS-11 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `PORTABILITY_SPEC (not installed claim)` | 08:L1602｜323339–324412 |

**回切結果**：25/25 個 method 的 block slice 逐位元相同；`METHOD-01…METHOD-25` 連續。

### 分母對帳（宣告 vs 實測）

| 缺口 | 章 | 宣告 | 實測 | 唯一 id | delta | 判定 |
|---|---|---:|---:|---:|---:|---|
| D-02 | CH-11 | 18 | 18 | 18 | +0 | MATCH |
| D-03 | CH-42 旁 | 12 | 12 | 12 | +0 | MATCH |
| D-03 | CH-42 旁 | 11 | 11 | 11 | +0 | MATCH |
| D-04 | CH-24 | 24 | 24 | 24 | +0 | MATCH |
| D-04 | CH-25 | 25 | 25 | 25 | +0 | MATCH |

五項宣告數（18／12／11／24／25）與來源實測數**全部相符**，不需更正任何分母；本輪沒有發現「宣告多列」或「宣告少列」的情形。

**W0 r4 控制稿自身是否列舉（同檔 regex 計數，非引述）**：

| 缺口 | 章 | 具名列舉 | 全檔 token 命中 |
|---|---|---|---|
| D-02 | CH-11 | **0 列** | `PM:T0`／`SE:T1`／`TPgM:T5` 型式＝0；「18 Stage」字樣＝5 |
| D-03 | （無專章） | **0 列** | `H4-nn`＝0；`SEAM-nn`＝0 |
| D-04 | CH-24 | **0 列** | `SLOT-xx-nn`＝0；「Donor24」字樣＝4 |
| D-04 | CH-25 | **0 列** | `METHOD-nn`＝0；「Method25」字樣＝4 |

也就是說：四個章節都只宣告「有幾個」，**沒有任何一個 id 出現在控制稿裡**。

**修補前的具名數（量測，非引述）**：

| 文件 | CH-24 具名 slot | CH-25 具名 method | 合計／49 |
|---|---:|---:|---:|
| W0 r4 skeleton（本次修補對象） | 0 | 0 | 0／49 |
| W0 r7 writeback（前輪已修版本） | 3 | 4 | 7／49 |

即：r4 控制稿的 CH-24／CH-25 章內**一個 slot／method id 都沒有**（`SLOT-`、`METHOD-` 在整份 r4 檔的命中數為 0），並非「只缺一部分」；
下一輪 writeback 已具名 7 個（3 slot＋4 method），其餘 42 個仍靠外部指標。本檔補的正是這 49 個。

### 本檔不主張

- 不主張任何列已被原 Domain Reader／Owner 讀回或追認（`ORIGINAL_ACK` 不在本輪）。
- 不主張 18 Stage 已被真 Host 執行、也不主張 H4／SEAM／96 Oracle 已被 Protected Checker 判定。
- 不主張 24 slot／25 method 中任何一個已取得 TechnologyAdmission 或授權（來源 disposition 僅為原字面）。



### C.5 閘：從 15 項到 16 項，並證明它會咬

`GSTACK` 在本輪的角色不是「再跑一次」，而是「**對 r6 回合重跑，並補上它結構上看不到的那一層**」。

| 情境 | 判決 | 事實 |
|---|---|---|
| 對 r6 回合重跑原 15 項 | **15/15 PASS，exit 0** | 116 個宣告 artifact 重雜湊、350 個 `source_ref` 從原始 bytes 重切、0 問題 |
| 注入三種違規（byte 層／prose 層／span 層） | **12/15，exit 1** | 紅在且僅紅在 `G2`／`G5b`／`G6`，`caught_extra` 為 0（證明閘有辨識力，不是空判） |
| 原 15 項對 r7 文件 | **全綠** | 這正是缺口：15 項都不檢查「文件自己宣告的父本 digest 是否解析得到」 |
| 新增 `G10-DOC-PARENT-CLAIM` 對 r7 | **FAIL（`COPY_AMBIGUITY`）** | 宣告 `69a08e7f…` 指向回合內副本；鏈上走的 KB 副本是 `9f9eb261…`；同名、同長度、不同 bytes |
| 同一支閘對 r8（本章） | **16/16 PASS** | 父本 `264787b0…`（r7）可直接解析，且 r8 前綴與 r7 逐位元相同 |

**為什麼要補這一項**：r7 的母本保全聲明對讀者是可驗證的承諾；15 項閘全綠而該承諾不可驗證，代表閘的覆蓋面有一個具體的洞。`G10` 只做一件事——把文件對自己來源的宣告，當成需要被重算的資料，而不是背景文字。

### C.6 明確不主張的事，與合併後的一份 OWNER 待辦

**不主張**（逐項對照 r7 §B.5，本輪未改變任何一項）：

- 不主張任何 WP 達到 `ORIGINAL_ACK`：六個 WP 的原域 Reader 收據數仍為 **0**。
- 不主張 `W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE=true`。
- 不主張 Fabric policy 生效、Issuer 恢復（registry 仍 rev 13 `3254714b…`）、T2、DEV 或任何世界效果。
- 不主張三份 SPEC 是原 PIPD schema `$id`，也不主張 Owner SourceFreeze。
- 不主張任何 PR 已併、已被人類審查、已發行：r7 的兩個 PR（SBL #50、Fabric #36）在本輪讀回時仍為 `open`／`mergeable`／未併。
- 不主張 96 Oracle 已被保護檢查者判定：它們是計畫，狀態 `NOT_EXECUTED / RUNNER_UNBOUND`。

**Owner 簽章需求＝0**（`OWNER_SIGNING_DEMAND_W0R7.json`）：本輪全部效果為 `SOURCE_READ`／`LOCAL_DRAFT_WRITE`／`LOCAL_PROCESS_EXECUTE`，加上以 repo token 授權的 feature-branch 發佈；registry 仍 rev 13、31 列全 `INSTALLED` 全已簽、root 簽章在場，本輪未新增或改寫任何列，故**未開窗、未簽任何東西**。

**合併後的一份具名待辦**（不逐一回頭問）：

| # | 待辦 | FirstFail | 需要什麼 Raw | Resume 條件 |
|---|---|---|---|---|
| 1 | `R1-ISSUER-REV14` | `REGISTRY_REV13_NO_ISSUER_RECOVERY` | rev 14 registry＋31 列與 root 的 owner 簽章 | 受保護終端開窗後由 owner 執行 issuer 工具 |
| 2 | `AUTHORITY-17-COLLISIONS`（含 `V-01` 的兩份 r6） | `NAME_COLLISION_DIFFERENT_DIGEST` | 每個同名組指定權威副本的 owner 聲明 | 聲明落地後重算 source lock |
| 3 | `LICENCE-FABRIC-HGK` | `LICENCE_ABSENT_IN_TWO_REPOS` | 兩庫授權決定 | 根層 LICENSE／NOTICE 存在且掃描重跑 |
| 4 | `HGK-CI-ABSENT` | `CI_SERVICE_ABSENT` | 是否建 CI 的決定 | 有 workflow 且能跑，或明示不建並收窄供應鏈期待 |
| 5 | `PIPD-15-VALUESET` | `CONTRACT_FAMILY_VALUE_SET_UNCLOSED` | 15 個 contract family 的 value-set 閉合 | 閉合落地且 schema 綁定 |

### C.7 母本保全與副本清冊

本檔 = `FHS_PIPD-LS-PKG_W0_r7.md` 全文（**492,290 bytes**，sha256 `264787b065fbca6a8e728054fd3abdb6133883bbeb87710ddf5e880071f61845`）＋本章。r7 的全部章節（含其 A.1–A.6 與 B.1–B.6）逐位元保留於本檔前綴，本章不修改、不摘要、不覆蓋任何 r7 條款。

**r6 副本清冊**（`V-01` 的完整陳述；兩份皆 481,212 bytes、正文相同、僅附錄 `產生時間` 4 bytes 不同）：

| 副本 | sha256 | 產生時間 | 誰在讀 |
|---|---|---|---|
| `…\知識庫\…\PIPD-LS-PKG\回寫\W0 ~ W2\FHS_PIPD-LS-PKG_W0_r6.md` | `9f9eb261c44f96488c2f0a3156b0a9fdc6ea91ddac823800fb8c1a593a9b6234` | 2026-11-07T23:10:08+0800 | 知識庫的「當期」閱讀路徑 |
| `…\FHS_W0W2_R4_20261107\writeback\W0\FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae0404d7fc33842d66c28a21684a6d13caa6ac40ba7a269411db28d5` | 2026-11-07T23:41:56+0800 | r7 文件宣告的父本 |

兩者的正文（0 – 475,271 bytes）逐位元相同；差異只在附錄時間戳。**本檔不對此下權威判斷**：哪一份是 canonical 是原 Owner 的決定（待辦 2）。本檔能做的是把它寫成可機械分辨的事實，而不是讓下一個讀者在兩條路徑上得到兩個答案。

---

## 實作修補回寫（Implementation Repair）— W0 r9

> **ArtifactID**：`FHS_PIPD-LS-PKG_W0_r9_REPAIR@2026-11-08`
> **Parent／Supersedes**：`FHS_PIPD-LS-PKG_W0_r8.md` @ `ccd545b5c7b4eecbf62bcd23e650a91d7832bfefe62f08ce2e589a58df087e22`（539,712 bytes）
> **本版 SHA256**：見同目錄 `W0_REVISION_MANIFEST.json`（本檔不記錄自身 digest，避免自我指涉）
> **產生時間**：2026-11-08T10:20:00+08:00
> **性質**：追加章節。r8 全文 539,712 bytes 逐位元保留為本檔前綴（寫入前以位元比對斷言）。
> **ClaimCeiling**：`W0_SEVEN_DEFECTS_REPAIRED_WITH_SCOPED_OWNER_HOLDS`。本章不授權任何世界效果，不代表任何原域 Reader ACK。

### D.0 一句話

r8 把上一輪量到的十個缺陷寫成句子；r9 把其中 8 個改回工具與產物裡，讓缺陷消失而不是被描述，另 2 個（canonical 副本選擇、跨庫 packaging／授權決定）依性質留給 owner。新增十個閘檢項，其中 6 個在修補前的產物上會紅、全部 10/10 在修補後轉綠，並以逐項注入證明每一個都會咬。

這一輪**沒有**新增任何權限：owner 簽章需求實測仍為 0（registry rev 13、31 列全 `INSTALLED` 全已簽、root 簽章在場、本輪不動任何列），所有效果仍是 `SOURCE_READ`／`LOCAL_DRAFT_WRITE`／`LOCAL_PROCESS_EXECUTE`／以 repo token 推候選分支。

### D.1 七個缺陷的現況（不是處置說明，是可重算的狀態）

| ID | r8 的狀態 | r9 實測狀態 | 依據 |
|---|---|---|---|
| `V-01` | 文件列舉兩份 r6 副本 | **工具化**：副本登記簿把 49 個被引用名稱全部解析成 digest；唯一歧義群 `FHS_PIPD-LS-PKG_W0_r6.md` 兩份同長 [481212]、4 bytes 不同、首個差異在 offset 475677；canonical=`OWNER_UNRESOLVED` | `out/SOURCE_COPY_REGISTER.json` |
| `V-02` | 改為分方法並列（散文） | **重算**：四族 × 三對，`max_overall`=0.245432（等於八個分解值的最大）；舊值 0.0755 只在**前輪自己的正規化**下重現為 0.075472（屬 `P-A / sentence_shingle_2gram`）；本輪正規化下最近值是 0.105，`reproduced_as_maximum`=False；負控克隆 0.996624 | `lanes/C/DISTINCTNESS_V2.json` |
| `V-03` | 改寫作用域（散文） | **拆欄位**：in-set 重複 basename=0、重複 digest=None；外部副本在**精確同名**規則下為 0，在**去掉尾碼 `(N)`** 規則下為 17——17 只在後者成立 | `lanes/A/AUTHORITY_CONFLICT_LEDGER_V2.json` |
| `V-04` | 標為「規則相依」 | **雙規則、雙計數**：`RULE_PER_LINE`=111,331（等於 31 檔換行數），`RULE_STRUCTURAL_BLOCK`=25,201；兩規則都對 0..filesize 全覆蓋（31/31 檔） | `lanes/B/U0_PARTITION_V2.json` |
| `V-05` | 改為 payload 內宣告 | **已於 r8 發佈落實，本輪加驗證器與閘**：r8 的 SBL 載荷 19/19 digest 在自身 payload 內解析；新增 `G18` 使跨 payload 的 digest 一律紅 | `out/stage/**/MANIFEST.json`、`G18` |
| `V-06` | 限定為「根層」 | **逐庫分層欄位**：SBL root=True／nested 2；Fabric root=False／nested 6；HG-KSEOS root=False／nested 8 | `lanes/D/WP19_V2.json` |
| `V-07` | 把相符限定為 bytes＋sha（散文） | **改工具**：四種行數慣例並列，`verdict` 需 bytes、lines、sha 三者全真；31/31 三欄全真，宣告合計 111,331＝實測 111,331；舊 `split` 慣例合計 111,362（差 31） | `lanes/A/SOURCE_LOCK_V2.json` |

### D.2 四項「前輪寫法被本輪量測推翻」的更正

這一節是本輪最重要的產出，因為它推翻的是**同一份文件的附錄**，不是更早的版本。

**（1）`A-01` 在兩個地方都寫錯。** 附錄寫「HG-KSEOS 有三個模組 import `cryptography`，而 pyproject 宣告 `dependencies = []`」。實測：

- `pyproject.toml:6` 是 `dependencies = ["cryptography>=42"]`——**已宣告**，不是空清單；
- 附錄點名的 `src/hg_kseos/fhs/issuer_binding.py` **不存在**；`cryptography` 只出現在 `native_admission.py` 與 `user_trust.py` 兩個檔；
- 真正未宣告的是 **`yaml`**：`src/hg_kseos/lane_policy.py:71`，函式內 lazy import，`except` 後 `return None`——是 fail-closed，但代價是「全新安裝時重複 key 檢查靜默失效」。三個 repo 的 `declared_covers_imports` 為 SBL=True／Fabric=False／HGK=False。

修補已做成可驗證的 patch（未套用到該 repo）：套用前 `UNDECLARED_DEPENDENCY`（未宣告 ['yaml']），套用後 `DECLARED_COVERS_IMPORTS`；`patch --binary -p1` 套用結果與候選檔逐位元相等＝True。內容是加一個 optional extra `yaml = ["PyYAML>=6"]`——與程式碼已經假設的「可選」一致，而不是把它升成硬依賴。

**（2）`A-02` 的機制比附錄寫的更窄。** 附錄說「naive identifier regex 會數到 10」。實測：只按空白切 token 仍然數到 11；只有**把 `/` 當欄位分隔**（即假設 `ID Title / SRC-nn:Lxxx` 三欄）的解析器才會丟掉 `SEAM-09`。本輪把兩種解析器都保存：naive=10、robust=11、缺 `SEAM-09`。所以 A-02 的正確說法是「某類解析器會低估」，不是「regex 會低估」。

**（3）`V-03` 的 17 需要一個沒被寫出來的規則。** 31 個源檔的檔名帶 `(1)` 尾碼，知識庫裡的副本不帶。用**精確同名**比對，外部副本數是 0（也就是「沒有同名副本」）；只有把尾碼 `(N)` 剝掉再比對，才得到 17 個源檔有相異副本、14 個完全相同。前兩輪的「17」成立，但依賴一條從未寫下的正規化規則。

**（4）`V-06` 的嵌套數變了，位置也和上一輪寫的不一樣。** 附錄寫 Fabric 深度 5、HG-KSEOS「全樹 0」。本輪逐庫遞迴量到 Fabric 6、HG-KSEOS 8——而 HGK 的 8 個**全部**在 `fhs_msc_handoff_20261030/WP-FHS-17/candidate/…` 之下（kind 全為 `other`），是 **tracked** 的授權檔，不是 vendored 快取；`candidate/package/LICENSE` 第 3 行逐字為「Copyright (c) 2026 the owner of this system. All rights reserved.」。所以「根層無授權檔」成立，「全樹無授權檔」不成立；而 HGK 的問題從「沒有授權檔」變成「有四組 proprietary 授權檔」，後者是 owner 要回答的問題，不是量測缺口。Fabric 由 5 變 6 的原因是 `LICENSES/` 目錄版的 REUSE 檔，已記在 artifact 的 `nested_count_by_rule`。

### D.3 閘：繼承 16 ＋ 新增 10，並用差分與注入各證明一次

| 層 | 判決 | 事實 |
|---|---|---|
| 繼承的 16 項（對 r6 回合、r8 為鏈子） | **16/16 PASS** | 116 個宣告 artifact 重雜湊、350 個 source ref 從原始 bytes 重切、0 問題；`G10` 對 r8 為 `RESOLVED` |
| 新增 10 項（對 r9 產物） | **10/10 PASS**（1 項待發佈載荷） | 見下表逐項 |
| 同一支新閘對**修補前**產物 | **6 FAIL／2 PASS／2 n/a** | 紅的是缺陷真的還在的那幾項；n/a 是前輪沒有對應 artifact |
| 逐項注入（每項一次標的性 mutation） | **10/10 FIRED** | 每一項都紅在它自己的代碼上，不是靠其他檢查順手抓到 |

| 檢查 | 修補後 | 修補前 | 它到底在看什麼 |
|---|---|---|---|
| `G11 LINE_CONVENTION` | PASS | FAIL | verdict 是否覆蓋它印出來的行數欄位 |
| `G12 SEGMENTATION_RULE` | PASS | FAIL | 兩個具名規則是否都存在且各自貼齊 |
| `G13 COUNT_SCOPE` | PASS | PASS | 每個計數是否帶作用域與比對規則 |
| `G14 MAXIMUM_IS_GLOBAL` | PASS | FAIL | 「上限」是否是全集合的最大值 |
| `G15 LICENCE_LAYER` | PASS | FAIL | 授權宣稱是否帶層（root／nested） |
| `G16 DECLARED_COVERS_IMPORTS` | PASS | FAIL | 宣告依賴是否覆蓋實際 import |
| `G17 ENUM_SLASH_SAFE` | PASS | PASS | 分母是否由不受標點影響的解析器得出 |
| `G18 DIGEST_LOCALITY` | PASS | NOT_APPLICABLE | 每個 manifest digest 是否在自身 payload 內解析 |
| `G19 COPY_REGISTER` | PASS | NOT_APPLICABLE | 多副本名稱是否以 digest 解析、canonical 是否留給 owner |
| `G20 SUPPLY_CHAIN_SPLIT` | PASS | FAIL | 離線可重現與 hosted 結論是否分開且不可互代 |

`G17` 在修補前是 PASS：前輪的 SEAM 數**是對的**，缺的是「這個數字怎麼來的」可被檢驗。差分抓不到的那一種缺陷，用注入證明——把 `naive` 改成 11 後 `G17` 立刻紅在 `SLASH_PARSE_NOT_DEMONSTRATED`。

### D.4 六個 WP 的現況（唯一有效版本）

| WP | r8 | r9 | 這一輪實際改了什麼 |
|---|---|---|---|
| `WP-FHS-00` | `MEASURED` | `MEASURED_REPAIRED` | source lock 的 verdict 現在含行數；31/31 三欄全真（31/31） |
| `WP-FHS-01` | `MEASURED` | `MEASURED_REPAIRED` | U0 改雙規則（111,331 行段／25,201 結構塊）；ACL 拆作用域 |
| `WP-FHS-15` | `MEASURED` | `MEASURED_REPAIRED` | 相似度四族並列、全域上限 0.245432、0.0755 降為子欄值 |
| `WP-FHS-16` | `MEASURED` | `MEASURED_UNCHANGED` | 這一輪的七個缺陷無一落在 WP16；不重跑，也不重述 |
| `WP-FHS-19` | `MEASURED` | `MEASURED_REPAIRED` | 授權拆層、宣告 vs import 對帳（['yaml']）、SBL 供應鏈主張拆兩半 |
| `WP-FHS-21` | `MEASURED` | `MEASURED_REPAIRED` | 分母改 slash-safe；15／96／12／11 四項 match，12×8 完備 |

`ORIGINAL_ACK` 仍是 **0**。`W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE` 仍是 **false**。這一輪沒有任何一句話在改變這件事。

### D.5 仍然沒有的東西，與合併後的一份 OWNER 待辦

| # | 待辦 | FirstFail | 需要什麼 Raw | Resume 條件 |
|---|---|---|---|---|
| 1 | `R1-ISSUER-REV14` | `REGISTRY_REV13_NO_ISSUER_RECOVERY` | rev 14 registry ＋ 31 列與 root 的 owner 簽章 | 受保護終端開窗後由 owner 執行（`--max-ops 33`） |
| 2 | `AUTHORITY-COLLISIONS` | `NAME_COLLISION_DIFFERENT_DIGEST` | 每個歧義名稱組指定權威副本的 owner 聲明（目前 1 組） | 聲明落地後重跑副本登記簿，該組離開 `ambiguous` |
| 3 | `LICENCE-FABRIC-HGK` | `LICENCE_ABSENT_AT_ROOT` | 兩庫的授權決定 | 根層 LICENSE／NOTICE 存在且掃描重跑 |
| 4 | `HGK-CI-ABSENT` | `CI_SERVICE_ABSENT` | 是否建 CI 的決定（現在有第二個理由：`yaml` 未宣告） | 有 workflow 且能跑，或明示不建並收窄期待 |
| 5 | `PIPD-15-VALUESET` | `CONTRACT_FAMILY_VALUE_SET_UNCLOSED` | 15 個 contract family 的 value-set 閉合 | 閉合落地且 schema 綁定 |
| 6 | `ORIGINAL-ACK-18` | `ORIGINAL_READER_ACK_UNOBSERVED` | 任一原域 Reader 對同 subject/scope 的 bytes 出具 ACK 或 scoped NACK | 收據落地 |

### D.6 母本保全與副本清冊

本檔 = `FHS_PIPD-LS-PKG_W0_r8.md` 全文（**539,712 bytes**，sha256 `ccd545b5c7b4eecbf62bcd23e650a91d7832bfefe62f08ce2e589a58df087e22`）＋本章。r8 的全部章節逐位元保留於前綴；本章不修改、不摘要、不覆蓋任何 r8 條款。

`V-01` 的完整陳述現在是一個 artifact 而不是一段話：`out/SOURCE_COPY_REGISTER.json` 登錄 49 個名稱、檢查 22 個檔案，只有 `FHS_PIPD-LS-PKG_W0_r6.md` 一組歧義（2 個 digest、4 bytes 不同）。哪一份是 canonical 仍由 owner 決定（待辦 2）。

### D.7 可重現指令

```bash
cd C:/Projects/Agent_Workspace/FHS_W0_R9_REPAIR_20261108

# 逐 lane 重算（每個都會覆寫自己的 JSON）
python lanes/A/tools/source_lock_v2.py
python lanes/A/tools/authority_conflicts_v2.py
python lanes/B/tools/u0_partition_v2.py && python lanes/B/tools/tile_proof.py
python lanes/C/tools/distinctness_v2.py
python lanes/D/tools/wp19_v2.py
python lanes/E/tools/wp21_enum_v2.py

# 副本登記簿與 A-01 patch
python tools/build_copy_register.py --sources <31 sources> --root <kb> --out out/SOURCE_COPY_REGISTER.json
python tools/a01_dependency_patch.py

# 閘：修補後、修補前、逐項注入
python tools/gate_w0r9.py --round . --json out/GATE_R9.json
python tools/gate_w0r9.py --prior ../FHS_W0_R6_20261108 --json out/GATE_R9_ON_PRIOR.json
python tools/gate_w0r9.py --round . --selftest

# 繼承的 16 項
cd ../FHS_W0_R7_VERIFY_20261108 && python tools/gate_w0r7.py \
  --object-round ../FHS_W0_R6_20261108 \
  --chain-child writeback/W0/FHS_PIPD-LS-PKG_W0_r9.md
```

### D.8 明確不主張

- 不主張任何 WP 達到 `ORIGINAL_ACK`：六個 WP 的原域 Reader 收據仍為 0。
- 不主張 `W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE=true`。
- 不主張两份 r6 之中哪一份是 canonical；只主張兩份都存在、同長、差 4 bytes。
- 不主張 HG-KSEOS 的 packaging 已修好：patch 已驗證但**未套用**，因為那是該 repo 的寫入，且它沒有 CI 可驗。
- 不主張 25,201 是「語意分割數」：它是 `RULE_STRUCTURAL_BLOCK` 的塊數，和 111,331 的行段數一樣都不是語意單元數。
- 不主張前輪的 24,003 錯了：那是另一條規則（整個 fenced block／整個 table 各算一塊），差 1,198 是規則差異，已寫在 `reconciliation`。

