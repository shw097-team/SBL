# NARROW REPAIR (R2-R1) — close the independent checker's findings on candidate ab17440

Checker: `openai-codex/gpt-6.1-sol` (VERIFY_SECURITY lane, rank 2, `required_arm == served_arm`, 494.79 s).
Verdict: **FAIL** — 4 HIGH, 3 MEDIUM, 1 INFO. Raw: `VERIFY_candidate_ab17440.json` + parsed verdict
`VERDICT_parsed.json` + the checker's own adversarial evidence (see the receipt's attempt log).

Repair rule: fix the CAUSE, never relax a check and never weaken an assertion. Each item below names the exact
file and the required post-condition. Keep every currently-passing behaviour (the checker accepted them).

## SEC-01 (HIGH) — a maker can impersonate the checker by naming it
`sbl_sp/sp.py` `sign_verdict(principal_id, maker_principal, verdict)` trusts caller-supplied names.
REQUIRED: the signature must require a secret the named principal actually holds.
- Add `sbl_sp/keys.json`: `{"schema":"SBL-SP-KEYS/1","keys":{"tpm_sp":"<32 hex>","commander_sp":"<32 hex>","external_challenge_sp":"<32 hex>"}}`
  (deterministic placeholder values are fine; this is a local demo keyring, say so in a docstring).
- `sign_verdict(principal_id, maker_principal, verdict, credential: str | None = None)`:
  - `assert_permission(principal_id, "challenge.sign")` first, then self-identity refusal (unchanged),
  - then `credential` must HMAC-match the principal's key: compute
    `hmac.new(key, json.dumps([principal_id, verdict], sort_keys=True).encode(), sha256).hexdigest()` and require
    `credential == that digest`; missing/incorrect → `SBLError("SBL_E_PERMISSION_DENIED")` with detail
    `{"reason": "credential_missing_or_invalid", "principal": ...}`.
  - `signature` in the output becomes this HMAC digest (drop the old `SIG-...` prefix form).
- `load_key(sp_id)` helper; never print key material; the key file is committed (documented as a demo keyring,
  NOT a secret) — the point is that a caller who does not hold the key cannot sign as that principal.
- Test updates in `tests/test_sp_isolation.py`: positive = sign with the correct credential; negatives = missing
  credential, wrong credential, and "maker names the checker principal but has no key" (all `SBL_E_PERMISSION_DENIED`).

## SEC-02 (HIGH) — the claim ceiling is caller-supplied
`sbl_core/m05_verify.py` `verdict(... claim_ceiling, claim ...)` lets the caller raise its own ceiling.
REQUIRED:
- `EvidenceVerification(ceiling: str = "LOCAL")` — the instance owns the ceiling; `RANK` table unchanged.
- `verdict(gate_id, maker, checker, status, claim, ceiling: str | None = None)`: effective ceiling =
  `self.ceiling`; an explicit `ceiling` argument above `self.ceiling` → `SBLError("SBL_E_CLAIM_CEILING_EXCEEDED")`
  (detail names both), i.e. a caller cannot raise it, only lower it.
- `claim` above the effective ceiling → `SBL_E_CLAIM_CEILING_EXCEEDED` (unchanged behaviour for the same case).
- `ShardedCore`/`core.py` constructs it with `ceiling="LOCAL"`; add a module constant `BUILD_CEILING = "LOCAL"`.
- Test: instance bound to LOCAL, caller passes `ceiling="PRODUCTION"` → exact code; and `claim="PRODUCTION"` → exact code.

## SEC-03 (HIGH) — a PASS is not bound to evidence; proxy/case-variant bypass
`sbl_core/m05_verify.py` + `sbl_sp/sp.py`:
- `verdict(...)` must look up the recorded `EvidenceItem` for `gate_id`; absent → `SBLError("SBL_E_BAD_STATE")`
  with detail `{"reason": "no_recorded_evidence", "gate_id": ...}`; recorded `exit_code != 0` → same refusal with
  `{"reason": "evidence_exit_nonzero", "exit_code": ...}`.
