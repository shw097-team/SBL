# R8 — EXECUTE re-bound to MiniMax M3.1 Flash

Round id: `SBL-R8-EXECUTE-MINIMAX` · evidence branch `evidence/r7-20261021-c7`

## 1. The mandate, and whether it was usable

| lane | mandated model | proven serving | rank |
|---|---|---|---|
| PLAN | GPT 6.1 SOL-MEDIUM (OpenAI OAuth) | `gpt-6.1-sol` | 1 |
| EXECUTE | MiniMax M3.1 Flash (OPENCODE GO) | `opencode-go/minimax-m3.1-flash-free` | 1 |
| VERIFY / SECURITY | GPT 6.1 SOL-MEDIUM (OpenAI OAuth) | `gpt-6.1-sol` | 1 |

The pause clause (`若無法使用以上模型方案，你必須直接暫停任務`) was treated as a gate, not a formality. Each arm was dispatched **before** any governed surface was touched, with a nonce and a usage receipt:

- EXECUTE was probed at its then-rank 2 and came back `ok=true`, nonce echoed, usage row 200, 3.71 s.
- PLAN and VERIFY were probed the same way on `openai-codex/gpt-6.1-sol`.

All three answered, so the round continued. The pause clause did not fire.

## 2. Lane plane vs session plane

This chat runs `deepseek-v4.1-flash` via `opencode-go`. That is the **session interaction plane**. It is recorded here as such and is **not** offered as evidence for any lane. Every lane claim in §1 comes from its own dispatcher receipt with its own nonce — not from a `config.yaml` that happens to name a model.

## 3. What moved

EXECUTE rank-1 `deepseek-v4.1-flash` → `minimax-m3.1-flash-free`, across all five governed surfaces at once:

- dispatch-time pool, routing registry (route / arms / fallbacks), assignment `lane_chains`
- the sealed lane declaration `config/hermes-codex-lane.json`
- the runtime declaration `config/hermes.json`

`deepseek` is **demoted to fallback 1 and kept** — a re-binding deletes nothing. PLAN and VERIFY are untouched. Registry epoch 26 → 28.

## 4. Three defects found on the way — all of them had passed a gate

**R8-D1.** The drift gate read **zero findings** while the two runtime declarations contradicted the policy surfaces. Each projection's pin still matched the file it pointed at; those files still said `deepseek`. The gate was satisfied and the system was incoherent.

> A clean drift gate is evidence that **pins match files**, not that the surfaces agree.

**R8-D2.** Resolving the `hermes-binding /provider_route/model` debt entry bumped the registry epoch 27 → 28 while the assignment still declared 27. The drift gate missed it — its `/registry_epoch` pin still matched the assignment. The **dispatcher's `ERR_LANE_STALE_EPOCH`** caught it.

> An epoch is a **joint** invariant. Pinning it on one side only makes a one-sided bump invisible.

**R8-D3.** The registry's EXECUTE `fallbacks` list **dropped** the demoted primary instead of demoting it to first fallback. This is the same class as a defect found in an earlier round — which means that repair fixed the artifact and left the generator.

> When a defect recurs after a targeted repair, fix the code path that produces it.

## 5. Conformance — measured, not asserted

Measured against a **checkout-of-HEAD baseline**, same suite, same environment:

| | passed | failed | subtests |
|---|---|---|---|
| baseline (HEAD config) | 575 | 21 | 90 |
| after this round | **580** | **16** | 90 |

**0 new failures. 5 baseline failures now pass.** The 16 remaining are pre-existing and unrelated to the mandate: a stale codex path inside one fixture, a stale HEAD pin, the `w3_solution` stub-banner cases, and M08's foreign-surface case. **They are not claimed fixed.**

## 6. Install → bootstrap → detect → accept

- **HERMES** — `sbl-v01 0.1.1rc1` installed into the canonical Hermes venv (140 → 141 packages, zero runtime dependencies), imports clean, three console scripts present.
- **Stack** — 14 components / 3 principals; `doctor` clean; `selftest` **9/9 including two negative cases**, so it cannot pass on the happy path alone.
- **HGK** — harness adapter probe `ROOT_READY` on 6/6 checks; adapter installed with digest-pinned files; `doctor` clean; ABI `hgk-harness-abi/1`.
- **FABRIC** — no SBL install target. Not attempted, not claimed.

## 7. What this does NOT prove — read this before quoting any of the above

- **Not a host install.** The stack reports `host_install_state=NOT_INSTALLED`; the adapter reports `claim_ceiling=HOST_PENDING`. A standalone install is not a host install.
- **No native effect.** The ABI itself declares `native_effect`, `permit_signing`, `workorder_admission` as `not_provided`; the probe reports `native_effect=NOT_GRANTED`.
- **Not an acceptance.** Exit 0 from an install or a doctor is not an acceptance verdict. R7's independent checker verdict remains `INCONCLUSIVE — NOT ACCEPTED`, honestly mapped to HGK `FAIL`.
- **Full contract still OPEN / PARTIAL.** Native PI/PD/ECP, the ChatGPT 3 host plugin, 149 children, 38 surfaces, cross-host and a signed `PASS_CHALLENGE` remain unclosed.

## 8. Repo hygiene defect, disclosed

`tests/test_matrix_d_full.py`, `tests/test_role_binding_enforcement.py` and `tests/test_execute_luna_route.py` are **untracked** in HG-KSEOS. The mandate update was applied to them on disk so the suite reflects the new order, but they were **not staged**: adding ~800 lines of another party's uncommitted test code under this commit would misattribute authorship.

The consequence is concrete: **a clean checkout cannot reproduce the 580 / 16 figure** until those three files are tracked. Only `tests/test_lane_policy.py` was committed. This is recorded rather than papered over by a convenient `git add`.

## 9. Receipts

| file | contents |
|---|---|
| `LANE_MANDATE_R8.json` | mandate, gate proof, plane separation, rebind, readback, live probes, drift, D1–D3, conformance baseline comparison, disclosures |
| `INSTALL_BOOTSTRAP_R8.json` | wheel digest, host target, stack bootstrap/doctor/status/selftest, HGK probe/adapter/doctor, what is and is not proven |

**Claim ceiling:** `CANDIDATE_ONLY` lane re-order under owner authority, plus a `STANDALONE_ONLY` install measured on this host. Not a native issuer signature, not an acceptance, not a pool promotion to `ACTIVE`. The lane arms are measured **available and serving** — availability is not acceptance.
