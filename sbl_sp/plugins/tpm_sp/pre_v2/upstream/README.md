# Original PIPD owner candidate

Base: `shw097-team/PIPD-LS-SP` main
`f6335a94157c61da75d92121d14c43feb413e981`.

The patch changes original `src/pipd_ls_sp/cli.py`, `pipeline.py`, package data,
and adds the MIT SBL author adapter (vendored verbatim with its closed Sidecar
schemas) plus bounded tests. Original PIPD software remains Apache-2.0. The
modified files include PRE-V2 modification notices. No raw governing documents,
donor implementations, credentials, or runtime stores are included.

```text
git switch -c candidate/pre-v2-owner <base-sha>
git apply --check pipd-pre-v2.patch
git apply pipd-pre-v2.patch
python -m unittest tests.test_pre_v2_adapters tests.test_pre_v2_planned_reader -v
python -m unittest tests.test_tqaep_design_positive tests.test_claim_ceiling_shape tests.test_atomic_requirements -v
```

Set `PYTHONPATH` to the checkout's `src` or install that original project in an
isolated environment. New options preserve legacy command defaults. The actual
CLI has 13 commands (13 including `repair`; original E7 forbids a 14th);
historical descriptions saying 14 are not an exact inventory. The canonical
registry remains 19 families. The new
schemas are separate Sidecars, not replacement canonical contracts.

This is a local owner candidate, not a merged PIPD main change or a release.
Synthetic Operation/Case registries cannot establish native authority. The full
repair PD scope remains UNBOUND where the original CLI admits only `src/**`.
