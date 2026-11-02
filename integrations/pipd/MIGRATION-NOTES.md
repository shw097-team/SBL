# Migration notes — what this snapshot does not carry

This directory is a **vendored snapshot** of `shw097-team/PIPD-LS-SP` at `aeb0d4790fd811dcdab6dafee69f7f3c226d84a7`,
taken for the U04 consolidation. The tree is verbatim except for this file and the two-line header in `README.md`.

Eight files were deliberately not copied:

| file(s) | why |
|---|---|
| `examples/first-run/run.sh`, `run.ps1` | SBL ships no `.sh`/`.ps1`/`.cmd`/`.bat` files: a repository invariant test refuses them because LF normalisation would break them. Both scripts remain readable at the pinned SHA above. |
| `tools/kanban_*.sh` (5 files) | round-tooling helpers for the old repository's kanban workflow; not product, and subject to the same invariant. |
| `tests/test_s4ext_first_run_portable.py` | it executes `examples/first-run/run.sh`, which cannot ship here for the reason above. |

Consequences, stated rather than hidden: the absorbed README's first-run quickstart still points at
`examples/first-run/run.sh`, which is not in this tree — the equivalent steps are reproduced in
[`docs/pipd-migration/BASELINE.md`](../../docs/pipd-migration/BASELINE.md) §8. The remaining 51 test modules are
run as recorded there; the 12 repository-state modules stay excluded for the reasons in that file.

Run-time scaffolding is excluded as well: `.hgk/**` (governance receipts and test scratch) and `dist/**`
(build output) are now ignored by `integrations/pipd/.gitignore`. Three `tqaep_design_tmp/*.json` files had
been committed by a test run before that ignore existed; they were removed from the tree, so the claim that
`.hgk/**` is not carried is true of the tracked content.

Nothing else was edited: `src/`, `schemas/`, `skills/`, `tools/`, `packaging/`, `setup.py` and the licence files
are byte-for-byte the upstream snapshot.
