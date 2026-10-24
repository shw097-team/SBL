# R17 session handoff — `EVIDENCE_BOUND` (candidate evidence, not product acceptance)

Companion to #9. **R17 Mission stays OPEN.** Nothing here is a Native WorkOrder/Permit, a Fabric Active
Designation, a SWOF W3, an independent AO acceptance or a Release seal.

## What this branch contains

`evidence/r17-session-handoff-20261024/` — a sanitised, hash-manifested mirror of the local handoff pack:

| file | role |
|---|---|
| `SESSION_HANDOFF_SUMMARY.md` | one page: state, lanes, blockers, next action |
| `SESSION_HANDOFF_R17.md` | the handoff itself (repos, lanes, services, blockers) |
| `SESSION_STATE_R17.json` | machine truth: `handoff_id`, queue counts, conservation, lanes, cron, repos |
| `R17_145_STATUS.csv` | per-ID state / owner / next legal action (145 denominator) |
| `REC01_09_CROSSWALK.md` | nine rounds: phenomenon → root cause → repair → receipt → open |
| `OPEN_TT_FAR_OWNER_DECISIONS.md` | what needs an owner, a native principal or rotation |
| `NEW_SESSION_BOOTSTRAP.md` | resume without reading the old chat |
| `REPO_STATE.json`, `SECRET_SCAN_REPORT.json` | repo readback, secret/PII scan (detector self-tested) |
| `SOURCE_MANIFEST.sha256`, `REPO_MANIFEST.sha256` | content hashes (16 files) |
| `receipts/` | 7 hashed receipts (lane admission, runner repair, orphan reconcile, C-family probes, …) |

## Verified at publish time

- 145-ID denominator intact: 145 unique IDs + `FABRIC-CANARY` as the single non-denominator row.
- Lane admission measured: PLAN `openai-codex/gpt-6.1-sol` rank 2 (OAuth) ok/nonce; VERIFY_SECURITY same arm
  ok/nonce; **EXECUTE unsettled** — the route serves (upstream `/v1/responses` 200; one real turn billed
  57,294 in / 1,210 out) but the nonce gate was never satisfied, and the corrected attempt was interrupted by
  the handoff order. That is recorded as an open blocker, not as a pass.
- Secret/PII scan: 0 hits, with an injected canary proving the detector fires.
- Local negative controls a/b/c/e/g/h/i pass; d/f are closed by the remote readback below.

## Explicitly not claimed

- No product acceptance, no native effect, no independent acceptance, no Host UAT, no release.
- No merge request: this stays a **Draft** PR; CI passing would not upgrade it either.
- The R17 durable runner is **paused** (cron `3602bce285e8`, since 2026-10-23T22:20:02+08:00), so autonomous
  continuation does not exist until an owner resumes it. This handoff deliberately starts no background process.
- The OpenCode Go key echoed into tool output in an earlier round still requires owner rotation; no
  contaminated raw is published here.

## Next legal action for a successor session

1. `C18-MANIFEST` — bind the TQAEP 96-cell denominator from DOC-08 (currently typed `PROBE_UNBOUND`).
2. `DEST-FIXTURES` — build DEST-01..16 in isolated copies.
3. `W01-CONF` — produce a real conformance receipt, then re-probe.
4. `EXECUTE` settle — restart `tools/ocg_shim_10105.py`, then dispatch with `--prompt "$(cat BRIEF.md)"`
   (inline text; the nonce must be the brief's first line).

See `NEW_SESSION_BOOTSTRAP.md` for the mechanical resume checks.
