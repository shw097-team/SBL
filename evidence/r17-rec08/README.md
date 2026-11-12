# R17 REC08 — evidence package (candidate, not native acceptance)

**Claim ceiling: `CANDIDATE_TESTED`.** Nothing in this package is an HGK Native Permit, a Fabric
Active Designation, an independent AO verdict, a Host UAT or a Release. Those signatures belong to
their own principals and are not present here.

Subject: HG-KSEOS `086a940`, Fabric `bb06b7a6`, SBL `10d510f7`. Published from SBL only, under
`evidence/r17-rec08/`; HGK and Fabric patches live in their own repositories and are referenced by
SHA, never copied here.

## What is in the package

| Path | What it is | Claim it supports |
|---|---|---|
| `tools/checker_workarea.py` | builds an isolated, **writable** checker area from an exact subject SHA | a regression suite can be executed by a different principal without the sandbox `PermissionError` |
| `tools/row_resume.py` | per-row resume queue + park-and-continue driver for the 145-ID ledger | the register can RESUME, not just report |
| `tools/lane_preflight.py` | separates RELAY_UNREACHABLE / PROVIDER_QUOTA / MODEL_UNSERVED / ARM_NO_NONCE / EXECUTOR_TIMEOUT | a lane failure is never rounded up to "model unavailable" |
| `kind_factory.py`, `lifecycle.py`, `run_three_kinds.py` | builds and drives real `CLI_TOOL`, `AGENT_SKILL`, `SIMPLE_AGENT` products | three new intents reach a real install/invoke/deny/uninstall cycle |
| `receipts/F1_PREFLIGHT_10105.json` | live relay handshake, 2.08 s, nonce echoed | `required_arm == served_arm` for EXECUTE at transport level |
| `receipts/F3A_SERVED_ARM_TEST.json` | 24 checks over served-arm identity | provider-qualified / bare / empty / same-value / foreign / unknown-model / nonce each behave as specified |
| `receipts/F2_CHECKER_FULL_SUITE.json` | full suite in the checker area at `086a940` | 717 passed, 3 skipped, 4 xfailed, 0 PermissionError |
| `receipts/F3D_THREE_KINDS.json` | 17 behavioural checks over three generated products | each Kind's POS **and** NEG observed from the installed artefact |
| `receipts/F4_ROW_RESUME.json` | per-row runs of the open obligation set | which rows advanced on real evidence, which parked and why |

## Reproduce

```bash
# 1. lane identity (needs the 10105 shim up)
python tools/lane_preflight.py --base http://127.0.0.1:10105/v1 \
       --model deepseek-v4.1-flash --nonce R17REC08-F1-01

# 2. checker area: the three environment conditions that make it EQUIVALENT
python tools/checker_workarea.py --subject 086a9402189a2bb0ac3b198a7a9805b3dcbe38d8 \
       --env PIPD_ROOT=C:/Projects/Agent_Workspace/PIPD \
       --mkdir worktrees --seed var/FAR-LANE-REUSE-RCA-20261015

# 3. three Kinds
python run_three_kinds.py
```

## Two environment facts a checker must know

1. **Depth-dependent anchors.** `PIPD_ROOT`, the sibling `TEST_RESULTS/` and the tmp root are all
   resolved by tree depth. In a worktree they silently point at the wrong place, so a naive run
   reports ~54 failures that have nothing to do with the change. Export them explicitly.
2. **Scratch must live outside the worktree.** A scratch dir *inside* it makes `git status` dirty
   and a working-tree hygiene test then fails for a reason the harness invented.

## Known gaps (stated, not rounded up)

- No live EXECUTE end-to-end run through Codex CLI in this round; the transport and the identity
  gate are proven, the bounded-writer turn is not.
- The `C` (CheckRun) family has no row probes: those rows park as `PROBE_UNBOUND`, which is an
  instrument gap on the agent side, not an owner blocker.
- 3 tests skip in the checker area for lack of untracked runtime state; the repo run has 0 skips.
- `sbl-todo` fixtures were **not** used; the three products come from three new intents.
