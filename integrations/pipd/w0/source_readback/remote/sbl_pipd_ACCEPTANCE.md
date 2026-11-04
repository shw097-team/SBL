> **R5Q (2026-10-10) — read this banner first.** The owner has granted **`Apache-2.0`** over this
> repository and authorised a limited **S4 open source preview / beta**. The distribution entry point
> is the tag **`v0.1.0-preview.1`**; `main` carries the historical R3 content plus a front-page
> pointer to that tag. The grant, the
> material-class split and the exclusion policy live in [`LICENSE`](LICENSE),
> [`NOTICE`](NOTICE), [`OWNER_LICENSE_DECISION.yaml`](OWNER_LICENSE_DECISION.yaml) and
> [`SBOM.cdx.json`](SBOM.cdx.json) (study FAR-PIPD-R5Q-LICENSE-001).
>
> The grant changes **no** engineering claim: `S0_S4_FULL_INDEPENDENT_CHALLENGE` stays
> `PARTIAL_CHALLENGE`, `DEL-018` stays **FAIL/EVIDENCE_GAP**, the SPEC/DEL denominator stays
> `28 / 10 / 19`, and `G-RELEASE_FULL_PASS` and `PRODUCTION_VERIFIED` remain **NOT claimed**. The
> release notes for the tag carry the full known-limitations list.
>
> **R5P (2026-10-10) — read this banner before the receipt below.**
>
> This file describes the **BASELINE** round (`r5-s4-packreader` @
> `0f06eec96386b7349db8b41ac6cf9c7455d326f1`). It is retained verbatim as history and was not rewritten.
> The branch under review now is **`r5p-post-challenge-repair`**, carrying the post-challenge repair for
> the external 2026-10-10 challenge.
>
> **The current subject's commit, tree, wheel hash and product digest are deliberately NOT quoted in this
> file.** This file sits inside the measured product surface, so committing a digest here would change the
> very subject that digest describes (the independent checker confirmed this and required an external
> binding entry point rather than self-reference). The authority for the branch's current subject is the
> round evidence directory, which the product digest excludes:
>
> - `.hgk/rounds/R5P-20261010-s4-post-challenge/CHECKPOINT_R5P.json` — current subject commit / tree /
>   wheel sha256 / bound product digest
> - `.hgk/rounds/R5P-20261010-s4-post-challenge/evidence/DIGEST_BINDING.json` — the round's single bound
>   product-digest definition, plus the rejected narrower alternative; reproduce with
>   `python .hgk/rounds/R5P-20261010-s4-post-challenge/ops/bound_digest.py <pristine-root>`
> - `.hgk/rounds/R5P-20261010-s4-post-challenge/evidence/host_fullsuite_repair_bound.txt` — host suite
>   receipt carrying its own command line, exit code and subject binding
> - `.hgk/rounds/R5P-20261010-s4-post-challenge/ao/out/AO_VERDICT.json`, `AO_VERDICT_V2.json`,
>   `AO_VERDICT_V3.json` — the independent checker's passes; never the Maker's own summary
>
> **Superseded attempt, kept as history only:** an earlier attempt of this round quoted attempt-2's
> identity (`812af79422c087f0ef5a07188fbec061df6b47e0`, tree `d3b79d2bc7aba08368a02a9f34204d14c9b06bbd`,
> wheel `bb070a6f525382edc521bcf7fe127579e1e329024113ab4fe2881eeeea7b0a76`, product digest
> `4ee712e899e9f4aa14d46ba1d3f879eb6b45ad0ae4a8b02bf1d9847b5f8cc579`) as though it were current. Those
> values belong to that superseded attempt only.
>
> Claim ceiling for every subject named above: **`CANDIDATE_ONLY`**; licence
> **`LicenseRef-PIPD-Proprietary`, no public-use grant**; no downstream stage inherits any PASS.

# External acceptance entry point — R5 S4 repair round (2026-10-10)

This branch was published so that an **independent verifier** can accept it. Everything here is written
for that reader. **Nothing in this repository is a claim of acceptance** — see the claim ceiling below.

