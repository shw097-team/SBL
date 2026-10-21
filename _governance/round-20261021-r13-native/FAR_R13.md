# FAR 裁決 — R13：O-2 檢查者隔離、O-4 Plugin 封裝法位、以及 D-05/06/07/09 的單一 HGK 專項 WO

**裁決者**：FAR（Fabric Acceptance Review 方法）· **執行者**：Hermes（受治理 Runtime 面）· **日期**：2026-10-21
**法位**：`SBL_PIPD-LS-PKG_DOC-00..13` = 產品規範；`HG-KSEOS` = 唯一 issuer／spine；`Fabric` = 政策契約；本文件 = 工程裁決 + 執行方案。

---

## 0. 一句話裁決

**不要新增 Permit/ECP 子系統**。HGK 已經有等價原生四元組（`projects → requirements → taskspecs → workorders` ＋ `role_binding(scope/expiry/arm)` ＋ `lease(holder/token/ttl)` ＋ `record_workorder_result(evidence bundle)`），契約語彙只是尚未對映。低阻力、不過度工程化的做法是**加一張對映表 + 用既有原語真的跑一次**，而不是在唯一的控制平面上再蓋一層。

---

## 1. 觀測（本回合直測，非引用）

| 事實 | 來源 |
|---|---|
| HGK `src/hg_kseos/` 內**沒有任何 `permit` 字樣**；契約的 ONE ECP／Permit／ExecutionBinding 在 HGK 沒有同名物件 | `grep -rn -i permit src/hg_kseos/*.py` → 0 |
| HGK 原生有：`ProjectLifecycleController.start/intake/plan/admit_workorders/admit_requirement/checkpoint/transition`（14 態 + 5 側態的合法轉移表） | `lifecycle.py:29-72,105-390` |
| 有 `create_workorder(workorder_id, taskspec_id, writer, worktree, base_head)`，`taskspec` 必須 `DRAFT` | `spine.py:297` |
| 有 `records_workorder_result(writer, checker, verdict, evidence_refs, role_evidence, subject)`，**writer==checker 直接拒**（`ERR_WORKORDER_SELF_REVIEW`） | `spine.py:325` |
| TaskSpec 的 `permissions_json` 就是 ExecutionBinding 的載體，`role_binding` 為 key；`validate_binding` 對 scope/expiry/arm 逐項 fail-closed | `role_binding.py:1-60,297-340` |
| `validate_role_evidence` 要求：`workorder/session/round/subject/mandate_digest/role/surface/artifact_digest/checker_identity/guard`＋真實 lane receipt＋log refs＋獨立 checker＋`guard=CLEAN` | `role_binding.py:375-470` |
| 有 `acquire_lease(resource, holder, token, ttl)`——permit 的租約語義已存在 | `spine.py:113` |
| **`_repo_head()` 缺陷已在本回合以原生 admission 重現**：CWD 非 repo 時 `admit_workorders` 拋 `InvariantViolation: ERR_WORKORDER_CRITICAL_FIELD_MISSING` | `var/R13-NATIVE-20261021/stage_red.json` |

---

## 2. 契約語彙 → HGK 原生對映（本裁決的核心）

| 契約語彙（DOC-05/07） | HGK 原生實體 | 對映強度 |
|---|---|---|
| TaskSpec（工作規格） | `taskspecs`（DRAFT→ADMITTED） | 1:1 |
| Native WorkOrder | `workorders`（`workorder_id`, `writer`, `worktree`, `base_head`, `rollback_pointer`） | 1:1 |
| **ONE ECP** | 一個 project 下唯一的 `REQ-<project>-PLAN` + 其 taskspec 集合 | 結構等價（多 taskspec 屬於同一 requirement） |
| **ExecutionBinding** | `taskspecs.permissions_json.role_binding`（schema `HGK-ROLE-BINDING/1`：scope/expiry/arm/base_head/subject/mandate_digest） | 1:1 |
| **issuer Permit** | `leases`（holder/token/ttl）＋ WO 的 `CREATED` 狀態為唯一可寫窗口 | 語義等價（無獨立簽章物件） |
| 受權 write-set | `role_binding.scope`（陣列，路徑級）＋ `write_scope` | 1:1 |
| 完成證據 | `record_workorder_result(evidence_refs)` ＋ role-evidence bundle（含 served arm、log sha、artifact digest、獨立 checker、guard CLEAN） | **強於**契約最低要求 |
| 撤銷／重放 | `release_lease`、WO 僅 `CREATED→VERIFIED/FAILED`、`rollback_workorder` | 部分（重放防護靠 nonce＋receipt digest） |

