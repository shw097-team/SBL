# Program SPEC（TPgM）

> 本文件為 **作者端 SPEC 草稿**（`FHS-WP15-SPEC-PROGRAM-DRAFT`）。宣稱上限：`AUTHOR_SIDE_SPEC_DRAFT_SOURCE_BOUND`。
> 不是 Owner SourceFreeze，不是原 PIPD schema `$id`，不帶 Original Reader ACK，不構成任何世界效果。三份 SPEC 共用同一 Subject，但 Consumer、非目標、驗收與 NEG 各自不同。

| 欄位 | 值 |
|---|---|
| artifact_id | `FHS-WP15-SPEC-PROGRAM-DRAFT` |
| version | `W0-r6-wp15-1` |
| role | `TPgM` |
| subject_ref | `FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001`（AUTHOR_W0_DEMO_SUBJECT__ORIGINAL_PIPD_UNBOUND） |
| 章節依據 | CH-11 / CH-37 / CH-42 |
| claim_ceiling | `AUTHOR_SIDE_SPEC_DRAFT_SOURCE_BOUND` |

## 1. goal（目標）

把一份 Product SPEC 與一份 Architecture SPEC，交成 22 個 WorkPackage、36 條邊的排程契約：每個 WP 恰一個 Primary Wave、一個 DonePredicate、一組 stop/resume，並且在第一波就能交付，不必等未來的世界收據。

## 2. scope（範圍）

**在範圍內**

- 22 個 WP 的 Primary Wave 指派與前置（36 條原邊不改）
- 每個 WP 的 DonePredicate、Stop／Resume、具名 HOLD
- W0-A／W0-B 的分界與 W1 交接信封

**不在範圍內**

- 重畫、刪除或新增 DAG 邊
- 宣告任何 WP 的世界效果已完成
- 代替原 Native PLAN Reader 決定 execution binding

EffectClass：`LOCAL_DRAFT_WRITE`；輸出 root：`evidence/WP15/stages`。

## 3. persona_or_owner（角色與責任界線）

- persona：TPgM：排程與交接責任人，對「誰先誰後、什麼算做完、卡住時停在哪」負責
- 不是：不是執行者；不發 WorkOrder，不簽 Receipt，不把排程當成已完成事件
- 本 SPEC 的作者角色：`tpm-program-plan（TPgM 作者角色）`

## 4. jtbd（使用者任務）

當我要把一整包變更交給後續幾波時，我需要一張能直接照著跑的順序表：哪一個工作包這一波就能做、做到什麼算完、卡住時要停在哪一格、醒來時從哪裡續，而不是等到第二波才發現第一波其實交不出東西。

## 5. fuo（第一個有用結果，十欄）

一份 ProgramSPECDraft：22 列 WP×Wave 表、36 條原邊的無環證明、每列一組 done/stop/resume，以及一份可被原 Program Reader 讀回的 W1 交接信封；其中沒有任何 WP 引用尚未觀測的收據。

| 欄 | 內容 |
|---|---|
| `who` | TPgM（排程作者），與 Original Program/DAG Reader 對讀 |
| `trigger` | Product 與 Architecture 兩份 SPEC 已可在隔離目錄讀取，且需要交成可執行順序 |
| `input` | 兩份 SPEC、原 22 WP 表、原 36 條邊、每個 WP 的 EffectClass |
| `operation` | 對每個 WP 指定唯一 Primary Wave 與前置、寫 DonePredicate、標 Stop 錐與 Resume 條件、登記具名 HOLD，最後跑一次拓撲檢查 |
| `output` | ProgramSPECDraft：WaveAssignment + DonePredicate + HoldRegister + HandoffEnvelope |
| `observable proof` | tools/verify_dag.py 對 36 條邊跑拓撲排序：節點 22、邊 36、無環、每個 WP 的 Primary Wave 與 WP 表一致（已量測 22/36 acyclic，見 evidence/dag_check.json）；沒有任何 done_predicate 需要 W2 以後的 receipt 才成立 |
| `consumer` | Original FHS BODY-11 Program/DAG Reader |
| `first_fail` | PROGRAM_WAVE_MISMATCH |
| `stop_rule` | 當某個 WP 的 done_predicate 需要未來 receipt 時，把該 WP 標 FUTURE_RECEIPT_DEPENDENCY 並停在那個 cone，不重排邊、不新增替代波 |
| `resume_predicate` | 該 receipt 由原 Consumer 讀回後，只恢復受影 cone 的 WP；同 WorkID 已 admitted 時，續工優先於新包 |

