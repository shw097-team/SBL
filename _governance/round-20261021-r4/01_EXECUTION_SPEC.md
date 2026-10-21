# R4 執行 SPEC（Execution Spec）

```
order_id            SBL-R4-20261020-C3-FIVE-TOOLS-SWOF-W12
schema              SBL-HGK-THIN-ROUTEOUT/4
compiler_changeset  CONTINUATION
compiler_status     EXTERNAL_CANDIDATE_NOT_COMPILED -> (本輪) 見 05_C0_C9 收據
initial_permission  READ_ONLY_PREFLIGHT -> 依序升級
owner_control_plane HG-KSEOS      (唯一規範控制平面)
executor            HGK_GOVERNED_HERMES (runtime / orchestration only)
round_dir           _governance/round-20261021-r4/
```

## 1. 基線

| 角色 | ref | SHA |
|---|---|---|
| 交付主體基線（Foundation） | `main` | `bedc11957d4fc2474b249b69d200829272c118ef` |
| 修補父（c3 原候選） | `candidate/c3-20261020-v1` | `39c604d52570922fdf84b6df9c9359765643b450` |
| 本輪 code 分支 | `candidate/c3-20261021-v2` | 由 `39c604d` 起 |
| 本輪證據分支 | `evidence/r4-20261021-c4` | 由 `cfedf09` 起 |

**不變式**：`main` 不得被本輪直接寫入；本輪只新增 candidate/evidence 分支。任何 merge 需另一次 Owner Gate。

## 2. 受影 WriteSet（本輪唯一允許的寫入面）

```
sbl_sp/plugins/__init__.py          # manifest 產生器（root cause）
sbl_sp/plugins/portable.py          # 新增：portable manifest 嚴格驗證器
sbl_sp/plugins/schema/plugin.schema.json  # 新增：vendored portable schema（1805 B）
sbl_sp/plugins/*/SKILL.md           # 三份受影 frontmatter（僅在必要時）
tools/build_sp_plugins.py           # 產包前驗證（fail closed）
tests/test_sp_plugins.py            # 受影回歸 + 負例
sbl_harness/                        # 新增：HGK harness adapter（B2）
sbl_stack/                          # 新增：SBL Stack installer/doctor（B3）
tools/build_sbl_stack.py            # 新增：stack 打包入口
pyproject.toml                      # 新增 entry point（sbl-stack）
.github/workflows/ci.yml            # 新增 plugin schema 驗證步驟（保持 2/2）
_governance/round-20261021-r4/**    # 治理與證據（evidence 分支）
```

**禁止寫入**：`HG-KSEOS/`、`Fabric/`、`PIPD/`、`SWOF/` 任何路徑（各自需新工單）；`main`；任何 `PROHIBITED` disposition 的 donor。

## 3. 受影施工順序（R4 §6 准入鏈）

1. `SOURCE_LEDGER`：14 DOC / 20 KP / 10 vols / 2 Skill bundle 的 locator 與 digest 狀態。
2. C0–C9 `CONTRACT.json` → 官方 compiler `lint` / `activation` / `acceptance` → `compile`。
3. `F-R4-C3-PLUGIN-SCHEMA-001` 最小修補（只碰 write-set）。
4. 三包重產 → **strict schema 驗證** → 三份 digest + `SP_SET.json`。
5. 五工具 packaging：HGK adapter（B2）、SBL Stack（B3）。
6. Docker 沙盒：install → discover → load → invoke → deny → rollback → uninstall → residue。
7. 本機 Hermes：rollback point → 安裝 → 真載入/叫用/禁操作 → 讀回（owner 已授權）。
8. `TOOLS5_HARNESS_MATRIX` + `OWNER_ACTION_PACKET`（未取得 Host 的欄位）。
9. `SBL_TO_SWOF_W2_SHADOW_HANDOFF.v1`（read-only，交棒 SWOF Owner）。
10. candidate/evidence push → remote readback → 證據回傳包。

## 4. 每個切片的完成定義

一個切片算完成，必須同時有：(a) 受影 diff、(b) POS 與 NEG 各一原始 exit、(c) 分母（不是「全部通過」而是 `n/n`）、(d) 獨立可重跑命令、(e) 對應 `CHK` 編號。缺一即 `PARTIAL`。

## 5. Fail-close 條件

- portable schema 驗證器本身可能 vacuous → 必須以**注入負例**證明它會 fail（`additionalProperties`、`name` pattern、缺 `$schema`、`extensions` 值非物件）。
- Docker 不可用 → 五工具 HOST 欄不得寫 PASS。
- 任何 host 安裝步驟要求 owner 憑證/帳號 → `OWNER_ACTION_PACKET`，不代填。
- 任一 `PROHIBITED` donor 被引入 → 立即 FAIL 該切片。
