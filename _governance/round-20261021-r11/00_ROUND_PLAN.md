# SBL R11 治理回合計畫書 — 核心大目標 / 執行SPEC / 任務清單 / 檢測清單

- `order_id`: `SBL-R11-20261021-POST-R8-R9-R10-FULL-CONTRACT`
- `round`: `round-20261021-r11`（intake / baseline / lane-mandate verification）
- `mission_id`: `SBL_FULL_PRODUCT`（**immutable，本輪不得縮限**）
- 產生日：2026-10-21（Asia/Taipei），執行主體：canonical Hermes（session 平面）+ HGK lane dispatcher（車道平面）
- 本文件性質：**施工計畫與量測回報**，不是 WorkOrder、不是 Permit、不是 `PROMPT_COMPILE_PASS`、不是全案通過證書。

---

## 1. 身份與法位（authority plane）

| 層 | 主體 | 本輪實際行為 |
|---|---|---|
| NORMATIVE（產品契約） | `SBL_PIPD-LS-PKG_DOC-00..DOC-13` 原件 14/14 | 逐 byte 重算，rollup `01b972c8…f9d` 相符（見 `20_SOURCE_LEDGER.json`） |
| 治理契約 | `Fabric`（policy consumer surface） | 只讀；本輪未寫入 Fabric，F0 六步 consumer trace 仍 OPEN |
| 控制平面（issuer） | `HG-KSEOS`（WorkOrder / ONE ECP / ExecutionBinding / Permit / SharedSpine） | 只讀量測；**未取得任何 issuer permit**（R9-04 OPEN） |
| Runtime/Orchestration | canonical Hermes（MSIX HERMES_HOME） | intake、量測、packet 產出 |
| Maker / EXECUTE | CODEX CLI + `opencode-go/deepseek-v4.1-flash` | 本輪只做 lane mandate 探針（未派工寫碼：無 permit） |
| Checker / VERIFY_SECURITY | CODEX CLI + `openai-codex/gpt-6.1-sol` (medium) | 本輪只做 lane mandate 探針（無 frozen candidate 可受審） |
| 產品 repo | `shw097-team/SBL` | 只新增 evidence branch（本 packet），**未改 main、未改 tag、未 force push** |

**唯一寫入面**：`shw097-team/SBL` 的 `evidence/r11-20261021-intake` 分支（本 packet 與可重算 digest）。產品程式碼、HGK/Fabric/PIPD/SWOF 原始碼、已發布 asset 一律未動。

---

## 2. 核心大目標（不可降規）

> 普通使用者無須懂 PIPD / HGK / SP / WorkOrder / Model Lane，只提供一項陌生、可落地的 CLI / Skill / Agent 需求，即可在受治理流程中完成：
> `意圖/JTBD/FUO → 源與授權驗證 → TPM-SP 需求／NFR／ADR → PIPD Native PI/PD/SPEC/ACC/TQAEP → Commander-SP PLAN 真調用 → HGK WorkOrder/ONE ECP/Permit + Hermes ExecutionBinding → bounded CODEX worker 建出可運行產物 → POS/NEG/ADV/REGRESSION → 有界自修補與 rollback/replay → read-only Acceptance Challenge-SP（Codex CLI VERIFY_SECURITY）真反證 → Owner 放行 → 五工具/Host 安裝調用／卸載 → 可稽核交付/維護`

五件必交物：`TPM-SP`、`Commander-SP`、`Acceptance Challenge-SP`、`HG-KSEOS Upgrade + Harness Adapter`、`SBL Full Stack`；三 SP 另須 ChatGPT 私人 Plugin Host 真實 create/install/`@invoke`/no-trigger/forbidden/uninstall/readback 各 1 組（目前 0/3，`HOST_PENDING`）。

**本輪 ACTIVE_SLICE（唯一被授權的切片）**：`R11-TS00/01/02/03/10` 的唯讀量測 + 官方 Compiler bundle 完整性重現 + 三車道 mandate 探針 + evidence packet 發布。切片外一律 OPEN/BLOCKED，不得以本輪結果替代。

**帳目分離**：`FOUNDATION_RELEASE_GATE`（v0.1.0 / v0.1.1rc1，已發行）≠ `SBL_FULL_PRODUCT_GATE`（本輪 **OPEN**）。`14/14 DOC pin`、`34 acceptance edges`、`21/21 subject binding`、`578 passed` 均只證各自直測性質。

---

## 3. 模型 mandate chain（Owner 2026-10-21 指令 vs 現地宣告）

