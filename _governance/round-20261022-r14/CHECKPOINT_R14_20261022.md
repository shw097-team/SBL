# CHECKPOINT — R14 回合暫停交接（可關機）

**寫入時間** 2026-10-22 · **原因** owner 要求暫停全部任務、落 checkpoint、交接後關機
**回合** `SBL-R14-FULL-DOC-POST-R13-20261022` · **master_goal** `SBL_FULL_PRODUCT`

---

## 0. 一句話現況

**21 / 31 義務 DONE**；5 PARTIAL、4 BLOCKED、1 BLOCKED_SOFT。所有可自行推進的部分都已推到「需要簽名／需要 permit／需要 owner 裁決」的邊界，**沒有任何工作在關機時處於半寫入狀態**。

---

## 1. 已停止的東西（關機前確認）

| 項目 | 狀態 |
|---|---|
| 子代理 `sa-0-655e0d50`（第十輪 TS23 M2 審查，`deleg_efdeefc6`） | **已下 stop**（interrupt_requested）。跑了大約 12 分鐘，未回報結論。它的 scratch 在 `...\hermes\cache\delegation\live\deleg_efdeefc6\`，可事後檢視但不保證完整 |
| 背景終端程序 | 全部已結束（`ts23_build` 兩次、`ts17_reexec` 一次、掃描程序皆 exit 0） |
| 寫入中的檔案 | 無。四個 repo 的 `git status` 已於本 checkpoint 前檢查 |

---

## 2. 各 repo 的落點（關機後回來就是從這裡接）

| Repo | HEAD | 遠端 | 工作樹 |
|---|---|---|---|
| `HG-KSEOS` | `b7ae9dc` + 本次 checkpoint commit | **無 remote**（本地） | 本次已提交，乾淨 |
| `_r14_ev`（evidence） | `38ec007` → 本次 checkpoint commit | `origin/evidence/r14-20261022-native` | 已推、本地＝遠端 |
| `SBL` | `10d510f`（branch `candidate/r14-ts15-kinds`） | 已推 | 有 2 個未追蹤項 `contracts/SBL_C0_C9_CONTRACT-R9.json`、`contracts/compiled-r9/`（**R9 舊物，非本回合產出**，未動） |
| `PIPD` | 未動 | — | 多個未追蹤 `.hgk/**/log_*.txt`、`tqaep_design_tmp/`（**先前回合殘留，本回合只讀不寫**） |

**恢復後第一件事**：`cd C:/Projects/Agent_Workspace/_r14_ev && git log --oneline -3` 確認 evidence 尖端，再讀本檔第 5 節。

---

## 3. Ledger（31 筆義務，權威來源）

檔案：`HG-KSEOS/var/R14-OBLIGATIONS/OBLIGATIONS.json`
驅動器：`HG-KSEOS/var/R14-OBLIGATIONS/next_obligation.py`（`--audit` 可驗證據路徑）

```
DONE 21 · PARTIAL 5 · BLOCKED 4 · BLOCKED_SOFT 1
未完成：TS12(soft) TS17 TS19 TS20 TS23 TS29 | TS25 TS26 TS27 TS30
```

### 5 筆 PARTIAL 的**精確**缺口

| 義務 | 已完成的部分 | 還缺什麼（不是模糊的「還沒做完」） |
|---|---|---|
| **TS17** | 768 格矩陣（8 skills × 12 TestClasses × 8 OracleTypes）；32 格 RUNTIME_QUALIFIED **本回合已真正重跑**（32/32 REPRODUCED，exit code 與 digest 全符） | 736 格 `DECLARED_ONLY`；**7 個 OracleType 在 repo 內沒有執行器**（STATE_READBACK、PROPERTY、REFERENCE_OUTPUT、STATISTICAL、SEMANTIC_JUDGE、HUMAN、COMPOSITE）；functional-native DOC-08 合格 = 0 |
| **TS19/20/21** | 1202 列 locator **全部結案**（642 在位、560 位元組相同、0 不可修）；441 列各有相異 `row_digest`；我重算 200 列 digest 全符 | **628 列沒有一列有執行收據**；TS19 上位藍圖**只剩回收桶副本**（見第 4 節）→ 需 owner 裁決「刪除副本可否充當上位」 |
| **TS23** | 九輪審查後修掉 3 個真缺陷（未解析路徑、U+2028 截斷、NBSP 被 strip）＋3 個儀器缺陷；37 變異 / 36 subjects / **36 caught、0 survived、九旗標全真** | **M2 仍 NOT_PASSED**。第十輪審查被暫停，未取得判定 |
| **TS29** | D-19 量測完成：全新安裝 14 元件 manifest，14/14 在位、14/14 入 manifest、14/14 digest 相符，doctor ok；8/8 skills 帶 `SKILL.md` 與 digest | 缺 **PIPD Source Owner 簽名**「哪一組才算 canonical」 |

### 4 筆 BLOCKED ＋ 1 SOFT（全部是**外部簽核**，我無權代簽）

| 義務 | 缺的東西 | 備好的檔案 |
|---|---|---|
| TS12 (SOFT) | ChatGPT Plugin 的 schema/host 權威 CR | `raw/ts10_12_PLAN.md` |
| TS25 / TS26 | SWOF **W3 permit**（TS24 已證明 0 permit） | `raw/ts24_w3_route_out.json` |
| TS27 | PIPD 語義分母**簽名** | `raw/ts27_denominator_proposal.md` + `ts27_denominator.json` |
| TS30 | 依賴 M2/M3，前四項鬆動後重發裁決 | `raw/ts30_m4_verdict.json` |

---

## 4. 關機前務必知道的兩件事

### (A) 上位文件只剩回收桶副本 — 不處理會消失
```
C:\$Recycle.Bin\S-1-5-21-...\$RY4OYY7\SBL_PIPD-LS-PKG_全DOC藍圖.md
2619602 bytes · sha256 8e8327dbc53be8a1722d1cd5…
```
**已另存**到 evidence 分支 `_governance/round-20261022-r14/upstream/SBL_PIPD-LS-PKG_全DOC藍圖_from_recyclebin.md`（同 digest 已驗），所以**關機不會弄丟**。但「recycle-bin 副本能否當上位正本」是 owner 決定（`TT-R14-053`）。

### (B) `PYTHONPATH` 會被上一個子代理污染（本次真的踩到）
曾出現 `PYTHONPATH=C:/Users/user/AppData/Local/Temp/ts23_r9/pkgs`，導致 `python -m` 載入舊副本、量測全錯。**恢復工作時，任何量測指令前先 `unset PYTHONPATH`**，或確認 harness 已印 `no_shadowed_imports: true`。

---

## 5. 恢復後的執行順序（照這個做，不要重新規劃）

```bash
cd C:/Projects/Agent_Workspace
unset PYTHONPATH

