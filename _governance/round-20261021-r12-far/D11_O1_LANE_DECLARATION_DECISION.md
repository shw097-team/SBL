# D-11 / O-1 裁決記錄 — PLAN 車道宣告面 vs 逐輪 mandate chain（R12 FAR）

**決策 ID**：`DEC-R12-D11-O1-20261023` ｜ **裁決日期**：2026-10-23（UTC+8）
**裁決面**：owner-decision worker `t_47017ac5`（blanket-authorization round，量測→裁決→記錄→續行）
**性質**：candidate-only 決策記錄 — 不自我驗收、不自我升格；獨立 Checker 閘（`t_00d2062c`）另行把關。

## 0. 輸入測量（全部可重算，命令見附錄）

| 事實 | 值 |
|---|---|
| HG-KSEOS HEAD | `1760fb443ab284c52c46a6b49f573e2a180530e6`，`config/` 工作樹乾淨 |
| `config/lane-routing-registry.yaml` | epoch **32**；**89** 個 projection `pointer:` pin |
| `config/model-lane-assignment.json` | revision **32** / registry_epoch 32；sha256 `16fc842a…e54cd512c`（== registry `source_of_routes.sha256`） |
| `config/lane-route-slots.candidate.json`（pool） | rev **20**；PLAN rank1 = `opencode-go/deepseek-v4.1-flash`（`gpt-6.1-sol` 降 rank2/fallback1）；EXECUTE rank1 = `minimax-m3.1-flash-free`；VERIFY rank1 = `deepseek-v4.1-flash` |
| lane suites（`test_lane_policy.py` + `test_lane_scope_isolation.py`，uv CPython 3.12.13、`PYTHONPATH=src`） | **10 passed / 90 subtests passed** |
| SBL 控制包 pin（`tools/check_control_package.py --verify`） | **`CONTROL_PACKAGE_PINNED`：14 docs、17,473,442 bytes、rollup `01b972c80341e1b8`**，exit 0 |

## 1. D-11 前提已被事件取代 → `CLOSED_SUPERSEDED_BY_EVENTS`

FAR 研究（2026-10-21）記錄的 drift 是「epoch 29 PLAN rank1=`minimax` vs mandate PLAN=`gpt`」。自該研究落筆後，**選項 (a) 的 rebind 路徑已在同一天被執行三次**，全部帶 WO 紀律：

| epoch | commit | 內容 |
|---|---|---|
| 30 | `924af95`（WO-TS-REBIND-01） | PLAN rank1→`gpt-6.1-sol`、EXECUTE→`minimax`；**87 個 projection binding 重新對帳** |
| 31 | `bb67397` | 修「what a green suite hid」：projection 落後一個群組、drift 基線被改去描述錯誤狀態；全部平面改由單一宣告推導 |
| 32 | `c3727d4` | 依 2026-10-22 GPT 配額令 PLAN→`deepseek-v4.1-flash`；`SOD006-C6` 以 `OPEN_OWNER_ORDERED` 登記（不隱藏）；pool PLAN DEFAULT→deepseek |

今日實測：宣告面（registry routes + pool ordered_pool + assignment[]）與**現行** owner 令一致 ⇒ D-11 原始 DEBT（宣告面互斥）已不存在。

## 2. O-1 裁決：拒絕二選一 — 「rebind-on-order 為常態 + mandate chain 為每輪斷言層」

(a) 與 (b) 不是互斥選項；實務上兩者已同時在役，本裁決將其定為常態規則：

1. **binding 變更走 rebind，宣告面必須追上**：任何改變車道預設 arm 的 owner order，由 HGK issuer 以 WO 落成 registry rebind —— epoch、assignment revision、pool、**全部** projection pin **與敘述欄位**一起前進；round 的 dispatch 在 rebind commit 之前不得把該 binding 當作宣告事實引用。
   結構證據：epoch 32 守衛已要求「session-tier PLAN 只有在宣告存在**且指名同一模型**時才放行 —— 未宣告的移動保持 red」（`c3727d4`）。
