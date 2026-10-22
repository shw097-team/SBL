# WO-R14-TS23-M2-TRIAD (live spine record) — what passed, what did not

**Verdict recorded in the live spine: FAIL.** This is deliberate and it is not a statement that the work is worthless.

## What passed (verified by the round orchestrator, not by the subagent's own report)

All three generated programs were re-run here, on real inputs, with real output:

```
ts23-newlines  SBL/README.md -> {"bytes": 5765, "newlines": 116, "sha256": "1ae8aaf2..."}   exit 0
ts23-headings  SBL/README.md -> 10 headings, level+line+text                                exit 0
ts23-review    --max-steps 2 workspace_queue.json -> {"halt_reason": "BUDGET", "remaining": 1, ...}  exit 0
```

Red -> green was recorded per program (test written first, exit 1 before the code, exit 0 after).

## Why the verdict is FAIL

The TaskSpec's acceptance step requires an **independent principal** to review the result. No independent model was
spawned; the checker was a *label* attached to a receipt, not a second reviewer reading the artefacts. The subagent
said so itself, and recording PASS on that basis would be exactly the self-acceptance this round exists to eliminate.

Two further deviations are disclosed rather than smoothed over:

1. The native chain ran against an **isolated spine backup** because the live DB sat outside the permitted write roots.
   This row is the live-spine record created afterwards; it is not a replay of the original transaction.
2. An initial pip run leaked transient caches into the user Temp directory. The corrected reinstall was confined, but
   the original deviation happened and is kept on the record.

## Consequence

M2 is **not** passed. The dogfood change exists and demonstrably works; the acceptance that would make it governed is
missing, and that is an Owner/independent-reviewer act, not something the maker can supply for itself.
