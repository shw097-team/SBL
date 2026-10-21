# ResearchSynthesis — FAR-20261021-023-sbl-r7-residual-closure

> run_id: `FAR-20261021-023-sbl-r7-residual-closure`
> task_class: `RESEARCH_LITERATURE_REPO` → route `NATIVE_WITH_SELECTED_ARIS` (`FAR_ROUTE_NATIVE_ARIS`)
> challenger: `aris` / `research-review`
> workorder: `WO-TS-req-hgk-prj-sbl-pipdls-r7-farclo` (base_head `3d06f3da83488219a3dcdf608c937b8c5285810c`)
> claim_ceiling: local / candidate-only. This is NOT an acceptance, NOT a Gate PASS, NOT authority.
> Full DOC-00..13 contract closure remains NOT CLAIMED.

## 1. Decision question and the answer

**Q.** Under the current Fabric governance contract, with HG-KSEOS as the only control plane and the
current canonical Hermes as its governed Runtime/Orchestration plane: for every R6 residual / gap /
blocker / open item, for every unmerged candidate branch of `shw097-team/SBL` and
`shw097-team/PIPD-LS-SP`, and for `R6-TS06-A` — what is the lowest-friction, highest-feasibility,
highest-necessity engineering ruling, and which part of it is executable now?

**A.** Three rulings, in order of engineering necessity:

1. **`RULING-1` — The build is not reproducible, and that is fixable now.** `TT-R6-WHEEL-NONREPRODUCIBLE-001`
   was filed as an open defect, but the measurement showed a **build-input** problem, not a product
   problem: `core.autocrlf=true` with no `.gitattributes` made a Windows checkout rewrite the shipped
   text to CRLF (the git objects were already LF-clean), and zip recorded each file's mtime. Fixing the
   *build contract* closes the item outright, instead of re-recording it as "non-reproducible by nature".
   **Executed this round** (§3.1).

