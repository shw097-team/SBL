# 自研究 / 自學習 / 自迭代 / 自進化（受 FABRIC & HGK 治理）

```yaml
schema: SBL_EVOLUTION_RECORD/1
subject: SBL-R15.2-CONTINUATION-20261022
round: round-20261022-r15_2
claim_ceiling: LOCAL_MEASURED; every lesson below cites the raw that produced it
```

本輪對自己的四個錯誤做了實測糾正。每一條都是「先量測、再改行為」，不是自我表揚。

## E1 — 自研究：把「探測」誤當成「執行」

- 症狀：對 relay 發出 `Reply with the single word OK` 並拿到 200，就宣稱「模型方案在傳輸層通過」。
- 量測：真正的 PLAN 任務一餵進去，模型的輸出量從 1 token 級跳到 4,858 completion tokens，並回傳 35 條 DAG 邊。
- 學到：**transport 200 只證明端點活著**；要證明 lane 可用，必須有 served model 回顯 + 實質輸出 + nonce。
- 固化：`hgk-codex-lane-recipe` 技能「Proof to require」章節。

## E2 — 自學習：宣告 blocker 前必須先搜成功配方

- 症狀：worker 用 `--ignore-user-config` + `-s read-only` 啟動 codex，全數 `CreateProcess` 被 policy 擋，我據此宣告 HARD BLOCKER 並停工。
- 量測：改回既有車道配方（複製 sealed `CODEX_HOME` + layered `-p` + `-s danger-full-access`）後，同一 binary 在 391ms 內跑出 `pwsh -Command echo`，三臂全通。
- 學到：**單一 worker 的失敗不是環境真相**；HG-KSEOS 的 `tools/lane_preflight.sh`、`run_codex_adapter.sh`、`run_iao_deepseek.sh` 的註解裡早就寫明這兩個坑（read-only 會擋 spawn、不要自製 config）。
- 固化：技能優先於重造；memory 記錄「宣告不可用前先搜成功配方」。

## E3 — 自迭代：從「自己呼叫模型」升級到「走官方車道」

- 症狀：PLAN/VERIFY 先用 `curl` 直打 relay，得到結果但沒有 lane 綁定、沒有 nonce、沒有 pool 依據。
- 量測：改用 `hgk-lane-dispatch.py` 後，`--require-arm gpt-6.1-sol` 直接被拒（`ERR_LANE_REQUIRED_ARM_ABSENT`），必須用 `openai-codex/gpt-6.1-sol`；缺 nonce 時即使 exit 0 也 `ok=False`。
- 學到：**lane 平面的正確性由 dispatcher 的拒絕能力證明**；能拒絕，才證明它真的在選模型。
- 固化：`LANE_DISPATCH_RECEIPTS.md` 記錄兩次真實拒絕。

## E4 — 自進化：把「有 full access 的 writer」關進籠子

本輪最嚴重的事故是 CWD 逃逸：第一次 EXECUTE 派工沒給 `--cwd`，writer 就把檔案寫進 **HG-KSEOS 受治理 repo**，隨後 300s timeout，形成「有效果、無有效收據」的最壞形狀。

- 圍堵：捕獲位元組 → 移除未追蹤 `workers/` → 驗證 `git status` 空、HEAD 未變（`1760fb4`）。
- 修正：重派時釘 `--cwd <round>`，同一 lane 20.9s 完成且 `ok=True`。
- 結構性提案（`TT-R15.2-HGK-EXECUTE-CWD-ESCAPE`）：`--cwd` 應改為必填，缺省即拒絕；每個 dispatch 前後都要斷言所有受治理 repo 的 `git status --porcelain` 不變。
- 學到：**danger-full-access 可以接受，但只有配上雙向 sha 守衛與 cwd 釘死才可接受**。

## 沉澱物（可被下一個 session 直接複用）

| 資產 | 位置 | 用途 |
|---|---|---|
| `capc-contract-authoring` 技能 | Hermes skills | 讓 CONTRACT.json 一次過官方四命令（含 9 條非顯然 invariant）|
| `hgk-codex-lane-recipe` 技能 | Hermes skills | Codex 載體的正確配方與 6 個坑 |
| `tools/source_freeze.py` / `build_contract_v2.py` | 本 round | 由真測哈希生成契約，可重跑 |
| `workers/*/RECEIPT.json` | 本 round | 7 個 worker 的 typed 收據 |
| `TT_R15_2_REGISTER.json` | 本 round | 13 項阻斷，每項帶 FAR 建議 |

## 未完成的自進化（誠實列出）

- `SOD006-C6` 未解：checker 與 maker 仍同機同 session，lane-level PASS 不能升格為 AO PASS。
- 官方 `openspec` 在既有 change 上失敗，本輪只做了 scoping 建議，未修那個 change。
- gstack 仍不存在，只出 NoFit。
- front door 仍未改成宣告驅動，本輪以「直連 relay + 明示 TT」繞行。

以上四項不影響本輪證據的可信度，但會限制下一個 round 能達到的上限。
