# EXECUTE brief — W08 three-lane consistency checker (write exactly two files)

Write ONLY these two files. No other path may be touched.

## 1. `tools/check_lane_consistency.py`

Offline. Reads lane dispatch receipts and the lane declaration, and answers one question: does each receipt show the
arm the declaration says that lane should be served by? Exit 0 only when every checked receipt is consistent;
exit 1 on any violation; exit 2 on a usage/IO error. Print one JSON object.

Inputs
- receipts: `<repo>/_governance/round-20261022-r15_2/receipts/dispatch/*.json`
- declaration: `C:/Projects/Agent_Workspace/HG-KSEOS/config/hermes-codex-lane.json` (read-only; do not modify)

Each receipt has: `lane` (PLAN | EXECUTE | VERIFY_SECURITY), `attempts` (list), and per attempt:
`rank`, `provider`, `model`, `transport_model`, `usage_model`, `usage_provider`, `usage_status`, `nonce_present`,
`exit`, `timed_out`. Also possibly `skipped_arms` (list of {rank, model, reason}).

Rules, each reported as its own predicate with the receipt path and the offending attempt rank:
- `R1_lane_declared`: the receipt's lane appears in the declaration.
- `R2_rank_valid`: the attempt's rank is one of the declared ranks for that lane.
- `R3_model_matches_arm`: the attempt's `model` equals the declared model for that lane at that rank AND the
  `usage_model` equals the `transport_model` (a served arm that differs from the declared arm is a violation, not
  a warning).
- `R4_provider_matches`: `provider` and `usage_provider` are consistent with the declared provider for the arm
  (accept the documented aliases: `openai-codex`/`openai-p*` for the GPT arm, `opencode-go` for the DeepSeek arm).
- `R5_no_silent_skip`: if `skipped_arms` is non-empty, the receipt must record a reason for each skipped arm; an
  unexplained skip is a violation.
- `R6_nonce_evidence`: `nonce_present` true with `exit` 0; a receipt with a missing nonce is reported as
  `NOT_GREEN` (not a consistency violation, but it must not count as green either).

Output shape:
`{"schema":"SBL-LANE-CONSISTENCY/1","declaration_sha256":"...","receipts_checked":N,
  "results":[{"receipt":"...","lane":"...","predicates":[{"id":"R2_rank_valid","ok":false,"rank":3,"note":"..."}],
              "verdict":"CONSISTENT|VIOLATION|NOT_GREEN"}],
  "counts":{"CONSISTENT":n,"VIOLATION":n,"NOT_GREEN":n},"exit_reason":"..."}`

Do not invent receipts, and do not treat a missing declaration as consistent: missing or unparsable declaration is
exit 2 with `DECLARATION_UNREADABLE`.

## 2. `tests/test_lane_consistency.py`

Pytest, no network, no writes outside tmp_path. Build synthetic receipts in `tmp_path` and assert, at minimum:
1. a receipt whose served model equals the declared arm -> CONSISTENT, exit 0;
2. a receipt whose `usage_model` differs from `transport_model` -> VIOLATION naming R3;
3. a receipt with an undeclared rank -> VIOLATION naming R2;
4. a `skipped_arms` entry with no reason -> VIOLATION naming R5;
5. a receipt with `nonce_present` false -> NOT_GREEN, and the overall exit code is nonzero;
6. a missing declaration file -> exit 2 / DECLARATION_UNREADABLE, never CONSISTENT.

The checker must import cleanly and take the receipts dir + declaration path as arguments/flags so the tests can
point at tmp data (default them to the real paths).

## Fences

- Do not modify any receipt, queue, denominator or governance record.
- Do not weaken a predicate to make a real receipt pass: if the current receipts genuinely violate R3, that is the
  finding and the tool must say so.
- No network. No `pip install`. Stdlib + pytest only; PyYAML is available if needed.
