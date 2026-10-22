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

## 7. Execution addendum — the stipulated model plan was actually exercised (and stopped on a hard blocker)

This section supersedes any earlier wording that implied the three arms were only probed. All rows below are backed by
raw files under `receipts/` and `workers/`.

| Stipulated arm | What was really run | Raw receipt | Verdict |
|---|---|---|---|
| PLAN = GPT 6.1 SOL-MEDIUM | `gpt-6.1-sol` via relay `/v1/chat/completions`, full 18-package brief; returned 13,028 chars / 4,858 completion tokens incl. a 35-edge DAG | `receipts/PLAN_commander_dag.json`, `.content.json`, `.http` | REAL RUN (served id matched) |
| VERIFY / SECURITY = GPT 6.1 SOL | `gpt-6.1-sol` adversarial review of this very status + TT + contract summary; returned 4,364 chars / 2,279 tokens with HIGH findings, including a real contradiction inside TT-R15.2-LEDGER-DIVERGENCE | `receipts/VERIFY_challenge_gpt61sol.*` | REAL RUN — but NOT an AO pass, and not the registry-bound checker arm |
| EXECUTE = Codex CLI + MiniMax M3.1 Flash | `codex.exe` 0.163.0-alpha.11 really launched (`codex exec ... -s read-only --ephemeral`), reached a model, exit 0 — then every `CreateProcess` was rejected by host policy, so it could read nothing | `workers/codex/RECEIPT.json` | **HARD BLOCKER** |
| VERIFY carrier = Codex CLI | same binary, same spawn rejection; relay also lacks `/v1/responses` (404) and direct upstream returns 401 `api.responses.write` | `workers/codex/RECEIPT.json` | **HARD BLOCKER** |
| SWARM | 4 parallel leaf workers (delegation `deleg_7b546db6`), 62 artefacts | `WORKER_RECEIPTS.json` | REAL RUN (workers inherit `deepseek-v4.1-flash`, not a lane model) |
| KANBAN | board `sbl-r15-2-20261022`, 18 cards, all blocked `NO_NATIVE_WORKORDER_PERMIT` | `receipts/kanban_cards.txt` | REAL (no dispatch) |
| OPENSPEC | `openspec validate --strict --all --no-interactive` exit 1 — pre-existing change `far-r12-20261021` has no delta specs | `workers/openspec/RECEIPT.json` | FAIL (real repo defect) |
| GSTACK | 24 probes, no provider anywhere; `~/.gstack` is state residue only | `workers/gstack/NOFIT_OR_RECEIPT.json` | NOFIT |

### Stop reason (per the user's own rule)

> 若無法使用以上模型方案，你必須直接暫停任務，並告知用戶！

Two of the three stipulated arms (EXECUTE, VERIFY/SECURITY) are carried by Codex CLI. On this host Codex CLI
reaches a model but **cannot spawn a single process**, and the local relay does not serve the Responses API it
needs. A Codex bounded write would therefore be unverifiable even if a permit existed. The round is stopped here
with `round_state = NO_LEGAL_PROGRESS_PENDING_OWNER_CARRIER_DECISION`; `TT-R15.2-CODEX-CLI-UNUSABLE` carries the
measured basis and two remediation options.

Nothing was signed. No repository effect was taken. The FACT that PLAN and VERIFY ran on `gpt-6.1-sol` raises the
evidence ceiling for those two arms only — it does not make the round a PASS.

### New blockers found by this round's own execution

- `TT-R15.2-CODEX-CLI-UNUSABLE` (HARD_BLOCKER)
- `TT-R15.2-R14-EVIDENCE-GAP`: only 12 of 17 R14 DONE items have all declared evidence present in the branch
  (20 PRESENT / 10 PARTIAL / 1 MISSING across 31).
- `TT-R15.2-OPENSPEC-STRICT-FAIL`: `far-r12-20261021` has no deltas.
- `TT-R15.2-GSTACK-NOFIT`.

### Self-check cross-reference

`workers/codex/raw/independent_check.json` is explicitly labelled
`INDEPENDENT_HERMES_CHECK_NOT_CODEX_EXEC`: 28/28 manifest files byte- and sha256-match, 0 mismatches, CONTRACT.json
valid. It is not a Codex result and must never be cited as one.

## 8. Correction — both stipulated Codex arms DO work (this supersedes the stop in §7)

§7 stopped the round on the belief that Codex CLI could not execute anything on this host. **That was wrong.** The
worker invoked `codex.exe` with `--ignore-user-config` (throwing away the proven lane home) and `-s read-only` (which
on this host refuses every process spawn). Reusing the established HGK recipe makes both stipulated arms run end to
end, and they were then used for real work:

