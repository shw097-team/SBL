# 30 · bounded writer receipt（DOCS-ONLY）

## 車道

| 欄位 | 值 |
|---|---|
| lane | `EXECUTE` |
| 要求 arm | `opencode-go/minimax-m3.1-flash-free` |
| 強制 rank | 2（rank1 為 `deepseek-v4.1-flash`，與 mandate 不符） |
| 執行檔 | `C:/Users/user/AppData/Local/OpenAI/Codex/bin/6257d9e8f63c0f2b/codex.exe` |
| sandbox | `workspace-write`，`--cwd C:\Projects\Agent_Workspace\_r12_docs` |
| 寫入範圍（brief 硬約束） | **只准 `README.md`**，禁止 git 指令、禁止碰 `contracts/ tests/ tools/ pyproject.toml _governance/` |

## 車道裁決：**FAIL — `ERR_NO_ARM_EMITTED_NONCE`**

writer 產出長篇工作輸出，**未在 arm 回應中回報 nonce**，因此 `--require-arm` 的 arm 驗證不成立：

```json
{"code": "ERR_NO_ARM_EMITTED_NONCE", "nonce_absent_arms": ["opencode-go/minimax-m3.1-flash-free"]}
```

**但寫入確實發生了**（`git diff --stat` = `README.md | 28 +++++++++++++-------------`，1 file changed, 18 insertions, 10 deletions）。

## 處置（不掩蓋、不重跑湊綠）

1. 車道憑證**不採納**為「已驗證的 bounded write」。
2. 改以**逐 byte 人工比對**驗收：`git diff README.md` 全量檢視，確認**僅**四處替換、無其他檔案、無夾帶指令碼或依賴變更。
3. 由 commit 作者（Hermes）整理段落換行，未改語義。
4. 事實入帳為新觀察 `O-R12-001`：**writer lane 的長輸出會吞掉 arm nonce**，`--require-arm` 對 writer 回合不可作為唯一的寫入憑證 → 之後 writer brief 必須把 nonce 指定為**第一行輸出**，或以 post-diff 檢查為主要 gate。

## 驗收（人工逐條）

| brief 要求 | 實際 | 判定 |
|---|---|---|
| R1 首段改為 released pre-release line | 已改，並補空行 | PASS |
| R2 `CANDIDATE_ONLY` 段整段替換，保留 claim ceiling（非 production、非獨立驗收） | 已改，且明示「pin ≠ native admission ≠ host install」 | PASS |
| R3 `one console script` → 三個 entrypoint | 已改；與 `pyproject.toml [project.scripts]` 的 `sbl-todo`/`sbl-stack`/`sbl-harness` 相符 | PASS |
| R4 `The CLI has no --help` → `sbl-todo has no --help` | 已改 | PASS |
| 只改 README | `git status` 僅 `README.md`（另有本回合新增的治理/文件檔，非 writer 所寫） | PASS |

## 主張上限

本檔只證明「一個 docs-only 變更被寫出且被人工逐條核對」。**不**證明 writer 車道已通過 arm 驗證、不證明 EXECUTE 車道的寫入權受 native permit 約束（那是 R9-04，仍 OPEN）。
