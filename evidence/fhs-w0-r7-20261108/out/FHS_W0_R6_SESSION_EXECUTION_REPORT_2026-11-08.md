# FHS W0 r6 → r7｜執行報告（給外部驗收官）

`round: FHS-W0-R6-EXEC-20261108` ｜ `generated: 2026-11-08` ｜ `control: FHS_PIPD-LS-PKG_W0_r6（草案）`
`claim_ceiling: W0_SIX_WP_MEASURED_WITH_SCOPED_HOLDS`

---

## 0｜一句話

`FHS_PIPD-LS-PKG_W0_r6` 原本有 **3 個 WP 標 `NOT_RUN`、3 個 WP 的證據薄於各自 DonePredicate**；本次把它當草案處理，六個 WP **全部實際執行**並留下可重算 Raw。**18 個原主責 WP 的原域 Reader 收據仍然是 0**——這是權威邊界，不是進度落後，本輪沒有、也不可能改變它。

---

## 1｜六個 WP 的實測結果

| WP | DonePredicate | r6 | r7 實測 | 層級 |
|---|---|---|---|---|
| `WP-FHS-00` | SourceManifest + RepoContext | `TESTED`（L0/L1/L2 `NOT_OBSERVED`） | 31/31 源檔 bytes+lines+sha256 全等；**六份上層文件 digest 全 MATCH**；三庫 HEAD 讀回成基線 | `SOURCE_READ` |
| `WP-FHS-01` | AuthorityConflictLedger + Oracle/ProfileBinding | `NOT_RUN` | 22,281,767 bytes 切成 **111,331 段**、31/31 檔位元全覆蓋（回合層獨立檢查器複驗）；U1 子義候選 6,524／父句 6,248；U2 **84** 個 DesignID（24 `INT`＋60 `FHS-DR`）；U3 22 個 `W0_REQUIRED` 全有 CH 錨；**19/19** schema family 對到真實 schema 檔與來源 span；17 筆同名不同 digest | `SOURCE_READ` |
| `WP-FHS-15` | 三 SPEC + 來源 readback + FUO 十欄 | `NOT_RUN`（另兩份是 470／385 字元 stub） | 三份**實質相異** SPEC（9,116／9,267／9,691 B），最低欄位齊備、FUO 十欄全填、15 條驗收（6 POS／9 NEG）；**52/52** span 回切等於引文；相似度上限 0.0755（句級）／0.2134（字元 5-gram），門檻 0.85；consumer 與 NEG 集合互斥；18 條 Stage 契約 | `LOCAL_DRAFT_WRITE` |
| `WP-FHS-16` | 24 slot／25 method 壓製候選 | `NOT_RUN`（目錄空） | Donor **24/24**、Method **25/25**，零 padding；`ADOPT_CANDIDATE` 8／`DEFER` 21／`NOFIT` 1／`HOLD` **19**；13/13 驗證 | `LOCAL_DRAFT_WRITE` |
| `WP-FHS-19` | CI/License/NOTICE/SBOM Raw | `TESTED`（只憑「main CI 本來綠」） | 三庫逐庫盤點＋live CI 回讀：Fabric LICENSE/NOTICE/SBOM **全缺席**、1 個 workflow 無供應鏈 job；SBL MIT＋NOTICE＋CycloneDX 1.5（8 components 未簽章）、`supply-chain` job 在 run `42361088797` 綠；HG-KSEOS LICENSE/NOTICE 全缺席、SBOM 非標準格式、**`CI_SERVICE_ABSENT`** | `SOURCE_READ` |
| `WP-FHS-21` | 96 Cell／H4／SEAM 原 Oracle 計畫 | `TESTED`（只有一個 runner 分辨 RED/GREEN） | AC15 **15**／Oracle96 **96**（12×8 完整交叉乘積）／H4 **12**／SEAM **11**，四分母 delta 全 0；檢查器 **155/155**；負控 5 類缺陷 **5/5 被抓**；鑑別示範 POS 過／NEG 敗，含 laundering probe | `SOURCE_READ` |