2. **mandate chain 是斷言／證據層，不是宣告面的替代品**：每次 governed dispatch 仍以 `--force-rank` + `--require-arm` 留下 `required_arm == served_arm` 收據（R11/R12 三車道探針實證：usage 200、nonce 對帳）。它只作為「owner 令落地與 rebind commit 之間」的輪內橋樑；**round 結束時宣告≠mandate 未關閉 ＝ 缺陷，不是常態**（FAR 研究列的「drift 永久存在、每輪人工覆蓋」後果被本條明文拒絕）。
3. **FAR 研究 O-1 的「(b) 先做」建議 → `SUPERSEDED`**：rebind 已先行（epoch 30–33 三次，見 §1）。

## 3. 新殘餘 D-11b：敘述面殘留 drift（issuer 簽發關閉，本 round 不代改）

routing face 已對齊，但 `model-lane-assignment.json` rev 32 的 **sod 敘述散文**仍描述 R14（PLAN=gpt）世界，且被 projection `expected` pin 釘死 —— drift gate 對著**自我矛盾的宣告面**保持 green，正是 `bb67397` 命名過的「green suite hid」失效模式第二次現形。逐字殘留：

| 欄位 | 現值（殘留） | 與之矛盾的同檔／同庫事實 |
|---|---|---|
| `sod.plan_lane` | "openai-codex / gpt-6.1-sol … owner mandate 2026-10-22 (R14)…" | `/assignment/0` = `opencode-go/deepseek-v4.1-flash` |
| `sod.verify_vs_plan_model_separation` | "PRESENT: PLAN openai-codex/gpt-6.1-sol differs from VERIFY_SECURITY …" | PLAN＝VERIFY＝`deepseek-v4.1-flash`（registry `SOD006-C6` OPEN_OWNER_ORDERED） |
| `sod.provider_separation` | "PLAN uses openai-codex; …" | PLAN provider = `opencode-go` |
| `sod.provider_separation_status` | "…PRESENT between PLAN and VERIFY_SECURITY. All three default models differ." | PLAN 與 VERIFY 同一 canonical identity |
| `sod.lane_deviation_recorded` | "…both declared maker/checker pairs now require distinct models." | registry `sod_invariants.pairs[PLAN,VERIFY].distinct_required = false` |

另兩處 registry 叙述標籤同病：top-level `authorization_basis`（epoch 32 仍寫 "PLAN openai-codex/gpt-6.1-sol…"）與 PLAN route `selection_authority: owner-order-20261022-r14-plan-gpt61sol-execute-minimax`（該 order 已被同日配額令取代）。

- **關閉路徑（S）**：一個 issuer rebind commit **同步**改「散文＋其 projection `expected` pin」兩側（只改一侧會把 gate 打紅）；seal 最後釘。**Owner**：HGK issuer。
- **本 round 不代改**：registry 是 issuer 文件；agent 自改宣告面正是本研究要防的越權。
- **在此之前的 claim ceiling**：可宣稱「宣告面 routing 軸已與 owner 令對齊（實測）」；**不可**引用 rev 32 的 `sod.*` 敘述散文作為現狀 —— 它是 stale。

## 4. 主張上限與邊界

- 本記錄是 owner-decision 候選記錄，**不是**驗收；不宣稱任何 independent-checker acceptance 或外部接受。
- SBL 產品樹零接觸（`contracts/`、`sbl_core/`、`tests/` 未動）；控制包 pin 實測未回歸（§0）。
- `SOD006-C6` 維持 `OPEN_OWNER_ORDERED`：PLAN 與 VERIFY 同模型，僅存 process／lane／evidence-path 分離 + no-self-acceptance；**不**宣稱模型多樣性。

## 附錄：重算命令

```
git -C C:/Projects/Agent_Workspace/HG-KSEOS rev-parse HEAD        # 1760fb443ab2…
git -C C:/Projects/Agent_Workspace/HG-KSEOS status --porcelain config/   # (clean)
grep -c "pointer:" …/HG-KSEOS/config/lane-routing-registry.yaml   # 89
cd …/HG-KSEOS && PYTHONPATH=src uv run --python 3.12 --with pytest --with pyyaml \
  python -m pytest tests/test_lane_policy.py tests/test_lane_scope_isolation.py -q
  # 10 passed, 90 subtests passed
cd C:/Projects/Agent_Workspace/_r12_docs && uv run --python 3.12 \
  python tools/check_control_package.py --verify
  # CONTROL_PACKAGE_PINNED: 14 docs, 17473442 bytes, rollup 01b972c80341e1b8
```
