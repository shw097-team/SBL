# R5 — 核心大目標（North Star）

order: `SBL-FULL-DOC00-13-R5-20261021`
round: `SBL-R5-20261021-C5`
contract_authority: `SBL_PIPD-LS-PKG_DOC-00..DOC-13`（14/14，source SHA 見 `10_PREFLIGHT/SOURCE_INTAKE.json`）
review_baseline: `SBL_FULL_DOC_CONTRACT_EXTERNAL_ACCEPTANCE_R5_2026-10-21`

## 唯一不可縮減的目標

在 `C:\Projects\Agent_Workspace\SBL` 與 `shw097-team/SBL` 建成符合十四 DOC 的 **SpecBuild Loop 自動產品工程引擎**：
普通使用者不需理解內部工具／供體／代理名稱，即可在合法來源與權限下完成

`人類目標 → G-KNOW 來源核對 → TPM 需求釐清(JTBD/FUO) → Source-bound PI/PD/SPEC/ACC → Kind/Host/Method 選路
→ 架構/ADR/TaskSpec → HGK WorkOrder/ONE ECP/ExecutionBinding/Permit → Hermes 受限 Build
→ 真 Test/SEC/Regression → Evidence-based bounded repair → 不同 Principal 獨立 Challenge
→ Package/Install/Invoke/Uninstall/Rollback → GitHub exact-SHA 證據 → SWOF 合法 Shadow/Native 接續`。

## 反降規宣告（HARD）

1. `v0.1.0-foundation-preview` 是**已完成的有限工程里程碑**，不是本委託終點。
2. `PASS_SCOPED`、ZIP、Docker `SIMULATED`、CI 綠燈、Host 有效載入、SWOF 可接續，**任一項都不得**替代 `SBL_FULL_DOC_CONTRACT_PASS`。
3. `sbl-todo` 單一 fixture、三 SP ZIP 格式合格、五工具本機安裝，都只是子能力證據，不得改寫全案狀態。
4. 441 原件不是 441 個安裝 KPI；`PROHIBITED`（8）不得安裝，`DEFERRED`/`STANDBY`/MethodOnly 依 DOC eligibility，不得為「看起來完成」而擅自提升。
5. `Agent Plugins 1.0 Working Draft`（`DOC-06/NOBJ24/NOBJ-017 = PROHIBITED`）不得升格為產品權威；`CR-PLUGIN-SCHEMA-AUTHORITY` 未經 DOC 授權 Owner 裁定前，三個 ChatGPT 私人 Plugin 不得給 HOST PASS。
6. `PREW3_SHADOW` 必 NoEffect；SWOF W3 需 Native ACK/Permit，SBL 不跨 Repo 寫入。

## 本輪第一優先（阻斷級）

`F-R5-HARNESS-UNINSTALL-TRAVERSAL-001`（`CONFIRMED_DEFECT`，PR #2 head `68c276d`）：
`sbl_harness.uninstall()` 把可變 `MANIFEST.json` 的 `files` 鍵直接當刪除清單，`../outside.txt` 可刪到安裝根之外。
在關閉前 **PR #2 不得合併**。修補必須是窄修（受影程式／測試／證據），不得因此重構六模組或 441 donor。

## 本輪宣稱上限（宣告用）

- 可以宣稱：`SOURCE_VERIFIED`（14/14 DOC + 20/20 KP + 10/10 vol + 2 Skill，SHA 逐一比對）
- 可以宣稱：`PROMPT_COMPILE_PASS`（本機 canonical compiler 四階段真 exit 0）
- 可以宣稱：`F-R5-HARNESS-UNINSTALL-TRAVERSAL-001 CLOSED_LOCALLY`（若 NEG/POS + 雙平台 CI 同 SHA 全綠）
- **不可**宣稱：`SBL_FULL_DOC_CONTRACT_PASS`、`HOST_EFFECTIVE_LOAD`、`NATIVE_EFFECT_AUDITED`、`INDEPENDENT_CASE_PASS`、`OWNER_RELEASE_APPROVED`
- 三 ChatGPT 私人 Plugin：本輪仍 `NOT_HOST_INSTALLED`（無 Host 寫入通道）
- HGK Native：本輪仍 `NOT_GRANTED`（WorkOrder/Permit 需 Native Owner 簽發）