2. **`RULING-2` — Exactly one candidate branch may enter MAIN, and it is the one already under review.**
   49 non-main branches were measured. Only `candidate/c3-20261021-v2` (PR #2) is `MERGE_NOW`, and only
   as a scoped merge: `merge-tree` exits 0, `main` is its ancestor (fast-forward possible), 6 ahead / 0
   behind, 27 files, +2,576/−63, and both Ubuntu and Windows CI runs are `success` on that exact head SHA.
   Everything else is `SUPERSEDED` (26), `EVIDENCE_ONLY` (16), `NOT_RECOMMENDED` (3) or `DO_NOT_MERGE` (3).
   **No PIPD-LS-SP branch is recommended for a whole-branch merge.** The eight official PIPD skills are
   already present on `main` with full contracts, so nothing is gained by merging a branch to obtain them.

3. **`RULING-3` — `R6-TS06-A` is one Owner action, not a build task.** The remaining steps (merge, new
   version, new digests, publish) are all mechanical once the Owner acts, and they are gated on exactly
   two human acts: pressing merge on PR #2, and authorising the release. Everything that can be prepared
   without a human act **was** prepared this round (§3.2). The version strategy is settled:
   **`0.1.1rc1`**, because the published `v0.1.0-foundation-preview` bytes must not be replaced and a
   prerelease must not reuse the `0.1.0` identity.

## 2. The residual set: every item, one bucket

Denominator: every `TT-*` / `CR-*` marker plus every R6 work item explicitly left `OPEN`,
`NOT_PERFORMED`, `NOT CLAIMED` or `NEXT_LEGAL_WORKORDER` in
`SBL/_governance/round-20261021-r6/90_EVIDENCE/SBL_R6_EXECUTION_STATUS.json`.
**16 items, each in exactly one bucket.** The full machine-readable list is
`SBL/_governance/round-20261021-r7/30_RESIDUAL/RESIDUAL_INVENTORY.json`.

| Bucket | Count | Items |
|---|---:|---|
| `executable_this_round` | 5 | `TT-R6-CHECKER-SANDBOX-ENV-001`, `TT-R6-WHEEL-NONREPRODUCIBLE-001`, `R6-TS15`, `R6-TS16`, `R6-TS07-CLOSURE` |
| `one_action_owner` | 4 | `CR-PLUGIN-SCHEMA-AUTHORITY`, `CR-GPTB-KP-R04-POLARITY`, `R6-TS06`, `R6-TS06-A` |
| `not_closable_this_round` | 5 | `TT-CHALLENGE-BUNDLE-MISSING`, `TT-METHOD09-LEDGER-DRIFT`, `R6-TS12`, `R6-TS21`, `R6-TS22-23-24` |
| `closed_by_lane_owner` | 1 | `TT-R6-VERIFY-TRANSPORT-VOCAB-001` |
| `closed_by_isolation` | 1 | `TT-R6-APPENDIX-STALE-MERGE-001` |

Two residual items were closed by measurement rather than by assertion:

- `TT-R6-VERIFY-TRANSPORT-VOCAB-001` — the lane owner closed it in `HG-KSEOS` commit `5d63e00`
  (registry epoch 24, root cause G8: the openai arm requires the **bare** transport id). This round
  re-measured it independently: all three lanes dispatched with `ok=True`, `nonce_present=True`,
  `exit=0` and a usage receipt with HTTP status **200**.
- `TT-R6-APPENDIX-STALE-MERGE-001` — closed as a *rule*, not as a patch. The R6 main body governs; the
  appendix wording is isolated by tag. There is nothing left to edit.

Two residual items are **not** defects and must not be "closed" by editing them:

- `TT-METHOD09-LEDGER-DRIFT` — a frozen Oracle must not be rewritten to match a current implementation.
  The recorded delta **is** the correct end state.
- `TT-CHALLENGE-BUNDLE-MISSING` — a signed `PASS_CHALLENGE` cannot be produced by an agent that did not
  sign it. Claiming it would be a false green.

## 3. What was executed this round

### 3.1 `RULING-1` — byte-reproducible build (closes `TT-R6-WHEEL-NONREPRODUCIBLE-001`)

Measured root cause, on candidate `a6bcdd0`:

| Cause | Evidence |
|---|---|
| CRLF introduced by the checkout | `core.autocrlf=true`, no `.gitattributes`; `git cat-file blob` showed the objects were already LF (CRLF=0), while the working tree had CRLF |
| zip member timestamps | 39 differing member timestamps between two builds minutes apart |
| sdist member timestamps + gzip header | 21 distinct member mtimes; the gzip header embedded wall-clock time |

The fix is a **build contract**, not a workaround:

- `.gitattributes` — `text eol=lf` for every shipped text type. Safe because the repo ships no
  `.cmd/.bat/.ps1/.sh/.sln/.vcxproj` (verified over all 198 tracked files), and a test pins that.
- `tools/build_reproducible.py` — exports a **named commit** with `-c core.autocrlf=false` (so the build
  input is the git blob content, never the working tree), pins `SOURCE_DATE_EPOCH`, and repacks the
  sdist with a fixed mtime, `uid/gid 0` and gzip `mtime=0`.

One real defect was found and fixed during the work: `tarfile.create_pax_header` only *overwrites* the
PAX `mtime` header when the value does not fit the ustar field, so an integer epoch survived and the
original float mtimes were still emitted. The header is now stripped explicitly.

**Result, measured twice through the tool:**

| Artifact | sha256 | Stable across two builds? |
|---|---|---|
| `sbl_v01-0.1.0-py3-none-any.whl` | `a161162fa4173460ad9041a9bc83afc31a52b6fc0539f4655f74de3b1147ecf6` | yes — identical |
| `sbl_v01-0.1.0.tar.gz` | `b147f674ffb2356123b63b6e95d6ad572a91f7364db56e859e562495fdd4a927` | yes — identical |

The wheel carries **one** distinct member timestamp. The candidate suite moved from 194 to 200
(`200 passed, 2 skipped`); 6 new tests pin the contract (`.gitattributes` present and LF-complete, no
Windows-only script exposed, git objects LF-clean, the tool present, the PAX/gzip pinning present, and a
`normalise_sdist` round trip).

This is a **product-side** change, so it lives on a candidate branch
(`candidate/r7-20261021-repro-build`), separate from the evidence branch. It does **not** touch the
published `v0.1.0-foundation-preview` bytes.

### 3.2 `RULING-3` — `R6-TS06-A` prepared, down to the Owner button

Measured from the live GitHub API and the local tree:

- PR #2: `head=a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2`, `base=main`, `open`, not draft, not merged,
  `mergeable=true` / `mergeable_state=clean`; CI `test (ubuntu-latest, py3.11): success` and
  `test (windows-latest, py3.11): success` on that exact head.
- `main` is an ancestor of the head ⇒ the merge is a **fast-forward**; `git merge-tree --write-tree`
  exits 0 with no conflict.
- The `0.1.0` lifecycle in an isolated venv is `LIFECYCLE_OK` with **0 residue**; scope is
  `STANDALONE_ONLY` (no native, no Host install) and that ceiling is stated in the receipt.
- `merge_method=merge` is prescribed (not squash) so the reviewed commit identities survive, and the
  branch is not deleted.

What remains is exactly two human acts: **press merge on PR #2**, and **authorise the release** with
the tag and scope. The step list, the per-step gate, the failure handling and the rollback for each step
are in `ResearchHandoff.yaml`.

### 3.3 `RULING-2` — the branch ruling

Full 49-row table with per-branch head SHA, merge-base, directory distribution and CI index:
`raw_worker_artifacts/CANDIDATE_BRANCH_RULING.md`.

Why the evidence branches must stay out of `main`: they are `_governance/` trees, they are the receipt
chain rather than a product delta, and merging them would move release-relevant bytes. Why the three
`DO_NOT_MERGE` branches must stay out: their measured conflicts hit the CI workflow, README, USER_GUIDE
and governance records — the parts of the tree that define what the build *is*.

The eight official PIPD skills (`pipd-route-intake`, `pipd-authority-source`, `pipd-profile-tailor`,
`pipd-pi-compile`, `pipd-pd-bind`, `pipd-execution-contract`, `pipd-assurance-tqaep`,
`pipd-package-project`) are **all present on `main`** with full contracts, typed IO and POS/NEG/EDGE/SEC
cases. Nothing in a branch is needed to obtain them.

## 4. Challenger review (`aris` / `research-review`)

The challenger questions that a decision like this must survive, and the answers:

- *Was the reproducibility claim over-stated?* No: it is scoped to a **named commit** plus a pinned
  `SOURCE_DATE_EPOCH` and a fixed builder. It is not a claim that a wheel built from an arbitrary
  dirty working tree is reproducible, and the tool refuses to build from one by construction.
- *Does closing the wheel item hide a product defect?* No: the product bytes are unchanged; only the
  build inputs and the archive metadata are pinned. The candidate test count went **up**.
- *Is the residual denominator honest?* Yes: 16 items, each in exactly one bucket, and the 5
  "not closable" items are named with the specific authority that is missing.
- *Did the ruling overreach into the human gate?* No: the merge and the release are named as Owner
  actions, and the version/tag/scope defaults are proposed, not applied.
- *Is the checker independent?* Yes: the independent re-check runs on the `VERIFY_SECURITY` lane
  (`openai-codex/gpt-6.1-sol`), a different principal from the maker lane, with a guard subject on the
  product trees, and the raw transcript is kept.

## 5. Abstentions

- No signed `PASS_CHALLENGE` is claimed: the canonical challenge bundle is still missing.
- No `Host-accepted` claim is made for any of the 38 surfaces or the 3 ChatGPT private plugins
  (0/3 stands; no host was authorised).
- No full-contract closure is claimed: `FAIL_FULL_CONTRACT / PARTIAL_CHALLENGE` stands from R6.
- The `v0.1.0-foundation-preview` release is untouched, and no new tag or release was created.

## 6. Raw evidence index

| Artifact | What it proves |
|---|---|
| `raw_worker_artifacts/CANDIDATE_BRANCH_RULING.md` | the 49-branch ruling with measured facts |
| `raw_worker_artifacts/TS06_RESEARCH_GITHUB.json` | the live GitHub API snapshot behind the PR #2 facts |
| `raw_worker_artifacts/TS06_RESEARCH_BUILD_RESULT.json` | the CRLF + timestamp measurement of the two builds |
| `raw_worker_artifacts/TS06_RESEARCH_LIFECYCLE_RESULT.json` | the clean-venv lifecycle, 0 residue |
| `raw_worker_artifacts/REPRO_BUILD_RESULT.json` | two identical builds through the new tool |
| `raw_worker_artifacts/skills-main.json` | the eight official PIPD skills on `main` |
| `SBL/_governance/round-20261021-r7/30_RESIDUAL/RESIDUAL_INVENTORY.json` | the 16-item residual set, machine-readable |
