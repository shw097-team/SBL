# L2 — FHS-3L&M binding hard-entry repair (closes EC-R26-002 / resume predicate R26-04)

Read `_COMMON.md` first. Worktree: `C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-3lm` (branch r27/fhs3lm-binding).
Target: `evidence/fhs-w0-r26-repair-20261109/tools/fhs_3lm.py` — repair in place. It owns NO routing; it reads HGK.

## Reproduced defects
- Hardcoded `HGK = C:\Projects\Agent_Workspace\HG-KSEOS` — that path does not exist on this host (real HGK is `C:/Projects/Agent_Workspace/FHS/HG-KSEOS`), so `--menu` crashes with a traceback (measured: exit 1). EC-R26-002 defect 1.
- `--bind` writes `BINDING_DIR/{lane}_{slot}.json` -> two sessions in the same slot overwrite each other (E02).
- `--assert` checks registry SHA + arm presence only: not `pool_sha256`, not the retired ledger, not numeric epoch, not session/work/nonce/ttl (E03/E04).
- `epoch()` parses `registry_epoch:` / `registry_version:`, which do not exist; the real YAML has `epoch: 41` (epoch 33 on main). The numeric epoch never reaches the binding.
- `retired_arms()` reads `pool["retired_arms"]`; on HGK **main (epoch 33)** that key is `null`, so the retirement ledger must be read from BOTH the pool and the registry's retirement section, and disagreement -> `HOLD_REGISTRY_POOL_DRIFT`.

## Required repair
1. **Discovery, no hardcoded absolute path**: resolve the HGK control plane from explicit `--hgk-root`, then env `HGK_ROOT`, then a discovery file `config/hgk-root.txt` shipped beside the tool, then fail closed `ERR_HGK_ROOT_UNRESOLVED` (exit 8). Refuse a root lacking `config/lane-routing-registry.yaml`. Record resolved root + `discovery_source` in every binding.
2. **Numeric epoch**: parse top-level `epoch:` as an integer; also record `status:` (IN_FORCE|CANDIDATE) and `contract_epoch` when present. No numeric epoch -> `ERR_EPOCH_UNRESOLVED` (exit 7).
3. **Session-unique atomic binding**: `--bind LANE SLOT --run-id --session-id [--work-id] [--ttl]` writes `lanes/bindings/<run_id>/<lane>_<slot>_<nonce>.json` created with `O_CREAT|O_EXCL` (collision -> `BINDING_ALREADY_EXISTS`, exit 10; never overwrite). Record carries: `binding_id` (= sha256 of canonical body), `run_id, session_id, work_id, lane, slot, provider, model, transport_model, pool_rank, policy_epoch (int), registry_sha256, pool_sha256, retired_ledger_sha256, nonce, bound_at, expires_at (default ttl 3600s), plane: LANE_CONTROL_PLANE, not_a_session_pin: true`.
4. **`--assert` re-verifies ALL of**: registry sha256, numeric epoch equality, pool sha256 equality, retired ledger (arm not retired), arm still in that lane's pool, lane/slot match, `expires_at` not passed, record body digest == `binding_id`, session/work present. Codes: `EPOCH_DRIFT`, `POOL_DIGEST_DRIFT`, `RETIRED_ARM`, `ARM_LEFT_POOL`, `BINDING_EXPIRED`, `BINDING_TAMPERED`, `HOLD_REGISTRY_POOL_DRIFT`.
5. **`--assert-arm` / `--menu` / `--bind` / `--assert` read the same single registry and the same retired ledger**; a retired arm still present in a pool is a drift HOLD, not a pass.
6. Keep exit codes 0/2/6/7/8/9; add 10 for binding collisions. No new router, no new registry, no session pin.

## Mandatory executed cases (each with captured log + exit)
- `E01` `--menu` against a real HGK root -> exit 0, 9 slots, `epoch=41` numeric, all 9 admitted. Use `--hgk-root C:/Projects/Agent_Workspace/FHS/HG-KSEOS` only if that working tree is on the epoch-41 branch; otherwise use the epoch-41 config copy under `C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-bridge` (branch r27/epoch41-bridge). State which you used and pin the registry sha256.
- `E02` two binds, same lane/slot, different `--run-id`/`--session-id` -> two distinct files + two distinct `binding_id`s, no overwrite; a third bind with the SAME run_id -> `BINDING_ALREADY_EXISTS` exit 10.
- `E03` mutate a COPY of the pool (never the real one) -> `--assert` -> `POOL_DIGEST_DRIFT`, non-zero exit.
- `E04` retired arm `opencode-go/mimo-v2.6-pro` -> `RETIRED_ARM` exit 9 against the epoch-41 ledger; and against the epoch-33 registry (no pool ledger) the registry retirement section must still decide it.
- `E05` same arm chosen for PLAN and VERIFY -> allowed and recorded (`same_arm_lanes: true`), no refusal.
- `E06` bind with `--ttl 0` -> `--assert` -> `BINDING_EXPIRED`.
- `E07` edit a COPY of a binding's `model` -> `BINDING_TAMPERED`.
- `E08` pool lists an arm the registry retires -> `HOLD_REGISTRY_POOL_DRIFT`.
Ship all of it as a runnable `evidence/fhs-w0-r26-repair-20261109/tools/selftest_fhs_3lm.py` (stdlib only, `subprocess`, exit non-zero on any mismatch) and run it.