**`H-W0-1` 結案**：L0/L1/L2 不是不存在，是上一輪的路徑沒找到。以 frontmatter 宣告的 digest 逐一解析，六份全 MATCH，改判 `DOC_PRESENT_DIGEST_MATCH`。這仍**不是** `SourceFreeze`，也**不是** `OWNER_CURRENTNESS_CONFIRMED`。

---

## 2｜明確不主張的事

- 任何 WP 達到 `ORIGINAL_ACK`：六個 WP 的原域 Reader 收據數 **0**。maker 的量測不是 domain acceptance。
- `W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE=true`：仍為 `false`。
- Fabric policy 生效：`FABRIC_ACTIVE_EPOCH@1` 仍無 Policy Owner 簽章。
- Issuer 恢復：registry 仍 rev 13（`3254714b…`）；rev 14 需 OWNER 在受保護終端執行。
- T2、DEV、任何世界效果：本輪世界寫入 **0**。
- 三份 SPEC 是原 PIPD schema `$id`，或已取得 Owner SourceFreeze。
- 49 個 slot 任一已被 TechnologyAdmission 核可；8 個 `ADOPT_CANDIDATE` 只是「授權已陳述、可供下游審」。
- 134 列 oracle 已被保護檢查者判定；每列狀態 `NOT_EXECUTED / RUNNER_UNBOUND`。
- **owner 金鑰**：本輪需求是量測值 **0**，未開窗、未簽任何東西（`out/OWNER_SIGNING_DEMAND_W0.json`：registry rev13、31 列全 `INSTALLED` 全已簽、root 簽章在場；沒有新增列、沒有改列、沒有改 root → ceremony 沒有東西可簽）。

---

## 3｜本輪發現的真實缺陷

| # | 缺陷 | 實測 | 誰能修 |
|---|---|---|---|
| `D-01` | 17 組同名原稿在知識庫內有多個不同 digest | 282 副本比對；`00_INDEX_AND_DECISION.md` 有 5 個 digest，僅 1 個等於 source digest | 原 Domain Owner 指名權威副本 |
| `D-02` | W0 CH-11 只宣告「18 Stage」這個數字，列舉 0 列 | 18 條契約只存在於來源 `02_…TPM(4).md` L38–55 | W0 章節 Curator／原 TPM Reader |
| `D-03` | W0 r6 完全未列舉 H4 與 SEAM | 12＋11 列僅由 `07_ACCEPTANCE_CHALLENGE(4).md` byte 201,749..210,204 支撐 | W0 章節 Curator／原 Oracle Owner |
| `D-04` | CH-24／CH-25 對 49 個 slot 只列舉 7 個具名 ID | 其餘靠 `WP16_TRANSLATION49.json` 指標 | W0 章節 Curator |
| `D-05` | 49 個 slot 中 41 個沒有任何授權陳述 | 8 個 `MIT` 來自 DOC-04 研究表，屬 `UNVERIFIED_RESEARCH_OBSERVATION` | 原 TechnologyAdmission Owner |
| `D-06` | Fabric 與 HG-KSEOS 根層沒有 LICENSE／NOTICE | Fabric 僅 5 個 vendored 深層授權；HG-KSEOS 全樹無 | OWNER |
| `D-07` | HG-KSEOS 沒有 CI | workflow 0、run 0、check-run 0 | OWNER |
| `D-08` | Fabric 唯一 CI job 不掃供應鏈 | `fhs-nav-static` 只跑 `validate_entry.py`＋unittest | Fabric 維護者 |
| `D-09` | WP-16 車道 `head` 預覽以 bytes 截斷 | 1,045 抽樣中 91 個尾端切成 U+FFFD（偏移與覆蓋仍全正確） | 已記錄，未改寫車道產物 |

---

## 4｜自我錯誤（本輪真的犯過）

