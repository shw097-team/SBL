---
artifact_id: FHS_vNEXT_PLP_全波次藍圖
source_manifest_sha256: bbcfb1331c6c7c7cf804bbc476d038992788c630975ee82268d87da0058e3096
supersedes: none (new L2 candidate)
scope: author candidate; not ratified
claim_ceiling: AUTHOR_DESIGN_WITH_SCOPED_HOLDS
rollback_ref: keep the previous effective document unchanged until an original reader adopts this file
generated: 2026-11-12T20:45:46
---

# FHS vNEXT PLP 全波次藍圖（L2 作者候選）

## 1. 波次 DAG

`W0（受界完成）→ W1（單庫＋ABI＋手冊接線）→ W2（首個 Protected Slice）→ W3（4Host×3SP/192Cell）→ W4（Cutover）`。
**下游正式規格不得早於其所依賴之上游有效基線的採納**：作者端候選可先行準備（prepare in advance），
但正式生效順序仍為 L0 → L1 → L2 → L3，不得倒置。W0 的 `E3` 判定為 `READY_TO_DRAFT_L0_L1_L2_WITH_SCOPED_HOLDS`，
因此本回合三份 L0/L1/L2 僅為作者候選，不構成任何下游正式規格的生效。

## 2. 每波 Done／FirstFail／Resume

| 波次 | Done 判準 | FirstFail | Resume |
|---|---|---|---|
| W0 | E0/E1 完成；E2-01..11 有 Raw；受界 HOLD 具名 | 來源 digest 不符 | 修受影來源後重跑該 Case |
| W1 | 私有 repo＋一棵 Git root＋模組 ABI＋手冊能力四分類 | RepoContext／ABI 缺 | 先補 RepoContext，不偽造 PD |
| W2 | 首個 Protected Slice 有原 WorkOrder／Grant／Checker | 無 Grant | 交原 Issuer，不自行核發 |
| W3 | 192 Cell 有真 Host Raw | Host 缺 | 標 Host HOLD |
| W4 | Cutover 可逆且舊服務退場有回執 | 舊根仍被引用 | 回復期內 rollback |

## 3. W1 入口七列（本回合已備證據）

見 `FHS_vNEXT_PLP_W1.md` §2 與 `out/W1_ENTRY_SECTION7_READINESS.json`：4 READY、1 READY_WITH_HOLD（SBL PIPD 原編譯入口屬 W1 接線）、
1 READY_NOT_CREATED_BY_DESIGN（GitHub FHS 單庫，文件禁止 W0 建）、1 REPORTED_OPEN_CONDITIONAL（Scope/Hold）。

## 4. 原分母與 NoFit

`50CH/22WP/36Edge/31Source/485Slot/949原子/192Cell/96Oracle/282B1` 不因本波縮小；NoFit 需原 Owner reason。

## 5. POS / NEG

- POS：三份候選各有獨立 `source_manifest_sha256`、`rollback_ref`、`claim_ceiling`，且不製造第二個 NAV／Issuer。
- NEG：L0 未變而先升 L1、PLP 被當成不同產品、r26 原義被刪、Draft 說成 Ratified → 退回原 Owner。

## 6. 本次未主張

任何波次的 Native 完成、Release 或原 Reader Ratification。
