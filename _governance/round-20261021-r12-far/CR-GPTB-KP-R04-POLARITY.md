# CR-GPTB-KP-R04-POLARITY（R12 FAR D-15 / O-5 裁決記錄）

| 欄 | 值 |
|---|---|
| CR id | `CR-GPTB-KP-R04-POLARITY`（R6 起登記，原狀態 `OPEN_CR`） |
| 決策狀態 | `DECIDED_ACKNOWLEDGE`（O-5 已關閉：選「承認衝突」，**不**選「改 KP」） |
| CR 執行狀態 | `RECORDED_SOURCE_UNCHANGED`（本 CR 落地；**0** 個 DOC / KP 來源檔被修改） |
| 落地時間 | 2026-10-23（kanban swarm `sbl-r12-far`，task `t_dd0f5282`，run 6） |
| 依何授權 | FAR R12 `O-5` 建議「承認並記 CR」（`FAR_DEVIATION_STUDY.md:60`）＋ 使用者 blanket preauthorization |
| 對應偏差 | FAR R12 **D-15**，等級 `OBS`，量 `XS`，Owner `Knowledge Owner`（`FAR_DEVIATION_STUDY.md:44`） |
| 檔案位置 | `_governance/round-20261021-r12-far/CR-GPTB-KP-R04-POLARITY.md`，branch `evidence/r12-20261021-far` |
| 不是什麼 | **不是** Knowledge Owner 親簽、**不是**外部驗收、**不是** Permit/WO、**不是**任何完成百分比 |

---

## 1. 衝突（可重算觀測）

**corpus**：`知識庫/工程基座/GPTs_GENIEMAKER_開發實作+驗收指揮官_KP_Builder_ReleasePack_v2026.06.03-r2/KnowledgePack/`（`00_`…`19_`，20 檔）

1. 每一檔 `L50` 有一條 `R04` rule row；**modality 欄全部是 `MUST NOT`**。
2. 全 corpus 內含 `| MUST NOT |` 的列 = **20**，而 `R04` 列 = **20** → corpus 中**所有** `MUST NOT` 都落在 R04 家族（R04 之外 0 條），R04 中 `MUST` 0 條。
3. 三欄互相矛盾：
   - modality 欄：`MUST NOT`
   - rule 欄：正向動作（16 條）或自帶否定（4 條）
   - TT/failure 欄：`TT-KPxx-04 when <同一動作> is violated` → 把該動作當作「未做才算失敗」，即該動作是**被要求**的 → 實質語義是 `MUST`
4. 因此**字面極性（`MUST NOT` ＋正向動作）**與**failure 極性（該動作必須做）**直接對撞：照字面執行會做出與 TT 期望相反的行為。

**兩個極端例**（FAR D-15 用這兩條代表，映射 `KP01/KP04（support 層）`）：

- `01_AUTHORITY_BOUNDARY.md:50` — `MUST NOT | Quarantine equal-rank conflicts`：字面 = 不得隔離同 rank 衝突；TT = `when quarantine equal-rank conflicts is violated`（未隔離才是失敗）。
- `04_PRODUCT_BUSINESS_RISK_ACCEPTANCE.md:50` — `MUST NOT | Detect metric overfitting`：字面 = 不得偵測 metric overfitting；TT = `when detect metric overfitting is violated`。
- 安全面最尖銳的一條：`06_BUILDER_CONFIG.md:50` — `MUST NOT | Default Apps/Actions OFF`：字面 = 不得預設關閉 → 變成預設開啟。

## 2. 20 條逐列（全部 `L50`，modality 全 `MUST NOT`）

型別 **A** = rule 欄為正向動作，字面極性反轉；型別 **B** = rule 欄自帶否定（`Do not`/`Never`），字面成雙重否定。A=16、B=4，合計 20。

