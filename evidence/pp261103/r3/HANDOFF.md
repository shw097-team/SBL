# HANDOFF — 這個 TPM 現在能做什麼、不能做什麼

> 只說明「如何使用」與「尚未取得什麼」；本文件**不含** `FHS_PIPD-LS-PKG_v2` 主產包、22 WP 或 W0–W3 內容。

## 1. 一句話

**`PRE_V2_CLOSEOUT=NO`**：設計級能力可用且有真證據；**受限 Host 執行**與**原 Case/Oracle 來源**兩項缺口使前置資格尚未成立。
不得把本輪成果表述為「合格 TPM 已可供 FHS v2 主產出使用」。

## 2. 現在就可以用（已驗）

| 能力 | 怎麼用 | 邊界 |
|---|---|---|
| 原 Writer 產四件並被原 Reader ACK | `python -m pipd_ls_sp.cli --root <R> validate --bundle <bundle.json> --require-four` → `PASS / checked 4 / complete true / exit 0` | `checked=4` ≠ Qualified |
| 錯誤物件被拒 | 同上，錯 schema → `exit 1` | 只驗結構與跨檔一致性 |
| Effect 由 operation 決定 | `pipd_ls_sp.operation_registry.load_from_repo(<SBL root>)` 取契約；`effect_for_operation()` | `authority_state=SOURCE_BOUND_OWNER_UNVERIFIED`；無效期集 ratify |
| Planned ≠ Live 分離 | `PlannedTQAEP` 可無 receipt 建立；假收據／假 grant 拒收 | `RUNNER_UNBOUND` 合法，但 `QUALIFIED` 不可聲稱 |
| 插件身分可追溯 | rc.2 `3a9da65…`、14 SKILL、Installed 位元組相同 | Host `Loaded/Used` 尚未成立 |

## 3. 現在不能用（兩個具名缺口）

| 缺口 | 影響 | 誰能解 |
|---|---|---|
| **受限 Host 無子程序建立**（`exec_command` 一律 `blocked by policy`，連 `cmd.exe`） | `P0_HOST_INVOKE`／`P0_ROLLBACK` 的 Host 段 | Host 端：安裝官方 PowerShell 7 到 `C:\Program Files\PowerShell\7`，並修 MXC 沙盒／改用可核准的互動模式 |
| **Slice 無原 Case／Oracle registry** | `P0_TQAEP_FUO` | SBL/PIPD 原 Case Owner 提供該 Slice 的 required 集 |

## 4. 建議的下一步（不新增 Gate）

1. Host 端修好後，跑一次 fresh Goal＋一次 Nontrigger，讀回 `Installed→Loaded→Invoked/Used`；
   再切回舊版重新 `Loaded`，補齊 `P0_ROLLBACK` 的 Host 段。
2. 取得該 Slice 的原 Case／Oracle registry 後重建 `PlannedTQAEP` required 集。
3. 兩項到位即重作**一次** `PRE_V2_CLOSEOUT`；本輪已 PASS 的八項不需重跑。

## 5. 安裝與回退（現況）

- 安裝：Codex plugin cache（隔離 `CODEX_HOME`）載入 `sbl-tpm-sp 0.3.0-rc.2`；rc.2 ZIP 未重建。
- 回退：Repo 級 `git checkout -- .` 已真跑並使缺陷復現；plugin 卸／重裝收據在案；**Host 級重載未證**。
- 不得以 `danger-full-access` 的執行結果作為 Host 安全資格。
