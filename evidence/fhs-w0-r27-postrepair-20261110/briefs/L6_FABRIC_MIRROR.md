# L6 — Fabric governance-mirror admission for r26 (EC-R26-013 / R26-09)

Read `_COMMON.md` first. Worktree: `C:/Projects/Agent_Workspace/FHS_R26_WT/fabric-mirror` (branch r27/r26-mirror-admission, cut from `origin/main` = 3b47550).

## The finding
PR #49 merged the r26 mirror, but the mirror is still `candidate / not policy loaded`: `INTEGRATION/MANIFEST.json` has no r26 entry, and `FHS-NAV/v2` declares `effect_permission=NONE`. A merged file is not an admission.

## What to do
1. Read, in this order, and quote the rule you are complying with: `AGENTS.md` (repo root), `INTEGRATION/FHS/README.md`, `INTEGRATION/FHS/repository-map.json`, `INTEGRATION/MANIFEST.json`.
2. Add an explicit, minimal admission record for the r26 mirror to `INTEGRATION/MANIFEST.json`: the mirrored subject's identity (`bytes`, `sha256` of the raw r26 document — verify the value from the mirrored file itself, do not copy a number from a report), the source repo + commit (`shw097-team/SBL@1cb8abb0ef118bdd80b08961fd9ca54c657881b9`), the mirror path, `effect_permission`, `admission_state`, `admitted_by`, `admitted_at`, and `claim_ceiling`. Preserve every existing entry byte-for-byte; only add. Validate the result is still parseable JSON and that any schema in `schemas/` that governs the manifest still validates (find and use it).
3. Update the mirror's own status file (`.../MIRROR_STATUS_FABRIC.md` wherever the r26 mirror lives in this repo — locate it) from `candidate/not policy loaded` to a state that states exactly what changed: `ADMITTED_FOR_NAVIGATION_ONLY` (recommended) or `ADMITTED_FOR_CONSUMPTION` — pick one, justify it, and keep `effect_permission` consistent with `FHS-NAV/v2`. Do not silently upgrade navigation to write permission.
4. Write a policy-consumption trace in the repo's own F0 pattern (`stage/RP002-STAGE-HGK/F0/F0_POLICY_CONSUMER_TRACE.json` is the reference shape): `policy_artifact`, `sha256`, `consumer`, `decision`, `evidence`. The consumer here is the FHS navigation surface; the decision is `ADMIT_MIRROR_FOR_NAVIGATION`.
5. `NEG-F1` — executed negative: feed the manifest validator a candidate entry whose `sha256` does not match the mirrored file -> must refuse with `MIRROR_DIGEST_MISMATCH`, non-zero exit. `NEG-F2` — an entry with `effect_permission: WRITE` while `FHS-NAV/v2` says `NONE` -> `EFFECT_PERMISSION_ESCALATION`, non-zero exit. Write the validator as `INTEGRATION/FHS/tools/validate_manifest_admission.py` (stdlib) and run both negatives + one positive.
6. `tests/` entry runnable with `C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe -m pytest`.

## Limits
- Fabric is a contract surface: no daemon, no second control plane, no policy invention. If a schema forbids the new entry shape, report that and use the schema's own extension point — do not edit the schema to fit.
- Do not claim "FHS-NAV is now effective for all sessions". The claim ceiling is: this repo admits the mirror for navigation, with the digest bound.
