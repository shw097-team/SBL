# FHS W0｜r10 整合交付（給外部驗收官）

> **一句話**：R10 與外部挑戰兩份報告點出的**十九項**已逐項處置；三項 HIGH 的根因都是「判決與它引用的欄位無關」，
> 本回合把每一項改成可被同一支閘反向證偽的契約（12 項磁碟突變全部觸發）。**十四／十五項 PASS，一項 `OPEN` 是刻意的**：
> `G16b` 說的是世界（三棵 HG-KSEOS），不是回合。原域 Reader 收據 **0**，依賴缺口 **未修**。
>
> **ClaimCeiling**：`AUTHOR_SIDE_MEASURED_WITH_SCOPED_HOLDS`
> **不主張**：`ORIGINAL_ACK`、`NATIVE_WORLDRAW`、`INDEPENDENT_PASS`、`RELEASE_GRANTED`、已併、已審、已發行、canonical 已定。

---

## 1｜主體與可重算身份

| 事實 | 值 |
|---|---|
| 文件 | `FHS_PIPD-LS-PKG_W0_r10.md`，**567,669 B**，sha256 `b75057f7c145a8b23c7fa1f182a166b0a183283f0f81a81582b0d4856fd76adc` |
| 父本 | `FHS_PIPD-LS-PKG_W0_r9.md`，552,605 B，sha256 `c15693d88d034679740f194fa3c873f7ada13e50a2056b282e3a1cda826bce9d`，**逐位元前綴** |
| 追加章節 | 第十三章，15,064 B |
| 修訂鏈 | r5→r6→r7→r8→r9→r10，每環附 digest 與「是前一版的逐位元前綴」證明（r8 這次在鏈上） |
| 回合根 | `C:\Projects\Agent_Workspace\FHS_W0_R10_REPAIR_20261108` |
| 閘 | **14/15 PASS**，blocking fail **0**，open reporting **1**（`G16b`），hygiene **0** |
| 自我證偽 | `--selftest`：**12 FIRED**、3 具名豁免、`exit 0` |
| 錯層稽核 | CANDIDATE 206／DISPOSABLE 81／**AUTHORITY 0** → `ALL_HOLD` |
| Owner 簽章需求 | **0**（registry 未被觸碰；31 列全簽是既有狀態，不是本回合的授權） |

---

## 2｜十九項處置

### 2.1 三項 HIGH：閘說了它名字沒說的事

| ID | 病灶 | 修法 | 反向證明 |
|---|---|---|---|
| `N-02` / `EC-R9-002` 的一半 | `G13` 讀 `duplicate_digest_groups`，artifact 寫 `duplicate_sha256_groups`；`dict.get` 回 `None`，`None in (0, None)` 為真 → **死斷言** | 所有欄位走 `require()`；查不到鍵即 `FIELD_ABSENT`，且 `FIELD_ABSENT` 是 FAIL | 改**真欄位**為 4 → `IN_SET_COLLISION_PRESENT`（舊閘仍綠） |
| `N-01` / `EC-R9-002` | `G16` 的 detail 印 `False` 仍 `PASS`；並把「cryptography 已宣告」凍成規則 → 修的樹反而紅 | 拆 `G16a`（artifact 必須等於閘從樹上重算的結果）與 `G16b`（覆蓋是否完整，`REPORTING`）；公理移除 | 舊閘三情境：baseline `PASS`、加 `cryptography` → `CRYPTOGRAPHY_FALSELY_MARKED_UNDECLARED`、修好 `yaml` → `YAML_NOT_LOCATED`（**未修綠、修好紅**） |
| `N-03` | `G10` 解析到 `264787b0`（r7 的 digest），r9 自己宣告的是 `ccd545b5`；r8 根本不在鏈上 | 只讀**最後一個** `Parent／Supersedes`（＝本章自己），並要求 r5→r10 全鏈且每版是前一版逐位元前綴 | 改任一環 digest → `CHAIN_DIGEST_MISMATCH` |

### 2.2 其餘十六項

