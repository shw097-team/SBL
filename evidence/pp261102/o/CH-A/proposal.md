# Validate four-objects denominator — `pipd validate --bundle` names what it checked

## Why

`pipd validate --bundle` reported `{"checked": 3, "closure": "FULL"}` for a bundle that was missing
`TQAEP`. Both fields were true in their own terms — three records were schema-checked, and the trace
graph among those three records closed — but the pair reads as "four objects closed". The round that
found this (`RUN-20261102-GJ02-01`) had to open the bundle to discover the fourth object was absent.

The defect is one of **denominator**, not of checking. A scoped validate of a partial bundle is legal
and must stay legal: a single `PI-PKG` legitimately closes against its own atoms, and the LITE slice
is validated exactly that way. What was missing was a field that says which denominator the result
was computed against, so a partial result can never be quoted as a four-object one.

## What changes

`pipd validate --bundle` results gain four fields, and the `validate` subcommand gains one flag:

| field | value | meaning |
|---|---|---|
| `scope` | `FOUR_OBJECT` \| `PARTIAL_BUNDLE` | which denominator this result was computed against |
| `required` | `["PI-PKG","PD-PKG","ECP","TQAEP"]` | the contract names the denominator is made of |
| `missing` | list (possibly empty) | required names absent from the bundle, in denominator order |
| `complete` | bool | `missing == []` |
| `closure` | unchanged: `FULL` \| `SCHEMA_ONLY` \| `FAILED` | trace graph among the records **present** |

- New flag `--require-four` (stored as `require_four`, `action="store_true"`): when any required object
  is absent the result is `FAIL` with a finding of `kind: "DENOMINATOR"` whose detail names the missing
  objects. Without the flag a partial bundle still returns `PASS`, and `scope`/`complete`/`missing`
  carry the qualification instead of the verdict.
- `closure` is **not** redefined. It keeps its S4EXT-R1 meaning (atomic trace closure over the bundle's
  edges), because redefining it to mean "four objects present" would make every legitimate single-record
  closure fail.
- The denominator constant is one tuple (`RELEASE_FOUR` in `src/pipd_ls_sp/validate.py`), used for both
  `missing` and `required`, so the reported denominator and the enforced one cannot diverge.
- The existing empty-bundle guard is unchanged and already speaks the same vocabulary: `validate_bundle({})`
  returns `FAIL` with a `DENOMINATOR` finding ("zero records checked cannot be a PASS").

Files touched: `src/pipd_ls_sp/validate.py`, `src/pipd_ls_sp/cli.py`,
`tests/test_validate_four_objects.py`.

## Not in scope

- **Not a Native qualification.** No native host binding, no receiver ACK, no Protected Checker receipt
  is claimed or produced by this change; it moves a CLI result field, nothing about native authority.
- **Not a Release.** No version bump, no tag, no publication, no claim-ladder movement.
- Not a change to what the per-record checks assert: schema validity and the semantic invariants are
  untouched, and no finding is removed.
- Not a new bundle format, schema family, or export surface.
- Not a change to `closure` semantics, to `trace_closure`, or to any existing test's expectation.
- Not a decision about whether a partial bundle *should* be quotable — that stays an operator
  decision, now explicit via `scope` and enforceable via `--require-four`.

## Impact

- Affected: `src/pipd_ls_sp/validate.py`, `src/pipd_ls_sp/cli.py`, `tests/test_validate_four_objects.py`.
- Unchanged: `pipeline.py`, `registry.py`, `schemas/`, `export_bundle.py`, every existing gate.
- Consumers of the JSON result see four **added** keys; no key is renamed or removed, so a reader that
  ignores unknown fields is unaffected. A reader that rendered `closure` alone as a completeness claim
  is the thing this change exists to correct.
- Claim ceiling: `CANDIDATE_ONLY` on branch `candidate/pre-v2-planning-20261102`.
