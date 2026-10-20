# SBL v0.1｜Round R2 狀態與裁決（PH00 唯讀預檢 → 正式編譯 → 切片施工）

```yaml
round: SBL-PIPDLS-20261020-R2
control_plane: HG-KSEOS
runtime_plane: current canonical Hermes (this session)
continuation_of: SBL-PIPDLS-20261020 (bootstrap commit ca6830d on shw097-team/SBL)
claim_ceiling: LOCAL_BOOTSTRAP + CANDIDATE_ONLY
self_acceptance: NONE (maker 不自簽；外審另由 distinct principal 執行)
```

## 1. PH00 唯讀預檢（fresh read，2026-10-20 13:20-13:30 +08:00）

| 檢查 | 結果 | 證據 |
|---|---|---|
| HG-KSEOS 控制平面存在 | PASS（AGENTS.md 14,055 B；config/lane-routing-registry.yaml） | 契約 `SRC-HGK-AGENTS` sha256 已入 contract |
| Fabric 契約面存在 | PASS（`Fabric/FABRIC/AGENTS.md`；`Fabric/AGENTS.md` 不存在 → 以實際路徑為準） | 契約 `SRC-FABRIC-AGENTS` |
| 上位來源 corpus | PASS：306 檔 / 132,383,611 B；14 份 DOC 逐檔 byte 重算 | `evidence/source/SOURCE_VERIFY.json`（aggregate `754cf7be…cda3b`） |
| 目標根 `C:\Projects\Agent_Workspace\SBL` | 非空：git repo、`main` = `ca6830d`、remote `origin` 已設 | `git log`, `git remote -v` |
| GitHub `shw097-team/SBL` | 已存在且 `private: false`（PUBLIC），`main` = `ca6830d9fc9d89b7b87e818670dd67b393472d79` | GitHub API 匿名讀回 + `git ls-remote` |
| C0..C9 編譯器 bundle | 存在且完整（root SKILL、references/ 9 檔、schema、scripts） | compiler sha256 `2c282ad6…57d9` |
| Pipeline 註記 | 前輪 `ROUND_MANIFEST.json` 引用 `scratch/lane_probe_*.json`，該目錄已不存在 → 前輪模型證據不可重讀（缺陷，非本輪可修） | 見 §5 D-01 |
| HGK EXECUTE frontdoor 10100 | 本輪啟動前 DOWN（僅 10101 relay 在聽）→ 以 `start-hgk-exec-frontdoor.ps1 -Action Start` 起，healthz `ok`、sanctioned pair `opencode-go/deepseek-v4.1-flash` | `netstat` + `/healthz` |
| 模型方案（owner mandate） | PASS：三張真實 receipt（見 §2） | 本輪自行重測，不引用前輪 scratch |

## 2. 模型方案落地證據（本輪實測，`_governance/round-20261020-r2/lanes/`）

| 角色 | 車道 | provider/model | 收據 | 關鍵欄位 |
|---|---|---|---|---|
| PLAN / Orchestrator | 本 Hermes 會話（lane PLAN engine=hermes） | `openai-codex/gpt-6.1-sol`（本會話）＋ PLAN 車道池 rank2 可服務 | 會話 runtime | — |
| EXECUTE（bounded writer） | `EXECUTE`（engine=codex-cli） | `opencode-go/deepseek-v4.1-flash` | `EXECUTE_probe2.json` | `ok=true`, `required_arm==served_arm`, `used_rank=1`, `nonce_present=true`, `usage_receipt_ok=true`, 2.92 s |
| VERIFY / SECURITY | `VERIFY_SECURITY`（engine=codex-cli, sandbox=read-only） | `openai-codex/gpt-6.1-sol` | `VERIFY_probe.json` | `ok=true`, `required_arm==served_arm`, `used_rank=2`, `nonce_present=true`, `usage_receipt_ok=true`, 2.73 s |

- 派送一律 `--force-rank <rank> --max-candidates 1 --require-arm <provider>/<model>`（`--require-arm` 只驗不選，需釘 rank）。
- toolchain：declared pin `e78bad…` 失效 → task-local `--codex-executable …/896a0166b774037a/codex.exe`（0.163.0-alpha.10.2），TT-CODEX-PIN-STALE-001 續開。
- 首次探測 `EXECUTE_probe.json` 因未帶 `--nonce` 回 `ERR_NO_ARM_EMITTED_NONCE`（已知誤判類），保留為對照組，不視為車道失敗。

## 3. C0..C9 正式編譯（本輪重新編譯，非沿用）

