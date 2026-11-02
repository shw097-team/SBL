# SBL private-overlay CLI count — correct 14 to 13, and forbid the 14 claim

## Why

The SBL private-overlay snapshot and its evidence text described the original PIPD CLI as having
**14 commands**. The measured inventory is **13**, and the `repair` command is one of the thirteen.
Original criterion E7 states *exactly 13 commands (no 14th)*, so the 14 claim does not merely
mis-describe the upstream tool — it asserts an inventory the original criterion forbids.

Three committed documents — plus the evidence object's `actual_cli_count` — carried the wrong number on
branch `repair/sbl-tpm-sp-rc2` at `bb419a1`:

| file | line | text at `bb419a1` |
|---|---|---|
| `docs/PRE_V2_HANDOFF_20261102.md` | 22 | "Actual PIPD main has **14 commands**, including repair" |
| `sbl_sp/plugins/tpm_sp/pre_v2/upstream/README.md` | 22 | "CLI has 14 commands (including `repair`); historical descriptions saying 13 are not an exact inventory" |
| `sbl_sp/plugins/tpm_sp/pre_v2/private-overlay/references/contracts/pre-v2-routing.md` | 20 | "Original PIPD main `f6335a94…` exposes 14 commands" |
| `evidence/pre-v2-20261102/summary.json` | — | `"actual_cli_count": 14` beside `"historical_cli_count": 13` |

The README variant is the worst of the four: it inverted the correction by telling a reader that the
accurate number is the inaccurate one. A private overlay whose stated purpose is an exact, source-bound
description of the upstream tool cannot carry a command count that its own referenced commit does not
have — every downstream denominator that cites "the 14-command CLI" inherits the error.

## What changes

- The three documents above state **13 commands (13 including `repair`; original E7 forbids a 14th)**
  and, where the historical confusion is worth recording, say that descriptions of 14 are not an exact
  inventory.
- `evidence/pre-v2-20261102/summary.json` carries `"actual_cli_count": 13` (it said `14` at
  `bb419a1`); `"historical_cli_count": 13` was already correct, so the two fields now agree instead of
  contradicting each other inside the same evidence object.
- The correction is recorded as a committed fix on `repair/sbl-tpm-sp-rc2`
  (`dadeb91 docs(pre-v2): correct the PIPD CLI count to 13 (repair included, E7 forbids a 14th)`), so the
  number is attributable to a revision rather than to a working-tree edit.
- **The 14 claim is forbidden from re-entering the repository.** Any text describing the original PIPD CLI
  inventory says 13; a review that finds 14 is a defect, not a stylistic choice.

Measured inventory (13 subcommands, `repair` included):

```
init  intake  profile  compile-pi  bind-pd  compile-ecp  compile-tqaep
validate  doctor  project  export  diff  repair
```

## Not in scope

- **Not a Native qualification.** No native host binding, receiver ACK, Protected Checker receipt or
  executor binding is claimed; this change corrects a number in documentation and evidence text.
- **Not a Release.** No version bump, tag, publication, merge to `main`, or claim-ladder movement.
- Not a change to the upstream PIPD code: the 13 commands are counted, not added to or removed from.
- Not a change to the 19 canonical Schema families, the patch bytes, or the overlay's behavioural claims.
- Not re-opening the other denominators (949/192/282 and 149/50/39/96); they are tracked separately and
  are outside this correction.
- Not a re-derivation of E7 itself: E7 is quoted as the governing criterion, not renegotiated.

## Impact

- Affected: `docs/PRE_V2_HANDOFF_20261102.md`, `sbl_sp/plugins/tpm_sp/pre_v2/upstream/README.md`,
  `sbl_sp/plugins/tpm_sp/pre_v2/private-overlay/references/contracts/pre-v2-routing.md`, and
  `evidence/pre-v2-20261102/summary.json` (`actual_cli_count` 14 → 13).
- Unchanged: `sbl_core/`, `sbl_sp/` code, `contracts/`, the patch, the CI configuration, every gate.
- Consumers of the overlay's description get a count that matches the referenced commit hash
  `f6335a94157c61da75d92121d14c43feb413e981`; consumers that copied the 14 into their own text must
  correct it there, which is stated rather than assumed.
- Claim ceiling: unchanged and still candidate-level — the overlay description is not a qualification.
