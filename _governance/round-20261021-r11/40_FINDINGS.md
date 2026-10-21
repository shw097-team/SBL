# R11 Findings / TT-CR Register（round-20261021-r11）

分類用語沿用 `challenge-review-SKILL`：`CONFIRMED_DEFECT` / `EVIDENCE_GAP` / `NON_BLOCKING_OBSERVATION` / `ORACLE_DISAGREEMENT` / `SOURCE_POLARITY` / `OWNER_CONFLICT`。
本檔只登錄**本輪實測或 readback 得到**的狀態；未重測者保持原輪狀態，不升級、不降級。

## A. R8 十件（F-R8-001..010）

| ID | 本輪狀態 | 證據 / 缺口 | Earliest owner → 最小修補 → 關閉條件 |
|---|---|---|---|
| F-R8-001 README 漂移 | **CONFIRMED_DEFECT（本輪現地重證）** | `main@345b9477 README.md`：L11 `CANDIDATE_ONLY`、L13 `Not released. No version is published, tagged, or promoted.`、L42 `installs one console script, sbl-todo`；同時 tags `v0.1.0-foundation-preview`、`v0.1.1rc1`→`345b9477`，`pyproject` 另有 `sbl-stack`/`sbl-harness` | Docs Owner → 只改 README 狀態段（版本/entrypoints/claim ceiling）→ 讀回 main 與 README diff，確認三個 entrypoint 與兩個 release 一致。**需產品 write permit（本輪未取得）** |
| F-R8-002 語義分母 UNKNOWN | EVIDENCE_GAP | 同名；本輪未出任何完成百分比（fail-safe 正確） | Source/PIPD Owner → 建 taxonomy + dedup/alias → Owner 簽分母 |
| F-R8-003 3 ChatGPT 私人 Plugin | EVIDENCE_GAP（0/3） | 無 Host-issued id；本輪未接觸 ChatGPT Plugin Host | Host/Plugin Owner → 三套 create/install/@invoke/no-trigger/forbidden/uninstall |
| F-R8-004 五工具端到端 | EVIDENCE_GAP | 本輪只有 Stack(14 comp)/Adapter(ABI) scoped 讀回 + 三車道探針，非同 source/subject 的單一 WO 鏈 | HGK+Hermes Owner → 一個 admitted WO 貫穿 |
| F-R8-005 checker 判決分歧 | ORACLE_DISAGREEMENT | 未重跑（R9-02 無授權） | Challenge Owner → isolated scratch + signed bundle |
| F-R8-006 PLAN+Commander | EVIDENCE_GAP | 本輪只證 PLAN 車道可服務（`gpt-6.1-sol`），**未 invoke Commander-SP** | Commander Owner → pre-handoff 薄 adapter |
| F-R8-007 VERIFY+Challenge | EVIDENCE_GAP | 同上，只證車道可服務 | Challenge Owner → pre-spawn 薄 adapter + canonical bundle |
| F-R8-008 harness TOCTOU/rglob | NON_BLOCKING_OBSERVATION | 未測；維持非阻斷（trusted single-user scoped） | Security Owner → hostile FS/multiuser 升為 blocker 時再測 |
| F-R8-009 manifest 測試污染 canonical | **本輪降風險證據**：`32d971d` detached worktree 跑 `tests/test_control_package_manifest.py` **6 passed**，跑後 `git status --porcelain` 空 | 中斷/並行 runner 強制清理測試仍未做 | Test Owner → 合成 fixture + Ctrl-C/kill 清理測試 |
| F-R8-010 441 逐項 runtime | EVIDENCE_GAP | 未動 | OSS/Native Owner → per-selected qualification |

## B. R9 六件 + SP-INT

| ID | 本輪狀態 | 證據 | 下一步 |
|---|---|---|---|
| R9-02 A5 獨立驗收 | **OPEN（blocker）** | 無 checker 專用 isolated writable scratch 授權 | lane Owner 發授權 → 一次真獨立驗收 |
| R9-03 4 錯綁修復 | CLOSED_SCOPED（未回退） | `32d971d` 契約/測試存在且綠 | 新增「故意錯綁必失敗」負控（TS32） |
| R9-04 Plane Permit | **OPEN** | 無 issuer permit/lease | HGK issuer |
| R9-05 untracked 測試 | **OPEN** | 本輪具名列出 9 個 untracked 測試模組 + 1 modified（見 `00_ROUND_PLAN.md` TS08），未 stage | 作者/Repo Owner 授權 → clean checkout 重現 |
| R9-06 `_repo_head()` CWD | **OPEN** | 未修（需 HGK 寫入授權） | HGK project Owner：先紅後綠最小修 |
| R9-07 control manifest 負控 | CLOSED_SCOPED（本輪重跑 6 passed） | 同上 F-R8-009 證據 | 保持不回退 |
| SP-INT 兩薄 adapter | **OPEN** | 無 SP 真 invoke | 需 dispatcher 寫入授權 |

