# CR-PLUGIN-SCHEMA-AUTHORITY（R13 裁決記錄）

**狀態**：`DECIDED_BY_OWNER_PREAUTHORIZATION`（2026-10-21，R13 FAR 裁決；依據使用者「最大預授權」）
**影響條款**：`DOC-06 / NOBJ24 / NOBJ-017`（`PROHIBITED`）、`DOC-12 / C-016..C-018`（三 SP 的 ChatGPT 私人 Plugin 交付面）

## 衝突

`DOC-06` 將 **Agent Plugins 1.0 Working Draft** 列為 `PROHIBITED`；而 `DOC-12 C-016..C-018` 要求三個 SP 具 ChatGPT 私人 Plugin 的 create／install／`@invoke`／卸載資格。目前可得的封裝面（草案 ZIP 形式）與前者直接衝突，且 R8 已指出「Hermes skill loader 讀得到 ZIP」不等於 Host 資格。

## 裁決

1. **不**以草案封裝出貨；**不**把本機 skill 載入宣稱為 Host 安裝。
2. 三 SP 目前合規交付面固定為：可攜 ZIP（既有）＋ Hermes skill（既有）＋ 文件化的 host 介面契約。
3. `C-016..C-018` 維持 `HOST_PENDING`，並在任何對外文件標明「未安裝、無 Host-issued id」。
4. 待**官方、非草案**的封裝面出現後，由 Owner 另開 CR 決定是否採用；在此之前任何「3/3 已安裝」的陳述一律視為偽 claim。

## 影響與成本（誠實揭露）

- 三條 Delivery Surface 在可預見期間不會閉合；`SBL_FULL_PRODUCT` 因此不可能在近期 PASS。
- 換得的是：零法務風險、零偽 claim、其餘 35 條 surface 不被這一條阻塞。

## 反轉條件

若 Owner 書面選定一個**非草案**且可驗證的 Host 封裝面，本 CR 可由新 CR 取代，並需重跑 `C-016..C-018` 的 create→install→`@invoke`→deny→uninstall 全生命週期。
