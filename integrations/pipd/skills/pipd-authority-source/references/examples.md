# pipd-authority-source — worked examples

## POS — POS-001: two source families freeze into one manifest and two bindings

Input payload:

```json
{
  "families": [
    {
      "name": "F1_BLUEPRINT",
      "manifest_sha256": "208ef5dcd6d218649cb12e62708b736651fdeab4babf4fe3a32e111456bf87a7",
      "files": [
        {
          "rel": "docs/S0_CONTRACT_SPEC.md"
        }
      ]
    },
    {
      "name": "F4_DONOR_SKILLS",
      "manifest_sha256": "c8117fb4271159cc1b0dfc356fb3c9e14a4a702708a39e3cd1c7723242e606ac",
      "files": [
        {
          "rel": "PROVENANCE.md"
        }
      ]
    }
  ]
}
```

Output payload:

```json
{
  "subject_id": "SFM-ab60515ad4806062",
  "content_hash": "5f0c5ee1eca63bfcc7e58e785c5a5005d124d49f131737814c3a901cbeec4278",
  "version": "1",
  "schema_version": "SourceFreezeManifest@1",
  "families": [
    "F1_BLUEPRINT",
    "F4_DONOR_SKILLS"
  ],
  "digests": [
    "208ef5dcd6d218649cb12e62708b736651fdeab4babf4fe3a32e111456bf87a7",
    "c8117fb4271159cc1b0dfc356fb3c9e14a4a702708a39e3cd1c7723242e606ac"
  ],
  "bindings": [
    {
      "subject_id": "AUTH-285512eec0c42c4e",
      "content_hash": "7305245944858ae0970a8768141b741e44893736f956011a30220c358b88e75b",
      "version": "1",
      "schema_version": "AuthorityBinding@1",
      "source_id": "F1_BLUEPRINT",
      "authority_rank": "R1",
      "locator": "docs/S0_CONTRACT_SPEC.md",
      "supersession": "CURRENT",
      "conflict_state": "NONE"
    },
    {
      "subject_id": "AUTH-1f76fde5bed5a312",
      "content_hash": "b2088d675f00f3380240bee54c3db357b62a72575dc9d98bd0e33bac94839c17",
      "version": "1",
      "schema_version": "AuthorityBinding@1",
      "source_id": "F4_DONOR_SKILLS",
      "authority_rank": "R2",
      "locator": "PROVENANCE.md",
      "supersession": "CURRENT",
      "conflict_state": "NONE"
    }
  ]
}
```

Expected: **ACCEPT** — both payloads round-trip through the declared schemas; routing `Freeze the authority for the blueprint and donor source families` expects **ROUTE**.

## NEG — NEG-001: a family without a manifest digest cannot be frozen

Input payload:

```json
{
  "families": [
    {
      "name": "F1_BLUEPRINT",
      "files": [
        {
          "rel": "docs/S0_CONTRACT_SPEC.md"
        }
      ]
    }
  ]
}
```

Expected: **REFUSE** with first-fail `input.required`; routing `What time is it in Berlin?` expects **NO_ROUTE** (non-trigger).

## SEC — SEC-001: file locators must not traverse out of the admitted root

Payload:

```json
{
  "families": [
    {
      "name": "F7_ARCHIVE",
      "manifest_sha256": "8652663de289f204ae4a3cd4adc7ee66639efdd35b09996c37a2fab9014a2b5c",
      "files": [
        {
          "rel": "../openspec/archive/sealed.zip"
        }
      ]
    }
  ]
}
```

Expected: **REFUSE** with first-fail `input.not`.
