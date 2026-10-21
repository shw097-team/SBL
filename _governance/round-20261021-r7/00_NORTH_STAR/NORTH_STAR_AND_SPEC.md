# SBL R7 — FAR 殘留關閉與候選裁決 (SBL-R7-FAR-RESIDUAL-CLOSURE)

> 回合 ID：`SBL-R7-FAR-RESIDUAL-CLOSURE`
> 控制平面：HG-KSEOS（唯一）；Runtime/Orchestration plane：current canonical Hermes（受治理）
> HGK admission：`REQ-HGK-PRJ-SBL-PIPDLS-R7-FARCLO` (FROZEN) → `TS-req-hgk-prj-sbl-pipdls-r7-farclo` (ADMITTED) → `WO-TS-req-hgk-prj-sbl-pipdls-r7-farclo` (CREATED)
> base_head：`3d06f3da83488219a3dcdf608c937b8c5285810c`
> 產出時刻：2026-10-21T05:24:28.777313+00:00

## 核心大目標
在 R6 已封存的可驗收基礎上，**用 FAR 做一次受治理的最佳工程裁決**，把 R6 殘留集合（TT/CR/open/blocked）與
所有未併入 MAIN 的候選分支，一次性分流成三個可執行 bucket：**本回合執行**、**Owner 一次動作**、**不可關閉**；
然後**只執行第一個 bucket**，用獨立 VERIFY 車道重驗，最後把候選與證據推上 `shw097-team/SBL` 供外部驗收官使用。

## 任務執行 SPEC（與上位 SBL_PIPD-LS-PKG + R6 驗收報告對齊）
1. **模型平面分離**：會話互動模型（MiniMax M3.1 Flash / opencode-go）≠ 車道模型。
   本回合車道 mandate 實測：PLAN=`openai-codex/gpt-6.1-sol`、EXECUTE=`opencode-go/deepseek-v4.1-flash`、
   VERIFY_SECURITY=`openai-codex/gpt-6.1-sol`，三者 nonce=True / exit=0 / usage HTTP 200。
2. **FAR 路由**：`FAR_CAPABILITY_MATRIX.yaml` 的 `RESEARCH_LITERATURE_REPO → NATIVE_WITH_SELECTED_ARIS`；
   run=`FAR-20261021-023-sbl-r7-residual-closure`；challenger=`aris/research-review`。
3. **分桶裁決**：每個殘留項目恰落一個 bucket，零遺漏、零假 PASS。Owner 項目必須寫成「一次動作」。
4. **執行邊界**：只執行不需要 Human/Native gate 的項。PR merge、新 release 發布、Host private plugin、
   Native issuer 簽發 → 一律留給 Owner（使用者預授權的是「FAR 裁決」，不是「繞過人類授權邊界」）。
5. **證據分層**：product candidate SHA 與 evidence SHA 分離；claim ceiling 逐項書寫；不把 scoped PASS 說成全產品結案。

## 任務執行清單（對應 Kanban 卡與 OpenSpec R7_DELTA）
- R7-01 FAR 殘留盤點 + 分桶裁決（Kanban `t_928f8743`）
- R7-02 未併候選分支裁決（SBL + PIPD-LS-SP）（`t_ab996bd9`）
- R7-03 R6-TS06-A 合法執行路徑（`t_81e07da3`）
- R7-04 EXECUTE 車道執行可執行裁定（`t_491b597c`）
- R7-05 VERIFY 車道獨立驗收（`t_ca9a0cc0`）
- R7-06 推送 + 遠端回讀（`t_00b9aa1d`）
- R7-07 自研究/自學習 ledger（`t_b3f3ed5a`）

## 檢測清單（每一項都要有 raw receipt）
| # | 檢測 | 判據 |
|---|---|---|
| C1 | 車道可用性 | 三車道各自 ok=True、nonce=True、usage status=200、transport_model 等於 mandate |
| C2 | HGK admission 鏈 | REQ FROZEN / TS ADMITTED / WO CREATED / base_head 綁定候選 SHA |
| C3 | FAR artifact set | 契約要求的 canonical 檔案齊備且 schema 通過 |
| C4 | 殘留覆蓋率 | residual 分母 == R6 殘留列數；每列恰一個 bucket |
| C5 | 候選分支裁決 | 每條裁決附量測的 git 事實（merge-base / ahead-behind / 衝突） |
| C6 | 獨立驗收 | maker ≠ checker；checker 原文含字面測試摘要；guard CLEAN |
| C7 | 推送 | 遠端 SHA == 本地 HEAD；staged secret scan CLEAN |
| C8 | 候選不越界 | 既有 `v0.1.0-foundation-preview` 資產未被覆寫；無 force push；無 tag |
