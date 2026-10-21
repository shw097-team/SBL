# SBL 移交包 — R10 (2026-10-21)

> **給新 SESSION 的第一句話**：這是 SBL 的實作移交。不要從零重建，不要重跑已完成的輪次。
> 先讀 §0 與 §2，再從 §6 的第一項開始做。§7 是本程式最容易重犯的錯，讀完再動手。

本文件由 R10 回合產生。所有數字均在該回合實測，標註了**實測時點與範圍**；沒有重測的一律標 `NOT_RE_MEASURED`。

---

## 0. 30 秒定向

**SBL = SBL_PIPD-LS-PKG**，14 份上位控制包（DOC-00..DOC-13，17,473,442 bytes / 75,630 行），
它是**唯一工程契約**。SBL 產品 repo 是它的實作。

| 平面 | 狀態 |
|---|---|
| HG-KSEOS（唯一控制平面） | 運作中。lane rebind 完成，drift 0，registry epoch **29** |
| SBL 產品（GitHub `shw097-team/SBL`） | main `345b9477`；candidate `32d971d`；suite **218 passed / 2 skipped** |
| 本機 HERMES 安裝 | `sbl-v01 0.1.1rc1` 已裝，14 組件／3 principals，selftest **9/9** |
| HGK spine | R9 鏈完整但 **acceptance = FAIL**（沒有獨立驗收） |
| FABRIC | **無 SBL 安裝目標**，未嘗試、未宣稱 |

**一句話現況**：產品與安裝面是真的可用且有測試支撐；**驗收面是空的**。下一個 session 的最高價值動作是拿到第一個獨立裁決，其餘項目都是它的下屬。

---

## 1. 模型 mandate 與如何自行複驗

現行 mandate（owner 2026-10-21，本回合已套用）：

| 車道 | provider / model | 執行方式 |
|---|---|---|
| PLAN | `opencode-go` / `minimax-m3.1-flash-free` | Hermes governed profile |
| EXECUTE | `opencode-go` / `deepseek-v4.1-flash` | CODEX CLI（sealed lane） |
| VERIFY / SECURITY | `openai-codex` / `gpt-6.1-sol`，`reasoning_effort=medium` | CODEX CLI |

**複驗指令**（唯讀，不會改任何東西）：

```bash
cd C:/Projects/Agent_Workspace/HG-KSEOS
./.venv/Scripts/python.exe scripts/hgk-lane-dispatch.py --lane PLAN \
  --prompt "Reply with exactly this token and nothing else: CHK-PLAN" --nonce CHK-PLAN \
  --pool config/lane-route-slots.candidate.json \
  --codex-executable C:/Users/user/AppData/Local/OpenAI/Codex/bin/6257d9e8f63c0f2b/codex.exe \
  --json-out var/CHK/gate_PLAN.json --attempt-log-dir var/CHK/gate_PLAN.json.logs --timeout 300
```

看 `ok=true`、`used_rank=1`、`used_transport_model` 符合上表、`attempts[-1].nonce_present=true`、
`attempts[-1].usage_status=200`。EXECUTE / VERIFY_SECURITY 同形（VERIFY 的 transport 是裸 `gpt-6.1-sol`）。

**R10 實測值**（`var/R10-GATE/final_summary.json`）：PLAN 3.75s、EXECUTE 3.57s、VERIFY 3.05s，全 `ok=true`。

**若 mandate 不可用**：依 owner 指示必須**暫停並告知**，不得自行換模型。

**兩個平面不可混用**：會話本身的互動模型（session plane）**不是**任何車道的綁定證據。
本回合的會話 plane 是 `deepseek-v4.1-flash`，車道是上表 —— 兩者互不引用。

---

## 2. 硬約束（照做，沒有例外）

