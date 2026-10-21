# FAR 裁決 R14-2 — 未開始／阻斷項、待 Owner 決策項、以及 M1 前置的下一合法步驟

**裁決者**：FAR · **執行者**：Hermes（受治理 Runtime 面）· **控制平面**：HG-KSEOS · **日期**：2026-10-22
**法位**：`SBL_PIPD-LS-PKG` DOC-00..13（產品規範）＋ HGK `AGENTS.md`/Shared Spine（唯一 issuer）＋ Fabric（治理政策）

---

## 0. 模型方案可辯（先驗，硬指令）

fresh probe 三次：`PLAN → openai-codex/gpt-6.1-sol`（rank2 強制）、`EXECUTE → opencode-go/minimax-m3.1-flash-free`（rank2 強制）、`VERIFY_SECURITY → openai-codex/gpt-6.1-sol`（rank1），三條 `ok=true` 且 brief 內含 typed nonce。**不需暫停。**

---

## 1. 主裁決：12 車道紅的根因不是 12 個缺陷，是**一個過期的 Owner mandate**

**實測**（本回合，非引用）：

| 事實 | 證據 |
|---|---|
| `config/model-lane-assignment.json` 仍是 **revision 29**，`declared_by` 逐字寫著 R11 期 mandate：PLAN=minimax、EXECUTE=deepseek，並明言「SUPERSEDES the earlier order (PLAN gpt-6.1-sol, EXECUTE minimax)」 | `raw/assignment.before.json` |
| `config/lane-routing-registry.yaml` 三條 route 的 rank1 與 arms 都照 rev.29 排（PLAN primary=minimax；EXECUTE primary=deepseek） | `raw/registry.before.yaml` |
| 現行命令（R12–R14）mandate 恰好相反：PLAN=gpt-6.1-sol、EXECUTE=minimax | 本地命令書原文 |
| 車道測試（`test_lane_policy` owner_chain）編碼的是**現行** mandate → 因此紅 | `tests/test_lane_policy.py:114-121` |

**推論**：R11–R14 每輪都得 `--force-rank`，不是因為車道壞了，而是**registry 停在舊 mandate**；測試與 registry 分屬兩個 mandate 世代。

### 裁決 A1：修 registry，但不是「改一行」

本回合先做了**最小局部編輯**（只動 route header 與 `arms[]`），結果：
- 目標測試沒有轉綠（測試讀的是 `route["fallbacks"]`，不是我改的 `arms`）；
- 並且**新增一個失敗** `test_lane_policy::test_drift_injection_subcases`（drift checker 判定 fatal，因為 `fallbacks` 與 pool/projection 不再連續）。

**已立即回退**（`raw/registry.before.yaml`、`raw/assignment.before.json` 原樣還原；回退後子集 13 紅與回合前**逐項相同**，`raw/after_revert_failed.txt`）。

**裁決**：rebind 是**一等政策變更**，必須一次移動四組東西才不會被判 fatal drift：
1. 每條 route 的 rank1 `provider/model` 與 `fallbacks` 鏈；
2. `arms[]`（pool 側表示）；
3. 每個 `projections[].bindings` 指向的檔案（`config/hermes.json`、pool、啟動腳本…）；
4. `model-lane-assignment.json` 的 revision 與 `declared_by`。
**這是 HGK-owner scoped WO 的工作**（另建 `WO-TS-REBIND-01` 已取 lease 與 binding，尚未施工）。低阻力替代：以 `--force-rank` 續用（現行做法）並把 mandate 世代差寫成 TT，而非局部改檔。

---

## 2. TS03 裁決：原生四元組已能承載 ONE ECP，但有**兩個精確缺口**

以 10 條性質對 live spine 實測：**8 SATISFIED / 2 GAP**（`raw/ts03_probe_matrix.json`）。

| 性質 | 結果 | 證據 |
|---|---|---|
| issuer identity | SATISFIED | writer=`codex`, checker=`openai-codex/gpt-6.1-sol` |
| ONE ECP 單一性 | SATISFIED | 無任何 project 有兩個 `-PLAN` requirement |
| before/after receipt | SATISFIED | `base_head=b22706e…` ＋ artifact digest |
| rollback pointer | SATISFIED | `RB-WO-TS-WO-01` |
| **scope 路徑強制** | **GAP** | `validate_binding` 接受「subject 不在 scope 內」的 binding → scope 只是宣告 |
| expiry | SATISFIED | `ERR_ROLE_BINDING_EXPIRED` |
| 防重放 | SATISFIED | `ERR_WORKORDER_RESULT_STATE` |
| maker≠checker | SATISFIED | `ERR_WORKORDER_SELF_REVIEW` |
| lease 互斥 | SATISFIED | `ERR_DUAL_WRITER:…:holder-a` |
| **撤銷語義** | **GAP** | `release_lease` 回 `None`；已落帳 verdict 不受影響，撤銷與裁決之間沒有連結 |

