# WP-FHS-16 Default30 Need → Occupant 對照矩陣

lane `WP-FHS-16`；schema `wp-fhs-16/1`；來源根 `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\FHS／FHS-MSC／SBL\FHS\PIPD-LS-PKG\定案\W0\FHS_PIPD-LS-PKG_W0_R4C`。

本檔由 `need_occupant.py` 從實體 JSON 解析產生，不是人工抄寫。每一列的 license、windows_fit、consumer、nofit_reason 都是來源欄位的逐字副本，並附 JSON Pointer 來源參照；來源沒有給的欄位標 `UNBOUND` 並列名具 HOLD。**本輪不安裝、不升級任何 Default30 項，也不把 Donor24/Method25 當 installer。**

## 統計

| 指標 | 值 |
| --- | --- |
| Need 分母 | 30 |
| Required=true | 30 |
| Required=false | 0 |
| SELECTED | 0 |
| OCCUPANT_PIN_HOLD | 28 |
| HOST_PIN_HOLD | 2 |
| NOFIT | 0 |
| UNBOUND（status） | 0 |
| install_state NOT_INSTALLED | 0 |
| install_state PIN_HOLD | 28 |
| install_state HOST_PIN_HOLD | 2 |
| license DECLARED | 0 |
| license DECLARED+HOST_ACK_PENDING | 1 |
| license READER_HOLD | 29 |
| license UNBOUND | 0 |
| windows_fit UNBOUND | 30 |
| windows_fit FIT | 0 |
| windows_fit NOFIT | 0 |
| 有 Donor/Method translator 的 Need | 15 |
| occupant_kind DONOR / METHOD / HOST / NONE | 4 / 11 / 15 / 0 |
| translator 數（donor / method） | 30（16 / 14） |

## 與 CURRENT_CANDIDATE_STATE 宣告對照

宣告字串（逐字）：「Default30 30/30 Required；28 OCCUPANT_PIN_HOLD＋2 HOST_PIN_HOLD；無 INSTALLED/VERIFIED 升格」

判決：**MATCH**

| 宣告項 | 宣告值 | 實算值 | 一致 |
| --- | --- | --- | --- |
| need_total | 30 | 30 | YES |
| required | 30 | 30 | YES |
| occupant_pin_hold | 28 | 28 | YES |
| host_pin_hold | 2 | 2 | YES |
| no_installed_or_verified_upgrade | True | True | YES |

## 30 筆矩陣

