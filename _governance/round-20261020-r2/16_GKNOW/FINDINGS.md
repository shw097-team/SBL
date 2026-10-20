# G-KNOW over the SBL corpus — build and probe report

Round: `round-20261020-r2` / artifact `16_GKNOW`
Corpus (read-only): `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL`
Tool reused: `C:/Projects/Agent_Workspace/SBL/sbl_core/gknow.py` (not copied, not modified)

## 1. What was built, and how

`index.json` is produced by **calling the existing product API** `sbl_core.gknow.build_index(corpus_root, out_path)`
verbatim, then adding metadata in a separate step (`scripts/enrich_index.py`). No gknow chunking, scoring or code was
re-implemented or copied; `gknow.query()` reads the delivered file unmodified because the schema string is still
`SBL-GKNOW-INDEX/1` and the `chunks[].text` field is untouched.

Exact command (also recorded inside `index.json` as `build_command`, and in `RUNS/02_build_and_enrich.txt`):

```
"C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe" scripts/enrich_index.py \
  --corpus "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL" \
  --out "C:/Projects/Agent_Workspace/SBL/_governance/round-20261020-r2/16_GKNOW"
```

Enrichment adds, per chunk: `path_rel` (relative to corpus root), `file_sha256` (whole-file hash),
`heading` / `heading_line` (entry heading at chunk start), `headings_within_chunk`, `anchor`, `locator`,
`start`/`end`, `chunk_sha256` (hash of the chunk text as gknow computed it).

## 2. Coverage actually achieved

| measure | value |
|---|---|
| files in corpus (all types) | 306 |
| files considered by `gknow.SUFFIXES` = `('.md','.json')` | 291 |
| **files indexed** | **227** |
| files skipped | 64 |
| chunks | **23174** (40 non-blank lines each) |
| chunk text bytes carried in `index.json` | 127,820,379 |
| files that failed strict UTF-8 decode | 0 |
| files containing U+FFFD after `errors="replace"` | 0 |

15 corpus files are outside the suffix filter and were never candidates: 10 `.csv`, 2 `.sha256`, 2 `.lnk`, 1 `.txt`.
There are no `.json` files in the corpus at all, so the index is markdown-only.

### 2.1 Skips are not benign — the two causes

**Cause A — size cap (3 files).** `gknow.MAX_FILE_BYTES = 2 MiB`:

- `SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-05.md` — 2,382,349 bytes
- `參考工程資料庫/PIPD-LS/PIPD-LS-SP_skeleton.md` — 16,078,915 bytes
- `參考工程資料庫/SKILLS_PLUGIN/SDLC_PRW_HLPE_SKILLS_PLUGIN_R2.md` — 4,708,011 bytes

**DOC-05 is one of the 14 authoritative design books and it has zero retrievable chunks.** 13 of 14 books are
indexed; any question whose answer lives in DOC-05 is unanswerable from this index, and the index does not know
that — see probe P9 in §3.

