# FAR 偏離研究與工程裁決 — SBL R12（2026-10-21）

**方法**：FAR（Fabric Acceptance Review）式偏離研究 — 只列**可重算的觀測**，逐項對映上位條款，給「低阻力、高可行、必要、不過度工程化」的最小關閉路徑，再做一次裁決（DECIDE / DEFER / NO-ACTION）。
**法位**：`SBL_PIPD-LS-PKG_DOC-00..13` 是唯一產品契約（normative）；`Fabric` 為政策契約面；`HG-KSEOS` 為唯一 issuer；本文件是**工程裁決建議**，不簽發 Permit、不代替 Owner、不代替獨立 Checker。
**輸入**：本機直測（DOC 14/14 + rollup、KP 20/20、skills 2/2、vols 10/10、compiler 四階段、R9 負控 6 passed、HGK conformance 18F/578P/90 subtests、三車道 mandate 探針、stack/adapter 讀回）、外部 reviewer R8（§0/§9/§10）、R9 FAR、R10 handover、GitHub 遠端讀回。

---

## 1. 直測基線（本回合）

| 事實 | 值 | 證據 |
|---|---|---|
| SBL `main` | `345b9477` → **本回合經 PR #5 併入 r9 後 `31406ad7`** | `git ls-remote` + API readback |
| 唯一未併候選 | `candidate/r9-20261021-ctrlpkg`（main 為其祖先，FF 可能；10 檔 +3362/-0，全新增） | `git merge-base --is-ancestor`、`git diff --stat` |
| 其餘候選 | `c3-20261021-v2`、`r7-20261021-repro-build`、`release/0.1.1rc1`、`r2-*`、`c3-20261020-v1` **全部已是 main 的祖先**（0 commits ahead） | `git rev-list --left-right --count origin/main...<b>` |
| r9 CI（該 SHA） | ubuntu **success** / windows **success** | GitHub check-runs API |
| 三車道 mandate | PLAN `gpt-6.1-sol`(rank2 強制)、EXECUTE `minimax-m3.1-flash-free`(rank2 強制)、VERIFY `gpt-6.1-sol`(rank1) 全部 `required==served`、usage 200 | `var/R12-FAR-20261021/*.json` |
| HGK conformance | 18F / 578P / 90 subtests（dirty tree，兩次同分母） | `evidence/r11-20261021-intake/hgk_conformance.log` |
| 宣告面 drift | registry epoch 29 PLAN rank1 = `minimax`，與 Owner mandate（PLAN=`gpt-6.1-sol`、EXECUTE=`minimax`）**對調** | registry bytes vs mandate |

---

## 2. 偏離登記（Deviation Register）

等級：`BLOCKER`（阻斷當前可交付）/ `GAP`（能力缺口）/ `DEBT`（工程債）/ `OBS`（觀察，不阻斷）。
工作量：`XS<1h`、`S 1–3h`、`M 1–2d`、`L >3d`。

