# R7 Delta — sbl-v01-candidate-build (SBL-R7-FAR-RESIDUAL-CLOSURE)

> 本 delta 只記錄 R7 回合的**新增**範圍與驗收邊。R1–R5 的既有條目不重寫、不回填。
> 依 OpenSpec 規則：每個 task 必須有可執行的驗證命令與期望產出物。

Governing authority: `SBL_PIPD-LS-PKG_DOC-00..DOC-13`（產品真相）、R6 獨立驗收報告（受影裁決）、
HG-KSEOS SharedSpine（本回合的控制平面與 admission 記錄）。

## 7. R7 — FAR 殘留關閉與候選裁決

- [ ] 7.1 FAR run `FAR-20261021-023-sbl-r7-residual-closure` 依 `FAR_CAPABILITY_MATRIX.yaml` 的
      `RESEARCH_LITERATURE_REPO -> NATIVE_WITH_SELECTED_ARIS` 路由執行，產出 canonical artifact set。
      Verify: `Fabric/fabric-autonomous-research/runs/FAR-20261021-023-sbl-r7-residual-closure/` 存在
      `ResearchRequest.yaml` `ResearchPlan.yaml` `ResearchSynthesis.md` `CandidateResearch.yaml`
      `ResearchHandoff.yaml` `ResearchRunReceipt.json` 與 8 個 ledger。
- [ ] 7.2 每個 R6 殘留項目有裁決列（executed / one-action-owner / not-closable），零遺漏、零假 PASS。
      Verify: `ClaimLedger.tsv` + `OpenQuestionLedger.tsv` 的列數等於 R6 殘留清單列數；
      `CandidateResearch.yaml` 的每個 claim 附來源路徑。
- [ ] 7.3 未併候選分支裁決（SBL + PIPD-LS-SP）每條附量測事實。
      Verify: `SourceSnapshotLedger.tsv` 每列有 merge-base / ahead-behind / diff 檔案數 / 衝突與否。
- [ ] 7.4 R6-TS06-A 執行方案：每步有前置條件、機械成功判據、失敗處置、rollback。
      Verify: `ResearchHandoff.yaml` 的 `execution_plan` 逐步可貼上執行。
- [ ] 7.5 HGK admission 鏈完整（REQ FROZEN → TS ADMITTED → WO CREATED，base_head 綁定候選 SHA）。
      Verify: `HG-KSEOS/var/shared-spine/hg-kseos.db` 的 requirements/taskspecs/workorders 三列回讀一致。
- [ ] 7.6 本回合執行項在獨立 VERIFY 車道取得原始裁決（maker ≠ checker）。
      Verify: `SBL/_governance/round-20261021-r7/40_VERIFY/` 有 checker 原文與 receipt；
      dispatcher receipt 的 `served provider/model` = `openai-codex/gpt-6.1-sol`。
- [ ] 7.7 候選與證據推送 `shw097-team/SBL`，遠端 SHA 回讀一致；分層 claim 不越界。
      Verify: `git ls-remote origin refs/heads/evidence/r7-*` 等於本地 HEAD；
      推送前 staged diff 的 secret scan = CLEAN。
- [ ] 7.8 受治理自研究／自學習／自迭代 ledger。
      Verify: `SBL/_governance/round-20261021-r7/90_EVIDENCE/SELF_RESEARCH_LEDGER.json` 存在，
      每條 lesson 是可遷移規則，且每個殘留項目恰落一個 bucket。

## Active / Deferred / Forbidden（本回合）

- Active：7.1–7.8。
- Deferred（需 Human/Native 一次動作，不在本回合執行）：PR #2 的 merge 授權、新 C3 prerelease 的
  公開發布與 tag 命名、3 個 ChatGPT 私人 Plugin 的 Host create/install、PIPD Native Writer 的簽發。
- Forbidden：force push、覆寫既有 `v0.1.0-foundation-preview` 資產、刪除遠端分支、
  改寫 frozen DOC/Oracle、把本回合的 scoped PASS 描述成全產品結案。