| item | value |
|---|---|
| branch to accept | `r5-s4-packreader` |
| subject commit | the tip of branch `r5-s4-packreader`. Two bindings pin it, and neither depends on where a later commit sits: (a) the **sha256 of both subject files** (table below) — stable across any commit, and the same digests the independent checker verified; (b) `.hgk/ao/pub/PUBLICATION_SUBJECT_ATTESTATION_R5S4_PACKREADER.json`, which carries top-level `commit` and `tree` naming the exact subject it was computed over, seals the product and manifest digests, and adds a `payload_digest` so tampering is detectable. Evidence-only commits were added after that binding to deliver the acceptance-officer re-runs; they change no product file, and the digests in (a) are unaffected. The repository's older `.hgk/ao/pub/PUBLICATION_SUBJECT_ATTESTATION.json` attests the earlier R3 published subject and is deliberately left untouched. |
| previous public state (parent) | `7f13b90dc06354a0c6b7bd013f83a8cc244bf93d`; its tree is `git rev-parse 7f13b90^{tree}` |
| round | `R5-20261009-s4-user-operability` |
| scope | exactly one confirmed defect (**D1**) repaired, then independently checked |
| independent verdict | `.hgk/rounds/R5-20261009-s4-user-operability/d1repair/D1_INDEPENDENT_VERDICT_V2.json` |
| the contract that checker executed | `.hgk/rounds/R5-20261009-s4-user-operability/d1repair/CONTRACT-verify-D1.v2.md` |
| superseded first contract (kept deliberately) | `.hgk/rounds/R5-20261009-s4-user-operability/d1repair/CONTRACT-verify-D1.v1.md` |
| writer order | `.hgk/rounds/R5-20261009-s4-user-operability/d1repair/WO-WS-A-codex-writer.md` |
| provenance audit of the defect class | `.hgk/rounds/R5-20261009-s4-user-operability/far/D1_PROVENANCE_AUDIT.md` |
| evidence manifest — every round artifact, delivered or withheld, each with a hash | `.hgk/rounds/R5-20261009-s4-user-operability/EVIDENCE_MANIFEST.json` |

## The defect (D1)

`tools/perf_budget.py` prints a `historical` block, commented as the recorded verdicts of earlier stages.
That block read **no stored value at all**: it re-measured the live corpus and printed the result as if it
were the record. The same field therefore took different values in different checkouts — observed live
readings `343547 / 368432 / 370091 / 372224 / 372935 / 375068` against a committed record of `343547` —
while the adjacent comment claimed the number was *preserved verbatim*. That contradicts the owner ruling
`S2_HISTORICAL_FAIL: PRESERVE` and the committed artifact `.hgk/artifacts/s2/PERF_BUDGET.json`
(`context_bytes_per_artefact = 343547`, verdict `FAIL`). `tests/test_perf_budget.py` could not catch it:
it hard-coded the expected number and asserted only the metric name.

## What changed

1. A `historical` row's `value` is now the **recorded** number, read at run time from the file its
   `origin {file, field}` names, with `recorded: true`. The live reading is **kept separately** in
   `measured_now`, so the drift is visible instead of disguised.
2. A row with no recorded counterpart sets `recorded: false` and states in plain text that its value is a
   live measurement, not a recorded one. No record is fabricated.
3. **No threshold, budget or voting metric changed** — verified byte-identical against the parent.
4. Four regression tests were added; the expectation is read from the recorded file at test time and is
   never hard-coded.

## Subject files, pinned by digest

| file | sha256 |
|---|---|
| `tools/perf_budget.py` | `f90c3d8d6061f55b9807c2e8740998f98124b56fbcb5c42397f459c4368ff015` |
| `tests/test_perf_budget.py` | `6c0d21fa8ce6c0a047539d2333973b88a75eea68c82ce031a96381749791d270` |

## Acceptance criteria — run these yourself, do not trust this file

