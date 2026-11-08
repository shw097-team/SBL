# ACCEPTANCE OFFICER BRIEF — ROUND 8 (receipt self-reference removed; confirm the shipped state)

You are the **Acceptance Officer** for round `FHS_W0_R13_ACCEPTANCE_20261108`, second pass.
You are a distinct process with a distinct model from the maker, running read-only.

## What happened in round 1

You returned **NACK** three times, each correctly. Round 1: G19 covered only the r6-focus subset.
Round 2: after that repair G19 reported "25 roots" while visiting 24 and performed no root walk.
Round 3, two findings: (a) the saved `out\GATE_R13.json` still recorded two blocking failures because
it had been written before the repairs — a stale report shipped beside a green gate; (b) the rewritten
G19 collected member digest/size mismatches into a list and **never judged it**, so the negative
control no longer bit. Both are repaired: the drift list is judged again, and the report is now
regenerated after the payload exists, then re-staged, so the shipped summary reads 18/17/0/1.

All verdicts are on file: `VERDICT_R13_OFFICER_R1.json`, `_R2.json`, `_R3.json`. The maker has repaired the
check and claims it now covers every declared group, every member and every root. **Your job is to
decide whether that claim is true — not to trust this paragraph.**

## What to check (all 19)

Round 7 returned NACK on item 9: the shipped gate report was stale, and correctly so, because the
receipts bound that report while the report's verdict (via G26) depends on the receipts - a cycle.

The repair is structural, not a re-run: **a receipt now binds only artefacts that cannot move because the
receipt did.** Concretely, `receipts\W0-RCPT-*.json` bind the candidate document and, in `source_sha`, the
31 source documents. They no longer bind `out\GATE_R13.json` or the officer bundle, and each receipt
carries a `why_only_inputs_are_bound` field saying why.

Check that the saved `out\GATE_R13.json` summary now agrees with a live run, and that no receipt binds an
artefact whose content depends on receipts. If you find one, it is blocking.

Beyond the 19 items, confirm specifically that each `receipts\W0-RCPT-*.json` binds the digest of
`officer\VERDICT_R13_OFFICER_FINAL.json` **as it exists now**, and that the bundle records six rounds
with the terminal round being this one's predecessor. If a receipt still names an older bundle digest,
that is a blocking defect.



Round 5's blocking finding was that the six receipts bound `out\GATE_R13.json` by a digest captured
before the gate was re-run, so they authenticated a report that was no longer shipped. The repair is not
a rebuild of the receipts: it is a gate check. `tools\gate_r13.py` now has **G26 RECEIPT_BINDING**
(BLOCKING), which recomputes every receipt's `evidence_refs[].sha256` and its `candidate_sha` against the
files on disk. Verify that it exists, that it is in the check list, and that it would catch the defect
you found - then confirm the round's verdict line reports 19 checks.



Three new items since round 4. The round now carries six receipts, one per primary work package
(WP-FHS-00/01/15/16/19/21), plus a signature instrument:

17. **Receipt field set.** For each of the six `receipts\W0-RCPT-WP-FHS-*.json`, confirm the seven fields
    required by L0.md:377 are present and non-empty: Subject, SourceSHA, CandidateSHA, Scope, Host,
    PolicyEpoch, OriginalConsumer. Confirm `CandidateSHA` equals the sha256 of
    `writeback\W0\FHS_PIPD-LS-PKG_W0_r13.md` as you compute it, and that `Status` is
    `OWNER_READER_ACK_PENDING` rather than any accepted state.
18. **SourceSHA is a set digest, not a single file's.** `tools\build_receipts.py` defines it as sha256 over
    sorted `name<TAB>sha256` lines of the 31 documents. Read that function and satisfy yourself the rule
    is what the receipt says it is; if you can, recompute it and compare.
19. **The signature instrument is unsigned and says so.** `receipts\OWNER_SEMANTIC_ACK.json` must carry
    `signature.signed_by = null`, `provenance = PENDING_OWNER_SIGNATURE`, and a ceiling of
    `OWNER_SEMANTIC_ACK` - not ORIGINAL_ACK, not NATIVE_SIGNED. A pre-filled or implied signature is a
    blocking defect.

Also confirm chapter 14.8 of the document states the same field set and the same ceiling, and that 14.5
no longer presents ORIGINAL_ACK as unreachable now that the ADR-05 route is recorded.



Item 9: read `out\GATE_R13.json` and confirm its `summary` block (`total`, `pass`, `blocking_fail`,
`open_reporting_findings`) agrees with a live run you perform yourself.
Item 16: the negative control must return `"check_bites": true`. If it returns false, the check does
not refuse a tampered member and the finding stands.


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
  "officer": "acceptance-officer/codex-cli/gpt-6.1-sol/round-8",
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
