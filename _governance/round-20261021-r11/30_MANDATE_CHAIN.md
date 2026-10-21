# 30 · Model Mandate Chain（車道平面 vs 會話平面）

## 1. Owner 指令（本次任務原文）

- PLAN：`GPT 6.1 SOL-MEDIUM`（OPEN AI OAuth）
- Codex bounded writer / EXECUTE：`DeepSeek V4.1 Flash`（OPENCODE GO），轉交 CODEX CLI
- Independent Acceptance Officer / VERIFY / SECURITY：`GPT 6.1 SOL-MEDIUM`（OPEN AI OAuth），轉交 CODEX CLI

## 2. 現地宣告（HGK epoch 29）

| 面 | PLAN | EXECUTE | VERIFY_SECURITY |
|---|---|---|---|
| `config/lane-routing-registry.yaml`（epoch 29, CANDIDATE） | `opencode-go/minimax-m3.1-flash-free`（rank1；`openai-codex/gpt-6.1-sol` 為 fallback1） | `opencode-go/deepseek-v4.1-flash` | `openai-codex/gpt-6.1-sol` (medium) |
| `config/lane-route-slots.candidate.json`（rev16） | rank1 minimax / **rank2 `gpt-6.1-sol`** | rank1 `deepseek-v4.1-flash` | rank1 `gpt-6.1-sol` |
| HEAD commit | `b22706e` `lanes(r10): PLAN and EXECUTE swap under the handover mandate` | | |

→ **PLAN 面存在 Owner 指令 vs 宣告面的實質衝突**（`O-R11-004`）。依 R11 §2.1/§7.1，不得自改 registry，也不得靜默換模型；本輪採 **role-mandate chain**：每次 dispatch 顯式 `--force-rank` + `--require-arm`，並在 receipt 留下 `required_arm == served_arm`。

## 3. 本輪三次探針（`mandate_probes/`）

| lane | 指令 | 要求 arm | 服務 arm | 耗時 | usage | nonce | receipt |
|---|---|---|---|---|---|---|---|
| PLAN | `--force-rank 2` | `openai-codex/gpt-6.1-sol` | `openai-codex/gpt-6.1-sol` | 3.71s | 200 | `HGK_PLAN_OK r11planprobe4417` | `PLAN_gpt61.json` |
| EXECUTE | `--force-rank 1` | `opencode-go/deepseek-v4.1-flash` | `opencode-go/deepseek-v4.1-flash` | 2.73s | 200 | `HGK_EXECUTE_OK r11execprobe4417` | `EXECUTE_deepseek.json` |
| VERIFY_SECURITY | `--force-rank 1` | `openai-codex/gpt-6.1-sol` | `openai-codex/gpt-6.1-sol` | 10.66s | 200 | `HGK_VERIFY_OK r11verprobe4417` | `VERIFY_gpt61.json` |

共同傳輸設定（三次一致）：`codex_executable=C:/Users/user/AppData/Local/OpenAI/Codex/bin/6257d9e8f63c0f2b/codex.exe`、`codex_home=C:\Users\user\AppData\Local\HG-KSEOS\codex-hermes`、`relay_base=http://127.0.0.1:10101/v1`、`sandbox=read-only`。

## 4. 觀察（都寫進 findings）

- `gpt-6.1-sol` 不在 relay `/v1/models`（92 筆）清單內，但 completion 仍 200 並帶 usage（`O-R11-005`）⇒ catalog ≠ 上游真相；Codex 印 `Model metadata not found. Defaulting to fallback metadata` ⇒ 能力主張上限僅「可路由/可服務」。
- 既有備註：`openai-codex` 傳輸必須用 **裸 id** `gpt-6.1-sol`；`openai-codex/gpt-6.1-sol` 會 400。本輪 `transport_model` 由 pool 提供（裸 id），與此一致。
- stderr 的 `websocket 426 Upgrade Required` 為常態（relay 只服務 HTTP），非故障。

## 5. 邊界（claim ceiling）

三次 receipt 只證明：token 可路由、該 turn 被服務、usage 對帳相符、要求 arm 未被降級。
**不證明**：Commander-SP / Challenge-SP 被調用；任何 WorkOrder/ECP/Permit 存在；任何 subject 被驗收；同模型跨角色即具 SoD（PLAN 與 VERIFY 同為 `gpt-6.1-sol`，只有 process/role 分離，模型軸未分離）。

## 6. 若要消除 drift（交 Owner）

1. 由 HGK issuer 對 lane rebind 發專項 WO，把 PLAN rank1 改為 `openai-codex/gpt-6.1-sol` 並同步 `model-lane-assignment.json` 的 `registry_epoch/revision` 與 90 個 drift pin → epoch 30；或
2. 明確書面承認「PLAN 以 mandate chain 逐輪覆蓋」為常態，並把該事實寫入 registry 的 `authorization_basis`（仍需 issuer 授權）。
