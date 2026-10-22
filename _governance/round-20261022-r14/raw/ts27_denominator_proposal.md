# R14-TS27 — unsigned semantic acceptance denominator proposal

**D_clause_semantic=UNRESOLVED. No semantic completeness percentage is authorized.**

## 1. Operational denominator and scope

Product: One Shared Core / SBLM01..06, three separate SP responsibilities, PIPD adapters, HGK/Fabric governed construction and assurance, Host/delivery lifecycle, SWOF dogfood. Sources: exact local DOC-00..13 bytes below. Similar filenames or references to upstream documents do not acquire authority from this proposal.

Final counting unit: one independently falsifiable semantic obligation keyed by authority namespace, source digest and clause span, actor/consumer, trigger/preconditions, one observable predicate, outcome/effect boundary and applicability context. Split compound predicates with distinct failure outcomes, consumers or authority. D is the cardinality of Source-Owner-ratified equivalence classes of applicable atomic obligations. A requirement ID, ACC link, Cxx family, test, source row, installed wheel or delivery surface is not automatically one obligation.

In scope: operative behavioral clauses, schema/ABI invariants, human/Native authority and security boundaries, negative cases, acceptance/Oracle conditions, receipt joins, install/upgrade/uninstall/rollback, cross-domain handoffs and recovery. R/D sections can add requirements beyond C chapters. Every operative source occurrence maps to a ratified atom or individually signed exclusion. Any active orphan blocks FULL PASS.

Out of final D only after recorded Source Owner disposition: pure navigation/physical inventories, non-operative history, duplicate restatements with equivalent predicate/scope/authority, and genuinely inapplicable contexts with signed reason. Preserve aliases and distinct predicates. Examples can contain operative obligations: no blanket exclusion. Blocked-but-required items remain in D; missing permit is not N/A. Research names do not imply installations. Source gaps remain UNKNOWN/open.

Measured candidate unit: one nonempty direct heading-body review packet including preamble. Split at ATX headings outside code fences. Parent introductory prose is retained; tables and fenced examples remain owned by the containing packet; empty heading-only intervals add no unit. No nested-content double counting or silent semantic merge. Packets may contain compound obligations or non-operative material. Their numeric total is review workload, NOT D_clause_semantic. Final atomic total is UNMEASURED pending decomposition, equivalence, supersession and applicability adjudication. Signing the parser count alone does not resolve TS27.

## 2. Measurement command and actual output

Full parser/generator: `C:/Projects/Agent_Workspace/_r14_packet/raw/ts27_measure.py`. Reads complete source bytes; not snippets. Table-key counts are actual rows, not numbers copied from titles. All exact regexes follow.

```text
python C:/Projects/Agent_Workspace/_r14_packet/raw/ts27_measure.py
MEASURED_UTC=2026-10-22T02:04:22.032829+00:00
DOC=DOC-00 packets=57 headings=73 bytes=465363 lines=1591 sha256=bd9c1a85ea0cae68fa8cde617e5592fca6123f72b4caf1a9d2894167d9a82e01
DOC=DOC-01 packets=164 headings=164 bytes=1041962 lines=4938 sha256=43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f
DOC=DOC-02 packets=112 headings=114 bytes=1148207 lines=11084 sha256=4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035
DOC=DOC-03 packets=100 headings=103 bytes=1704253 lines=4851 sha256=ea69e1d3718ed86aecd74a3ebcc933960eacc30b586ab80fcb9f733037e33476
DOC=DOC-04 packets=141 headings=142 bytes=618110 lines=3036 sha256=ee90cb1c86f6f7350c11c9c962233a89b035ca41ff82c8968f7968608fc6f6e0
DOC=DOC-05 packets=169 headings=241 bytes=2382349 lines=7888 sha256=3b47a0b6224b1984a4047cf53aac5ac50615c93a560fea46e1b43d079a5d9f27
DOC=DOC-06 packets=67 headings=68 bytes=1554880 lines=2858 sha256=64ea4977dab3093301f82dc7469413cc754998fc53946467842e06d83645102b
DOC=DOC-07 packets=124 headings=131 bytes=1265128 lines=3620 sha256=a366d3783c82089c5593ffabb0704d8507632cce45622684f7a0186f2ae310f8
DOC=DOC-08 packets=53 headings=65 bytes=925526 lines=11139 sha256=c7029c1ff07abe3135d33d3abf858a5fecedd911b494cd69c16eb1ddb8158288
DOC=DOC-09 packets=98 headings=118 bytes=904598 lines=3978 sha256=6450f7c15915ec8b304f4e5fd4093ea707434db8bae9d2bb6e66c30ab6eed2e1
DOC=DOC-10 packets=106 headings=123 bytes=1397936 lines=3888 sha256=a64aa21c977334dd74d660a86377ee10c4d329aa5fde0dae25ff81a3e69e8d8f
DOC=DOC-11 packets=237 headings=254 bytes=1831131 lines=5005 sha256=12f8705d780b76f264457c194a6ff359da8d74b5d6d8c83fa245b74d2a37508e
DOC=DOC-12 packets=122 headings=135 bytes=982931 lines=7940 sha256=d1e470d82ca14319582cb8947aa52007927aa38e726249b1430804cfe8c8ca56
DOC=DOC-13 packets=193 headings=197 bytes=1251068 lines=3814 sha256=7cc0c8b17311130c875910b2548b93c28bd4e1c8ee04d300f85fc33d4c09beb1
DIAGNOSTIC=Cxx contract-family H1 IDs count=54
DIAGNOSTIC=Requirement/atom ID lexemes count=208
DIAGNOSTIC=Acceptance ID lexemes count=1631
DIAGNOSTIC=U-child IDs DOC-01 count=149
DIAGNOSTIC=DeliverySurface IDs DOC-00 count=38
DIAGNOSTIC=TQAEP cells DOC-08 count=96
TOTAL_CANDIDATE_REVIEW_PACKETS=1743
CLASSIFIED_STATUS_PACKETS={"UNKNOWN": 1743, "absent": 0, "implemented": 0, "partial": 0}
SOURCE_MANIFEST_SHA256=83eb1cb1b985c8af67a740d9bd8c1eacd594cd45b1fa674f5c88435ee6d6eea6
SOURCE_SUMMARY_DIGESTS_MATCH=true
SIGNED=false; SIGNER=null; ATOMIC_SEMANTIC_TOTAL=UNMEASURED
```

