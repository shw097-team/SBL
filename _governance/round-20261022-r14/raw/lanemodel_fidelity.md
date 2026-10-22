# R14 通道模型忠實度量測

量測時間（UTC）：2026-10-22T03:12:29.646837+00:00。四份設定唯讀；未重新綁定、未修改設定、未派送新模型呼叫。

## 結論

共檢查 363 個結構比較，另列出現行文字矛盾；合計 44 筆不一致（含 metadata、宣告及文字重述）。目前 `check_drift()` 回傳空清單，但不代表語意一致，更不代表每次呼叫的實際模型正確。

## 主通道表

| 角色 | 宣告 provider/model | CLI transport_model | 來源 | relay 目錄包含 |
|---|---|---|---|---|
| PLAN | `openai-codex/gpt-6.1-sol` | `gpt-6.1-sol` | registry `primary`；pool rank 1 | 否 |
| EXECUTE | `opencode-go/minimax-m3.1-flash-free` | `opencode-go/minimax-m3.1-flash-free` | registry `primary`；pool rank 1 | 否 |
| VERIFY | `openai-codex/gpt-6.1-sol` | `gpt-6.1-sol` | registry `primary`；pool rank 1 | 否 |
| SECURITY | `openai-codex/gpt-6.1-sol` | `gpt-6.1-sol` | registry `primary`；pool rank 1 | 否 |

實際 GET /v1/models 回傳 HTTP 200，共 92 個 id。以上「否」只表示目錄沒有該 id，並不證明上游不能服務；既有 receipt 已顯示部分未列名模型的成功 usage。原始回應見 `lanemodel_relay_models.json`。

## Rev 18：修到哪裡

pool revision=18（另有歷史字串 rev=far-closure-20261021-r2）。三個 pool 的 rank 1 均為 default=true / automatic_selection=true，後續 rank 全為 false/false；registry 的 arms 亦同。**只在 pool 與 registry 這兩處一致**。assignment 尚有：

- PLAN chain[0] 宣告 openai-codex/gpt-6.1-sol，transport_model 卻是 opencode-go/minimax-m3.1-flash-free；chain[1] 宣告又重複 GPT，而 registry/pool rank 2 應是 MiniMax。
- EXECUTE chain[0] 宣告 MiniMax，transport_model 卻是 DeepSeek，automatic_selection=false；chain[1] 宣告 DeepSeek，transport_model 卻是 MiniMax，automatic_selection=true。
- VERIFY_SECURITY chain[0] GPT 的 automatic_selection=false；chain[1] MiniMax 的 automatic_selection=true。supply_selector 也保留同樣的反向 auto 旗標。
- assignment[0] 仍宣告 PLAN=opencode-go/MiniMax；assignment[1] 仍宣告 EXECUTE=opencode-go/DeepSeek，均與現行 registry 不符。

## 執行期可觀測證據

| 角色 | 唯一應保留的可觀測值 | 本輪是否已有 |
|---|---|---|
| PLAN | 以 invocation/request_id 綁定實際 Hermes PLAN 呼叫的 provider usage served-model 欄位 | **未在檢查的本輪封包中找到**。有 PLAN 標籤的 Codex CLI 探針 receipt，但 engine 不同，不能替 Hermes orchestration 歸因。 |
| EXECUTE | 與該 invocation 唯一關聯的 usage.jsonl.resolvedModel | 有既存 forced-rank receipt 的 usage_model/provider/status/offset；本次按 offset 回讀原始 ledger 得到 resolvedModel。不是本次新呼叫。 |
| VERIFY | 與該 invocation 唯一關聯的 usage.jsonl.resolvedModel | 有 VERIFY_SECURITY 既存 receipt 及回讀 ledger。 |
| SECURITY | 與該 invocation 唯一關聯的 usage.jsonl.resolvedModel | 僅有共用 VERIFY_SECURITY 證據；**沒有獨立 SECURITY 呼叫歸因**。 |

既存 receipt 的 usage_model 複製的是 ledger.model，不是 resolvedModel；served_arm 則由所選 pool entry 組成。所有既存呼叫的逐筆索引與回讀行雜湊在 JSON 的 existing_round_receipts。offset、時間及相同 provider/model 仍不是併發情境下的唯一 invocation join。relay 自己的 resolvedModel 是路由／用量紀錄證據，並非對上游權重的密碼學證明。

## 漂移是否會被抓到