**裁決 A2（最小原生升級，不另造子系統）**：
- GAP-1：`validate_binding` 增一行斷言——`subject` 必須落在 `scope` 內，否則 `ERR_ROLE_BINDING_SUBJECT_OUT_OF_SCOPE`。
- GAP-2：`release_lease` 回 typed receipt 並寫 `revoked_at`；同時明定**撤銷只能前向**（不得回溯改寫已落帳裁決），並新增一條：被撤銷 permit 的 WO 不得作為**新**受理的證據。
- 兩者皆為 HGK 本體改動 → 需 HGK-owner scoped WO（與 A1 合併成同一個 WO 家族，避免碎片化）。

---

## 3. TS04 裁決：動態 checker 在車道沙箱內**不可行**，這是車道設計缺口，不是流程問題

**實測三次**：

| 嘗試 | 結果 |
|---|---|
| checker 以 `workspace-write` 在隔離副本跑 pytest | `ERR_SANDBOX_ESCALATION_REFUSED`（需 `--allow-sandbox-escalation`） |
| 加上升權旗標 | `ERR_GUARD_REQUIRED_FOR_ESCALATED_CHECKER`（無 `--guard-subject` 的升權一律拒） |
| 加 guard-subject 後執行 | `ok=true`、served `openai-codex/gpt-6.1-sol`，但 pytest 在收集前 **`PermissionError` 讀 `sniffio/__init__.py`** → `exit=1`、0 tests |
| 同一指令**在車道外**（人工）於同一副本 | **9 passed**（R13 兩測試＋7 個 G0） |

**推論**：lane sandbox 讀不到 workspace 外的共用 venv；而 checker 又不能自己帶 runtime。於是「獨立 principal 在隔離副本動態實跑」在現行車道**結構上做不到**。
**裁決 A3（低阻力優先序）**：
1. **首選**：checker 輸出根內置**自帶 runtime**（把 venv 複製進 checker root，或 `venv --system-site-packages` 建在 root 內），lane 一律 `read-only`＋`--guard-subject`；不給寫入權，測試在**副本**內跑。
2. 次選：dispatcher 開放「interpreter 根 allowlist」參數（需 HGK-owner 改 dispatcher）。
3. **不接受**：由 maker 自己跑測試再自稱動態驗收（本回合人工 9 passed 只能作**harness 證據**，不得當獨立 checker 的 PASS）。

---

## 4. TS06/07 裁決：SP 介面可以薄，但 invocation id 必須綁在同一 TaskSpec/WO 上

裁決：以薄 adapter 發出 `commander_invocation_id` / `challenge_invocation_id`，內容至少 `{sp_id, sp_version, input_digest, output_digest, subject, workorder_id, lane, served_arm}`，並寫入 spine 證據；SP **不得**自簽 permit（簽發仍是 HGK）。在 adapter 未落地前，維持 `LANE_ONLY`，不得因 WO VERIFIED 升格。

---

## 5. 執行方案與本回合結果

| # | 動作 | 結果 |
|---|---|---|
| E1 | 三車道 fresh probe | 全部 served==required（`raw/lane2_*.json`） |
| E2 | 建 project `HGKR14-REBIND` + WO `WO-TS-REBIND-01`，寫入 binding 與 lease | `raw/rebind_receipt.json` |
| E3 | 局部 rebind → 觀測到 1 新增 fatal → **回退** | `raw/after_rebind_failed.txt` vs `raw/after_revert_failed.txt`（回退後與回合前逐項相同） |
| E4 | TS03 十條性質實測 | 8 SATISFIED / 2 GAP（`raw/ts03_probe_matrix.json`） |
| E5 | TS04 動態 checker 三次嘗試（含兩個 typed 拒絕） | `raw/checker_escalation_refusal.json`、`raw/checker_dynamic.json`、`raw/checker_dynamic2.json` |
| E6 | 隔離副本人工基準（harness 證據，非 checker PASS） | 9 passed |

---

## 6. 主張上限

可宣稱：車道三條可用且 arm 一致；12 車道紅的根因已定位為 mandate 世代差並有反證（局部修會製造 fatal drift）；原生四元組 10 條性質已逐條實測 8 過 2 缺；車道沙箱對動態 checker 的限制有三次 typed 證據。
**不可**宣稱：HGK 全綠、SP 已呼叫、動態獨立 checker 已成立、registry 已 rebind、語義分母已定、`SBL_FULL_PRODUCT` 通過。
