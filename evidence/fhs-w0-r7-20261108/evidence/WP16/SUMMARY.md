# WP-FHS-16｜Donor24 / Method25 槽位翻譯投影（作者端候選）

- 工作包：`WP-FHS-16`；效果類別 `LOCAL_DRAFT_WRITE`；宣稱上限 **AUTHOR_SIDE_PROJECTION_CANDIDATE**。
- 本輪性質：W0 r6 首次實作。先前 `evidence/WP16/` 為空（NOT_RUN），本檔為第一份真實投影，非補寫。
- 來源（唯讀）：`C:/Projects/Agent_Workspace/FHS_W1_Work_Final/FHS_W1_Work_Final/sources/08_TECHNOLOGY_DEFAULT_HOTSWAP(4).md`
  - sha256 `1df04680319796aa253256c5da9c8adea47a5601abfe17086f3598d4f0470f8d`，1128554 bytes
- 章節回溯：`C:/Projects/Agent_Workspace/FHS_W0W2_R4_20261107/writeback/W0/FHS_PIPD-LS-PKG_W0_r6.md`（CH-24 / CH-25）

## 一、測量結果

| 集合 | 藍圖名稱 | 實際枚舉 | 差異 |
|---|---|---|---|
| Donor 槽 | 24 | **24** | +0 |
| Method 槽 | 25 | **25** | +0 |
| 合計 | 49 | **49** | +0 |

每個紀錄的 `source_ref` 為 UTF-8 位元組切片（`byte_start`/`byte_end`），`quoted_text` 即該切片原文；`tools/verify_projection.py` 會重新切一次並逐字比對。

### 處置分布

| 處置 | Donor24 | Method25 | 合計 |
|---|---|---|---|
| ADOPT_CANDIDATE | 4 | 4 | 8 |
| DEFER | 12 | 9 | 21 |
| NOFIT | 0 | 1 | 1 |
| HOLD | 8 | 11 | 19 |
| 合計 | 24 | 25 | 49 |

## 二、Donor24（24 槽）

