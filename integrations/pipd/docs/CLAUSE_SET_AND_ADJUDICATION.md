# `intake --clause-set` and `validate --adjudications`

Two additive flags on the existing 13 verbs. No 14th verb, no change to any default output, no
change to `FAILURE_CODES`, and no change to the S0 exact-19 contract registry.

| what | who produces it | who may NOT produce it |
|---|---|---|
| `atoms[]` per Source ID, `FirstFail` per Source ID | the compiler (`intake --clause-set`) | — |
| `ACCEPT` / `NOT_APPLICABLE` / `NACK` per Source ID | the **original SBL PIPD Reader**, signed | the compiler, the maker, any lane |

The compiler answers "what does this clause oblige, or why can I not compile it". It does not
answer "should this clause be accepted", because it has no applicability input, no reader identity
and no authority to grant acceptance (`TQ_SOD`, `self_accept: false`).

---

## 1. `pipd intake --clause-set <path> --subject <path>`

Compiles a whole table of pinned clause spans against ONE pinned subject in a single call and
emits one `sources[]` row per span. This replaces the hand-written "run the whole command once per
clause and read the exit code" loop that every prior lane had to write.

### Input

`--clause-set` accepts `.tsv` (header row, tab separated), `.jsonl`, or `.json` (array or
`{"rows": [...]}`). Each row must give the span, either as `span: [start, end]` or as the
`span_start` / `span_end` columns of the wave Source Span table:

```tsv
row_no	source_id	clause_id	span_start	span_end	clause_sha256	subject_sha256
1	SRC-1524eb3af62fc6f65b76	clause-4471-4615	4471	4615	3aff00e7…	5aca7b5e…
```

The identity columns are **optional and checked, never trusted**. When present the compiler
re-derives each of them and refuses the row if it disagrees:

| refused code | meaning |
|---|---|
| `SPAN_NOT_A_CLAUSE_BOUNDARY` | the span is not a boundary `requirements._parts` yields; the compiler does not re-cut a source span |
| `SOURCE_ID_MISMATCH` | the declared `source_id` is not the one `requirements.source_id_for` derives |
| `CLAUSE_ID_MISMATCH` | the declared `clause_id` is not `clause-<start>-<end>` for that span |
| `CLAUSE_SHA_MISMATCH` | the declared `clause_sha256` is not the digest of the subject bytes at that span |
| `SUBJECT_SHA_MISMATCH` | the row binds a different subject digest than the pinned subject |
| `SOURCE_LOCATOR_MISMATCH` | the row names a different file than `--subject` |

`--subject` is required: spans index into one subject, and `SRC-…` binds that subject's digest.

### Output — `ClauseSetIntake@1`

Not an `IntentCard@1`. One goal string is not the input, so the card must not be readable as a
single-goal intake.

```jsonc
{
  "schema_version": "ClauseSetIntake@1",
  "subject_id": "CLAUSESET-…", "content_hash": "…",
  "goal": null,
  "subject": "…/W1_r3_body.md", "subject_sha256": "5aca7b5e…",
  "clause_set": {"path": "…", "sha256": "…", "rows": 428, "format": "tsv:…"},
  "sources": [
    {
      "row_no": 1,
      "source_id": "SRC-1524eb3af62fc6f65b76",
      "clause_id": "clause-4471-4615",
      "span": [4471, 4615],
      "file": "…/W1_r3_body.md",
      "subject_sha256": "5aca7b5e…",
      "clause_sha256": "3aff00e7…",
      "state": "REFUSED",              // ATOMS | REFUSED
      "stage": "intake",
      "code": "INTAKE_INVALID",
      "message": "ambiguous compound: explicit subjects and predicates required",
      "atoms": [],                     // unchanged compile_requirements atom view
      "polarity": [],                  // union of the row's atom polarities
      "atom_count": 0,
      "first_fail": {"verb": "intake", "stage": "intake",
                     "code": "INTAKE_INVALID", "message": "ambiguous compound: …"}
    }
  ],
  "atoms": [ /* every atom of every row, unchanged shape */ ],
  "counts": {"sources": 428, "distinct_source_ids": 428, "atoms_rows": 0,
             "refused_rows": 428, "atoms": 0},
  "first_fail_histogram": {"INTAKE_INVALID": 428},
  "verdict": "FAIL",
  "claim_ceiling": "PER_SOURCE_FIRST_FAIL_ONLY",
  "reader_disposition": "NOT_PRODUCED_BY_COMPILER",
  "findings": []
}
```

