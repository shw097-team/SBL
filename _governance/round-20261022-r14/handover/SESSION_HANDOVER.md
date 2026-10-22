# SESSION HANDOVER — R14（新 SESSION 從這裡接手）

**寫入** 2026-10-22 · **前一個 SESSION** `20261021_224136_53890b`
**回合** `SBL-R14-FULL-DOC-POST-R13-20261022` · **master_goal** `SBL_FULL_PRODUCT`
**控制平面** SBL（產品工程指揮入口）＋ HG-KSEOS（唯一原生授權／狀態／驗收）· **Hermes** = 受治理 Runtime／Orchestration Plane

> 這份文件假設讀者**完全沒有**本 session 的記憶。凡是「上次」「先前」都用路徑與 commit 指到實體證據，不靠回憶。

---

## 0. 三句話現況

1. **31 筆義務：21 DONE / 5 PARTIAL / 4 BLOCKED / 1 BLOCKED_SOFT**。可自行推進的都推到「需簽名／需 permit／需 owner 裁決」的邊界。
2. **M1 SIGNED、M2 NOT_PASSED、M3 BLOCKED、M4 BLOCKED；`SBL_FULL_PRODUCT` 未完成。** DOC-00..13 語義驗收**不可宣稱**。
3. **有一個未結的審查訊號必須先處理**：第十輪 TS23 審查被中斷前，已在 `ts23_review` 找到一筆 **SURVIVED** 變異（見第 4 節）。在那筆坐實前，不得宣稱 M2 有進展。

---

## 1. 唯一權威來源（先讀這四個）

| 用途 | 路徑 |
|---|---|
| 義務清單（31 筆，機器可讀） | `C:/Projects/Agent_Workspace/HG-KSEOS/var/R14-OBLIGATIONS/OBLIGATIONS.json` |
| 義務驅動器（單步／審計） | `HG-KSEOS/var/R14-OBLIGATIONS/next_obligation.py`（`--audit` 驗證據路徑是否存在） |
| 命令文件（任務原文） | `C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/attachments/SBL_R14_POST_R13_HERMES_HGK_FABRIC_FULL_PRODUCT_COMMAND_PROMPT_2026-10-22.md` |
| 技術債／裁決登記（65 筆） | `_r14_ev/_governance/round-20261022-r14/SBL_R14_TT_CR_REGISTER.json` |

上一輪的暫停 checkpoint 與部分發現：
- `_r14_ev/_governance/round-20261022-r14/CHECKPOINT_R14_20261022.md`
- `_r14_ev/_governance/round-20261022-r14/REVIEW10_PARTIAL_FINDINGS.md`
- `_r14_ev/_governance/round-20261022-r14/R14_OWNER_DECISION_PACKET.md`（**只剩 owner 能做的五件事**）
- `_r14_ev/_governance/round-20261022-r14/FAR_R14_6_GSTACK_ADMISSION.md`

---

## 2. 四個 repo 的落點（交接時實測）

| Repo | HEAD | Branch | 狀態 |
|---|---|---|---|
| `HG-KSEOS` | `c94da94` | `codex/hgk-final-closure-002` | 乾淨。**無 remote**（本地即權威） |
| `_r14_ev`（證據） | `9c161c6` | `evidence/r14-20261022-native` | 乾淨，**本地＝遠端** |
| `SBL` | `10d510f` | `candidate/r14-ts15-kinds` | 2 個未追蹤項目是 **R9 舊物**（`contracts/SBL_C0_C9_CONTRACT-R9.json`、`contracts/compiled-r9/`），非本回合產出 |
| `PIPD` | `39079c0` | `rescue/r5p-uncommitted-20261016` | **dirty 218**，全是先前回合殘留；本回合**只讀不寫** |

`state_at_handover.json`（同目錄）有機器可讀版本，含 upstream 檔的 bytes/sha256。

---

## 3. 逐筆義務：5 PARTIAL 的精確缺口

