# ADR-0008 — Repository state and branch/PR hygiene inventory

- **Status**: Accepted (round `R7-20261014-merge-hygiene-closeout`, 2026-10-14)
- **Context**: after PR #8 was merged into `main` under explicit owner authorization, the repository held
  19 branches and six pull requests; the state and what may be cleaned had to be recorded and bound to
  rules so a later session cannot delete a verifiability anchor by accident.
- **Decision**: keep every branch that an evidence pack cites as a frozen subject; close superseded pull
  requests with the ancestry evidence that shows they are already contained; never relax the write-set
  gate for convenience; record the inventory below as the single source of truth for hygiene.
- **Consequences**: hygiene actions are proposals grounded in this table; deletion of a frozen-subject
  branch is forbidden; any change here is a governance action, not housekeeping.

---
Round: `R7-20261014-merge-hygiene-closeout`. Scope: the state after **PR #8** was merged into
`main` under explicit owner authorization. Merged `main` =
`b3a27c1f00c90b010feec7b4da5f420d45edec61` (**1911 blobs**); `ci` on that commit = **success**.
This document is an inventory of what exists and what may be cleaned. It grants nothing:
`BUILD_PASS != PORTAL_APPROVED != PUBLISHED != HOST_QUALIFIED != S4_PASS`.

## (a) Branch inventory

`19 branches exist` on the remote besides `main` (**20** `refs/remotes/origin/*` entries including
`origin/main`). A branch marked **frozen subject** carries a commit that an evidence pack cites by
hash; deleting it would break a verifier's ability to reproduce that pack, so it must be kept. Rows
marked "proposable-for-deletion" are not frozen subjects and have no evidence pointer — no deletion
was performed, and this table is a proposal only.

