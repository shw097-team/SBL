# Round-20261022-r15_2 — read this before acting

**Mandate is enforced, not remembered.** The role split lives in `MANDATE_R15_2.json`:

| role | lane | provider/model |
|---|---|---|
PLAN | PLAN | `openai-codex/gpt-6.1-sol` |
EXECUTE | EXECUTE | `opencode-go/minimax-m3.1-flash-free` |
VERIFY | VERIFY_SECURITY | `openai-codex/gpt-6.1-sol` |

Before doing research, a product write, or an acceptance check, run:

    python tools/mandate_gate.py check --role PLAN|EXECUTE|VERIFY

If it refuses, dispatch first and make it cheap:

    python tools/run_lane.py --role PLAN --brief <brief.md>

Before declaring anything finished:

    python tools/mandate_gate.py audit      # exits 1 if a DONE item has no bound lane receipt
    python tools/continuation_guard.py      # exits 2 if agent work remains, a parked item is unissued, or a lease is stale

Neither gate may be edited to pass. A red gate is a finding, not an obstacle.
