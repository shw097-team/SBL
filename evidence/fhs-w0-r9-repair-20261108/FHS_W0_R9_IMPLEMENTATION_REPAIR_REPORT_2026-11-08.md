# FHS W0｜把 r8 的七個缺陷從「被描述」改成「被修好」

> **對象**：外部驗收官、原 Maintainer、下一個 session。
> **一句話**：`FHS_PIPD-LS-PKG_W0_r8` 是草案；這一輪把它的缺陷修進工具與產物，新增十項閘，其中 6 項在修補前的產物上會紅、10/10 在修補後轉綠，並逐項注入證明每一個都會咬。**原域 Reader 收據仍是 0。**
> **ClaimCeiling**：`W0_SEVEN_DEFECTS_REPAIRED_WITH_SCOPED_OWNER_HOLDS`。不主張 `ORIGINAL_ACK`、`NATIVE_WORLDRAW`、`RELEASE_GRANTED`、`INDEPENDENT_PASS`、已併、已審、已發行。

| 事實 | 值 |
|---|---|
| 被修對象 | `FHS_PIPD-LS-PKG_W0_r8`（草案）＋其實作回合 `FHS_W0_R6_20261108` |
| 本回合根 | `C:/Projects/Agent_Workspace/FHS_W0_R9_REPAIR_20261108` |
| 產物 | `FHS_PIPD-LS-PKG_W0_r9.md`（552,605 B，sha256 `c15693d88d034679…`），r8 逐位元保留為前綴 |
| 閘 | 繼承 16/16 ＋ 新增 10/10；對修補前 6 FAIL；注入 10/10 FIRED |
| 缺陷 | 10 項中 8 項 CLOSED、2 項 owner-scoped |
| 原域 ACK | **0** |
| 對三庫的寫入 | 0（三庫 porcelain 與 lane D 基線相同；registry 仍 rev 13） |
| Owner 簽章需求 | 0（未開窗）：31/31 列已簽、root 簽章在場 |

---

## 1｜十個缺陷：現在的狀態與依據

| ID | 修補 | 量測 | 依據檔 |
|---|---|---|---|
| `V-01` 同名 r6 兩份 | **工具化**（canonical 留 owner） | 49 個名稱、1 組歧義：`FHS_PIPD-LS-PKG_W0_r6.md` 兩份同長 [481212]、差 4 bytes、首差 offset 475677 | `out/SOURCE_COPY_REGISTER.json` |
| `V-02` 相似度上限寫錯 | **CLOSED** | `max_overall`=0.245432；舊 0.0755 重現為 0.075472（P-A / sentence_shingle_2gram），`reproduced_as_maximum`=False；負控 0.996624 | `lanes/C/DISTINCTNESS_V2.json` |
| `V-03` 17 的作用域 | **CLOSED（並細化）** | in-set 重複 0；外部：精確同名 0、剝尾碼後 17 | `lanes/A/AUTHORITY_CONFLICT_LEDGER_V2.json` |
| `V-04` 段數＝行數 | **CLOSED** | 行段 111,331／結構塊 25,201，兩規則 31/31 貼齊 | `lanes/B/U0_PARTITION_V2.json` |
| `V-05` manifest 跨 payload | **r8 已修，本輪加閘** | SBL 載荷 26/26、Fabric 1/1 皆在自身 payload 內解析 | `out/stage/**/MANIFEST.json` |
| `V-06` 授權只在根層 | **CLOSED** | SBL root=True/nested 2；Fabric root=False/nested 6；HGK root=False/nested 8 | `lanes/D/WP19_V2.json` |
| `V-07` 行數不符卻 MATCH | **CLOSED** | 31/31 bytes+lines+sha 全真；宣告 111,331＝實測 111,331；舊 split 慣例 111,362 | `lanes/A/SOURCE_LOCK_V2.json` |
| `A-01` 未宣告依賴 | **本輪推翻原敘述並修補** | `cryptography>=42` 已宣告；`fhs/issuer_binding.py` 不存在；真缺陷是 `yaml`（patch 已驗證、未套用） | `out/A01_DEPENDENCY_PATCH/RESULT.json` |
| `A-02` SEAM 少一列 | **CLOSED（機制更窄）** | naive=10／robust=11，缺 `SEAM-09`；只有把 `/` 當欄位分隔的解析器才會低估 | `lanes/E/WP21_ENUM_V2.json` |
| `A-03` 供應鏈兩半 | **CLOSED** | 離線自測 exit 0、拒絕 3 個 mutation；hosted `NOT_OBSERVED`（不假造 run id） | `lanes/D/WP19_V2.json` |

