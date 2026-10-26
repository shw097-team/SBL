# CR-ORACLE-001 field compatibility RFC, R00.1 revision 0

State: OWNER_DIRECTION_RECORDED / CR_ORACLE_001_OPEN / HOLD_AFFECTED_ONLY.
This document proposes a versioned migration; it is not a signed Canonical Erratum.
Source references below are identity/section locators, not copies of source prose.

## Verified source identities

| Source | SHA256 | exact consumed location |
|---|---|---|
| PIPD_LS DOC-02 | a021998dd3b63015e89af1dd40e0b413744a69b872da46c6bf5f4d92f7f23d0b | 14.1 VerificationPlan L2143-2147; 14.2 OracleRegistry L2485-2489 |
| PIPD_LS DOC-03 | d89d82dcd2c8603ec6b86c5ec8c40845e4594bc181adf5272bd48a3de7c88f0f | PD-08 L540-558; OracleType L607-618 |
| PIPD_LS DOC-07 | a68dae1c3670d07bcfa3476a1e37463c534594df5cd65d8dab0dca064b5a9fc1 | Canonical role L58; Oracle contract L619-658; Writer boundaries L2298-2324 |
| Installed P4 output schema | 4ae7d32a4ad04b6878a17ddac42b36e085f3485f2ad9f8cd60840dbd74149e71 | urn:pipd:skill:pipd-pi-compile:output:1; /properties/acceptance |
| SBL DOC-03 conflict discussion | ea69e1d3718ed86aecd74a3ebcc933960eacc30b586ab80fcb9f733037e33476 | L124,565,959,1210; conflict description, not an Oracle Writer grant |

Installed P4 and PIPD_ROOT output schema bytes match; the Git blob also equals current
PIPD-LS-SP main. Actual Canonical DOC-02/03/07 contain zero DOMAIN_ORACLES literals.
The unqualified legacy string must not be silently bound to PIPD DOC-03, SBL DOC-03
or a guessed registry. A true domain-source identity remains a ratification prerequisite.

## Field crosswalk

| Semantic field | PIPD DOC-02 / DOC-03 | DOC-07 responsibility | installed P4 / current producer | smallest compatible proposal and remaining gate |
|---|---|---|---|---|
| verification writer | DOC-02 builds PI; DOC-03 builds PD/TQAEP | sole TEST/ORACLE/FIXTURE semantics Writer, not lifecycle/permission/release authority | scalar source label has no Writer/namespace/version binding | external versioned SourceRef proposal; true Writer and schema Owner ratification required |
| acceptance.mode | bound requirement / plan relations | conformance semantics and stable FFI | const bound | preserve unchanged |
| acceptance.oracle_source | OracleRegistry/OracleBinding refs; TQAEP oracle_bindings | version/hash/currentness/subject/environment and checker bindings | const DOC-03 DOMAIN_ORACLES, emitted in pipeline.py L171 | keep literal for old ABI; introduce an explicitly versioned binding contract only after Owner Erratum; never edit const alone |
| per-atom mapping | VER/ORACLE/REQ/Fixture/Procedure/FFI; test_case_refs and expected_observations | exact oracle/fixture/profile and decision rule | PI atoms and trace exist; scalar acceptance is insufficient for these semantics | separate candidate map with exact atom identity, oracle version/hash, POS/NEG fixture refs, predicate; no coverage collapse |
| source currentness | exact source refs and candidate_ref | stale/foreign evidence rejection before scoring | scalar literal cannot identify authoritative source bytes | pin schema and DOC-07 hash; hold actual legacy source binding until fully qualified |
| identity / trace | PI identity and trace; PD/TQAEP candidate/env refs | verifies consumed identities; does not rewrite sibling ownership | P4 trace has from/to refs but no separate trace artifact identity fields; current S0 PI requires trace item identity fields | explicit schema-version crosswalk and content-hash/trace requalification required; preserve legacy PI object |
| additionalProperties | contract-specific artifact fields | adapter cannot gain Writer authority | P4 root/acceptance reject extra keys; S0 acceptance is unconstrained at schema level | no new field inserted into PI-PKG@1; proposal has its own closed candidate schema |
| test/fixture/oracle types | DOC-03 TQAEP construction and environment | eight OracleType classes, 12 TestClass classes and profile rules | P4 const/schema alone cannot prove semantic coverage | retain original denominators; run only affected local fixtures now; formal coverage remains NOT_RUN |
| conformance/acceptance | DOC-03 required gate plan | schema green / CI green / maker PASS do not imply independent acceptance | root S0 schema may accept an unsupported acceptance shape | report schema-level observation only; independent Checker and Native effect gates stay unbound |

