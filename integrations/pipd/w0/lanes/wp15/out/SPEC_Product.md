# SPEC_Product｜SPEC-Product-W0-wp15-local

> claim_ceiling=`AUTHOR_LOCAL_TEST`；native_effect=`NOT_RUN`；body_sha256=`56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a`
> 本文件只由 `spec_pipeline.py` 從正文與 registry 實算產生，未執行任何 Native 效果。

## §0 Subject Binding 與 Claim Ceiling

- subject_id: `FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001`
- body: `FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md` / 463034 bytes / sha256 `56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a`
- candidate: `FHS-W0-AUTHOR-STATIC-FINAL-CANDIDATE-r4-candidate-b41d2e`（CURRENT_CANDIDATE）
- 原 PIPD 簽名：`NOT_OBSERVED`；claim_ceiling=`AUTHOR_LOCAL_TEST`
- 三份 SPEC 共用同一個 subject 區塊；差異在於各自的主體欄位與章節，不在標題。

## §1 Persona 與 JTBD

**Persona**：唯一 Human Owner，單人本機、日常普通 Goal；模型/工具原生 Worker 是執行角色，非新的 Owner/Issuer

- 可量測 POS：不必先填完整 PIPD schema 即可取用可追溯答案或 SPEC
- 排除 NEG／FirstFail：要求所有短問答先開 22 WP → `FUO_BURIED_BY_PROCESS`
- 來源：`FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md:226`

**JTBD**：將普通 Goal 與已許可來源轉成可用的 source-bound SpecDelta，只有受保護世界效果才提升 Gate

| 面向 | 內容 |
|---|---|
| 可量測 POS | `goal, affected_scope, source_refs, user_value, acceptance±` 全有 |
| 排除 NEG | 只輸出「已建立 30 個文件」→ `NO_USER_VALUE` |
| 來源 | `FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md:227` |

## §2 FUO Register

共 **13** 筆 FUO（11 筆來自 W0_REQUIRED22 的 Product 需求列，2 筆來自 CH-01 宣告列）。

> acceptance POS 對 W0_REQUIRED 來源列即其 `requirement` 原文（該 registry 未另存 POS 欄）；acceptance NEG 取自同列的 `source_negative`。CH-01 宣告列的 POS/NEG 取自正文表格。