| Stipulated arm | Command recipe | Real result |
|---|---|---|
| EXECUTE = Codex CLI + MiniMax M3.1 Flash | isolated copy of sealed `CODEX_HOME`, layered `-p exe`, `model = opencode-go/minimax-m3.1-flash-free`, `base_url http://127.0.0.1:10101/v1`, `wire_api = responses`, `-s danger-full-access` | `pwsh -Command 'echo SHELL_GATE_OK'` **succeeded in 391ms**; created exactly `workers/codex_writer/EXECUTE_WRITER_RECEIPT.md`; guard `MODIFIED=0 REMOVED=0` outside the write set |
| VERIFY = Codex CLI + GPT 6.1 SOL | same home, layered `-p ver`, `model = gpt-6.1-sol` | exit 0; independent audit returned `{"verdict":"PASS","addition_only":true,"overclaims":[]}` |
| (bonus) PLAN = GPT 6.1 SOL | relay `/v1/chat/completions` | 35-edge DAG, 4,858 completion tokens |

Raw logs: `workers/codex_lane/log_execute.log`, `log_verify.log`, `log_writer.log`, `log_checker.log`,
`guard_before.txt` / `guard_after.txt`.

### What was genuinely blocking, and what still is

- **Found and disclosed:** `TT-R15.2-FRONTDOOR-SANCTIONED-DRIFT` — the sealed front door on 10100 pins
  `deepseek-v4.1-flash` at compile time while the lane declaration now says `minimax-m3.1-flash-free`, so it refuses to
  start (`ERR_EXEC_FRONTDOOR_SANCTIONED_DRIFT`). The working runs above therefore point Codex at the shared relay 10101
  directly, which **bypasses the isolation layer the front door exists to provide**. This is a real, disclosed deviation,
  not a resolved issue.
- **Still blocking a full R15.2:** no native WorkOrder / Permit, no SWOF W3 admission, no ChatGPT host IDs, pre-existing
  `openspec` failure on `far-r12-20261021`, and gstack absent. The carrier was never the blocker for those.

Claim ceiling unchanged: `native_run NOT_RUN`, `independent_acceptance NOT_RUN`, `release BLOCKED`. What changed is that
the two arms are now demonstrated carriers with a demonstrated bounded write and a demonstrated independent check — which
is a strictly larger evidence base than §7 claimed, and still not a PASS.

## 9. All three stipulated arms now run through the sanctioned HGK dispatcher

The models are no longer invoked by hand. Every arm below went through
`HG-KSEOS/scripts/hgk-lane-dispatch.py` against pool `config/lane-route-slots.candidate.json` rev 20, with
`--force-rank` + `--require-arm` + a fresh nonce, and `--cwd` pinned to this round directory.

| lane | forced rank | required arm | served model | nonce | ok | secs |
|---|---|---|---|---|---|---|
| PLAN | 2 | `openai-codex/gpt-6.1-sol` | `gpt-6.1-sol` | yes | **PASS** | 18.3 |
| EXECUTE | 1 | `opencode-go/minimax-m3.1-flash-free` | `opencode-go/minimax-m3.1-flash-free` | yes | **PASS** | 20.9 |
| VERIFY_SECURITY | 2 | `openai-codex/gpt-6.1-sol` | `gpt-6.1-sol` | yes | **PASS** | 19.9 |

Two refusals proved the gate is real rather than decorative: `--require-arm gpt-6.1-sol` alone returns
`ERR_LANE_REQUIRED_ARM_ABSENT` (the pool's arm key is `openai-codex/gpt-6.1-sol`), and a run with no nonce in an
agent message cannot pass even at exit 0.

The VERIFY arm then judged the EXECUTE arm's artefact:

```json
{"nonce":"VERIFY-NONCE-3D90F2B6","receipt_present":true,"lines":4,
 "declared_model":"opencode-go/minimax-m3.1-flash-free","overclaims":[],"verdict":"PASS"}
```

### Incident this produced, disclosed in full

The **first** EXECUTE dispatch omitted `--cwd`, so the writer ran with cwd = `HG-KSEOS` and created
`HG-KSEOS/workers/codex_lane/EXEC_DISPATCH_RECEIPT.md` — a write inside a governed repository with no permit. The run
then timed out (300s, `ok=False`), i.e. an **effect with a failed receipt**. It was contained: bytes and tree captured
(`receipts/incidents/`), the untracked `workers/` directory removed, and `git -C HG-KSEOS status --porcelain` verified
empty with HEAD unchanged at `1760fb4`. Re-dispatched with `--cwd` pinned, the same lane finished `ok=True` in 20.9s and
the file landed in the evidence worktree instead. Filed as `TT-R15.2-HGK-EXECUTE-CWD-ESCAPE`.

### Ceiling (unchanged)

`native_run NOT_RUN` — no native WorkOrder/Permit id was issued, so no work package may claim completion.
`independent_acceptance NOT_RUN` — the checker shares this host and session (SOD006-C6 open). `release BLOCKED`.
What changed is that the role→model binding the user mandated is now demonstrated **through the lane plane**, with the
orchestrating session model demonstrably different from all three lane models.
