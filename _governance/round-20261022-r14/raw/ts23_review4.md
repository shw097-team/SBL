# R14-TS23 — fourth independent review

**Verdict: FAIL.** N3/N4/N5/N7/N8 are closed, and the exit-code gate now really returns nonzero. The harness can still falsely certify crashes, and two new wrong implementations survive.

## Boundary and execution

Only this report and its JSON companion were written. Installed programs, generated tests, sandbox, repository and receipts were not edited. Real sandbox-venv Python subprocesses executed single-substitution source mutants using an in-memory import loader. The generated tests were executed unchanged, except that their already-identical fixture writes were suppressed. The harness main/flag/exit code ran unchanged in separate subprocesses with source and receipt IO redirected to memory. Thus these are read-only adapted executions, not a claim of a direct disk-mutating harness run.

Protected-file verification: **3054 files hashed; zero changes; zero new sandbox files**. All three retained baselines execute **one test** and exit 0. Read-only direct installed-module invocations also exit 0 with correct JSON. Initial adapter setup failures/zero-test runs were discarded and corrected; details are in JSON.

## 1. Review-3 holes

| Finding | Generated assertion | Independent result |
|---|---|---|
| N3 | `test_skill.py:17–18`: exact second- and first-document paths | Wrong path fails an output-value AssertionError. A first-document-only mutant independently fires line 18. |
| N4 | `test_agent.py:19`: limited review paths equal `queue[:1]` | Limited-only wrong path fails a value AssertionError; default answer remains correct. |
| N5 | `test_agent.py:20`: limited exact SHA-256 values | Limited-only fake digest fails a value AssertionError; no crash. |
| N7 | `test_agent.py:21`: limited remaining equals `len(queue)-1` | Limited-only `999` fails `AssertionError: 999 != 2`. |
| N8 | `test_agent.py:22`: limited halt reason is `BUDGET` | Limited-only `QUEUE_EXHAUSTED` fails a value AssertionError. |

The five corresponding shipped mutants also fail. The full ten-mutant shipped corpus returns exit 0 with all flags true in the read-only adapter; these ten catches were inspected as output-value assertions, not crashes. The limited-only variants matter: the shipped agent mutations would otherwise be rejected earlier by default-run assertions and would not independently prove the repaired one-step assertions.

## 2. Honesty attacks

| Attack | Result |
|---|---|
| Environment | Insert `if os.environ.get("TS23_MODULE"): raise NameError(...)` at census `main()`. Probe does not set that variable; test does. Probe JSON exactly equals baseline. Test crashes before output. Harness records `caught=true`, `false_red=false`, `crash_not_evidence=false`. **False catch.** |
| Cwd | Crash only outside sandbox cwd. Probe explicitly runs in sandbox; test inherits `C:/Users/user`. Probe is correct; test crashes. **False catch.** |
| Arguments | Agent crashes only for `--max-steps 1`. Probe and default test answer correctly; limited invocation crashes. Return-code assertion is counted as detection. **False catch.** |
| Stateful second invocation / side effects | A temporary loopback counter returns invocation numbers 1 and 2. Mutant answers correctly on 1, raises NameError on 2. Observed counter `[1, 2]`. **False catch.** No state file was written; listener was closed. |
| Cached bytecode | Same-length census mutation counts CR instead of LF. An inherited timestamp loader reading the real existing pyc, with source bytes overlaid but matching real timestamp/size, executes cached baseline: test passes. Force-source control detects the very same mutation. **Execution/source binding gap.** |

The cache case is a controlled in-memory timestamp-collision experiment, **not proof of a historical maker cache collision**. Current cached bytecode structurally matches restored source. `-B`/`PYTHONDONTWRITEBYTECODE` do not disable reading valid caches. The harness neither invalidates caches nor attests the executed source. Restoring source bytes alone does not cover bytecode or arbitrary side effects.

No subject-file poisoning attempt was executed: doing so would violate the explicit no-modification boundary. This limitation is not silently counted as a successful check.

### Full-harness false green

A separate process executing unchanged `main()` with just the environment-dependent crash mutation produced:

```text
CLI_TOOL     caught=True  ran=True  restored=True test-only crash
  all_caught: True
  no_false_reds: True
  all_restored: True
  baseline_all_pass: True
process exit: 0
```

The program supplied no incorrect JSON. It answered correctly under the probe and crashed under the test; the test wrapped that crash in `AssertionError: 1 != 0`. The probe therefore does not close G2: it measures a different invocation, and the harness still mistakes a return-code assertion for a value assertion.

## 3. Exit-code policy

