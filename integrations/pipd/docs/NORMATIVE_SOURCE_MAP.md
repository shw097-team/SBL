# NORMATIVE SOURCE MAP (DERIVED INDEX)

> **This file is a DERIVED INDEX. It is NOT a competing master.**
>
> * The external canonical standard `PIPD-LIFECYCLE-SPEC@1.1.0` remains the **single source of
>   truth**. Nothing in this repository restates, supersedes or re-derives its normative content.
> * This index only **points at** source families: where each lives, who owns it, its version, a
>   digest (or an explicit "not readable here" marker), and which consumers read it.
> * **No source body is copied here.** Blueprint / PKG / DOC / skeleton / standard prose stays at
>   its own locator; this file carries identity metadata only.
> * A digest below is written **only after recomputing it from the live file at that locator**.
>   Where a source is not readable from this workstation the cell says `NOT_VERIFIED_HERE`
>   (digest) or `NOT_PUBLIC` (as the live source allows). No hash was invented.
>
> Provenance of this index: compiled under WorkOrder `WO-S4-SELFBOOT-04`
> (`POSTRELEASE-20261011-s4-narrow-repair`). Family digests cross-checked against the in-repo
> preflight manifest `.hgk/preflight/source-manifest.json`; per-file digests additionally
> recomputed live from disk (see the receipt
> `.hgk/rounds/POSTRELEASE-20261011-s4-narrow-repair/lane/WO-S4-SELFBOOT-04_RECEIPT.md`).

Standing of this document: **candidate-only, read-only index**. It creates no authority, grants no
claim, and is itself superseded by any future refresh of the preflight source manifest.

---

## 0. Owner / authority statement

The normative lifecycle authority for PIPD-LS-SP is the **external** standard
`PIPD-LIFECYCLE-SPEC@1.1.0` (preflight normative claim **NC-02**). HG-KSEOS is the sole control
plane (NC-01). The sources below are the *inputs* this repository is compiled against; the
repository is a bounded consumer, never a normative author.

Locators are given relative to the knowledge root
`C:/Projects/Agent_Workspace/知識庫/`; absolute paths in the preflight manifest prefix that root.

---

## 1. Source families

Six required families (preflight `source_scan.required_source_families`). Family digest =
`manifest_sha256` = SHA-256 over the canonical JSON of `[rel, size, sha256]` rows for the family's
file set. These family digests are recorded as-is from the in-repo preflight manifest; member-file
digests quoted in §2 are **recomputed live**.

| Family | Role | Rank | Owner / authority | Version | Manifest SHA-256 | External locator |
|---|---|---|---|---|---|---|
| `F1_GPTB_KNOWLEDGE` | NORMATIVE | R1 | GPTs GENIEMAKER Builder ReleasePack | `v2026.06.03-r2` | `6e1270bc028770dbbf440a29cd8398bd9c8040937e8451826a0237ba92946c0c` | `知識庫/工程基座/GPTs_GENIEMAKER_…_KP_Builder_ReleasePack_v2026.06.03-r2/KnowledgePack/` |
| `F2_PIPD_STANDARD` | NORMATIVE | R1 | PIPD-LS standard (external canonical SSOT) | `PIPD-LIFECYCLE-SPEC@1.1.0` | `0a7c8538427f1f089aeab7131a9fc2e67083b18d2ae99fe983e401a7a52ec4d6` | `知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/PIPD/PIPD_LS/` |
| `F3_PIPD_DESIGN` | NORMATIVE | R1 | PIPD-LS-SP design set (blueprint + packages) | see §2 | `73253c8b3cda60c1e14e810ac6874192b069c4a6d2e830673711152cc3762e5b` | `知識庫/…/PIPD/` (skeleton, `PIPD-LS-SP_PIPD-PKG/`, `PIPD-LS-SP_藍圖/`) |
| `F4_ENGINEERING_DONORS` | SUPPORT | R2 | Engineering donor skill plugins | `R2` / `v2.0.1` | `5c1101a7691fbd6c85be1cf6595797ef7395fefb9f2c4425cf82bf9510d408de` | `知識庫/…/PIPD/SKILLS_PLUGIN/` |
| `F5_COMMAND_BASIS` | NORMATIVE | R1 | HG-KSEOS command/compile basis | `construction-acceptance-prompt-compiler` | `069c9940ebda166873392f16f8d6d76516a940d9bdf2a3b64c551a6c446f3aec` | `知識庫/實作相關DOC/HG-KSEOS/construction-acceptance-prompt-compiler/`; `Fabric/docs/`, `HG-KSEOS/docs/` |
| `F6_MACHINE_TRUTH` | STATE_EVIDENCE | R1 | Live machine truth (HG-KSEOS / Fabric runtime) | live | `240227060211002b5ead3578216ddd0db2bfc5d39fd87717ea620a34d817511e` | `C:/Projects/Agent_Workspace/HG-KSEOS`, `C:/Projects/Agent_Workspace/Fabric` |

Consumers of families (all six feed the compiler; the mapping is by role):

