# R4 — Fresh-session goal: named consumer readback per W0 main work package

Round: FHS_HERMES_023_NATIVE_INTEGRATION_20261110 (read-only audit of W0 evidence)
Question: for which of the six W0 main WPs (00, 01, 15, 16, 19, 21) does a **named consumer readback** exist?
Definition used: a downstream/original consumer actually consumed the producer's output and left evidence —
a re-hashed digest, a re-sliced source span, or a typed ACCEPT/NACK. File existence or a self-reported
`PASS` does not count. Nothing outside this file was written.

Contract source for the per-WP consumer:
`C:\Projects\Agent_Workspace\FHS_W1_Work_Final\FHS_W1_Work_Final\sources\11_WORKPACKAGES_AND_DAG(4).md`,
line `- **EvidenceExpectation**: ... Reader=<name>` of each WP card.

## 1) Verdict table

| WP | consumer named in the contract | readback evidence found (path + field) | verdict |
|---|---|---|---|
| **WP-FHS-00** | 原 TPM/PIPD Source Reader — `11_WORKPACKAGES_AND_DAG(4).md:29` (`Reader=原 TPM/PIPD Source Reader`) | **Yes, by downstream WPs.** `WP01/AUTHORITY_CONFLICT_LEDGER.json` → `measurement.manifest_rows_parsed=31`, `sha_match=31`, and its `declared_vs_observed[0..30].observed_sha256` re-derive 31/31 from disk when I recomputed them (`declared_sha256=bd9c1a85…` for `SBL_PIPD-LS-PKG_DOC-00(1).md`). Also `WP15/specs/product_SPEC.json` (52/52 spans, `verify_spans.py` reproduced `TOTAL 52/52 PASS`) and `WP16/tables/DONOR24.json` (52/52 `quoted_text` byte-slices reproduce; `raw/verify_projection.log: checks passed 13/13`). Reader layer: `receipts/reader/WP-FHS-00.signed.json` → `body.clauses[0..7]`, 8 clauses, `sig=OK PASS`. | **ACCEPT** |
| **WP-FHS-01** | PIPD compile-pi — `11_WORKPACKAGES_AND_DAG(4).md:45` (`Reader=PIPD compile-pi`) | **No.** No artifact anywhere cites `PROFILE_ORACLE_BINDING.json`'s digest `6d60f80e…`: `grep -rl 6d60f80e` over `receipts/` + `lanes/` = **0 files**, and over `WP21/**` = **NONE** (this confirms `WIRING_CONSUMPTION.json:edge E36.consumption_evidence.plan_cites_binding=false`, `verdict=PARTIAL`). The only ACK is `receipts/reader/WP-FHS-01.signed.json` → `body.OriginalConsumer="SBL Original Source/Requirement/Corpus Semantic Reader"` with 5 clauses — not compile-pi, and it binds the shared *candidate* (`CandidateSHA=f69677fc…`), not the ledger. | **NONE** |
| **WP-FHS-15** | 原 PIPD Intake — `11_WORKPACKAGES_AND_DAG(4).md:281` (`Reader=原 PIPD Intake`) | **No.** Downstream is WP-07 in W1 and the effect never ran: `WIRING_CONSUMPTION.json:later_wave[E12].hold_code="W1_PLAN_EFFECT_NOT_RUN"`, `verdict="HANDOFF_READY_EFFECT_HELD"`. WP itself disclaims: `WP15/REPORT.json:not_claimed[0]="ORIGINAL_ACK（三份 SPEC 均無 Original Reader 讀回）"` and `status_note="…不代表原 Reader 已讀回"`. Reader layer: `receipts/reader/WP-FHS-15.signed.json` 12 clauses, `citation_density="SUFFICIENT"`, `sig=OK PASS` — shared consumer again, binds r15 not the SPECs. | **NONE** |
| **WP-FHS-16** | 原 TPM/PIPD/HGK 各受影 Consumer — `11_WORKPACKAGES_AND_DAG(4).md:297` | **No.** Downstream WP-20 is W1 and held: `WIRING_CONSUMPTION.json:later_wave[E35].hold_code="W1_HOST_MATRIX_NOT_RUN"`. Only ACK is `receipts/reader/WP-FHS-16.signed.json` (4 clauses, `OriginalConsumer="SBL Original Source/Requirement/Corpus Semantic Reader"`); `WP16/REPORT.json:claim_ceiling="AUTHOR_SIDE_PROJECTION_CANDIDATE"`. | **NONE** |
| **WP-FHS-19** | 原 release-readiness Reader — `11_WORKPACKAGES_AND_DAG(4).md:345` | **No.** Downstream WP-14 is W4 and held: `WIRING_CONSUMPTION.json:later_wave[E26].hold_code="W4_RELEASE_EFFECT_NOT_RUN"`. WP itself holds: `WP19/REPORT.json:holds[0].id="HOLD_ORIGINAL_CI_READER"` ("不是 original CI reader ACK"). No WP19 artifact cites `49c65214…`/`SOURCE_LOCK` (`grep` over `WP19/**` = NONE), matching `edge E33.consumption_evidence.scan_cites_source_manifest_digest=false`, `verdict=PARTIAL`. Reader ACK `receipts/reader/WP-FHS-19.signed.json` has only 2 clauses and `citation_density="UNDER_CITED"`. | **NONE** |
| **WP-FHS-21** | 原 Protected AO Request Reader — `11_WORKPACKAGES_AND_DAG(4).md:377` | **No.** Downstream WP-09 is W2 and held: `WIRING_CONSUMPTION.json:later_wave[E16].hold_code="W2_PROTECTED_RUN_NOT_QUALIFIED"`. `WP21/REPORT.json:holds[0].id="ORACLE_RUNNER_BIND_HOLD"`, `not_claimed[0]="不是 protected-checker verdict，未經任何原 Checker 讀取或簽發"`. Reader ACK `receipts/reader/WP-FHS-21.signed.json` has **1** clause and `citation_density="UNDER_CITED"`. | **NONE** |

