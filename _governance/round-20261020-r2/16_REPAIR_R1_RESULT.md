# REPAIR R1 — result, and why the writer lane did not author it

## Lane outcome (disclosed)

| attempt | lane / arm | result |
|---|---|---|
| `EXECUTE_repairR1.json` | EXECUTE, `opencode-go/deepseek-v4.1-flash` (rank 1) | `ok=false`, `ERR_LANE_ALL_ROUTES_EXHAUSTED` — the child's `apply_patch` was rejected (`multiple operations target .../sbl_core/m05_verify.py`) and the turn died at 9 s |
| `EXECUTE_repairR1a.json` | EXECUTE, same arm | `ok=false`, `ERR_LANE_ALL_ROUTES_EXHAUSTED` — attempt exited 1 after 9.59 s with `Reading additional input from stdin...`; the prompt never reached the child |

Two failures with different causes on the same task shape. Per the round policy (a lane that fails twice
hands the work to a deterministic route and the substitution is recorded), **PLAN authored this repair
directly** and the finding-by-finding result was then handed to a *different* principal
(`openai-codex/gpt-6.1-sol`, VERIFY_SECURITY) for re-verification. Maker/checker separation is preserved:
the checker never authored these changes.

## What changed, per finding

| finding | change | test that would fail if the fix is removed |
|---|---|---|
| SEC-01 | `sbl_sp/sp.py` now requires an HMAC credential over `json.dumps([principal_id, verdict], sort_keys=True)` keyed by that principal's entry in the new `sbl_sp/keys.json`; `expected_signature()` is the only way to obtain it. Naming a principal is no longer authority. | `test_signing_without_credential_is_refused`, `test_signing_with_another_principals_credential_is_refused`, `test_maker_cannot_impersonate_the_checker` |
| SEC-02 | `EvidenceVerification(ceiling="LOCAL")` owns the ceiling; a caller asking for a higher one is refused (`SBL_E_CLAIM_CEILING_EXCEEDED`, detail carries `build_ceiling`). `BUILD_CEILING = "LOCAL"`. | `test_verify_ceiling_belongs_to_the_instance` |
| SEC-03 | `verdict()` looks up recorded evidence for the gate (`no_recorded_evidence` / `evidence_exit_nonzero`), normalises status (`strip().upper()`), and only accepts `PASS/FAIL/BLOCKED_HITL/BLOCKED_EXTERNAL`; signing refuses proxy or undeclared statuses. | `test_verify_negative_pass_without_evidence`, `test_verify_negative_pass_after_failing_evidence`, `test_verify_negative_proxy_status_variants`, `test_verify_negative_undeclared_status`, `test_proxy_or_undeclared_status_cannot_be_signed` |
| SEC-04 | `tools/secret_scan.py` applies the allowlist to the **matched span** (`finditer`), not the line; masking kept. | `tests/test_secret_scan.py` (7 cases, incl. "append `example.com` and the token is still blocked") |
| VERIFY-01 | `tools/verify_source.py` requires the exact `DOC-00..DOC-13` inventory (missing / unexpected / duplicates) and supports `--record` for alternative receipts. | `tests/test_verify_source.py` (5 cases, incl. the empty-inventory receipt that used to pass) |
| VERIFY-02 | `tools/run_gates.py` parses every `<n> <outcome>` on pytest's summary line and records `failed` separately; zero-denominator pytest gates still fail the runner. | live: `G-SUITE-FULL` denominator 112 (= suite total), `G-CORE-MODULES` 42 |
| VERIFY-03 | `shutil.rmtree(..., ignore_errors=True)` replaces the 3.12-only `onexc=` in both e2e fixtures. | the whole suite run under CPython 3.11.9 |

## Raw results after the repair (same host, same candidate)

```
py312  python -m pytest -p no:cacheprovider           -> 112 passed, exit 0
py311  py -3.11 -m pytest -p no:cacheprovider         -> 112 passed, exit 0
       tools/run_gates.py                             -> exit 0, 11/11 gates, 211 gate executions
       tools/verify_source.py --verify                -> ok true, docs 14, mismatches []
       tools/secret_scan.py --root .                  -> CLEAN, 150 files, 0 findings
```

## Honest notes

- `sbl_sp/keys.json` is a **public demo keyring** with deterministic placeholder keys, not a credential store.
  It exists so that "naming a principal" is insufficient; a real deployment replaces it with an externally
  provisioned keyring.
- The new tests are stricter than the ones they replace: several previously-passing calls now record evidence
  first, because a verdict without a receipt is exactly what SEC-03 forbade.
- The checker's own copy lacked `.git`; this round's verify copy carries it so the repo-context test can run.