* **8 skills** (`skills/pipd-*`): `pipd-route-intake`, `pipd-authority-source`, `pipd-pi-compile`,
  `pipd-pd-bind`, `pipd-profile-tailor`, `pipd-execution-contract`, `pipd-assurance-tqaep`,
  `pipd-package-project`. The intake/authority/compile skills read **F2/F3/F5**; the bind skill
  reads **F6**; assurance/TQAEP reads **F4** (donor patterns) + **F2**; package/project reads
  **F3**; the route skill reads **F1/F5** governance shape.
* **19 schema families** (`schemas/registry.json`, exact set/order): `ArtifactIdentity`,
  `AuthorityBinding`, `RequirementAtom`, `ProfileBinding`, `TechnologyAdmission`, `PI-PKG`,
  `PD-PKG`, `TraceLink`, `TaskSpecSeed`, `ConstructionContract`, `WorkOrderCandidate`, `ECP`,
  `TQAEP`, `ExecutionHandoff`, `EvidenceExpectation`, `ClaimCeiling`,
  `SurfaceProjectionManifest`, `GENIEProjectionRef`, `ExecutionBindingRef`.
* **S0–S4 stages**: S0 (source freeze, `AuthorityBinding`, `ArtifactIdentity`) reads **F2/F3/F5**;
  S1 (intent→PI→PD) reads **F2/F3** and binds **F6**; S2 (technology admission / TQAEP) reads
  **F4/F5**; S3 (surface/GENIE projection) reads **F3/F6**; S4 (candidate delivery / self-bootstrap)
  consumes all six read-only.

---

## 2. Named sources (exact per-file digest, recomputed live)

Absolute base for this section:
`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/PIPD/`.
Each SHA-256 below was **recomputed from the live file** and matched the preflight manifest.

### 2.1 External canonical standard (family F2)

| Source | Owner | Version | SHA-256 | Locator | Note |
|---|---|---|---|---|---|
| `PIPD_LS_canonical_standard.md` | external standard (PIPD Core is the implementer, not the owner) | `PIPD-LIFECYCLE-SPEC@1.1.0` | `6f6aafece90b34e33786647e14fee840f5424893995b3164cbb52953a5c4f14a` | `PIPD_LS/PIPD_LS_canonical_standard.md` | **Authoritative SSOT. NOT restated here.** The digest is recorded, not the body. |

> The external canonical standard is the subject of preflight **NC-02**: *"PIPD-LS-SP implements
> PIPD-LIFECYCLE-SPEC@1.1.0 across 11 design packages (PIPD-PKG-00..10)."* It is authoritative and
> is deliberately **not** reproduced in this repository — an in-repo copy would be the competing
> lifecycle SSOT that `docs/SPEC_DEL_CROSSWALK.json` (row `PIPD-SP-SPEC-002`) forbids.

### 2.2 Blueprint (family F3)

| Source | Owner | Version | SHA-256 | Locator |
|---|---|---|---|---|
| `PIPD-LS-SP_藍圖.md` | PIPD-LS-SP design | design set (F3) | `a751a9e91dc6d0b7914b0598519e5d7a0f7adaccb6704e9c7d2aa503f80b0d68` | `PIPD-LS-SP_藍圖/PIPD-LS-SP_藍圖.md` |

(Companion `PIPD-LS-SP_PIPD-EC_SGM_總藍圖.md` shares the F3 family; recorded here for locator
completeness at `PIPD-LS-SP_藍圖/PIPD-LS-SP_PIPD-EC_SGM_總藍圖.md`,
sha256 `0a29095745c628728e6fd7eb5934ecede0368ed870dda9d2b8139ec67296c6b1`.)

### 2.3 Skeleton (family F3)

| Source | Owner | Version | SHA-256 | Locator |
|---|---|---|---|---|
| `PIPD-LS-SP_skeleton.md` | PIPD-LS-SP design | design set (F3) | `a320d344785da9700aff8f48699b307ef150e0bb89d15735722f2930e46faa0e` | `PIPD-LS-SP_skeleton.md` |

### 2.4 Eleven design packages `PIPD-PKG-00..10` (family F3)

Locator prefix `PIPD-LS-SP_PIPD-PKG/PIPD-LS-SP_PIPD-PKG-00~PKG-10/`.

