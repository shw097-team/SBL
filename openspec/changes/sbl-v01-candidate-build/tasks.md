# Tasks — sbl-v01-candidate-build

Status vocabulary: `[x]` = done with a raw receipt in this round · `[~]` = partially done (scope stated) ·
`[ ]` = not done (blocker or pending named). A bare `[ ]` with no note is a defect.

Round R2 note: the original text named helper scripts (`tools/source_ledger.py`,
`tools/knowledge_probe.py`, `tests/test_core_registry.py`, `test_spec_flow.py`, ...) that were never built; the
commands below are the ones that actually exist and ran. The rename is disclosed, not back-filled silently.

## 1. Source freeze and knowledge base

- [x] 1.1 Byte-level source freeze over 306 corpus files with the two >MAX_PATH originals mirrored short.
      Verify: `python tools/verify_source.py --verify` → `{"ok": true, "docs": 14, "mismatches": []}` (exit 0).
- [~] 1.2 G-KNOW retrieval: the index/query surface exists and refuses unanswerable queries
      (`python -m pytest tests/test_gknow.py -q` → 6 passed). NOT done: an index built over the real
      DOC-00..DOC-13 corpus as a published artefact — the positive/negative probes run on fixture corpora.
- [x] 1.3 C0..C9 contract compiled by the canonical compiler: `lint`/`activation`/`acceptance`/`compile`
      all exit 0 (`PROMPT_COMPILE_PASS`); receipt `contracts/compiled/compiler-receipt.json`.

## 2. Shared Core and modules

- [x] 2.1 `sbl_core` package with typed DTOs, one error model and the six modules wired through `SharedCore`.
      Verify: `python -m pytest tests/test_core_modules.py -q` → 32 passed.
- [x] 2.2 `SBLM01` goal intake + `SBLM02` guided specification (unlocated clause refused). Covered inside 2.1's suite.
- [x] 2.3 `SBLM03` governed routing + `SBLM04` bridge with a bounded write-set and stale-HEAD refusal.
      Covered inside 2.1's suite and `tests/e2e/test_gj02_patch.py`.
- [x] 2.4 `SBLM05` evidence verification + `SBLM06` bounded repair. Covered inside 2.1's suite.

## 3. SP separation and modes

- [x] 3.1 Three SP manifests with permission sets; the challenge SP cannot mutate product state and a maker
      cannot sign its own challenge. Verify: `python -m pytest tests/test_sp_isolation.py -q` → 8 passed.
- [x] 3.2 Mode gate: `PREW3_SHADOW` is `NO_EFFECT` for every effect; `SWOF_CONNECTED` refuses without a native ACK.
      Verify: `python -m pytest tests/test_modes.py -q` → 10 passed (39-gate matrix asserted).

## 4. Golden journeys

- [x] 4.1 `GJ01` `sbl-todo`: init/add/list/restart/uninstall with typed refusals.
      Verify: `python -m pytest tests/e2e/test_gj01_cli.py -q` → 7 passed.
- [x] 4.2 `GJ02` brownfield scoped patch: bind → red → green → out-of-writeset refusal → stale-HEAD refusal →
      rollback to the baseline digest. Verify: `python -m pytest tests/e2e/test_gj02_patch.py -q` → 7 passed.
- [x] 4.3 `GJ03` skill host bridge: discover → effective load → trigger/non-trigger → provider-off refusal →
      unload with no residue. Verify: `python -m pytest tests/test_gj03_bridge.py -q` → 7 passed.

## 5. Evidence, publication and independent acceptance

- [x] 5.1 Evidence pack: per-gate raw receipts (`evidence/gates/GATES_RAW.json`), scrubbed secret scan
      (`evidence/security/SECRET_SCAN.json`, verdict CLEAN), manifest (`evidence/EVIDENCE_MANIFEST.json`).
      NOT done: SBOM and licence — the licence is an open owner decision (`TX-LICENSE-OWNER-RULING`).
- [x] 5.2 Public repo `shw097-team/SBL` exists (`private: false`), candidate branch and evidence commit pushed,
      exact remote SHAs read back in `_governance/round-20261020-r2/30_PUBLICATION_READBACK.json`.
- [ ] 5.3 VERIFY/SECURITY lane (`openai-codex/gpt-6.1-sol`, read-only) against the frozen candidate with
      `required_arm == served_arm` and a raw verdict: dispatched after the candidate SHA was frozen; the verdict
      and its admissibility are recorded in the round evidence MD. Until an independent checker's raw receipt
      exists, the claim stays `LOCAL`, never `INDEPENDENT_CASE_PASS`.

