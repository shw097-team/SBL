# FHS W0｜r11 修補回合：封掉「未來才會假綠」的三條路

> **對象**：外部驗收官、原 Maintainer、下一個 session。
> **一句話**：r10 修好的閘自己還有三條可以讓**未來**回合假綠的路（空 manifest、不完整掃描、optional extra），本回合各用一個否證條件封住，並改正一句我自己寫錯的依賴語意；同時把上一個被我手寫而過時的整合交付，改成由 builder 產生。
> **ClaimCeiling**：`AUTHOR_SIDE_MEASURED_WITH_SCOPED_HOLDS`。不主張 `ORIGINAL_ACK`、`NATIVE_WORLDRAW`、`INDEPENDENT_PASS`、`RELEASE_GRANTED`、已併、已審、已發行。

| 事實 | 值 |
|---|---|
| 主體 | `FHS_PIPD-LS-PKG_W0_r11.md`，**577,257 B**，sha256 `24fb2d9ec5d2f220496647088463819bbc0a3082fc5fc754491408bda1d1316e` （SBL LF 版 577,175 B，`1833e21b2c9a24e4f8a4f3426529043e601c23388fec32aaec273ebe055258ff`） |
| 父本 | `FHS_PIPD-LS-PKG_W0_r10.md`，568,120 B，`2285baaf…`，逐位元前綴 |
| 閘 | **15/16 PASS**、blocking fail 0、open reporting 1 |
| selftest | **13 FIRED**、EXEMPT 2（G21, G22）、BASELINE_RED 1（G16b） |
| 原域 ACK | **0** |

---

## 1｜三個「未來假綠」路徑

外部驗收對 r10 的閘提出三項，我逐一在自己的程式上重現（車道直接 import 本回合的閘，不是抄一份模型）：

| ID | r10 行為 | 重現 | r11 的否證條件 |
|---|---|---|---|
| `EC-R10-002` | `files: []` 或缺鍵 → `G18` 回 **PASS 0/0** | **True**（含 `files` 缺失變體；負控 `PATH_OUTSIDE_PAYLOAD` 正確轉紅） | 鍵必須存在 → `FIELD_ABSENT`；不得為空 → `EXPECTED_ENTRY_SET_EMPTY`；必須等於 `expected_entry_set` → `EXPECTED_ENTRY_SET_NOT_COVERED` / `ENTRY_OUTSIDE_EXPECTED_SET` |
| `EC-R10-003` | `scan_complete=false`、未掃到 → 缺集合為空 → `G16b` **PASS** | **True**（另附 `scan_complete=true` 對照） | 任一 subject 掃描不完整 → `UNQUALIFIED_INCOMPLETE_SCAN`，不是 PASS |
| `EC-R10-004` | `dependencies ∪ optional-dependencies` 當 declared → 補 `[yaml]` extra 即 `covers=true` | **True** | required 與 extras 分離；覆蓋以**預設安裝**為準；只由 extra 提供的另列 `provided_only_by_extra`，並由 `G16c` 檢查其 `feature_when_absent` |

**這三條與 r10 修的 `G13` 是同一個病**：檢查讀到的東西不在它宣稱的集合裡。差別是 `G13` 現在就壞，這三條要等到某次無關改動之後才會突然變綠——而那種綠最難發現，因為沒有人會去看一個本來就綠的檢查。

## 2｜`yaml`：我上一輪寫錯了

r10 把 `yaml` 記成 `fail-open`。讀 `lane_policy.py` 之後，正確的是 **{}**：

| 輸入 | PyYAML 在 | PyYAML 不在 |
|---|---|---|
| `.json` | 解析，重鍵 `ValueError` | 同左 |
| `.yaml`，JSON-shaped | 解析，重鍵 `ValueError` | 退回 strict JSON，成功則通過 |
| `.yaml`，YAML-only 語法 | 解析 | **丟例外**，呼叫端記 coverage error |

車道把模組從 `sys.meta_path` 藏起來實跑：非 JSON 的 `.yaml` → **LOUD_REJECT**、JSON-shaped → **parsed**、`cryptography` → **LOUD_REJECT**。

結論改成：**缺 PyYAML 是「YAML-only 語法不被支援」，而且是**大聲拒絕**，不是安全繞過**。要宣稱繞過，需要一个真的會被 ACCEPT 的惡意 fixture，本回合沒有，所以不宣稱。

## 3｜CI 真的跑閘

`EC-R10-007` 成立：SBL 四個既有 job 沒有一個呼叫 `gate_r10.py`。r11 新增 `.github/workflows/fhs-w0-gate.yml`，內容就是

```yaml
python tools/verify_payload_manifest.py --root .
python tools/gate_r11.py --round . --profile payload --skip-hygiene
python tools/gate_r11.py --round . --profile payload --skip-hygiene --selftest --quiet
sha256sum -c SHA256SUMS
```

`--profile payload` 是為此加的：同一支程式在回合裡與在 payload 裡解析到同一批 artifact，所以 CI 跑的不是「給 CI 用的簡化版」。