| 車道 | Owner 指定（本次任務） | HGK epoch 29 registry / pool rev16 rank1 | 本輪實際 dispatch | 結果 |
|---|---|---|---|---|
| PLAN | `openai-codex/gpt-6.1-sol`（SOL-MEDIUM, OpenAI OAuth） | **`opencode-go/minimax-m3.1-flash-free`** | `--force-rank 2 --require-arm openai-codex/gpt-6.1-sol` | **SERVED**（3.71s, usage 200, nonce 回傳） |
| EXECUTE | `opencode-go/deepseek-v4.1-flash`（CODEX CLI） | `opencode-go/deepseek-v4.1-flash` | `--force-rank 1 --require-arm opencode-go/deepseek-v4.1-flash` | **SERVED**（2.73s, usage 200） |
| VERIFY_SECURITY | `openai-codex/gpt-6.1-sol`（CODEX CLI） | `openai-codex/gpt-6.1-sol` | `--force-rank 1 --require-arm openai-codex/gpt-6.1-sol` | **SERVED**（10.66s, usage 200） |

- **模型方案可用** ⇒ 依 Owner 指令不需暫停全案。
- **宣告 drift（`R11-LANE-DRIFT`）**：registry epoch 29 / pool rev16 的 PLAN rank1 是 `minimax-m3.1-flash-free`（R10 handover 的 PLAN/EXECUTE 對調），與本次 Owner mandate 的 PLAN=`gpt-6.1-sol` **不一致**。本輪**未修改** registry / pool / assignment（不自改宣告面），改以逐次 `--force-rank` + `--require-arm` 的 role-mandate chain 覆蓋，並在每次 receipt 留下 `required_arm = served_arm` 證據。要消除 drift 需 Owner 決定是否發正式 rebind（HGK 專項 WO）。
- **平面分離**：本次互動 session 本身跑在 `deepseek-v4.1-flash`（opencode-go）＝ EXECUTE 模型；session pin 不構成 PLAN 車道綁定，PLAN 車道證據只來自上述 dispatcher receipt。
- **claim ceiling（lane）**：三車道 receipt 只證「token 可路由、該 turn 被服務、usage 對帳相符」。不證 SP 被調用、不證任何 subject 被驗收；`gpt-6.1-sol` 在 relay catalog 無 metadata（Codex 印 fallback metadata warning），模型能力主張不得超出可路由/可服務。

---

## 4. 任務執行 SPEC（本輪落點）

| SPEC | 要求 | 本輪落點 |
|---|---|---|
| SPEC-01 Source/Goal | 14 DOC 逐 byte + rollup + canonical↔mirror、20 KP、2 Skill、10 design vols、權威分層、Goal Fidelity Diff | 14/14 + rollup + mirror equality **PASS**；KP 20/20、2 Skill、10 vols 全數 match；Fidelity Diff 見 §7（DOC 主題粒度，語義分母仍 UNKNOWN） |
| SPEC-02 Compiler C0–C9 | 本機定位官方 bundle（scripts/references/schema）→ lint/activation/acceptance/compile/duplication | bundle **已定位**（`知識庫/工程基座/construction-acceptance-prompt-compiler/…`，含 7 refs + schema + scripts + tests + assets）；對 R9 控制契約四階段 **rc0 / PROMPT_COMPILE_PASS**，`contract_sha256=dd200277…`，`claim_ceiling=LOCAL`。**R11 契約尚未撰寫／編譯** ⇒ R11 自身仍無 PROMPT_COMPILE_PASS |
| SPEC-03 Native route-out | WO/ONE ECP/Permit/ExecutionBinding 由 HGK issuer 產生 | **未取得**（`NOT_AUTHORIZED`）。因此本輪無 bounded writer 派工、無產品程式碼變更 |
| SPEC-04 兩薄 Adapter | PLAN pre-handoff 真呼叫 Commander-SP；VERIFY pre-spawn 真呼叫 Challenge-SP | **未實作**（需 HGK 專項 WO 授權寫入 `scripts/hgk-lane-dispatch.py` 的 pre-spawn/pre-handoff 接點）→ `SP-INT` OPEN |
| SPEC-05 Qualification | 每 ACTIVE 十階段 + POS/NEG/ADV/REGRESSION | 僅 source/lane/install/compiler 段有直測；其餘 OPEN |
| SPEC-06 Iterative delivery | 最小合法 slice + checkpoint + 獨立 evidence commit + readback | 本 packet（evidence branch）＝ 一個 slice，readback 見 `50_RETURN.json` |

