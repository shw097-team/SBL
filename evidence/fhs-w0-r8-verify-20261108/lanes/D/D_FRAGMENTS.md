# D_FRAGMENTS｜W0 r6 列舉缺口（D-02／D-03／D-04）可插入片段

> **性質**：插入用片段。每一列的文字都是原來源 bytes 的逐字切片，`座標` 欄為該來源檔的絕對 byte offset；
> 全部片段已回切比對（quote 的 UTF-8 bytes == 來源 `bytes[start:end]`），逐列結果見 `D_ENUMERATIONS.json` 的 `slice_verified`。
> **ClaimCeiling**：`SOURCE_READ_ONLY`／`LOCAL_DRAFT_WRITE`；本檔不主張 `ORIGINAL_ACK`，不主張 `NATIVE_WORLDRAW`，不主張任何來源章節已被原 Owner 追認。
> **用法**：每節可直接貼進對應 CH；貼上後該 CH 的「只宣告數字」改為「宣告數字＋具名列舉」。

## 來源綁定（本檔所有座標的基準）

| 短名 | 檔名 | bytes | sha256 |
|---|---|---:|---|
| `02` | `02_PIPD_LIFECYCLE_AND_TPM(4).md` | 73,292 | `c336d3d9d702834e84bc2e45037e21e6ac56fb99c7abcb3adea372d901824ea2` |
| `07` | `07_ACCEPTANCE_CHALLENGE(4).md` | 211,405 | `81a8c2f1cc4629f59829f11f87aebd14cd57f7c4dd0970d672880e90e2899741` |
| `08` | `08_TECHNOLOGY_DEFAULT_HOTSWAP(4).md` | 1,128,554 | `1df04680319796aa253256c5da9c8adea47a5601abfe17086f3598d4f0470f8d` |

## D-02｜CH-11：TPM 18 Stage 具名列舉

> **來源**：`02_PIPD_LIFECYCLE_AND_TPM(4).md`；sha256 `c336d3d9d702834e84bc2e45037e21e6ac56fb99c7abcb3adea372d901824ea2`
> **區段**：§2 `STATIC-v1 三角色 18 Stage：按插件原 Clause Reader 的實際契約` 表（L36–L55；byte 4371–9518）。
> 同檔 `R2-02-STAGE：K0–K3 與原18-stage投影`（L451–L470）為同 18 列之鏡像投影，id 與順序逐列相同（已比對）。
> **插入位置**：`CH-11` 主體 `**W0 主責：三 SPEC 與 18 Stage。**` 段之後、`### 受影 r4 設計卡` 之前。
> **18 列＝PM 6＋SE 6＋TPgM 6**；此為 Stage 契約 draft，不是 StateEnum，也不代表該階段已執行。