```python
HEAD = '^ {0,3}(#{1,6})[ \\t]+(.+)$'
FENCE = '^ {0,3}(`{3,}|~{3,})(.*)$'
REQ = '(?<![A-Za-z0-9_-])(?:SBL-PROP-(?:REQ|ATOM)-[A-Z0-9]+(?:-[A-Z0-9]+)*|D[0-9]{2}-REQ-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)(?![A-Za-z0-9_-])'
ACC = '(?<![A-Za-z0-9_-])(?:SBL-PROP-ACC|ACC)-[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*(?![A-Za-z0-9_-])'
CHILD = '^\\|[ \\t]*`?(U[0-9]{2}\\.[0-9]+)`?[ \\t]*\\|'
SURFACE = '^\\|[ \\t]*`?(C-[0-9]{3})`?[ \\t]*\\|'
CELL = '^\\|[ \\t]*(POS|NEG|EDGE|SEC|PERF|PARITY|RECOVERY|UPGRADE|ROLLBACK|UNINSTALL|MUT|JOURNEY)/(DETERMINISTIC|STATE_READBACK|PROPERTY|REFERENCE_OUTPUT|STATISTICAL|SEMANTIC_JUDGE|HUMAN|COMPOSITE)[ \\t]*\\|'
```

Fence closure: same marker, width at least opening width, whitespace-only suffix. Diagnostics exclude fenced text but may retain templates/historical mentions; REQ/ACC are lexical subsets, not exhaustive semantic extraction. Cxx IDs are deduped globally; children/surfaces/TQAEP use selected source documents and exact keys. Diagnostics overlap the packet corpus and are never added together.

| Unit | Measured count | Included in packet total? |
|---|---:|---|
| DOC-00 clause-review packets | 57 | yes |
| DOC-01 clause-review packets | 164 | yes |
| DOC-02 clause-review packets | 112 | yes |
| DOC-03 clause-review packets | 100 | yes |
| DOC-04 clause-review packets | 141 | yes |
| DOC-05 clause-review packets | 169 | yes |
| DOC-06 clause-review packets | 67 | yes |
| DOC-07 clause-review packets | 124 | yes |
| DOC-08 clause-review packets | 53 | yes |
| DOC-09 clause-review packets | 98 | yes |
| DOC-10 clause-review packets | 106 | yes |
| DOC-11 clause-review packets | 237 | yes |
| DOC-12 clause-review packets | 122 | yes |
| DOC-13 clause-review packets | 193 | yes |
| Cxx contract-family H1 IDs | 54 | no: overlapping diagnostic |
| Requirement/atom ID lexemes | 208 | no: overlapping diagnostic |
| Acceptance ID lexemes | 1631 | no: overlapping diagnostic |
| U-child IDs DOC-01 | 149 | no: overlapping diagnostic |
| DeliverySurface IDs DOC-00 | 38 | no: overlapping diagnostic |
| TQAEP cells DOC-08 | 96 | no: overlapping diagnostic |


Historical source-record, different-ID and ACC-link universes named by the round are not adopted as semantic D. Their equivalence is UNMEASURED. JSON total sums only in_scope=true rows, with an explicit structural total_kind. Diagnostic in_scope=false means excluded from arithmetic because overlapping, NOT authority to discard those obligations. All packet source spans and diagnostic ID occurrences are materialized in JSON.

## 3. Status per unit and evidence basis

Every packet and diagnostic item is UNKNOWN for implementation. This is NOT a finding of absent product behavior. This source-measurement task did not assess a packet-specific implementation/raw-test/independent-checker join. JSON.packet_inventory supplies source path, digest, exact interval, status_basis and implementation_evidence=[] for each packet; diagnostic_inventories supplies each ID and exact occurrences. Those are source evidence, not implementation evidence.

| Unit | Implementation status | Evidence / judgement scope |
|---|---|---|
| DOC-00 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-00.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-01 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-01.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-02 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-02.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-03 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-03.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-04 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-04.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-05 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-05.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-06 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-06.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-07 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-07.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-08 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-08.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-09 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-09.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-10 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-10.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-11 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-11.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-12 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-12.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |
| DOC-13 packets | UNKNOWN for every packet | `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_DOC-13.md`; per-packet spans/status_basis in JSON; NOT_ASSESSED for subject-bound implementation |


Implemented requires every applicable predicate to have pinned implementation, genuine consumer/world readback, applicable positive/negative/boundary/security raw results and independent checker. Partial requires evidence for an identified proper subset and explicit gaps. Absent requires positive evidence of missing required applicable behavior on the exact candidate, such as a controlled failing case with asserted expected outcome. No adequate evidence or no assessment = UNKNOWN, never absent. CLASSIFIED_STATUS_PACKETS counts classifications in THIS proposal, not product failure totals.

Evidence read: `C:/Projects/Agent_Workspace/_r14_ev/_governance/round-20261022-r14/SBL_R14_EXECUTION_STATUS.md#L65-L71` is an earlier checkpoint recording semantic denominator UNKNOWN / Source Owner unsigned, not a fresh full-product verdict. `C:/Projects/Agent_Workspace/SBL/evidence/source/SOURCE_FREEZE_SUMMARY.json#L81-L82` limits its freeze to local bytes, not Owner-approved SourceFreeze; file digests were freshly compared above. `C:/Projects/Agent_Workspace/SBL/evidence/EVIDENCE_MANIFEST.json#L1-L12` is a file manifest, not an obligation-to-implementation closure proof. Existing code or global test totals do not establish packet implementation.

