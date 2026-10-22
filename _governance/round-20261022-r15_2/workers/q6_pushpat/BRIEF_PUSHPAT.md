# EXECUTE brief — stop shipping a `.sh` script in the SBL tree (red reproducible-build guard)

Bounded writer. You may change exactly:
- create `_governance/round-20261022-r15_2/tools/push_pat.py` (port of `push_pat.sh`, same behaviour, same messages)
- `git rm --cached _governance/round-20261022-r15_2/tools/push_pat.sh` and delete it from the working tree
- nothing else. No commit, no lane dispatch, no sub-agents.

## Measured red (reproduce before you touch anything)

```bash
cd C:/Projects/Agent_Workspace/_r152_ev
python -m pytest -q -p no:cacheprovider tests/test_reproducible_build.py::test_repo_ships_no_windows_only_script_that_lf_would_break
```

Fails with: `LF normalisation would break these Windows-only scripts … ['_governance/round-20261022-r15_2/tools/push_pat.sh']`.
The repo's `.gitattributes` pins `eol=lf` for every shipped text type, and a second test
(`test_git_applies_lf_to_the_shipped_text_files`) requires **every** shipped text file to resolve to `eol=lf`.
So adding a CRLF rule is not an available fix — it would break the other guard. The file must stop being shipped as `.sh`.

## Fix

1. Read `tools/push_pat.sh`. Port it to `tools/push_pat.py` with the same steps: read the PAT from
   `C:/Projects/Agent_Workspace/API KEY/GITHUB-REPO_SHW097-4.txt`, write a credential-store entry at a **native**
   path, set `credential.interactive=never` and `GIT_TERMINAL_PROMPT=0`, do a lookup self-check, then push.
   Use `subprocess.run([...], check=False)` with explicit argument lists — no shell string building. The script
   must never print, echo or log the token; on failure print only the remote's message.
2. `git rm --cached` the `.sh` and delete it. Leave every other file alone.
3. Verify:
   - `python -m pytest -q -p no:cacheprovider tests/test_reproducible_build.py` → the whole file must pass.
   - `python -m pytest -q -p no:cacheprovider tests/test_repro_mutation_probe.py::test_each_contract_breaking_mutation_is_caught`
     → must pass (it was failing only because the clean-tree precondition was red).
   - `python -c "import ast;ast.parse(open(r'_governance/round-20261022-r15_2/tools/push_pat.py',encoding='utf-8').read())"` → rc 0.
   - `git status --porcelain | head -20` → show it; no product file may be modified.
4. Write `workers/q6_pushpat/RESULT.json`:
   `{"red": {"cmd": "...", "rc": 1, "observed": "..."}, "green": {"file": "tests/test_reproducible_build.py", "passed": N, "rc": 0},
     "mutation_probe": {"rc": 0}, "removed_from_tracking": [".../push_pat.sh"], "added": [".../push_pat.py"],
     "token_leak_check": "grep for the token prefix in push_pat.py returned nothing", "claim_ceiling": "..."}`

## Rules

- Do not edit either test. If the guard cannot pass without editing a test, write the blocker and stop.
- Keep your final message to: the two test results, the untracked/removed file names, and the leak-check result.
