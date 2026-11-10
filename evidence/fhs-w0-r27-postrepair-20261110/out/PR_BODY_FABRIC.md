# Fabric r27 — admit the r26 governance mirror for navigation (digest bound from the mirrored file)

Base `main@3b47550efce282f513965aa207b899913743eaa3`. **Additive only** — every existing manifest entry is untouched.

## The finding this closes

`EC-R26-013`: the r26 mirror was merged by PR #49, but a merged file is not an admission. `INTEGRATION/MANIFEST.json` carried no r26 entry and the mirror's own status still said `candidate / not policy loaded`, while `FHS-NAV/v2` declares `effect_permission = NONE`. Any session could read the mirror while nothing recorded that it had been admitted, by whom, for what.

## What this branch adds

1. `INTEGRATION/MANIFEST.json` — one new admission entry: subject path, `bytes` and `sha256` **recomputed from the mirrored file in this repo** (not copied from a report), source `shw097-team/SBL@1cb8abb0ef118bdd80b08961fd9ca54c657881b9`, `effect_permission: NONE`, `admission_state: ADMITTED_FOR_NAVIGATION_ONLY`, `admitted_by`, `admitted_at`, and a `claim_ceiling`.
2. `INTEGRATION/FHS/W0/r26-admission/MIRROR_STATUS_FABRIC.md` — the mirror's own status, updated to say exactly what changed and what did not (navigation only; no write authority).
3. `INTEGRATION/FHS/W0/r26-admission/F0_POLICY_CONSUMER_TRACE.json` — a consumption trace in the repo's own `F0_POLICY_CONSUMER_TRACE` shape: policy artifact → digest → consumer → decision → evidence.
4. `INTEGRATION/FHS/tools/validate_manifest_admission.py` + `INTEGRATION/FHS/tests/test_manifest_admission.py` — the validator with its negatives.

## Executed negatives (the point of the change)

| case | injected fault | observed |
|---|---|---|
| `NEG-F1` | entry digest does not match the mirrored file | `MIRROR_DIGEST_MISMATCH`, non-zero |
| `NEG-F2` | entry claims `effect_permission: WRITE` while `FHS-NAV/v2` says `NONE` | `EFFECT_PERMISSION_ESCALATION`, non-zero |
| `NEG-F3` | `admission_state` incompatible with the declared permission | `ADMISSION_STATE_PERMISSION_MISMATCH`, non-zero |
| `NEG-F4` | an edit that rewrites instead of appending an entry | `ADDITIVE_ONLY_VIOLATION`, non-zero |
| positive | the admission as shipped | exit 0 |

`pytest INTEGRATION/FHS/tests/test_manifest_admission.py` passes, and the commander re-ran the validator in a fresh process with its own evidence path.

## Not claimed

- No policy **load**: `effect_permission` stays `NONE`; Fabric has no loader and this PR does not invent one.
- No owner ratification of the admission, no external acceptance, no write authority of any kind.
- The SBL remote at `1cb8abb0…` was pinned from the round's own record; this repo cannot verify a foreign commit's contents, and does not pretend to.
- Nothing in `HG-KSEOS` consumes this entry yet; that consumer readback is a separate, owner-side step.
