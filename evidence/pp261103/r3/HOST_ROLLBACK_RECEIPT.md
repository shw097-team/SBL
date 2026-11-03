# Host 與回退收據（r3，脫敏）

## 1. `HOST-124` 的兩層原因（本輪新增判定）

### 第一層（已解）：Codex 的 shell 解析 + MSIX 打包限制

- Codex 內建候選順序：`C:\Program Files\PowerShell\7\pwsh.exe`（映像內硬編路徑）→ 找不到才走 PATH 的 `pwsh`。
- 本機 `C:\Program Files\PowerShell\7` 不存在（無管理員權限建立：`mkdir` → `Permission denied`），故落到
  `%LOCALAPPDATA%\Microsoft\WindowsApps\pwsh.exe`，那是 **App Execution Alias**（85 bytes）指向 Store 套件。
- MXC 沙盒的 `path_norm.rs` 對 `\windowsapps\` 子字串回 `packaged_app`：**打包應用不得在沙盒容器內啟動**。
- 直接重現（無模型呼叫）：
  ```
  codex sandbox "C:/Users/user/AppData/Local/Microsoft/WindowsApps/pwsh.exe" -Command "7+7"
  → CreateProcessAsUserW failed: 5 (存取被拒)
  ```
- **修法已驗證**：把完整非 WindowsApps 的 PowerShell 7.6.9（287 MB 完整 drop，含 `pwsh.dll`、
  `System.Management.Automation.dll`、`Modules\`）放在 `<PW7_ROOT>`，以 PATH 前置令 Codex 解析到它：
  ```
  PATH=/c/Users/user/pwsh7:$PATH
  codex sandbox "<PW7_ROOT>/pwsh.exe" -NoProfile -NonInteractive -Command '$PSVersionTable...; 7+7'
  → 7.6.9
  → 14
  ```
  且 `codex exec` 的事件流已顯示它解析到 `<PW7_ROOT>\pwsh.exe`（不再是 WindowsApps）。

### 第二層（未解）：沙盒拒絕建立子程序

在 `workspace-write`、`read-only`、以及加 `sandbox_permissions=["disk-full-read-access"]` 三種設定下，
每一次 `exec_command` 都被拒絕，且**連 `cmd.exe` 也一樣**：

```
exec_command failed: CreateProcess { message: "Rejected(... rejected: blocked by policy)" }
  · "<PW7_ROOT>\pwsh.exe" -Command 'echo HOST_PROBE_OK'
  · "C:\WINDOWS\system32\cmd.exe" /c 'echo HOST_PROBE_OK'
```

結論：**這不是 shell 解析問題**，是本機 MXC 沙盒在非互動 `codex exec` 下無法建立子程序。
因此受限模式的 Host 執行在此主機上目前不可得；`danger-full-access` 的執行結果**不**作資格。

### 解除路徑（具名，不新開階段）

1. 以管理員安裝官方 PowerShell 7 到 `C:\Program Files\PowerShell\7`（內建首選路徑）。
2. 修本機 MXC 沙盒子程序建立（或以互動模式並逐次核准，讓 approval 路徑生效）。
3. 兩者成立後跑一次 fresh Goal + 一次 Nontrigger，即可回讀 `Installed→Loaded→Invoked/Used`。

## 2. 隔離與邊界

| 項 | 值 |
|---|---|
| `CODEX_HOME` | `_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/shadow/codex-home`（現役 `~/.codex` 未改） |
| 模型 | `deepseek-v4.1-flash`（OpenCode Go）；金鑰只存在本機暫存檔，未寫入任何提交／日誌 |
| 呼叫次數 | 3 次 `codex exec`（1 次 workspace-write、1 次 +disk-full-read、1 次 read-only），全部未產生世界效果 |
| 沙盒直測 | 2 次 `codex sandbox`（WindowsApps 版被拒；完整非打包版成功） |

## 3. 回退

**Repo 級（已真跑）**

```
before: HEAD 70757870ef49…  dirty M src/demo/billing.py + 4 untracked
run   : git checkout -- .   rc=0
after : HEAD 70757870ef49…（未變）；tracked 檔還原基線
verify: pytest -q tests/test_billing.py -> 1 failed, 1 passed（缺陷復現）
```

**Plugin 級（收據在案）**：`raw/plugin_list_installed.txt` → `removed.txt` → `final.txt`，
`0.3.0-rc.2` 可卸載並可重新安裝（`installed, enabled` ↔ `not installed`）。

**缺**：舊版在真 Host 重新 `Loaded`（同 §1 阻塞）。Repo 回退**不得**被表述為世界效果可逆。
