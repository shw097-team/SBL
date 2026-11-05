# SPEC_Program｜SPEC-Program-W0-wp15-local

> claim_ceiling=`AUTHOR_LOCAL_TEST`；native_effect=`NOT_RUN`；body_sha256=`56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a`
> 每個數字都由 registry 實算並附 source_ref；本檔不含 WP 執行、不含 Native 收據。

## §0 Subject Binding 與 Claim Ceiling

- subject_id: `FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001`
- body_sha256: `56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a`
- 與 Product／Architecture 同 Subject；本檔差異欄位是 work_packages／edges／counts。

## §P1 WP 矩陣（22）

共 **22** 個 WP（`WP-FHS-00` → `WP-FHS-21`）。

| WP | name | primary_wave | dependencies |
|---|---|---|---|
| `WP-FHS-00` | WP-FHS-00` Source/Host Discovery` | W0 | - |
| `WP-FHS-01` | WP-FHS-01` Authority/Oracle/Profile` | W0 | `WP-FHS-00` |
| `WP-FHS-02` | WP-FHS-02` Fabric Policy Consumer` | W1 | `WP-FHS-01` |
| `WP-FHS-03` | WP-FHS-03` HGK Registry/Issuer` | W1 | `WP-FHS-01` |
| `WP-FHS-04` | WP-FHS-04` Hermes Durable Runtime` | W1 | `WP-FHS-00` |
| `WP-FHS-05` | WP-FHS-05` PIPD Native Compiler` | W1 | `WP-FHS-01` |
| `WP-FHS-06` | WP-FHS-06` Legal First Reversible Slice` | W2 | `WP-FHS-02`, `WP-FHS-03`, `WP-FHS-04`, `WP-FHS-05`, `WP-FHS-17` |
| `WP-FHS-07` | WP-FHS-07` Native PLAN Commander A/B/C` | W1 | `WP-FHS-01`, `WP-FHS-15` |
| `WP-FHS-08` | WP-FHS-08` FHS Execute Worker` | W2 | `WP-FHS-06`, `WP-FHS-07` |
| `WP-FHS-09` | WP-FHS-09` Challenge/Protected AO` | W2 | `WP-FHS-08`, `WP-FHS-21` |
| `WP-FHS-10` | WP-FHS-10` B1 3 GWO & G-A/G-B` | W3 | `WP-FHS-09`, `WP-FHS-20` |
| `WP-FHS-11` | WP-FHS-11` Portable Host Dogfood` | W1 | `WP-FHS-05`, `WP-FHS-16` |
| `WP-FHS-12` | WP-FHS-12` W18 Normal Mode` | W3 | `WP-FHS-10`, `WP-FHS-11` |
| `WP-FHS-13` | WP-FHS-13` CAP On-Demand + HotSwap` | W3 | `WP-FHS-16`, `WP-FHS-17` |
| `WP-FHS-14` | WP-FHS-14` Release/Retire Candidate` | W4 | `WP-FHS-09`, `WP-FHS-19` |
| `WP-FHS-15` | WP-FHS-15` TPM Corpus & SPEC 18Stage` | W0 | `WP-FHS-00` |
| `WP-FHS-16` | WP-FHS-16` Donor/Method Slot Translation` | W0 | `WP-FHS-00` |
| `WP-FHS-17` | WP-FHS-17` CAP-BOOT Native Occupants` | W1 | `WP-FHS-00`, `WP-FHS-02`, `WP-FHS-03` |
| `WP-FHS-18` | WP-FHS-18` FAR Bounded Repair & Incident` | W2 | `WP-FHS-08` |
| `WP-FHS-19` | WP-FHS-19` CI/Supply Chain & Requal` | W0 | `WP-FHS-00` |
| `WP-FHS-20` | WP-FHS-20` CLI/Agent/Host Kind Matrix` | W1 | `WP-FHS-05`, `WP-FHS-16` |
| `WP-FHS-21` | WP-FHS-21` Challenge 96/H4/SEAM Coverage` | W0 | `WP-FHS-01` |

## §P2 DAG 邊（36）

共 **36** 條邊；波次分佈：W0→W0=5, W0→W1=9, W0→W2=1, W0→W3=1, W0→W4=1, W1→W1=4, W1→W2=6, W1→W3=3, W2→W2=3, W2→W3=1, W2→W4=1, W3→W3=1。

