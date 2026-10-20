# 50 — HANDOFF CHECKPOINT（2026-10-20 16:10 +08:00，使用者要求關機前保存）

**一句話狀態：** 可運作的 SBL v0.1 候選已推上公開 repo（6 個不可變候選分支 + 1 個 WIP），
本輪獨立外審跑了 **6 回合**，每一回合都找到真缺陷且都被修掉（產品類缺陷全數關閉）；
最後一回合唯一殘留的判定是 **GATE TOOLING**（掃描器 local-part 允許清單），修正已寫但 **尚未重跑 gate、未經 checker 複驗**。
本輪 **沒有任何 `INDEPENDENT_CASE_PASS`、沒有 `RELEASED`、沒有 `PRODUCTION`**，claim ceiling 維持 `LOCAL_QUALIFIED_CANDIDATE`。

---

## 1. 恢復執行前必須先做的事（照順序）

```bash
# 1) 控制平面：EXECUTE 前門若不在，先起來（它不會自動啟動）
cd C:/Projects/Agent_Workspace/HG-KSEOS
pwsh -NoProfile -File scripts/start-hgk-exec-frontdoor.ps1 -Action Start
curl -s http://127.0.0.1:10100/healthz

# 2) 回到工作分支
cd C:/Projects/Agent_Workspace/SBL
git checkout wip/r2-r6-localpart      # 目前 HEAD = a01d336（含未驗證的 R6 修正）
git status --porcelain                # 應為空

# 3) 重跑 gate（R6 修正的驗證就從這裡開始）
PY="C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe"
"$PY" tools/run_gates.py; echo "GATES_EXIT=$?"
py -3.11 -m pytest -q -p no:cacheprovider
```

`tools/run_gates.py` 必須 exit 0、每個 pytest gate denominator > 0、`G-SUITE-FULL` denominator = 真實總數
（v6 時是 124；R6 修正後應為 125）。若綠燈，把 wip 併成新候選分支（`candidate/r2-20261020-v7`）並推，
再決定是否再請 checker 跑一回合。

## 2. 車道／模型（已實測可用，勿改）

| 車道 | 模型 | rank | 實測 |
|---|---|---|---|
| EXECUTE | `opencode-go/deepseek-v4.1-flash` | 1 | 3 次成功（slice A/B1/B2/C），2 次 `ERR_LANE_ALL_ROUTES_EXHAUSTED`（修補形狀） |
| VERIFY_SECURITY | `openai-codex/gpt-6.1-sol` | 2 | 6 次成功，每次 234–495 s，`required_arm == served_arm` |

必要參數範例（少一個就會失敗）：

```
--lane VERIFY_SECURITY --force-rank 2 --max-candidates 1 --require-arm openai-codex/gpt-6.1-sol \
--pool config/lane-route-slots.candidate.json \
--codex-executable C:/Users/user/AppData/Local/OpenAI/Codex/bin/896a0166b774037a/codex.exe \
--cwd <copy outside the subject> --sandbox workspace-write --allow-sandbox-escalation \
--guard-subject C:/Projects/Agent_Workspace/SBL --nonce <NONCE> --timeout 1800 \
--json-out <scratch>/r.json --attempt-log-dir <scratch>
```

**兩個已踩過的坑：**（a）`--json-out` / `--attempt-log-dir` 若落在 `--guard-subject` 內，直接
`ERR_GUARD_ROOT_CONTAINS_HARNESS_OUTPUT`；（b）checker 的 copy 必須含 `.git`，否則 repo-context 測試失敗、
也無法認證 SHA。詳見 skill `hgk-kanban-and-lane-routing/references/lane-pitfalls-measured.md`。

## 3. 候選鏈與外審結果（原始收據都在第 6 節的路徑）

| 分支 | commit | 外審 | 結論 |
|---|---|---|---|
| `candidate/r2-20261020` | `ab17440` | R1 | FAIL：4 HIGH / 3 MED / 1 INFO（冒充 principal、ceiling 由呼叫者決定、PASS 未綁證據、掃描器整行白名單、空來源清冊、denominator 少算、3.12-only API） |
| `candidate/r2-20261020-v2` | `8640f02` | R2 | FAIL：SEC-03/VERIFY-01..03 **closed**；新開 NEW-01/02/03 + ENV-01 |
| `candidate/r2-20261020-v3` | `49dab08` | R3 | FAIL：A..I **9/9 closed**；新 1 HIGH（`=changeme` 後綴）+ 2 ENV |
| `candidate/r2-20261020-v4` | `7202922` | R4 | FAIL：R3-NEW-01 closed、12 項全 closed；新 1 MEDIUM（`attackerexample.com`）|
| `candidate/r2-20261020-v5` | `718a48d` | R5 | FAIL：R4-NEW-01 closed；新 2 項（hyphen 截斷、空 root 回 CLEAN）|
| `candidate/r2-20261020-v6` | `eb2e07c` | R6 | FAIL：R5-NEW-01/02 closed（9 變體全擋）；**唯一殘留 = R6-NEW-01，checker 自評 `GATE TOOLING`**（`alice!user@…` 截斷後撞上 local-part 白名單）|
| `wip/r2-r6-localpart` | `a01d336` | — | **未驗證**：移除 local-part 白名單的修正 |

**重要判讀：** 6 回合 FAIL 不是「產品壞掉」，而是「每一回合都還有東西可以修，且都修掉了」。
checker 在第 6 回合把殘留項明確歸類為 repo 自家 gate 工具（`tools/`），不是 `sbl_core/sbl_sp/sbl_cli`。
仍不可對外宣稱通過——最後一次完整外審的 verdict 是 FAIL。