| # | Stage | 名稱（操作，逐字） | 用途（一子句：輸出／Consumer） | Guard／FirstFail／退出 | 座標 |
|--:|---|---|---|---|---|
| 1 | `PM:T0` | segregate facts from user guesses; detect unanswered JTBD | ProductKnownState@1(goal_sha,missing_questions) / ProductOwner/PIPD Reader | GoalCard+known_answer_refs; source_sha present；KNOWN_ANSWER_REASK；ASK_NEW_ONLY；`T1` | 02:L38｜4371–4656 |
| 2 | `PM:T1` | rank questions by user information gain | QuestionPriority@1(qid,impact,source_ref) / ProductOwner/PIPD Reader | Persona+PainLedger+JTBD; source_sha present；JTBD_UNBOUND；FUO_PATH_BOUND；`T2` | 02:L39｜4657–4909 |
| 3 | `PM:T2` | define observable CLI/add,list,delete or brownfield user result | ProductSuccess@1(FUO,exit_code,negative_cases) / ProductOwner/PIPD Reader | FUO+UserOutcome+variants; source_sha present；FUO_UNTESTABLE；USER_VALUE_MEASURABLE；`T3` | 02:L40｜4910–5202 |
| 4 | `PM:T3` | compile ProductSPEC draft and acceptance cues | ProductSPECDraft@1(journey_id,kind,acceptance_sha) / ProductOwner/PIPD Reader | ProductSuccess+PrimaryKind; source_sha present；KIND_ID_DRIFT；OWNER_REVIEW_REQUESTED；`T4` | 02:L41｜5203–5484 |
| 5 | `PM:T4` | issue user-facing POS/NEG proposal, not Native verdict | ProductAcceptanceProposal@1(pos,neg,raw_expect) / ProductOwner/PIPD Reader | ProductSPECDraft+ACC_NEG; source_sha present；ACC_NOT_BOUND；PIPD_ACC_REF_AVAILABLE；`T5` | 02:L42｜5485–5768 |
| 6 | `PM:T5` | compare observable use vs claimed outcome; create repair request | ProductReviewRequest@1(gap,affected_journeys) / ProductOwner/PIPD Reader | FUO_raw_refs+feedback; source_sha present；FUO_RAW_MISSING；REVIEW_WITH_RAW_OR_HOLD；`T5 final review or affected T3/T4 rework` | 02:L43｜5769–6095 |
| 7 | `SE:T0` | enumerate source/destination trust seams | SystemReadset@1(owners,sha,scope) / ArchitectureOwner/HostReader | RepoBoundaries+SourceIndex; source_sha present；SYSTEM_SOURCE_GAP；SOURCE_BOUND；`T1` | 02:L44｜6096–6353 |
| 8 | `SE:T1` | assign every seam to exactly one writer | OwnershipSeamMap@1(writer,reader,forbidden_effect) / ArchitectureOwner/HostReader | SystemReadset+ADRRefs; source_sha present；SEAM_OWNER_CONFLICT；ONE_WRITER_PER_SEAM；`T2` | 02:L45｜6354–6626 |
| 9 | `SE:T2` | trade off typed ABI and provider-off reliability | ADRSet@1(option,tradeoff,security_guard) / ArchitectureOwner/HostReader | RiskInventory+HostCaps; source_sha present；ARCHITECTURE_RISK_OPEN；ADR_OWNER_REVIEW；`T3` | 02:L46｜6627–6900 |
| 10 | `SE:T3` | bind schemas and compatibility version | ArchitectureSPEC@1(abi,compat,host_matrix) / ArchitectureOwner/HostReader | ADRSet+C4+ComponentCards; source_sha present；ABI_SCHEMA_MISMATCH；SCHEMA_READER_BOUND；`T4` | 02:L47｜6901–7171 |
| 11 | `SE:T4` | test scope/token/provider-off/thin adapter semantics | ArchitectureNEGRequest@1(neg,oracle_source) / ArchitectureOwner/HostReader | ArchitectureSPEC+BoundaryNEG; source_sha present；PERMISSION_NEG_MISSING；NEG_PROPOSAL_READY；`T5` | 02:L48｜7172–7466 |
| 12 | `SE:T5` | re-evaluate actual host ABI and raw results | ArchitectureReview@1(findings,repair_cone) / ArchitectureOwner/HostReader | NativeRawRefs+IntegrationRisks; source_sha present；HOST_RAW_MISSING；RAW_OR_HOLD；`T5 final review or affected T3/T4 rework` | 02:L49｜7467–7780 |
| 13 | `TPgM:T0` | identify budget milestones without claiming approval | ProgramIntent@1(milestone,owner,risk) / ProgramOwner/NativeRouter | OwnerRoster+CostTime; source_sha present；MILESTONE_OWNER_MISSING；OWNER_ROSTER_COMPLETE；`T1` | 02:L50｜7781–8056 |
| 14 | `TPgM:T1` | record sequencing constraints and blocking decisions | SchedulingAssumptions@1(edges,confidence) / ProgramOwner/NativeRouter | UnknownDependencies+ResourceCaps; source_sha present；UNBOUNDED_WORK；DEPENDENCY_DISCLOSED；`T2` | 02:L51｜8057–8350 |
| 15 | `TPgM:T2` | toposort bounded DAG and cycle check | ProgramDAG@1(topo,locks,no_fit) / ProgramOwner/NativeRouter | OwnerGates+DependencyEdges; source_sha present；DAG_CYCLE；ACYCLIC_AND_SCOPED；`T3` | 02:L52｜8351–8599 |
| 16 | `TPgM:T3` | package work with traceable scope and approver | ProgramSPEC@1(wp,effort,owner,stop) / ProgramOwner/NativeRouter | ProgramDAG+ProductSPEC+ArchitectureSPEC; source_sha present；WP_SCOPE_UNKNOWN；WORK_PACKAGE_OWNER_REVIEW；`T4` | 02:L53｜8600–8903 |
| 17 | `TPgM:T4` | route to correct Native ECP/Oracle Owner | HandoffReferral@1(expected_grants,oracle_conflict) / ProgramOwner/NativeRouter | PI_PD_refs+VerifierReferral; source_sha present；CR_ORACLE_001；NATIVE_REF_NOT_SYNTHESIZED；`T5` | 02:L54｜8904–9189 |
| 18 | `TPgM:T5` | review schedule with evidence status; refreeze affected only | ProgramReview@1(blocked_waves,replan_cone) / ProgramOwner/NativeRouter | MilestoneRaw+IssueLedger; source_sha present；STALE_MILESTONE_EVIDENCE；REVIEW_OR_HOLD；`T5 final review or affected T3/T4 rework` | 02:L55｜9190–9518 |

