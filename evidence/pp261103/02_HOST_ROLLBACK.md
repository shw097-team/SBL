# Host 與回退（實測）— 2026-11-03

## 1. Host 身份

| 項 | 實值 |
|---|---|
| CLI | `codex-cli 0.164.0` |
| Python | `3.14.9`（PIPD 用 `3.11` venv） |
| git | `2.53.0.windows.1` |
| 沙盒 shell | `C:\Users\user\AppData\Local\Microsoft\WindowsApps\pwsh.exe` → Store 版 PowerShell `7.6.9` |
| 隔離 `CODEX_HOME` | `_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home`（現役 `~/.codex` 全程未改） |

## 2. `HOST-124` 現況：**未修復**

- 現象：`codex exec --sandbox workspace-write` 下每個 `exec_command` 以 `"…\WindowsApps\pwsh.exe" -Command …` 執行，被 sandbox policy 拒絕，turn 掛到 `exit 124`。
- 本輪查明的**新事實**：該 `pwsh.exe` 不是假 stub，而是指向 Store 版 PowerShell 7.6.9 的 App Execution Alias（symlink 85 bytes）。被拒的原因是**執行路徑落在 `WindowsApps`**，不是二進位缺失。
- 已備的合法修法（**尚未驗證**）：把真實 `pwsh.exe` 複製到穩定路徑
  `_run_sbl_tpm_pre_v2_final_20261103/host/bin/pwsh.exe`（301,360 bytes），並以 PATH 前置讓 Codex 解析到非 `WindowsApps` 路徑。
- 為何未驗證：驗證需要一次真實 Host 模型呼叫，需讀取本機模型憑證；該讀取動作**未獲 Owner 同意**（審批逾時）。依規則**不重試、不改道**，故此項維持未證。

**因此**：`P0_HOST_INVOKE` = `HOLD`。`danger-full-access` 可完成任務但**不得**充作受限模式資格（控制方案 §2.2 明文禁止）。

## 3. 回退：repo 級**已實際執行**

隔離 sandbox repo `shadow/gj02-repo`，baseline commit `70757870ef495b0c3c7193fbf35df1223f8a6566`：

```
before: HEAD 70757870ef49…  dirty: M src/demo/billing.py + 4 untracked
run   : git checkout -- .            rc=0
after : HEAD 70757870ef49…（未變）  tracked 檔案已還原基線
verify: python -m pytest -q tests/test_billing.py
        -> 1 failed, 1 passed       （缺陷復現 = 回退真的生效）
```

- 未追蹤產物（`README.md`、`host_notes.md`、`specs/`、`__pycache__/`）保留，未刪；此為設計取捨，已在計數中照實記（dirty_count=5）。
- **plugin 級**：`raw/plugin_list_installed.txt` → `removed.txt` → `final.txt` 顯示 `0.3.0-rc.2` 可卸載並可重新安裝（`installed, enabled` ↔ `not installed`）。
- **缺**：舊版在**真 Host 重新 Loaded** 的證據（需 Host 呼叫，同 §2 阻塞）。

## 4. 安全面

- 全程未寫入世界效果、未簽 Grant、未產生 Nonce、未呼叫原 Issuer／Checker。
- 未修改 `~/.codex`、現役 plugin cache、原 WorkID／Journal。
- 憑證未寫入任何提交、日誌或 remote URL；本輪未成功讀取任何憑證（審批未通過）。