Required evidence chain per ratified atom: source clause -> semantic predicate -> implementation symbol/path -> test/Oracle -> raw receipt with exact subject/candidate digest -> independent checker -> Owner decision. Stale/foreign subject evidence cannot advance status. No product runtime tests were executed in this proposal.

## 4. Concrete Source Owner signature block — deliberately unsigned

Before signing an OFFICIAL denominator, materialize the reviewed atomic ledger and every source-packet disposition, equivalence/supersession decision and legitimate exclusion. Bind exact bytes in an external signed receipt. Approval to review this proposal alone is not denominator ratification or product acceptance.

```text
decision_kind: OFFICIAL_SEMANTIC_DENOMINATOR_RATIFICATION
proposal_version: TS27-DRAFT-1 (or named reviewed successor)
source_scope: exact SBL_PIPD-LS-PKG_DOC-00..13 snapshot below
source_manifest_sha256: 83eb1cb1b985c8af67a740d9bd8c1eacd594cd45b1fa674f5c88435ee6d6eea6
manifest_encoding: DOC-ID SPACE lowercase-file-sha256 LF; ordered DOC-00..13; final LF
final_proposal_json_sha256: TO_BE_COMPUTED_BY_SIGNER_FROM_FINAL_BYTES
ratified_semantic_ledger_path_and_sha256: UNSUPPLIED
equivalence_supersession_ledger_sha256: UNSUPPLIED
applicability_and_exclusion_ledger_sha256: UNSUPPLIED
source_doc_versions: exact headers in JSON.sources plus manifest digests; Owner confirms
atomic_semantic_denominator: UNMEASURED / NOT_RATIFIED
product_kind_mode_host_risk_profile_permission_scope: UNSUPPLIED
source_owner_name_principal_organization: UNSIGNED
source_owner_authority_basis: UNSIGNED
decision_date_time_with_timezone: UNSIGNED
assertion: every operative clause maps to a ratified atom or signed exclusion; no silent orphan
signature_or_verifiable_receipt: UNSIGNED
change_rule: changed source/applicability/ledger bytes require new ratification
```

