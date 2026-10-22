# R14-TS19 / TS20 / TS21 measured inventories

Observed at: 2026-10-22T09:58:53.860567+08:00
Scope: read-only parsing of canonical local DOCs and existing SBL R6 evidence ledgers. Writes are confined to `C:/Projects/Agent_Workspace/_r14_packet/raw`. No installs, dispatch, tests of product behavior, repository edits, admission, acceptance, or remote operations were performed.

## Measured counts and honest deltas

| Obligation | Expected | Measured unique identities | Delta (measured minus expected) | Missing identity evidence |
|---|---:|---:|---:|---:|
| TS19 parents | 50 | 50 | 0 | 0 |
| TS19 children | 149 | 149 | 0 | 0 |
| TS20 source identities | 441 | 441 | 0 | 0 |
| TS21 delivery surfaces | 38 | 38 | 0 | 0 |

Counts are identity inventory coverage, NOT runtime closure or full DOC acceptance.

## TS19 method and orphan proof

Source: `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-01.md`. Parse only the C05.1 and C05.2 Markdown tables; split unescaped pipes; accept first-column parent IDs with `U\d{2}` and child IDs with `U\d{2}\.\d+`. Child-to-parent links come from the explicit SECOND column of C05.2, not an assumed prefix. A second extraction by line ranges independently agreed with the section parser.

- Parent IDs measured in C05.1: 50; children measured in C05.2: 149; unique children: 149.
- Set subtraction `set(child.parent_id) - set(parent.id)` = `[]`.
- Actual orphan child list = `[]`.
- Parents with no children: `[]`.
- Existing ledger: `C:/Projects/Agent_Workspace/SBL/evidence_ledger/child_outcome_ledger.json` sections `/parents` and `/children`; measured 50 parents and 149 children.
- Canonical-minus-ledger child IDs = `[]`; ledger-minus-canonical = `[]`.
- CSV has one row per child, and preserves exact titles including awkward source fragments. Each row cites existing canonical parent/child lines plus its ledger JSON pointer and recorded status. Recorded upstream filename/line is an unverified upstream citation, not a claim that the historical upstream file exists.
- Child records with `raw_evidence: null`: 149/149; current status counts: `{"OPEN": 149}`. Thus zero structural orphans does not establish active closure, independent testing, or implementation evidence.

## TS20 method, frozen/current semantics, and limitations

Parse `C:/Projects/Agent_Workspace/SBL/evidence_ledger/source_identity_441_ledger.json` as JSON; concatenate existing `/donors`, `/slots`, `/methods`, and `/named_identities` arrays. Preserve IDs exactly as stored; do NOT invent IDs by numbering to 441. Measured group sizes: `{"donors": 6, "slots": 24, "methods": 25, "named_identities": 386}`; unique ID count 441; duplicate identities 0. The record locators are JSON pointers into this existing file. The digest column hashes that whole ledger file, not the external package and not a formal Owner source freeze.

`kind=frozen` means a historical frozen-disposition record, NOT an R14 formally frozen source or an installed package. Every row's disposition carries BOTH `recorded_frozen_disposition` and `recorded_current_execution`, with `live_execution=NOT_MEASURED_READ_ONLY_INVENTORY`. Recorded R6 execution is not misrepresented as current R14 execution. Recorded current execution counts: `{"NOT_EXECUTED_THIS_ROUND": 440, "EXECUTED_IN_R5_R6_CI": 1}`.

Canonical independent eight-bucket data-row parse: 386 unique named identities, bucket sizes `{"NOBJ24": 24, "OSS19": 19, "PD06_31": 31, "W3_TECH17": 17, "SUPPLY17": 17, "P0_TOOL78": 78, "NTD40": 40, "LEGACY160": 160}`. Ledger minus canonical set: `[]`; canonical minus ledger: `[]`. This parse selects data rows under the eight `C33.2.BUCKET` headings, excluding header/separator rows. Every line-number join for slots/methods/named identities also asserts that the canonical first-column ID equals the recorded ID (after removing only the existing named-identity bucket prefix for comparison, not altering output identity).

Canonical corroboration uses exact recorded `DOC-XX:Lnnn` locators for slots, methods and named technologies. Donors are joined to DOC-06/C32.1 by existing name; the Matt Pocock / mattpocock/skills name correspondence is disclosed in the builder, while the ledger identity is preserved. Canonical original rows are included in each CSV note. Unresolved canonical locators: `[]`.