| edge | predecessor | successor | wave |
|---|---|---|---|
| `E01` | `WP-FHS-00` | `WP-FHS-01` | W0→W0 |
| `E02` | `WP-FHS-01` | `WP-FHS-02` | W0→W1 |
| `E03` | `WP-FHS-01` | `WP-FHS-03` | W0→W1 |
| `E04` | `WP-FHS-00` | `WP-FHS-04` | W0→W1 |
| `E05` | `WP-FHS-01` | `WP-FHS-05` | W0→W1 |
| `E06` | `WP-FHS-02` | `WP-FHS-06` | W1→W2 |
| `E07` | `WP-FHS-03` | `WP-FHS-06` | W1→W2 |
| `E08` | `WP-FHS-04` | `WP-FHS-06` | W1→W2 |
| `E09` | `WP-FHS-05` | `WP-FHS-06` | W1→W2 |
| `E10` | `WP-FHS-17` | `WP-FHS-06` | W1→W2 |
| `E11` | `WP-FHS-01` | `WP-FHS-07` | W0→W1 |
| `E12` | `WP-FHS-15` | `WP-FHS-07` | W0→W1 |
| `E13` | `WP-FHS-06` | `WP-FHS-08` | W2→W2 |
| `E14` | `WP-FHS-07` | `WP-FHS-08` | W1→W2 |
| `E15` | `WP-FHS-08` | `WP-FHS-09` | W2→W2 |
| `E16` | `WP-FHS-21` | `WP-FHS-09` | W0→W2 |
| `E17` | `WP-FHS-09` | `WP-FHS-10` | W2→W3 |
| `E18` | `WP-FHS-20` | `WP-FHS-10` | W1→W3 |
| `E19` | `WP-FHS-05` | `WP-FHS-11` | W1→W1 |
| `E20` | `WP-FHS-16` | `WP-FHS-11` | W0→W1 |
| `E21` | `WP-FHS-10` | `WP-FHS-12` | W3→W3 |
| `E22` | `WP-FHS-11` | `WP-FHS-12` | W1→W3 |
| `E23` | `WP-FHS-16` | `WP-FHS-13` | W0→W3 |
| `E24` | `WP-FHS-17` | `WP-FHS-13` | W1→W3 |
| `E25` | `WP-FHS-09` | `WP-FHS-14` | W2→W4 |
| `E26` | `WP-FHS-19` | `WP-FHS-14` | W0→W4 |
| `E27` | `WP-FHS-00` | `WP-FHS-15` | W0→W0 |
| `E28` | `WP-FHS-00` | `WP-FHS-16` | W0→W0 |
| `E29` | `WP-FHS-00` | `WP-FHS-17` | W0→W1 |
| `E30` | `WP-FHS-02` | `WP-FHS-17` | W1→W1 |
| `E31` | `WP-FHS-03` | `WP-FHS-17` | W1→W1 |
| `E32` | `WP-FHS-08` | `WP-FHS-18` | W2→W2 |
| `E33` | `WP-FHS-00` | `WP-FHS-19` | W0→W0 |
| `E34` | `WP-FHS-05` | `WP-FHS-20` | W1→W1 |
| `E35` | `WP-FHS-16` | `WP-FHS-20` | W0→W1 |
| `E36` | `WP-FHS-01` | `WP-FHS-21` | W0→W0 |

## §P3 E26 方向裁決

**方向**：`WP-FHS-19→WP-FHS-14`（E26），wave=W0→W4。

- operation：**WP19 的 CI／License／NOTICE／SBOM 原掃描 Raw 作為 WP14 Release 候選的供應鏈前置**；W0 只出設計契約與 typed 期望值，不產生也不替代該 Raw
- blocking_rule：Hard：WP14 的 `RELEASE` effect 必須有同 Subject／Scope 的原 CI Raw 與原 Publisher 收據；只交 TraceClosure 即標 WP19 DONE 為拒收
- firstfail：`WP19_ORIGINAL_OUTPUT_MISSING`；secondary：`ORIGINAL_DAG_EDGE_MISSING`
- original_reader_ack：`NOT_OBSERVED`
- 正文條款：CH-37 §r4-candidate E26 與六個 W0 主責 WP 的逐操作綁定

