# SBL v0.1｜任務執行 SPEC

```yaml
schema: SBL-ROUND-EXECUTION-SPEC/1
round: SBL-PIPDLS-20261020
project_id: HGK-PRJ-SBL-PIPDLS
workorders:
  - WO-TS-PIPDLS-01   # Source discovery / freeze
  - WO-TS-PIPDLS-02   # Core implementation
  - WO-TS-PIPDLS-03   # Acceptance and evidence
  - WO-TS-PIPDLS-04   # Package and delivery
kanban_board: sbl-pipdls-20261020
swarm: {root: t_bf8acd6d, workers: [t_88de4454, t_543f8bf3, t_30f8c302, t_73364f50], verifier: t_38296605, synthesizer: t_b598a788}
```

## 1. 模型方案（owner mandate 2026-10-20，已實測可用）

| 角色 | 模型 | 執行面 | 實測收據（本輪） |
|---|---|---|---|
| PLAN / Orchestrator | `openai-codex/gpt-6.1-sol` medium (OpenAI OAuth) | Hermes（PLAN 車道） | `plan_gpt_probe.json`：`ok=true`, `required_arm==served_arm`, 2.89s |
| EXECUTE（bounded writer） | `opencode-go/deepseek-v4.1-flash` | CODEX CLI（sealed lane） | `lane_probe_EXECUTE.json`：`ok=true`, rank1, 5.05s |
| VERIFY / SECURITY（independent checker） | `openai-codex/gpt-6.1-sol` medium | CODEX CLI（read-only） | `lane_probe_VERIFY_SECURITY.json`：`ok=true`, rank2→gpt-6.1-sol, 2.53s |

規則：
- 每次派送必須 `--force-rank <n> --require-arm <provider>/<model>`，收據斷言 `required_arm == served_arm`，
  且 `usage_receipt_ok=true`；只有 `ok=true` 不足以宣稱該回合完成工作（需另驗產物）。
- 車道模型 ≠ 互動會話模型；會話 pin（本輪 `deepseek-v4.1-flash/opencode-go`）不構成 PLAN 能力判定。
- 已宣告 drift（TT）：`config/lane-routing-registry.yaml` epoch22 `routes[]` 仍是 2026-10-16 owner order
  （PLAN=glm-5.3-flash、VERIFY=deepseek-v4.1-flash），與 AGENTS.md/使用說明 v2026.10.15-r1（PLAN/VERIFY 預設
  gpt-6.1-sol）不一致；registry 宣告 PLAN `engine: hermes`，dispatcher 實作一律 spawn codex-cli。
  本輪**不** promote registry，以逐輪 role mandate chain 覆蓋，drift 交 owner。
- CLI pin stale（TT）：`config/hermes-codex-lane.json` 指到不存在的 `…\bin\e78bad9887fa50cf\codex.exe`；
  每次派送必須帶 task-local `--codex-executable …\bin\896a0166b774037a\codex.exe`（0.163.0-alpha.10.2），
  否則 fail-closed `ERR_LANE_PIN_IDENTITY_INVALID`。

## 2. 授權與禁區

已授權：`C:\Projects\Agent_Workspace\SBL` 內部一切修改／增刪／重命名；建立 `shw097-team/SBL` public repo
並推候選與脫敏證據（憑證只由本機非模型程序讀 `API KEY\GITHUB-REPO_SHW097-4.txt`，值不進 LLM／log／commit）。

未授權：改 HG-KSEOS/Fabric 封存政策、其他 repo、本地來源庫、credential store；Maker 自簽 PASS；
`PREW3_SHADOW` 世界副作用；`SWOF_CONNECTED` 無 Native ACK 宣稱；以自造 compiler 取代正式
`construction-acceptance-prompt-compiler`。

## 3. 六個執行面（本輪啟用）

| 面 | 载体 | 狀態 |
|---|---|---|
| HGK | Shared Spine：project + 4 WorkOrders + lifecycle transitions | 已建立（見 ROUND_MANIFEST） |
| KANBAN | board `sbl-pipdls-20261020` + swarm DAG 6 卡 | 已建立 |
| SWARM | 4 worker + verifier + synthesizer 卡（併行） | 已建立，逐卡 claim/complete |
| GSTACK | `HGK_GSTACK_ROLE_MAP.yaml` + named_methods route(flow) | 待跑（TS03） |
| OPENSPEC | `SBL/openspec/changes/<change>` + `openspec validate --strict` | 待建（本輪第一個寫入） |
| CODEX | EXECUTE/VERIFY 真 spawn（每次一收據） | 已 probe；待逐批派發 |

## 4. 分階段 Gate（fail-closed）

1. **G0 模型與工具鏈**：三車道 probe 收據（已過）。
2. **G1 SourceFreeze**：306 檔 byte-level ledger + 原文唯讀 + mirror 驗證（進行中）。
3. **G2 Compiler**：C0..C9 contract → 正式 `prompt_contract_compiler.py` 的 `lint`/`activation`/`acceptance`/`compile`，
   每步存 exit code + 脫敏 stdout/stderr + 報告 SHA。BLOCKED 即停受影 mutation。
4. **G3 產品**：Shared Core + SBLM01..06 + 3 SP + 3 Mode + GJ01..03，POS/NEG/EDGE/SEC 真測試。
5. **G4 證據**：evidence manifest、SEC/secret scan、SBOM/license、checkpoint/replay/rollback。
6. **G5 公開候選**：repo create（public）、candidate branch + evidence commit、remote exact SHA readback。
7. **G6 獨立驗收**：VERIFY/SECURITY 車道 read-only 重驗，不同 Principal，產 verdict；maker 不得自簽。
8. **G7 閉環**：單一 evidence MD、TT/CR 清單、claim ceiling、resume pointer。

## 5. 失敗與復原

`FirstFail → root cause raw evidence → repair cone → checkpoint → smallest patch → 新 candidate SHA →
focused test → affected regression/SEC → 新 checker → 公開候選`。
禁止為 PASS 降 test/oracle/threshold；舊 SHA 收據依 dependency invalidation 失效。
`BLOCKED / PAUSED_REMEDIABLE / STOP_ESCALATE` 不得冒稱 `COMPLETED_ACCEPTED`。

## 6. 本 SPEC 的自我限制

本 SPEC 為 **作者端**（PLAN/Orchestrator）產物，未經獨立 Checker 驗證；其正確性只在其引用的原始收據範圍內成立。