| Package | SHA-256 | Size (bytes) |
|---|---|---|
| `PIPD-LS-SP_PIPD-PKG-00.md` | `89b60fde8b7bb93522c897a250a3ffbf9f2c4f91556493e74ee2da269710ecfe` | 594228 |
| `PIPD-LS-SP_PIPD-PKG-01_…FULL_SUBSTANTIVE_BODY.md` | `4c468e38d461595f21cd4d696dd2b97b655a438d7c8ef2fa1fec29637f8e139f` | 984996 |
| `PIPD-LS-SP_PIPD-PKG-02_…INTEGRATED_SUBSTANTIVE_BODY.md` | `decf42108f693563b1127064864b891d233ace2cf63b33db8f8e57e5ef29e977` | 676216 |
| `PIPD-LS-SP_PIPD-PKG-03_…INTEGRATED_SUBSTANTIVE_BODY.md` | `a8d61dc4ab3062f401427c0787f596093671c6e0d7408c6e924be3362423043f` | 735475 |
| `PIPD-LS-SP_PIPD-PKG-04_…INTEGRATED_SUBSTANTIVE_BODY.md` | `967c0a4906d735f7f0973987b6162993d8a87d88d8675d9bd1675f31b1055a77` | 840568 |
| `PIPD-LS-SP_PIPD-PKG-05_…INTEGRATED_SUBSTANTIVE_BODY.md` | `b01b170519b1343c6f4593b4e039b28bb9b4f3f68dbd9c17be52b198d542ff94` | 295627 |
| `PIPD-LS-SP_PIPD-PKG-06_…INTEGRATED_SUBSTANTIVE_BODY.md` | `073592099de22584e12b5ca892c52b298ccca2504f759e723c258a52c2b14dc9` | 307177 |
| `PIPD-LS-SP_PIPD-PKG-07_…INTEGRATED_SUBSTANTIVE_BODY.md` | `213b49c53f060ea780657def96a22b7e2815a222726874187d154f844a5c9872` | 736406 |
| `PIPD-LS-SP_PIPD-PKG-08_…INTEGRATED_SUBSTANTIVE_BODY.md` | `e93fe81371192b43c2b583423a33cfb728b6a6b99a7eef48ef19ff2516e18445` | 712350 |
| `PIPD-LS-SP_PIPD-PKG-09_…INTEGRATED_SUBSTANTIVE_BODY.md` | `b2952652d511ff726fac0b7f80147f807d1624ad4392c682635aa5582e386197` | 733299 |
| `PIPD-LS-SP_PIPD-PKG-10_…INTEGRATED_SUBSTANTIVE_BODY.md` | `e089fa095aa83f130be4846b478edc14bea9f410d4cc99ad52e4b6b5375391bd` | 1099995 |

### 2.5 Ten documents `PIPD_LS_DOC-00..09` (family F2)

Locator prefix `PIPD_LS/`. (The `_2026-10-07_…` suffixes are part of the on-disk filenames.)

| Document | SHA-256 | Size (bytes) |
|---|---|---|
| `PIPD_LS_DOC-00_…FULL_SUBSTANTIVE_BODY.md` | `be3a672ec20aa0e6b5e0e35097fc08de749bfe7f59f827d18e38aef67dd68ea4` | 251982 |
| `PIPD_LS_DOC-01_…FULL_SUBSTANTIVE_BODY.md` | `b753f2e5cdd5598a818f8a113d57b7f815aeb3f1dfa061ce74c76bb3553ac8c7` | 177451 |
| `PIPD_LS_DOC-02_…(1).md` | `a021998dd3b63015e89af1dd40e0b413744a69b872da46c6bf5f4d92f7f23d0b` | 1306240 |
| `PIPD_LS_DOC-03_…FULL_SUBSTANTIVE_BODY.md` | `d89d82dcd2c8603ec6b86c5ec8c40845e4594bc181adf5272bd48a3de7c88f0f` | 454167 |
| `PIPD_LS_DOC-04_…FULL_SUBSTANTIVE_BODY.md` | `fa64d84da3d747b183e4affff62f4d2fb86c80bb5075f5dd933c09b20caeddcf` | 181988 |
| `PIPD_LS_DOC-05_…FULL_SUBSTANTIVE_BODY.md` | `7b40584540c162cda6debfd09a4c04321416706acdb03a7a3c2b41383dc585f4` | 227894 |
| `PIPD_LS_DOC-06_…FULL_SUBSTANTIVE_BODY.md` | `20e44ea4dd8e53c9b0a076ce861136bbea86f52687019307f6e995cd9079d303` | 405028 |
| `PIPD_LS_DOC-07_…FULL_SUBSTANTIVE_BODY.md` | `a68dae1c3670d07bcfa3476a1e37463c534594df5cd65d8dab0dca064b5a9fc1` | 689563 |
| `PIPD_LS_DOC-08_…FULL_SUBSTANTIVE_BODY.md` | `e46caa7e440392a6cfa7a86421aead5bce8a2a229fec97b133429db6b6748e42` | 197972 |
| `PIPD_LS_DOC-09_…FULL_SUBSTANTIVE_BODY.md` | `eaf0aefe2b4711c140fc3274223d88fdc38ad4ec2b7184f756a0f2471f3b0b54` | 144948 |

---

## 3. Digest verification method

Every per-file SHA-256 in §2 was produced by streaming the live file through SHA-256
(`hashlib.sha256` over 1 MiB blocks) and was compared against
`.hgk/preflight/source-manifest.json`; all matched (`OK` in the run log). Family digests in §1 are
the preflight `manifest_sha256` values, quoted as recorded. No digest in this document was
hand-entered, and none was invented: if a source had been unreadable, the cell would read
`NOT_VERIFIED_HERE` (digest) / `NOT_PUBLIC`. As of this writing every named source above was
readable and every quoted per-file digest was recomputed live.

## 4. Exclusions

Bodies are **not** in this repository. Only identity metadata (owner, version, digest, locator,
consumers) is indexed. This file is a derived index and yields to the external canonical standard
and the preflight source manifest on any discrepancy.
