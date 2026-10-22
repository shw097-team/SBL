# Bounded writer task (EXECUTE lane)

Liveness token (echo verbatim; it carries no meaning and proves you read this file): EXEC-R15-2-WO04-NONCE-3D81B7E2

You are the SBL bounded writer for work order WO-TS-20261022c-04 (core product surface exercised by its own suite).
You may write **only** inside `workers/codex_exec/`. You may read anything. Do not touch any other directory, do not
run git write commands, do not install packages.

## What is already true

`tests/test_reproducible_build.py::test_git_applies_lf_to_the_shipped_text_files` used to fail on this host with
`FileNotFoundError: [WinError 206] 檔名或副檔名太長` because it passed every tracked path to a single
`git check-attr eol --` invocation, exceeding the Windows command-line limit. A batching fix may or may not be present
in the file right now. The suite result recorded for this work order is 227 tests, 0 failures, 4 skipped.

## Your job (all four steps, in order)

1. Reproduce the failure mode without editing anything: run `git -C <repo> check-attr eol -- <all tracked text files>`
   in one call and record the raw exit code and stderr. Then run the same thing in batches of 60 and record that it
   succeeds. Capture the real numbers (how many tracked text files, how many characters the single command line was).
2. Read `tests/test_reproducible_build.py` and state whether the batching fix is present. Quote the exact lines.
3. If and only if the fix is absent, write it: batch the path list, keep the assertion identical. Never weaken an
   assertion to make a test pass.
4. Write `workers/codex_exec/EXEC_RECEIPT.json` containing: the token, every command you ran with its raw stdout,
   raw stderr and exit code, the tracked-file count, the length of the offending command line, whether the batching
   fix was present, and your verdict `PASS` or `FAIL` about step 1 and step 2. Write no prose outside that JSON and
   this directory.

Report the numbers you actually measured. If a command fails, record the failure rather than a summary of it.