`check_drift()` 只比較 projection 內的固定 expected 值；本次回傳 []，但以上 assignment 矛盾仍存在。這證明目前的綠燈不能涵蓋跨欄位語意、transport 與全部 auto 旗標。

本次另外執行純記憶體控制案例（非實際流量、沒有修改設定）：正確 usage.model 可通過，錯誤 usage.model 被拒絕；僅把 resolvedModel 改錯，或 conversationId 換成無關呼叫，仍會通過 receipt_matches。這是現行 predicate 的覆蓋缺口，不是聲稱已觀察到真實錯配。

## 每筆不一致（含精確欄位路徑）

1. **PLAN / structured** `config/model-lane-assignment.json#/lane_chains/PLAN/0/transport_model`
   - 讀到：`"opencode-go/minimax-m3.1-flash-free"`
   - 應比對：`"gpt-6.1-sol"`；依據 `config/lane-routing-registry.yaml#/routes/0/arms/0/transport_model`。
2. **PLAN / structured** `config/model-lane-assignment.json#/lane_chains/PLAN/1/provider`
   - 讀到：`"openai-codex"`
   - 應比對：`"opencode-go"`；依據 `config/lane-routing-registry.yaml#/routes/0/arms/1/provider`。
3. **PLAN / structured** `config/model-lane-assignment.json#/lane_chains/PLAN/1/model`
   - 讀到：`"gpt-6.1-sol"`
   - 應比對：`"minimax-m3.1-flash-free"`；依據 `config/lane-routing-registry.yaml#/routes/0/arms/1/model`。
4. **PLAN / structured** `config/model-lane-assignment.json#/lane_chains/PLAN/1/transport_model`
   - 讀到：`"gpt-6.1-sol"`
   - 應比對：`"opencode-go/minimax-m3.1-flash-free"`；依據 `config/lane-routing-registry.yaml#/routes/0/arms/1/transport_model`。
5. **PLAN / structured** `config/model-lane-assignment.json#/assignment/0/assigned_provider`
   - 讀到：`"opencode-go"`
   - 應比對：`"openai-codex"`；依據 `config/lane-routing-registry.yaml#/routes/0/provider`。
6. **PLAN / structured** `config/model-lane-assignment.json#/assignment/0/assigned_model`
   - 讀到：`"minimax-m3.1-flash-free"`
   - 應比對：`"gpt-6.1-sol"`；依據 `config/lane-routing-registry.yaml#/routes/0/model`。
7. **PLAN / structured** `config/model-lane-assignment.json#/assignment/0/canonical_identity`
   - 讀到：`"minimax-m3.1-flash-free"`
   - 應比對：`"gpt-6.1-sol"`；依據 `config/lane-routing-registry.yaml#/routes/0/canonical_identity`。
8. **PLAN / structured** `config/model-lane-assignment.json#/assignment/0/auth`
   - 讀到：`"env_ref:OPENCODE_GO_API_KEY"`
   - 應比對：`"openai_oauth"`；依據 `config/lane-routing-registry.yaml#/routes/0/auth`。
9. **PLAN / structured** `config/model-lane-assignment.json#/assignment/0/oauth`
   - 讀到：`false`
   - 應比對：`true`；依據 `config/lane-routing-registry.yaml#/routes/0/oauth`。
10. **EXECUTE / structured** `config/model-lane-assignment.json#/lane_chains/EXECUTE/0/transport_model`
   - 讀到：`"opencode-go/deepseek-v4.1-flash"`
   - 應比對：`"opencode-go/minimax-m3.1-flash-free"`；依據 `config/lane-routing-registry.yaml#/routes/1/arms/0/transport_model`。
11. **EXECUTE / structured** `config/model-lane-assignment.json#/lane_chains/EXECUTE/0/automatic_selection`
   - 讀到：`false`
   - 應比對：`true`；依據 `config/lane-routing-registry.yaml#/routes/1/arms/0/automatic_selection`。
12. **EXECUTE / selection_role** `config/model-lane-assignment.json#/lane_chains/EXECUTE/0/role`
   - 讀到：`"fallback1"`
   - 應比對：`"primary"`；依據 `config/lane-routing-registry.yaml#/routes/1/arms/0/arm`。
13. **EXECUTE / structured** `config/model-lane-assignment.json#/lane_chains/EXECUTE/1/transport_model`
   - 讀到：`"opencode-go/minimax-m3.1-flash-free"`
   - 應比對：`"opencode-go/deepseek-v4.1-flash"`；依據 `config/lane-routing-registry.yaml#/routes/1/arms/1/transport_model`。
