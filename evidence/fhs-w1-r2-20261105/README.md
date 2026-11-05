# FHS W1 r2 — pre-implementation admission evidence (SBL side)

**ChangeSet:** `FHS-W1-R2-PREIMPL-20261105`
**Source:** W1 r2 author final, body `e40df2999fbffdb96a32a2e35cddce228abdd82080d5a5bedd415dfc938669ce`, source manifest `06628b6b4c6ba1b0d4d9b31b795141aaf51ade4c7df8304d1af093a229227f60`, ZIP `ce1e27ea948212b4312bf4243d9a6760d39b913e94bb5cc27fd871f378182e8e`

Claim ceiling of this change: **candidate evidence only**. It is not an acceptance, not a release, and it
carries no canonical or native standing.

## What is here

| file | what it is |
|---|---|
| `W1_R2_ROLE_SPECS.json` | the three author-side role SPECs (Product / Architecture / Program) with their pinned W0 SPEC hashes |
| `READER_REQUESTS.jsonl` | 14 same-scope questions for the original readers, each with `required_raw`, `first_fail`, `resume_predicate` |
| `HOLD_AND_RESUME.json` | W0 1203's 71 holds with their original values and the W1 affected projection |
| `AFFECTED_REPAIR_MATRIX.jsonl` | F-01..F-14 and N-01..N-08 with 18 fields each |
| `STATIC_ACCEPTANCE.json` | author-side static acceptance: baseline, r2 invariants, 14 destructive negatives |
| `PIPD_CLI_SLICE_RAW.json` | the measured slice of the installed-from-source PIPD CLI (see verdict inside) |

## Reproduce

```bash
python - <<'PY'
import json,hashlib,pathlib
b=pathlib.Path("evidence/fhs-w1-r2-20261105/W1_R2_ROLE_SPECS.json").read_bytes()
print(len(b), hashlib.sha256(b).hexdigest())
PY
```

(The full replay suite lives in the W1 r2 package: `validation/author_validator.py`,
`validation/run_negative_fixtures.py`. Its 14 destructive negatives are the ones summarised in
`STATIC_ACCEPTANCE.json`.)

## POS / NEG

- POS: every row keeps its source locator, original reader and first-fail; the 71 holds are byte-faithful
  to the W0 1203 seal; the three role SPECs are separable and pinned.
- NEG: a fabricated original ACK, a 7:0 -> `WP19_DONE` promotion, a second PIPD writer, or an asset
  status promotion fails the respective first-fail and is not merged.

## What is NOT claimed

`ORIGINAL_READER_ACK`, `CANONICAL_PIPD`, `HOST_INSTALL_LOAD`, `PROTECTED_CHECKER`, `RELEASE`.
