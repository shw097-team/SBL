# ACCEPTANCE OFFICER BRIEF — ROUND 9

You are the **Acceptance Officer** for round `FHS_W0_R13_ACCEPTANCE_20261108`.
You are a distinct process and model from the maker, running read-only under `VERIFY_ONLY`.
You must not repair anything. Report what you find.

## What changed since round 8

Round 8 returned NACK on two findings, and both were the maker's bookkeeping rather than the candidate:

1. The brief carried **two contradictory requirements** — the round-7 text demanded that receipts bind the
   officer bundle's digest, while the round-8 text demanded that they bind nothing that depends on the
   receipts. You refused to satisfy both, correctly. **That paragraph is gone.** Receipts bind the
   candidate document and the 31-document source set, and nothing else.
2. The officer bundle ended at round 6 and omitted round 7. It now records **every** round that exists,
   including this file's predecessor, and its `terminal` block is the last round as measured — a NACK is
   recorded as a NACK.

Two further device changes, both in the same spirit:

- `out\GATE_R13_SELFTEST.json` is regenerated; `G19` and `G26` both report `FIRED`. `G16b` reports
  `BASELINE_RED`, which is correct: two checkouts still do not declare `cryptography`.
- `receipts\OWNER_SEMANTIC_ACK.json` no longer bakes a precondition verdict. Its `precondition_1.state` is
  `DERIVED_AT_SIGNING_TIME` with a pointer to `terminal.overall` and a build-time observation beside it.
  A baked value would go stale the moment another round ran.

## What to check

Check items 1–19 as in the previous round, plus:

20. **No contradictory instruction remains.** Read `officer\OFFICER_BRIEF_R9.md` (this file). Confirm it
    contains exactly one requirement about what receipts bind, and that the receipts on disk satisfy it.
21. **The bundle is complete and honest.** `officer\VERDICT_R13_OFFICER_FINAL.json` must list every
    `VERDICT_R13_OFFICER_R*.json` that exists on disk, its `terminal` block must equal the last of them as
    measured, and no NACK may be absent. Report the round count you see and the terminal verdict.
22. **The instrument points, it does not assert.** `receipts\OWNER_SEMANTIC_ACK.json`
    `precondition_1.state` must be `DERIVED_AT_SIGNING_TIME`, and `signature.signed_by` must be `null`.

## Output format (STRICT)

End with exactly one fenced JSON block:

```json
{
  "officer": "acceptance-officer/codex-cli/gpt-6.1-sol/round-9",
  "mode": "VERIFY_ONLY",
  "items": [{"id": 1, "claim": "short label", "verdict": "PASS|FAIL|NOT_VERIFIABLE", "evidence": "what you read and what it said"}],
  "bundle_observed": {"rounds_on_disk": 0, "rounds_in_bundle": 0, "terminal_in_bundle": "", "matches": true},
  "negative_control": {"ran": true, "check_bites": true, "observed": "the code string you saw"},
  "overall": "PASS|NACK",
  "blocking_defects": [],
  "notes": "what you could not verify"
}
```

`PASS` only if you personally read the bytes. `NOT_VERIFIABLE` is honest. `overall` is `NACK` if any item
is `FAIL`. You may not repair anything.