拒收點：
- traceclosure_substituted_for_ci_raw → `WP19_ORIGINAL_OUTPUT_MISSING`
- edge_deleted → `ORIGINAL_DAG_EDGE_MISSING`
- primary_wave_rewritten_to_delivery_wave → `WAVE_PRIMARY_CONFLATION`

## §P4 Design84 卡與 25 跨波

共 **84** 張 Design Card，其中 **25** 張跨波語義歧義（JOIN_AMBIGUOUS_AFFECTED）。

| DesignID | requirement_delivery_wave | primary_wp_id | wp_primary_wave | scope |
|---|---|---|---|---|
| `INT-01` | W0 | `WP-FHS-15` | W0 | NO_WP_WAVE_CONFLICT |
| `INT-02` | W3 | `WP-FHS-20` | W1 | JOIN_AMBIGUOUS_AFFECTED |
| `INT-03` | W0 | `WP-FHS-15` | W0 | NO_WP_WAVE_CONFLICT |
| `INT-04` | W0 | `WP-FHS-15` | W0 | NO_WP_WAVE_CONFLICT |
| `INT-05` | W1 | `WP-FHS-03` | W1 | NO_WP_WAVE_CONFLICT |
| `INT-06` | W1 | `WP-FHS-05` | W1 | NO_WP_WAVE_CONFLICT |
| `INT-07` | W1 | `WP-FHS-04` | W1 | NO_WP_WAVE_CONFLICT |
| `INT-08` | W2 | `WP-FHS-08` | W2 | NO_WP_WAVE_CONFLICT |
| `INT-09` | W2 | `WP-FHS-08` | W2 | NO_WP_WAVE_CONFLICT |
| `INT-10` | W0 | `WP-FHS-01` | W0 | NO_WP_WAVE_CONFLICT |
| `INT-11` | W0 | `WP-FHS-00` | W0 | NO_WP_WAVE_CONFLICT |
| `INT-12` | W0 | `WP-FHS-15` | W0 | NO_WP_WAVE_CONFLICT |
| `INT-13` | W1 | `WP-FHS-05` | W1 | NO_WP_WAVE_CONFLICT |
| `INT-14` | W1 | `WP-FHS-11` | W1 | NO_WP_WAVE_CONFLICT |

（其餘 70 張全量見 JSON `design84.cards`。）

**25 張跨波卡**：`INT-02`, `INT-17`, `INT-21`, `INT-24`, `FHS-DR-001`, `FHS-DR-004`, `FHS-DR-005`, `FHS-DR-006`, `FHS-DR-009`, `FHS-DR-010`, `FHS-DR-011`, `FHS-DR-013`, `FHS-DR-017`, `FHS-DR-018`, `FHS-DR-023`, `FHS-DR-028`, `FHS-DR-029`, `FHS-DR-034`, `FHS-DR-042`, `FHS-DR-043`, `FHS-DR-044`, `FHS-DR-049`, `FHS-DR-052`, `FHS-DR-057`, `FHS-DR-059`

## §P5 W0_REQUIRED22

共 **22** 筆 W0_REQUIRED；spec_kind 分佈：Architecture=8, Product=11, Program=3。

