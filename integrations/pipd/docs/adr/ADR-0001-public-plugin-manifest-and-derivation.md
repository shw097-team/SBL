# ADR-0001 — The package root manifest is the official Agent Plugins 1.0 manifest

- Status: ACCEPTED (Stage B candidate; nothing is published by this decision)
- Date: 2026-10-12
- Scope: `packaging/public-plugin/**`, `tools/build_public_plugin.py`,
  `tests/test_public_plugin_packaging.py`

## Context

The Agent Plugins 1.0.0 vendor schema (sha256
`0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883`, 1805 bytes) permits only
`$schema, name, version, description, author, homepage, repository, license, keywords, extensions`,
requires `["$schema","name"]` and sets `additionalProperties: false`. The former package root was
PIPD's own internal manifest (`PIPD-PUBLIC-PLUGIN-MANIFEST/1`, keys
`plugin_id/display_name/skills/official_schema_sha256/publisher/icons/release`). As the plugin root
`plugin.json` that document is rejected by the vendor schema, so it cannot be the root.

## Decisions

1. **Two manifests, one package.** `plugin.json` is the official manifest; PIPD's release
   bookkeeping is `plugin.release.json`, embedded verbatim in the manifest's
   `extensions["com.pipd.s4"]` namespace. The builder refuses if the two disagree
   (`RELEASE_EXTENSION_MISMATCH`) and validates both: the official manifest against the vendor
   schema, the bookkeeping against the locally authored `plugin.schema.json` subset.
2. **The vendor schema is byte-locked, not vendor-validated.** `vendor-plugin.schema.json` is a
   byte copy of the downloaded specification schema. The builder requires the manifest `$schema` to
   equal the vendor `$id` (`OFFICIAL_SCHEMA_ID_MISMATCH`), validates the manifest against those
   bytes with its own subset validator, and refuses when the vendor bytes drift from the locked
   digest or when the digest pinned in `extensions["com.pipd.s4"].official_schema_sha256` (and in
   `plugin.release.json`) does not match the bytes validated against
   (`VENDOR_SCHEMA_DIGEST_MISMATCH`). This *renames* the old
   `OFFICIAL_SCHEMA_DIGEST_MISMATCH`: the pin now names the official vendor schema, not the local
   subset, whose legacy description sentence about that pin is superseded here (the subset file is
   outside this change's write set and keeps its role as the release-bookkeeping validator).
3. **Every skill needs an owner-approved derivation.** The eight `SKILL.md` packs carry
   non-portable frontmatter (`version/owner/triggers/schemas/references/tests`), while the Agent
   Skills specification lists exactly
   `name/description/license/compatibility/metadata/allowed-tools`. A byte-copy projection is
   therefore impossible: the build REFUSES (`OWNER_INPUT_MISSING`) unless each skill has a record
   whose `source_sha256` matches the frozen ledger and whose `approved_by`/`approval_receipt` are
   real, and the projected skill body stays byte-identical
   (`DERIVED_WITH_OWNER_APPROVAL` in the mapping).
4. **The icon is generated, never committed as an opaque binary.** A deterministic RGBA PNG is
   written in-repo by a stdlib writer (zlib + struct) and decoded structurally (signature, IHDR,
   every chunk CRC, inflated IDAT). Residual: owner brand assets, the vendor's own validator and
   the Agent Plugins Portal icon scan remain **NOT_EXECUTED**.
5. **Stdlib only.** The frontmatter parser (YAML-free), the subset schema validator and the PNG
   writer/decoder are ours; the build carries no third-party dependency and no network. This
   deviates from the triple-upgrade blueprint's hash-pinned Pillow/jsonschema/PyYAML proposal and
   is disclosed as that deviation: the local validators are not the vendors'.

## Consequences

- The refusal order for owner-gated inputs is unchanged: missing derivation record, unpinned
  official/vendor schema digest, unpinned publisher identity, unpinned or invalid icon.
- `claim_ceiling` stays `LOCAL_PACKAGER_PASS_ONLY` and `official_portal_verification` stays
  `NOT_EXECUTED` in the receipt: this lock is a local byte lock, not a portal or vendor approval.