| # | 錯 | 修 |
|---|---|---|
| `E-01` | 把子代理**中途摘要**當終值寫進章節（「23 條驗收」，實為 15；相似度 0.2139，實為 0.2134） | 改由建置器直讀車道最終 `REPORT.json`，並回頭修正章節。**摘要不是產物** |
| `E-02` | 我的 GSTACK 把誠實的「不宣稱」判成裸聲稱 | 擴豁免詞表；**沒有**改 SPEC 措辭迎合掃描器 |
| `E-03` | 閘只認檔名不認 SourceID，131 個 ref 一度全紅 | 由 source lock 建映射；**沒有**放寬 span 斷言 |
| `E-04` | 閘的計數對帳只認一種鍵名 | 改別名解析；仍要求表格實際列數等於宣告數 |
| `E-05` | 建置器引用不存在的 `WP00/REPORT.json` | 建置以 exit 3 失敗（正確行為），補寫產生器 |
| `E-06` | 非空轉測試期間四次改動證據檔 | 全部從 byte 備份還原，digest 恢復為 `ae17b9fa…`／`cf21cd62…`／`a823b6bc…`，閘回 15/15 |
| `E-07` | 發佈時把「位元保全」放在 repo 既有不變量之上 | SBL 的 `test_git_objects_are_lf_clean` 判紅；改以 repo 規則為準（LF＋雙 digest），Fabric 維持位元精確 |

## 5｜GSTACK 閘（新寫，且已證明會咬）

`tools/gstack_w0.py` 不信任何車道自報：自己重算 artifact digest、自己從原始 bytes 重切每個 `source_ref`、自己把宣告計數與表格列數對帳。

| 狀態 | 判決 |
|---|---|
| 空回合目錄（尚無產物） | `exit 2` `FAIL_CLOSED_PRECONDITION` |
| 真實樹 | **15/15 PASS, `exit 0`**：116 artifact 重雜湊、350 source ref 重切、0 問題 |
| 注入違規 | `exit 1`，四族同時咬住：`G2` digest 漂移、`G5b` 裸聲稱、`G6` span 不符、`G7` 計數謊報 |
| 還原後 | digest 復原、回 15/15 PASS |
| `G8` | 三庫 HEAD/dirty 對 WP-00 基線：**0 drift** |

---

## 6｜可重現指令

```bash
cd C:/Projects/Agent_Workspace/FHS_W0_R6_20261108
SRC="C:/Projects/Agent_Workspace/FHS_W1_Work_Final/FHS_W1_Work_Final/sources"
R6="C:/Projects/Agent_Workspace/FHS_W0W2_R4_20261107/writeback/W0/FHS_PIPD-LS-PKG_W0_r6.md"

# 1) 源鎖：31/31 + 六份上層文件（期望 sources 31/31 MATCH, upper 6/6）
python tools/wp00_source_lock.py --out evidence/WP00/raw/SOURCE_LOCK.json

# 2) U0 分割的獨立複驗（期望 tiles=31/31, ALL_PASS=True）
python tools/verify_u0_partition.py \
  --partition evidence/WP01/raw/U0_byte_partition.jsonl --sources "$SRC" \
  --out evidence/WP01/raw/U0_INDEPENDENT_CHECK.json

# 3) 各車道自己的驗證器（期望 52/52、13/13、155/155）
python evidence/WP15/tools/verify_spans.py
python evidence/WP16/tools/verify_projection.py
python evidence/WP21/tools/oracle_plan_check.py

# 4) 不變量閘（期望 VERDICT PASS 15/15 exit 0）
python tools/gstack_w0.py --round . --json out/GSTACK_W0.json

# 5) r7 母本保全（期望 prefix identical: True，r6 仍為 69a08e7f…）
python -c "
b6=open(r'$R6','rb').read(); b7=open('writeback/W0/FHS_PIPD-LS-PKG_W0_r7.md','rb').read()
print('prefix identical:', b7[:len(b6)]==b6, len(b6), len(b7))"

# 6) OpenSpec（期望 Change is valid）
openspec validate fhs-w0-r6-completion --strict --no-interactive
```

---

## 7｜發佈結果（已推、未併）

依 Fabric 的 FHS Engineering Entry（`FHS-NAV/v2`，`effect_permission=NONE`）分類後發佈：

