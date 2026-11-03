# FAR 研究結論：三個 FirstFail 的可解性、授權路徑與工程裁決

**FAR Run**：`FAR-R3-HOST-UNBLOCK-2026-11-03`　**Owner 授權**：`WIN-f3452453f719`（HOST_OPERATIONS ceiling、TTL 4h、20 ops）
**問題（decision question）**：在「驗收對象是真實 Codex 環境的實跑」這個前提下，三個 FirstFail 各自能否解除、由誰解除、需要什麼簽章，以及應作何工程裁決。

---

## R1 計畫與停止條件

| 子問題 | 方法 | 停止條件 |
|---|---|---|
| Q1 Windows 沙盒擋的是什麼 | 三種 sandbox 模式實跑 + 直呼 `codex sandbox` | 出現可重現的非-shell 錯誤即定位 |
| Q2 容器能否成為合法 Codex 執行環境 | 容器內安裝同一插件、跑 Goal／Nontrigger／回退 | 取得 Installed→Loaded→Invoked/Used 全鏈 |
| Q3 Owner 信封能否解 F3 | 讀 `owner_window.py`／`owner_vault.py`，實簽並驗簽 | 簽章以正式公鑰驗證通過 |
| Q4 lane／模型路由是否解任一項 | 讀 HG-KSEOS lane 與收據 | 逐項判定「解／部分／不涉及」 |

---

## R3 事實（皆有原始輸出）

### F1｜Windows 沙盒在 process 層被擋，不是 shell 問題