| # | need_id | need_class | required | occupant | kind | license | windows_fit | consumer | install_state | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `Default30:P0-TOOL-001` | RUNTIME | true | Hermes Agent | HOST | upstream LICENSE bytes pinned in research/Hermes_LICENSE; distribution/Host applicability HOLD | UNBOUND | RUNTIME.HERMES→HGK SharedSpine→canonical Hermes executable/PID | HOST_PIN_HOLD | HOST_PIN_HOLD |
| 2 | `Default30:P0-TOOL-002` | CORE | true | SDLC_PRW | HOST | LICENSE_READER_HOLD | UNBOUND | CORE.SDLC_PRW→PIPD phase compiler→HGK SharedSpine schema reader | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 3 | `Default30:P0-TOOL-003` | CORE | true | SRU Kernel | HOST | LICENSE_READER_HOLD | UNBOUND | CORE.SRU_KERNEL→HGK Native Registry/SourceReuse scoped resolver | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 4 | `Default30:P0-TOOL-004` | KNOWLEDGE | true | DocETL | HOST | LICENSE_READER_HOLD | UNBOUND | KNOWLEDGE.DOCETL→SBL/PIPD Document Reader + known file/source parser | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 5 | `Default30:P0-TOOL-005` | RUNTIME | true | Codex | HOST | LICENSE_READER_HOLD | UNBOUND | RUNTIME.CODE_WORKER_PRIMARY→Hermes delegated Codex CLI via HGK executor registry | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 6 | `Default30:P0-TOOL-006` | RUNTIME | true | OpenCode | HOST | LICENSE_READER_HOLD | UNBOUND | RUNTIME.CODE_WORKER_ALTERNATE→Hermes approved OpenCode/OpenCode Go provider adapter | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 7 | `Default30:P0-TOOL-008` | KNOWLEDGE | true | LLM Wiki | HOST | LICENSE_READER_HOLD | UNBOUND | KNOWLEDGE.LLM_WIKI→SBL Knowledge K09 wiki compiler/validated local reader | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 8 | `Default30:P0-TOOL-010` | SPEC | true | Spec Kit | DONOR | LICENSE_READER_HOLD | UNBOUND | SPEC.GREENFIELD_SPEC_KIT→SBL TPM/spec HostAdapter, optional official Spec Kit | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 9 | `Default30:P0-TOOL-011` | SPEC | true | OpenSpec | DONOR | MIT upstream bytes in research/OpenSpec_LICENSE; original Host License Reader ACK pending | UNBOUND | SPEC.BROWNFIELD_OPENSPEC→SBL proposal adapter+OpenSpec allowed Host skill | HOST_PIN_HOLD | HOST_PIN_HOLD |
| 10 | `Default30:P0-TOOL-016` | METHOD | true | mattpocock-skills v1.1 | DONOR | LICENSE_READER_HOLD | UNBOUND | METHOD.MATTPOCOCK_SKILLS→TPM Skill loader+approved original v1.1 method contract | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 11 | `Default30:P0-TOOL-017` | METHOD | true | Grill Me | METHOD | LICENSE_READER_HOLD | UNBOUND | METHOD.GRILL_ME→TPM Document/QuestionLedger Skill Host | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 12 | `Default30:P0-TOOL-020` | METHOD | true | Superpowers | DONOR | LICENSE_READER_HOLD | UNBOUND | METHOD.SUPERPOWERS→SBL bounded code-repair method slot via Host Skill | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 13 | `Default30:P0-TOOL-024` | FORMAT | true | Agent Skills | METHOD | LICENSE_READER_HOLD | UNBOUND | FORMAT.AGENT_SKILLS→SBL skills/ HostAdapter + Skill Loader | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 14 | `Default30:P0-TOOL-025` | PROTO | true | Model Context Protocol | METHOD | LICENSE_READER_HOLD | UNBOUND | PROTO.MCP→HGK Tool/Method registry and approved host MCP adapter | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 15 | `Default30:P0-TOOL-026` | SOURCE | true | AGENTS.md | HOST | LICENSE_READER_HOLD | UNBOUND | SOURCE.AGENTS_MD→Git repo AGENTS.md parser read-only | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 16 | `Default30:P0-TOOL-028` | SOURCE | true | DESIGN.md | HOST | LICENSE_READER_HOLD | UNBOUND | SOURCE.DESIGN_MD→SBL TPM design reader for versioned DESIGN.md | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 17 | `Default30:P0-TOOL-030` | CORE | true | Loop Engineering | HOST | LICENSE_READER_HOLD | UNBOUND | CORE.LOOP_ENGINEERING→HGK SharedSpine/Hermes reducer/Checkpoint | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 18 | `Default30:P0-TOOL-031` | CORE | true | Harness Engineering | HOST | LICENSE_READER_HOLD | UNBOUND | CORE.HARNESS_ENGINEERING→HGK native harness + Runner/Tool registry | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 19 | `Default30:P0-TOOL-032` | RUNTIME | true | Multi-Agent | HOST | LICENSE_READER_HOLD | UNBOUND | RUNTIME.MULTI_AGENT→Hermes SWARM/Worker pool via HGK admission | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 20 | `Default30:P0-TOOL-034` | RUNTIME | true | Sub-Agent | HOST | LICENSE_READER_HOLD | UNBOUND | RUNTIME.SUB_AGENT→HGK lease-bound Hermes child worker | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 21 | `Default30:P0-TOOL-053` | OBS | true | OpenTelemetry | HOST | LICENSE_READER_HOLD | UNBOUND | OBS.OTEL→Host telemetry exporter via approved OpenTelemetry adapter | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 22 | `Default30:P0-TOOL-059` | SEC | true | Semgrep | METHOD | LICENSE_READER_HOLD | UNBOUND | SEC.SEMGREP→Security CI runner Semgrep pinned ruleset | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 23 | `Default30:P0-TOOL-060` | SEC | true | CodeQL | METHOD | LICENSE_READER_HOLD | UNBOUND | SEC.CODEQL→Security CI or GitHub Actions CodeQL required workflow | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 24 | `Default30:P0-TOOL-061` | SEC | true | Trivy | METHOD | LICENSE_READER_HOLD | UNBOUND | SEC.TRIVY→Security CI Trivy binary runner | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 25 | `Default30:P0-TOOL-062` | SUPPLY | true | GitHub Actions | METHOD | LICENSE_READER_HOLD | UNBOUND | SUPPLY.CI_GITHUB_ACTIONS→SBL/PIPD repository workflow caller | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 26 | `Default30:P0-TOOL-063` | SUPPLY | true | OpenSSF Scorecard | METHOD | LICENSE_READER_HOLD | UNBOUND | SUPPLY.OSSF_SCORECARD→Security Owner Scorecard workflow | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 27 | `Default30:P0-TOOL-064` | SUPPLY | true | SBOM | METHOD | LICENSE_READER_HOLD | UNBOUND | SUPPLY.SBOM→Release Owner SBOM generator/output registry | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 28 | `Default30:P0-TOOL-065` | SUPPLY | true | Artifact Attestation | METHOD | LICENSE_READER_HOLD | UNBOUND | SUPPLY.ARTIFACT_ATTESTATION→Release Owner GitHub Attestation/Cosign binding | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 29 | `Default30:P0-TOOL-068` | SEC | true | OSV | HOST | LICENSE_READER_HOLD | UNBOUND | SEC.OSV→Security/vuln feed Reader or pinned approved OSV API | PIN_HOLD | OCCUPANT_PIN_HOLD |
| 30 | `Default30:P0-TOOL-072` | CORE | true | SQLite | METHOD | LICENSE_READER_HOLD | UNBOUND | CORE.SQLITE→HGK existing src/hg_kseos/spine.py / DB actual host discovery | PIN_HOLD | OCCUPANT_PIN_HOLD |

