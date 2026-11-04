# SPEC_Architecture｜SPEC-Architecture-W0-wp15-local

> claim_ceiling=`AUTHOR_LOCAL_TEST`；native_effect=`NOT_RUN`；body_sha256=`56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a`
> 五個域階段與五條 seam 全部由 CH-37 表格與 SEAM_CONTRACTS.json 實算，未執行任何 Native 效果。

## §0 Subject Binding 與 Claim Ceiling

- subject_id: `FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001`
- body_sha256: `56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a`（463034 bytes）
- 與 Product／Program SPEC 共用同一 subject 區塊；本檔的差異欄位是 domain_stages／seams／principal_separation。

## §A1 五域階段界線（Fabric Policy→SBL Compiler→HGK Issuer→Hermes Worker→Checker/Publisher）

Fabric Policy → SBL 原 PIPD Compiler → HGK 唯一 Native Issuer → Hermes Worker → 原 Checker／Publisher 五個域界不得合併、不得由 W0 草案跨越。

| stage | 名稱 | 原 Canonical Owner／Writer | 綁定 seam | 禁止 | 章 |
|---|---|---|---|---|---|
| `STAGE-1-FABRIC-POLICY` | Fabric Policy（治理與 ActiveEpoch） | Fabric Policy Owner / FAR Reader | S4 | 不得由作者文件或以 W0 Draft 代替 ActivePolicyEpoch／LoadedDigest | `CH-17:846` |
| `STAGE-2-SBL-PIPD-COMPILER` | SBL 原 PIPD Compiler（canonical PI 唯一 Writer） | SBL-hosted PIPD canonical Compiler / Original Source Reader | S2, S3 | 作者草案不得產 canonical PI；PI/PD/ECP 只由原 Writer 編譯 | `CH-12:722` |
| `STAGE-3-HGK-NATIVE-ISSUER` | HGK 唯一 Native Issuer（SharedSpine／WorkID／permit） | HGK Original Issuer / SharedSpine | S4 | 不得存在第二 Issuer；無 permit 先 park | `CH-18:870` |
| `STAGE-4-HERMES-WORKER` | Hermes bounded Worker（Execution 角色） | Original Hermes bounded Worker/World Receiver | S5 | Worker 是執行角色，不是新的 Owner/Issuer；不得自簽 verdict | `CH-30:1232` |
| `STAGE-5-CHECKER-PUBLISHER` | 原 Checker／Publisher（獨立驗證與發布） | Original Protected Checker / Publisher | S5 | Maker 不得自任 Checker；不得以 W0 文件代替 Verdict／Release | `CH-38:1690` |

**入口接縫**：`S1` — W0 草案入口接縫：在五個域階段的任何 effect 之前先接收三份 SPEC

- 不併入五階段之理由：此接縫的原 Producer 是作者側 TPM、原 Reader 是 SBL Product/PIPD Intake；它不是 Fabric Policy／Compiler／Issuer／Worker／Checker 任一個既有域的正本，故列為入口而不併入五階段。
- 來源：`FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md:1491`
- 判定規則：entry seam = the seam not claimed by any of the five domain stages

## §A2 Seam ABI 表

| seam | wave | abi（宣告值） | abi state | reader_source_pin |
|---|---|---|---|---|
| `S1` | W0-A | `ORIGINAL_RUNTIME_ABI_UNBOUND` | `ORIGINAL_RUNTIME_ABI_UNBOUND` | `SOURCE31_PHYSICAL_IDENTITY.json` |
| `S2` | W1 | `19 original families / 13 CLI source pinned; runtime UNBOUND` | `19 original families / 13 CLI source pinned; runtime UNBOUND` | `SBL:integrations/pipd/src/pipd_ls_sp/cli.py@004e88913d5c` |
| `S3` | W1 | `19 original families / 13 CLI source pinned; runtime UNBOUND` | `19 original families / 13 CLI source pinned; runtime UNBOUND` | `SBL:integrations/pipd/src/pipd_ls_sp/pipeline.py@004e88913d5c` |
| `S4` | W1/W2 | `ORIGINAL_RUNTIME_ABI_UNBOUND` | `ORIGINAL_RUNTIME_ABI_UNBOUND` | `HG-KSEOS:b1_closure_20261028/evidence/signed_runner_registry.json@0143b50331f7` |
| `S5` | W2/W3/W4 | `ORIGINAL_RUNTIME_ABI_UNBOUND` | `ORIGINAL_RUNTIME_ABI_UNBOUND` | `HG-KSEOS:src/hg_kseos/native_admission.py@0143b50331f7` |