## 6. Closure

- [ ] 6.1 Single evidence MD (claim ceiling / binding / gates / nonclaims / STOP) frozen last —
      `_governance/round-20261020-r2/40_EVIDENCE.md`; it is written after the last lane exits.
- [x] 6.2 TT/CR register updated (`_governance/round-20261020-r2/00_ROUND_STATE.md` §5) and a resume checkpoint
      written (`_governance/round-20261020-r2/20_RESUME_CHECKPOINT.json`).


## 7. R7 — FAR residual closure and candidate ruling (SBL-R7-FAR-RESIDUAL-CLOSURE)

> 本節依 `R7_DELTA.md` 執行。勾選只依實際收據，不依敘述。

- [x] 7.1 FAR run `FAR-20261021-023-sbl-r7-residual-closure`（route `NATIVE_WITH_SELECTED_ARIS`，
      challenger `aris/research-review`，challenge + experiment trigger 皆啟用）。
      Verify: `Fabric/fabric-autonomous-research/runs/FAR-20261021-023-sbl-r7-residual-closure/`
      存在 `ResearchRequest.yaml` `ResearchPlan.yaml` `ResearchSynthesis.md` `CandidateResearch.yaml`
      `ResearchHandoff.yaml` `ResearchRunReceipt.json` `VERDICT.json` `LEARNING.md` `METHOD.md`
      `SELF_EVOLUTION_DELTA.json` 與 10 個 ledger（Claim/Query/SourceSnapshot/SourceDisposition/
      Hypothesis/OpenQuestion/Contradiction/Disagreement/RejectedAlternative/FitGap + ExtractionLedger.jsonl）。
- [x] 7.2 殘留分桶：16 項，每項恰落一個 bucket，零遺漏零假 PASS。
      Verify: `_governance/round-20261021-r7/30_RESIDUAL/RESIDUAL_INVENTORY.json`
      （5 executable / 4 one-action-owner / 5 not-closable / 1 closed-by-lane-owner / 1 closed-by-isolation）。
- [x] 7.3 候選分支裁決，每條附量測事實。
      Verify: `.../20_FAR/far-20261021-023/raw_worker_artifacts/CANDIDATE_BRANCH_RULING.md`
      49 列（MERGE_NOW 1 / SUPERSEDED 26 / EVIDENCE_ONLY 16 / NOT_RECOMMENDED 3 / DO_NOT_MERGE 3），
      原始量測 `raw_worker_artifacts/audit.json`。
- [x] 7.4 R6-TS06-A 執行方案：9 步，每步有 gate、失敗處置、rollback，含紅線與 6 項 owner 決策建議。
      Verify: `.../20_FAR/far-20261021-023/ResearchHandoff.yaml`。
- [x] 7.5 HGK admission 鏈完整並回讀。
      Verify: `HG-KSEOS/var/shared-spine/hg-kseos.db` 的
      `REQ-HGK-PRJ-SBL-PIPDLS-R7-FARCLO`=FROZEN、`TS-req-hgk-prj-sbl-pipdls-r7-farclo`=ADMITTED、
      `WO-TS-req-hgk-prj-sbl-pipdls-r7-farclo`=CREATED（base_head `3d06f3d…`）。
      NOTE: 記錄一個控制平面缺陷 —— `admit_requirement` 回傳 workorder id 但 spine 內 TaskSpec 仍為
      DRAFT 且無 WorkOrder（`_repo_head()` 取呼叫端 CWD，repo 外回空字串，InvariantViolation 被 except 吞掉）；
      本回合以公開的 `create_workorder` API 補齊並三列回讀。
