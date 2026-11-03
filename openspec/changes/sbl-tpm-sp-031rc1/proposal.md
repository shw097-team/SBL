# CHANGE sbl-tpm-sp-0.3.1-rc.1 — rebuild the candidate against the repaired reader

**Status**: built, host-verified, evidence merged. No change to `0.3.0-rc.1` or `0.3.0-rc.2`.

## proposal.md

### Why

The previous round repaired the reader (`integrations/pipd`): `compile-ecp` stopped accepting a
caller-supplied registry, and `operation_registry.py` was added. That changed the reader's identity —
14 → 15 modules under `src/pipd_ls_sp/` plus two edited files — so **every pin set captured before
it is incomplete by construction**. The plugin's bridge (`scripts/pre_v2.py::OriginalPipd`) refuses
to call the writer unless its pin set equals the reader's files exactly (`ORIGINAL_READER_PIN_SET`)
and each digest matches (`ORIGINAL_READER_DRIFT`). A repaired reader plus an un-repinned candidate
equals a candidate that cannot run.

Separately, the pin set had to be assembled by whoever wanted to pass — the wrong direction. The
reader must issue its own identity.

### What changed

| change | detail |
|---|---|
| reader issues pins | `integrations/pipd/tools/issue_reader_pins.py` (SBL PR #35): scope mirrors the bridge, refuses a dirty tree, re-reads every file from the `HEAD` blob, emits `git_head`, per-file digests and one `pin_set_sha256` |
| pins signed | owner window `WIN-9d10aa7face0` signed `RATIFY_READER_PIN_SET` over `pin_set_sha256 f0b287dd…` (effect class `READ_ONLY_PROBE`) |
| new candidate | `sbl-tpm-sp-0.3.1-rc.1`: version bump in `plugin.json` and `.codex-plugin/plugin.json`, pins + signature shipped under `references/reader-pins/`, loader `scripts/reader_pins.py`, CHANGELOG entry |
| sealed artefacts untouched | `0.3.0-rc.1` (`c4181e24…`) and `0.3.0-rc.2` (`3a9da65…`) keep their bytes |

### Not in scope

No change to the 19 canonical families, the 13 CLI verbs, the ECP ABI or `--require-four`. No grant,
no native effect, no live checker, no `FHS_PIPD-LS-PKG_v2` package.

## tasks.md

- [x] reader pin issuer implemented, tested (4 tests), merged (SBL `a5d3a767`)
- [x] pin set issued from a clean checkout: 35 files, `pin_set_sha256 f0b287dd…`, `git_head a5d3a767`
- [x] pin set signed by the owner window (1 of 20 ops)
- [x] candidate rebuilt: 180 members, 14 `SKILL.md`, no bytecode, `plugin.json` 0.3.1-rc.1
- [x] candidate's own author suite: 186 passed (same count as rc.2)
- [x] host chain: install → loaded → skill used → nontrigger → rollback to rc.2 → restore 0.3.1-rc.1
- [x] archived with `SHA256SUMS`

## design.md

### Why a version bump instead of patching rc.2 in place

The control plan forbids overwriting a sealed candidate, and it is also technically wrong: the pin
set is content-addressed, so a candidate whose reader changed is a *different candidate*. `0.3.1-rc.1`
is that candidate.

### What the owner signature does and does not mean

It records **who ratified the reader identity** (a specific 35-file, one-digest statement at a named
commit). It is not a grant, not a checker receipt, and it does not make any effect executable. The
runtime check remains the digest comparison in `OriginalPipd`.

### Residual

`0.3.1-rc.1` inherits the container sandbox mode `RUNTIME_SECCOMP_UNCONFINED` and the Windows native
host's `HOST_124_HOLD`. Both are host limits, recorded, not repaired here.
