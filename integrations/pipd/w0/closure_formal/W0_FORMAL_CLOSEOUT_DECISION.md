# W0 正式結案裁決 — 2026-11-05（run 1040）

| 欄位 | 值 |
|---|---|
| W0 verdict | **`W0_CLOSEOUT_PENDING`** |
| 六 WP 全部 DONE | **FALSE** |
| W1 intake verdict | **`W1_AUTHOR_INTAKE_PACKAGE_COMPLETE_READER_PENDING`** |
| W1 typed receiver accepted | **FALSE**（只有原 W1 Reader 能設） |
| 基準前像 | closeout `bced4b07…`（617 成員）＋原 R4C `f3838fb0…`（592 成員） |
| 四實體 | Product `e60dc4bb…`／Architecture `68d95a51…`／Program `28ebc681…`／SourceManifest `06628b6b…`（4/4 逐 byte 相符） |
| 新 W1 Subject | `FHS-W1-r4-candidate-b41d2e-W0-CLOSEOUT-20261105-0832`（非 EXAMPLE） |

## 1｜為什麼仍是 PENDING

`W0_FULL_CLOSEOUT_ACCEPTED` 需要 WP16／19 的**原 Consumer／Program Reader 真 ACK**，或原 Program Owner 對同 Scope 的具名延期。本輪：

- 原 SBL CI/Program Reader：**NOT_OBSERVED**
- 原 Technology/License/Host Reader（WP16 12 筆）：**NOT_OBSERVED**
- 三庫原域接收：SBL/Fabric 仍 open／0 review；HG-KSEOS 依規則差異**零寫入**
- 覆核輸入 `W0_R4C_CLOSEOUT_20261105_REVIEWED_W1_SCOPED_GO_r1.zip`（`aaf66dd8…`）與兩份 review MD：**本機不存在**，記 `SOURCE_HOLD`

沒有任何一項可以作者端代簽，因此不升 `ACCEPTED`。

## 2｜F2：WP19 三個受影修補（真上游 root）

受測根 = `git archive origin/main:integrations/pipd` @ `004e8891…`（樹內無 `w0/`）。

| 修補 | 檔案 | 性質 |
|---|---|---|
| SBOM 版本漂移 | `SBOM.cdx.json` | `metadata.component.version 0.1.0 → 0.1.1a5`（與 pyproject 一致） |
| pytest 未宣告 | `pyproject.toml` | test extra 加 `pytest>=8,<9` |
| gate 混淆 runtime 與 extras | `w0/lanes/wp19/supply_chain_gate.py`（＋2 條新測試） | `SBOM_COMPONENT_RECONCILE` 只比 runtime；extras 列 `optional_not_listed`；runtime 缺件用獨立碼 `SBOM_COMPONENT_MISSING_RUNTIME` |

**修補後**：PASS 6／FAIL 1／HOLD 0，exit 1。剩下的 FAIL 是 `UNDECLARED_DEPENDENCY`：`hg_kseos` 只在 `tools/` 的開發工具被 import（repo-external dev tool），列 `WP19_DEP_DEVTOOL_HOLD`。

原 CI ACK 未取得 → `WP19_DONE=false`，`E26 = WP19→WP14 (W4)` 保留 `UNSATISFIED_WP19_ORIGINAL_RAW_MISSING`。

## 3｜F3：WP16 十二筆受影消費

五層分離：`SELECTED 12／BOUND 1／INSTALLED 0／INVOKED 0／VERIFIED 0`；11 筆各有一條具名 HOLD（owner＋required_raw＋resume＋firstfail），其餘 18 筆維持前輪狀態不動。`installs_performed=0`。

## 4｜F1／F5：W1 作者端接收包

- 四份真檔逐 byte 相符，包內以 `inputs/` 實體攜帶並釘 `sha256`。
- 三 SPEC role 不混、`subject_id` 非 EXAMPLE、31 源與 22 Parent/NEG 完整、`receiver_ack=NOT_OBSERVED`。
- 唯讀先行的 effect 邊界：`SOURCE_READ`、`LOCAL_DRAFT_WRITE`；其餘 HOLD。

## 5｜三庫現況

| repo | PR | HEAD | 狀態 |
|---|---|---|---|
| SBL | #41 | `cd4b2eb1…` | open／未合併／0 review；本輪追加 WP19 修補 |
| Fabric | #27 | `e7b5a06a…` | open／未合併／0 review；導航 check success |
| HG-KSEOS | #11 | `8da3cb3c…` | open／未合併；**本輪零寫入**（`AGENTS.md` 差異待原 Owner 裁定） |

## 6｜HOLD

本輪結束 **70 筆全 OPEN**：前輪 68＋`WP19_DEP_DEVTOOL_HOLD`、`W1_RECEIVER_ACK_HOLD`。另有 `SOURCE_HOLD`（reviewed ZIP 與兩份 review MD 不在本機）。

## 7｜未宣稱

`W0_FULL_CLOSEOUT_ACCEPTED`、`W0_WAVE_CLOSEOUT_ACCEPTED_WITH_DEFERRED_EFFECTS`、`WP19_DONE`、`PIPD_CANONICAL`、`HGK_ADMITTED`、`HOST_NATIVE_E2E`、`PROTECTED_CHECKER`、`RELEASED`、`W1_TYPED_RECEIVER_ACCEPTED`、超出 `AUTHOR_STATIC` 的 `TraceClosure`。

本裁決是作者端讀回；不是原 Reader ACK、不是 HGK Permit、不是密碼學簽章。
