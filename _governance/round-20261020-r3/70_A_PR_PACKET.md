# 70 — Track A packet: M4-LITE for `bedc119`

## Subject

| Field | Value |
|---|---|
| repo | `github.com/shw097-team/SBL` |
| candidate | `candidate/r2-20261020-v13` @ `bedc11957d4fc2474b249b69d200829272c118ef` |
| tree | `fa7c12923589201fb2286c131e6511432de600a9` |
| base (`main`) | `ca6830d9fc9d89b7b87e818670dd67b393472d79` — **unmoved** |
| evidence | `evidence/r2-20261020-c3` @ `6cb9d03f…`, then this round's evidence branch |
| hosted CI | run `39426671565`, ubuntu job `118640874662` + windows job `118640874677`, both success, `145 passed, 1 skipped` each |

## What this round produced

A procedural harness, `M4LITE/run_m4lite.py`, that any reviewer can run against a checkout of the
frozen candidate. It executes 24 cases: 6 properties × (repo tests + an independent probe that calls the
public API directly, so a tautological test cannot carry the review alone).

Run it:

```
git clone https://github.com/shw097-team/SBL && cd SBL
git checkout bedc11957d4fc2474b249b69d200829272c118ef
python <evidence-branch>/_governance/round-20261020-r3/M4LITE/run_m4lite.py \
    --subject-root . --out-dir /tmp/m4lite --reviewer "<your name>"
```

Observed this round (maker-side execution, **not** a signature):

| Case group | Cases | Result |
|---|---|---|
| AC-M4-01 GKNOW-ID | POS + NEG | 2/2 pass |
| AC-M4-02 GKNOW-SEP | NEG (5 variants) + POS | 2/2 pass |
| AC-M4-03 GKNOW-BIND | POS + NEG | 2/2 pass |
| AC-M4-04 MODE-ACK | POS + 2 NEG + shadow | 4/4 pass |
| AC-M4-05 MODE-SIG | NEG + POS | 2/2 pass |
| AC-M4-06 BRIDGE-SETTLE | 2 NEG + POS | 3/3 pass |
| repo tests (separate processes) | 12 | 12/12 pass |
| **total** | **24** | **24 pass, 0 fail** |
| subject mutation | — | **CLEAN** (912 files / same digest before and after) |

Raw receipts: `M4LITE/receipts/M4LITE_RAW.json` (per-case command, exit, expected/observed, own
sha256), `M4LITE/receipts/M4LITE_TRANSCRIPT.md` (human-readable table).

## What is still missing, and why only a human can supply it

The runner's own verdict is `HOLD_PENDING_HUMAN_SIGNATURE`, by construction — there is no `--sign` flag.
The missing artefact is a `HUMAN_PROCEDURAL_ACCEPTANCE` receipt:

```json
{
  "schema": "SBL-HUMAN-PROCEDURAL-ACCEPTANCE/1",
  "reviewer_identity": "<name or handle>",
  "reviewer_independence": "not the maker | owner-reviewing-own-product",
  "subject_sha": "bedc11957d4fc2474b249b69d200829272c118ef",
  "date_utc": "<iso8601>",
  "checks_run": ["python <...>/run_m4lite.py --subject-root . --out-dir /tmp/m4lite", "<any variant you tried>"],
  "properties": {"GKNOW-ID": "pass", "GKNOW-SEP": "pass", "GKNOW-BIND": "pass",
                 "MODE-ACK": "pass", "MODE-SIG": "pass", "BRIDGE-SETTLE": "pass"},
  "findings": [],
  "verdict": "PASS",
  "label": "HUMAN_PROCEDURAL_ACCEPTANCE",
  "limits": "what this review did not cover",
  "carrier_note": "the mandated openai-codex carrier refuses this code (websocket 426 / content filter); this review substitutes for that receipt"
}
```

Owner self-review is allowed under FAR option 5 and must say `owner-reviewing-own-product`. It may not be
labelled `INDEPENDENT_CASE_PASS`, and the maker may not fill it in.

## Merge sequence after the signature

1. Open a PR from `candidate/r2-20261020-v13` to `main` (base `ca6830d`, head `bedc119`), attach this
   packet and the signed receipt.
2. Owner reviews the PR and presses merge — fast-forward or a non-force merge; no force push, no
   autonomous merge.
3. Read back `main` and record `MERGED` **only** if it equals `bedc11957d4fc2474b249b69d200829272c118ef`
   (or the exact resulting merge commit).

Until step 3 lands, the claim stays `MERGE_READY_HUMAN_REVIEWED` at best, and today it is `M4_LITE_HOLD`.

## Explicit non-claims

- Not `INDEPENDENT_CASE_PASS`; the mandated checker never completed a verdict on this code.
- Not `MERGED`; `main` has not moved.
- Not `FULL_SBL_ACCEPTED`; the audit's F13-03/04/07 items are C track.
- The 24 passing cases do not raise any claim ceiling; they only show the six properties held under a
  procedure that a human can now repeat and sign.
