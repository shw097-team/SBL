# R7 Independent Verify Brief (round SBL-R7-FAR-RESIDUAL-CLOSURE, CHK-R7)

## Your task
You are the separate model-axis independent checker for SBL round R7. Your mandate:
1. Read the raw inputs below and independently RE-DERIVE every claim. Accept nothing on the maker's say-so.
2. For each finding, copy the exact command, its exit code and the literal output that proves it.
3. Output a SHORT verdict (English, markdown) with sections: STRENGTHS / WEAKNESSES / ITEMS-LIST / VERDICT.
4. Do NOT modify any file in the product or evidence trees. You are read-only.

## The single product change to check
Round R7 changed exactly two things on top of the R6 candidate, on a dedicated branch:

    branch : candidate/r7-20261021-repro-build
    base   : a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2   (the R6 candidate, PR #2 head a6bcdd0)
    head   : 00cf15f9de5808260b1af6a697d0e2fefaad5d1f
    files  : .gitattributes, tools/build_reproducible.py, tests/test_reproducible_build.py

The change claims to close `TT-R6-WHEEL-NONREPRODUCIBLE-001`: that a wheel/sdist built from the SAME
commit was not byte-reproducible, because (a) a Windows checkout rewrote the shipped text to CRLF
(`core.autocrlf=true`, no `.gitattributes`) while the git objects were already LF, and (b) the archive
recorded each file's mtime.

## What you must independently re-derive
1. **The diagnosis.** Confirm the git objects are LF-clean (`git cat-file blob` on the shipped text
   files) and that the claim "the working tree was CRLF" is consistent with the repo configuration
   (`core.autocrlf`, presence/absence of `.gitattributes`).
2. **The fix actually produces reproducible bytes.** Run the build tool TWICE, independently, and
   compare the digests. The tool is `tools/build_reproducible.py`:
       python tools/build_reproducible.py --commit <sha> --outdir <dir1> --verify
   Use a python that has the `build` package available; if the ambient interpreter lacks it, say so
   explicitly in your verdict rather than assuming.
   Success = both builds yield the identical wheel sha256 AND the identical sdist sha256, AND the
   wheel carries exactly ONE distinct member timestamp.
3. **The change did not silently alter the product.** The candidate test suite must still pass and the
   count must have gone UP (194 -> 200), not down. Run it yourself:
       python -m pytest -q -p no:cacheprovider --basetemp <fresh-dir>
   Report the literal summary line (e.g. "200 passed, 2 skipped").
4. **The new tests actually test the contract.** `tests/test_reproducible_build.py` must fail if the
   `.gitattributes` LF rule or the sdist normalisation is removed. At minimum, read the six tests and
   state whether each assertion could pass on a broken tree. If you can mutate a THROWAWAY COPY of the
   tree (never the protected one) to show a test fails, that is the strongest evidence; if you cannot
   mutate, say so.
5. **No scope creep.** The change must not touch product behaviour, must not alter the published
   `v0.1.0-foundation-preview` bytes, and must not add a version bump. Verify with `git diff --stat`.

## Raw inputs (all under C:/Projects/Agent_Workspace/SBL)
- _governance/round-20261021-r7/00_NORTH_STAR/NORTH_STAR_AND_SPEC.md        (round spec + lane/session plane separation)
- _governance/round-20261021-r7/00_NORTH_STAR_AND_SPEC.json                 (machine form of the same)
- _governance/round-20261021-r7/30_RESIDUAL/RESIDUAL_INVENTORY.json        (the 16-item residual set, one bucket each)
- C:/Projects/_sbl_r4/c3v2                                               (the candidate worktree @ 00cf15f9de5808260b1af6a697d0e2fefaad5d1f)
- C:/Projects/Agent_Workspace/_sbl_candidate_check                          (a second trusted worktree you may use)
- C:/Projects/Agent_Workspace/_sbl_checker_env                             (a venv with pytest)
- C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\cache\scratch\r7-repro-tool\repro_result.json                 (the maker's own build receipt - verify it, do not trust it)

## Baseline references
- R6 external acceptance report: PR #2 = RECOMMEND_MERGE_SCOPED_NOW, **the Reviewer did not press merge**.
- Full-contract verdict stays FAIL_FULL_CONTRACT / PARTIAL_CHALLENGE; 3 ChatGPT private plugins 0/3
  host-issued IDs; NOT_ADMITTED hosts remain NOT_ADMITTED. This round does NOT change any of that.
- The lane pool's openai arm needs the BARE transport id `gpt-6.1-sol`; the qualified id
  `openai-codex/gpt-6.1-sol` is rejected by the relay with HTTP 400 "Model is unavailable".

## Claim ceiling to enforce
This round may claim ONLY: a scoped R7 closure (one closed residual, a measured branch ruling, and a
prepared-but-not-executed TS06-A plan). If you find the maker overstating any of that, say so in
WEAKNESSES and downgrade the VERDICT accordingly.
