# R5 — 任務執行 SPEC

## 0. 身分

| 欄位 | 值 |
|---|---|
| order_id | `SBL-FULL-DOC00-13-R5-20261021` |
| round_id | `SBL-R5-20261021-C5` |
| route | `DESIGN_TO_OROCHI_FACTORY_ORDER_TO_HGK_WORKORDER` |
| change_set | `CONTINUATION` ＋ 第一個 `NARROW_REPAIR`（TS05） |
| control_plane | `HG-KSEOS_Native`（唯一） |
| runtime | `HERMES_governed` |
| contract_surface | `Fabric` |
| product_root | `C:\Projects\Agent_Workspace\SBL` |
| source_root | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG` |
| baseline_main | `bedc11957d4fc2474b249b69d200829272c118ef` |
| blocked_candidate | `68c276d354dae2b1bc2baef290f89e539fb34751`（PR #2，OPEN） |
| evidence_branch | `evidence/r5-20261021-c5` |
| compiler | `C:\Projects\Agent_Workspace\知識庫\工程基座\construction-acceptance-prompt-compiler\construction-acceptance-prompt-compiler\scripts\prompt_contract_compiler.py`，sha256 `2c282ad6539a465c3b1d751868cab98437a8f35e9728be686117e364a70857d9` |

## 1. 模型方案（mandate vs 實測；車道 ≠ 會話）

會話（session）互動模型 = `deepseek-v4.1-flash@opencode-go`（本 Hermes 會話，非本輪車道綁定）。
車道（lane）模型由 `scripts/hgk-lane-dispatch.py` 以 `--model`／`--force-rank` 釘在子行程。

| 角色 | mandate | 車道 | 釘選 arm | 實測（2026-10-21T02:00Z） |
|---|---|---|---|---|
| PLAN | GPT 6.1 SOL-MEDIUM (OpenAI OAuth) | PLAN (`engine: hermes`→codex-cli read-only) | `openai-codex/gpt-6.1-sol` rank 2 | `ok:true`、`required_arm==served_arm`、nonce 回覆、7.1 s |
| EXECUTE | DeepSeek V4.1 Flash (OPENCODE GO) | EXECUTE (codex-cli) | `opencode-go/deepseek-v4.1-flash` rank 1 | `ok:true`、`served_arm` 相符 |
| VERIFY/SECURITY | GPT 6.1 SOL-MEDIUM (OpenAI OAuth) | VERIFY_SECURITY (codex-cli read-only) | `openai-codex/gpt-6.1-sol` rank 2 | `ok:true`、`served_arm` 相符 |

收據：`10_PREFLIGHT/LANE_PROBES.json`（含各 attempt 的 stdout/stderr sha256 與 usage receipt）。
registry `config/lane-route-slots.candidate.json` rev 10 仍寫 PLAN rank1=glm / VERIFY rank1=deepseek：
**本輪不改 registry（native owner 的檔）**，以 role mandate 逐輪覆蓋並記錄 drift（NF-05 同類宣告）。
註：`codex` 0.163 仍先嘗試 `ws://127.0.0.1:10101` 得 426，但 HTTP fallback 成功完成 turn —— 這是 R4 的 VERIFY 阻斷被解除的實測依據。

## 2. 執行順序（本輪）

1. TS00 唯讀預檢（repo/PR/CI/lane/source）
2. TS01 來源 intake 14/14 + 20/20 + 10/10 + 2 Skill + R5 report，逐一 SHA
3. TS02 canonical compiler C0–C9（lint→activation→acceptance→compile→duplication）
4. **TS05 安全窄修**（唯一寫入產品的一項）
5. TS06 之一部分：真 wheel 內容驗證（沿用既有 `tools/check_wheel_contents.py`）
6. 證據入帳 + 雙平台 CI 同 SHA + （可行時）獨立唯讀 checker 車道

TS07–TS25 本輪**不假裝完成**：列為 OPEN_ACTIVE 並附 resume pointer（見 `03_DETECTION_LIST.md` §尾）。

## 3. 寫入邊界（WriteSet）

允許：
- `sbl_harness/__init__.py`、`tests/test_sbl_harness.py`（TS05 受影程式）
- `sbl_core/errors.py`（必要時新增 typed error code）
- `_governance/round-20261021-r5/**`、`contracts/SBL_C0_C9_CONTRACT-R5.json`、`contracts/compiled-r5/**`
- `openspec/changes/sbl-v01-candidate-build/R5_DELTA.md`

禁止：`main` 直寫、`sbl_core/m01..m06` 邏輯重構、441/149/38 frozen ledger 覆寫、
`HG-KSEOS/config/*` registry、`Fabric/**`、SWOF repo、任何 `PROHIBITED` 項安裝。

## 4. FAIL-CLOSED 規則

- compiler 任一階段非 0 → 只准補正契約，禁止改門檻
- manifest 不可信（非法 key／`..`／絕對路徑／resolve 逃逸／symlink/junction）→ 卸載必須**拒絕**且不動任何 bytes
- 外部 sentinel 檔 bytes 改變 → 該輪判 FAIL，不得以 CI 綠燈覆蓋
- checker 非獨立 principal → 只能記 `PARTIAL_CHALLENGE`，不得稱 `INDEPENDENT_CASE_PASS`