- 五條 seam 的 ABI 皆未綁定原 runtime；W0 只交 typed 期望值與 fixture SHA。

## §A3 Seam Reader／Consumer

| seam | original_reader | ABI/Reader cell（正文） | consumer alias | ACK |
|---|---|---|---|---|
| `S1` | SBL Product / Source Reader | Original SBL Product/Program/PIPD Intake Reader | SBL Product / Source Reader | `NOT_OBSERVED` |
| `S2` | SBL original PIPD Intake/Profile/PI Reader | Current original PIPD DOC02 Compiler+Authority/Profile Reader | SBL original PIPD Intake/Profile/PI Reader | `NOT_OBSERVED` |
| `S3` | SBL original RepoContext/PD/ECP Reader | Original RepoContext/Effect Registry/ECP Reader | SBL original RepoContext/PD/ECP Reader | `NOT_OBSERVED` |
| `S4` | Fabric original Policy + HGK single Issuer | ActiveEpoch/LoadedDigest+HGK Registry/SharedSpine/Issuer | Fabric original Policy + HGK single Issuer | `NOT_OBSERVED` |
| `S5` | Hermes original durable Runtime + original independent Checker | Original WorldRaw + Protected Checker/Publisher | Hermes original durable Runtime + original independent Checker | `NOT_OBSERVED` |

## §A4 Effect 與 Permission

| seam | permission mode | matched token | effect class | executed |
|---|---|---|---|---|
| `S1` | `ISOLATED_DRAFT_WRITE` | `SPECDraft` | `no_world_effect_at_this_seam` | `NOT_RUN` |
| `S2` | `CANONICAL_WRITER_HANDOFF` | `ACK` | `no_world_effect_at_this_seam` | `NOT_RUN` |
| `S3` | `READ_ONLY_REPO_BIND` | `不寫世界` | `no_world_effect_at_this_seam` | `NOT_RUN` |
| `S4` | `PROTECTED_EFFECT_ADMISSION` | `permit` | `protected_world_effect` | `NOT_RUN` |
| `S5` | `WORLD_EFFECT_CHECKED` | `WorldRaw` | `protected_world_effect` | `NOT_RUN` |

- permission 由該 seam 列的用字決定（WorldRaw > permit > 不寫世界 > ACK > SPECDraft 之優先序），原 ACL 一律 `NOT_OBSERVED`。

## §A5 POS／NEG／FirstFail 晶格

| seam | POS | NEG | firstfail primary | expected |
|---|---|---|---|---|
| `S1` | 具 FUO+ACC± | 雙轉 Canonical PI→SPEC_NOT_SOURCE_BOUND；可刪隔離 Draft | `SPEC_IDENTITY_OR_SOURCE_MISMATCH` | `SPEC_IDENTITY_OR_SOURCE_MISMATCH` |
| `S2` | 原 5 namespace/Parent/NEG intact | `_profile_meta` schema → PI_SCHEMA_NACK；無 ACK 則不 promotion | `CANONICAL_WRITER_BOUNDARY` | `CANONICAL_WRITER_BOUNDARY` |
| `S3` | real Repo bind | stale HEAD/out-of-scope→REPO_BIND_HOLD；不寫世界 | `HOST_REPOCONTEXT_UNBOUND` | `HOST_REPOCONTEXT_UNBOUND` |
| `S4` | exact token/cas | source/epoch mismatch→ADMISSION_NACK；無 permit 先 park | `HOST_POLICY_EFFECTIVE_LOAD_HOLD` | `HOST_POLICY_EFFECTIVE_LOAD_HOLD` |
| `S5` | world diff/rollback/negative tested | fake raw/signer→INDEPENDENCE_NACK；UNKNOWN先 reconcile | `UNKNOWN_RECONCILE_REQUIRED` | `UNKNOWN_RECONCILE_REQUIRED` |

全域 firstfail：`SPEC_NOT_SOURCE_BOUND`, `FUO_NOT_OBSERVABLE`, `CANONICAL_WRITER_BOUNDARY`, `ORACLE_RUNNER_BIND_HOLD`

## §A6 Stop／Resume／Rollback

