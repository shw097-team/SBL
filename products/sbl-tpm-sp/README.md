# sbl-tpm-sp (candidate identity)

A portable **plugin identity**, not a compiler. It exists so the SBL TPM surface can be shipped as one plugin
that consumes the `pipd-ls-sp` distribution built from [`integrations/pipd/`](../../integrations/pipd) — the
single modifiable copy of `pipd_ls_sp`.

**Status:** `CANDIDATE_PENDING_D1`. Nothing here is published, released, or authoritative.

## What it may do

- declare its identity, version and the distribution it consumes (`plugin.json`);
- carry the eight PIPD skills derived from `integrations/pipd/skills/` at build time;
- act as the SBL-side entry point **after** the owner records D1 (canonical cutover).

## What it must not do

- hold a second, independently patchable copy of `pipd_ls_sp`;
- compile, sign, or issue anything on its own authority;
- stand in for a WorkOrder, Permit, Grant, policy decision, HGK admission, host load or release.

## Wiring (post-D1, not in this candidate)

1. `sbl-v01` declares a versioned dependency on the built `pipd-ls-sp` wheel (optional extra, not a duplicated
   module tree);
2. the adapter imports `pipd_ls_sp` from the installed distribution and maps TPM intents onto its 13 commands;
3. the plugin's skill bundle is produced by one build script from `integrations/pipd/skills/`, so the eight
   skills are never hand-maintained twice.

The decision that turns this identity into a shipped plugin is recorded in
[`docs/pipd-migration/U04-CUTOVER.md`](../../docs/pipd-migration/U04-CUTOVER.md).