| Branch | Head (short) | Purpose | Frozen subject? | Disposition | Evidence pointer |
|---|---|---|---|---|---|
| `main` | `b3a27c1` | Distribution entry point; merged candidate | n/a (integration target) | **keep** | `ci` run on `b3a27c1` = success |
| `feat/s4r5y-plugin-publication-20261014` | `062d84a` | R5Y skills-only plugin packaging; the frozen build source commit | **frozen subject** (`062d84ae…`) | **keep** | `PIPD_S4_R6_FAR_AND_ALIGNMENT_RETURN/VERIFICATION_PROTOCOL.md`, `ZIP_REPRODUCTION.json` |
| `feat/s4r5x-manifest-fit-20261014` | `e00ab7b` | R5X official `com.openai.interface` listing fields | **frozen subject** | **keep** | `PIPD_S4_R6_FAR_AND_ALIGNMENT_RETURN/R4_EVIDENCE_EXPANDED/R5X_FINAL_RESULT.md` |
| `feat/s4r5z-readme-plugin-route-20261014` | `9643495` | R5Z README private-plugin route + ADR-0007 (second parent of the merge) | **frozen subject** | **keep** | `PIPD_S4_R5Z_SESSION_CONFORMANCE_RETURN/` |
| `fix/s4r3-stage-a-ci-truthfulness-20261013` | `759b9f0` | Stage A: `ci` carries the suite's exit code; hosted-Linux failures repaired | **frozen subject** | **keep** | `PIPD_S4_R4_EVIDENCE_RETURN/`, `.hgk/rounds/S4R3-…/evidence/12_GATES/` |
| `feat/s4r3-stageb-successor-20261013` | `940a37d` | Stage B successor (write-set gate + Web artefact) | **frozen subject** | **keep** | `PIPD_S4_R4_EVIDENCE_RETURN/`, `.hgk/rounds/S4R3-…/ROUND_RESULT_S4R3X.md` |
| `r5z-evidence-return-20261014` | `6d6af2d` | Evidence-return branch carrying the four return packs | **frozen subject** (evidence branch) | **keep** | `PIPD_S4_R6_FAR_AND_ALIGNMENT_RETURN/` and the other three packs |
| `feat/s4post-triple-upgrade-20261013-r3` | `e71fee6` | R3 frozen base cited by the write-set baseline diff | **frozen subject** | **keep** | `.hgk/rounds/S4R3-…/evidence/12_GATES/C3_ALLOWLIST_BASELINE_DIFF.txt` |
| `fix/s4post-integration-repair-20261012` | `52542c3` | S4POST integration repair; two independent FAR acceptance lanes | cited in lineage | **keep** | `.hgk/rounds/S4POST-…/`, `docs/ROUND_DISCLOSURE.md` |
| `s4-r2-affected-only-20261011` | `3f6c7dc` | S4-R2 affected-only repair verification metadata | cited in lineage | **keep** | `.hgk/rounds/S4R2-20261011-affected-only/` |
| `chore/s4post-verification-harness` | `eea1543` | S4POST round verification harness | no direct frozen citation | proposable-for-deletion (superseded by the merged lineage; no deletion performed) | — |
| `feat/s4post-triple-upgrade-20261012` | `38f9067` | Earlier S4POST candidate branch (local head ahead/behind `origin`) | no direct frozen citation | proposable-for-deletion (superseded by `r3`; no deletion performed) | — |
| `feat/s4post-triple-upgrade-20261012-r2` | `d3bb4e9` | S4POST candidate r2 | no direct frozen citation | proposable-for-deletion (superseded by `r3`; no deletion performed) | — |
| `feat/s4r3-stage-b-distribution-20261013` | `c52c219` | Earlier Stage B head, a sibling of Stage A (re-stacked by the successor) | no (superseded by `940a37d`) | proposable-for-deletion (superseded; no deletion performed) | `.hgk/rounds/S4R3-…/ROUND_RESULT_S4R3X.md` records the re-stack |
| `feat/s4r5z-evidence-readme-20261014` | `51bd8e5` | R5Z evidence/README work branch | no direct frozen citation | proposable-for-deletion (content carried into the merged tree; no deletion performed) | — |
| `fix/s4-external-challenge-20261012-r1-provenance-trace` | `eef951a` | S4EXT-R1 FAR round 2 adjudication study | no direct frozen citation | proposable-for-deletion (study material; no deletion performed) | `.hgk/rounds/R4-20261009-focused-repair/` lineage |
| `fix/s4post-far-adjudication-20261012` | `ad33c0c` | Candidate adjudication implementation (v2 spec) | no direct frozen citation | proposable-for-deletion (superseded; no deletion performed) | — |
| `r5-s4-evidence` | `2ad1f16` | R5 publication subject attestation + redacted credential receipt | no direct frozen citation | proposable-for-deletion (historical; no deletion performed) | — |
| `r5-s4-readme` | `f418153` | R5 README rewrite | no direct frozen citation | proposable-for-deletion (historical; no deletion performed) | — |

Local-only branches not on the remote (`master`, `r5p-post-challenge-repair`,
`r5q-owner-opensource-preview`, and this round's
`feat/s4r7-main-upgrade-and-repo-state-20261014`) are not counted in the 19 above. `main`'s remote
head and every head above are read from `refs/remotes/origin/*`; short forms are the first 7
characters of the full SHA.

## (b) Pull-request dispositions

| PR | Disposition | Reason / binding fact |
|---|---|---|
| #8 | **merged** | Merge commit `b3a27c1f00c90b010feec7b4da5f420d45edec61`. `main` (`2245914`) is an ancestor of `#8`; zero conflict. |
| #6 | **closed** | Contained in the merge: head `062d84a` is an ancestor of the merged `main`. |
| #5 | **closed** | Contained in the merge: head `940a37d` is an ancestor of the merged `main`. |
| #3 | **closed** | Contained in the merge: head `759b9f0` is an ancestor of the merged `main`. |
| #2 | **closed** | Failed the `public-plugin-verify` gate (`unstable`). |
| #4 | **closed** | `dirty`, and superseded by `#5`. |

