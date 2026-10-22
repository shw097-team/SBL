# VERIFY_SECURITY — independent challenge, pass 4 (read-only; ONE question: does the green receipt now own the patch?)

Read-only, `$TMPDIR` for scratch, **at most 8 shell commands**. One question only; everything else about this round has
already been adjudicated in passes 2 and 3 (`workers/verify/VERDICT_PASS2.md`, `VERDICT_PASS3.md`).

## Pass 3 said

`A7 → NARROWED, not closed`: the behaviour was evidenced by a green receipt, but `product_code_changed: false` meant
the patch had been authored under a **red** receipt, so the change could not count as completion.

## What was done about it (not a claim — check it)

1. The patch was reverted to its pre-repair bytes so three committed oracle tests went red again.
2. A bounded lane (10-command budget, 900 s) then authored the change itself:
   `receipts/dispatch/EXECUTE__Q5_DOCTOR_AUTHORED_GREEN.json` — expect ok=true, ~120 s, nonce present;
   `workers/q5_repair/DOCTOR_REPAIR2.json` — expect `product_code_changed: true`, `shell_commands_used: 10`,
   9 passed; `workers/q5_repair/DOCTOR_REPAIR2.diff` — the patch as it stands.

## Judge exactly this

- Does the green receipt's own retained stdout show the lane **writing** the patch (an edit/apply step against
  `sbl_stack/__init__.py`), or only running tests against someone else's file?
- Does the lane's own command count in the raw log match the `shell_commands_used` it reported? (pass 3 caught a lane
  claiming 8 while its log held 16 — count again, do not trust the summary.)
- Is the resulting state internally consistent: the diff, the typed code (`SBL_E_COMPONENT_UNRESOLVED`), and
  `python -m pytest -q -p no:cacheprovider tests/test_stack_verbs.py` passing?

## Output

```
VERDICT: PASS | FAIL
A7 — CLOSED | STILL_NARROWED <one line>
evidence: <what you re-derived: gh events, command count you measured vs reported, test result you ran>
still_open: <anything that leaves A7 short of mandate-compliant completion>
```

This remains a same-host, same-family challenge. If the answer is "closed", say closed and name the residual limits
without softening them; if it is not, say so.