| ID | 觀測（可重算） | 對映條款 | 級 | FAR 裁決 | 最小關閉路徑 | Owner | 量 |
|---|---|---|---|---|---|---|---|
| **D-01** README/Release 宣稱漂移 | `main@345b9477` README 寫 `CANDIDATE_ONLY`／`Not released`／`one console script, sbl-todo`；實際 2 個 release、`pyproject` 3 個 entrypoint | DOC-12 C43/C49；DOC-00 R03 bounded claims | DEBT（公開可誤導） | **DECIDE：立即修（純文件）** | 一次 docs PR：狀態段 + 3 entrypoints + 保留 claim ceiling；不重寫架構 | Docs Owner | XS |
| **D-02** r9 控制包 pin 未併 | FF 可併、CI 兩 OS 綠、10 檔全新增、R8 WO-01 建議 | DOC-00 C48；DOC-06 C33.2 | BLOCKER（已解） | **DECIDE：已併（PR #5）** | 已完成：`31406ad7` | repo Owner | XS |
| **D-03** 過期候選堆積 | 7 個 candidate/release 分支皆為 main 祖先 | DOC-13 版本治理 | DEBT | **NO-ACTION（標註，不刪）** | 在各分支加 archive 說明或刪分支指標；不重寫歷史 | repo Owner | XS |
| **D-04** 語義分母 UNKNOWN | DOC-02 L128 / DOC-04 L99 / DOC-12 L7829 自述；4738/4589/1341 三種計數並存 | DOC-02 C01–C09；DOC-08 | GAP | **DEFER（Owner trigger）** | 分階段 taxonomy + dedup/alias + Owner 簽分母；**在此之前禁止任何完成百分比** | PIPD Source Owner | L |
| **D-05** 五工具端到端鏈未證 | stack `14 components / STANDALONE_ONLY / host NOT_INSTALLED`；harness `HOST_PENDING / native_effect NOT_GRANTED` | DOC-12 C-001..038 | BLOCKER（需授權） | **DECIDE：編入 HGK 專項 WO** | 一個 admitted WO 貫穿 dispatcher→writer→checker→readback；不是再量的問題 | HGK issuer + Hermes Owner | M |
| **D-06** Commander/Challenge 兩薄 adapter 未接 | PLAN/VERIFY 車道可服務，但無 SP `invocation_id` | DOC-04 C15；DOC-08 C40；DOC-10 | BLOCKER（需授權） | **DECIDE：編入同一 WO（與 D-05 合併）** | pre-handoff / pre-spawn 兩個接點 + `required==served` + SP 收據 | Commander/Challenge Owner | M |
| **D-07** R9-02 獨立 Checker 無 scratch | 無 isolated writable scratch 授權 | DOC-08 C39–C42 | BLOCKER | **DECIDE：Owner 一次授權** → **已授權 2026-10-23（`DEC-R12-D07-O2-20261023`）：CLOSED-GUARD** —— grant 已落地（scope+expiry+subject digest，候選唯讀，subject 凍結 `origin/main@dc5428f2`）；granted scratch 內全套 SBL suite 218 passed / 2 skipped / 0 failed，pin `CONTROL_PACKAGE_PINNED`，subject tree 不變；**R9-02 驗收回合本身仍 OPEN** | 授權一個 checker-only 可寫根（候選唯讀）→ 跑一次並留 raw（已做，見 `O2_D07_CHECKER_SCRATCH_GRANT.md` + `o2_checker_scratch/`） | lane Owner | S |
| **D-08** 他人 untracked 測試 9 模組 | HGK dirty tree：9 測試模組 + 2 `.bak` + `tests/w3_solution/` + 1 modified | DOC-07 C44；DOC-11 | DEBT | **DECIDE：二選一（建議收編）** → **已裁決 2026-10-23：收編（ADOPT）已執行** —— 9 模組皆 tracked（`7d9b64b`/`9fa79dd`），`.bak` 隔離保留於 `var/quarantine/bak-20261022/tests/`，modified 測試原樣留檔 `db68ee4`；R9-05 乾淨 checkout 對齊仍 PARTIAL（無完成百分比，D-04 ceiling）；見 `O3_D08_ADOPTION_RECORD.md` | 由作者確認後以獨立 commit 收編，或在 `var/` 隔離；**禁止本回合名義 stage**（已按收編路徑執行） | HGK Test Owner | S |
| **D-09** `_repo_head()` CWD 缺陷 | `lifecycle.py:462` 的 `git rev-parse HEAD` **未帶 `cwd=`／`-C`**，繼承 launcher CWD；`line 463` 把非零 exit 轉成 `""`（靜默失敗）；`_repo_head()` 本身不吞例外，但 **caller `admit_requirement()` 在 `line 606–607` 把 `InvariantViolation` 吞掉**。callers 在 `line 383/604` | DOC-05 C19 | GAP | **DECIDE：HGK 專項 WO 修（26 行 diff + 2 個測試函式／6 cases 已於記憶體套用驗證 RED→GREEN，repo 未改）** | 先 RED（target≠CWD、例外上拋）→ 最小修 → 受影響 regression | HGK project Owner | S |
| **D-10** conformance 指令不可照抄 | `--timeout=900` 不存在；`hg_kseos` 未安裝進 venv；18F/16F 分母不可互比 | DOC-00 R03（證據誠實） | DEBT | **DECIDE：文件化 + CI guard** | 在 repo 記下唯一可重跑指令與前置；CI 固定同一條 | HGK Docs Owner | XS |
| **D-11** 車道宣告面互斥 | epoch 29 PLAN rank1=minimax vs mandate PLAN=gpt —— **已被事件取代**：epoch 30/31/32 rebind 已於 2026-10-22 帶 WO 紀律落地（`924af95`/`bb67397`/`c3727d4`），2026-10-23 實測宣告面 routing 軸與 owner 令一致 | DOC-04 C15（角色分離） | ~~DEBT~~ → **CLOSED_SUPERSEDED_BY_EVENTS** | **DECIDED（DEC-R12-D11-O1-20261023）：(a)+(b) 並用為常態** —— binding 變更走 issuer rebind（宣告面必須追上，含敘述欄位），mandate chain 為每輪斷言／證據層 | 殘餘 **D-11b**：rev32 `sod.*` 敘述散文 stale 且被 projection `expected` 釘死（gate 綠但宣告面自我矛盾）→ issuer 一個 commit 同步改散文＋pin；見 `D11_O1_LANE_DECLARATION_DECISION.md` | Owner + HGK issuer | S |
| **D-12** 三 ChatGPT 私人 Plugin 0/3 | 無 Host-issued id | DOC-12 C-016..018 | BLOCKER（外部） | **DEFER（Host 權限）** | Host 授權後 3×create/install/@invoke/deny/uninstall | Host Owner | M |
| **D-13** 441/149/38 runtime 逐項 | 只有 identity/ledger，無 per-item runtime | DOC-06 C33.2；DOC-01 C05 | GAP | **DEFER（順序裁決）** | **不得先做**：須在 D-05/D-06 通了之後才有意義 | OSS/Native Owner | L |
| **D-14** CR-PLUGIN-SCHEMA-AUTHORITY | `NOBJ-017` 為 `PROHIBITED`，與 ChatGPT 插件封裝實務衝突 | DOC-06；DOC-12 | BLOCKER（法位） | **DECIDE：Owner 一次裁決** → **已裁決 2026-10-23（O-4）：選定 ChatGPT private GPT（GA, DOC-12 C36.3）為合規封裝面**；`NOBJ-017`（Agent Plugins 1.0 WD）**維持 PROHIBITED**（例外已記錄，未由 agent 解禁）；C-016..C-018 仍 `HOST_PENDING`；見 `O4_NOBJ017_EXCEPTION_RECORD.md` + `O4_NOBJ017_exception.json` | 明文選定合規封裝面，並記錄例外；不得由 agent 解禁（已按此執行） | Product/Host Owner | XS |
| **D-15** CR-GPTB-KP-R04 極性 | 多處 `MUST NOT` 與正向語義相衝 | KP01/KP04（support 層） | OBS | **DECIDE：承認 polarity，不改 DOC** → **已裁決 2026-10-23（O-5）：承認並記 CR** —— `CR-GPTB-KP-R04-POLARITY.md` 已落地（source unchanged，0 DOC/KP 檔被改），20/20 R04 維持 `POLARITY_UNVERIFIED` 隔離，DOC 為上位；KP corpus 加列交 Knowledge Owner（7 份位元組相同副本，canonical 未指定） | 開 CR 記錄，KP 不得覆寫 DOC（已做） | Knowledge Owner | XS |
| **D-16** SWOF W3 未授予 | 無 ACK/permit | DOC-07；DOC-13 | OBS | **NO-ACTION（維持 shadow）** | PREW3_SHADOW 一律 NO_EFFECT | SWOF Owner | XS |
| **D-17** TPM/Commander 候選包路徑壞 | 兩者 README 指向不存在的 packaged skill 路徑（`subagent/SKILLS_PRACTICALITY.md` 逐檔核對） | DOC-12 C-001/C-002 | DEBT | **DECIDE：先修 package layout 再談落地** | 選定 direct-skill 或 portable-plugin layout 之一並驗證；不得兩者混用 | SP Packaging Owner | S |
| **D-18** `sbl-stack` doctor 顯示 live-source digest drift | 已部署 stack 的 **14 個元件中 13 個 digest 不符**（子代理實跑 `doctor`）；operator 文件漏列必要參數 | DOC-12 C-033；DOC-13 | DEBT | **DECIDE：由 owner 對齊 pins 並補指令文件** | 重跑 doctor 到 0 mismatch；補 `--root/--target` 必要參數 | Stack Owner | S |
| **D-19** 兩個 canonical bundle 缺 literal `SKILL.md` | `construction-acceptance-prompt-compiler` 與 `challenge-review` 都只有 `*-SKILL.md`，無 literal `SKILL.md` entry file → **challenge-review 過不了自身 qualification check**（compiler 的 lint + 5 唯讀測試含 18 golden fixtures 仍通過） | DOC-08 C39–C42 | DEBT | **DECIDE：owner 補 entry file，不 fork** | 由 bundle owner 最小修正並回報 digest；本 repo 不 vendoring | Checker Owner | XS |