| ID | 判定 | 一句話 |
|---|---|---|
| `N-04` / `V-01` | **CLOSED**（canonical 仍 owner） | r6 **3 份 2 個 digest**：兩份位元相同（`69a08e7f…`），知識庫那份差 4 bytes @ offset 475,677 |
| `N-05` / `V-02` | **CLOSED_WITH_DRIFT** | 21 格矩陣全公布，`max_overall=0.519037`／`min=0.046948`；不再宣稱單一上限 |
| `N-06` / `V-05` | **CLOSED** | 27／26+1／34 是三個集合（gate 當時的 stage ≠ 後來的 payload），已列對帳 |
| `N-07` / `EC-R9-007` `EC-R9-008` | **CLOSED** | `G21` 驗交接 bytes 與 digest、`G22` 驗文件寫的 exit code 等於實跑 |
| `N-08` / `A-02` | **CLOSED** | 四種結構讀法並列（R1 **22,669 本工具／22,672 車道 C**／R2 25,201／R3 111,331／R4 25,198；R1 兩實作差 3 塊即規則未釘死的證據）；`word-boundary=11`、`slash-split=10`，**只有把 `/` 當欄位分隔的解析器會低估** |
| `EC-R9-001` `EC-R9-003` `EC-R9-004` | **CLOSED（量測）；修補屬 owner** | 三棵樹逐棵量，見 §3；patch 針對 GitHub main 重產並 `--dry-run` 驗證，**未套用** |
| `EC-R9-005` | **CLOSED（範圍縮小）** | `G18` 只主張「payload 內自身可解析」，不主張遠端 blob 全量重雜湊 |
| `EC-R9-006` | **CLOSED（降級）** | `G20` 更名 `SUPPLY_CHAIN_CLAIM_SHAPE`、severity `REPORTING`，自承是 lint |
| `EC-R9-009` | **CLOSED** | `A-03`（供應鏈離線／hosted 分離）在正文具名；`G23` 強制每個 CLOSED 的 ID 都出現 |
| `EC-R9-010` | **CLOSED（根因是造假）** | r9 的 `10:20` 是**釘選常數**，比 commit 晚 1h46m；本回合全部用 `datetime.now()` |
| `EC-R9-011` | **OPEN_BY_DESIGN** | 22 MB 原檔不入庫；改以 `verify_source_tree.py --sources <path>` 讓持有者自算 |
| `A-01` | **撤銷** | 跨兩棵互不為祖先的 checkout 的比較，不可比 |

---

## 3｜三棵 HG-KSEOS：同一行、三個答案

| | `HG-KSEOS@6c9fc73` | `worktrees/r4-hgk@a7046a3` | `GitHub-main@acd9196f` |
|---|---|---|---|
| `pyproject.toml:6` | `dependencies = ["cryptography>=42"]` | `dependencies = []` | `dependencies = []` |
| `issuer_binding.py` | **不存在** | 存在（193 行，L71-72 import cryptography） | 存在（193 行，L71-72） |
| 未宣告 | `['yaml']` | `['cryptography', 'yaml']` | `['cryptography', 'yaml']` |
| 模組層無保護 import | — | `user_trust.py:30-31` **cryptography** | 同左 |
| root 授權 | False | False | False |
| nested 授權 | **8**（`fhs_msc_handoff_20261030/WP-FHS-17/`，含 4 組 proprietary） | 0 | 0 |
| CI workflow | 0 | 0 | 0 |

前輪的敘述對 `6c9fc73` 成立；r9 的敘述也對 `6c9fc73` 成立，但它被寫成對「HGK」的結論；而在 `a7046a3` 與 `acd9196f` 上，**前輪逐字正確**。`G16` 就是被這個錯結論污染的。

**三棵都量、三棵都列，不挑一棵當默認**：`HGK-REF-CANONICAL` 留 owner。

---

## 4｜閘 v3 的十五項

