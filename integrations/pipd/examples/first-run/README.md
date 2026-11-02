# first-run — the fixture the README's compiler walk-through uses

This directory is the checked-in input for the runnable compiler chain on the front page. The
[`README.md`](../../README.md) commands point at these exact paths, so a reader who copies the block
runs *this* fixture — there are no placeholders to fill in. The walk-through passes the goal and
source on the `intake` command line directly; `intent.json` is the same input kept in the tree as a
single frozen record of what that command-line input is, not a separate file the CLI reads.

## Files

| Path | Role |
|---|---|
| `source.txt` | the normative clause source the requirement atoms are compiled from |
| `intent.json` | the frozen intent card (goal + one source locator + constraint + non-goal) |
| `assemble_bundle.py` | the one helper the CLI has no verb for (see the known limitation below) |

Everything here is self-contained public text: no PII, no secrets, no upstream document bodies.

## What a real run produces

The chain `intake -> compile-pi -> bind-pd -> compile-ecp -> compile-tqaep -> validate` was executed
twice in two fresh scratch workspaces outside the repository, binding PD against the *same* read-only
`RepoContext` directory. All seven steps exited `0`, `validate` returned `{"verdict":"PASS",
"checked":4,"findings":[]}`, and every artefact was **byte-identical across the two runs**:

| artefact | sha256 (both runs) | subject_id |
|---|---|---|
| `intent.card.json` | `f5a44e273c26ef4b76803e49635f23480e985b98a1cff41b6e8e31d4d79e2641` | `INTENT-9f8e9a1b6dc344fc` |
| `pi.json` | `9cc0c1b101431cfcb30e6435284ef24707a61ad6c91cd7f35adfda836b8c1c99` | `PI-50952b3a3822b28c` |
| `pd.json` | `351363de85ddd26b92b2491297429e139c2592c2e20ad4b0f81bd14482669843` | `PD-336c387a7aa71c9d` |
| `ecp.json` | `2e81277b0783b84c4a112ed74910724ccfbf6625b70de2664087a9704412372c` | `ECP-73cf63e34806711a` |
| `tqaep.json` | `1481fbda4ffdf26aafe88ea9cf681c62dd33761bed623902c3a22945f64fa434` | `TQAEP-2bf7b7e31b820fb7` |

Refusal is typed and non-zero: `intake --source examples/first-run/missing.txt` exits `2` with
`{"verdict": "FAIL", "code": "AUTHORITY_UNKNOWN", "message": "source locator does not exist: ..."}`
and writes no artefact.

## Known limitation

The 13-command CLI has no verb that *assembles* the compilers' stdout into the single object
`validate --bundle` reads, and this work order forbids adding one. `assemble_bundle.py` therefore
does exactly that one thing — `{pi, pd, ecp, tqaep} -> {"PI-PKG", "PD-PKG", "ECP", "TQAEP"}` — with
no additions, removals or edits. It is a documented stand-in for a missing verb, stated rather than
hidden.

`tests/test_first_run_examples.py` drives this fixture end to end (positive, reproduced, refusal).
