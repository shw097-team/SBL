# R14-TS23 — eighth independent review

**Verdict: FAIL.** The installed modules are the reviewed sources, but the suite still accepts wrong programs and the mutation instrument can still return a false green.

## What is verified

- All three `ts23_src/*.py` files are byte-identical to their generated package and **actually imported installed module**. Imports were executed with `PYTHONPATH` removed; SHA256 was recomputed from runtime module paths. There is no stale-source substitution in this snapshot.
- The builder reads these sources at line 164 and writes them at line 185. Its three test literals also exactly match the generated test files. All recorded build source/installed file digests recompute correctly.
- All three baseline suites pass against the actual installed modules and restored scratch copies.
- Independent replay of the current maker list returns exit 0, 27 rows and all five flags true. This confirms that bounded receipt, not its coverage or all-fixed interpretation.

| Source | Reviewed = generated = installed SHA256 |
|---|---|
| CLI_TOOL | `a5c643d9dea9782d0d54030e4540335d896e009c96ee5dbfd7d664f562b142ed` |
| AGENT_SKILL | `2928fce9da16a60b43280016f110320086846f3bf0e65b356f6d2d349a1f9778` |
| SIMPLE_AGENT | `a6576fbb92174c564e768474a3cdc79eb5a016d48188e8f5b96707a72d3e6c45` |

## Round-7 closure

| Round-7 item | Experimental result |
|---|---|
| N01 binary UTF-8 decoding | Suite now rejects the exact decode/encode mutation, but via child UnicodeDecodeError and parent JSONDecodeError, not a value assertion. Maker's read_text mutation fails earlier on CRLF translation. |
| N02/N03 census exit 7 / stdout on error | Both wrong answers rejected. |
| N04 tab separator | Rejected. |
| N07 internal double-space collapse | Exact prior behaviour rejected. Internal **tab** collapse remains a new survivor. |
| N09/N10 heading undecodable crash / exit 7 | Both rejected. |
| N14 nonempty exhausted queue reports BUDGET | Exact nonempty-only mutation rejected on the new max-steps 20 run. |
| N15 unreadable entry skipped | Rejected. |
| N16 nonarray acceptance | **Class not closed:** coercing objects to arrays passes; `{}` incorrectly becomes a successful empty review. The `{ "a": 1 }` fixture can error for unreadable path `a` instead of invalid queue type. |
| N17 queue exit 7 | Rejected. |
| N19 NFKD | Exact return-list normalization rejected using the compatibility character. |
| N20 missing separator | Isolated optional-separator mutation rejected. |
| N21 identical-byte input rewrite | **Still survives.** Hash equality does not establish absence of writes. Independent file mtime changed from the deliberately old timestamp. |
| Empty heading | Acceptance mutation rejected. |
| C03/C04 empty-queue fatal exit, with/without JSON | Specific cases fixed: both report caught=false, crash_not_evidence=true, main exit 1. The general missing-invocation defect remains. |
| G01 trimming wording | Corrected to explicitly trim ends while preserving internal whitespace. |
| G02 budget domain | N=3 works now; negative/zero domain and equality precedence remain unpinned. |
| G03 bundle/output/path | **Not closed; remediation claim refuted.** SCOPE never mentions SKILL.md, a bundle, or resolved-path semantics. |
| G04 fixture preconditions | Level-six guard fixed. CRLF→lone-CR and terminators-only→empty still pass their shape guards and fail only after invoking the program. |
| G05 instrument | Empty cases fixed, max-steps 20 fatal exit falsely accepted. |
| G06 counts/claims | 27 claimed equals 27 executed. Broader every-invocation/all-fixed claims remain false. |
| G07 whitespace definitions | Empty-text rule fixed; closing-sequence Unicode-whitespace domain remains undefined. Baseline retains NBSP before closing hashes. |
| G08 mixed exclusions | Fence behaviour now guarded; heading BOM stripping still passes despite the positive no-stripping sentence in the exclusion list. |

## Surviving program mutations

