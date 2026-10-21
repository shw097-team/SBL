# SBL_R14_EXECUTION_STATUS — round-20261022-r14

**Order**：`SBL-R14-FULL-DOC-POST-R13-20261022`（EXTERNAL_ROUTE_OUT，需本機 canonical 編譯）
**裁決**：**PARTIAL**（本回合完成 M1 前置：來源身分、正式編譯、分母重現、車道實測）
**主觀目標**：`SBL_FULL_PRODUCT` — **OPEN**；優先產品 Gate `SBL_SWOF_FIRST_GOVERNED_CHANGE` — **NOT_STARTED（BLOCKED，見 §6）**

---

## 1. Freshness（TS00，2026-10-22T00:47+08:00 實測）

| Repo | 本機分支 | 本機 HEAD | 遠端 main | 備註 |
|---|---|---|---|---|
| SBL | `evidence/r7-20261021-c7` | `2dde2d8` | `dc5428f2` | 本機樹**不在 main**；產品施工須自 `origin/main` 開分支 |
| HG-KSEOS | `codex/hgk-final-closure-002` | `5119c97` | 無 remote | 7 modified ＋ 291 untracked（他人工作，未碰） |
| Fabric | `pub/far-minimax-mandate-20261021` | `d626356` | `bcd91043` | 本機分支 ≠ main |
| SWOF | `evidence/swof-w2r5-closure-repair` | `417f115` | `acdbfaa` | 本機分支 ≠ main |
| PIPD | `rescue/r5p-uncommitted-20261016`（目錄名 `PIPD`） | — | `e95942ab` | **與命令書 `PIPD-LS-SP` 不符** → `TT-R14-001` |

R13 資產：HGK `49f48ae` / `5119c97` 在本機 HEAD 歷史內；SBL evidence `ffd786c8` 遠端可讀。**未重做、未覆蓋**。

## 2. TS01 來源身分（新算，非引用）

- 14/14 DOC 逐檔 SHA-256 與 `CONTROL_PACKAGE_MANIFEST.json`（r9 pin）**完全相同**；`total_bytes=17,473,442` 相同。
- rollup 依 manifest 宣告方法（`'<DOC-ID> <sha256>'` 以 LF 串接）重算 = **`01b972c8…f9cf9d`**，**重現歷史值**。
- canonical root 與 `_sbl_src_mirror` 14 檔**逐位元相同**。
- 證據：`raw/TS01_source_identity.json`、`raw/CONTROL_PACKAGE_MANIFEST.json`。

## 3. TS01 正式編譯（CAPC，四命令）

| 契約 | contract_sha256 | lint | activation | acceptance | compile | task_id |
|---|---|---|---|---|---|---|
| `SBL_C0_C9_CONTRACT-R9.json` | `dd200277…d55d` | 0 | 0 | 0 | 0 | `SBL-PIPDLS-20261021-R9-C3` |
| `SBL_C0_C9_CONTRACT-R14.json`（本回合新作） | `8643749…4a89` | 0 | 0 | 0 | 0 | `SBL-PIPDLS-20261022-R14-C1` |

R14 契約以 R9 為底，改寫 `intent.goal / constraints / claim_ceiling=LOCAL`、`changeset=CONTINUATION`（baseline_verified=true、`must_not_reopen` 加 R13 兩切片與 R9 pin），並排除草案封裝與語義百分比。**注意**：`claim_ceiling` 只接受 enum（`LOCAL`），初版寫 `LOCAL_CANDIDATE` 被 `PL-014` 擋下 —— 已改，非繞過。
證據：`raw/compile_r14/{compiler-receipt.json,compiler-report.json,thin-prompt.md}`。

## 4. TS02 分母（同一環境重跑，全量）

`18 failed / 580 passed / 90 subtests / 149.24s / exit=1` — 與 R13 final **逐項相同集合**，新增失敗 0。
18 案逐案 first-fail 已抽成 `raw/failed18_map.txt`（每案實跑一次、取第一條 `E`）。

| 叢集 | 案數 | 代表 first-fail | 最早 Owner |
|---|---|---|---|
| 車道宣告／serving | 12 | `test_lane_policy`: registry 宣告 `minimax` vs 投影 `gpt-6.1-sol`；`ERR_MANDATE_ARM_UNRESOLVED`；`ERR_LANE_TOO…` | HGK Owner（registry/epoch） |
| 文件投影／canonical runtime | 5 | `denominator_head 22e21f03 ≠ 5119c97`；guide 投影缺 `caf0c4ff…`；config 解析到 APPData 而非 `Local\hermes` | 文件投影 Owner／Hermes 設定 Owner |
| 外來 dirty tree | 1 | `test_r4_only_allowed_files_changed`：他人 291 untracked 導致 allowed-files 集合不符 | 工作區 Owner |

命令書假設 13/4/1；**本回合實測為 12/5/1**，差異在 `start-hgk-hermes.ps1:153` 例外（歸車道腳本）與 `task014` config 路徑（歸 canonical runtime）。以實測為準，不套用假設。
**不宣稱 HGK 全綠**：18 紅全部 OPEN，本回合未關閉任何一案。

## 5. TS05 車道實測（fresh probe，brief 內含 typed nonce）

| lane | required | served | rank | ok |
|---|---|---|---|---|
| PLAN | `openai-codex/gpt-6.1-sol` | 同左 | 2（rank1=minimax） | ✔ |
| EXECUTE | `opencode-go/minimax-m3.1-flash-free` | 同左 | 2（rank1=deepseek） | ✔ |
| VERIFY_SECURITY | `openai-codex/gpt-6.1-sol` | 同左 | 1 | ✔ |

**更正 `O-R13-001`**：把 `nonce <x>` 以字面行寫進 brief，三條車道**全部回報 nonce**、`--require-arm` 通過。
因此 R13 的結論要修：不是 runner 丟掉 nonce，而是**brief 未把 nonce 當成必要輸出**；缺它時 runner 回 `ERR_NO_ARM_EMITTED_NONCE`。
仍然成立的部分：**不得以 usage 200 當寫入憑證**，寫入須以 `git diff + SHA + WriteSet + Native result` 佐證。
證據：`raw/lane_{PLAN,EXECUTE,VERIFY_SECURITY}.json`、`SBL_R14_TT_CR_REGISTER.json` 的 `CORR-R14-001`。

## 6. 未開始／阻斷（誠實）

- **TS03/TS04**：原生四元組語義與動態 checker 尚未做；R13 checker 仍是 `STATIC_ONLY`（`Tests not run`），不得當動態 TQAEP PASS。
- **TS06/TS07**：Commander-SP／Challenge-SP **未真呼叫**，維持 `LANE_ONLY`。
- **TS08–TS30**：全部 `NOT_STARTED`。
- **M3/SWOF**：無 W3 permit／Receiver ACK → `BLOCKED_WAIT_OWNER`，不得以 Shadow 造 PASS。
- **語義分母**：`UNKNOWN`（PIPD Source Owner 未簽），不得由 149/441/38 推百分比。

## 7. 本回合不變量

R13 兩切片與 evidence 未動；他人 7 modified／291 untracked 未 stage、未 reset；無 force-push；SBL main 未合併、未發 Release。