| ID | 檔案:L | rule 欄（modality = `MUST NOT`） | 型 |
|---|---|---|---|
| `GPTB-KP00-R04` | `00_KNOW_INDEX.md:50` | Do not decide policy directly | B |
| `GPTB-KP01-R04` | `01_AUTHORITY_BOUNDARY.md:50` | Quarantine equal-rank conflicts | A |
| `GPTB-KP02-R04` | `02_OUTPUT_CONTRACT.md:50` | Include missing evidence table | A |
| `GPTB-KP03-R04` | `03_INTAKE_P2E_HANDOFF.md:50` | Convert ambiguity into questions or TT | A |
| `GPTB-KP04-R04` | `04_PRODUCT_BUSINESS_RISK_ACCEPTANCE.md:50` | Detect metric overfitting | A |
| `GPTB-KP05-R04` | `05_SDD_ADR_TASKSPEC.md:50` | Produce reversible PR plan | A |
| `GPTB-KP06-R04` | `06_BUILDER_CONFIG.md:50` | Default Apps/Actions OFF | A |
| `GPTB-KP07-R04` | `07_BUILDER_INSTRUCTIONS.md:50` | Never ask unnecessary clarification when best-effort is possible | B |
| `GPTB-KP08-R04` | `08_KNOWLEDGE_RAG_SOURCE_TO_ANCHOR.md:50` | Never cite unavailable anchors | B |
| `GPTB-KP09-R04` | `09_OROCHI_FACTORY_ORDER.md:50` | Require evidence_return_pack | A |
| `GPTB-KP10-R04` | `10_AGENTIC_SWE_HARNESS.md:50` | Do not assume harness state | B |
| `GPTB-KP11-R04` | `11_EVIDENCE_REQUIREMENT_MATRIX.md:50` | Tie evidence to acceptance criteria | A |
| `GPTB-KP12-R04` | `12_EVAL_REGRESSION_LLM_JUDGE.md:50` | Track regression baseline | A |
| `GPTB-KP13-R04` | `13_SECURITY_PRIVACY_PROMPT_INJECTION.md:50` | Quarantine tool poisoning | A |
| `GPTB-KP14-R04` | `14_APPS_ACTIONS_MCP_ROUTEOUT.md:50` | Require auth/privacy/scope review | A |
| `GPTB-KP15-R04` | `15_MEMORY_STATE_TRACE_REPLAY.md:50` | Checkpoint before risky patch | A |
| `GPTB-KP16-R04` | `16_RELEASE_PACKAGING_CHECKSUM_READBACK.md:50` | Separate package pass from production pass | A |
| `GPTB-KP17-R04` | `17_UX_ONBOARDING_NO_BRAIN_FLOW.md:50` | Map each starter to a core workflow | A |
| `GPTB-KP18-R04` | `18_TT_CR_DRIFT_REGISTER.md:50` | Require close evidence and owner | A |
| `GPTB-KP19-R04` | `19_KP_INDEX_CROSSWALK.md:50` | Identify overlap and orphan files | A |

自指範例：`KP18` 本身是 TT/CR register，其 `R04` 字面讀法是「不得要求 close evidence and owner」，而它的 `R02` 是 `Classify CR separately from defect`、`R08` 是 `Carry open TT into release decision` — 同一檔內正反語義互撞，這正是本 CR 要承認的衝突，不是翻譯口味問題。

## 3. 不是本回合第一次發現（既有記錄）

| 來源 | 記載 |
|---|---|
| R6 `TT_CR_REGISTER.json:70-73`（branch `evidence/r11-20261021-intake`） | id `CR-GPTB-KP-R04-POLARITY`、`status: OPEN_CR`、owner `Knowledge rule owner`、`the 20 R04 MUST NOT polarity conflicts were isolated; no source file was edited` |
| SWOF w2r6 `R6_COMPILER_BUNDLE/SWOF_HGK_ACA_RBWI.md` §4.3「Full 20-KP R04 polarity quarantine」 | `20/20` R04 row 先隔離為 `POLARITY_UNVERIFIED / QUARANTINED`，「本 Runbook 不自行把 `MUST NOT` 翻成 `MUST`」，execution effect = `Excluded from normative execution until higher-authority reconciliation` |
| r11 `40_FINDINGS.md:51`（同 branch） | `CR-GPTB-KP-R04-POLARITY` \| `OPEN（SOURCE_POLARITY）` \| `GPT B Knowledge Owner：只修被批准的文件，不翻轉 DOC` |
| R7 `90_EVIDENCE/OWNER_DECISIONS.md` `OWNER-4` | 預設 = 在擁有 R04 的 KP corpus 記錄極性裁決 + `19_KP_INDEX_CROSSWALK` 加列（**本回合未執行**，理由見 §6） |
| SBL `DOC-12:6738` / `DOC-13:2292`（`_sbl_src_mirror/SBL_PIPD-LS-PKG/`，sha256 `d1e470d8…` / `7cc0c8b1…`） | `LEGACY160:GPTB-KP04-R04` → `MUST NOT → REPAIR_POLARITY → SUPERSEDED`、`LEGACY_RULE_READ_ONLY`、`NEG=LEGACY_POLARITY_OR_HOME_CONFLICT`、`LEGACY_POLARITY_DRIFT` first-fail — 產品契約早已把 KP 極性當 legacy 缺陷處理，且**不讓 KP 反向定義 DOC** |

## 4. 裁決

