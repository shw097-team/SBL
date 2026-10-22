NONCE: EXECUTE-R152-005857-0281

Begin your reply with exactly this token on its own line: EXECUTE-R152-005857-0281

NONCE: EXEC-R152-W15B-NONCE-1F7C82DA

Begin your reply with exactly this token on its own line: EXEC-R152-W15B-NONCE-1F7C82DA

# EXECUTE brief: re-emit the DELIVERY_READY guard proposal under the bounded writer

You are the EXECUTE lane (SBL-EXECUTE & Codex bounded writer), model `opencode-go/minimax-m3.1-flash-free`.

## Write set — do not write outside it

    workers/candidate_proposals/w15_gate/**

`src/hg_kseos/**` is READ-ONLY for you. You are producing a candidate diff that a control-plane owner may apply; you are
not applying it.

## Task

1. Read `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lifecycle.py`.
2. Locate the `CS-A D4` guard inside `transition()`. Measured fact: it fires only for `to_state == "DELIVERED"`, so a
   project with FAILED work orders can still reach `DELIVERY_READY`, a name that reads as ready.
3. Write `workers/candidate_proposals/w15_gate/proposal.diff`: a unified diff that extends the guard to
   `to_state in ("DELIVERY_READY", "DELIVERED")` and appends `(refused at {to_state})` to the error message.
4. Write `workers/candidate_proposals/w15_gate/VERDICT.json` with:
   `{"anchor_found": true|false, "guard_line_before": "<the exact line>", "guard_line_after": "<the exact line>",
     "diff_lines": <int>, "applied": false, "why_not_applied": "control-plane change requires a HGK owner"}`
5. Do not modify `lifecycle.py`. Do not run `git apply`.

## Acceptance for this brief

- `proposal.diff` exists and contains exactly one hunk touching the guard condition and the error string.
- `VERDICT.json` records the before/after line verbatim, so a checker can confirm the diff matches the file without
  trusting your summary.