| fuo_id | statement | acceptance POS | acceptance NEG | deliver_id | source_ref |
|---|---|---|---|---|---|
| `FUO-INT-01` | 以 Subject+Scope+SourceSHA 鍵重用 KnownAnswer/QuestionLedger，只有差額重問 | 以 Subject+Scope+SourceSHA 鍵重用 KnownAnswer/QuestionLedger，只有差額重問 | NEG：沿用相同 SourceSHA 卻重問同一已知答案；或混同一個 Human Owner 與技術 Checker 身分 | `DEL-W0-INT-01` | `W0_REQUIRED22_TRACE.json` L1-r4 span=[769, 769] |
| `FUO-INT-03` | 短 Goal 可產直接有用答案／SPEC，寫入則需實際 Diff/Host | 短 Goal 可產直接有用答案／SPEC，寫入則需實際 Diff/Host | NEG：只交文件數量、沒有使用者可取用之 FUO，或冒稱 Host 已執行 | `DEL-W0-INT-03` | `W0_REQUIRED22_TRACE.json` L1-r4 span=[771, 771] |
| `FUO-INT-04` | A 全量產品語義守恆；B 最短合法 Effect 路徑 | A 全量產品語義守恆；B 最短合法 Effect 路徑 | NEG：把 A 全量需求全作每次 B READ 的前置 OPS Permit | `DEL-W0-INT-04` | `W0_REQUIRED22_TRACE.json` L1-r4 span=[772, 772] |
| `FUO-INT-12` | PM JTBD/FUO；SE ADR/ABI；TPgM DAG/Exit | PM JTBD/FUO；SE ADR/ABI；TPgM DAG/Exit | NEG：三 SPEC 同文換標題或沒有不同 Consumer/ACC | `DEL-W0-INT-12` | `W0_REQUIRED22_TRACE.json` L1-r4 span=[780, 780] |
| `FUO-INT-18` | 六類 Effect 對應最低充分原 Evidence | 六類 Effect 對應最低充分原 Evidence | NEG：缺 OPS/RELEASE Permission 使合法 READ/DRAFT 全域停工 | `DEL-W0-INT-18` | `W0_REQUIRED22_TRACE.json` L1-r4 span=[786, 786] |
| `FUO-FHS-DR-002` | Goal 不需先選九個 MissionOptions 或填完整 PIPD Schema | Goal 不需先選九個 MissionOptions 或填完整 PIPD Schema | 新 PID 可取得可追溯答案 | `DEL-W0-FHS-DR-002` | `W0_REQUIRED22_TRACE.json` L1-r4 span=[799, 799] |
| `FUO-FHS-DR-003` | 模糊 Goal 可以進三 SPEC，來源缺件只保留受影 Need | 模糊 Goal 可以進三 SPEC，來源缺件只保留受影 Need | 三 SPEC 各自有 ACC/NEG/NonGoals | `DEL-W0-FHS-DR-003` | `W0_REQUIRED22_TRACE.json` L1-r4 span=[800, 800] |
| `FUO-FHS-DR-021` | Portable TPM 能以 PM/SE/TPgM 產三獨立 SPEC | Portable TPM 能以 PM/SE/TPgM 產三獨立 SPEC | 各 SPEC 有原來源和非目標 | `DEL-W0-FHS-DR-021` | `W0_REQUIRED22_TRACE.json` L1-r4 span=[818, 818] |
| `FUO-FHS-DR-022` | 18 Stage/K0–K3 及原問題去重仍遵守 | 18 Stage/K0–K3 及原問題去重仍遵守 | 當次階段結果可原位交下游 | `DEL-W0-FHS-DR-022` | `W0_REQUIRED22_TRACE.json` L1-r4 span=[819, 819] |
| `FUO-FHS-DR-047` | LOCAL_DRAFT_WRITE 需隔離 output root/原文未修改 | LOCAL_DRAFT_WRITE 需隔離 output root/原文未修改 | 真檔案來源/字元編碼/Readback | `DEL-W0-FHS-DR-047` | `W0_REQUIRED22_TRACE.json` L1-r4 span=[844, 844] |
| `FUO-FHS-DR-055` | L0/L1/L2/L3 是文檔視圖，非四套 Canonical | L0/L1/L2/L3 是文檔視圖，非四套 Canonical | 逐層交 downstream 不改原 Writer | `DEL-W0-FHS-DR-055` | `W0_REQUIRED22_TRACE.json` L1-r4 span=[852, 852] |
| `FUO-A` | 讀取已上傳來源後，直接交付需求／風險／可行更改的帶來源回答 | 選定一段原需求能回溯 SourceSHA、Parent、NEG、Consumer | grep-only 當語義通過 → `SEMANTIC_HOLD` | _chapter-level_ | `FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md:228` |
| `FUO-B` | 需改程式時先交 Product、Architecture、Program 三份不同 SPEC 的**草案**與最小原接收請求 | 三份互相對齊、各有 1 個對應 Original Consumer、各有 POS/NEG | 以草稿自稱 native PI 編譯完成 → `CANONICAL_WRITER_BOUNDARY` | _chapter-level_ | `FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md:229` |

## §3 MVP 範圍

W0-A 完成問題/已知答案/源索引和三 SPEC；W0-B 交付五 Seam 的預期 Input/Output、原 Receiver 和最短可測 fixture

- POS：無 Host Raw 也能作合法 W1 文檔交接；未觀測項在 HOLD
- NEG：要求 W0 執行 GJ02 的 REPO_WRITE → `FUTURE_RECEIPT_DEPENDENCY`
- 波次：W0-A / W0-B

## §4 Non-Goals

不建第二 HGK 控制層、Compiler、Queue、Independent Checker、Release Gate；不重新分配 SBL 領域正本

- 不建：第二 HGK 控制層
- 不建：第二 Compiler
- 不建：第二 Queue
- 不建：Independent Checker
- 不建：Release Gate
- 邊界來源：`FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md:129`

