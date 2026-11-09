# FHS_PIPD-LS-PKG_W0 r26｜整合說明（給外部驗收官）

**主體**：`writeback/W0/FHS_PIPD-LS-PKG_W0_r26.md`，668,540 bytes，`0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f`，r25 的逐位元前綴。

## 1. 這一輪的唯一任務

OWNER 2026-11-09 裁決：`PLAN/opt2` 的 `opencode-go/mimo-v2.6-flash` 必須進 PLAN pool；`opencode-go/mimo-v2.6-pro` 是錯的模型，必須退役並防止誤用。第 26 章把它落成設定、拒絕檢查與量測。

| 項目 | 前 | 後 |
|---|---|---|
| HGK registry `epoch` | 40 | **41** |
| PLAN `arms[3]`／`fallbacks[2]`／pool `rank 4` | `opencode-go/mimo-v2.6-pro` | `opencode-go/mimo-v2.6-flash` |
| 退役帳 `retired_arms` | 無 | `opencode-go/mimo-v2.6-pro`（epoch 41、OWNER、replacement 指名） |
| `model-lane-assignment.json` | pro 在 executor 臂宇宙 | pro 移除、flash 列入，revision 43 |
| 拒絕檢查 | 無 | `scripts/lane_arm_retirement_check.py`（exit 4／5）、`fhs_3lm.py --assert-arm`（exit 9） |

## 2. 量測

```
scripts/lane_arm_retirement_check.py            retired_still_live [] / required_missing [] / PASS
scripts/hgk-lane-policy.py validate             fatal:false（僅剩既有 PROJECTION_DEBT warn）
scripts/hgk-lane-policy.py diff-live            fatal:false, 0 items
tools/fhs_3lm.py --menu                         9/9 槽全部納入
tools/fhs_3lm.py --assert-arm .../mimo-v2.6-pro exit 9 RETIRED_ARM
tools/fhs_3lm.py --bind PLAN opt2               bound, mimo-v2.6-flash, rank 4
```

## 3. 被 VERIFY 抓到的兩個真缺陷（都已修）

1. 換臂後 `lane_projections` 的 `/lane_chains/PLAN/3/model` 仍釘舊臂、`/revision` 仍釘 41 → `validate` 回
   `fatal:true`。已更新為 flash／43。
2. 第一次修補把「讀者重簽窗口」與「語義接受窗口」混為一談（r25 期間）→ r26 起分別指名。

## 4. 發布邊界（不得含糊）

| 對象 | 狀態 |
|---|---|
| HG-KSEOS 分支 `config/plan-mimo-flash-20261109` | 已推送，HEAD `86f40ec114f1` |
| HG-KSEOS `main` | `acd9196fcd74`，registry 仍 **epoch 33**，落後 in-force 血緣 **327** 個 commit；**未合併** |
| SBL／Fabric（本文件與證據） | 見 §5 |

本文件只主張「in-force 控制平面已套用且有兩道拒絕」，不主張 HGK `main` 已更新。

## 5. 閘門

```
tools/gate_r20.py --round . --json out/GATE_R26.json    # PASS 21/22, 0 blocking, G16b REPORTING OPEN, hygiene 0
tools/gate_r20.py --round . --selftest                  # exit 0, every BLOCKING check fires, tree unchanged
tools/verify_quorum.py --root .                         # 128 properties, 0 findings
tools/verify_reader_ack.py --round .                    # 6/6 receipts, quorum-aware
```

payload profile 為 16 項（含 `G29`）；與 full 的 22 項是兩個 scope，不得互相引用。

## 6. 不可主張

HGK `main` 已更新或已合併、327 個 commit 已併、`NATIVE_SIGNED`、`RELEASE_GRANTED`、外部驗收官的 PASS、
對 `mimo-v2.6-flash` 在 PLAN 車道做過 live 推論探測、`G16b` 已閉合、Fabric 政策已生效。