### License / Windows-fit / NOFIT 來源參照

| need_id | license_state | license_source_ref | windows_fit_evidence | nofit_reason | nofit_ref |
| --- | --- | --- | --- | --- | --- |
| `Default30:P0-TOOL-001` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/0/license` | `DEFAULT30_CHOICES.json#/0/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | UNAVAILABLE_REQUIRED_CAPABILITY; L0 read-only；REVOKE_TOKEN | `DEFAULT30_CHOICES.json#/0/original_business` |
| `Default30:P0-TOOL-002` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/1/license` | `DEFAULT30_CHOICES.json#/1/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | ReadOnly PhasePlan, not Live admission | `DEFAULT30_CHOICES.json#/1/original_business` |
| `Default30:P0-TOOL-003` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/2/license` | `DEFAULT30_CHOICES.json#/2/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | NOFIT until existing SRU identity proven | `DEFAULT30_CHOICES.json#/2/original_business` |
| `Default30:P0-TOOL-004` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/3/license` | `DEFAULT30_CHOICES.json#/3/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | plain source-pinned file read for accepted document types only | `DEFAULT30_CHOICES.json#/3/original_business` |
| `Default30:P0-TOOL-005` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/4/license` | `DEFAULT30_CHOICES.json#/4/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | Approved OpenCode only if same scope+POS/NEG, else NOFIT；REVOKE_TOKEN | `DEFAULT30_CHOICES.json#/4/original_business` |
| `Default30:P0-TOOL-006` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/5/license` | `DEFAULT30_CHOICES.json#/5/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | Codex if independently approved and not conflicting SoD；REVOKE_TOKEN | `DEFAULT30_CHOICES.json#/5/original_business` |
| `Default30:P0-TOOL-008` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/6/license` | `DEFAULT30_CHOICES.json#/6/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | source-anchored direct document view (reduced feature; wiki NOFIT) | `DEFAULT30_CHOICES.json#/6/original_business` |
| `Default30:P0-TOOL-010` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/7/license` | `DEFAULT30_CHOICES.json#/7/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | canonical PIPD compiler for PI only, not exact SpecKit parity；UNLOADABLE | `DEFAULT30_CHOICES.json#/7/original_business` |
| `Default30:P0-TOOL-011` | LICENSE_DECLARED_HOST_ACK_PENDING | `DEFAULT30_CHOICES.json#/8/license` | `DEFAULT30_CHOICES.json#/8/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | source-bound native change-candidate (only if accepted parity)；UNLOADABLE | `DEFAULT30_CHOICES.json#/8/original_business` |
| `Default30:P0-TOOL-016` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/9/license` | `DEFAULT30_CHOICES.json#/9/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | native question ledger for known-answer skip (if fidelity proven)；UNLOADABLE | `DEFAULT30_CHOICES.json#/9/original_business` |
| `Default30:P0-TOOL-017` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/10/license` | `DEFAULT30_CHOICES.json#/10/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | native source-bound clarification only, full parity pending；UNLOADABLE | `DEFAULT30_CHOICES.json#/10/original_business` |
| `Default30:P0-TOOL-020` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/11/license` | `DEFAULT30_CHOICES.json#/11/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | existing HGK red/green as scoped partial behavior, method NOFIT until parity；UNLOADABLE | `DEFAULT30_CHOICES.json#/11/original_business` |
| `Default30:P0-TOOL-024` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/12/license` | `DEFAULT30_CHOICES.json#/12/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | source document read only; cannot claim effective Skill Loaded | `DEFAULT30_CHOICES.json#/12/original_business` |
| `Default30:P0-TOOL-025` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/13/license` | `DEFAULT30_CHOICES.json#/13/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | direct approved native tool call only if same ABI/permissions | `DEFAULT30_CHOICES.json#/13/original_business` |
| `Default30:P0-TOOL-026` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/14/license` | `DEFAULT30_CHOICES.json#/14/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | pinned repository instructions explicit read；N/A | `DEFAULT30_CHOICES.json#/14/original_business` |
| `Default30:P0-TOOL-028` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/15/license` | `DEFAULT30_CHOICES.json#/15/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | frozen design artifact with references, no host activation；N/A | `DEFAULT30_CHOICES.json#/15/original_business` |
| `Default30:P0-TOOL-030` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/16/license` | `DEFAULT30_CHOICES.json#/16/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | existing reducer only if state invariants verified；RESTORE_POLICY | `DEFAULT30_CHOICES.json#/16/original_business` |
| `Default30:P0-TOOL-031` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/17/license` | `DEFAULT30_CHOICES.json#/17/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | existing tested harness only if matching original Oracle | `DEFAULT30_CHOICES.json#/17/original_business` |
| `Default30:P0-TOOL-032` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/18/license` | `DEFAULT30_CHOICES.json#/18/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | single native sequential worker when independent parallelism not required；REVOKE_TOKEN | `DEFAULT30_CHOICES.json#/18/original_business` |
| `Default30:P0-TOOL-034` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/19/license` | `DEFAULT30_CHOICES.json#/19/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | single eligible worker for nonparallel task (partial semantics)；REVOKE_TOKEN | `DEFAULT30_CHOICES.json#/19/original_business` |
| `Default30:P0-TOOL-053` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/20/license` | `DEFAULT30_CHOICES.json#/20/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | local structured HGK operation log if trace IDs preserved; OTel NOFIT | `DEFAULT30_CHOICES.json#/20/original_business` |
| `Default30:P0-TOOL-059` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/21/license` | `DEFAULT30_CHOICES.json#/21/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | NOFIT for Semgrep-specific check; local analyzer not equivalent；UNLOADABLE | `DEFAULT30_CHOICES.json#/21/original_business` |
| `Default30:P0-TOOL-060` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/22/license` | `DEFAULT30_CHOICES.json#/22/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | NOFIT until real CodeQL allowed；UNLOADABLE | `DEFAULT30_CHOICES.json#/22/original_business` |
| `Default30:P0-TOOL-061` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/23/license` | `DEFAULT30_CHOICES.json#/23/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | NOFIT unless equal approved scanner accepted by owner；UNLOADABLE | `DEFAULT30_CHOICES.json#/23/original_business` |
| `Default30:P0-TOOL-062` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/24/license` | `DEFAULT30_CHOICES.json#/24/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | isolated local tests only for L2; not release CI | `DEFAULT30_CHOICES.json#/24/original_business` |
| `Default30:P0-TOOL-063` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/25/license` | `DEFAULT30_CHOICES.json#/25/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | NOFIT for Scorecard-specific assurance；UNLOADABLE | `DEFAULT30_CHOICES.json#/25/original_business` |
| `Default30:P0-TOOL-064` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/26/license` | `DEFAULT30_CHOICES.json#/26/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | proven compatible Syft/other generator with owner permission | `DEFAULT30_CHOICES.json#/26/original_business` |
| `Default30:P0-TOOL-065` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/27/license` | `DEFAULT30_CHOICES.json#/27/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | NOFIT without real signing and verify；REVOKE_TOKEN | `DEFAULT30_CHOICES.json#/27/original_business` |
| `Default30:P0-TOOL-068` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/28/license` | `DEFAULT30_CHOICES.json#/28/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | fresh signed local cache within TTL, else NOFIT | `DEFAULT30_CHOICES.json#/28/original_business` |
| `Default30:P0-TOOL-072` | LICENSE_READER_HOLD | `DEFAULT30_CHOICES.json#/29/license` | `DEFAULT30_CHOICES.json#/29/fit` = DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND | none for sole SharedSpine; L0 can read frozen snapshot；N/A | `DEFAULT30_CHOICES.json#/29/original_business` |