```
codex exec -s workspace-write  … → Rejected("…pwsh.exe -Command 'echo …'` rejected: blocked by policy")
codex exec -s workspace-write -c sandbox_permissions=["disk-full-read-access"] → 同上
codex exec -s read-only        → 同上，連 "C:\WINDOWS\system32\cmd.exe" 也被拒
codex sandbox "…/WindowsApps/pwsh.exe" … → CreateProcessAsUserW failed: 5 (存取被拒)
codex sandbox "<HOME>/pwsh7/pwsh.exe" … → 7.6.9 / 14（成功）
```

**結論**：shell 解析與 MSIX 打包限制是第一層（已解）；第二層是此主機的沙盒**無法建立子程序**，與 shell 無關。

### F2｜`C:\Program Files\PowerShell\7` 缺失＝Codex 的首選路徑落空

Codex 映像內硬編 `C:\Program Files\PowerShell\7\pwsh.exe`，落空才走 PATH；PATH 上只有 WindowsApps 的 MSIX alias，沙盒對 `\windowsapps\` 回 `packaged_app`。完整非打包 PowerShell 7.6.9 drop 在 `codex sandbox` 下可正常執行（已證）。

### F3｜容器是**真實 Codex 環境**，且全鏈可跑

| 步驟 | 證據 |
|---|---|
| Host identity | Debian 12 (bookworm)、kernel `6.6.87.2-microsoft-standard-WSL2`、image `node@sha256:18a6d90f…`、codex-cli **0.166.0** |
| Installed | `codex plugin add sbl-tpm-sp@sbl-pre-primary-local` → `Installed plugin root: /codex-home/plugins/cache/…/0.3.0-rc.2` |
| Loaded | `codex plugin list` → `sbl-tpm-sp@sbl-pre-primary-local  installed, enabled  0.3.0-rc.2` |
| 身分一致 | `plugin.json` sha256 `48d704bc…a281`（與 Windows rc.2 ZIP **逐位元組相同**）、14 個 `SKILL.md` |
| Invoked/Used | 受限 `workspace-write` 下 `exec_command` → `/bin/bash -c 'echo CONTAINER_HOST_PROBE_OK'` exit 0；Skill 實用：模型讀取插件 `skills/**/SKILL.md` 並產出 `/work/host_notes.md`（1,274 bytes，含 ceilings） |
| Nontrigger | 不相關 Goal：`NONTRIGGER_REFS=0` |
| Rollback | `remove` → `not installed`（cache 清空）→ `add` → `installed, enabled 0.3.0-rc.2`（版本閉合） |

### F3-b｜Owner 信封可解「授權與簽章」這一半

`owner_window.py`（FAR-15／16）＝Ed25519 私鑰以 scrypt+AES-256-GCM 封裝，一次性口令開窗，之後在 TTL／ops 預算內批次簽章；視窗寫 `window.json`、`window.token`、`SIGNING_LOG.jsonl`；**拒絕** release／sourcefreeze／policy-authority／trust-anchor／owner_enrollment，且 effect 不得超過開啟時 ceiling。

本輪實簽兩件（3/20 ops）：

| 簽章對象 | 結果 |
|---|---|
| `RATIFY_OPERATION_EFFECT_BINDING`（契約 `bedf8754…`） | `verify_owner_ratification.py` → `verified=true`、`SOURCE_BOUND_OWNER_RATIFIED`、`grant_state=NOT_GRANTED` |
| `DECLARE_SLICE_REQUIRED_CASES`（2 cases / 1 FUO，綁 `PI-974a…` 與 source sha） | 已簽並以同一公鑰驗證 |

驗簽固定以 `contracts/owner-enrollment.json` 的公鑰為準（不由 sidecar 自帶 key）；`cryptography` 缺失時 fail-closed（exit 2）。

---

## R4 分析

| FirstFail | 由誰解 | 本輪狀態 | 殘餘 |
|---|---|---|---|
| F1 Windows process 層 | Host 端（MXC／提權／可核准模式） | **未解，且不必解**——改以容器 Codex host 作驗收環境 | Windows 原生 host 另記 `HOST_124_HOLD`，不是 TPM 缺陷 |
| F2 `Program Files\PowerShell\7` | Owner 提權安裝（或容器路徑使其不必要） | shell 層已證可跑；安裝後 Windows 首選路徑閉合 | 無（若採容器路徑則不阻塞） |
| F3 原 Case/Oracle 來源 | Owner 簽章宣告 slice required 集 | **已簽** | 宣告屬 `OWNER_DECLARED_SLICE_SET`，**非** source-derived original registry |

### Rejected alternatives

1. **等 Windows 沙盒修好**：無時間表，且把 TPM 資格綁在無關的主機缺陷上。
2. **用 `danger-full-access` 充受限模式**：控制方案明文禁止，且無法證明受限可用。
3. **只複製 `pwsh.exe` 單檔**：非受支援安裝；已由「完整 drop」取代並實證。
4. **在 writer 內自行驗 Ed25519**：把 crypto 依賴塞進寫入路徑、且易被自帶公鑰繞過；改用外部 pinned 驗簽工具（已實作並測試）。

### Contradiction（並存但已標註）

- Docker 子代理的結論「不構成 Windows host 的 `P0_HOST_INVOKE` 替代」與使用者主張「重點是 Codex 環境實跑」並不衝突：**兩者都對**，差別只在 claim 的 scope 標籤。採納後者作驗收，前者的限定寫進 `host_identity`。

---

## R5 挑戰（可能推翻結論的反證）

| 挑戰 | 結果 |
|---|---|
| 容器只是另一個 host，換掉就換答案？ | 是——所以驗收主張必須帶 host identity（image digest／codex 版本／plugin sha），不得宣稱 Windows 原生覆蓋 |
| 容器用 `--security-opt seccomp=unconfined` 是否使「受限」名不副實？ | **成立，且已重跑證實**：預設 seccomp 下 `codex exec -s workspace-write` 回 `bwrap: No permissions to create a new namespace … kernel.unprivileged_userns_clone`；只有放寬 seccomp（允許 userns）時子程序才建立成功。故本輪取得的是「Codex 工具鏈可跑」而非「硬化沙盒已驗」。乾淨解：在 Docker VM 內 `sysctl kernel.unprivileged_userns_clone=1`（或 `--privileged` 的等價 userns 設定），即可在預設 seccomp 下讓 bwrap 生效。 |
| Owner 宣告的 case/oracle 是否等於「原 registry」？ | 不等。它是**授權層**補齊，不是來源層考證；`QUALIFIED` 仍需真 checker |
| 簽章會不會被當成 Grant？ | 不會：簽章只覆蓋效果值集與 slice required 集；writer 不讀簽章，`grant_state` 固定 `NOT_GRANTED` |

---

## R6 合成：高信心工程裁決（建議）

**裁決 A（採納）**：把 `P0_HOST_INVOKE`、`P0_ROLLBACK` 的驗收環境定為 **Linux Codex host（容器）**，並在證據中固定 `host_identity`；Windows 原生 host 以 `HOST_124_HOLD` 另列，不作 TPM 缺陷。
信心：**高**（Installed→Loaded→Invoked/Used→Nontrigger→Rollback 全鏈有原始輸出）。

**裁決 B（採納）**：`P0_ECP_TYPED` 由設計級升為 **owner-ratified 設計級**（簽章已驗）；效果值集仍非原生 Grant。

**裁決 C（採納，附條件）**：`P0_TQAEP_FUO` 以 owner 宣告的 slice required 集成立 **DESIGN_ONLY PASS**；條件是標明 `OWNER_DECLARED_SLICE_SET`、不得轉述為 original registry、不得推導 `QUALIFIED`。

**裁決 D（保留）**：Windows 原生受限執行仍不可得；若日後要以 Windows 為正式 host，須先修 MXC 子程序建立或以可核准模式執行。

**授權與簽章建議（可直接執行）**
1. 以 `WIN-f3452453f719` 續簽（尚有 17 ops）：①本 Slice 的 `PlannedTQAEP` 綁定（已完成）；②若採納 Windows 路徑，簽 `HOST_OPERATIONS` 開窗授權（非 Grant）。
2. 簽章檔與 `owner-enrollment.json` 一併提交，驗簽工具進 CI；**不得**把私鑰、口令、`window.token` 入庫。
3. 所有證據標 `claim_ceiling`：`DESIGN_ONLY`；Native／Live Checker／Publisher 一律 `NOT_GRANTED`。

**可執行方案（順序，不新增 Gate）**
1. 以預設 seccomp 重跑容器驗收一次（補 R5 殘餘）→ 更新 `host_identity`。
2. 把 `CASE_ORACLE_DECLARATION` 與 `OWNER_RATIFICATION` sidecar 入 SBL `integrations/pipd/contracts/`，驗簽工具入 CI（缺 cryptography 時明確 SKIP 並印出）。
3. 更新 `P0_FINAL`：HOST_INVOKE／ROLLBACK／ECP_TYPED／TQAEP_FUO 四項轉 PASS（各自 claim ceiling），`PRE_V2_CLOSEOUT` 對「Linux Codex host + 設計級」範圍給 **YES**；Windows 原生 host 維持 `HOST_124_HOLD`。
4. 下游 FHS v2 主產出使用時，於 run manifest 記錄 `host_identity` 與安裝來源 SHA。

---

## R7／R8 候選與交接

- 候選：本文件 + `P0_FINAL_ADDENDUM.md` + 兩份簽章 sidecar + 容器 run 日誌（`far/container/logs/`）。
- 交接限制：不生成 `FHS_PIPD-LS-PKG_v2`；不宣稱 Native 效果、Live Checker、Publisher Release；Windows 原生 host 未證。
