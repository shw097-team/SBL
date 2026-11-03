# `P0_FINAL` 追加裁決（Codex 環境實跑替代 Windows 原生 host）

**前提校正**：驗收對象是「**真 Codex 環境的實跑**」，不是「證明這台 Windows 的 Loaded/Used」。因此以 **Linux Codex host（容器）** 取得的 Installed→Loaded→Invoked/Used→Nontrigger→Rollback 全鏈，屬合法 Host 證據；Windows 原生 host 的沙盒缺陷另立 `HOST_124_HOLD`，不計為 TPM 缺陷。

## 一、四項改判

| # | P0 | 原判定 | 新判定 | 依據（原始輸出） |
|---|---|---|---|---|
| 5 | `P0_ECP_TYPED` | PASS（設計，未 ratify） | **PASS（owner-ratified 設計級）** | `verify_owner_ratification.py` → `verified=true`、`SOURCE_BOUND_OWNER_RATIFIED`、`grant_state=NOT_GRANTED` |
| 6 | `P0_TQAEP_FUO` | HOLD（無原 Case/Oracle） | **PASS（DESIGN_ONLY，`OWNER_DECLARED_SLICE_SET`）** | owner 簽章宣告 2 cases／1 FUO，綁 `PI-974a4204…` 與 source sha；`RUNNER_UNBOUND` 合法 |
| 9 | `P0_HOST_INVOKE` | HOLD | **PASS（host = linux-container）** | 容器：codex 0.166.0；`plugin add` → `installed, enabled 0.3.0-rc.2`；`plugin.json` sha `48d704bc…`（與 ZIP 同位元組）、14 SKILL；`workspace-write` 下 `exec_command` exit 0；Skill 實用產出 `/work/host_notes.md`；Nontrigger `0` |
| 10 | `P0_ROLLBACK` | HOLD | **PASS（host reload 閉合）** | `remove` → `not installed`（cache 清空）→ `add` → `installed, enabled 0.3.0-rc.2` |

`host_identity`：`linux-container / node@sha256:18a6d90fd60542269850c80ca03b29b1d9b14d6b221ac7ee8e35b0d33ef904bd / Debian 12 / kernel 6.6.87.2-microsoft-standard-WSL2 / codex-cli 0.166.0`

## 二、總裁決

| 範圍 | 裁決 | 限制 |
|---|---|---|
| **Codex 環境（Linux 容器）+ 設計級** | **`PRE_V2_CLOSEOUT=YES`** | 十項適用 P0 皆有真讀回；`claim_ceiling=DESIGN_ONLY` |
| Windows 原生 host | **`HOST_124_HOLD`** | MXC 沙盒無法建立子程序（三種模式皆 `blocked by policy`），與 TPM 無關 |
| Native 效果／Live Checker／Publisher | `NOT_GRANTED` | 未跑、未簽、未發 |

## 三、明確不主張

1. 不主張 Windows 原生 host 已能受限執行。
2. 不主張 owner 宣告的 case/oracle 等於「原 source registry」（屬授權層補齊，非來源考證）。
3. 不主張簽章＝Grant；writer 不讀簽章，`grant_state` 恆為 `NOT_GRANTED`。
4. 容器驗收的 sandbox 模式是 `SANDBOX_MODE=RUNTIME_SECCOMP_UNCONFINED`：預設 seccomp 下 `bwrap: No permissions to create a new namespace`（Docker VM 未開 `kernel.unprivileged_userns_clone`），只有放寬 seccomp 才建立子程序。因此本輪證明的是 **Codex 工具鏈與插件全鏈可跑**，不是「硬化沙盒已驗」。乾淨解：Docker VM 開 userns 後以預設 seccomp 重跑（殘餘 F-1）。
5. 不生成 `FHS_PIPD-LS-PKG_v2` 主產包。
