# R3 Task List (任務執行清單) — TS00..TS19 沿用，不另建平行表

狀態詞彙：`DONE`（本輪有真收據）／`PARTIAL`（有受影成果未完成）／`HOST_PENDING`（等 Host/人類）／
`NOT_RUN`／`DEFERRED`（本輪 scope 外，具原因）。空格不得標 DONE。

| TS | 執行目的 | 本輪 state | 收據 locator | first_fail / resume |
|---|---|---|---|---|
| TS00 | Fresh HGK/Hermes/Fabric doctor、Repo/權限現況 | DONE | `10_BASELINE_PREFLIGHT.json` | — |
| TS01 | SourceLedger / 14 DOC 權威 / C0 | PARTIAL | `20_SOURCE_LEDGER.json`（public manifest 自檢；私有原文不在本機重算） | 私有 corpus 未掛載 → 需 mirror 才能 full verify |
| TS02 | G-KNOW / RAG / NRTV / CJK / coverage boundary | PARTIAL | `M4LITE` AC-M4-01..03 raw；`F13-06` TT | CJK 分詞與 61 長路徑為已知限制 |
| TS03 | HGK/Fabric/Hermes/八 PIPD Skill/ABI 重用 | PARTIAL | `30_LANE_AND_REUSE.md` | PIPD 官方 Writer 未在本機執行 |
| TS04 | 50/149 + 8 ProductKind + 38 surface 受影規格 | PARTIAL | `40_REQUIREMENT_LEDGER.json`（50/149 逐 ID）；`41_SURFACE_MATRIX.json`（38） | 以 disposition 計，非全部 PROVEN |
| TS05 | C0–C9 canonical Compiler / PI-PD / TQAEP | DONE | `12_COMPILER_RESULT.json` | — |
| TS06 | Repo Context、候選/證據 branch、PR、Owner merge | PARTIAL | `70_A_PR_PACKET.md` | PR 需人類簽名後開；merge 需 Owner |
| TS07 | Shared Core 六模組 / ProductKind 擴展 | DONE（現況引用） | `85_EVIDENCE_RETURN_v13.json` §local | 擴展為 C，非本輪 |
| TS08 | 三 SP 各自 ZIP / identity / Cloud install | HOST_PENDING | `50_SP_PACKAGES/` + `51_HOST_INSTALL_REQUEST.md` | ChatGPT workspace 權限 |
| TS09 | GJ01 clean CLI / FUO | DONE | `60_R2_PREVIEW/` clean-install FUO | — |
| TS10 | GJ03 真 Skill + SIMPLE_AGENT Host 橋 | HOST_PENDING | `51_HOST_INSTALL_REQUEST.md` | Host loader 未取得 |
| TS11 | 441 donor/slot/method/identity 逐項 disposition | DONE | `42_DONOR_LEDGER.json`（441，含 2 條 stale 更新） | 安裝 ≠ disposition；無硬裝 |
| TS12 | 真 PIPD→HGK WorkOrder/OPS+DEV ECP/ONE Permit | NOT_RUN | `30_LANE_AND_REUSE.md` §PIPD | 需 HGK Native permit |
| TS13 | 3 Mode × 13 Gate cells / ACK / NO_EFFECT | PARTIAL | AC-M4-04/05；`sbl_core/modes.py` | 39 cells 未逐一 Host 實測 |
| TS14 | Claim/Evidence/Trace/Checkpoint/Replay/Rollback | DONE | `90_EVIDENCE_RETURN_R3.json` | — |
| TS15 | CI / SEC / SBOM / LICENSE / R2 wheel+sdist | DONE | `60_R2_PREVIEW/*`、CI run | SBOM 未產出（無 syft） |
| TS16 | GJ01/02/03 + SP/Host、負例、安全與回歸 | PARTIAL | 148 local / 145+1 CI | Host 面 HOST_PENDING |
| TS17 | M4-LITE + 逐批獨立 Challenge | PARTIAL | `M4LITE/M4LITE_RAW.json`；`84_HUMAN_REVIEW_PACK.md` | **人類簽名未取得** |
| TS18 | 每次許可 patch 的 candidate/evidence push 與 readback | DONE | `80_REMOTE_READBACK.json` | — |
| TS19 | R2 Preview / 完整產品交接 / Installer / SWOF W2 | PARTIAL | `60_R2_PREVIEW/`、`95_SWOF_W2_HANDOFF.md` | Release Gate 與 W3 皆未授權 |

## 本輪三個必閉項目

- [x] A：六性質 harness + 12 筆 POS/NEG raw receipts（maker-side 程序執行，非簽名）
- [x] B：`bedc119` wheel + sdist + clean-install FUO + uninstall + digest readback
- [x] C：三 SP ZIP + 3 份 HOST_INSTALL_REQUEST + 441/149/38 三本 ledger
- [ ] A 終態：人類 `HUMAN_PROCEDURAL_ACCEPTANCE` 簽名（唯一阻斷，Maker 不得代簽）
- [ ] B 終態：Owner Release/Tag 授權
- [ ] C 終態：ChatGPT workspace 實裝、HGK Harness 原生安裝、PIPD Native Writer 執行