十欄齊備性由 `tools/spec_distinctness.py` 的完整性檢查斷言（每欄非空、共十欄）；每一欄的 consumer 與 first_fail 另由 `tools/verify_spans.py` 的 firstfail code 證據交叉驗證。

## 6. non_goals（非目標）

- 不改動 36 條原邊的方向、數量或 hard/soft 判定；不新增 W4 替代方案來縮工
- 不把 WP-FHS-06（First Reversible Slice）提前到 W0 執行，也不宣稱它已可逆通過
- 不建立第二個排程器、Kanban 佇列或 shadow queue
- 不以 Scheduled／In Progress 當成 Done，也不以文件存在當成世界效果
- 不代替原 HGK Issuer 發 WorkOrder，或代替原 Protected Checker 發 verdict

## 7. assumptions（假設）

- 22 個 WP 與 36 條邊是來源 11 與 CH-37 已列名的原結構，本輪不改
- W0 的六個 WP（00/01/15/16/19/21）只做 READ 與隔離 Draft，因此可在無 Host Raw 時交付
- 同一 WorkID 的續工優先於新包啟動，此假設沿用 CH-37 的 stop/resume 條文

## 8. decisions（決策）

- D-G1：每個 WP 只能有一個 Primary Wave；跨波需求以邊表達，不以第二個 Wave 欄位表達
- D-G2：DonePredicate 必須是可在本輪觀測的條件；需要未來的 receipt 時，該 WP 不得標 DONE
- D-G3：Stop 以「第一失敗依賴的 cone」為界，其他 READY 的 WP 繼續
- D-G4：交接信封裡的 hold 一律具名 owner 與 unblock 條件，未具名者不得進入信封

## 9. acceptance（驗收：POS／NEG）

| id | kind | statement | oracle | consumer | firstfail_code |
|---|---|---|---|---|---|
| `G-ACC-01` | POS | 22 個 WP 各恰一個 Primary Wave，36 條邊的拓撲排序成功且節點數為 22 | python tools/verify_dag.py：從 W0 CH-37 兩張表解析後跑 Kahn 拓撲排序，斷言 22 WP／36 邊／無環／wave 與 WP 表一致 | Original FHS BODY-11 Program/DAG Reader | `PROGRAM_WAVE_MISMATCH` |
| `G-ACC-02` | POS | 每個 WP 都有 done_predicate、stop_rule、resume_predicate 與至少一個具名 hold 或明示無 hold | 逐列檢查四欄；缺欄或 hold 未具名 owner 即不成立 | Original FHS BODY-11 Program/DAG Reader | `FUTURE_RECEIPT_DEPENDENCY` |
| `G-ACC-03` | NEG | 把 WP-FHS-06 列為 W0 已執行完成（或其可逆效果已通過） | 對照 Primary Wave 表；WP-06 屬 W2 且需 W1 的 PI/PD/RepoContext/Permit（verify_dag.py 量測 WP-FHS-06 primary wave = W2） | Original Program Reader | `PROGRAM_WAVE_MISMATCH` |
| `G-ACC-04` | NEG | 首份 W0 Draft 要等未來 W2 的 receipt 才願交付，使第一波沒有可讀產物 | 檢查 W0 六個 WP 的 done_predicate 是否引用未觀測 receipt | Original Program Reader | `FUTURE_RECEIPT_DEPENDENCY` |
| `G-ACC-05` | NEG | 為縮工而改動原 DAG 邊、刪除 WP 或新增替代波，仍宣稱 22/36 保持不變 | 邊集合與節點集合逐項比對來源 11；差集非空即拒收 | Original FHS BODY-11 Program/DAG Reader | `SPEC_TRACE_BROKEN` |