| 目標 | PR | Head | 內容 | 檢查 |
|---|---|---|---|---|
| **SBL**（`sbl_product` / `pipd_canonical`，產品域） | **#50** | `934094bea8` | 67 檔：r7 本文、三份 SPEC、U0–U4 表、Donor/Method 投影、134 列 oracle 計畫、授權/SBOM/CI 盤點、source lock、gate 判決、各車層驗證器 | 4/4 綠（windows test／ubuntu test／pipd-compat／supply-chain） |
| **Fabric**（治理鏡像／FHS 入口宿主） | **#36** | `9896d7892b` | 10 檔：r7 本文＋五份 sidecar＋逐 WP 矩陣＋整合報告＋provenance，置於既有 `INTEGRATION/FHS/docs/as-built/W0/r7/` | 1/1 綠（fhs-nav-static） |

**兩個 PR 都仍是 open，未併、未取得人類審查。** 綠燈不等於驗收，這一點寫在 PR 本文的第一行。

`raw/` 的 19 MB 分割表**不進 repo**：MANIFEST 只留 digest，`tools/verify_u0_partition.py` 可重建後比對。PIPD-LS-SP 已封存，不作為路由目標。

### 7.1 發佈期間被 repo 自己的測試擋下（真實事件）

第一次推 SBL 時，我用本地 `.gitattributes * -text` 想保全 CRLF 位元。SBL 既有的
`tests/test_reproducible_build.py::test_git_objects_are_lf_clean` 立刻判紅：
**17 個 blob 含 CRLF**，並連帶讓 `test_repro_mutation_probe` 失去意義（乾淨樹自己不通過，mutation probe 就沒有立足點）。

處置：**以 repo 規則為準**——移除 `-text`、payload 正規化為 LF，並在 `MANIFEST.json` 逐檔記錄兩個 digest：

- `sha256_round`：車道量測到的位元（該 CRLF 的就是 CRLF）
- `sha256_published`：實際入庫的 LF 位元

兩者可以橋接（把回合副本以 universal newlines 正規化即可對上）。Fabric 沒有這條不變量，所以鏡像改回**位元精確**，其 sidecar 記載的 digest 與隔壁檔案一致。已驗證：正規化後 r7 的 r6 前綴仍 byte-identical。

## 8｜留給 OWNER 的具名待辦（一份，不分散）

| # | 待辦 | 為什麼只有 OWNER 能做 | 解除後解鎖 |
|---|---|---|---|
| 1 | `R1-ISSUER-REV14`：在受保護終端跑一次 `--reissue-issuer`（不加 `--rotate`／`--force-issuer-key`／`--allow-route-count-change`） | 需 issuer 私鑰，且該鍵不在本機 | registry rev14、Leaf@2、Permit POS/NEG |
| 2 | 指名 17 組同名原稿的權威副本 | 只有原 Domain Owner 能決定有效版本 | `AuthorityConflictLedger` 17 筆衝突可關 |
| 3 | 決定 Fabric 與 HG-KSEOS 的授權 | 授權是 owner 的決定，不是掃描器的結論 | 對外散佈前提；Fabric `MANIFEST.pending` 原本就列著 |
| 4 | 在 HG-KSEOS 決定是否建 CI | 同上；目前 `CI_SERVICE_ABSENT` | WP-19 在該庫才有 CI 面可讀 |
| 5 | 對三份 SPEC／49 個 slot ／134 列 oracle 出具或拒發原域收據 | 原域 Reader 的簽核不可代簽 | 這些產物才可能離開 `AUTHOR_SIDE` 層 |

一鍵開窗指令（**本輪未使用**，留給 R1）：

```bash
python C:/Projects/Agent_Workspace/HG-KSEOS/ops/session-20261031/tools/owner_window.py open \
  --task FHS-R1-REV14 --ttl-hours 2 --max-ops 33 \
  --scope registry_row_sign,merkle_root_sign --effect-ceiling REPOSITORY_WRITE \
  --workspace C:/Projects/Agent_Workspace/var/B1-PIPD-PKG-20261027
```
（`33 = 31 列 + 1 root + 1 餘裕`；開窗後 OWNER 仍須在自己的終端跑 issuer 工具。）
