# PIPD-LS-SP — user guide

**This is the only user guide.** It is task-first: find the row for what you are trying to do and
follow it. It is *not* a second installation document — version pins, hashes, the fetch commands,
uninstall and rollback live in exactly one place, [`docs/install/README.md`](install/README.md), and
this guide links there rather than copying it.

Three ceilings apply to everything below, and no result here can lift them:

- `DOC_MOUNT_ONLY` — the Web route is a document drop. It installs nothing and executes nothing.
- `pipd validate PASS` is **not** a full trace qualification for a **published** wheel. The
  `v0.1.1-preview.3` wheel carries the known Trace false-PASS defect (`FAIL_CHALLENGE`, product
  scope) and the source repair lives on `main`. Whether the current `v0.1.1-preview.4` wheel
  (`pipd_ls_sp-0.1.1a4`) inherits that repair is **not established by this guide**: check the tag
  your wheel was built from, and do not read a `validate PASS` as anything more than its own scope.
- **`S4_FULL_PASS` is `NOT_GRANTED`.** `v0.1.1-preview.4` **was published on 2026-10-14** and the
  routes below are usable against it; the earlier `Merge and release HOLD` wording described the
  preview.3-era state and no longer applies. Full S4 qualification, `HOST_QUALIFIED` and production
  remain separately **`NOT_GRANTED`**.

## 0. Which task are you here for?

