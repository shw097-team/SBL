# SBL v0.1 candidate build — proposal

## Why

`SBL_PIPD-LS-PKG` (DOC-00..DOC-13) specifies a SpecBuild Loop product: Guided Spec → Governed Build →
Evidence-based Verify → Bounded Repair. No installable, testable product exists yet; the target root
`C:/Projects/Agent_Workspace/SBL` was empty and not a git repository (measured 2026-10-20).

## What changes

- Introduce one Shared Core plus six logical modules `SBLM01..SBLM06` (Goal Intake, Guided Specification,
  Governed Routing, Governed Build Bridge, Evidence Verification, Bounded Repair/Evolution).
- Introduce three responsibility-separated SPs: `TPM-SP`, `Commander-SP`, `External Challenge-SP`, with
  isolated manifests and permissions; the external checker cannot be the maker.
- Implement three modes: `STANDALONE` (default, local effects only), `PREW3_SHADOW` (read-only, NoEffect),
  `SWOF_CONNECTED` (blocked until a native receiver ACK + Permit exists).
- Ship the first real FUO as a `CLI_TOOL` (`sbl-todo`): clean install → `add --title` → `list --json` →
  restart → uninstall with no residue.
- Publish each qualified candidate plus scrubbed evidence to the public repository
  `github.com/shw097-team/SBL` for independent external acceptance.

## Non-goals

- No release/production claim; release requires a human/native gate (DOC-13).
- No installation of all 386 named donor technologies; only admitted slots (DOC-06).
- No modification of HG-KSEOS or Fabric sealed policy from inside this change.
- `SWOF_CONNECTED` is not claimed connected without a native ACK/Permit.

## Claim ceiling

`CANDIDATE_NOT_INDEPENDENTLY_ACCEPTED`. Locally measured items are labelled `LOCAL_VERIFIED`; everything
else stays unclaimed until a distinct-principal checker produces a raw verdict.
