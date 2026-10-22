# R14-TS23 second independent review: FAIL

## Findings requiring remediation

1. **G1 — agent byte-count assertions still accept wrong output.** I changed only `ts23_review`'s `'bytes':len(data)` to `'bytes':0` in the installed module. Its installed `test_agent.py` exited **0**, `Ran 1 test ... OK`. The two inputs actually contain **5765 and 5776 bytes**. The assertion at line 13 checks only integer/nonnegative values, not correctness. Compare each reported byte count with `len(Path(input).read_bytes())`, including the one-step result, and show this mutation failing on that comparison.
2. **G2 — the maker's “3/3 caught” receipt is false-red evidence.** `ts23_test_strength.json` shows a nonexistent `fixture.md` (`FileNotFoundError`) for CLI, undefined `p` (`NameError`) for headings, and undefined `queue` (`NameError`) for the agent. These do not prove the intended output defects were caught. Preserve this receipt historically and emit a superseding receipt with valid runnable mutants, the correct fixture/environment, intended output assertions, baseline/restored greens and digests. Unexpected exceptions must invalidate an experiment rather than count as behavioural catches.

## Check results

| Check | Verdict | Independently observed evidence |
|---|---|---|
| 3: behavioural RED | PASS | Each of the three remediated build RED receipts exits 1 on `assertTrue(got.stdout.strip(), 'program produced no output')`, with one assertion failure and no import/entrypoint/collection error. |
| 2: tests catch breakage | FAIL | Three valid maker-style mutants caught on output assertions; one reviewer-only zero-byte mutation survives. Maker mutation receipt is invalid for its stated causal claim. |
| 5: isolation | PASS | Hermetic config; distributions and actual imports inside sandbox venv; absent in the three inspected external runtimes; source tracked diff empty before/after. |
| 4: positive controls | PASS | All three installed tests exit 0 before and after mutation; legitimate outputs independently matched their inputs. |

## Independent installed-module experiments

All commands ran from `ts23_sandbox` using `venv/Scripts/python.exe -B SBL/ts23_tests/test_<kind>.py`, with `PYTHONPATH`/`PYTHONHOME` removed, `PYTHONDONTWRITEBYTECODE=1`, and the correct `TS23_MODULE`, `TS23_FIXTURE=SBL/ts23_tests/headings.md`, `TS23_QUEUE=workspace_queue.json` (absolute paths in JSON).

| Experiment | Exit | Actual failing assertion |
|---|---:|---|
| Remove real census implementation; replace with runnable main returning 0 and printing wrong JSON | 1 | `test_cli.py:10 self.assertEqual(json.loads(got.stdout), expected)` — bytes **0 != 28**, newlines **0 != 4**, wrong SHA256. Program return-code and nonempty-output checks already passed. |
| Maker class: census zero counts | 1 | Same line 10 exact JSON comparison; correct digest retained but byte/newline counts wrong. |
| Maker class: fixture-constant headings | 1 | `test_skill.py:17 self.assertEqual(got2['headings'],expect)` — One/Two/Three at lines 1/3/4 versus Alpha/Beta/Gamma at lines 1/5/6. |
| Maker class: wrong halt reason and negative byte counts | 1 | `test_agent.py:12 self.assertEqual(data['halt_reason'],'BUDGET')` — `'WRONG' != 'BUDGET'`. This combined mutant does not separately prove detection of the negative count. |
| Reviewer-only: all agent byte counts become zero, otherwise real processing | **0** | **None: survived.** Exact digest, paths and budget checks still pass. |

Full replacement source, exact argv/environment, stdout/stderr and SHA256 preimage/mutant/restore records are embedded in `ts23_review2.json`.

## Restore proof

Every experiment restored its original file in `finally`. Original and restored SHA256 values:

- `ts23_newline/__init__.py`: `fa8134f7298b73d06ff96a372c5771ac5ea92e9bef316d41aea56015d03dfb0a` = `fa8134f7298b73d06ff96a372c5771ac5ea92e9bef316d41aea56015d03dfb0a`.
- `ts23_headings/__init__.py`: `46a89d205ddab4644dd93ea6a1e9f6fa9397894afdbe9dc625f9c9cd46094135` = `46a89d205ddab4644dd93ea6a1e9f6fa9397894afdbe9dc625f9c9cd46094135`.
- `ts23_review/__init__.py`: `84eba02064ef09ef7a24c890d7988e857c24c068d52fc91cddf4e2d842a3c5b6` = `84eba02064ef09ef7a24c890d7988e857c24c068d52fc91cddf4e2d842a3c5b6`.

The full three-package file/digest inventories match before/after, all eight installed receipt file digests match, fixture bytes remain identical, and each installed test passes again after restoration.

## Isolation details

`venv/pyvenv.cfg` contains `include-system-site-packages = false`; `site.ENABLE_USER_SITE` is false. Exactly one metadata entry each for `ts23-cli`, `ts23-skill`, and `ts23-agent` version 0.0.1 resolves to `ts23_sandbox/venv/Lib/site-packages`. Actual imports' `__file__` paths resolve there, not to sandbox source roots. All three distributions and modules are absent from the Hermes maker interpreter, its base interpreter including user site, and `HG-KSEOS/.venv`. This is a bounded runtime check, not a universal claim that no other copy exists anywhere on disk.

`git -C C:/Projects/Agent_Workspace/SBL diff HEAD --` exits 0 with empty stdout before and after. Source `git status --porcelain` remains exactly the two pre-existing R9 untracked entries (`contracts/SBL_C0_C9_CONTRACT-R9.json`, `contracts/compiled-r9/`).

## Legitimate behaviour accepted

- Census: the actual 28-byte fixture produces 4 LF bytes and SHA256 `2d34cad9832c1bef733d424191234a2e4428b8697cea72eb1940f98aff528051`; installed census test accepts it (and an empty file).
- Headings: actual One/Two/Three headings at lines 1/3/4 and levels 1/2/3 are accepted; the installed test also accepts its distinct Alpha/Beta/Gamma document and bundled skill metadata.
- Agent: actual first two queued files yield 5765 and 5776 bytes and independently matching hashes, `steps=2`, `remaining=1`, `halt_reason=BUDGET`; installed test accepts the valid implementation before and after restoration and exercises one-step limiting. The positive byte counts are independently verified here, but the shipped test still fails to enforce their exactness.

## Scope and disposition

Independent second review of the currently installed remediated R14-TS23 artifacts, not product qualification, general coverage, independent-model attestation or M2/Gate acceptance. FAIL: behavioural RED and hermetic runtime isolation are substantiated, and legitimate behaviour is accepted, but the agent byte-count coverage hole survives and the maker mutation-evidence claim is invalid. Historical ts23_m2_dogfood.json remains a pre-remediation record with its own FAIL and older REDs; it was not promoted or rewritten. Absence outside the sandbox was checked only in the three relevant external runtimes, not all filesystems/environments.

Only `ts23_review2.json` and this `.md` are persistent review deliverables. No maker artifacts, source repository files or governance records were modified; temporary installed mutations were restored. No execution blocker occurred. **Do not close M2 from this review.**