Supporting facts that apply to the whole column "readback evidence":

- **The six reader receipts are real and verify.** Ran the round's own reader unmodified:
  `6/6 receipts verified`, `EXIT=0`, every line `sig=OK PASS` (`WP-FHS-00|01|15|16|19|21.signed.json`).
  So the reader layer is *not* the gap; the gap is **whose** output and **which** consumer.
- **No receipt binds any WP artifact.** `grep -rl` for the seven WP output digests
  (`49c65214`, `c9160ec3`, `6d60f80e`, `13e64bf4`, `ae17b9fa`, `6878c368`, `8b6789c3`) across
  `FHS_W0_R13_ACCEPTANCE_20261108\receipts\` and `...\lanes\` returns **0 files for all seven**.
  All six receipts instead bind the one shared candidate
  `writeback/W0/FHS_PIPD-LS-PKG_W0_r15.md` (`CandidateSHA=f69677fc…`, on-disk hash reproduced) and the
  L1 blueprint (`SourceSHA=cbdd75fd…`). That is a readback of the W0 candidate document, not of
  `WP00/raw/SOURCE_LOCK.json`, `WP15/specs/*.json`, `WP16/tables/DONOR24.json`, the WP19 inventories, or
  `WP21/tables/ORACLE96.json`.
- **One consumer name serves all six.** Every receipt's `body.OriginalConsumer` is the identical string
  `"SBL Original Source/Requirement/Corpus Semantic Reader"`, so it matches the contract's per-card reader
  for none of 01/15/16/19/21 and only by family for 00 (label drift, recorded verbatim above).
- **No typed NACK exists** for any WP: `lanes/DISAGREEMENT_REGISTER.json.disagreements=[]` and all six
  `receipts[].open_properties=0, issuable=true`. So the NONE verdicts are "no readback", not "rejected".

Wiring rows of `FHS_HERMES_023_NATIVE_INTEGRATION_20261110\evidence\WIRING_CONSUMPTION.json` that I
re-checked myself, against the artifacts rather than the file's own claims:
`E01` producer+consumer sha256 (`49c65214…`, `c9160ec3…`) and `E27` producer+consumer sha256
(`13e64bf4…`) both reproduce byte-for-byte; `E01`'s `sha_match=31` re-derives 31/31 from the 31 sources;
`E27`'s `spans_verified=52` reproduces as `TOTAL 52/52 PASS` by running `WP15/tools/verify_spans.py`;
`E28`'s `checks_passed=13` reproduces (`verify_projection.log`), though its `note` says "49 source_refs"
while `DONOR24.json` holds **52** byte-span refs, all 52 re-slicing correctly — the note's number is low,
the verdict is not affected; `E33.scan_cites_source_manifest_digest=false` and
`E36.plan_cites_binding=false` both reproduce (grep = NONE).

## 2) What "readback" forced me to check that a file-existence check would have missed

A file-existence check would have opened `receipts/reader/`, seen six `.signed.json` files that parse, and
reported 6/6. Getting to an honest answer required five things that existence cannot tell you. First,
identity: the same receipts carry three different candidate digests in different places —
`body.CandidateSHA=f69677fc…` (resolves to `writeback/W0/FHS_PIPD-LS-PKG_W0_r15.md`, hash confirmed),
`binding.candidate_sha256=421617aa…` (resolves to `r20`), and `W0-RCPT`-era `60ba757b…` (resolves to
`r13`) — so "the candidate" had to be resolved to bytes before any span could be judged, and the only
version that both exists and matches the ACKed body is r15. Second, the spans: the locators `WP-FHS-xx:L1:<n>`
are coordinates into the L1 blueprint, which `lanes/CLAUSES.json.source` resolves to
`C:\Users\user\AppData\Local\Temp\bp_r4\L1.md` — a `%TEMP%` witness whose digest happens to still equal
`cbdd75fd…`; re-slicing all 32 clauses byte-exactly (32/32 against `clause_sha256`) and re-deriving all 32
`cited_from.candidate_line_sha256` from r15 line bytes (32/32) is what makes the ACKs evidence rather than
decoration. Third, direction: the clauses are **source** lines being checked for preservation in the
candidate, so passing them proves the reader read L1 and the candidate, not that anyone read
`WP15/specs/product_SPEC.json`; the seven-digest grep (0 hits) is what flips "six readbacks exist" into
"zero readbacks bind a WP output". Fourth, the consumer's name: all six ACKs name one shared SBL corpus
reader, so the contract's per-WP readers (compile-pi, Intake, release-readiness, Protected AO Request,
TPM/PIPD/HGK consumers) each still have no readback — invisible to a file count. Fifth, the tool itself:
`python tools/verify_reader_ack.py` first printed `0/6 receipts verified` with
`SIGNATURE_INVALID … No module named 'cryptography'`; that is a missing-dependency artifact, not a
signature failure, and it only became `6/6 PASS` after switching to an interpreter that has
`cryptography` (3.12.13 / 50.0.2) — a check that trusts its first green *or* its first red light would have
published the wrong verdict.

## 3) Commands run (verbatim)

```bash
# inventory of the three evidence roots
ls -la "C:/Projects/Agent_Workspace/FHS_W0_R6_20261108/evidence/"
ls -la "C:/Projects/Agent_Workspace/FHS_W0_R13_ACCEPTANCE_20261108/"
ls -la "C:/Projects/Agent_Workspace/FHS_HERMES_023_NATIVE_INTEGRATION_20261110/evidence/"
find lanes -maxdepth 2 -type f; find receipts -type f

# contract: what consumer each WP card names
cd "C:/Projects/Agent_Workspace/FHS_W1_Work_Final/FHS_W1_Work_Final/sources"
grep -n "WP-FHS-0[01]\|WP-FHS-1[569]\|WP-FHS-21" "11_WORKPACKAGES_AND_DAG(4).md"

# hashes of the wiring rows I re-checked (E01, E27, E28, E33, E36)
cd "C:/Projects/Agent_Workspace/FHS_W0_R6_20261108/evidence"
sha256sum WP00/raw/SOURCE_LOCK.json WP01/AUTHORITY_CONFLICT_LEDGER.json WP01/PROFILE_ORACLE_BINDING.json \
          WP15/specs/product_SPEC.json WP16/tables/DONOR24.json WP19/SCAN_SUMMARY.json WP21/REPORT.json
stat -c '%s %n' WP00/raw/SOURCE_LOCK.json WP01/AUTHORITY_CONFLICT_LEDGER.json WP15/specs/product_SPEC.json \
          WP16/tables/DONOR24.json WP19/SCAN_SUMMARY.json WP21/REPORT.json

# candidate resolution + clause re-slice (python 3.14.9, heredoc)
cd "C:/Projects/Agent_Workspace/FHS_W0_R13_ACCEPTANCE_20261108"
sha256sum writeback/W0/FHS_PIPD-LS-PKG_W0_r{13,14,15,16,17,18,19,20,24,25,26}.md
ls -la "$LOCALAPPDATA/Temp/bp_r4/"; sha256sum "$LOCALAPPDATA/Temp/bp_r4/L1.md"
# -> 32/32 clause_sha256 re-slice OK; 32/32 candidate_line_sha256 reproduce from r15

# provenance of the locator namespace and of the candidate per receipt
#   lanes/CLAUSES.json  -> candidate=r15 f69677fc…, source=%TEMP%\bp_r4\L1.md cbdd75fd…
#   lanes/DISAGREEMENT_REGISTER.json -> disagreements=[], six receipts issuable=true
#   lanes/POSTREPAIR_VERDICT.json    -> no NACK, two clauses re-affirmed true

# the round's own reader, unmodified (first run: missing dependency, NOT a signature failure)
python tools/verify_reader_ack.py
#   -> 0/6, sig=BAD ModuleNotFoundError: No module named 'cryptography'
"C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe" tools/verify_reader_ack.py
#   -> 6/6 receipts verified, EXIT=0, each line sig=OK PASS

# the consumer's own span verifier, unmodified (E27 reproduction; script only reads)
cd "C:/Projects/Agent_Workspace/FHS_W0_R6_20261108/evidence/WP15"
python tools/verify_spans.py     # -> TOTAL 52/52 PASS, RESULT PASS, exit 0

# does any receipt/lane promote a WP's own output digest?
cd "C:/Projects/Agent_Workspace"
for h in 49c65214 c9160ec3 6d60f80e 13e64bf4 ae17b9fa 6878c368 8b6789c3; do
  grep -rl "$h" FHS_W0_R13_ACCEPTANCE_20261108/receipts FHS_W0_R13_ACCEPTANCE_20261108/lanes --include=*.json
done      # -> 0 files for all seven

# E01 / E28 / E33 / E36 independent re-derivation (python heredocs)
#   E01: 31/31 ledger rows reproduce from disk (declared_sha256 == observed_sha256 == recomputed)
#   E28: 52/52 DONOR24 quoted_text byte-slices reproduce; verify_projection.log "checks passed 13/13"
#   E33: grep 49c65214|SOURCE_LOCK over WP19/** -> NONE
#   E36: grep 6d60f80e|PROFILE_ORACLE_BINDING over WP21/** -> NONE
```

`__pycache__` under `.../tools/` exists from the verifier import; no governed artifact, receipt, lane file
or repo was modified, and no install, no network call, no GitHub call was made. The only file written by
this session is this report.
