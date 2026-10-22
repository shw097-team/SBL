# Lane dispatch receipts (sanctioned HGK dispatcher)

Driven by `HG-KSEOS/scripts/hgk-lane-dispatch.py` with `--force-rank` + `--require-arm` + `--nonce`
against `config/lane-route-slots.candidate.json` rev 20, `--cwd` pinned to this round directory.

| lane | forced rank | required arm | served transport model | nonce | ok | secs | receipt |
|---|---|---|---|---|---|---|---|
| PLAN | 2 | `openai-codex/gpt-6.1-sol` | `gpt-6.1-sol` | True | PASS | 18.3 | `receipts/dispatch/PLAN_gpt61sol.json` |
| EXECUTE | 1 | `opencode-go/minimax-m3.1-flash-free` | `opencode-go/minimax-m3.1-flash-free` | True | PASS | 20.94 | `receipts/dispatch/EXECUTE_minimax_cwd.json` |
| VERIFY_SECURITY | 2 | `openai-codex/gpt-6.1-sol` | `gpt-6.1-sol` | True | PASS | 19.89 | `receipts/dispatch/VERIFY_gpt61sol_judgement.json` |

## Why this is the lane plane and not the session plane

The orchestrating Hermes session runs `deepseek-v4.1-flash`. Every model above was selected by the **pool
rank inside the dispatcher**, not inherited from the session: PLAN and VERIFY were pinned to `gpt-6.1-sol`
(pool rank 2, declared `transport_model: gpt-6.1-sol`) and EXECUTE to `opencode-go/minimax-m3.1-flash-free`
(pool rank 1). The dispatcher refuses a run whose required arm is absent from the lane pool
(`ERR_LANE_REQUIRED_ARM_ABSENT`) and refuses a run whose nonce never appears in an agent message — so a
200-with-no-work cannot pass as a dispatch.

## §verify judgement on the writer receipt

```json
{"nonce":"VERIFY-NONCE-3D90F2B6","receipt_present":true,"lines":4,
 "declared_model":"opencode-go/minimax-m3.1-flash-free","overclaims":[],"verdict":"PASS"}
```

This is a lane-level check by the mandated checker model. It is **not** an Independent Acceptance Officer
PASS: the checker principal shares this host and this session, so SOD006-C6 remains open.