1. **candidate-only**。可寫 candidate/evidence 分支、可寫候選宣告；**不可** promotion 到 ACTIVE、不可冒充 native issuer、不可自簽 acceptance。
2. **不可自我驗收**。maker ≠ checker。你跑綠的測試是 evidence，不是 acceptance。HGK 只接受 `PASS`/`FAIL`；沒有裁決 → 誠實記 `FAIL`。
3. **不可 `git add -A`**。不 stage 他人未提交檔案，不刪他人檔案。
4. **credential 一律不輸出**。GitHub 用 sealed askpass（`_handover/R5R3-20261016-preview4-closeout/_askpass_r5r3.cmd`）；token 來源 `API KEY/GITHUB-REPO_SHW097-4.txt`。永不印出、永不 commit。
5. **spine 只走 typed API**，不 raw SQL 寫入。lease 紀律：`resolve_acceptance` 的 lease 掛在 **acceptance id** 上（不是 requirement id），且 `expected_version` 用的是該筆 acceptance 的版本（首筆為 `0`）。
6. **不可手打 hash**。一律由工具計算。
7. **不重寫歷史記錄**。帶日期的 note（`model_routing_change`、`owner_mandate_20261021`、`round_rebinding_note`）是 RECORD，保留原 bytes；新回合用**新增**欄位。
8. **宣稱天花板要逐項寫**。`scoped PASS` 不可升格為 `full contract PASS`；PR 可 fast-forward 不是已合併。

---

## 3. 平面清單與確切狀態

| 平面 | 位置 | 狀態 | 天花板 |
|---|---|---|---|
| HG-KSEOS | `C:/Projects/Agent_Workspace/HG-KSEOS`，branch `codex/hgk-final-closure-002`，HEAD **`b22706e`** | 運作中，**無 git remote** | candidate 宣告 |
| SBL product | GitHub `shw097-team/SBL` | main `345b9477` | — |
| SBL candidate | `candidate/r9-20261021-ctrlpkg` @ `32d971d`；worktree `_sbl_r9_candidate/` | 218/2 綠 | 未合併 |
| SBL evidence | `evidence/r7-20261021-c7` @ `fccad0f` | 已推 | 證據，非驗收 |
| 本機安裝 | canonical Hermes venv（`.../hermes-agent/venv/Scripts/python.exe`） | `sbl-v01 0.1.1rc1`，141 dists | `STANDALONE_ONLY` |
| HGK adapter | `HG-KSEOS/_sbl_harness_adapter/`（3 檔，untracked） | `ROOT_READY` 6/6，3 digest 釘定 | `HOST_PENDING` |
| Host install | — | **`host_install_state = NOT_INSTALLED`** | 未取得 |
| Native integration | — | ABI 自宣告 `native_effect/permit_signing/workorder_admission = not_provided` | 未取得 |
| FABRIC | — | **無 SBL 安裝目標** | 未嘗試、未宣稱 |
| CODEX / CODEX CLI | `6257d9e8f63c0f2b/codex.exe`，`0.163.0-alpha.11` | 可服務車道 | 非 SBL-specific qualification |
| Release | `v0.1.1rc1`，id `419526963`，tag→`345b9477` | 已發布 prerelease，資產 digest 回讀相符 | prerelease |

---

## 4. 已完成並驗證（附證據）

### 4.1 R9-03 合約 capability 錯綁 → 關閉
4 個 `runtime_readiness` 列原本都指向 `ACC-SBL_SHARED_CORE`。
- mismatches **4 → 0**；acceptance edges **34 不變**（edge 本來就存在，錯的是指標）
- 四階段 `lint/activation/acceptance/compile` 全 `PROMPT_COMPILE_PASS`、0 errors
- 合約 sha256 `dd200277ca1b9352d751a178fb51b8a5a5d857d0a472f11119fcc56f0471d55d` 對得起 receipt
- `tests/test_contract_binding.py` **先證明在修正前 2 failed** 才轉綠
- **天花板**：四列 `current_verdict` 仍 `NOT_READY`、16 個 lifecycle cell 全 OPEN。這是修指標，不是 ready。