# 1) 確認三處尖端
cd _r14_ev && git log --oneline -2 && git status --porcelain
cd ../HG-KSEOS && git log --oneline -2 && git status --porcelain

# 2) 讀義務清單與下一步
cd HG-KSEOS && ./.venv/Scripts/python.exe var/R14-OBLIGATIONS/next_obligation.py
./.venv/Scripts/python.exe var/R14-OBLIGATIONS/next_obligation.py --audit

# 3) 全套件（務必 PYTHONPATH=src）
PYTHONPATH=src ./.venv/Scripts/python.exe -m pytest tests/ -q -p no:cacheprovider --no-header
```

**接下來要做的三件（已排序）**

1. **重派第十輪 TS23 審查**（原本 `deleg_efdeefc6`，被暫停）。指令要點已固定在 `ts23_remediation9.json` 與第九輪 `ts23_review9.json`：專攻 digest 閘門、probe 的錯誤呼叫覆蓋、`SHADOWED_IMPORT`、以及 SCOPE 是否只剩一種說法。**這一項決定 M2，也連帶決定 TS30。**
2. **TS17 的 7 個 OracleType 執行器**：先做 `STATE_READBACK` 與 `REFERENCE_OUTPUT`（可用既有輸出與參考檔判定，不需發明語義），每接一個就把對應格從 `DECLARED_ONLY` 轉 `RUNTIME_QUALIFIED` 並留下執行收據。
3. **TS19/20/21 的執行收據**：628 列中挑**可執行**的引用產生真實收據；不可執行的要明列理由，不要把「有 locator」寫成「有收據」。

---

## 6. 這回合真正學到的（已寫進 TT，恢復時別重犯）

| TT | 一句話 |
|---|---|
| 049 | 換模型必然改變 SoD 事實 → 寫成宣告（`SOD006-C6`），不是把守衛調鬆 |
| 050 | 車道若有一處綁定住在車道檔之外（`config.yaml` 的 delegation），rebind 必須列清單逐項量測 |
| 051 | 同名套件被 `PYTHONPATH` 搶先載入 → 先解析「會被載入的那個檔案」再變異 |
| 052 | probe 的 `ok` 不可用來判「答錯」；只有 traceback 才是崩潰 |
| 053 | 上游只剩回收桶副本 → 位元組可證、位置不可證 |
| 054 | 441 列同一個 digest = 欄位在、語意不在；判準用「相異值數 == 列數」 |
| 055 | GSTACK 不是沒裝，是控制包把 CAND-11 列為 REFERENCE 卻又被路由檢查標 CERTIFIED → 走 native fallback |

---

## 7. 誠實天花板（恢復後不得往上調）

- `SBL_FULL_PRODUCT` **未完成**；M1 SIGNED、**M2 NOT_PASSED**、M3 BLOCKED、M4 BLOCKED。
- 「HGK conformance 0 紅」只代表控制平面自身 harness，**不等於** DOC-00..13 語義驗收。
- 全量套件最後一次：**646 passed / 90 subtests / exit 0**（`var/R14-OBLIGATIONS/full_suite_after_delegation.log`）；本 checkpoint 之後的 `OBLIGATIONS.json` 變更只是註記，未重跑套件。