---

## 3. 需 Owner 決策（不可由 agent 代決）

| # | 決策 | 選項 | FAR 建議 | 若未決的後果 |
|---|---|---|---|---|
| O-1 | PLAN 車道宣告面 | (a) epoch 30 rebind（同步 90 pin）／(b) 常態 mandate chain | **已裁決 2026-10-23（DEC-R12-D11-O1-20261023）：拒絕二選一** —— (a) 已於 2026-10-22 三次執行（epoch 30/31/32，WO 紀律）；常態規則＝**rebind-on-order**（binding 變更必須讓宣告面追上）＋ mandate chain 作為每輪斷言／證據層；原「(b) 先做」建議 **SUPERSEDED**。殘餘 D-11b 交 issuer | —（決策已落；D-11b 由 issuer 一個 commit 關閉，見 `D11_O1_LANE_DECLARATION_DECISION.md`） |
| O-2 | Checker scratch（R9-02） | 授權／不授權 | **已裁決 2026-10-23：已授權**（`DEC-R12-D07-O2-20261023`，24h expiry，scope 限 checker scratch round root，候選唯讀，subject digest guard） | —（決策已落；R9-02 驗收回合本身仍 OPEN，見 `O2_D07_CHECKER_SCRATCH_GRANT.md`） |
| O-3 | untracked 測試收編（D-08） | 收編／隔離／丟棄 | **已裁決 2026-10-23：收編（ADOPT）已執行** —— 9 模組 tracked，misattribution 關閉（作者不從 git 歷史推定） | —（決策已落；R9-05 乾淨 checkout 對齊仍 PARTIAL，見 `O3_D08_ADOPTION_RECORD.md`） |
| O-4 | Plugin schema 法位（D-14） | 選合規封裝／維持禁止 | **已裁決 2026-10-23：選 ChatGPT private GPT（GA, DOC-12 C36.3）並記例外**；NOBJ-017 維持 PROHIBITED | —（決策已落；三 Plugin 仍 `HOST_PENDING`，見 `O4_NOBJ017_EXCEPTION_RECORD.md`） |
| O-5 | KP-R04 polarity（D-15） | 承認衝突／改 KP | **已裁決 2026-10-23：承認並記 CR，不改 KP** | —（決策已落；標準答案固化於 `CR-GPTB-KP-R04-POLARITY.md`，後續回合引用不再重辯） |

