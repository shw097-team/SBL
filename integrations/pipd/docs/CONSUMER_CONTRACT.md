check consumer_gate().accepted, nothing else

# `CONSUMER_CONTRACT.md` — what an automated consumer of `validate --adjudications` MUST check

Family: `SBL.SourceAdjudication@1` · verb: `pipd validate --bundle … --adjudications …`
Status: **candidate** (branch `feat/clause-set-adjudication-candidate`). No Source ID in the
shipped tree is decided; all 428 rows of the W1 r3 candidate remain `NOT_DECIDED` until the
original Reader files its own per-Source-ID disposition under its own enrolled key.

---

## 1. The one rule

> **`consumer_gate(validate_payload)["accepted"] is True` is the only lawful passage.**
> Nothing else is a decision — not the exit code, not `bundle.verdict == "PASS"`, not a
> fixture-complete verdict. A consumer that proceeds on any of those has accepted an undecided wave.

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

The CLI also **stamps that same gate result into the payload** it returns, at
`adjudication.consumer_gate`, and can enforce it:

```bash
pipd validate --bundle b.json --adjudications a.jsonl \
              --source-index wave.tsv --subject subject.md --require-consumer-gate
```

`--require-consumer-gate` exits **3** when `accepted` is false, with `CONSUMER_GATE_NOT_ACCEPTED`
prefixed to the refusal list. The bundle half of the payload is unchanged and still `PASS`; only
the exit code changes, so "the command succeeded" stops being readable as "the wave was decided".
The flag without `--adjudications` is a typed usage refusal (`INPUT_SHAPE_INVALID`, exit `2`),
because there is no gate result to require.

## 3. The three signals that are each individually insufficient

| signal | what it actually says | refusal code it earns when it is all you have | NEG |
|---|---|---|---|
| exit `0` | "the command ran; the bundle did not fail" | `CONSUMER_VERDICT_NOT_COMPLETE` | `test_neg1_exit_zero_alone_is_refused` |
| `bundle.verdict == "PASS"` | "this four-object bundle is schema-and-trace valid" | `CONSUMER_NO_ADJUDICATION_BLOCK` (nothing to read) / `CONSUMER_VERDICT_NOT_COMPLETE` (undecided adjudication) | `test_neg2_bundle_pass_alone_is_refused` |
| `adjudication.verdict == "COMPLETE_FIXTURE_KEY_ONLY"` | "every signature verified — under a **fixture** key" | `CONSUMER_VERDICT_NOT_COMPLETE` + `CONSUMER_ORIGINAL_READER_UNVERIFIED` | `test_neg3_fixture_complete_is_refused` |

The mapping is published by the gate itself, as `insufficient_signals` and `signal_refusals`, so a
consumer can pin it instead of re-deriving it:

```python
gate["insufficient_signals"]      # ['exit_code_0', 'bundle_verdict_PASS',
                                  #  'adjudication_verdict_COMPLETE_FIXTURE_KEY_ONLY']
gate["signal_refusals"]           # {signal: [codes consumer_gate() returns for it]}
```

The three denominators are independent by construction: the bundle verdict owns the exit code and is
never changed by `--adjudications`; the adjudication verdict owns the decisions and is never changed
by the bundle; and a fixture key owns neither, because it is not the reader. That is why each signal
can be true while the wave is undecided, and why only a called gate can tell.

## 4. Why each field exists

| field | who may set it | meaning |
|---|---|---|
| `adjudication.verdict` | the checker | `COMPLETE` only when the declared denominator is fully verified against the **original reader's** enrolled key |
| `records[].state` | the checker | `VERIFIED` / `UNVERIFIED` / `REFUSED` for that row |
| `records[].decision` | **the reader, via a signed record** | `null` unless the row is `VERIFIED` |
| `records[].claimed_decision` | the record's own text | what the file *claims*, verified or not — never read this as a decision |
| `records[].original_reader_signature_verified` | the checker | per-row: this row's signature verified against a **non-fixture** enrolled key |
| `complete` | the checker | the only full-completion flag; false unless the declared denominator is fully covered by rows signed under the reader's own key |
| `completion_refusals` | the checker | the named reasons `complete` is false, so `false` is never mistaken for "not checked" |
| `coverage` | the checker | `expected`, `verified`, `verified_in_denominator`, `not_in_denominator`, `every_row_verified` |
| `denominator_declared` | the checker | `--source-index` **and** `--subject` were both supplied |
| `hold_h01` | the checker | H-01's state (`HELD` / `RELEASED`), `released_by: ORIGINAL_READER_PER_SOURCE_ID_DISPOSITION`, and the reader's own disposition counts — all zero under a fixture key |
| `consumer_gate` | the checker (`enforce_consumer_gate`) | the gate's own result: `accepted`, `refusals`, `required`, `insufficient_signals`, `signal_refusals` |

## 5. NEG — exit `0` + `PASS` bundle + verdict not all-decided is refused

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

The fixture-COMPLETE case is the sharpest one, because every number in it looks right: 428 of 428
rows `VERIFIED`, `decided == expected`, and a verdict that literally begins with `COMPLETE`. It is
still refused (`test_neg3_fixture_complete_is_refused`, plus the 428-row lane evidence in
`GATE_ENFORCEMENT.json`).

## 6. What a consumer may NEVER treat as a decision

- exit `0`, or `bundle.verdict == "PASS"`;
- `COMPLETE_FIXTURE_KEY_ONLY` — that name says the *verifier* works, not that the reader decided. It
  can never release **H-01**, because a fixture signature carries no disposition (see
  `CLAUSE_SET_AND_ADJUDICATION.md` §"H-01 — what the hold waits on");
- a `reader_identity` string or an `authority_ref` path inside a record;
- `ADJUDICATION_MISSING` counts, `by_decision` totals, or `expected` when
  `denominator_declared` is false (the denominator is then just "however many records the file
  carried");
- a `decision` value on a row whose `state` is not `VERIFIED` (it is `null` by construction; read
  `claimed_decision` only to *diagnose*, never to decide);
- any count from a run over the r3 mother standing in for the r8 signed subject, or the reverse —
  the two bodies are separate lines, and a decision set over one proves nothing about the other
  (`R3_vs_R8_LEDGER.tsv`).

## 7. Claim ceiling

`READER_ADJUDICATION_NOT_PRODUCT_ACCEPTANCE`. A `COMPLETE` adjudication block is the reader's
decision set, not product acceptance, and it never changes the bundle verdict.
