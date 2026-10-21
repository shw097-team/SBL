# R5 — 檢測清單（CHK00–CHK25）

| ID | Oracle / 正負邊界 | 本輪狀態 | 證據 |
|---|---|---|---|
| CHK00 | HGK/Hermes/Fabric/PIPD/Host 真 doctor 與版本；policy consumption | [x] | `10_PREFLIGHT/ENV_SNAPSHOT.json` |
| CHK01 | DOC 14/14、KP 20/20、vol 10/10、Skill 2/2、R5 SHA/locator | [x] | `10_PREFLIGHT/SOURCE_INTAKE.json` |
| CHK02 | C0–C9 四階段真 exit 0；activation/acceptance 0 orphan | [x] | `30_CONTRACT/COMPILER_RECEIPT.json` |
| CHK03 | G-KNOW 正向定位／缺答拒答／CJK／drift／injection | [ ] | OPEN（`TT-GKNOW-CJK-01`） |
| CHK04 | FullProduct 不被 `PASS_SCOPED` 吞掉；149 orphan=0 | [~] | 本輪只鎖「不得降規」規則，未做 149 逐條 |
| **CHK05** | **uninstall traversal：`../`、絕對、symlink/junction、malformed manifest、normalize；sentinel bytes 不變；合法往返 OK；雙 OS 同 SHA** | [x] | `20_TS05/NEGATIVE_MATRIX.json` |
| CHK06 | wheel/sdist 真解包＋package-data 三 manifests；clean venv `load_manifest` | [~] | wheel 內容斷言跑；clean venv 安裝待 TS06 完整 |
| CHK07–CHK14 | TPM/SPEC/Kind/Build/Brownfield/PIPD/Test/Repair | [ ] | OPEN_ACTIVE |
| CHK15 | `CR-PLUGIN-SCHEMA-AUTHORITY` 未裁決前拒 HOST PASS | [x] | 本輪仍 `OPEN_CR`，三 Plugin 維持 `NOT_HOST_INSTALLED` |
| CHK16–CHK18 | 三 ChatGPT 私人 Plugin 真 UAT | [ ] | `EVIDENCE_GAP`（無 Host 通道） |
| CHK19 | HGK Harness 真 Hermes/HGK Native（WorkOrder/ECP/Permit/effect） | [~] | adapter 可安裝；Native `NOT_GRANTED`；卸載邊界已修 |
| CHK20 | Stack install/doctor/selftest/status/upgrade/rollback/uninstall | [~] | R4 `LOCAL_STANDALONE_INSTALL` 未重測 |
| CHK21 | GJ01–03 使用者 FUO | [ ] | OPEN_ACTIVE |
| CHK22 | 441 逐 ID disposition；PROHIBITED 真未安裝 | [~] | 本輪複核 PROHIBITED 未被安裝（無新安裝） |
| CHK23 | 38 Surface 逐 C-ID | [ ] | R5 §7 基線，未新增 |
| CHK24 | Maker/Checker 分權、holdout、raw logs、獨立 Challenge | [~] | 本輪 VERIFY 車道 `gpt-6.1-sol` 可用；正式 checker 收據待跑 |
| CHK25 | token 未外洩、secret/PII scan、candidate vs evidence SHA 分離、readback | [x] | `90_EVIDENCE/SECRET_SCAN.json` + `REMOTE_READBACK.json` |

## 未關閉阻斷（本輪結束時仍成立）

1. `SBL_FULL_DOC_CONTRACT_PASS`：**未取得**（149/441/38 未逐條閉合，Native/Host 證據缺口）。
2. 三 ChatGPT 私人 Plugin：`NOT_HOST_INSTALLED`（0/3 Host-issued ID）。
3. HGK Native effect：`NOT_GRANTED`（WorkOrder/Permit 需 Native Owner）。
4. `CR-PLUGIN-SCHEMA-AUTHORITY`：`OPEN_CR`。
5. SWOF W3：`NOT_GRANTED`（W1/W2 shadow only）。
6. 獨立 checkers' `INDEPENDENT_CASE_PASS`：未取得（本輪最多 `PARTIAL_CHALLENGE`）。

## Resume pointer

`next_unclosed_requirement_ids = [TS04, TS07, TS08, TS09, TS13, TS14, TS16, TS17, TS20, TS22, TS25]`
`smallest_workorder = TS07（149 Child trace 骨架：先建 ChildOutcome 空表 + source locator，不假造 PASS）`
`resume_command = python tools/run_gates.py && python scripts/prompt_contract_compiler.py lint contracts/SBL_C0_C9_CONTRACT-R5.json`
