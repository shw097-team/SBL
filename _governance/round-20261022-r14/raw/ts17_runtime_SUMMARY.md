# R14-TS17 runtime follow-up

- Total rows: 96; RUNTIME_QUALIFIED: 30; DECLARED_ONLY: 66; NO_ORACLE: 0.
- Existing-case rows exercised: 32/32; case rows retained DECLARED_ONLY after unsuccessful schema enforcement: 2.
- Host: `DESKTOP-57EO414`; commit: `d09dda04c2b2ca1607da1a910a70e29c9b6cec59`; checked UTC: 2026-10-22T03:07:37.485547+00:00.
- Qualification means the named schema oracle was executed once on this host at this commit with captured exit/output; it is not a guarantee of future behaviour.
- Schema qualification ONLY: both input and output schemas meta-checked; existing POS-001 valid instances accepted; required-field-deletion invalid instances rejected; every listed fixture for THIS row evaluated. REFUSE must cause schema rejection. No fabricated output/receipt or analogous test credited.
- This does NOT establish live skill invocation, compiler-generated output, source hash truth, semantic authorization, no-state-diff, Host effective load, independent acceptance, release, or DOC-08 native qualification.

## Matrix/spec mismatch (preserved, not silently repaired)

- DOC-08 C39.1 lines 360-384 and C39.2 define TestClass x eight OracleTypes (DETERMINISTIC, STATE_READBACK, PROPERTY, REFERENCE_OUTPUT, STATISTICAL, SEMANTIC_JUDGE, HUMAN, COMPOSITE). The supplied CSV is instead TestClass x eight official_skill values and contains no OracleType column. Its 96 rows are NOT the DOC-08 96 OracleType cells. Appended states apply only to the supplied skill rows and their schema oracles. No OracleType mapping was invented.
- All original CSV field values are preserved, including historical runtime_covered=False and execution_scope. New state/qualification_scope describe this follow-up; original fields are historical, not rewritten.
- NO_ORACLE=0 deliberately: missing runnable cases remain DECLARED_ONLY as requested, with individual reasons rather than being silently reclassified.

## Artifact discovery and execution

- Each exercised row records exact schema/case file paths, exact command, exit, timestamp, <=200-character real output tail. Full stdout/stderr is in ts17_runtime_executions.jsonl; reproducible harness is ts17_runtime_probe.py.
- HG-KSEOS tests/scripts searched for exact skill/case/semantic identifiers. Relevant hits and source digests are in ts17_runtime_environment.json. scripts/pipd_skills_conformance.py is schema/frontmatter measurement, not a functional consumer; its main writes ts13_* and was intentionally NOT invoked. Its schema logic was independently exercised by the packet-only harness.
- The semantic.distinct and semantic.claim_gate fixtures are not enforced by their schemas; no matching row-specific executable semantic oracle was found in HG-KSEOS/tests or scripts. Their accepted negative inputs are preserved as real failures, not credited.
- Source matrix, DOC-08, skill schema and fixture hashes unchanged; git HEAD and porcelain status unchanged (clean before/after). All writes confined to raw/ts17_*.

## All rows not qualified (unexecuted or execution did not establish the oracle)

