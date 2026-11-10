# L6 — Fabric 治理鏡像 r26 驗收入口（EC-R26-013 / R26-09）

**Verdict: `PASS`** — 鏡像已納入 `INTEGRATION/MANIFEST.json`，digest 由鏡像檔本身重算綁定，兩個（實測四個）negative 都以具名 refusal code + 非零 exit 拒絕。

## 做了什麼

| 項目 | 結果 |
|---|---|
| 驗收入口 | `INTEGRATION/MANIFEST.json` 新增唯一一個 key `subject_admissions`，含一筆 `ADM-FABRIC-R26-FHS-W0-MIRROR-001` |
| digest | `sha256=0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f`、`bytes=668540`，以 `sha256sum` 從 `INTEGRATION/FHS/docs/as-built/W0/r26/FHS_PIPD-LS-PKG_W0_r26.md` 重算（非抄自報告） |
| 來源 | `shw097-team/SBL@1cb8abb0ef118bdd80b08961fd9ca54c657881b9`（本回合**未**連線 SBL 遠端複驗，已列入 not_claimed） |
| 狀態 | `admission_state=ADMITTED_FOR_NAVIGATION_ONLY`、`effect_permission=NONE`、`claim_ceiling=MIRROR_ADMITTED_FOR_NAVIGATION_WITH_BOUND_DIGEST_ONLY` |
| 加法性 | `git diff --numstat` = `25 insertions, 0 deletions`；逐 key 比對 `3b47550:INTEGRATION/MANIFEST.json`：18 個既有 key 全部 `SAME`、0 removed、0 changed、僅新增 1 個 key |
| 鏡像 payload | `git status --short -- INTEGRATION/FHS/docs/as-built/W0/r26/` 為空：9 個檔案、全部 pinned digest 未動 |
| 讀取器 | `INTEGRATION/FHS/tools/validate_manifest_admission.py`（stdlib、唯讀、fail-closed） |
| 測試 | `INTEGRATION/FHS/tests/test_manifest_admission.py` 21 個；全樹 `51 passed`（pytest 與 `unittest discover` 皆綠） |

## Negatives（本次執行，非引用他回合）

| id | 注入 | 預期 code | 實測 code | exit |
|---|---|---|---|---|
| `NEG-F1` | `sha256` 換成 64 個 0 | `MIRROR_DIGEST_MISMATCH` | `MIRROR_DIGEST_MISMATCH` | 2 |
| `NEG-F2` | `effect_permission: NONE -> WRITE`（`FHS-NAV/v2` 仍為 `NONE`） | `EFFECT_PERMISSION_ESCALATION` | `EFFECT_PERMISSION_ESCALATION` | 2 |
| `NEG-F3` | `claim_ceiling` 升為 `..._EXTERNALLY_ACCEPTED_AND_RELEASED`、`admission_state` 設為 `ADMITTED_FOR_CONSUMPTION`（permission 仍 `NONE`） | `ADMISSION_STATE_PERMISSION_MISMATCH` | `ADMISSION_STATE_PERMISSION_MISMATCH`、`CLAIM_CEILING_ESCALATION` | 2 |
| `NEG-F4` | 以改寫既有 top-level entry 的方式換取 admission | `ADDITIVE_ONLY_VIOLATION` | `ADDITIVE_ONLY_VIOLATION` | 2 |
| 對照 | 同一 binary 餵未竄改的 entry（`logs/05_control_admitted_entry.txt`） | `OK` | `OK` | 0 |

若沒有對照組，「拒絕」與「這個 binary 什麼都拒絕」無法區分，因此對照組與 negatives 使用同一支程式、同一條路徑。

## 兩個判斷與其理由

1. **`ADMITTED_FOR_NAVIGATION_ONLY`，不是 `ADMITTED_FOR_CONSUMPTION`。** `FHS-NAV/v2` 宣告 `effect_permission=NONE`、`source_state=PROPOSED_NOT_OWNER_RATIFIED`，本 repo 沒有任何 loader／daemon 會把 r26 當 policy 載入或供應；宣稱 consumption 沒有 artifact 支撐，且讀取器會在 permission 非 `WRITE` 時以 `ADMISSION_STATE_PERMISSION_MISMATCH` 拒絕。導覽不得被悄悄升級成寫入權。
2. **沒有改 `r26/MIRROR_STATUS.md`。** 它是 payload 的一部分，digest 被 `r26/MANIFEST.json` 與 `r26/SHA256SUMS` 兩處釘住，而 `r26/PROVENANCE.json` 宣稱「describes exactly the files beside it」；改它會破壞兩處 pinned digest，改寫它的 manifest entry 則違反本回合規則，往 `r26/` 內塞新檔又會讓那句宣稱變成假的。因此 Fabric 側狀態寫在**同層** `r26-admission/MIRROR_STATUS_FABRIC.md`，payload 保持 byte-identical。

## 沒有聲稱

未 owner-ratified、未對外 acceptance、未作為 policy 載入、無任何寫入權（`effect_permission` 維持 `NONE`）、未複驗 SBL 遠端、未聲稱 `schemas/` 內有 schema 驗證本 manifest（實測不存在，見 `logs/13_schema_search.txt`）、不聲稱「`FHS-NAV` 對所有 session 生效」。claim ceiling 為：本 repo 以已綁定 digest 接受此鏡像作為導覽來源。

## 證據

- 逐字指令、exit code、log 與其 sha256：`evidence/L6/logs/`、索引 `evidence/L6/LOGS_SHA256.txt`、機器可讀摘要 `out/L6_RESULT.json`
- 關鍵 log：`logs/01_positive_validate.txt`（`exit=0`）、`logs/02_neg_f1_digest_mismatch.txt`、`logs/03_neg_f2_effect_escalation.txt`、`logs/04_neg_f3_claim_ceiling.txt`、`logs/06_neg_f4_additive_only.txt`、`logs/14_additive_keywise.txt`、`logs/16_final_positive.txt`、`logs/17_post_commit.txt`
- commit：`985a886bd4563a75ac58bb6abf93caf03cbf6bc2`（branch `r27/r26-mirror-admission`，ahead 1，**未 push**）