1. **承認** R04 家族（20/20）存在極性衝突。**不**修改 `SBL_PIPD-LS-PKG_DOC-00..13`（唯一產品契約；FAR §法位，`FAR_DEVIATION_STUDY.md:4`）。
2. **不翻轉 KP**：不把任何 `MUST NOT` 改成 `MUST`，不修改 KP corpus 任何來源檔。理由：(a) 極性判定需要 raw upstream reconciliation，現有證據不支持由 agent 改寫；(b) 承 r11 約束「只修被批准的文件，不翻轉 DOC」；(c) SWOF §4.3 已用同一理由隔離而非改寫。
3. **KP 不得覆寫 DOC**：20 條 R04 維持 `POLARITY_UNVERIFIED / QUARANTINED`，不進 normative execution path；任何依賴 R04 的能力若與 DOC 衝突，一律以 DOC 為準，衝突回到本 CR，不回到底層 KP 欄位。
4. **本 CR 不授予任何效果**：不開 Permit、不開 WO、不改變車道 / pool / control-package pin（`contracts/SBL_C0_C9_CONTRACT-R9.json` 與 `compiled-r9/` 未被本次接觸）；`SBL_FULL_PRODUCT` 仍 `OPEN`。
5. **既答**：R04 極性問題自本 CR 起以「承認、隔離、DOC 為上位」為標準答案，後續回合引用本 CR，不再重開爭論（消除 O-5「若未決：每輪重複爭論」的後果）。

## 5. 影響與成本（誠實揭露）

- 20 條 R04 持續被隔離 → 依賴 R04 的能力在 higher-authority reconciliation 前**拿不到**可引用的 normative 依據。這是本裁決的已知代價，不掩飾。
- 換得：零偽 claim、DOC 不被 legacy 層反向改寫、下游不必各自猜極性、每輪省一次重辯。
- 本 CR 的效力**只到**「已記錄、本機與該 branch 可重算」為止；沒有外部 reviewer 接受，沒有 Owner 親簽。

## 6. 反轉條件與未執行項

- **Superseding CR**：由 GPT B Knowledge Owner 提供 raw upstream reconciliation（上游原始列 + 極性依據 + 指定 canonical corpus copy），即可由新 CR 逐條改判；改判只作用於**被批准的文件**，仍不翻轉 DOC。
- **未執行（明示）**：R7 `OWNER-4` 的「KP corpus 內記錄 + `19_KP_INDEX_CROSSWALK` 加列」**未做**。原因：同一 corpus 存在 **7 份位元組完全相同的副本**（`01_AUTHORITY_BOUNDARY.md` 7/7 sha256 = `4fcbf184144d38918aa4599ee8665c8078f1992f107b6bd5e106a9b6d2e6e6a2`；`04_PRODUCT_BUSINESS_RISK_ACCEPTANCE.md` 7/7 sha256 = `e6d357b7ecbeeb1ff972b7aae6fb7388566a73e0dfe92527f43c29c28ec81f01`），未經 Owner 指定 canonical 之前寫入任何一份都是二選一的靜默決定。該項維持 `OPEN`，交 Knowledge Owner。

## 7. 主張上限

**本機已驗證（可重算）**：§1/§2 的列數、行號、modality、20=A16+B4 分類、兩檔 sha256、DOC-12/DOC-13 的 legacy 極性處理列、R6/r11/SWOF/R7 的既有記載。
**未宣稱**：Owner 親簽、外部接受、DOC 或 KP 的任何修改、任何 native/Host 效果、任何完成百分比。

## 附錄 A — 重算指令

```bash
kp="C:/Projects/Agent_Workspace/知識庫/工程基座/GPTs_GENIEMAKER_開發實作+驗收指揮官_KP_Builder_ReleasePack_v2026.06.03-r2/KnowledgePack"
grep -rn "GPTB-KP[0-9]*-R04" "$kp" | wc -l        # -> 20（且全在 L50）
grep -rh "| MUST NOT |" "$kp" | wc -l              # -> 20（= R04 全集）
grep -rh "| MUST |"  "$kp" | grep -c "R04"         # -> 0
grep -n "GPTB-KP01-R04" "$kp/01_AUTHORITY_BOUNDARY.md"     # :50
grep -n "GPTB-KP04-R04" "$kp/04_PRODUCT_BUSINESS_RISK_ACCEPTANCE.md"  # :50
find 知識庫 _sbl_src_mirror -name 01_AUTHORITY_BOUNDARY.md -print0 \
  | xargs -0 sha256sum | awk '{print $1}' | sort -u | wc -l  # -> 1（7 份同檔）
```