**回切結果**：18/18 列 slice 與來源 bytes 逐位元相同；`PM:T0…TPgM:T5` 無缺號、無重複。

## D-03｜H4（12）與 SEAM（11）具名列舉

> **來源**：`07_ACCEPTANCE_CHALLENGE(4).md`；sha256 `81a8c2f1cc4629f59829f11f87aebd14cd57f7c4dd0970d672880e90e2899741`
> **區段**：`## R2-07-H4-SEAM：12 H4與11 SEAM保持原Oracle`（L1336–L1362；byte 201871–210202）。
> **插入位置**：`CH-42` 之後新增 `CH-42A`（或併入 CH-42 的 Oracle 族說明）：H4 為 12 列驗收 Case，SEAM 為 11 列故障面；兩者與 96 Oracle 是不同的分母，不可互抵。
> **註**：下表 `POS／NEG／退出` 欄省略了每列完全相同的尾句（H4：`；FirstFail 受影 H4 停止，原 Checker Owner 證明退出／重測，不影響無關案。`；SEAM：`；FirstFail 停受影 Receiver；原 Owner 更正/驗原 Raw 後才可重入。`）。

### D-03a H4（宣告 12；實測 12）

| ID | 標題 | 斷言什麼（原業務契約，逐字） | POS／NEG／退出（尾句省略） | 座標 |
|---|---|---|---|---|
| `H4-01` | Fresh Context | 原 checker_principal, loaded_history_ids, write_cap → fresh-context-proof；Consumer/Owner Checker Registry；換真獨立 context／re-run；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS checker≠maker、無重疊私有歷史、無受審檔寫權；NEG 看過 Maker private notes 或可寫候選 → CHECKER_CONTEXT_TAINTED | 07:L1340｜201871–202363 |
| `H4-02` | Frozen Binding | 原 subject sha, source manifest, raw refs → exact-hash-binding；Consumer/Owner Source Owner；重凍結後重測；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 每個 SourceLocator 可讀且 sha 與 frozen 一致；NEG source[3] 漂移 → FROZEN_BINDING_MISMATCH | 07:L1341｜202364–202797 |
| `H4-03` | A∪B∪C | 原 stable A/B/C IDs, waiver → attack union ledger；Consumer/Owner Challenge Owner；補原攻擊而非改分母；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS A={x,y}, B={y,z}, C={w} 得唯一 4 件且都有 disposition；NEG count=3 或藏未測 → ATTACK_DENOMINATOR_UNDERCOUNT | 07:L1342｜202798–203243 |
| `H4-04` | Anti-Correlation | 原 high-risk flags, challenge origin/principal → independence matrix；Consumer/Owner Protected Checker；獨立再生案例；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 高風險有至少一條非 Maker 派生的攻擊與新 context；NEG tests 全取同一 Maker Memo → CORRELATED_BLIND_SPOT | 07:L1343｜203244–203712 |
| `H4-05` | 11 Seams | 原 seam_case_ids[11]，tamper fields → SeamTestLedger；Consumer/Owner Security/Native Owners；逐 Seam 真測；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 11 個不同故障面各一正一負且對應不同 FirstFail；NEG 11 個僅改標題、未實測 → SEAM_UNTESTED | 07:L1344｜203713–204151 |
| `H4-06` | Next-Wave | 原 current+next-wave consumer, policy → under-enforcement check；Consumer/Owner Policy Owner；保持拒收；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 當前沒消費但 next-wave 仍必拒過期權；NEG no current reader 竟豁免 → NEXT_WAVE_UNDERENFORCED | 07:L1345｜204152–204581 |
| `H4-07` | Regression Retention | 原 previous F IDs, new SHA, change cone → regression matrix；Consumer/Owner Regression Owner；舊判決保留；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 過往 F17 仍在新 SHA 重測集，除非受權變更；NEG 靜默刪 prior rejection → REGRESSION_SILENT_DROP | 07:L1346｜204582–205030 |
| `H4-08` | Two-Pass Blind | 原 PassA seal time/SHA, PassB open time → order proof；Consumer/Owner Checker Owner；新 Session 重新盲審；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS A immutable frozen 後才開 B，能重算 timestamp；NEG B 先開或封印被改 → BLIND_REVIEW_INVALID | 07:L1347｜205031–205466 |
| `H4-09` | Dual Axis | 原 candidate truth, reviewer process qualified → two-axis result；Consumer/Owner AO；分軸判斷不可平均；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS candidate=FAIL、process=PASS 時全案仍 HOLD；NEG reviewer 合格便宣稱 candidate PASS → DUAL_AXIS_COLLAPSE | 07:L1348｜205467–205906 |
| `H4-10` | Native Receipt | 原 issuer/subject/raw digest/sig → trusted binding；Consumer/Owner HGK Native Owner；驗真 key/ACL；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS sig+scope+raw 同 Subject 有效；NEG S2 收據重播給 S1 → NATIVE_RECEIPT_SUBJECT_MISMATCH | 07:L1349｜205907–206321 |
| `H4-11` | RepairCone | 原 first failing invariant, DAG, legal writeset → minimal repair cone；Consumer/Owner Maker/Repair Owner；用受限 L2 ECP；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 只修依賴受影最小集合，重測對應案；NEG 擴寫無關 Source/Oracle → REPAIR_SCOPE_OVERREACH | 07:L1350｜206322–206767 |
| `H4-12` | PRE-W3 | 原 first W3 packet, SWOF Gate, dispatch raw → non-dispatch proof；Consumer/Owner SWOF Owner；正式 Gate 前只 shadow；本版只產 H4CaseProposal，Reader=Protected AO/適用 Reviewer。 | POS 沒正式 Gate 時 NOT_DISPATCHED 可驗；NEG 無 Gate 卻寫 W3 → PREW3_GATE_BYPASS | 07:L1351｜206768–207184 |