- [ ] 7.6 獨立 VERIFY 車道對凍結後候選的原始裁決（maker ≠ checker）。
      ROUND 1（arm `openai-codex/gpt-6.1-sol`，nonce `R7CHK-NC-20261021-A1`）：已執行 392 秒，
      產生 byte-exact 證據（`stdout_sha256=80397dbb…`、`usage_status=200`、`nonce_present=true`），
      但在給出裁決前 provider 配額耗盡 → dispatcher 記為 `ERR_NO_ARM_EMITTED_NONCE`（ok=false）。
      分類為 `INCOMPLETE_ROUND_PROVIDER_QUOTA`：**保留、不計為驗收、不上浮為 FAIL，也不當 PASS**。
      收據：`40_VERIFY/checker_round1_receipt.json` + `40_VERIFY/checker_round1_receipt/`。
      ROUND 1 提出的兩項實質發現已在候選 `59d2138` 修復並重測（202 passed / 2 skipped）：
        F8 測試只斷言原始碼文字 → 2/3 的合約破壞變異仍全過（已改為行為斷言 + mutation probe）
        F9 建置依賴 ambient interpreter 的 `build` 套件 → 已加入 `_builder_python()` 解析器
      ROUND 2：arm 依回合中 owner 指示改為 `opencode-go/minimax-m3.1-flash-free`
      （nonce `R7CHK-NC-20261021-A2`，guard-subject 覆蓋候選 worktree），執行中。
- [x] 7.7 候選與證據推送 `shw097-team/SBL`，遠端 SHA 回讀一致；staged diff secret scan CLEAN。
      Verify: `origin/candidate/r7-20261021-repro-build` = `59d2138750223b325159fab536f218a0d9aa4ab5`，
      `origin/evidence/r7-20261021-c7` = `60f344631c4e299115bb016f22452ed3e268280a`（`git ls-remote` 回讀）。
      FAR 產物另推送 `shw097-team/Fabric`：`origin/pub/far-lane-remediation-20261021` = `8fdb9f39124fdd47812a61dd54646a170549307b`。
- [x] 7.8 受治理自研究／自學習／自迭代 ledger。
      Verify: `_governance/round-20261021-r7/90_EVIDENCE/SELF_RESEARCH_LEDGER.json`（9 條可遷移規則，
      每條附產生它的失敗與量測）；FAR `SELF_EVOLUTION_DELTA.json`（7 條，本回合全部採納）。

### 7.x 本回合實際關閉的產品項

- [x] 7.9 `TT-R6-WHEEL-NONREPRODUCIBLE-001` CLOSED（產品變更，獨立分支）。
      根因：Windows checkout 因 `core.autocrlf=true` 且無 `.gitattributes` 把已交付文字改成 CRLF
      （git objects 本身為 LF），加上 archive 記錄 mtime。
      修復：`.gitattributes` 固定 LF；`tools/build_reproducible.py` 以 `git -c core.autocrlf=false archive`
      匯出指定 commit、釘住 `SOURCE_DATE_EPOCH`、並重新打包 sdist（固定 mtime、uid/gid 0、gzip mtime=0）。
      量測：兩次獨立建置得到**完全相同**的 wheel sha256 `a161162fa4173460ad9041a9bc83afc31a52b6fc0539f4655f74de3b1147ecf6`
      與 sdist sha256 `b147f674ffb2356123b63b6e95d6ad572a91f7364db56e859e562495fdd4a927`；
      測試分母 194 → 200（`200 passed, 2 skipped`），分支 `candidate/r7-20261021-repro-build` @ `00cf15f`。
- [x] 7.9 回合中 owner 指示：PLAN 與 VERIFY/SECURITY 車道模型改為 `minimax-m3.1-flash-free`（opencode-go）。
      套用於 canonical dispatch-time pool（`HG-KSEOS/config/lane-route-slots.candidate.json` revision 11，
      commit `3f81b4b7d32da0f9eaae01c7ecd05728206f33d9`），並在 **canonical pool 上實測**兩條車道：
      served_arm == required_arm、nonce_present=true、usage HTTP 200、exit=0。
      `openai-codex/gpt-6.1-sol` 降為 rank-2 fallback（**未移除**，無人值守窗戶的 identity 需求仍需該 arm）。
      EXECUTE 維持 `deepseek-v4.1-flash`，經 owner 明確確認。
      已記錄衝突：planner 與 checker 現為**同一身分**，dispatcher 不執行 maker==checker REFUSE（D1），
      故此為「已記錄的 重疊」而非「被阻擋」——checker 不再對 planner 提供模型軸上的獨立性。
      Verify: `_governance/round-20261021-r7/40_VERIFY/lane_rebind_minimax/REBIND_RECORD.json`
      與 `.../lane_rebind_minimax/probe_canonical_*.json`。
- [x] 7.10 spine 誠實性：曾於獨立裁決出現前把 PASS 寫入 HGK workorder，已用 typed rollback API
      （`rollback_workorder`）撤回，spine 現為 `ROLLED_BACK` 並有 rollback_record 說明原因；
      self-check C2 現會拒絕「無獨立裁決卻 VERIFIED」的狀態。
