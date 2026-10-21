# R4 任務清單（TS00–TS19）

狀態語意：`DONE`＝本輪有原始收據；`ACTIVE`＝本輪施工中；`DEFERRED`＝依 R4 §4 明示不阻斷、記理由；`NOT_IMPLEMENTED`＝具名缺口 + TT。
**不得**以 `DONE` 取代驗收；`DONE` 只代表本切片產物存在且可重跑。

| Task | 目標 | 狀態 | 收據 / 理由 |
|---|---|---|---|
| TS00 | Fresh doctor：HGK/Hermes/Fabric/SBL/SWOF 精確 SHA、Registry、讀權限 | DONE | `10_PREFLIGHT_READBACK.json`；8 個 R4 SHA 全數相符 |
| TS01 | 14 DOC / 20 KP / 10 vols / 2 Skills 的 SourceLedger | PARTIAL | `11_SOURCE_LEDGER.json`；DOC 14/14 以 R4 報告 digest 對 SBL `SOURCE_VERIFY.json`，KP/vols 本機無原文 → `NON_AUTHORITATIVE_LOCATOR` |
| TS02 | G-KNOW 真 Anchor / 假 DOC / CJK 拒絕 | DEFERRED | R4 §4 非阻斷；CJK 分詞與長路徑限制沿用 R3 `GKNOW-CJK` TT |
| TS03 | HGK Native Lane / Hermes isolation / Fabric F0 消費 | PARTIAL | lane 埠實測（10101/10102 = 200，其餘 000）；F0 policy 消費以 SBL 側宣告為限 |
| TS04 | DOC-01 50/149、8 ProductKind、38 surfaces 差異追溯 | DEFERRED | R4 `G-R4-FULL-DESIGN` = NON_BLOCKING_OBSERVATION；沿用 R3 三本 ledger，不重算 |
| TS05 | C0–C9 JSON Contract + 官方 compiler（lint/activation/acceptance/compile） | DONE | `05_C0_C9_CONTRACT_RECEIPT.json` |
| TS06 | SBL main/release 讀回；c3 只開新 candidate/evidence 分支 | DONE | PR #1 merged、`bedc119`、release tag 已回讀 |
| TS07 | One Shared Core M01..06 + Stack 選中 Host 路徑 | ACTIVE | `sbl_stack/`（install/doctor/status/uninstall + selftest） |
| TS08 | **修 `F-R4-C3-PLUGIN-SCHEMA-001`**；3 包 strict-schema-valid、重算 hash | ACTIVE | `sbl_sp/plugins/`；三包 digest 見 `40_SP_PACKAGES/SP_SET.json` |
| TS09 | 三 SP 私人 Host create/install/3 IDs/@invoke/POS/NEG/uninstall | PARTIAL | Docker 沙盒真跑；ChatGPT 私人 plugin = `HOST_PENDING`（需 owner 帳號動作） |
| TS10 | 五工具獨立 Harness packaging/installer/launch/op/uninstall | ACTIVE | `TOOLS5_HARNESS_MATRIX.json` 五行 |
| TS11 | 441 供體 source+execution disposition；選中者 license/pin/test | DEFERRED | R4 明示「非 441 種軟體全裝 KPI」；沿用 R3 `42_DONOR_LEDGER.json` |
| TS12 | PIPD 八 Skills 真 Writer / PI→PD→ECP/TQAEP | PARTIAL | 官方 writer bundle 在 `PIPD/skills/`，本輪未取得原生執行收據 → `REFERENCE_BOUND` |
| TS13 | 三模式 39 gate cells 適用性、W3 effect deny | PARTIAL | ModeGate POS/NEG 由既有測試覆蓋；39 格為設計矩陣非 39 次 host 驗收 |
| TS14 | Trace/ClaimCeiling/Checkpoint/Rollback | DONE | `ROUND_MANIFEST.json`（git blob digest）、`CORRECTIONS` 不覆寫舊凍結證據 |
| TS15 | Windows/Ubuntu CI、clean install/uninstall、package digest | ACTIVE | Docker 沙盒 receipt + 新 head CI |
| TS16 | GJ01/02/03 + J4/J5/J6 功能／安全／過載／negative | PARTIAL | J1（sbl-todo FUO）沿用 R3；J4/J5 本輪 Docker 實跑；J6 = SWOF shadow |
| TS17 | Maker/Checker 分離、Gate Calibration、TT/CR | PARTIAL | 本輪無獨立 checker 車道（ws 426 已證死）→ 不宣稱 `INDEPENDENT_CASE_PASS` |
| TS18 | 每次授權 patch 的 secret-safe push + 遠端 SHA/CI readback | ACTIVE | `80_REMOTE_READBACK.json` |
| TS19 | Foundation seal、c3 merge ceiling、五工具 pack、SWOF W1/W2 handoff | ACTIVE | `95_SWOF_W2_SHADOW_HANDOFF.json` |

## 具名缺口（TT）

| ID | 缺口 | 歸屬 |
|---|---|---|
| `TT-R4-HOST-CHATGPT` | ChatGPT 私人 plugin 三 ID 建立/安裝需 owner 帳號動作 | owner |
| `TT-R4-HGK-UPGRADE` | HGK 原生 root 升級需 HGK Owner WorkOrder（SBL 只交付 adapter + pin） | HGK owner |
| `TT-R4-PIPD-WRITER` | PIPD 8 P4 skill 的原生 PI/PD/ECP/TQAEP 執行收據 | PIPD owner |
| `TT-R4-CHECKER` | `openai-codex` ws 426 使 VERIFY 車道不可用 | HGK lane owner |
| `CR-R4-PLUGIN-SCHEMA-AUTHORITY` | DOC-06 `NOBJ24/NOBJ-017` 記 Agent Plugins 1.0 WD 為 `PROHIBITED`，與 Host 今日要求 portable `$schema` 的張力 | owner / DOC owner |