---

## 5. 任務執行清單（`R11-TS00`–`R11-TS48`）

狀態用語：`DONE`＝本輪有直測原始證據且無殘留義務；`PARTIAL`＝有部分直測，缺口具名；`OPEN`＝未開始且非授權阻斷；`BLOCKED`＝需 issuer/Owner/Host 授權才能前進；`FAIL`＝有明確反例。

| ID | 內容 | 狀態 | 直測證據 / 缺口 |
|---|---|---|---|
| TS00 | 唯讀 fresh baseline + conformance | DONE（有保留） | HGK `b22706e`（dirty）、SBL main `345b9477`、tag `v0.1.1rc1`→`345b9477`、R9 `32d971d`、本地 SBL worktree `2dde2d8`；conformance `18 failed / 578 passed / 90 subtests / 142.14s`（**與 R10 記錄的 580/16 不同分母**，dirty tree 含 9 個他人 untracked 測試模組 + 1 個 modified 測試）→ 舊 baseline 不可重現，`R10-CONFORM` 以本輪數字為準 |
| TS01 | Control Package byte pin + 三負例 | DONE | 14/14 SHA、`17,473,442` bytes、rollup 相符、mirror 逐檔 byte-equal；R9 `tests/test_control_package_manifest.py` 於 `_r9_negtest`（detached `32d971d`）**6 passed**，跑後 worktree clean（canonical 未被留下污點） |
| TS02 | 46 基礎件 + 來源角色 ledger | PARTIAL | KP 20/20、2 Skill（`9ecd2366…` / `214c7f04…`）、10 design vols（vol-01..10）全數 SHA 相符；R5/R6/R7/R10 敘述、兩手冊未逐份 hash；缺口列於 ledger `missing_critical` |
| TS03 | GOAL_FIDELITY_DIFF / 反降規 | PARTIAL | §7 已產出 DOC 主題級 diff；**語義分母仍 UNKNOWN**（DOC-02 L128 / DOC-04 L99 / DOC-12 L7829），不得出完成百分比 |
| TS04 | R11 官方 Compiler | PARTIAL | bundle 完整性與指令形狀已證（R9 控制契約四階段 PASS）；**R11 契約未撰寫**⇒ R11 `PROMPT_COMPILE_PASS` 不存在 |
| TS05 | 權威 / Scope / 原生入場 | BLOCKED | 無 issuer WO/ECP/Permit；Fabric F0 六步未跑 |
| TS06 | R9-02 獨立 A5 checker scratch | BLOCKED | 未取得 Checker 專用可寫 isolated scratch 授權；不得重跑無授權驗收 |
| TS07 | Runtime/Orchestration Plane Permit | BLOCKED | 無 issuer lease/scope/permit |
| TS08 | R9-05 untracked 測試所有權 | OPEN | 已具名列出：`tests/test_execute_luna_route.py`、`test_far_lane_fix_20261015.py`、`test_governed_runtime_controller.py`(+`.bak`)、`test_lane_effort_enforcement.py`、`test_lane_guard.py`(+`.bak`)、`test_lane_policy.py.bak…`、`test_mandatory_tool_guard.py`、`test_matrix_d_full.py`、`test_role_binding_enforcement.py`、`test_source_repoint.py`、`tests/w3_solution/`、modified `test_task014_named_method_closure.py`；作者/授權未知，**未 stage** |
| TS09 | R9-06 `_repo_head()` CWD bug | OPEN | 需 HGK 專項寫入授權；本輪只讀 |
| TS10 | 車道聯合不變式 | PARTIAL | 三車道 mandate receipt（§3）；registry/pool/assignment/projection 的聯合等式尚未全欄比對；PLAN rank1 drift 已具名 |
| TS11 | PLAN↔Commander-SP 薄 adapter | OPEN | 需 dispatcher 寫入授權 + Commander-SP 真 invoke 協定 |
| TS12 | VERIFY↔Challenge-SP 薄 adapter | OPEN | 同上 + frozen subject |
| TS13 | Fabric F0 六步消費 | BLOCKED | 需 HGK typed route + WO |
| TS14 | Hermes full SBL install/upgrade | PARTIAL | `sbl-stack status`：`installed=true, components=14, claim=STANDALONE_ONLY, host_install_state=NOT_INSTALLED`；`sbl-harness doctor`：`ok=true, abi=hgk-harness-abi/1, claim=HOST_PENDING, native_effect=NOT_GRANTED`；五工具逐名 effective-load / restart / uninstall 未做 |
| TS15 | SBL 單一 control façade | BLOCKED | 需 HGK issuer + 雙控制面負例 |
| TS16 | TPM-SP 真產品經理能力 | OPEN | 無 Host trigger receipt |
| TS17 | PIPD 8 Skills live bridge | OPEN | 8 Skill source 存在 ≠ native writer 已跑 |
| TS18 | PIPD PI/PD/TQAEP writer | OPEN | 需 PIPD native writer 授權 |
| TS19 | SBLM01–06 Engine contract | OPEN | 未做行為級驗證 |
| TS20 | GJ01 新 CLI_TOOL | OPEN | `sbl-todo` 僅 fixture，不可替代 |
| TS21 | GJ02 brownfield 建造/修復 | OPEN | — |
| TS22 | GJ03 新 Skill Host UAT | OPEN | — |
| TS23 | GJ03 minimal agent | OPEN | — |
| TS24 | 三 SP 身份/權限隔離 | PARTIAL | 三個 local skill 目錄存在、stack 宣告 3 principals；跨角色 destructive deny 未測 |
| TS25 | ChatGPT 私人 Plugin 3 套 | BLOCKED | `HOST_PENDING 0/3`；無 Host-issued id |
| TS26 | HGK Upgrade / Harness Adapter | PARTIAL | adapter doctor ok、ABI 宣告；native effect 未授予 |
| TS27 | Full Stack + 五工具獨立 | PARTIAL | 14 components 安裝收據；五工具各自 install/invoke/deny/uninstall 未做 |
| TS28 | DOC-12 38 Surface 逐項 | OPEN | 需逐 ID runtime 級證據 |
| TS29 | DOC-01 50+149 | OPEN | 需逐 Child raw closure |
| TS30 | DOC-06 441 identities | OPEN | 需 selected active 的 host/load/deny 證據 |
| TS31 | 語義分母 reconciliation | OPEN | 4738/4589/1341 演算法未獨立核對；10 engineer-day stop-loss 未啟動 |
| TS32 | R9 4→0 binding 回歸守護 | PARTIAL | 34 edges 檔案存在且 R9 測試綠；未做「故意錯綁必失敗」新負控 |
| TS33 | control manifest test 隔離 | DONE（scoped） | 於 detached `32d971d` worktree 跑，6 passed、跑後 clean；中斷/並行 runner 強制清理測試未做 |
| TS34 | README / Release 資訊修補 | FAIL（確認缺陷） | `main@345b9477` README 仍寫 `CANDIDATE_ONLY` / `Not released` / `installs one console script, sbl-todo`，與已發 2 個 release、3 個 entrypoint 衝突（F-R8-001）；修補需產品 write permit，本輪只列最小 patch 方案 |
| TS35 | G-KNOW / CJK / injection | OPEN | — |
| TS36 | 12×8 TQAEP matrix | OPEN | — |
| TS37 | 自修補 / replay / resume | OPEN | — |
| TS38 | GJ01–03 / M00–15 / P01–07 | OPEN | — |
| TS39 | G00–G12 × 3 modes | OPEN | PREW3_SHADOW no-effect 未測 |
| TS40 | 6 donor 取捨 | OPEN | — |
| TS41 | 供應鏈 / 秘密 / Race | PARTIAL | 本輪未輸出 secret；token 只以 askpass helper 讀取，未進 argv/log |
| TS42 | GitHub 內容與證據提交 | PARTIAL | 本 packet 推 `evidence/r11-20261021-intake` + readback（§9） |
| TS43 | clean-room Acceptance Challenge | BLOCKED | 無獨立 Checker scratch 授權、無 frozen candidate 授權 |
| TS44 | 五工具跨 host matrix | PARTIAL | Hermes host 1/5 面；ChatGPT host 0/3 |
| TS45 | Release provenance | OPEN | 未動 v0.1.1rc1 |
| TS46 | SWOF typed handoff | BLOCKED | 無 W3 ACK / permit ⇒ NO_EFFECT |
| TS47 | TT/CR/debt 追蹤 | PARTIAL | `40_FINDINGS.md` 逐件列 owner / 最小修補 / 關閉條件 |
| TS48 | Full Product Final Gate | FAIL（未達） | 見 §8；`SBL_FULL_PRODUCT=OPEN` |