- All 441 rows have a frozen and recorded-current disposition field; no live-current per-identity measurement was performed.
- No source identity record supplies a `raw_evidence` receipt field: 441/441. Missing per-record live effect evidence is 441, not missing identity evidence.
- Named identities whose canonical DOC-06 original disposition is NOT equal to the ledger's frozen label: 386. These are distinct historical/canonical fields, not asserted runtime contradictions. The CSV retains both rather than silently promoting the historical label to source law. In particular, any source-law prohibition remains authoritative.
- Existing identity ledger and canonical documents exist. External software/version/license artifacts and per-identity current invoke/deny/rollback receipts were not verified. The 441 identity count does not prove 441 installed components.

## TS21 method and host applicability

Parse `C:/Projects/Agent_Workspace/SBL/evidence_ledger/surface_c001_c038_ledger.json` `/surfaces`, then join exact IDs to `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-12.md` section D12-04.PATCH. Its table first column is matched with backtick-delimited `C-\d{3}`. Each source row is cited by exact absolute path and line. Host applicability and delivery kind are classified from that source-exact surface name; generic Skill/local-host rows explicitly remain host-dependent, not implicitly applicable to every host.

- Canonical table identities 38; existing surface ledger identities 38; duplicate CSV IDs 0.
- Expected C-001..C-038 minus measured: `[]`; unexpected IDs: `[]`.
- Ledger IDs minus canonical source IDs (surface structural orphans): `[]`.
- Recorded status counts: `{"PARTIAL_LOCAL_SCOPED": 12, "OPEN": 21, "NOT_ADMITTED_NO_DISPATCH": 5}`.
- Actual NOT_ADMITTED IDs: `["C-007", "C-011", "C-015", "C-032", "C-036"]`. These were not installed or dispatched.
- `install_evidence` contains the existing record's scoped historical claim and explicitly null raw receipt, plus the REQUIRED design locator; it is NOT an install-success claim. `deny_evidence` explicitly states no per-surface raw deny reference in the ledger and cites the design's negative oracle rather than inventing a test result.
- Records with `raw_evidence: null`: 38/38. No current install/effective-load/trigger/deny/uninstall lifecycle was measured. Missing per-record lifecycle raw evidence: 38; identity delta is nevertheless 0.
- C-016..018 are preserved as ZIP-kind delivery rows from DOC-12. ChatGPT private Plugin qualification remains HOST_PENDING under R14 TS12. ZIP packaging is not a Host-issued Plugin ID or Host qualification.

## Existing versus absent evidence

The three expected inventory ledgers and canonical DOC-01/DOC-06/DOC-12 are PRESENT. No inventory was fabricated for an absent artifact. Per-child and per-surface raw references are explicitly null in these existing ledgers; per-source live receipt fields are absent. This observation is scoped to those records, NOT a claim that no relevant evidence exists anywhere in the workspace. Active closure under TS19/20/21 remains OPEN pending exact current receipts and independent/Owner qualification.

## Output verification

CSV files were re-opened with Python csv.DictReader; row counts, unique IDs, canonical parent/child set equality and existing evidence files were asserted. Source document/ledger digests (SHA-256, measured bytes):

- `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-00.md`: `bd9c1a85ea0cae68fa8cde617e5592fca6123f72b4caf1a9d2894167d9a82e01`
- `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-01.md`: `43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f`
- `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-06.md`: `64ea4977dab3093301f82dc7469413cc754998fc53946467842e06d83645102b`
- `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-12.md`: `d1e470d82ca14319582cb8947aa52007927aa38e726249b1430804cfe8c8ca56`
- `C:/Projects/Agent_Workspace/SBL/evidence_ledger/child_outcome_ledger.json`: `26466c7e2374b8ad3d997913e4449b137f9e5eea0de011f17dc5015190e98c7e`
- `C:/Projects/Agent_Workspace/SBL/evidence_ledger/source_identity_441_ledger.json`: `e0eee84c95ea0d0287e652c78899ca09ddb4dd6585df5c7c0e54faa3e244af9a`
- `C:/Projects/Agent_Workspace/SBL/evidence_ledger/surface_c001_c038_ledger.json`: `81a3c48109f1be035cc42c3ee57ce5fd06d00d907f1fb6fbb51cd8b41aefb5f7`

Produced CSV receipts:
- `ts19_traceability.csv`: 149 rows; SHA-256 `a61a5ffeb65b9db3e0adb1ce8359d3f0f113e3b26fff806d6153e39df2f587c6`.
- `ts20_sources.csv`: 441 rows; SHA-256 `eacd385338b4933a7a1a58e824f65168f7f4812128d3145301b8a4f8e5b63ff7`.
- `ts21_surfaces.csv`: 38 rows; SHA-256 `ba507a5d3e94adf90f604ec37b74b363b46c3ff205cd2ce40b015cf768d9bf54`.

Reproduction: run `python C:/Projects/Agent_Workspace/_r14_packet/raw/build_ts19_21_inventory.py` (reads the live artifacts and rewrites only the four inventory deliverables in this output root). No product acceptance verdict is issued.
