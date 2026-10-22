# R14-TS23 — Sixth independent review

**Verdict: FAIL.** The four review-5 wrong-answer survivors are now rejected on the current fixtures. The pinned semantics are findable outside test code and the census matched independent terminator probes. However, four newly invented wrong-answer implementations still pass, two fatal-exit variants still fool the mutation harness, and fixture precondition enforcement is incomplete.

## Scope and controls

- Reviewed installed package bytes, generated tests, builder, mutation harness, remediation 5 and prior records; prior claims were not accepted as evidence.
- All three actual installed-module suites passed under `ts23_sandbox/venv/Scripts/python.exe`. Their would-write fixture bytes were checked against existing disk bytes and not written. All three source-overlay baselines also passed.
- Replayed all 16 maker mutations and independently replayed the missing ASCII-only heading filter and a precise, nonempty-guarded unterminated-line mutant. All 18 are rejected; see the qualification below about the maker's unterminated mutation.
- Only `ts23_review6.json` and this Markdown report were written. All subject edits, fixture drift and new inputs were RAM overlays. Reviewed source/test/receipt hashes remained unchanged.
- Mutant programs ran in real sandbox-interpreter child processes; unchanged test assertions evaluated their outputs. Original harness classification/aggregation ran over RAM source/receipt adapters. This is not a physical, write-enabled native harness run.

## 1. Review-5 closure experiments

### Lone CR — closed for the current fixture

The LF-only mutant answers with zero terminators for the lone-CR fixture. The assertion that fires is:

```python
# test_cli.py:24
self.assertEqual(gotl['newlines'],3,'a lone CR is a line terminator')
```

Observed: `AssertionError: 0 != 3 : a lone CR is a line terminator`.
The test also asserts CR presence and LF absence before this invocation. The fixture actually contains `alpha\rbeta\rgamma\r`.

### Unterminated final line — closed for the current fixture, not fixture-drift-proof

A mutant adding one for a nonempty unterminated final line reaches:

```python
# test_cli.py:27
self.assertEqual(gotu['newlines'],1,'only the terminator counts, the last partial line does not')
```

Observed: `AssertionError: 2 != 1 : only the terminator counts, the last partial line does not`.
The actual current fixture is hex `616c7068610a62657461` (`alpha\nbeta`).

**Qualification:** the maker's own mutation does not guard empty input; it fails earlier on the empty-file assertion. That earlier failure is not evidence that the unterminated assertion fires. The independently replayed guarded mutation above supplies that evidence. Separately, the fixture lacks an explicit final-byte precondition and can drift to terminated `alpha\n` while the test stays green.

### Empty queue — closed for the current fixture

```python
# test_agent.py:26-27
self.assertEqual((ed['steps'],ed['remaining'],ed['reviews']),(0,0,[]))
self.assertEqual(ed['halt_reason'],'QUEUE_EXHAUSTED','nothing was queued, so nothing was budget-limited')
```

The constant-BUDGET mutant reaches the second assertion and fails with `'BUDGET' != 'QUEUE_EXHAUSTED'`, followed by the explanatory assertion message. The baseline returns exactly zero steps, zero remaining, no reviews and `QUEUE_EXHAUSTED`.

### UTF-8 headings — ASCII-only survivor closed; preservation coverage incomplete

```python
# test_skill.py:23
self.assertEqual(got2['headings'],expect)
```

The former ASCII-only-filter survivor now produces a list missing `知識庫 heading`, and this assertion fires with `Lists differ`. The full diff is retained in JSON. There is no separate explicit CJK-presence assertion: the oracle derives its list from the fixture. A new normalization mutation survives despite the rule that text is kept as-is; see section 3.

### cwd mismatch — closed

The actual harness `probe()` and `run_test()` launch functions were exercised through a read-only subprocess spy. Both explicitly pass the same sandbox cwd, module binding and `PYTHONDONTWRITEBYTECODE=1`.

The reviewer assertion executed successfully:

```python
assert len(launches)==2 and all(
    x['cwd']==str(S) and x['module']=='ts23_review'
    and x['dontwrite']=='1' for x in launches
)
```