| RequirementID | spec_kind | primary_wp_id | wave | deliver_id | chapters |
|---|---|---|---|---|---|
| `INT-01` | Product | `WP-FHS-15` | W0 | `DEL-W0-INT-01` | CH-01, CH-10 |
| `INT-03` | Product | `WP-FHS-15` | W0 | `DEL-W0-INT-03` | CH-01, CH-38 |
| `INT-04` | Product | `WP-FHS-15` | W0 | `DEL-W0-INT-04` | CH-15, CH-18, CH-38 |
| `INT-10` | Architecture | `WP-FHS-01` | W0 | `DEL-W0-INT-10` | CH-03, CH-05, CH-06, CH-07 |
| `INT-11` | Architecture | `WP-FHS-00` | W0 | `DEL-W0-INT-11` | CH-00, CH-04, CH-17 |
| `INT-12` | Product | `WP-FHS-15` | W0 | `DEL-W0-INT-12` | CH-11 |
| `INT-18` | Product | `WP-FHS-15` | W0 | `DEL-W0-INT-18` | CH-15, CH-39, CH-43 |
| `INT-23` | Program | `WP-FHS-00` | W0 | `DEL-W0-INT-23` | CH-37 |
| `FHS-DR-002` | Product | `WP-FHS-15` | W0 | `DEL-W0-FHS-DR-002` | - |
| `FHS-DR-003` | Product | `WP-FHS-15` | W0 | `DEL-W0-FHS-DR-003` | - |
| `FHS-DR-014` | Architecture | `WP-FHS-00` | W0 | `DEL-W0-FHS-DR-014` | - |
| `FHS-DR-015` | Architecture | `WP-FHS-01` | W0 | `DEL-W0-FHS-DR-015` | - |
| `FHS-DR-019` | Architecture | `WP-FHS-01` | W0 | `DEL-W0-FHS-DR-019` | - |
| `FHS-DR-020` | Architecture | `WP-FHS-00` | W0 | `DEL-W0-FHS-DR-020` | - |
| `FHS-DR-021` | Product | `WP-FHS-15` | W0 | `DEL-W0-FHS-DR-021` | - |
| `FHS-DR-022` | Product | `WP-FHS-15` | W0 | `DEL-W0-FHS-DR-022` | - |
| `FHS-DR-046` | Architecture | `WP-FHS-00` | W0 | `DEL-W0-FHS-DR-046` | - |
| `FHS-DR-047` | Product | `WP-FHS-15` | W0 | `DEL-W0-FHS-DR-047` | - |
| `FHS-DR-053` | Program | `WP-FHS-00` | W0 | `DEL-W0-FHS-DR-053` | - |
| `FHS-DR-054` | Architecture | `WP-FHS-01` | W0 | `DEL-W0-FHS-DR-054` | - |
| `FHS-DR-055` | Product | `WP-FHS-15` | W0 | `DEL-W0-FHS-DR-055` | - |
| `FHS-DR-056` | Program | `WP-FHS-15` | W0 | `DEL-W0-FHS-DR-056` | - |

本 SPEC 直接綁定的 Program-kind RequirementID：`FHS-DR-053`, `FHS-DR-056`, `INT-23`。
（其餘 19 筆屬 Product／Architecture 的欄位責任，見各自 SPEC，不在此重複認領。）

## §P6 章圖 CH-00..49

共 **50** 個 H1 章（`CH-00` → `CH-49`）；章表 50 列。

