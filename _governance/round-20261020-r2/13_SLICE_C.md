# Slice C (bounded) — packaging, CI, docs

Root: `C:/Projects/Agent_Workspace/SBL` only. Do not modify `sbl_core/`, `sbl_sp/`, `sbl_cli/`, `tests/`.

## 1. `pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "sbl-v01"
version = "0.1.0"
description = "SBL / SpecBuild Loop v0.1 — candidate build (not released)"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
sbl-todo = "sbl_cli.sbl_todo:main"

[tool.setuptools]
packages = ["sbl_core", "sbl_sp", "sbl_cli"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q -p no:cacheprovider"
```
Do NOT add a licence field (the licence is an owner decision, still open).

## 2. `.github/workflows/ci.yml`
- name `ci`, triggers `push` on branches `["main", "candidate/**"]` and `pull_request` on `main`.
- job `test`, `strategy.matrix.os: [ubuntu-latest, windows-latest]`, `python-version: ["3.11"]`.
- steps: checkout, setup-python, `pip install -e .`, `python -m pytest -q -p no:cacheprovider`,
  `python tools/verify_source.py --verify` (this step must run only on the windows runner: `if: runner.os == 'Windows'`,
  because the source mirror path is Windows-only — say so in a comment).
- No secrets, no deploy step, no write permissions: add `permissions: contents: read` at workflow level.

## 3. `docs/ARCHITECTURE.md`
Module map table (SBLM01..06 → file → one-line responsibility), the SP separation table (three manifests →
permissions → forbidden), the mode table (STANDALONE / PREW3_SHADOW / SWOF_CONNECTED → effect allowed /
refusal code), the evidence flow (gate → raw receipt → independent checker), and one ASCII diagram of
`Goal → Spec → Route → Bridge → Verify → Repair`. State the claim ceiling: `CANDIDATE_ONLY`.

## 4. `docs/JOURNEYS.md`
Exact copy-pasteable commands for the three journeys, each with its expected output and its negative case:
- GJ01: `python -m sbl_cli.sbl_todo init --data-dir ./.demo`, `add --title "buy milk"`, `list --json`,
  separate-process readback, `add` duplicate (exit 3), `uninstall --yes --data-dir ./.demo`, residue check.
- GJ02: the fixture recipe (temp git repo, bind, prepare, apply, red→green, out-of-writeset refusal, stale-head
  refusal, rollback) as a short script.
- GJ03: `python -c` snippet that loads `skills/sbl_todo/skill.json` through `sbl_sp.bridge.SkillBridge`,
  shows discover/match true and match false, `effective_load` refusal when `provider_on` is False, and `unload`
  with empty residue.
Every command in this file must be one you actually executed while writing it; put the observed output under it.

## 5. `README.md` (rewrite, keep it honest)
Sections: what this is (SBL / SpecBuild Loop v0.1, candidate build), status + claim ceiling
(`CANDIDATE_ONLY`, not released, not production, no independent acceptance claimed), what is implemented
(one paragraph + the module table pointer), install (`pip install -e .`, `python -m sbl_cli.sbl_todo --help`),
the three journeys (pointer to docs/JOURNEYS.md with the one-line GJ01 command), the governance model (HG-KSEOS is
the only control plane; maker≠checker; evidence under `evidence/`), repo layout, and a "not in scope" list
(no SWOF connection, no 386 donors, no release). Licence: state explicitly `LICENSE: pending owner ruling`.
No absolute Windows paths except the source-mirror note.

## Acceptance
1. `python -m pytest -q -p no:cacheprovider` → all green (report the exact count).
2. `python -c "import tomllib,pathlib;tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))"` → exit 0.
3. `python -c "import pathlib;print(pathlib.Path('.github/workflows/ci.yml').read_text(encoding='utf-8')[:40])"` → exit 0
   and state PyYAML NOT_RUN if it is not installed (do not add a dependency).
4. Every command quoted in `docs/JOURNEYS.md` executed at least once; paste the observed output.
No network, no git write verbs, no writes outside the repo root.
