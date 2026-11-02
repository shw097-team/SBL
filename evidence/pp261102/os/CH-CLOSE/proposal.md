# rc.2 engineering closeout — proposal

Round `RUN-20261102-GJ02-01`, decision observed 2026-11-03 (Asia/Taipei).

## Why this record exists

The round closed the rc.2 repair work and ended with a **promotion decision**, not a product change.
This record freezes that decision where the next round can reopen it by named evidence instead of by
re-reading a run log. It adds documents only; the code it describes was merged earlier, in other PRs.

## Decision

**`PRE_V2_DESIGN_SIDECAR_READY`**, with `NATIVE_GOLDEN_HOLD` unchanged.

Not `PRE_V2_GENERATION_READY`. Not `NATIVE_GOLDEN_SLICE_PASS`.

The two labels answer different questions:

| label | question |
|---|---|
| `PRE_V2_DESIGN_SIDECAR_READY` | do the design artefacts exist, agree with each other, pass the pre-v2 author gate, and refuse when they should? |
| `PRE_V2_GENERATION_READY` | can an **effect-specific** ECP be produced and admitted, and can the objects a host writes be acknowledged by the canonical reader? |

The round proved the first. It did not prove the second, for two independent reasons:

1. **Effect-specific ECP is unbound** (`EFFECT_REGISTRY_UNBOUND`). The only ECP that exists is the
   generic one from the original writer. A typed effect class needs a pinned original Operation/Effect
   Registry, and no such artefact exists in SBL, PIPD, Fabric or HG-KEOS — the 19 PIPD schema families
   carry no operation-type or effect-class enum, and the one effect mapping inside the original
   pipeline is a path heuristic that the control plan forbids as a classifier.
2. **Canonical ACK covers the writer chain, not the host-authored objects** (`CANONICAL_ACK_HOLD`).
   The natural-goal session wrote four `@2` design objects; the original canonical reader rejects them
   on shape (`PI-PKG/: 'stable_semantic_contract' is a required property`). Canonical ACK exists for
   `01_products/pipd` (`checked 4`, `PASS`). Saying the host produced canonical PIPD objects would be
   false, and that sentence is exactly what `GENERATION_READY` would license.

## What is proven

| Claim | Receipt that carries it |
|---|---|
| rc.2 package identity | candidate zip sha256 `3a9da65…`, 173 members, 14 Skills, CRC OK; sealed input `c4181e24…` untouched (`00_run_manifest/00_run_manifest.json`) |
| Real Codex host install | `codex plugin add sbl-tpm-sp@sbl-pre-primary-local` → *installed, enabled, 0.3.0-rc.2* on codex-cli 0.164.0; isolated `CODEX_HOME`, real `~/.codex` untouched |
| Model route | `deepseek-v4.1-flash` via provider `opencode_go`; host wrote it into `host_notes.md`; lane receipt `served_arm=opencode-go/deepseek-v4.1-flash` |
| Natural-goal routing (M3) | fresh session, no skill named in the goal → three planning documents (`product-requirement.md`, `technical-architecture.md`, `execution-plan.md`) and four `@2` objects (`PI`, `PD`, `ECP`, `PlannedTQAEP`), plus a 2-line fix with two **new** tests and no edited expectation |
| Author gate (M2) | `pre_v2_gate_r2.py bundle_r2` → exit 0, `AUTHOR_CONTRACT_CONSISTENT`, requirements 2, cases 2, `effect_state=DESIGN_ONLY_NOT_ADMITTED`, `checker=NOT_RUN`, `release=FAIL_CLOSED`; three negatives fail closed |
| PIPD four-object denominator (M2b) | merged `7073fe2` (PR #26); `validate` returns `scope`/`complete`/`missing`/`required`; `--require-four` fails closed with a `DENOMINATOR` finding; full suite 664 passed / 20 skipped |
| Design-level governance (M4) | two dependent design steps, **0** human approvals, byte-identical reruns (KnownAnswer reuse, candidate `93387936…`), 6/6 design-level refusals |

## What is NOT proven

- **Effect-specific ECP binding** — no original registry, issuer or grant; none was fabricated.
- **Canonical ACK for host-authored objects** — `@2` design objects are not canonical objects.
- **Live TQAEP / FUO** — no protected checker, runner or product consumer (`ORIGINAL_CHECKER_UNBOUND`).
- **Native effect** — the only reachable HG-KEOS surface is a lane-model mandate carrying `nonce=None`,
  which is not an effect grant (`NATIVE_GOLDEN_HOLD`).
- **ChatGPT private host** — no official interface; `PRIVATE_HOST_HOLD`.

Any sentence that needs one of these five is outside this record's ceiling.

## No code change

This change is documents only. No file in SBL, PIPD-LS-SP, Fabric or HG-KEOS is modified by it, and no
test, schema, gate, adapter or validator byte is changed here. The behaviour described above was merged
in PR #15 / #18 / #20 (SBL) and #26 / #28 (PIPD-LS-SP) before this record was written. If this record
and the code ever disagree, the code wins and the record is the defect.

## Not in scope

- **No Native qualification.** No issuer, protected checker or publisher was reachable, and this record
  does not substitute a local proxy for one.
- **No Release.** `release=FAIL_CLOSED` stays; nothing here promotes a candidate to a release.
- **No new governance plane.** The round reused the existing gate and the existing refusal surface.
  Adding a second approval path to make the numbers look better is explicitly not wanted.
- No fix for the two recorded host defects (`HOST-124` sandbox/pwsh alias; `FIND-VALIDATE-CLOSURE`,
  which M2b already answers in the validator), and no change to the OpenCode Go key pool state.

## Claim ceiling

`PRE_V2_DESIGN_SIDECAR_READY` + `NATIVE_GOLDEN_HOLD`. Local pre-primary use of the Codex flow stays
limited to the verified design-level path. Everything in "What is NOT proven" stays unclaimed until a
distinct-principal artefact exists for it.