## C. 本輪新發現（`O-R11-*`）

| ID | 分類 | 事實（可重算） | 影響 / owner |
|---|---|---|---|
| O-R11-001 | EVIDENCE_GAP | HGK `b22706e` conformance 新分母：**18 failed / 578 passed / 90 subtests / 142.14s**（`PYTHONPATH=src`, `-p no:cacheprovider`），與 R10 記錄 `580 passed / 16 failed` 不同 | R10 的 baseline 不可重現；`R10-CONFORM` 應以本輪數字重設。HGK Test Owner |
| O-R11-002 | CONFIRMED_DEFECT（環境） | 指令 `pytest tests -q --timeout=900` 在本機 **失敗**：`unrecognized arguments: --timeout=900`（pytest-timeout 未安裝） | R11 指揮稿的原文指令不能照抄；CHK06 需改成不含 `--timeout`。HGK Test Owner / 文件 Owner |
| O-R11-003 | CONFIRMED_DEFECT（環境） | `.venv` 內 `import hg_kseos` → `ModuleNotFoundError`；conformance 必須帶 `PYTHONPATH=src`（或先 `pip install -e .`） | 任何人照 R10 的裸 `pytest tests` 都會 collection error。HGK Owner |
| O-R11-004 | OWNER_CONFLICT（已宣告） | registry epoch 29 / pool rev16 **PLAN rank1 = `opencode-go/minimax-m3.1-flash-free`**，與本次 Owner mandate `PLAN=openai-codex/gpt-6.1-sol` 相反 | 以 `--force-rank 2 --require-arm` 執行並留證；要真正消除需 Owner 決定是否發 epoch 30 rebind |
| O-R11-005 | NON_BLOCKING_OBSERVATION | relay `/v1/models` 92 筆**不含** `gpt-6.1-sol`，但實際 completion 回 200 並帶 usage；Codex 同時印 `Model metadata … not found. Defaulting to fallback metadata` | 再次確認「relay catalog ≠ 上游真相」；能力主張上限＝可路由/可服務 |
| O-R11-006 | EVIDENCE_GAP（已解） | R11 指揮稿宣告 `local_compiler_verdict=NOT_RUN_MISSING_BUNDLED_SCRIPT_AND_SCHEMA` 的前提**已失效**：官方 bundle 在本機完整存在（7 refs + schema + scripts + tests + assets + agents），四階段對 R9 控制契約 rc0 | 可在下一輪直接編 R11 契約；但 R11 自身仍無 PASS |
| O-R11-007 | EVIDENCE_GAP | `sbl-stack` 安裝狀態 `installed=true / 14 components / STANDALONE_ONLY / host_install_state=NOT_INSTALLED`；`sbl-harness doctor` `ok=true / abi=hgk-harness-abi/1 / HOST_PENDING / native_effect=NOT_GRANTED` | 與 R10 記載一致；不得升格為 host 或 native 效果 |

## D. 未關閉的 CR（沿用）

| CR | 狀態 | 需誰決定 |
|---|---|---|
| `CR-PLUGIN-SCHEMA-AUTHORITY` | OPEN | Product/Host Owner：排除 `NOBJ-017` 禁止草案，選合規官方封裝 spec |
| `CR-GPTB-KP-R04-POLARITY` | OPEN（SOURCE_POLARITY） | GPT B Knowledge Owner：只修被批准的文件，不翻轉 DOC |

## E. 本輪的 fail-closed 宣告

- `SBL_FULL_PRODUCT` = **OPEN**；本輪 `PARTIAL`。
- 未取得 issuer permit ⇒ 未執行任何 world-effect、未改產品程式碼、未動已發布 asset。
- CHK52 全契約 stop test 依規定回 **FAIL**（正確 fail-closed），不是工程失敗的隱藏。