14. **EXECUTE / structured** `config/model-lane-assignment.json#/lane_chains/EXECUTE/1/automatic_selection`
   - 讀到：`true`
   - 應比對：`false`；依據 `config/lane-routing-registry.yaml#/routes/1/arms/1/automatic_selection`。
15. **EXECUTE / selection_role** `config/model-lane-assignment.json#/lane_chains/EXECUTE/1/role`
   - 讀到：`"primary"`
   - 應比對：`"fallback1"`；依據 `config/lane-routing-registry.yaml#/routes/1/arms/1/arm`。
16. **EXECUTE / structured** `config/model-lane-assignment.json#/assignment/1/assigned_model`
   - 讀到：`"deepseek-v4.1-flash"`
   - 應比對：`"minimax-m3.1-flash-free"`；依據 `config/lane-routing-registry.yaml#/routes/1/model`。
17. **EXECUTE / structured** `config/model-lane-assignment.json#/assignment/1/canonical_identity`
   - 讀到：`"deepseek-v4.1-flash"`
   - 應比對：`"minimax-m3.1-flash-free"`；依據 `config/lane-routing-registry.yaml#/routes/1/canonical_identity`。
18. **VERIFY / SECURITY / structured** `config/model-lane-assignment.json#/lane_chains/VERIFY_SECURITY/0/automatic_selection`
   - 讀到：`false`
   - 應比對：`true`；依據 `config/lane-routing-registry.yaml#/routes/2/arms/0/automatic_selection`。
19. **VERIFY / SECURITY / selection_role** `config/model-lane-assignment.json#/lane_chains/VERIFY_SECURITY/0/role`
   - 讀到：`"fallback1"`
   - 應比對：`"primary"`；依據 `config/lane-routing-registry.yaml#/routes/2/arms/0/arm`。
20. **VERIFY / SECURITY / structured** `config/model-lane-assignment.json#/lane_chains/VERIFY_SECURITY/1/automatic_selection`
   - 讀到：`true`
   - 應比對：`false`；依據 `config/lane-routing-registry.yaml#/routes/2/arms/1/automatic_selection`。
21. **VERIFY / SECURITY / selection_role** `config/model-lane-assignment.json#/lane_chains/VERIFY_SECURITY/1/role`
   - 讀到：`"primary"`
   - 應比對：`"fallback1"`；依據 `config/lane-routing-registry.yaml#/routes/2/arms/1/arm`。
22. **VERIFY / SECURITY / structured** `config/model-lane-assignment.json#/assignment/2/supply_selector/arms/0/automatic_selection`
   - 讀到：`false`
   - 應比對：`true`；依據 `config/lane-routing-registry.yaml#/routes/2/arms/0/automatic_selection`。
23. **VERIFY / SECURITY / structured** `config/model-lane-assignment.json#/assignment/2/supply_selector/arms/1/automatic_selection`
   - 讀到：`true`
   - 應比對：`false`；依據 `config/lane-routing-registry.yaml#/routes/2/arms/1/automatic_selection`。
24. **PLAN / wiring_restatement** `config/model-lane-assignment.json#/effective_wiring/main_agent/provider`
   - 讀到：`"opencode-go"`
   - 應比對：`"openai-codex"`；依據 `config/lane-routing-registry.yaml#/routes/0/provider`。
25. **PLAN / VERIFY / SECURITY / shared_delegation_not_lane_bound** `config/model-lane-assignment.json#/effective_wiring/delegation.provider`
   - 讀到：`"opencode-go"`
   - 應比對：`"openai-codex"`；依據 `config/lane-routing-registry.yaml#/routes/0/provider`。
26. **PLAN / VERIFY / SECURITY / shared_delegation_not_lane_bound** `config/model-lane-assignment.json#/effective_wiring/delegation.model`
   - 讀到：`"glm-5.3-flash"`
   - 應比對：`"gpt-6.1-sol"`；依據 `config/lane-routing-registry.yaml#/routes/0/model`。
27. **PLAN / effort_restatement** `config/model-lane-assignment.json#/sod/plan_reasoning_effort`
   - 讀到：`null`
   - 應比對：`"medium"`；依據 `registry primary reasoning_effort`。
28. **VERIFY / SECURITY / effort_restatement** `config/model-lane-assignment.json#/sod/verify_security_reasoning_effort`
   - 讀到：`null`
   - 應比對：`"medium"`；依據 `registry primary reasoning_effort`。
