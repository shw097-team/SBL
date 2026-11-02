# rc.2 工程結案（C0–C2）— 2026-11-03

結論：**工程結案 = YES。產品主用資格 = 未升級（`PRE_V2_DESIGN_SIDECAR_READY` 保留）。**
`NATIVE_GOLDEN_HOLD` 不變。本輪未新增任何 Native 效果、未簽 Grant、未切換主用路由。

---

## C0 結案封存（重讀真值）

| 對象 | 實讀值 |
|---|---|
| SBL main | `25a4c13c34`（Merge PR #20），main CI **success** |
| PIPD-LS-SP main | `a25fb56910`（Merge PR #28），check-runs **success** |
| SBL #15 / #18 / #20 | `closed / merged=true`（`aac7ab9` / `24d1205` / `25a4c13`） |
| PIPD #26 / #28 | `closed / merged=true`（`7073fe2` / `a25fb56`） |
| rc.2 ZIP | `3a9da65561ab19cad90a6d7cbfb2eae0abf59b87ba565a118790bce5612326a8`，173 成員、14 Skills，**未重建** |
| 舊 Run | `RUN-20261102-GJ02-01` 證據樹在 main 上非空且可解析 |

獨立複核：`gstack2/VERIFY_C0.md` — 23 項檢查全過、0 mismatch。

## C1 原 Effect Authority 最小接線 — `EFFECT_REGISTRY_UNBOUND`（具名停損）

在本機四庫做一次性精確偵查（`c1/REGISTRY_RECON.md`）：

- `rg OperationRegistry` 於 SBL／PIPD／Fabric／HG-KSOS → **0 hits**；無任何 `*operation*registry*`、`*effect*registry*`、`operation-types.json`、`effects.json`。
- PIPD 19 個 canonical schema 內含 `"enum"` 的檔案數 = **0**。
- 現役 runtime 只把 `registry.json` 當 **contract schema 索引**讀（`registry.load_schema/load_registry`），**從不讀 effect 映射**。
- 存在三套互不相容、且都未被原 Owner 批准的詞彙：
  1. SBL KB DOC-05 的 576 列設計路由表（8 類：READ／TEST／CODE_WRITE／DEPLOY／BACKUP／RESTORE／ROLLBACK／UNINSTALL），markdown、未批准、且方向相反（(Kind,Mode,Effect,Host)→route）。
  2. `PIPD/schemas/ECP.schema.json` 的 `effect_class` 為 **無 enum 的字串**，`x-s0-vocabulary.status = CANDIDATE_VOCABULARY_PENDING_OWNER`（值集 4 類）。
  3. HG-KSOS `owner_window.py:44` 硬編同一 4 類作為 ceiling ladder，無 schema／owner／epoch。
- Fabric 對 `operation_type|effect_class|REPOSITORY_WRITE|HOST_OPERATIONS|REMOTE_RELEASE` → **0 hits**，不讀任何 registry。

**精確接口差額（只記一次，不再搜尋）**：需原 PIPD Owner 在 `PIPD/schemas/` 新增
`operation-registry.json` + `OperationRegistry.schema.json`，並在 `PIPD/schemas/registry.json`
（`PIPD-S0-CONTRACT-REGISTRY/1`）登錄為 family，使 `registry.load_registry()` 能以內容雜湊 pin；
檔案須宣告 `SBL.OperationRegistry.Binding@2`、`operations[] = {operation_type, effect_class}`（每個
operation_type 唯一）、owner、version／policy epoch、`authority_state`，且 effect 值集須由
HG-KSOS `config/issuer` 的單一 owner 批准（DOC-05 與 ECP 詞彙互不相容）。

**本輪未做的事（依指示）**：不自造 registry、不新增平行全域 Registry、不發 Grant。

### 更正一項先前敘述
先前 `05_M1_M4_results.json` 寫「原 pipeline 內唯一的 effect 映射是路徑 heuristic」。重讀後更正：
- **現役 PIPD main 的 `pipeline.py`（sha256 `c5156010…`）完全沒有 effect 映射**（無 registry、無 heuristic）；
- 該路徑 heuristic（`effect_class = "REPOSITORY_WRITE" if scope and not scope.startswith(("/","C:","\\\\"))`，line 388）只存在於 **R21 歷史修補副本** `PIPD/docs/evidence/R21-FAR-20261101/s5/patch/.../pipeline.py`，屬歷史證據而非權威。

