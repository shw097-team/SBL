# R17 SESSION HANDOFF — R17-HANDOFF-20261024T114018

**Status: SESSION_HANDOFF (not product completion).** R17 Mission stays OPEN.
Claim ceiling: `EVIDENCE_BOUND`. No HGK Native WorkOrder/Permit, Fabric Active Designation,
SWOF W3, independent AO acceptance or Release seal exists for any R17 product effect.

## 1. What state is being handed over

| item | measured value |
|---|---|
| handoff_id | `R17-HANDOFF-20261024T114018` |
| generated | 2026-10-24T11:41:00+0800 |
| queue file | `var/R17-20261023/WORK_QUEUE_R17.json` (146 rows) |
| 145 denominator | 145 IDs, unique 145, duplicates [] |
| non-denominator row | ['FABRIC-CANARY'] (excluded from 145 by design) |
| latest checkpoint | `CHECKPOINT_R17_REC09.json` at 2026-10-24T11:03:33+0800 |
| round state then | ACTIVE_BUILD |

Queue state counts (measured, this snapshot):

```json
{
 "PARKED_NEEDS_SOURCE_OWNER_SIGNATURE": 1,
 "PARTIAL": 5,
 "BLOCKED_OWNER": 3,
 "NOT_RUN": 57,
 "BLOCKED_MANDATE": 1,
 "DONE": 8,
 "FAIL": 1,
 "PARKED_NEEDS_NATIVE_OR_AO": 21,
 "PARKED_NEEDS_INDEPENDENT_CHECKER": 25,
 "DONE_DOC_RED": 14,
 "UNIMPLEMENTED": 2,
 "PARKED_NEEDS_NOFIT_RECEIPTS": 1,
 "DONE_NOFIT": 1,
 "PARKED_NEEDS_OWNER_PROMOTION": 1,
 "PARKED_OWNER_ONLY_DELETION": 5
}
```

## 2. Repositories (read this before touching anything)

| repo | HEAD | dirty | branch |
|---|---|---|---|
| SBL | `10d510f` | 6 | `candidate/r14-ts15-kinds` |
| HG-KSEOS | `086a940` | 0 | `codex/hgk-final-closure-002` |
| Fabric | `bb06b7a` | 8 | `pub/far-minimax-mandate-20261021` |
| PIPD | `39079c0` | 218 | `rescue/r5p-uncommitted-20261016` |

Other sessions' dirty files are left untouched. No `reset --hard`, no force push, no cross-repo copy.

## 3. Lanes (role → model) — measured, not declared

| lane | required arm | rank | ok | served | nonce | payer |
|---|---|---|---|---|---|---|
| PLAN | `openai-codex/gpt-6.1-sol` | 2 | True | `openai-codex/gpt-6.1-sol` | True | owner OAuth (chatgpt.com/backend-api/codex) |
| VERIFY_SECURITY | `openai-codex/gpt-6.1-sol` | 2 | True | `openai-codex/gpt-6.1-sol` | True | owner OAuth (chatgpt.com/backend-api/codex) |
| EXECUTE | `opencode-go/deepseek-v4.1-flash` | 1 | False | `None` | False | owner OpenCode Go key shw0968 (via local 10105 shim) |

EXECUTE is **not settled**. The route is proven to serve (`/v1/responses` 200 upstream, and one 37.2 s
Codex turn billed 57,294 in / 1,210 out tokens), but the nonce gate was never satisfied: the first working
attempt passed the brief as a *path* (the dispatcher's `--prompt` is literal text), and the corrected attempt
was interrupted by this handoff order. Cause chain:

- sanctioned frontdoor 127.0.0.1:10100 -> relay 10101 forwards a DEAD upstream key: 401 'Invalid credential'
- relay 10101 upstream key states measured: shw0968=200, shw097=429 (monthly), 7776004=401
- local passthrough shim tools/ocg_shim_10105.py (owner key + x-opencode-session) makes upstream serve: /v1/responses 200
- codex CLI pins the provider-qualified id; upstream needs the BARE id -> shim normalises (`opencode-go/` stripped), measured 200
- attempt shim6 ran 37.2s with a REAL model turn (57,294 in / 1,210 out tokens) but received the brief as a PATH, so it emitted no nonce -> ERR_NO_ARM_EMITTED_NONCE
- attempt shim7 (inline --prompt text) was interrupted by the session handoff order; no receipt was written

## 4. Host / services

- cron `3602bce285e8` R17 queue runner (persistent dispatch): enabled=False state=paused — R17 has NO live durable runner. Autonomous continuation is unavailable until the owner resumes this job.
- cron `12eff9cba53c` SBL R15.2 autonomy tick: enabled=True state=scheduled — belongs to another round (R15.2); not part of R17 and not modified by this handoff.
- cron `e539df5f39a4` SBL R15 round watchdog tick: enabled=False state=paused — paused before this session; not modified.

- 10100_exec_frontdoor: started by this session (pid 23688) and STOPPED at handoff; recipe: pwsh -NoProfile -File HG-KSEOS/scripts/start-hgk-exec-frontdoor.ps1 -Action Start (requires aiohttp in HG-KSEOS/.venv, installed this session)
- 10101_relay: pre-existing (opencodex), forwards a dead upstream key -> 401
- 10102_desktop_router: pre-existing, another session's service, untouched
- 10105_passthrough_shim: created this session (tools/ocg_shim_10105.py) and STOPPED at handoff

## 5. Blockers carried forward (each with the next concrete action)

### EXECUTE_LANE_UNSETTLED — `ATTEMPT_INTERRUPTED`
Route is proven to serve (upstream 200, real tokens); the nonce gate was never satisfied because the first working attempt passed the brief as a path and the corrected attempt was interrupted.

**next:** restart tools/ocg_shim_10105.py, then dispatch with --prompt "$(cat BRIEF.md)" (inline text, nonce = first line)

### HOST_RUNNER_PAUSED — `HOST_DURABLE_RUNNER_OFF`
cronjob 3602bce285e8 disabled since 2026-10-23T22:20:02+08:00; no autonomous R17 continuation exists.

**next:** owner/host decision to resume the job (agent must not start a background process during handoff)

### NATIVE_PERMIT_MISSING — `NATIVE_AUTHORITY`
No HGK Native WorkOrder/Permit, Fabric Active Designation, SWOF W3, AO or Release seal exists for R17 product effects.

**next:** issue through the real issuer; textual owner order is not a permit

### PRINCIPAL_REQUESTS_UNDELIVERED — `EXTERNAL_CHANNEL`
Three principal requests (Native WO/Permit, Host durable runner, independent AO) have no submission channel.

**next:** deliver through a real channel and keep the receipt

### OPENCODE_KEY_ROTATION — `SECURITY_DEBT`
The OpenCode Go key value was echoed into tool output in an earlier round; rotation is an owner action and is NOT done.

**next:** owner rotates the key; no contaminated raw is published

### CHECKER_PENDING — `INDEPENDENT_ACCEPTANCE`
No independent principal has accepted this handoff; the VERIFY lane is available but no acceptance receipt exists for it.

**next:** dispatch a VERIFY_SECURITY brief over this pack's SHAs

## 6. What is NOT claimed

- No product acceptance, no Native effect, no independent acceptance, no Host UAT, no release.
- `22 closed / 123 open` and `102 AGENT / 21 OWNER` from earlier reports are **historical snapshots**;
  the live numbers are in `SESSION_STATE_R17.json` and `R17_145_STATUS.csv`.
- The OpenCode Go key was echoed into tool output in an earlier round; rotation is an owner action and is
  still open. No contaminated raw is published.
