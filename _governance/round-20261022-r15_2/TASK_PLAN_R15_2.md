# R15.2 任務計畫：核心大目標 / SPEC / 執行清單 / 檢測清單

```yaml
subject: SBL-R15.2-CONTINUATION-20261022
round: round-20261022-r15_2
branch: evidence/r15_2-20261022
plan_authority: this file is a PLAN artefact, not a WorkOrder, Permit, PASS or Release
claim_ceiling: ROUTEOUT_CANDIDATE + LOCAL_RAW_ONLY
final_gate: FAIL_CLOSED
```

## 0. 三個平面（不可混用）

| 平面 | 誰 | 本輪實證 |
|---|---|---|
| 產品前門 | **SBL 唯一** | 本輪所有產物落 `SBL` repo 的 evidence 分支 |
| 原生授權／狀態／驗收 | **HG-KSEOS 唯一** | 三臂皆經 `hgk-lane-dispatch.py` + pool rev20 派工；未取得 WorkOrder/Permit |
| 受治理 Runtime／Orchestration | **current canonical Hermes** | 本 session（`deepseek-v4.1-flash`）只做編排，不冒充 lane 模型 |

**lane 模型 ≠ session 模型**：session 是 deepseek；PLAN／VERIFY 由 pool rank2 釘 `gpt-6.1-sol`，EXECUTE 由 rank1 釘 `opencode-go/minimax-m3.1-flash-free`。三者由 dispatcher 選出並回顯 served model，與 session pin 無關。

## 1. 核心大目標

> 讓 SBL 成為唯一產品工程指揮入口：以 R14 已完成的有效工作為起點，依上位 `SBL_PIPD-LS-PKG` 控制包與 R15.1 全量施工契約，把 E01–E09／M1–M4 的適用產品能力落地、執行、檢測、驗收、交付；HG-KSEOS 保持唯一原生授權／狀態／驗收平面；Hermes 僅作受治治理編排。

本輪**可交付的部分**：源碼凍結、C0–C9 官方編譯、三臂車道綁定實證、一次受限寫入＋一次獨立裁決、SWARM 自檢測／自修補／自驗收、TT 與 NO_EFFECT DecisionPack、遠端證據分支。
本輪**不可交付的部分**：任何 WP 的「完成」宣告（缺 native WorkOrder/Permit）。

## 2. 任務執行 SPEC

| # | 條款 | 落地方式 | 狀態 |
|---|---|---|---|
| S1 | 來源 SSOT 必須可重現 | `SOURCE_FREEZE.json`：24 份文件逐一 `observed.sha256` vs R15.1 宣告，24/24 MATCH | DONE |
| S2 | 必須走官方 C0–C9 編譯，不得自製 gate | 官方 bundle `lint`/`activation`/`acceptance`/`compile` 四命令全 exit 0，單一 `contract_sha256=414005c1…` | DONE |
| S3 | 角色→模型綁定必須經 lane 平面 | `--force-rank` + `--require-arm` + `--nonce`，PLAN/EXECUTE/VERIFY 皆 `ok=True` 且 nonce 回顯 | DONE |
| S4 | 任何 effect 必須有 readback＋rollback | writer 只新增 1 檔；`MODIFIED=0 REMOVED=0`；CWD 逃逸事件已捕獲、移除、樹已驗證乾淨 | DONE（含 1 起已圍堵事故） |
| S5 | 不得自我驗收 | checker 與 maker 同機同 session → 只能算 lane-level check，`SOD006-C6` 保持 OPEN | PARTIAL（結構性） |
| S6 | final gate FAIL_CLOSED | `native_run NOT_RUN`、`independent_acceptance NOT_RUN`、`release BLOCKED` | DONE |
| S7 | 每個阻斷都要 FAR 裁決建議 | `TT_R15_2_REGISTER.json` 13 項，每項含 `next_legal_step` + `far_recommendation` | DONE |
| S8 | 自研究／自學習／自迭代／自進化 | `EVOLUTION_R15_2.md` + 兩個新技能（`capc-contract-authoring`、`hgk-codex-lane-recipe`） | DONE |

## 3. 任務執行清單（W00–W17，含本輪真實狀態）