## §5 ACC+ 正例

| acc_id | kind | statement | first_fail | source_ref |
|---|---|---|---|---|
| `ACC+-CH01` | BODY_ACCEPTANCE_POS | POS：三 SPEC 均同 Subject、各有可取用 FUO、Owner 可逐項讀回正/負例。 | `-` | `FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md` 198 |
| `ACC+-AC-C39-POS-DETERMINISTIC` | ORACLE96_POS_DETERMINISTIC | fixtures/AC-C39-POS-DETERMINISTIC.pos.json | `MISSING_POS_FUNCTION` | `ORACLE96_CONTRACTS.json` span [172, 183] |
| `ACC+-AC-C39-POS-STATE_READBACK` | ORACLE96_POS_STATE_READBACK | fixtures/AC-C39-POS-STATE_READBACK.pos.json | `MISSING_POS_FUNCTION` | `ORACLE96_CONTRACTS.json` span [184, 195] |
| `ACC+-AC-C39-POS-PROPERTY` | ORACLE96_POS_PROPERTY | fixtures/AC-C39-POS-PROPERTY.pos.json | `MISSING_POS_FUNCTION` | `ORACLE96_CONTRACTS.json` span [196, 207] |
| `ACC+-AC-C39-POS-REFERENCE_OUTPUT` | ORACLE96_POS_REFERENCE_OUTPUT | fixtures/AC-C39-POS-REFERENCE_OUTPUT.pos.json | `MISSING_POS_FUNCTION` | `ORACLE96_CONTRACTS.json` span [208, 219] |
| `ACC+-AC-C39-POS-STATISTICAL` | ORACLE96_POS_STATISTICAL | fixtures/AC-C39-POS-STATISTICAL.pos.json | `MISSING_POS_FUNCTION` | `ORACLE96_CONTRACTS.json` span [220, 231] |
| `ACC+-AC-C39-POS-SEMANTIC_JUDGE` | ORACLE96_POS_SEMANTIC_JUDGE | fixtures/AC-C39-POS-SEMANTIC_JUDGE.pos.json | `MISSING_POS_FUNCTION` | `ORACLE96_CONTRACTS.json` span [232, 243] |
| `ACC+-AC-C39-POS-HUMAN` | ORACLE96_POS_HUMAN | fixtures/AC-C39-POS-HUMAN.pos.json | `MISSING_POS_FUNCTION` | `ORACLE96_CONTRACTS.json` span [244, 255] |
| `ACC+-AC-C39-POS-COMPOSITE` | ORACLE96_POS_COMPOSITE | fixtures/AC-C39-POS-COMPOSITE.pos.json | `MISSING_POS_FUNCTION` | `ORACLE96_CONTRACTS.json` span [256, 267] |

## §6 ACC− 反例與 FirstFail