No artifact self-digest is embedded: external receipt binds final JSON and reviewed ledger bytes. Source Owner signs denominator truth, not Native permits, independent acceptance or release. Today signer identity/authority, decision date, atomic count/ledger, equivalence, applicability/exclusions and signature are unsigned/unprovided. No agent may fill them as Owner. signed=false states this candidate status, not a global signature-store search.

## 5. Exact claim ceiling today

Unsigned measured inventory and denominator proposal only. D_clause_semantic=UNRESOLVED; atomic semantic total=UNMEASURED. No semantic completeness percentage, FULL PASS, M4 completion, Owner ratification, Native acceptance or release is authorized. UNKNOWN is not absent.

Allowed: source-bound review workload, lexical/table inventories, unsigned definition, explicitly scoped artifact observations and UNKNOWNs. Prohibited: any semantic completeness percentage, including a zero-complete percentage inferred from UNKNOWN; FULL PASS/M4 closure; all requirements implemented/absent; Owner-approved denominator/SourceFreeze; Native acceptance, world-effect permission or release. After denominator signature, a percentage still needs a separately evidence-validated numerator over exactly the same scope; this proposal provides neither that numerator nor product acceptance.

## 6. Reproducible source snapshot

Measured UTC: 2026-10-22T02:04:22.032829+00:00. Version identity is exact file bytes/digest. JSON.sources includes opening version/header text. Source root: `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG`.

| DOC | bytes | lines | SHA256 |
|---|---:|---:|---|
| DOC-00 | 465363 | 1591 | `bd9c1a85ea0cae68fa8cde617e5592fca6123f72b4caf1a9d2894167d9a82e01` |
| DOC-01 | 1041962 | 4938 | `43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f` |
| DOC-02 | 1148207 | 11084 | `4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035` |
| DOC-03 | 1704253 | 4851 | `ea69e1d3718ed86aecd74a3ebcc933960eacc30b586ab80fcb9f733037e33476` |
| DOC-04 | 618110 | 3036 | `ee90cb1c86f6f7350c11c9c962233a89b035ca41ff82c8968f7968608fc6f6e0` |
| DOC-05 | 2382349 | 7888 | `3b47a0b6224b1984a4047cf53aac5ac50615c93a560fea46e1b43d079a5d9f27` |
| DOC-06 | 1554880 | 2858 | `64ea4977dab3093301f82dc7469413cc754998fc53946467842e06d83645102b` |
| DOC-07 | 1265128 | 3620 | `a366d3783c82089c5593ffabb0704d8507632cce45622684f7a0186f2ae310f8` |
| DOC-08 | 925526 | 11139 | `c7029c1ff07abe3135d33d3abf858a5fecedd911b494cd69c16eb1ddb8158288` |
| DOC-09 | 904598 | 3978 | `6450f7c15915ec8b304f4e5fd4093ea707434db8bae9d2bb6e66c30ab6eed2e1` |
| DOC-10 | 1397936 | 3888 | `a64aa21c977334dd74d660a86377ee10c4d329aa5fde0dae25ff81a3e69e8d8f` |
| DOC-11 | 1831131 | 5005 | `12f8705d780b76f264457c194a6ff359da8d74b5d6d8c83fa245b74d2a37508e` |
| DOC-12 | 982931 | 7940 | `d1e470d82ca14319582cb8947aa52007927aa38e726249b1430804cfe8c8ca56` |
| DOC-13 | 1251068 | 3814 | `7cc0c8b17311130c875910b2548b93c28bd4e1c8ee04d300f85fc33d4c09beb1` |


## 7. Unresolved work and side effects

- PIPD Source Owner has not ratified this candidate, scope, decomposition, equivalence/supersession, applicability or exclusions. signed=false describes this proposal, not a global signature search.

- UNMEASURED: unique applicable atomic semantic obligations; packets can contain compound obligations or non-operative material; Owner adjudication required.

- UNMEASURED: implemented/partial/absent product totals; each packet is UNKNOWN because exact subject-bound implementation/evidence/checker joins were not assessed.

- Uncoded natural-language requirements and schema invariants are not exhaustively atomicized by REQ/ACC lexical diagnostics.

- Orphan-free source-to-atom trace and legitimate exclusions are not established. Active orphan prevents FULL PASS.

- Host lifecycle, Native PIPD receipts, SWOF W3 permit and acceptance/release were not revalidated in this proposal.

Only ts27_denominator_proposal.md, ts27_denominator.json and retained ts27_measure.py are written under requested raw output directory. Source DOCs, product repos and existing round governance artifacts are not modified. No self-acceptance, Owner signature, runtime product test or official denominator is issued.