### TS17 — DOC-08 軸線矩陣
- 已完成：768 格（8 skills × 12 TestClasses × 8 OracleTypes）；**32 格本回合真正重跑**（32/32 `REPRODUCED`，exit code 與 evidence digest 全符，`ts17_reexec_v3.py`）
- 缺：736 格 `DECLARED_ONLY`；**7 個 OracleType 無執行器**（STATE_READBACK、PROPERTY、REFERENCE_OUTPUT、STATISTICAL、SEMANTIC_JUDGE、HUMAN、COMPOSITE）；functional-native = 0
- 下一步：先做 `STATE_READBACK` 與 `REFERENCE_OUTPUT`（可用既有輸出與參考檔判定，不需發明語義），每接一個就把對應格轉 `RUNTIME_QUALIFIED` 並留執行收據

### TS19 / TS20 / TS21 — 上游 locator
- 已完成：**1202 列全部結案**（642 在位、560 位元組相同、0 不可修、0 位元組不同）；441 列各有相異 `row_digest`（舊值是 identity ledger 自身雜湊，欄位在語意不在）；我重算 200 列 digest **200 全符**
- 缺：**628 列沒有一列有執行收據**；TS19 上位藍圖**只剩回收桶副本**
- 下一步：為**可執行**的引用產生真收據，不可執行的明列理由。**不要把「有 locator」寫成「有收據」**

### TS23 — M2 sandbox（本回合主戰場）
- 已完成：九輪獨立審查；修掉 3 個**出貨缺陷**（未解析路徑、U+2028 截斷、尾端 NBSP 被 strip）＋3 個**儀器缺陷**（崩潰被當 catch、no-op 與 survivor 共用處置、死碼 `crash_shaped`）；37 變異 / 36 subjects / 36 caught / 0 survived / 九旗標全真
- 缺：**M2 NOT_PASSED**。第十輪審查被中斷，且**已有反證**（第 4 節）
- 誠實邊界：`remediation9.json` 明寫「本檔不宣告 M2 通過」

### TS29 — D-19 canonical bundle
- 已完成：全新安裝 manifest **14 元件**，14/14 在位、14/14 入 manifest、14/14 digest 相符、doctor ok；**8/8 PIPD skills** 帶 `SKILL.md` 與 digest。清單來源是產品自身宣告（`sbl_stack.COMPONENT_MODULES`、`PIPD/skills/*/SKILL.md`），**不是本回合同意出來的**
- 缺：**PIPD Source Owner 簽名**「哪一組才算 canonical」

---

## 4. 必須先處理：第十輪審查的部分發現

逐字 transcript：`_r14_ev/_governance/round-20261022-r14/raw/review10_partial/transcript.log`（原在會被 prune 的 cache，已入庫）

| 訊號 | 內容 | 動作 |
|---|---|---|
| **A（阻斷性）** | `ts23_review` 一筆變異 **SURVIVED**，`mutant_ran_and_answered: true`（不是崩潰，是活著答錯） | 讀 transcript 45–100 列抄出 `original`/`mutant` → 重跑確認 → **先加測試（RED）再修程式（GREEN）** → 加入 `MUTATIONS` 當回歸 |
| **B** | `no_op_control_detected` 曾變 `False` | 可能是旗標依賴「清單裡剛好有那筆」，也可能是真缺陷；**不可預設是前者**。修法：先驗 CONTROL 條目存在且 `original == mutant`，再看處置 |
| C（好消息） | 刪 `except UnicodeError` 的變異 → `CAUGHT` 且 `no_crash_counted: True`；narrowing 變異 → `crash_not_evidence`，不算 catch | 儀器修正有效，保留 |
| D（好消息） | 審查者自製 `PYTHONPATH` 遮蔽 → 全部判 `SHADOWED_IMPORT`，沒冒充 survivor | `TT-051` 修正有效，保留 |

**順序不可顛倒**：A 坐實 → 修 → 才重派第十一輪。**A 未坐實前，M2 沒有任何進展可宣稱。**

---

## 5. 4 BLOCKED ＋ 1 SOFT：全部是外部簽核（詳細版見 `R14_OWNER_DECISION_PACKET.md`）

| 義務 | 缺口 | 已備好的檔案 |
|---|---|---|
| TS12 (SOFT) | ChatGPT Plugin schema/host 權威 CR | `raw/ts10_12_PLAN.md` |
| TS25 / TS26 | SWOF **W3 permit**（TS24 已量測 0 permit） | `raw/ts24_w3_route_out.json` |
| TS27 | PIPD 語義分母**簽名** | `raw/ts27_denominator_proposal.md`、`ts27_denominator.json` |
| TS30 | 依賴 M2/M3 | `raw/ts30_m4_verdict.json` |