---

## 6. 檢測清單（`R11-CHK00`–`R11-CHK52`）

| CHK | predicate | 狀態 | 原始證據 |
|---|---|---|---|
| CHK00 | README/main 與 release metadata 一致 | **FAIL（確認缺陷）** | `main@345b9477 README.md:11,13,42` vs tags `v0.1.0-foundation-preview`,`v0.1.1rc1`；`pyproject` 有 `sbl-stack`/`sbl-harness` |
| CHK01 | 14 DOC hash+rollup+三負例 | PASS | §5/TS01；`20_SOURCE_LEDGER.json` |
| CHK02 | 20 KP + 10 vols + 2 Skill | PASS（含缺件揭露） | 全數 SHA 相符；兩手冊未 hash（記缺口） |
| CHK03 | Compiler C0–C9 與語意保真 | PARTIAL | R9 控制契約四階段 rc0；R11 契約未編 |
| CHK04 | R9 4 binding 互比較 | NOT_RUN | 需跑契約內 subject↔acceptance join 腳本 |
| CHK05 | repo/candidate/evidence SHA cross binding | PARTIAL | SHAs 已讀回；evidence SHA 於本 packet 產生後回填 |
| CHK06 | HGK conformance post R10 | PASS（量測完成） | `hgk_conformance.log`：18F/578P/90 subtests |
| CHK07 | R9-02 scratch isolation | BLOCKED | 無授權 |
| CHK08 | Permit issuer/multi-binding | BLOCKED | 無 issuer |
| CHK09 | untracked 所有權 | OPEN | TS08 清單 |
| CHK10 | `_repo_head` CWD negative | OPEN | 需寫入授權 |
| CHK11 | R10 joint lane inequality | PARTIAL | 三車道 served；registry↔pool↔assignment 全欄未對 |
| CHK12 | 三車道 rank1 live service | **PASS（mandate 版）** | PLAN rank2 gpt-6.1-sol / EXECUTE rank1 deepseek / VERIFY rank1 gpt-6.1-sol，全 usage 200 |
| CHK13–CHK17 | SP / Fabric 六步 | BLOCKED | 無 SP invoke、無 WO |
| CHK18 | Hermes pin/profile guard | PARTIAL | HERMES_HOME、skills/sbl 5 目錄已讀；CodeX_HOME 隔離未驗 |
| CHK19 | 五工具 effective-install | PARTIAL | stack 14 comp / adapter doctor ok；逐工具 lifecycle 未做 |
| CHK20 | 單一 issuer / 第二控制面拒絕 | BLOCKED | — |
| CHK21–CHK30 | 產品能力 / GJ / SP / Plugin | OPEN 或 BLOCKED（同 TS） | — |
| CHK31 | HGK upgrade+adapter native effect | PARTIAL | `native_effect=NOT_GRANTED` 為正確宣告 |
| CHK32 | 五工具分別可部署 | PARTIAL | 同一 Stack 證據，未拆 |
| CHK33/34/35 | 38 surface / 199 需求 / 441 identities | NOT_RUN | 需逐 ID 執行 |
| CHK36 | 語義分母 fail-safe | PASS（保守） | 本輪未出任何完成百分比 |
| CHK37 | control manifest 不寫 canonical | PASS（scoped） | detached worktree 跑後 clean |
| CHK38–CHK41 | CJK / TQAEP / repair / moments | NOT_RUN | — |
| CHK42 | 39 mode gates | NOT_RUN | — |
| CHK43 | 6 donor | NOT_RUN | — |
| CHK44 | token / public scrub | PASS（本輪） | token 經 askpass helper，未進 argv/log/commit |
| CHK45 | uninstall symlink/TOCTOU | NOT_RUN | F-R8-008 維持非阻斷觀察 |
| CHK46 | GitHub candidate/evidence readback | PARTIAL | 見 §9 readback |
| CHK47 | canonical challenge bundle | BLOCKED | 無 checker |
| CHK48 | release scope/重現 | NOT_RUN | 未動 release |
| CHK49 | SWOF W3 | BLOCKED | 無 ACK |
| CHK50 | R8 10 findings 覆蓋 | PARTIAL | `40_FINDINGS.md` 全 10 件在冊，僅 F-001 有現地新證據 |
| CHK51 | R9 02/04/05/06/INT 閉合 | FAIL（全 OPEN） | 見 §40_FINDINGS |
| CHK52 | 全契約 stop test | **FAIL（正確 fail-closed）** | active clause orphan、五工具/三 Plugin 未驗、無 native/checker ⇒ 不得結案 |

