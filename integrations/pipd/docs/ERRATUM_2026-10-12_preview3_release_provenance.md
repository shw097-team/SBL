# ERRATUM 1 — v0.1.1-preview.3 Web Mount pack release identity

> **Document ID**：`PIPD-ERRATUM-2026-10-12-PREVIEW3-PROVENANCE`
> **Raised**：2026-10-12 (Asia/Taipei) · **Round**：`S4EXT-R1-20261012-external-challenge-repair`
> **Finding of record**：`F001` of `PIPD-LS-SP-S4-EXTERNAL-CHALLENGE-2026-10-12-R1` (CONFIRMED_DEFECT, P1)
> **Frozen tuple**：`docs/RELEASE_TUPLE.json` · **Status**：`SOURCE_CORRECTED / PUBLISHED_ASSET_REPLACED_IN_PLACE / RELEASE HOLD`
>
> **Reconciled 2026-10-12 (S4POST integration-repair round).** The first version of this banner read
> `PUBLISHED_ASSET_IMMUTABLE`, which described the repair-branch path that was **not** taken. The
> served asset was replaced in place by the S4R2M release correction; see §3 and
> `docs/RELEASE_TUPLE.json`, which now carries both the first-shipped and the served digest.
> The rest of this document is kept as raised, with the sections that describe the superseded path
> marked in place rather than rewritten, so the earlier finding stays auditable.

## 1. What was wrong

The published GitHub release **`v0.1.1-preview.3`** carries a Web Mount ZIP whose eight documents
declared the release identity as:

```text
v0.1.1-preview.3 — tag commit 8faa64e581e8c25f5ec355475e29561847da3ead
```

That value is **the `v0.1.0-preview.2` tag target**, not this release's. The GitHub tag object
dereferences to a different commit:

| fact | value | how it is obtained |
| --- | --- | --- |
| `v0.1.1-preview.3` annotated tag object | `e94cc7f9567acb59de4691ee6166815ac96a9700` | `git rev-parse v0.1.1-preview.3` |
| **release tag target** (dereference) | `cbf69756d7fc90fc1cdfb3a45a1cc42cc603cb0a` | `git rev-parse v0.1.1-preview.3^{commit}` |
| release tree | `91b1156f5f34f598bd1c81f9fc2ab04518328fd6` | `git rev-parse v0.1.1-preview.3^{tree}` |
| **stale value in the published pack** | `8faa64e581e8c25f5ec355475e29561847da3ead` | `v0.1.0-preview.2` tag target |

`dist/mount/pipd-ls-sp-s4-chatgpt-mount-v0.1.1-preview.3/references/PIPD_SOURCE_MAP.md` additionally
recorded the **preview.2 tree prefix** (`58301503`) instead of `91b1156f`.

Root cause: the identity was a hand-copied literal that collapsed two distinct facts — *which commit
the tag points at* and *which commit the distributed bytes were built from* — into one string. Only the
version string was bumped between preview.2 and preview.3; the commit literal was not re-derived.

Impact: the pack mis-described its own subject, so a consumer copying the prompt, a source crosswalk or
a provenance citation from the pack would cite a foreign object as this release's identity. A correct
ZIP digest does not protect against this — the digest faithfully protects a wrong description.

## 2. What this round changed (source only)

1. **`docs/RELEASE_TUPLE.json`** — the frozen identity table. `release_tag_target` and
   `build_source_commit` are **separate fields**, each resolvable by the listed git command. The only
   sanctioned way for pack text to state its identity is by deriving it from this tuple.
2. **The eight preview.3 pack documents** — every stale `tag commit 8faa64e5…` claim is replaced by
   the explicit pair (`release tag target` `cbf69756…`; `build source commit` `cbf69756…`), and the
   preview.2 tree prefix is corrected to `91b1156f`. `SKILL.md` front matter now carries
   `release_tag_target` + `build_source_commit` instead of a single `release_tag_commit`.
   **(SUPERSEDED — never shipped.)** The served pack does **not** use that caption scheme: the string
   `release tag target` occurs **zero** times in it, `SKILL.md`'s front matter still carries the single
   `release_tag_commit`, and the identity is stated as *release id + tag commit* in all eight
   documents. This item describes the repair-branch rebuild only.
