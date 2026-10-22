# TS19/20/21 line-anchor verification

Schema: `SBL-TS19-21-ANCHORS/1`

ANCHOR_VERIFICATION_ONLY: VERIFIED means all extracted distinct line locators for that row exist, decode strictly as UTF-8, are nonempty and contain an explicit row identifier. Primary-anchor counts are separately reported and do not override failed upstream anchors. No runtime execution, installation, acceptance, qualification, upstream source/version authenticity, or receipt validity is established.

## Denominators and row states

| CSV | Denominator | Anchor-verified (all locators) | Not anchor-verified | Primary anchor VERIFIED |
|---|---:|---:|---:|---:|
| ts19_traceability.csv | 149 | 0 | 149 | 149 |
| ts20_sources.csv | 441 | 24 | 417 | 435 |
| ts21_surfaces.csv | 38 | 38 | 0 | 38 |

These are exactly the requested 149 / 441 / 38 input rows. A row with a verified canonical line and a missing historical citation is NOT anchor-verified overall.

| CSV | VERIFIED | CONTENT_MISMATCH | EMPTY_LINE | MISSING_FILE | LINE_OUT_OF_RANGE | UNPARSEABLE_LOCATOR | UTF8_DECODE_ERROR | READ_ERROR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ts19_traceability.csv | 0 | 0 | 0 | 149 | 0 | 0 | 0 | 0 |
| ts20_sources.csv | 24 | 6 | 0 | 411 | 0 | 0 | 0 | 0 |
| ts21_surfaces.csv | 38 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Method / limitations

- **row_aggregation**: VERIFIED iff all distinct locators VERIFIED; worst state otherwise; full per-anchor failures in anchor_details.json
- **id_policy**: Exact bounded tokens: child_id (primary TS19), parent_id (other TS19 anchors), surface_id, identity; TS20 also permits a syntactically explicit canonical_source_row[0] identifier already present in input. No guessed aliases, suffix stripping, title/name matching or nearby-line search.
- **locator_scope**: All string leaves in each row, recursively decoding disposition JSON, including historical citations in canonical_source_row; deduplicate identical resolved path+range but preserve occurrences.
- **resolution**: Absolute paths exact; relative paths under configured DOC root; DOC-XX shorthand resolves to SBL_PIPD-LS-PKG_DOC-XX.md. No basename hunting/replacement.
- **hash_scope**: SHA256 UTF-8 bytes of selected lines INCLUDING original line terminators; range digest concatenates line bytes. Per-line hashes/heads and whole-source hashes in anchor_details.json. CSV multi-anchor digest/head fields are JSON arrays in locator order.
- **receipt_policy**: NOT_PRESENT unless an explicit receipt-key field names a file path; a ledger JSON pointer or a requirement to produce a receipt is not a receipt.

- `EMPTY_LINE`, `UTF8_DECODE_ERROR`, and `READ_ERROR` are explicit unverified states rather than being mislabeled as missing files or content mismatch.
- Bracketed section labels and historical `@sha256` suffixes remain in the original input CSVs but are not asserted to authenticate current file bytes; hashes are recomputed from current exact lines.
- JSON pointers without `:L` are inventory references, not line anchors or execution receipts.
- CJK decoding: no strict UTF-8 decoding errors encountered in files successfully opened; missing files cannot be decoded or assessed.

## Ten worst rows

Severity: UTF8_DECODE_ERROR > READ_ERROR > UNPARSEABLE_LOCATOR > MISSING_FILE > LINE_OUT_OF_RANGE > EMPTY_LINE > CONTENT_MISMATCH; then descending failed-anchor count, CSV, input row. Full locator-level diagnostics: `ts1921_evidence_anchor_details.json`.

- **ts19_traceability.csv #1 `U01.1` — MISSING_FILE** (1/3 anchors unverified)
  - `SBL_PIPD-LS-PKG_全DOC藍圖(8).md:L3676` — **MISSING_FILE**: File not found at resolved exact path
- **ts19_traceability.csv #2 `U01.2` — MISSING_FILE** (1/3 anchors unverified)
  - `SBL_PIPD-LS-PKG_全DOC藍圖(8).md:L3677` — **MISSING_FILE**: File not found at resolved exact path