## 4｜閘的十六項

| 檢項 | 名稱 | 嚴重度 | 判決 | 代碼 | 實測 |
|---|---|---|---|---|---|
| `G10` | CHAIN_INTEGRITY | BLOCKING | **PASS** | OK | chain r5→r6→r7→r8→r9→r10→r11; own parent 2285baaf3788 == r10; 7 declarations, th |
| `G11` | LINE_CONVENTION | BLOCKING | **PASS** | OK | 31/31 bytes+lines+sha; 111331/111331 |
| `G12` | SEGMENTATION_RULE | BLOCKING | **PASS** | OK | per_line=111331 structural=25201 rule published |
| `G13` | COUNT_SCOPE | BLOCKING | **PASS** | OK | duplicate_sha256_groups=0 (key present); external [('kb_external_exact', 0), ('k |
| `G14` | MAXIMUM_IS_GLOBAL | BLOCKING | **PASS** | OK | 21 cells, range [0.046948, 0.519037] |
| `G15` | LICENCE_LAYER | BLOCKING | **PASS** | OK | HG-KSEOS@6c9fc73:False/8; worktrees/r4-hgk@a7046a3:False/0; GitHub-main@acd9196f |
| `G16a` | DEPENDENCY_TRUTHFUL | BLOCKING | **PASS** | OK | 3 subjects agree with what can be verified here |
| `G16b` | DEPENDENCY_CLOSED | REPORTING | **OPEN** | UNQUALIFIED_INCOMPLETE_SCAN | {"incomplete": {"hgk-main": {"scan_complete": false, "note": "only the three fil |
| `G16c` | OPTIONAL_SEMANTICS | REPORTING | **PASS** | OK | 2 non-required modules carry a measured absent-state: {'yaml': 'DEGRADED_BUT_BOU |
| `G17` | ENUM_SLASH_SAFE | BLOCKING | **PASS** | OK | 15/96/12/11; naive(slash)=10 robust=11 |
| `G18` | DIGEST_LOCALITY | BLOCKING | **PASS** | OK | 41/41 resolve inside their own payload (realpath), 3 manifests, entry sets match |
| `G19` | COPY_REGISTER | BLOCKING | **PASS** | OK | 45 names, r6 copies=3 in ['FHS_W0W2_R4_20261107', 'worktrees/r4-fabric', '知識庫'], |
| `G20` | SUPPLY_CHAIN_CLAIM_SHAPE | REPORTING | **PASS** | OK | offline=EXECUTED hosted=NOT_OBSERVED (claim-shape lint only) |
| `G21` | NUMBER_CONSISTENCY | BLOCKING | **PASS** | OK | handover states 577,257 B (and no stale size) with a matching digest |
| `G22` | SELFTEST_CONTRACT | BLOCKING | **PASS** | OK | documented exit 0 == actual |
| `G23` | TRACE_ID_NAMED | BLOCKING | **PASS** | OK | 17 defects, all closed ones named in the body |

非 PASS 項：G16b=OPEN。

`G16b` 仍 `OPEN` 是刻意的：`HG-KSEOS@acd9196f` 與 `worktrees/r4-hgk@a7046a3` 都沒有宣告 `cryptography`，`6c9fc73` 沒有宣告 `yaml`。**世界沒修好，不該讓回合看起來沒問題。**

## 5｜過時身份：11 個 STALE

車道掃了 30 條「檔案 + bytes/digest」的宣稱：MATCH 18、MATCH_WITH_HISTORY 1、**STALE 11**，分布 5 個檔。

成因不是筆誤：r10 的《整合交付》是手寫的，文件之後被重產（567,669 → 568,120 B），整合交付沒跟著重建。r11 的規則是**任何聲稱 bytes/digest 的文件都由 builder 插值**；本檔與《整合交付》都是 `build_r11_report.py` 的輸出。

## 6｜明確不主張

- 不主張 `ORIGINAL_ACK`（六 WP 原域收據仍 0）、不主張 `W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE=true`。
- 不主張三棵 HG-KSEOS 中哪一棵是 canonical（`HGK-REF-CANONICAL` 留 owner）。
- 不主張 `G16b` 會轉綠；不主張 CI 綠等於原域 Checker 簽收。
- 不主張 31 冊原 Raw 可由外部獨立重播（`EC-R9-011` 仍 `OPEN_BY_DESIGN`）。
- 不主張 `yaml` 缺依賴構成實際安全繞過。

## 7｜可重現

```bash
cd C:/Projects/Agent_Workspace/FHS_W0_R11_REPAIR_20261108
python tools/build_r11.py && python tools/build_r11_report.py
python tools/gate_r11.py --round .
python tools/gate_r11.py --round . --selftest
python tools/stage_r11.py
cd out/stage/sbl/evidence/fhs-w0-r11-repair-20261108
python tools/gate_r11.py --round . --profile payload
python tools/verify_payload_manifest.py --root .
```
