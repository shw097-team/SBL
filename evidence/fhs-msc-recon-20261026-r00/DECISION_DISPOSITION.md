# FHS-MSC R00.1 decision disposition

Task: FHS-MSC-CODEX-R00.1-OWNER-DECISIONS/2026-10-26-r1  
Observed: 2026-10-26T11:29:06+08:00, Asia/Taipei.  
Claim ceiling: DESIGN_BASELINE_EVIDENCE_CANDIDATE.  
DESIGN_BASELINE_READY=PARTIAL_WITH_EXPLICIT_HOLDS.

This is an append-only continuation of PR12's evidence commit
`6d820f14ddca611e7780e08c7c0c9f233b794e06`. The original four R00 artifacts are unchanged.
The present four derived documents supersede affected observations only; they do not
retroactively change the original observation or its publication manifest.

## DEC-01

- OWNER_DIRECTION: inspect the newly supplied PIPD root; DOC-07 owns oracle/fixture semantics; retain the existing DOC-03 legacy ABI until actual schema compatibility and Writer ratification.
- ACTUAL_READBACK: PIPD_ROOT is a true Git worktree at the Owner's newly supplied location, HEAD `39079c02b8f2a3a3e63d3f2a2d5537805d3a3594`, branch `rescue/r5p-uncommitted-20261016`, origin `https://github.com/shw097-team/PIPD-LS-SP.git`, 947 tracked, modified=0, staged=0, no upstream. Its 237 untracked **directory-mode entries** include opaque directories; this is not an all-file count. The repository relationship is proved by Git metadata, not by the directory name. PIPD-LS-SP product worktree is FOUND at PIPD_ROOT. The external Canonical DOC-00..09 family has exactly one physical file per ID; only DOC-02/03/07 were substantively read and hashed for this correction. Physical source identity is not SourceFreeze or Writer ratification.
- RESOLVED_OR_HOLD: ROOT_FOUND; the prior PIPD_ROOT_MISSING is resolved for the correct user-supplied root. OWNER_DIRECTION_RECORDED; CR_ORACLE_001_OPEN / HOLD_AFFECTED_ONLY for formal PI/TQAEP and promotion.
- FIRSTFAIL: LEGACY_DOMAIN_SOURCE_NAMESPACE_UNRATIFIED and SCHEMA_OWNER_ERRATUM_NOT_ISSUED. The installed literal has no qualified source namespace. Actual PIPD DOC-03 is the PD/TQAEP construction source; it is not automatically a DOMAIN_ORACLES registry. A SBL DOC-03 passage describes the conflict without ratifying a legacy source binding.
- NEXT_LEGAL_STEP: DOC-02/DOC-07/schema Owners ratify the fully qualified domain-source ref and versioned compatibility Erratum; then independently verify affected producer/schema/consumer/identity/fixture migration. No direct const-only repair was made.

## DEC-02

- OWNER_DIRECTION: inspect current Host identities non-invasively; never execute the recovery-capable CLI to obtain a version.
- ACTUAL_READBACK: Get-Command still resolves the authorized Hermes Recovery executable, 114995 bytes, file-version metadata empty, on-disk SHA256 `c02538dd297474191546684681344c0ad859580a635047e577947b8bebd559e8`. Discovered source checkout HEAD remains `f97608f178d1ffeca59860195ab7da295f7c8e5f`; source-declared version is 0.21.5. The old HGK v0.20.0 declaration remains a recorded drift. At 2026-10-26T11:19:35+08:00, a bounded CIM query over Hermes/Python executable names plus relevant entrypoint tokens found no matching PID; therefore no corresponding executable/module map was obtained. Relevant services observed=0; relevant scheduled tasks observed=1, state Ready, action executable basename wscript.exe. Scheduler Ready is not an active job. Non-secret stage indices show no current lease record at the inspected entry, a fence counter present, and 18 opaque claim entries; claim contents and raw queue/DB were not read.
- RESOLVED_OR_HOLD: NOT_RUNNING_OBSERVED_IN_BOUNDED_QUERY; LOADED_UNVERIFIED; active job/lease validity and HGK Issuer identity UNBOUND. Absence in this query does not prove the whole system is stopped.
- FIRSTFAIL: NO_CURRENT_PROCESS_MODULE_OR_NATIVE_ISSUER_RECEIPT. Stage bytes and historical PR11 claims are not Loaded SHA.
- NEXT_LEGAL_STEP: a permitted native current process/module/Issuer receipt from the actual Host. No service, scheduler, runner, recovery or queue resume was executed.

## DEC-03

