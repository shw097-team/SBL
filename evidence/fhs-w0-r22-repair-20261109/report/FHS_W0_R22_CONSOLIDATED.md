# FHS W0｜r22 整合報告（給外部驗收官）

> 對象：外部驗收官、原 Maintainer、下一個 session。
> 一句話：第四次驗收的兩個阻斷缺陷已關閉，`--selftest` 在唯讀沙箱可自行重現，限定詞紀律到達機器可讀產物；
> 六份 reader 收據以 `fhs_original_reader_ack` 重簽，傳統 per-domain ACK 仍為 0/6。
> ClaimCeiling：`AUTHOR_SIDE_MEASURED`，外加一個獨立 VERIFY 車道判決（見 §6）。

| 事實 | 值 |
|---|---|
| 交付文件 | `FHS_PIPD-LS-PKG_W0_r22.md`，638,888 bytes，sha256 `c06e2b850da7e26bf2d326a7d80f3b397b40c6de1c589c82f478f55bf0f19d37` |
| 前綴 | r21（634,869 B）→ r22；r20 → r21；r13（592,369 B）仍為前綴 |
| 閘 | `tools/gate_r20.py`（GSTACK v6），21 項，0 BLOCKING FAIL，1 REPORTING OPEN（G16b） |
| 自測 | 16/16 BLOCKING FIRED；19 FIRED 總數（含 G16c/G20/G25）；G22 EXEMPT（REPORTING）；G16b BASELINE_RED（REPORTING）；`wrote_inside_round: false`、`round_tree_unchanged: true`；exit 0 |
| 標籤紀律 | 0 violations（散文 0／機器可讀 0）；4 個控制全 FIRED |
| 收據 | 6 份 reader 收據 v2 + 1 份 semantic acceptance；owner 窗口 `WIN-fc83c1d80cb6` ops 7/8 |
| 原域 ACK | 傳統 **0/6**；`FHS_ORIGINAL_ACK` 6/6（三車道 reader 角色） |

## 0.5｜r21 與 r22 的更正（先說明，免得讀者以為 §1 是全部）

r20 的驗收判決 NACK，三點：文件描述的副本機制與實作不符；`traditional` 弱標記可被肯定句利用；
`G21` 以豁免代替突變。r21 以第二十一章 append-only 更正文件，將標記分為 STRONG／WEAK 兩級
（WEAK 只在字串無肯定斷言時豁免），並讓 `G21` 以 overlay 突變交接檔的位元數宣稱。

### 0.6｜r22 追加（r21 車道的三點）

計數更正（16/16 BLOCKING，不是 19/19）；`` 經 heredoc 落檔成 U+0008，改為 ASCII 邊界字元類；
標記在字串任一處即豁免整串 → 機器路徑改子句級（散文維持行級，理由見第二十二章 §R22.3）。

## 1｜這一輪修的是什麼

### CE-07 `r19-inplace-mutation`

`gate_r19.py` 的自測把突變 bytes **寫進回合目錄**再還原（`gate_r19.py:1520-1549`）。在
`--sandbox read-only` 下第一個寫入就被拒，於是「突變會 FIRED」與「已還原」只有具寫入權的作者能主張。

r20 的機制：`mutated_bytes(path, data)` 以 in-process 的 `builtins.open` 覆寫，只改「檢查讀到的位元」，
全程不寫任何檔案；另以 `tree_fingerprint()` 對回合目錄取 `路徑|大小|mtime_ns` 的 sha256，前後相等才輸出
`round_tree_unchanged: true`。

**為什麼不是複製到 temp**：實測 `codex exec --sandbox read-only` 下 **沒有任何可用的臨時目錄**
（`tempfile` 對每個候選路徑都丟 `FileNotFoundError`）。複製方案因此不可行，in-memory overlay 是唯一能在
檢查者實際使用的沙箱裡跑起來的形式。這一點在 `out/GATE_R20_SELFTEST.json` 的 `mutation_mechanism` 欄位留痕。

**自傷紀錄**：第一次修法用 `FHS_G27_TEXT` 環境變數傳 621 KB 文件，撞上 Windows 32,767 字元上限，
自測回報 `G27 ERROR:ValueError`。改為模組層級 `_G27_TEXT_OVERRIDE` 後才 FIRED。

### CE-08 `r19-label-scope`

`label_discipline.py` v1 只掃 markdown 與 JSON 的 `label|kind|claim` 三鍵（大小寫敏感），
`body.kind = "original_reader_ack"` 與 `consequence` 散文欄位完全在視野之外。實測 **12 個站點**。