**結論**：缺的不是能力，是**對映權威**。裁決：以 `docs/HGK_CONTRACT_MAPPING.md` 形式把上表落成 repo 文件（本回合執行），並以真實一次 admission→write→check→record 證明它不是紙上對映。

---

## 3. O-2 裁決：檢查者要的不是「可寫 scratch」，是「隔離輸出 + 唯讀候選」

- **問題重述**：R9-02 的阻斷被描述成「缺 isolated writable scratch」，於是解法看起來像「發一張可寫授權給 checker」。這是**方向錯誤**：給 checker 寫入權，等於讓它有能力污染受審物。
- **裁決**：
  1. **候選永遠唯讀**給 checker（`--sandbox read-only`）。
  2. checker 的產物（報告、測試 stdout、diff digest）寫到**獨立輸出根** `var/checker-scratch/<round>/`，由 dispatcher 落盤並記 sha；此根**不在**產品 repo、不在受版控路徑。
  3. 若 checker 必須執行測試，給它**候選的暫存副本**（`git worktree` 或 `cp -r` 到 scratch），永不給原件。
  4. 授權以「scope + 到期 + 主體 digest」記錄，而非一張空白可寫通行證。
- **為何低阻力**：不需要改 HGK、不需要新角色、不需要新的簽章體系；現有 `lease` + `role_binding.scope` 已能表達。
- **殘留**：若 Owner 堅持「checker 必須對候選有寫入權」，那與 DOC-08 的獨立性直接衝突，本裁決不採；列為 `OWNER_OVERRIDE_REQUIRED`。

---

## 4. O-4 裁決：三 Plugin 停在 `HOST_PENDING`，不追逐草案封裝

- **法位衝突**：`DOC-06/NOBJ24/NOBJ-017` 明確 `PROHIBITED`（Agent Plugins 1.0 Working Draft）。任何以該草案為基礎的「ChatGPT 私人 Plugin」封裝都違反上位條款。
- **裁決**：
  1. **不**以草案封裝出貨，**不**把 Hermes skill loader 讀得到 ZIP 說成 ChatGPT Host 資格。
  2. 三個 SP 目前合規的交付面 = 可攜 ZIP + Hermes skill（已存在）＋ 文件化的 host 介面契約；`C-016..018` 維持 `HOST_PENDING`。
  3. 開 `CR-PLUGIN-SCHEMA-AUTHORITY`（本回合以檔案落地）：要求 Owner 在**官方、非草案**的封裝面出現後再裁決；在那之前任何「3/3 已安裝」都是偽 claim。
- **為何低阻力**：零工程、零法務風險，且不阻塞其他 35 個 Delivery Surface。
- **代價**：`DOC-12 C-016..018` 三條在可預見期間維持未閉合 —— 這是**誠實的成本**，不是遺漏。

---

## 5. 單一 HGK 專項 WO（D-05/06/07/09 合併）

**WO 範圍**（最小可證單元）：
- 目標：修 `_repo_head()`，使 `base_head` 來自 project `target_root`，git 失敗時以 typed error 上拋（不再回空字串）。
- 受權 write-set：`src/hg_kseos/lifecycle.py`、`tests/test_r13_repo_head_cwd.py`。
- 角色：writer = `opencode-go/minimax-m3.1-flash-free`（EXECUTE，rank2 強制）；checker = `openai-codex/gpt-6.1-sol`（VERIFY_SECURITY，rank1）；兩者為**不同 arm、不同行程**。
- 證據：RED（patch 前 2 failed）→ patch → GREEN → 獨立 checker 重跑 → `record_workorder_result` 只在 role-evidence bundle 完整時才可能 PASS。

**為何一個 WO 就同時關閉四項**：
| 缺口 | 這個 WO 怎麼關 |
|---|---|
| D-05 五工具端到端 | 同一 project／同一 spine 內跑完 admission→write→check→record |
| D-06 Commander/Challenge adapter | writer 與 checker 分別由 EXECUTE／VERIFY 車道真實執行；差別是「SP 身份」而非「模型」——本回合誠實標為 `LANE_ONLY`，不偽稱 SP 已接 |
| D-07 檢查者隔離 | 以 §3 的裁決執行：唯讀候選 + 獨立輸出根 |
| D-09 `_repo_head` | 就是 WO 的交付物 |

