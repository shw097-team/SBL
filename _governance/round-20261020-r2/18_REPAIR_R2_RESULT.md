# REPAIR R2 — closing the second independent challenge (candidate 8640f02)

Second checker turn: `openai-codex/gpt-6.1-sol`, VERIFY_SECURITY rank 2, `required_arm == served_arm`,
403.94 s, `subject_mutation.verdict = CLEAN` (0 added / 0 changed / 0 removed — the orchestrator wrote
nothing inside the guarded subject this time). Verdict reported by the checker: **FAIL**, with the seven
round-1 findings either closed or re-opened through new paths.

## What the second checker accepted (closed)

| id | its result |
|---|---|
| SEC-03 | closed — PASS without evidence, PASS after `exit_code=1`, `file_exists`, `FILE_EXISTS ` all refused with `SBL_E_BAD_STATE` |
| VERIFY-01 | closed — empty inventory refused, all 14 required documents reported missing |
| VERIFY-02 | closed — mixed `1 failed, 1 passed` recorded denominator 2; full-suite denominator matches independent collection |
| VERIFY-03 | closed — the 3.12-only `onexc` incompatibility did not reproduce |

## What it re-opened (new defects) and what changed here

| id | its finding | change in this candidate | test that pins it |
|---|---|---|---|
| NEW-01 | `EvidenceVerification(ceiling="PRODUCTION")` and the mutable `.ceiling` attribute bypassed the build ceiling | the constructor refuses any ceiling above `BUILD_CEILING` (`SBL_E_CLAIM_CEILING_EXCEEDED`) and `ceiling` is a read-only property | `test_verify_constructor_cannot_raise_the_build_ceiling`, `test_verify_ceiling_attribute_is_read_only` |
| NEW-02 | `sbl_sp` exported `load_key` **and** `expected_signature`, so any caller could mint a challenger credential; the repo also shipped a keyring | `keys.json` is deleted; keys come only from `SBL_SP_KEY_<SP>` in the environment; neither accessor is exported from `sbl_sp` | `test_no_key_provisioned_means_no_signature`, `test_package_does_not_export_key_material` |
| NEW-03 | putting the allowlisted text *inside* the matched value still suppressed the finding | the scanner replaced the global substring list with per-rule predicates: email allowances key on the domain/local part, secret allowances only accept a literal placeholder value (`<token>`, `<redacted>`, …) | `test_allowlisted_text_inside_the_value_does_not_hide_it`, `test_allowlisted_text_inside_a_token_line_still_blocks` |
| ENV-01 | its gate run was red because `git init` failed inside the fixture (`fatal: not in a git directory`) and `py -3.11` was unavailable in its sandbox | the e2e `_git` helper now strips inherited `GIT_*`, sets `GIT_CONFIG_NOSYSTEM=1` and points `HOME`/`USERPROFILE` at the fixture root, so an inherited `GIT_DIR` cannot break the run | the e2e suites themselves (GJ02, rollback) under a hostile env |

ENV-01 is not a product defect, but a fixture that goes red for environmental reasons produces an
uninterpretable verdict, so it was fixed rather than argued about.

## Raw results (this candidate)

```
py312  python -m pytest -p no:cacheprovider     -> 118 passed, exit 0
py311  py -3.11 -m pytest -p no:cacheprovider   -> 118 passed, exit 0
       tools/run_gates.py                       -> exit 0, 11/11 gates, 221 gate executions
       tools/verify_source.py --verify           -> ok true, docs 14, mismatches []
       tools/secret_scan.py --root .             -> CLEAN, 150 files, 0 findings
```

## Standing caveat, stated plainly

Python has no in-process principal boundary. The signing seam now requires an out-of-repo key, which
means a fresh checkout cannot mint a challenger credential — but any process that *holds* the env key
can sign. That is a property of the deployment, not of this library, and it is the honest limit of what
byte-level code review can enforce here.