| # | slot_id | donor | licence | Host/Pack | 處置 | consumer | FirstFail |
|---|---|---|---|---|---|---|---|
| 1 | `SLOT-OS-01` | OpenSpec | UNKNOWN_NOT_STATED | SPEC.BROWNFIELD_OPENSPEC | HOLD | WP-FHS-13 | `NACK_SOURCE` |
| 2 | `SLOT-OS-02` | OpenSpec | UNKNOWN_NOT_STATED | SPEC.BROWNFIELD_OPENSPEC | HOLD | WP-FHS-13 | `NACK_SCOPE` |
| 3 | `SLOT-OS-03` | OpenSpec | UNKNOWN_NOT_STATED | SPEC.BROWNFIELD_OPENSPEC | HOLD | WP-FHS-16 | `ECP_PERMISSION_DENIED` |
| 4 | `SLOT-OS-04` | OpenSpec | UNKNOWN_NOT_STATED | SPEC.BROWNFIELD_OPENSPEC | HOLD | WP-FHS-13 | `NACK_ARCHIVE` |
| 5 | `SLOT-SK-01` | Spec Kit | UNKNOWN_NOT_STATED | SPEC.GREENFIELD_SPEC_KIT | DEFER | WP-FHS-13 | `NACK_AUTHORITY` |
| 6 | `SLOT-SK-02` | Spec Kit | UNKNOWN_NOT_STATED | SPEC.GREENFIELD_SPEC_KIT | DEFER | WP-FHS-13 | `PI_NOT_READY` |
| 7 | `SLOT-SK-03` | Spec Kit | UNKNOWN_NOT_STATED | SPEC.GREENFIELD_SPEC_KIT | DEFER | WP-FHS-13 | `NACK_DAG` |
| 8 | `SLOT-SK-04` | Spec Kit | UNKNOWN_NOT_STATED | SPEC.GREENFIELD_SPEC_KIT | DEFER | WP-FHS-13 | `NACK_UNPINNED_WORKFLOW` |
| 9 | `SLOT-MP-01` | mattpocock/skills | MIT | METHOD.MATTPOCOCK_SKILLS | ADOPT_CANDIDATE | WP-FHS-13 | `NACK_SKILL_ROUTE` |
| 10 | `SLOT-MP-02` | mattpocock/skills | MIT | METHOD.MATTPOCOCK_SKILLS | ADOPT_CANDIDATE | WP-FHS-13 | `NACK_DUPLICATE_QUESTION` |
| 11 | `SLOT-MP-03` | mattpocock/skills | MIT | METHOD.MATTPOCOCK_SKILLS | ADOPT_CANDIDATE | WP-FHS-13 | `NACK_DOMAIN_CONFLICT` |
| 12 | `SLOT-MP-04` | mattpocock/skills | MIT | METHOD.MATTPOCOCK_SKILLS | ADOPT_CANDIDATE | WP-FHS-15 | `NACK_ISSUE_PUBLISH` |
| 13 | `SLOT-GS-01` | GSD | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | WP-FHS-13 | `NACK_CHECKPOINT_STALE` |
| 14 | `SLOT-GS-02` | GSD | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | WP-FHS-13 | `NACK_MILESTONE_EVIDENCE` |
| 15 | `SLOT-GS-03` | GSD | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | WP-FHS-08 | `NACK_EFFECT_REPLAY` |
| 16 | `SLOT-GS-04` | GSD | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | WP-FHS-13 | `NACK_RELEASE_READINESS` |
| 17 | `SLOT-GT-01` | gstack | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | WP-FHS-13 | `NACK_PRODUCT_FUO` |
| 18 | `SLOT-GT-02` | gstack | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | WP-FHS-13 | `NACK_ENG_REPRO` |
| 19 | `SLOT-GT-03` | gstack | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | WP-FHS-09 | `MAKER_SELF_ACCEPT` |
| 20 | `SLOT-GT-04` | gstack | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | WP-FHS-13 | `NACK_SHIP_POLICY` |
| 21 | `SLOT-SP-01` | Superpowers | UNKNOWN_NOT_STATED | METHOD.SUPERPOWERS | HOLD | WP-FHS-13 | `NACK_ADR` |
| 22 | `SLOT-SP-02` | Superpowers | UNKNOWN_NOT_STATED | METHOD.SUPERPOWERS | HOLD | WP-FHS-13 | `NACK_RED_PHASE` |
| 23 | `SLOT-SP-03` | Superpowers | UNKNOWN_NOT_STATED | METHOD.SUPERPOWERS | HOLD | WP-FHS-13 | `NACK_ROOT_CAUSE` |
| 24 | `SLOT-SP-04` | Superpowers | UNKNOWN_NOT_STATED | METHOD.SUPERPOWERS | HOLD | WP-FHS-13 | `NACK_COMPLETION_GATE` |

`consumer` 僅列 WP 代號，完整字串在 JSON；`NO_BINDING` 表示來源未給 Host/Pack 綁定（非推定值，理由在 `host_fit`）。
## 三、Method25（25 槽）

