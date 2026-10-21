# LEARNING — FAR-20261021-023-sbl-r7-residual-closure

> The rules below were each extracted from a failure that ACTUALLY happened in this round,
> with the measurement that produced it. Nothing here is a generalisation from theory.

## L1 — A build that is not a function of its source cannot be a release artifact
**Trigger.** `TT-R6-WHEEL-NONREPRODUCIBLE-001` was filed as an open defect. The obvious reading is
"Python packaging is not reproducible, so this is a property of the platform and we record it".
**Measurement.** `git cat-file blob` showed the committed objects were already LF-clean (CRLF=0),
while the working tree had CRLF — because `core.autocrlf=true` and there was no `.gitattributes`.
zip then recorded 39 differing member timestamps.
**Rule.** Export the build input from the object store, never from the disk. The tool
(`tools/build_reproducible.py`) exports a NAMED COMMIT with `-c core.autocrlf=false` and pins
`SOURCE_DATE_EPOCH`.
**Transfer.** A "known limitation" in our own build inputs is not a limitation; it is our bug.

## L2 — Verify reproducibility per ARTIFACT, not per build system
**Trigger.** After the LF fix, the wheel became reproducible but the sdist did not.
**Measurement.** The `.tar.gz` carried 21 distinct member mtimes and its gzip header embedded the
wall-clock time. setuptools honours `SOURCE_DATE_EPOCH` for the wheel and not for the sdist.
**Rule.** A wheel that is reproducible says nothing about the sdist sitting next to it. Check each
artifact separately and repack the ones the build system does not pin.

## L3 — When normalising an archive, strip the extended header, not just the field
**Trigger.** The first `normalise_sdist` set `member.mtime = epoch` and still emitted 20 non-constant
mtimes.
**Measurement.** `tarfile` in PAX_FORMAT keeps a sub-second mtime in `member.pax_headers["mtime"]`,
and `create_pax_header` only OVERWRITES that header when the value does not fit the 12-digit ustar
field. An integer epoch fits, so the original float survived.
**Rule.** `member.pax_headers = {k: v for k, v in member.pax_headers.items() if k != "mtime"}` before
assigning. A partial fix that leaves the output looking plausible is worse than no fix.

## L4 — Before deferring a residual, ask WHO is missing
**Trigger.** The R6 residual list mixed four different kinds of "not done": a human decision, a
host/native effect, a new build slice, and a defect in our own inputs.
**Measurement.** The wheel item sat in the same list as the plugin-host items, but its missing thing
was US. It closed in one round.
**Rule.** Classify every open item as HUMAN AUTHORITY / HOST-NATIVE EFFECT / NEW BUILD SLICE /
OUR OWN INPUTS. The fourth is fixable now; conflating it with the others is how a fixable item
becomes a permanent "known limitation".

## L5 — A nonce proves the model answered only if the model was asked to say it
**Trigger.** The first R7 lane probe returned `ERR_NO_ARM_EMITTED_NONCE` with `exit=0` and a good
usage row — the arm had served perfectly.
**Measurement.** The nonce must appear in an ASSISTANT message, and the prompt is what puts it there.
Adding the token to the prompt turned all three lanes `ok`.
**Rule.** The prompt carries the nonce, not just the `--nonce` flag. Without it, a healthy lane looks
broken and a broken lane can look healthy.

## L6 — An admission that returns an id is not an admission
**Trigger.** `admit_requirement` returned a workorder id, but the spine readback showed the TaskSpec
still in `DRAFT` and no WorkOrder row at all.
**Measurement.** `_repo_head()` runs `git rev-parse HEAD` in the CALLER's cwd. Outside a repo it
returns `''`, `create_workorder` raises `InvariantViolation`, and the `except InvariantViolation: pass`
swallowed it. The API reported success anyway.
**Rule.** Read the three rows back — requirement, taskspec, workorder — before believing an admission.
A swallowed exception is indistinguishable from a completed transition at the API boundary.

## L7 — A branch review that is not a measurement is an opinion
**Trigger.** 49 non-main branches across two repos, each with a merge decision.
**Measurement.** merge-base, ahead/behind, `diff --stat`, `git merge-tree --write-tree` exit code and
patch-equivalence collapsed 49 branches to exactly one `MERGE_NOW`.
**Rule.** `merge-tree` exit code is the conflict answer; ancestry is the supersede answer. Read the
CI check-runs of the frozen head SHA, never of main and never of a hypothetical merge result.

## L8 — The 8 official PIPD skills were already on main
**Trigger.** A candidate branch in PIPD-LS-SP looked like it might carry the official skills.
**Measurement.** All eight (`pipd-route-intake`, `pipd-authority-source`, `pipd-profile-tailor`,
`pipd-pi-compile`, `pipd-pd-bind`, `pipd-execution-contract`, `pipd-assurance-tqaep`,
`pipd-package-project`) are present on `main` with full contracts, typed IO and POS/NEG/EDGE/SEC cases.
**Rule.** Before merging a branch to obtain a capability, check whether main already has it. Merging
a branch that only restates main brings back conflicts and stale READMEs.

## L9 — The pre-authorisation covered the ruling, not the human boundary
**Trigger.** The owner's message pre-authorised executing the FAR ruling, and the ruling's most
valuable step is merging PR #2.
**Measurement.** The R6 report states plainly that the Reviewer recommended a scoped merge and **did
not press the button**; merge, release, permission grants and Host plugin creation are separately
gated effects.
**Rule.** A pre-authorisation of "execute your recommendation" is not a grant of a Native effect. The
ruling names the merge as a one-action Owner item with a mechanically executable step list, and the
rest of the work was done without waiting for it. That is the honest reading, and it is also the
reading that survives an external acceptance.