| seam | stop | resume | rollback |
|---|---|---|---|
| `S1` | Only affected seam/world promotion | Original SBL Product / Source Reader supplies same Subject/Candidate/Source/Scope/Host/PolicyEpoch ACK and ra… | Withdraw this seam request; retain old candidate and original journal… |
| `S2` | Only affected seam/world promotion | Original SBL original PIPD Intake/Profile/PI Reader supplies same Subject/Candidate/Source/Scope/Host/PolicyE… | Withdraw this seam request; retain old candidate and original journal… |
| `S3` | Only affected seam/world promotion | Original SBL original RepoContext/PD/ECP Reader supplies same Subject/Candidate/Source/Scope/Host/PolicyEpoch… | Withdraw this seam request; retain old candidate and original journal… |
| `S4` | Only affected seam/world promotion | Original Fabric original Policy + HGK single Issuer supplies same Subject/Candidate/Source/Scope/Host/PolicyE… | Withdraw this seam request; retain old candidate and original journal… |
| `S5` | Only affected seam/world promotion | Original Hermes original durable Runtime + original independent Checker supplies same Subject/Candidate/Sourc… | Withdraw this seam request; retain old candidate and original journal… |

## §A7 單一 Writer 與 No-Second-Issuer

本草案屬 W0:DraftMaker / AUTHOR_DESIGN_ONLY；SBL/PIPD/Fabric/HGK Canonical Writers、原 HGK Issuer、Protected Checker、Publisher 全部不移轉。

- 不移轉：SBL Canonical Writer
- 不移轉：PIPD Canonical Writer
- 不移轉：Fabric Canonical Writer
- 不移轉：HGK Issuer
- 不移轉：Protected Checker
- 不移轉：Publisher
- 來源：`FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md:129`

## §A8 Principal 分離：唯一 Human Owner ≠ Maker／Issuer／Checker

**斷言**：唯一 Human Owner 不是 Maker／Issuer／Checker 同一個技術 Principal。

| Principal | 角色 | 不得兼任 |
|---|---|---|
| 唯一 Human Owner（1 人） | 授權與取捨 | 不得自任 Checker |
| Maker（W0 DraftMaker／Hermes bounded Worker：執行角色） | 技術執行 | 不得升格為 Owner |
| Issuer（HGK Original Issuer：permit 與 WorkID） | 技術執行 | 不得升格為 Owner |
| Checker（Original Protected Checker：獨立 Verdict） | 技術執行 | 不得升格為 Owner |

- 模型／工具原生 Worker 是執行角色，非新的 Owner/Issuer（`FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md:226`）
- 混同一個 Human Owner 與技術 Checker 身分是 NEG 拒收（`FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md:204`）
- 三職能被當三個獨立 Principal 屬 NEG（`FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md:679`）
- Canonical Writer／Issuer／Checker／Publisher 全部不移轉（`FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md:129`）

### ADR（由 Architecture-kind W0_REQUIRED 需求列實算，共 8 條）

| ADR | 決策 | 被拒方案 | requirement |
|---|---|---|---|
| `ADR-INT-10` | 31 冊兩 Scope、U0–U4、四表、Parent/NEG preserved | NEG：只計 949 筆字串，漏掉 Parent NEG/例外仍宣全義接受 | `INT-10` |
| `ADR-INT-11` | 有權原 Writer/Owner 決定有效版本、比對 Same Scope | NEG：README／作者文件 SHA 當 Original Effective Canonical | `INT-11` |
| `ADR-FHS-DR-014` | 31 冊原位身份與 31 snapshot sha 不丟失 | 31/31 bytes/sha 檔案映射可重算 | `FHS-DR-014` |
| `ADR-FHS-DR-015` | 每個原 Parent/Child/NEG/Exception/Applicability 必保存 | 每個原 ID 有候選或具名 HOLD | `FHS-DR-015` |
| `ADR-FHS-DR-019` | 複合「各有/分別/對應」依原作用域拆需求 | 該 Parent 子 claim 的 POS+NEG 個別讀回 | `FHS-DR-019` |
| `ADR-FHS-DR-020` | 來源 Currentness 由原有權 Reader 讀回 | 新舊版本衝突不會被靜默覆蓋 | `FHS-DR-020` |
| `ADR-FHS-DR-046` | SOURCE_READ 只需合法來源/ACL/Locator/SourceSHA | 短 READ 有用結果 | `FHS-DR-046` |
| `ADR-FHS-DR-054` | r4 U0–U4 全量語義保存，四 JSONL 是候選事實表 | 所有非空片段有處置或 HOLD | `FHS-DR-054` |

### Open holds
- 五 seam 的 original_abi 全為 ORIGINAL_RUNTIME_ABI_UNBOUND；無任何 ABI 真綁定
- S2–S5 的 original Reader ACK 皆 NOT_OBSERVED；W0 只停在 AUTHOR_DESIGN
- H-ABI-05：HGK reducer enum／OperationType／S3–S5 Receiver ABI 未綁