## 2｜四項「前輪寫法被本輪量測推翻」

1. **`A-01` 兩處都錯**：`pyproject.toml:6` 是 `dependencies = ["cryptography>=42"]`，不是 `[]`；附錄點名的 `src/hg_kseos/fhs/issuer_binding.py` 不存在。真正未宣告的是 `yaml`（`lane_policy.py:71`，函式內 lazy、`except` 後 `return None`）。修補：optional extra `yaml = ["PyYAML>=6"]`，套用前後 `UNDECLARED_DEPENDENCY` → `DECLARED_COVERS_IMPORTS`。
2. **`A-02` 機制更窄**：只按空白切 token 仍得 11；只有以 `/` 當欄位分隔者才丟掉 `SEAM-09`。
3. **`V-03` 的 17 依賴一條沒寫下的規則**：源檔名帶 `(1)`，精確同名比對得 0 份外部副本；剝掉尾碼才得 17。
4. **`V-06` 的嵌套數變了**：Fabric 6（前輪記 5）、HG-KSEOS 8（前輪記 0），HGK 的 8 個全在 vendored 外掛快取樹內。

## 3｜閘：繼承 16 ＋ 新增 10

| 層 | 判決 |
|---|---|
| 繼承 16 項（對 r6 回合，r9 為鏈子） | **16/16 PASS**，`G10` 對 r9 宣告的父本為 `RESOLVED` |
| 新增 10 項（對 r9 產物） | **10/10 PASS** |
| 新增 10 項對**修補前**產物 | **6 FAIL／2 PASS／2 n/a** |
| 逐項注入 | **10/10 FIRED** |
| 空回合（fail-closed） | 第一次跑在 lane 產物尚未齊備時即非零退出，不是「先綠再說」 |

| 檢查 | 修補後 | 修補前 |
|---|---|---|
| `G11 LINE_CONVENTION` | PASS | FAIL |
| `G12 SEGMENTATION_RULE` | PASS | FAIL |
| `G13 COUNT_SCOPE` | PASS | PASS |
| `G14 MAXIMUM_IS_GLOBAL` | PASS | FAIL |
| `G15 LICENCE_LAYER` | PASS | FAIL |
| `G16 DECLARED_COVERS_IMPORTS` | PASS | FAIL |
| `G17 ENUM_SLASH_SAFE` | PASS | PASS |
| `G18 DIGEST_LOCALITY` | PASS | NOT_APPLICABLE |
| `G19 COPY_REGISTER` | PASS | NOT_APPLICABLE |
| `G20 SUPPLY_CHAIN_SPLIT` | PASS | FAIL |

`G17` 在修補前是 PASS——前輪的 SEAM 數本來就對，缺的是「怎麼算出來的」可被檢驗。這一類只有注入能證明，差分證明不了。

## 4｜六個 WP 的狀態

| WP | r9 | 修了什麼 |
|---|---|---|
| `WP-FHS-00` | MEASURED_REPAIRED | verdict 現在含行數；31/31 三欄全真 |
| `WP-FHS-01` | MEASURED_REPAIRED | 雙規則分割；ACL 拆作用域 |
| `WP-FHS-15` | MEASURED_REPAIRED | 四族相似度、全域上限 0.245432 |
| `WP-FHS-16` | MEASURED_UNCHANGED | 本輪缺陷無一落在 WP16，不重跑 |
| `WP-FHS-19` | MEASURED_REPAIRED | 授權拆層、宣告 vs import、供應鏈主張拆半 |
| `WP-FHS-21` | MEASURED_REPAIRED | 15／96／12／11；12×8 完備=True |