| WP | 範圍 | 本輪狀態 | 依據 |
|---|---|---|---|
| W00 | source freeze + C0–C9 編譯 | **DONE（唯讀）** | `SOURCE_FREEZE.json`, `receipts/CAPC_*.json`, `output/` |
| W01 | HGK native conformance / issuer | **BLOCKED** | `TT-R15.2-NATIVE-ISSUER-UNBOUND` |
| W02 | Fabric active policy → HGK APL | **TEMP_CLOSED** | `TT-R15.2-FABRIC-ACTIVE-POLICY-UNRESOLVED` |
| W03 | PLAN Commander-SP 真派工 | **DONE（唯讀）** | `receipts/dispatch/PLAN_gpt61sol.json` |
| W04 | VERIFY_SECURITY checker 真派工 | **DONE（lane-level）** | `receipts/dispatch/VERIFY_gpt61sol_judgement.json` |
| W05 | PIPD 8 skills / 19 families / 13 verbs 追溯 | NOT_RUN | 需 permit 才能落碼 |
| W06 | One Core 六模組 install/run/uninstall | NOT_RUN | 需 permit |
| W07 | first-fail bounded repair | NOT_RUN | 需 W03–W09 先閉合 |
| W08 | 三車道 required vs served 一致性 | **PARTIAL** | pool rev20 已核；registry epoch 32 未由 native 回讀 |
| W09 | KANBAN claim/lease/heartbeat + SWARM fan-in | **PARTIAL** | board `sbl-r15-2-20261022` 18 卡 + 兩波 SWARM（4+3 worker）|
| W10 | OPENSPEC propose / strict validate + gstack | **FAIL / NOFIT** | `TT-R15.2-OPENSPEC-STRICT-FAIL`, `TT-R15.2-GSTACK-NOFIT` |
| W11 | bounded standing grant / FAR / resume | **DONE（本檔即產物）** | 本檔 + TT register |
| W12 | SWOF W2 rechallenge / W3 admission | **BLOCKED** | `TT-R15.2-SWOF-W3-ABSENT` |
| W13 | 五工具 / 三 ZIP / 三私有 host | **BLOCKED** | `TT-R15.2-CHATGPT-HOST-PENDING` |
| W14 | 50/149/441/38/39/24 分母 | NOT_RUN | 需四表投影 |
| W15 | secure CI / SBOM / provenance | NOT_RUN | 需 release-owner WO |
| W16 | B0/B1/B2 配對量測 | NOT_RUN | 唯讀可做，未排入本輪 |
| W17 | R14 31 TS / 31 CHK 續作與最終裁決 | **PARTIAL** | `R14_LEDGER_READBACK.json` + `TT-R15.2-R14-EVIDENCE-GAP` |

## 4. 檢測清單（每項都要有真 raw，否則不得勾）

| # | 檢測 | 判準 | 結果 |
|---|---|---|---|
| C00 | 來源完整性 | 24/24 sha 相符 | PASS |
| C01 | CAPC schema + invariant | `lint` exit 0 | PASS |
| C02 | Activation Bridge | `activation` exit 0 | PASS |
| C03 | Acceptance 邊完備 | `acceptance` exit 0 | PASS |
| C04 | 薄型 prompt 編譯 | `compile` exit 0，`thin-prompt.md` 產出 | PASS（20,799 chars）|
| C05 | PLAN 車道 arm | `--require-arm openai-codex/gpt-6.1-sol` 且 nonce 回顯 | PASS |
| C06 | EXECUTE 車道 arm | rank1 minimax、exit 0、非 timeout | PASS（第二次，`--cwd` 釘住後 20.9s）|
| C07 | VERIFY 車道 arm | rank2 gpt-6.1-sol、回傳 JSON 裁決 | PASS（lane-level，非 AO）|
| C08 | 受限寫入 | 只新增 write-set 內 1 檔 | PASS |
| C09 | 非侵入守衛 | write-set 外 `MODIFIED=0 REMOVED=0` | PASS |
| C10 | CWD 圍堵 | HG-KSEOS `git status` 空、HEAD 未變 | PASS（事故後）|
| C11 | KANBAN 真實性 | 18 卡皆 blocked `NO_NATIVE_WORKORDER_PERMIT` | PASS（fail-closed）|
| C12 | OPENSPEC strict | `openspec validate --strict --all` exit 0 | **FAIL**（既有 `far-r12-20261021` 無 delta）|
| C13 | gstack 可得性 | 安裝存在或 typed NoFit | NOFIT（24 次探測）|
| C14 | R14 證據存在性 | 每項 declared evidence 皆在該 commit | **PARTIAL**（20/10/1；17 DONE 只有 12 齊全）|
| C15 | 獨立驗收 | checker principal ≠ maker | **NOT_RUN**（同機同 session）|
| C16 | native 執行 | WorkOrder/Permit id 存在 | **NOT_RUN** |
| C17 | Release | owner seal | **BLOCKED** |

**判決**：`PARTIAL`。C00–C11 為真，C12/C14 部分失敗，C15–C17 未達；不得宣稱 FULL PASS 或 Release。
