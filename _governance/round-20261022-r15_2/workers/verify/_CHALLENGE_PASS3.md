NONCE: VERIFY-R152-PASS3-NONCE-555f361e

Begin your reply with exactly this token on its own line: VERIFY-R152-PASS3-NONCE-555f361e

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# VERIFY_SECURITY — independent challenge, pass 3 (read-only; confirm or refuse the two repairs from pass 2)

Read-only. Create nothing, change nothing, use `$TMPDIR` (outside every repo) for scratch. **Budget: at most 12 shell
commands** — enough to re-derive the two repairs, not enough to re-audit the whole round. Your final message is the
verdict; it is captured by the receipt.

## Pass 2 returned FAIL with these findings. Two were repaired; check them yourself, do not take this text's word.

1. **C6 raw evidence** was FAIL because identical command tails overwrote each other (4 of 11 captures no longer
   matched their recorded bytes/sha) and there were no sha sidecars.
   Repair claimed: monotonic 3-digit capture prefix + a `.sha256` sidecar per raw file.
   Re-derive: for every row in `workers/q5_tools/LIFECYCLE_RECEIPT.json` that carries `raw_path`, hash the file on disk
   and compare with `raw_sha256`; confirm the `.sha256` sidecar agrees; confirm the paths are distinct.
2. **A7 doctor repair** was FAIL because the product change's lane receipt was RED (900 s timeout, no nonce), so the
   change could not count as completion.
   Repair claimed: a third dispatch with a hard 8-command budget produced a green receipt for the same behaviour —
   `receipts/dispatch/EXECUTE__Q5_DOCTOR_GREEN.json` (ok=true, 102.12 s, nonce present) with
   `workers/q5_repair/DOCTOR_REPAIR.json` (doctor rc 2, typed `SBL_E_MANIFEST_UNTRUSTED`, no traceback, 9 tests pass,
   `product_code_changed: false`).
   Attack this specifically: is a green receipt that re-earns the *behaviour* enough when the *code change* was authored
   by the red-receipt lane? Say plainly whether this closes A7 or only narrows it.

## Unchanged from pass 2 (do not re-litigate, just say if it still bites)

- `mandate_gate audit` accepts a bound receipt without checking it exists, is green, or matches the item — recorded as
  `TT-R15.2-MANDATE-AUDIT-IS-SHALLOW`. The round compensates by hand-matching each receipt's brief path to its item.
- A4's `outside_scope_unchanged` predicate still has no before/after content manifest.
- The claim ceiling: one host, one family; this cannot be an independent PASS.

## Output

```
VERDICT: PASS | PARTIAL | FAIL
basis: <one paragraph>
1) C6 raw evidence — PASS/FAIL <what you re-derived: rows, mismatches, sidecars>
2) A7 doctor repair — PASS/FAIL/NARROWED <and why>
3) what still bites — <numbered>
conditions before an independent PASS could exist — <numbered>
```

Do not soften a FAIL to be agreeable; do not upgrade anything to independent acceptance.