Ancestry was checked with `git merge-base --is-ancestor <head> b3a27c1f00c90b010feec7b4da5f420d45edec61`
against the merged `main`. `#2` is not an ancestor.

## (c) CI state

Two workflows exist in `.github/workflows/`.

| Workflow | Trigger scope | Last conclusion on merged `main` |
|---|---|---|
| `ci` | `push`, `pull_request` | **success** on `b3a27c1f00c90b010feec7b4da5f420d45edec61` |
| `public-plugin-verify` | `pull_request` (path-filtered), `workflow_dispatch` | `NOT_RUN` on `main` — reason: its trigger does not include `push`, so a merge to `main` does not start it. Its last known PR-head conclusion was success at the R5Z head `9643495` per `PIPD_S4_R5Z_SESSION_CONFORMANCE_RETURN/`. |

Neither workflow grants anything: a green run is not a release, a merge, a portal approval or an S4
acceptance. `ci` copies the frozen subject read-only with no secrets and no publish step;
`public-plugin-verify` has no privileged pull-request trigger and reads no configured secret.

## (d) Local worktrees and what they hold

Listed from `git worktree list`. The round tree
`C:\Projects\Agent_Workspace\PIPD\.hgk\rounds\R7-20261014-merge-hygiene-closeout` is out of scope for
this round's writes; it is not enumerated below because it is not a worktree.

| Worktree | Branch / HEAD | What it holds |
|---|---|---|
| `C:/Projects/Agent_Workspace/PIPD` | `r5p-post-challenge-repair` (`2efc84e`) | Main working tree; R5P post-challenge repair |
| `…/worktrees/r7-wt` | `feat/s4r7-main-upgrade-and-repo-state-20261014` (`b3a27c1`) | **This round's writer worktree**; README upgrade + repo-state/next-session docs |
| `…/worktrees/r5y-wt` | `feat/s4r5y-plugin-publication-20261014` (`062d84a`) | Frozen plugin build source; the worktree the ZIP reproducibility command runs from |
| `…/worktrees/r5z-ev-wt` | `r5z-evidence-return-20261014` (`6d6af2d`) | Evidence-return packs |
| `…/worktrees/r5z-wt` | `feat/s4r5z-readme-plugin-route-20261014` (`9643495`) | R5Z README private-plugin route + ADR-0007 |
| `…/worktrees/r5q-release-wt` | `r5q-owner-opensource-preview` (`9bd33a1`) | R5Q owner open-source preview release work |
| `…/worktrees/s4r3-wt` | `feat/s4post-triple-upgrade-20261013-r3` (`e71fee6`) | R3 frozen base worktree |
| `…/worktrees/s4r3a-wt` | `fix/s4r3-stage-a-ci-truthfulness-20261013` (`759b9f0`) | Stage A repair worktree |
| `…/worktrees/s4r3b-wt` | `feat/s4r3-stage-b-distribution-20261013` (`c52c219`) | Earlier Stage B worktree |
| `…/worktrees/s4r3c-wt` | `feat/s4r5x-manifest-fit-20261014` (`e00ab7b`) | R5X manifest-fit worktree |
| `…/worktrees/s4post-a-wt` | `fix/s4post-integration-repair-20261012` (`52542c3`) | S4POST integration repair |
| `…/worktrees/s4post-b-wt` | detached (`125071e`) | Detached S4POST scratch worktree |
| `…/worktrees/s4post-far-wt` | `fix/s4post-far-adjudication-20261012` (`ad33c0c`) | FAR adjudication worktree |
| `…/worktrees/s4r2m-merge-wt` | `main` (`2245914`) | Pre-merge `main` worktree (local `main` ref, behind the merged `origin/main`) |
| `…/worktrees/s4ext-r1-wt` | `fix/s4-external-challenge-20261012-r1-provenance-trace` (`eef951a`) | S4EXT-R1 provenance-trace worktree |
| `C:/Projects/Agent_Workspace/PIPD-postrelease-wt` | `s4-r2-affected-only-20261011` (`3f6c7dc`) | Post-release S4-R2 worktree |

