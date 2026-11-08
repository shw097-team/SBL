# FHS W0｜r10 修補回合：讓判決等於它名字說的事

> **對象**：外部驗收官、原 Maintainer、下一個 session。
> **這份文件的一句話**：r9 的閘有三項判決「說的不是它名字說的事」——本回合把它們換成可被同一支閘反向證偽的契約，12 項突變全部觸發、2 項具名豁免；同時撤銷上一輪 `A-01` 的判定，因為那是跨兩棵樹的比較。**原域 Reader 收據仍是 0，依賴缺口仍未修。**
> **ClaimCeiling**：`AUTHOR_SIDE_MEASURED_WITH_SCOPED_HOLDS`。不主張 `ORIGINAL_ACK`、`NATIVE_WORLDRAW`、`INDEPENDENT_PASS`、`RELEASE_GRANTED`、已併、已審、已發行。

| 事實 | 值 |
|---|---|
| 被修對象 | `FHS_PIPD-LS-PKG_W0_r9`（552,605 B，sha256 `c15693d8…`）＋其實作回合 `FHS_W0_R9_REPAIR_20261108` |
| 本回合產物 | `FHS_PIPD-LS-PKG_W0_r10.md`（**568,120 B**，sha256 `2285baaf37884399d85d114672a2a4ca155420af184e5c473d18b0d7a32f1859`） |
| 追加章節 | 第十三章，15,515 B；r9 逐位元為前綴（builder 寫入前後各斷言一次，`G10` 再驗一次） |
| 閘 | **14/15 PASS**，blocking fail **0**，open reporting **1** |
| 閘的自我證偽 | selftest：**12 FIRED**、豁免 2（G21, G22） |
| 原域 ACK | **0** |
| Owner 簽章需求 | 0（未開窗；registry 未被觸碰，`32.5k` 列全簽仍成立但不構成本回合的授權） |

---

## 1｜三個閘缺陷：同一個病

外部驗收（R10）把它們列為三個 HIGH，實際上是同一件事：**判決與它所引用的欄位無關**。

| 缺陷 | 表面 | 根因 | 本回合 |
|---|---|---|---|
| `N-02` | `G13` 永遠綠 | 讀 `duplicate_digest_groups`，artifact 寫 `duplicate_sha256_groups`；`dict.get` 回 `None`，`None in (0, None)` 為真 | 所有欄位走 `require()`；查不到鍵即 `FIELD_ABSENT`，而 `FIELD_ABSENT` 是 FAIL |
| `N-01` | `G16` detail 寫 `False` 仍 PASS | 語意是「誠實回報缺口就給過」，`False` 成了通過條件；且把「cryptography 已宣告」凍成規則 | 拆成 `G16a`（artifact 必須等於閘自己從樹上重算的結果）與 `G16b`（覆蓋是否完整，`REPORTING`）；公理移除 |
| `N-03` | `G10` 檢查到 `264787b0`（r7 的 digest） | 抓的是文件內文**第一個** `Parent／Supersedes`，而 r9＝r8＋章、r8＝r7＋章 | 只讀**最後一個**宣告（＝本章自己），並要求 r5→r10 全鏈、每版是前一版的逐位元前綴 |

車道的鑑識已把三項都做成可重跑的對照（`lanes/A/GATE_FORENSICS.json`）：
`G13` 在改**真正寫的欄位**後仍 `PASS`、改它自己讀的鍵才 `FAIL`；
`G16` 三情境為 baseline `PASS`（`False`）、加入 `cryptography` → `CRYPTOGRAPHY_FALSELY_MARKED_UNDECLARED`、把 `yaml` 修好 → `YAML_NOT_LOCATED`——**未修綠、修好紅**；
`G10` 解析到 `264787b0…`，而 r9 自己宣告的是 `ccd545b5…`。

**`G18` 的 containment 也是同一形狀**：`str.startswith` 讓 `payload-evil/` 通過（`'payload-evil'.startswith('payload')`），`commonpath` 不通過。已改用 `realpath` ＋ `commonpath`。

---

