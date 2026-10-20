# v13 → R3 delta (full-coverage continuation)

Appended to the same OpenSpec change, as with `V10_DELTA.md`. The v13 change itself was validated before
this round; this records only what R3 added and what it deliberately did not.

## Track A — merge qualification (`bedc119`, unchanged tree)

| Item | Before R3 | After R3 |
|---|---|---|
| Six-property review | a checklist in `84_HUMAN_REVIEW_PACK.md`; no runnable procedure | `_governance/round-20261020-r3/M4LITE/run_m4lite.py`: 24 cases (repo tests + independent probes) with per-case command/exit/observed and a before/after subject digest |
| Receipt | none | `M4LITE/receipts/M4LITE_RAW.json` — 24/24 pass, `subject_mutation: CLEAN`, verdict `HOLD_PENDING_HUMAN_SIGNATURE` |
| Remaining gate | human signature | unchanged: a signature is still required and cannot be produced by the maker |

## Track B — preview packaging (`bedc119`, no source change)

| Item | Before R3 | After R3 |
|---|---|---|
| Artefacts | none; `85_EVIDENCE_RETURN_v13.json` recorded HOLD | wheel `95e57c44…` (27,181 B) and sdist `5babefeb…` (36,278 B), built from `bedc119` via `git archive` + `build --no-isolation` |
| Install lifecycle | unverified | fresh 3.11 venv, `--no-index` install, `sbl-todo init/add/list --json` in a **separate process**, `uninstall --yes`, `pip uninstall`, residue scan: no `sbl_*` module and no console script |
| Negative | — | an empty title is refused rather than stored |
| Gate | Owner release decision | still Owner's; the round claims `FOUNDATION_PREVIEW_READY`, not released |

## Track C — first packaging slice (new branch `candidate/c3-20261020-v1` @ `39c604d`)

| Item | Before R3 | After R3 |
|---|---|---|
| Three principals | manifests and in-process isolation tests only | `sbl_sp/plugins`: deterministic ZIP builder, one skill each, three distinct identities, `plugin.json` derived from the principal's own manifest |
| Ceiling | not expressible | `claim_ceiling: HOST_PENDING` is not a parameter; `build_package(..., claim_ceiling=...)` raises `TypeError` by signature |
| Tests | none | `tests/test_sp_plugins.py` — 8 cases: identity separation, derivation, determinism, ceiling, unknown principal, read-only challenge, no smuggled corpus |
| Suite | 148 passed | 156 passed, 11/11 gates exit 0, CI `39438217104` both jobs green |
| Requirement status | not met | `HOST_PENDING`: packages exist, host receipts do not |

## Requirements touched

- "three specialised principals are mutually non-impersonating" — now also true at the packaging layer:
  distinct plugin names, per-principal permissions copied from the manifest, and a collision check.
- "no claim exceeds its evidence" — `claim_ceiling` and `host_install_state` are emitted into every
  package manifest so a downstream consumer cannot read a ZIP as an installation.
- "G-KNOW answers are locators, not authority" — unchanged; the R3 probes re-assert the three negatives.

## Not done, on purpose

441 donor rows remain dispositions (0 installed), 149 children remain `NOT_PROVEN` with locators, 38
delivery surfaces remain `HOST_PENDING`/`NOT_ADMITTED`, the eight PIPD writers were not executed, the HGK
harness was not installed, and `main` was not moved. Each of those is a named open item in
`90_EVIDENCE_RETURN_R3.json`, not an omission.
