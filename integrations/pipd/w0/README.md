# FHS W0 R4C — author-side implementation toolkit (candidate only)

**Status: candidate PR. Not canonical, not admitted, not released.** Nothing in this directory
mints an HGK permit, replaces the PIPD compiler, or claims a native effect. The 13-command PIPD
CLI is untouched; no 14th command is added.

## What is here

| Work package | Entry point | What it actually does |
|---|---|---|
| `WP-FHS-00` | `lanes/wp00/source_probe.py` | Recomputes the input ZIP/body identity, does a two-way manifest declared-vs-present check, reads the 31-source and 22-upper identity files, records the three repos' local vs remote head drift and a host capability probe. Read-only, rerunnable. |
| `WP-FHS-01` | `lanes/wp01/authority_router.py` | Classifies sources into `CANONICAL_ORIGINAL / GOVERNANCE_MIRROR / SKILL_SIDECAR / HISTORICAL_ARCHIVED / AUTHOR_CANDIDATE`; refuses mirror-as-authority and skill-as-permit; emits typed scope HOLDs. |
| `WP-FHS-15` | `lanes/wp15/spec_pipeline.py` | Generates three heterogeneous SPECs (Product / Architecture / Program) plus a Goal→SPEC→W0 deliver→FUO chain with a recomputable readback digest. |
| `WP-FHS-16` | `lanes/wp16/need_occupant.py` | Default30 Need→Occupant matrix with licence, Windows-fit, consumer and NOFIT columns; translator specs for selected Donor/Method items, all `is_installer=false`. |
| `WP-FHS-19` | `lanes/wp19/supply_chain_gate.py` | Executable licence / NOTICE / SBOM / dependency / secret / CI-entry gate with typed codes and non-zero exit. Author-side only: `wp19_done=false`. |
| `WP-FHS-21` | `lanes/wp21/trace_runner.py` | 96 typed Oracle fixtures + declarative runner, S1–S5 seam contract validation, 22 WP / 36 edge / E26 / 84 card / 25 wave-join checks, W1–W4 consumer handoff. |

## Reproduce

```bash
python integrations/pipd/w0/reproduce.py --source-root /path/to/FHS_PIPD-LS-PKG_W0_R4C
```

`reproduce.py` runs the six entry points and all six unittest suites against the package you
point it at, writes per-step logs under `runs/<timestamp>/`, and exits non-zero on the first
failure. The expected input identity is ZIP
`f3838fb095e56ea8d636e5c52f4bd69e9d529d110569b87376c168ea35ab2a2a` and body
`56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a` (463034 bytes, 50 chapters).

## Measured in this round

- 152 parent-rerun unit tests across the six lanes, all passing (`tests/parent_rerun/` in the round root).
- Goal→SPEC→FUO: 11 declared chains, 11 joined to a real original requirement id and a typed
  fixture with the same subject, 0 missing.
- Oracle96: 96/96 typed rows match their declared first-fail; the 288-row archived replay is
  reconciled row by row.
- Seams: S1–S5 declared, all five sealed in the source package; original reader ACK **not observed**.

## What is NOT claimed

`PIPD_CANONICAL`, `HGK_ADMITTED`, `HOST_NATIVE_E2E`, `PROTECTED_CHECKER`, `RELEASED`, `WP19_DONE`,
`TraceClosure` beyond `AUTHOR_STATIC` — none of these are claimed here. The original SBL PIPD /
Program reader has not accepted these bytes. 39 carried holds stay open, plus the round's own
scoped holds listed in `docs/HOLD_LEDGER.json`.
