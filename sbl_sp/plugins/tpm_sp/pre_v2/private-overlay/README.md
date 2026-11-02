# Owner-private baseline software overlay

This is an additive source overlay for the exact retained owner baseline, not
a standalone public Plugin package. The original 24 DOC Corpus, SourceManifest,
old fixture history and private runtime data are deliberately absent. Preserve
the baseline files and canonical schema IDs. Overlay these software files only
on an isolated copy, then run `python refresh_bom.py <private-plugin-root>`.

All 14 Skill names are retained. New author routing references are source-only
design instructions. Existing v1 Skill schemas and fixtures stay byte-identical.
The package preflight now rejects stale BOM versions or any file/byte mismatch.
`scripts/pre_v2.py` is the same SBL MIT adapter as ../adapter.py. PIPD-derived
Skill software uses the original owner's engineering-output Apache-2.0 grant;
see ../upstream/PIPD-LICENSE.txt and PIPD-NOTICE.txt. Those grants do not establish
redistribution rights for the raw private DOC Corpus or excluded donor material.

Run the owner baseline's corpus verifier, unit tests, semantic replay, and final
package preflight after applying. Historical graph EDGE-001 remains a refused
counterexample. Host tests and private account update are separate operations.
The actual private Plugin ID/current release must come from its official Host.
No current account ID or credential is distributed in this overlay.