---

## 7. GOAL_FIDELITY_DIFF（DOC 主題級，語義分母 UNKNOWN）

| 上位能力 | 現況 | 是否核心 | 處置 |
|---|---|---|---|
| DOC-00 SourceFreeze/authority/bounded claims | 來源身份完成（14/14+rollup） | 是 | scoped 完成 |
| DOC-01 ProductKinds/50+149/GJ | fixture 級 | 是 | OPEN（TS20/29/38） |
| DOC-02 intent→spec→build→verify | fixture 級 | 是 | OPEN |
| DOC-03 PIPD writer / 8 Skills | 只有 source | 是 | OPEN（TS17/18） |
| DOC-04 One Core/3 SP/6 modules | stack 14 comp 存在，lane handoff 未證 | 是 | PARTIAL |
| DOC-05 RepoContext/ONE ECP/rollback | 無 permit、無 bounded write | 是 | BLOCKED（TS05/07） |
| DOC-06 441 eligibility | ledger 有、runtime 無 | 是（不得百分比） | OPEN（TS30/31） |
| DOC-07 security/SoD | lane 分離有、native revoke 無 | 是 | PARTIAL |
| DOC-08 TQAEP / independent challenge | 無 signed bundle | 是 | BLOCKED（TS43） |
| DOC-09 G-KNOW/RAG | 未測 | 是 | OPEN |
| DOC-10 Commander plan→WO | 無 SP invoke | 是 | OPEN（TS11） |
| DOC-11 repair/replay | 未測 | 是 | OPEN |
| DOC-12 38 surfaces / host / plugin | 0/3 host；stack scoped | 是 | PARTIAL/BLOCKED |
| DOC-13 bootstrap/evolution | RC 系列有、自舉全鏈無 | 是 | OPEN（TS48） |