---

## 4. 候選項 / SKILL 落地實用性（FAR 裁決）

| 對象 | 現況 | 裁決 | 理由（低阻力/不過度工程化） |
|---|---|---|---|
| `contracts/SBL_C0_C9_CONTRACT-R9.json` + `compiled-r9/` | 已併入 main（PR #5） | **LANDED** | 控制包身份 pin 是後續一切的前提；additive、CI 綠 |
| `tools/check_control_package.py` + 2 個測試 | 已併入 main | **LANDED** | 三負例可重跑，是防 drift 的最小機械守衛 |
| Hermes `sbl-stack` skill | 可跑 status/diagnosis；但 `doctor` 顯示已部署 pins 與 live source **digest drift**，且 operator 指令漏列必要參數（D-18） | **NEEDS-WORK** | 能用 ≠ 可交付；先由 owner 對齊 pins 與補參數，否則把 drift 寫成文件只會固化錯誤 |
| Hermes `hgk-governed-runtime` skill | 機器綁定的 adapter/config，非可攜控制包 | **KEEP-EXTERNAL** | 把機器配置搬進產品 repo 會製造第二權威 |
| Hermes `tpm-sp` skill | 會話層 demand 釐清可用；but 候選目錄 README 指向**不存在的 packaged skill 路徑**（D-17） | **NEEDS-WORK** | 先選定 direct-skill 或 portable-plugin layout 並驗證，再談落地 |
| Hermes `commander-sp` skill | 讀取/凍結輸入可用；同樣 package path 壞（D-17） | **NEEDS-WORK** | 同上；prompt 可用 ≠ 可運行且受權的 build package |
| Hermes `external-challenge-sp` skill | 唯讀、候選綁定的諮詢式審查；**不是**已簽的 canonical verdict | **KEEP-EXTERNAL** | 本機副本含 host-local research 增補，不得靜默升格為產品 canonical reviewer |
| `construction-acceptance-prompt-compiler` bundle | refs/schema/scripts 齊、四階段 rc0、lint + 5 唯讀測試（含 18 golden fixtures）通過；但缺 literal `SKILL.md`（D-19） | **KEEP-EXTERNAL + 待 owner 補 entry file** | 17MB 級參考物不得 vendoring；entry file 缺失由其 owner 修，本 repo 只記 digest |
| `challenge-review` bundle | 含 `verify_review_bundle.py`；同樣缺 literal `SKILL.md`，**過不了自身 qualification check**（D-19） | **KEEP-EXTERNAL + 待 owner 補 entry file** | 留在 maker repo 之外才可能獨立；修好前不得作為 release-significant checker |
| `openspec/changes/sbl-v01-candidate-build` | 既有 | **KEEP** | 歷史變更記錄，不回改 |
| 新 OpenSpec change（本回合） | 未建 | **CREATE（窄）** | 只記錄 FAR 裁決與本次併入/修補，不重述 DOC |
| 過期候選（D-03） | 7 個已是祖先 | **NO MERGE / 標註** | 合併無內容可併；刪除會破壞外部引用 |

