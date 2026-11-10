---
board_id: FHS-W0-R26-POSTREPAIR-20261110
created: 2026-11-10T23:50+08:00
goal: 完成《FHS_W0_r26_External_Challenge_PostRepair_Acceptance_Report_2026-11-09》全部項目並解決其提出的全部問題
mode: MULTI-AGENT / KANBAN / SWARM / GSTACK / OPENSPEC
subject_sha256: 0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f
---

# KANBAN — FHS W0 r26 post-repair round

> 本板是**協調狀態**（coordination），不是權威（authority）。權威仍是各原域 WorkOrder / 簽章收據 / Gate。
> 每一張卡只有在「本輪真實執行的命令 + exit code + raw log」存在時才可移到 DONE。

## 0. 追蹤面說明（誠實條款）

- `todo_list` 工具：本輪實際呼叫（見 session turn）。
- `/goal` slash command：本 build **無法由 agent 呼叫**（`tool_search` 對 "goal" 無命中），故本輪把 goal 逐字寫在 `GOAL.md` 並鎖為 `todo_list` 第 1 項；**不宣稱 `/goal` 已執行**。
- `KANBAN` 工具：本 build 無 kanban tool；以本檔 + `evidence/` 為持久板面，重啟後可續。

## 1. 車道與模型（lane plane ≠ session plane）

| lane | required（owner 指定） | selected | invoked | actual_served |
|---|---|---|---|---|
| Commander & PLAN | `openai-codex/gpt-6.1-sol` (medium, OpenAI OAuth) | pending | pending | pending |
| EXECUTE（Codex bounded writer） | `opencode-go/deepseek-v4.1-flash` | 由 SWARM 子代理實作 | pending | pending |
| VERIFY / SECURITY / Acceptance Challenge | `openai-codex/gpt-6.1-sol`（Codex CLI checker） | pending | pending | pending |

**會話 plane**：本 GUI session 的 pin 是 `deepseek-v4.1-flash`（EXECUTE arm），它**不是** PLAN 或 VERIFY 的車道綁定。任何 PLAN/VERIFY 宣稱都必須另有車道收據，否則記 `NOT_DISPATCHED`。

## 2. 卡片

| # | 卡 | finding / predicate | 車道 | 狀態 |
|---|---|---|---|---|
| K01 | G29 票証嚴格化 + 3 新負例 + CI | EC-R26-003 / R26-01 | L1 sbl-quorum | **DONE**（128/128 掃描 0 findings） |
| K02 | FHS-3L&M 綁定：去硬編碼/數值 epoch/per-run 原子檔/雙 SHA/退役/TTL | EC-R26-002 / R26-04 | L2 sbl-3lm | **DONE**（E00–E11 全跑） |
| K03 | L1 bytes/lines、76 properties、EVIDENCE_SCOPE、G24 typed check | EC-R26-004/009/011 / R26-02 | L3 sbl-meta | **DONE**（G24 負例由 Commander 反證） |
| K04 | 七份 owner 簽章 Ed25519 真驗 + preauth 時區 finding | EC-R26-008 / R26-06 | L3 sbl-meta | **DONE（驗章）／HOLD_OWNER（時區重簽）** |
| K05 | HGK H0 DAG 鑑識 + H1 config 差額台帳 + H2 main 衍生橋接 | EC-R26-005/006 / R26-07/08 | L4 hgk-bridge | **DONE**（DISJOINT；PR #16 draft） |
| K06 | 機械硬入口：pre-dispatch guard + token + fresh-PID bypass NEG | EC-R26-001 / R26-03 | L5 hgk-hook | **DONE_WITH_DEBT**（122 個既有測試待遷移） |
| K07 | Fabric r26 mirror 政策准入 + manifest + 消費軌跡 + 2 負例 | EC-R26-013 / R26-09 | L6 fabric-mirror | **DONE**（PR #54） |
| K08 | r27 append-only 候選 + 七份藍圖差額 + claim ceiling | EC-R26-010/012 / R26-10 | L7 sbl-docs | **DONE**（prefix 逐位元相同） |
| K09 | ActualServed 實測（relay/codex 車道） | EC-R26-007 / R26-05 | Commander | **PARTIAL**（3 served / 5 pre-spawn refused） |
| K10 | 整合驗收（獨立 process/evidence path 重跑） | R26-11 | VERIFY | **PARTIAL**（14/14 重跑；長回合車道無收據） |
| K11 | 發佈：SBL / HGK / Fabric 三庫 branch + PR | — | Commander | **DONE**（#66 / #16 draft / #54） |
| K12 | 最終報告 + 證據索引 | all | Commander | **DONE** |

## 3. Done 的定義

一張卡能移到 DONE 的條件，全部都要成立：
1. 變更存在於具名 branch（非 main）。
2. 至少一個**負例**由本輪執行產生具名拒絕碼 + 非零 exit。
3. 該卡宣稱的每個數字，都能用檔案內的路徑 + sha256 重算。
4. 沒有改動已簽收據、沒有改動 r26 凍結文件、沒有改動其它車道的檔案。

## 4. 明確不在本輪範圍

- 不發行（RELEASE）、不做 Native 全域安裝、不改 GitHub default branch、不合併 main。
- 不重簽任何既有簽章；owner 需重簽者記 `HOLD_OWNER_WINDOW`。
- 不重跑 31 冊原始 Windows round。