29. **ALL / revision_link** `config/model-lane-assignment.json#/registry_epoch`
   - 讀到：`29`
   - 應比對：`30`；依據 `config/lane-routing-registry.yaml#/epoch`。
30. **EXECUTE / stale_current_restatement** `config/hermes-codex-lane.json#/execute_route_contract/chain_must_be_pinned`
   - 讀到：`"invoke with -ModelChain deepseek-v4.1-flash so the chain cannot advance to another model; assert write_model_used in the receipt"`
   - 應比對：`"Restatement consistent with active registry routes; no repair applied"`；依據 `config/lane-routing-registry.yaml#/routes`。
   - Requires -ModelChain deepseek-v4.1-flash, while active EXECUTE is minimax-m3.1-flash-free.
31. **EXECUTE / stale_current_restatement** `config/hermes-codex-lane.json#/execute_route_contract/child_model_enforcement/config_surface`
   - 讀到：`"subagentModels/models/selectedModels = pinned to deepseek-v4.1-flash"`
   - 應比對：`"Restatement consistent with active registry routes; no repair applied"`；依據 `config/lane-routing-registry.yaml#/routes`。
   - Says pinned to deepseek; execute_lane_child_models[0] is minimax.
32. **EXECUTE / stale_current_restatement** `config/model-lane-assignment.json#/effective_wiring/execute_dispatch`
   - 讀到：`"scripts/start-hgk-hermes.ps1 -Action Write, invoked with -ModelChain deepseek-v4.1-flash"`
   - 應比對：`"Restatement consistent with active registry routes; no repair applied"`；依據 `config/lane-routing-registry.yaml#/routes`。
   - Says -ModelChain deepseek-v4.1-flash, while active EXECUTE is minimax.
33. **PLAN / stale_current_restatement** `config/model-lane-assignment.json#/assignment/0/rationale`
   - 讀到：`"Revision 19 owner order 2026-10-15: rank-1 default is now opencode-go/glm-5.3-flash (medium) for the in-Hermes PLAN & Orchestrator plane; the GPT arm is exhausted and demoted to a non-default, non-automatic alternate. Prior rationale (revision 18 GPT-6.1_SOL default) preserved in revision_19_reason / rebind_note_revision_18."`
   - 應比對：`"Restatement consistent with active registry routes; no repair applied"`；依據 `config/lane-routing-registry.yaml#/routes`。
   - Says rank-1 opencode-go/glm-5.3-flash; active registry rank-1 openai-codex/gpt-6.1-sol.
34. **VERIFY / SECURITY / stale_current_restatement** `config/model-lane-assignment.json#/assignment/2/supply`
   - 讀到：`"DEFAULT primary arm A = OpenCode Go / glm-5.3-flash; arm B = OpenAI OAuth / gpt-6.1-sol is fallback only. Both arms are medium."`
   - 應比對：`"Restatement consistent with active registry routes; no repair applied"`；依據 `config/lane-routing-registry.yaml#/routes`。
   - Says glm default and gpt fallback; active registry says gpt default.
35. **VERIFY / SECURITY / stale_current_restatement** `config/model-lane-assignment.json#/assignment/2/rationale`
   - 讀到：`"Owner adjudication resolves default PLAN/VERIFY model collision: primary VERIFY arm A is glm-5.3-flash; arm B gpt-6.1-sol is fallback only and may not check a PLAN-made artifact. Provider separation is not required."`
   - 應比對：`"Restatement consistent with active registry routes; no repair applied"`；依據 `config/lane-routing-registry.yaml#/routes`。
   - Says glm primary and gpt fallback; active registry says gpt primary.
36. **EXECUTE / stale_current_restatement** `config/model-lane-assignment.json#/sod/verify_vs_execute_model_separation`
   - 讀到：`"PRESENT on the model axis: EXECUTE is opencode-go/deepseek-v4.1-flash and VERIFY_SECURITY is openai-codex/gpt-6.1-sol, so the maker and the checker are on DIFFERENT models AND different providers."`
   - 應比對：`"Restatement consistent with active registry routes; no repair applied"`；依據 `config/lane-routing-registry.yaml#/routes`。
   - Names EXECUTE deepseek, not current minimax. Separation conclusion remains true; model name is stale.
