#!/usr/bin/env python3
"""Build the R7 independent-verify brief and status files.

The R7 round has ONE product change (the reproducible build) on top of the R6
candidate, plus the hardening that the FIRST independent round forced. The brief
must let a different model axis re-derive the change itself, not merely read the
maker's summary of it.

Round 1 is included on purpose: it ended without a verdict (the provider quota
was exhausted) but it did make two substantive findings, and those findings are
what the maker repaired. The checker must be able to see whether the repair is
real, not whether the maker says it is.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SBL = Path(r"C:\Projects\Agent_Workspace\SBL")
OUT = SBL / "_governance" / "round-20261021-r7" / "40_VERIFY"
OUT.mkdir(parents=True, exist_ok=True)
R7 = SBL / "_governance" / "round-20261021-r7"


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(repo: Path, *args: str) -> str:
    r = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=180
    )
    return r.stdout.strip()


CAND = Path(r"C:/Projects/_sbl_r4/c3v2")
CAND_SHA = git(CAND, "rev-parse", "HEAD")
BASE_SHA = "a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2"
REPRO_JSON = R7 / "50_TS06" / "repro_result.json"
repro = json.loads(REPRO_JSON.read_text(encoding="utf-8")) if REPRO_JSON.exists() else {}

CHANGED = git(CAND, "diff", "--name-only", BASE_SHA, CAND_SHA).splitlines()

brief = f"""# R7 Independent Verify Brief (round SBL-R7-FAR-RESIDUAL-CLOSURE, CHK-R7)

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
    base   : {BASE_SHA}   (the R6 candidate, PR #2 head a6bcdd0)
    head   : {CAND_SHA}
    files  : {", ".join(CHANGED)}

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
(`{CAND_SHA[:12]}`). Your job includes RE-VERIFYING that repair:

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
   count must have gone UP (194 -> 202), not down. Run it yourself:
       python -m pytest -q -p no:cacheprovider --basetemp <fresh-dir>
   Report the literal summary line (e.g. "202 passed, 2 skipped").
4. **The new tests actually test the contract.** `tests/test_reproducible_build.py` and
   `tests/test_repro_mutation_probe.py` must fail if the `.gitattributes` LF rule or the sdist
   normalisation is removed. The strongest evidence is a mutation you performed yourself on a
   THROWAWAY COPY (never the protected tree); if you cannot mutate, say so explicitly.
5. **No scope creep.** The change must not touch product behaviour, must not alter the published
   `v0.1.0-foundation-preview` bytes, and must not add a version bump. Verify with `git diff --stat`.

## Raw inputs (all under C:/Projects/Agent_Workspace/SBL)
- _governance/round-20261021-r7/00_NORTH_STAR_AND_SPEC.md                  (round spec + lane/session plane separation)
- _governance/round-20261021-r7/00_NORTH_STAR_AND_SPEC.json               (machine form of the same)
- _governance/round-20261021-r7/30_RESIDUAL/RESIDUAL_INVENTORY.json        (the 16-item residual set, one bucket each)
- _governance/round-20261021-r7/50_TS06/repro_result.json                 (the maker's own build receipt - verify it, do not trust it)
- _governance/round-20261021-r7/40_VERIFY/checker_round1_receipt/         (round 1's byte-exact transcript)
- C:/Projects/_sbl_r4/c3v2                                               (the candidate worktree @ {CAND_SHA})
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
"""

(OUT / "CHECKER_BRIEF.md").write_text(brief, encoding="utf-8", newline="\n")
status = {
    "schema": "SBL_R7_CHECKER_STATUS/1",
    "captured_at_utc": datetime.now(timezone.utc).isoformat(),
    "candidate_branch": "candidate/r7-20261021-repro-build",
    "candidate_head": CAND_SHA,
    "base_sha": BASE_SHA,
    "changed_files": CHANGED,
    "brief_bytes": len(brief.encode("utf-8")),
    "brief_sha256": sha_bytes(brief.encode("utf-8")),
    "maker_repro_receipt": {
        "wheel_sha256": next(
            (a["sha256"] for a in repro.get("artifacts", []) if a["name"].endswith(".whl")), None
        ),
        "sdist_sha256": next(
            (a["sha256"] for a in repro.get("artifacts", []) if a["name"].endswith(".tar.gz")), None
        ),
        "verify_identical": repro.get("verify", {}).get("identical"),
    },
    "round1": {
        "classification": "INCOMPLETE_ROUND_PROVIDER_QUOTA",
        "is_a_verdict": False,
        "substantive_findings": ["F8", "F9"],
        "repaired_in_commit": CAND_SHA[:12],
    },
    "note": "the maker receipt is an INPUT to the checker, not evidence; the checker re-derives it",
}
(OUT / "CHECKER_STATUS.json").write_text(
    json.dumps(status, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n"
)
print(json.dumps(status, ensure_ascii=False, indent=1))
