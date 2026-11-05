# WP16｜W1 受影 Need/Occupant 綁定讀回（C3 lane）

> 只處理 W1 八個主責 WP 的受影子集。其餘 Need 逐筆留在 remainder，維持具名 `PIN_HOLD`，原 owner / resume 不變。
>
> `selected_not_installed=true`、`installs_performed=0`。本檔沒有任何 `INSTALLED`／`VERIFIED`／`SELECTED` 宣告。

## 0｜統計

| 指標 | 值 |
|---|---|
| Needs 分母 | 30 |
| consumed（W1 會消費） | 12 |
| bound | 1 |
| pin_hold | 29 |
| nofit | 0 |
| unbound | 0 |
| remainder（未消費，保留） | 18 |
| consumed + remainder | 30 |

`BOUND` 只代表 occupant 身份、version decision、license source ref 與具名 reader 四者都解析到來源指標；**artifact byte pin、Windows fit、host admission 一律仍是 HOLD**。

## 1｜W1 八 WP 分組

### WP02｜Fabric Policy（WP-FHS-02）

- W1 可即刻合法工作：FHS NAV → 原 Fabric Policy source reader，來源/epoch 候選建模
- 不得提前宣稱：ActivePolicy、loaded epoch、Policy effect 必須真 readback

| need_id | role | occupant | kind | version_pin | license_state | windows_fit | status |
|---|---|---|---|---|---|---|---|
| `Default30:P0-TOOL-026` | DESIGN_ONLY | AGENTS.md | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |

- `Default30:P0-TOOL-026` DESIGN_ONLY｜SOURCE.AGENTS_MD 唯讀 parser 只作為 NAV/source 輸入被引用；Fabric Policy 無 Default30 occupant，不綁
  - status_reason: role=DESIGN_ONLY under WP02; occupant never bound in this lane
  - license_source_ref: `DEFAULT30_CHOICES.json#/14/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/14/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/14/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `NOT_CONSUMED_BY_W1_EIGHT_WP`

### WP03｜HGK Control（WP-FHS-03）

- W1 可即刻合法工作：原 HGK Source Export／Registry 唯讀探索、Consumer envelope
- 不得提前宣稱：Original Issuer/ACL/Permit/WorkID 不由文檔或 GitHub 索引賦予

| need_id | role | occupant | kind | version_pin | license_state | windows_fit | status |
|---|---|---|---|---|---|---|---|
| `Default30:P0-TOOL-003` | CONSUMED | SRU Kernel | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |
| `Default30:P0-TOOL-025` | DESIGN_ONLY | Model Context Protocol | METHOD | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |
| `Default30:P0-TOOL-072` | CONSUMED | SQLite | METHOD | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |

- `Default30:P0-TOOL-003` CONSUMED｜CORE.SRU_KERNEL→HGK Native Registry/SourceReuse scoped resolver 正是 W1 唯讀探索的 registry 契約
  - status_reason: consumed by WP03 but occupant version/license still on original reader HOLD
  - license_source_ref: `DEFAULT30_CHOICES.json#/2/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/2/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/2/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`
- `Default30:P0-TOOL-025` DESIGN_ONLY｜PROTO.MCP→HGK Tool/Method registry 只在 Consumer envelope 設計中被引用；W1 不綁 MCP adapter
  - status_reason: role=DESIGN_ONLY under WP03; occupant never bound in this lane
  - license_source_ref: `DEFAULT30_CHOICES.json#/13/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/13/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/13/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `NOT_CONSUMED_BY_W1_EIGHT_WP`
- `Default30:P0-TOOL-072` CONSUMED｜CORE.SQLITE→HGK existing spine.py/DB host discovery 是 registry 落點的實際 store 契約
  - status_reason: consumed by WP03 but occupant version/license still on original reader HOLD
  - license_source_ref: `DEFAULT30_CHOICES.json#/29/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/29/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/29/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`

### WP04｜Hermes Runtime（WP-FHS-04）

- W1 可即刻合法工作：Profile/Journal/Worker API 設計、existing host readback 計畫
- 不得提前宣稱：Fresh PID/Loaded/Invoked/ActualServed 與 OPS effect 需當期主機證據

| need_id | role | occupant | kind | version_pin | license_state | windows_fit | status |
|---|---|---|---|---|---|---|---|
| `Default30:P0-TOOL-001` | CONSUMED | Hermes Agent | HOST | v0.22.5 DESIGN_BASELINE | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |
| `Default30:P0-TOOL-005` | DESIGN_ONLY | Codex | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |
| `Default30:P0-TOOL-006` | DESIGN_ONLY | OpenCode | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |
| `Default30:P0-TOOL-030` | CONSUMED | Loop Engineering | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |
| `Default30:P0-TOOL-034` | CONSUMED | Sub-Agent | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |

