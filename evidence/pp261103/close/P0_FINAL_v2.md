# `P0_FINAL` v2（本輪收口後的十項裁決）

**附加檔，不覆寫** `evidence/pp261103/r3/P0_FINAL.md` 與 `far/P0_FINAL_ADDENDUM.md`；歷史 NO 與本次 YES 的差別、適用範圍見 §3。

**裁決：`PRE_V2_CLOSEOUT=YES`**（適用範圍：**已驗的 Linux Codex Host** × **`DESIGN_ONLY` 能力**）

## 1. 十項

| # | P0 | 判定 | RawRef | 本輪變動 |
|---|---|---|---|---|
| 1 | `P0_SOURCE_BASELINE` | PASS | `far/00_BASELINE.json`（95 命令）；ZIP `3a9da65…`、14 SKILL、Installed 位元組相同 | 沿用 |
| 2 | `P0_LIFECYCLE` | PASS | `test_pre_v2_planned_reader.py`、`test_claim_ceiling_shape.py`；假 grant／假收據／nested checker 拒 | 沿用 |
| 3 | `P0_PI_ID` | PASS | 原 writer PI：`REQ-1fc8f618…`、`REQ-bf8f22cb…`、`PI-974a4204962f5dc8`、ORACLE 對應 | 沿用（本輪未重產 PI） |
| 4 | `P0_PD_REALITY` | PASS（設計降級） | 真 HEAD `70757870…`、dirty 照記；`claim_ceiling=DESIGN_ONLY` | 沿用 |
| 5 | `P0_ECP_TYPED` | **PASS（受信任 CLI）** | `close/CT03_CLI_TRUSTED.md`：`load_trusted()`＋Ed25519 驗簽；6 passed（1 POS／5 NEG）；契約 `bedf8754…` | **本輪強化**：CLI 不再接受自帶 registry／自帶 SHA |
| 6 | `P0_TQAEP_FUO` | PASS（`OWNER_DECLARED_SLICE_SET`／`DESIGN_ONLY`） | `far/CASE_ORACLE_DECLARATION.slice-r3.json` ＋ owner 簽章；`RUNNER_UNBOUND` | 沿用 |
| 7 | `P0_COMPATIBILITY` | PASS | `validate --require-four` → `PASS/checked 4/complete true/exit 0`；錯 Schema→`exit 1`；13 verbs／19 families 未變 | 本輪重驗 |
| 8 | `P0_AUTHOR_TESTS` | PASS（slice） | `far/T01_T24_MAP.md`（15 重用＋5 補測）＋本輪 6 新測（CT-03） | 補 2 類安全 NEG |
| 9 | `P0_HOST_INVOKE` | PASS（linux-container） | `far/logs/step1|3`；`installed, enabled 0.3.0-rc.2`、exec exit 0、Skill 實用、Nontrigger=0 | 沿用 |
| 10 | `P0_ROLLBACK` | **PASS（真舊版閉合）** | `close/CT05_ROLLBACK.md`：rc.1（ZIP `c4181e24…`）→ `AGENT 0.3.0-rc.1` → 恢復 rc.2 → `AGENT 0.3.0-rc.2` | **本輪新證**：不再是「卸裝同版」 |

## 2. 薄治理與安全負例

`RepeatQuestions=0`、`FalseBlockCount=0`；本輪新增 `REGISTRY_NOT_CANONICAL`、`REGISTRY_SHA_MISMATCH`、`OWNER_SIGNATURE_INVALID`、`SIGNED_CONTRACT_SHA_MISMATCH`、`OWNER_RATIFICATION_REQUIRED` 五類 typed 拒收，全部 exit 2。A/B 成本仍 `AB_CAUSAL_SAVING_UNVERIFIED`（無可比 Raw，不宣稱百分比）。

## 3. 適用範圍與非主張（必讀）

| 項目 | 範圍 |
|---|---|
| Host | **僅**已驗的 Linux container Codex host（codex 0.164.0/0.166.0、image digest 已記） |
| Windows 原生 host | `HOST_124_HOLD` **仍成立**：MXC 沙盒在非互動模式下拒絕建立任何子程序 |
| Sandbox 硬化 | 容器以 `--security-opt seccomp=unconfined` 執行；**不主張**預設 seccomp 下可用 |
| 能力上限 | `claim_ceiling=DESIGN_ONLY`；`grant_state=NOT_GRANTED`；無 Native 效果、無 Live Checker、無 Publisher Release |
| 主產包 | 本輪**未**生成 `FHS_PIPD-LS-PKG_v2` |
