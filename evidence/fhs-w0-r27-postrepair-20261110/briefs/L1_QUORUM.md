# L1 — G29 signed-vote quorum repair (closes EC-R26-003 / resume predicate R26-01)

Read `_COMMON.md` first. Worktree: `C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-quorum` (branch r27/quorum-g29).
Target file (repair in place, keep the module's role): `evidence/fhs-w0-r26-repair-20261109/tools/verify_quorum.py`

## Reproduced defects (external challenge section 7.1 — verified, do not re-litigate)
The current `evaluate()/_valid_votes()` returns `ACCEPTABLE_FOR_FHS_READER_SCOPE` for:
1. `MISSING_CANDIDATE_SHA_ACCEPTED` — dict-style `votes_r25` with `{"A": true, "B": true}` and NO per-vote candidate sha.
2. `TAMPERED_RAW_HASH_NOT_CHECKED` — votes that carry a fabricated `raw_sha256` ("00"*32) that is never re-computed.
3. `INTEGER_ONE_AS_BOOLEAN_ACCEPTED` — JSON integer `1` accepted as a boolean vote (`1 == True` in Python).

## Required repair (bounded — same file, same predicate role)
1. Exact typing: `type(value) is bool`; per-vote `type(vote) is bool`. Integer 1 / string "true" -> `VOTE_TYPE_INVALID` (new code), non-zero exit.
2. A repair vote in `votes_r25` is countable ONLY when ALL of these are present and non-empty:
   `lane_id, candidate_sha256, source_sha256, clause_id, property, raw_path, raw_sha256, timestamp, session_id, process_id`.
   Missing candidate binding -> `MISSING_CANDIDATE_BINDING`.
3. Re-hash the raw transcript: if `raw_path` resolves, `sha256(bytes) == raw_sha256` else `RAW_DIGEST_MISMATCH`. If it does not resolve -> `RAW_EVIDENCE_UNREADABLE`
   (never silently accepted). Add a `--raw-root` argument so the scan can resolve relative paths; default = round root.
4. Candidate binding: every repair vote's `candidate_sha256` must equal the effective candidate; else `STALE_CANDIDATE_VOTE` — and this must apply to BOTH dict and list vote shapes (today the dict shape skips it entirely).
5. Deduplicate on `lane_id` AND on `(session_id, process_id)`; same lane twice -> `LANE_ID_DUPLICATE`, same process twice -> `PROCESS_ID_DUPLICATE` (new code).
6. Keep the two real r25 repair votes in the signed receipts valid: your repaired verifier MUST still return `ACCEPTABLE_FOR_FHS_READER_SCOPE` for the two repaired properties (WP-FHS-00 L1:817, WP-FHS-01 L1:812). DO NOT edit the signed receipts to make this true. If the real votes lack a field your new rule requires, measure it, record it as finding `R26-01_GAP`, and decide explicitly between (a) hard requirement or (b) `--strict`-only requirement. State which you chose and why, with the measured data.

## Mandatory negative fixtures (all added to `CASES`, all FIRED by `--selftest`)
- `NEG-Q8` missing candidate binding -> `MISSING_CANDIDATE_BINDING`
- `NEG-Q9` fabricated raw digest, real file differs -> `RAW_DIGEST_MISMATCH`
- `NEG-Q10` integer `1` vote -> `VOTE_TYPE_INVALID`
- `NEG-Q11` two votes sharing the same process id -> `PROCESS_ID_DUPLICATE`
- keep NEG-Q1/Q2/Q4/Q5/Q7/Q1b and POS-Q3 green.
`--selftest` must print every case with expected/observed and exit 0 only if all match.

## Acceptance
- `verify_quorum.py --selftest` -> exit 0, all cases match (capture log).
- `verify_quorum.py` (receipt scan over the round) -> capture exit + JSON; report properties_checked and every finding verbatim.
- Wire the selftest into the SBL CI workflow that already runs the r26 gate (find it under `.github/workflows/`); add a step, weaken nothing.
- Do not change QUORUM_MIN and do not change the schema of already-signed files.
