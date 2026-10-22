# VERIFY_SECURITY — independent challenge, pass 2 (read-only; the previous verdict said FAIL, check whether it still does)

You are the independent acceptance officer for one round tree. **Read-only**: change nothing, create nothing, and do not
run any command that writes into `C:/Projects/Agent_Workspace/_r152_ev` (use `$TMPDIR` for scratch, and it is outside
every repo). Your verdict is your final message; it is captured by the receipt.

## What changed since pass 1 (which returned FAIL, `workers/verify/VERDICT_PASS1.md`)

1. `C6-raw-evidence` — `tools/q5_lifecycle_probe.py` now persists each verb's full stdout/stderr under
   `workers/q5_tools/raw/` with sha256 sidecars, and `LIFECYCLE_RECEIPT.json` carries the raw paths/truncation flags.
   Re-derive this yourself: open the receipt, open the raw files, confirm the observation equals the raw text.
2. `MANDATE-AUDIT` — `tools/mandate_gate.py audit` now returns AUDIT_CLEAN over 26 items. Re-run it.
3. `A4` (Q3/M2) — a re-run of the isolated E2E chain landed with a **green** lane receipt
   (`receipts/dispatch/EXECUTE__BRIEF_Q3_E2E.json`, ok=true, 629.89 s, nonce present) and
   `workers/q3_e2e/Q3_RESULT.json` claims six true predicates. Verify the claims against the raw stage logs
   (`workers/q3_e2e/logs_q3b/`) and against the sha256 pair it reports.
4. `A5` (APPLIED) — `workers/candidate_proposals/w06_kinds2/APPLIED.json` plus `workers/q1_apply/ALIAS.json`.
5. `A7` (REPAIR) — the doctor crash was repaired to a typed refusal; the lane receipt for that repair is **RED**
   (900 s timeout) and the product change is disclosed as red in `QUEUE_R15_2.json` (`lane_receipt_red`) and
   `TT_R15_2_REGISTER.json`. Decide whether a product change with a red lane receipt may be counted at all.
6. A regression this round introduced (the eight-kind candidate dropped `SKILL`, breaking
   `tests/test_core_modules.py::test_routing_positive_default_policy`) was repaired additively; the old test was not
   edited. Confirm with git (the test file is byte-identical to HEAD) and with `python -m pytest -q -p no:cacheprovider
   tests/test_core_modules.py tests/test_kind_matrix.py`.

## What to attack

- Does any claim exceed its evidence? Name the claim and the missing artefact.
- Is the mutation detection real (assertion failure) or an artefact of an import error / missing file? Read the raw log.
- Does `Q3_RESULT.json`'s "affected_regressions_pass" rest on a suite run that actually happened, or on a summary?
- Is any "DONE" item bound to a receipt about a different subject (receipt-name collision is a known defect this round:
  `TT_R15_2-RECEIPT-NAME-COLLISION`)? Check the receipt's brief path against the item.
- Is the claim ceiling honest (`PROMPT_COMPILE_PASS ≠ RUNTIME_READY ≠ INDEPENDENT_PASS ≠ HOST_INSTALLED ≠ RELEASED`)?
- The round pauses the autonomy cron; is that disclosed where a reader would find it?

## Output

Your final message must be:

```
VERDICT: PASS | PARTIAL | FAIL
basis: <one paragraph>
1) C6-raw-evidence — <PASS/FAIL> <evidence you re-derived>
2) MANDATE-AUDIT — <...>
3) A4 Q3/M2 — <...>
4) A5 APPLIED — <...>
5) A7 REPAIR (red receipt) — <...>
6) SKILL regression repair — <...>
7) claim ceiling — <...>
findings: <numbered, each with the exact file and the exact line/claim>
conditions: <what must be true before this can be called an independent PASS>
```

Do not soften a FAIL to be agreeable, and do not call anything an independent PASS: you are one principal inside the
same host and family.
