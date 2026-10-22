# FAR-R14-6：GSTACK 不是「沒裝」，是「控制包自己沒准入」

**回合** `SBL-R14-FULL-DOC-POST-R13-20261022` · 2026-10-22 · 觸發原因：使用者要求啟用 KANBAN／SWARM／GSTACK／OPENSPEC，前幾輪我只記 `NOT_INSTALLED_IN_ENV (bun: command not found)`，這個記法太淺。

## 一、量到的事實

| 來源 | 內容 | 含義 |
|---|---|---|
| `PIPD/.hgk/artifacts/s1/TECHNOLOGY_ADMISSIONS.json` | `CAND-11 / external_name: gstack`，`disposition: "REFERENCE"`，`source_repository: SOURCE_REPOSITORY_RECHECK_REQUIRED`，`license: LICENSE_NOT_INDEPENDENTLY_PIN_VERIFIED`，`immutable_pin: PIN_REVALIDATION_REQUIRED` | 控制包把 gstack 列為**參考捐贈者**，來源、授權、版本三者**皆未釘**。它從未被准入為可執行技術。 |
| `PIPD/.hgk/surfaces/gstack_route_check.json` | `flows.review`: `provider: gstack.review`, `state: CERTIFIED`, `route: GSTACK`, `fallback: hgk_native_review`；`flows.qa` 同理；`design/implementation/acceptance/validation` 皆 `route: NATIVE` | 路由檢查把 **review 與 qa 宣告成「已認證走 GSTACK」** |
| 磁碟全盤搜尋（`/c/Projects` 深度 3、PIPD `git grep` 全歷史 40 個 revision） | 無任何 `gstack` 可執行檔、無安裝說明、無 repo 副本；只有上述 JSON 紀錄 | 宣告的 provider 沒有對應的可執行體 |
| 宿主工具鏈 | `node v24.19.0`、`npm 11.17.0` 存在，`bun` 不存在 | 先前把阻塞歸因於 `bun` 缺失，是**症狀**不是原因：就算裝了 bun，也沒有東西可執行 |

## 二、真正的缺陷（這才是要裁決的）

控制包**自相矛盾**：同一包裡，技術准入說 CAND-11 只能是 `REFERENCE`（來源與授權未釘），路由檢查卻把 review/qa 兩條流程標成 `CERTIFIED` 且 `route: GSTACK`。

- 若照路由檢查走 → 等於**用一個未准入、來源未釘的技術做審查**，而審查正是本回合 M2 的判定機制。
- 若照技術准入走 → review/qa **必須**走宣告的 fallback `hgk_native_review` / `hgk_native_qa`。

## 三、本回合的裁決（已執行，不是建議）

**採技術准入的約束，review/qa 一律走 `hgk_native_*` fallback。** 理由：准入紀錄是可否執行的授權來源；路由檢查只是路由偏好，不能反過來授權一個未准入的技術。這與本回合既有事實一致——九輪 TS23 審查全部由 Codex CLI／checker 車道（deepseek）執行，沒有任何一輪依賴 gstack。

因此 `route: GSTACK` 的宣稱在 CAND-11 取得**已釘來源 + 已驗授權 + 已釘版本**之前**不得被引用為已達成**。本回合不把它算進任何 Gate 的證據。

## 四、要 owner 做的（一個動作）

在 `PIPD/.hgk/artifacts/s1/TECHNOLOGY_ADMISSIONS.json` 對 CAND-11 二者擇一：

1. **維持 REFERENCE**：同時把 `gstack_route_check.json` 的 review/qa 改成 `route: NATIVE`（或保留 GSTACK 但 `state: ROUTE_UNAVAILABLE`），讓兩份檔案不再互相矛盾；或
2. **准入為可執行**：釘住 repo、commit、license，並提供可執行入口；之後路由檢查的 CERTIFIED 才有依據。

在那之前，任何「GSTACK 已啟用」的敘述都是不成立的。

## 五、附帶結論（其餘三個表面）

- **KANBAN**：`hgk kanban` CLI 與 `.hgk/kanban/` 存在且可用（本回合的義務以 `next_obligation.py` 驅動，屬同層）。
- **SWARM**：`SWARM` 目錄與車道派工在跑；本回合以 delegate 併行（TS17、TS19/20、TS23 第九／十輪）。
- **OPENSPEC**：`openspec validate r14-full-doc-20261022 --strict` → valid，deltaCount 3。
- **GSTACK**：如本文——未准入，走 native fallback。
