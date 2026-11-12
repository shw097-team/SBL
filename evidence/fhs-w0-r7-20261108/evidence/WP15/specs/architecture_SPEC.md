# Architecture SPEC（SE）

> 本文件為 **作者端 SPEC 草稿**（`FHS-WP15-SPEC-ARCHITECTURE-DRAFT`）。宣稱上限：`AUTHOR_SIDE_SPEC_DRAFT_SOURCE_BOUND`。
> 不是 Owner SourceFreeze，不是原 PIPD schema `$id`，不帶 Original Reader ACK，不構成任何世界效果。三份 SPEC 共用同一 Subject，但 Consumer、非目標、驗收與 NEG 各自不同。

| 欄位 | 值 |
|---|---|
| artifact_id | `FHS-WP15-SPEC-ARCHITECTURE-DRAFT` |
| version | `W0-r6-wp15-1` |
| role | `SE` |
| subject_ref | `FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001`（AUTHOR_W0_DEMO_SUBJECT__ORIGINAL_PIPD_UNBOUND） |
| 章節依據 | CH-11 / CH-15 / CH-42 |
| claim_ceiling | `AUTHOR_SIDE_SPEC_DRAFT_SOURCE_BOUND` |

## 1. goal（目標）

把 Product SPEC 宣告的差額，落到五個 typed seam 上：每個 seam 一個 writer、一個 reader、一組被禁止的效果，並指出 ABI 版本候選與這一輪不能宣告的 Host 狀態。

## 2. scope（範圍）

**在範圍內**

- 五個 seam 的 writer/reader/forbidden_effect 指派
- ADR 選項與 trade-off、ABI 版本候選
- EffectClass 分類（SOURCE_READ / LOCAL_DRAFT_WRITE / REPO_WRITE / HOST_OP / RELEASE）
- seam 的 first_fail 與 rollback 語義

**不在範圍內**

- 產品差額的取捨（Product SPEC 已定）
- WP 波次與 stop/resume（Program SPEC 已定）
- 任何 Permit、Admission、PolicyEpoch 的發行

EffectClass：`LOCAL_DRAFT_WRITE`；輸出 root：`evidence/WP15/specs`。

## 3. persona_or_owner（角色與責任界線）

- persona：SE：讀得懂現役 registry 與 ABI 的架構作者，站在既有三庫 Writer 的旁邊做候選設計
- 不是：不是新 Issuer；不簽 Permit；不代替 HGK 原 Receiver 宣告 admission
- 本 SPEC 的作者角色：`tpm-system-plan（SE 作者角色）`

## 4. jtbd（使用者任務）

當一份差額需要跨過 SBL／PIPD／HGK／Fabric／Hermes 的邊界時，我要能一眼看出「這段由誰寫、誰讀、誰絕不能寫」，這樣才不會出現第二個 Issuer 或第二份真相，也不用等到 Host 出事才發現界線模糊。

## 5. fuo（第一個有用結果，十欄）

一份 ArchitectureSPECDraft，內含五個 seam 的 owner 表、ADR 選項與 ABI 候選版本，每一個 seam 都能指出它的 forbidden_effect 與 first_fail；在同一份文件裡，READ／DRAFT／REPO／OPS／RELEASE 五類效果不會被折成一類。

