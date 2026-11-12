# WP-FHS-21｜Acceptance Challenge 15／Original 96 Oracle／H4／SEAM 覆蓋計畫

> **這是一份計畫，不是判決。** 本檔與同目錄的 `tables/`、`tools/` 只證明「覆蓋分母已被逐列、逐位元組綁回原來源，且每一列的 POS／NEG／FirstFail／Consumer 足以讓下游原 Oracle 擁有者直接執行」。本輪沒有任何 oracle 對真實世界執行過，也沒有任何 protected checker 看過這份計畫。
>
> `claim_ceiling = AUTHOR_SIDE_ORACLE_PLAN_SOURCE_BOUND`　`effect_class = SOURCE_READ`　`wp = WP-FHS-21`

## 0. 一句話

WP-FHS-21 的 DonePredicate 是「96 cell／H4／SEAM 的 original oracle plan」。前幾輪只證明 GJ02 runner 能在相同 oracle bytes 上分開 RED 與 GREEN checkout（那是 *oracle discrimination*，不是覆蓋計畫）。本輪交出的是覆蓋計畫本體：**15 條 AC15 異構邊、96 個 original oracle cell、12 條 H4、11 條 SEAM**，合計 134 列，每一列都有自己的 byte span、POS 觀測、NEG 觸發、FirstFail code 與 Consumer。

## 1. 來源釘選

| 項目 | 值 |
|---|---|
| 主來源 | `sources/07_ACCEPTANCE_CHALLENGE(4).md` |
| sha256 | `81a8c2f1cc4629f59829f11f87aebd14cd57f7c4dd0970d672880e90e2899741` |
| 大小 | 211,405 bytes |
| 與 W0 r6 的關係 | CH-30 所載「FHS-BODY-07 真 SHA」= 上述 sha256，**完全相同**（本輪實測，非引用） |
| AC15 出處 | §8.1 `AC-E01`～`AC-E15`（byte 1,699 起） |
| 96 Oracle 出處 | §8.2 `AC-C39-<TestClass>-<OracleType>`（byte 16,129 起） |
| H4／SEAM 出處 | `R2-07-H4-SEAM` 表（byte 201,749～210,204） |
| 摘要來源（僅 cross-check） | `FHS_PIPD-LS-PKG_W0_r6.md` CH-30／CH-31／CH-32 |

W0 r6 的 CH-30／CH-31 只寫「12 TestClass×8 OracleType=96 原型別」與「15 條異構 edge」，**沒有逐列列舉**；全檔掃描 `H4-` 與 `SEAM-` 皆為 0 命中。因此本計畫一律以 FHS-BODY-07 的列舉為準，W0 只當第二來源交叉核對。

## 2. 覆蓋表

### 2.1 96 Original Oracle：12 TestClass × 8 OracleType（無空洞）

| TestClass | DET | STATE | PROP | REF | STAT | SEMJ | HUMAN | COMP | 合計 |
|---|---|---|---|---|---|---|---|---|---|
| `POS` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| `NEG` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| `EDGE` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| `SEC` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| `PERF` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| `PARITY` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| `RECOVERY` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| `UPGRADE` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| `ROLLBACK` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| `UNINSTALL` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| `MUT` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| `JOURNEY` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 8 |
| **合計** | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | **96** |

交叉乘積完整性：96 個 (TestClass, OracleType) 對，理論值 12×8=96，**實測 96**；`__CORRUPT__001`～`__CORRUPT__096` 連續且與 cell 一對一。

### 2.2 TestClass 軸（12 類；每類的前置條件與 FirstFail 不同）

