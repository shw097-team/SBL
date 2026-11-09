# ACCEPTANCE OFFICER BRIEF — ROUND 3 (re-check after the second NACK)

You are the **Acceptance Officer** for round `FHS_W0_R13_ACCEPTANCE_20261108`, second pass.
You are a distinct process with a distinct model from the maker, running read-only.

## What happened in round 1

You returned **NACK** twice, and both times correctly. Round 1: G19 covered only the r6-focus subset.
Round 2: after that repair, G19 reported "25 roots" while visiting 24 (a root with `required=false` was
skipped) and performed no root walk at all, contradicting the document's own claim. Both verdicts are
on file at `officer\VERDICT_R13_OFFICER_R1.json` and `officer\VERDICT_R13_OFFICER_R2.json`. The maker has repaired the
check and claims it now covers every declared group, every member and every root. **Your job is to
decide whether that claim is true — not to trust this paragraph.**

## What to check (all 16)

Re-check items 1–15 from round 1 against the current bytes, and add:

16. **Negative control.** Run, read-only:
    `python officer\negative_control.py` from the round directory. It loads the copy register, tampers
    one member digest **in memory only**, and calls the check directly. Report the exact JSON it prints.
    `"check_bites": true` means the check refuses a tampered member with `MEMBER_DIGEST_DRIFT` while the
    real register still passes. Read the script first and satisfy yourself that it really tampers the
    field the check reads, and that it performs no write.

For item 12 specifically, read `tools\gate_r13.py`'s `g19_copy_register` and confirm from the code that it:
walks `names_exact` **and** `names_normalised` (not `r6_focus`), re-hashes **every** member of every
group, re-checks **every** root, and recomputes each group's `distinct_digests` rather than reading it.
Then compare its reported coverage against `COPY_REGISTER_ALL.json`'s own declared totals
(`len(names_exact)`, `len(names_normalised)`, `len(roots_scanned)`, `scan_bounds.files_hashed`).
The current run reports 45+45 groups, 437 copies re-hashed, 25 roots — check those numbers are
consistent with the artifact rather than merely printed.

Also verify the two gate runs claimed by the maker:

- `python tools\gate_r13.py --round . --skip-hygiene` in the round directory → the verdict line. Note
specifically what G19 prints: the number of groups, the number of copies re-hashed, how many
declared-present roots were actually walked, and whether any fixture directories were excluded by name.
Compare each number against what the code does and against the artifact's own declared totals.
- the same command with `--profile payload --scope payload` from
  `out\stage\sbl\evidence\fhs-w0-r13-repair-20261108` → the verdict line, and note which checks that
  scope **excludes** and whether the exclusion is announced in the output.

## Output format (STRICT)

End with exactly one fenced JSON block:

```json
{
  "officer": "acceptance-officer/codex-cli/gpt-6.1-sol/round-3",
  "mode": "VERIFY_ONLY",
  "items": [{"id": 1, "claim": "short label", "verdict": "PASS|FAIL|NOT_VERIFIABLE", "evidence": "what you read and what it said"}],
  "negative_control": {"ran": true, "check_bites": true, "observed": "the code string you saw"},
  "overall": "PASS|NACK",
  "blocking_defects": [],
  "notes": "what you could not verify, and anything a reader must know"
}
```

`PASS` only if you personally read the bytes. `NOT_VERIFIABLE` is honest; never upgrade it.
`overall` is `NACK` if any item is `FAIL`. You may not repair anything you find.
