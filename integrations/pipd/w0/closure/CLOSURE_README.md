# W0 CLOSEOUT overlay (non-normative)

This directory is an author-side closeout readback placed on top of the unchanged
`FHS_PIPD-LS-PKG_W0_R4C` package. The original 592 members are byte-identical; nothing in
them was rewritten. `CLOSURE_MANIFEST.json` at the archive root lists every member with its
sha256 and never hashes itself.

- `W0_CLOSEOUT_DECISION.md/json` - `W0_CLOSEOUT_PENDING`; six-WP-all-done is FALSE.
- `W0_TO_W1_HANDOFF.json` - `W1_SCOPED_SOURCE_DRAFT_GO` envelope (read/draft only).
- `WP16_19_SCOPED_READBACK.json` - WP16 W1-consumed selection and the WP19 real-root run.
- `BODY_ANNEX_PAIR_READBACK.corrected.json`, `ADDITIONAL_SCOPED_HOLDS_r4c.corrected.json` -
  the two stale-SHA corrections, computed from the real bytes in this archive.
- `SUPERSEDED_MARKERS.json` - the original two files are historical, not current.
- `WP19_REAL_ROOT_RAW.json`, `NEG_REAL_ROOT/` - upstream `integrations/pipd` at origin/main,
  PASS 5 / FAIL 2, with four typed negative fixtures.
- `HOLD_LEDGER_CLOSEOUT.json` - 68 holds, all open.

Claim ceiling: `AUTHOR_LOCAL_TEST`. This is not an original reader ACK, not an HGK permit,
not a protected checker verdict, not a release, and it does not make any PR merged.

## What is deliberately NOT in this repository copy

The untrimmed gate raw (`WP19_REAL_ROOT_RAW.json`) and the four mutated-tree negatives stay
outside the repository, inside the W0 CLOSEOUT archive under `closure/`, because this
repository's `AGENTS.md` rule 4 forbids committing raw lane output. The typed summary and the
ACK status in this directory are the citable evidence; the raw is one `zipfile` read away in
the archive named in the round handoff.