3. **An erratum banner** in `README_MOUNT.md`, `SKILL.md` and `references/PIPD_SOURCE_MAP.md` stating
   what the already published asset says and why it is not being rewritten. **(SUPERSEDED — never
   shipped.)** The served documents carry no such banner; the in-place replacement made the asset
   state the corrected identity directly, which is why the banner was unnecessary.
4. **A corrected rebuild (SUPERSEDED — never shipped)** — `dist/mount/PIPD-LS-SP_S4_WEB_MOUNT_v0.1.1-preview.3-erratum1.zip`
   plus its `.sha256` sidecar, built from the corrected source by `tools/build_mount_pack.py` (the single
   writer of `dist/mount/**`), together with the regenerated in-pack `MANIFEST.sha256`. The owner instead
   took the in-place correction described in §3, so this candidate was never published and is **not
   expected to exist** on the integrated tree; the tuple keeps its path only as a historical disclosure.

## 3. What this round did NOT do

* It did **not** rewrite, retag or delete the published `v0.1.1-preview.3` tag or any release asset.
  **SUPERSEDED 2026-10-12 (S4POST integration-repair round).** This paragraph previously stated that
  the published ZIP "remains byte-identical at `73c6c7e255846e9012a4f5f0e849af93343b363fb158f2474b4d18143d1dcfde`".
  That claim is **withdrawn**: a different repair path was taken by the owner instead. The S4R2M
  release correction **replaced the published web ZIP in place**, and the served asset is now
  `af342d281f02ba04f284a1625f4a58a6f2de15549cc182a0c61ce357ec6b504f` — the byte-identical artifact
  checked in under `dist/mount/` with an agreeing sidecar, and reproducible from the current tree.
  `docs/RELEASE_TUPLE.json` records the first-shipped digest and the served digest as separate fields
  together with the replacement record. Neither path is a release action, and one thing is still
  **not** closed: the immutable `v0.1.1-preview.3` tag still holds the pre-correction pack, so a
  rebuild from the tag's tree does not reproduce the served bytes. Closing that needs a **new
  immutable preview**, not another in-place replacement.
* It did **not** claim that the corrected rebuild is a release. `PIPD-LS-SP_S4_WEB_MOUNT_v0.1.1-preview.3-erratum1.zip`
  is a **candidate** for the next immutable preview (`preview.4`) and carries the preview.3 identity
  because that is the source it corrects. Publishing it, issuing an erratum release note, or pointing
  consumers at it are **Release Owner** acts that are **not granted** by this round.
* It did **not** touch the `v0.1.0-preview.2` pack, whose identity was already correct.

## 4. How the defect is prevented from recurring

`tests/test_s4ext_release_provenance.py` derives the expected identity from the working tree's own git
objects and refuses a pack that disagrees:

* **positive** — for every tuple entry with a `pack_dir`, `git rev-parse <tag>^{commit}` equals the
  tuple's `release_tag_target`, and every pack document contains that value and does **not** contain
  any other release's tag target;
* **negative (stale value)** — injecting the preview.2 value `8faa64e5…` into a preview.3 document
  must be refused, and the assertion that would have passed pre-repair (the value matching *some*
  release) must not be accepted as an identity match.

## 5. Claim ceiling

`FILE_PRESENT` for the corrected source, `LOCAL_QUALIFIED` for the tuple-driven test on this checkout.
**Not** claimed: a new release, a publication approval, a GitHub-side asset change, or an external
verdict. `S4` release admission remains **HOLD** until an independent requalification of a newly frozen
subject, under its own owner gate.
