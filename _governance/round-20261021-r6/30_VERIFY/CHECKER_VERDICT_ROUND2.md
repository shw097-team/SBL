## STRENGTHS
Independent read-only checks confirm all 46/46 intake hashes. The evidence branch is `evidence/r6-20261021-c6` at `19bca2efc02bc74ee0ed54ed1ab1daa75ed16a88`; the frozen candidate is clean at `a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2`.

All three ledger recounts succeed: 50 parents, 149 children, 38 surfaces, and 441 source identities. No duplicate IDs within the recounted collections, source-wide duplicate IDs, or orphan children were found. The three ledger corrections are present. The required live SP permission probe refuses `external_challenge_sp` access to `product.write`.

## WEAKNESSES
The brief’s mandatory TS05 locator remains absent, although a readback exists under `20_TS05` instead. That readback’s wheel hash does not match either available wheel. The required `192 passed, 2 skipped` result could not be independently reproduced under the available interpreter and strict no-file-creation constraint. The clean-install lifecycle remains recorded evidence, not independently replayed acceptance.

## ITEMS-LIST
1. **R6CHK29R2-01 — BLOCKER: TS05 locator remains incorrect.** Executed:
   ```powershell
   python -B -c "from pathlib import Path; print(Path('_governance/round-20261021-r6/40_TS05/TS05_READBACK.json').exists())"
   ```
   Exit `0`; output:
   ```text
   False
   ```
   The committed readback actually exists at `_governance/round-20261021-r6/20_TS05/TS05_READBACK.json:1`. Therefore, evidence is not universally absent, but the exact mandatory input and round-1 correction claim remain inconsistent with disk.

2. **R6CHK29R2-02 — MAJOR: wheel evidence is not bound to an available matching artifact.** The alternate TS05 readback records SHA-256 `8bb9dfb918a37a3c1ef440bd4ebdb64ef26fe47bb6a2b4a4036c8c0e173fb293`. Executed:
   ```powershell
   python -B -c "import hashlib; from pathlib import Path; print(hashlib.sha256(Path('C:/Projects/_sbl_r4/dist/sbl_v01-0.1.0-py3-none-any.whl').read_bytes()).hexdigest())"
   ```
   Exit `0`; output:
   ```text
   e5767bf8a8ba309553f5b979f3ddb2e9f883ab9a378b0766ad444efbb26ade36
   ```
   This wheel has the recorded 39 members and all eight listed package-data paths. The sandbox wheel instead hashes to `e2ae3c123ae5b9fa7f58f122b96aa884b754f0338db1d7fad42d03d5b921ac2b`, contains 38 members, and lacks `sbl_stack/SKILL.md`. Neither validates the recorded wheel digest; this does not by itself establish differing code bytes.

3. **R6CHK29R2-03 — Verification blocked: pytest outcome not reproduced.** In `C:/Projects/_sbl_r4/c3v2`, executed `python -B -m pytest tests/ -p no:cacheprovider`; output ends `python.exe: No module named pytest`. An existing pytest-capable interpreter was then tried with an in-memory write-denying audit guard; startup failed with `FileNotFoundError: [Errno 2] No usable temporary directory found`. A guarded collection attempt reported `176 tests collected, 3 errors in 0.91s`, with temporary-directory failures in three E2E modules. These are verification-environment limitations, not evidence of candidate test regressions. Neither `192/2` nor the fresh install/uninstall lifecycle is independently established.

4. **R6CHK29R2-04 — VERIFIED: outcome and surface corrections.** Recount yields parents `37 OPEN + 13 PARTIAL_EVIDENCE_ONLY`, children `149 OPEN`, and zero PASS statuses. Surfaces are `21 OPEN + 12 PARTIAL_LOCAL_SCOPED + 5 NOT_ADMITTED_NO_DISPATCH`, covering exactly `C-001` through `C-038`. The five corrected rows are precisely `C-007/011/015/032/036`.

5. **R6CHK29R2-05 — VERIFIED: METHOD-09 delta correction.** Recount yields exactly one executed row, `METHOD-09 = EXECUTED_IN_R5_R6_CI`, matching the summary and executed-ID list. Frozen dispositions remain `ACTIVE=1`, `NATIVE_SUBSTITUTED=6`, `STANDBY=3`, `PROHIBITED=8`, `DEFERRED=423`. This verifies ledger consistency, not an independent replay of the cited CI run.

6. **R6CHK29R2-06 — VERIFIED: required SP refusal.** Called `assert_permission('external_challenge_sp', 'product.write')` against the frozen candidate using `python -B -`; exit `0` after catching the expected refusal:
   ```text
   NEG-CHALLENGE-PRODUCT-WRITE: REFUSED SBL_E_PERMISSION_DENIED: specialised principal is not permitted to perform this action
   ```
   The SP readback contains 13 matching recorded cases; only the mandated permission probe was independently replayed here. No files were modified, created, or deleted.

## VERDICT
VERDICT: FAIL

The ledger corrections are verified, but the mandatory TS05 locator remains wrong, the recorded wheel digest is uncorroborated by the available artifacts, and mandatory runtime-count verification remains incomplete.

R6CHK29R2-NC