| TestClass | applicability 前置條件（原條款） | FirstFail | cell 數 |
|---|---|---|---|
| `POS` | `feature_invoked and acceptance_predicate_declared` | `MISSING_POS_FUNCTION` | 8 |
| `NEG` | `invalid_input_contract or forbidden_action_declared` | `NEGATIVE_ACCEPTED` | 8 |
| `EDGE` | `input_boundary_or_resource_limit_declared` | `EDGE_BOUND_VIOLATION` | 8 |
| `SEC` | `trust_boundary or secrets or untrusted_source or permission_effect` | `SECURITY_BOUNDARY_BREACH` | 8 |
| `PERF` | `nfr_sli_slo_id and benchmark_dataset_pin and metric_threshold` | `PERF_SLO_EXCEEDED` | 8 |
| `PARITY` | `provider_off_required and provider_off_profile_id and fallback_contract` | `PARITY_PROVIDER_OFF_FAIL` | 8 |
| `RECOVERY` | `effect_or_failure_recovery_required and rollback_ref` | `RECOVERY_STATE_MISMATCH` | 8 |
| `UPGRADE` | `upgrade_path_declared and from_version and to_version` | `UPGRADE_VERSION_MISMATCH` | 8 |
| `ROLLBACK` | `mutating_effect and rollback_ref and preimage_digest` | `ROLLBACK_PREIMAGE_MISSING` | 8 |
| `UNINSTALL` | `installation_workpackage and retention_policy` | `UNINSTALL_RESIDUE` | 8 |
| `MUT` | `testable_predicate and mutation_operator and fixed_seed` | `MUTANT_SURVIVED` | 8 |
| `JOURNEY` | `consumer_entrypoint and user_outcome_defined and supported_kind` | `FUNCTIONAL_CONSUMER_MISSING` | 8 |

### 2.3 OracleType 軸（8 類；每類要求不同的觀測機制）

| OracleType | 判準（criterion） | 必要觀測（expected_observation） | cell 數 |
|---|---|---|---|
| `DETERMINISTIC` | `exact_eq / observed must equal source-bound expected` | expected_value → observed_value | 12 |
| `STATE_READBACK` | `state_transition / pre+post digest from real world` | pre_digest+expected_post_digest → native_world_pre+native_world_post | 12 |
| `PROPERTY` | `all_invariant / seeded generated cases + shrunk counterexample` | invariant+seed → generated_cases+minimal_counterexample | 12 |
| `REFERENCE_OUTPUT` | `pinned_reference_eq / reference SHA pinned` | reference_sha+canonical_output → observed_output | 12 |
| `STATISTICAL` | `bound_confidence / dataset+calibration+threshold` | dataset_sha+calibration_sha+confidence+threshold → sample_metrics | 12 |
| `SEMANTIC_JUDGE` | `calibrated_rubric / model+human calibration+disagreement` | rubric_sha+judge_model_pin+human_calibration → scores+disagreements | 12 |
| `HUMAN` | `rights_veto / real authorized principal, consent and signed decision` | rubric+principal+consent_or_basis → signed_human_decision | 12 |
| `COMPOSITE` | `all_hard_and / ordered hard component receipts` | components+ordering+failure_policy → component_raw_receipts | 12 |

### 2.4 AC15：15 條異構 sender→receiver 邊