v2：走訪 `out/*.json`、`receipts/**/*.json`、`evidence/*.json` 的每個字串值；token 為
`original_(reader_)?ack`；合格前綴 `FHS_`、`BARE_`，或一條明示箭頭的改名紀錄；`not_claimed`／
`*_verbatim`／`still_open`／`non_claims` 屬否定容器或逐字引述。掃描面寫在 `out/SCAN_SCOPE.json`，
每個排除都附理由；試圖排除 `receipts/`、`out/PRINCIPAL_DEFINITION.json`、`out/FHS_ORIGINAL_ACK.json`
的 scope 會被 `SCOPE_EXCLUDES_A_MUST_SCAN_ARTEFACT` 拒絕。

## 2｜六個 W0 WP 的現狀

| WP | 主題 | 收據 | 負測 | 判定 |
|---|---|---|---|---|
| WP-FHS-00 | Source／Host Discovery | v2 已簽 | 6/6 | PASS |
| WP-FHS-01 | Requirement 對映 | v2 已簽 | 6/6 | PASS |
| WP-FHS-15 | Corpus 邊界 | v2 已簽 | 6/6 | PASS |
| WP-FHS-16 | Authority Ledger | v2 已簽 | 6/6 | PASS |
| WP-FHS-19 | Supply-chain 宣稱形狀 | v2 已簽 | 6/6 | PASS |
| WP-FHS-21 | Enum／seam 分母 | v2 已簽 | 6/6 | PASS |

`tools/verify_reader_ack.py` 每次都從 `lanes/CLAUSES.json` 的來源位元重切 span、重算 clause
digest，不做跳過；簽章先於結構驗證。

## 3｜閘 v6 的 21 項

`G10 CHAIN_INTEGRITY`、`G11 LINE_CONVENTION`、`G12 SEGMENTATION_RULE`、`G13 COUNT_SCOPE`、
`G14 MAXIMUM_IS_GLOBAL`、`G15 LICENCE_LAYER`、`G16a DEPENDENCY_TRUTHFUL`、
`G16b DEPENDENCY_CLOSED`（REPORTING／OPEN）、`G16c OPTIONAL_SEMANTICS`、`G17 ENUM_SLASH_SAFE`、
`G18 DIGEST_LOCALITY`、`G19 COPY_REGISTER`、`G20 SUPPLY_CHAIN_CLAIM_SHAPE`、
`G21 NUMBER_CONSISTENCY`、`G22 SELFTEST_CONTRACT`、`G23 TRACE_ID_NAMED`、
`G24 IDENTITY_CLAIMS`、`G25 EXTRA_QUALIFIED`、`G26 RECEIPT_BINDING`、
`G27 LABEL_DISCIPLINE`、`G28 MACHINE_READABLE_QUALIFIER`（r20 新增）。

## 4｜未完成與阻斷（具名）

| ID | 狀態 | 業主 | 說明 |
|---|---|---|---|
| `G16b` | OPEN（REPORTING） | owner（HG-KSEOS 授權） | `hgk-main` 在本機只落地釘住 commit 的三個檔案，無法宣告預設安裝覆蓋 |
| `LICENCE` | 未決 | owner | 法律行為，不是工程判斷 |
| `PIPD-15-VALUESET` | 未決 | owner | 產品語意 |
| `R1-ISSUER-REV14` | 未決 | owner（保護終端） | registry mutation，需 owner 金鑰 |
| 傳統 `ORIGINAL_ACK` | 0/6 | 各原域 reader | 本輪不主張 |
| codex pin | 過期 | owner | `config/hermes-codex-lane.json` 宣告 0.166.0-alpha.5.1，實際安裝 0.167.0-alpha.3.2；本輪以 `--codex-executable` 逐次指定，**未修改**該設定 |

## 5｜錯層稽核

| 層 | 位置 | 判定 |
|---|---|---|
| 權威層 | `SBL/main`、`Fabric/main` | 未寫入（合併待 PASS 判決） |
| 候選層 | PR #58、PR #44 | r20 全部交付物 |
| 作者工作層 | `FHS_W0_R13_ACCEPTANCE_20261108/` | 全部來源 |
| 可棄層 | `out/stage/**` | 可重建載荷副本 |

控制平面變更：**無**。

## 6｜獨立驗收

VERIFY 車道以 `codex exec --sandbox read-only -m gpt-6.1-sol` 執行，只讀候選、不修補，
判決寫在 `lanes/VERIFY_R20_VERDICT.json`；brief 與 raw 分別為 `lanes/VERIFY_R20_BRIEF.md`、
`lanes/VERIFY_R20_RAW.txt`。

## 7｜可重現指令

```text
cd C:\Projects\Agent_Workspace\FHS_W0_R13_ACCEPTANCE_20261108
python tools/gate_r20.py --round . --skip-hygiene
python tools/gate_r20.py --round . --skip-hygiene --selftest
python tools/verify_reader_ack.py
python tools/label_discipline.py --selftest
python tools/gate_r20.py --round out/stage/sbl/evidence/fhs-w0-r20-repair-20261109 --profile payload --scope payload --skip-hygiene
python tools/stage_r20.py
```
