# W0 結案裁決 — 2026-11-05

| 欄位 | 值 |
|---|---|
| verdict | **`W0_CLOSEOUT_PENDING`** |
| 作者端成果 | `VERIFIED_WITH_SCOPED_HOLDS`（`AUTHOR_LOCAL_TEST`） |
| 六 WP 全部 DONE | **FALSE** |
| W1 閘門 | **`W1_SCOPED_SOURCE_DRAFT_GO`**（只含 SOURCE_READ／SPEC／隔離 DRAFT） |
| 輸入 ZIP | `f3838fb095e56ea8d636e5c52f4bd69e9d529d110569b87376c168ea35ab2a2a`（原包未改） |
| 正文 | `56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a`／463,034 bytes／50 CH |
| 附錄（實測） | `ec828e3ffc88e60f8b32fbce5b1e51c3bdcf744c2d7bdd654cfb36292c867274`／7,840 bytes |

## 1｜兩個 stale SHA（C1，實檔重算）

| 檔案 | 舊值（保留為歷史） | 實測新值 | 處置 |
|---|---|---|---|
| `BODY_ANNEX_PAIR_READBACK.json` annex | `f16a572a9c67ae8e…` | `ec828e3ffc88e60f…`（bytes 同為 7,840） | `SUPERSEDED_HISTORICAL`，以 `BODY_ANNEX_PAIR_READBACK.corrected.json` 取代 |
| `ADDITIONAL_SCOPED_HOLDS_r4c.json` `candidate_body_sha256` | `ca2e65468b33acf1…` | `56d0df3db6765ee7…` | `SUPERSEDED_HISTORICAL`，以 `ADDITIONAL_SCOPED_HOLDS_r4c.corrected.json` 取代（其餘 14 筆 hold 內容逐欄不變） |

`589 files + 2 evidence + manifest self = 592` 已再次驗證，**不是缺檔**；本輪不再把它當缺陷（`MANIFEST_PAIR_CHECK.json`）。

## 2｜WP19 真 root 實跑（C2）

受測根是 `origin/main` 的 `integrations/pipd` 純上游樹（不是候選分支、也不是來源包鏡像；該樹**不含** `w0/`）：

| 項目 | 值 |
|---|---|
| 來源 | `origin/main` @ `004e88913d5c1fb57e09e8d2bf744ef1547fecbc` |
| 掃描 | 334 檔 |
| 結果 | **PASS 5／FAIL 2／HOLD 0／NOT_APPLICABLE 0**，gate exit `1` |
| FAIL 1 | `SBOM_COMPONENT_MISMATCH`：SBOM 1 個元件，manifest 宣告 6 個，5 個 declared-only（build／cryptography／pyyaml／setuptools／wheel） |
| FAIL 2 | `UNDECLARED_DEPENDENCY`：2 個模組未在任何 manifest（`hg_kseos` 在 `tools/`、`pytest` 在 `tests/`） |
| 原 CI Reader ACK | **NOT_OBSERVED** |

另有一次反向探針（`REJECTED_SUBJECT_FALSE_PASS_PROBE.json`）：把含 `w0/` fixtures 的候選 worktree 當受測樹、刪掉 root `NOTICE`，gate 仍回 `NOTICE_PRESENT`（fixture 內有 4 個 NOTICE）→ 證明該樹不能當 WP19 主體，故改用純上游樹。

**這兩個 FAIL 要拆開看，不能一律當產品缺陷：**

1. **真缺陷**：`SBOM.cdx.json` 的 `metadata.component.version = 0.1.0`，而 `pyproject.toml` 是 `0.1.1a5` → SBOM 版本漂移（`WP19_SBOM_VERSION_DRIFT`）。
2. **gate 的量測邊界**：gate 把 `[project.optional-dependencies]` 的 test extra 一併算成「declared」，因此 runtime-only 的 SBOM 看起來少了 5 個 → 這一半是 gate 語義問題，不是套件少宣告。
3. **真但已知**：`pytest` 不在 test extra（CI 另外 `pip install pytest` 並在 workflow 註解說明），屬宣告缺口（`WP19_DEPENDENCY_DECLARATION_GAP`）。
4. **設計上的外部工具**：`hg_kseos` 由 `tools/hgk_admission_driver.py` 等開發工具 import，本來就不是 pip 依賴。