| acc_id | kind | statement | firstfail codes | source_ref |
|---|---|---|---|---|
| `ACC--CH01` | BODY_ACCEPTANCE_NEG | NEG：將完成三檔當最終產品 Native 閉環；FirstFail=FUO_NOT_OBSERVABLE。 | `FUO_NOT_OBSERVABLE` | `FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md` 199 |
| `ACC--AC-C39-NEG-DETERMINISTIC` | ORACLE96_NEG_DETERMINISTIC | 將拒收轉成功或寫入禁止state；observed_value改成非expected | `NEGATIVE_ACCEPTED` | `ORACLE96_CONTRACTS.json` span [268, 279] |
| `ACC--AC-C39-NEG-STATE_READBACK` | ORACLE96_NEG_STATE_READBACK | 將拒收轉成功或寫入禁止state；actual_post_state不同或foreign world Reader | `NEGATIVE_ACCEPTED` | `ORACLE96_CONTRACTS.json` span [280, 291] |
| `ACC--AC-C39-NEG-PROPERTY` | ORACLE96_NEG_PROPERTY | 將拒收轉成功或寫入禁止state；至少一generated case破invariant | `NEGATIVE_ACCEPTED` | `ORACLE96_CONTRACTS.json` span [292, 303] |
| `ACC--AC-C39-NEG-REFERENCE_OUTPUT` | ORACLE96_NEG_REFERENCE_OUTPUT | 將拒收轉成功或寫入禁止state；更換reference或輸出差異 | `NEGATIVE_ACCEPTED` | `ORACLE96_CONTRACTS.json` span [304, 315] |
| `ACC--AC-C39-NEG-STATISTICAL` | ORACLE96_NEG_STATISTICAL | 將拒收轉成功或寫入禁止state；刪dataset/改confidence/樣本不達界 | `NEGATIVE_ACCEPTED` | `ORACLE96_CONTRACTS.json` span [316, 327] |
| `ACC--AC-C39-NEG-SEMANTIC_JUDGE` | ORACLE96_NEG_SEMANTIC_JUDGE | 將拒收轉成功或寫入禁止state；judge未校準/不同rubric卻聲稱一致 | `NEGATIVE_ACCEPTED` | `ORACLE96_CONTRACTS.json` span [328, 339] |
| `ACC--AC-C39-NEG-HUMAN` | ORACLE96_NEG_HUMAN | 將拒收轉成功或寫入禁止state；Maker冒Human或決議是另一scope | `NEGATIVE_ACCEPTED` | `ORACLE96_CONTRACTS.json` span [340, 351] |
| `ACC--AC-C39-NEG-COMPOSITE` | ORACLE96_NEG_COMPOSITE | 將拒收轉成功或寫入禁止state；刪hard component或soft分數蓋hard fail | `NEGATIVE_ACCEPTED` | `ORACLE96_CONTRACTS.json` span [352, 363] |

## §7 Requirement 綁定表

共 **11** 個 RequirementID；registry 內可綁定總數 84。

| RequirementID | kink | source_id | source_sha | span | chapters | consumer |
|---|---|---|---|---|---|---|
| `INT-01` | Product | `L1-r4` | `cbdd75fd609b5353` | [769, 769] | CH-01, CH-10 | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) |
| `INT-03` | Product | `L1-r4` | `cbdd75fd609b5353` | [771, 771] | CH-01, CH-38 | SBL Product/Kind/Host Original Consumer、Original Domain Owner/Reader (scope binding pending) |
| `INT-04` | Product | `L1-r4` | `cbdd75fd609b5353` | [772, 772] | CH-15, CH-18, CH-38 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、HGK Original Issuer/SharedSpine/Protected… |
| `INT-12` | Product | `L1-r4` | `cbdd75fd609b5353` | [780, 780] | CH-11 | Original Domain Owner/Reader (scope binding pending) |
| `INT-18` | Product | `L1-r4` | `cbdd75fd609b5353` | [786, 786] | CH-15, CH-39, CH-43 | SBL-hosted PIPD canonical Compiler/Original Source/Repo/Case Reader、HGK Original Issuer/SharedSpine/Protected… |
| `FHS-DR-002` | Product | `L1-r4` | `cbdd75fd609b5353` | [799, 799] | - | [CH-01](#ch-01)/[CH-02](#ch-02) |
| `FHS-DR-003` | Product | `L1-r4` | `cbdd75fd609b5353` | [800, 800] | - | [CH-11](#ch-11)/[CH-01](#ch-01) |
| `FHS-DR-021` | Product | `L1-r4` | `cbdd75fd609b5353` | [818, 818] | - | [CH-11](#ch-11) |
| `FHS-DR-022` | Product | `L1-r4` | `cbdd75fd609b5353` | [819, 819] | - | [CH-11](#ch-11) |
| `FHS-DR-047` | Product | `L1-r4` | `cbdd75fd609b5353` | [844, 844] | - | [CH-15](#ch-15) |
| `FHS-DR-055` | Product | `L1-r4` | `cbdd75fd609b5353` | [852, 852] | - | [CH-45](#ch-45) |

### Open holds
- H-U4：原 SBL Product / PIPD Intake Reader 未 ACK，FUO 只到 AUTHOR_DESIGN
- H-ORACLE-RAW96：96 個 Oracle 個案無原 Host Runner／Fixture 真 bytes
- 所有人類簽章、Judge 校準、WorldRaw 皆 EXPECTED_NOT_OBSERVED