No subject assertion is supposed to fire for this repair. The former cwd-sensitive mutant now passes both the default probe and the behavioural suite. The harness correctly records it **not caught** and exits 1 when asked to count that observationally equivalent mutant as detected. There is no longer a cwd-generated false catch.

### Crash without traceback — specific replay closed, general class NOT closed

The exact one-step `ZeroDivisionError` mutant with `sys.tracebacklimit=0` fires:

```python
# test_agent.py:16
self.assertEqual(limited.returncode,0,limited.stderr)
```

Observed: `AssertionError: 1 != 0 : ZeroDivisionError: division by zero`.
The harness now sets `caught=false`, `crash_shaped_assertion=true` and exits 1. It nevertheless leaves `false_red=false` and `crash_not_evidence=false`, contrary to the remediation's stated metadata.

A one-step hard exit with just `fatal` on stderr fires the **same returncode assertion**, not an output-value assertion. It is falsely recorded `caught=true`, `false_red=false`, `crash_not_evidence=false`; the harness exits **0**. Both `os.write` and `sys.stderr.write` variants reproduce. The default-only probe still cannot certify the limited invocation; the Error/Exception message regex only recognizes some crashes.

### Cache purge — new failure guard works in the permitted RAM experiment

Executed the actual `_purge_cache()` with an in-memory path/rmtree adapter:

```python
# ts23_mutation_check.py:86
assert not leftovers, f"bytecode cache could not be removed: {leftovers}"
```

A silent no-op deletion fires `AssertionError: bytecode cache could not be removed: [RAM/site-packages/ts23_newline/__pycache__]`. An injected `PermissionError` propagates rather than being ignored. Successful deletion leaves no cache.

An actual importlib `SourceLoader` with equal-size source revisions and the same timestamp loads stale value **1** before purge and updated value **2** after invoking the real purge routine over the RAM cache. No physical same-mtime package mutation/deletion was performed under the two-file write allowlist. This is a tested logical closure with a disclosed physical-verification ceiling, not a claim that an actual OS deletion failure occurred.

### ATX closing sequence — ordinary case closed, boundary coverage incomplete

Removing the strip operation makes the same `test_skill.py:23` list-equality assertion fail: `Beta ##` differs from `Beta`. Thus the closing sequence is no longer merely described. The explicit space-before-closing-hashes distinction is not tested: a new mutation stripping a content hash from `# tag#` survives.

## 2. Pinned semantics and fixtures

### The four rules ARE findable outside test code

`ts23_remediation5.json:6-10`, `semantics_now_pinned`, explicitly states:

1. LF, CRLF and lone CR are terminators; count terminators, not final partial lines.
2. ATX levels 1–6 count, 7+ do not; space-plus-hash closing sequences are stripped.
3. Non-ASCII heading text is kept as-is.
4. Empty queue means zero steps, zero remaining, empty reviews and `QUEUE_EXHAUSTED`.

This meets the requested findable non-test-document requirement. The installed `SKILL.md` does not repeat/link the detailed contract, but that alone is not scored as an absence of specification.

### TT-R14-039 is not fully enforced

Five fixture-only regressions were injected at the existing write boundary, without changing the assertions or implementation:

| Fixture regression | Result |
|---|---|
| Remove `###### Six` | Test passes |
| Remove `####### Seven` | Test passes; `assertNotIn('Seven', ...)` becomes vacuous |
| Remove the CJK heading | Test passes |
| Replace `## Beta ##` with `## Beta` | Test passes |
| Replace unterminated `alpha\nbeta` with terminated `alpha\n` | Test passes |

There are no presence assertions for those four heading features and no final-partial-line assertion for the unterminated fixture. The heading expectation is derived from whatever input remains. This is not merely theoretical: removing level six, CJK, or closing hashes also lets the corresponding previously rejected wrong implementation pass (three additional paired experiments, all green).

The current fixture bytes do contain their intended features; the finding is that fixture drift is not independently rejected.

### Terminator edge shapes

An independently written left-to-right state machine consumes CRLF as one, otherwise counts each CR or LF. It does not reuse the implementation's count-add-subtract formula.

