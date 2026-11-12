# FHS-MSC R00.1 baseline handoff

Observed: 2026-10-26T11:29:06+08:00 (Asia/Taipei). DESIGN_BASELINE_READY=PARTIAL_WITH_EXPLICIT_HOLDS.
Task: FHS-MSC-CODEX-R00.1-OWNER-DECISIONS/2026-10-26-r1.

## Design/public baseline

| Repository | current main commit | current main Tree |
|---|---|---|
| Fabric | `bcd91043b89b69c9d2f08309e46e31898ac87d89` | `83b65a65207e4c14bed9a49ea6f755eebd0ca433` |
| SBL | `dc5428f23d15f0ec56cbc3d25b22f5381fce8771` | `3f95125c5fe1d5436e1b0a112753d91f5a7e2af7` |
| PIPD-LS-SP | `e95942abcb6aa07e69304607ab8afc22a74fc67d` | `1a929d1b7c609fc0e9e70df0edb3bddaaee214c1` |
| SWOF | `acdbfaadd19d12927eb5bd542b09ed230bbc481e` | `438dce18cdae6e2bb6a9543b8f4643562655ff10` |

Fixed upstream evidence: SBL Draft PR12 commit `6d820f14ddca611e7780e08c7c0c9f233b794e06`.
This R00.1 four-document append must have that commit as its sole parent. The final new
SBL commit/Tree/blob byte verification is returned in the caller session after push;
these documents do not assert their own future commit hash. Original R00 four-file
contents and original publication manifest remain unchanged. The R00 manifest covers
its original three other artifacts only; it is not retroactively claimed to cover R00.1.

## Local candidates and active boundary

| Candidate | actual Git SHA | role |
|---|---|---|
| HGK | 086a9402189a2bb0ac3b198a7a9805b3dcbe38d8 | independent local candidate; 2 modified, 0 staged |
| Fabric | bb06b7a6c17c45c777a636e9dae3196e21eb77b9 | independent local candidate; 1 modified, 0 staged |
| SBL | 10d510f7b052e6139fd4eb536f970c0245002e17 | independent local candidate; 0 tracked modified/staged; untracked remains |
| PIPD at Owner-supplied root | 39079c02b8f2a3a3e63d3f2a2d5537805d3a3594 | remote-bound product candidate; 0 tracked modified/staged; untracked opaque entries remain |
| R00.1 isolated Oracle proposal | 6e20c2c6264b9e54992b627e6dae04a20800c02c | LOCAL_ONLY, four new candidate files, 15 maker-side targeted tests passed |

True runtime baseline: UNBOUND. Hermes source-declared version 0.21.5 is not a Loaded
version. No matched relevant PID was observed in the bounded current query. One Ready
scheduled task and existing opaque claim entries do not establish an active job/lease.
R17 current stage runner/advance byte identities match PR11 candidate
`bf3cccfe7abd94053eb147b586da4f9f95815921`; loaded identities remain UNVERIFIED.
See EFFECTIVE_HOST_MAP.tsv for REUSE/PATCH/STALE/QUARANTINE at exact subjects.

## Prepared next request, not an admitted contract

- subject_sha: `6ab0332f9eaab34ab1c59c46faaa1ad854a8390f3e9746a2029f03558e0d09fe`; local candidate commit `6e20c2c6264b9e54992b627e6dae04a20800c02c`.
- source_refs: pinned four main commits, PR12 R00 evidence, verified PIPD DOC-02/03/07 identities and pinned P4 output schema.
- exact isolated WriteSet: candidate/fhs_msc_r001/oracle_adapter.py; candidate/fhs_msc_r001/test_oracle_adapter.py; candidate/fhs_msc_r001/binding-proposal.schema.json; candidate/fhs_msc_r001/ERRATUM_RFC.md.
- effect kind: NO_LIVE_EFFECT_ISOLATED_PROPOSAL; no Canonical/installed/Host writes approved here.
- preconditions for formal migration: qualified domain source; DOC-02/DOC-07/schema Owner versioned Erratum; exact consumer/identity compatibility; independent Checker; Native admission for future effects.
- expiry: 2026-10-27T11:23:52.576155+08:00; idempotency key FHS-MSC-R001-6ab0332f9eaab34ab1c59c46faaa1ad854a8390f3e9746a2029f03558e0d09fe; no automatic effect retries.
- rollback: retain original roots; Owner may abandon the isolated candidate. No reset/clean/restore of source roots.
- checker principal: UNBOUND; Permit NOT_ISSUED; formal ECP NOT_COMPILED.
- readback predicates: exact candidate parent/WriteSet; installed schema unchanged; all affected fixtures bind the subject; current loaded/Issuer claims require independent native evidence.

## Five blocking gaps for formal work

1. ORACLE_SOURCE_AND_ERRATUM_UNRATIFIED: DOC-07 direction is recorded; actual legacy namespace and versioned schema/Writer compatibility still require true Owner contracts.
2. HOST_LOADED_ACTIVE_UNVERIFIED: current Python module imports, active job and valid lease lack decisive readback; a disk/stage hash cannot substitute.
3. NATIVE_ISSUER_ADMISSION_UNBOUND: source API presence and chat scope are not a Native Permit.
4. INDEPENDENT_CHECKER_UNBOUND: 15 local tests have no independent acceptance authority.
5. LOCAL_MAIN_DRIFT_AND_HISTORICAL_COVERAGE: bounded current-source facts are available; local product candidates differ from main and historical inventory remains incomplete. No blind merge or full historical cleanup is authorized.

## Designer consumption boundary

ROOT_FOUND; LOADED_UNVERIFIED; design/public SHA baseline BOUND, overall PARTIAL;
PRIVATE_INVENTORY_BOUNDED with historical INCOMPLETE scope; HOLD_NATIVE_GATE;
CR_ORACLE_001_OPEN. Owner can begin affected PI/PD/ECP/TQAEP design from these facts.
Formal packages, Native repair/activation, SourceFreeze, independent AO, promotion,
PR merge, release and SWOF PRE-W3 readiness remain unissued/unverified.

Only new sanitized derived findings are published. Private-store location, security
descriptors, raw inventory filenames/bytes, raw Host records, credentials, Canonical
prose and original source code are excluded. Existing denominators stay NOT_RUN.