- `Default30:P0-TOOL-001` CONSUMED｜Profile/Journal/Worker API 設計以 RUNTIME.HERMES 這個 host 為 substrate；Notebook 需其 version/host_preflight 才可寫 API 契約
  - status_reason: consumed by WP04 but occupant version/license still on original reader HOLD
  - license_source_ref: `DEFAULT30_CHOICES.json#/0/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/0/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/0/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`
- `Default30:P0-TOOL-005` DESIGN_ONLY｜Codex 為 delegated code worker；W1 只做 Profile/Journal/Worker API 設計，不派工，故不綁
  - status_reason: role=DESIGN_ONLY under WP04; occupant never bound in this lane
  - license_source_ref: `DEFAULT30_CHOICES.json#/4/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/4/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/4/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `NOT_CONSUMED_BY_W1_EIGHT_WP`
- `Default30:P0-TOOL-006` DESIGN_ONLY｜OpenCode 為 alternate code worker adapter；W1 無派工/載入，故不綁
  - status_reason: role=DESIGN_ONLY under WP04; occupant never bound in this lane
  - license_source_ref: `DEFAULT30_CHOICES.json#/5/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/5/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/5/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `NOT_CONSUMED_BY_W1_EIGHT_WP`
- `Default30:P0-TOOL-030` CONSUMED｜Journal/Checkpoint 契約即 CORE.LOOP_ENGINEERING→SharedSpine reducer/Checkpoint；W1 需其 consumer 介面做 Journal 設計
  - status_reason: consumed by WP04 but occupant version/license still on original reader HOLD
  - license_source_ref: `DEFAULT30_CHOICES.json#/16/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/16/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/16/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`
- `Default30:P0-TOOL-034` CONSUMED｜Worker API 設計的 lease-bound child worker 語義來自 RUNTIME.SUB_AGENT consumer
  - status_reason: consumed by WP04 but occupant version/license still on original reader HOLD
  - license_source_ref: `DEFAULT30_CHOICES.json#/19/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/19/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/19/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`

### WP05｜PIPD Native Compiler（WP-FHS-05）

- W1 可即刻合法工作：按 SBL `integrations/pipd/` 讀源、PI/PD/ECP/TQAEP 隔離候選與 schema 契約
- 不得提前宣稱：Canonical compiler 真執行／SourceFreeze／RepoContext 受原 Reader/有效權限約束

| need_id | role | occupant | kind | version_pin | license_state | windows_fit | status |
|---|---|---|---|---|---|---|---|
| `Default30:P0-TOOL-002` | CONSUMED | SDLC_PRW | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |
| `Default30:P0-TOOL-004` | CONSUMED | DocETL | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |
| `Default30:P0-TOOL-008` | DESIGN_ONLY | LLM Wiki | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |
| `Default30:P0-TOOL-028` | CONSUMED | DESIGN.md | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |

- `Default30:P0-TOOL-002` CONSUMED｜CORE.SDLC_PRW→PIPD phase compiler 即 PI/PD 階段編譯的 consumer；W1 schema 契約需其 version/consumer
  - status_reason: consumed by WP05 but occupant version/license still on original reader HOLD
  - license_source_ref: `DEFAULT30_CHOICES.json#/1/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/1/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/1/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`
- `Default30:P0-TOOL-004` CONSUMED｜KNOWLEDGE.DOCETL→SBL/PIPD Document Reader 是 W1 讀源的 document reader 契約
  - status_reason: consumed by WP05 but occupant version/license still on original reader HOLD
  - license_source_ref: `DEFAULT30_CHOICES.json#/3/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/3/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/3/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`
- `Default30:P0-TOOL-008` DESIGN_ONLY｜LLM Wiki 屬 K09 wiki compiler；W1 PIPD 編譯不載入，故不綁
  - status_reason: role=DESIGN_ONLY under WP05; occupant never bound in this lane
  - license_source_ref: `DEFAULT30_CHOICES.json#/6/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/6/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/6/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `NOT_CONSUMED_BY_W1_EIGHT_WP`
- `Default30:P0-TOOL-028` CONSUMED｜SOURCE.DESIGN_MD→SBL TPM design reader 是 versioned DESIGN.md schema 契約來源
  - status_reason: consumed by WP05 but occupant version/license still on original reader HOLD
  - license_source_ref: `DEFAULT30_CHOICES.json#/15/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/15/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/15/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`

### WP07｜PLAN Commander（WP-FHS-07）

- W1 可即刻合法工作：原 PLAN/CAS 接口分析、候選計畫與 typed NEG
- 不得提前宣稱：真 CAS/受保護 PLAN effect 必須原 ACK/permit