| Input | Expected | Actual current implementation |
|---|---:|---:|
| CR CR LF | 2 | 2 |
| LF CR | 2 | 2 |
| UTF-8 BOM alone | 0 | 0 |
| BOM + `# X` + CR CR LF | 2 | 2 |
| CRLF CRLF | 2 | 2 |
| CR CR LF LF CR, no content | 4 | 4 |
| Empty | 0 | 0 |
| Unterminated `last` | 0 | 0 |
| NUL FF LF CR | 2 | 2 |
| UTF-8 U+2028/U+0085/U+2029 | 0 | 0 |

Also executed the real current census `main()` in RAM on **3,280** exhaustive strings over CR/LF/x through length 7: no oracle disagreement. No bounded experiment is presented as proof over all files.

A BOM-prefixed heading is omitted by the heading parser. The pinned rules do not specify BOM stripping for headings, so that observation is **not** promoted to an invented conformance defect.

## 3. Newly invented mutations

Each wrong-answer mutant is one textual substitution in the actual installed implementation bytes. All retain imports and CLI execution. Exact substitutions and boundary hex are in JSON.

| Mutation | Full shipped behavioural test | Independent boundary |
|---|---|---|
| `LFCR_PAIR_MERGED`: additionally subtract `data.count(b'\n\r')` | **SURVIVES**, exit 0 | LF CR: expected/current 2, mutant 1 |
| `TERMINATORS_ONLY_SUPPRESSED`: report zero when `data.strip(b'\r\n')` is empty | **SURVIVES**, exit 0 | CR CR LF LF CR: expected/current 4, mutant 0 |
| `UNICODE_NORMALIZATION`: NFKD-normalize heading text | **SURVIVES**, exit 0 | `café 😀` changes U+00E9 to U+0065 U+0301, violating kept-as-is |
| `CONTENT_HASH_STRIPPED`: change closing regex from whitespace-plus-hashes to hashes alone | **SURVIVES**, exit 0 | `# tag#` changes `tag#` to `tag` without a closing sequence |
| `LINE_OFFSET_PLUS_ONE`: report `number+1` | **REJECTED**, AssertionError | First heading line becomes 2 instead of 1; `test_skill.py:10` fires |

Two additional novel instrument mutations use the same one-step-only fatal exit with different diagnostic delivery:

- `FATAL_EXIT_FALSE_CATCH`: `os.write(2,b'fatal\n')` then `os._exit(1)`.
- `FATAL_BUFFERED_EXIT_FALSE_CATCH`: `sys.stderr.write('fatal\n')` then `os._exit(1)`.

Both default probes exit 0 and answer JSON. Both one-step invocations exit 1 without JSON. Both behavioural tests fail only at the returncode precondition, yet the original harness reports `caught=true` and exits 0. They survive the harness's honesty check, not the behavioural suite; these are explicitly different survival scopes.

## 4. Receipt/coverage discrepancy

The actual automatic mutation list contains **16** cases and no ASCII-only/non-ASCII-drop mutation. Remediation 5 says review-5 UTF-8 mutations are included, and the harness prose says every reviewer mutation is carried. This is a claim-layer overstatement: the current test does catch the missing mutation when independently run, but the advertised automatic replay is absent.

## Residuals and verdict basis

- Four novel wrong-answer survivors violate pinned rules while passing current behavioural tests.
- Two fatal-exit variants expose one remaining crash-classification defect; named-exception recognition did not close the class.
- Fixture preconditions remain incomplete, with five passing fixture regressions and three masked implementation defects.
- Automatic UTF-8 mutation-coverage wording exceeds the actual mutation list.

**FAIL**, not acceptance. The specific review-5 output examples are enforced now; the stronger claims of fixture self-validation, crash/catch fidelity and adequate pinned-rule boundary coverage are not.

## Execution issue and verification ceiling

An initial reviewer baseline adapter ran test classes in the reviewer interpreter, causing child module-import failures. This was not a subject defect. It was corrected by running the actual test scripts under the explicit sandbox interpreter; all three then passed. Raw corrected baseline output is in JSON.

Cache failure injection and installed-source mutations stayed in RAM; no helper script, source, fixture, bytecode cache or previous receipt was written. The JSON retains exact mutations, inputs, assertion outputs, source digests, controls and method limitations so a later authorized physical runner can reproduce them without mistaking these trials for native filesystem mutation.