| Your task | Section |
|---|---|
| "I just want the skills, I have no shell" | [1. Web (GPT-6, Plus/Free)](#1-web--gpt-6-plusfree-no-shell) |
| "Install the 8 skills into my agent host" | [2. Agent hosts](#2-agent-hosts-hermes--codex-desktop--codex-cli--claude-code) |
| "Drive the CLI/Wheel directly" | [3. CLI and wheel](#3-cli-and-wheel) |
| "Something was refused and I don't know why" | [4. Typed refusals](#4-typed-refusals-what-they-mean) |
| "Remove it again" | [5. Rollback and uninstall](#5-rollback-and-uninstall) |

## 1. Web — GPT-6 (Plus/Free), no shell

1. Download **[`PIPD_WEB_FALLBACK.md`](install/PIPD_WEB_FALLBACK.md)** and its digest file
   `PIPD_WEB_FALLBACK.md.sha256` from the same commit.
2. Check the bytes: the file's own header (`release_id`, `release_commit`, `size_cap_bytes`) must
   match the `.sha256` line beside it. If they diverge, stop — you have a mixed pair.
3. Attach the single document to the conversation and ask your task. The document opens with a
   **member inventory** (member path + sha256); a member whose bytes do not match its inventory row
   must be refused rather than used.
4. If a task needs a source the document does not contain, the correct outcome is a **typed NACK**
   naming the missing source — not an invention. `DOC_MOUNT_ONLY` means the document cannot write to
   your repository, cannot run the CLI and cannot be a substitute for an installed plugin.

Installing the **private Skills-only plugin ZIP** instead, and updating one you already installed
under the same `plugin_id`, are both covered in exactly one place:
[`docs/install/README.md`](install/README.md) — see *Updating a plugin you already installed* there.

**Plus vs Free:** both can attach a document; that is the whole of what is verified here. Nothing in
this repository claims that either tier can install, discover or execute the plugin from a public
directory, because no such listing exists yet — that route is `NOT_SUPPORTED` today, not `FAILED`.

## 2. Agent hosts (Hermes / Codex Desktop / Codex CLI / Claude Code)

Use the single copy-paste prompt, [`PIPD_AGENT_INSTALL_PROMPT.md`](install/PIPD_AGENT_INSTALL_PROMPT.md).
For each host the acceptance question is the same, and **file presence is not the answer**:

1. **Discover** — the host lists the eight skills by name from its own registry, not from a directory
   listing you produced.
2. **Effective load** — ask the host to load a skill and report what it loaded. Eight of eight, or
   the host reports `NOT_VERIFIED`.
3. **Positive trigger** — a prompt that should engage a skill does engage it.
4. **Negative trigger** — a prompt that should *not* engage it does not, and a request for a source
   the skill does not have is refused with a typed NACK.
5. **Rollback** — remove it and show discovery is empty again.

Record host name, version, OS, the source SHA you installed from, and the raw transcript. A run
where the host only copied files is `NOT_VERIFIED`, not a pass. Do **not** cite `pipd doctor` as
evidence of host discovery — that command checks the Python distribution, which is a different
thing.

## 3. CLI and wheel

Install from [`docs/install/README.md`](install/README.md) (the published tag's wheel, hash-checked).
Then, in a virtual environment:

```bash
pipd doctor                 # is the installation sane? JSON with --json
pipd intake --goal "…" --source <a path that exists>   # -> IntentCard, or a typed refusal
pipd compile-pi --intent intent_card.json
pipd bind-pd --intent intent_card.json --repo-root <dir>
pipd compile-ecp --intent intent_card.json --pd pd.json
pipd compile-tqaep --intent intent_card.json
pipd validate --records <the records you produced>
```

Two things to keep straight:

- **`version` is a string, and `"1"` is legal.** If a document uses a bare `"1"`, convert it to a
  string rather than "fixing" it to a semver — a wrong-type value is refused, and that refusal is
  the feature working.
- **A `validate PASS` on a published wheel is not a trace qualification** (see the ceilings above).
  Full negative coverage (wrong type, orphan link, wrong hash, missing source) is what
  `tests/test_s4ext_trace_closure.py` exercises on the `main` line; which of that coverage your wheel
  actually carries depends on the tag it was built from. Do not round a `validate PASS` up to a trace
  qualification.

Every verb takes `--json` and writes machine-readable output. Prefer `--json` in scripts: the human
form is for reading, not for parsing.

## 4. Typed refusals, what they mean

A refusal is a result, not a crash. The important distinction is *whose* fault it is:

| Code | Meaning | Your next action |
|---|---|---|
| `TOOL_MISSING` | A helper the checker needs is absent (e.g. PyYAML for `cases.yaml`) | Install the declared dependency; the tool refuses rather than guessing |
| `INTAKE_INVALID` / source NACK | The clause source named does not exist or cannot be read | Fix the path; do not retype the source by hand |
| `REPAIR_SCOPE_FAIL` | A repair subject resolves outside the authorised root | Keep subjects inside the root; a foreign-absolute path is refused on purpose |
| `DESTINATION_SYMLINK` | The output destination is a symlink | Choose a real path; the tool will not follow it |
| `ICON_MISSING` | A required branding asset is absent | Supply the owner-approved asset; generated placeholders are not it |

A refusal you cannot explain is a bug report, not a workaround target.

## 5. Rollback and uninstall

- **Wheel:** remove the virtual environment you installed into, or `pip uninstall pipd-ls-sp`. The
  package writes nothing outside the project directory you point it at.
- **Agent host:** follow that host's skill-removal procedure, then re-run step 1 of section 2 and
  show discovery is empty. An uninstall you cannot demonstrate is not an uninstall.
- **Web:** discard the document. Nothing was installed.
- **Repair:** `pipd repair` records a rollback pointer; read it before deciding, and keep the
  record — the artefact it names is the only copy of the pre-repair state.

## 6. Limits this guide does not paper over

- Four-host UAT, vendor/portal validation, a real public plugin build and a new immutable release are
  `NOT_EXECUTED` in this round. Treat every host claim as `NOT_VERIFIED` until a receipt with a host
  version, a source SHA and a raw transcript exists.
- The repository is large because it carries its own evidence history; that is a known DX cost, and
  it is not a defect in the toolkit.
- macOS is not claimed. Linux and Windows are what the receipts cover.
