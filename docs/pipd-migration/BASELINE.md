# PIPD → SBL absorption baseline (C0)

**Record ID:** `U04-BASELINE-2026-11-02-r1`
**Measured:** 2026-11-02 (Asia/Taipei) · **Method:** one read of each `main`, one local inventory, no re-verification loop.
**Status:** `C0_MEASURED / D0_RECOMMENDED_PENDING_OWNER` — no owner signature for D0 exists in this record.

This is the C0 deliverable of the execution plan `SBL-PIPD-U04-EXEC-CONTROL-2026-11-02-r1`. It records what the
two repositories are today, which commit is proposed as the D0 canonical baseline, and what a later migration
must not silently change. It does **not** cut over the writer.

## 1. Sources read (once, at these SHAs)

| repository | `main` at read time | role |
|---|---|---|
| `shw097-team/SBL` | `e166d67cf4ae7ed318df11292e906e324dc4fc9e` | absorption target, `sbl-v01` 0.1.1rc1, MIT |
| `shw097-team/PIPD-LS-SP` | `8a0c85225323a7e7c61bfd6aa99e4cd3dc87419a` | current canonical compiler, `pipd-ls-sp` 0.1.1a4, Apache-2.0 |
| `shw097-team/Fabric` | `59bb783dd0d28cc66ce5ba58a4e3a167fe7eb9f5` | FHS entry (L1 navigation closed, unchanged by this round) |
| `shw097-team/HG-KSEOS` | `0143b50331f7fef007a5921bb743e61f59b0a7bd` | native control plane, not touched |

Local source candidates were checked once: `C:\Projects\pipd-ls-sp` **does not exist** on this host. The
working clone at `C:\Projects\Agent_Workspace\PIPD` is on branch `candidate/r21-far-20261101`
(`3b48c262f4174217cb35391c6da22bc53f068755`), is dirty, and is **not** `main`; it was read for comparison only
and is not the source of the absorbed tree.

## 2. What PIPD `main` contains

| item | measured | note |
|---|---|---|
| Python package | `src/pipd_ls_sp/` — 13 modules | import namespace `pipd_ls_sp`, console script `pipd` |
| contract families | **19** `*.schema.json` + `registry.json` | `registry.EXPECTED_FAMILIES == 19` |
| skills | **8** (`skills/*/SKILL.md`) | pipd-assurance-tqaep, -authority-source, -execution-contract, -package-project, -pd-bind, -pi-compile, -profile-tailor, -route-intake |
| CLI | **13** commands | `init, intake, profile, compile-pi, bind-pd, compile-ecp, compile-tqaep, validate, doctor, project, export, diff, repair` |
| test modules | 52 `tests/test_*.py` | plus fixtures and examples |
| licence | Apache-2.0 + `NOTICE` | `OWNER_LICENSE_DECISION.yaml`, `SBOM.cdx.json`, `PROVENANCE.md` present |
| releases | 4 preview releases + `b1-promote-20261028` tag | immutable assets, not rewritten by this round |
| open PRs | #26, #22, #20, #19, #15 | in-flight work; C4 inventory, untouched here |

## 3. The 13-vs-14 CLI question, measured

The plan flags a 13/14 CLI discrepancy. It is real and it is **not** on `main`:

| ref | SHA | CLI count | state |
|---|---|---|---|
| `PIPD-LS-SP` `main` | `8a0c852…` | **13** | the published line; every release tag descends from it |
| `candidate/r21-far-20261101` | `3b48c26…` | **14** (adds `compile-cc`) | unmerged candidate; 30 files changed against `main` (+981/−1085) in `src/`, `schemas/`, `skills/` |

So the "14th command" belongs to an unmerged candidate, not to the canonical line. Absorbing `main` does not
change any CLI contract and does not decide the candidate's fate. If the owner later selects R21 as D0, the
30-file delta is re-absorbed on top of this tree — a bounded re-copy, not a redesign.

## 4. D0 decision table (proposal, not a decision)

| source | SHA | CLI | proposed role | why |
|---|---|---|---|---|
| `PIPD-LS-SP@main` | `8a0c852…` | 13 | **proposed D0 baseline** | it is the only line with release tags and published assets; absorbing it changes no ABI |
| `candidate/r21-far-20261101` | `3b48c26…` | 14 | not absorbed | unmerged, unreleased, and its `compile-cc` would need an owner-approved ABI amendment |

