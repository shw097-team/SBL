# L4 — HGK history reconciliation H0 + main-derived epoch-41 bridge (EC-R26-005, EC-R26-006 / R26-07, R26-08)

Read `_COMMON.md` first. Worktree: `C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-bridge` (branch r27/epoch41-bridge, cut from `origin/main` = acd9196f).

## H0 — already measured by the commander (reproduce and extend, keep the raw logs)
Published claim under review: `main_is_ancestor=true`, `commits_ahead=327`.
Measured on this host against the real clone `C:/Projects/Agent_Workspace/FHS/HG-KSEOS`:
- `git merge-base acd9196f 86f40ec` -> no output, exit 1 (NO common ancestor)
- `git rev-list --max-parents=0 acd9196f` -> `a2389c138cf51641c95494c3fa551c249a6c0058`
- `git rev-list --max-parents=0 86f40ec` -> `ec58a0be385b2b387bb7fb336aceef90259e7a1a`
- `git rev-list --left-right --count acd9196f...86f40ec` -> `90	328`
So the two lineages are DISJOINT at the root; `327` is not a fast-forward range and `main_is_ancestor=true` is false.

Required H0 evidence file: `.../out/H0_DAG_RECONCILIATION.json` with, for BOTH commits: full sha, `git cat-file -p` parents line, root commit, `git rev-list --count`, `git log -1 --format=%T` tree sha, the merge-base result + exit, the left-right counts, `is_shallow_repository`, and any `.git/shallow`, `info/grafts`, `refs/replace/*` findings. Verdict field: `SAME_ROOT | DISJOINT | UNKNOWN` (expected DISJOINT — confirm or correct with raw output).

## H1 — difference classification (bounded, not all 2470 files)
`git diff --name-only acd9196f 86f40ec | wc -l` = 2470 changed paths. Do NOT classify all 2470.
Classify the **config/ control-plane surface only** (14 files, `git diff --stat ... -- config/`) plus `scripts/lane_policy_reconcile.py` and the retirement tool. Emit `.../out/H1_CONFIG_DELTA_LEDGER.json`: one row per config file with `path, main_sha256, branch_sha256, disposition (PORT|REPLAY|REIMPLEMENT|DO_NOT_MERGE), reason`. Everything outside `config/` must be listed once as `OUT_OF_SCOPE_FOR_THIS_PR` with the count, never silently dropped.

## H2 — bridge branch (this worktree): port ONLY the P0 route+retire authority
From `origin/main` (epoch 33), bring in the epoch-41 authority content as a *content port*, not a cherry-pick of the branch history:
1. `config/lane-routing-registry.yaml`: `epoch: 41`, `status: IN_FORCE` (this is the owner-ordered candidate; the file already carries `authorization_basis` prose — extend it with the r27 bridge note and the owner order of 2026-11-09 that admitted `mimo-v2.6-flash` to PLAN rank 4 and retired `mimo-v2.6-pro`), `contract_epoch: 34`.
2. `config/lane-route-slots.candidate.json`: the nine slots exactly as the epoch-41 branch carries them —
   PLAN: `openai-codex/gpt-6.1-sol`(1), `opencode-go/deepseek-v4.1-flash`(2), `opencode-go/glm-5.3-flash`(3), `opencode-go/mimo-v2.6-flash`(4), `nvidia/z-ai/glm-5.3-flash`(5), `nvidia/deepseek-ai/deepseek-v4.1-flash`(6);
   EXECUTE: `opencode-go/deepseek-v4.1-flash`(1), `opencode-go/mimo-v2.6-flash`(2), `openai-codex/gpt-6-luna`(3), `nvidia/deepseek-ai/deepseek-v4.1-flash`(4);
   VERIFY_SECURITY: `openai-codex/gpt-6.1-sol`(1), `opencode-go/mimo-v2.6-flash`(2), `opencode-go/deepseek-v4.1-flash`(3), `opencode-go/glm-5.3-flash`(4), `nvidia/deepseek-ai/deepseek-v4.1-flash`(5);
   plus `retired_arms`: `{"opencode-go/mimo-v2.6-pro": {retired_epoch:41, ordered_by:"OWNER", ordered_at:"2026-11-09", reason:"wrong model family for this lane set; never selectable", replacement:"opencode-go/mimo-v2.6-flash"}}` and `status/epoch = 41` numeric.
   Copy the branch file's own bytes where possible (`git show 86f40ec:config/<path>`) so the port is byte-faithful, then re-apply only what main's schema requires.
3. `config/model-lane-assignment.json` + `config/lane-arm-aliases.json`: keep them consistent with the registry. If `scripts/lane_policy_reconcile.py` regenerates projections, run it and record the diff rather than hand-editing projections.
4. Do NOT port issuer keys, ACLs, dependencies, licenses, or anything outside `config/` in this PR (that is H3, a separate owner decision).

## Mandatory negatives (executed, with logs)
- `NEG-H1` a registry claiming `epoch: 41` whose pool still lists `opencode-go/mimo-v2.6-pro` -> your validator must refuse, code `RETIREMENT_DRIFT`.
- `NEG-H2` `epoch` non-numeric (e.g. `epoch: forty-one`) -> `EPOCH_UNPARSEABLE`.
- `NEG-H3` a pool whose PLAN rank-4 arm is `mimo-v2.6-pro` while the registry retires it -> refuse (`RETIRED_ARM_IN_POOL`).
- `POS-H4` the ported epoch-41 config -> validator exit 0, 9/9 slots admitted, epoch numeric 41, retired arm absent from every pool.
Write the validator as `scripts/lane_epoch_validate.py` (stdlib only) plus `tests/test_lane_epoch_validate.py` runnable with `C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe -m pytest`. Do NOT edit existing tests to pass.

## Do not
- No `git merge`, no `--allow-unrelated-histories`, no force push, no default-branch change, no edits under `src/` or `evidence/`.
- Do not claim the epoch is effective on any host: this PR is a candidate that must pass the repo's own CI and the owner's merge decision.
