# FHS W0｜r6 草案本地實作的獨立驗證、實跑、檢測與驗收（2026-11-08）

> **對象**：外部驗收官、原 Maintainer、下一個 session。
> **這份文件的一句話**：六個 W0 工作包的頭條數字全部重現；過程中量到七個文件層缺陷，其中一個是「15 項閘全綠卻仍出貨」的閘缺口，已補成 16 項並在 r8 上轉綠；**原域 Reader 收據仍是 0**。
> **ClaimCeiling**：`AUTHOR_SIDE_MEASURED_WITH_SCOPED_HOLDS`。不主張 `ORIGINAL_ACK`、`NATIVE_WORLDRAW`、`RELEASE_GRANTED`、`INDEPENDENT_PASS`、已併、已審、已發行。

| 事實 | 值 |
|---|---|
| 被驗對象 | `FHS_PIPD-LS-PKG_W0_r6`（草案）＋其實作回合 `FHS_W0_R6_20261108` |
| 本回合根 | `C:\Projects\Agent_Workspace\FHS_W0_R7_VERIFY_20261108` |
| 本回合產物 | `FHS_PIPD-LS-PKG_W0_r8.md`（539,712 B，sha256 `ccd545b5…`），r7 逐位元保留為前綴 |
| 閘 | 16/16 PASS（r8）；同一支閘對 r7 為 15/16 FAIL（`G10` 紅） |
| 新增閘檢項 | `G10-DOC-PARENT-CLAIM` |
| 原域 ACK | **0** |
| 對三庫的寫入 | 0（`G8` 以 WP-00 基線比對，0 drift） |
| Owner 簽章需求 | 0（未開窗）；5 項具名待辦合併為 1 份 |

---

## 1｜六個 W0 工作包的逐項結果

| WP | 頭條宣稱 | 獨立重測 | 判決 |
|---|---|---|---|
| `WP-FHS-00` | 31/31 源檔 bytes+lines+sha256；上層 6 份；三庫 HEAD | 31/31 bytes 與 sha 相符；上層 6/6；三庫 0 drift；回合 `SHA256SUMS` 162/162 通過 | **REPRODUCED**（行數慣例見 V-07） |
| `WP-FHS-01` | 111,331 段／22,281,767 B；84 DesignID；22 `W0_REQUIRED`；19 schema；17 同名 | 22,281,767 B 全覆蓋；84（24 INT＋60 DR）；22；19；**集內同名碰撞 0** | **REPRODUCED_WITH_DEFINITION_DRIFT**（V-03／V-04） |
| `WP-FHS-15` | 3 份相異 SPEC；52/52 span；15 ACC（6/9）；18 Stage | 3 份相異；52/52 EXACT；15（6 POS／9 NEG）；18 | **REPRODUCED**（V-02） |
| `WP-FHS-16` | 24 donor／25 method；8/21/1/19；8/49 具名授權 | 24/25；8/21/1/19（合計 49）；8/49；49/49 座標 EXACT | **REPRODUCED** |
| `WP-FHS-19` | 三庫授權／NOTICE／SBOM／依賴／CI，3 處缺席 | SBL 齊備；Fabric 根層缺、深度 5 個；HG-KSEOS 全無 CI | **REPRODUCED**（V-06） |
| `WP-FHS-21` | AC15 15／Oracle96 96／H4 12／SEAM 11；155/155；5/5 | 全部重現；96 = 12×8 完備、0 缺格 | **REPRODUCED** |

母代理另行獨立算出的四個數字：`AC-C39-*` 96、類別 12、型別 8；L1 卡 24＋60；`W0_REQUIRED` 22／`W1-W4_HANDOFF` 62；回合 digest 162/162。

## 2｜七個缺陷（這是本輪的主要產出）