## 本波受選 Donor/Method translator（全部 is_installer=false）

| need_id | translator | kind | occupant_class | is_installer | refusal 首碼 | source_ref |
| --- | --- | --- | --- | --- | --- | --- |
| `Default30:P0-TOOL-010` | `TRANSLATOR:Donor24:SLOT-SK-01` | DONOR | OPTIONAL_GREENFIELD | false | NACK_AUTHORITY | `WP16_TRANSLATION49.json#/4` |
| `Default30:P0-TOOL-010` | `TRANSLATOR:Donor24:SLOT-SK-02` | DONOR | OPTIONAL_GREENFIELD | false | DONOR_NOFIT_OR_SCOPE_HOLD | `WP16_TRANSLATION49.json#/5` |
| `Default30:P0-TOOL-010` | `TRANSLATOR:Donor24:SLOT-SK-03` | DONOR | OPTIONAL_GREENFIELD | false | NACK_DAG | `WP16_TRANSLATION49.json#/6` |
| `Default30:P0-TOOL-010` | `TRANSLATOR:Donor24:SLOT-SK-04` | DONOR | OPTIONAL_GREENFIELD | false | NACK_UNPINNED_WORKFLOW | `WP16_TRANSLATION49.json#/7` |
| `Default30:P0-TOOL-010` | `TRANSLATOR:Method25:METHOD-07` | METHOD | CANDIDATE_WRAP | false | NACK_AUTHORITY | `WP16_TRANSLATION49.json#/30` |
| `Default30:P0-TOOL-011` | `TRANSLATOR:Donor24:SLOT-OS-01` | DONOR | SELECTIVE_NATIVE_REUSE | false | NACK_SOURCE | `WP16_TRANSLATION49.json#/0` |
| `Default30:P0-TOOL-011` | `TRANSLATOR:Donor24:SLOT-OS-02` | DONOR | SELECTIVE_NATIVE_REUSE | false | NACK_SCOPE | `WP16_TRANSLATION49.json#/1` |
| `Default30:P0-TOOL-011` | `TRANSLATOR:Donor24:SLOT-OS-03` | DONOR | SELECTIVE_NATIVE_REUSE | false | DONOR_NOFIT_OR_SCOPE_HOLD | `WP16_TRANSLATION49.json#/2` |
| `Default30:P0-TOOL-011` | `TRANSLATOR:Donor24:SLOT-OS-04` | DONOR | SELECTIVE_NATIVE_REUSE | false | NACK_ARCHIVE | `WP16_TRANSLATION49.json#/3` |
| `Default30:P0-TOOL-011` | `TRANSLATOR:Method25:METHOD-06` | METHOD | CANDIDATE_TRANSLATE | false | NACK_SCOPE | `WP16_TRANSLATION49.json#/29` |
| `Default30:P0-TOOL-016` | `TRANSLATOR:Donor24:SLOT-MP-01` | DONOR | METHOD_REUSE | false | NACK_SKILL_ROUTE | `WP16_TRANSLATION49.json#/8` |
| `Default30:P0-TOOL-016` | `TRANSLATOR:Donor24:SLOT-MP-02` | DONOR | METHOD_REUSE | false | NACK_DUPLICATE_QUESTION | `WP16_TRANSLATION49.json#/9` |
| `Default30:P0-TOOL-016` | `TRANSLATOR:Donor24:SLOT-MP-03` | DONOR | METHOD_REUSE | false | NACK_DOMAIN_CONFLICT | `WP16_TRANSLATION49.json#/10` |
| `Default30:P0-TOOL-016` | `TRANSLATOR:Donor24:SLOT-MP-04` | DONOR | METHOD_REUSE | false | NACK_ISSUE_PUBLISH | `WP16_TRANSLATION49.json#/11` |
| `Default30:P0-TOOL-017` | `TRANSLATOR:Method25:METHOD-02` | METHOD | METHOD_ONLY | false | METHOD_AS_INSTALL_DENY | `WP16_TRANSLATION49.json#/25` |
| `Default30:P0-TOOL-020` | `TRANSLATOR:Donor24:SLOT-SP-01` | DONOR | METHOD_REUSE | false | NACK_ADR | `WP16_TRANSLATION49.json#/20` |
| `Default30:P0-TOOL-020` | `TRANSLATOR:Donor24:SLOT-SP-02` | DONOR | METHOD_REUSE | false | NACK_RED_PHASE | `WP16_TRANSLATION49.json#/21` |
| `Default30:P0-TOOL-020` | `TRANSLATOR:Donor24:SLOT-SP-03` | DONOR | METHOD_REUSE | false | NACK_ROOT_CAUSE | `WP16_TRANSLATION49.json#/22` |
| `Default30:P0-TOOL-020` | `TRANSLATOR:Donor24:SLOT-SP-04` | DONOR | METHOD_REUSE | false | NACK_COMPLETION_GATE | `WP16_TRANSLATION49.json#/23` |
| `Default30:P0-TOOL-020` | `TRANSLATOR:Method25:METHOD-08` | METHOD | CANDIDATE_TRANSLATE | false | NACK_RED_PHASE | `WP16_TRANSLATION49.json#/31` |
| `Default30:P0-TOOL-024` | `TRANSLATOR:Method25:METHOD-25` | METHOD | PORTABILITY_SPEC | false | METHOD_AS_INSTALL_DENY | `WP16_TRANSLATION49.json#/48` |
| `Default30:P0-TOOL-025` | `TRANSLATOR:Method25:METHOD-10` | METHOD | PROTOCOL_ONLY | false | METHOD_AS_INSTALL_DENY | `WP16_TRANSLATION49.json#/33` |
| `Default30:P0-TOOL-059` | `TRANSLATOR:Method25:METHOD-16` | METHOD | CANDIDATE | false | METHOD_AS_INSTALL_DENY | `WP16_TRANSLATION49.json#/39` |
| `Default30:P0-TOOL-060` | `TRANSLATOR:Method25:METHOD-15` | METHOD | CANDIDATE | false | METHOD_AS_INSTALL_DENY | `WP16_TRANSLATION49.json#/38` |
| `Default30:P0-TOOL-061` | `TRANSLATOR:Method25:METHOD-21` | METHOD | CANDIDATE | false | METHOD_AS_INSTALL_DENY | `WP16_TRANSLATION49.json#/44` |
| `Default30:P0-TOOL-062` | `TRANSLATOR:Method25:METHOD-09` | METHOD | CANDIDATE_WRAP | false | METHOD_AS_INSTALL_DENY | `WP16_TRANSLATION49.json#/32` |
| `Default30:P0-TOOL-063` | `TRANSLATOR:Method25:METHOD-12` | METHOD | SUPPORT_ONLY | false | METHOD_AS_INSTALL_DENY | `WP16_TRANSLATION49.json#/35` |
| `Default30:P0-TOOL-064` | `TRANSLATOR:Method25:METHOD-20` | METHOD | CANDIDATE | false | METHOD_AS_INSTALL_DENY | `WP16_TRANSLATION49.json#/43` |
| `Default30:P0-TOOL-065` | `TRANSLATOR:Method25:METHOD-19` | METHOD | CANDIDATE | false | METHOD_AS_INSTALL_DENY | `WP16_TRANSLATION49.json#/42` |
| `Default30:P0-TOOL-072` | `TRANSLATOR:Method25:METHOD-22` | METHOD | LOCAL_FIRST_OPTION | false | METHOD_AS_INSTALL_DENY | `WP16_TRANSLATION49.json#/45` |

未受選的 WP16 項（不產生 translator）：19 筆；清單見 `TRANSLATOR_MAP.json` 的 `excluded_unselected`。

## Holds（具名）

- `WINDOWS_FIT_UNBOUND`：30/30，來源欄位 `fit` 逐字為 `DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND`。
- `LICENSE_READER_HOLD`：29/30，來源 license 欄位只到 Reader/Host HOLD，未達可發佈的授權判定。
- `PIN_UNBOUND` / 版本未釘：見 `TECH_CHOICE_READBACK.json` 各筆 `unbound`。
- `INSTALLED` / `VERIFIED`：本輪 0 筆，install_state 詞彙中不存在此二值。

## 讀回與可宣稱上限

- 讀回：`TECH_CHOICE_READBACK.json`（30 筆 need、330 條證據、TECH485 逐列 sha256 重算 485/485 PASS）。
- claim_ceiling：`AUTHOR_LOCAL_TEST`。本檔證明「作者本機可從來源 JSON 重算矩陣」，不證明任何 Host 安裝、Bound、Invoked 或 Verified。