There is **no** `disposition`, `accept`, `not_applicable` or `ack` field, and
`reader_disposition` is a constant string so a consumer cannot mistake its absence for a verdict.
`INTAKE_INVALID` is a compiler refusal; converting it into `NACK` is exactly what the reader
ownership rule forbids, so the payload has nowhere to put one.

### Exit codes

| exit | when |
|---|---|
| `0` | every row produced atoms |
| `1` | at least one row is `REFUSED` (the card's `verdict` is `FAIL`) |
| `2` | the clause set itself is unusable (unreadable, wrong format, zero rows, bad span, no `--subject`) — the usual typed `{verdict, code, message}` envelope |

`2` stays what it has always been on this surface: a typed refusal envelope. A mixed batch is a
`FAIL` result, not a refusal, so it reports `1` and carries the per-row detail.

### Default behaviour is untouched

Without `--clause-set`, `intake` is the same verb it was: `--goal` is `required=True` in exactly
the same parser, the same `pipeline.intake` call runs, and a missing `--goal` still exits `2` with
the same `USAGE_INVALID` envelope.

---

## 2. `pipd validate --bundle <b> --adjudications <path> [--source-index <tsv>] [--subject <p>]`

**Read-only.** The `adjudication` block is attached beside the existing result; `verdict`,
`checked`, `closure`, `scope`, `missing`, `complete` and `findings` are never touched. "Is this
four-object bundle schema-and-trace valid" and "did the reader decide the wave" are different
denominators, and neither may fail the other:

* a valid bundle stays `PASS` while the wave is undecided;
* a complete adjudication set does not make an invalid bundle pass.

The exit code follows the **bundle** verdict, as it always has. The adjudication has its own
`adjudication.verdict`, because one exit integer cannot carry two denominators.

`--require-consumer-gate` is the one opt-in exception, and it exists because a function that nobody
calls is not a gate: with it set, a refused `consumer_gate()` exits **3** (never overriding a bundle
`FAIL` (1) or a typed refusal (2)), while the bundle half of the payload stays byte-identical and
still `PASS`. Passing it without `--adjudications` is a typed usage refusal (exit `2`).

### `SBL.SourceAdjudication@1`

One record per Source ID. Schema: `contracts/SourceAdjudication.schema.json` (deliberately **not**
in `schemas/`, which is the S0 exact-19 surface that `tools/registry_reconcile.py` guards).

```jsonc
{
  "schema": "SBL.SourceAdjudication@1",
  "source_id": "SRC-1524eb3af62fc6f65b76",
  "subject_sha256": "5aca7b5e…",       // the whole pinned subject
  "clause_id": "clause-4471-4615",
  "span": [4471, 4615],
  "clause_sha256": "3aff00e7…",        // the exact bytes at `span`
  "decision": "ACCEPT",                // ACCEPT | NOT_APPLICABLE | NACK
  "basis": "…the reader's own reason, quoted from the ruling…",
  "reader_id": "ORIGINAL_SBL_PIPD_READER",
  "decided_at": "2026-11-17T00:00:00+08:00",
  "claim_ceiling": "READER_ADJUDICATION_NOT_PRODUCT_ACCEPTANCE",
  "signature": {
    "alg": "ed25519",
    "reader_id": "ORIGINAL_SBL_PIPD_READER",
    "payload_sha256": "…",
    "signature_hex": "…"
  }
}
```

The signature covers the canonical JSON of exactly these fields:

```
schema, source_id, subject_sha256, clause_id, span, clause_sha256,
decision, basis, reader_id, decided_at, claim_ceiling
```

so a signature binds the **decision to the clause**, not just the decision word.

### `UNVERIFIED` is the default

A record is `VERIFIED` only when all of the following hold. Everything else is `UNVERIFIED` (or
`REFUSED`, when the record is positively wrong):

1. it carries a `signature.signature_hex`;
2. `signature.payload_sha256` recomputes over the record's own binding fields;
3. the Ed25519 signature verifies against a public key read from
   **`contracts/reader-enrollment.json`** — never from the record.

`reader_id`, `reader_identity` and `authority_ref` are documentation. Anyone can type a reader's
name into a file, and a path is not a proof, so a record carrying only those is `UNVERIFIED` with
`ADJUDICATION_UNSIGNED`.

The committed enrollment ships with an **empty** `reader_public_hex` and
`"state": "AWAITING_ORIGINAL_READER_KEY"`. Until the owner enrolls the original reader's key,
every record is `UNVERIFIED` — including one that is correctly signed with some other key. That is
the correct state of the tree today, not a limitation to be worked around.

### Refusal codes

| code | meaning |
|---|---|
| `ADJUDICATION_UNSIGNED` | no signature; a name or a path is not proof → `UNVERIFIED` |
| `READER_KEY_NOT_ENROLLED` | the committed enrollment has no reader key → `UNVERIFIED` |
| `READER_ENROLLMENT_NOT_TEST_FIXTURE` | `--reader-enrollment` was pointed at a non-test enrollment → refused |
| `ADJUDICATION_SIGNATURE_INVALID` | Ed25519 verification failed |
| `ADJUDICATION_PAYLOAD_MISMATCH` | `payload_sha256` does not cover the record's own binding fields |
| `ADJUDICATION_SUBJECT_MISMATCH` | the record binds a different subject digest |
| `ADJUDICATION_SOURCE_MISMATCH` | `clause_id` / `span` / `clause_sha256` does not resolve to the bound clause, or the digest does not match the subject bytes |
| `ADJUDICATION_SOURCE_UNKNOWN` | the Source ID is not in the bound index |
| `ADJUDICATION_MISSING` | a Source ID in the bound index has no verified decision |
| `ADJUDICATION_DUPLICATE` | two records for one Source ID |
| `ADJUDICATION_UNKNOWN_DECISION` | a decision token outside the three |
| `ADJUDICATION_READER_MISMATCH` | the record names a different reader than the enrolled one |
| `SELF_ACCEPT` | the record's reader is the maker (`TQ_SOD`) |
| `INTAKE_INVALID_IS_NOT_A_DISPOSITION` | the basis is a compiler refusal code; a refusal may not be recorded as a decision |

### `adjudication.verdict`

`REFUSED` (any record positively refused) > `UNVERIFIED` (any record unverified, or an index row
undecided) > `INCOMPLETE_DENOMINATOR_UNDECLARED` (no `--source-index`) >
`INCOMPLETE_SUBJECT_UNBOUND` (no `--subject`) > `INCOMPLETE_PARTIAL_COVERAGE` >
`COMPLETE_FIXTURE_KEY_ONLY` > `COMPLETE`. A decision histogram (`by_decision`) counts **verified**
decisions only, so a NACK that failed verification never appears as a decided NACK.

### The four completion gates

Completion is a claim about a **declared denominator**, so it cannot be reached by omission. Every
run reports `complete`, `completion_refusals`, `coverage` and `denominator_declared`; a consumer
reads those, never the exit code — see `CONSUMER_CONTRACT.md`.

| gate | refused/capped by | what it stops |
|---|---|---|
| G1a no `--source-index` | `ADJUDICATION_DENOMINATOR_UNDECLARED` → `INCOMPLETE_DENOMINATOR_UNDECLARED` | a records-only file whose "denominator" is just the number of records it happens to carry |
| G1b no `--subject` | `ADJUDICATION_SUBJECT_UNBOUND` → `INCOMPLETE_SUBJECT_UNBOUND` | a verified signature over a binding no byte of the pinned subject was checked against |
| G2 signed subset | `ADJUDICATION_PARTIAL_SIGNATURE_SET`, `complete: false` | 3 signed rows reporting themselves as the 428-source wave |
| G3 partial aggregate | `ADJUDICATION_ORIGINAL_READER_UNVERIFIED`; per-row flag on every row | `original_reader_signature_verified` flipping true from partial coverage |
| G4 consumer | `consumer_gate()` → `CONSUMER_*`; `--require-consumer-gate` → exit `3` | an automated consumer accepting exit 0 / bundle `PASS` / `COMPLETE_FIXTURE_KEY_ONLY` as a decision |

`consumer_gate()` is the **only** lawful passage: `accepted is True`. The three signals that look
like one are each individually insufficient, and the gate publishes the mapping it refuses them
with (`insufficient_signals`, `signal_refusals`):

| signal | what it is | refused by |
|---|---|---|
| exit `0` | the bundle did not fail | `CONSUMER_VERDICT_NOT_COMPLETE` |
| `bundle.verdict == "PASS"` | four objects are schema-and-trace valid | `CONSUMER_NO_ADJUDICATION_BLOCK` / `CONSUMER_VERDICT_NOT_COMPLETE` |
| `adjudication.verdict == "COMPLETE_FIXTURE_KEY_ONLY"` | every signature verified, under a **fixture** key | `CONSUMER_VERDICT_NOT_COMPLETE` + `CONSUMER_ORIGINAL_READER_UNVERIFIED` |

Each has a NEG that fails if it ever becomes sufficient
(`tests/test_clause_set_adjudication.py::ConsumerGateIsTheOnlyPassage`), and the gate result is
stamped into the returned payload at `adjudication.consumer_gate`.

### H-01 — what the hold waits on

H-01 is the hold on the wave's undisposed Source IDs, and it is released by exactly one thing: the
**original Reader's own per-Source-ID disposition** — one `ACCEPT` / `NOT_APPLICABLE` / `NACK` per
Source ID of the declared denominator, bound to the pinned subject, signed under the key the owner
enrolled for that reader. It is *not* released by a signature as such, by a bundle verdict, by an
exit code, or by any number of fixture-signed rows.

A `TEST_FIXTURE_ONLY` key is **structurally incapable** of releasing it: `_enrollment()` marks the
run `fixture_key: True`, every row's `original_reader_signature_verified` stays false, the verdict
is capped at `COMPLETE_FIXTURE_KEY_ONLY`, and `hold_h01.dispositions` counts only rows whose per-row
original-reader flag is true — which is zero for a fixture. 428 of 428 fixture-signed rows therefore
report `hold_h01.state == "HELD"`. That is the correct state, and it is asserted
(`test_h01_hold_is_never_released_by_a_fixture_key`). The hold is reported per run as:

```jsonc
"hold_h01": {
  "hold_id": "H-01",
  "state": "HELD",                                     // RELEASED only on verdict COMPLETE
  "released_by": "ORIGINAL_READER_PER_SOURCE_ID_DISPOSITION",
  "dispositions": {"ACCEPT": 0, "NOT_APPLICABLE": 0, "NACK": 0},
  "fixture_key_cannot_release": true,
  "why": "…"
}
```

`original_reader_signature_verified` is now **per row** (`records[i].original_reader_signature_verified`,
true only for a row whose own signature verified against a non-fixture enrolled key) and the
aggregate is true only when every row of the declared denominator carries the per-row true. With no
key enrolled, all of them are false — which is the correct state of this tree.

### Test-fixture keys

`sig` verification has to be demonstrable before the original reader publishes a key, so
`--reader-enrollment <path>` accepts a file **only** when it declares
`"authority": "TEST_FIXTURE_ONLY"`. In that mode a fully verified set reports
`COMPLETE_FIXTURE_KEY_ONLY`, `original_reader_signature_verified: false` and
`claim_ceiling: FIXTURE_KEY_NOT_ORIGINAL_READER`. A fixture key proves the verifier runs; it never
reads as original-reader authority.
