# Product SPEC（PM）

> 本文件為 **作者端 SPEC 草稿**（`FHS-WP15-SPEC-PRODUCT-DRAFT`）。宣稱上限：`AUTHOR_SIDE_SPEC_DRAFT_SOURCE_BOUND`。
> 不是 Owner SourceFreeze，不是原 PIPD schema `$id`，不帶 Original Reader ACK，不構成任何世界效果。三份 SPEC 共用同一 Subject，但 Consumer、非目標、驗收與 NEG 各自不同。

| 欄位 | 值 |
|---|---|
| artifact_id | `FHS-WP15-SPEC-PRODUCT-DRAFT` |
| version | `W0-r6-wp15-1` |
| role | `PM` |
| subject_ref | `FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001`（AUTHOR_W0_DEMO_SUBJECT__ORIGINAL_PIPD_UNBOUND） |
| 章節依據 | CH-01 / CH-11 / CH-42 |
| claim_ceiling | `AUTHOR_SIDE_SPEC_DRAFT_SOURCE_BOUND` |

## 1. goal（目標）

把一個普通 Goal 加上已授權來源，轉成 Owner 能逐條接受或拒絕的產品差額（SpecDelta），並把「第一個有用結果」說成使用者真的拿得到的東西，而不是生成檔案的數量。

## 2. scope（範圍）

**在範圍內**

- SBL14／FHS17 已授權且 SHA 可讀的來源段落
- W0-A 階段的產品差額（persona、JTBD、FUO、non-goals、ACC±）
- 同一 Subject+Scope+SourceSHA 的 QuestionLedger 重用

**不在範圍內**

- 任何 Repo、Host、Release 的世界效果
- 原 PIPD schema 的 $id、PI/PD 版本晉升
- 其他 SPEC 的 seam 或波次決策

EffectClass：`LOCAL_DRAFT_WRITE`；輸出 root：`evidence/WP15/specs`。

## 3. persona_or_owner（角色與責任界線）

- persona：單人 Human Owner：本機、日常普通 Goal、不預先具備 PIPD/TPM 詞彙
- 不是：模型、工具、Worker、Agent 都不是 Owner，也不是第二個 Issuer/Checker
- 本 SPEC 的作者角色：`tpm-product-plan（PM 作者角色）`

## 4. jtbd（使用者任務）

當我有一個還說不清楚的變更念頭時，我要用一句普通話把來源指給我，然後拿到一份逐條可判斷「這條我要／不要」的差額清單，這樣我不必先學會 22 個 WorkPackage 或填完 PIPD schema 才能開始。

## 5. fuo（第一個有用結果，十欄）

Owner 打開 ProductSPECDraft，看到每一條差額都掛著來源身分與使用者可見價值，可以在同一輪內逐條接受或拒絕，並知道被拒絕的條目不會被下游悄悄復活。

| 欄 | 內容 |
|---|---|
| `who` | 單人 Human Owner（非工程角色），在同一個本機工作階段內操作 |
| `trigger` | Owner 提出一句普通 Goal，且手上有一份已授權來源（或明確宣告缺源） |
| `input` | Goal、source_refs[]（含 file_sha256 與 byte 範圍）、KnownAnswerRef、read_acl |
| `operation` | PM 綁 persona／pain／JTBD，重用同 Subject/Scope/SourceSHA 的已知答案，只對差額開新問題，然後把可觀察結果寫成 SpecDelta 條目 |
| `output` | ProductSPECDraft + SpecDelta（每條帶 user_value 與 ACC±） |
| `observable proof` | Owner 在終端逐條讀出 diff 並標 accept/reject；每條都可反查 file_sha256+byte_start/byte_end 且重切結果等於 quoted_text |
| `consumer` | Original SBL Product Reader → Original PIPD Intake |
| `first_fail` | PRODUCT_SPEC_FUO_MISSING |
| `stop_rule` | 當每一條差額都已掛上來源或具名 HOLD，就停止擴寫；不以增加章節數延長本階段 |
| `resume_predicate` | 同一 Subject+Scope+SourceSHA 的 QuestionLedger 已有回答時不重問，只補來源或決策版本變更所產生的差額 |

十欄齊備性由 `tools/spec_distinctness.py` 的完整性檢查斷言（每欄非空、共十欄）；每一欄的 consumer 與 first_fail 另由 `tools/verify_spans.py` 的 firstfail code 證據交叉驗證。

## 6. non_goals（非目標）

- 不建立新的 Issuer、Compiler、Queue、Independent Checker 或 Release Gate
- 不重新分配 SBL／PIPD／Fabric／HGK 的領域正本，也不刪除既有 Kind/Mode/Host 命名
- 不以檔案數量、章節數量或 Kanban 狀態代替使用者可取的結果
- 不在本 SPEC 內決定 seam 歸屬（那是 Architecture SPEC 的職責）或波次（那是 Program SPEC 的職責）
- 不把 P01–P07 七個痛點壓成一句「符合需求」

## 7. assumptions（假設）

- 31 份來源的 bytes/SHA 已由 WP-FHS-00 的 SourceManifest 鎖定，且在本輪內不變動
- Owner 能讀懂中文條列與 diff，但不需要讀 JSON
- 原生 Worker（模型、CLI、IDE）只是執行角色，其人數不代表 Owner 的數量

## 8. decisions（決策）

- D-P1：以「差額」為交付單位，不以「文件」為交付單位；一條差額一個可判斷句
- D-P2：FUO 一律寫成使用者動作＋可見結果＋反查方式；三欄缺一即不成立
- D-P3：已知答案以 Subject+Scope+SourceSHA 三方鍵重用，鍵不同才重問
- D-P4：本 SPEC 內所有 ID（P.W0.PROD.*）皆為作者端標記，非 PIPD schema $id

