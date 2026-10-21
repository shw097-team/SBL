# CR-PLUGIN-SCHEMA-AUTHORITY

**Class**: CR（法位衝突查詢），不是缺陷。
**Opened**: 2026-10-21, R4.
**Range**: `sbl_sp/plugins/**` 的 manifest 形狀；不外溢到 SBL 其他部分。

## 兩條互斥的讀法

**讀法 A（DOC-06 字面）**：`DOC-06/NOBJ24/NOBJ-017` 把「Agent Plugins 1.0 Working Draft」列為
`PROHIBITED`。既然禁止，SBL 產物就不該出現該規格的任何結構元素 —— 包括 `$schema` 指向
`agent-plugins.org` 的 1.0.0 schema。

**讀法 B（R4 §4 特別 CR 段）**：該 `PROHIBITED` 管的是**不要把 Working Draft 當成上位權威或
donor runtime 引進**；而現行宿主只認得帶 portable `$schema` 的根 manifest，缺了它，套件在宿主
眼中不是「這個格式」，等於交付物不可安裝。此時 `$schema` 是**傳輸層的必要 metadata**，不是權威
承認。

R4 已明確採讀法 B，並要求「若適用性確有同一標準內容衝突，開 CR」。本檔即該 CR。

## 這一輪實際做了什麼（在 CR 未關閉前仍然合法）

- 只取 schema 的**傳輸約束**：`$schema` 常數、`additionalProperties: false`、`name` 樣式。
- 沒有引進該草案的 runtime、validator 服務、donor 程式或任何行為語義。
- 內部 `SBL-AGENT-PLUGIN/1` 沒有被刪除，它被降級為**來源帳本識別碼**，寫在
  `extensions["org.sbl.principal"].source_schema`，不再佔用頂層鍵。
- `NOBJ-017` 的 disposition 維持 `PROHIBITED`，本輪**沒有**改動 441 表的任何一列。

## 仍未解的部分（不自行裁決）

1. `extensions` 命名空間用 `org.sbl.principal` 是否構成「採用草案的擴充機制」？目前判斷為傳輸
   容器，不是規範採納。
2. 若日後宿主要求更多草案專屬欄位（例如權限宣告移入 manifest），衝突會從「metadata」升級為
   「語義採納」，屆時必須回到 `DOC-06` 走正式 disposition 變更，不能在 SBL 內自行放寬。

## 關閉條件

Owner 或 HGK native authority 對下列之一作出書面裁定：

- **B1**：確認讀法 B，`NOBJ-017` 維持 `PROHIBITED` 但允許 `$schema` 作為 ingestion metadata（本輪現狀）。
- **B2**：改判 `NOBJ-017` 對「portable manifest 傳輸層」為 `NATIVE_SUBSTITUTED`，並在 441 表附
  一列變更收據。
- **B3**：否決讀法 B —— 則三份套件回到不可安裝狀態，五工具中三個的宿主路線一併停止。

在裁定之前，三份套件的 ceiling 一律停在 `PACKAGED_HOST_PENDING`，不得升為 `INSTALLED` 或
`EFFECTIVE_LOAD` 的**跨宿主**宣稱。
