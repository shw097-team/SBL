# R7 Independent Verify Brief (round SBL-R7-FAR-RESIDUAL-CLOSURE, CHK-R7)

## Your task
You are the separate model-axis independent checker for SBL round R7. Your mandate:
1. Read the raw inputs below and independently RE-DERIVE every claim. Accept nothing on the maker's say-so.
2. For each finding, copy the exact command, its exit code and the literal output that proves it.
3. Output a SHORT verdict (English, markdown) with sections: STRENGTHS / WEAKNESSES / ITEMS-LIST / VERDICT.
4. Do NOT modify any file in the product or evidence trees. You are read-only. If you mutate anything, it
   must be a THROWAWAY COPY under your own scratch directory.

## The product change to check
Round R7 changed exactly these files on top of the R6 candidate, on a dedicated branch:

    branch : candidate/r7-20261021-repro-build
    base   : a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2   (the R6 candidate, PR #2 head a6bcdd0)
    head   : 26a289ff1d9c9dddddc1a5eb413121d8980d9031
    files  : .gitattributes, tests/test_repro_mutation_probe.py, tests/test_reproducible_build.py, tools/build_reproducible.py

The change claims to close `TT-R6-WHEEL-NONREPRODUCIBLE-001`: that a wheel/sdist built from the SAME
commit was not byte-reproducible, because (a) a Windows checkout rewrote the shipped text to CRLF
(`core.autocrlf=true`, no `.gitattributes`) while the git objects were already LF, and (b) the archive
recorded each file's mtime.

## What the FIRST independent round found (and what you must re-check)
Round 1 ran on the lane and produced real evidence, but it ended WITHOUT a verdict: the provider
quota was exhausted after 392 s, so the dispatcher recorded `ERR_NO_ARM_EMITTED_NONCE` (ok=false)
with a valid usage receipt (HTTP 200) and a byte-exact transcript. It is classified as
`INCOMPLETE_ROUND_PROVIDER_QUOTA` and is NOT acceptance. Its transcript is at
`_governance/round-20261021-r7/40_VERIFY/checker_round1_receipt/`.

Before the limit it made two substantive findings. The maker then made a further commit
(`26a289ff1d9c`). Your job includes RE-VERIFYING that repair:

  * **F8** The reproducibility tests asserted SOURCE TEXT, not BEHAVIOUR. Round 1 mutated the tree
    three ways and two mutants still PASSED: `.gitattributes` rewritten to `eol=crlf` (the test only
    checked the file contained the literal `eol=lf`), and `normalise_sdist(sdist, epoch)` replaced by
    `pass` (the test checked the source for the CALL, so removing the call was invisible). Only the
    deletion of `.gitattributes` was caught. The repair claims to rewrite the tests to assert behaviour
    and to add `tests/test_repro_mutation_probe.py`, which breaks each mechanism on purpose in a
    throwaway copy and asserts the suite goes red. VERIFY THIS YOURSELF: does the probe actually fail
    when it should, and is it possible to write a mutant the probe still misses?
  * **F9** The build tool required the `build` package to be importable from the ambient interpreter.
    Round 1's venv has no `build`, so the build failed for an environmental reason. The repair claims
    a `_builder_python()` resolver (`SBL_BUILD_PYTHON`, then `sys.executable`, then PATH, then a local
    venv). VERIFY THIS YOURSELF: run the build from an interpreter that does NOT have `build` and
    confirm it either works or fails with a message that names what it tried.

## What the SECOND independent round found (and what you must re-check)
Round 2 ran to completion on the lane and produced a real verdict, served by
`openai-codex/gpt-6.1-sol`. It found three defects. The maker then made a further commit. Your job
includes RE-VERIFYING that repair, and it is the substance of this round:

  * **W1 — the interpreter probe was a false positive.** `_has_build()` asked `import build`. This
    repository contains a `build/` DIRECTORY (gitignored: `build/bdist.win-amd64`, `build/lib`), so
    `import build` succeeds as a NAMESPACE PACKAGE and the resolver selected an interpreter that could
    not build anything. The brief's own command then failed with "No module named build.__main__;
    'build' is a package and cannot be directly executed". The repair claims the probe now asks
    `python -m build --version` (falling back to importing `build.__main__`). VERIFY THIS YOURSELF:
    run the resolver against an interpreter with no `build` package, from INSIDE this repository, and
    confirm it does NOT claim the interpreter is usable.
  * **W2 — nothing asserted the actual property.** Every test asserted a LOCAL property (a rule is
    present, a normalisation changes a file, a timestamp is constant) and none built anything twice.
    The checker showed that a mutation replacing `DEFAULT_SOURCE_DATE_EPOCH` with wall-clock
    `time.time()` leaves the whole suite GREEN while destroying reproducibility: the two builds differ
    (wheel `f182f0cd...` vs `0d26e23b...`, `identical=false`). A local property can hold while the
    global property fails. The repair claims two new end-to-end tests (two builds as SEPARATE
    PROCESSES, compared byte-for-byte; and the epoch read in two processes more than a second apart
    and required to be equal), plus the checker's own MUT_D and MUT_E added to the mutation set.
    VERIFY THIS YOURSELF: is there still a mutant that turns the suite green while breaking
    reproducibility? Try to write one.
  * **W3 — the mutation probe wrote THROUGH into the protected worktree.** Copying a LINKED
    WORKTREE's `.git` — which is a pointer file into a shared admin dir — made the copy's
    `git add -A` stage into the PROTECTED tree's index; with an unstaged edit there, the copy
    silently staged it. The repair claims the copy now gets its OWN git dir (a fresh `git init` plus
    one commit, no shared objects, no shared index, no path back), and that the probe asserts the
    protected repository's STAGED TREE, HEAD and status are unchanged. VERIFY THIS YOURSELF: make an
    unstaged edit in the protected tree, run the probe, and confirm nothing was staged. NOTE the
    invariant is the STAGED TREE, not the index FILE's hash: git rewrites the index file's stat cache
    on any read, which changes its bytes without changing what is staged. A raw index-file hash
    comparison is a FALSE POSITIVE here.

## What you must independently re-derive
1. **The diagnosis.** Confirm the git objects are LF-clean (`git cat-file blob` on the shipped text
   files) and that the claim "the working tree was CRLF" is consistent with the repo configuration
   (`core.autocrlf`, presence/absence of `.gitattributes`).
2. **The fix actually produces reproducible bytes.** Run the build tool TWICE, independently, and
   compare the digests. The tool is `tools/build_reproducible.py`:
       python tools/build_reproducible.py --commit <sha> --outdir <dir1> --verify
   Success = both builds yield the identical wheel sha256 AND the identical sdist sha256, AND the
   wheel carries exactly ONE distinct member timestamp.
3. **The change did not silently alter the product.** The candidate test suite must still pass and the
   count must have gone UP (194 -> 207), not down. Run it yourself:
       python -m pytest -q -p no:cacheprovider --basetemp <fresh-dir>
   Report the literal summary line (e.g. "207 passed, 2 skipped").
4. **The new tests actually test the contract.** `tests/test_reproducible_build.py` and
   `tests/test_repro_mutation_probe.py` must fail if the `.gitattributes` LF rule or the sdist
   normalisation is removed. The strongest evidence is a mutation you performed yourself on a
   THROWAWAY COPY (never the protected tree); if you cannot mutate, say so explicitly.
5. **No scope creep.** The change must not touch product behaviour, must not alter the bytes of the
   existing `v0.1.0-foundation-preview` release, and must not add a version bump. Verify with
   `git diff --stat`.

## Raw inputs (all under C:/Projects/Agent_Workspace/SBL)
- _governance/round-20261021-r7/00_NORTH_STAR_AND_SPEC.md                  (round spec + lane/session plane separation)
- _governance/round-20261021-r7/00_NORTH_STAR_AND_SPEC.json               (machine form of the same)
- _governance/round-20261021-r7/30_RESIDUAL/RESIDUAL_INVENTORY.json        (the 16-item residual set, one bucket each)
- _governance/round-20261021-r7/50_TS06/repro_result.json                 (the maker's own build receipt - verify it, do not trust it)
- _governance/round-20261021-r7/40_VERIFY/checker_round1_receipt/         (round 1's byte-exact transcript)
- C:/Projects/_sbl_r4/c3v2                                               (the candidate worktree @ 26a289ff1d9c9dddddc1a5eb413121d8980d9031)
- C:/Projects/Agent_Workspace/_sbl_candidate_check                          (a second trusted worktree you may use)
- C:/Projects/Agent_Workspace/_sbl_checker_env                             (a venv with pytest; it does NOT have `build`)

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

## The nonce
Your first line of output MUST be exactly: R7CHK-NC-20261021-A2