37. **ALL / stale_current_restatement** `config/model-lane-assignment.json#/sod/provider_separation`
   - 讀到：`"PLAN and EXECUTE now SHARE the opencode-go provider (different models: minimax-m3.1-flash-free vs deepseek-v4.1-flash); VERIFY_SECURITY is on openai-codex. Provider separation therefore survives between the maker planes and the checker, but NOT between PLAN and EXECUTE - recorded, not claimed otherwise."`
   - 應比對：`"Restatement consistent with active registry routes; no repair applied"`；依據 `config/lane-routing-registry.yaml#/routes`。
   - Names PLAN opencode-go/minimax and EXECUTE deepseek; active registry PLAN openai-codex/gpt, EXECUTE opencode-go/minimax.
38. **PLAN / VERIFY / SECURITY / stale_current_restatement** `config/model-lane-assignment.json#/sod/lane_deviation_recorded`
   - 讀到：`"Owner order 2026-10-21: all three lanes on one model. Recorded as SOD006-C4 (PLAN vs VERIFY) and SOD006-C5 (EXECUTE vs VERIFY), both OPEN_OWNER_ORDERED."`
   - 應比對：`"Restatement consistent with active registry routes; no repair applied"`；依據 `config/lane-routing-registry.yaml#/routes`。
   - Says all three lanes on one model; current registry has different EXECUTE model.
39. **EXECUTE / stale_current_restatement** `config/lane-routing-registry.yaml#/sod_invariants/pairs/0/note`
   - 讀到：`"Owner order 2026-10-21 (GPT quota restored): EXECUTE is opencode-go/deepseek-v4.1-flash and VERIFY_SECURITY is openai-codex/gpt-6.1-sol. The models DIFFER and so do the providers, so the maker/checker separation HOLDS on the model axis and is asserted here."`
   - 應比對：`"Restatement consistent with active registry routes; no repair applied"`；依據 `config/lane-routing-registry.yaml#/routes`。
   - Names EXECUTE deepseek, not current minimax.
40. **VERIFY / SECURITY / stale_current_restatement** `config/lane-routing-registry.yaml#/routes/2/selection_authority`
   - 讀到：`"owner-order-20261021-handover-plan-minimax-execute-deepseek"`
   - 應比對：`"Restatement consistent with active registry routes; no repair applied"`；依據 `config/lane-routing-registry.yaml#/routes`。
   - Still names 20261021 handover plan-minimax/execute-deepseek order; authorization_basis names R14 20261022.
41. **EXECUTE (restated in PLAN) / self_contradictory_prose** `config/lane-route-slots.candidate.json#/lanes/0/selection_note`
   - 讀到：`"Owner order 2026-10-21 (GPT quota restored): the PLAN execution model and the Independent Acceptance Officer / VERIFY / SECURITY checker model are BOTH openai-codex/gpt-6.1-sol (GPT 6.1 SOL-MEDIUM, OpenAI OAuth). This SUPERSEDES the earlier 2026-10-21 order that put minimax-m3.1-flash-free on PLAN and VERIFY_SECURITY. The EXECUTE lane is not named by the order and stays on opencode-go/deepseek-v4.1-flash, per the owner's standing clarification. For THIS lane (PLAN) the rank-1 arm is openai-codex/gpt-6.1-sol with reasoning effort medium, and it is the lane's automatic selection. The transport id is the BARE 'gpt-6.1-sol': the OpenAI transport rejects the provider-qualified form 'openai-codex/gpt-6.1-sol' with HTTP 400 'Model is unavailable'. The arms below it stay reachable as fallbacks. A rank-1 arm is a SELECTION, not an acceptance: it says which model the lane dispatches to, not that anything has been accepted."`
   - 應比對：`"EXECUTE rank 1 is minimax, not deepseek"`；依據 `config/lane-route-slots.candidate.json#/lanes/1/ordered_pool/0/model`。
   - The paragraph says EXECUTE stays on deepseek, contrary to current EXECUTE rank-1 minimax.