結論方向不變（更嚴格）：現役原系統**連一個可引用的效果分類器都沒有**，因此 `EFFECT_REGISTRY_UNBOUND` 成立。

## C2 同產包 → 原 Writer／Reader 接線 — 作者級 PASS

用 **host 自己寫出的來源位元組**（`shadow/gj02-repo-m3/docs/pipd/source/billing.py`，
sha256 `2511e9d3a01d5b44883eefbd0a70c617a62782baa7963a4c9d59399dc5f34418`）餵原 PIPD CLI：

- `init → intake → compile-pi → bind-pd（真 sandbox repo）→ compile-ecp → compile-tqaep`
- writer 自行算出 subject `PI-974a4204962f5dc8`（host 的 `GJ02-BILLING-ROUND-ONCE` 僅是標籤，未被當成原 ID）
- **POS**：`pipd validate --bundle c2/bundle.json --require-four` → `PASS / checked 4 / closure FULL /
  scope FOUR_OBJECT / complete=true / findings 0 / exit 0`
- **NEG**：ECP 換成錯 schema → `FAIL / exit 1`（`Additional properties … 'effect_intent' is a required property`）
- **TQAEP**：原 writer 只到 `claim_ceiling=TQAEP_DESIGNED`、`independent_acceptance=NOT_GRANTED`
  → 具名 `CANONICAL_TQAEP_HANDOFF_HOLD`。交付合法 PI／PD／ECP + `PlannedTQAEP@2`，未造假收據。

**與 M3 的關係（不混淆）**：host 自產的 `@2` 四件仍被 canonical reader 拒收（`@2 ≠ canonical`），
本輪並未把它們升格；canonical ACK 只屬於原 writer 產出的那一套。

## 一次性主用裁決

**`PRE_V2_DESIGN_SIDECAR_READY`（維持）**，不給 `PRE_V2_GENERATION_READY`。唯一主要原因：
C1 未取得原 Effect Authority 綁定（無可 pin 的 registry／owner／epoch），因此 effect-specific ECP 不存在；
次要原因：canonical ACK 覆蓋的是 writer 產物，不是 host 自產的 `@2` 物件。

已驗範圍的設計級使用（Codex Shadow：來源讀取、隔離 DRAFT、SPEC／候選 PIPD、Author Gate、已授權 GitHub 工作）**維持有效**，不需再次核准。

## Host 是否切換

**未切換**（`PROMOTION_QUALIFIED_BUT_HOST_SWITCH_HOLD` 不適用，因為連 GENERATION_READY 都未達）。
`~/.codex`、現役 plugin cache、`~/.opencodex` 全程未改；`danger-full-access` 僅先前隔離診斷，**不作無人值守預設**。

## Native／ChatGPT

- Native GJ02：`NOT_RUN`（無原 Fabric Policy、HGK Issuer Grant/Nonce/TTL、WorkID/Lease/CAS、Protected Checker、Publisher）。
- ChatGPT 私人 Plugin：`PRIVATE_HOST_HOLD`（無官方同 Plugin 更新介面；Codex 的 PASS 不借用）。

## FirstFail（最多三個）與對應原 Owner

| # | FirstFail | Owner | 解除條件 |
|---|---|---|---|
| 1 | `EFFECT_REGISTRY_UNBOUND` | PIPD Contract Owner + HG-KSOS Issuer | 新增並批准 `operation-registry.json`／`OperationRegistry.schema.json` 並登錄 family |
| 2 | `CANONICAL_TQAEP_HANDOFF_HOLD` | Original Protected Checker | 真 checker execution receipt（同 Subject/Candidate/Host/Scope/Epoch） |
| 3 | `HOST-124`（workspace-write 下 pwsh alias 被 policy 拒→exit 124） | Hermes/Codex Host | 宿主修 shell 解析或沙盒策略；未修前不得宣稱安全自治主用 |

## 參照

`c1/REGISTRY_RECON.md`、`c2/C2_RESULTS.json`、`gstack2/VERIFY_C0.md`、
`openspec/CHANGE-rc2-engineering-closeout/`、先前 `05_M1_M4_results.json`、`06_closeout_addendum.md`。
