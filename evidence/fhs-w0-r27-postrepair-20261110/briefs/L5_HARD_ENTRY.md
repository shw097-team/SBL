# L5 — FHS-3L&M native pre-dispatch hard entry (EC-R26-001 / R26-03)

Read `_COMMON.md` first. Worktree: `C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-hook` (branch r27/fhs-entry-hook, cut from `origin/main`).

## The finding
The r26 external challenge (BLOCKER EC-R26-001) is precise: `fhs_3lm.py --bind/--assert` exists, but nothing makes another session / fresh PID / Codex child call it **before** a dispatch. A prompt line in `AGENTS.md` is not a mechanical interception. The host must validate a `SessionBinding` **before** it spawns.

## What to build (repair the existing dispatcher — do NOT build a second router)
The single sanctioned spawn point in this repo is `scripts/hgk-lane-run.sh` -> `scripts/hgk-lane-dispatch.py`. Also present: `scripts/runtime_role_binding_assert.py`.

1. `scripts/fhs_entry_guard.py` (new, stdlib only) — the mechanical gate:
   - `assert-entry --binding <path> --lane LANE --arm PROVIDER/MODEL [--require-bound]`
   - It re-reads the HGK registry + pool (`config/lane-routing-registry.yaml`, `config/lane-route-slots.candidate.json`), recomputes their sha256, and calls the SBL binding reader **by path only** (`--binding-reader`, default resolved from a discovery file `config/fhs-3lm-path.txt`) so the tool stays single-sourced and never re-implements the predicate.
   - Fail-closed codes, each with its own exit: `FHS_ENTRY_ASSERT_REQUIRED` (no binding supplied / absent) exit 20, `FHS_ENTRY_BINDING_INVALID` exit 21, `FHS_ENTRY_EPOCH_DRIFT` exit 22, `FHS_ENTRY_POOL_DRIFT` exit 23, `FHS_ENTRY_RETIRED_ARM` exit 24, `FHS_ENTRY_ARM_MISMATCH` exit 25, `FHS_ENTRY_BINDING_EXPIRED` exit 26, `FHS_ENTRY_GUARD_UNRESOLVED` exit 27 (reader path missing).
   - A `--guard-token <nonce>` mode: the guard writes a one-shot, run-scoped capability file (`var/fhs-entry/<run_id>.json`, `O_CREAT|O_EXCL`, TTL 300 s, binds binding_id + lane + arm + pid) and the dispatcher REFUSES to spawn without a valid unspent token for its own run_id (`FHS_ENTRY_TOKEN_REQUIRED` exit 28, replay `FHS_ENTRY_TOKEN_CONSUMED` exit 29).
2. Wire it into `scripts/hgk-lane-run.sh` and `scripts/hgk-lane-dispatch.py` at the spawn boundary: no token -> no spawn, and the refusal happens BEFORE any child process is created (prove it: the log must show zero `codex` spawns and zero relay attempts).
3. `AGENTS.md`: add a short, non-authoritative note under the governed-execution section that the entry is now mechanical, naming the two scripts. Do not restate policy, do not create new authority.

## Mandatory executed cases (each with captured log + exit code + raw sha256)
- `E01` FRESH PROCESS BYPASS: `python scripts/hgk-lane-dispatch.py --lane EXECUTE ...` invoked directly with **no** `--fhs-binding` -> must refuse with `FHS_ENTRY_ASSERT_REQUIRED`, exit 20, **no model call, no child spawn**. Then show `pgrep`/`tasklist`-equivalent evidence or the dispatcher's own attempt log proving zero attempts. This is the finding's own falsifier — make it real.
- `POS-E01b` CONTROL: the same dispatcher invoked WITH a valid unspent token + a valid binding (bound against the epoch-41 config copy at `C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-bridge`, using the L2 lane's repaired `fhs_3lm.py` at `C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-3lm/evidence/fhs-w0-r26-repair-20261109/tools/fhs_3lm.py`) must get PAST the entry guard and fail only at the next, environment-dependent stage (relay unavailable is acceptable and expected — record its exact error). If the repaired 3LM tool is not yet present when you run, build against the current one and re-run once it lands; state which.
- `E02` token replay: consume a token, then reuse -> `FHS_ENTRY_TOKEN_CONSUMED`, exit 29.
- `E03` epoch drift: token bound at registry sha X, registry file replaced with a copy of different bytes -> `FHS_ENTRY_EPOCH_DRIFT` exit 22.
- `E04` retired arm: token/arm = `opencode-go/mimo-v2.6-pro` -> `FHS_ENTRY_RETIRED_ARM` exit 24.
Ship as `tests/test_fhs_entry_guard.py` (pytest, stdlib + pytest only) plus a plain `scripts/selftest_fhs_entry_guard.py` that runs the five cases standalone and exits non-zero on any mismatch. Run BOTH.

## Scope limits
- Do not touch `config/` (L4 owns it), do not touch `src/`, do not modify `scripts/hgk-lane-dispatch.py` beyond the single guard hook at the spawn boundary (keep the diff minimal and reversible), no network, no model calls required for the negatives.
- State clearly in your result what remains unreachable: the guard proves interception **inside this repo's dispatcher**; desktop-app sessions and other hosts must adopt the same ABI, which this repo cannot enforce on their behalf.
