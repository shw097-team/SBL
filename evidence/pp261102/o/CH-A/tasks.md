# Validate four-objects denominator — tasks

Status legend: `[x]` done and read back · `[ ]` open, owner named · `[!]` blocked on an owner/native decision.

Repository: PIPD-LS-SP · branch `candidate/pre-v2-planning-20261102` · change landed on the branch as
`67ba96e fix(validate): name the four-object denominator, add --require-four` (on top of `011faab`).

## Landed

- [x] `RELEASE_FOUR = ("PI-PKG", "PD-PKG", "ECP", "TQAEP")` declared in `src/pipd_ls_sp/validate.py`
      as the single denominator constant.
      Verified: `grep -n 'RELEASE_FOUR' src/pipd_ls_sp/validate.py` → declaration + 2 uses
      (`missing = [c for c in RELEASE_FOUR if c not in bundle]`, `"required": list(RELEASE_FOUR)`).
- [x] `validate_bundle(bundle, schemas_dir=None, require_four=False)` returns `scope`, `missing`,
      `complete`, `required` alongside the unchanged `verdict`, `checked`, `closure`, `findings`.
      Verified: `grep -n '"scope"\|"missing"\|"complete"\|"required"' src/pipd_ls_sp/validate.py`.
- [x] `--require-four` registered on the `validate` subparser with `dest="require_four"`,
      `action="store_true"`, and threaded into `validate.validate_bundle(...)` in the CLI dispatch.
      Verified: `grep -n 'require-four\|require_four' src/pipd_ls_sp/cli.py`.
- [x] A missing object under `--require-four` produces `verdict: FAIL` with a
      `{"contract": "*", "kind": "DENOMINATOR"}` finding naming the absent object(s).
      Verified: `PYTHONPATH=src python -m unittest tests.test_validate_four_objects -v` → 4 tests, OK.
- [x] `closure` left semantically untouched (still `FULL` / `SCHEMA_ONLY` / `FAILED` over present records).
      Verified: `grep -n 'closure_state' src/pipd_ls_sp/validate.py` → the value is passed through from
      `closure_findings(bundle)`, not recomputed from `missing`.

## Verification (run from the repo root)

```sh
PYTHONPATH=src python -m unittest tests.test_validate_four_objects -v
PYTHONPATH=src python -m unittest tests.test_s4ext_trace_closure tests.test_s1_lite_slice
```

- [x] New behaviour suite: `tests.test_validate_four_objects` — 4 tests, `OK`
      (full bundle → `FOUR_OBJECT`/`complete`; partial → `PARTIAL_BUNDLE`/`missing:["TQAEP"]` and still
      `PASS`; `require_four=True` → `FAIL` + `DENOMINATOR`; CLI default exit 0 vs `--require-four`
      non-zero).
- [x] Regression: `tests.test_s4ext_trace_closure` + `tests.test_s1_lite_slice` — 37 tests, `OK`. These
      are the tests that assert `closure: FULL` for bundles that are not four objects; they pass
      unchanged, which is the proof that `closure` was not redefined.
- [x] Manual readback of the reported shape on a three-object bundle:
      `scope=PARTIAL_BUNDLE`, `checked=3`, `missing=["TQAEP"]`, `complete=false`,
      `required=["PI-PKG","PD-PKG","ECP","TQAEP"]`, and `closure` still reporting the graph among the
      three present records.

## Open / follow-up (not required for this change)

- [ ] Decide whether any CI/pre-v2 receipt should call `validate --bundle --require-four` (owner
      decision; today the default stays permissive so scoped validation keeps working).
- [ ] If a downstream reader (portal, bundle report, closeout template) prints `closure` as a
      completeness claim, switch it to `scope`/`complete` — such a reader would be in another repo and
      is not part of this change.

## Explicitly not done

- [ ] No change to `closure` semantics, to `pipeline.trace_closure`, or to the empty-bundle guard.
- [ ] No redefinition of `checked` (it still counts records actually schema-checked).
- [ ] No Native qualification, no Release, no claim-ladder movement.