| # | slot_id | 方法 | 原用途（節錄） | licence | Host/Pack | 處置 | FirstFail |
|---|---|---|---|---|---|---|---|
| 1 | `METHOD-01` | BMAD-METHOD | BMAD bounded requirements map + human decisions | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | `PARALLEL_COMPILER` |
| 2 | `METHOD-02` | mattpocock/skills:grill-with-… | deduplicated QuestionLedger | MIT | METHOD.MATTPOCOCK_SKILLS | ADOPT_CANDIDATE | `NONE_DECLARED` |
| 3 | `METHOD-03` | mattpocock/skills:domain-mode… | DomainModel + Glossary + ADR conflict | MIT | METHOD.MATTPOCOCK_SKILLS | ADOPT_CANDIDATE | `NACK_DOMAIN_CONFLICT` |
| 4 | `METHOD-04` | mattpocock/skills:to-spec | SpecCandidate{atoms,ACC,source_refs} | MIT | METHOD.MATTPOCOCK_SKILLS | ADOPT_CANDIDATE | `SPEC_SEED_INCOMPLETE` |
| 5 | `METHOD-05` | mattpocock/skills:to-tickets | TaskSpecSeed+TicketCandidate local JSON | MIT | METHOD.MATTPOCOCK_SKILLS | ADOPT_CANDIDATE | `ISSUE_PUBLISH_DENIED` |
| 6 | `METHOD-06` | OpenSpec | ChangeDraft→SpecDelta→bounded patch/ref+archive… | UNKNOWN_NOT_STATED | SPEC.BROWNFIELD_OPENSPEC | HOLD | `NACK_SCOPE` |
| 7 | `METHOD-07` | Spec Kit | ConstBinding/Spec/Plan/TaskDAG | UNKNOWN_NOT_STATED | SPEC.GREENFIELD_SPEC_KIT | HOLD | `NACK_AUTHORITY` |
| 8 | `METHOD-08` | Superpowers | DesignDecision/RedGreenTrace/RootCause/ReviewGa… | UNKNOWN_NOT_STATED | METHOD.SUPERPOWERS | HOLD | `NACK_RED_PHASE` |
| 9 | `METHOD-09` | GitHub Actions | CI status checks/readback expectations | UNKNOWN_NOT_STATED | SUPPLY.CI_GITHUB_ACTIONS | HOLD | `CI_TRUST_BOUNDARY` |
| 10 | `METHOD-10` | MCP | TypedToolDescriptor/transport mapping | UNKNOWN_NOT_STATED | PROTO.MCP | DEFER | `MCP_SCOPE_DENIED` |
| 11 | `METHOD-11` | ACP | AgentMessageCandidate | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | `MESSAGE_TRUST_DENIED` |
| 12 | `METHOD-12` | OpenSSF Scorecard | ScorecardSignals and PolicyReview | UNKNOWN_NOT_STATED | SUPPLY.OSSF_SCORECARD | DEFER | `SCORECARD_PROXY` |
| 13 | `METHOD-13` | SLSA | SLSA ProvenanceExpectation | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | `PROVENANCE_MISSING` |
| 14 | `METHOD-14` | OWASP | negative fixtures and guarded failure expectati… | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | `SECURITY_PROXY` |
| 15 | `METHOD-15` | CodeQL | SARIF findings+query provenance | UNKNOWN_NOT_STATED | SEC.CODEQL | HOLD | `QUERY_PACK_UNTRUSTED` |
| 16 | `METHOD-16` | Semgrep | Rule ID/path/priority findings | UNKNOWN_NOT_STATED | SEC.SEMGREP | HOLD | `RULE_PIN_MISSING` |
| 17 | `METHOD-17` | Renovate | Renovate update proposal PR candidate | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | `SUPPLY_DEPENDENCY_FAIL` |
| 18 | `METHOD-18` | Dependabot | Dependabot update proposal (source-specific own… | UNKNOWN_NOT_STATED | NO_BINDING | DEFER | `OWNER_DECISION_REQUIRED` |
| 19 | `METHOD-19` | Cosign | Signature verification report | UNKNOWN_NOT_STATED | SUPPLY.ARTIFACT_ATTESTATION | HOLD | `SIGNER_SOD_FAIL` |
| 20 | `METHOD-20` | Syft | Syft SBOM (SPDX/CycloneDX) | UNKNOWN_NOT_STATED | SUPPLY.SBOM | HOLD | `SBOM_SUBJECT_MISMATCH` |
| 21 | `METHOD-21` | Trivy | Trivy scanner result+policy outcome | UNKNOWN_NOT_STATED | SEC.TRIVY | HOLD | `SCAN_TARGET_UNKNOWN` |
| 22 | `METHOD-22` | SQLite/FTS5 | SQLite schema/FTS5 index and query evidence | UNKNOWN_NOT_STATED | CORE.SQLITE | HOLD | `FTS_PROVENANCE_FAIL` |
| 23 | `METHOD-23` | FAR/FDA | Native owned FAR/FDA reference only | UNKNOWN_NOT_STATED | NO_FIT | NOFIT | `FABRIC_OWNER_REQUIRED` |
| 24 | `METHOD-24` | OpenAI Agents SDK | HITL pause/resume donor pattern | UNKNOWN_NOT_STATED | NO_BINDING | HOLD | `SDK_HOST_UNVERIFIED` |
| 25 | `METHOD-25` | Agent Skills specification | SKILL.md format and dependency validation | UNKNOWN_NOT_STATED | FORMAT.AGENT_SKILLS | DEFER | `HOST_NOT_LOADED` |

`NONE_DECLARED` 表示來源 NEG 未給錯誤碼（METHOD-02 的 NEG 是 fallback 指令，不是 code），未代填。
## 四、計數對帳（COUNT_RECONCILIATION）

藍圖稱 `Donor24` / `Method25`。本輪不補、不湊：

- Donor：量得 **24**，藍圖 **24**，差 **+0**。
- Method：量得 **25**，藍圖 **25**，差 **+0**。
- 49 與上游載體檔名 `WP16_TRANSLATION49.json` 相符；與他輪 49 筆身份集合完全一致（donor=True、method=True）。

理由與限制：

1. 逐一列舉**不在** CH-24／CH-25 正文。CH-24 僅以範圍指名 `SLOT-OS-01..04`、`SLOT-GT-01..04`、`SLOT-GS-01..04`，另以 `MP/SK/SP` 群組代稱；明寫的單一 ID 只有 3 個（`SLOT-GS-01`、`SLOT-GT-01`、`SLOT-OS-01`）。
2. CH-25 只斷言範圍 `METHOD-01..25`，明寫的單一 ID 為 4 個（`METHOD-01`、`METHOD-06`、`METHOD-10`、`METHOD-23`）。
3. 真正的逐項列舉在 `FHS-BODY-08`（`Donor24:SLOT-xx` / `Method25:METHOD-xx` 共 49 個 `####` 區塊），故 `source_ref` 綁 BODY-08 位元組，`chapter_ref` 綁 CH-24／CH-25 的範圍條款。
4. 24 與 25 內部無身份重複：donor 名稱雖有 6 組共用（OpenSpec／Spec Kit／mattpocock／GSD／gstack／Superpowers），但 `slot_id` 與 trigger／output 兩兩不同，屬同一 donor 的 4 個不同能力槽，不是重複條目。
5. 未出現需要剔除的重複或跨章拼湊，因此本輪無「量得少於藍圖」的缺口。

## 五、驗證

```
python tools/build_projection.py          # 產生兩張表
python tools/verify_projection.py         # 13 項檢查逐項 PASS
python tools/verify_projection.py --selftest   # 注入 5 種缺陷，抓到 5 種
```

驗證涵蓋：`source_ref` 重新切片逐字相等、`slot_id` 唯一、處置只允許四值、**ADOPT_CANDIDATE 不得帶 `UNKNOWN_NOT_STATED` licence**（違反即 FAIL 並要求降 HOLD）、已述 licence 必須有出處、章節回溯可重切。

## 六、保留與不主張

- 19 筆 HOLD 全部且僅因 licence 未述；8 筆 MIT 來自 DOC-04 研究表，未讀 upstream LICENSE／NOTICE digest。
- 49 筆 `host_qualification=NOT_OBSERVED`、install/load/invoke 未執行；原 Reader／Owner ACK 未觀測。
- 本輪**不**主張 TechnologyAdmission 已核、安裝已准、licence 已清、槽位已壓制。

## 七、交付物

| 檔案 | 用途 |
|---|---|
| `tables/DONOR24.json` | 24 筆 donor 槽投影（含 byte-exact source_ref） |
| `tables/METHOD25.json` | 25 筆 method 槽投影 |
| `tools/build_projection.py` | 由來源重建兩張表 |
| `tools/verify_projection.py` | 13 項檢查 + `--selftest`（5 種缺陷注入） |
| `tools/make_report.py` | 產生 SUMMARY／REPORT／crosscheck |
| `raw/verify_projection.log` | 驗證輸出（含 exit code） |
| `raw/verify_selftest.log` | 負向對照輸出 |
| `raw/crosscheck.json` | 章節範圍、licence 直方圖、他輪身份對帳 |