| CH | title | primary wave | body line |
|---|---|---|---|
| `CH-00` | 正式入口、主體法位、不可降級 H1 規則 | W0 | 117 |
| `CH-01` | FHS 產品定位、Owner／JTBD／FUO 和非目標 | W0 | 118 |
| `CH-02` | 七大痛點、原始動機與逐產品旅程 | W0 | 119 |
| `CH-03` | 功能需求、OriginalID、強弱語義及完整不變量 | W0 | 120 |
| `CH-04` | 31 冊 SourceFreeze、AuthorityBinding、Currentness、版本衝突 | W0 | 121 |
| `CH-05` | U0 全位元組內容盤點：表格、負條件、Code、原版附錄 | W0 | 122 |
| `CH-06` | U1 子要求逐義拆解：各有／分別／對應／若／不得 | W0 | 123 |
| `CH-07` | U2–U4 Crosswalk、版本去向、Owner 語義核簽與反例 | W0 | 124 |
| `CH-08` | SBL SharedCore 六模組與三 SP 的完整產品鏈 | W1 | 125 |
| `CH-09` | 八 Kind、三 Mode、四 Host、16 Moments、38 Delivery Surfaces | W3 | 126 |
| `CH-10` | 已知答案、Source-bound 檢索、FAR／知識服務 | W0 | 127 |
| `CH-11` | TPM 三 SPEC：Product、Architecture、Program 與 18 Stage | W0 | 128 |
| `CH-12` | PIPD 13 CLI／19 Contract Families／8 Skills 與唯一 Writer | W1 | 129 |
| `CH-13` | Authority SourceFreeze／Profile Tailoring／原 PI 的 18 領域 | W1 | 130 |
| `CH-14` | PD-01..10、RepoContext Currentness、Scope 與晚綁 | W1 | 131 |
| `CH-15` | ConstructionContract／ECP：DEV、OPS、USER、RELEASE 不混用 | W2 | 132 |
| `CH-16` | 跨庫 Typed ABI、Producer→Consumer、Same Subject 交接 | W1 | 133 |
| `CH-17` | Fabric Policy／FAR／治理鏡像與 FHS 工程入口 | W1 | 134 |
| `CH-18` | HG-KSEOS 唯一 Native Issuer／SharedSpine／WorkID／許可 | W1 | 135 |
| `CH-19` | Hermes 三 Lane、模型路由、Profiles、ActualServed | W1 | 136 |
| `CH-20` | Hermes Native Kanban／Delegation／Swarm／長任務編排 | W1 | 137 |
| `CH-21` | Windows Host／CLI／Plugin／Skill：安裝與實際載入三段驗收 | W3 | 138 |
| `CH-22` | Native20：現役唯一原生核心與維護權 | W1 | 139 |
| `CH-23` | Default30：默認能力、可配置佔用與 NoFit | W3 | 140 |
| `CH-24` | Donor24：可借用外部輪子與授權條件 | W3 | 141 |
| `CH-25` | Method25：演算法／流程工具方法的原用途 | W3 | 142 |
| `CH-26` | TECH386：逐原 ID 技術功能與非降級 Disposition | W3 | 143 |
| `CH-27` | SBL 50 Parent／149 Child：原生產品分母專章 | W3 | 144 |
| `CH-28` | R15 949 原產品原子與 B1 66／254／629 映射 | W3 | 145 |
| `CH-29` | Kind×Mode×Host×LegacyToken 192 Cell 的原始逐格行為 | W3 | 146 |
| `CH-30` | Original 96 Oracle：Test Class×Oracle 的型別與逐格準則 | W3 | 147 |
| `CH-31` | Acceptance Challenge 15 條異構 Sender→Receiver Edge | W2 | 148 |
| `CH-32` | B1 120 Parent／124 Child／38 Node＝282 Case 的獨立驗收 | W3 | 149 |
| `CH-33` | B1 原 27 PI→31 PD Slot：拓撲與 Effect ECP | W3 | 150 |
| `CH-34` | Portable Commander Guide A／B／C 與原 Native PLAN | W1 | 151 |
| `CH-35` | FHS-EXECUTE：Lease、Journal、UNKNOWN、World Reconcile | W2 | 152 |
| `CH-36` | B1 自舉與 W18：Fresh PID 普通 Goal 的第一成果 | W3 | 153 |
| `CH-37` | Program SPEC：W0～W3、原 22 WP／36 DAG 邊及 W0-A/B | W0 | 154 |
| `CH-38` | 最小 Native E2E、GJ01–03、Golden/V2-T 與停止規則 | W2 | 155 |
| `CH-39` | 安全：SoD、Process ACL、秘鑰、原授權、Consent/Privacy | W1 | 156 |
| `CH-40` | 三 SPEC／PI／PD／ECP／TQAEP 對原 Reader 的交接矩陣 | W1 | 157 |
| `CH-41` | TQAEP：POS／NEG／FirstFail／獨立 Oracle 的可執行計畫 | W2 | 158 |
| `CH-42` | 來源／要求／Case／Evidence／Delivery LEDGER：一筆一真值 | W0 | 159 |
| `CH-43` | ClaimCeiling、測量層、Producer/Checker/Publisher 的不同責任 | W4 | 160 |
| `CH-44` | CI、供應鏈、部署、Cutover、Rollback 的原服務區分 | W4 | 161 |
| `CH-45` | L0–L3 文件包、DELIVER、原 Consumer ACK 與長期可維護性 | W4 | 162 |
| `CH-46` | 成本／FinOps／KnownAnswer 復用及三種 Dogfood Loop | W3 | 163 |
| `CH-47` | OpenSpec、gstack、Hermes 外部研究與 Build-or-Use 准入 | W3 | 164 |
| `CH-48` | 受界 ChangeSet、風險／具名 HOLD、Stop-Resume 與決策閉環 | W0 | 165 |
| `CH-49` | 逐章正式驗收標準、H1 防壓平測試與裁決 | W4 | 166 |