42. **EXECUTE (restated in EXECUTE) / self_contradictory_prose** `config/lane-route-slots.candidate.json#/lanes/1/selection_note`
   - 讀到：`"Owner order 2026-10-21 (GPT quota restored): the PLAN execution model and the Independent Acceptance Officer / VERIFY / SECURITY checker model are BOTH openai-codex/gpt-6.1-sol (GPT 6.1 SOL-MEDIUM, OpenAI OAuth). This SUPERSEDES the earlier 2026-10-21 order that put minimax-m3.1-flash-free on PLAN and VERIFY_SECURITY. The EXECUTE lane is not named by the order and stays on opencode-go/deepseek-v4.1-flash, per the owner's standing clarification. For THIS lane (EXECUTE) the rank-1 arm is opencode-go/minimax-m3.1-flash-free, and it is the lane's automatic selection. The transport id is the provider-qualified slug 'opencode-go/minimax-m3.1-flash-free'. The arms below it stay reachable as fallbacks. A rank-1 arm is a SELECTION, not an acceptance: it says which model the lane dispatches to, not that anything has been accepted."`
   - 應比對：`"EXECUTE rank 1 is minimax, not deepseek"`；依據 `config/lane-route-slots.candidate.json#/lanes/1/ordered_pool/0/model`。
   - The paragraph says EXECUTE stays on deepseek, contrary to current EXECUTE rank-1 minimax.
43. **EXECUTE / self_contradictory_prose** `config/lane-route-slots.candidate.json#/lanes/1/ordered_pool/0/probe_note`
   - 讀到：`"measured lane arm (round FAR-CLOSURE-20261021): the Codex-CLI lane served this arm at required_arm == served_arm. A PROBE arm is NOT a policy default and must not be selected by an unpinned dispatch; it is an explicitly pinnable measured capability."`
   - 應比對：`"Do not describe a default=true automatic_selection=true arm as not a policy default"`；依據 `config/lane-route-slots.candidate.json#/lanes/1/ordered_pool/0/default`。
44. **EXECUTE (restated in VERIFY_SECURITY) / self_contradictory_prose** `config/lane-route-slots.candidate.json#/lanes/2/selection_note`
   - 讀到：`"Owner order 2026-10-21 (GPT quota restored): the PLAN execution model and the Independent Acceptance Officer / VERIFY / SECURITY checker model are BOTH openai-codex/gpt-6.1-sol (GPT 6.1 SOL-MEDIUM, OpenAI OAuth). This SUPERSEDES the earlier 2026-10-21 order that put minimax-m3.1-flash-free on PLAN and VERIFY_SECURITY. The EXECUTE lane is not named by the order and stays on opencode-go/deepseek-v4.1-flash, per the owner's standing clarification. For THIS lane (VERIFY_SECURITY) the rank-1 arm is openai-codex/gpt-6.1-sol with reasoning effort medium, and it is the lane's automatic selection. The transport id is the BARE 'gpt-6.1-sol': the OpenAI transport rejects the provider-qualified form 'openai-codex/gpt-6.1-sol' with HTTP 400 'Model is unavailable'. The arms below it stay reachable as fallbacks. A rank-1 arm is a SELECTION, not an acceptance: it says which model the lane dispatches to, not that anything has been accepted."`
   - 應比對：`"EXECUTE rank 1 is minimax, not deepseek"`；依據 `config/lane-route-slots.candidate.json#/lanes/1/ordered_pool/0/model`。
   - The paragraph says EXECUTE stays on deepseek, contrary to current EXECUTE rank-1 minimax.

### offset 不是成功行編號

`lane2_EXECUTE.json` 的 usage_offset=30226390、usage_rows_after_offset=2；第一行實際是 401 invalid_api_key，而不是摘要的 200。本次保留整個兩行區段及符合摘要的候選成功行，避免把區段起點誤當成成功請求。這個現象本身不代表 receipt 造假；必須連同第二行及 requestId 一起檢查。

## 未來必留、尚未證明的部分

- 每次 invocation 固定保存 round/workorder/role/engine/arm/rank、宣告 provider/model、transport_model、egress 與設定雜湊。
- 保存 provider usage 的 requestId、conversationId、requestedModel、resolvedModel、provider、status、usage，並與 invocation 建立唯一關聯；不要只挑相同 model 的最後一行。
- 實際 Hermes PLAN 與 SECURITY 必須有自身關聯，或明說只測了替代引擎／共用 checker。
- 從 registry routes 動態導出宣告檢查，涵蓋 assignment、supply_selector、pool 的 transport 與 default/auto；加入真實 unpinned selection 與併發錯配拒絕測試。
- **本次只量測設定、目錄與既存紀錄；沒有新捕捉 live per-call attribution。檔案相同，只能證明檔案相同。未證明全部任務、未來 fallback、模型能力、上游權重或系統整體正確。**

輸出：`lanemodel_fidelity.json`（四份快照、欄位比較、完整不一致及證據索引）、`lanemodel_fidelity.md`、`lanemodel_relay_models.json`、可重跑唯讀量測程式 `lanemodel_measure.py`。四份設定前後 SHA-256 均未變。