**回切結果**：12/12 列 slice 逐位元相同；`H4-01…H4-12` 連續。

### D-03b SEAM（宣告 11；實測 11）

| ID | 標題 | 斷言什麼（原契約，逐字） | POS／NEG／退出（尾句省略） | 座標 |
|---|---|---|---|---|
| `SEAM-01` | Activation | host_loader.trigger_route 必註冊；受影 Domain Reader=Host Operator。 | 合法 Skill 真觸發；不存在 route 卻稱 Active → HOST_NOT_EFFECTIVE | 07:L1352｜207185–207459 |
| `SEAM-02` | Pre-gate bypass | gate.receipt_ref 在 dispatch 前驗；受影 Domain Reader=HGK Issuer/Receiver。 | 有權 Gate 先於 effect；dispatch_at<admit_at → PRE_GATE_BYPASS | 07:L1353｜207460–207737 |
| `SEAM-03` | Input downgrade | schema_version/security attributes 不降；受影 Domain Reader=Schema/PIPD Owner。 | 不變欄被保留；v1 threat fields 被刪成 v0 → SCHEMA_DOWNGRADE_DENIED | 07:L1354｜207738–208028 |
| `SEAM-04` | Internal Oracle | oracle.principal_id != maker；受影 Domain Reader=Oracle/Checker Owners。 | 有權 Checker 真分離；Maker 上白名單 → TQ_SOD | 07:L1355｜208029–208288 |
| `SEAM-05` | Canonical Owner | pi.writer_namespace 唯 PIPD；受影 Domain Reader=PIPD Owner。 | 正式 PI Writer 正確；SBL 假 PI → SECOND_CANONICAL_WRITER | 07:L1356｜208289–208545 |
| `SEAM-06` | Fallback compatibility | provider-off 必保持 Required FUO；受影 Domain Reader=Product/Host Owner。 | fallback 有同等 FUO；缺 delete 仍稱 parity → PROVIDER_OFF_FUO_LOSS | 07:L1357｜208546–208835 |
| `SEAM-07` | Alternate route | 每條 route 保持 issuer authority；受影 Domain Reader=HGK/SWOF Owners。 | 本地與連線 Route 不換權威；secondary local grant → WRONG_AUTHORITY_GRANT | 07:L1358｜208836–209125 |
| `SEAM-08` | Post-gate effect | Dispatch 實時 nonce/expiry valid；受影 Domain Reader=HGK Receiver。 | 當下可驗效期；plan 後過期仍動手 → POST_GATE_PERMISSION_EXPIRED | 07:L1359｜209126–209404 |
| `SEAM-09` | Replay/stale | nonce/op_id at-most-once；受影 Domain Reader=Hermes/Issuer。 | Unknown 先 readback；timeout blind retry → EFFECT_REPLAY_DENIED | 07:L1360｜209405–209660 |
| `SEAM-10` | TOCTOU | repo_context.head_sha 鎖 preimage；受影 Domain Reader=L2 Repo Owner。 | 写前 HEAD 同凍結版；中途漂移 → TOCTOU_REPO_HEAD | 07:L1361｜209661–209913 |
| `SEAM-11` | Exact evidence | raw_receipt.subject_sha 同候選；受影 Domain Reader=Evidence/Checker Owner。 | candidate/raw/manifest exact match；舊 SHA Raw 冒用 → RAW_SUBJECT_MISMATCH | 07:L1362｜209914–210202 |

