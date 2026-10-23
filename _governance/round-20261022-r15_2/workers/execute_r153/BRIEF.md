# EXECUTE brief — R15.3 bounded product writes (C11 delta, C22 CI)

You are the SBL-EXECUTE lane and a bounded writer. Work in `C:/Projects/Agent_Workspace/_r152_ev` (branch
`evidence/r15_2-20261022`). Write **exactly the files listed below** and then stop. Do not dispatch, spawn or poll
another lane or agent. Do not touch any other file, do not `git add`, do not commit, do not run a formatter over the
tree. If a file already exists, edit only the listed part.

## File 1 — `openspec/changes/far-r12-20261021/specs/sbl-release-claims/spec.md` (new)

Why: `openspec validate --all --strict` fails on `change/far-r12-20261021` because the change has a proposal and
tasks but **no delta spec**. The change is real (merged), so the delta is a record of what the change did to the
capability, not a new design.

Read first: `openspec/changes/far-r12-20261021/proposal.md` and `tasks.md`, and copy the section format used by
`openspec/changes/sbl-r15-2-native-admission/specs/sbl-native-admission/spec.md`
(`# <capability> Specification`, `## ADDED Requirements`, `### Requirement: ...` with SHALL/MUST,
`#### Scenario: ...` with `- **WHEN**` / `- **THEN**`).

Write at least four requirements, each traceable to a statement that exists in the proposal or tasks file:
1. Public claim text matches the published artefacts (the two pre-release tags and the three console scripts).
2. A conformance count is only valid together with the tree state it was measured on.
3. The control package is pinned by identity, and its negative controls exist (three of them).
4. The native chain (WorkOrder -> ONE ECP -> Permit -> writer -> isolated checker) is NOT claimed by this change.
Each requirement needs one or two scenarios with WHEN/THEN. No invented facts: if the proposal does not say it,
do not write it, and list the omission in the receipt.

## File 2 — `.github/workflows/ci.yml` (edit, minimal)

Two things only, and nothing else in the file may change:

a) Pin the two actions to these exact commit SHAs, keeping the version as a trailing comment:
  - `actions/checkout@v4` -> `actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4`
  - `actions/setup-python@v5` -> `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5`

b) Append two steps after the existing `Verify published source manifest` step, indented to match it:

```yaml
      - name: Secret scan (hard gate)
        run: python tools/secret_scan.py --json-out evidence/security/SECRET_SCAN.json

      - name: Dependency inventory (SBOM input)
        run: python -m pip list --format=json > evidence/security/PIP_INVENTORY.json
```

Do not invent another SHA, do not upgrade the actions, do not add a job.

## File 3 — `workers/execute_r153/EXECUTE_RECEIPT.json` (new)

```json
{"schema":"SBL_EXECUTE_RECEIPT/1","lane":"EXECUTE","role":"bounded writer",
 "files":[{"path":"...","action":"created|edited","why":"...","bytes":0}],
 "not_done":["anything you deliberately did not do, with the reason"],
 "claim_ceiling":"candidate edits only; not validated, not accepted, not committed"}
```

Add one entry per file you touched, with the real byte size you can read back.

## Rules

- Exactly these three files. Nothing else, no renames, no deletions.
- If a SHA or a fact looks wrong, write `TT_EXECUTE_INPUT` in the receipt instead of guessing.
- End by printing one line per file with its byte size.
