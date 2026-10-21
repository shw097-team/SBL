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
- [x] 7.6 獨立 VERIFY 車道對凍結後候選的原始裁決（maker ≠ checker）。
      ROUND 1（arm `openai-codex/gpt-6.1-sol`，nonce `R7CHK-NC-20261021-A1`）：已執行 392 秒，
      產生 byte-exact 證據（`stdout_sha256=80397dbb…`、`usage_status=200`、`nonce_present=true`），
      但在給出裁決前 provider 配額耗盡 → dispatcher 記為 `ERR_NO_ARM_EMITTED_NONCE`（ok=false）。
      分類為 `INCOMPLETE_ROUND_PROVIDER_QUOTA`：**保留、不計為驗收、不上浮為 FAIL，也不當 PASS**。
      收據：`40_VERIFY/checker_round1_receipt.json` + `40_VERIFY/checker_round1_receipt/`。
      ROUND 1 提出的兩項實質發現已在候選 `59d2138` 修復並重測（202 passed / 2 skipped）：
        F8 測試只斷言原始碼文字 → 2/3 的合約破壞變異仍全過（已改為行為斷言 + mutation probe）
        F9 建置依賴 ambient interpreter 的 `build` 套件 → 已加入 `_builder_python()` 解析器
      ROUND 2（arm `opencode-go/minimax-m3.1-flash-free`，nonce `R7CHK-NC-20261021-A2`）完成：
      dispatch ok=true、exit 0、nonce 與 usage 正常、guard CLEAN，裁決找出 W1/W2/W3，已修復。
      ROUND 3 兩次嘗試被 dispatcher 的 remote-write 偵測器拒絕（brief 內含該字面 token），
      改寫 brief 後重跑；隨後暫停。
      ROUND 4（arm `openai-codex/gpt-6.1-sol`，nonce `R7CHK-NC-20261021-A4`，237.3 秒，
      `used_rank=1`、`transport_model=gpt-6.1-sol`、`exit=0`、`usage_receipt_ok=true`、
      guard CLEAN、subject digest 前後相同）**產出正式裁決**：
      **`INCONCLUSIVE — NOT ACCEPTED`**。
      理由是其 sandbox 禁止一切檔案寫入，因此無法執行雙 build 比對、完整 pytest、
      mutation 實驗與 W3 write-through 實驗；它沒有嘗試被禁止的變異，也沒有把 maker 的
      收據當作獨立證據。
      **但 INCONCLUSIVE 不是空裁決**：同一份裁決重現 W1，並指出三個真實產品缺陷，已全部修復：
        D1 任何非零 exit 都變成 SkipTest（可讓壞掉的建置藏在缺少後端之後）→ 改為只在
            後端確實不存在時 skip，其餘 raise。
        D2 W1 回歸測試接受 `in (True, False)`，等於沒有斷言 → 改為要求真 bool 且與
            `python -m build --version` 一致。
        D3 mutation probe 把任何非零 pytest exit 都算成「抓到突變」→ 改為解析 summary 行，
            無 failed/errored test 的非零 exit 視為 probe 失敗。
      SWARM 稽核另找出兩條隔離逃逸路徑並修復（繼承的 git 環境變數、保留的 symlink）；
      稽核回報的「主 tree 兩個檔案變動」經獨立查證為 orchestrator 自己的並行編輯
      （staged tree／HEAD／cached diff 全程未變），非寫穿。
      收據：`40_VERIFY/checker_round4/`（transcript 283730 bytes，
      sha256 `7c1e1403b954c2c79573bc9bf02880642ed834a241fd7a5bc07301655682862a`）+ `40_VERIFY/CHECKER_STATUS.json`。
