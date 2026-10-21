## STRENGTHS
Independent read-only checks confirm 46/46 source hashes, the external-report hash, compiler/contract/prompt hash bindings, and byte-identical prompt regeneration. The frozen candidate is clean at `a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2`. All 13 SP probes reproduce their recorded outcomes. Ledger counts are 50/149/38/441, with no duplicate IDs, orphan children, or fabricated PASS statuses.

## WEAKNESSES
Required TS05 evidence is absent. Ledger summaries and admission classifications contain inconsistencies. Compiler success is explicitly not runtime or independent acceptance; upstream report assertions cannot replace missing raw evidence.

## ITEMS-LIST
1. **R6CHK29-01 — BLOCKER:** Re-executed `Path('_governance/round-20261021-r6/40_TS05/TS05_READBACK.json').exists()` twice using `python -B -`; process exit `0`, result `False`. The claimed local `192/2`, CI Windows `191/3`, CI Ubuntu `189/5`, and wheel-manifest parity lack the required round readback and remain independently unverified.
2. **R6CHK29-02 — MAJOR:** Re-read `surface_c001_c038_ledger.json`; exit `0`. Cases `C-007`, `C-011`, `C-015`, `C-032`, `C-036` each have `r6_state="`NOT_ADMITTED`"`, but `status="PARTIAL_LOCAL_SCOPED"` and `raw_evidence=null`. This is contradictory scoped-progress classification, although not an explicit installed/PASS claim.
3. **R6CHK29-03 — MINOR:** Recounted `source_identity_441_ledger.json`; exit `0`. `METHOD-09.current_execution="EXECUTED_IN_R5_R6_CI"` yields one executed row, while `summary.current_executed_this_round=0`. Frozen-disposition counts independently match `1/6/3/8/423`.
4. **R6CHK29-04 — MINOR:** Recounted ledger statuses and child-to-parent links; exit `0`. Parents are `37 OPEN + 13 PARTIAL_EVIDENCE_ONLY`; children `149 OPEN`; surfaces `21 OPEN + 17 PARTIAL_LOCAL_SCOPED`. Thus “every row OPEN” is false, but child-summary `open=186` is correct; zero PASS statuses and zero orphans were found.
5. **R6CHK29-05 — MINOR, verified control:** Re-executed `python -B <compiler> lint|activation|acceptance contracts/SBL_C0_C9_CONTRACT-R6.json`; each exit `0`, `PROMPT_COMPILE_PASS`. Re-executed `compile_contract` with writes/digests redirected to memory; return `0`, rendered bytes identical. Compiler, contract and prompt hashes match `contracts/compiled-r6/compiler-receipt.json`; contract SHA-256 is `11721a0b2f0ce52ad4e3e227ce4d97a7d8372fc31049f591326518cbc0a857e1`. This is compile-only proof.
6. **R6CHK29-06 — MINOR, verified control:** Ran `python -B -c <extracted SP probe>` against the frozen candidate; exit `0`, all `13/13` cases and stdout hash match. `NEG-PROXY-STATUS-SIGN` returns `SBL_E_BAD_STATE`; `NEG-SELF-SIGN` returns `SBL_E_SELF_CHECK_FORBIDDEN`; tampered credentials return `SBL_E_PERMISSION_DENIED`. No leak appeared in these probes.
7. **R6CHK29-07 — MINOR, verification limit:** Independently SHA-256-hashed all 46 intake files and the report; exit `0`, zero mismatches, report hash `ac2db3cb5a4b377fd7fb2bc75a8148eb8ea872e136fee1370cf9be5f96842cde`. All ledger IDs occur in that report. `git --no-optional-locks -c safe.directory=C:/Projects/_sbl_r4/c3v2 -C C:/Projects/_sbl_r4/c3v2 rev-parse HEAD` exits `0` at the required SHA; status is clean. Fresh remote/CI state was not verified; read-only HGK SQLite opening failed.

## VERDICT
VERDICT: FAIL

The missing mandatory TS05 evidence blocks round verification. Retain `FAIL_FULL_CONTRACT / PARTIAL_CHALLENGE`, `0/3 HOST_ACCEPTED`, DeepSeek `NOT_ADMITTED`, and Owner-only merge authority.

Model-axis disclosure, accepted as supplied rather than re-derived: CHK29 is designated `openai-codex/gpt-6.1-sol` (OAuth); the upstream report’s different-model-axis provenance remains an additive disclosure.

R6CHK29-NC