- **ts19_traceability.csv #3 `U01.3` — MISSING_FILE** (1/3 anchors unverified)
  - `SBL_PIPD-LS-PKG_全DOC藍圖(8).md:L3678` — **MISSING_FILE**: File not found at resolved exact path
- **ts19_traceability.csv #4 `U02.1` — MISSING_FILE** (1/3 anchors unverified)
  - `SBL_PIPD-LS-PKG_全DOC藍圖(8).md:L3679` — **MISSING_FILE**: File not found at resolved exact path
- **ts19_traceability.csv #5 `U02.2` — MISSING_FILE** (1/3 anchors unverified)
  - `SBL_PIPD-LS-PKG_全DOC藍圖(8).md:L3680` — **MISSING_FILE**: File not found at resolved exact path
- **ts19_traceability.csv #6 `U02.3` — MISSING_FILE** (1/3 anchors unverified)
  - `SBL_PIPD-LS-PKG_全DOC藍圖(8).md:L3681` — **MISSING_FILE**: File not found at resolved exact path
- **ts19_traceability.csv #7 `U03.1` — MISSING_FILE** (1/3 anchors unverified)
  - `SBL_PIPD-LS-PKG_全DOC藍圖(8).md:L3682` — **MISSING_FILE**: File not found at resolved exact path
- **ts19_traceability.csv #8 `U03.2` — MISSING_FILE** (1/3 anchors unverified)
  - `SBL_PIPD-LS-PKG_全DOC藍圖(8).md:L3683` — **MISSING_FILE**: File not found at resolved exact path
- **ts19_traceability.csv #9 `U03.3` — MISSING_FILE** (1/3 anchors unverified)
  - `SBL_PIPD-LS-PKG_全DOC藍圖(8).md:L3684` — **MISSING_FILE**: File not found at resolved exact path
- **ts19_traceability.csv #10 `U04.1` — MISSING_FILE** (1/3 anchors unverified)
  - `SBL_PIPD-LS-PKG_全DOC藍圖(8).md:L3685` — **MISSING_FILE**: File not found at resolved exact path

## Exact failure inventory

Missing files below are scoped to exact resolution under the configured DOC root; no claim is made that they are absent everywhere in the workspace.
- MISSING_FILE: `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL_PIPD-LS-PKG_全DOC藍圖(8).md` — 149 row-anchor references.
- MISSING_FILE: `C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG\SBL｜SpecBuild Loop：整合工程總藍圖_v2.0r1(1).md` — 411 row-anchor references.
- CONTENT_MISMATCH: ts20_sources.csv `DONOR-OPENSPEC` — `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-06.md:L134`
- CONTENT_MISMATCH: ts20_sources.csv `DONOR-SPEC-KIT` — `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-06.md:L135`
- CONTENT_MISMATCH: ts20_sources.csv `DONOR-MATT` — `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-06.md:L138`
- CONTENT_MISMATCH: ts20_sources.csv `DONOR-GSD` — `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-06.md:L139`
- CONTENT_MISMATCH: ts20_sources.csv `DONOR-GSTACK` — `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-06.md:L136`
- CONTENT_MISMATCH: ts20_sources.csv `DONOR-SUPERPOWERS` — `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-06.md:L137`

## Receipt states

- ts19_traceability.csv: {"NOT_PRESENT": 149}
- ts20_sources.csv: {"NOT_PRESENT": 441}
- ts21_surfaces.csv: {"NOT_PRESENT": 38}

## Artifacts / mutation boundary

- `ts1921_evidence_anchors.csv`: exactly one row per input row; includes row state, all locators/digests/heads, primary state, and receipt state.
- `ts1921_evidence_anchor_details.json`: every locator, occurrence field, exact resolved path/range, expected/matched IDs, state, digest, per-line heads and diagnostics.
- `ts1921_evidence_SUMMARY.json`: machine-readable counts, input digests and claim ceiling.
- `ts1921_evidence_code/ts1921_verify_anchors.py`: reproducible verifier; placed below an allowed prefix directory to preserve requested basename.
- Input CSV digests checked unchanged after the run. No input CSV, source DOC, ledger, or repository was written.
