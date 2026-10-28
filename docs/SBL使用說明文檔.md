# SBL 使用說明文檔

> **B1 closure 2026-10-28（本文件為本次新增）**
> 本棧在 FHS-MSC B1（PKG_00～08）的角色、驗證方式與證據位置，已整合進
> `docs/FHS-B1_使用說明文檔.md`（跨棧單一入口）。本文件只講 SBL 自己。
> claim ceiling：**SBL 在本輪是來源與語義的上游**；本包對 SBL 只做「讀取、引用、留證」，不做凍結。

## 1. SBL 是什麼／不是什麼

| 是 | 不是 |
|---|---|
| `SBL_PIPD-LS-PKG_DOC-00～13` 十四冊語義來源＋藍圖資料庫＋參考工程資料庫 | 不是可執行服務；沒有 runtime endpoint |
| B1 的**語義權威**：狀態機、角色表、R15 id 目錄（`PKG_06` 949 個 `R15-nnn`、15 個 effect family） | 不是驗收方；不簽 HGK Native Permit |
| 上游 owner 可凍結的來源（`formal_sourcefreeze`） | 不是由本包代簽的對象 |

## 2. 五分鐘上手

```bash
# 列出十四冊與藍圖／參考資料庫
ls C:/Projects/Agent_Workspace/SBL/sbl-tpm-sp-0.2.0rc1/references/corpus/sbl | head
# 狀態機與角色
grep -n "INDEPENDENT_CHECK\|RELEASE_ELIGIBLE" C:/Projects/Agent_Workspace/SBL/sbl-tpm-sp-0.2.0rc1/references/corpus/sbl/SBL_PIPD-LS-PKG_DOC-13.md | head
# R15 id 目錄（B1 的語義來源之一）
grep -c "^#### R15-" C:/Projects/Agent_Workspace/var/B1-PIPD-PKG-20261027/input_20261027/FHS_MSC_B1_PIPD_LS_PKG_06_PRODUCT_COVERAGE_AND_R15-2.md
```

## 3. B1 從 SBL 取用了什麼（可回溯）

| 取用 | 出處 | 在 B1 的落點 |
|---|---|---|
| 狀態機順序（獨立檢查在 native effect 之後、release 之前） | `DOC-13 L109` | `FAR_B1_v7`／`FAR_B1_v9` 的順序裁決 |
| G-A＋三張 GWO＋G-B 的合取定義；READY/RUNNING 非零不得 Mission Complete | `PKG_08 L45`、`L49` | `gates.py` 的 `gates_conjunction` 與 `READY_RUNNING_ZERO` |
| G-B 必須「先真 revoke，再由不同 OS PID/Session 自發續同 Subject」 | `PKG_08 L47` | G-B 證據與 `revoke_boundary`／`post_revoke_successor` runner |
| 上游來源標記 `READABLE_USER_INPUT;NOT_FORMAL_SOURCEFREEZE` | `DOC-00 L327–330` | `SOURCEFREEZE_DECLARED_HOLD`（量測 9/9 冊 `HOLD`） |
| 自舉禁改 SourceFreeze 回頭自證 | `DOC-13 L109` | 裁決「不簽 sourcefreeze」，由 owner 簽章記錄 HOLD |

## 4. SourceFreeze：現況與誰能改

```
input_20261027/FHS_MSC_B1_PIPD_LS_PKG_00…08  front matter → 9/9 冊 formal_sourcefreeze: HOLD
```

- **現況**：上游來源從未正式凍結；`DOC-00 L327–330` 也如此標記。
- **誰能改**：上游 owner（本機使用者以 SBL owner 身分）。本包不能自證，也不代簽。
- **若要凍結**：採「凍結不改正本」——逐檔 sha256 manifest ＋ owner 簽章 ＋ `SOURCEFREEZE.json`，來源 bytes 不動。
  成本：1 次解鎖、1 個簽章、0 位元組變更。
- **不要做**：不要為了讓閘門變綠而對未凍結的位元組簽一張 `source_freeze` reference；那會製造「已凍結」的假象。

## 5. 證據在哪

| 問題 | 檔案 |
|---|---|
| GWO-SBL 的 PASS 是什麼 | `artifacts/GWO_SBL_EVIDENCE.json`（`INSTALL/ADD/LIST1/REMOVE/LIST2/UNINSTALL`） |
| SourceFreeze 的裁決 | `wave1/OWNER_RULING_v1.json`（`SOURCEFREEZE_DECLARED_HOLD → ACCEPTED_AS_DECLARED_HOLD`） |
| 為何不做 30/30 effect | `FAR_B1_v9_20261028.md`（分母＝registry 列數；PKG 只要求 `INSTALLED`，30/30 已滿足） |
| 跨棧總覽 | `docs/FHS-B1_使用說明文檔.md` |

## 6. 不要再做的事

1. 不要用 SBL 文件的存在當成「已驗收」；SBL 是語義來源，判定在 HGK gates ＋ owner 裁決。
2. 不要自行改 `DOC-00～13` 的 bytes 來配合實作（改 bytes 會讓所有引用 sha 的審計與 crosswalk 失效）。
3. 不要把 949 個 `R15-nnn` 與 registry 的 30 列混為一談：兩者交集為 0，前者是語義目錄，後者是本機 runner 清單。

## 7. 名詞

| 名詞 | 意思 |
|---|---|
| `R15-nnn` | `PKG_06` 的 id 目錄項，帶 `effect family` 與 `disposition` |
| `formal_sourcefreeze` | 上游對來源位元組的正式凍結狀態（本輪 9/9 為 `HOLD`） |
| `NOT_FORMAL_SOURCEFREEZE` | `DOC-00` 對上游九冊的標記：可讀的人類輸入，非正式凍結 |
| SourceFreeze manifest | 逐檔 sha256 ＋ owner 簽章的凍結記錄（尚未產生） |

## 8. 變更記錄

| 日期 | 變更 |
|---|---|
| 2026-10-28 | 建立本文件；記錄 B1 從 SBL 取用的五項語義、SourceFreeze HOLD 的裁決與唯一合法凍結路徑 |