| # | ac_id | sender → receiver | payload_kind | FirstFail | 來源 byte span |
|---|---|---|---|---|---|
| 01 | `AC-E01` | OWNER/TPM → TPM Intake | `GoalIntake` | `INTAKE_INVALID` | [2239,2348) L26 |
| 02 | `AC-E02` | SBL TPM → 原PIPD Intake | `ThreeSpecHandoff` | `CANONICAL_WRITER_COLLISION` | [3149,3266) L36 |
| 03 | `AC-E03` | 原Source/Profile Writer → 原PIPD DOC02 Writer | `PICompileRequest` | `PI_SCHEMA_OR_ORACLE_HOLD` | [4054,4181) L46 |
| 04 | `AC-E04` | 原PIPD DOC02 → 原PIPD DOC03 Binder | `PDBindRequest` | `PD_BIND_NACK` | [4976,5092) L56 |
| 05 | `AC-E05` | 原PD Writer → 原DOC05 ECP/DOC07 TQAEP | `ExecutionPlanSplit` | `PLANNED_IS_NOT_ACCEPTED` | [5911,6030) L66 |
| 06 | `AC-E06` | 原PIPD ECP/Admission → 原HGK Issuer | `AdmissionRequest` | `ADMISSION_DENIED` | [6861,6991) L76 |
| 07 | `AC-E07` | 原HGK Admission → 原Hermes SharedSpine | `LeaseCAS` | `LEASE_FENCING_DENY` | [7807,7924) L86 |
| 08 | `AC-E08` | 原Hermes Worker → 原World Effect Receiver | `EffectInvocation` | `EFFECT_REPLAY_DENY` | [8792,8918) L96 |
| 09 | `AC-E09` | 原World Raw Reader → 原Frozen Readset Reader | `RawFreeze` | `RAW_SUBJECT_MISMATCH` | [9723,9833) L106 |
| 10 | `AC-E10` | Frozen Reader → SBL External Challenge | `ChallengeRead` | `FROZEN_SUBJECT_DRIFT` | [10642,10773) L116 |
| 11 | `AC-E11` | SBL Challenge Advisory → 原HGK AO Receiver | `AOInboxSubmit` | `CHECKER_INBOX_PERMISSION_DENY` | [11630,11765) L126 |
| 12 | `AC-E12` | 原AO Receiver ACK → 原Protected Checker | `ProtectedCheckerRun` | `NACK_WRONG_DOMAIN_SCHEMA/SELF_ACCEPTANCE_DENY` | [12672,12843) L136 |
| 13 | `AC-E13` | Protected AO Checker → 原HGK Reducer | `VerdictReduce` | `VERDICT_AUTHORITY_DENY` | [13682,13816) L146 |
| 14 | `AC-E14` | 原Reducer/Native Commander → 原Maker/Authorized Dev | `RepairConeDispatch` | `REPAIR_SCOPE_DENY` | [14676,14811) L156 |
| 15 | `AC-E15` | Closed B1 Evidence → 原W18 NormalMode Owner | `NormalModeQualification` | `NORMAL_MODE_NOT_QUALIFIED` | [15704,15851) L166 |

每條邊的 `payload_kind`／`required_fields`／`output_type`／`effect_class`／`rollback_exit_resume` 各自獨立，依 §8 開頭規則**不得與另一條邊互借**（同一 `SourceRef` 袋子不能代替全部 ABI）。15 條邊的 (sender,receiver) 對兩兩不同。

### 2.5 H4：12 條 gate

| cell_id | gate | oracle_kind | POS 觀測 | NEG 觸發 | FirstFail | Consumer |
|---|---|---|---|---|---|---|
| `H4-01` | Fresh Context | `FRESH_CONTEXT_PROOF` | checker≠maker、無重疊私有歷史、無受審檔寫權 | 看過 Maker private notes 或可寫候選 | `CHECKER_CONTEXT_TAINTED` | Checker Registry |
| `H4-02` | Frozen Binding | `EXACT_HASH_BINDING` | 每個 SourceLocator 可讀且 sha 與 frozen 一致 | source[3] 漂移 | `FROZEN_BINDING_MISMATCH` | Source Owner |
| `H4-03` | A∪B∪C | `ATTACK_UNION_LEDGER` | A={x,y}, B={y,z}, C={w} 得唯一 4 件且都有 disposition | count=3 或藏未測 | `ATTACK_DENOMINATOR_UNDERCOUNT` | Challenge Owner |
| `H4-04` | Anti-Correlation | `INDEPENDENCE_MATRIX` | 高風險有至少一條非 Maker 派生的攻擊與新 context | tests 全取同一 Maker Memo | `CORRELATED_BLIND_SPOT` | Protected Checker |
| `H4-05` | 11 Seams | `SEAM_TEST_LEDGER` | 11 個不同故障面各一正一負且對應不同 FirstFail | 11 個僅改標題、未實測 | `SEAM_UNTESTED` | Security/Native Owners |
| `H4-06` | Next-Wave | `UNDER_ENFORCEMENT_CHECK` | 當前沒消費但 next-wave 仍必拒過期權 | no current reader 竟豁免 | `NEXT_WAVE_UNDERENFORCED` | Policy Owner |
| `H4-07` | Regression Retention | `REGRESSION_MATRIX` | 過往 F17 仍在新 SHA 重測集，除非受權變更 | 靜默刪 prior rejection | `REGRESSION_SILENT_DROP` | Regression Owner |
| `H4-08` | Two-Pass Blind | `ORDER_PROOF` | A immutable frozen 後才開 B，能重算 timestamp | B 先開或封印被改 | `BLIND_REVIEW_INVALID` | Checker Owner |
| `H4-09` | Dual Axis | `TWO_AXIS_RESULT` | candidate=FAIL、process=PASS 時全案仍 HOLD | reviewer 合格便宣稱 candidate PASS | `DUAL_AXIS_COLLAPSE` | AO |
| `H4-10` | Native Receipt | `TRUSTED_BINDING` | sig+scope+raw 同 Subject 有效 | S2 收據重播給 S1 | `NATIVE_RECEIPT_SUBJECT_MISMATCH` | HGK Native Owner |
| `H4-11` | RepairCone | `MINIMAL_REPAIR_CONE` | 只修依賴受影最小集合，重測對應案 | 擴寫無關 Source/Oracle | `REPAIR_SCOPE_OVERREACH` | Maker/Repair Owner |
| `H4-12` | PRE-W3 | `NON_DISPATCH_PROOF` | 沒正式 Gate 時 NOT_DISPATCHED 可驗 | 無 Gate 卻寫 W3 | `PREW3_GATE_BYPASS` | SWOF Owner |

