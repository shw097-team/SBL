# KANBAN — TPM 前置修補最終驗收 r2（2026-11-03）

Run：`_run_sbl_tpm_pre_v2_final_20261103`　WIP ≤ 3
GSTACK：G1 無憑證外洩｜G2 不改 MAIN／不改寫歷史｜G3 受影寫入｜G4 真值讀回｜G5 設計級不得冒 Native

## Done
| # | 卡 | Exit 證據 |
|---|---|---|
| K-01 | 上位文件身份核對 | 控制方案 `8d0f33ad…c46b`、藍圖 `e985b885…2719` 實算相符 |
| K-02 | CT-00 漂移發現 | PIPD 已 archive；canonical writer = SBL `b7445b0` `integrations/pipd` 0.1.1a5 → `00_baseline/DRIFT_NOTE.md` |
| K-03 | 新 canonical 相容重驗 | 13 verbs／19 families／`validate --require-four` exit 0（`samples/validate_sbl_0111a5.out`） |

## Doing
| # | 卡 | 現況 |
|---|---|---|
| K-04 | CT-00 baseline（SWARM-A） | 真值讀回中 |
| K-05 | CT-01/02/04 證據對映（SWARM-B） | 跑中 |
| K-06 | GSTACK 十 P0 對抗（SWARM-C） | 跑中 |

## Blocked（需 Owner／原權威）
| # | 卡 | 阻塞原因 |
|---|---|---|
| K-07 | CT-03 typed ECP | 原 Operation/Effect Registry 不存在；需 PIPD Contract Owner＋HG-KSOS Issuer 批准 |
| K-08 | CT-05 HOST-124 修復 | 已備妥真實 `pwsh.exe` 於穩定路徑（`host/bin/pwsh.exe`），但驗證需一次 Host 模型呼叫；憑證讀取未獲同意 → 不重試、不繞道 |
| K-09 | P0_HOST_INVOKE 受限模式 | 同上；既有 Invoked/Used 證據為 `danger-full-access` 模式，不得充作受限模式資格 |

## Backlog（非本輪）
Live Checker Receipt｜Native GJ02 effect｜ChatGPT 私人 Host｜FHS v2 主產包（下一階段）
