# SBL private-overlay CLI count — tasks

Status legend: `[x]` done and read back · `[ ]` open, owner named · `[!]` blocked on an owner/native decision.

Repository: SBL · branch `repair/sbl-tpm-sp-rc2` (the `codex/sbl-tpm-sp-pre-v2-20261102` pre-v2 line).
Defect present at `bb419a1`; correction committed as
`dadeb91 docs(pre-v2): correct the PIPD CLI count to 13 (repair included, E7 forbids a 14th)`.

## Measured inventory (the authority for every number below)

- [x] Count the subcommands at the commit the overlay cites,
      `f6335a94157c61da75d92121d14c43feb413e981`, in the PIPD repository:
      `git show f6335a94…:src/pipd_ls_sp/cli.py | grep -o 'add_parser("[a-z-]*"' | wc -l` → **13**.
- [x] Confirm `repair` is one of them:
      `git show f6335a94…:src/pipd_ls_sp/cli.py | grep -c 'add_parser("repair")'` → **1**.
      Inventory: `init intake profile compile-pi bind-pd compile-ecp compile-tqaep validate doctor
      project export diff repair`.
- [x] Record that original criterion E7 states *exactly 13 commands (no 14th)* — the 14 claim is not a
      rounding difference, it is a forbidden inventory.

## Text correction

- [x] `docs/PRE_V2_HANDOFF_20261102.md:22` — "has **14 commands**, including repair" → "has **13
      commands** (13 including repair; original E7 forbids a 14th)".
- [x] `sbl_sp/plugins/tpm_sp/pre_v2/upstream/README.md:22` — removes the inverted claim that
      descriptions of 13 are inexact; now states 13 and that descriptions of 14 are not an exact
      inventory.
- [x] `sbl_sp/plugins/tpm_sp/pre_v2/private-overlay/references/contracts/pre-v2-routing.md:20` — the
      commit-pinned description now says 13 (including `repair`, per E7).
- [x] `evidence/pre-v2-20261102/summary.json` — `"actual_cli_count": 14` → `13`;
      `"historical_cli_count": 13` was already correct, so the evidence object no longer contradicts
      itself. Verified: `grep -n 'cli_count' evidence/pre-v2-20261102/summary.json` → lines 12 and 13,
      both `13`.

## Verification (run from the SBL repo root)

```sh
grep -rn '14 commands' --include=*.md .            # expect: no match
grep -rn '13 commands' --include=*.md .            # expect: the three corrected documents
git grep -n '14 commands' HEAD -- docs sbl_sp evidence   # expect: no match on the repair head
```

- [x] `grep -rn '14 commands' --include=*.md .` → **0 matches**.
- [x] `grep -rn '13 commands' --include=*.md .` → 3 matches, at
      `docs/PRE_V2_HANDOFF_20261102.md:22`, `sbl_sp/plugins/tpm_sp/pre_v2/upstream/README.md:22`,
      `sbl_sp/plugins/tpm_sp/pre_v2/private-overlay/references/contracts/pre-v2-routing.md:20`.
- [x] Re-count against the cited original commit (command above) still returns **13** with `repair`
      present, i.e. the document now matches the code and not the other way round.
- [x] `git status --porcelain` on the repair branch is clean at the correcting commit — the number is
      attributable to a revision, not to an uncommitted working-tree edit.

## Guard against re-introduction

- [x] The rule is recorded here and in the corrected text: **any description of the original PIPD CLI
      inventory says 13 (including `repair`); 14 is a defect.**
- [ ] Optional CI guard (owner decision): a one-line `grep -rn '14 commands'` over `docs/`, `sbl_sp/`
      and `evidence/` that fails the build on a match. Not added in this change, because the change
      corrects claims and does not touch CI configuration.

## Explicitly not done

- [ ] No change to the upstream PIPD CLI, its subcommand set, or its patch bytes.
- [ ] No re-derivation or renegotiation of criterion E7.
- [ ] No change to the 19 canonical Schema families or to the other tracked denominators.
- [ ] No Native qualification, no Release, no merge to `main`.
