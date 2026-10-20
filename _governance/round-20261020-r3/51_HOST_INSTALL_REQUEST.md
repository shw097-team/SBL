# 51 — Host install request (three private plugins)

> **State: `HOST_PENDING`.** These are packages, not installations. No plugin id has been issued, no
> host has loaded anything, and nothing in this repository can change that. Whoever performs the steps
> below owns the receipt; the maker may not write it for them.

Source: built from `candidate/c3-20261020-v1` @ `39c604d52570922fdf84b6df9c9359765643b450`
(`sbl_sp/plugins/__init__.py`, `tools/build_sp_plugins.py`). Byte-deterministic: rebuilding from that SHA
reproduces the same digests (verified twice, two output directories, identical bytes).

## Packages

| Principal | File | Bytes | SHA-256 | Distinct id required |
|---|---|---|---|---|
| TPM-SP | `dist/sbl-tpm-sp-0.1.0.zip` | 2087 | `eb26683dc1657bc897b71bb17822aa7da4bfce1951317e85d73d52802209abc8` | `sbl-tpm-sp` → host-issued id |
| Commander-SP | `dist/sbl-commander-sp-0.1.0.zip` | 2129 | `f981d53fc164b1ef4eb0a3e8fcf4439ca7b1132d76c5956e9961a33b654dcb78` | `sbl-commander-sp` → host-issued id |
| External Challenge-SP | `dist/sbl-external-challenge-sp-0.1.0.zip` | 2200 | `75a904c470bba582e0a7f0c5282c7039b4f9ae4a7decbae334fafc559f148746` | `sbl-external-challenge-sp` → host-issued id |

Each archive contains exactly: `plugin.json`, `skills/<plugin-name>/SKILL.md`, `README.md`.

## What the operator does (per principal, separately)

1. Check the archive digest against the table above before importing.
2. Create a **private** plugin in the workspace (ChatGPT plugin creator, or the equivalent Claude
   skill/plugin surface). One plugin per principal — do not import the three skills into one plugin and
   call it three installs.
3. Record the host-issued plugin id, version and install timestamp.
4. Invoke it with `@` and a trigger sentence; then invoke it with a sentence that must **not** trigger it.
5. Attempt a forbidden action (Commander: sign a verdict; Challenge: write product code) and confirm the
   refusal.
6. Disable it, uninstall it, and read back the residue state.
7. Return the receipt in the shape below. Anything not observed stays `NOT_RUN`.

## Receipt shape (one per principal)

```json
{
  "schema": "SBL-HOST-INSTALL-RECEIPT/1",
  "principal": "tpm_sp | commander_sp | external_challenge_sp",
  "package_sha256": "<from the table>",
  "host": {"surface": "chatgpt_private_plugin", "workspace": "<id>", "operator": "<identity>"},
  "plugin_id": "<host-issued>",
  "version": "<host-shown>",
  "installed_utc": "<iso8601>",
  "effective_load": "PASS | FAIL | NOT_RUN",
  "trigger": {"positive": "<prompt>", "positive_result": "PASS|FAIL", "negative": "<prompt>", "negative_result": "PASS|FAIL"},
  "refusal": {"case": "<forbidden action>", "result": "PASS|FAIL"},
  "uninstall": {"executed": true, "residue": "CLEAN | PRESENT | NOT_RUN"},
  "readback": {"source": "host UI", "screenshot_or_text_sha256": "<hash>"},
  "limits": "what was not observed"
}
```

## What must not be written

- `THREE_PRIVATE_PLUGINS_HOST_VERIFIED` until three distinct host-issued ids exist and each has a
  receipt above.
- `INSTALLED` on the strength of a ZIP existing, a manifest being valid, or a local Python test passing.
- A single shared plugin id presented as three installs.
- A local MCP tool call presented as a cloud plugin capability: a desktop-adapter tool does not become
  available in a web workspace because a private plugin was created there.

## Known constraint on this round

The maker has no host account, no workspace permission and no plugin creator authority. Step 2 could not
be attempted, and pretending otherwise would be the exact failure this document exists to prevent.
The next legal action is a human with workspace rights running steps 1–7; the maker's part (a
checksummed, identity-separated, deterministic package) is done.
