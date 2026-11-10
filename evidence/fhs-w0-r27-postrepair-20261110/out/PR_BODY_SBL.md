# FHS W0 r27 — post-repair change set for the r26 external-challenge findings

**This PR is a candidate. It is not an acceptance, not a release, and not an in-force control plane.**
Base: `main@1cb8abb0ef118bdd80b08961fd9ca54c657881b9`. Subject under repair:
`FHS_PIPD-LS-PKG_W0_r26` (668,540 B raw / 667,205 B LF, sha256 `09c666da…`).

## What the external challenge found, and what this branch does about it

| Finding | Class | This branch |
|---|---|---|
| `EC-R26-003` G29 accepts a missing candidate binding, a fabricated raw digest, and JSON `1` as a boolean | BLOCKER-class false green | `tools/verify_quorum.py` now requires exact `bool`, per-vote `candidate_sha256`/`source_sha256`/`clause_id`/`property`/`raw_path`/`raw_sha256`/`timestamp`/`session_id`/`process_id`, re-hashes the raw transcript, dedupes on lane **and** process. New codes: `MISSING_CANDIDATE_BINDING`, `RAW_DIGEST_MISMATCH`, `RAW_EVIDENCE_UNREADABLE`, `VOTE_TYPE_INVALID`, `PROCESS_ID_DUPLICATE`. |
| `EC-R26-002` `fhs_3lm.py` overwrites bindings per slot, checks registry SHA only, never parses `epoch:` | HIGH | Session-unique `O_CREAT\|O_EXCL` bindings under `lanes/bindings/<run_id>/`, dual SHA (registry + pool) + retired-ledger SHA, numeric epoch, TTL, `binding_id` self-digest. Codes: `POOL_DIGEST_DRIFT`, `RETIRED_ARM`, `BINDING_EXPIRED`, `BINDING_TAMPERED`, `BINDING_ALREADY_EXISTS`, `HOLD_REGISTRY_POOL_DRIFT`. The hardcoded `C:\Projects\Agent_Workspace\HG-KSEOS` path is gone (it did not exist on this host; `--menu` used to crash). |
| `EC-R26-004` `l1.bytes = 111331` vs the real 6,224,679 | MAJOR | Metadata re-derived from the file: `l1.bytes = 6224679`, `l1.lines = 28005`, and the 31-source total moved to `source_inventory.total_lines = 111331`. |
| `EC-R26-011` `unaffected_proof` says `32-4=28 properties` | MAJOR | Recomputed from the receipts: 4 WPs × 19 clauses × 4 preservation properties = **76**. |
| `EC-R26-009` `EVIDENCE_SCOPE.full.excluded` lists six gates the full profile claims to run | MODERATE | `full.excluded = {}`; the six move to `full.not_runnable_in_CI` with reasons. |
| `EC-R26-008` the seven owner signatures were never independently re-verified | MAJOR | `tools/verify_public_bundle.py` re-derives each payload digest and verifies the Ed25519 signature against the enrolled owner key `d42c654c…`. Measured: **7/7 verified**. The `preauth_at` timezone defect is recorded as an open finding, not silently rewritten. |
| `EC-R26-010` CH26.5 names the stale HGK head | MODERATE | `evidence/fhs-w0-r27-repair-20261110/…W0_r27.md` appends CH27 and marks the old line superseded. Its prefix is **byte-identical** to the frozen r26 file (`prefix_identical: true`, +20,943 appended bytes). |
| `EC-R26-012` "no forced SoD" could be read as cancelling credential separation | GOVERNANCE HOLD | CH27.7 states the split explicitly: `model_diversity_optional = true`, `protected_identity_permissions = UNCHANGED`. |

## Executed evidence (not summaries)

- `verify_quorum.py --selftest` → exit 0; the three named false greens now refuse with their own codes.
- `selftest_fhs_3lm.py` → exit 0 over E01–E08 (menu on epoch 41, atomic per-run binds, `POOL_DIGEST_DRIFT`, `RETIRED_ARM`, `BINDING_EXPIRED`, `BINDING_TAMPERED`, `HOLD_REGISTRY_POOL_DRIFT`).
- `gate_r20.py --profile payload` → `VERDICT PASS pass=16/16 blocking_fail=0`.
- The **new G24 check was falsified by this round**: a mirror copy with `l1.bytes` set back to `111331` produced `SOURCE_CONTRACT_BYTES_MISMATCH` and `VERDICT FAIL` (log kept with the round).
- `verify_public_bundle.py` → `VERDICT ALL_SEVEN_VERIFIED`; `--selftest` fires 6/6 mutations.
- Independent re-execution by the commander, in fresh processes with its own evidence path: **14/14 checks matched their expected exit codes**.

## Not claimed

- No `NATIVE_SIGNED`, no `PASS_CHALLENGE`, no `RELEASE_GRANTED`, no `FULL_W0_CLOSEOUT`.
- The full 22-gate profile still needs the 31-volume corpus and the original Windows round tree; it exits 2 on this host and is **not** reported as a pass.
- The r27 owner semantic acknowledgement needs an owner signature; the owner signing window was opened for it (scope `owner_semantic_accept`), and the instrument is not attached to this PR.
- `CH27.5` lists refusal codes that are executable only where the repaired tools are installed; only `RETIRED_ARM` pre-existed.
- No merge, no force-push, no default-branch change. The base branch is untouched.

## Reading order for an external engineer

1. `evidence/fhs-w0-r26-repair-20261109/tools/verify_quorum.py` (G29 predicate, its `CASES`, its new refusals)
2. `evidence/fhs-w0-r26-repair-20261109/tools/fhs_3lm.py` (binding + assert contract)
3. `evidence/fhs-w0-r26-repair-20261109/tools/selftest_fhs_3lm.py` (the executed cases)
4. `evidence/fhs-w0-r26-repair-20261109/tools/verify_public_bundle.py` (real crypto verifier)
5. `evidence/fhs-w0-r27-repair-20261110/doc/FHS_PIPD-LS-PKG_W0_r27.md` CH27 (the append-only correction)