### 2.6 SEAM：11 條不變式

| cell_id | 不變式 | POS 觀測 | NEG 觸發 | FirstFail | 受影 Reader |
|---|---|---|---|---|---|
| `SEAM-01` | `host_loader.trigger_route` | 合法 Skill 真觸發 | 不存在 route 卻稱 Active | `HOST_NOT_EFFECTIVE` | Host Operator |
| `SEAM-02` | `gate.receipt_ref 在 dispatch 前驗` | 有權 Gate 先於 effect | dispatch_at<admit_at | `PRE_GATE_BYPASS` | HGK Issuer/Receiver |
| `SEAM-03` | `schema_version/security attributes 不降` | 不變欄被保留 | v1 threat fields 被刪成 v0 | `SCHEMA_DOWNGRADE_DENIED` | Schema/PIPD Owner |
| `SEAM-04` | `oracle.principal_id != maker` | 有權 Checker 真分離 | Maker 上白名單 | `TQ_SOD` | Oracle/Checker Owners |
| `SEAM-05` | `pi.writer_namespace 唯 PIPD` | 正式 PI Writer 正確 | SBL 假 PI | `SECOND_CANONICAL_WRITER` | PIPD Owner |
| `SEAM-06` | `provider-off` | fallback 有同等 FUO | 缺 delete 仍稱 parity | `PROVIDER_OFF_FUO_LOSS` | Product/Host Owner |
| `SEAM-07` | `每條 route 保持 issuer authority` | 本地與連線 Route 不換權威 | secondary local grant | `WRONG_AUTHORITY_GRANT` | HGK/SWOF Owners |
| `SEAM-08` | `Dispatch 實時 nonce/expiry valid` | 當下可驗效期 | plan 後過期仍動手 | `POST_GATE_PERMISSION_EXPIRED` | HGK Receiver |
| `SEAM-09` | `nonce/op_id at-most-once` | Unknown 先 readback | timeout blind retry | `EFFECT_REPLAY_DENIED` | Hermes/Issuer |
| `SEAM-10` | `repo_context.head_sha 鎖 preimage` | 写前 HEAD 同凍結版 | 中途漂移 | `TOCTOU_REPO_HEAD` | L2 Repo Owner |
| `SEAM-11` | `raw_receipt.subject_sha 同候選` | candidate/raw/manifest exact match | 舊 SHA Raw 冒用 | `RAW_SUBJECT_MISMATCH` | Evidence/Checker Owner |

