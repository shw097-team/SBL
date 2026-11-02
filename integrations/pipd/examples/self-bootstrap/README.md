# Self-bootstrap example (source-constrained)

WorkOrder: `WO-S4-SELFBOOT-04` (`POSTRELEASE-20261011-s4-narrow-repair`). Candidate-only.

This example drives **this repository's shipped CLI** through the real compiler chain

    intent -> compile-pi -> bind-pd -> compile-ecp -> compile-tqaep -> validate

using a frozen intent card, a self-contained clause-source file, and a minimal read-only
`RepoContext`. Nothing is hand-authored: the transcript and the negative output are the **raw**
stdout/stderr/exit of an actual run, and every digest is recomputed from that run.

## What this proves

* The repository is **self-bootstrapping on the positive path**: a fresh, isolated workspace can be
  created (`init`) and driven through the documented commands with no interactive input and no
  model on the compilation path.
* The chain is **replay-deterministic for identical rooted inputs**: no timestamp enters a digested
  field, so the **same intent, the same clause source and the same `RepoContext.root`** produce
  identical artefact digests across runs (`digests.json`). The determinism is bounded on purpose:
  PD binds an absolute `RepoContext.root` **by design**, and ECP is derived from PD, so a *different*
  root legitimately yields different PD and ECP digests while PI and TQAEP stay identical. That is
  **environment binding, not nondeterminism** — the same inputs at a different root are not the same
  inputs.
* Refusals are **typed and non-zero**: a missing source locator is refused `AUTHORITY_UNKNOWN`, and
  a stale `RepoContext` is refused `STALE_PROVIDER`; both are captured verbatim in
  `negative_stale_context.txt`.

## What this does NOT prove

* **Not independent acceptance.** The TQAEP record is a *design-time* candidate
  (`claim_ceiling = TQAEP_DESIGNED`); a checker receipt string is recorded, not verified. A live S5
  runtime checker must re-run it before any independent acceptance is claimed.
* **Not a release.** No commit, push, tag or release is produced; this is a candidate artefact.
* **Not the whole lifecycle.** Only the S1 LITE vertical slice is exercised. S0 source freeze, S2
  technology admission, S3 surface/GENIE projection and any runtime stage are out of scope.
* **Not the external standard.** It does not restate, re-derive or copy any body of
  `PIPD-LIFECYCLE-SPEC@1.1.0`, the Blueprint, the 11 packages or the 10 documents; it only binds a
  self-contained local clause source (see `docs/NORMATIVE_SOURCE_MAP.md`).
* **Not a claim of correctness of the repository's own logic.** It shows the pipe runs and refuses
  the two named negative cases; it is not a proof of the compiler's semantics.

## Layout

| Path | Role |
|---|---|
| `input/intent.json` | minimal intent card (goal + one source locator) |
| `input/source_clauses.txt` | the self-contained clause source the atoms are compiled from |
| `input/repocontext.json` | minimal read-only RepoContext template |
| `run_selfbootstrap.py` | the driver (creates the workspace in an isolated root, runs the chain) |
| `digests.json` | recomputed digests of the actual run |
| `transcript.txt` | REAL stdout/stderr/exit of the positive run |
| `negative_stale_context.txt` | REAL output of the two negative cases |

## Run

```
PYTHONPATH=<repo>/src <interpreter> examples/self-bootstrap/run_selfbootstrap.py \
    --root <disposable-dir-outside-the-repo>
PYTHONPATH=<repo>/src <interpreter> examples/self-bootstrap/run_selfbootstrap.py \
    --root <disposable-dir> --negative missing-source     # expect non-zero, typed
```

`--root` is refused if it resolves inside the repository. The workspace is always created **outside**
the repository.

## Notes on non-interactive driving

One documented command, `compile-construction-contract`, is **not** a CLI subcommand (the 13-command
surface does not expose it), so it is exercised only through the pipeline API used by the unit test
`tests/test_postrelease_selfbootstrap.py`. This is stated here rather than silently skipped.