**回切結果**：11/11 列 slice 逐位元相同；`SEAM-01…SEAM-11` 連續。

## D-04｜CH-24 Donor24（24）與 CH-25 Method25（25）具名列舉

> **來源**：`08_TECHNOLOGY_DEFAULT_HOTSWAP(4).md`；sha256 `1df04680319796aa253256c5da9c8adea47a5601abfe17086f3598d4f0470f8d`
> **區段**：§5.3 `Donor24：24 個原身份逐項功能與處置`（byte 158197–242138）與 §5.4 `Method25：25 個原身份逐項功能與處置`（byte 244859–324412）。
> **插入位置**：`CH-24` 主體 `**原產品主題／受影接收**` 段之後（在受影 r4 設計卡之前）；`CH-25` 同位置。
> **邊界**：列舉只還原「原身份／原功能／原處置」，**不構成 TechnologyAdmission 核可**，也不把任何 `原處置` 升為安裝同意。

### D-04a Donor24：24 個 slot（宣告 24；實測 24）

| Slot ID | Donor | Need（原功能，逐字） | Output／Consumer | 原處置 | 座標 |
|---|---|---|---|---|---|
| `SLOT-OS-01` | OpenSpec | OS-01: if unclear→Explore; if conflict→TT | Trigger = Explore when ambiguous 有效且符合原 disposition → DecisionLedger+QuestionDelta；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1076] | `SELECTIVE_NATIVE_REUSE` | 08:L761｜158197–159165 |
| `SLOT-OS-02` | OpenSpec | OS-02: diff current spec to requested behavior | Trigger = CurrentHEAD+desired scope bounded diff 有效且符合原 disposition → SpecDelta+ChangeProposal；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1077] | `SELECTIVE_NATIVE_REUSE` | 08:L779｜161785–162788 |
| `SLOT-OS-03` | OpenSpec | OS-03: apply only legal write paths then verify | Trigger = Approved Change+WriteSet+Native ECP 有效且符合原 disposition → ChangeSet+ApplyReadback；Reader=WP-FHS-16 受影原 PIPD/SBL/HGK Consumer，effect REPOSITORY_WRITE_ONLY_WITH_NATIVE_DEV_ECP，不可越權；[SRC-MASTER:L1078] | `SELECTIVE_NATIVE_REUSE` | 08:L797｜165461–166488 |
| `SLOT-OS-04` | OpenSpec | OS-04: archive only when truth & trace settled | Trigger = Verified change + trace closed archive 有效且符合原 disposition → ArchiveRecord+Supersession；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1079] | `SELECTIVE_NATIVE_REUSE` | 08:L815｜169162–170174 |
| `SLOT-SK-01` | Spec Kit | SK-01: carry precedence into all downstream artifacts | Trigger = Product kind + Constitution + non-goals 有效且符合原 disposition → ConstitutionBinding；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1080] | `OPTIONAL_GREENFIELD` | 08:L833｜172858–173851 |
| `SLOT-SK-02` | Spec Kit | SK-02: clarify only new high-value unknowns | Trigger = Unknown requirement + value of information 有效且符合原 disposition → RequirementAtom+ACCSeed；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1081] | `OPTIONAL_GREENFIELD` | 08:L851｜176510–177498 |
| `SLOT-SK-03` | Spec Kit | SK-03: topologically sort task nodes after dependencies | Trigger = Bounded task nodes + dependency and owner 有效且符合原 disposition → TaskDAG+TopoOrder；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1082] | `OPTIONAL_GREENFIELD` | 08:L869｜180158–181127 |
| `SLOT-SK-04` | Spec Kit | SK-04: compose only admitted modules | Trigger = Approved workflow manifests with versions 有效且符合原 disposition → WorkflowComposition；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1083] | `OPTIONAL_GREENFIELD` | 08:L887｜183762–184748 |
| `SLOT-MP-01` | mattpocock/skills | MP-01: route domain need, not donor brand | Trigger = Goal+intent type+host capability 有效且符合原 disposition → SkillRouteDecision；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1084] | `METHOD_REUSE` | 08:L905｜187402–188357 |
| `SLOT-MP-02` | mattpocock/skills | MP-02: maximize information gain / known answers never reask | Trigger = Document context+known answers+uncertainty 有效且符合原 disposition → QuestionLedger；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1085] | `METHOD_REUSE` | 08:L923｜190955–191939 |
| `SLOT-MP-03` | mattpocock/skills | MP-03: normalize glossary before ADR | Trigger = Glossary terms+boundary+events 有效且符合原 disposition → DomainModel+Glossary+ADR；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1086] | `METHOD_REUSE` | 08:L941｜194578–195553 |
| `SLOT-MP-04` | mattpocock/skills | MP-04: atom→task seed and acceptance ref | Trigger = Approved SpecCandidate+ACC+task owner 有效且符合原 disposition → TaskSpecSeed+TicketCandidate；Reader=WP-FHS-15 受影原 PIPD/SBL/HGK Consumer，effect LOCAL_DRAFT_NOT_REMOTE_PUBLISH，不可越權；[SRC-MASTER:L1087] | `METHOD_REUSE` | 08:L959｜198179–199188 |
| `SLOT-GS-01` | GSD | GS-01: partition immutable refs and task context | Trigger = SourceHash+Goal+Phase context 有效且符合原 disposition → CheckpointManifest；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1088] | `REFERENCE_ONLY/ARCHIVED_LINEAGE_CHECK` | 08:L977｜201852–202851 |
| `SLOT-GS-02` | GSD | GS-02: gate previous phase before next | Trigger = Milestone DAG + gate prerequisites 有效且符合原 disposition → MilestoneGateDecision；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1089] | `REFERENCE_ONLY/ARCHIVED_LINEAGE_CHECK` | 08:L995｜205402–206423 |
| `SLOT-GS-03` | GSD | GS-03: resume after readback and nonce proof | Trigger = Saved Checkpoint+nonce+effect result 有效且符合原 disposition → ResumeDecision+EffectReadback；Reader=WP-FHS-08 受影原 PIPD/SBL/HGK Consumer，effect RECONCILE_FIRST_NO_REPLAY，不可越權；[SRC-MASTER:L1090] | `REFERENCE_ONLY/ARCHIVED_LINEAGE_CHECK` | 08:L1013｜209012–210058 |
| `SLOT-GS-04` | GSD | GS-04: bind release input sha to test sha | Trigger = Build SubjectSHA+verification+release rights 有效且符合原 disposition → ReleaseReadinessReport；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1091] | `REFERENCE_ONLY/ARCHIVED_LINEAGE_CHECK` | 08:L1031｜212679–213691 |
| `SLOT-GT-01` | gstack | GT-01: role review product value with concrete alternatives | Trigger = ProductKind+JTBD/FUO target 有效且符合原 disposition → ProductReviewFindings；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1092] | `REFERENCE/EVAL_ONLY` | 08:L1049｜216283–217265 |
| `SLOT-GT-02` | gstack | GT-02: review usability,NFR,error paths | Trigger = Arch+NFR+UX baseline 有效且符合原 disposition → EngineeringUXFindings；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1093] | `REFERENCE/EVAL_ONLY` | 08:L1067｜219798–220736 |
| `SLOT-GT-03` | gstack | GT-03: independent review/QA on exact source | Trigger = Test plan+candidate hash+independent checker 有效且符合原 disposition → QAReviewFindings+CheckerRequest；Reader=WP-FHS-09 受影原 PIPD/SBL/HGK Consumer，effect ADVISORY_ONLY_UNTIL_TRUE_CHECKER，不可越權；[SRC-MASTER:L1094] | `REFERENCE/EVAL_ONLY` | 08:L1085｜223211–224214 |
| `SLOT-GT-04` | gstack | GT-04: check ship gate and log retro without modifying Oracle | Trigger = Status checks+user value+release evidence 有效且符合原 disposition → ShipReadinessFindings；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1095] | `REFERENCE/EVAL_ONLY` | 08:L1103｜226793–227781 |
| `SLOT-SP-01` | Superpowers | SP-01: freeze key ADR before effect | Trigger = Design options+source-risk-ADR 有效且符合原 disposition → ArchitectureADR+WriteIntentCandidate；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1096] | `METHOD_REUSE` | 08:L1121｜230342–231296 |
| `SLOT-SP-02` | Superpowers | SP-02: run Red on old HEAD → modify → Green on new HEAD | Trigger = Failing test OldHEAD+exact code scope 有效且符合原 disposition → RedGreenTrace+RunnerRawLog；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1097] | `METHOD_REUSE` | 08:L1139｜233921–234913 |
| `SLOT-SP-03` | Superpowers | SP-03: identify invariant then smallest affected cone | Trigger = Observed failure+repro+root cause 有效且符合原 disposition → RootCauseRecord+RepairCone；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1098] | `METHOD_REUSE` | 08:L1157｜237573–238535 |
| `SLOT-SP-04` | Superpowers | SP-04: bounded plan/test/independent review | Trigger = Plan+independent evidence+review request 有效且符合原 disposition → CompletionGateCandidate；Reader=WP-FHS-13 受影原 PIPD/SBL/HGK Consumer，effect NO_EFFECT_OR_READ_ONLY，不可越權；[SRC-MASTER:L1099] | `METHOD_REUSE` | 08:L1175｜241161–242138 |

