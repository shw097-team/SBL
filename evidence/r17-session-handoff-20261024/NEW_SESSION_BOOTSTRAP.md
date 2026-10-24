# NEW SESSION BOOTSTRAP — how to resume R17 without reading the old chat

Read these in order. Each step has a pass/fail you can check mechanically.

## Step 1 — load the machine truth

```bash
cd C:/Projects/Agent_Workspace/var/R17-20261023
python -c "import json;d=json.load(open('HANDOFF/SESSION_STATE_R17.json'));print(d['handoff_id'],d['queue']['rows'],d['queue']['conservation'])"
```

PASS when `handoff_id == "R17-HANDOFF-20261024T114018"`, `rows == 146`, and `conservation.ok is True`.

## Step 2 — confirm the queue is the only work authority

`WORK_QUEUE_R17.json` is the queue; `HANDOFF/R17_145_STATUS.csv` is the per-ID view; `ROW_AUDIT_R17.json`
is the 145-row audit. Do not create a second queue, scheduler or issuer.

## Step 3 — confirm nothing moved under you

Re-run `git -C <repo> rev-parse --short HEAD` for SBL/HG-KSEOS/Fabric/PIPD and compare with
`HANDOFF/REPO_STATE.json`. A difference is not an error: it is drift to re-measure before any claim.

## Step 4 — pick exactly one legal next action

Agent-doable, in this order:
1. `C18-MANIFEST` — bind the TQAEP 96-cell denominator from DOC-08 (currently `PROBE_UNBOUND`).
2. `DEST-FIXTURES` — build DEST-01..16 in isolated copies.
3. `W01-CONF` — produce a real conformance receipt, then re-probe (never infer from ABI counts).
4. `EXECUTE` lane settle — restart `tools/ocg_shim_10105.py`, then dispatch with
   `--prompt "$(cat BRIEF.md)"` (inline text; nonce must be the first line).

Everything else needs an owner or a native principal; see `OPEN_TT_FAR_OWNER_DECISIONS.md`.

## Step 5 — do not do these

- Do not claim product acceptance, native effect, independent acceptance or release.
- Do not publish contaminated raw, keys or personal paths.
- Do not resume a paused cron, start background processes, or force push.
- Do not treat `PROBE_*`, `DONE_DOC_RED`, `DONE_NOFIT` or `PARKED_*` as product DONE.