H4-05 的 POS 要求「11 個不同故障面各一正一負且對應不同 FirstFail」；本表 11 條 SEAM 的 `firstfail_code` 實測有 11 個相異值，結構上滿足該條件（可滿足 ≠ 已測）。

## 3. 可執行計畫陳述

每一列都可以被下游原 Oracle 擁有者**單獨取用並執行**，因為每列都含四件事：

1. **來源定位**：`source_ref.byte_start/byte_end/quoted_text` —— 可用 `xxd`／`dd` 直接切出原文，內容逐位元組相等。
2. **POS 觀測**：`expected_observation`（要看到什麼）＋ `criterion`（用什麼機制判）。
3. **NEG 觸發**：`neg_observation`（要怎麼把 POS 弄壞）＋ `firstfail_code`（壞掉時必須先失敗的代碼）。
4. **Consumer**：誰有權出這個 verdict／ACK（作者端不可代簽）。

單列回放（會即時重讀來源並驗證 span）：

```
python tools/oracle_plan_check.py --cell AC-C39-SEC-HUMAN
python tools/oracle_plan_check.py --cell AC-E11
python tools/oracle_plan_check.py --cell H4-09
python tools/oracle_plan_check.py --cell SEAM-10
```

全表驗證：`python tools/oracle_plan_check.py`（9 類檢查，任一失敗即非零退出）。
機制可執行性示範：`python tools/discriminate.py`（同一列的 POS fixture 必須 PASS、NEG fixture 必須以該列 FirstFail 失敗）。

剩餘一步**不屬於作者端**：把 fixture 換成原 Runner／原 Host 的真 Raw，並由表列 Consumer 簽收。在那之前每一列的狀態都是 `NOT_EXECUTED / RUNNER_UNBOUND`。

## 4. 對帳（COUNT_RECONCILIATION）

| 表 | 來源宣告 | 實測 | delta | 結論 |
|---|---|---|---|---|
| AC15 | 15（CH-31 標題、§8.1 標題） | 15 | +0 | 對帳成功 |
| ORACLE96 | 96（CH-30「12×8=96」、§8.2 標題） | 96 | +0 | 對帳成功（且為完整交叉乘積） |
| H4 | 12（`R2-07-H4-SEAM` 標題「12 H4」） | 12 | +0 | 對帳成功 |
| SEAM | 11（`R2-07-H4-SEAM` 標題「11 SEAM」、H4-05 `seam_case_ids[11]`） | 11 | +0 | 對帳成功 |

四張表都**沒有**需要補齊或裁切的差額：沒有一列是為了湊數而生的，也沒有任何列被丟棄。以下發現不改變分母，但下游必須知道：

| # | 級別 | 發現 |
|---|---|---|
| F1 | INFO | 四個分母皆對帳，delta 全為 0；本輪未做任何 padding，`ORACLE96` 的 96 來自完整 12×8 交叉乘積，非逐列湊數。 |
| F2 | **WARN** | W0 r6 全檔對 `H4-`／`SEAM-` 的列舉命中數為 0。H4／SEAM 的 23 列只由 FHS-BODY-07 `R2-07-H4-SEAM` 表支撐；若下游只讀 W0 章節，會看不到這 23 列。 |
| F3 | INFO | W0 r6 附錄 96 列的 `SourceByteSpan`（如 `16215:18072`）經本輪實測，96/96 都精確起始於 FHS-BODY-07 的 `#### AC-C39-<ID>`，可作為獨立第二來源印證本表的 byte 綁定。 |
| F4 | **WARN** | 同一 OracleType 的 12 個 cell，其 `expected_observation` 文字完全相同（8 個 kind 各只有 1 種寫法）。類別判別力不在機制文字，而在 `applicability` 前置條件、`firstfail_code` 與 `__CORRUPT__NNN`。只比對機制字串的 checker 無法區分 12 個 class —— `tools/discriminate.py` 的 laundering probe 就是把同一 POS fixture 掛到 `AC-C39-SEC-DETERMINISTIC` 上，必須被 scope 拒收。 |
| F5 | INFO | `AC-E12` 的 NEG 帶兩個代碼（`NACK_WRONG_DOMAIN_SCHEMA/SELF_ACCEPTANCE_DENY`）。本表 `firstfail_code` 逐字保留，未擅自拆成單一值；下游 runner 必須接受兩者之一。 |
| F6 | INFO | 本輪未處理 CH-32 的 282（120 Parent／124 Child／38 Node）。僅記錄：workspace 內 `10A_B1_TQAEP_120_124_38(4).md` 列舉的是 27 組 × 4 polarity = 108 個 `TQ-B1-*` case 標題，並未在檔內列舉出 282 項。282 屬 W3/CH-32 分母，不在 WP21 範圍，本輪不對它作任何結論。 |

