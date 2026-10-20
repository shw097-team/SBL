# SBL v0.1｜任務執行清單（TS00..TS19）

狀態詞彙：`DONE`（有 raw 收據）／`IN_PROGRESS`／`TODO`／`BLOCKED`（具名 FirstFail）／`DEFERRED`（條件未成立）。
本清單在每個 TS 完成時回填；殘留 `[ ]` 即為缺陷。

| TS | 任務 | 主責面 | 可核對 Exit | 狀態 |
|---|---|---|---|---|
| TS00 | Windows/HGK/Hermes/Fabric Doctor、Capability、權限、目標現況 | HGK + Hermes | fresh machine-state receipt | `[~]` IN_PROGRESS（目標根空、非 git 已測；doctor 待跑） |
| TS01 | 上位來源全讀、AuthorityBinding、缺件/衝突處置 | PLAN | SourceLedger/SourceFreeze 或 HOLD | `[~]` IN_PROGRESS（306 檔 byte ledger + mirror 已建） |
| TS02 | G-KNOW Index/FTS/RAG/Anchor/正反檢索 | PLAN + HGK Knowledge | raw retrieval + anti-hallucination probes | `[ ]` TODO |
| TS03 | 原生 HGK/Fabric/Hermes 工程基座重用與 ABI（含 GSTACK route） | HGK | Reuse BOM / NoSecondPlane proof | `[~]` IN_PROGRESS（spine/board/lane 已重用） |
| TS04 | Product/UX/Source 需求全拆解、ModeGate/Host disposition | PLAN | Requirement→ACC 完整度、orphan=0 | `[ ]` TODO |
| TS05 | C0..C9 Compiler + PIPD 原生 PI/PD/ECP/TQAEP | PLAN + HGK | Compiler PASS + native admission 或 FirstFail | `[ ]` TODO（bundle 已定位） |
| TS06 | 首次建立公開 `shw097-team/SBL`、git init、remote/branch/CI | HGK OPS + Hermes | public repo + visibility/remote readback | `[ ]` TODO |
| TS07 | One Shared Core、六模組 SBLM01..06、Typed DTO/API | EXECUTE | 模組 POS/NEG/SEC 真測試 | `[ ]` TODO |
| TS08 | TPM/Commander/Challenge SP 界面隔離 | EXECUTE | 三 SP manifest/permissions/非自簽 | `[ ]` TODO |
| TS09 | `CLI_TOOL` 第一 FUO（GJ01 安裝/重啟/卸載） | EXECUTE | GJ01 真 CLI receipt | `[ ]` TODO |
| TS10 | `AGENT_SKILL` / `SIMPLE_AGENT` 真 Host Bridge（GJ03） | EXECUTE | effective-load/trigger/nontrigger | `[ ]` TODO |
| TS11 | 六 Donor × 24 slot / 25 methods / 386 tech 准入 | PLAN | selected 逐項 admission；其餘 disposition | `[ ]` TODO |
| TS12 | 受治理 PIPD→HGK WorkOrder/ECP、回讀 | HGK | same-subject permit/effect trace | `[~]` IN_PROGRESS（4 WO 已 admit） |
| TS13 | SBL 39 ModeGate（G00..G12 × 3）STANDALONE/SHADOW/CONNECTED | EXECUTE + PLAN | SHADOW NoEffect；W3 無 ACK 不產生效果 | `[ ]` TODO |
| TS14 | Claim/Evidence/Trace/Checkpoint/Replay/Rollback | PLAN + HGK | 同 SHA raw evidence + 正反案例 | `[ ]` TODO |
| TS15 | CI、供應鏈安全、授權、SBOM、封裝與分支保護 | EXECUTE + HGK | 非零實測測試、Ruleset readback | `[ ]` TODO |
| TS16 | GJ01/GJ02/GJ03 / Host×SP / FUO 全測 | EXECUTE + VERIFY | POS+NEG+EDGE+SEC+Regression | `[ ]` TODO |
| TS17 | HGK Officer 與真正外部獨立 Challenge、缺陷迭代 | VERIFY | distinct principal raw checker/report | `[ ]` TODO |
| TS18 | 每輪公開候選與脫敏 evidence commit 推送 | HGK OPS | remote candidate/evidence exact SHA readback | `[ ]` TODO |
| TS19 | 安裝/卸載/Release readiness、正式交接 | HGK | manifest/checksums/rollback/Human Gate | `[ ]` TODO |

## 目前 FirstFail / TT

- `TT-LANE-REGISTRY-DRIFT-001`：registry `routes[]`（epoch22）與 AGENTS.md/使用說明宣告不一致；PLAN `engine` 宣告 vs dispatcher 實作不一致。→ 逐輪 role mandate 覆蓋，owner 裁決。
- `TT-CODEX-PIN-STALE-001`：`config/hermes-codex-lane.json` codex 路徑失效（`e78bad…` 不存在）。→ 每批派送帶 task-local `--codex-executable`。
- `TT-SRC-LONGPATH-001`：原始 corpus 有 2 檔路徑 267 字元（>MAX_PATH），plain API 不可讀；已建 `_sbl_src_mirror`（306 檔 robocopy，byte 相等）並以短別名（保留 sha256 對照）解決。
- `TT-COMPILER-SKILL-VARIANT-001`：`construction-acceptance-prompt-compiler_SKILL.md` 兩版本（7,534B vs 9,396B）；script 與 schema 三份副本 byte-identical。→ 以 9,396B（HG-KSEOS var worktree + 知識庫/實作相關DOC）為 canonical，待 provenance 裁決。

## 每個 TS 的完成紀律

1. 先有 raw 收據，再把狀態改 `DONE`；狀態升級必須同一回合內有可重算的命令與 exit code。
2. 任何 active TS 無測試即阻斷其 claim（見 03_DETECTION_LIST）。
3. 修補只做受影最小錐；新候選 = 新 SHA，舊 SHA 收據失效。