## 9. acceptance（驗收：POS／NEG）

| id | kind | statement | oracle | consumer | firstfail_code |
|---|---|---|---|---|---|
| `P-ACC-01` | POS | 每一條 SpecDelta 條目都帶可重切的來源（file_sha256+byte 範圍），且 Owner 能對它給出接受或拒絕 | verify_spans.py 重切 == quoted_text；Owner 的 accept/reject 逐條記錄在同一份 draft 旁 | Original SBL Product Reader | `SPEC_NOT_SOURCE_BOUND` |
| `P-ACC-02` | POS | FUO 十欄全部有值，且 observable_proof 是可在本機重跑的命令，而不是形容詞 | 十欄完整性檢查 + 重跑 observable_proof 所述命令 | Original SBL Product Reader | `PRODUCT_SPEC_FUO_MISSING` |
| `P-ACC-03` | NEG | 以「已建立 N 個文件／N 個章節」交付，沒有任何使用者可取用的差額 | 掃 SpecDelta 是否缺 user_value 或 ACC±；缺即拒收 | Original SBL Product Reader | `PRODUCT_SPEC_FUO_MISSING` |
| `P-ACC-04` | NEG | 把三份 SPEC 合併成一段 prose，或三份同文只換標題，仍宣稱已編成 PI | spec_distinctness.py 的 pairwise 門檻與 consumer/NEG 交集檢查 | Original SBL Product Reader | `SPEC_NOT_SOURCE_BOUND` |
| `P-ACC-05` | NEG | 把「Owner 已簽核並發行」寫進 FUO，而本輪沒有任何 Original Reader 讀回 | 對照 original_reader.ack 欄；未觀測即不可寫成已發行 | Original SBL Product Reader | `FUO_NOT_OBSERVABLE` |

所有 firstfail_code 均曾在 W0 r6 文件中出現，位置見 `evidence/firstfail_codes.json`，並由 `tools/verify_spans.py` 重切驗證。

## 10. source_refs（來源綁定）

每一列的 `quoted_text` 存在同名 JSON 的 `source_refs`，且等於該檔 `[byte_start:byte_end)` 的實際 bytes。

| ref | file | sha256（前 12） | byte span | 節錄 |
|---|---|---|---|---|
| `P01-W0-CH01-PROD-TABLE` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 44036–46004 | ### W0 Product SPEC｜受界第一有用結果（P.W0.PROD.001～007，作者端 ID）  \| 類… |
| `P02-W0-CH01-NEG-FUO` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 40357–40474 | **Acceptance NEG／FirstFail**：NEG：將完成三檔當最終產品 Native 閉環；FirstF… |
| `P03-W0-CH11-PM-CONTRACT` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 131557–132102 | **Product SPEC — `W0/PM/ProductSPEC-DRAFT`**：`persona=single… |
| `P04-W0-CH42-SPEC-LEDGER` | `FHS_PIPD-LS-PKG_W0_r6.md` | `69a08e7fae04` | 320914–321225 | \| SPEC_LEDGER \| `OriginalRequirementID+SpecClauseID+SpecKi… |
| `P05-SRC01-PRODUCT-SPEC` | `01_PRODUCT_AUTHORITY_SPINE(4).md` | `e257dfcd01f2` | 10737–12137 | ### Product SPEC｜單人 Owner 交付 FUO  - **Persona/JTBD**：同一 OWNE… |
| `P06-SRC01-R201-CONSUMER` | `01_PRODUCT_AUTHORITY_SPINE(4).md` | `e257dfcd01f2` | 15018–15482 | Product SPEC：單人 OWNER 輸入 goal/source/known_answers，PM 將 Pers… |
| `P07-SRC02-PM-STAGES` | `02_PIPD_LIFECYCLE_AND_TPM(4).md` | `c336d3d9d702` | 4657–5202 | \| PM:T1 \| persona, painledger, jtbd, source_sha256 \| rank… |

## 11. open_questions（未決問題）

- Q-P1：Owner 的 accept/reject 是否需要固定的機器可讀格式，或自由批註即可？（本輪未定，暫以自由批註＋行號為準）
- Q-P2：P01–P07 中哪幾個痛點在本輪真的被觸發，需由 Original Product Reader 指定，而不是由作者挑選
- Q-P3：差額條目的粒度要停在「一條需求」還是「一個可判斷句」，待 W1 原 Intake 回應

## 12. affected_holds（受影具名 HOLD）

| hold | scope | owner | unblock |
|---|---|---|---|
| `H-WP15-P-ORIGINAL-PRODUCT-READER` | 產品語義與痛點對應 | Original SBL Product Reader | 同 Subject/Scope 的原 Reader 讀回或具名 NACK |
| `H-WP15-P-SEMANTIC-OWNER` | OriginalRequirementID/Parent/NEG 語義 | Original Semantic Owner | 原句 span 與否定作用域經原 Reader 核定 |

## 13. original_reader（原始 Reader 與 ACK 狀態）

- reader：Original SBL Product Reader → Original PIPD Intake
- ack：`ORIGINAL_READER_ACK_UNOBSERVED`
- note：本輪只完成 AUTHOR_DESIGN；沒有 ACK 不得 promotion。

## 14. claim_ceiling（宣稱上限）

`AUTHOR_SIDE_SPEC_DRAFT_SOURCE_BOUND`

本 SPEC 不宣稱：`ORIGINAL_ACK`、Owner SourceFreeze、原 PIPD schema `$id`、Host Active 讀回、任何世界效果或 Release。

