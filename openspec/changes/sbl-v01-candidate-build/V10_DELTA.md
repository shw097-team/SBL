# v8 → v10 delta (narrow repair after external acceptance)

Appended to this change rather than creating a second OpenSpec change. This is the delta the external
report `SBL-EIAR-20261020-R1` asked for; the change itself was validated at the v8 state.

## What changed

| Area | v8 (`fb7af87`) | v10 (`2d1c32d`) |
|---|---|---|
| CI (M1) | installed the package, then ran pytest with no pytest present; a Windows-only step read a private mirror path that no hosted runner has | installs `pytest>=8,<9` as a CI tool before the suite; verifies the published manifest with `verify_source.py --self-check` and states `byte_verification: NOT_PERFORMED`; no `continue-on-error`; no second `-q` that would hide the summary |
| Write-set containment (M2) | `abspath` + `relpath` only, so a symlink or junction inside the writeset carried a write outside the root | real destination resolved and re-checked against the real root and writeset before writing; `SBL_E_WRITE_OUTSIDE_WRITESET`; tests for escape, inside-link success and the lexical negatives |
| G-KNOW authority (M3) | 2 MiB cap silently dropped `DOC-05` (2,382,349 B); a question naming a non-existent `DOC` was answered from the nearest neighbour | cap above the largest book; every skip recorded in `coverage_gaps`; `SBL_E_KNOWLEDGE_NO_ANSWER` and `SBL_E_KNOWLEDGE_COVERAGE_GAP`; every hit stamped `NON_AUTHORITATIVE_LOCATOR` |
| Verification tooling | `verify_source.py --verify` needed the private corpus and could not run on a runner | new `--self-check` proves inventory and aggregate consistency without the corpus, and refuses to look like a byte check |

## Requirements touched

- `sbl-core` requirement "evidence verification must refuse an incomplete or unverifiable inventory" — the
  refusal vocabulary gains `SBL_E_KNOWLEDGE_NO_ANSWER` and `SBL_E_KNOWLEDGE_COVERAGE_GAP`.
- Requirement "governed build writes only inside its write set" — now enforced on the real path, not the
  literal path.
- Requirement "the product must not present retrieval as authority" — hits carry an explicit
  non-authoritative stamp.

## Validation state

- `openspec validate sbl-v01-candidate-build --strict` passed at the v8 state, and passed again after this
  delta file was added (`Change 'sbl-v01-candidate-build' is valid`). The delta lives on the evidence
  branch, so the candidate tree's own validation state is unchanged.
- Task list in `tasks.md` still reflects v8 scope; the M1–M4 work is tracked in
  `_governance/round-20261020-r2/70_NARROW_REPAIR_M1_M4.md` and `80_FAR_RULING.md`, not duplicated here.
