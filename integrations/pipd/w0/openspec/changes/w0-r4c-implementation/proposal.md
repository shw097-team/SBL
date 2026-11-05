# OPENSPEC change — `w0-r4c-implementation`

## Why

The W0 r4-candidate package (`56d0df3d…`, 463034 bytes, 50 chapters) is a static author
candidate: it carries the three SPEC drafts, 96 Oracle contracts and the seam fixtures, but
the six W0 work packages had no runnable entry point. A reader could not re-run the identity
checks, could not generate the three SPECs from the body, and could not execute the
supply-chain or oracle gates. This change adds that executable layer without touching the
canonical PIPD compiler, its 13 CLI commands, its 19 schema families, or the source package.

## What changed

| Path | Type | Summary |
|---|---|---|
| `integrations/pipd/w0/lanes/wp00/` | added | Source probe: ZIP/body identity, two-way manifest coverage, 31 source / 22 upper identity, three-repo head drift, host probe. |
| `integrations/pipd/w0/lanes/wp01/` | added | Authority router: five authority classes, mirror/skill refusal, typed scope HOLDs (189 routed entries). |
| `integrations/pipd/w0/lanes/wp15/` | added | Three-SPEC generator + Goal→SPEC→FUO chain with recomputable readback digest. |
| `integrations/pipd/w0/lanes/wp16/` | added | Default30 Need→Occupant matrix, translator specs (`is_installer=false`). |
| `integrations/pipd/w0/lanes/wp19/` | added | Supply-chain gate: licence, NOTICE, SBOM, dependency, secret, CI entry. `wp19_done=false`. |
| `integrations/pipd/w0/lanes/wp21/` | added | 96 typed Oracle fixtures + runner, S1–S5 seam checks, 22/36/E26/84/25/22, W1–W4 handoff. |
| `integrations/pipd/w0/reproduce.py` | added | One replayable entry for all six lanes; non-zero on first failure. |
| `integrations/pipd/w0/docs/` | added | Three generated SPECs, Goal→FUO, ECP/TQAEP design, W1–W4 consumer handoff. |
| `integrations/pipd/w0/openspec/` | added | This change record. |

Nothing is modified in place: the change is additive, under a new directory, and every
added test lives in that directory rather than in the existing pinned `tests/` tree.

## Affected scope

- Original ids: WP 22 / E 36 (E26 = WP-FHS-19 → WP-FHS-14), 84 cards (25 wave-join
  ambiguous), 22 required trace, 96 Oracle cases, 31 sources, 485 technical identities —
  all recomputed from the package, none renumbered.
- PIPD CLI surface: unchanged at 13 commands; no new schema family.
- Source package: read-only. The r4c ZIP and its expanded tree are not copied or modified.

## Verification

- `python integrations/pipd/w0/reproduce.py --source-root <package>` → six tool steps and six
  unittest suites; 152 tests; `verdict=PASS_AUTHOR_LOCAL`.
- Parent-side GSTACK gate: 21/21 invariants PASS (`I1`–`I9` in the round handoff).
- Goal→SPEC→FUO→fixture join: 11 chains, 11 joined, 0 missing.
- Negative first-fails asserted by code, not by exit status: source SHA mismatch, manifest
  member missing, remote head drift, mirror-as-authority, skill-as-permit, dual canonical,
  scope unbound, spec not heterogeneous, FUO missing, method-as-installer, licence unbound,
  NOTICE missing, SBOM mismatch, undeclared dependency, secret pattern, firstfail mismatch,
  seam field missing, E26 direction, wave count.

## Rollback

Delete `integrations/pipd/w0/`. No existing file is edited, no packaging entry is added, no
CI workflow is changed, so removal restores the previous tree exactly.

## Not claimed

`PIPD_CANONICAL`, `HGK_ADMITTED`, `HOST_NATIVE_E2E`, `PROTECTED_CHECKER`, `RELEASED`,
`WP19_DONE`, and any `TraceClosure` beyond `AUTHOR_STATIC`. The original SBL PIPD / Program
reader has not accepted these bytes; the 39 carried holds stay open.
