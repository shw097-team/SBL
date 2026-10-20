# Shipped-material inventory (R1 evidence)

Purpose: the licence file may only be signed by an owner who knows exactly what ships. This is that list,
measured from the tracked tree, not from the source corpus behind it.

## Ships, under the repository's MIT licence

| Path | What it is | Provenance |
|---|---|---|
| `sbl_core/`, `sbl_sp/`, `sbl_cli/`, `skills/` | product code: shared core, three SPs, CLI, one skill manifest | authored for this product in the HGK-governed SBL round |
| `tests/` | unit, e2e and regression tests | authored for this product |
| `tools/` | gate runner, evidence manifest, source verifier, secret scanner, run-log fetcher | authored for this product |
| `docs/`, `README.md` | architecture, journeys, operator-facing description | authored for this product |
| `contracts/`, `openspec/`, `_governance/` | compiled C0–C9 contract, OpenSpec change, round and governance records | authored for this product; quotations of governing documents are short locator cites, not reproductions |
| `evidence/` | scrubbed gate receipts, manifests, scan results, CI summaries | produced by the gates in this round |
| `pyproject.toml`, `.github/workflows/ci.yml` | packaging metadata and the candidate CI workflow | authored for this product |

## Does not ship, and is not redistributed

| Material | Why it is excluded |
|---|---|
| `SBL_PIPD-LS-PKG DOC-00..DOC-13`, `SBL_MASTER` | owner-held specification corpus, read in place; only short locator citations appear in this tree |
| `00_KNOW_INDEX..19_KP_INDEX_CROSSWALK` (20 files) | referenced by locator only; no vendored copy (this is a FAR `DROP` decision) |
| `GPTs_GENIEMAKER_設計實作 vol-01..10` | design reference, not redistributed |
| `Fabric`, `PIPD-LS-SP`, `SWOF` repositories | referenced by URL and locator; their own licences govern them |
| the G-KNOW chunk index (`~128 MB`) and the 306-file source corpus | too large to publish and not licensed for redistribution |
| `API KEY/`, any credential, any `.env` | never read into the tree, never committed |

## Third-party code bundled here

None. `pytest` is a CI-only tool, not a runtime dependency, and nothing under the product imports a
vendored third-party module. If that ever changes, `NOTICE` must gain the entry before the next release.

## Known limits of this inventory

- It states what the tree contains; it does not assert that every *idea* in the product is free of third-party
  claims. The donor ledger (`_governance/round-20261020-r2/17_DONORS/`) records that 1 donor is ACTIVE, 6 are
  native-substituted, 3 standby and 8 prohibited; nothing from the prohibited set was implemented.
- Copyright holder is recorded as the organisation handle `shw097-team`. If the owner wants a legal entity or
  a person named, that is a one-line change to `LICENSE` before publication.