### 4.2 R9-07 控制包可追溯 → 關閉
`contracts/CONTROL_PACKAGE_MANIFEST.json` 釘 14 份 digest + rollup `01b972c8…`。
**刻意不 vendored 17 MB**：重製品會變成第二個權威，而「第二權威偏離第一權威」正是本程式的核心缺陷類別。
`tools/check_control_package.py` 三種負控各自精準失敗：`ERR_SIZE_DRIFT`、`ERR_SHA256_DRIFT`（**同長度單一位元**篡改）、`ERR_DOC_ABSENT`。

### 4.3 R10 lane rebind → 完成
PLAN/EXECUTE 對調，`VERIFY` 不動。registry epoch 28→**29**，drift **0 findings**。
工具：`var/R10-LANES/apply_plan_exec_swap.py`（載入 R8 的 671 行 builder 並覆寫兩個 global，**不 fork**）、
`var/R10-LANES/sync_runtime_decls.py`（3 個 runtime 宣告同步）。

### 4.4 本機安裝 → 部分真實
`sbl-v01 0.1.1rc1`（140→141 dists、零依賴、3 個 CLI 可 import）；stack 14 組件／3 principals；
doctor clean；selftest **9/9**（含 2 個 negative case）；HGK adapter `ROOT_READY` 6/6。

---

## 5. 未關閉項目（每項附 blocker、owner、close condition）

| ID | 項目 | 嚴重度 | Blocker / Owner | Close condition（可證偽） |
|---|---|---|---|---|
| R9-02 | **獨立驗收**（A5 checker） | **blocker** | 需**可寫的隔離 scratch root**（R7 的 `INCONCLUSIVE` 正是沙箱禁寫所致）。owner：lane 負責人 | 一次獨立 VERIFY_SECURITY 回合對凍結 subject 產出 `ACCEPTED`，且 verdict 落在可讀回的 artifact |
| R9-04 | Hermes Runtime/Orchestration **Plane permit** | high | 可寫 binding record 能產出；**permit 不能**。owner：HGK binding/permit 授權方 | 授權方提供或核准 scoped permit 參照，且回讀相符 |
| R9-05 | HG-KSEOS repo 不可重現 | high | 3 個測試檔在 HEAD 為 **untracked**；stage 別人 ~800 行未提交碼會錯置作者。owner：測試檔作者 | 乾淨 checkout 跑出同樣的 conformance 計數 |
| R9-06 | `lifecycle.py::_repo_head()` 讀 CWD 並吞 `InvariantViolation` | high | 需**乾淨基線**的獨立回合；HG-KSEOS 現有 16 個既有失敗＋並行寫者 | 新增測試在專案 repo 非 CWD 時仍解析正確 HEAD，且 `InvariantViolation` 不再被吞 |
| SP-INT | PLAN↔Commander-SP、VERIFY↔Challenge-SP 整合 | high | 需自己的 admitted change。**dispatcher 綁的是模型，不是 SP**；無任何已檢視路徑呼叫 `commander_sp`/`external_challenge_sp`/`sign_verdict` | dispatcher 在 PLAN handoff 與 VERIFY pre-spawn 實際呼叫對應 SP，且留下 receipt |
| DOC-00..13 | 全量落地 | high | **分母 UNKNOWN**（見 §7.2）。需分階段計畫 + 10 engineer-day stop-loss | 見 §6.6 |
| CONFORM | HG-KSEOS conformance | medium | 上次測量在 `fa1ac06`：**580 passed / 16 failed**（baseline 575/21） | 對 `b22706e` 重測並報告絕對值＋相對 baseline |

**注意 R9-05 的連帶效應**：因為那 3 個測試檔 untracked，`580/16` **無法**從乾淨 checkout 重現。任何人引用這個數字都必須同時引用這個限制。

---

## 6. 下一步（依價值排序，含指令）