---

## 5. FAR 裁決（Adjudication）

1. **控制包先落地**：r9 併入 main（已完成，`31406ad7`）。這是唯一有外部 reviewer 明文建議、CI 兩 OS 綠、且 additive 的候選。
2. **宣稱先對齊**：README 只改「狀態 + entrypoints」，不重寫產品敘事（D-01）。公開 repo 的錯誤宣稱是目前最廉價、最傷信任的缺陷。
3. **把「量」換成「鏈」**：D-05/D-06/D-07 是同一個 blocker 的三段（WO→SP→checker）；分開做等於三次空轉，**必須合併為一個 HGK 專項 WO**。
4. **拒絕過度工程**：semantic denominator（D-04）、441/149/38（D-13）在三段鏈通之前**不啟動**；先建鏈，再談分母。
5. **法位一次講清**：D-14/D-15 由 Owner 一次裁決，避免每輪重開。
6. **不刪歷史**：過期候選標註不刪；`.bak` 與 evidence 分支保留。

---

## 6. 執行方案（Owner 預授權範圍內）

| # | 動作 | 執行者 | 驗收 | Rollback |
|---|---|---|---|---|
| E1 | 併入 r9（PR #5） | Hermes + GitHub API（owner-authorized） | merge sha `31406ad7`；remote main readback | `git revert -m 1 31406ad7` |
| E2 | README 宣稱修正（D-01） | **CODEX CLI bounded writer**（EXECUTE=`minimax-m3.1-flash-free`），cwd=worktree、只准改 README | diff 僅 README、四處替換、claim ceiling 保留 | 丟棄分支 `docs/r12-claims-20261021` |
| E3 | conformance 指令文件化（D-10） | 同 E2 分支（docs） | 新增 `docs/RUN_CONFORMANCE.md`，指令可照抄 | 同上 |
| E4 | OpenSpec change 記錄（FAR 裁決） | 同 E2 分支 | `openspec/changes/far-r12-20261021/{proposal,tasks}.md` | 同上 |
| E5 | PR + Owner 合併（非 force） | GitHub API | CI 兩 OS 綠 + merge sha | revert |
| E6 | FAR 證據封包 + 推送 evidence 分支 | Hermes | 遠端 SHA == 本地 | 刪分支 |
| E7 | Kanban SWARM DAG | `hermes kanban swarm` | board readback 寫入封包 | 刪 board |
| E8 | **不執行**（需授權）：D-05/06/07/09/12/13/14 | — | 卡片保持 open，附 owner 與最小條件 | — |