`D0` stays `PENDING` until a named SBL/PIPD owner records the choice. Nothing in this PR transfers the writer,
publishes a package, or marks the entry ratified.

## 5. Absorption scope as built (C1 candidate)

Copied verbatim from `PIPD-LS-SP@8a0c852` into `integrations/pipd/` (318 files, 2.34 MB):

`pyproject.toml`, `setup.py`, `MANIFEST.in`, `requirements.lock`, `src/pipd_ls_sp/`, `schemas/` (19 + registry),
`skills/` (8), `tests/`, `fixtures/`, `examples/`, `packaging/`, `tools/`, `docs/`, `LICENSE`, `NOTICE`,
`README.md`, `PROVENANCE.md`, `SBOM.cdx.json`, `OWNER_LICENSE_DECISION.yaml`, `ACCEPTANCE.md`,
`PREVIEW_NOTES_*.md`.

Deliberately **not** copied: `.hgk/**` (governance receipts), `dist/**` (release artefacts), `openspec/**`
(change archive), evidence-return bundles, worktrees, `.github/**`, and the Git history. Those stay readable in
the historical repository at the SHA above.

Eight further files were dropped by one host-repository rule: SBL refuses to ship `.sh`/`.ps1` scripts (an
existing invariant test, because LF normalisation would break them), so `examples/first-run/run.sh`, `run.ps1`,
the five `tools/kanban_*.sh` helpers and the test that executes the first-run script were not carried. That is a
carve-out of this migration, not a change to SBL's rule; `integrations/pipd/MIGRATION-NOTES.md` states it next
to the snapshot.

## 6. Verification performed here (C2 candidate)

Run with Python 3.11 in two throw-away environments: one for the absorbed tree, one that installs **only** the
built wheel.

| check | result |
|---|---|
| build from `integrations/pipd` (`tools/build_dist.py`) | `pipd_ls_sp-0.1.1a4-py3-none-any.whl`, 287 844 bytes, sha256 `47b58d72…`, 41 members |
| install wheel into a clean venv with **no SBL package** | `import pipd_ls_sp` resolves from `site-packages`, `pipd --help` lists 13 commands |
| independent-use negative | `import sbl_core` in that venv → `ModuleNotFoundError` (PIPD does not need SBL) |
| contract registry from the wheel | `EXPECTED_FAMILIES == 19`; `pipd doctor` reports `families: 19`, `schema_source.mode = INSTALLED` |
| absorbed product test subset | **494 tests, 0 failed, 0 errors, 19 skipped** (Python 3.11, run at this branch) |
| round-evidence tests | 12 modules, 83 tests fail because they assert on `.hgk/`, `dist/` and release assets that were not migrated (§7) |

## 7. Test scope, stated so nobody reads it as "all green"

The absorbed suite is 51 modules. Fourteen are excluded from the product signal:

- **2 governance-input modules** — `test_oracle_disagreement.py`, `test_evidence_manifest.py` — read
  `.hgk/knowledge/…` and `.hgk/artifacts/evidence_manifest.json`, which are governance scaffolding and were not
  migrated by design.
- **12 repository-state modules** — perf budget, post-release web mount, quarantine review, R10 evidence,
  R5R3 install-route identity, R6 doc identity, S4EXT artefact reproducibility, S4EXT release provenance,
  spec-delta crosswalk, technology admission, tooling execution, TT summary. They assert on release assets,
  `.hgk` registers, or pinned historical document identities of the old repository.

The remaining 37 modules (contract schemas, CLI surface, pipeline, workspace, validate, requirements,
profiles, projection, repo-context, export, registry and the release-surface checks that do not need retired
artefacts) run **494 tests with 0 failures and 19 skips**. That is the compiler's own contract suite; the
exact command is in §8.

## 8. How to reproduce

```bash
cd integrations/pipd
python3.11 -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
python tools/build_dist.py                    # writes dist/pipd_ls_sp-*.whl
python -m pytest -q --ignore=tests/test_oracle_disagreement.py \
                      --ignore=tests/test_evidence_manifest.py
python -m venv /tmp/indep && /tmp/indep/bin/pip install dist/*.whl
/tmp/indep/bin/python -c "from pipd_ls_sp import registry; assert registry.EXPECTED_FAMILIES == 19"
```