**Cause B — path length (61 files).** All 61 are under `參考工程資料庫/GPTs_GENIEMAKER_設計實作/…` with absolute path
length 261–305 characters. `os.path.getsize` fails with `WinError 3`; the same file opens with a `\\?\` extended-length
prefix (verified in `RUNS/07_coverage_check.txt`: plain `FAIL`, extended `size 96756`). `build_index` catches the
`OSError`, increments `files_skipped`, and emits **no per-file record**, so this loss is silent in the product API.
The full list is preserved in `index.json.files_skipped_os_error` and `RUNS/coverage_report.json`.

Combined: **227/306 = 74.2 % of files, and 227/291 = 78.0 % of suffix-eligible files**, are in the index. The 61
unopened files also have **unverified encodings** — they were never read, so "0 undecodable" only covers the 227 files
that were actually opened.

## 3. Probes (`probes.json`)

17 probes, **13 pass / 4 fail**. Positive expectations are derived from the corpus file itself (anchor line →
enclosing heading computed by `scripts/run_probes.py` from the file, not from the index), so a probe can fail.
The 9 positives use anchors that occur exactly once in the indexed corpus; a passing positive therefore means the
retrieval landed on the unique chunk that contains the anchor, not merely "some chunk from the right book".

| # | query | expected | actual | result |
|---|---|---|---|---|
| P1 | `FullScanLocatorIndex openapis` | DOC-11, heading @4391 | `DOC-11.md#L4384-4426` score 1.0 | pass |
| P2 | `AcceptancePredicateMatrix AffectedHost` | DOC-07 | `DOC-07.md#L1490-1537` | pass |
| P3 | `AppendOnlyEventEnvelope domainowner` | DOC-09 | `DOC-09.md#L1605-1648` | pass |
| P4 | `AntiCorrelationMatrix joinintegrityvalidator` | DOC-04 | `DOC-04.md#L761-816` | pass |
| P5 | `ArchitectureConstructionEnvelope searchbeforebuildadmission` | DOC-11 | `DOC-11.md#L3867-3911` | pass |
| P6 | `AdmissionDecisionReadAck requirementtraceack` | DOC-03 | `DOC-03.md#L4423-4467` | pass |
| P7 | `AtomMutationBundle rowcount` | DOC-08 | `DOC-08.md#L5701-5743` | pass |
| P8 | `AliasDecision roleroutematrix` | DOC-13 | `DOC-13.md#L3008-3052` | pass |
| P9 | `NATIVE_PERMISSION_DENIED` | DOC-05 (2.38 MB, skipped) | `DOC-00.md#L1418-1467` score 1.0 | **FAIL** — wrong locator, not a refusal |

Negatives:

| # | query | expected | actual | result |
|---|---|---|---|---|
| N1 | `""` | refusal | `SBL_E_KNOWLEDGE_NO_ANSWER` ("no searchable tokens") | pass |
| N2 | `量子退火稀釋冷凍機的低溫恆溫器` | refusal | same code ("no searchable tokens") | pass |
| N3 | `dilution refrigerator cryostat helium` | refusal | same code (below `min_score`) | pass |
| N4 | `thylakoid chlorophyll photosynthesis` | refusal | same code | pass |
| N5 | `sourdough starter hydration baker` | refusal | same code | pass |
| N6 | `SBL_PIPD-LS-PKG_DOC-27 v2099.12.31` | refusal | **answered**, `DOC-00.md#L1158-1197` score 0.889 | **FAIL — false accept** |
| N7 | `SBL_PIPD-LS-PKG_DOC-99 phantom artifact` | refusal | **answered**, `DOC-07.md#L2675-2714` score 0.875 | **FAIL — false accept** |
| N8 | `SBL Writer may issue Native Effect without HGK approval` | refusal | **answered**, `DOC-06.md#L2658-2711` score 1.000 | **FAIL — false accept** |

The four failures are the substance of this report, not noise.

## 4. What this index cannot do (specific)

1. **It cannot bind identity or version.** Score is `|query ∩ chunk tokens| / |query tokens|`. `SBL_PIPD-LS-PKG_DOC-27`
   tokenizes to `{sbl, pipd, ls, pkg, doc, 27}`; five of six are in thousands of chunks, so the fabricated document
   number scores ≥ 0.83 and is *answered* (N6, N7). A document that does not exist retrieves a real locator with full
   confidence. **Any locator this index returns must be re-checked against the file before being cited.**
2. **It cannot detect contradiction.** The scorer is set overlap with no polarity: a claim the corpus denies scores
   1.0 whenever its words appear in a denial paragraph (N8 returns a DOC-06 chunk). Retrieval is not entailment and
   must not be used as an oracle for "does the corpus assert X".
3. **Chinese content is invisible.** `TOKEN_RE = [a-z0-9]+` yields **zero** tokens for pure CJK text, so any zh-TW query
   is unconditionally refused (N2) — this is a refusal by accident, not judgement. Because the corpus is overwhelmingly
   zh-TW, the reachable surface is essentially the embedded ASCII identifiers, field names and hashes. There is no
   semantic, stemming, synonym or cross-lingual retrieval here.