| ID | 一句話 | 量測 | 處置 |
|---|---|---|---|
| `V-01` | 同名 r6 有**兩份**，同長度、差 4 bytes（附錄時間戳） | `9f9eb261…`（知識庫路徑）vs `69a08e7f…`（回合 writeback）；皆 481,212 B | r8 列舉兩份；canonical 由 Owner 決定 |
| `V-02` | 「相似度上限 0.0755」既非上限也未重現 | 前輪自身 `max` 欄 0.2134；本輪六族上限 0.2063，0.0755 未重現 | r8 改為分方法並列 |
| `V-03` | 「17 筆同名不同 digest」作用域寫錯 | 31 源集內 0 組碰撞；真相是 17 個源檔在 KB 他處有 digest 相異的同名副本 | r8 改寫 |
| `V-04` | 「111,331 段」= 行數，非語意區塊 | per-line 111,331；block 規則 24,003；bytes 相同 | 標為規則相依 |
| `V-05` | 發佈 manifest 有 11 筆 digest 不指向它所指的 bytes | SBL manifest 82 筆中 71 在 payload 內對帳，11 筆描述 Fabric 鏡像檔（r7 文件 492,208 LF vs 492,290 原樣） | r8 出版改為「**每個 digest 只在它所在的 payload 內宣告**」 |
| `V-06` | 「Fabric／HG-KSEOS 無授權檔」只在根層成立 | Fabric 根層 0、深度 5（含 2 個 vendored MIT） | r8 限定為「根層」 |
| `V-07` | WP00 lock 自量 31/31 行數不符、判決仍寫 MATCH | lock 的 `observed.lines` 每檔多 1（合計 111,362）；宣告值＝`wc -l`＝111,331 | 本章把相符限定為 bytes＋sha |

## 3｜閘：15 → 16，並證明會咬

| 情境 | 判決 |
|---|---|
| 繼承 15 項對 r6 回合 | 15/15 PASS（116 artifact 重雜湊、350 span 重切） |
| 注入 byte／prose／span 三層違規 | 12/15，紅在 `G2`／`G5b`／`G6`，`caught_extra`＝0 |
| 繼承 15 項對 r7 文件 | 全綠 ← **這就是缺口** |
| 新增 `G10` 對 r7 | **FAIL（`COPY_AMBIGUITY`）** |
| 新增 `G10` 對 r8 | **PASS（`RESOLVED`）** |

## 4｜仍然沒有的事（依解鎖順序）

| # | 仍缺 | 誰能做 |
|---|---|---|
| 1 | 任一 WP 的 `ORIGINAL_ACK` | 原 SBL／Fabric／HGK Domain Reader |
| 2 | registry rev14（Issuer 復原） | OWNER（受保護終端＋issuer 私鑰） |
| 3 | 17 個源檔同名副本的權威選擇（含 `V-01` 兩份 r6） | 原 Domain Owner |
| 4 | Fabric／HG-KSEOS 的授權決定 | OWNER |
| 5 | HG-KSEOS 是否建 CI | OWNER |
| 6 | 15 個 PIPD contract family 的 value-set 閉合 | 原 PIPD contract Owner |
| 7 | Fabric policy 生效／T2／任何世界效果 | 依原序列 |

以上合併為 1 份具名待辦：`out/OWNER_SIGNING_DEMAND_W0R7.json`（5 項，各帶 FirstFail／RequiredRaw／ResumePredicate）。

## 5｜本輪自我錯誤（全在 `out/SELF_ERRORS.md`）

`E-01` 把 `COPY_AMBIGUITY` 誤判成 `UNRESOLVED`｜`E-02` 鏈解析器錨在標籤而非父本檔名｜`E-03` 閘以代號比對檔名｜`E-04` 雙 digest 量錯方向（34 筆假不符）｜`E-05` `V-02` 第一版寫得太輕｜`E-06` 曾把車道自報當完成。
最該記住的兩條：**一個 digest 不解析，先找同名副本**；**車道摘要不是產物，只有落地欄位與自己重算的數字能進章節**。

## 6｜可重現指令（外部驗收官可直接跑）

```bash
cd C:/Projects/Agent_Workspace/FHS_W0_R7_VERIFY_20261108

# 1 繼承閘（對被驗回合）
python tools/gate_w0r7.py --object-round C:/Projects/Agent_Workspace/FHS_W0_R6_20261108 \
  --chain-child writeback/W0/FHS_PIPD-LS-PKG_W0_r8.md --json out/GATE_R8_OBJECT.json
#   期望 VERDICT PASS pass=16 fail=0 exit=0

# 2 負控（三層注入，應紅在 G2/G5b/G6）
python tools/gate_negative_control.py

# 3 修訂鏈（r5→r6→r7→r8）
python tools/verify_revision_chain2.py out/REVISION_CHAIN.json

# 4 重建 r8（前綴必須逐位元等於 r7，否則拒絕寫入）
python tools/build_w0_r8.py

# 5 逐 WP 對帳與發佈更正
python tools/build_matrix.py

# 6 OpenSpec
openspec validate fhs-w0-r7-verification --strict --no-interactive
```

## 7｜一句話收束

這一輪把「前次說六個 WP 都做完了」變成「六個 WP 的數字可在另一個 process 重算，且七個說錯的地方各有名字與處置」；但 **18 個原域 ACK 仍是 0**，因為剩下的每一步都需要別人的私鑰、簽章或權威決定。這不是進度落後，是權威邊界。