因此 WP19 的狀態維持 `IMPLEMENTED_ENTRY_ONLY`，不升 `WP19_DONE`；`E26 = WP-FHS-19 → WP-FHS-14 (W4)` 保留且 `UNSATISFIED_WP19_ORIGINAL_RAW_MISSING`。

## 3｜WP16 受影選型（C3）

只針對 W1 八個主責 WP 會消費的 Need 重新讀回：

| 量測 | 值 |
|---|---|
| Need 總數 | 30 |
| W1 消費（CONSUMED） | 12 |
| 設計參考（DESIGN_ONLY） | 8 |
| 不消費 | 10 |
| `BOUND` | **1** |
| `PIN_HOLD` | 29（其中 11 筆屬 consumed） |
| NOFIT | 0 |
| 未被 W1 消費而保留 PIN_HOLD 的 remainder | 18 |
| 安裝 | **0**（`selected_not_installed=true`） |

結論：W1 可以設計與讀取，但**沒有一項 Default Need 達到「已綁版本＋License＋Windows fit＋Host＋Consumer」的完整 BOUND**；唯一 bound 的那一筆仍需原 Host Reader 背書。

## 4｜六 WP 狀態與三庫

| WP | 狀態 |
|---|---|
| WP-FHS-00／01／15／21 | `DONE_LOCAL`（沿用前輪 13／25／30／25 tests，未重跑未受影全集） |
| WP-FHS-16 | `IMPLEMENTED_WITH_SCOPED_HOLD`（1 bound／29 pin hold／0 installed） |
| WP-FHS-19 | `IMPLEMENTED_ENTRY_ONLY`（真 root 5 PASS／2 FAIL；無原 CI ACK） |

| repo | PR | HEAD | 狀態 |
|---|---|---|---|
| SBL | [#41](https://github.com/shw097-team/SBL/pull/41) | `d4b1eb789120fda3d8fbfe865ae87d3fd216438e`（本輪再追加結案讀回 commit 後另記） | open／未合併／0 review |
| Fabric | [#27](https://github.com/shw097-team/Fabric/pull/27) | `ab712e3d8f07e0beac11d783027159d6fe3ade9c`（同上） | open／未合併／0 review |
| HG-KSEOS | [#11](https://github.com/shw097-team/HG-KSEOS/pull/11) | `8da3cb3c942f38799dd481c9e784fc4c69cecb5c` | open／未合併；**本輪不追加任何遠端寫入**（`AGENTS.md` 版本差異未經原 HGK Owner 裁定） |

## 5｜HOLD

本輪結束時 **68 筆全部 OPEN**：前輪 64 筆（39 carried＋14 additional＋11 lane＋2 gate）＋本輪 4 筆：

- `WP19_ORIGINAL_RAW_ACK_HOLD`（原 SBL CI／Program Reader）
- `WP19_SBOM_VERSION_DRIFT`（原 SBL PIPD packaging owner）
- `WP19_DEPENDENCY_DECLARATION_GAP`（同上）
- `W1_AFFECTED_NATIVE_EFFECT_HOLD`（原 PIPD／Fabric Policy／HGK Issuer／Host readers）

沒有任何一筆被刪除或假結清。

## 6｜W1 GO 的範圍

**可即刻做**：八個 W1 主責 WP（02／03／04／05／07／11／17／20）的 `SOURCE_READ`、SPEC、隔離 `LOCAL_DRAFT_WRITE`、候選設計與測試；已釘 W0 candidate／SourceManifest／三 SPEC role SHA／OriginalID＋NEG。

**不可做**：canonical PI／PD、issuer permit、host install／load／invoke、repo merge、release、W18／W2–W4 的效果型驗收。

## 7｜未宣稱

`W0_ALL_SIX_WP_DONE`、`WP19_DONE`、`PIPD_CANONICAL`、`HGK_ADMITTED`、`HOST_NATIVE_E2E`、`PROTECTED_CHECKER`、`RELEASED`、超出 `AUTHOR_STATIC` 的 `TraceClosure`：全部未宣稱。本裁決是作者端讀回，不是原 Reader ACK、不是 HGK Permit、不是密碼學簽章。