| need_id | role | occupant | kind | version_pin | license_state | windows_fit | status |
|---|---|---|---|---|---|---|---|
| `Default30:P0-TOOL-010` | DESIGN_ONLY | Spec Kit | DONOR | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |
| `Default30:P0-TOOL-011` | CONSUMED | OpenSpec | DONOR | v1.16.0 DESIGN_BASELINE | LICENSE_DECLARED_HOST_ACK_PENDING | UNBOUND | **BOUND** |
| `Default30:P0-TOOL-017` | DESIGN_ONLY | Grill Me | METHOD | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |

- `Default30:P0-TOOL-010` DESIGN_ONLY｜Spec Kit 為 greenfield adapter；W1 只做 PLAN/CAS 接口分析與 typed NEG，不綁
  - status_reason: role=DESIGN_ONLY under WP07; occupant never bound in this lane
  - license_source_ref: `DEFAULT30_CHOICES.json#/7/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/7/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/7/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `NOT_CONSUMED_BY_W1_EIGHT_WP`
- `Default30:P0-TOOL-011` CONSUMED｜SPEC.BROWNFIELD_OPENSPEC proposal adapter 是候選計畫/proposal 形狀的唯一具體 occupant；W1 接口分析需其 version+license
  - status_reason: occupant identity + version decision + license source ref + named reader all resolved from source pointers
  - license_source_ref: `DEFAULT30_CHOICES.json#/8/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/8/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/8/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_HOST_ACK_PENDING`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`
- `Default30:P0-TOOL-017` DESIGN_ONLY｜Grill Me 為 QuestionLedger method slot；W1 typed NEG 只取形狀，不綁方法宿主
  - status_reason: role=DESIGN_ONLY under WP07; occupant never bound in this lane
  - license_source_ref: `DEFAULT30_CHOICES.json#/10/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/10/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/10/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `NOT_CONSUMED_BY_W1_EIGHT_WP`

### WP11｜Portable Host（WP-FHS-11）

- W1 可即刻合法工作：Source/Need/Host 對照、樣本/手冊/Loader SPEC
- 不得提前宣稱：真 Host install/load/invoke/卸載證據與授權

| need_id | role | occupant | kind | version_pin | license_state | windows_fit | status |
|---|---|---|---|---|---|---|---|
| `Default30:P0-TOOL-020` | DESIGN_ONLY | Superpowers | DONOR | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |
| `Default30:P0-TOOL-031` | CONSUMED | Harness Engineering | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |

- `Default30:P0-TOOL-020` DESIGN_ONLY｜Superpowers 為 Host Skill 方法槽；W1 只寫 Loader SPEC，不載入
  - status_reason: role=DESIGN_ONLY under WP11; occupant never bound in this lane
  - license_source_ref: `DEFAULT30_CHOICES.json#/11/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/11/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/11/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `NOT_CONSUMED_BY_W1_EIGHT_WP`
- `Default30:P0-TOOL-031` CONSUMED｜CORE.HARNESS_ENGINEERING→HGK native harness + Runner/Tool registry 是 Portable Host Loader SPEC 的對照宿主
  - status_reason: consumed by WP11 but occupant version/license still on original reader HOLD
  - license_source_ref: `DEFAULT30_CHOICES.json#/17/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/17/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/17/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`

### WP17｜CAP-BOOT（WP-FHS-17）

- W1 可即刻合法工作：Native/Default Required Need 落點、Windows fit／License 調查
- 不得提前宣稱：真 installer、Host admission、授權與 original Consumer ACK

| need_id | role | occupant | kind | version_pin | license_state | windows_fit | status |
|---|---|---|---|---|---|---|---|
| `Default30:P0-TOOL-024` | CONSUMED | Agent Skills | METHOD | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |

- `Default30:P0-TOOL-024` CONSUMED｜FORMAT.AGENT_SKILLS→SBL skills/ HostAdapter + Skill Loader 是 CAP-BOOT 最小 Native Occupant 落點；W1 需其 fit/license 調查對象
  - status_reason: consumed by WP17 but occupant version/license still on original reader HOLD
  - license_source_ref: `DEFAULT30_CHOICES.json#/12/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/12/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/12/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`

### WP20｜Host Kind Matrix（WP-FHS-20）

- W1 可即刻合法工作：192 Cell 適用性/NoFit 來源與設計測例
- 不得提前宣稱：多 Host/Mode 真 load/trigger/parity 不可由靜態表代替

| need_id | role | occupant | kind | version_pin | license_state | windows_fit | status |
|---|---|---|---|---|---|---|---|
| `Default30:P0-TOOL-032` | CONSUMED | Multi-Agent | HOST | PIN_UNBOUND | LICENSE_READER_HOLD | UNBOUND | **PIN_HOLD** |