| 檢項 | 嚴重度 | 判決 | 實測 |
|---|---|---|---|
| `G10` CHAIN_INTEGRITY | BLOCKING | **PASS** | 鏈 r5→r10；自身父本 `c15693d8` = r9；檔案內 6 個宣告，最後一個算數 |
| `G11` LINE_CONVENTION | BLOCKING | **PASS** | 31/31 bytes+lines+sha；111,331＝111,331 |
| `G12` SEGMENTATION_RULE | BLOCKING | **PASS** | per_line=111,331、structural=25,201、規則已公布 |
| `G13` COUNT_SCOPE | BLOCKING | **PASS** | `duplicate_sha256_groups=0`（鍵在）；external 0／17，分母 31／31 |
| `G14` MAXIMUM_IS_GLOBAL | BLOCKING | **PASS** | 21 格，range [0.046948, 0.519037] |
| `G15` LICENCE_LAYER | BLOCKING | **PASS** | 三主體 False/8、False/0、False/0，各附 HEAD |
| `G16a` DEPENDENCY_TRUTHFUL | BLOCKING | **PASS** | 3 主體與樹一致 |
| `G16b` DEPENDENCY_CLOSED | **REPORTING** | **OPEN** | main 與 r4-hgk 未宣告 `cryptography`；6c9fc73 未宣告 `yaml` |
| `G17` ENUM_SLASH_SAFE | BLOCKING | **PASS** | 15/96/12/11；slash=10、word-boundary=11 |
| `G18` DIGEST_LOCALITY | BLOCKING | **PASS** | 29/29 解析於自身 payload（`realpath` containment），3 份 manifest |
| `G19` COPY_REGISTER | BLOCKING | **PASS** | 45 名稱；r6 3 份於 3 個 root，2 個 digest |
| `G20` SUPPLY_CHAIN_CLAIM_SHAPE | REPORTING | **PASS** | offline=EXECUTED、hosted=NOT_OBSERVED（lint only） |
| `G21` NUMBER_CONSISTENCY | BLOCKING | **PASS** | 交接寫 567,669 B 且 digest 相符 |
| `G22` SELFTEST_CONTRACT | BLOCKING | **PASS** | 文件寫 exit 0，實跑 exit 0 |
| `G23` TRACE_ID_NAMED | BLOCKING | **PASS** | 19 項缺陷，所有 CLOSED 的 ID 都在正文 |

**嚴重度分離的理由**：`BLOCKING` 紅代表「這一回合壞了」；`REPORTING` 紅代表「世界還沒修好」。
把兩者混為一談，就會出現「十項全綠卻仍出貨」與「修好反而紅」這兩種相反的說謊方式。

---

## 5｜六個 W0 WP

| WP | 本回合 | 上限 |
|---|---|---|
| `WP-FHS-00` | 31/31 bytes、31/31 lines、31/31 sha（本回合獨立重算，非引用） | `SOURCE_READ` 完成；原域 ACK 0 |
| `WP-FHS-01` | 111,331 行段／25,201 結構塊，規則與四種讀法並列 | 語意分割未做；15 ValueSet 未閉合 |
| `WP-FHS-15` | 相似度改為區間＋21 格全矩陣 | 三 SPEC 原 Intake 0 |
| `WP-FHS-16` | **未重跑**（`MEASURED_UNCHANGED`） | 不假裝驗過 |
| `WP-FHS-19` | 依賴／授權改為逐樹量測；缺口具名 | **HOLD**：兩棵樹未宣告 `cryptography`、一棵未宣告 `yaml` |
| `WP-FHS-21` | 15/96/12/11；兩種低估解析器都公布 | 原 Oracle Runner 未綁 |

其餘 16 個 WP 主波在 W1–W4，本回合一個都沒量，也不對它們主張任何事。

---

## 6｜一份 OWNER 待辦（不逐一回頭問）

| # | 待辦 | FirstFail | 需要什麼 | Resume |
|---|---|---|---|---|
| 1 | `HGK-REF-CANONICAL` | `TWO_CHECKOUTS_DIFFER` | 三棵之中哪一棵是 W0 基準（`6c9fc73`／`a7046a3`／`acd9196f`） | 指名後重跑 `G16a/G16b` 與授權分層 |
| 2 | `HGK-DEPENDENCY-EXTRA` | `UNDECLARED_DEPENDENCY` | 在選定 HEAD 上補 `cryptography`（必要）與 `yaml`（optional） | patch 已備（兩份），套用後 `G16b` 應轉綠 |
| 3 | `AUTHORITY-COLLISIONS` | `NAME_COLLISION_DIFFERENT_DIGEST` | r6 三份的權威 digest 指定 | 指名後重跑副本登記簿 |
| 4 | `LICENCE-FABRIC-HGK` | `LICENCE_ABSENT_AT_ROOT` | 兩庫根層授權決定；`6c9fc73` 的 8 份 nested（含 4 組 proprietary）如何處置 | 根層 LICENSE/NOTICE 落地 |
| 5 | `HGK-CI-ABSENT` | `CI_SERVICE_ABSENT` | 是否建 CI | 有 workflow 或明示不建 |
| 6 | `R1-ISSUER-REV14` | `REGISTRY_REV13_NO_ISSUER_RECOVERY` | rev 14 registry＋31 列與 root 簽章 | 受保護終端開窗後執行 issuer |
| 7 | `PIPD-15-VALUESET` | `CONTRACT_FAMILY_VALUE_SET_UNCLOSED` | 15 個 family 的 value-set | 閉合且 schema 綁定 |
| 8 | `ORIGINAL-ACK-18` | `ORIGINAL_READER_ACK_UNOBSERVED` | 任一原域 Reader 的同 scope ACK/NACK | 收據落地 |