**代簽禁令**：這五項都不能由 agent 自己簽或自己裁成通過。TS27 特別注意——**不要自己挑一組數字當分母**，提案本身就寫明「packet 總數是 review workload，不是 `D_clause_semantic`」。

---

## 6. 車道與模型（registry epoch 32）

| 車道 | 模型 |
|---|---|
| PLAN | `opencode-go/deepseek-v4.1-flash` |
| EXECUTE（＆ Codex bounded writer） | `opencode-go/minimax-m3.1-flash-free` |
| VERIFY／SECURITY／Acceptance | `opencode-go/deepseek-v4.1-flash` |
| `config.yaml` delegation | `opencode-go/deepseek-v4.1-flash` |

- **`SOD006-C6`（OPEN_OWNER_ORDERED）**：PLAN 與 VERIFY 同模型是 owner 2026-10-22 為 GPT 配額下的命令；**殘存的分離只有流程、車道、證據路徑**。不要把它講成模型軸分離。
- 車道三平面（registry／assignment／pool）必須由**單一宣告**導出；`source_of_routes.sha256` **最後才釘**（`TT-047`）。
- pool 的 DEFAULT 是**旗標**（`role`/`default`/`automatic_selection`），不是陣列索引（`TT-048`）。
- 車道若有一處綁定住在車道檔之外（如 `config.yaml`），rebind 必須列清單逐項量測（`TT-050`）。

---

## 7. 恢復後照這個順序做

```bash
cd C:/Projects/Agent_Workspace && unset PYTHONPATH     # 見第 9 節，這行不是形式

# 1) 尖端與乾淨度
for r in HG-KSEOS _r14_ev SBL PIPD; do echo "== $r"; (cd $r && git log --oneline -1 && git status --porcelain | head -3); done

# 2) 義務現況
cd HG-KSEOS && ./.venv/Scripts/python.exe var/R14-OBLIGATIONS/next_obligation.py
./.venv/Scripts/python.exe var/R14-OBLIGATIONS/next_obligation.py --audit

# 3) 全套件（3 分鐘；PYTHONPATH=src 不可省，套件未裝進 venv）
PYTHONPATH=src ./.venv/Scripts/python.exe -m pytest tests/ -q -p no:cacheprovider --no-header

# 4) 回到本回合主戰場
cd ../_r14_packet/raw && sed -n '45,100p' ../_r14_ev/_governance/round-20261022-r14/raw/review10_partial/transcript.log
```

**第一件工作**：第 4 節訊號 A。**第二件**：TS17 的 `STATE_READBACK`／`REFERENCE_OUTPUT` 執行器。**第三件**：TS19/20/21 的執行收據。

---

## 8. 執行契約（owner 已給的授權，不要重新問）

- **Blanket authorization**：只有 HARD blocker（不可復原的破壞、憑證真缺、指定車道不可用）可停；其餘一律 量測 → 裁決 → 記 TT → 繼續，「像 owner 決策」必須附量測。
- **回合結束判準**：`next_obligation.py` 回 `DONE`，或 `ONLY_BLOCKERS` 且每個封鎖都有硬證據。進度一律報 `done/total, next <id>`。
- **M1 簽名**：owner 已明示「M1簽名」，`M1_NATIVE_CHAIN_READY` 4/4 已簽，**不要重簽也不要推翻**。
- **審查方判定才算 M2**：自己修只能是 remediation。八輪 FAIL、第九輪 FAIL 全部照實承接。
- **憑證**：`C:\Projects\Agent_Workspace\API KEY\GITHUB-REPO_SHW097-4.txt` 只以 wrapper 讀取，值一律 `[REDACTED]`，不進摘要、不進 commit。

---


---

## 8.5 檔案索引（同名容易搞混的，照這張表找）

