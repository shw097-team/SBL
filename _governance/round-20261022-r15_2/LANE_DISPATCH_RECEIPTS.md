# Lane dispatch receipts (sanctioned HGK dispatcher)

> All rows below are **transport/lane-level** results. None of them is an Independent Acceptance Officer
> PASS, and none certifies a work package. `--cwd` status is now stated per dispatch (AO-F04).

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

## cwd discipline, per dispatch (AO-F04)

| dispatch | --cwd given? | effective cwd | consequence |
|---|---|---|---|
| PLAN (rank 2) | **no** | `C:/Projects/Agent_Workspace/HG-KSEOS` | read-only sandbox, no write observed; still a governed-repo cwd and must be disclosed |
| EXECUTE #1 (rank 1) | **no** | `C:/Projects/Agent_Workspace/HG-KSEOS` | wrote a file into HG-KSEOS, then timed out → `TT-R15.2-HGK-EXECUTE-CWD-ESCAPE` |
| EXECUTE #2 (rank 1) | yes | round directory | wrote only its declared file |
| EXECUTE #3, guarded (rank 1) | yes | round directory | whole-tree guard: added 6, removed 0, modified 0; exactly one writer-attributable |
| VERIFY (rank 2) | yes | round directory | read-only, spawned commands with exit 0 (read-only is NOT broken) |
| VERIFY non-leading (rank 2) | yes | round directory | independent evidence standard, own verdict |

## Non-circular check

`receipts/dispatch/VERIFY_nonleading2.json`: the brief carries only a liveness nonce and no expected verdict or
schema. Its answer accepts the writer claim **within the recorded snapshot scope** and states that an
unrestricted "nothing else was touched" is not proven — the honest reading of a before/after snapshot pair.