---

## 7｜自我錯誤（全文 `out/SELF_ERRORS.md`）

| # | 我做了什麼 | 抓到它的東西 |
|---|---|---|
| `E-S01` | 在修 `G13` 的同一個檔案裡造出一個 `0/0` 的假通過（class 名寫錯 → 分母 0） | 新加的「分母必須等於 31」 |
| `E-S02` | 幾乎照抄車道的靜態抽取（報「7 項讀到不存在的鍵」，實際只有 `G13` 是死的） | 把 `fired` 欄與 `key_present` 欄並讀 |
| `E-S03` | 改 selftest 時切片刪掉 `hygiene()` | 完整模式的 `NameError` |
| `E-S04` | `G10` 假設「自己的 header 在檔案開頭」，append-only 文件在結尾 | 閘自己的輸出 |
| `E-S05` | `G22` 遞迴叫自己，跑 180 秒超時 | 指令超時 |
| `E-S06` | 交接沒把 bytes 寫在檔名旁，`G21` 抓不到 | `G21` |
| `E-S07` | 把 69.5 MB tarball 留在回合目錄 | `hygiene` OVERSIZE |
| `E-S08` | 差點把一次 `FAIL` 的閘結果打包出去 | staged vs final 逐欄比對 |
| `E-S09` | 斜線解析器實作成整行切分，得到 `0`（看起來像量測） | 與 `naive=10` 對不上 |
| `E-S10` | 上一輪四個錯誤：釘選時間、交接 bytes、捏造 exit code 語意、跨樹 `A-01` | 本回合全部具名並改掉 |

最該記住的一條：**「修好會紅」比「壞了會綠」更難發現**。`G16` 的錯不是它太鬆，是它的方向反了。

---

## 8｜可重現指令（無需任何憑證）

```bash
cd C:/Projects/Agent_Workspace/FHS_W0_R10_REPAIR_20261108

python tools/dependency_subjects.py            # 三個主體的描述（不是結論）
python tools/build_r10_artifacts.py            # 從 31 冊原檔重算四個 artifact
python tools/build_r10.py                      # 產生 r10（含前綴斷言）
python tools/gate_r10.py --round .             # 15 項
python tools/gate_r10.py --round . --selftest  # 12 FIRED，exit 0
python tools/verify_payload_manifest.py        # 29/29 於自身 payload 內解析
python tools/layer_audit.py                    # AUTHORITY 0 → ALL_HOLD
python tools/verify_source_tree.py --sources <你的 31 冊路徑>   # 獨立重算
sha256sum -c out/SHA256SUMS                    # 256 檔
```

**外部能不能獨立重播，取決於你有沒有那 31 冊原檔**：有，`verify_source_tree.py` 會給你逐檔三欄；
沒有，`G11`/`G12` 只能驗到「本回合的 artifact 自洽且規則已公布」這一層，報告已如此標示。

---

## 9｜機器可讀裁決

```yaml
schema: FHS.W0.RoundVerdict/3
round: FHS_W0_R10_REPAIR_20261108
subject: {doc: FHS_PIPD-LS-PKG_W0_r10.md, bytes: 567669, sha256: b75057f7c145a8b23c7fa1f182a166b0a183283f0f81a81582b0d4856fd76adc}
parent:  {doc: FHS_PIPD-LS-PKG_W0_r9.md,  bytes: 552605, sha256: c15693d88d034679740f194fa3c873f7ada13e50a2056b282e3a1cda826bce9d, prefix_exact: true}
gate: {checks: 15, pass: 14, blocking_fail: 0, open_reporting: 1, hygiene: 0, selftest_fired: 12, selftest_exempt: 3, selftest_exit: 0}
open_findings: [DEPENDENCY_CLOSED, EC-R9-011]
original_domain_ack: 0
owner_signing_demand: 0
hgk_canonical: OWNER_UNRESOLVED
withdrawn: [A-01]
not_claimed: [ORIGINAL_ACK, NATIVE_WORLDRAW, INDEPENDENT_PASS, RELEASE_GRANTED, MERGED, REVIEWED, RELEASED]
claim_ceiling: AUTHOR_SIDE_MEASURED_WITH_SCOPED_HOLDS
```
