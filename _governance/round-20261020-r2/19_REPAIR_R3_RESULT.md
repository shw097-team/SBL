# REPAIR R3 — closing one new HIGH and re-testing the nine probes

Third checker turn: `openai-codex/gpt-6.1-sol`, VERIFY_SECURITY rank 2, `required_arm == served_arm`,
410.81 s, `subject_mutation.verdict = CLEAN` (0 added, 0 changed, 0 removed — no orchestrator writes during
the window).

## Its verdict on the previous repair

All nine probes it was asked to re-run came back **closed**:

| probe | result |
|---|---|
| A `EvidenceVerification(ceiling='PRODUCTION')` | closed — `SBL_E_CLAIM_CEILING_EXCEEDED` |
| B `verifier.ceiling = 'PRODUCTION'` | closed — `AttributeError: property 'ceiling' has no setter`, ceiling stays `LOCAL` |
| C `verdict(..., claim_ceiling='PRODUCTION')` on a LOCAL instance | closed — `SBL_E_CLAIM_CEILING_EXCEEDED` |
| D package exports + signing with no key | closed — `hasattr(sbl_sp,'load_key') == False`, `SBL_E_PERMISSION_DENIED / no_key_provisioned` |
| E assigned value containing `example.com` | closed — `BLOCKED` |
| F token value with `-example.com` inside the quotes | closed — `BLOCKED` |
| G PASS without evidence / after `exit_code=1` / `file_exists` / `FILE_EXISTS ` | closed — `SBL_E_BAD_STATE` each |
| H empty docs inventory | closed — refused, 14 documents reported missing |
| I mixed `1 failed, 1 passed` | closed — denominator 2 |

## Its new HIGH, and this repair

`R3-NEW-01`: `_value_of()` split the matched text on the **last** separator, so an assigned value whose
tail was `=changeme` collapsed to `changeme` and matched the placeholder allowlist.

Change: split on the **first** separator only and require the whole remaining value to be a literal
placeholder. Test: `test_a_placeholder_after_an_equals_sign_does_not_hide_the_value` — it fails if the
fix is reverted (verified locally: with the old `rsplit` the scanner returns `CLEAN`, with the new
`find` it returns `BLOCKED`).

Two ENV findings were also raised (git fixtures could not create a repository in its sandbox; no Python
3.11 launcher available). These are environment limitations of the checker, not product findings; the
fixture hardening from R2 stands and both interpreters pass on this host.

## Raw results after this repair

```
py312  python -m pytest -p no:cacheprovider     -> 119 passed, exit 0
py311  py -3.11 -m pytest -p no:cacheprovider   -> 119 passed, exit 0
       tools/run_gates.py                       -> exit 0, 11/11 gates, 222 gate executions
       tools/verify_source.py --verify           -> ok true, docs 14, mismatches []
       tools/secret_scan.py --root .             -> CLEAN, 151 files, 0 findings
```