- Normalise `status`: `status.strip().upper()`; the proxy set must be matched case-insensitively and with
  surrounding whitespace ignored (`FILE_EXISTS`, `file_exists`, `FILE_EXISTS ` all refused).
- Unknown status (not in a declared allowed set `{"PASS","FAIL","BLOCKED_HITL","BLOCKED_EXTERNAL"}`) → `SBLError("SBL_E_BAD_STATE")`.
- `sign_verdict` must refuse to sign a verdict whose `status` normalises into the proxy set or is unknown, with
  `SBLError("SBL_E_BAD_STATE")`.
- Tests: PASS with no evidence → refused; PASS after recording exit_code=1 → refused; `"file_exists"` and
  `"FILE_EXISTS "` → refused; signing a proxy-status verdict → refused.

## SEC-04 (HIGH) — an allowed substring suppresses the whole line in the secret scanner
`tools/secret_scan.py`: the allowlist is applied to the LINE before rules, so appending `example.com` hides a token.
REQUIRED: apply the allowlist to the MATCHED SPAN only.
- For each rule use `pattern.finditer(line)`; for each match `m`, skip only if
  any(token in m.group(0) for token in ALLOW_SUBSTRINGS) — otherwise report.
- Keep masking (`excerpt` must stay masked).
- Test (new file `tests/test_secret_scan.py`): a token-shaped fixture is BLOCKED; the same line with
  `example.com` appended is STILL BLOCKED; a genuine placeholder `password="<token>"` is CLEAN; an
  `user@example.com` line is CLEAN. Import the scanner module directly (no subprocess).

## VERIFY-01 (MEDIUM) — verification can pass with an empty inventory
`tools/verify_source.py`: a receipt with `docs: []` returned ok.
REQUIRED: require `len(docs) == 14` and the exact ids `DOC-00..DOC-13` present (set equality); otherwise
`ok=false`, exit 1, `mismatches` naming `missing_docs` / `unexpected_docs`.
Test in `tests/test_verify_source.py`: build a temporary receipt with `docs: []` (write it under the test scratch
root), point the tool at it via `--record PATH` (add that option, default `evidence/source/SOURCE_VERIFY.json`)
and assert exit 1 + `ok=false`; then the real receipt passes when the mirror exists.

## VERIFY-02 (MEDIUM) — the gate denominator undercounts mixed outcomes
`tools/run_gates.py`: the summary regex is anchored at line start, so `"1 failed, 31 passed"` records only 1.
REQUIRED: parse every `<n> <word>` pair on the pytest summary line (`passed|failed|error|errors|skipped`),
denominator = passed + failed + error(s) (skipped excluded but reported), and record `failed` separately in the
row. A pytest gate whose parsed denominator is 0 must be marked failed by the runner (keep that rule).
Self-check: run the runner and confirm `G-SUITE-FULL` denominator equals the suite's real total.

## VERIFY-03 (MEDIUM) — tests are not 3.11-compatible
`tests/e2e/test_gj02_patch.py`, `tests/e2e/test_rollback.py`: `shutil.rmtree(..., onexc=...)` is 3.12+.
REQUIRED: use `shutil.rmtree(path, ignore_errors=True)` (or a `try/except` around it). Then the suite must pass
under BOTH interpreters:
- `C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe` (3.12)
- `python` on PATH (3.11.x)
Find any other 3.12-only API with `python -c "import ast,sys"`-style review or by simply running the 3.11 suite.

## Acceptance for this repair
1. `python -m pytest -p no:cacheprovider` → 0 failed, 0 errors, on 3.11 AND on 3.12.
2. `python tools/run_gates.py` → exit 0, every pytest gate denominator > 0, `G-SUITE-FULL` denominator equals the
   suite total.
3. `python tools/verify_source.py --verify` → exit 0.
4. `python tools/secret_scan.py --root .` → CLEAN.
5. Every finding above has at least one test that FAILS if the fix is removed (state which test covers which id).
No network, no git write verbs, writes only under the repo root (`.pytest_tmp` is unusable — use the test
scratch helper in `tests/conftest.py`).