## Implemented isolated proposal

Local branch `candidate/fhs-msc-r001-oracle-adapter`, commit `6e20c2c6264b9e54992b627e6dae04a20800c02c`;
base current PIPD-LS-SP main `e95942abcb6aa07e69304607ab8afc22a74fc67d`.
Bundle SHA256 `6ab0332f9eaab34ab1c59c46faaa1ad854a8390f3e9746a2029f03558e0d09fe` (LF-joined path and SHA256 pairs in the private receipt's
listed order; receipt itself excluded). Four new local candidate files: typed Python
adapter, closed candidate JSON schema, targeted tests and Erratum proposal. No existing
pipeline, skill schema, Canonical source or deployed artifact was edited. Candidate code
was not published to any remote; these public documents contain derived findings only.

The adapter checks input subject digest, pinned P4 schema bytes, actual P4 validation,
DOC-07 hash/version/namespace, explicit legacy domain namespace, complete unique atom
coverage, unique oracle IDs, fixture polarity and trace identity. It returns a separate
FHS-MSC-OracleBindingProposal@0 with effect_kind NONE and CR_ORACLE_001_OPEN. It never
compiles a PI/TQAEP or re-seals the legacy artifact. The test domain-source is expressly
synthetic; no actual domain registry mapping is claimed.

## Actual affected tests

15 tests passed, exit 0, on commit `6e20c2c6264b9e54992b627e6dae04a20800c02c`. Raw maker test output SHA256
`c523ec917b81bb44efc738c20a9ee181cb4f60ec8a1a9b7beb2311475600ac4c`. These are maker-side isolated results, not independent AO.

| Fixture | Actual expected result |
|---|---|
| POS legacy-preserving proposal | exact input object and digest preserved; new candidate validates; not valid as a PI-PKG |
| NEG direct const string rewrite | P4_LEGACY_SCHEMA_REJECTED |
| NEG mutated schema admitting new const | P4_SCHEMA_PIN_MISMATCH |
| NEG stale/foreign subject | STALE_OR_FOREIGN_SUBJECT before other errors |
| NEG foreign DOC-07 bytes | DOC07_SOURCE_PIN_MISMATCH |
| NEG ambiguous DOC-03 namespace | LEGACY_NAMESPACE_UNBOUND |
| NEG zero maps | ZERO_ORACLE_MAPPINGS |
| NEG dropped/orphan atom | ORACLE_ATOM_COVERAGE_MISMATCH |
| NEG reused POS/NEG fixture | FIXTURE_POLARITY_COLLAPSED |
| NEG undeclared acceptance sidecar | P4_LEGACY_SCHEMA_REJECTED |
| NEG foreign trace digest | LEGACY_TRACE_IDENTITY_MISMATCH |
| NEG duplicate oracle ID across two atoms | ORACLE_ID_COLLISION |
| SEC candidate claiming Native acceptance/Permit | candidate schema rejects both changes |
| Boundary S0 schema accepts a shape P4 refuses | observed shape-level divergence; no product semantic PASS inferred |

## Versioned migration and release holds

1. Ratify fully qualified legacy domain-source identity and decide whether it remains read-only source or needs versioned retirement.
2. DOC-02/DOC-07/schema Owners issue a versioned Erratum identifying compatible old/new contracts and their consumers. No claim is made that this RFC supplies their signature.
3. Choose versioned separate binding versus versioned PI acceptance extension; update producer, PD/TQAEP consumers, identity/trace rules, fixtures and installed distribution together. Preserve old-version ABI and identity where still consumed.
4. Run affected real source fixtures and stale/foreign/duplicate/missing/sidecar/permission negatives under an independently authorized Checker, bound to the exact candidate.
5. Obtain actual Native admission for any future effect. Formal compile, promotion, SourceFreeze, AO, merge and release remain HOLD until prerequisites have genuine receipts.

No second PI Compiler, Issuer, Scheduler or Policy DB was introduced. R15.1 949,
R17 145-ID, 42 findings and all Golden Journeys remain NOT_RUN in this round.
