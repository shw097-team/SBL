# R4 檢測清單（CHK00–CHK17 + 本輪特殊驗收）

每個 case 必回填：`case_id, subject_sha, expected, actual, command, exit, denominator, raw_log_sha256, verdict, first_fail`。
**打勾不算通過**；沒有 exit code 與分母的列一律 `NOT_RUN`。

| Check | 本輪必要檢測 / 負例 | 狀態 |
|---|---|---|
| CHK00 | HGK doctor、Hermes pinned binding、錯誤 Host / 無 Permit 拒絕 | PARTIAL（lane 埠實測；F0 trace 未取得） |
| CHK01 | 14 DOC hash 聚合 `754cf7be…` 與 SBL `SOURCE_VERIFY.json` 一致；KP/vols 同版本 | PARTIAL（本機無 KP/vols 原文） |
| CHK02 | 假 DOC-27、SEP 變形、Source-BIND、NRTV、CJK/Path 拒絕 | NOT_RUN（沿用 R3 `GKNOW-*`，本輪未重跑） |
| CHK03 | 50/149、8 Kind、38 surfaces 每 ID selected/defer | DEFERRED（R4 非阻斷） |
| CHK04 | 六模組／三 principal 隔離；無第二控制平面；Challenge 無寫權 | ACTIVE |
| CHK05 | Foundation `sbl-todo` FUO 回讀（保留舊證據）；SBL Stack install/action/uninstall | ACTIVE |
| CHK06 | GJ02 WriteSet/HEAD/link/TOCTOU/invalid effect/rollback | PARTIAL（沿用 v13 測試） |
| CHK07 | **三 SP 各自 plugin schema / identity / host installed ID / effective-load / POS / NEG / uninstall** | ACTIVE（本輪主測） |
| CHK08 | 五工具各自 install→discover→load→call→deny→rollback→uninstall | ACTIVE |
| CHK09 | 441 行 ID + SOURCE/EXECUTION/SELECTED + prohibited 不誤裝 | DEFERRED |
| CHK10 | PIPD 真 writer 產物、無權 issuer/空 atom 拒絕 | NOT_RUN（無原生收據） |
| CHK11 | Secret/PII/token mask、path traversal/reparse/symlink、injection、challenge read-only | ACTIVE（secret_scan + 打包路徑檢查） |
| CHK12 | CI ubuntu/windows SHA、schema、test denominator、package digest/source/license | ACTIVE |
| CHK13 | candidate/evidence/hash/manifest/trace/replay/rollback/currentness | ACTIVE |
| CHK14 | push 後 remote candidate/evidence PR/base/head SHA 讀回 | ACTIVE |
| CHK15 | 主體只讀獨立 checker、Host true qualification；owner 自審不冒稱獨立 | PARTIAL（本輪無獨立車道） |
| CHK16 | gate strictness、holdout、FP/FN、adversarial、baseline、HITL | PARTIAL |
| CHK17 | SWOF W2 shadow handoff source/evidence/checksums；W3 永 NO_EFFECT | ACTIVE |

## 本輪特殊驗收（R4 新增，機器化）

| ID | 驗收 | 通過條件 |
|---|---|---|
| `AC-R4-SCHEMA-01` | 三包 root `plugin.json` 通過 vendored portable schema **嚴格**驗證 | 3/3，且 `$schema` 值等於 canonical 常數 |
| `AC-R4-SCHEMA-02` | 驗證器**非 vacuous**：注入 4 類負例全部被拒 | 4/4 被拒（缺 `$schema`、多餘頂層鍵、`name` 違 pattern、`extensions` 值非物件） |
| `AC-R4-SCHEMA-03` | 三份 `skills/<name>/SKILL.md` frontmatter 正規且 `name` 等於目錄名 | 3/3 |
| `AC-R4-IDENTITY-01` | 三包 identity 不可互換（name/sp_id/role 兩兩不同） | 3 對比較全不同 |
| `AC-R4-REPRO-01` | 三包 byte 可重現（兩次建置到不同目錄，digest 相同） | 3/3 |
| `AC-R4-TOOLS5-01` | 五行矩陣每行有 package digest + install 命令 + 真 exit | 5/5 有原始收據；Host 欄可為 `HOST_PENDING` |
| `AC-R4-TOOLS5-02` | 五工具**各自單獨**安裝成功（不得以組合成功掩蓋單體失敗） | 5/5 單體 |
| `AC-R4-TOOLS5-03` | 每工具都有 unauthorized NEG（拒絕而非默默通過） | 5/5 |
| `AC-R4-SWOF-01` | handoff 的 6 個 SHA 等於今日 live readback | 6/6 |
| `AC-R4-SWOF-02` | handoff `forbidden` 含 `WORLD_EFFECT` / `W3_AUTO_ADMISSION`；SBL 未寫 SWOF | 2/2 |

## 分母宣告（防混用）

- 單元測試分母以 CI 兩平台各自 `passed, skipped` 分別記錄，**不加總**。
- `39` = 3 mode × 13 gate **設計格**，不是 39 次 host 驗收。
- `441` = DOC-06 供體條目，不是 441 個安裝目標。
- `50/149` = 需求父/子，`38` = delivery surfaces；本輪皆 `DEFERRED`，不計入完成率。