**結論**：無任何核心能力被合法永遠 deferred；所有缺口皆具名、有 owner 路徑、保留 OPEN。

---

## 8. 本輪結果與 claim ceiling

- **決策**：`PARTIAL`（intake/量測/證據切片完成；全案 `SBL_FULL_PRODUCT = OPEN`）。
- 已直接證明：來源身份（14/14+rollup+mirror）、KP/Skill/vols 身份、R9 負控測試可重跑且不污染 canonical、官方 Compiler bundle 可用（控制契約四階段 rc0）、三車道 mandate 模型可服務（含 usage 對帳）、Stack/Adapter 的 scoped 安裝狀態與正確的 `HOST_PENDING / NOT_GRANTED` 宣告、HGK conformance 新分母（18F/578P）。
- **未證明（不得宣稱）**：任何 Native WorkOrder/ECP/Permit 效果；任何 SP 真調用（Commander/Challenge）；任何 Host 級 ChatGPT plugin；五工具各自 lifecycle；149/441/38 的 runtime 驗收；TQAEP/獨立 challenge；release 重現。`PROMPT_COMPILE_PASS` 只屬於 R9 控制契約，不屬於 R11。
- **副作用揭露**：新增 HGK `var/R11-LANE-MANDATE-20261021/`（lane receipts + logs，`var/` 為 gitignored，未改任何 HGK 受版控檔）；新增 scratch `…/hermes/cache/scratch/r11_compile_r9`；新增 worktree `C:\Projects\Agent_Workspace\_r11_packet`（evidence branch）、`C:\Projects\Agent_Workspace\_r9_negtest`（detached `32d971d`，唯讀用途，跑後 clean）；HGK 主工作樹 dirty 狀態**未變更**（未 stage、未 reset）。

## 9. 下一步合法動作（依序）

1. `HITL-1`（Owner）：決定 PLAN rank1 drift 的正式 rebind（epoch 30）或維持逐輪 mandate chain。
2. `HITL-2`（HGK issuer）：對本切片發 `WorkOrder → ONE ECP → Permit/ExecutionBinding`（scope=defect repair cone：README/F-R8-001 + R9-06 `_repo_head` + SP-INT 兩薄 adapter）。
3. `HITL-3`（lane owner）：發 Checker 專用 isolated writable scratch 授權（解 R9-02），並凍結受審 subject。
4. 上述到位後：R11 契約撰寫 → 四階段 Compiler → bounded writer 修 F-R8-001 → isolated checker → challenge bundle。
5. `HITL-4`（Host owner）：ChatGPT 私人 Plugin 三套 create/install/`@invoke`/uninstall。
