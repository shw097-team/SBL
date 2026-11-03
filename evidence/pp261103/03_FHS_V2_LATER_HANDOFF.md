# 給下一階段：使用（或不得使用）這個 TPM 的方式

> 依控制方案 §5.1，本文**只說明交接**，不包含 `FHS_PIPD-LS-PKG_v2` 的任何 SPEC／22 WP／W0–W3 內容。

## 1. 現在的答案

**`PRE_V2_CLOSEOUT=NO`** — 修補後 TPM **尚不可**作為 `FHS_PIPD-LS-PKG_v2` 主產出的正式前置輸入。

原因不是「差一個小修」，而是**三個明確缺件**：

| 缺件 | 影響的階段 | 誰能補 |
|---|---|---|
| rc.2 從未有過 Host 執行（`P0_HOST_INVOKE`） | 「Host 真的用過這個插件」這一整條主張 | Hermes/Codex Host 端（受限 sandbox 可用後跑一次 Fresh Goal） |
| 原 Operation/Effect Registry 不存在（`P0_ECP_TYPED`） | typed ECP、效果綁定、K4 路徑等價 | PIPD Contract Owner ＋ HG-KSOS Issuer |
| 缺 Host 級舊版重載（`P0_ROLLBACK`） | 回退資格 | 同上 Host 端 |

## 2. 今天就可以用的部分（設計級，已有真證據）

| 能力 | 狀態 | 依據 |
|---|---|---|
| 原 PIPD Writer 產四件並被原 Reader ACK | **可用** | `validate --require-four`：`PASS / checked 4 / closure FULL / complete=true / exit 0`（新樹 `pipd-ls-sp 0.1.1a5` 與舊樹結果相同） |
| 錯 schema 物件被拒 | **可用** | `exit 1` + `SCHEMA` finding |
| Planned ≠ Live 分離 | **可用** | `TQAEP_DESIGNED / NOT_GRANTED`；假收據、假 grant、cross-subject、blind retry 全拒 |
| 泛用 ECP（無 effect 綁定） | **可用但受限** | 標 `EFFECT_UNBOUND`／`claim_ceiling=AUTHOR_DESIGN_ONLY` |
| 插件安裝／卸載／SHA 可追溯 | **可用** | 14 SKILL.md、plugin.json 與 ZIP 位元組相同 |

## 3. 下一階段可安全怎麼開始

1. **可以**用原 writer 對受界真實來源產 PI／PD／ECP（泛用）＋ receipt-free PlannedTQAEP，作 FHS v2 的**規劃輸入樣本**。
2. **不可以**把它當成「已 qualified 的 TPM 產出」對外主張；`checked=4` 與作者 Gate PASS 都不等於 Live Qualified。
3. **不可以**在缺原 registry 的情況下讓任何 effect-specific 決策進入施工或驗收；`EFFECT_UNBOUND` 必須一路保留到原 Owner 批准新契約。
4. **不可以**用 `danger-full-access` 的執行結果充作 Host 安全資格。

## 4. 解除路徑（依序，不新增 Gate）

1. Host 端修 `HOST-124`（或用原策略允許的等效受限模式）→ 跑一次 Fresh Goal → 回讀 `Installed→Loaded→Invoked/Used` → `P0_HOST_INVOKE` 可望轉 PASS。
2. 同一批命令再跑一次舊版重載 → `P0_ROLLBACK` 補齊 Host 段。
3. 原 Owner 批准 `operation-registry.json` ＋ `OperationRegistry.schema.json` 並登錄 family（不得擅自加第 20 family）→ `P0_ECP_TYPED` 可望轉 PASS。
4. 三項齊備後再作**一次** `PRE_V2_CLOSEOUT` 裁決；不需重跑本輪其他已 PASS 的視圖。
