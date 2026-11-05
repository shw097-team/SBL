> **Vendored snapshot** of `shw097-team/PIPD-LS-SP@aeb0d479`, absorbed for the SBL U04 consolidation.
> See [MIGRATION-NOTES.md](MIGRATION-NOTES.md) for the eight files that were not carried and why.

# PIPD-LS-SP — Pre-Implementation / Pre-Dev Lifecycle Skills Plugin

A governed, contract-first toolkit for the **pre-implementation** stage of a project: it turns a
stated intent into a validated chain of machine-readable artefacts — PI → PD →
ConstructionContract → ECP / TQAEP — each bound to one of **19 canonical JSON Schema families**,
and it refuses to hand you something it cannot check. It ships **8 skills** and a **13-command
CLI** (`init` `intake` `profile` `compile-pi` `bind-pd` `compile-ecp` `compile-tqaep` `validate`
`doctor` `project` `export` `diff` `repair`) that produce and verify those artefacts
deterministically.

Licensed **Apache-2.0**. This repository is an owner-authorised open-source **preview / beta**, not
a production release — read [Claim ceiling](#claim-ceiling) before building on it.

[FHS Engineering Entry — cross-repository navigation (non-authoritative)](https://github.com/shw097-team/Fabric/blob/main/INTEGRATION/FHS/README.md)

## Start here — the only navigation you need

This README is an **entry point, not a manual**: it says what this is, what state it is in, and where
each thing lives. Shell-level installation detail has exactly one home and is not repeated here.

| If you are… | Go to | What it is |
|---|---|---|
| New, and you want to know what this is / is not | [What it does, and does not](#what-is-in-this-tree) | Scope and non-goals |
| Checking whether it is safe to build on | [Claim ceiling](#claim-ceiling) · [Known limitations](#known-limitations) | What is verified, what is not |
| Installing it, by any of the three routes | [`docs/install/README.md`](docs/install/README.md) | **The single install SSOT** — versions, hashes, uninstall |
| Want a private ChatGPT plugin (no directory listing) | [Private plugin route](#install) | ZIP download + four UI steps, verified 2026-10-14 |
| Actually using it, task by task | [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | **The single user guide** — the only manual |
| Driving the CLI/Wheel directly | [CLI advanced](#choose-your-path-cli-or-skills) | 13 verbs, JSON output, typed refusals |
| Want the current state, evidence and gates in one place | [Current state and evidence entry points (2026-10-14)](#current-state-and-evidence-entry-points-2026-10-14) | Merged main, evidence packs, lane receipts, gates |

Three routes exist. **Web** (one document, no shell) and **Agent** (one copy-paste prompt) are the two
the install page describes first; the third is the **private plugin ZIP** — download one skills ZIP from
the release and add it to your own ChatGPT account, no shell required
([`docs/install/README.md`](docs/install/README.md), *Route 3*). The historical shell transcripts further
down are retained as evidence of what was actually executed against the published wheel — they are
**not** an installation instruction. When these routes disagree,
[`docs/install/README.md`](docs/install/README.md) and the [user guide](docs/USER_GUIDE.md) win; the
install page is the SSOT for all three.

## Current state and evidence entry points (2026-10-16)

This front page is an **entry point, not a manual**: it states where things are and what is proven,
and the manual itself lives in [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) and
[`docs/install/README.md`](docs/install/README.md).

**As of 2026-10-16** `main` is `d3bd5456afbff21a8c8837994a49f57be3e1b97e` and the repository is in an
owner-authorized **merged candidate** state, not a release. Two pull requests are **open and
non-blocking**, both carrying `MERGE_APPROVED_SCOPE_ONLY` from the external final review and both
waiting on an owner merge:

| PR | Branch tip | Scope |
|---|---|---|
| #18 | `c17aa761b26033fc0a2a2aa3df5ad0f61f2e5a20` | docs identity truth + update route + guard — 4 files, no `src/`, no `schemas/` |
| #17 | `97a01dab95bc53a08b8c372e3c3b04e69a923d7d` | one-file release-ZIP readback (`docs/install/ASSET_READBACK…json`) |

An owner merge creates a **new** merge commit on `main`; until that happens the tips above are
candidate branches only, and re-reading `main` before acting remains mandatory.

| Where | What it holds |
|---|---|
| Evidence branch `repo-hygiene-evidence-20261016` (this round) → `s4-final-closeout-evidence-20261016` (head `5750c6904ea6a12fde4a7ce56936d516f661c428`) → `r6-evidence-return-20261014` → `r5z-evidence-return-20261014` | The externally readable evidence packs, no credential needed to read them. The S4 FINAL closeout pack is `S4_FINAL_PR18_EXECUTION_RETURN/`; the repo-hygiene/handover pack is `PIPD_REPO_HYGIENE_AND_HANDOVER_RETURN/` |
| `PIPD_S4_R6_FAR_AND_ALIGNMENT_RETURN/` | R6 FAR + Tier-1 pack: `VERIFICATION_PROTOCOL.md`, `UPG_TRACEABILITY_R6.tsv` (**105 rows**), `ZIP_REPRODUCTION.json`, `06_verification/VERDICT_R6_PASS.json`, and `03_execute/` with the candidate ZIP plus its lane receipt |
| `PIPD_S4_R6_FAR_AND_ALIGNMENT_RETURN/acceptance/` | The **five** governing documents and `GOVERNING_DOCS_MANIFEST.json` (5/5 hash match; one redaction rule, `<REDACTED_CREDENTIAL_LOCATOR>`) |
| Repository state and hygiene inventory | [`docs/adr/ADR-0008-repository-state-and-hygiene-inventory.md`](docs/adr/ADR-0008-repository-state-and-hygiene-inventory.md) — branches, pull-request dispositions, CI state, hygiene rules |
| Starting a new session on this repo | [`docs/adr/ADR-0009-session-handover-and-next-session-start.md`](docs/adr/ADR-0009-session-handover-and-next-session-start.md) — state, open owner decisions, reproducible commands, lane dispatch template |
| `PIPD_S4_R5Z_SESSION_CONFORMANCE_RETURN/`, `PIPD_S4_R5Y_GPT_PLUGIN_EVIDENCE_RETURN/`, `PIPD_S4_R4_EVIDENCE_RETURN/` | The other three return packs: session conformance, the private-plugin UI/functional evidence, and the expanded R4 evidence return |

> **Lane-arm note (2026-10-16).** The rows below are the **historical R6 receipts** and are not
> edited. On 2026-10-16 the owner re-bound all three lanes (PLAN/Orchestrator, EXECUTE, VERIFY_SECURITY)
> to `opencode-go/deepseek-v4.1-flash`; the current `VERIFY_SECURITY` arm is **rank 1**, served =
> required. Because writer and checker then share one arm (`SOD006-C3`), model-level segregation **does
> not exist** and no round may describe its checks as cross-model independent.

The binding evidence for the R6 work is the **lane receipt**, not a self-report:

| Lane | Engine | Arm (required = served) | Rank | ok | Window |
|---|---|---|---|---|---|
| EXECUTE | CODEX CLI | `opencode-go/deepseek-v4.1-flash` | 1 | true | `2026-10-14T06:19:07Z` (476.0 s) |
| VERIFY_SECURITY | CODEX CLI | `opencode-go/glm-5.3-flash` | 3 | true | `2026-10-14T06:23:25Z` (130.72 s) |

Both receipts record `subject_mutation` verdict **CLEAN**; VERIFY_SECURITY returned `overall` **PASS**.

The plugin ZIP is reproducible. Run from the frozen R5Y worktree at commit
`062d84ae3e951d02b2ba6bb732359b18799d2864`:

```bash
python tools/freeze_public_plugin_source.py --repo-root . --out ledger.json
python tools/build_public_plugin.py --ledger ledger.json --source-commit 062d84ae3e951d02b2ba6bb732359b18799d2864 \
  --packaging-root packaging/public-plugin --out-dir out --generate-icons
```

This reproduces the **historical R5Y build**: `out/pipd-ls-sp-public-skills.zip` — **68,355 bytes**,
sha256 `2f9ae010a6eba90787037a93a17e77f50bbc29dea5628f6fbe3e0f278fd2d199`, **56 entries**, **8 `SKILL.md`**
— the bytes frozen at `062d84ae3e951d02b2ba6bb732359b18799d2864` and attached to the R5Y evidence return.
Those bytes are **superseded as a download**: the artefact a user installs is the `v0.1.1-preview.4`
release asset `pipd-ls-sp-public-skills.zip` — **68,357 bytes**, sha256
`545e359a5ca6abc7bcbbaa2316f8e062244ad4a132ae1ae839bc9a8e17d95d75`, 56 entries, 8 `SKILL.md`. Two
independent builds are byte-identical. A local packager PASS is not portal approval.

| Gate | State | What it means |
|---|---|---|
| Private plugin route (download ZIP, install on your own account) | **PASS** (owner's own account) | Creation, installation and one `@pipd-route-intake` call observed; evidence in `PIPD_S4_R5Y_GPT_PLUGIN_EVIDENCE_RETURN/09_ui_fda/` |
| Public directory listing | **HOLD** | OpenAI developer identity verification is a human gate; no submit/review/publish was performed |
| Tag / release | **Superseded by the published preview** | At the R5Y record time no tag had been created for the merged candidate. `v0.1.1-preview.4` (tag object `0618d73c725da0d8c3280f99ef369d13741b5197`, target `cc6c1930765160697e7e51d6e37735b9220a30db`) was published on 2026-10-14 and is the current immutable preview; `main` has since advanced past it, so read the tag's tree — not `main` — for the released bytes |

Truth-ticket status as recorded: **TT-004** (citation defects) **CLOSED**; **TT-005** (lane arm
binding) **CLOSED**; **TT-001** (PLAN model declaration) closed as a **documented substitute** — the
PLAN lane ran on `opencode-go/deepseek-v4.1-flash` while the declared PLAN model is
`opencode-go/glm-5.3-flash`, so the segregation is engine separation (Hermes vs CODEX CLI) with
receipt-backed measurement, not model-level segregation.

`BUILD_PASS != PORTAL_APPROVED != PUBLISHED != HOST_QUALIFIED != S4_PASS`

### S4 final review outcome (2026-10-16) — what is granted and what is not

An independent external review of `main@d3bd5456`, `PR#18@c17aa761b` and
`v0.1.1-preview.4@cc6c1930` reached these rulings (report `PIPD-LS-SP-S4-EXTERNAL-FINAL-20261016`):

| Item | Ruling |
|---|---|
| S4 / Preview-MVP phase | **`TEMP_CLOSED_RECOMMENDED`** — an owner signature is still required before it reads `TEMP_CLOSED` |
| D1/D2, ClaimCeiling, trace closure | `PASS_SCOPED` |
| PR #18 / PR #17 | `MERGE_APPROVED_SCOPE_ONLY` (owner merge outstanding) |
| `v0.1.1-preview.4` | `PUBLISHED_PASS_SCOPED` — **immutable**: its tag, assets and checksums must never be replaced in place |
| Private ChatGPT plugin ZIP | `FORMAT_PASS / ONE_ACCOUNT_PARTIAL` |
| `preview.5` / next public release | `DEFER_UNTIL_DISTRIBUTION_NEEDED` |
| Four-host qualification, `S4_FULL_PASS` | **`NOT_GRANTED`** |
| Private-host UAT | **`NOT_RUN`** |
| Production, public plugin directory | **`NOT_GRANTED` / `OUT_OF_SCOPE`** |

The S4 final closeout evidence pack (`S4_FINAL_PR18_EXECUTION_RETURN/`, including a verbatim checker
verdict that returned `PARTIAL` because the sandbox had no outbound network) is on
`s4-final-closeout-evidence-20261016`; the repo-hygiene and session-handover pack is on
`repo-hygiene-evidence-20261016`.

## Verification entry point — historical (superseded 2026-10-16)

> **Superseded.** Everything from here down describes the 2026-10-13/14 candidate round and is kept as
> history, not as current state; the dated trail lives in
> [`docs/FRONT_PAGE_HISTORY.md`](docs/FRONT_PAGE_HISTORY.md).

**As recorded on 2026-10-14:** the plugin candidate is
`feat/s4r5y-plugin-publication-20261014` @ `062d84ae3e951d02b2ba6bb732359b18799d2864` (draft PR #6 →
`main`): a Skills-only ZIP whose manifest carries the official listing fields, with the private-install
evidence beside it. The conformance answer to the R4 command prompt and to the 2026-10-13 acceptance
report is in `PIPD_S4_R5Z_SESSION_CONFORMANCE_RETURN/`, and the R4 closeout receipts are in
`PIPD_S4_R4_EVIDENCE_RETURN/`. The R3/S4POST text below is kept as history.

The current candidate is **not** on `main`, and `main` is not what the entry document describes.
The verification entry document is
[`R3_PUBLICATION.md`](.hgk/rounds/S4POST-20261012-postrepair-recheck-and-triple-upgrade/R3_PUBLICATION.md)
on branch **`feat/s4post-triple-upgrade-20261013-r3`** (tip `5df5a3f0f41a15027f06f8a5d9b9c16755cca566`),
with the round's verification harness on `chore/s4post-verification-harness`.

**Gates that are FAILING or not granted, stated up front rather than buried:**

- `PIPD_S4_FULL_PASS` — **NOT GRANTED**. The public release gate is **`FAIL-CLOSED / HOLD`**.
- Independent acceptance of the S4POST candidate: latest verdict **`FAIL_CHALLENGE`** (9 findings, all
  inside the round's own verification harness). No round here has produced a `PASS_CHALLENGE`.
- Four-host UAT, Portal scan/review/publish, security scan and a real candidate build: **`NOT_EXECUTED`**.
  Four owner supplies and four owner-only acts are outstanding — see the candidate's
  `OWNER_ACTION_REQUEST.md`.
- The **`v0.1.1-preview.3`** wheel carries the known Trace false-PASS defect (`FAIL_CHALLENGE`,
  product scope). **`v0.1.1-preview.4`** supersedes it: it is built from the merged `main` that
  repairs the D1 negation-polarity/scope and D2 clause-boundary defects and adds the ClaimCeiling
  claim-shape guard, and it re-publishes the **same eight** skills (no ninth skill, no MCP, no Apps,
  no Hooks). Every limitation listed above still holds for it.

Everything below this section describes the **published preview**, not this candidate.

## Install

Install is one of **three routes**, and [`docs/install/README.md`](docs/install/README.md) is the
single source of truth for all three:

- **Web** — no public plugin directory listing exists yet, so the Web route today is the single
  document **[`docs/install/PIPD_WEB_FALLBACK.md`](docs/install/PIPD_WEB_FALLBACK.md)** — a real,
  downloadable file (not a generator you have to be able to run), with its digest recorded in
  `docs/install/PIPD_WEB_FALLBACK.md.sha256`. Its ceiling is **`DOC_MOUNT_ONLY`**: no Python CLI, no
  MCP, no repository write, no S4 acceptance. A directory listing, once one is published and
  account-visible, is a *conditional* future route and is not available today.
  Signs to check before you trust that file: it must carry the same `release_id`, `release_commit`
  and `content_sha256` as the `.sha256` file beside it, and the generating command in
  `docs/install/README.md` must reproduce those bytes.<span></span>
- **Web — a private ChatGPT plugin (added 2026-10-14, verified on one account).** The public Plugin
  Directory route is still closed: on 2026-10-14 `platform.openai.com/plugins` itself answered
  *“You need a verified developer identity before you can create or upload a plugin.”* — an owner
  identity/KYC step. A **private** plugin does not need it. Download the **release asset**
  `https://github.com/shw097-team/PIPD-LS-SP/releases/download/v0.1.1-preview.4/pipd-ls-sp-public-skills.zip`
  (**68,357 bytes**, sha256 `545e359a5ca6abc7bcbbaa2316f8e062244ad4a132ae1ae839bc9a8e17d95d75` — the digest the
  release's own `SHA256SUMS` carries; one plugin root `pipd-ls-sp-public-skills/`, one `plugin.json`, 8 ×
  `skills/<name>/SKILL.md`, no MCP/Actions/Hooks) and in ChatGPT do: `chatgpt.com/plugins` →
  **Plugins** → **Add** → **Upload plugin archive** → pick the ZIP → **Add plugin** →
  **Install plugin** → **Set up**. It then appears under *Settings → Plugins → Installed plugins* and
  its skills are callable as `@skill-name` in a chat. **Verified:** creation, installation and one
  `@pipd-route-intake` invocation whose fail-closed rule fired — per-action log, tree dumps and
  screenshots in `PIPD_S4_R5Y_GPT_PLUGIN_EVIDENCE_RETURN/09_ui_fda/`. **Not verified:** that your
  account shows the same upload entry (that is an account entitlement, not a package property) and any
  directory listing. If the entry is missing or the ZIP is refused, fall back to the single document
  route above.

  *Superseded artefact, kept only as history:* the R5Y evidence-branch ZIP
  `.hgk/rounds/R5Y-20261014-gpt-plugin-publication/04_package/build/build-a/pipd-ls-sp-public-skills.zip`
  (**68,355 bytes**, sha256 `2f9ae010a6eba90787037a93a17e77f50bbc29dea5628f6fbe3e0f278fd2d199`) is the
  pre-release build frozen at `062d84ae`. Do not install it: it is not the bytes the release serves, and
  its digest appears in no `SHA256SUMS` asset of `v0.1.1-preview.4`.
- **Agent** — one copy-paste prompt,
  [`docs/install/PIPD_AGENT_INSTALL_PROMPT.md`](docs/install/PIPD_AGENT_INSTALL_PROMPT.md), for the
  four supported hosts (Hermes Agent, Codex Desktop (GUI), Codex CLI, Claude Code). Each host must
  prove **real discovery** and an **8/8 effective load** of the eight skills; file presence is not
  evidence, and a host that only copied files reports `NOT_VERIFIED`.

Version pin, hashes, uninstall/rollback and how to report a failure live in
[`docs/install/README.md`](docs/install/README.md).

## Start here

| | |
|---|---|
| **Installable preview** | tag **`v0.1.1-preview.4`** — Apache-2.0 |
| **Release page** | https://github.com/shw097-team/PIPD-LS-SP/releases/tag/v0.1.1-preview.4 |
| **Download the tag, not the branch** | `main` now carries the repaired code, but a branch tip is a moving target. The **immutable** bytes are the tag's. |
| **Superseded** | `v0.1.0-preview.1`, `v0.1.0-preview.2` and `v0.1.1-preview.3` — all still downloadable. `.1` ships the two defects described below, `.2` predates the S4-R2 repairs and `.3` predates the D1/D2 semantic repair. Use `.4`. |
| **What is not claimed** | [Claim ceiling](#claim-ceiling) and the release notes |

## Choose your path: CLI or Skills

The published wheel and a chat-host skill pack are **two different artefacts with two different
boundaries**. Pick the one your job needs — installing the wheel does not make the eight logical
skills appear in a web chat host, and mounting the pack does not put `pipd` on your machine.

**Current distribution — `pipd-ls-sp 0.1.1a5`, built from this repository's canonical source.**
Since the U04 cutover the canonical compiler lives in `shw097-team/SBL` under `integrations/pipd/`; the
first distribution built from it is `0.1.1a5`, released under the tag `pipd-ls-sp-v0.1.1a5`:

```bash
curl -fsSLO https://github.com/shw097-team/SBL/releases/download/pipd-ls-sp-v0.1.1a5/pipd_ls_sp-0.1.1a5-py3-none-any.whl
curl -fsSLO https://github.com/shw097-team/SBL/releases/download/pipd-ls-sp-v0.1.1a5/SHA256SUMS
sha256sum -c SHA256SUMS --ignore-missing
python -m pip install ./pipd_ls_sp-0.1.1a5-py3-none-any.whl
```

`pipd_ls_sp-0.1.1a5-py3-none-any.whl` — sha256 `ff3d0f69a509df36d301d6ab631ecc723c3a2594ceaf656e42582f7359050418`.
The 8-skill bundle `sbl-tpm-sp-skills-0.1.1a5.zip` (sha256
`418c33f3397ac9564fa881b2a747a4bedf97dc2510c2c301bca3b6c7924a4a95`) ships on the same release. The
`v0.1.1-preview.*` paragraphs below describe the **historical** assets, which stay downloadable and are
not rewritten.

**CLI / headless harness (historical: `v0.1.1-preview.4`)** — download the immutable wheel published under the **`v0.1.1-preview.4`**
tag (`pipd_ls_sp-0.1.1a4-py3-none-any.whl`; published digest
`3b59a985dc9fc1cd4c1c5ca9a7b779122459ab7cadc8f439e17063d6c934cc0c`, verified against the tag's
`SHA256SUMS`). Install with **Python >= 3.11** into a **virtual environment**, then run `pipd doctor`.
The wheel carries the Python **13-command CLI** and the **19 installed schemas**; it does **not**
install or auto-load the eight logical skills into a web host.

**Skills / document consumption** — the versioned mount pack
`dist/mount/PIPD-LS-SP_S4_WEB_MOUNT_v0.1.1-preview.3.zip` (with its `.sha256` sidecar and the
`MANIFEST.sha256` inside the unpacked directory) — published as a release asset of the same tag
(`v0.1.1-preview.3`). `v0.1.1-preview.4` ships the Wheel, the private skills-only plugin ZIP, the
source ZIP, the release notes and the Web fallback document; the pack above remains the **last
published mount pack** (a preview.4-stamped pack is a deferred item, not a release gate). Two
sub-options:

- **(a) native skill uploader** — a host that has a real native skill uploader could register the
  pack; this path is **not yet demonstrated here**.
- **(b) manual document / Knowledge attachment** — attach `SKILL.md` plus the short starter prompt
  (`PIPD_LS_SP_QUICKSTART_PROMPT.md`) to a conversation or Project Knowledge. This document path
  does **not** execute `pipd` on the reader's machine.

## Quickstart

Copy-paste, from a shell. Requires **Python >= 3.11** and `curl`. The installable identity is the
**immutable** tag `v0.1.1-preview.4`; `main` is rolling, so pin the tag rather than the branch.

### bash / POSIX

```bash
set -e                             # stop at the first failing step; no step fails silently
# 1. Fetch the published wheel and the checksum list, from the immutable tag.
BASE=https://github.com/shw097-team/PIPD-LS-SP/releases/download/v0.1.1-preview.4
curl -fsSLO "$BASE/pipd_ls_sp-0.1.1a4-py3-none-any.whl"
curl -fsSLO "$BASE/SHA256SUMS"

# 2. Verify the bytes. Check exactly what step 1 downloaded: SHA256SUMS lists every published asset
#    of this release, but only the wheel is present here, so select its line. This is the ONLY
#    integrity check offered: there is no install-time or startup cryptographic readback, and no
#    release signature.
#    Published wheel digest: 3b59a985dc9fc1cd4c1c5ca9a7b779122459ab7cadc8f439e17063d6c934cc0c
grep '  pipd_ls_sp-0.1.1a4-py3-none-any.whl$' SHA256SUMS | sha256sum -c -
#    expect: pipd_ls_sp-0.1.1a4-py3-none-any.whl: OK
#    Alternative, only after fetching EVERY asset SHA256SUMS lists, the whole file checks clean:
#      curl -fsSLO "$BASE/pipd-ls-sp-v0.1.1-preview.4-source.zip"
#      curl -fsSLO "$BASE/PREVIEW_NOTES_v0.1.1-preview.4.md"
#      curl -fsSLO "$BASE/pipd-ls-sp-public-skills.zip"
#      curl -fsSLO "$BASE/PIPD_WEB_FALLBACK.md"
#      curl -fsSLO "$BASE/PIPD_WEB_FALLBACK.md.sha256"
#      sha256sum -c SHA256SUMS       # expect one ": OK" line per listed asset (six here)

# 3. Install into a virtual environment.
python -m venv .venv
. .venv/bin/activate 2>/dev/null || . .venv/Scripts/activate   # POSIX: .venv/bin/ ; Windows: .venv/Scripts/
python -m pip install ./pipd_ls_sp-0.1.1a4-py3-none-any.whl

# 4. Check the install, then use it.
pipd doctor                        # expect: {"verdict": "PASS", ...}
pipd --help                        # 13 commands

# 5. Start a project. Both of these lines were executed against the published wheel.
pipd --root ./myproject init      # -> exit 0; creates docs/ schemas/ src/ tests/ dist/
pipd doctor                       # -> {"verdict": "PASS", ...}, and it names the schema source it resolved
```

### Windows (PowerShell)

```powershell
$ErrorActionPreference = 'Stop'   # stop at the first failing step; no step fails silently
# 1. Fetch the same wheel and checksum list, from the immutable tag.
$Base = "https://github.com/shw097-team/PIPD-LS-SP/releases/download/v0.1.1-preview.4"
Invoke-WebRequest -Uri "$Base/pipd_ls_sp-0.1.1a4-py3-none-any.whl" -OutFile "pipd_ls_sp-0.1.1a4-py3-none-any.whl"
Invoke-WebRequest -Uri "$Base/SHA256SUMS" -OutFile "SHA256SUMS"

# 2. Verify the wheel against its published digest. SHA256SUMS lists every published asset of this
#    release but only the wheel was fetched, so compare the wheel's own hash to the published literal.
$expected = "3b59a985dc9fc1cd4c1c5ca9a7b779122459ab7cadc8f439e17063d6c934cc0c"
$actual = (Get-FileHash -Algorithm SHA256 -Path "pipd_ls_sp-0.1.1a4-py3-none-any.whl").Hash.ToLower()
if ($actual -ne $expected) { throw "wheel SHA-256 mismatch: $actual" }
"pipd_ls_sp-0.1.1a4-py3-none-any.whl: OK"   # expect this line

# 3. Install into a virtual environment.
python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "python -m venv failed (exit $LASTEXITCODE)" }
.\.venv\Scripts\Activate.ps1
python -m pip install .\pipd_ls_sp-0.1.1a4-py3-none-any.whl
if ($LASTEXITCODE -ne 0) { throw "pip install failed (exit $LASTEXITCODE)" }

# 4. Check the install, then use it.
pipd doctor                        # expect: {"verdict": "PASS", ...}
if ($LASTEXITCODE -ne 0) { throw "pipd doctor failed (exit $LASTEXITCODE)" }
pipd --help                        # 13 commands
if ($LASTEXITCODE -ne 0) { throw "pipd --help failed (exit $LASTEXITCODE)" }
pipd --root .\myproject init       # --root before the subcommand (the global form)
if ($LASTEXITCODE -ne 0) { throw "pipd init failed (exit $LASTEXITCODE)" }
```

### Unverified one-line install (no hash check)

If you do not need to check the bytes against the published digest, pip can fetch and install the
wheel in one line:

```bash
python -m pip install "https://github.com/shw097-team/PIPD-LS-SP/releases/download/v0.1.1-preview.4/pipd_ls_sp-0.1.1a4-py3-none-any.whl"
```

This performs **no hash verification** - pip installs whatever the URL serves when you run it. Use
the verified path above when the bytes matter.

Beyond that the pipeline is `intake` -> `compile-pi` -> `bind-pd` -> `compile-ecp` /
`compile-tqaep` -> `validate`, and **the middle steps take real inputs, not free text** — verified
against the CLI rather than assumed.

### Run it: one command, no shell expertise needed

> **Migration note (U04):** the two self-locating scripts (`run.sh`, `run.ps1`) are not shipped in
> this copy — the host repository refuses to carry `.sh`/`.ps1` files. The chain below is the same
> work, and it is the supported route here. See `MIGRATION-NOTES.md`.

The chain checks its preconditions first and fails typed with a non-zero exit when one is missing;
it prints a success token only after `validate` has passed.

### Run it: the whole compiler chain, copy-paste

These are the exact commands that produced the checked-in [`examples/first-run/`](examples/first-run/)
fixture, run from this checkout root. For `init`, `intake`, `profile`, `compile-pi`, `bind-pd`,
`compile-ecp`, `compile-tqaep`, `validate` and `doctor`, `--root` is a global option and must
precede the subcommand; `project` and `export` **additionally** accept `--root` after the
subcommand. `--root <dir>` points at a workspace (use a directory outside the tree so scratch files
never pollute the checkout), and the fixture paths are the real files in this repository. Nothing
below is pinned to a developer machine: `PY` is your own interpreter and `PYTHONPATH` is this
checkout's `src/` (any Python >= 3.11 with `jsonschema` works):

```bash
PY=python3                                              # any Python >= 3.11 + jsonschema
export PYTHONPATH="$PWD/src"                            # this checkout's src/
ART="$(mktemp -d)/pipd-first-run"                       # a scratch dir OUTSIDE the checkout
rm -rf "$ART" && mkdir -p "$ART"
CTX="$ART/ctx"; mkdir -p "$CTX"          # RepoContext dir bind-pd probes
git -C "$CTX" init -q                    # bind-pd binds only a RESOLVED git toplevel (fail closed)

"$PY" -m pipd_ls_sp.cli --root "$ART" init                 # exit 0; creates docs/ schemas/ src/ tests/ dist/

# intake: compile source clauses into an IntentCard (typed refusal if the source does not exist)
"$PY" -m pipd_ls_sp.cli --root "$ART" intake \
  --goal "Compile this example clause source into a validated PI to PD to ECP to TQAEP chain." \
  --source examples/first-run/source.txt \
  --constraint "candidate-only, no release" \
  --non-goal "no upstream document bodies copied" \
  > "$ART/intent.card.json"            # -> INTENT-9f8e9a1b6dc344fc

"$PY" -m pipd_ls_sp.cli --root "$ART" compile-pi \
  --intent "$ART/intent.card.json" --profile LITE \
  > "$ART/pi.json"                     # -> PI-50952b3a3822b28c

# bind-pd derives a READ-ONLY RepoContext from --repo-root (an empty git checkout, so it is
# stable) and REFUSES a root that is not a resolved git toplevel;
# the same intent + the same RepoContext.root reproduce every digest byte for byte.
"$PY" -m pipd_ls_sp.cli --root "$ART" bind-pd \
  --pi "$ART/pi.json" --repo-root "$CTX" \
  > "$ART/pd.json"                     # -> PD-336c387a7aa71c9d

"$PY" -m pipd_ls_sp.cli --root "$ART" compile-ecp \
  --pd "$ART/pd.json" --pi "$ART/pi.json" \
  > "$ART/ecp.json"                    # -> ECP-73cf63e34806711a

"$PY" -m pipd_ls_sp.cli --root "$ART" compile-tqaep \
  --pi "$ART/pi.json" --ecp "$ART/ecp.json" \
  --maker HERMES-MAKER --checker GLM-5.3-FLASH-AO-LANE --checker-receipt deleg_example/lane-C \
  > "$ART/tqaep.json"                  # -> TQAEP-2bf7b7e31b820fb7 (claim ceiling TQAEP_DESIGNED)

# The 13-command CLI has no "assemble" verb, so bundle the four records with the checked-in helper.
"$PY" examples/first-run/assemble_bundle.py \
  "$ART/pi.json" "$ART/pd.json" "$ART/ecp.json" "$ART/tqaep.json" > "$ART/bundle.json"

# validate: schema + semantic invariants over two schema records each
"$PY" -m pipd_ls_sp.cli --root "$ART" validate --bundle "$ART/bundle.json"
# -> exit 0; {"verdict": "PASS", "checked": 4, "findings": []}
```

Every `sha256` is stable across runs: the same fixture driven twice into two fresh workspaces against
the same `CTX` produced identical `intent.card.json`, `pi.json`, `pd.json`, `ecp.json` and `tqaep.json`
(`PI`/`TQAEP` depend only on the fixture; `PD`/`ECP` also bind `CTX` — so keep `CTX` fixed to reproduce
them). Full digests are in [`examples/first-run/README.md`](examples/first-run/README.md). A source
locator that does not exist (`--source examples/first-run/missing.txt`) is refused
`{"code": "AUTHORITY_UNKNOWN"}`, exit `2`, with no artefact written — the CLI is deliberately strict
rather than guessing on your behalf.

Known limitation: there is **no CLI verb that assembles a bundle**, which is why the block calls
`examples/first-run/assemble_bundle.py` (it only re-serialises the four records). Run
`pipd <command> --help` for each command's real flags. `pipd doctor` is the self-check; it reports
which schema source it resolved and refuses to be silent about it.

The three `--root` forms the parser really accepts, each run from a scratch directory and observed
exiting `0`:

```bash
pipd --root ./demo init                  # exit 0 — global --root before the subcommand
pipd project --root ./demo --dry-run     # exit 0 — subcommand-local --root (project only)
pipd export --root ./demo --dry-run      # exit 0 — subcommand-local --root (export only)
```

`pipd init --root ./demo` is refused (exit `2`): `init` does not accept a subcommand-local `--root`,
which is the boundary the paragraph above describes.

## What is in this tree

| path | what it is |
|---|---|
| `schemas/` | the **19 canonical machine-contract families** + `registry.json` (Draft 2020-12, `additionalProperties: false`), written by the Codex bounded writer |
| `src/pipd_ls_sp/` | the plugin runtime (12 modules): intake, profile binding, the PI→PD→ConstructionContract→ECP/TQAEP pipeline, deterministic validators, the 13-command CLI |
| `skills/` | the **8 published skills** — `pipd-route-intake`, `pipd-profile-tailor`, `pipd-pi-compile`, `pipd-pd-bind`, `pipd-execution-contract`, `pipd-assurance-tqaep`, `pipd-authority-source`, `pipd-package-project` — each with `SKILL.md`, `references/`, `schemas/` and `tests/cases.yaml` |
| `tests/` | deterministic tests: the S0 contract set, the LITE vertical slice, negative and adversarial cases, rollback, secret patterns, tooling guards, quarantine disposition (POS/NEG/EDGE), oracle-disagreement, evidence-MD hard-gate refusal |
| `tools/` | governed-round tooling: knowledge probe, HGK admission driver, kanban receipts, CLI smoke, publication manifest and attestation, destructive-destination guards |
| `docs/` | `S0_CONTRACT_SPEC.md` (the frozen spec that drives `schemas/`), the round disclosure records, and [`FRONT_PAGE_HISTORY.md`](docs/FRONT_PAGE_HISTORY.md) |
| `fixtures/` | typed negative and golden fixtures used by the tests |
| `examples/` | runnable fixtures: [`examples/first-run/`](examples/first-run/) is the real input the compiler walk-through above uses, and `examples/self-bootstrap/` is the self-bootstrap transcript |
| `openspec/` | the change proposals these rounds implemented |
| `dist/` | **the published build** — wheel `pipd_ls_sp-0.1.1a4-py3-none-any.whl` (SHA-256 `3b59a985…`), its `.sha256`, `WHEEL_MANIFEST.json` and `web/` packs |
| `.hgk/` | the rounds' governance record: admission, kanban, knowledge index, preflight, round receipts and surfaces |
| `pyproject.toml` | packaging metadata (`pipd-ls-sp` 0.1.1a4, `requires-python >= 3.11`, `license = "Apache-2.0"`) |
| `LICENSE`, `NOTICE`, `OWNER_LICENSE_DECISION.yaml`, `SBOM.cdx.json` | the Apache-2.0 grant, its attribution, the owner's operative decision record (`decision: Apache-2.0`) and the machine-readable component inventory |
| `PROVENANCE.md`, `ACCEPTANCE.md` | how the artefacts were produced, and what was accepted |
| `.agents`, `.hermes`, `.gitattributes`, `.gitignore` | agent and repository plumbing |

## Claim ceiling

Status words are kept separate on purpose, and none of them is upgraded by this page.

| claim | state |
|---|---|
| `PROMPT_COMPILE_PASS` | claimed locally, evidence in `.hgk/preflight/` |
| `HGK_ADMITTED` | claimed locally — the HGK lifecycle reached `EXECUTING` |
| `LOCAL_QUALIFIED` | claimed locally (deterministic tests + CLI smoke) |
| `RUNTIME_READY` | **NOT claimed** |
| `INDEPENDENT_PASS` | **NOT claimed as a full pass.** Verifiers working only from published bytes returned scoped receipts — `9/9` on the preview, `6/6` on a defect repair, and a further `PASS` on `v0.1.0-preview.2` — but the S0–S4 challenge as a whole is **`PARTIAL_CHALLENGE`**, not a full pass |
| `PUBLICATION_APPROVED` | **GRANTED for the limited preview only** — owner licence decision `Apache-2.0`. **`G-RELEASE_FULL_PASS` is NOT granted.** |
| `RELEASED` | limited to `OWNER_AUTHORIZED_OPEN_SOURCE_PREVIEW_BETA_PUBLISHED`, at the preview tags |
| `PRODUCTION_VERIFIED` | **NOT claimed** |
| `PRIVATE_PLUGIN_CREATED_INSTALLED_INVOKED` | **verified 2026-10-14** on the owner's own ChatGPT account — evidence `PIPD_S4_R5Y_GPT_PLUGIN_EVIDENCE_RETURN/09_ui_fda/` |
| `PUBLIC_DIRECTORY_PUBLISHED` | **NOT claimed** — the Portal blocks at developer identity verification; no submit/review/publish was performed |
| `PUBLIC_CONSUMER_VERIFIED` | **NOT claimed** — no unrelated third party has installed it from a directory |

**Stage coverage.** S0 and S1 were reached; the S2–S4 work followed. **S5 (HGK live), S6 (GENIE),
S7 (JIT), S8 (SWOF/SGM), PRE-W3 and the 22 inactive external technologies are deferred.**

## Known limitations

Stated here rather than left only on the release page, because they matter when you decide what to
build on this:

1. **No vulnerability or supply-chain scan of this project's own source.** A dependency audit of the
   declared closure found no known advisories, but `pipd-ls-sp` is not on PyPI and was itself
   **skipped** by that audit — the dependency closure was scanned, the source was not. There is also
   **no lock file**, so the audited set is not necessarily the set you will install.
2. **No release signature and no build attestation.** Only a published SHA-256, for manual
   download-consistency checking. That is not provenance, and it does not bind the artefact to a
   builder identity.
3. **The SPEC/DEL denominator stays `28 evidenced / 10 active gaps / 19 deferred` of 57 rows.**
   `EVIDENCED != PASS`; not every applicable row has been individually audited.
4. **`RELEASE_MANIFEST@1` (`DEL-018`)** — was `FAIL` / `EVIDENCE_GAP` on the release line and was
   **closed** for the published subject by regenerating the projection; that closure ships in
   `v0.1.0-preview.2`. **On this branch it is `PASS`.** After the repaired lineage was merged here the
   tree briefly had `253` product paths with one — `docs/FRONT_PAGE_HISTORY.md` — carrying no
   release-evidence disposition, because the **evidence manifest's seal was stale by four rounds**
   (bound to the R5R execute commit `9667783`) and had never enumerated a file that only ever existed
   on this branch's line. Re-sealing the evidence manifest from the current tree and rebuilding the
   projection resolved both: `--verify` exits `0`, the manifest carries `1085` entries, and
   `--check --current` now exits `0` with `253/253` covered and `0` violations, the file correctly
   disposed `NOT_PUBLISHED`. No tag moved, no release asset changed, no validator edited.
5. **Native Windows symlink / junction / reparse behaviour is not certified** beyond the tested
   scope (`TT-R5P-01`, `TT-R5P-06`).
6. **`v0.1.0-preview.1` carries two defects**, both reproduced against its published bytes:
   `validate` did not resolve wheel-installed schemas the way `doctor` does (it exited `2` with
   `INPUT_SHAPE_INVALID`, looking for `<cwd>/schemas/PI-PKG.schema.json`), and a bundle assembled
   from the compilers' unmodified stdout was rejected because `compile-pi` emitted a top-level
   `_profile_meta` that `PI-PKG` forbids. **Both are fixed in `v0.1.0-preview.2`.** A published tag
   is never rewritten, which is why the fix arrived as a successor release rather than an edit.

## Licence

**Apache-2.0** (`LICENSE`, `NOTICE`). The owner granted it in round R5Q
(`FAR-PIPD-R5Q-LICENSE-001`); `OWNER_LICENSE_DECISION.yaml` records `decision: Apache-2.0`. The
grant is effective wherever this tree is checked out, including `main`.

## History and evidence

This page is a rewrite, and it has now been rewritten twice — which is itself recorded rather than
hidden.

- **R6** replaced an append-only log (an R3 body, an R4 section, an R5Q banner, a dangling `## 8.`
  fragment) whose sections contradicted each other. The section that held the R3 audit-repair
  snapshot, and the trailing fragment, are preserved **verbatim** in
  [`docs/FRONT_PAGE_HISTORY.md`](docs/FRONT_PAGE_HISTORY.md).
- **R8** merged the repaired lineage into `main` and **re-derived every claim on this page** against
  the merged tree rather than carrying the previous wording over. The pre-merge text asserted five
  things that the merge made false — that this branch's wheel was an old R3 build, that the
  Apache-2.0 grant did not apply here, that `main` was not the distribution entry point, that
  installing from here was "the wrong thing to do", and that the defects were fixed only off-branch.
  A front page that keeps saying those things after the merge is worse than one that says nothing.

The round-by-round record stays in the tree: `docs/ROUND_DISCLOSURE.md`,
`docs/ROUND3_DISCLOSURE.md`, `docs/S0_CONTRACT_SPEC.md`, and the per-round receipts and registers
under `.hgk/`. **Nothing was deleted to make this page read better — the history is moved, not
removed.**


## B1 closure 2026-10-28

`b1_closure_20261028/` is the evidence index for the FHS-MSC B1 bootstrap-repair round (PKG_00~08) on the PIPD side.

- `b1_closure_20261028/EVIDENCE_INDEX.md` — question → file#line → the command that reproduces it
- `b1_closure_20261028/MANIFEST.json` — per-file bytes + sha256 (the packet is verifiable offline)
- `b1_closure_20261028/HANDOVER.md` — ten-point orientation for an external reviewer

Claim ceiling (measured, not asserted): `mission_complete true` under `b1_closure_20261028/evidence/GATES.json`
means the gate conjunction passed, no residual blocker remained, and every blocking declaration was
owner-ruled. It does **not** mean release (`release: NOT_RUN`), promotion, or third-party acceptance.
Databases, raw lane output, the owner key envelope and credentials are excluded by design.