| Data row | TestClass | Skill | Execution | Reason |
| --- | --- | --- | --- | --- |
| 15 | NEG | pipd-assurance-tqaep | exit=1 | DECLARED_ONLY: NEG-001: expected REFUSE, schema accepted; semantic.distinct |
| 16 | NEG | pipd-package-project | exit=1 | DECLARED_ONLY: NEG-001: expected REFUSE, schema accepted; semantic.claim_gate |
| 33 | PERF | pipd-route-intake | NOT_RUN | No row case, pinned workload, SLI/SLO threshold, or benchmark execution bound. No substitute-by-analogy used. |
| 34 | PERF | pipd-authority-source | NOT_RUN | No row case, pinned workload, SLI/SLO threshold, or benchmark execution bound. No substitute-by-analogy used. |
| 35 | PERF | pipd-profile-tailor | NOT_RUN | No row case, pinned workload, SLI/SLO threshold, or benchmark execution bound. No substitute-by-analogy used. |
| 36 | PERF | pipd-pi-compile | NOT_RUN | No row case, pinned workload, SLI/SLO threshold, or benchmark execution bound. No substitute-by-analogy used. |
| 37 | PERF | pipd-pd-bind | NOT_RUN | No row case, pinned workload, SLI/SLO threshold, or benchmark execution bound. No substitute-by-analogy used. |
| 38 | PERF | pipd-execution-contract | NOT_RUN | No row case, pinned workload, SLI/SLO threshold, or benchmark execution bound. No substitute-by-analogy used. |
| 39 | PERF | pipd-assurance-tqaep | NOT_RUN | No row case, pinned workload, SLI/SLO threshold, or benchmark execution bound. No substitute-by-analogy used. |
| 40 | PERF | pipd-package-project | NOT_RUN | No row case, pinned workload, SLI/SLO threshold, or benchmark execution bound. No substitute-by-analogy used. |
| 41 | PARITY | pipd-route-intake | NOT_RUN | No row case or bound provider-off profile/fallback and egress measurement. No substitute-by-analogy used. |
| 42 | PARITY | pipd-authority-source | NOT_RUN | No row case or bound provider-off profile/fallback and egress measurement. No substitute-by-analogy used. |
| 43 | PARITY | pipd-profile-tailor | NOT_RUN | No row case or bound provider-off profile/fallback and egress measurement. No substitute-by-analogy used. |
| 44 | PARITY | pipd-pi-compile | NOT_RUN | No row case or bound provider-off profile/fallback and egress measurement. No substitute-by-analogy used. |
| 45 | PARITY | pipd-pd-bind | NOT_RUN | No row case or bound provider-off profile/fallback and egress measurement. No substitute-by-analogy used. |
| 46 | PARITY | pipd-execution-contract | NOT_RUN | No row case or bound provider-off profile/fallback and egress measurement. No substitute-by-analogy used. |
| 47 | PARITY | pipd-assurance-tqaep | NOT_RUN | No row case or bound provider-off profile/fallback and egress measurement. No substitute-by-analogy used. |
| 48 | PARITY | pipd-package-project | NOT_RUN | No row case or bound provider-off profile/fallback and egress measurement. No substitute-by-analogy used. |
| 49 | RECOVERY | pipd-route-intake | NOT_RUN | No row case or bound failure injection, rollback target and state digest readback. No substitute-by-analogy used. |
| 50 | RECOVERY | pipd-authority-source | NOT_RUN | No row case or bound failure injection, rollback target and state digest readback. No substitute-by-analogy used. |
| 51 | RECOVERY | pipd-profile-tailor | NOT_RUN | No row case or bound failure injection, rollback target and state digest readback. No substitute-by-analogy used. |
| 52 | RECOVERY | pipd-pi-compile | NOT_RUN | No row case or bound failure injection, rollback target and state digest readback. No substitute-by-analogy used. |
| 53 | RECOVERY | pipd-pd-bind | NOT_RUN | No row case or bound failure injection, rollback target and state digest readback. No substitute-by-analogy used. |
| 54 | RECOVERY | pipd-execution-contract | NOT_RUN | No row case or bound failure injection, rollback target and state digest readback. No substitute-by-analogy used. |
| 55 | RECOVERY | pipd-assurance-tqaep | NOT_RUN | No row case or bound failure injection, rollback target and state digest readback. No substitute-by-analogy used. |
| 56 | RECOVERY | pipd-package-project | NOT_RUN | No row case or bound failure injection, rollback target and state digest readback. No substitute-by-analogy used. |
| 57 | UPGRADE | pipd-route-intake | NOT_RUN | No row case or bound from/to version migration with invariant oracle. No substitute-by-analogy used. |
| 58 | UPGRADE | pipd-authority-source | NOT_RUN | No row case or bound from/to version migration with invariant oracle. No substitute-by-analogy used. |
| 59 | UPGRADE | pipd-profile-tailor | NOT_RUN | No row case or bound from/to version migration with invariant oracle. No substitute-by-analogy used. |
| 60 | UPGRADE | pipd-pi-compile | NOT_RUN | No row case or bound from/to version migration with invariant oracle. No substitute-by-analogy used. |
| 61 | UPGRADE | pipd-pd-bind | NOT_RUN | No row case or bound from/to version migration with invariant oracle. No substitute-by-analogy used. |
| 62 | UPGRADE | pipd-execution-contract | NOT_RUN | No row case or bound from/to version migration with invariant oracle. No substitute-by-analogy used. |
| 63 | UPGRADE | pipd-assurance-tqaep | NOT_RUN | No row case or bound from/to version migration with invariant oracle. No substitute-by-analogy used. |
| 64 | UPGRADE | pipd-package-project | NOT_RUN | No row case or bound from/to version migration with invariant oracle. No substitute-by-analogy used. |
| 65 | ROLLBACK | pipd-route-intake | NOT_RUN | No row case or bound preimage, rollback action and exact-state comparator. No substitute-by-analogy used. |
| 66 | ROLLBACK | pipd-authority-source | NOT_RUN | No row case or bound preimage, rollback action and exact-state comparator. No substitute-by-analogy used. |
| 67 | ROLLBACK | pipd-profile-tailor | NOT_RUN | No row case or bound preimage, rollback action and exact-state comparator. No substitute-by-analogy used. |
| 68 | ROLLBACK | pipd-pi-compile | NOT_RUN | No row case or bound preimage, rollback action and exact-state comparator. No substitute-by-analogy used. |
| 69 | ROLLBACK | pipd-pd-bind | NOT_RUN | No row case or bound preimage, rollback action and exact-state comparator. No substitute-by-analogy used. |
| 70 | ROLLBACK | pipd-execution-contract | NOT_RUN | No row case or bound preimage, rollback action and exact-state comparator. No substitute-by-analogy used. |
| 71 | ROLLBACK | pipd-assurance-tqaep | NOT_RUN | No row case or bound preimage, rollback action and exact-state comparator. No substitute-by-analogy used. |
| 72 | ROLLBACK | pipd-package-project | NOT_RUN | No row case or bound preimage, rollback action and exact-state comparator. No substitute-by-analogy used. |
| 73 | UNINSTALL | pipd-route-intake | NOT_RUN | No row case or isolated install/uninstall target with retention/residue oracle. No substitute-by-analogy used. |
| 74 | UNINSTALL | pipd-authority-source | NOT_RUN | No row case or isolated install/uninstall target with retention/residue oracle. No substitute-by-analogy used. |
| 75 | UNINSTALL | pipd-profile-tailor | NOT_RUN | No row case or isolated install/uninstall target with retention/residue oracle. No substitute-by-analogy used. |
| 76 | UNINSTALL | pipd-pi-compile | NOT_RUN | No row case or isolated install/uninstall target with retention/residue oracle. No substitute-by-analogy used. |
| 77 | UNINSTALL | pipd-pd-bind | NOT_RUN | No row case or isolated install/uninstall target with retention/residue oracle. No substitute-by-analogy used. |
| 78 | UNINSTALL | pipd-execution-contract | NOT_RUN | No row case or isolated install/uninstall target with retention/residue oracle. No substitute-by-analogy used. |
| 79 | UNINSTALL | pipd-assurance-tqaep | NOT_RUN | No row case or isolated install/uninstall target with retention/residue oracle. No substitute-by-analogy used. |
| 80 | UNINSTALL | pipd-package-project | NOT_RUN | No row case or isolated install/uninstall target with retention/residue oracle. No substitute-by-analogy used. |
| 81 | MUT | pipd-route-intake | NOT_RUN | No row case or bound mutation operator/seed and specific runtime POS/NEG oracle. No substitute-by-analogy used. |
| 82 | MUT | pipd-authority-source | NOT_RUN | No row case or bound mutation operator/seed and specific runtime POS/NEG oracle. No substitute-by-analogy used. |
| 83 | MUT | pipd-profile-tailor | NOT_RUN | No row case or bound mutation operator/seed and specific runtime POS/NEG oracle. No substitute-by-analogy used. |
| 84 | MUT | pipd-pi-compile | NOT_RUN | No row case or bound mutation operator/seed and specific runtime POS/NEG oracle. No substitute-by-analogy used. |
| 85 | MUT | pipd-pd-bind | NOT_RUN | No row case or bound mutation operator/seed and specific runtime POS/NEG oracle. No substitute-by-analogy used. |
| 86 | MUT | pipd-execution-contract | NOT_RUN | No row case or bound mutation operator/seed and specific runtime POS/NEG oracle. No substitute-by-analogy used. |
| 87 | MUT | pipd-assurance-tqaep | NOT_RUN | No row case or bound mutation operator/seed and specific runtime POS/NEG oracle. No substitute-by-analogy used. |
| 88 | MUT | pipd-package-project | NOT_RUN | No row case or bound mutation operator/seed and specific runtime POS/NEG oracle. No substitute-by-analogy used. |
| 89 | JOURNEY | pipd-route-intake | NOT_RUN | No row case or bound skill consumer entrypoint with genuine end-to-end outcome. No substitute-by-analogy used. |
| 90 | JOURNEY | pipd-authority-source | NOT_RUN | No row case or bound skill consumer entrypoint with genuine end-to-end outcome. No substitute-by-analogy used. |
| 91 | JOURNEY | pipd-profile-tailor | NOT_RUN | No row case or bound skill consumer entrypoint with genuine end-to-end outcome. No substitute-by-analogy used. |
| 92 | JOURNEY | pipd-pi-compile | NOT_RUN | No row case or bound skill consumer entrypoint with genuine end-to-end outcome. No substitute-by-analogy used. |
| 93 | JOURNEY | pipd-pd-bind | NOT_RUN | No row case or bound skill consumer entrypoint with genuine end-to-end outcome. No substitute-by-analogy used. |
| 94 | JOURNEY | pipd-execution-contract | NOT_RUN | No row case or bound skill consumer entrypoint with genuine end-to-end outcome. No substitute-by-analogy used. |
| 95 | JOURNEY | pipd-assurance-tqaep | NOT_RUN | No row case or bound skill consumer entrypoint with genuine end-to-end outcome. No substitute-by-analogy used. |
| 96 | JOURNEY | pipd-package-project | NOT_RUN | No row case or bound skill consumer entrypoint with genuine end-to-end outcome. No substitute-by-analogy used. |