| 欄 | 內容 |
|---|---|
| `who` | SE（架構作者），與原 Registry Reader 同席審閱 |
| `trigger` | Product SPEC 的某條差額確定要跨庫，或現役 ABI 無法表達該差額 |
| `input` | Product SPEC、五個 seam 的現役 producer/consumer、三庫現役 ABI 與 Effect Registry 條目 |
| `operation` | 逐 seam 指派唯一 writer 與 reader、標出 forbidden_effect、挑 ADR 選項、標 ABI 版本候選，並把每個 seam 的效果歸到單一 EffectClass |
| `output` | ArchitectureSPECDraft：SeamOwnershipMap + ADRSet + ABI candidate + EffectMatrix + SoD NEG |
| `observable proof` | 每個 seam 的 writer 與 forbidden_effect 可對回現役 registry 的具名條目；同一 seam 的 writer 與 checker 不為同一 principal，且可由表格交集運算證明為空 |
| `consumer` | Original SBL/HGK/Fabric Architecture Registry Reader |
| `first_fail` | ARCH_SOD_BREACH |
| `stop_rule` | 當某 seam 的 reader 在現役 registry 找不到時，該 seam 停在具名 HOLD，不再新增 ABI 欄位或臨時 adapter |
| `resume_predicate` | 該 seam 的原 Registry Reader 讀回後，只重做該 seam 的 ADR 與 owner 列，其他 seam 不動 |

十欄齊備性由 `tools/spec_distinctness.py` 的完整性檢查斷言（每欄非空、共十欄）；每一欄的 consumer 與 first_fail 另由 `tools/verify_spans.py` 的 firstfail code 證據交叉驗證。

## 6. non_goals（非目標）

- 不建立第二個 HGK Issuer、第二條 Queue、第二個 SharedSpine 或第二個 Protected Checker
- 不以 adapter 生成 Permit、Admission 或 PolicyEpoch，也不把 GitHub HEAD／staging 當 Host Active
- 不改寫 PIPD 的 19 個 contract family 或 13 個 CLI 動詞，不加第 14 個 verb
- 不決定 WP 的 Primary Wave，也不宣告任何 WP 已完成
- 不把效果分類壓成單一 OPS 權限，也不為未綁定的 OperationType 造 ABI

## 7. assumptions（假設）

- 現役三庫的 ABI 與 Effect Registry 在本輪為唯讀；任何不一致先記 HOLD，不就地修
- 五個 seam 的 producer/consumer 已由來源 01 的 seam 表列名，可直接引用
- ABI 版本候選只是候選，需原 Registry 讀回才成立

## 8. decisions（決策）

- D-A1：seam 以「一個 writer + 一個 reader + 一組 forbidden_effect」為最小欄位組，缺一不算 seam
- D-A2：EffectClass 為五值列舉，seam 只能歸一類；跨界要拆成兩個 seam，不得共用一個 grant
- D-A3：SoD 以 principal 集合證明：writer∩checker=∅，並在表中留下可運算的欄位
- D-A4：ABI 相容性以版本候選＋reader 讀回為條件，未讀回前標 CANDIDATE

## 9. acceptance（驗收：POS／NEG）

| id | kind | statement | oracle | consumer | firstfail_code |
|---|---|---|---|---|---|
| `A-ACC-01` | POS | 五個 seam 每個恰有一個 writer、一個 reader 與一組 forbidden_effect，且全部可對回現役 registry | seam 表與來源 01 的 seam 表逐列 join；writer 與 checker 的 principal 交集必須為空 | Original SBL/HGK/Fabric Architecture Registry Reader | `ARCH_SOD_BREACH` |
| `A-ACC-02` | POS | EffectMatrix 把五類效果分列，每個 seam 只落一類，且每類都寫出 permission_basis | 對照來源 03 的 EffectClass 表逐列檢查；缺 permission_basis 即不成立 | Original HGK Effect Registry Reader | `EFFECT_UNBOUND` |
| `A-ACC-03` | NEG | 同一個新服務同時簽 Permit 又當 Checker（SoD 破壞）仍被接受 | principal 交集運算；非空即拒收 | Original HGK Issuer Registry Reader | `ARCH_SOD_BREACH` |
| `A-ACC-04` | NEG | 把 GitHub HEAD 或 staging 的狀態當成 Host Active 讀回，並據此宣告 ABI 已綁 | 檢查每個 seam 的讀回來源；非 Host Raw 即不得寫 active | Original Host Raw Reader | `HOST_READBACK_HOLD` |
| `A-ACC-05` | NEG | 把所有操作歸成一律 OPS 權限，使 READ／DRAFT 也被 Permit 阻塞 | 檢查 EffectMatrix 是否只剩一類；只剩一類即拒收 | Original HGK Effect Registry Reader | `EFFECT_CLASS_COLLAPSED` |