## 5｜仍然沒有的東西（依解鎖順序）

| # | 仍缺 | 誰能做 | Resume 條件 |
|---|---|---|---|
| 1 | 任一 WP 的 `ORIGINAL_ACK` | 原域 Reader | 同 subject/scope 的 ACK 或 scoped NACK |
| 2 | registry rev 14 | OWNER | 受保護終端＋issuer 私鑰（`--max-ops 33`） |
| 3 | 兩份 r6 的 canonical 選擇（1 組） | 原 Domain Owner | 指定一個 digest |
| 4 | Fabric／HG-KSEOS 根層授權 | OWNER | 根層 LICENSE/NOTICE 存在 |
| 5 | HG-KSEOS 是否建 CI | OWNER | 有 workflow 或明示不建 |
| 6 | HG-KSEOS `yaml` optional extra | 該 repo 維護者 | 套用已驗證 patch 並重跑覆蓋檢查 |
| 7 | 15 個 PIPD contract family value-set | 原 contract Owner | 閉合落地 |

## 6｜本輪自我錯誤（全文在 `out/SELF_ERRORS.md`）

`E-R01` `--prior` 沒切模式，差分其實是同一棵樹跑兩次｜`E-R02` 閘先假設 schema，四項檢查直接拋例外｜`E-R03` 把附錄的錯誤寫進檢查器｜`E-R04` 把自家模組與 dist/import 異名判成未宣告｜`E-R05` `patch -p0` 對 `a/` 前綴找不到檔｜`E-R06` 重建文件讓 payload 過期｜`E-R07` 7 與 10 在同一句混用｜`E-R08` 位數抄對、位置卻寫成自己早先 `find` 的結果（HG-KSEOS 8 個嵌套授權檔的位置）。

最該記住的兩條：**差分測試要先證明兩邊不同**；**把別人的結論寫進檢查器，等於把那個結論升格成規則**。

## 7｜可重現指令

```bash
cd C:/Projects/Agent_Workspace/FHS_W0_R9_REPAIR_20261108

python lanes/A/tools/source_lock_v2.py            # → 31/31 bytes+lines+sha
python lanes/A/tools/authority_conflicts_v2.py    # → in-set 0 / external 依規則
python lanes/B/tools/u0_partition_v2.py && python lanes/B/tools/tile_proof.py
python lanes/C/tools/distinctness_v2.py           # → max_overall + 負控
python lanes/D/tools/wp19_v2.py                   # → 授權分層 + 依賴覆蓋 + 供應鏈兩半
python lanes/E/tools/wp21_enum_v2.py              # → 15/96/12/11 + naive vs robust
python tools/a01_dependency_patch.py              # → patch 套用等於候選

python tools/gate_w0r9.py --round .                                  # 期望 10/10 PASS exit 0
python tools/gate_w0r9.py --prior ../FHS_W0_R6_20261108              # 期望 FAIL（差異矩陣）
python tools/gate_w0r9.py --round . --selftest                       # 期望 10/10 FIRED

python tools/verify_payload_manifest.py out/stage/sbl/evidence/fhs-w0-r9-repair-20261108
python tools/verify_payload_manifest.py out/stage/fabric/INTEGRATION/FHS/docs/as-built/W0/r9

cd ../FHS_W0_R7_VERIFY_20261108
python tools/gate_w0r7.py --object-round ../FHS_W0_R6_20261108 \
  --chain-child ../FHS_W0_R9_REPAIR_20261108/writeback/W0/FHS_PIPD-LS-PKG_W0_r9.md
```

## 8｜不主張

- 不主張任何 WP 達到 `ORIGINAL_ACK`；`W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE` 仍為 `false`。
- 不主張兩份 r6 之中哪一份 canonical。
- 不主張 HG-KSEOS packaging 已修好：patch 已驗證但未套用。
- 不主張 25,201 是語意分割數；它是 `RULE_STRUCTURAL_BLOCK` 的塊數。
- 不主張前輪 24,003 錯了；那是另一條規則，差 1,198 已在 `reconciliation` 解釋。