---

## 6. 執行方案（本回合已執行，逐步可稽核）

| # | 動作 | 證據 |
|---|---|---|
| E1 | 建 project `HGKR13-RED`（target=HGK），從**非 repo CWD** 跑 admission | `stage_red.json`：`ERR_WORKORDER_CRITICAL_FIELD_MISSING` |
| E2 | 建 project `HGKR13-WO`（CWD=HGK），admission 成功 → `WO-TS-WO-01/02`、`base_head=b22706e` | `stage_wo.json` |
| E3 | 把 `HGK-ROLE-BINDING/1` 寫入 TaskSpec `permissions_json`，並取 lease | `binding.json` |
| E4 | 先寫測試（本回合），patch 前跑 → **RED 2 failed** | `RED_test_output.txt` |
| E5 | EXECUTE 車道 bounded writer 套 patch（只准 lifecycle.py） | `EXECUTE_write.json` + `git diff` |
| E6 | patch 後跑測試 → GREEN；VERIFY 車道獨立 checker 唯讀複核 | `GREEN_test_output.txt`、`CHECKER_REPORT.json` |
| E7 | `record_workorder_result(writer≠checker, verdict, evidence_refs, role_evidence)` | spine `workorders.result_json` |
| E8 | 建 `HGKR13-GREEN`：非 repo CWD 下 admission 成功且 `base_head=HGK HEAD` | `stage_green.json` |

**Rollback**：`git -C HG-KSEOS checkout -- src/hg_kseos/lifecycle.py`；WO `rollback_pointer=RB-WO-TS-WO-01`；lease 到期自動失效。

---

## 7. 風險與殘留（不掩蓋）

| 風險 | 處理 |
|---|---|
| HGK repo **無 remote**，patch 只在本機 | 證據（diff＋收據＋測試輸出）複製到 SBL evidence 分支；HGK 端以 `checkpoint` 記錄 |
| 本回合 writer/checker 是**車道**而非 SP 身份 | 明確標 `LANE_ONLY`；D-06 仍 OPEN，不因本次成功而降級宣稱 |
| `validate_role_evidence` 的 bundle 需真實 receipt | 用本次 EXECUTE/VERIFY 的實際 json + log sha 填；若欄位不足則誠實記 `PARTIAL` |
| 測試以 monkeypatch.chdir 模擬 CWD | 另有 E1/E8 兩次**真實** CWD 差異的 project 級證據，不單靠 monkeypatch |

---

## 8. 主張上限

可宣稱：`_repo_head` 缺陷已在原生 admission 路徑上重現並修復，WO 由 HGK spine 建、lease 由 spine 取、結果由 spine 記，writer 與 checker 為不同 arm 的真實車道執行。
**不可**宣稱：SP 身份整合完成（`LANE_ONLY`）、ChatGPT Plugin 已安裝（`HOST_PENDING`）、`SBL_FULL_PRODUCT` 通過（仍 OPEN）、DOC 語義分母已建立（仍 `UNKNOWN`）。

---

## 9. 執行後修正（裁決不變，事實補正）

E6 之後先只跑了新測試就落帳 `WO-TS-WO-01`；**全量掃描**才暴露 5 個 G0 控制測試依賴「無 `target_root` 就繼承 CWD」的舊行為。
這是本裁決在落地時自己造成的回歸，處置如下（不修改裁決本身）：

1. 切第二個 WO `WO-TS-WO-02`，主體限定 `tests/test_g0_wave3_controls.py`；只新增 `_target_repo()` 並傳入 `target_root`，斷言零變動。
2. VERIFY 車道第二次獨立複核，明言「no tests weakened, skipped or deleted」→ PASS → 落帳 VERIFIED（`d53b2238`）。
3. 全量分母：回合前 18F/578P/90 subtests → 兩切片後 **18F/580P/90 subtests**，失敗集合**完全相同**（無新增失敗、+2 通過）。
4. 教訓寫入 skill：**先寫測試不等於先跑分母**；任何 `fail-closed` 收緊都必須在落帳前跑全量，否則「已驗證」只是在窄分母上成立。

因此本裁決的工程結論不變：不建 Permit/ECP 子系統、以既有四元組對映並真的跑通；checker 維持唯讀 + 隔離輸出根；Plugin 停在 `HOST_PENDING`。