1. **R7_N21_REWRITE_OBSERVED:** `path.write_bytes(data)` immediately after reading. Test exit 0; independent mtime proves a rewrite with unchanged bytes.
2. **R7_N16_EMPTY_OBJECT_ACCEPTED:** replace the main nonarray ValueError with `queue = list(queue)`. Test exit 0; `{}` returns steps 0 and QUEUE_EXHAUSTED instead of exit 2.
3. **NEW_INTERNAL_TAB_COLLAPSE:** append `.replace("\t", " ")` to body processing. Test exit 0; `## A<TAB>B` returns `A B`, violating preserved internal whitespace.
4. **NEW_THIRD_REVIEW_DIGEST:** hash only entries with index < 2; return 64 zeroes otherwise. Test exit 0, including max-steps 20; the third review's digest is false. The new exhausted-run assertions check counts/halt but not every entry.
5. **SCOPE_CLOSING_TAB:** restrict the closing sequence regex from space-or-tab to space only. Test exit 0; `## Title<TAB>##` retains the closing hashes, contradicting SCOPE32–33's whitespace wording.
6. **NEW_CENSUS_TRACEBACK_STDERR:** call `traceback.print_exc()` on the caught OSError. Test exit 0 despite an actual traceback; expected exit 2, ERR_INPUT and empty stdout remain intact.
7. **R7_O01_BOM_STRIPPED_DIRECT:** strip heading BOM before parsing. Test exit 0; BOM-prefixed `# Hidden` becomes visible. This is classified separately as an **unguarded positive promise inside ambiguous exclusion wording**, not an unconditional full-Markdown requirement.

The tab-content and third-entry mutations are distinct from the earlier separator-tab and all-entry fake-digest mutations. Available prior-review JSON and the maker list contain no matching attempts; undisclosed history cannot be ruled out.

## Four named residuals attacked

- **Negative --max-steps:** baseline -1/0 over three files returns steps 0, remaining 3, BUDGET; the empty queue returns QUEUE_EXHAUSTED. A mutation changing negative limits to default 2 still passes. This proves an unpinned boundary, not a uniquely determined contract violation: SCOPE specifies neither rejection nor clamping.
- **Bundle/SKILL.md:** deleting the resource fails with FileNotFoundError; changing its name fails an exact-string assertion. Both are undeclared conformance gates. Contrary to remediation7, the current SCOPE does not even contain the allegedly minimal installed-SKILL.md sentence. Resolved output paths are likewise asserted but not specified.
- **Crash heuristic:** emit the valid JSON value `halt_reason: "ValueError"` instead of BUDGET. All probes answer; the suite gives the legitimate assertion **`'ValueError' != 'BUDGET'`**. Actual harness main marks caught=false and returns 1 solely because the assertion's value contains an exception name. This is a false negative in the instrument, not a suite survivor.
- **No-op mutation:** remove just the duplicate main queue-type guard. The callable's remaining guard still rejects the tested nonarray, so this is not a functional hole. Actual main prints SURVIVED and returns 1. Even original==replacement reports applied=true and SURVIVED. Equivalent/no-change mutations need a separate disposition; do not relabel them as missing coverage.

## Instrument false acceptance

Inject `os._exit(3)` only when `max_steps == 20`. The generated suite fails its return-code assertion, **`3 != 0`**, without an exception-name token. All three fixed probes answer, so actual harness main records **caught=true, false_red=false, every flag=true, exit 0**. The failure class claimed closed by C03/C04 is therefore still open.

Observed baseline invocations versus harness probes:

| Module | Actual calls | Successful calls | Fixed probes |
|---|---:|---:|---:|
| ts23_newline | 10 | 9 | 1 |
| ts23_headings | 5 | 3 | 1 |
| ts23_review | 6 | 4 | 3 |

A fixed probe list is not “every invocation.” Intended-error calls also need their own expected status and stderr/stdout contract, not a universal exit-0 rule.

## Evidence and ceiling

The JSON embeds substitutions, direct outputs, test failures, probe results, actual-main receipts, digests, fixture perturbations and the per-item closure matrix. It enumerates **54 attempts**: 27 maker replays, 19 additional source attempts (including repeated demonstrations), 6 instrument attacks and 2 bundle-resource attacks. Seven distinct program/wording survivors are listed; no-op and unspecified-negative variants are deliberately excluded from that functional count.

All mutations ran in scratch copies. Subject hashes and restored scratch sources/tests were verified unchanged; only `ts23_review8.json` and `ts23_review8.md` were written under raw. Full builder execution was not repeated because it rewrites the subject; source loading, literal test generation, runtime import binding and digests were independently checked instead. An exploratory tracer argv error was corrected and all affected experiments rerun; no collection-error result is used as evidence.

**Claim ceiling:** source identity and baseline success are established for this snapshot. Exhaustive conformance, complete round-7 closure, sound mutation classification, M2 acceptance and production readiness are not established. PASS conditions are not met.