**回切結果**：24/24 個 slot 的 block slice 逐位元相同；分組為 OS 4／SK 4／MP 4／GS 4／GT 4／SP 4＝24，無缺號。

### D-04b Method25：25 個 method（宣告 25；實測 25）

| Method ID | 名稱 | 用途（Trigger→Output／Consumer，逐字） | 原處置 | 座標 |
|---|---|---|---|---|
| `METHOD-01` | BMAD-METHOD | 只有原適用 Trigger/來源條款支持時 BMAD bounded requirements map + human decisions → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `METHOD_ONLY (not installed claim)` | 08:L1194｜244859–245926 |
| `METHOD-02` | mattpocock/skills:grill-with-docs | 只有原適用 Trigger/來源條款支持時 deduplicated QuestionLedger → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `METHOD_ONLY (not installed claim)` | 08:L1211｜248255–249305 |
| `METHOD-03` | mattpocock/skills:domain-modeling | 只有原適用 Trigger/來源條款支持時 DomainModel + Glossary + ADR conflict → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `METHOD_ONLY (not installed claim)` | 08:L1228｜251595–252655 |
| `METHOD-04` | mattpocock/skills:to-spec | 只有原適用 Trigger/來源條款支持時 SpecCandidate{atoms,ACC,source_refs} → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `METHOD_ONLY (not installed claim)` | 08:L1245｜254955–256005 |
| `METHOD-05` | mattpocock/skills:to-tickets | 只有原適用 Trigger/來源條款支持時 TaskSpecSeed+TicketCandidate local JSON → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `METHOD_ONLY (not installed claim)` | 08:L1262｜258303–259379 |
| `METHOD-06` | OpenSpec | 只有原適用 Trigger/來源條款支持時 ChangeDraft→SpecDelta→bounded patch/ref+archive candidate → WP-FHS-16 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE_TRANSLATE (not installed claim)` | 08:L1279｜261700–262775 |
| `METHOD-07` | Spec Kit | 只有原適用 Trigger/來源條款支持時 ConstBinding/Spec/Plan/TaskDAG → WP-FHS-16 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE_WRAP (not installed claim)` | 08:L1296｜265107–266107 |
| `METHOD-08` | Superpowers | 只有原適用 Trigger/來源條款支持時 DesignDecision/RedGreenTrace/RootCause/ReviewGate → WP-FHS-18 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE_TRANSLATE (not installed claim)` | 08:L1313｜268369–269421 |
| `METHOD-09` | GitHub Actions | 只有原適用 Trigger/來源條款支持時 CI status checks/readback expectations → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE_WRAP (not installed claim)` | 08:L1330｜271727–272763 |
| `METHOD-10` | MCP | 只有原適用 Trigger/來源條款支持時 TypedToolDescriptor/transport mapping → WP-FHS-17 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `PROTOCOL_ONLY (not installed claim)` | 08:L1347｜274959–275980 |
| `METHOD-11` | ACP | 只有原適用 Trigger/來源條款支持時 AgentMessageCandidate → WP-FHS-17 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `PROTOCOL_ONLY (not installed claim)` | 08:L1364｜278170–279142 |
| `METHOD-12` | OpenSSF Scorecard | 只有原適用 Trigger/來源條款支持時 ScorecardSignals and PolicyReview → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `SUPPORT_ONLY (not installed claim)` | 08:L1381｜281283–282327 |
| `METHOD-13` | SLSA | 只有原適用 Trigger/來源條款支持時 SLSA ProvenanceExpectation → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `SUPPORT_ONLY (not installed claim)` | 08:L1398｜284610–285620 |
| `METHOD-14` | OWASP | 只有原適用 Trigger/來源條款支持時 negative fixtures and guarded failure expectations → WP-FHS-09 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `SUPPORT_ONLY (not installed claim)` | 08:L1415｜287799–288822 |
| `METHOD-15` | CodeQL | 只有原適用 Trigger/來源條款支持時 SARIF findings+query provenance → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE (not installed claim)` | 08:L1432｜291012–291989 |
| `METHOD-16` | Semgrep | 只有原適用 Trigger/來源條款支持時 Rule ID/path/priority findings → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE (not installed claim)` | 08:L1449｜294218–295204 |
| `METHOD-17` | Renovate | 只有原適用 Trigger/來源條款支持時 Renovate update proposal PR candidate → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `DEFER (not installed claim)` | 08:L1466｜297441–298455 |
| `METHOD-18` | Dependabot | 只有原適用 Trigger/來源條款支持時 Dependabot update proposal (source-specific owner TT) → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `NO_SOURCE_EVIDENCE (not installed claim)` | 08:L1483｜300640–301711 |
| `METHOD-19` | Cosign | 只有原適用 Trigger/來源條款支持時 Signature verification report → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE (not installed claim)` | 08:L1500｜303938–304934 |
| `METHOD-20` | Syft | 只有原適用 Trigger/來源條款支持時 Syft SBOM (SPDX/CycloneDX) → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE (not installed claim)` | 08:L1517｜307099–308064 |
| `METHOD-21` | Trivy | 只有原適用 Trigger/來源條款支持時 Trivy scanner result+policy outcome → WP-FHS-19 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `CANDIDATE (not installed claim)` | 08:L1534｜310203–311176 |
| `METHOD-22` | SQLite/FTS5 | 只有原適用 Trigger/來源條款支持時 SQLite schema/FTS5 index and query evidence → WP-FHS-15 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `LOCAL_FIRST_OPTION (not installed claim)` | 08:L1551｜313402–314450 |
| `METHOD-23` | FAR/FDA | 只有原適用 Trigger/來源條款支持時 Native owned FAR/FDA reference only → WP-FHS-18 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `HGK_FABRIC_EXISTING_ONLY (not installed claim)` | 08:L1568｜316720–317780 |
| `METHOD-24` | OpenAI Agents SDK | 只有原適用 Trigger/來源條款支持時 HITL pause/resume donor pattern → WP-FHS-17 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `SUPPORT_QUARANTINE (not installed claim)` | 08:L1585｜319993–321058 |
| `METHOD-25` | Agent Skills specification | 只有原適用 Trigger/來源條款支持時 SKILL.md format and dependency validation → WP-FHS-11 所有者之 Read/Method Consumer；DEFER/NO_SOURCE_EVIDENCE 不進必裝 Queue。 | `PORTABILITY_SPEC (not installed claim)` | 08:L1602｜323339–324412 |

