# W0 結案收斂裁決（2026-11-05 run 1203）

| 項 | 裁決 |
|---|---|
| W0 | **`W0_AUTHOR_LOCAL_CLOSEOUT_ACCEPTED_WITH_SCOPED_HOLDS`** |
| W0 全量結案 | 否（`w0_full_closeout=false`） |
| 波次具名延期 | 否（`w0_wave_accepted=false` — 只有原 Program Owner 能給） |
| W1 | **`W1_AUTHOR_INTAKE_PACKAGE_COMPLETE_READER_PENDING`**，`W1_TYPED_RECEIVER_ACCEPTED=false` |
| W1 施工授權 | SOURCE_READ／SPEC／LOCAL_DRAFT_WRITE = **GO**；Canonical／Host／Permit／Merge／Release = HOLD |

## 1｜這一輪實際改了什麼

**M1（WP19 最後缺口）**：真 root（`git archive origin/main:integrations/pipd` @ `004e8891`，334 檔）修正四項後
**7 PASS / 0 FAIL、exit 0**。第四項是把 `tools/`、`scripts/` 的 import 從「runtime 依賴」判定面移出（改為
`counts.dev_only_*` 計數），因為那些模組在套件 runtime 根本不可 import，宣告成依賴也永遠不可能成立。

這一改動可被否證，不是刪檢查：
- `--strict-dev-tools` 對同一棵樹回到舊判定 → **6 PASS / 1 FAIL `UNDECLARED_DEPENDENCY`**；
- `src/` 下未宣告的 import 仍 FAIL；
- 三條測試同時釘住兩半（34/34 OK）。

四個真突變全部在自己的碼翻轉：`NOTICE_MISSING`、`SECRET_PATTERN_FOUND`、`UNDECLARED_DEPENDENCY`、
`SBOM_COMPONENT_MISMATCH`。

**M2（WP16）**：12 筆 W1 消費 Need → 1 `BOUND`、11 `PIN_HOLD`，逐筆 `blocked_operation`／`required_raw`／
`resume`，並標 `reader_disposition=NOT_OBSERVED`。Owner 階段性批准**不等於** Host/License 資格，未升 BOUND。

**M3（三庫）**：SBL #41 `a3a99b3`（本輪 +1 commit）、Fabric #27 `0a3b198`、HG-KSEOS #11 `8da3cb3` **零寫入**。
全部 open、未合併、無原域 review。合併需原 merge gate，未做。

## 2｜為什麼不是 FULL、也不是 WAVE

`W0_FULL_CLOSEOUT_ACCEPTED` 需要 WP16/19 的原 Consumer/Program Reader 真 ACK；`W0_WAVE_...DEFERRED_EFFECTS`
需要**原具權 Program/WP Owner** 的具名延期。本輪兩者都只有「請求已送出、`NOT_OBSERVED`」。
作者端測試全綠、Owner 也已接受作者端階段成果 —— 這正好對應本輪裁決的字面：`AUTHOR_LOCAL` + `SCOPED_HOLDS`。

## 3｜輸入身份（不可變前像）

W0 closeout `749208ef2df37b39…`／626 員；
W1 intake `9cbdb193f3f6ec65…`／19 員；
原 R4C `f3838fb0…`；正文 `56d0df3d…`；四實體 4/4 相符。

## 4｜HOLD

71 筆全 OPEN（前 70＋`WP16_DEFERRAL_DECISION_HOLD`）。關鍵三筆：
`WP19_ORIGINAL_RAW_ACK_HOLD`（原 SBL CI Reader）、`WP16_DEFERRAL_DECISION_HOLD`（原 Program/Technology/Host/License）、
`W1_RECEIVER_ACK_HOLD`（原 W1 Receiver）。

## 5｜未宣稱

`W0_FULL_CLOSEOUT_ACCEPTED`、`W0_WAVE_CLOSEOUT_ACCEPTED_WITH_DEFERRED_EFFECTS`、`W1_TYPED_RECEIVER_ACCEPTED`、
`WP19_DONE`、`PIPD_CANONICAL`、`HGK_ADMITTED`、`HOST_NATIVE_E2E`、`PROTECTED_CHECKER`、`RELEASED`。

本文件是作者端讀回；不是原 Reader ACK、不是 HGK Permit、不是密碼學簽章。
