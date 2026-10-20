# SBL v0.1｜檢測清單（CHK00..CHK17）

每條檢測必須留下：Case ID、Source Locator、Requirement ID、Oracle Owner、環境、精確命令、
expected/actual、exit code、分母、raw log SHA、Maker/Checker、候選 SHA。
`CHK` 是本輪 Seed ID；正式 `TEST/OR` 只能由 PIPD Native Writer 產出（本輪尚未宣稱）。

| CHK | 最小必測條件 | 必須留下的原始證據 / 拒收條件 | 狀態 |
|---|---|---|---|
| CHK00 | HGK/Fabric/Hermes 真安裝、版本、WorkOrder 與 policy consumption | doctor／binding／policy digest→decision→dispatch trace；僅有 YAML 不合格 | `[~]` spine+board 已驗，doctor 待跑 |
| CHK01 | 來源全量列舉、版本／法位／重複／碰撞、Scope | file hash/locator、AuthorityBinding、Profile/GRP/Oracle FirstFail；欠件不得 SourceFreeze PASS | `[~]` 306 檔 ledger 已建；DOC 內部 TT/CR 待抽 |
| CHK02 | G-KNOW 正向、無答案負向、過期／衝突與 NRTV | 同版 source locator、檢索分母、拒答行為；衍生知識不得升格 Normative | `[ ]` |
| CHK03 | U01–U50／149 children、P01–P07、M00–M15、三 GJ | SourceClause→SPEC→ACC/TEST→Deliverable 雙向 trace、orphan 數 | `[ ]` |
| CHK04 | One Shared Core、三 SP、六模組身分／ABI／拒收 | Maker/Checker 隔離、跨 SP 錯誤輸入 NACK、無第二控制面 | `[ ]` |
| CHK05 | GJ01：clean install→add→list JSON→重啟→卸載 | 唯一 ID/title/status readback、獨立使用者目錄、無殘留、錯誤碼 | `[ ]` |
| CHK06 | GJ02：dirty/stale/範圍受限→Diff→修補→回滾 | RepoContext/HEAD 比對、Red→Green、受影 regression、rollback hash | `[ ]` |
| CHK07 | GJ03：發現／生效載入／觸發／不觸發 | 真 Host invocation、provider-off、拒權效果、fallback、卸載殘留 | `[ ]` |
| CHK08 | 三模式與 SBL 39 ModeGate 的適用與權限 | SHADOW 真 NoEffect；W3 無 Native ACK/Permit 不得產生世界效果 | `[ ]` |
| CHK09 | 被選中的 Donor/Slot/method/Identity 決策 | 每 active cell 的 source/current disposition、License、安全、載入、回退 | `[ ]` |
| CHK10 | PIPD PI/PD、ONE ECP、WorkOrder/ExecutionBinding | 版本/主體/Permit/Write scope 一致；過期、外來、跨根及重放被拒 | `[~]` 4 WO 已 admit；ECP 待建 |
| CHK11 | Secrets/PII、Token、path traversal/junction、prompt injection | 掃描命令、退出碼、負例、零外洩與無憑證殘留；不得 log Token | `[ ]` |
| CHK12 | CI/Static/Unit/Integration/Host/Contract/SBOM/License | 命令、分母非零、pass/fail/error、Windows Host raw trace；綠燈非真載入 | `[ ]` |
| CHK13 | Evidence/Claim/Checkpoint/重播及同一受審候選 | SHA、evidence manifest、原始 log、撤銷舊收據、可復原指標 | `[ ]` |
| CHK14 | 公開 `shw097-team/SBL` 建立及每輪 push | visibility=public、origin、remote SHA readback、PR/branch、去敏掃描 | `[ ]` |
| CHK15 | 獨立 Officer + clean-room External Challenge | Principal 隔離、唯讀候選、Frozen Subject/Evidence、POS/NEG/SEC/反證 | `[ ]` |
| CHK16 | Gate Calibration Failure 防禦 | objective/risk/strictness、holdout、FP/FN、judge counterbalance、HITL | `[ ]` |
| CHK17 | 安裝/卸載/回滾/交付物/Release 差異 | manifest/checksums/readback、真功能、rollback、Human release permit | `[ ]` |

## 反證組（必須主動測，任一成立即不得宣稱 PASS）

- 以備份取代 source；以 50 parent 對 149 children 代驗。
- CI 0 個 test 卻 PASS；輸出 `{"ok": true}` 假成功。
- 未有效載入卻宣稱 installed；Maker 自造 Checker。
- 接受外來 SHA／過期 permit；Public GitHub 漏出私人知識庫。
- 為得到 PASS 自改門檻／oracle／測試。

## 檢測方法

從正向、負向、邊界、安全、對抗、復原六類建立 Native TQAEP 候選；高風險功能以 deterministic Oracle 為主，
不接受 LLM judge 單方自證；所有通過只在其環境、功能、候選與 Claim Ceiling 內有效。
