# R3 Execution Spec (任務執行 SPEC)

## 1. ChangeSet

`CONTINUATION`，基線 `bedc11957d4fc2474b249b69d200829272c118ef`（v13）。本輪對產品原始碼的變更**只允許**：
M4-LITE 若發現可重現中高風險缺陷時的窄修、R2 封裝缺件、以及 C 批次的新候選分支（不得倒灌 A/B）。

## 2. 分域權威（不互相升格）

| 域 | 權威 | 本輪用法 |
|---|---|---|
| 產品需求/驗收 | `source_root/SBL_PIPD-LS-PKG_DOC-00..13`（14/14） | 只讀；以 locator 引用，不重印 |
| 產品實作 | `C:\Projects\Agent_Workspace\SBL`（git） | 唯一產品寫入面 |
| 執行/控制 | `HG-KSEOS`（lane / WorkOrder / registry） | 派工與收據；不反向成為產品權威 |
| 治理契約 | `Fabric` | 契約面 |
| 外審 | `SBL-EIAR-20261020-R2-V13-FULL`（sha256 `e476a1d8…`） | Observation/Finding/Scope，不取代 DOC/Native Writer/Permit |
| 知識 | `00_KNOW_INDEX..19_KP_INDEX_CROSSWALK`、`GPTs_GENIEMAKER_vol-01..10` | 設計相容/regression reference，不裝入產品 runtime |

## 3. 執行 DAG

```
G0 currentness (git/remote/CI) 
 → G1 C0–C9 CONTINUATION 編譯 (lint→activation→acceptance→compile)
 → A  M4-LITE: 6 properties × POS/NEG raw receipts → 人類簽名 Gate
 → A' PR + Owner manual merge Gate
 → B  R2: wheel+sdist → clean install → FUO → uninstall → digests → Owner release Gate
 → C  SP packages + HOST_INSTALL_REQUEST + 441/149/38 ledgers（每批另行准入）
 → Evidence branch → remote readback → Kanban/OpenSpec → TT/SWOF handoff
```

## 4. 每個寫入批次的固定形狀

`FirstFail → RepairCone/WriteSet → checkpoint(before_sha) → smallest patch → new SHA → POS/NEG/SEC + affected regression
→ separate checker → rollback/readback`。新產品 SHA 使**受影**舊收據失效；未受影封存成果不重跑。

## 5. 不變量（違反即 STOP）

1. 不改 Oracle、不降測試門檻、不以 Python gate 計數冒充 Native/Host 功能。
2. 不 force push `main`；`main` 只在 Owner 手動 merge 時移動，移動後立即 readback。
3. Token 只由本機 credential helper 一次性讀取，不入 repo / commit / log / evidence。
4. Checker 不得修改受審主體；一輪所有 orchestrator 寫入完成後才派 checker。
5. 私有 DOC/KP/GENIEMAKER 原文與知識全文索引不進 public repo。
6. 沒有 Host 收據時，三 SP 只能是 `HOST_PENDING`，不得宣稱 `INSTALLED`。

## 6. 本輪軌道與工作量上限

| Track | 可自行完成 | 必須 HITL |
|---|---|---|
| A | 六性質 harness、raw receipts、PR 前置材料 | **人類簽名**（唯一阻斷） |
| B | wheel/sdist、clean install、FUO、uninstall、digest | Release/Tag 授權 |
| C | 三 SP ZIP、checksums、HOST_INSTALL_REQUEST、ledger 逐項 disposition | ChatGPT workspace 安裝、HGK 原生安裝、PIPD Native Writer |