## (e) Rules for hygiene

1. **Never delete a frozen-subject branch.** Any branch whose head is cited by an evidence pack is a
   verifiability anchor; removing it makes that pack unreproducible. The frozen subjects here are
   `feat/s4r5y-plugin-publication-20261014`, `feat/s4r5x-manifest-fit-20261014`,
   `feat/s4r5z-readme-plugin-route-20261014`, `fix/s4r3-stage-a-ci-truthfulness-20261013`,
   `feat/s4r3-stageb-successor-20261013` and `r5z-evidence-return-20261014`.
2. **Never relax the write-set gate for convenience.** The `public-plugin-verify` allowlist is
   measured, not negotiable; widening it to make a change land would erase the guarantee that frozen
   paths (`skills/`, `src/`, `schemas/`, `dist/`) stay read-only outside their declared single-path
   exemptions.
3. **Treat the lane receipt as the evidence, not a self-report.** A lane run is bound by its receipt
   (engine, required arm, served arm, rank, `ok`, `subject_mutation`); a green self-summary without a
   matching receipt is not evidence.
4. **Keep credentials out of the tree.** The published governing corpus redacts the single
   credential-locator string to `<REDACTED_CREDENTIAL_LOCATOR>`; no token and no credential-path was
   written into any file in this round.

`BUILD_PASS != PORTAL_APPROVED != PUBLISHED != HOST_QUALIFIED != S4_PASS`

---

## Addendum — 2026-10-16: local engineering-hygiene inventory and the actions taken

Owner order 2026-10-16 asked for a ruling on repo/local hygiene (round
`PIPD-REPO-HYGIENE-AND-HANDOVER-20261016`, study `FAR-20261016-021-repo-hygiene-and-handover`). The
inventory above covers the **repository**; this addendum adds the **local machine** layer that a new
session actually starts from.

| Item | Measured | Action | Guard / proof |
|---|---|---|---|
| `main` tree (remote) | clean — no round directories at the root (`git ls-tree main`) | none | no defect to fix |
| Local worktrees | 29 (19 clean, 9 dirty) | **12 reclaimed** → 17 remain | reclaimed only when `dirty==0` **and** `HEAD == origin/<branch>`; the worktree in use by the round was excluded by design |
| Primary clone `PIPD/` | parked on `r5p-post-challenge-repair` (HEAD dated 2026-10-10) with 6 uncommitted tracked files, incl. `src/pipd_ls_sp/{cli,pipeline,validate}.py` (+203/−6) | **rescued**, not discarded: new local branch `rescue/r5p-uncommitted-20261016` @ `39079c0`; original branch left exactly as found; not pushed | tracked modifications afterwards: 0; the 218 untracked files were left in place |
| Untracked `.hgk/…` in the clone | 211 files, but the prefix still holds **644 tracked** files | **no ignore rule applied** | a rule was to be added only if a single safe prefix was provable; it was not provable, so the candidate is delivered unapplied for the owner |
| Regenerable scratch | 5 extraction directories under the S4-FINAL round | deleted | reproducible at will via `git archive` |
| Local `main` ref | `224591431a164ab72a9423cd180e417e8a762403` — 153 commits behind `origin/main` | none (outside this round's writable scope) | owner decision: switch back and fast-forward |
| Governance spine | one orphaned project `PIPD-REPO-HYGIENE-HANDOVER` (`RUN-BB375102`, `PLAN_READY`, 0 work orders), created when a first admission attempt derived task-spec ids from the segment `HANDOVER`, which was already taken | none — deliberately not deleted | owner decision: prune or keep |

**Rule worth keeping:** a local deletion is only acceptable when the object is *provably recoverable*
(tip present on `origin`) or *provably regenerable*. Work of unknown intent is rescued to a new branch,
never removed — `git checkout -- .` and `git clean -fd` have no place in a hygiene pass.