**E2–E5 的邊界**：只碰 `README.md`、`docs/RUN_CONFORMANCE.md`、`openspec/changes/far-r12-20261021/**`。不碰 `sbl_core/`、`sbl_sp/`、`contracts/`、`tests/`。

---

## 7. 不過度工程化聲明

- 本輪**沒有**新增抽象層、沒有引入新依賴、沒有改產品程式碼。
- 沒有把兩個 17MB 級 bundle vendoring 進 repo（那會製造第二權威）。
- 沒有為了「看起來完整」而啟動 semantic denominator 或 441 逐項安裝（那些需要 L 級工程量且此刻無意義）。
- 每一項裁決都可回溯到：一條 DOC 條款、一個可重算的觀測、一個具名 owner。

## 8. 主張上限

本文件是**建議 + 已執行清單**，不是驗收。`SBL_FULL_PRODUCT` 仍 **OPEN**；本輪可宣稱的上限是：
「控制包身份 pin 已併入 main（`31406ad7`，CI 兩 OS 綠）、公開宣稱已對齊實際 release、四項 Owner 決策已具名、三段鏈（WO→SP→checker）已被識別為單一 blocker 並排入下一步」。
**不可**宣稱：任何 native 效果、任何 Host 安裝、任何 DOC 語義條款的完成、任何完成百分比。

## 9. 附錄：子代理研究輸入與本文件的修正

本文件 §4 的第一版是在兩個並行子代理回到結論**之前**寫的；子代理回報後已就地修正（本節即更正記錄，不掩蓋）：

| 子代理 | 產出 | 對本文件的影響 |
|---|---|---|
| skills／bundle 實用性稽核 | `subagent/SKILLS_PRACTICALITY.md`（逐檔核對 frontmatter／references／scripts／assets，並實跑 `sbl-stack doctor`） | §4 由「全部 KEEP」改為：`tpm-sp`／`commander-sp`／`sbl-stack` = **NEEDS-WORK**（packaged skill 路徑壞、digest drift、指令漏參數）；`external-challenge-sp`／`hgk-governed-runtime`／compiler／challenge-review = **KEEP-EXTERNAL**；新增 D-17/D-18/D-19 |
| `_repo_head()` 缺陷分析 | `subagent/R9-06_repo_head_report.md`（行號、26 行 unified diff、RED→GREEN 測試、可重跑唯讀 runner） | D-09 由「未修」細化為**精確行號 + 現成 patch + 測試**，維持「未套用（需 HGK permit）」 |

兩個子代理皆為**唯讀授權**，未寫入 HG-KSEOS／SBL 任何受版控檔案；其報告只落在本回合封包內，未改動任何產品程式碼。