**回切結果**：25/25 個 method 的 block slice 逐位元相同；`METHOD-01…METHOD-25` 連續。

## 分母對帳（宣告 vs 實測）

| 缺口 | 章 | 宣告 | 實測 | 唯一 id | delta | 判定 |
|---|---|---:|---:|---:|---:|---|
| D-02 | CH-11 | 18 | 18 | 18 | +0 | MATCH |
| D-03 | CH-42 旁 | 12 | 12 | 12 | +0 | MATCH |
| D-03 | CH-42 旁 | 11 | 11 | 11 | +0 | MATCH |
| D-04 | CH-24 | 24 | 24 | 24 | +0 | MATCH |
| D-04 | CH-25 | 25 | 25 | 25 | +0 | MATCH |

五項宣告數（18／12／11／24／25）與來源實測數**全部相符**，不需更正任何分母；本輪沒有發現「宣告多列」或「宣告少列」的情形。

**W0 r4 控制稿自身是否列舉（同檔 regex 計數，非引述）**：

| 缺口 | 章 | 具名列舉 | 全檔 token 命中 |
|---|---|---|---|
| D-02 | CH-11 | **0 列** | `PM:T0`／`SE:T1`／`TPgM:T5` 型式＝0；「18 Stage」字樣＝5 |
| D-03 | （無專章） | **0 列** | `H4-nn`＝0；`SEAM-nn`＝0 |
| D-04 | CH-24 | **0 列** | `SLOT-xx-nn`＝0；「Donor24」字樣＝4 |
| D-04 | CH-25 | **0 列** | `METHOD-nn`＝0；「Method25」字樣＝4 |

也就是說：四個章節都只宣告「有幾個」，**沒有任何一個 id 出現在控制稿裡**。

**修補前的具名數（量測，非引述）**：

| 文件 | CH-24 具名 slot | CH-25 具名 method | 合計／49 |
|---|---:|---:|---:|
| W0 r4 skeleton（本次修補對象） | 0 | 0 | 0／49 |
| W0 r7 writeback（前輪已修版本） | 3 | 4 | 7／49 |

即：r4 控制稿的 CH-24／CH-25 章內**一個 slot／method id 都沒有**（`SLOT-`、`METHOD-` 在整份 r4 檔的命中數為 0），並非「只缺一部分」；
下一輪 writeback 已具名 7 個（3 slot＋4 method），其餘 42 個仍靠外部指標。本檔補的正是這 49 個。

## 本檔不主張

- 不主張任何列已被原 Domain Reader／Owner 讀回或追認（`ORIGINAL_ACK` 不在本輪）。
- 不主張 18 Stage 已被真 Host 執行、也不主張 H4／SEAM／96 Oracle 已被 Protected Checker 判定。
- 不主張 24 slot／25 method 中任何一個已取得 TechnologyAdmission 或授權（來源 disposition 僅為原字面）。
