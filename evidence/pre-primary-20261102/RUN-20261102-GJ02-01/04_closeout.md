# 04 — Closeout, RUN-20261102-GJ02-01

**Verdict: `PRE_V2_DESIGN_SIDECAR_READY` + `NATIVE_GOLDEN_HOLD`.**
Not `PRE_V2_GENERATION_READY` and not `NATIVE_GOLDEN_SLICE_PASS`.

## What was actually proven

| Layer | Result | Hard evidence |
|---|---|---|
| Package identity | PASS | sealed input `c4181e24…` untouched; candidate `3a9da65…`, 173 members, 14 Skills, CRC OK |
| Real Codex host install | **PASS** | `codex plugin add sbl-tpm-sp@sbl-pre-primary-local` → *installed, enabled, 0.3.0-rc.2*; local marketplace manifest accepted (the schema that failed last round: `{"name":…, "plugins":[{"name":…, "source":{"source":"local","path":"./plugins/…"}}]}`) |
| Model route | PASS | `deepseek-v4.1-flash` via provider `opencode_go` (`https://opencode.ai/zen/go/v1`); the run itself wrote `configured model: deepseek-v4.1-flash; provider: opencode_go` into `host_notes.md`; HG-KSEOS lane receipt `served_arm=opencode-go/deepseek-v4.1-flash` |
| Ordinary goal (no plan hints) | PASS | rounding defect fixed, 2 insertions / 1 deletion, `pytest` 2 passed, test expectations untouched, exit 0 |
| Explicit skill trigger | PASS | session read `skills/*/SKILL.md` + references from the installed cache, produced `host_notes.md` and the three SPECs |
| Nontrigger | PASS | unrelated goal → 0 references to `sbl-tpm-sp`/`SKILL.md`, exit 0 |
| Rollback | PASS | remove → *not installed* (cache dir gone) → reinstall → *installed, enabled*; other marketplaces and real `~/.codex` untouched |
| 3 SPECs | PASS at design ceiling | `AUTHOR_DESIGN_ONLY`, `DESIGN_CANDIDATE`, real source sha of `src/demo/billing.py` |
| Original PIPD writer | PASS | PI 17 atoms with real clause spans and original oracle ids; PD bound to real HEAD `70757870` (dirty recorded); ECP produced; `validate` → PASS, checked 4, **closure FULL** |
| Planned vs Live | PASS with ceiling | no receipt → `TQ_SOD` exit 2; arbitrary receipt → `TQAEP_DESIGNED`, `independent_acceptance=NOT_GRANTED` |

## What is held, and why

- **Effect-specific ECP**: the canonical `compile-ecp` produced a generic ECP. Binding a typed effect needs a pinned original Operation Registry — `EFFECT_REGISTRY_UNBOUND`.
- **PlannedTQAEP @2 through the author gate**: not produced for this slice, so the four objects shipped here are canonical PI/PD/ECP + a design-ceiling TQAEP, not the `@2` bundle set.
- **TQAEP usability**: no protected checker, runner or product consumer → `ORIGINAL_CHECKER_UNBOUND`.
- **Owner / autonomy / recovery**: no broker, no work spine → `OWNER_BROKER_UNBOUND`, `SPINE_UNBOUND`, `NO_EFFECT_EXECUTED`.
- **Native GJ02**: `NATIVE_GOLDEN_HOLD`. The only reachable HGK surface is a lane-model mandate (`nonce=None`), which is not an effect grant. The sandbox commit is a test fixture, not a governed world effect.
- **A/B cost**: `NO_COMPARABLE_BASELINE`; no savings percentage is claimed.

## Two host defects found (not patched, owner decision)

1. `FIND-HOST-124`: with `--sandbox workspace-write`, Codex resolves `pwsh.exe` to the WindowsApps store alias and every `exec_command` is rejected as *blocked by policy*; the turn then hangs to a 124 timeout. Same goal with `danger-full-access` exits 0. Workaround used for this run only.
2. `FIND-VALIDATE-CLOSURE`: the original `validate --bundle` returns `checked=3, closure=FULL` when the TQAEP is missing, so "closure FULL" alone cannot prove all four objects exist.

Plus one environment finding: two of the three pooled OpenCode Go keys return `429 GoUsageLimitError`, one returns `401`; only one key answers 200 for `deepseek-v4.1-flash`.

## Shortest next unlock

1. Bind a pinned original Operation Registry (or the Fabric/HGK reader that owns it) → closes G04 and lets the effect-specific ECP run.
2. Produce the `@2` four objects and run `scripts/pre_v2_gate_r2.py` on the bundle → closes the last gap to `PRE_V2_GENERATION_READY`.
3. For Native: one bounded owner pre-authorization + original issuer/checker on an isolated repo.

## Reproduction

```text
# host
CODEX_HOME=<isolated> codex plugin marketplace add <case root with .agents/plugins/marketplace.json>
CODEX_HOME=<isolated> codex plugin add sbl-tpm-sp@sbl-pre-primary-local
CODEX_HOME=<isolated> OPENCODE_GO_API_KEY=<local key> codex exec -C <sandbox repo> --sandbox danger-full-access --json "<goal>"

# original writer
pipd init / intake / compile-pi / bind-pd / compile-ecp / compile-tqaep / validate  (see 01_products/pipd)
```