## 4. 已完成（有原始收據）

- 產品：Shared Core + `SBLM01..06`、三個 SP 與 manifest/權限/憑證、GJ01 `sbl-todo`、GJ02 brownfield patch+rollback、GJ03 skill bridge、39 格 ModeGate、G-KNOW 檢索（含拒答）。
- 測試：**124 個測試**在 CPython **3.12.14 與 3.11.9** 都綠；gate 執行數 227。
- 來源凍結：14 冊 `DOC-00..13`，aggregate `754cf7be…cda3b`，清冊強制精確（空清冊會被拒）。
- Contract：C0..C9 `lint/activation/acceptance/compile` 全 exit 0，`PROMPT_COMPILE_PASS`（僅契約形狀）。
- GitHub：`shw097-team/SBL` **public**、default `main` 仍停在 bootstrap `ca6830d`，所有候選都在側分支，
  每次 push 後都以 GitHub API 匿名回讀比對 SHA（全部相符）。
- 治理：`_governance/round-20261020-r2/` 下有 `00_ROUND_STATE`、`10_BUILD_SPEC`、`11/12/13` 切片規格、
  `14_REPAIR_R1`、`15_EXTERNAL_CHALLENGE_R1`、`16/18/19_REPAIR_R*_RESULT`、`40_EVIDENCE`、
  `30_PUBLICATION_READBACK`、`20_RESUME_CHECKPOINT`。
- 並行子代理成果：`16_GKNOW/`（227 檔 / 23,174 chunks / 17 probes，13 pass 4 fail 誠實記錄）、
  `17_DONORS/`（441 列，6 donor / 24 slot / 25 method / 386 key 全部在語料中找到並逐列引用；1 ACTIVE、6 NATIVE_SUBSTITUTED、423 DEFERRED、8 PROHIBITED）。

## 5. 未完成（恢復後接手清單，依重要性）

1. **R6 修正驗證**：跑 §1 的 gate；綠燈才升候選 v7，否則修到綠。
2. **再一回合 checker**（建議）：窄範圍只測 R6-NEW-01 + 迴歸，約 5 分鐘。
3. **證據 commit**：把 `_governance/round-20261020-r2/` 與 `evidence/` 打包成 **獨立 evidence commit**
   （建議分支 `evidence/r2-20261020`，parent = 凍結候選），並寫 `evidence_commit_sha` 進
   `40_EVIDENCE.md` 與 `30_PUBLICATION_READBACK.json`。
4. **把 6 回合成績收據搬進 repo**：從 `_sbl_round_artifacts/r2/verify-runs*/` 取
   `VERIFY_candidate_*.json` 與 `VERDICT_parsed_*.json`，放到 `_governance/round-20261020-r2/verdicts/`
   （先跑 `tools/secret_scan.py --root .` 確認乾淨）。
5. **`40_EVIDENCE.md` §6 更新**：補 R5/R6 與最終 verdict（目前只寫到 R4）。
6. **manifest**：`python tools/evidence_manifest.py --root . --paths ... --out evidence/MANIFEST.json`
   （工具已存在，尚未產生 final manifest）。
7. **Kanban 收尾**：board `sbl-pipdls-20261020` 的 verifier / synthesizer 卡尚未 claim/complete。
8. **Open TT**：GitHub 分支保護未設（`protected:false`）、LICENSE 未裁定（Owner 決定，勿猜）、
   GitHub Actions 從未觀測到執行（不得宣稱 CI green）、`SWOF_CONNECTED` 無原生 ACK 仍 blocked、
   U01–U50/149 children 與 P01–P07/M00–M15 的 trace closure 未建、PIPD P4 native intake/ECP/TQAEP 未執行。
9. **環境殘留（不可刪，已 gitignore）**：`SBL/.pytest_cache`、`SBL/.pytest_tmp`（sandbox ACL 拒絕本使用者）。

## 6. 檔案位置

| 內容 | 路徑 |
|---|---|
| 回合治理與證據 | `C:/Projects/Agent_Workspace/SBL/_governance/round-20261020-r2/` |
| 6 回合 checker 原始收據（含 attempts、parsed verdict） | `C:/Projects/Agent_Workspace/_sbl_round_artifacts/r2/verify-runs1..6/` |
| G-KNOW 127 MB 索引 + RUNS（**刻意不進公開 repo**） | `C:/Projects/Agent_Workspace/_sbl_round_artifacts/r2/bulk/` |
| 公開 repo | https://github.com/shw097-team/SBL |
| Token 使用方式 | 只由本機 credential helper 讀取（scratch/ghcred.sh，不進 repo、不進 argv、不落 log） |

## 7. 回滾

```
git -C C:/Projects/Agent_Workspace/SBL reset --hard ca6830d9fc9d89b7b87e818670dd67b393472d79
# 或只丟棄本輪：刪除 candidate/r2-20261020{,-v2..-v6} 與 wip/r2-r6-localpart（本地 + 遠端）
python -m sbl_cli.sbl_todo uninstall --yes --data-dir <dir>
```

## 8. Claim ceiling（恢復後也不得跳級）

`PROMPT_COMPILE_PASS` ✅（契約）｜`RUNTIME_READY` 未評｜`LOCAL_QUALIFIED` 為 maker 側主張（gate+測試）
｜`INDEPENDENT_CASE_PASS` ❌（最後 verdict FAIL）｜`RELEASED` ❌｜`PRODUCTION` ❌。