| Executed main() case | OS process exit | Flags |
|---|---|---|
| Unappliable snippet | **1** | `all_caught=false`, `all_restored=false`, baseline passes |
| Valid level-six omission that tests cannot catch | **1** | `all_caught=false`, restore and baseline pass |
| Test-only crash falsely called caught | **0** | Every flag true despite no wrong-answer detection |

The formerly always-zero policy is fixed. Its inputs remain unsound, so a zero exit is not an honest behavioral acceptance certificate.

## 4. New behavioral mutations

| Mutation | Suite result | Independent counterexample |
|---|---|---|
| Exclude terminal LF from census | Detected by value AssertionError | Existing nonempty fixture: 3 reported vs 4 LF bytes. |
| Append one duplicate heading | Detected by value AssertionError | Existing fixture has an extra duplicate of `One`. |
| **Change `#{1,6}` to `#{1,5}`** | **SURVIVES: test exits 0** | Virtual UTF-8 input `###### Six
`: baseline yields level-6 `Six`, mutant yields `[]`; both exit 0. |
| **Add CR count to LF count** | **SURVIVES: test exits 0** | Virtual bytes `41 0d 0a` (`A` + CRLF): baseline newlines=1, mutant=2; all other fields correct and both exit 0. |

These four mutation descriptions are absent from the available first/second/third review JSON records and the current shipped corpus. This establishes novelty against the recorded reviews, not undocumented attempts. Both surviving examples are valid inputs to the existing implementation, not expansions into fenced-code or other excluded parsing scope.

## Complete individual-experiment ledger

| ID | Result |
|---|---|
| N3 | Detected by output-value AssertionError |
| N4 | Detected by output-value AssertionError |
| N5 | Detected by output-value AssertionError |
| N7 | Detected by output-value AssertionError |
| N8 | Detected by output-value AssertionError |
| N4_limited | Detected by output-value AssertionError |
| N5_limited | Detected by output-value AssertionError |
| N7_limited | Detected by output-value AssertionError |
| N8_limited | Detected by output-value AssertionError |
| H_ENV_CRASH | FALSE CATCH: program NameError wrapped by return-code assertion |
| H_CWD_CRASH | FALSE CATCH: program NameError wrapped by return-code assertion |
| H_ARGS_CRASH | FALSE CATCH: program NameError wrapped by return-code assertion |
| NEW_TRAILING_LF | Detected by output-value AssertionError |
| NEW_DUPLICATE_HEADING | Detected by output-value AssertionError |
| NEW_LEVEL6_OMISSION | SURVIVES: wrong implementation; test exits 0 |
| NEW_CR_AS_NEWLINE | SURVIVES: wrong implementation; test exits 0 |
| H_SECOND_INVOCATION | FALSE CATCH: program NameError wrapped by return-code assertion |
| H_CACHE_SAME_SIZE | Cache hides source mutation; test exits 0 |
| H_CACHE_FORCE_SOURCE_CONTROL | Detected by output-value AssertionError |
| N3_first_only | Detected by output-value AssertionError |

## Residual gaps and claim ceiling

- **G2_INVOCATION_MISMATCH** — Crash-only mutants are recorded caught: environment, cwd, limited arguments and stateful second invocation all bypass the one-shot probe. H_ENV_CRASH also makes the full unchanged main() exit 0 with all flags true. No wrong JSON was needed.
- **CACHE_BINDING** — A same-size source change with matching timestamp can load the old valid pyc instead. The cache-control experiment changes only source-loading policy and changes a passing test into an output assertion. Current actual cache code shapes are baseline, not demonstrated stale mutants.
- **LEVEL6_COVERAGE** — Generated headings fixtures cover levels 1-3 only; changing #{1,6} to #{1,5} survives while ###### Six produces no heading.
- **CRLF_COVERAGE** — Census fixture is LF-only plus empty. Counting CR in addition to LF survives and returns newlines=2 for A\r\n instead of 1.

N3/N4/N5/N7/N8 are genuinely closed at their output-value assertions, including isolated one-step variants; all ten shipped mutations are value-detected in the read-only adapter. Exit 1 on a failed flag is real. This is NOT acceptance: G2 remains open through unmatched invocations, four crash-only variants are falsely caught, a full harness process can falsely exit 0, two new behavioral mutants survive, and a controlled timestamp-cache collision hides a source mutation. No subject/receipt mutation was performed; results are bounded to explicitly disclosed in-memory source/IO adapters and real venv subprocess execution.

Created only `ts23_review4.json` and `ts23_review4.md`. No repair or acceptance is claimed.