所有 firstfail_code 均曾在 W0 r6 文件中出現，位置見 `evidence/firstfail_codes.json`，並由 `tools/verify_spans.py` 重切驗證。

## 10. source_refs（來源綁定）

每一列的 `quoted_text` 存在同名 JSON 的 `source_refs`，且等於該檔 `[byte_start:byte_end)` 的實際 bytes。

| ref | file | sha256（前 12） | byte span | 節錄 |
|---|---|---|---|---|
| `A01-W0-CH11-SE-CONTRACT` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 132104–132662 | **Architecture SPEC — `W0/SE/ArchitectureSPEC-DRAFT`**：`syst… |
| `A02-W0-CH11-SE-CONSUMER` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 128694–129083 | \| Architecture SPEC \| Product SPEC 同 Subject + 五 Typed Sea… |
| `A03-W0-CH15-EFFECT-CLASSES` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 146967–147473 | `SOURCE_READ`=原 ACL+hash；`LOCAL_DRAFT_WRITE`=授權隔離 output roo… |
| `A04-SRC01-ARCH-SPEC` | `01_PRODUCT_AUTHORITY_SPINE(4).md` | `e257dfcd01f2` | 12138–13915 | ### Architecture SPEC｜單一 Writer 與有版本的 ABI  \| Seam \| Produc… |
| `A05-SRC03-FIVE-ABI` | `03_ARCHITECTURE_ABI_AND_EFFECT(4).md` | `58628861e639` | 8543–9934 | ## R2-03-ABI：五個 typed handoff  1. Source/Intent/Profile → PI… |
| `A06-SRC03-EFFECT-TABLE` | `03_ARCHITECTURE_ABI_AND_EFFECT(4).md` | `58628861e639` | 6817–7509 | ## R2-03-EFFECT：效果與退出按類處理  \| EffectClass \| tier \| permiss… |
| `A07-SRC02-SE-STAGES` | `02_PIPD_LIFECYCLE_AND_TPM(4).md` | `c336d3d9d702` | 6096–6626 | \| SE:T0 \| repoboundaries, sourceindex, source_sha256 \| en… |

## 11. open_questions（未決問題）

- Q-A1：五個 seam 之外是否還需要第六個 seam 來承接 W18 的 normal-entry，待原 Registry Reader 回答
- Q-A2：ABI 版本候選要用語意版號還是 date-stamp，需與原 PIPD Compiler 對齊
- Q-A3：seam 的 forbidden_effect 是否要細到 OperationType 層級，本輪只到 EffectClass

## 12. affected_holds（受影具名 HOLD）

| hold | scope | owner | unblock |
|---|---|---|---|
| `H-WP15-A-ORIGINAL-ARCH-READER` | seam 歸屬與 ABI 相容性 | Original SBL/HGK/Fabric Architecture Registry Reader | 同 Subject/Scope 的原 Reader 讀回，或具名 NACK 指明哪個 seam |
| `H-WP15-A-HOST-RAW` | Host Active 與 LoadedSHA | Original Host Raw Reader | 真 Host Raw 讀回；在此之前不得寫 active |

## 13. original_reader（原始 Reader 與 ACK 狀態）

- reader：Original SBL/HGK/Fabric Architecture Registry Reader
- ack：`ORIGINAL_READER_ACK_UNOBSERVED`
- note：ABI 與 seam 都只到 CANDIDATE；沒有讀回不得升為現役。

## 14. claim_ceiling（宣稱上限）

`AUTHOR_SIDE_SPEC_DRAFT_SOURCE_BOUND`

本 SPEC 不宣稱：`ORIGINAL_ACK`、Owner SourceFreeze、原 PIPD schema `$id`、Host Active 讀回、任何世界效果或 Release。

