# FHS W0｜r23 整合報告（給外部驗收官）

> 對象：外部驗收官、原 Maintainer、下一個 session。
> 一句話：第四次驗收的兩個阻斷缺陷已關閉，`--selftest` 在唯讀沙箱可自行重現，限定詞紀律到達機器可讀產物；
> 六份 reader 收據以 `fhs_original_reader_ack` 重簽，傳統 per-domain ACK 仍為 0/6。
> ClaimCeiling：`AUTHOR_SIDE_MEASURED`，外加一個獨立 VERIFY 車道判決（見 §6）。

| 事實 | 值 |
|---|---|
| 交付文件 | `FHS_PIPD-LS-PKG_W0_r23.md`，644,491 bytes，sha256 `3cbcf3822d704b64874b389674a126612b2e42c37fb14b71cf0407ee755078b6` |
| 前綴 | r22（638,888 B）→ r23；r13（592,369 B）仍為前綴 |
| 閘 | `tools/gate_r20.py`（GSTACK v6），21 項，0 BLOCKING FAIL，1 REPORTING OPEN（G16b） |
| 自測 | 16/16 BLOCKING FIRED；19 FIRED 總數（含 G16c/G20/G25）；G22 EXEMPT（REPORTING）；G16b BASELINE_RED（REPORTING）；`wrote_inside_round: false`、`round_tree_unchanged: true`；exit 0 |
| 標籤紀律 | 0 violations（散文 0／機器可讀 0）；4 個控制全 FIRED |
| 收據 | 6 份 reader 收據 v2 + 1 份 semantic acceptance；owner 窗口 `WIN-fc83c1d80cb6` ops 7/8 |
| 原域 ACK | 傳統 **0/6**；`FHS_ORIGINAL_ACK` 6/6（三車道 reader 角色） |

## 0.4｜r23 的詮釋導正（本輪主題）

業主 2026-11-09 裁決：傳統 per-domain 承認不適用於 FHS，因為它預設「車道不能替 OWNER 讀」，
違反 Native E2E。第二十三章把該讀法退役，舊定義狀態改為 `NOT_APPLICABLE_BY_DESIGN (HIST-01)`，
機制寫成「三車道讀 → 互補糾錯 → VERIFY 過審 → OWNER 口令預授權 → FHS 完成簽核」，
並新增反例 `CE-09`／`CE-10`。

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

## 8｜獨立判決與發布（本回合最終狀態）

| 項 | 值 |
|---|---|
| VERIFY 車道 | `openai-codex/gpt-6.1-sol`，`codex exec --sandbox read-only`，6/6 指令實跑 |
| 判決 | **PASS**（`lanes/VERIFY_R22_VERDICT.json`） |
| BLOCKING | 16/16 FIRED；`G22` REPORTING EXEMPT；`G16b` REPORTING BASELINE_RED |
| 回合樹 | 檢查者獨立快照 1,039 檔前後一致；`wrote_inside_round: false` |
| 反例 | 「Traditional per-domain ORIGINAL_ACK was obtained.」與「… 6/6 …; examples follow.」兩者皆被拒絕 |
| SBL | PR #58 合併，merge commit `c40256362f4f`；CI 五項全綠（含 `gate`，payload scope） |
| Fabric | PR #44 合併，merge commit `e6bb48bd705b`；`fhs-nav-static` 綠；未登記 `INTEGRATION/MANIFEST.json` |

### 這一輪不能主張什麼

- 傳統 per-domain `ORIGINAL_ACK`：**0/6**。`FHS_ORIGINAL_ACK 6/6` 是三車道 reader 角色的合規標籤，
  與傳統標籤不互換（文件第十七章）。
- OS 帳號或人身層級的身分分離：三條車道在同一個 Windows 帳號下，只有 process／model／evidence-path 分離。
- `G16b` 已閉合：`hgk-main` 在本機只落地釘住 commit 的三個檔案。
- Fabric 政策層已載入或供應此鏡像；`INTEGRATION/MANIFEST.json` 未被修改。
- `NATIVE_SIGNED`、`RELEASE_GRANTED`：未主張。
- 合併是倉庫狀態變更，不是外部驗收。

### 我這一輪犯的錯（全部已修並留痕）

1. `FHS_G27_TEXT` 用環境變數傳 621 KB 文件，撞 Windows 32,767 上限 → 改模組層級覆寫。
2. 把「副本到 temp」寫進第二十章，實測唯讀沙箱沒有可寫 temp → 改 in-process overlay，第二十一章更正。
3. `traditional` 當成負面標記，肯定句可通過 → 強弱標記分級。
4. `` 經 shell heredoc 落檔成 U+0008 → 改 ASCII 邊界字元類（第二十二章）。
5. 標記在字串任一處即豁免整串 → 機器路徑改子句級（第二十二章）。
6. BLOCKING 計數說成 19/19（實為 16/16）→ 第二十二章更正。
7. CI 首次紅燈：workflow YAML 的 step 名稱含冒號（零 job）；修好後又以 round scope 跑 payload → 改 `--scope payload`。