- `Default30:P0-TOOL-032` CONSUMED｜RUNTIME.MULTI_AGENT→Hermes SWARM/Worker pool via HGK admission 是 Host/Mode cell 適用性的具體多工 cell
  - status_reason: consumed by WP20 but occupant version/license still on original reader HOLD
  - license_source_ref: `DEFAULT30_CHOICES.json#/18/license`
  - reader_ref: `DEFAULT30_CHOICES.json#/18/hold_owner`
  - host_ref: `DEFAULT30_CHOICES.json#/18/host_preflight`
  - hold_codes: `WINDOWS_FIT_UNBOUND`, `LICENSE_READER_HOLD`, `OCCUPANT_VERSION_PIN_HOLD`, `ARTIFACT_BYTE_PIN_HOLD`, `HOST_ADMISSION_PIN_HOLD`

## 2｜NOFIT 判斷

本輪 `nofit=0`，且**不是漏判**：全部 30 筆 `windows_fit` 皆為 `UNBOUND`，在無 fit 證據時宣告 NOFIT 等於無來源判斷。因此以具名 HOLD `NOFIT_JUDGMENT_BLOCKED_WINDOWS_FIT_UNBOUND` 取代，待原 Reader 回 Windows fit 證據後才做 NOFIT 判斷。

## 3｜HOLD 代碼彙總

| code | field | count | resolution |
|---|---|---|---|
| `ARTIFACT_BYTE_PIN_HOLD` | artifact_sha256 | 12 | W1 consumer records artifact sha256 at load time; not available in W0 closeout round |
| `HOST_ADMISSION_PIN_HOLD` | host_admission | 12 | Host admission/OPS evidence on the current Windows host; not claimed here |
| `LICENSE_HOST_ACK_PENDING` | license | 1 | Original Host License Reader issues the pending ACK for the exact artifact |
| `LICENSE_READER_HOLD` | license | 29 | Original License Reader returns license bytes + Host applicability for the exact artifact |
| `NOFIT_JUDGMENT_BLOCKED_WINDOWS_FIT_UNBOUND` | nofit | 12 | NOFIT cannot be asserted while windows_fit is UNBOUND for every Need; nofit count stays 0 with this named hold instead of an invented NOFIT |
| `NOT_CONSUMED_BY_W1_EIGHT_WP` | w1_scope | 18 | Resume when a W1/W3 WP actually consumes the Need; owner unchanged |
| `OCCUPANT_VERSION_PIN_HOLD` | version_pin | 28 | Original reader pins immutable artifact (tag+sha256) for the Need |
| `WINDOWS_FIT_UNBOUND` | windows_fit | 30 | Original Technology/License/Host Reader resolves per-Need Windows fit evidence |

## 4｜Remainder（未被 W1 消費，逐筆保留）

見 `WP16_REMAINDER_HOLDS.json`。共 18 筆，全部 `status=PIN_HOLD`，原 `hold` / `hold_owner` / `resume_predicate` 原樣保留。

| need_id | 原 hold | 原 owner（reader） | status | resumed_by |
|---|---|---|---|---|
| `Default30:P0-TOOL-005` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for RUNTIME.CODE_WORKER_PRIMAR | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-006` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for RUNTIME.CODE_WORKER_ALTERN | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-008` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for KNOWLEDGE.LLM_WIKI→SBL Kno | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-010` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for SPEC.GREENFIELD_SPEC_KIT→S | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-016` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for METHOD.MATTPOCOCK_SKILLS→T | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-017` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for METHOD.GRILL_ME→TPM Docume | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-020` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for METHOD.SUPERPOWERS→SBL bou | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-025` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for PROTO.MCP→HGK Tool/Method  | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-026` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for SOURCE.AGENTS_MD→Git repo  | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-053` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for OBS.OTEL→Host telemetry ex | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-059` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for SEC.SEMGREP→Security CI ru | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-060` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for SEC.CODEQL→Security CI or  | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-061` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for SEC.TRIVY→Security CI Triv | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-062` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for SUPPLY.CI_GITHUB_ACTIONS→S | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-063` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for SUPPLY.OSSF_SCORECARD→Secu | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-064` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for SUPPLY.SBOM→Release Owner  | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-065` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for SUPPLY.ARTIFACT_ATTESTATIO | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |
| `Default30:P0-TOOL-068` | OCCUPANT_PIN_HOLD | Original Technology/License/Host Reader for SEC.OSV→Security/vuln feed | PIN_HOLD | W1 eight-WP consume event or Explicit Owner release |

## 5｜已知界線

- 本 lane 為 `AUTHOR_LOCAL_TEST`：只跑本機 unittest，未取得任何原 Reader／Owner ACK。
- 無網路、未安裝任何 Need；`installs_performed=0`。
- `version_pin` 非 artifact byte pin；`DESIGN_BASELINE` 亦僅為設計基線。
- 未改寫前一輪 `NEED_OCCUPANT_MATRIX.json`；其狀態以 `inherited_matrix_status` 保留。
