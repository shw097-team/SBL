# PIPD-LS-SP — `v0.1.1-preview.3` preview notes

**Tag** `v0.1.1-preview.3` · **distribution version** `0.1.1a3` · **licence** Apache-2.0
**Supersedes** `v0.1.0-preview.2` (still downloadable; it does not carry the S4-R2 repairs)

## What this is

The same S4 command-line contract compiler as `preview.2`, plus the S4-R2 repairs, packaged under a
**new distribution version so that installing it is a real upgrade** rather than a silent replacement
of the same filename. `preview.1` and `preview.2` were both published as
`pipd_ls_sp-0.1.0-py3-none-any.whl` while differing in bytes; this release does not repeat that.

## Assets in this release

| asset | what it is |
|---|---|
| `pipd_ls_sp-0.1.1a3-py3-none-any.whl` | the Python CLI (13 commands) and the 19 installed schemas plus registry |
| `PIPD-LS-SP_S4_WEB_MOUNT_v0.1.1-preview.3.zip` | the chat-host document/skill pack, built for this version, with `MANIFEST.sha256` inside |
| `pipd-ls-sp-v0.1.1-preview.3-source.zip` | the source tree at the release commit |
| `PREVIEW_NOTES_v0.1.1-preview.3.md` | this file |
| `SHA256SUMS` | digests for every asset above |

Installing the wheel gives you `pipd` on your machine. It does **not** load the eight logical skills
into a web chat host; that is what the mount pack is for, and the two are separate consumer packages
on purpose.

## What changed since `preview.2`

1. **A documentation split between the two onboarding paths.** Installing the wheel never made the
   eight skills appear in a chat host, but the front page read as if it might. `README.md` now names
   both paths and their boundaries in one place, and states that the mount pack is a release asset of
   the same tag.
2. **The `--root` statements are now true.** The previous text presented `--root` as a single global
   option that must always precede the subcommand. `project` and `export` additionally accept a
   subcommand-local `--root`. The doc now matches the shipped parser.
3. **Profile input is typed and fails closed.** A record whose `profile`, `axes`, `vetoes`,
   `artifact_depth` or `assurance` has the wrong shape is refused with a finding that names the
   field, while a genuine compiler-issued record is still accepted. Unknown and duplicated axes are
   refused.
4. **Universal identity/trace typing across the 19 schema families** — the S4-R2 repair set already
   present on the branch, now actually deliverable to a reader.

## What this release does NOT claim

- **Not a full acceptance.** The independent challenge over S0–S4 remains **`PARTIAL_CHALLENGE`**.
  Scoped checks passed; a whole-lifecycle pass was never granted.
- **`G-RELEASE_FULL_PASS`, `PRODUCTION_VERIFIED` and `S5_RUNTIME_READY` are not claimed.** S5 and
  beyond (HGK live, GENIE, JIT, SWOF) and the 22 inactive external technologies are deferred.
- **Native skill loading is not demonstrated.** The mount pack's native uploader path has no
  effective-load receipt on any host. The manual / Knowledge document route is what is actually
  offered, and it does not execute `pipd` on the reader's machine.
- **Risk assessment is not automated.** Profiles report `NOT_ASSESSED`; there is no 12-axis risk
  engine. Do not treat a low-risk profile label as a safety approval for irreversible, personal-data
  or otherwise high-risk work — that decision stays with a human.
- **Version-string grammar is deliberately loose.** Artifact `version` fields are type- and
  length-checked, not grammar-checked, because the compiler's own legal output is `"1"`. A stricter
  rule is deferred until a normative syntax exists.
- **Not verified on every platform or host.** The checks behind this release ran on one Windows host
  against one interpreter. Other operating systems and other chat hosts are untested here.

## Verify before you install

```bash
BASE=https://github.com/shw097-team/PIPD-LS-SP/releases/download/v0.1.1-preview.3
curl -fsSLO "$BASE/pipd_ls_sp-0.1.1a3-py3-none-any.whl"
curl -fsSLO "$BASE/SHA256SUMS"
grep '  pipd_ls_sp-0.1.1a3-py3-none-any.whl$' SHA256SUMS | sha256sum -c -
#    expect: pipd_ls_sp-0.1.1a3-py3-none-any.whl: OK
python -m venv .venv && . .venv/bin/activate
python -m pip install ./pipd_ls_sp-0.1.1a3-py3-none-any.whl
pipd doctor          # schema_source should read INSTALLED
```

Upgrading an existing `0.1.0` installation:

```bash
python -m pip install --pre -U pipd-ls-sp==0.1.1a3
```

## Provenance

Built from the release commit on the repository at tag `v0.1.1-preview.3`. The wheel, the mount pack
and the source ZIP are produced from that same commit. `SHA256SUMS` lists every uploaded asset; if a
digest does not match, do not install — report it instead.