| 口語名稱 | 實際路徑 |
|---|---|
| `next_obligation.py` | `HG-KSEOS/var/R14-OBLIGATIONS/next_obligation.py` |
| `remediation9.json` | `_r14_packet/raw/ts23_remediation9.json` |
| `review9.json` | `_r14_packet/raw/ts23_review9.json` |
| `SCOPE` | `_r14_packet/raw/ts23_SCOPE.md` |
| 變異 harness | `_r14_packet/raw/ts23_mutation_check.py` |
| 三支實作正本 | `_r14_packet/raw/ts23_src/{CLI_TOOL,AGENT_SKILL,SIMPLE_AGENT}.py` |
| 契約測試 | `_r14_packet/raw/ts23_src/extra/test_{cli,skill,agent}_extra.py` |
| build 產生器 | `_r14_packet/raw/ts23_build.py` |
| 生成沙箱 | `_r14_packet/raw/ts23_sandbox/`（`venv/`、`SBL/ts23_tests/`） |
| `config.yaml`（Hermes） | `C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/config.yaml` |
| 車道三平面 | `HG-KSEOS/config/{lane-routing-registry.yaml, model-lane-assignment.json, lane-route-slots.candidate.json}` |
| 8 個 PIPD skills | `PIPD/skills/*/SKILL.md` |
| 本交接的機器可讀版 | `_handover/R14-SESSION-HANDOVER-20261022/state_at_handover.json` |

## 9. 環境陷阱（本回合真的踩過的，不要再踩）

| 陷阱 | 症狀 | 正確做法 |
|---|---|---|
| **`PYTHONPATH` 污染** | `python -m` 載入 `.../Temp/ts23_r9/pkgs` 的舊同名套件，10 筆變異假 SURVIVED、2 筆 baseline 假紅 | 任何量測前 `unset PYTHONPATH`；harness 已用 `import_origin()` 擋（`SHADOWED_IMPORT`），但 shell 要先清 |
| 原生工具不吃 MSYS 路徑 | `git -C /c/...`、`node /tmp/a.js` 失敗 | 給 `C:/...` 形式 |
| Windows 不解析相對執行檔 | `subprocess` 找不到 `./.venv/.../python.exe` | 先 `(Path(cwd)/argv[0]).resolve()` |
| `write_file`／`patch` 內的 `\r\n` 逃逸 | 寫出的檔案字串內出現真換行，語法崩 | 用 `chr(13)+chr(10)` 或 `bytes.fromhex('0d0a')` 組字串 |
| `bash -c "$cmd"` 動態命令 | 被審批閘門擋、5 分鐘無回應 | 拆成 argv 以 `shell=False` 執行（`ts17_reexec_v3.py` 就是範例） |
| 子代理回報「綠」 | 可能是 baseline 被搬到錯誤狀態 | 自己重導三平面再驗（`TT-046`） |
| Codex CLI 路徑會隨 app 更新失效 | — | 現查：`ls -t C:/Users/user/AppData/Local/OpenAI/Codex/bin/*/codex.exe \| head -1` |
| **全套件必須在乾淨樹上跑** | `test_c2_case_run.py::test_r4_only_allowed_files_changed` 直接讀 `git status --porcelain`，任何未提交的改動（白名單外）都會讓它紅 | 先把改動 commit，再跑；不要把它的紅當成程式缺陷 |
| YAML 整檔重寫 | `yaml.safe_dump` 會蒸發註解（本回合真的發生：-286/+76 行） | 治理文件只做**單行手術式**修改 |

---

## 10. 誠實天花板（新 SESSION 不得往上調）

1. `SBL_FULL_PRODUCT` **未完成**；M2 NOT_PASSED、M3 BLOCKED、M4 BLOCKED。
2. 「HGK conformance 0 紅／646 passed」只代表**控制平面自身 harness**，不等於 DOC-00..13 語義驗收。
3. TS23 的「36 caught / 0 survived」是**我寫的變異集**下的結果；第十輪已證明**別人寫的變異會存活**。這個數字不能被引用為「合約成立」。
4. TS19 的 149 列修復，指向的是**被刪除的檔案**。位元組已保存（`upstream/`、`8e8327db…`），但「位置」不可證。
5. `GSTACK` **未准入**（CAND-11 = REFERENCE，來源／授權／版本未釘）。review/qa 走 `hgk_native_*` fallback；`route: GSTACK` 不得引用為已達成（`TT-055`、`FAR_R14_6`）。
6. 全量套件最後一次 **646 passed / 90 subtests / exit 0**（`var/R14-OBLIGATIONS/full_suite_after_delegation.log`）；其後的變更只有 ledger 註記與證據檔，**未重跑套件**——新 session 第一步請重跑。