## §P7 Source31

共 **31** 冊原始 Source（SBL 14／FHS 17）。

| SourceID | original_name | bytes | lines | sha256（前 16） |
|---|---|---|---|---|
| `SBL-DOC-00` | SBL_PIPD-LS-PKG_DOC-00(1).md | 465363 | 1591 | `bd9c1a85ea0cae68` |
| `SBL-DOC-01` | SBL_PIPD-LS-PKG_DOC-01(1).md | 1041962 | 4938 | `43a0a7ed26d2adf9` |
| `SBL-DOC-02` | SBL_PIPD-LS-PKG_DOC-02(1).md | 1148207 | 11084 | `4ff0cda5ab00ba5f` |
| `SBL-DOC-03` | SBL_PIPD-LS-PKG_DOC-03(1).md | 1704253 | 4851 | `ea69e1d3718ed86a` |
| `SBL-DOC-04` | SBL_PIPD-LS-PKG_DOC-04(1).md | 618110 | 3036 | `ee90cb1c86f6f735` |
| `SBL-DOC-05` | SBL_PIPD-LS-PKG_DOC-05(1).md | 2382349 | 7888 | `3b47a0b6224b1984` |
| `SBL-DOC-06` | SBL_PIPD-LS-PKG_DOC-06(1).md | 1554880 | 2858 | `64ea4977dab30933` |
| `SBL-DOC-07` | SBL_PIPD-LS-PKG_DOC-07(1).md | 1265128 | 3620 | `a366d3783c82089c` |
| `SBL-DOC-08` | SBL_PIPD-LS-PKG_DOC-08(1).md | 925526 | 11139 | `c7029c1ff07abe31` |
| `SBL-DOC-09` | SBL_PIPD-LS-PKG_DOC-09(1).md | 904598 | 3978 | `6450f7c15915ec8b` |
| `SBL-DOC-10` | SBL_PIPD-LS-PKG_DOC-10(1).md | 1397936 | 3888 | `a64aa21c977334dd` |
| `SBL-DOC-11` | SBL_PIPD-LS-PKG_DOC-11(1).md | 1831131 | 5005 | `12f8705d780b76f2` |
| `SBL-DOC-12` | SBL_PIPD-LS-PKG_DOC-12(1).md | 982931 | 7940 | `d1e470d82ca14319` |
| `SBL-DOC-13` | SBL_PIPD-LS-PKG_DOC-13(1).md | 1251068 | 3814 | `7cc0c8b17311130c` |
| `FHS-BODY-00` | 00_INDEX_AND_DECISION(4).md | 8236 | 83 | `cb4727d5b0c190ab` |
| `FHS-BODY-01` | 01_PRODUCT_AUTHORITY_SPINE(4).md | 17661 | 145 | `e257dfcd01f2e8af` |
| `FHS-BODY-02` | 02_PIPD_LIFECYCLE_AND_TPM(4).md | 73292 | 858 | `c336d3d9d702834e` |
| `FHS-BODY-03` | 03_ARCHITECTURE_ABI_AND_EFFECT(4).md | 12144 | 106 | `58628861e63956ae` |
| `FHS-BODY-04` | 04_FABRIC_HGK_CONTROL(4).md | 16794 | 120 | `a7d54bdeb9129e7e` |
| `FHS-BODY-05` | 05_COMMANDER_GUIDE_AND_NATIVE_PLAN(3).md | 6726 | 59 | `ee47e07455767c06` |
| `FHS-BODY-06` | 06_FHS_EXECUTE_HERMES_RUNTIME(4).md | 16807 | 117 | `6bc5de0d26c8d13f` |
| `FHS-BODY-07` | 07_ACCEPTANCE_CHALLENGE(4).md | 211405 | 1370 | `81a8c2f1cc4629f5` |
| `FHS-BODY-08` | 08_TECHNOLOGY_DEFAULT_HOTSWAP(4).md | 1128554 | 5900 | `1df04680319796aa` |
| `FHS-BODY-09` | 09_SBL_DOC00_13_FULL_UPGRADE(4).md | 300559 | 2198 | `1a0fcbdd77998bc9` |
| `FHS-BODY-09A` | 09A_R15_949_ORIGINAL_ATOMS(4).md | 1855910 | 12639 | `ce14d5d45ef76ded` |
| `FHS-BODY-09B` | 09B_KIND_MODE_HOST_192(4).md | 474159 | 3050 | `aed2234821768307` |
| `FHS-BODY-10` | 10_B1_W18_SELF_BOOTSTRAP(4).md | 7761 | 76 | `13b0764732bc1501` |
| `FHS-BODY-10A` | 10A_B1_TQAEP_120_124_38(4).md | 572218 | 8042 | `39ffde0115cdf894` |
| `FHS-BODY-10B` | 10B_B1_PI27_PD31(4).md | 44264 | 405 | `7c33e2472a6510a6` |
| `FHS-BODY-11` | 11_WORKPACKAGES_AND_DAG(4).md | 46467 | 380 | `6c526c991b5996c2` |
| `FHS-BODY-12` | 12_VERIFICATION_AND_DELIVERY(4).md | 15368 | 153 | `e4f7512a27ecbec1` |

