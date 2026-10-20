# SBL — SpecBuild Loop v0.1

SBL is a governed build loop: a request becomes a source-bound specification,
routes to exactly one permitted build target, is applied through a bridge that
can only write inside a declared writeset, is backed by raw evidence, and is
repaired in a bounded cone or escalated. This repository is the **v0.1
candidate build** of that product.

## Status and claim ceiling

**`CANDIDATE_ONLY`.**

- Not released. No version is published, tagged, or promoted.
- Not production. No production claim is made or implied.
- No independent acceptance is claimed. The maker lane cannot accept its own
  work; an independent checker has not yet returned a verdict on this tree.
- What does hold: the test suite runs green locally, and the packaging metadata
  and CI definition are present and parse.

`LOCAL` evidence exists under `evidence/`; that is not the same as acceptance.

## What is implemented

One Shared Core with six modules — goal intake, guided specification, governed
routing, governed build bridge, evidence verification, and bounded repair —
plus three permission-separated specialised principals, a three-mode gate
(`STANDALONE`, `PREW3_SHADOW`, `SWOF_CONNECTED`), a local source-bound
knowledge index, a `sbl-todo` CLI, and a skill/host bridge. Every refusal is a
typed `SBLError` carrying a code from one table. Source and tests live in
`sbl_core/`, `sbl_sp/`, and `sbl_cli/`; the full module map, SP permission
matrix, and mode table are in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Install

Python 3.11 or newer. Product code is standard library only, so the install
pulls no runtime dependencies.

```powershell
python -m pip install -e .
```

The package name is `sbl-v01` and it installs one console script, `sbl-todo`.
The CLI has no `--help` flag; it prints one JSON object per invocation and
refuses unknown subcommands with exit code 2.

```powershell
python -m sbl_cli.sbl_todo --data-dir ./.demo init
python -m sbl_cli.sbl_todo --data-dir ./.demo add --title "buy milk"
python -m sbl_cli.sbl_todo --data-dir ./.demo list --json
```

`--data-dir` is a global option and must precede the subcommand. Without it the
CLI uses `SBL_TODO_HOME`, then `~/.sbl_todo`.

## The three journeys

Full commands, observed output, and each journey's negative case are in
[docs/JOURNEYS.md](docs/JOURNEYS.md).

- **GJ01 — local tool lifecycle.** `python -m sbl_cli.sbl_todo --data-dir ./.demo init` → add → separate-process `list --json` → duplicate refused with exit 3 → `uninstall --yes` leaves no residue.
- **GJ02 — brownfield patch.** Bind a fixture repo's `HEAD`, prepare a writeset order, apply a fix from red to green, then confirm an out-of-writeset write and a stale-`HEAD` write are refused and that rollback restores the baseline bytes.
- **GJ03 — skill bridge.** Discover `skills/sbl_todo/skill.json` through `sbl_sp.bridge.SkillBridge`, prove trigger and non-trigger matching, show `effective_load` refusing when `provider_on` is `False`, and unload with an empty residue.

## Governance model

HG-KSEOS is the only normative control plane for this project: task admission,
effect authorisation, and evidence authority live there. This repository is the
product tree, not a second control plane.

Maker is not checker. The writer lane and the verification lane are separate
processes with separate model pins, and the checker is read-only. A local green
run is a writer-side receipt; only a distinct principal can turn it into a
verdict, and the verdict is capped by the claim ceiling.

Evidence lives under `evidence/`. Gate runs freeze raw stdout/stderr and their
digests in `evidence/gates/`; the source freeze record is
`evidence/source/SOURCE_VERIFY.json`. Claims are made from those receipts, not
from prose.

## Repository layout

| Path | Contents |
|---|---|
| `sbl_core/` | Shared Core: `SBLM01..SBLM06`, DTOs, typed errors, mode gate, G-KNOW, composition root |
| `sbl_sp/` | Three SP manifests, permission checks, challenge signing, `SkillBridge` |
| `sbl_cli/` | `sbl-todo` CLI (`python -m sbl_cli` also works) |
| `skills/sbl_todo/` | Skill manifest and `SKILL.md` for the bridge journey |
| `tests/` | Unit, isolation, and end-to-end tests for GJ01–GJ03 and rollback |
| `tools/` | Source verification, gate receipt runner, secret scan, contract build |
| `evidence/` | Scrubbed raw gate receipts, source-verify record, security scan |
| `docs/` | `ARCHITECTURE.md` and `JOURNEYS.md` |
| `openspec/`, `contracts/`, `_governance/` | Round record, compiled prompt contract, and governance state |
| `pyproject.toml`, `.github/workflows/ci.yml` | Packaging metadata and the candidate CI workflow |

## Not in scope

- No SWOF world connection. `SWOF_CONNECTED` refuses without a native ACK and
  no such ACK exists for this build.
- No 386-donor technology installation. This is one bounded product tree, not a
  platform rollout.
- No release, tag, package publication, deploy step, or production operation.
- No independent acceptance, and no independent acceptance claim.
- No multi-user or remote sync; the todo store is local to one machine.

## Licence

`LICENSE: pending owner ruling`. No licence is granted by this repository, by
its metadata, or by anything it produces.