```bash
git clone --branch r5-s4-packreader https://github.com/shw097-team/PIPD-LS-SP.git pipd-accept
cd pipd-accept

# A1 the digests above match
python -c "import hashlib,pathlib;[print(f,hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()) for f in ['tools/perf_budget.py','tests/test_perf_budget.py']]"

# A2 the recorded value is invariant, and the live reading is disclosed separately
python tools/perf_budget.py --check
#   historical row must read: value=343547 recorded=true origin={file,field} measured_now=<this checkout's own reading>

# A3 the record really is read from the file it names (perturb a COPY, never the repo)
cp -r . /tmp/pipd-perturb && cd /tmp/pipd-perturb
python - <<'PY'
import json,pathlib
p=pathlib.Path('.hgk/artifacts/s2/BYTES_PER_ATOM_BASELINE.json')
d=json.loads(p.read_text()); d['pi_bytes']=1
p.write_text(json.dumps(d))
PY
python -m unittest tests.test_perf_budget
#   must go RED; a green suite here means the test is inert
cd - && rm -rf /tmp/pipd-perturb

# A4 no regression, and the branch is green where the parent is green
python -m unittest discover -s tests
#   expect: Ran 283 tests ... OK (skipped=4)

# A5 no threshold moved against the parent
git diff 7f13b90 HEAD -- tools/perf_budget.py
#   budgets and voting_metrics must be untouched

# A6 the repository's own spec and projection gates
npx openspec validate --changes --strict
python tools/build_publication_manifest.py --check --commit "$(git rev-parse HEAD)" --tree "$(git rev-parse HEAD^{tree})"
#   expect: violations: []
```

## What was NOT done, and where this could still be wrong

- The independent check was performed by a **different model and a different lane from the maker**
  (`gpt-6.1-sol`, `openai-codex` OAuth, Hermes-native, read-only) against a contract written for it. It
  returned `ALL_PASS`: 9 of 9 properties `RE_DERIVED`, `DISAGREED=0`, `UNCERTAIN=0`. Its first pass over an
  earlier contract returned `FAIL_CHALLENGE`, and that pass's two disagreements were **defects in that
  contract, not in the code**. Both contracts and both verdicts are published side by side so a verifier can
  judge that call rather than take it.
- Seven raw transcripts exceed the evidence threshold and are **withheld with a recorded hash** rather than
  committed; `EVIDENCE_MANIFEST.json` names each one with its size and sha256.
- No deployment, publication or production operation was performed.
- The suite carries pre-existing failures in some environments: run inside a working tree that holds deep
  round artifacts, Windows path limits break two tooling tests. In a clean clone the suite is green. That is
  the parent's property, not this candidate's; `EVIDENCE_MANIFEST.json` records which runs were in which tree.
- The round's own `openspec/specs/` directory is empty, as it is for every other change in this repository —
  changes are kept as validated proposals in `openspec/changes/`, which is the repository's convention, not
  a gap left by this round.
- Four acceptance cases in the officer's report were `NOT_RUN`. Two of them (its labels B4 and B5) were
  re-run after this round and both are now `PASS`; the runs, the harnesses, and **two of the maker's own
  earlier results that were retracted** are in `.hgk/rounds/R5-20261009-s4-user-operability/ao/`
  (`rerun_b4_verdict.json` carries the verdict and the retractions). `A10` (symlink escape) remains
  `NOT_RUN` because it cannot be closed on this host: `os.symlink` raises `OSError WinError 1314`, the
  account lacks the privilege. `UAT-10-source` does not apply in source mode by design.
- Re-running B4 also showed that **no CLI subcommand surfaces an incomplete installed schema set**: the
  guard lives in `registry.load_registry()` and works, but `src/pipd_ls_sp/cli.py` never calls it, so
  `doctor` cannot report a missing schema. That is disclosed as an observation. It predates this repair,
  no product file was changed for it, and it is left for the external verifier to weigh.

## Claim ceiling for this round

| claim | state |
|---|---|
| `D1_REPAIR_LOCALLY_VERIFIED_BY_INDEPENDENT_CHECKER` | **claimed**, scoped to the published contract and the pinned digests |
| `ARTIFACT_PUBLICLY_CONSUMABLE` | **claimed** — verified by anonymous clone |
| `INDEPENDENT_PASS` | **NOT claimed by the maker** — the maker does not sign its own acceptance |
| `PUBLICATION_APPROVED` | **NOT claimed** |
| `RELEASED` | **NOT claimed** |
| `PRODUCTION_VERIFIED` | **NOT claimed** |

Granting any of those is the external verifier's act, not this round's.
