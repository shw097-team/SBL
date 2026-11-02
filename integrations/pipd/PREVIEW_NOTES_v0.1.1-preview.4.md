# PIPD-LS-SP — `v0.1.1-preview.4` preview notes

**Tag** `v0.1.1-preview.4` · **distribution version** `0.1.1a4` · **licence** Apache-2.0
**Supersedes** `v0.1.1-preview.3` (still downloadable; it carries the pre-repair semantic defects
described below and its own `0.1.1a3` wheel)

## What this is

The same S4 command-line contract compiler as `preview.3`, plus **one focused semantic repair** and a
**new private plugin route**, packaged under a new distribution version so that installing it is a
real upgrade rather than a silent replacement of the same filename.

This is a **preview**, not a production release. It is the `S4_PREVIEW_MVP` phase deliverable:
`PUBLIC_DIRECTORY`, four-host full UAT and `PRODUCTION` remain `NOT_GRANTED` / `OUT_OF_SCOPE`.

## Assets in this release

| asset | what it is |
|---|---|
| `pipd_ls_sp-0.1.1a4-py3-none-any.whl` | the Python CLI (13 commands) and the 19 installed schemas plus registry |
| `pipd-ls-sp-public-skills.zip` | the **private ChatGPT plugin** (skills-only): one plugin root, one manifest, exactly the eight existing skills. No MCP, no Apps, no Hooks, no backend |
| `pipd-ls-sp-v0.1.1-preview.4-source.zip` | the source tree at the release commit |
| `PIPD_WEB_FALLBACK.md` | the single-document Web route for readers whose account has no plugin-upload option. Ceiling **`DOC_MOUNT_ONLY`** |
| `PREVIEW_NOTES_v0.1.1-preview.4.md` | this file |
| `SHA256SUMS` | digests for every asset above |

Dropped relative to `preview.3`: the Web **mount pack** is not rebuilt here. It is optional for this
release and the single fallback document covers the same route; the `preview.3` pack remains the last
published mount pack and is untouched.

## What changed since `preview.3`

1. **D1 — negation polarity and scope (P1).** The requirement compiler recognised only the baseline
   prohibitions (`must not`, `不得`, `禁止`, …). A prohibition written as `不允許`, `不許可`, `請勿` or
   `should not` was therefore compiled as a **MUST**, silently inverting an obligation. The surface now
   includes those source-bound phrasings. Two further scope defects are fixed: a positive obligation
   and a prohibition sharing one clause are no longer flattened into a single polarity (each segment
   keeps its own scope), and a clause that carries a positive modal *and* a negation with no boundary
   to split on is now **refused by type** instead of being guessed.
2. **D2 — clause boundary (P1).** The scanner treated every ASCII period as a clause boundary, so
   `api.example.com`, `v1.2.3` and `1.25` dissolved into meaningless atoms and the atom count stopped
   matching the source. A period flanked on both sides by ASCII alphanumerics is now internal; a real
   sentence-final period still ends the clause. Unicode spans, `clause_id`, `req_id` and
   `source_sha256` are preserved, so provenance is unchanged.
3. **ClaimCeiling claim shape (P2, bounded).** `allowed_claims` / `forbidden_escalation` were declared
   as bare `{}` in the schema and read with `set(...)` / `CLAIM_LADDER.index(...)` in the library, so
   five schema-admissible shapes (`null`, a mapping entry, an undeclared claim name, in either field)
   escaped as native `TypeError` / `ValueError` instead of a named finding. Both lists are now typed
   against the declared claim ladder, and the library reports every one of those shapes by name. The
   CLI's existing typed `INPUT_SHAPE_INVALID` behaviour does not regress.
4. **Install surface repointed.** `README.md` and `docs/install/README.md` now name this release's
   tag, wheel and digest, name the private-plugin ZIP route and its permission requirement, and close
   the previously documented open item about a tag whose tree disagreed with its served asset.

## Boundaries you should not read past

- **The private plugin ZIP is not a directory submission.** It is for a ChatGPT account/workspace that
  actually offers the upload option. Without that permission the honest state is
  `NOT_SUPPORTED_FOR_ACCOUNT`, and the Web fallback document is the route to use. Nothing here claims
  a public listing, a Publisher review, KYC or a Directory placement.
- **One triggered skill on one account is not a qualification of all eight skills on all hosts.**
  `ALL_8_SKILLS_HOST_QUALIFIED` and four-host full UAT stay `NOT_GRANTED`.
- **The wheel does not load the skills into a chat host** and the document route does not put `pipd`
  on your machine. The two consumer packages are separate on purpose.
- `S4_FULL_PASS`, `PRODUCTION` and any Universal claim remain **`NOT_GRANTED`**.

## Verify before you use

```bash
BASE=https://github.com/shw097-team/PIPD-LS-SP/releases/download/v0.1.1-preview.4
curl -fsSLO "$BASE/SHA256SUMS"
curl -fsSLO "$BASE/pipd_ls_sp-0.1.1a4-py3-none-any.whl"
grep '  pipd_ls_sp-0.1.1a4-py3-none-any.whl$' SHA256SUMS | sha256sum -c -
python -m pip install ./pipd_ls_sp-0.1.1a4-py3-none-any.whl
pipd doctor
```

For the private plugin route, download `pipd-ls-sp-public-skills.zip`, check it against `SHA256SUMS`,
and import it through your account's plugin upload flow. Uninstall/rollback for the plugin is
**remove the plugin from the account**; for the wheel it is uninstalling `pipd-ls-sp`. The previous
preview stays downloadable, so rolling back means pointing at `v0.1.1-preview.3` again.