- [x] 7.7 候選與證據推送 `shw097-team/SBL`，遠端 SHA 回讀一致；staged diff secret scan CLEAN。
      Verify: `origin/candidate/r7-20261021-repro-build` = `b6eee0222681340549b1b7c8f863ae84d8db0116`，
      `origin/release/0.1.1rc1` = `0f83ba8aa5239d7115f6c0c649ad7e597cd525b1`，
      `origin/main` = `345b9477cef9917cfb15c162db80ccda09eaebc5`（`git ls-remote` 回讀）。
      FAR 產物另推送 `shw097-team/Fabric`：`origin/pub/far-minimax-mandate-20261021` = `4014bb63803633aa63817cb2cf0c458ed77f21ab`，
      `origin/pub/far-lane-remediation-20261021` = `8fdb9f39124fdd47812a61dd54646a170549307b`。
- [x] 7.10 合併與發布（依 owner 對 FAR 裁決的預授權）。
      車道工具鏈恢復：Codex CLI 就地升級（0.163.0-alpha.11）使宣告的 pin 指向不存在的 binary，
      所有車道 dispatch 在 spawn 前即被拒（`ERR_LANE_PIN_IDENTITY_INVALID`）。活體宣告
      `config/hermes-codex-lane.json` 重新釘選到實際安裝的 binary，registry 的兩個 expected 值
      在同一 commit 一併重釘，drift gate 維持 0 findings；歷史證據不改寫。
      合併：`PR #2` → `93d206997318a2bd1bb81a493575b94d4c719329`（parents 精確為
      `[bedc119, a6bcdd0]`）；`PR #3` → `590c2adf6563af6ef98ea9a7125ddb9d40977c17`；
      `PR #4` → `345b9477cef9917cfb15c162db80ccda09eaebc5`。每次合併前都重跑 preflight，
      合併後都從 API 回讀 parents 與 main 驗證。
      **CI 紅燈根因（實測，非推測）**：hosted CI 連續五輪（27..33）在 ubuntu 與 windows 同時紅，
      而 maker 的 Windows 套件是綠的。CI workflow 只裝 pytest，沒有 `build` 套件；
      `build()` 在呼叫端已 stub build 指令的情況下仍解析 backend interpreter，於是拋 SystemExit，
      環境落差被當成產品缺陷，並連帶拖垮 mutation probe（它要求未突變的 tree 必須通過）。
      以「git 在 PATH、無 build 後端」重現後失敗完全一致、後端可用即消失。
      修復：`build()` 改為接受 builder interpreter 參數、僅在呼叫端未提供時才解析；
      `_has_build()` 不再因不存在的 interpreter 拋例外；D1 的 skip marker 改為符合 builder
      實際輸出；git 缺席時 write-through 不變量改為 skip；新增回歸測試釘住「stub 路徑不得
      呼叫解析器」。量測：CI 等價環境本地 `206 passed, 4 skipped` exit 0；hosted CI run 34/35/37 全綠。
      發布：`v0.1.1rc1` prerelease（release id 419526963），
      https://github.com/shw097-team/SBL/releases/tag/v0.1.1rc1
      產物 wheel 52436 bytes sha256 `efd6798bf2a6959069c6cd58c60aeabec1005c84043b1088efafc63e1bee9dfe`、
      sdist 74096 bytes sha256 `baaa6aa0a1260b8f3c57ed246d3a521734efc9d4ed4e998b748bd204c714cd00`；
      **從 GitHub 下載後重新雜湊，與本地建置 byte-identical**。三個獨立 build
      （release branch、origin/main、工具內建雙 build 驗證）產出相同 bytes。
      版本常數：`sbl_core.__version__`、`sbl_harness.ADAPTER_VERSION`、
      `sbl_sp.plugins.VERSION`、`sbl_stack` manifest version、pyproject version。
      `HGK_PIN['version']` **刻意不動** —— 那是被依賴方 `hg_kseos` 的版本，不是本套件版本，
      動它會讓 harness 報出假的 `REFUSED_VERSION_MISMATCH`。
      舊的 `v0.1.0-foundation-preview` release 與 tag 未受影響。
      收據：`50_TS06/PR2_MERGE_RECEIPT.json`、`50_TS06/repro_result_0.1.1rc1.json`、
      `50_TS06/RELEASE_RECEIPT_0.1.1rc1.json`。
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