- OWNER_DIRECTION: separate public design, local product candidate and actual active layers; preserve tested R17 repair candidates.
- ACTUAL_READBACK: four main refs and PR12's fixed evidence parent were re-read and unchanged. HGK/Fabric/SBL local HEAD and modified/staged counts remain as R00; PIPD_ROOT is now separately bound. EFFECTIVE_HOST_MAP.tsv records bounded candidate/main/stage/loaded comparisons. R17 runner and advance stage Git blob identities still equal PR11's pinned candidate blobs; REUSE preserves them without activating them. PIPD installed/local/main P4 output schema matches, while local pipeline, S0 PI/TQAEP schemas and validator differ from main. The local S0 PI trace schema lacks the newer main trace-item constraints. Fabric policy consumer also differs. No merge/reset/rebase/cherry-pick/pull was performed on the source branches.
- RESOLVED_OR_HOLD: design/public baseline identities BOUND; overall PARTIAL because Active Runtime remains UNBOUND and candidate migration semantics remain pending.
- FIRSTFAIL: LOCAL_CANDIDATE_IS_NOT_ACTIVE_BASELINE.
- NEXT_LEGAL_STEP: consume pinned main plus PR12 as design evidence; review only the bounded PATCH/STALE rows before any separately admitted product repair. SBL 46 ahead/26 behind is not an authorization to push/pull those commits.

## DEC-04

- OWNER_DIRECTION: create and validate the designated local private Evidence Store; cover necessary Bootstrap/current-source facts without a historical all-file crawl.
- ACTUAL_READBACK: PRIVATE_STORE_VALIDATED. User binding, path containment and storage safety checks passed before any data write. Public artifacts reveal neither the private store path nor its inventory filenames or security descriptors. Bounded non-secret metadata entries: HGK 92, Fabric 1, SBL 18, PIPD 39 (150 total), maximum relative depth 2, cap 300 per root. No reparse traversal or errors occurred within this selected scope. Only explicitly safe source/schema digests, sanitized Host fields, candidate test receipts and proposal contracts were retained.
- RESOLVED_OR_HOLD: PRIVATE_INVENTORY_BOUNDED. Historical whole-root inventory remains INCOMPLETE by scope; R00's 17 reparse directories, 983 traversal errors and 60/65 long-path warning observations are retained, not declared fixed.
- FIRSTFAIL: OUT_OF_SCOPE_HISTORICAL_DENOMINATOR_NOT_RESCANNED.
- NEXT_LEGAL_STEP: use the bounded facts for design. Expand only for a separately necessary affected source or Native repair; no demand for a clean 55k untracked/180k ignored history.

## DEC-05

- OWNER_DIRECTION: permit isolated adapter/Erratum preparation and candidate contracts, with no self-issued Native authority.
- ACTUAL_READBACK: isolated PIPD candidate branch `candidate/fhs-msc-r001-oracle-adapter`, commit `6e20c2c6264b9e54992b627e6dae04a20800c02c`, parent `e95942abcb6aa07e69304607ab8afc22a74fc67d`. It adds only four new proposal/test files under candidate/fhs_msc_r001. It was not pushed to PIPD. Subject bundle SHA256 `6ab0332f9eaab34ab1c59c46faaa1ad854a8390f3e9746a2029f03558e0d09fe`. Actual targeted tests: 15, exit=0; maker-side only. The adapter preserves the legacy PI object/identity, checks schema/source/subject pins, rejects lost/orphan/colliding atom bindings, and emits a separate candidate object constrained to NONE effects and CR_OPEN. No PI/TQAEP or Native Permit is minted. Bounded NEXT_WORK_REQUEST and ECP Candidate were prepared with exact subject, WriteSet, expiry, idempotency, rollback and readback predicates.
- RESOLVED_OR_HOLD: candidate preparation completed; HOLD_NATIVE_GATE; independent Checker UNBOUND; formal ECP NOT_COMPILED; CR_ORACLE_001_OPEN.
- FIRSTFAIL: ISSUER_ADMISSION_AND_INDEPENDENT_CHECKER_UNBOUND.
- NEXT_LEGAL_STEP: submit the candidate request to the actual Native Issuer only after the named source/schema compatibility prerequisites; a different independently authorized principal must supply acceptance evidence.

## Denominators and publication scope

R15.1 949 atoms, R17 145-ID obligations, 42 findings and all Golden Journeys remain
NOT_RUN/NOT_REQUALIFIED in this round. The 15 tests cover only this isolated adapter.
Only the four new non-sensitive derived reports are eligible for this SBL append.
No Canonical source text, original Host logs, private inventory entries, raw runtime
state or credential values are copied. Publication does not establish Native acceptance,
SourceFreeze, independent AO, SWOF PRE-W3 readiness, promotion or release.
