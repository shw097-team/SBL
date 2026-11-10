# HG-KSEOS r27 — epoch-41 route/retire content port on a main-derived branch, and a mechanical FHS entry guard

**DRAFT candidate only.** No merge, no force-push, no default-branch change, no host cutover. `main` is untouched.

> **Why draft:** the entry guard is enforced by default, and the 122 pre-existing dispatcher tests that
> dispatch an *unbound* process now fail closed with `FHS_ENTRY_ASSERT_REQUIRED` — the exact refusal the
> finding asked for. No other code changed behaviour (blast radius: 122 failed / 127 passed, all with the
> same code). Migrating those fixtures onto a bound-entry fixture is a named resume predicate and needs a
> governance decision for the tests that dispatch synthetic arms the control plane does not admit. This PR
> must not be merged until that decision is recorded.

## Why a branch derived from `main` and not a merge of `config/plan-mimo-flash-20261109`

The published claim under review was `main_is_ancestor = true`, `commits_ahead = 327`. It is refuted on a full local clone:

| measurement | result |
|---|---|
| `git merge-base acd9196f 86f40ec` | **no output, exit 1** |
| `git merge-base --is-ancestor`, both directions | **exit 1 / exit 1** |
| root of `acd9196f` (main) | `a2389c138cf51641c95494c3fa551c249a6c0058` |
| root of `86f40ec` (epoch-41 branch) | `ec58a0be385b2b387bb7fb336aceef90259e7a1a` |
| `git rev-list --left-right --count acd9196f...86f40ec` | `90	328` |
| shallow / grafts / replace refs | none present; the DAG read is the stored DAG |

Two lineages with **different roots**. `328` is the branch's whole commit count and `90` is main's, so there is no "ahead by" relation and no fast-forward range. The full record, including the parent lines from `git cat-file -p` and the ref carriers of each root, is in `H0_DAG_RECONCILIATION.json`.

Strategy adopted: **content port from `main`** (`H2`), not a history merge. The 2,470 changed paths were classified at the control-plane surface only: 14 config files + 2 tools → `PORT 3`, `REPLAY 2`, `DO_NOT_MERGE 11`, and 2,456 paths recorded once as `OUT_OF_SCOPE_FOR_THIS_PR` (ledger: `H1_CONFIG_DELTA_LEDGER.json`). Issuer keys, ACLs, front-door policy, dependencies, licences and evidence are **not** ported here — that is `H3`, a separate owner decision.

## What this branch changes

1. `config/lane-routing-registry.yaml` → `epoch: 41` (numeric), `status: IN_FORCE` as the owner-ordered candidate, `contract_epoch: 34`.
2. `config/lane-route-slots.candidate.json` → the nine owner slots, with the retirement ledger present:
   - PLAN: `openai-codex/gpt-6.1-sol`(1), `opencode-go/deepseek-v4.1-flash`(2), `opencode-go/glm-5.3-flash`(3), `opencode-go/mimo-v2.6-flash`(4), `nvidia/z-ai/glm-5.3-flash`(5), `nvidia/deepseek-ai/deepseek-v4.1-flash`(6)
   - EXECUTE: `opencode-go/deepseek-v4.1-flash`(1), `opencode-go/mimo-v2.6-flash`(2), `openai-codex/gpt-6-luna`(3), `nvidia/deepseek-ai/deepseek-v4.1-flash`(4)
   - VERIFY_SECURITY: `openai-codex/gpt-6.1-sol`(1), `opencode-go/mimo-v2.6-flash`(2), `opencode-go/deepseek-v4.1-flash`(3), `opencode-go/glm-5.3-flash`(4), `nvidia/deepseek-ai/deepseek-v4.1-flash`(5)
   - `retired_arms["opencode-go/mimo-v2.6-pro"] = {retired_epoch: 41, ordered_by: OWNER, ordered_at: 2026-11-09, replacement: opencode-go/mimo-v2.6-flash}`
3. `config/model-lane-assignment.json` → projected from the registry for the same epoch.
4. `scripts/lane_epoch_validate.py` + `tests/test_lane_epoch_validate.py` — the negative-capable validator.
5. `scripts/fhs_entry_guard.py` + `tests/test_fhs_entry_guard.py` + a single hook at the spawn boundary of `scripts/hgk-lane-dispatch.py` — a **mechanical** pre-dispatch check, replacing the claim that a line in `AGENTS.md` is an entry contract.

## Executed evidence

- `lane_epoch_validate.py` positive → exit 0: epoch numeric 41, nine slots admitted, retired arm in no pool.
- Negatives, each with its own log: `RETIREMENT_DRIFT`, `EPOCH_UNPARSEABLE`, `RETIRED_ARM_IN_POOL` → all non-zero.
- `pytest tests/test_lane_epoch_validate.py` → pass.
- Entry guard: a **fresh process** calling the dispatcher with no binding is refused `FHS_ENTRY_ASSERT_REQUIRED` **before any spawn**; a bound run passes the guard and stops only at the next environmental stage; token replay `FHS_ENTRY_TOKEN_CONSUMED`; epoch drift `FHS_ENTRY_EPOCH_DRIFT`; retired arm `FHS_ENTRY_RETIRED_ARM`.
- Commander's independent re-execution in fresh processes: `L4.*` and `L5.*` checks matched their expected exit codes.

## Measured on the live relay (this host, not a claim about any host)

| lane | arm | outcome |
|---|---|---|
| PLAN | `openai-codex/gpt-6.1-sol` | **served**, exit 0, nonce present, 60.16 s |
| EXECUTE | `opencode-go/deepseek-v4.1-flash` | **served**, exit 0, 20.61 s |
| VERIFY_SECURITY | `openai-codex/gpt-6.1-sol` | **served**, exit 0, 23.26 s |
| PLAN rank 2 / rank 4, EXECUTE rank 2 / rank 3, VERIFY rank 2 | — | refused **pre-spawn** `ERR_ARM_NOT_IN_ASSIGNMENT` |

That refusal is a finding in its own right: `model-lane-assignment.json#lane_chains` lists six PLAN arms while the dispatcher's assignment reader resolves PLAN as **primary-only** (`fallbacks_declared: false`, `alternates_are_operator_selectable: false`). Pool membership, projection and assignment disagree — a "9/9 admitted" menu is **not** nine assignable slots. It is recorded here rather than repaired by relaxing a guard.

## Pre-existing defects on `main` (baseline, not introduced here)

On pristine `main`: the repo's drift reader reports 22 fatal findings, and `tests/test_lane_policy.py` is already 2 failed / 4 passed. Baselines are kept with the round (`evidence/L4/baseline_*`). This PR does not turn that suite green, and does not edit the test to make it.

## Not claimed

No host cutover, no `ActualServed` beyond the three rows above, no merge to `main`, no claim that any other session or desktop app is now bound by the guard — the guard proves interception inside **this repo's dispatcher**; another host must adopt the same ABI.
