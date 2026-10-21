# Running the conformance suite (HG-KSEOS)

This file exists because the literal command quoted in earlier round documents **does not run on this
host**. Measured twice on 2026-10-21 at `HG-KSEOS@b22706e`.

## The command

```bash
cd C:/Projects/Agent_Workspace/HG-KSEOS
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="C:/Projects/Agent_Workspace/HG-KSEOS/src"
./.venv/Scripts/python.exe -m pytest tests -q -p no:cacheprovider --tb=no -rf
```

- `PYTHONPATH=src` is **required**: the venv does not install the `hg_kseos` package, so a bare
  `pytest tests` dies during collection with `ModuleNotFoundError: No module named 'hg_kseos'`.
  `pip install -e .` is an equivalent alternative; `PYTHONPATH` is the non-mutating one.
- `--timeout=900` is **rejected** (`unrecognized arguments`): `pytest-timeout` is not installed.
- `-p no:cacheprovider` avoids writing `.pytest_cache` into the tree; `PYTHONDONTWRITEBYTECODE=1`
  avoids `__pycache__`.
- `--tb=no -rf` prints the failing test ids without per-test tracebacks — the ids are what you need
  for triage, the full traceback is reproducible on demand.

## A count is only valid together with the tree state

Record, every time: `git rev-parse HEAD`, `git status --porcelain | wc -l`, the untracked test count,
and the exact command. Two runs of the same command on the same tree reproduce each other; a count
taken on a different tree does not.

Measured baseline (2026-10-21, `b22706e`, **dirty**: 7 modified + 291 untracked, including 9 untracked
test modules):

```
18 failed, 578 passed, 90 subtests passed in 143.58s
```

An earlier round recorded `580 passed / 16 failed` on the same HEAD. **The two are not comparable**:
the difference is other authors' uncommitted files, not a regression.

## Reading the failures

| Cluster | Tests | Meaning |
|---|---|---|
| Lane declaration surface (13) | `test_lane_policy::test_registry_and_projection_shape`, `test_far_lane_fix_20261015` (5), `test_execute_luna_route` (2), `test_matrix_d_full::M07/M08` (3), `test_role_binding_enforcement::test_prespawn_require_arm_omission_derives_mandatory_arm` | registry / pool rank-1 contradicts the current owner mandate |
| Doc projection (4) | `test_task013_hermes_v020_closure::test_cov_11_06_source_text_unchanged`, `test_task014_named_method_closure::test_config_resolves_scheme_b_appdata_runtime`, `test_task015_coherence_closure` (3) | documentation/projection drift against the live config |
| Worktree scope (1) | `test_c2_case_run::test_r4_only_allowed_files_changed` | the dirty worktree itself — **not** a product regression |

Fix the declaration surfaces and the doc projections before treating any of these as product defects.
