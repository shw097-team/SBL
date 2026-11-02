# PIPD-LS-SP v0.1.0-preview.2

**This is a repaired successor to `v0.1.0-preview.1`, not a rewrite of it.** `v0.1.0-preview.1` is left
exactly as published; this tag supersedes it, as the owner grant requires.

## What is in these bytes

| | |
|---|---|
| Wheel | `pipd_ls_sp-0.1.0-py3-none-any.whl` |
| Wheel sha256 | `d6c3e295f817b50108b1232a120564c18b517864ad1ad19c4f8d915f396d364f` |
| Built from commit | `1ab17d1eac02a86eda0770cb7dcf25b1a4389c6c` |
| Licence | Apache-2.0 |

## What changed relative to v0.1.0-preview.1

`v0.1.0-preview.1` shipped with two defects that made the core chain unusable from an installed wheel
outside the source tree. Both are repaired in these bytes:

1. **CE-1 - `validate` could not find the schemas it shipped with.** Schema resolution is now
   `OVERRIDE -> INSTALLED -> SOURCE`, so a wheel installed into a clean virtual environment resolves
   the schemas packaged *inside the wheel* and reports where it found them.
2. **CE-2 - the compilers' own stdout was not schema-valid.** A non-record sidecar
   (`_profile_meta`) was being emitted into records the schemas reject. The hash-exclusion set and
   the stripped-sidecar set are now separate, so the compilers' own stdout validates.
3. **CE-CODEX-TRACE-WIDENING** - an undeclared `trace` key was accepted on `PD-PKG`/`ECP`/`TQAEP`.
   It is now rejected by `additionalProperties` and named in the findings.

The wheel bytes themselves were unchanged between v0.1.0-preview.1 and this tag for the packaging layer;
what changed is the library code inside it.

## DEL-018 is closed in this tree

`RELEASE_MANIFEST@1` had failed since the R3 crosswalk: the publication projection carried no
disposition for every product path in the tree. It now dispositions 252/252 with zero violations and
`--check --current` exits 0. The regeneration removed 1085 stale `.hgk/` round-artifact entries and
**no product path**; that is asserted mechanically, because a manifest that covers less would also
pass.

## Claim ceiling - read this before quoting anything here

Published capability: `OWNER_AUTHORIZED_OPEN_SOURCE_PREVIEW_BETA_PUBLISHED`.

This is **not** a full gate pass. Not granted, and must not be quoted as granted:
`FULL_S0_S4_INDEPENDENT_PASS`, `G_RELEASE_FULL_PASS`, `PRODUCTION_VERIFIED`, `S5_RUNTIME_READY`,
`ALL_HOSTS_LIVE_CERTIFIED`. No release signature or build attestation by an external signing
identity is attached, and no host-native (S5-S8) certification has been performed.

## Known limitations

1. The preview is an S4-stage open-source preview, not a production release.
2. DEL-018 is closed in this tree; the superseded tag's failure remains on record against it.
3. The default publication attestation sidecar in the tree attests an R3-era subject, not this tag.
4. No dependency-vulnerability scan result is claimed for this tag beyond the factory scans below.
5. `pip install` from PyPI is not offered; take the wheel from this release and verify its hash.
6. Windows-first: the tooling is verified on Windows with CPython 3.11; other hosts are untested.
7. The `Doctor`/composition surfaces remain the documented S0-S4 scope, not the full S5-S8 chain.

## Factory evidence carried with this tag

- history secret scan over 2339 objects and the worktree: 0 hits, CLEAN
- deny-list scan: PASS, 0 writer usages inside the R4 scope
- full test suite on the release tree: see the round record
- licence: Apache-2.0, with the corpus-derived vs agent-authored split kept in `NOTICE`