### 6.1 先重測 conformance（5 分鐘，任何其他動作的前提）
`b22706e` 之後**沒有**重測。沒有這個數字，後面所有「沒退化」的宣稱都是空的。

```bash
cd C:/Projects/Agent_Workspace/HG-KSEOS
./.venv/Scripts/python.exe -m pytest tests -q --timeout=900
```
期望：`580 passed / 16 failed` 附近。**必須同時報告 baseline**，不能只報絕對值。

### 6.2 R9-02 獨立驗收 —— 最高價值
唯一真正的 blocker。沒有它，R7 永久停在 `INCONCLUSIVE / NOT ACCEPTED`，HGK 永久記 `FAIL`。
前置：向 lane 負責人取得**可寫的隔離 scratch root**（bounded to the checker）。
有了之後：以 `--sandbox workspace-write` + 明示授權 + digest guard 派一次 VERIFY 回合，nonce、usage receipt、served identity 全保存。
**不要**在沒有授權的情況下重跑 —— 那只會產生第二個 `INCONCLUSIVE`，什麼都沒證明。

### 6.3 R9-06 `_repo_head()` 修復（乾淨基線回合）
真缺陷，範圍明確，但必須在沒有 16 個既有失敗干擾的基線下做，否則會把別人的破損記到你帳上。

### 6.4 R9-05 repo 衛生（需 owner 決策）
把決定丟給測試檔作者，不要自己 stage。若 owner 同意，才把那 3 檔納入並重測。

### 6.5 SP 整合（設計已定，未實作）
最小設計：**兩個薄 typed adapter 掛在既有接縫**（PLAN handoff、VERIFY pre-spawn）＋邊界檢查。
不新增服務、不建第二個 registry、不建第四個 SP。`PREW3_SHADOW` 回 `NOT_DISPATCHED`。
已揭露未修：PLAN 與 VERIFY 過去共用同一模型（本回合已分開，但**模型級 SoD ≠ principal 級 SoD**）。

### 6.6 DOC-00..13 分階段計畫
先建**語意分母**（目前 UNKNOWN），再談完成度。沒有分母就報百分比＝把我們的計數選擇扮成契約的。
stop-loss：10 engineer-day 後無分母則停並回報。

---

## 7. 已證實的陷阱（不要重新發現）

### 7.1 每一道 gate 認證的是「存在」，不是「對應」
這是本程式最大的系統性缺陷，八個實例：

| gate | 實際比較 | 被誤當成 |
|---|---|---|
| drift gate | pin 對得起它指向的檔案 | 治理面彼此一致 |
| registry epoch | pin 對得起 assignment | registry 與 assignment 一致 |
| compiler | id／locator 存在且合法 | acceptance 屬於引用它的 capability |
| lane probe | 模型有服務 | SP 被呼叫 |
| selftest 9/9 | 本機旅程 | 受治理 native 鏈 |
| `ROOT_READY` 6/6 | 路徑存在、可 import | native admission |
| 14 components | 14 個 hash 存在 | 14 個能力已合格 |
| 218 passed | 測試會過 | 契約被滿足 |

**規則**：gate 只能為它直接量測的性質背書。任何「X 與 Y 一致」的宣稱，檢查必須**拿 X 比 Y**，
不能是「X 對 X 的 pin、Y 對 Y 的 pin」。

**本回合活生生的例子（D1 重現）**：pool/registry/assignment 改完後 drift gate 讀 **0 findings**，
但三個 runtime 宣告全都還寫舊模型。乾淨的 gate 完全沒有保護到真正該保護的東西。

### 7.2 控制包自己宣告分母 UNKNOWN
- DOC-02 L128 `D_clause_semantic=UNRESOLVED`
- DOC-04 L99 `semantic_source_clauses_total=NOT_ESTABLISHED`
- DOC-12 L7829 全域分母 `UNKNOWN`

