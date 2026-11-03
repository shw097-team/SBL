# Effect 與 Case 綁定（CT-03／CT-04）

## 1. Effect 綁定（本輪新實作，PR #27 → SBL main `7aab3c82`）

| 項 | 值 |
|---|---|
| 契約路徑 | `integrations/pipd/contracts/operation-registry.pre-v2-r3.json` |
| 契約 SHA256 | `bedf8754284a15a877cea86e257c13871da98160a7ca70c7e8b779d80cf7a631` |
| schema | `SBL.OperationRegistry.Binding@2` |
| `authority_state` | **`SOURCE_BOUND_OWNER_UNVERIFIED`**（誠實：來源已綁，值集未 ratify） |
| owner | `SBL-PIPD-CONTRACT-OWNER`，`decision_ref: null`，`decision_state: PENDING_OWNER_RATIFICATION` |
| version / epoch | `r3.1` / `2026-11-03T00:00:00Z` |
| loader | `integrations/pipd/src/pipd_ls_sp/operation_registry.py` |

### 已綁定的三個 operation（本 Slice 最小集合）

| operation_type | operation_id | effect_class | original_consumer | consumer_abi | scope |
|---|---|---|---|---|---|
| `SOURCE_READ` | `OP-SRC-READ-01` | `SOURCE_READ` | `SBL-SOURCE-READER` | `ABI-SOURCE-READ-1` | `src/demo/billing.py`, `tests/test_billing.py` |
| `LOCAL_DRAFT_WRITE` | `OP-DRAFT-WRITE-01` | `LOCAL_DRAFT_WRITE` | `SBL-ISOLATED-DRAFT-WRITER` | `ABI-DRAFT-WRITE-1` | `src/demo/billing.py` |
| `REPOSITORY_WRITE`（DEV） | `OP-DEV-REPO-WRITE-01` | `REPOSITORY_WRITE` | `SBL-DEV-REPOSITORY-WRITER` | `ABI-REPO-WRITE-1` | `src/demo/billing.py` |

`HOST_OPERATIONS`／`USER_DATA_EFFECT`／`REMOTE_RELEASE` **不在本 Slice**，故未綁；不為湊滿六類而先建全集。

### 為什麼這樣才算「不是自封權威」

| 舊風險 | 現在的機制 |
|---|---|
| 呼叫者可自帶 registry 檔＋自帶 sha | loader 只認**唯一 canonical 路徑**；其他路徑不可載入 |
| 作者改檔就地生效 | 必須是 `HEAD` 已追蹤的 blob，且**工作檔位元組必須等於 HEAD blob**，否則 `OPERATION_REGISTRY_WORKTREE_DIVERGES_FROM_HEAD` |
| 加個 `RATIFIED` 字串就升格 | `ALLOWED_AUTHORITY` 不含 `RATIFIED`；`owner_ratified()` 在現行 schema 下**不可達**，升格需 owner 側改動＋`decision_ref` |
| 用路徑猜 Effect | `effect_for_operation()` 只看契約；`scope_representation_invariant()` 證明相對／絕對／UNC 不改變 effect，越界直接拒收 |

### 拒收碼（實跑，11 passed）

`OPERATION_REGISTRY_MISSING`、`OPERATION_REGISTRY_UNTRACKED`、`OPERATION_REGISTRY_WORKTREE_DIVERGES_FROM_HEAD`、
`OPERATION_REGISTRY_DUPLICATE_OPERATION`、`OPERATION_REGISTRY_UNKNOWN_EFFECT`、`OPERATION_REGISTRY_SCOPE_NOT_RELATIVE`、
`OPERATION_TYPE_UNKNOWN_OR_DUPLICATE`、`SCOPE_LEAVES_OPERATION_SCOPE`。

整合證明：原 adapter 以本契約產出的 intent 仍是 `effect_state=EFFECT_UNBOUND`、`grant_state=NOT_GRANTED`、
`claim_ceiling=AUTHOR_DESIGN_ONLY` — **設計語意成立，原生授權未發生**。

## 2. Case／Oracle／FUO（CT-04）

| 項 | 狀態 |
|---|---|
| 適用 case | `CASE-EXPORT-POS` 等兩例，`original_requirement_id` 對應原 writer 的 `REQ-…` |
| Oracle | 由原 writer PI 提供 `original_oracle_id`；`fuo_id` 為 **`AUTHOR_DERIVED`** |
| Runner | `runner_binding=RUNNER_UNBOUND`（無 protected checker／runner） |
| 無 receipt 的 Planned | 可建立；`tqaep_noReceipt.out` = `TQ_SOD` 拒收（假收據） |
| 判定 | 設計關聯成立，但**本 Slice 無原 Case／Oracle registry** → `P0_TQAEP_FUO = HOLD`（**基於來源**，非缺 Live） |

### 解除 `P0_TQAEP_FUO` 所需（不要求 Native Checker）

1. 該 Slice 的**原 Required Case／Original Oracle／FUO registry**（或原 Domain Reader 的等價輸出）。
2. 以同 Subject／Candidate 重建 `PlannedTQAEP` 的 required 集並對映 `original_*` id。
3. 到此即可 `PASS（DESIGN_ONLY）`；`QUALIFIED` 仍須原 Checker 真執行，不屬前置範圍。
