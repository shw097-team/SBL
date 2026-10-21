# R4 delta — sbl-v01-candidate-build

Round 4 (order `SBL-R4-20261020-C3-FIVE-TOOLS-SWOF-W12`) continues the same change. No new OpenSpec
change is opened: this is `CONTINUATION`, and creating a second change would give the same work two
identities.

## Modified capabilities

### `plugin-packaging`

- **Before**: `plugin.json` carried `"schema": "SBL-AGENT-PLUGIN/1"`, no `$schema`, and principal
  fields at the top level; skills lived at `skills/sbl-<principal>` while their frontmatter declared a
  different name.
- **After**: portable manifest validated against a vendored copy of
  `agent-plugins.org/schemas/1.0.0/plugin.schema.json`; principal metadata under
  `extensions["org.sbl.principal"]`; `skills/<frontmatter-name>/SKILL.md`.
- **Requirement delta**: `R4-REQ-PLUGIN-PORTABLE-MANIFEST` — a package that no conforming host can
  parse must fail at build time, not at install time.

### `distribution-integrity` (new)

- **Requirement**: `R4-REQ-WHEEL-DATA` — the built wheel must contain every data file a runtime needs.
  An editable install is not evidence.
- **Why**: the wheel shipped without `sbl_sp/manifests/*.json` from the foundation release onward.

### `stack-installability` (new)

- `sbl-stack install/doctor/selftest/status/uninstall` over the composed M01..M06 core, with an
  integrity manifest and a refusal to own anything it did not write.
- Ceiling: `LOCAL_STANDALONE_INSTALL`; `host_install_state` stays `NOT_INSTALLED`.

### `harness-adapter` (new)

- `sbl-harness` declares a pinned `hg_kseos` version, a `hgk-harness-abi/1` surface, and
  probe/install/doctor/uninstall. It provides `plan/execute/verify` and **requires**
  `WorkOrder/ExecutionBinding/Permit` from the native plane; it cannot issue them.
- Ceiling: adapter installed; native effect `NOT_GRANTED`.

## Unchanged on purpose

`main` (`bedc119`), the `v0.1.0-foundation-preview` release bytes, the M4 owner receipt, and the
441/50+149/38 frozen ledgers. Re-opening any of them would be scope creep against R4 §4.

## Open

`CR-PLUGIN-SCHEMA-AUTHORITY` (B1/B2/B3), the ChatGPT private-plugin route (host-issued identity), and
SWOF W1/W2, which is SWOF's own decision.