可數的（≠ 語意分母）：4,738 筆文件限定需求記錄／4,589 個不同需求 id／1,341 個連結 ACC id。
**任何完成率都是偽造。**

### 7.3 其他踩過的
- **D2**：epoch 是**聯合**不變式。單邊釘等於看不到單邊 bump。是 dispatcher 的 `ERR_LANE_STALE_EPOCH` 抓到的，不是 gate。
- **D3**：修了產物沒修產生它的程式碼 → 同類缺陷復發。R10 因此**載入** R8 builder 而不 fork。
- **registry 的 `arms` 與 `fallbacks` 是兩個有序清單**，必須從新的 `arms` 推導 `fallbacks`，否則兩者互相矛盾。
- **drift 紅了先判斷哪一側錯**。R10 那次：route 與宣告都已對齊 mandate，**是 projection 期望過時** → 補完宣告、保留檢查。放寬期望讓檢查變綠＝刪掉檢查。
- **lease 掛在 acceptance id**，`expected_version` 用該筆 acceptance 自己的版本（首筆 `0`，不是 requirement 的版本）。
- **`var/` 被 gitignore**（`.gitignore:9`）→ 回合工具、備份、receipt **只存在磁碟，不在 repo**。這是 R9-05 同類的可重現性缺陷。
- **並行寫者是真的**：本回合 `config/project.json`、`src/hg_kseos/{knowledge,spine}.py`、`scripts/hermes-core.ps1`、`source-freeze/TT_LEDGER.csv`、`tests/test_task014_named_method_closure.py` 都被**別人**改動中。不要 stage。
- **FAR run 編號會撞號**：R9 封緘期間有人建了 `FAR-...-024-fallback-chain-reorder`，本回合改號 025 並揭露。
- **subagent summary 不保證落盤**：R9 的 4 份 worker 輸出只有 3 份有檔案，第 4 份 inline 遞送、harness 沒寫檔。宣稱時要說「3 份」不是「4 份」。

---

## 8. 關鍵路徑地圖

### HG-KSEOS（控制平面）
```
config/lane-route-slots.candidate.json     canonical pool（PLAN r1=minimax, EXECUTE r1=deepseek）
config/lane-routing-registry.yaml          routes/arms/fallbacks/projections，epoch 29
config/model-lane-assignment.json          registry_epoch 29（必須與 registry 同步）
config/hermes-codex-lane.json              sealed EXECUTE lane（model=deepseek）
config/hermes.json                         provider_route.model=deepseek
scripts/hgk-lane-dispatch.py               派工（--force-rank 選 arm，--require-arm 是斷言不是選擇器）
src/hg_kseos/lane_policy.py                check_drift()
src/hg_kseos/lifecycle.py                  typed admission；_repo_head() 缺陷在此
var/shared-spine/hg-kseos.db               HGK spine
var/R10-LANES/apply_plan_exec_swap.py      本回合 rebind 工具（var/ 被 gitignore！）
var/R10-LANES/sync_runtime_decls.py        本回合 runtime 宣告同步工具
var/R10-GATE/final_summary.json            改綁後三車道實測
_sbl_harness_adapter/                      3 檔，untracked
```

### SBL（產品）
```
_sbl_r9_candidate/                          R9 product worktree（candidate 32d971d）
contracts/SBL_C0_C9_CONTRACT-R9.json        34 edges, 0 mismatch, sha256 dd200277…
contracts/CONTROL_PACKAGE_MANIFEST.json     14 docs pinned, rollup 01b972c8…
contracts/compiled-r9/                      四階段 compile 產物 + COMPILER_RECEIPT
tools/check_control_package.py              控制包驗證器（3 種負控）
tests/test_contract_binding.py              合約綁定回歸測試（4 斷言）
tests/test_control_package_manifest.py      控制包 manifest 測試（6 測試，可攜）
_governance/round-20261021-r9/FAR-R9-RULING.md    R9 FAR 裁決
_governance/round-20261021-r9/SELF_CHECK_R9.json  10/10 PASS
```