## 2｜閘的結果（14/15 PASS）

| 檢項 | 名稱 | 嚴重度 | 判決 | 代碼 | 實測 |
|---|---|---|---|---|---|
| `G10` | CHAIN_INTEGRITY | BLOCKING | **PASS** | OK | chain r5→r6→r7→r8→r9→r10; own parent c15693d88d03 == r9; 6 declarations in the file, the |
| `G11` | LINE_CONVENTION | BLOCKING | **PASS** | OK | 31/31 bytes+lines+sha; 111331/111331 |
| `G12` | SEGMENTATION_RULE | BLOCKING | **PASS** | OK | per_line=111331 structural=25201 rule published |
| `G13` | COUNT_SCOPE | BLOCKING | **PASS** | OK | duplicate_sha256_groups=0 (key present); external [('kb_external_exact', 0), ('kb_extern |
| `G14` | MAXIMUM_IS_GLOBAL | BLOCKING | **PASS** | OK | 21 cells, range [0.046948, 0.519037] |
| `G15` | LICENCE_LAYER | BLOCKING | **PASS** | OK | HG-KSEOS@6c9fc73:False/8; worktrees/r4-hgk@a7046a3:False/0; GitHub-main@acd9196f:False/0 |
| `G16a` | DEPENDENCY_TRUTHFUL | BLOCKING | **PASS** | OK | 3 subjects agree with the trees |
| `G16b` | DEPENDENCY_CLOSED | REPORTING | **OPEN** | UNDECLARED_DEPENDENCY_OPEN | {"hgk-main": {"undeclared": ["cryptography", "yaml"], "module_level": [], "scan_complete |
| `G17` | ENUM_SLASH_SAFE | BLOCKING | **PASS** | OK | 15/96/12/11; naive(slash)=10 robust=11 |
| `G18` | DIGEST_LOCALITY | BLOCKING | **PASS** | OK | 32/32 resolve inside their own payload (realpath containment), 3 manifests |
| `G19` | COPY_REGISTER | BLOCKING | **PASS** | OK | 45 names, r6 copies=3 in ['FHS_W0W2_R4_20261107', 'worktrees/r4-fabric', '知識庫'], digests |
| `G20` | SUPPLY_CHAIN_CLAIM_SHAPE | REPORTING | **PASS** | OK | offline=EXECUTED hosted=NOT_OBSERVED (claim-shape lint only) |
| `G21` | NUMBER_CONSISTENCY | BLOCKING | **PASS** | OK | handover states 568,120 B and a matching digest |
| `G22` | SELFTEST_CONTRACT | BLOCKING | **PASS** | OK | documented exit 0 == actual |
| `G23` | TRACE_ID_NAMED | BLOCKING | **PASS** | OK | 19 defects, all closed ones named in the body |

**這張表最重要的一列是 `G16b`**：它是 `OPEN`，不是 `PASS`。回合通過自己的閘，同時把「世界還沒修好」印在同一份輸出裡——這兩件事以前被混為一件事，所以閘會往反方向說謊。

`12` 項突變全部 `FIRED`；豁免三項，各有理由：`G21`、`G22` 讀的是本次執行的交接與退出碼（在自身執行中改它會讓結果失效），`G16b` 量的是三棵真實 checkout 而不是 artifact（它的證偽物是 `lanes/B` 的 patch，套在拋棄式副本上）。

---

## 3｜撤銷 `A-01`：那是跨兩棵樹的比較

| | `HG-KSEOS@6c9fc73` | `worktrees/r4-hgk@a7046a3` | `GitHub-main@acd9196f` |
|---|---|---|---|
| `pyproject.toml:6` | `["cryptography>=42"]` | `[]` | `[]` |
| `issuer_binding.py` | **不存在** | 存在 | 存在 |
| 未宣告 | `[{'module': 'yaml', 'distribution': 'PyYAML', 'verdict': 'FAIL_OPEN', 'import_sites': 1, 'paths': ['src/hg_kseos/lane_policy.py']}]` | `[{'module': 'cryptography', 'distribution': 'cryptography', 'verdict': 'UNGUARDED', 'import_sites': 10, 'paths': ['src/hg_kseos/fhs/issuer_binding.py', 'src/hg_kseos/native_admission.py', 'src/hg_kseos/user_trust.py']}, {'module': 'yaml', 'distribution': 'PyYAML', 'verdict': 'FAIL_OPEN', 'import_sites': 1, 'paths': ['src/hg_kseos/lane_policy.py']}]` | `[{'module': 'cryptography', 'distribution': 'cryptography', 'verdict': 'UNGUARDED', 'import_sites': 10, 'paths': ['src/hg_kseos/fhs/issuer_binding.py', 'src/hg_kseos/native_admission.py', 'src/hg_kseos/user_trust.py']}, {'module': 'yaml', 'distribution': 'PyYAML', 'verdict': 'FAIL_OPEN', 'import_sites': 1, 'paths': ['src/hg_kseos/lane_policy.py']}]` |
| nested 授權 | 8 | 0 | 0 |
| CI workflow | 0 | 0 | 0 |

前輪說「HGK 宣告 `cryptography`、`issuer_binding.py` 不存在」——對 `HG-KSEOS@6c9fc73` 成立。
r9 說「已經宣告、檔案不存在、前輪兩處都錯」——對 `HG-KSEOS@6c9fc73` 成立，但把它寫成對「HGK」的結論。
在 `worktrees/r4-hgk@a7046a3` 與 `GitHub-main@acd9196f` 上，**前輪的敘述逐字成立**：`dependencies = []`、`issuer_binding.py` 存在、第 71–72 行載入 `cryptography`。`worktrees/r4-hgk@a7046a3` 的 `user_trust.py:30-31` 更是**模組層無保護 import**。

**因此 `A-01` 的判定撤銷**，改判 `CROSS_TREE_COMPARISON_NOT_COMPARABLE`；`V-06` 的單一 HGK 數字同理作廢。哪一棵是 W0 基準留 `HGK-REF-CANONICAL` 給 owner，本回合不挑。

對 `GitHub-main@acd9196f` 與 `worktrees/r4-hgk@a7046a3` 各重產一份 patch，在拋棄式副本上證明 `declared_covers_imports` 由 `false` 轉 `true`——**兩份都未套用**，因為寫入 HG-KSEOS 不是本回合的權限。

---

## 4｜兩個「綁方法」的數字

### 4.1 相似度是區間，不是上限

矩陣 **21 格**（3 對 × 7 方法）：`max_overall = 0.519037`（`{'pair': 'P-G', 'method': 'char5gram_cosine_tf'}`）、`min_overall = 0.046948`。

- r9 的 `0.245432` 是子集上的最大值；外部算 `0.267852`、另一車道 `0.368972`、本回合 21 格到 `0.519037`。**四個都真，量的是不同方法集合。**
- 本回合不再宣稱任何單一上限，只宣稱區間 `[0.046948, 0.519037]` 與完整矩陣。
- 它的用途是「三份 SPEC 不是彼此的複本」，不是「低於某門檻」。

### 4.2 結構塊：25,201 只在 R2 下成立

| 讀法 | 規則 | 總數 |
|---|---|---|
| R1 | fence 整體一塊、table 整體一塊 | **22,669**（本工具）／22,672（車道 C） |
| **R2** | 逐行分類後合併同類連續區間（本回合採用） | **25,201** |
| R3 | 逐行但不合併（＝行數） | 111,331 |
| R4 | R2 但 `html_comment` 併入 `text` | 25,198 |

本回合**自己重寫分類器**（狀態機，優先序 comment > fence-body > fence-delim > comment-open > heading > blank > table-row > text，fence 與區塊註解 sticky），得到 `25,201`，與 r9 相同。這證明「照公布規則可重現」，不證明「不寫規則也能得到」。R1 與 R4 的差額就是後者的證據。

### 4.3 三份 r6、兩個 digest

`3` 份、`2` 個 digest：
`FHS_W0W2_R4_20261107/writeback/W0` 與 `worktrees/r4-fabric/…/as-built/W0` **位元相同**（`69a08e7f…`），知識庫那份不同（`9f9eb261…`），差 **4 bytes**，首差 offset **475,677**（附錄 `產生時間` `23:41:56` vs `23:10:08`）。

前輪的登記簿只掃四個 root、漏 `worktrees/`，所以報「兩份」。**三份是位置數，兩個是 digest 數**，兩個都對，混用就錯。canonical 仍 `OWNER_UNRESOLVED`。

### 4.4 17 的分母

| scope | 分母 | 有相異副本的來源檔 |
|---|---|---|
| 精確同名 | 31 | `0` |
| 剝 `(N)` 後同名 | 31（348 份副本） | **17** |

r9 說「17/282」：分子相同，分母是**所有同名檔案數**。本回合分子仍 17，分母改為 31 個來源檔。**引用 17 而不帶分母**才是原本的缺陷。

---

## 5｜六個 W0 WP

| WP | 本回合 | 上限 |
|---|---|---|
| `WP-FHS-00` | 31/31 bytes、31/31 lines、31/31 sha（獨立重算） | `SOURCE_READ` 完成；原域 ACK 0 |
| `WP-FHS-01` | 111,331 行段／25,201 結構塊（規則已公布） | 語意分割未做 |
| `WP-FHS-15` | 相似度改為區間＋全矩陣 | 三 SPEC 原 Intake 0 |
| `WP-FHS-16` | 本輪未重跑 | 不假裝驗過 |
| `WP-FHS-19` | 依賴／授權改逐樹量測 | **HOLD**：`GitHub-main@acd9196f`、`worktrees/r4-hgk@a7046a3` 未宣告 `cryptography`；`HG-KSEOS@6c9fc73` 未宣告 `yaml` |
| `WP-FHS-21` | 15/96/12/11；word-boundary=11、slash-split=10 | 原 Runner 未綁 |

---

## 6｜明確不主張

- 不主張 `ORIGINAL_ACK`（六 WP 原域收據仍 0）、不主張 `W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE=true`。
- 不主張三棵 HG-KSEOS 中哪一棵是 canonical。
- 不主張 25,201 是語意分割數；不主張相似度低於任何門檻。
- 不主張 `G18` 證明遠端 blob 全量重雜湊——它只證明「payload 內自身可解析」。
- 不主張 `G20` 是供應鏈證明——它是 claim-shape lint，且已降為 `REPORTING`。
- 不主張 31 冊原 Raw 可被外部獨立重播：22 MB 不入庫，改由 `verify_source_tree.py` 讓持有者自算（`EC-R9-011` 仍 `OPEN_BY_DESIGN`）。
- 不主張兩個 PR 已併、已審、已發行。

---

## 7｜本回合自我錯誤

見 `out/SELF_ERRORS.md`（E-S01..）。最該記住的三條：

1. **同一個病會在自己的修補裡重演**：`build_r10_artifacts.py` 第一版把 external scope 的 class 寫錯，得到 `0/0` 的「通過」——正是 `G13` 的死斷言形狀。是「分母必須等於 31」這條新檢查抓到的。
2. **車道的靜態抽取會誤報**：`GATE_FORENSICS.json` 報「7 項讀到不存在的鍵」，但那 7 項的突變都 `FIRED`，只有 `G13` 沒觸發。**突變結果才是證據，靜態抽取不是**。
3. **釘選時間等於造假**：r9 的 `generated_at=10:20` 是我釘的常數，比 commit 還晚 1 小時 46 分。本回合所有時間一律 `datetime.now()`。

---

## 8｜可重現指令

```bash
cd C:/Projects/Agent_Workspace/FHS_W0_R10_REPAIR_20261108
python tools/dependency_subjects.py
python tools/build_r10_artifacts.py
python tools/build_r10.py
python tools/gate_r10.py --round .            # 15 項
python tools/gate_r10.py --round . --selftest # 12 FIRED
python tools/verify_payload_manifest.py
python tools/verify_source_tree.py --sources <你的 31 冊路徑>
```
