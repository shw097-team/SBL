# R5 — 任務執行清單（TS00–TS25）

標記：`[x]` 本輪完成並具原始證據｜`[~]` 本輪部分（附缺口）｜`[ ]` OPEN_ACTIVE（未動，附 resume pointer）

| ID | 工程指令 | 本輪狀態 | 證據 / resume |
|---|---|---|---|
| TS00 | 本機 doctor：Git remote/branch/PR/CI/Release、HGK/Hermes/Fabric/PIPD 版本與權限 | [x] | `10_PREFLIGHT/ENV_SNAPSHOT.json` |
| TS01 | 讀取 14 DOC + 20 KP + 10 設計卷 + 2 Skill + R5，逐一 SHA | [x] | `10_PREFLIGHT/SOURCE_INTAKE.json` |
| TS02 | canonical compiler C0–C9 全案契約（lint→activation→acceptance→compile→duplication） | [x] | `contracts/compiled-r5/`、`30_CONTRACT/` |
| TS03 | HGK TaskSpec/WorkOrder/issue→task→PR DAG（有權限才啟動） | [~] | Kanban 卡＋`OROCHI_FACTORY_ORDER.v1`（`01_EXECUTION_SPEC.md` §0）；Native WorkOrder 仍 `NOT_GRANTED` |
| TS04 | SourceBound G-KNOW（doc/anchor/hash、CJK、負檢索、拒答） | [ ] | 沿用 R4 G-KNOW 殘留清單；resume：`TT-GKNOW-CJK-01` |
| **TS05** | **封閉 `F-R5-HARNESS-UNINSTALL-TRAVERSAL-001`**（窄修＋NEG/POS＋sentinel） | [x] | `20_TS05/`、candidate commit、CI |
| TS06 | wheel/sdist 真內容＋clean install SP load；c3 portable ZIP；release 文案漂移 | [~] | 真 wheel 驗證沿用 `tools/check_wheel_contents.py`；新發行未做 |
| TS07 | 50 Parent / 149 Child / P01–P07 / M00–M15 / GJ01–03 映射 | [ ] | R5 附錄 B 為分母；resume：`TT-TRACE-149-01` |
| TS08 | TPM 真需求/問題/決策記錄（JTBD/FUO、Quick/Guided/Critical） | [ ] | resume：`TS08` |
| TS09 | Guided SPEC 編譯（原子需求、PI/PD proposal、ACC/NEG、ADR/NFR） | [ ] | resume：`TS09` |
| TS10 | Kind/Mode/Host/Permission Selector + 39 gates | [ ] | 既有 `modes.mode_gate_matrix()` 39 cells 為基礎 |
| TS11 | Plan/Task DAG、OpenSpec brownfield delta/sync/archive、RepoContext | [ ] | resume：`TT-DONOR-GATE-01` |
| TS12 | PIPD 八 Skills → Native PI/PD/ECP/TQAEP 與 HGK WorkOrder/Permit | [ ] | `NOT_GRANTED`（需 Native Owner） |
| TS13 | 通用 Build engine：新 CLI/Skill/Minimal Agent 各一條真任務 | [ ] | resume：`TS13` |
| TS14 | Test→diagnose→bounded repair→retest→checkpoint/replay/rollback | [ ] | resume：`TS14` |
| TS15 | 三 SP 能力與隔離（各自 ZIP/identity/version） | [~] | R4 ZIP 已存在；本輪未重製 |
| TS16 | `C-016` TPM ChatGPT 私人 Plugin 真 create/install/@POS/@NEG/uninstall | [ ] | `NOT_HOST_INSTALLED`（無 Host 寫入通道） |
| TS17 | `C-017`/`C-018` 同流程 | [ ] | 同上 |
| TS18 | HGK Harness 獨立 installer/doctor/effect bridge/uninstall | [~] | TS05 修好卸載邊界；Native effect 仍 `NOT_GRANTED` |
| TS19 | SBL Full Stack 獨立分發與 Compose | [~] | R4 `LOCAL_STANDALONE_INSTALL`；未重測 |
| TS20 | 三 Journey + 16 Moments + 五工具 FUO 真使用者測試 | [ ] | resume：`TS20` |
| TS21 | 441 原件逐項 disposition | [ ] | frozen ledger 未改；resume：`TT-DONOR-GATE-02` |
| TS22 | 38 Surface 逐 C-ID disposition | [ ] | R5 §7 為基線；resume：`TS22` |
| TS23 | 供應鏈/秘密/SBOM/license/raw evidence/獨立 Checker | [~] | secret scan 本輪重跑；獨立 checker 見 §獨立性 |
| TS24 | approved candidate/evidence 分 SHA 推送 + 遠端 readback | [x] | 本輪 push 後 readback |
| TS25 | 14 DOC / 149 Child / 441 / 38 / 五工具 full-contract disposition | [ ] | 全案仍 `FAIL_FULL_CONTRACT`（誠實保持） |
