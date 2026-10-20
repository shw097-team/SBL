# R3 Detection List (檢測清單) — CHK00..CHK17 沿用

每列須有 `case_id, expected, actual, command, exit, denominator, raw_sha256, subject_sha, checker, scope_verdict`。
空值不得標 DONE。本輪新增受影索引不增設新制度 Gate：`AC-M4-01..06`、`AC-R2-01..05`、`AC-SP-*`、`AC-TOOLS-441`、`AC-REQ-50-149`、`AC-SURFACE-001..038`。

| CHK | 驗收焦點 | 本輪 state | 收據 |
|---|---|---|---|
| CHK00 | HGK/Hermes/Fabric 真消費、Host doctor | PARTIAL | `10_BASELINE_PREFLIGHT.json`（lane/relay/ports 實測） |
| CHK01 | 14 DOC / source hashes / 權威 / 缺件 | PARTIAL | `20_SOURCE_LEDGER.json` |
| CHK02 | G-KNOW locator / 假來源 / 否定 / NRTV / CJK | DONE（maker + 獨立 probe） | AC-M4-01..03 |
| CHK03 | 50/149、ProductKind、SPEC/ACC trace | PARTIAL | `40_REQUIREMENT_LEDGER.json` |
| CHK04 | 六模組 / 三 SP 隔離 / 無第二 plane | DONE | `tests/test_sp_isolation.py` 18 passed（gate） |
| CHK05 | GJ01 安裝 / 操作 / 重啟 / 卸載 / no residue | DONE | `60_R2_PREVIEW/AC_R2_*.json` |
| CHK06 | GJ02 writeset / HEAD / symlink / race / rollback | DONE | AC-M4-06 + `tests/e2e/test_gj02_patch.py` |
| CHK07 | GJ03 + 三 Private Plugin effective load | HOST_PENDING | `51_HOST_INSTALL_REQUEST.md` |
| CHK08 | Mode 39 cells / Shadow NoEffect / Native ACK | PARTIAL | AC-M4-04/05；39 cells 未逐一 Host 實測 |
| CHK09 | 441 donor adoption vs policy | DONE | 執行 disposition 未變更，僅 2 條 stale 更新 |
| CHK10 | PIPD 真 Writer / ONE ECP / 同主體 binding | NOT_RUN | 需 Native permit（`30_LANE_AND_REUSE.md` §PIPD） |
| CHK11 | PII/Secret/Token/symlink/junction/Injection | DONE | `secret_scan` CLEAN + 掃描收據 |
| CHK12 | Windows+Ubuntu CI / Tests / SBOM / License / Artifact | PARTIAL | CI 兩平台綠；SBOM 未產生（無 syft，具名 gap） |
| CHK13 | frozen SHA / manifest / checkpoint / replay / rollback | DONE | `80_REMOTE_READBACK.json` |
| CHK14 | GitHub public candidate+evidence / PR SHA readback | PARTIAL | evidence readback 完成；PR 待簽名 |
| CHK15 | 非 Maker M4-LITE + clean-room Challenge | PARTIAL | harness + raw receipts；**簽名缺** |
| CHK16 | Gate Calibration、holdout/負例/Regression 反平衡 | PARTIAL | `13_GATE_CALIBRATION.md` |
| CHK17 | Release packaging / uninstall / digest / HITL / SWOF handoff | PARTIAL | `60_R2_PREVIEW/`；Release 未授權 |

## 不得跨越的宣稱門檻

1. 145 / 148 passed 不能證明三 SP 已裝。
2. Python gate 綠不能證明 Native ECP / Permit / HGK effect。
3. M4-LITE harness 綠不是 `INDEPENDENT_CASE_PASS`，也不是人類簽名。
4. wheel 存在不等於 `FOUNDATION_PREVIEW_RELEASED`。
5. 441 條 disposition 完整不等於 441 項已安裝。