### 上位控制包（唯一工程契約）
```
C:/Projects/Agent_Workspace/_sbl_src_mirror/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-00.md … DOC-13.md
C:/Projects/Agent_Workspace/知識庫/.../SBL_PIPD-LS-PKG/      byte-identical 第二來源
```
**17 MB 不要整份讀**。用 `tools/check_control_package.py` 釘 digest，按需讀單份。

### 其他
```
C:/Projects/Agent_Workspace/Fabric/fabric-autonomous-research/runs/FAR-20261021-025-sbl-r9-ctrlpkg/
C:/Users/user/AppData/Local/hermes/kanban.db          canonical Kanban（board sbl-pipdls-20261020）
.../Local/hermes/profiles/hgk-governed/config.yaml    governed PLAN profile（現為 minimax/opencode-go）
.../Local/hermes/hermes-agent/venv/Scripts/python.exe canonical Hermes venv（已裝 sbl-v01）
C:/Projects/Agent_Workspace/_sbl_checker_env/Scripts/python.exe   checker venv（有 pytest/build）
```

---

## 9. 宣稱天花板

**本回合 = `CANDIDATE_ONLY`**：
- lane rebind 是 **candidate pool + candidate 宣告**的重排，在 owner 授權下套用
- **不是** native issuer 簽章、**不是**任何 subject 的 acceptance、**不是** pool promotion 到 ACTIVE
- **不是**任何車道在綁定下執行的證明 —— 每車道只有一次實測探針
- governed PLAN profile 的變更**在下次啟動該平面時才生效**，尚未在該模型下啟動過
- 安裝仍是 `STANDALONE_ONLY`／`HOST_PENDING`；native effect 仍是 `NOT_GRANTED`

**延續的既有天花板**：
- R7 獨立裁決永久為 `INCONCLUSIVE — NOT ACCEPTED`，HGK 記 `FAIL`
- `full_contract_state = OPEN__PARTIAL__NOT_FULL_CONTRACT_PASS`
- DOC-00..13 **沒有**完成率，因為分母 UNKNOWN

---

## 10. 新 SESSION 的前 5 個指令

```bash
# 1. 看控制平面現況（唯讀）
cd C:/Projects/Agent_Workspace/HG-KSEOS && git log --oneline -3 && git status --porcelain | head -20

# 2. 確認 drift 與 epoch
./.venv/Scripts/python.exe -c "import sys;sys.path.insert(0,'src');from hg_kseos import lane_policy as lp;f=lp.check_drift();print('findings',len(f),'fatal',lp.drift_is_fatal(f))"

# 3. 複驗 mandate（§1 的三條 probe；任一 ok=false 就停下問 owner）

# 4. 重測 conformance（§6.1）—— 這是後面所有宣稱的前提
./.venv/Scripts/python.exe -m pytest tests -q --timeout=900

# 5. 讀 HGK spine 的 R9 鏈，確認 acceptance = FAIL 而不是你以為的 PASS
./.venv/Scripts/python.exe -c "import sqlite3;c=sqlite3.connect('var/shared-spine/hg-kseos.db');print(c.execute(\"select acceptance_id,verdict,evidence_ref from acceptances where acceptance_id like '%R9%'\").fetchall())"
```

然後從 §6.2 開始：**去拿第一個獨立裁決**。

---

## 附錄：R10 回合自身的揭露

- HG-KSEOS `b22706e`：5 檔 staged。**未** stage 他人改動的 6 個檔案。
- 本回合工具在 `var/R10-LANES/`，但 `var/` 被 gitignore → **不在 repo**（同 R9-05 缺陷）。
- FAR run 由 024 改號 **025**，因並行寫者佔用 024；對方 run 未被觸碰。
- 先驗證後改綁：三個目標 arm 在**改綁前**以 `--force-rank` 實測通過，改綁後再測一次。暫停條款從未觸發。