## 5. 這不是什麼

- **不是 protected-checker verdict。** 沒有任何原 Protected Checker／原 Reader／原 Host 看過這份計畫，`ORIGINAL_READER_ACK_UNOBSERVED`。
- **不是 independent pass。** 作者端（Maker 側）自檢不構成獨立性；`AUTHOR_SIDE` 字樣出現在每個 artifact 的 `claim_ceiling`。
- **沒有任何 oracle 對真實世界跑過。** HUMAN 簽章、Judge 校準、WorldRaw 全部是 `EXPECTED_NOT_OBSERVED`；所有 fixture 皆為 AUTHOR synthetic。
- **不是 PASS 分母。** 15／96／12／11 是**計畫分母**（可執行列的數量），不是通過數。每一列的狀態是 `PLANNED_NOT_RUN`。
- **不是 B1 282 的替代。** CH-32 的 282 有獨立身份，不因本計畫存在而被吸收或認證。

## 6. HOLD 清單

| hold | 內容 | 解除條件 |
|---|---|---|
| `ORACLE_RUNNER_BIND_HOLD` | 96 列的原 Runner／原 Raw schema 未綁 | 原 Case/Oracle Registry Reader 給出 runner_entry + signature + raw_schema |
| `ORIGINAL_READER_ACK_UNOBSERVED` | 原 Domain Reader 未對任何一列簽 ACK | 原 Reader 逐列讀回 binding |
| `H4_SEAM_W0_ABSENCE` | W0 r6 未列舉 H4／SEAM（F2） | W0 章節補列，或下游明確以 FHS-BODY-07 為唯一來源 |
| `EDGE_ACK_AUTHORITY_HOLD` | 15 條邊的 ACK 只能由表列 Consumer 簽發 | 各邊原 Receiver 實際簽發 ACK(payload_hash,consumer_identity,schema_version) |
| `AC_E12_DUAL_CODE` | E12 NEG 雙代碼（F5） | 原 Challenge Owner 指定單一 first_fail 或確認雙值皆合法 |
| `HUMAN_JUDGE_WORLDRAW_NOT_OBSERVED` | HUMAN 簽章、SEMANTIC_JUDGE 校準、WorldRaw 全為 `EXPECTED_NOT_OBSERVED` | 原具權 principal 真簽、原 Judge 真校準、原 Host 真 Raw |
| `NEGATIVE_CONTROL_SCOPE` | `tools/negative_control.py` 只證明 checker 會擋下 5 類注入缺陷，不證明語意正確 | 原 Reader 對本計畫做語意核讀 |

## 7. 重跑指令

```
cd C:\Projects\Agent_Workspace\FHS_W0_R6_20261108\evidence\WP21
python tools/build_tables.py            # 由來源重建 4 張表（含 byte span）
python tools/make_plan.py              # 由表重建本文件
python tools/oracle_plan_check.py      # 9 類檢查，非零退出代表計畫不自洽
python tools/discriminate.py           # POS/NEG fixture 判別示範
python tools/negative_control.py       # 負控制：故意弄壞的副本必須被 checker 擋下
python tools/make_report.py            # 重算 artifacts 的 bytes/sha256
python tools/make_report.py --verify   # 逐項重算 sha256 並比對
```