所有 firstfail_code 均曾在 W0 r6 文件中出現，位置見 `evidence/firstfail_codes.json`，並由 `tools/verify_spans.py` 重切驗證。

## 10. source_refs（來源綁定）

每一列的 `quoted_text` 存在同名 JSON 的 `source_refs`，且等於該檔 `[byte_start:byte_end)` 的實際 bytes。

| ref | file | sha256（前 12） | byte span | 節錄 |
|---|---|---|---|---|
| `G01-W0-CH37-WP15-ROW` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 242935–243434 | \| `WP-FHS-15` TPM Corpus & SPEC 18Stage \| 原三SPECDraft、來源re… |
| `G02-W0-CH37-WP-TABLE-HEAD` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 238474–238906 | ### 完整 22 個 Original WP、唯一 Primary Wave 與 Effect（L2 r4 §4.1）… |
| `G03-W0-CH37-DAG-HEAD` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 245239–245614 | ### 原 36 邊 DAG（L2 r4 §4.2，原 Reader 判定 consumption 時 Hard/Sof… |
| `G04-W0-CH37-POS-NEG` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 237241–237353 | **Acceptance POS**：POS：22/36 原資料有向無環；每原 WP 只有一主波，受影 effect 需… |
| `G05-W0-CH37-TPGM-CONTRACT` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 132664–133119 | **Program SPEC — `W0/TPgM/ProgramSPEC-DRAFT`**：`milestone=W0… |
| `G06-SRC11-WP15` | `11_WORKPACKAGES_AND_DAG(4).md` | `6c526c991b59` | 31113–33568 | ### WP-FHS-15｜TPM Corpus & SPEC 18Stage   #### HANDOFF-v1 首工… |
| `G07-SRC01-PROGRAM-SPEC` | `01_PRODUCT_AUTHORITY_SPINE(4).md` | `e257dfcd01f2` | 13916–14907 | ### Program SPEC｜Typed DAG、最小自舉與有界續工  - **起跑線**：WP-FHS-00 → … |
| `G08-SRC02-TPGM-STAGES` | `02_PIPD_LIFECYCLE_AND_TPM(4).md` | `c336d3d9d702` | 8351–8903 | \| TPgM:T2 \| ownergates, dependencyedges, source_sha256 \| … |

## 11. open_questions（未決問題）

- Q-G1：W0-B 的 WP06 準備工作是否可在 W0 內以純設計形式存在（不產生 Repo diff），待原 Program Reader 回答
- Q-G2：36 條邊的 hard/soft 判定權在原 Operator，本輪只標候選，需確認是否要逐邊列出
- Q-G3：W1 交接信封的 YAML 是否要固定 schema 版本，或維持 CH-37 的自由欄位

## 12. affected_holds（受影具名 HOLD）

| hold | scope | owner | unblock |
|---|---|---|---|
| `H-WP15-G-ORIGINAL-PROGRAM-READER` | 22WP/36 邊與 wave 指派 | Original FHS BODY-11 Program/DAG Reader | 同 Subject/Scope 的原 Reader 讀回，或具名 NACK 指明哪條邊 |
| `H-WP15-G-CR-DOC04-STATE-MAP` | T4/T5 transition 當期映射 | Original PIPD Compiler Owner | T4/T5 映射經原 Compiler 確認；在此之前維持 HOLD，不升為 StateEnum |

## 13. original_reader（原始 Reader 與 ACK 狀態）

- reader：Original FHS BODY-11 Program/DAG Reader → Native PLAN Reader
- ack：`ORIGINAL_READER_ACK_UNOBSERVED`
- note：排程只到候選；W1 之後的 execution binding 由原 Native PLAN Reader 決定。

## 14. claim_ceiling（宣稱上限）

`AUTHOR_SIDE_SPEC_DRAFT_SOURCE_BOUND`

本 SPEC 不宣稱：`ORIGINAL_ACK`、Owner SourceFreeze、原 PIPD schema `$id`、Host Active 讀回、任何世界效果或 Release。

