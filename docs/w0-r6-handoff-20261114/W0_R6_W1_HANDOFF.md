# FHS vNEXT W0 → W1 交接（2026-11-14，round `W0_R6_W1ENTRY_20261114`）

**Domain**：`sbl_product` ／ `pipd_canonical`（依 Fabric `INTEGRATION/FHS/repository-map.json`，`FHS-NAV/v2`）
**Claim ceiling**：`SOURCE_READ + HOST_RAW(本次實測) + AUTHOR_DESIGN + LOCAL_CHECK`。**不是**原生准入、**不是**原域語義核簽、**不是** Release。
**完整交付（含全部 Raw）**：`shw097-team/HG-KSEOS` → `docs/w0-r6-20261114/`（同分支 `w0-r6-20261114`）。本檔只做 SBL 側的交接，不複製全文，避免兩份正文分歧。

---

## 1. 這一份要你（SBL 側）做什麼

| # | W1 項目 | 本回合判定 | SBL 側需要給的東西 |
|---|---|---|---|
| R2 | 首個 WorkOrder 十欄 | `READY_WITH_HOLD` | 十欄規格見 FHS 側 `docs/FHS_vNEXT_PLP_W1.md` §3；缺真 RepoContext |
| R4 | PIPD 原編譯入口接線 | `READY_WITH_HOLD` | `integrations/pipd` 為唯一 Canonical。本回合實測：CLI 恰好 13 verbs（`selfcheck` POS-03 PASS）、`compile-pi` 重現 origin fixture digest `9cc0c1b1…c1c99`（POS-04 PASS） |
| R7 | 原 Reader 對 W0 r8／vNEXT 的採納範圍 | `HOLD`（原域） | 現有 ACK 為 `subject=None/scope=None` 的 scoped 版本；需同 Subject／Scope／SourceSHA 的 scoped ACK |

## 2. 不可以由本輪代替的事

- PI／PD／ECP／TQAEP 的正式編譯（`canonical_compiler=NOT_INVOKED`；本輪未執行 SBL CLI 生產件）。
- 三份 TPM SPEC 不等於 Canonical PI：`_local/W0_SPEC/SPEC-A|B|C` 只在作者端；`spec_identity_check` 證明它們**同 Goal、四項相異**（`ok=true`），不證明語義被原 Reader 接受。
- 任何以文件完成度推導的世界效果。

## 3. 來源定位（SBL 側可自行重算）

| 對象 | 定位 |
|---|---|
| Fabric 導航入口 | `shw097-team/Fabric` → `INTEGRATION/FHS/README.md`（5463 B `3c1c2b0a…`）、`repository-map.json`（1558 B `373120f5…`）；`effect_permission=NONE` |
| 歷史 PIPD 庫 | `shw097-team/PIPD-LS-SP`：`role=HISTORICAL_CANONICAL_MOVED_TO_SBL`、`write_authority=NONE`、archived |
| W0 規格 r8 | 680998 B `42546311c3c62ae4c721403740ac675b748f3f66898157fca94c328af592ecc4` |
| 過渡基線 | 114616 B `f1ee542923e3725b8d87040a2ba63f6dc0018a5d7c945a2674d706e13ff62237` |

## 4. 兩個實測缺口（會影響 W1 排程）

1. **PLAN／VERIFY 車道在現行 assignment revision 44 下不能 served 指定模型**：`hgk-lane-dispatch.py --require-arm opencode-go/deepseek-v4.1-flash` → `ERR_ARM_NOT_IN_ASSIGNMENT`（exit 4；deepseek 在 PLAN chain rank 2、VERIFY chain rank 3）。屬原域改派，不得以 `--force-rank` 繞。
2. **HGK guard 的 epoch 欄位錯接**：`_live_epoch()` 讀 `source_of_routes` 文件的 `revision`（44）再與 registry `epoch`（41）比較 → 任何呼叫都 `ERR_LANE_STALE_EPOCH`。同一檔案同時帶 `epoch=41`／`registry_epoch=41`。

兩項都只停受影效果（受影 lane dispatch），不阻合法 READ／DRAFT。

## 5. 回退

本輪所有產物在 `FHS_NEXT_Workspace/W0_R6_W1ENTRY_20261114/`，可整目錄丟棄；未改 SBL 任何 origin bytes。
