# PIPD-LS-SP — install (single source of truth)

This page is the **install SSOT**: every other page that mentions installing PIPD-LS-SP either is
this page or points at it. There are **three install routes** — **Web**, **Agent**, and the **private
plugin ZIP** — and they have different ceilings. Pick one, read its ceiling, and do not read a green
build (or a copied file) as anything more than what the
[states table](#states-that-are-not-the-same) below says.

Version pin for everything on this page: release **`v0.1.1-preview.4`**; its annotated tag object
`0618d73c725da0d8c3280f99ef369d13741b5197` dereferences to release-tag target
**`cc6c1930765160697e7e51d6e37735b9220a30db`** (tree `7d277a0afaff28b6841836cea3a31ffd0b214d94`).
`cbf69756d7fc90fc1cdfb3a45a1cc42cc603cb0a` is the **`v0.1.1-preview.3`** target and is *not* a
preview.4 identity. The preview.4 entry's `build_source_commit` is
`4754d92cc98c0c02b59bf9700d08c0b7bf452e3d`, and its own `build_source_scope` limits that field to the
wheel `pipd_ls_sp-0.1.1a4-py3-none-any.whl` only — it is **not** a claim about the plugin ZIP. The
authority for these facts is [`docs/RELEASE_TUPLE.json`](../RELEASE_TUPLE.json); read it before you
rely on any digest quoted below.

---

## Route 1 — Web (single-document fallback)

There is **no public plugin directory listing yet**: nothing has been published to a plugin
directory, so no user can install PIPD-LS-SP from one. The Web route today is therefore a **single
document**, `PIPD_WEB_FALLBACK.md`, produced by [`tools/build_web_fallback.py`](../../tools/build_web_fallback.py)
from a frozen mount pack. You attach that one document to a conversation or a Knowledge base; you do
not install anything. Its ceiling is **`DOC_MOUNT_ONLY`** — no Python CLI, no MCP, no repository
write, no S4 acceptance (spelled out [below](#the-web-fallback-document-and-its-doc_mount_only-ceiling)).
The conditional directory route is described [further down](#the-directory-route-conditional-not-available-today).

---

## Route 2 — Agent (one copy-paste prompt)

The Agent route is **one copy-paste prompt**: [`PIPD_AGENT_INSTALL_PROMPT.md`](PIPD_AGENT_INSTALL_PROMPT.md).
It targets four supported hosts — **Hermes Agent**, **Codex Desktop (GUI)**, **Codex CLI** and
**Claude Code** — and it makes the host do the work: detect its own identity/version/OS, prove its
own discovery mechanism, show the exact paths and the diff, stop for approval, and then verify the
load. **File presence is not evidence.** A host is only counted when it proves *real discovery* and
an **8/8 effective load** of the eight skills, each with one positive and one negative trigger; if
all that happened is that files were copied, the correct report is `NOT_VERIFIED`. Web GPT-6 is a
**consumer of the fallback document, not an agent host** — it does not load the skills and is not a
qualifying host for this route.

The eight skills the route installs are the eight `skills/pipd-*` packs — `pipd-route-intake`,
`pipd-authority-source`, `pipd-profile-tailor`, `pipd-pi-compile`, `pipd-pd-bind`,
`pipd-execution-contract`, `pipd-assurance-tqaep`, `pipd-package-project` — six files each, **48
files** in total.

---

## Route 3 — Private plugin ZIP (ChatGPT, your own account)

This route installs the eight skills as a **private ChatGPT plugin on your own account**. It needs no
shell and no directory listing: you download one ZIP from the immutable release and add it through the
ChatGPT plugin UI.

**The artefact.** `pipd-ls-sp-public-skills.zip` — **68,357 bytes**, sha256
`545e359a5ca6abc7bcbbaa2316f8e062244ad4a132ae1ae839bc9a8e17d95d75`, **56 entries**, **8 `SKILL.md`**,
one plugin root `pipd-ls-sp-public-skills/` and one `plugin.json`:

`https://github.com/shw097-team/PIPD-LS-SP/releases/download/v0.1.1-preview.4/pipd-ls-sp-public-skills.zip`

**The four UI steps.** In ChatGPT: create a plugin → upload that ZIP → install it on your own account →
smoke it with one `@pipd-route-intake` call. **If a plugin with the same `plugin_id` is already
installed, do not add a second one** — follow
[Updating a plugin you already installed](#updating-a-plugin-you-already-installed) instead.

**Its ceiling.** `FORMAT_PASS / ONE_ACCOUNT_PARTIAL`: creation, installation and one skill call were
observed, but **on the owner's own account only**. That is not a portal review and not a listing — the
directory listing is a *different, conditional* route, see
[The Directory route](#the-directory-route-conditional-not-available-today).

---

## The Web fallback document and its `DOC_MOUNT_ONLY` ceiling

`PIPD_WEB_FALLBACK.md` is one markdown document built from a *frozen mount pack* — a directory that
carries its own `MANIFEST.sha256`. **`v0.1.1-preview.4` ships no mount pack** (its `RELEASE_TUPLE`
entry sets `pack_dir`/`zip` to `null` on purpose), so there is no preview.4 pack to build from. The
committed document's own header reads `release_id: v0.1.1-preview.3` and
`release_commit: cbf69756d7fc90fc1cdfb3a45a1cc42cc603cb0a`, which is the last release that ships a
pack. The command below is therefore the **legacy preview.3 example**, matching the committed
document's own header:

```bash
# legacy preview.3 example — preview.4 ships no mount pack
python tools/build_web_fallback.py \
  --mount-pack dist/mount/pipd-ls-sp-s4-chatgpt-mount-v0.1.1-preview.3 \
  --release-id v0.1.1-preview.3 \
  --release-commit cbf69756d7fc90fc1cdfb3a45a1cc42cc603cb0a \
  --out PIPD_WEB_FALLBACK.md
```

**The built document is committed**, so a reader with no shell can obtain it directly:

| artefact | path | digest |
|---|---|---|
| the document | [`docs/install/PIPD_WEB_FALLBACK.md`](PIPD_WEB_FALLBACK.md) | `c88ddc49cfe5fb59fe1a713fdde4cfd6a06ed54cc5831885130e053ce990c2af` |
| its digest file | [`docs/install/PIPD_WEB_FALLBACK.md.sha256`](PIPD_WEB_FALLBACK.md.sha256) | — |

Rebuilding with the command above must reproduce those bytes exactly; the builder is deterministic
and embeds no timestamp, so a mismatch is a real finding, not a race. The document's own header
carries `release_id`, `release_commit`, `size_cap_bytes` and the per-member inventory — check those
against the `.sha256` line before you rely on either file.

The tool is fail-closed, not best-effort. It **refuses** (typed reason, non-zero exit) instead of
warning, on `MANIFEST_DIGEST_MISMATCH`, `MEMBER_SYMLINK`, `PATH_ESCAPE`, `UNEXPECTED_EXTRA_FILE`,
`RELEASE_STAMP_MISSING`, `MEMBER_NOT_TEXT`, `SIZE_CAP_EXCEEDED` (it never truncates) and
`DESTINATION_EXISTS` / `DESTINATION_SYMLINK`. It writes with `O_EXCL`, embeds no timestamp, stamps
`DOC_MOUNT_ONLY` plus the member inventory, and is byte-deterministic across rebuilds.

**The ceiling is `DOC_MOUNT_ONLY`.** That means, precisely:

| not available through the fallback document | why |
|---|---|
| the Python **CLI** (`pipd`) | the document is content; it runs no `pipd` on the reader's machine |
| **MCP** or any tool surface | nothing is registered and nothing is invoked |
| **repository writing** | the document writes nothing to any checkout |
| **S4 acceptance** | mounting a document accepts no stage, qualifies no host and approves no release |

The host that consumes it is a read-only semantic surface: it can help you *design* work; it cannot
execute, install, test, approve or release anything. For an 8/8 loaded skill set with real
discovery, use the Agent route.

---

## The Directory route (conditional, not available today)

A plugin directory listing is a *different* route, and it is **conditional on a published,
account-visible listing** — one that actually exists and can be found from an account. None exists
today. Treat every "install from the directory" instruction you read anywhere as **not available**
until all of the following are true, and each is separately evidenced:

1. the package root manifest conforms to the directory's own vendor schema (Agent Plugins 1.0), not
   to PIPD's internal bookkeeping manifest;
2. the directory's portal has reviewed and approved the submitted package (its own record, not ours);
3. the listing is published and account-visible, and the bytes it serves match the receipt digest.

Until then the Web route is exactly the single document in Route 1. Do not present a conditional
route as an available one.

---

## States that are NOT the same

These five words are kept apart on purpose. None of them is upgraded by a green build, and the
right-hand column is what would have to exist for the word to be true — **not** what exists now.

| state | meaning | required evidence | state today |
|---|---|---|---|
| `BUILD_PASS` | the deterministic packager built the candidate and its own tests are green | the build tool exits `0` with a byte-identical rebuild (two builds, same input, same bytes), the two upgrade test modules plus the full suite green, and a receipt whose `claim_ceiling` is `LOCAL_PACKAGER_PASS_ONLY` | **NOT claimed** — the builder *refuses* on the deliberately absent owner inputs (`derivations.json` is empty, no pinned publisher identity, no pinned official/vendor schema digest, no icon), so no candidate ZIP is claimed |
| `PORTAL_APPROVED` | the plugin directory's own review approved the submitted package | the portal's approval record / identifier for that submission — the directory's verdict, never our own summary | **NOT_EXECUTED** — the manifest records `official_portal_verification: NOT_EXECUTED`; no submission was reviewed |
| `PUBLISHED` | the package is live in the public directory and its served bytes are the ones we hashed | a published, account-visible listing **plus** the served asset's digest agreeing with the receipt | **NOT_PUBLISHED** — no public directory listing exists yet |
| `HOST_QUALIFIED` | a specific host really loads the eight skills | per-host, host-produced evidence: the host resolved the project root, really discovered the skills, reported **8/8 effective load**, and passed one positive and one negative trigger; raw logs attached | **NOT_VERIFIED** — no host has produced that evidence; a copied file reports `NOT_VERIFIED` |
| `S4_FULL_PASS` | the S0–S4 challenge is accepted as a *full* pass | independent verifier receipts covering the whole S0–S4 challenge, not scoped receipts | **NOT claimed** — the challenge is `PARTIAL_CHALLENGE`; scoped receipts only, and `G-RELEASE_FULL_PASS` is not granted |

`BUILD_PASS` != `PORTAL_APPROVED` != `PUBLISHED` != `HOST_QUALIFIED` != `S4_FULL_PASS`. A green
`BUILD_PASS` on this repository does **not** imply any of the other four — and there is no `BUILD_PASS`
today either.

---

## Advanced and recovery

Everything below is subordinate to the three routes above. It is not an alternative route.

### Version pin

Pin the **immutable** identity, never a moving branch tip:

- release id **`v0.1.1-preview.4`**; its tag object `0618d73c725da0d8c3280f99ef369d13741b5197`
  dereferences to target commit `cc6c1930765160697e7e51d6e37735b9220a30db`, tree
  `7d277a0afaff28b6841836cea3a31ffd0b214d94`. The release carries **no** `RELEASE_TUPLE_*.json` asset;
  its identities live in the `v0.1.1-preview.4` entry of
  [`docs/RELEASE_TUPLE.json`](../RELEASE_TUPLE.json) in this tree, and the digests a downloader verifies
  against are the release's own `SHA256SUMS` asset. Both are independently re-derivable:
  `git rev-parse <tag>`, `git rev-parse <tag>^{commit}`, `git rev-parse <tag>^{tree}`, and
  `sha256sum <downloaded asset>` against `SHA256SUMS`. The earlier releases' entries stay as history —
  a tag's tree is never rewritten.
- **Closed open item:** the previous immutable preview's tag held the pre-correction pack, so a
  rebuild *from that tag's tree* did not reproduce the served asset. `v0.1.1-preview.4` is the new
  immutable preview built from the repaired merged `main`, so the corrected source and the served
  bytes now share one tag; the older tag stays historical and untouched.

### Hashes

- Wheel `pipd_ls_sp-0.1.1a4-py3-none-any.whl`: the published digest is recorded in the repository
  front page (`README.md`). Verify the bytes you downloaded against that digest before installing;
  this page does not replace the sidecar.
- Private skills-only plugin ZIP `pipd-ls-sp-public-skills.zip`: the **ChatGPT Web private route**
  (import a ZIP you own, eight skills, no MCP/Apps/Hooks). Download it from
  <https://github.com/shw097-team/PIPD-LS-SP/releases/tag/v0.1.1-preview.4>; the release's own
  `SHA256SUMS` asset records its digest, which is
  `545e359a5ca6abc7bcbbaa2316f8e062244ad4a132ae1ae839bc9a8e17d95d75` (68,357 bytes) — verify the
  bytes you downloaded against it before uploading, and treat `SHA256SUMS` (not this page) as the
  sidecar of record. The ZIP carries a single plugin root, one manifest and exactly the eight
  existing skills. Uploading it needs an account/workspace that actually offers the upload option —
  without that permission the ceiling stays `NOT_SUPPORTED_FOR_ACCOUNT` and the Web fallback document
  below is the route to use. **If you already installed this plugin under the same `plugin_id`, do
  not press Add again — see
  [Updating a plugin you already installed](#updating-a-plugin-you-already-installed).**
- Mount pack ZIP `PIPD-LS-SP_S4_WEB_MOUNT_v0.1.1-preview.3.zip`: digest recorded in
  `docs/RELEASE_TUPLE.json` (`published_asset_sha256`), with a `.sha256` sidecar next to the ZIP.
- Inside an unpacked pack, `MANIFEST.sha256` lists every member's sha256 (LF-normalised text bytes
  hash as stored). `tools/build_web_fallback.py` recomputes it and refuses on any mismatch.
- **Served-document provenance drift.** The `v0.1.1-preview.4` release serves a `PIPD_WEB_FALLBACK.md`
  whose sha256 is `c88ddc49cfe5fb59fe1a713fdde4cfd6a06ed54cc5831885130e053ce990c2af` (the same bytes as
  the committed file above), and that served copy's own header declares the **earlier**
  `release_id: v0.1.1-preview.3` / `release_commit: cbf69756...` provenance. This is a real drift in
  an immutable release. That document is a frozen asset of `v0.1.1-preview.4`, so it can only be
  corrected by a future release; no in-place repair of the release asset is possible here.

### Updating a plugin you already installed

This is the route for a plugin you installed earlier under the **same `plugin_id`**. Adding a second
package under an id you already have is what a host refuses, and that refusal is about the id already
being present — **it is not evidence that the ZIP is damaged.**

1. **Identify first.** On the ChatGPT plugins page, check whether the plugin is already listed as
   installed, and note its `plugin_id` (and the display name). Compare it with the `plugin_id` in the
   ZIP's root `plugin.json` before you upload anything.
2. **Same id → Update.** If the id matches, use the plugin's own **Manage → Update** flow, or
   **Upload new version** if your host offers that option, and point it at the freshly downloaded
   ZIP. Do not use Add.
3. **If no Update/Upload-new-version option exists** for that host/account, update by replacement:
   back up anything you stored in the plugin first, then **uninstall the old plugin yourself** and
   add the newly downloaded ZIP once. This is a consent step you take, not something a tool should
   do for you.
4. **A different id is a different plugin.** If you (or anyone) re-package the same skills under a
   **new** `plugin_id`, the result is a **derived candidate**, not the published release asset. The
   release asset `pipd-ls-sp-public-skills.zip` keeps its own digest above; a renamed rebuild must
   never be presented as that asset.
5. **Rollback.** Keep the previous ZIP (and its digest) before you update. To roll back, uninstall
   the new plugin and re-add the previous ZIP; nothing outside the plugin itself changes.

If your account or workspace has no upload/update option at all, the ceiling is
`NOT_SUPPORTED_FOR_ACCOUNT` and the Web fallback document in this page is the route to use.

### Uninstall / rollback

- **Web fallback:** delete `PIPD_WEB_FALLBACK.md`, and detach it from the conversation or Knowledge
  base. Nothing was installed, so nothing else changes.
- **Agent route:** remove exactly the files the prompt listed in its *uninstall path* line before it
  wrote anything — the prompt refuses to run without printing that path first, and it refuses global
  writes, so removal is confined to the project-local skill directory. Re-run the prompt to see the
  list again; do not delete files it did not name.
- **Wheel (CLI):** inside the virtual environment you installed into,
  `python -m pip uninstall pipd-ls-sp`; or delete that environment. Nothing is installed outside it.

### Reporting a failure

Report what the host or the tool actually produced, not a summary of what you hoped for. Include:

- host, OS and host version, and the shell/file/network permissions the host declared;
- the pinned source you used (repo URL + the 40-hex commit, and the pack ZIP digest if you used one);
- the **effective** skill count (discovered and loaded, not files copied);
- every refusal case you hit, with the tool's or host's typed reason, verbatim;
- the raw log paths.

This repository's own read-only gate for the upgrade is
[`.github/workflows/public-plugin-verify.yml`](../../.github/workflows/public-plugin-verify.yml); it
uploads its raw logs as the `public-plugin-verify-raw-logs` artifact, which is the shape a failure
report should have. A failure report is never an acceptance claim: see the
[states table](#states-that-are-not-the-same) — none of those five words is granted by reporting.
