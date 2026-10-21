# R12 回合 · 落地後讀回（POST_MERGE_READBACK）

時間：2026-10-21（Asia/Taipei）· 執行者：Hermes（受治理 Runtime 面）· 車道：PLAN `openai-codex/gpt-6.1-sol` / EXECUTE `opencode-go/minimax-m3.1-flash-free` / VERIFY `openai-codex/gpt-6.1-sol`

## 1. 已落地（遠端可讀回）

| 動作 | 結果 | 讀回證據 |
|---|---|---|
| PR #5 併入 `candidate/r9-20261021-ctrlpkg` | merged，merge commit `31406ad7ad6c95d6124b464ef978e97b5cd9f29f` | `git ls-remote refs/heads/main`；API commits/main |
| PR #6 併入 `docs/r12-claims-20261021` | merged，merge commit `37c4d1aa52737f3236426aff6d1fac900a7e4d14` | 同上 |
| `main` 目前 | `37c4d1aa`（remote） | `git ls-remote` |
| CI @ `31406ad7` | ubuntu **success**、windows **success** | check-runs API |
| CI @ `37c4d1aa` | ubuntu **success**、windows 於本檔寫出時仍在執行 | `readback/ci_main.json`（快照） |
| 新增 entrypoint 宣稱 | `pyproject.toml [project.scripts]` = `sbl-todo` / `sbl-stack` / `sbl-harness` 三項 | 直接讀檔 |

## 2. 車道 (lane) 與會話 (session) 分離

三次 mandate 探針都是**車道子行程**（`--force-rank` + `--require-arm` + relay nonce + usage 200），與本會話模型無關：

| lane | required | served | rank | usage |
|---|---|---|---|---|
| PLAN | `openai-codex/gpt-6.1-sol` | 同左 | 2（rank1 為 minimax，與 mandate 相反） | 200 |
| EXECUTE | `opencode-go/minimax-m3.1-flash-free` | 同左 | 2（rank1 為 deepseek） | 200 |
| VERIFY_SECURITY | `openai-codex/gpt-6.1-sol` | 同左 | 1 | 200 |

→ 這是 `--force-rank` 覆蓋 registry 宣告面的**逐輪 mandate**，不是修改 registry（D-11 待 Owner 裁決）。

## 3. Bounded writer 誠實記錄

`EXECUTE` 車道寫 `README.md` 的回合**寫入成功、arm 驗證失敗**（`ERR_NO_ARM_EMITTED_NONCE`）。處置：不採納車道憑證、改以逐 byte 人工比對四處替換、由 commit 者整理換行。詳見 `30_WRITER_RECEIPT.md`；新觀察 `O-R12-001`。

## 4. 編排面

- **KANBAN / SWARM**：board `sbl-r12-far`（`kanban.db` 實體），swarm root `t_c1b4d403`，5 workers `t_47017ac5 t_c7c44c52 t_aea902e3 t_0d384783 t_dd0f5282`（逐一對應 O-1..O-5），verifier `t_00d2062c`，synthesizer `t_5f76be91`。讀回見 `readback/kanban_readback.txt`。
- **OPENSPEC**：`openspec/changes/far-r12-20261021/{proposal,tasks}.md` 已隨 PR #6 進 main。
- **GSTACK**：本輪**未選用**（單一寫者、無平行審查需求）；狀態記為 `NOT_SELECTED`，不宣稱已启用。

## 5. 未落地（保持 OPEN，需 Owner/issuer）

D-04 語義分母、D-05/D-06/D-07 三段鏈、D-09 `_repo_head`、D-12 三 Plugin、D-13 441/149/38、D-16 SWOF。
`SBL_FULL_PRODUCT` = **OPEN**。
