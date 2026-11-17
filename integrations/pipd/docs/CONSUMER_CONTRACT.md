# `CONSUMER_CONTRACT.md` — what an automated consumer of `validate --adjudications` MUST check

Family: `SBL.SourceAdjudication@1` · verb: `pipd validate --bundle … --adjudications …`
Status: **candidate** (branch `feat/clause-set-adjudication-candidate`). No Source ID in the
shipped tree is decided; all 428 rows of the W1 r3 candidate remain `NOT_DECIDED` until an original
reader is enrolled and signs.

---

## 1. The one rule

> **Exit code and `bundle.verdict` are NOT a decision.** They answer "is this four-object bundle
> schema-and-trace valid". Only `adjudication.verdict == "COMPLETE"`, with every per-row decision
> verified **and** coverage equal to the declared denominator, is "the reader decided the wave".

The two denominators are deliberately independent: a valid bundle keeps `PASS` and exit `0`
whatever the reader's records say, and a fully verified decision set cannot rescue a broken bundle.
A consumer that reads only the exit code therefore accepts an undecided wave every time.

## 2. The exact check

```python
from pipd_ls_sp.adjudication import consumer_gate

out = json.loads(validate_stdout)          # the WHOLE validate payload
gate = consumer_gate(out)                  # or consumer_gate(out, out["adjudication"])
if not gate["accepted"]:
    refuse(gate["refusals"])               # each entry: {"code": ..., "detail": ...}
```

`consumer_gate` performs, in order, exactly these assertions — and nothing weaker is conformant:

| # | assertion | refusal code |
|---|---|---|
| 1 | an `adjudication` block exists at all | `CONSUMER_NO_ADJUDICATION_BLOCK` |
| 2 | `adjudication.read_only is True` | `CONSUMER_BLOCK_IS_NOT_A_READ_CHECK` |
| 3 | `validate_output.verdict == "PASS"` (necessary, never sufficient) | `CONSUMER_BUNDLE_NOT_PASS` |
| 4 | **`adjudication.verdict == "COMPLETE"`** | `CONSUMER_VERDICT_NOT_COMPLETE` |
| 5 | `adjudication.denominator_declared is True` | `CONSUMER_DENOMINATOR_UNDECLARED` |
| 6 | `decided == expected == len(records) == coverage.verified_in_denominator` | `CONSUMER_PARTIAL_COVERAGE` |
| 7 | **every `records[i].state == "VERIFIED"`** | `CONSUMER_ROW_NOT_VERIFIED` |
| 8 | **every `records[i].decision ∈ {ACCEPT, NOT_APPLICABLE, NACK}`** | `CONSUMER_ROW_DECISION_UNKNOWN` |
| 9 | **every `records[i].original_reader_signature_verified is True`** | `CONSUMER_ORIGINAL_READER_UNVERIFIED` |
| 10 | aggregate `original_reader_signature_verified is True` | `CONSUMER_ORIGINAL_READER_UNVERIFIED` |
| 11 | `adjudication.complete is True` | `CONSUMER_VERDICT_NOT_COMPLETE` |

Per-row refusals are grouped by code and report a count plus the first source ids, so a 428-row wave
produces a handful of named refusals rather than 428 lines.

## 3. Why each field exists

| field | who may set it | meaning |
|---|---|---|
| `adjudication.verdict` | the checker | `COMPLETE` only when the declared denominator is fully verified |
| `records[].state` | the checker | `VERIFIED` / `UNVERIFIED` / `REFUSED` for that row |
| `records[].decision` | **the reader, via a signed record** | `null` unless the row is `VERIFIED` |
| `records[].claimed_decision` | the record's own text | what the file *claims*, verified or not — never read this as a decision |
| `records[].original_reader_signature_verified` | the checker | per-row: this row's signature verified against a **non-fixture** enrolled key |
| `complete` | the checker | the only full-completion flag; false unless the declared denominator is fully covered by verified rows |
| `completion_refusals` | the checker | the named reasons `complete` is false, so `false` is never mistaken for "not checked" |
| `coverage` | the checker | `expected`, `verified`, `verified_in_denominator`, `not_in_denominator`, `every_row_verified` |
| `denominator_declared` | the checker | `--source-index` **and** `--subject` were both supplied |

## 4. NEG — exit `0` + `PASS` bundle + verdict not all-decided is refused

Real run, `out/GATES_AFTER.json` case `NEG2_partial_signature`
(3 of 428 rows signed with a `TEST_FIXTURE_ONLY` key; `--source-index` and `--subject` both given):

```
cli exit               0
bundle.verdict         PASS
adjudication.verdict   UNVERIFIED
decided / expected     3 / 428
complete               false
completion_refusals    ["ADJUDICATION_ORIGINAL_READER_UNVERIFIED",
                        "ADJUDICATION_PARTIAL_SIGNATURE_SET"]
```

| check a consumer might run | result | verdict |
|---|---|---|
| `exit_code == 0` | **True** | accepts an undecided wave — WRONG |
| `bundle.verdict == "PASS"` | **True** | accepts an undecided wave — WRONG |
| `adjudication.verdict == "COMPLETE"` | False | correct |
| `consumer_gate(out)["accepted"]` | **False** | correct, with named refusals |

`consumer_gate` returns, for that payload:

```
CONSUMER_VERDICT_NOT_COMPLETE   adjudication.verdict is 'UNVERIFIED'; only 'COMPLETE' is a decided wave
CONSUMER_PARTIAL_COVERAGE       decided=3 expected=428 rows=3 verified_in_denominator=3
CONSUMER_ORIGINAL_READER_UNVERIFIED  3 of 3 row(s) fail this check: SRC-1524…, SRC-e236…, SRC-b980…
CONSUMER_ORIGINAL_READER_UNVERIFIED  the aggregate original_reader_signature_verified is not true
CONSUMER_VERDICT_NOT_COMPLETE   the run does not set complete=true
```

And on the shipped tree the default case is worse for a naive consumer: the committed enrollment
carries **no** key, so even a correctly signed record is `UNVERIFIED` and `consumer_gate` refuses —
while `validate` still exits `0` with `PASS`.

## 5. What a consumer may NEVER treat as a decision

- exit `0`, or `bundle.verdict == "PASS"`;
- a `reader_identity` string or an `authority_ref` path inside a record;
- `COMPLETE_FIXTURE_KEY_ONLY` — that name says the *verifier* works, not that the reader signed;
- `ADJUDICATION_MISSING` counts, `by_decision` totals, or `expected` when
  `denominator_declared` is false (the denominator is then just "however many records the file
  carried");
- a `decision` value on a row whose `state` is not `VERIFIED` (it is `null` by construction; read
  `claimed_decision` only to *diagnose*, never to decide).

## 6. Claim ceiling

`READER_ADJUDICATION_NOT_PRODUCT_ACCEPTANCE`. A `COMPLETE` adjudication block is the reader's
decision set, not product acceptance, and it never changes the bundle verdict.