## §P8 R15 949

共 **949** 個 R15 原子（distinct=949）。R15 949 屬原 SBL Full Product，不是 W0 必實作；本 SPEC 只作身份分母。

- 樣本：`R15-003`, `R15-004`, `R15-005`, `R15-006`, `R15-007`, `R15-008` … `R15-949`, `R15-950`, `R15-951`
- 全量 id 見 JSON `r15_949.ids`。

## §P9 Cell 192

共 **192** 個 Kind×Mode×Host×LegacyToken Cell（distinct=192）。192 Cell 的 Provider ON/OFF 原標籤有歧義，未經原 Host/Provider Owner ACK 前保持 HOLD。

- 樣本：`CELL-d0cf30ffd7c1`, `CELL-e8a4077d37ad`, `CELL-6582a70fd427`, `CELL-434c21c50bc3`, `CELL-41348f62f97c`, `CELL-4bf76833ac66`

## §P10 Parent50／Child149

SBL 原產品 **Parent 50** ／ **Child 149**。

- 規則：每個 Child 必須引用已存在的 Parent；Child 身份不得被刪除或假稱 supersede。
- Parent ids：`U01`, `U02`, `U03`, `U04`, `U05`, `U06`, `U07`, `U08`, `U09`, `U10`
- Child 樣本：`U01.1`, `U01.2`, `U01.3`, `U02.1`, `U02.2`, `U02.3`, `U03.1`, `U03.2`

## §P11 Oracle96

共 **96** 個 Original Oracle 個案；class 分佈：EDGE=8, JOURNEY=8, MUT=8, NEG=8, PARITY=8, PERF=8, POS=8, RECOVERY=8, ROLLBACK=8, SEC=8, UNINSTALL=8, UPGRADE=8。

- runner_binding：`UNBOUND（原 Host Runner／Fixture bytes 未取回）`
- 樣本：`AC-C39-POS-DETERMINISTIC`, `AC-C39-POS-STATE_READBACK`, `AC-C39-POS-PROPERTY`, `AC-C39-POS-REFERENCE_OUTPUT`, `AC-C39-POS-STATISTICAL`, `AC-C39-POS-SEMANTIC_JUDGE`

## §P12 Tech485

共 **485** 個正交技術身份；family 分佈：Default30=30, Donor24=24, Method25=25, Native20=20, TECH386=386。

- 485 正交技術身份為分母，不得相加為必安裝數

## §P13 計數對帳

| claim | 來源宣告 | 實算 | match |
|---|---|---|---|
| chapters | 50 | 50 | True |
| work_packages | 22 | 22 | True |
| edges | 36 | 36 | True |
| design84_cards | 84 | 84 | True |
| wave_split_25 | 25 | 25 | True |
| w0_required | 22 | 22 | True |
| e26_direction | WP-FHS-19→WP-FHS-14 | WP-FHS-19→WP-FHS-14 | True |

### Open holds
- E26 的 original_reader_ack=NOT_OBSERVED；W0 只出 typed 契約，不產生 CI Raw
- W2 Native E2E 未執行；本 SPEC 不宣稱任何 Native 效果
- 25 張跨波卡待原 Program Reader 裁決（JOIN_AMBIGUOUS_AFFECTED）
