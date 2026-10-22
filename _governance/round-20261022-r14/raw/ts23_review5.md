# R14-TS23 — fifth independent review

**Verdict: FAIL.** LEVEL6 and CRLF are genuinely repaired. G2 is not closed, and four new wrong-answer mutants survive the shipped tests. All three native installed baseline tests pass.

## Scope and write discipline

Only `ts23_review5.json` and `ts23_review5.md` were written. Installed sources, generated tests, fixtures, caches and existing receipts were not changed. Mutants were single textual substitutions in the actual installed source delivered to real venv child processes through an in-memory source overlay. Generated test assertions were unchanged. Fixture writes were replaced with exact would-write-byte equality checks against existing disk bytes, then suppressed. Baselines were also run against the native installed modules without source overlay.

The original harness aggregation/classifier ran with RAM source/receipt adapters and real child executions. This is not claimed as an unmodified native filesystem-mutation run. JSON contains exact substitutions, return codes, assertion messages, tails, source digests and the bounded method.

## Review-4 closure

### LEVEL6 — PASS

Generated `test_skill.py:17` now writes levels 1 through 7 on distinct lines. Its would-write bytes match the disk fixture, including real Windows CRLF. Level six is `###### Six` on line 9; level seven is `####### Seven` on line 10. The `(#{1,6})` → `(#{1,5})` mutation raises an **AssertionError** specifically because line 9 / level 6 / Six is missing. The test excludes Seven.

### CRLF — PASS

Generated `test_cli.py:15` writes `b'alpha\r\nbeta\r\ngamma\r\n'`; its exact disk bytes are `616c7068610d0a626574610d0a67616d6d610d0a`. The precondition checks CR really exists. Adding CR count to LF count raises **AssertionError: 6 != 3**. All twelve inherited wrong-answer mutations fail with AssertionErrors in the replay.

### G2_INVOCATION_MISMATCH — FAIL

`TS23_MODULE` now matches, but the cwd claim remains false: `probe()` sets `cwd=SB` at harness lines 89–91; `run_test()` omits cwd at line 103. Its test subprocess and program children inherit the caller cwd. This review ran from `C:/Users/user`, not SB. The default probe also never exercises `--max-steps 1`.

Two concrete false catches:

1. Replace `result=review(fixed,args.max_steps)` with `__import__('sys').tracebacklimit=0; result=review(fixed,args.max_steps) if args.max_steps==2 else 1/0`. Default probe returns valid JSON. One-step test hits a genuine **ZeroDivisionError**, emitting no JSON and exiting 1. The assertion is only `1 != 0 : ZeroDivisionError: division by zero`. Harness reports **caught=true, false_red=false, crash_not_evidence=false, exit=0**.
2. Make the same result assignment exit 2 with `ERR_INPUT: cwd mismatch` outside SB. Probe answers from SB; first test invocation fails from the inherited review cwd. Harness again reports **caught=true and exit=0**.

Controls: unconditional division-by-zero is correctly rejected with harness exit 1. A one-step division-by-zero retaining an ordinary traceback is also rejected as a catch, although `false_red` and `crash_not_evidence` misleadingly remain false because the default probe succeeded.

### CACHE_BINDING — PARTIAL, explicitly bounded

The pre/post purge and `PYTHONDONTWRITEBYTECODE=1` exist. An actual `importlib.SourceLoader` experiment used RAM source/cache bytes with identical size and timestamp: `value=1` cached, source edited to same-size `value=2`. Before purge import returns 1; after the real purge function is applied through filesystem adapters, import returns 2. This demonstrates the mechanism, not a physical installed-source same-mtime edit, which the write allowlist prohibits.

A deletion-failure model returns normally from `rmtree(..., ignore_errors=True)` without removing the cache: import still returns 1. The harness never verifies absence. This is injected deletion failure, not a claim that an OS deletion failed in this review. The no-bytecode-write setting alone does not prevent reading old bytecode.

## Novel category attempts — every result

| Attempt | Observed baseline / result | Assessment |
|---|---|---|
| Lone CR: `a\rb\r` | bytes 4, newlines 0 | Correct for explicit LF-byte contract; a mutant reporting 2 survives. Not proof of a universal line-ending census. |
| Last line unterminated: `alpha\nbeta` | bytes 10, newlines 1 | Correct; mutant reporting 2 survives. |
| ATX closing sequence: `# Alpha ###` | text `Alpha ###` | Closing hashes retained. Missing fixture and raw-text/content semantics unresolved; not asserted as an external Markdown conformance violation. |
| Empty queue `[]` | steps 0, remaining 0, reviews [], QUEUE_EXHAUSTED | Correct; BUDGET-on-empty mutant survives. |
| Queue names existing directory | exit 2, ERR_INPUT, no JSON | Correctly rejected. |
| UTF-8 heading: Chinese, café, emoji | Text preserved | Correct; ASCII-only-filter mutant survives. |
| Bare dash-prefixed filename | argparse exit 2 | Correctly rejected; no shell interpolation. |
| Dash-prefixed filename after `--` | Literal filename accepted; heading Safe | Correct, no argument injection observed. |

## Surviving wrong-answer mutations

- **LONE_CR_IGNORED_BY_SUITE** — count lone CR only when there is no LF. Shipped CLI test exits 0; independent `a\rb\r` probe changes newlines 0 → 2.
- **UNTERMINATED_LINE_COUNTED_AS_NEWLINE** — add one for a nonempty unterminated final line. Shipped CLI test exits 0; independent `alpha\nbeta` probe changes newlines 1 → 2.
- **EMPTY_QUEUE_REPORTS_BUDGET** — change halt condition to `if not fixed or len(reviews)<len(fixed) else`. Shipped agent test exits 0; empty-queue probe changes QUEUE_EXHAUSTED → BUDGET.
- **UTF8_HEADINGS_DROPPED** — replace `return headings` with `return [h for h in headings if h['text'].isascii()]`. Shipped skill test exits 0; UTF-8 probe changes one heading → empty inventory.

These are coverage holes demonstrated against the local shipped behaviour, not defects alleged in baseline outputs that were correct.

## Instrument judgment and causal path

**Yes: a mutation can be recorded as caught for an unrelated failure.** Harness lines 130–134 combine a successful *different default invocation* with any test failure containing `AssertionError`; the only crash exclusion is literal `Traceback (most recent call last)` in the first captured assertion-message line. Lines 105–107 use text matching rather than structured failure attribution. `test_agent.py:19` raises an AssertionError on the one-step process return code before any answer is parsed. Consequently an exception with no traceback header or an environment-dependent exit earns a false behavioural catch. Lines 140–141 classify crash flags solely from the separate probe, compounding the misreport.

## Claim ceiling

This review supports rejection, not acceptance. LEVEL6/CRLF are closed; four new wrong-answer survivors and two false catches remain. Cache success is independently demonstrated through a RAM-backed importlib model; a physical same-mtime package edit is NOT_RUN under the write restriction. Source/harness bytes match the initial reads. No package repairs, receipt rewrites, cache deletions, skill writes or repository changes were made.

One reviewer-adapter trial initially failed with missing `tail`; the adapter was corrected and every reported classifier trial rerun. It was not counted as a subject defect.