```
python3 scripts/prompt_contract_compiler.py lint       → exit 0  PROMPT_COMPILE_PASS
python3 scripts/prompt_contract_compiler.py activation → exit 0  PROMPT_COMPILE_PASS
python3 scripts/prompt_contract_compiler.py acceptance → exit 0  PROMPT_COMPILE_PASS
python3 scripts/prompt_contract_compiler.py compile    → exit 0  PROMPT_COMPILE_PASS
```
- 以 `HG-KSEOS/.venv/Scripts/python.exe`（jsonschema 4.26.0）執行，四步 raw stdout/stderr 落 `evidence/compiler/*.std{out,err}.txt`。
- receipt：`contracts/compiled/compiler-receipt.json`，`contract_sha256=dd9afa48…9e60f`、`prompt_sha256=4b02997e…504dc`、`compiler_sha256=2c282ad6…57d9`、`runtime_claim=NOT_EVALUATED`、`independent_claim=NOT_EVALUATED`、`production_claim=NOT_CLAIMED`。
- 前輪 FirstFail（`TypeError: unhashable type: 'dict'`，`required_source_families` 以物件提供）已修正為 schema-合法字串族集合，並改為 schema 驅動（role enum、sha256 pattern、`missing` 需為空字串陣列、`requested_delivery` 需對應 acceptance subject）。

## 4. 施工切片（本輪）

| 切片 | 內容 | 寫入者 | 驗收命令 |
|---|---|---|---|
| A | Shared Core：SBLM01..06、modes（39 gate）、G-KNOW、errors/dto/core | Codex EXECUTE lane（deepseek-v4.1-flash） | `pytest tests/test_core_modules.py tests/test_modes.py tests/test_gknow.py -q` |
| B | 三 SP + skill bridge（GJ03）+ `sbl-todo` CLI（GJ01）+ RepoContext patch（GJ02）+ rollback + `tools/verify_source.py` | Codex EXECUTE lane | `pytest tests/test_sp_isolation.py tests/test_gj03_bridge.py tests/e2e -q`；`tools/verify_source.py --verify` |
| C | CI、packaging、docs（README/ARCHITECTURE/JOURNEYS） | Codex EXECUTE lane | `pytest -q` 全綠；YAML 解析 |
| VERIFY | 唯讀獨立查核（read-only，gpt-6.1-sol） | Codex VERIFY_SECURITY lane | 對 frozen candidate 逐項重跑/重算，輸出 verdict JSON |

PLAN-authored 契約與 spec（`contracts/SBL_C0_C9_CONTRACT.json`、`tools/build_prompt_contract.py`、`_governance/round-20261020-r2/10_BUILD_SPEC.md`）由 orchestration 面撰寫，**不冒充 Codex writer 產出**。

## 5. 缺陷 / TT 登記（本輪新增或更新）

| ID | 類別 | 描述 | 處置 |
|---|---|---|---|
| D-01 | EVIDENCE_GAP | 前輪 manifest 引用 `scratch/lane_probe_*.json`、`scratch/plan_gpt_probe.json`，實際不存在（scratch 已清） | 本輪重測三車道並把 receipt 放進 round 目錄；前輪該欄位標記 NOT_RE-MEASURABLE |
| D-02 | EVIDENCE_GAP | 契約 `G-SOURCE-FREEZE` 原引用 `tools/source_ledger.py`（不存在） | 本輪改為 `tools/verify_source.py`，並要求該檔實際存在（Slice B） |
| TT-CODEX-PIN-STALE-001 | TOOLCHAIN | `config/hermes-codex-lane.json` codex 路徑 `e78bad…` 不存在 | 每批派送帶 task-local `--codex-executable`；canonical 修復屬控制平面回合 |
| TT-LANE-REGISTRY-DRIFT-001 | ROUTING | registry epoch/宣告與 AGENTS.md 宣告不一致 | 逐輪 role mandate 覆蓋 + `--force-rank/--require-arm`；owner 裁決 |
| TT-COMPILER-SKILL-VARIANT-001 | PROVENANCE | compiler SKILL.md 兩版本（7,534 B / 9,396 B），script 與 schema byte-identical | 以 9,396 B + `2c282ad6…` script 為 canonical，待 owner provenance 裁決 |
| TT-SRC-LONGPATH-001 | SOURCE | 原始 corpus 2 檔路徑 267 字元（>MAX_PATH）plain API 不可讀 | 以 `_sbl_src_mirror`（306 檔 byte-equal）為工作鏡像；原始根唯讀 |

## 6. 本回合明確不宣稱

`INDEPENDENT_CASE_PASS`、`RELEASED`、`PRODUCTION`、任何 SWOF 世界連接、任何外審 PASS。
`PROMPT_COMPILE_PASS` 只代表契約可編譯，不代表 runtime 可用。
