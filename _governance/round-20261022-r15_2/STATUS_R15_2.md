# SBL R15.2 round status — round-20261022-r15_2

task_id: `SBL-R15.2-CONTINUATION-20261022`
branch: `evidence/r15_2-20261022`
claim ceiling: `ROUTEOUT_CANDIDATE + LOCAL_RAW_ONLY`
native_run: `NOT_RUN`
independent_acceptance: `NOT_RUN`
release: `BLOCKED`

## 1. What this round actually did (locally verified, reproducible)

| # | Item | Verdict | Raw evidence |
|---|---|---|---|
| 1 | Source freeze of the 24 normative documents (10 PIPD + 14 SBL) byte-level | `MATCH 24/24` | `SOURCE_FREEZE.json`, `counts` block |
| 2 | Official CAPC bundle located, complete (SKILL + 7 references + schema + script + tests) | `BUNDLE_COMPLETE` | `SOURCE_FREEZE.json.compiler_bundle[10]` |
| 3 | Official CAPC `lint` | `PROMPT_COMPILE_PASS`, 0 errors | `receipts/CAPC_lint.json` |
| 4 | Official CAPC `activation` | `PROMPT_COMPILE_PASS`, 0 errors | `receipts/CAPC_activation.json` |
| 5 | Official CAPC `acceptance` | `PROMPT_COMPILE_PASS`, 0 errors | `receipts/CAPC_acceptance.json` |
| 6 | Official CAPC `compile` | `PROMPT_COMPILE_PASS`, 0 errors, `contract_sha256=414005c1b8c1322bb5fc2d429e6e8e6944d43f21bb66ba01148e168f86828ef3` | `receipts/CAPC_compile.json`, `output/compiler-receipt.json`, `output/thin-prompt.md` (20,799 chars) |
| 7 | Model plan probe, three lanes against the local relay | PLAN `gpt-6.1-sol` HTTP 200 served `gpt-6.1-sol`; EXECUTE `opencode-go/minimax-m3.1-flash-free` HTTP 200 served same; VERIFY `gpt-6.1-sol` HTTP 200 | `receipts/model_PLAN.*`, `receipts/model_EXECUTE.*`, `receipts/model_VERIFY.*` |
| 8 | Hermes Kanban real board and 18 cards (W00..W17) | board `sbl-r15-2-20261022` created, 18 cards created and blocked | `receipts/kanban_create_board.txt`, `receipts/kanban_cards.txt` |
| 9 | R14 obligation ledger read from the native evidence branch | 31 items read, status distribution recorded | `R14_LEDGER_READBACK.json` |

## 2. What this round did **not** do, and why

| Item | Status | First blocking reason |
|---|---|---|
| Native WorkOrder / ECP / RoleBinding / Lease / Permit | `NOT_RUN` | No HGK native issuer ABI is bound on this host for this subject; `APPROVALS.mode` is not a legal auto-permit. |
| Commander-SP real PLAN invocation (C03) | `NOT_RUN` | Requires the native PLAN pre-handoff ABI; a model probe is not an SP invocation. |
| Challenge-SP / independent AO re-execution (C05) | `NOT_RUN` | Requires a frozen candidate produced under a permit plus a distinct checker principal. |
| Fabric active policy consumption (C02) | `TEMP_CLOSED` | Local policy files exist (hashed) but there is no observed HGK consumer readback proving which digest is *active* rather than Stage-1 frozen. |
| SWOF W2 rechallenge → W3 admission → first SWOF PR (C19) | `NOT_RUN` | No SWOF W2 accepted readset and no W3 domain-owner admission on this host. Zero effect taken. |
| Five tools / three ZIPs / three ChatGPT private hosts (C20, C21) | `NOT_RUN` | No host-issued private plugin IDs; a portable ZIP is not a host registration. |
| 50/149/441/38/39/24 semantic closure (C18) | `PARTIAL` (identity only) | Source identity counts are preserved in the contract; per-item live acceptance is not executed. |
| CI / supply chain / release (C22) | `NOT_RUN` | No workflows were modified; no release is claimed. |
| B0/B1/B2 matched performance (C23) | `NOT_RUN` | Requires paired runs on identical workload and hardware. |
| M1..M4 | `NOT_RUN` | All four milestones depend on the native chain above. |

`PROMPT_COMPILE_PASS != RUNTIME_READY != INDEPENDENT_PASS != HOST_INSTALLED != RELEASED`.
Nothing in this round may be read as a product PASS.

## 3. Honest reading of the user-requested model plan

- The three arms are **available** (all three returned HTTP 200 with the exact model id echoed by the relay).
- The HGK lane assignment at `revision 32` binds VERIFY_SECURITY to `opencode-go/deepseek-v4.1-flash`, not to `openai-codex/gpt-6.1-sol`. The requested checker model is therefore *served-able* but **not the currently assigned lane arm**. This is recorded as `TT-R15.2-VERIFY-LANE-SOD006-C6` (OPEN, owner-ordered) and is a registry change that needs a native config WorkOrder — it is **not** a self-service edit.
- Lane model and session interaction model are two planes. The probes above are *transport* evidence for the lane arms; they are not lane bindings, not SP invocations, and not effects.

## 4. Reproduce this round

```bash
python tools/source_freeze.py                     # re-measures all 24 sources
python tools/build_contract_v2.py                 # rebuilds CONTRACT.json from the measured freeze
cd "<CAPC bundle>"
python scripts/prompt_contract_compiler.py lint       CONTRACT.json
python scripts/prompt_contract_compiler.py activation CONTRACT.json
python scripts/prompt_contract_compiler.py acceptance CONTRACT.json
python scripts/prompt_contract_compiler.py compile    CONTRACT.json --out-dir output
```

Expected: four exit-0, one `contract_sha256`, `PROMPT_COMPILE_PASS`.
