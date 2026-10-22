# R14-TS23 — independent review 7

**Verdict: FAIL**

Contract SHA256: `e3af229a40ac81585ecd401a28955578f24e3af29b189f33a561bcce2ecdb994`

49 mutation attempts: 20 maker replays plus 29 additional attempts. **14 clearly in-scope suite survivors**, two additional exclusion/promise ambiguities, and two false catches in the mutation harness. Three original-installed baselines pass; all 20 maker-list replays are honestly detected. The exact review-6 NFKD survivor still passes.

## Rule-by-rule contract audit

| Rule / SCOPE lines | Result | Counterexamples and observations |
|---|---|---|
| N0 / 7 | FAIL | Read-only census. Rewriting every input with identical bytes passes the generated suite; independent stat records changed mtime. No test asserts absence of writes. Attempts: N21_INPUT_REWRITTEN |
| N1 / 9 | FAIL | Exact byte size; bytes never decoded. Exact ordinary-file size is enforced. UTF-8 decode/encode mutation passes; independent ff000a800d input crashes with UnicodeDecodeError rather than reporting five bytes and two terminators. Attempts: maker: census bytes=0, N01_DECODE_BINARY, BINARY_READ |
| N2 / 10-17 | PASS_BOUNDED | Terminator formula, trailing LF, unterminated line, lone CR, LF+CR and terminators-only. All five named wrong formulas fail value assertions while answering. Primary LF fixture ends with LF; a missing-terminator overcount is also rejected. This is a bounded mutation result, not exhaustive proof over byte strings. Attempts: maker: CRLF counted twice, maker: lone CR not counted, maker: unterminated final line counted, maker: LF+CR pair merged, maker: terminators-only reports zero |
| N3 / 18 | PASS_BOUNDED | SHA256 of exact input bytes. Fake digest rejected; unmodified binary-input digest agrees with independently computed exact-byte SHA256. Binary-decode survivor is separately N1. Attempts: maker: census fake digest, BINARY_READ |
| N4 / 19 | FAIL | Missing/unreadable: exit 2, ERR_INPUT stderr, empty stdout. Baseline meets contract; generated tests require only nonzero and ERR_INPUT for missing input. Exit 7 and unexpected stdout both survive; directory unreadability is not tested. Attempts: N02_INPUT_EXIT7, N03_ERROR_STDOUT, NL_MISSING, NL_UNREADABLE_DIRECTORY |
| H1 / 23 | FAIL | Column-zero 1-6 hashes, mandatory space/tab, then text. Tab rejection survives. Unisolated optional-separator mutation is rejected because it also accepts level 7; adding (?!#) isolates mandatory-separator defect and survives. Thus that first red does not establish the separator rule. Empty-text boundary remains ambiguous; see G07. Attempts: N04_TAB_REJECTED, N05_NO_SEPARATOR, N20_NO_SEPARATOR_ISOLATED, HEADING_EDGES |
| H2 / 24 | PASS_BOUNDED | Ignore 7+ hashes without error. Both accepting seven hashes and rejecting six are detected. Fixture contains levels 1-7 today, but its continued presence is not precondition-guarded (P01). Attempts: N06_LEVEL7, maker: level-six headings dropped |
| H3 / 25-26 | PASS_ASCII_ONLY | Strip whitespace-prefixed closing hashes; preserve bare content hash. Both ASCII-space closing/hash counterexamples are rejected; direct tab closing sequence is correctly removed. Scope says whitespace without defining its Unicode domain; NBSP is not removed (G07). Attempts: maker: ATX closing sequence kept, maker: trailing hash stripped without sequence, HEADING_EDGES |
| H4 / 27-28 | FAIL | Keep text exactly, nonASCII and NFD; no Unicode normalization. NonASCII drop and NFC composition are detected. Exact review6 NFKD mutation STILL PASSES, changing composed café to cafe+combining acute on an independent input. Internal-space collapse also survives. Baseline strips trailing content spaces despite exact-text wording (G01). Attempts: N07_INTERNAL_WHITESPACE_COLLAPSED, N18_NONASCII_DROPPED, N19_REVIEW6_EXACT_NFKD, maker: Unicode normalisation, HEADING_EDGES |
| H5 / 29 | PASS_BOUNDED | One-based file line number. Offset mutation is rejected by exact heading list assertions, including blank/body lines. Attempts: N08_LINE_ZERO |
| H6 / 30 | FAIL | Missing/undecodable: exit 2 and ERR_INPUT stderr. Baseline correct; dropping UnicodeError handler and replacing exit 2 with exit 7 both pass tests. Undecodable input is absent from generated suite. Attempts: N09_UNDECODABLE_CRASH, N10_HEADING_EXIT7, HEADING_UNDECODABLE, HEADING_MISSING |
| R1 / 34 | FAIL_CONTRACT_TEST_MISMATCH | JSON path queue order; max-steps N bounds; default 2. Order reversal, ignoring explicit limit, and default 1 rejected. Baseline forbids N=3 despite scope not stating a 1-or-2 domain; test_agent.py:29 requires rejection and fails the mutation which permits N=3 and correctly reviews all three files. Scope must specify its allowed N domain, not inherit test intent. Attempts: N11_QUEUE_ORDER, N12_BUDGET_IGNORED, N13_ALLOW_N3, N23_DEFAULT1, QUEUE_N3 |
| R2 / 35 | PASS_BOUNDED | Per-entry path, exact bytes, exact digest. Existing default and one-step assertions check exact paths, sizes and digests. All corresponding maker mutations are detected. Attempts: maker: agent bytes=0, maker: wrong path, maker: fake digest |
| R3 / 36 | PASS_BOUNDED | Steps number reviewed; remaining queue length minus steps. All named numeric corruptions rejected on the exercised default/limited cases; empty fields also asserted exactly. Attempts: N22_STEPS999, maker: remaining=0, maker: remaining=999 |
| R4 / 37-39 | FAIL | BUDGET vs QUEUE_EXHAUSTED, including empty queue. Empty-queue and truncated-queue cases guarded; nonempty exhausted queue missing. Returning BUDGET for every nonempty queue passes and is wrong on a one-file queue with default budget two. Equality at budget/queue length also lacks an explicit precedence sentence. Attempts: N14_SHORT_QUEUE_BUDGET, maker: empty queue reports BUDGET, maker: QUEUE_EXHAUSTED while budget-limited, QUEUE_SHORT |
| R5 / 40 | FAIL | Unreadable entry or nonarray queue exits 2, no skipping. All three wrong implementations pass suite. {} becomes successful empty review under disabled validation; nonexistent entry is silently skipped; input errors may exit 7 undetected. Baseline handles these correctly. Attempts: N15_SKIP_UNREADABLE, N16_NONARRAY_ACCEPTED, N17_QUEUE_EXIT7, QUEUE_NONARRAY, QUEUE_UNREADABLE |
| O1 / 44-46 | SCOPE_MIXED | Fence/code-block parsing excluded, but fence headings explicitly still reported. Baseline reports fenced heading; a fence-suppressing mutation passes. Full Markdown context parsing can legitimately be excluded, but the positive still-reported sentence conflicts with the blanket no-test-expectation framing. Do not silently use the exclusion to erase the positive statement. Attempts: FENCE, O02_FENCE_SUPPRESSED |
| O2 / 47 | LEGITIMATELY_OUT_OF_SCOPE | Setext excluded. Direct unmodified probe ignores Setext. No requirement to implement full Markdown is imposed; no defect scored for absent Setext support. Attempts: SETEXT |
| O3 / 48 | SCOPE_MIXED | BOM excluded, but counted and not stripped before parsing. Baseline does not strip BOM; a stripping mutation passes. Positive no-stripping promise and no-test-expectation framing should be reconciled; counted bytes already follows universal N1. Attempts: BOM, O01_BOM_STRIPPED |
| O4 / 49-50 | LEGITIMATELY_OUT_OF_SCOPE | Symlinks/devices/changing files; concurrency/retry/caching/nonlocal I/O excluded. No tests or unsupported features demanded for these explicit exclusions. They do not cover invalid UTF8 census, tabs, NFKD, local queue errors, or crash classification. Bytecode-cache correctness of the TEST INSTRUMENT is not excused by application caching exclusion. Attempts: Explicit exclusions; no invented requirements. |
| M1 / 4-5,54-59 | FAIL | Each rule fixture/precondition; build RED/GREEN/location; every invocation probed; only noncrash assertion counts; exit reflects flags. Recorded REDs are output assertions, current recorded source/installed digests match and three installed tests pass; full builder not re-executed under two-output write limit. Level-six fixture removal passes. Harness probes 1/1/2 invocations versus tests 8/3/4 (including intended errors); even successful empty queue is omitted. Limited hard exits now honestly fail harness, but empty-queue hard exits are falsely caught and actual harness main exits 0 with every flag true. Attempts: P01-P08, C01-C04, maker replay, build receipt audit |

## Review-6 closure, experimentally checked

- **LF+CR: CLOSED_BOUNDED** — Maker LFCR subtraction mutant answers but fails new value assertion; P04 CRLF-shape regression fails its precondition.
- **terminators-only: BEHAVIOUR_CLOSED_PRECONDITION_PARTIAL** — Zero-on-only-terminators mutant rejected. P03 empty fixture passes vacuous strips-to-empty guard and fails only later value assertion.
- **Unicode normalisation: NOT_CLOSED** — New NFC mutant caught, but exact prior NFKD mutant N19 passes and changes café to decomposed cafe+acute on independent composed input.
- **bare trailing hash: CLOSED_BOUNDED** — Unconditional trailing-hash stripping rejected; P06 missing tag# trips precondition.
- **hard exit in limited invocation: SPECIFIC_CASE_CLOSED_CLASS_NOT_CLOSED** — C01/C02 caught=false; actual main returns 1 for each. C03/C04 empty-queue hard exits remain false catches, actual C03 main returns 0.
- **fixture preconditions: NOT_CLOSED** — P01 level-six fixture removed and suite passes; P02/P03 wrong fixture shape not rejected by their nominal preconditions. P04-P08 guarded.
- **coverage claims: NOT_CLOSED** — 21 advertised vs 20 automated; missing nonASCII drop; NFKD prior survivor substituted by NFC. Independent N18 drop is caught, but not part of maker automation.

## Every mutation attempt

“Rejected” is not automatically a good catch: N05 fails on collateral level-seven parsing; N13 is a contract-compatible extension rejected by an undeclared constraint. C01/C02 are correctly classified crashes, not behavioural catches. C03/C04 fail the suite but dishonestly earn caught=true. Full substitutions, probe results, stdout/stderr and assertion messages are embedded in the JSON.

| ID | Attempt | Suite / instrument outcome |
|---|---|---|
| MAKER_01 | census reports bytes=0 for a non-empty file | CORRECTLY_REJECTED; {'bytes': 0, 'newlines': 4, 'path': 'C:\\Us[227 chars]051'} != {'path': 'C:\\Users\\user\\AppData\\Local\\[228 chars]051'} |
| MAKER_02 | census reports a fake 64-character digest | CORRECTLY_REJECTED; {'bytes': 28, 'newlines': 4, 'path': 'C:\\U[228 chars]000'} != {'path': 'C:\\Users\\user\\AppData\\Local\\[228 chars]051'} |
| MAKER_03 | headings are fixture constants regardless of the document | CORRECTLY_REJECTED; Lists differ: [{'level': 1, 'line': 1, 'text': 'One'}, {'le[72 chars]ee'}] != [{'line': 1, 'level': 1, 'text': 'Alpha'}, {'[335 chars]ix'}] |
| MAKER_04 | correct headings but a wrong path | CORRECTLY_REJECTED; 'wrong' != 'C:\\Users\\user\\AppData\\Local\\Packages[125 chars]d.md' |
| MAKER_05 | agent reports bytes=0 per file | CORRECTLY_REJECTED; Lists differ: [0, 0] != [5765, 5776] |
| MAKER_06 | agent reports remaining=0 while a file is still queued | CORRECTLY_REJECTED; 0 != 1 |
| MAKER_07 | correct byte counts but a wrong path in the one-step run | CORRECTLY_REJECTED; Lists differ: ['wrong', 'wrong'] != ['C:\\Projects\\Agent_Workspace\\SBL\\READM[94 chars]son'] |
| MAKER_08 | one-step run reports a fake digest | CORRECTLY_REJECTED; Lists differ: ['00000000000000000000000000000000000000000[88 chars]000'] != ['1ae8aaf22407a4657a666054ba3558330f8c9f4df[88 chars]e71'] |
| MAKER_09 | one-step run reports remaining=999 | CORRECTLY_REJECTED; 999 != 1 |
| MAKER_10 | one-step run claims the queue is exhausted | CORRECTLY_REJECTED; 'QUEUE_EXHAUSTED' != 'BUDGET' |
| MAKER_11 | level-six headings are silently dropped | CORRECTLY_REJECTED; Lists differ: [{'level': 1, 'line': 1, 'text': 'Alpha'}, {'[294 chars]on'}] != [{'line': 1, 'level': 1, 'text': 'Alpha'}, {'[335 chars]ix'}] |
| MAKER_12 | CRLF is counted twice | CORRECTLY_REJECTED; 6 != 3 |
| MAKER_13 | a lone CR is not counted as a line terminator | CORRECTLY_REJECTED; 0 != 3 : a lone CR is a line terminator |
| MAKER_14 | an unterminated final line is counted as a newline | CORRECTLY_REJECTED; {'bytes': 0, 'newlines': 1, 'path': 'C:\\Us[232 chars]855'} != {'path': 'C:\\Users\\user\\AppData\\Local\\[232 chars]855'} |
| MAKER_15 | the ATX closing sequence stays in the heading text | CORRECTLY_REJECTED; Lists differ: [{'level': 1, 'line': 1, 'text': 'Alpha'}, {'[338 chars]ix'}] != [{'line': 1, 'level': 1, 'text': 'Alpha'}, {'[335 chars]ix'}] |
| MAKER_16 | an empty queue is reported as budget-limited | CORRECTLY_REJECTED; 'BUDGET' != 'QUEUE_EXHAUSTED' |
| MAKER_17 | an LF+CR pair is merged into one terminator | CORRECTLY_REJECTED; 1 != 2 : LF then CR is two terminators |
| MAKER_18 | a file made only of terminators reports zero | CORRECTLY_REJECTED; 0 != 4 : three terminators plus one more |
| MAKER_19 | heading text is Unicode-normalised instead of kept as-is | CORRECTLY_REJECTED; Lists differ: [{'level': 1, 'line': 1, 'text': 'Alpha'}, {'[334 chars]ix'}] != [{'line': 1, 'level': 1, 'text': 'Alpha'}, {'[335 chars]ix'}] |
| MAKER_20 | a trailing hash is stripped even without a closing sequence | CORRECTLY_REJECTED; Lists differ: [{'level': 1, 'line': 1, 'text': 'Alpha'}, {'[334 chars]ix'}] != [{'line': 1, 'level': 1, 'text': 'Alpha'}, {'[335 chars]ix'}] |
| N01_DECODE_BINARY | N1 bytes never decoded | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N02_INPUT_EXIT7 | N4 missing/unreadable exit exactly 2 | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N03_ERROR_STDOUT | N4 empty stdout on input error | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N04_TAB_REJECTED | H1 tab is valid separator | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N05_NO_SEPARATOR | H1 space/tab required | REJECTED_ON_COLLATERAL_LEVEL7_DEFECT; suite exit 1, harness caught=True; Lists differ: [{'level': 1, 'line': 1, 'text': 'Alpha'}, {'[380 chars]en'}] != [{'line': 1, 'level': 1, 'text': 'Alpha'}, {'[335 chars]ix'}] |
| N06_LEVEL7 | H2 ignore level 7 | CORRECTLY_REJECTED; suite exit 1, harness caught=True; 'Seven' unexpectedly found in ['Alpha', 'Beta', '知識庫 heading', 'Café', 'tag#', 'Gamma', 'Delta', 'Epsilon', 'Six', 'Seven'] |
| N07_INTERNAL_WHITESPACE_COLLAPSED | H4 text kept exactly as written including internal whitespace | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N08_LINE_ZERO | H5 one-based line numbers | CORRECTLY_REJECTED; suite exit 1, harness caught=True; Lists differ: [{'level': 1, 'line': 0, 'text': 'One'}, {'le[72 chars]ee'}] != [{'line': 1, 'level': 1, 'text': 'One'}, {'li[72 chars]ee'}] |
| N09_UNDECODABLE_CRASH | H6 undecodable exits 2 with ERR_INPUT | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N10_HEADING_EXIT7 | H6 missing exits exactly 2 | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N11_QUEUE_ORDER | R1 queue order | CORRECTLY_REJECTED; suite exit 1, harness caught=True; Lists differ: [4353, 5776] != [5765, 5776] |
| N12_BUDGET_IGNORED | R1 explicit --max-steps bound | CORRECTLY_REJECTED; suite exit 1, harness caught=True; 2 != 1 |
| N13_ALLOW_N3 | R1 scope N unrestricted vs test prohibits N3 | REJECTED_CONTRACT_COMPATIBLE_EXTENSION_UNDECLARED_RESTRICTION; suite exit 1, harness caught=True; 0 == 0 |
| N14_SHORT_QUEUE_BUDGET | R4 nonempty exhausted queue | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N15_SKIP_UNREADABLE | R5 unreadable entry must not skip | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N16_NONARRAY_ACCEPTED | R5 reject nonarray queue | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N17_QUEUE_EXIT7 | R5 error exits exactly 2 | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N18_NONASCII_DROPPED | H4 preserve nonASCII | CORRECTLY_REJECTED; suite exit 1, harness caught=True; Lists differ: [{'level': 1, 'line': 1, 'text': 'Alpha'}, {'[245 chars]ix'}] != [{'line': 1, 'level': 1, 'text': 'Alpha'}, {'[335 chars]ix'}] |
| C01_LIMITED_HARD_EXIT | M1 crash must not count as catch | CORRECTLY_CLASSIFIED_CRASH_NOT_CATCH; suite exit 1, harness caught=False; 3 != 0 : |
| C02_LIMITED_BUFFERED_EXIT | M1 crash must not count as catch | CORRECTLY_CLASSIFIED_CRASH_NOT_CATCH; suite exit 1, harness caught=False; 3 != 0 : |
| C03_EMPTY_HARD_EXIT | M1 crash must not count as catch | FALSE_CATCH_IN_HARNESS; suite exit 1, harness caught=True; 3 != 0 : |
| C04_EMPTY_BUFFERED_EXIT | M1 crash must not count as catch | FALSE_CATCH_IN_HARNESS; suite exit 1, harness caught=True; 3 != 0 : |
| N19_REVIEW6_EXACT_NFKD | H4 no Unicode normalisation; exact review-6 survivor | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N20_NO_SEPARATOR_ISOLATED | H1 mandatory separator; retains H2 seven-hash rejection | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| O01_BOM_STRIPPED | O3 excluded BOM but positive no-stripping sentence | SURVIVED_EXCLUSION_WITH_POSITIVE_PROMISE_AMBIGUITY; suite exit 0, harness caught=False |
| O02_FENCE_SUPPRESSED | O1 excluded fence parsing but positive still-reported sentence | SURVIVED_EXCLUSION_WITH_POSITIVE_PROMISE_AMBIGUITY; suite exit 0, harness caught=False |
| N21_INPUT_REWRITTEN | N0 read-only census | SURVIVED_IN_SCOPE; suite exit 0, harness caught=False |
| N22_STEPS999 | R3 steps is number reviewed | CORRECTLY_REJECTED; suite exit 1, harness caught=True; 999 != 2 |
| N23_DEFAULT1 | R1 default limit 2 | CORRECTLY_REJECTED; suite exit 1, harness caught=True; 1 != 2 |

## In-scope survivors

- **N01_DECODE_BINARY** — N1 bytes never decoded; generated suite exits 0. Independent counterexample is captured in JSON.
- **N02_INPUT_EXIT7** — N4 missing/unreadable exit exactly 2; generated suite exits 0. Independent counterexample is captured in JSON.
- **N03_ERROR_STDOUT** — N4 empty stdout on input error; generated suite exits 0. Independent counterexample is captured in JSON.
- **N04_TAB_REJECTED** — H1 tab is valid separator; generated suite exits 0. Independent counterexample is captured in JSON.
- **N07_INTERNAL_WHITESPACE_COLLAPSED** — H4 text kept exactly as written including internal whitespace; generated suite exits 0. Independent counterexample is captured in JSON.
- **N09_UNDECODABLE_CRASH** — H6 undecodable exits 2 with ERR_INPUT; generated suite exits 0. Independent counterexample is captured in JSON.
- **N10_HEADING_EXIT7** — H6 missing exits exactly 2; generated suite exits 0. Independent counterexample is captured in JSON.
- **N14_SHORT_QUEUE_BUDGET** — R4 nonempty exhausted queue; generated suite exits 0. Independent counterexample is captured in JSON.
- **N15_SKIP_UNREADABLE** — R5 unreadable entry must not skip; generated suite exits 0. Independent counterexample is captured in JSON.
- **N16_NONARRAY_ACCEPTED** — R5 reject nonarray queue; generated suite exits 0. Independent counterexample is captured in JSON.
- **N17_QUEUE_EXIT7** — R5 error exits exactly 2; generated suite exits 0. Independent counterexample is captured in JSON.
- **N19_REVIEW6_EXACT_NFKD** — H4 no Unicode normalisation; exact review-6 survivor; generated suite exits 0. Independent counterexample is captured in JSON.
- **N20_NO_SEPARATOR_ISOLATED** — H1 mandatory separator; retains H2 seven-hash rejection; generated suite exits 0. Independent counterexample is captured in JSON.
- **N21_INPUT_REWRITTEN** — N0 read-only census; generated suite exits 0. Independent counterexample is captured in JSON.

## Fixture precondition attacks

| ID | Test exit | Observation |
|---|---|---|
| P01_LEVEL6_REMOVED | 0 | No failure: the regressed fixture passes. |
| P02_CRLF_BECOMES_LONECR | 1 | 3 != 0 |
| P03_TERMINATORS_BECOME_EMPTY | 1 | 0 != 4 : three terminators plus one more |
| P04_LFCR_BECOMES_CRLF | 1 | b'\r\n' unexpectedly found in b'a\r\nb' : the pair must not be a CRLF |
| P05_NFD_BECOMES_NFC | 1 | 'Café' not found in '# Alpha\n\ntext\n\n## Beta ##\n## 知識庫 heading\n## Café\n## tag#\n### Gamma\n#### Delta\n##### Epsilon\n###### Six\n####### Seven\n' : fixt |
| P06_BARE_HASH_REMOVED | 1 | '## tag#' not found in '# Alpha\n\ntext\n\n## Beta ##\n## 知識庫 heading\n## Café\n## tag\n### Gamma\n#### Delta\n##### Epsilon\n###### Six\n####### Seven\n' : fi |
| P07_UNTERMINATED_TERMINATED | 1 | True is not false : fixture must not end with a terminator |
| P08_EMPTY_QUEUE_NONEMPTY | 1 | Lists differ: ['missing'] != [] |

P02 and P03 fail answer comparisons, not shape guards. P04–P08 fail explicit fixture assertions. P01 is decisive: level six disappears and the derived expectation follows it into a green.

## Surviving gaps and contract judgment

### G01 — Baseline strips trailing heading text spaces, contradicting exact-text wording.
## Tail followed by two spaces returns Tail without either space. No closing hash sequence exists; N07 additionally demonstrates internal-space preservation is unguarded.

**Direction:** Specify any intended content trimming explicitly or preserve text and add independent exact-whitespace tests.

### G02 — Unstated budget-domain restriction is enforced; budget-boundary semantics incomplete.
Scope promises --max-steps N, baseline choices=[1,2], test requires N=3 rejection. N13 permits 3, correctly reviews all files, and fails that test. N=0/negative validity and equality precedence not specified.

**Direction:** Declare valid N and halt precedence, then align implementation/tests. Do not classify N13 as a semantic defect.

### G03 — Tests enforce output/path and bundle rules absent from SCOPE.
test_cli.py:12,15 and test_skill.py:24-25 require resolved absolute path; test_skill.py:11-13 requires bundled SKILL.md and exact name/command strings. SCOPE has no newline/headings output schema or path rule and no package-data contract.

**Direction:** State output schema, path semantics and bundle requirements, or remove undeclared conformance gates.

### G04 — Every-fixture-precondition closure is false.
P01 replaces ###### Six by ##### Six and test still exits 0, because expected output is derived from regressed fixture. P02 CRLF-to-lone-CR and P03 terminators-to-empty fail only answer assertions, not claimed fixture guards. P04-P08 correctly fail explicit shape preconditions.

**Direction:** Assert required levels 6/7, actual CRLF pairs and nonempty terminators-only shape before running the program; add preconditions for every promised boundary.

### G05 — Harness still records a crash as caught and exits successfully.
C03/C04 crash only on empty queue. Default and limited probes succeed; test fails 3 != 0 with no Error/Exception text. Actual main with C03 sets caught=true, false_red=false and all four flags=true and returns 0.

**Direction:** Capture status and answers for every actual successful test invocation, including empty/alternate inputs; do not infer behavioural failures from first-line assertion strings.

### G06 — Review6 coverage/all-fixed claim is still inaccurate.
Remediation6 lists 21 names but automated list has 20; non-ASCII-drop replay is absent. ATX closing sequence appears once, not an explanation for missing replay. Citing fatal-exit self-tests does not reconcile the nonASCII omission. More importantly exact review6 NFKD mutation N19 still survives: replacing it with an NFC mutation changed the challenged behaviour.

**Direction:** Correct the enumerated receipt and all-fixed ceiling; replay exact prior counterexamples before claiming closure.

### G07 — Heading text/whitespace boundary definitions are incomplete.
# followed by two spaces yields an empty-text heading despite followed-by-text wording. Closing sequence uses unspecified whitespace; NBSP before ## is retained while ASCII/tab separators are stripped. Exact-text versus trimming is G01.

**Direction:** Define nonempty text, separator versus content whitespace, Unicode whitespace domain, and heading line boundaries. Current ordinary rules are enforceable; these boundary clauses are not unambiguous.

### G08 — Exclusion list mixes true exclusions with positive promises.
Scope says excluded topics need no test coverage, then promises fenced headings are still reported and BOM is not stripped. O01/O02 survive while violating those literal promises.

**Direction:** Keep full Markdown/BOM-aware semantics excluded if desired, but mark these positive behaviours as normative tested rules or explicitly advisory descriptions. This ambiguity cannot excuse any of the 14 clearly in-scope survivors.

## Out-of-scope ruling

Full Markdown context/Setext support, devices/symlinks/changing files, nonlocal I/O, and concurrency/retry are legitimate exclusions. They do not excuse tabs, byte decoding, exact-text mutation, ordinary local queue errors, or the test instrument falsely crediting crashes. No intent to evade is asserted. The fence/BOM bullets nevertheless make positive promises within a list which says those topics need not be tested. O01/O02 expose that scope ambiguity; they are recorded separately, not inflated into the 14 clear in-scope survivors.

## Verification and claim ceiling

FAIL against the exact digest-bound SCOPE. Three generated tests pass both on original installed modules and byte-identical scratch copies; all 20 maker-list mutants are detected in replay. This is NOT full contract coverage or closure: 14 clearly in-scope mutations survive, exact review6 NFKD survives, and two empty-queue crashes earn false catches. Mutations ran against scratch copies of installed sources, not physical site-packages, preserving the user write boundary; package locations were verified. Builder/install/network stages were not rerun. No exhaustive proof, release acceptance or independent-model attestation is claimed.

Original installed tests were exercised using scratch fixtures with PYTHONPATH removed; import locations resolve to the supplied venv. Mutation runs bind byte-identical source copies through explicit PYTHONPATH; no claim of physical site-packages mutation is made. Recorded source/installed build-receipt digests agree; recorded REDs are nonempty-output assertions, not missing imports. Current subject digests and restored copied modules match. The full builder was not rerun because it writes outside the two requested outputs. Raw observations are embedded in JSON, so this report does not depend on temporary logs surviving.

An initial exploratory run used runtime TMPDIR which resolved to the system user Temp. Authoritative experiments were rerun under the explicit Hermes scratch path; embedded evidence is from that rerun and subsequent scratch-only probes. Only the two requested review artifacts were written under raw/.