4. **Recall is a hard threshold on the whole query.** `min_score=0.34` with no IDF means every token counts equally and
   any query whose absent tokens exceed two-thirds is dropped, even if the matching third is the decisive phrase.
   Conversely a chunk that matches only ubiquitous words (`sbl`, `doc`, `the`) at ≥ 0.34 is returned as a hit. Verbose
   natural-language questions are systematically disadvantaged versus 2–3 token identifier queries.
5. **Chunk boundaries are fixed and non-overlapping** (40 non-blank lines). A statement split across the boundary is
   retrievable only if one half independently clears the threshold; there is no sliding window, no parent-section
   expansion, no neighbour stitching. A chunk that starts mid-section also inherits a stale entry `heading` — three
   probes (P1–P4 in the first run) initially "failed" on heading until `headings_within_chunk` exposed the section
   boundary inside the chunk. Locator line ranges are correct; the single `heading` field is granularity-limited.
6. **No diversity control.** The corpus repeats tables thousands of times (e.g. `INDEXED_NOT_SEMANTICALLY_ADJUDICATED`
   appears on 519 lines of DOC-11; `NATIVE_PERMISSION_DENIED` on 1217 lines of DOC-05). `top_k=5` can return five
   near-duplicate rows of the same table; ties at equal score are broken by locator string, not by usefulness.
7. **Operationally heavy, not incremental.** Full chunk text is stored (128 MB), each `query()` call re-reads and
   re-tokenizes the entire index: **~4.6 s per query** measured cold (`RUNS/summary.json`). Any corpus change requires a
   full rebuild; nothing re-verifies `file_sha256` at query time, so drift between build and use is undetectable from
   the index alone.
8. **Coverage gaps are invisible to the caller** (DOC-05, 61 long-path files). A refusal would at least be honest; P9
   shows the index instead answering from a different book. Until coverage is complete or gaps are declared, a locator
   here is evidence of retrieval, not of corpus-wide absence.

## 5. What it is actually good for

Exact ASCII identifier lookup. All 8 identifier probes that are inside the index returned the unique chunk at score
1.0, with file, line range and chunk hash — that is enough to cite `DOC-11.md#L4384-4426` instead of re-reading a
1.8 MB book. For SBL rounds this covers the common case "where is `X` defined?", not "what does SBL say about Y?".

## 6. Reproduction

```
RUNS/01_gknow_api_surface.txt   API surface + constants (schema, CHUNK_LINES, MAX_FILE_BYTES, SUFFIXES)
RUNS/02_build_and_enrich.txt    build_index summary + enrichment result (227 files / 23174 chunks)
RUNS/03_anchor_discovery.json   identifier scan over the 14 DOC books
RUNS/04_rare_tokens.json        chunk-support scan (anchor uniqueness)
RUNS/05_probe_candidates.json   candidate probe + negative sweep (pre-selection)
RUNS/06_probes_stdout.txt       final probe run, per-probe verdicts
RUNS/07_coverage_check.txt      coverage accounting + MAX_PATH hypothesis test
RUNS/08_summary.txt             final summary
RUNS/09_stage_removal.txt       sha256 + size of the deleted raw build_index output
RUNS/coverage_report.json       per-file chunk counts, skip lists
RUNS/summary.json               sha256 of index.json and probes.json, pass/fail counts
```

Regenerate end to end (order matters; `--out` must be the 16_GKNOW directory):

```
python scripts/enrich_index.py --corpus "<corpus root>" --out "<16_GKNOW>"
python scripts/run_probes.py
python scripts/summarize.py
```

`RUNS/stage_gknow_raw.json` (the untouched `build_index` output, ~123 MB) is deleted after enrichment to keep the
artifact lean; its summary line is preserved in `RUNS/02_build_and_enrich.txt`.
