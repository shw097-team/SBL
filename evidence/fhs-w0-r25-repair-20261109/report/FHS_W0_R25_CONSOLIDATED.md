# FHS_PIPD-LS-PKG_W0 r25｜整合說明（給外部驗收官）

**主體**：`writeback/W0/FHS_PIPD-LS-PKG_W0_r25.md`，663,601 bytes，
`9b35b6ee6a850afd6cabde3ea9d7ec3b117d95b47379efcb7c4edfac9d2e0829`，r24 的逐位元前綴。
**這一輪的性質**：針對 `FHS_W0_r24_External_Challenge_PostRepair_Acceptance_Report_2026-11-09`
（`review_verdict: FAIL`）的受界修補，不是重做整套 W0。

## 1. 外部判決與本輪處置

| ID | 級別 | 外部觀測 | 本輪處置 | 位置 |
|---|---|---|---|---|
| `EC-R24-001` | CRITICAL | 128 個保留判斷中 2 筆 `DECIDED` 只有 1 張同意票 | 兩條條款由 PLAN／VERIFY 各重讀一次，2/2 同意，兩份 envelope 重簽（ops 3、4；ops 1、2 已被取代） | `lanes/votes/`、`out/QUORUM_REPAIR_R25.json` |
| `EC-R24-002` | HIGH | 驗證器只查 `value` 是否布林 | `tools/verify_quorum.py` + gate `G29`（BLOCKING、突變必 FIRED） | `tools/verify_quorum.py`、`out/GATE_R25_SELFTEST.json` |
| `EC-R24-003` | HIGH | 簽 r15／綁 r20／語義 r21／交付 r24，角色未命名 | `subject_scope` 四欄分離 + `unaffected_proof` | `out/FHS_ORIGINAL_ACK.json` |
| `EC-R24-004` | MAJOR | ack 的 `document.path` 指 r20 | 改為由一次讀取產生的 r25 物件，r20 進 history | 同上 |
| `EC-R24-005` | MAJOR | payload 15/15 與 full 20/21 混用 | `out/EVIDENCE_SCOPE.json` 明確邊界 | 同左 |
| `EC-R24-006` | MAJOR | 無法在無秘密條件下檢查時序 | 公開驗證束（公鑰、enrollment 摘要、三段時序） | `out/PUBLIC_VERIFICATION_BUNDLE.json` |
| `EC-R24-007` | MAJOR | HGK `dependencies=[]`、root license 0 | `OPEN_SCOPED`：只封 HGK Host/Issuer 效果 | 第 25 章 §25.8 |
| `EC-R24-008` | MAJOR | Fabric mirror 已併、`INTEGRATION/MANIFEST.json` 未納管 | 只主張 `MIRROR_MERGED`，不主張政策生效 | 同左 |
| `EC-R24-009` | OPEN_EXTERNAL | U0–U4、96 Oracle、Native 未證 | W1–W4 範圍，不在 W0 作全球阻斷 | 同左 |

## 2. 六個 W0 主責 WP 現狀

| WP | 本輪狀態 | 依據 |
|---|---|---|
| `WP-FHS-00` Source/Host Discovery | 受影條款 `L1:817 exceptions_preserved` 重讀 2/2 同意、重簽 | `receipts/reader/WP-FHS-00.signed.json`、`lanes/votes/` |
| `WP-FHS-01` Requirement/U0–U4 | 受影條款 `L1:812 scope_preserved` 重讀 2/2 同意、重簽 | `receipts/reader/WP-FHS-01.signed.json` |
| `WP-FHS-15` Product/Architecture/Program SPEC | 收據位元組不變、28 個未受影屬性重掃通過 | `out/QUORUM_REPAIR_R25.json` |
| `WP-FHS-16` Capability/Authority Slots | 同上；HostFit 仍為 W1 範圍 | 同左 |
| `WP-FHS-19` SupplyChain | 同上；`G16b` 仍 `REPORTING OPEN` | `out/GATE_R25.json` |
| `WP-FHS-21` Oracle/SEAM | 同上；96 Oracle 仍為規劃狀態 | 同左 |

## 3. 閘門實測

```
python tools/gate_r20.py --round . --json out/GATE_R25.json     # PASS 21/22, 0 blocking, G16b REPORTING OPEN, hygiene 0
python tools/gate_r20.py --round . --selftest                    # exit 0, 17 BLOCKING FIRED, tree unchanged
python tools/verify_quorum.py --selftest                         # 7 cases, exit 0
python tools/verify_quorum.py --root .                           # 128 properties, 0 findings
python tools/verify_reader_ack.py --round .                      # 6/6 receipts, quorum-aware
```

CI 只跑 `payload` profile（16 項，含 `G29`）；full profile 的 22 項不得與 CI 的 15 項互相引用。

## 4. 自我錯誤（本輪實際踩到並修掉的）

1. `G21` 首輪 `CLAIM_NOT_FOUND`：handover 把 bytes 與 sha 分兩行，正則跨不了換行 → 併成一行。
2. `G22` 連帶 `SELFTEST_EXIT_DOCUMENTED_WRONG`：因 `G21` baseline 紅，兩列 `BASELINE_RED` 未 FIRED → 修 `G21` 後消失。
3. hygiene `count=1`：豁免仍被計為失敗 → 改為 `EXEMPT_WITH_REASON` + `counts_as_clean`，並在報告中列出豁免與理由（不隱藏）。
4. `VERDICT FAIL` 但 `hygiene=0`：verdict 與 exit code 仍用未過濾的 `hy` → 一併改用過濾後清單。
5. `patch` 以 `\n` 比對 CRLF 檔失敗 → 改以 `newline=""` 讀寫。

## 5. FHS-3L&M（車道／模型硬入口）

`tools/fhs_3lm.py` 讀 HG-KSEOS 既有 pool 與 registry（唯讀），提供 `--menu` / `--bind` / `--assert`。
實測：PLAN `primary`＝`gpt-6.1-sol`、`opt1`＝`deepseek-v4.1-flash` 可用；`opt2`＝`mimo-v2.6-flash` **不在 PLAN pool**，
`--bind PLAN opt2` 以 `NOT_IN_LANE_POOL` 拒絕（`--allow-fallback` 可退到 `primary` 並記錄）。
EXECUTE／VERIFY 三槽全部可用。不強制 SoD；同 arm 跨車道只記錄不拒絕。
session pin 與車道綁定是兩個平面：`--bind` 寫控制平面綁定（含 epoch、pool 摘要），`--assert` 只讀綁定檔。

## 6. 不可主張

`NATIVE_SIGNED`、`RELEASE_GRANTED`、外部驗收官的 PASS、三個互異模型或 OS 帳號隔離、`G16b` 已閉合、
Fabric 政策已生效、HGK 依賴與授權已解、U0–U4 或 96 Oracle 已 Native 執行。
