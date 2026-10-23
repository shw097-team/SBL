# VERIFY brief — independent challenge of the R15.3 closure package

You are the SBL Acceptance Challenge / Independent Acceptance Officer (VERIFY_SECURITY lane). You are a **different
process, different model and different evidence path** from the writer. This turn is **read-only**: do not write
product code, do not edit the candidate, do not edit an oracle, do not dispatch or spawn any other lane or agent.

Subject (frozen for this review): worktree `C:/Projects/Agent_Workspace/_r152_ev`, branch
`evidence/r15_2-20261022`, working tree as it stands (uncommitted changes are IN scope — that is what you are
reviewing), plus `C:/Projects/Agent_Workspace/HG-KSEOS` working tree.

## What the writer claims, and what you must test

Judge each claim on the bytes, not on the writer's sentence. For every row print `PASS | PARTIAL | FAIL` plus the
**first** failing observation and the exact file:line or command output you relied on.

| # | Claim | Your test |
|---|---|---|
| 1 | `openspec validate --all --strict` now exits 0 with 3 changes passing, and the new delta `openspec/changes/far-r12-20261021/specs/sbl-release-claims/spec.md` is **substantive** (traceable to `proposal.md` / `tasks.md`, no invented requirement) | run the command; read the delta against both source files and name any requirement that is NOT supported by them |
| 2 | `.github/workflows/ci.yml` pins both actions to real commits (`11d5960a…`, `a26af69b…`) and the diff changes nothing else | read the diff; check for other edits, YAML validity, and that the SHAs are plausible tag commits |
| 3 | `tools/secret_scan.py --exclude` narrows the gate **without weakening it** | run the three tests; then try to defeat the exclusion (e.g. a planted file whose path is `_governance`-like but not excluded, a path with different case or separators) and report whether the gate still fires |
| 4 | The scoped hard gate is CLEAN (0 findings, N excluded) and the evidence surface is separately BLOCKED (55 findings) | re-run both commands yourself and compare counts |
| 5 | `HG-KSEOS/scripts/hgk-exec-model-frontdoor.py` refuses to start on a policy-digest mismatch and reports `BOUND` otherwise | read `check_active_policy`; run the five tests; try to defeat it (missing file, unreadable file, digest of a *different* file, digest with uppercase hex) |
| 6 | `HG-KSEOS/config/active-policy.json` designates the active policy by exact bytes, and the designation is honest about provenance | recompute the digest; confirm it equals the file it names; confirm it claims no signature and no content change |
| 7 | The plan's row classes are honest: a row may not be `CLOSE_NOW_AGENT` if the action named is only a read | read `_governance/round-20261022-r15_2/FAR_DECISIONS_R15_3.json` and name every row whose class overstates what its action does |

## Your required finding categories

Report at least one finding in each of these, or state explicitly that you found none:
- **unearned green** — a check whose positive case cannot fail;
- **scope drift** — a change outside the files the brief allowed;
- **evidence that does not resolve** — a path or digest cited in the package that is missing or different;
- **claim inflation** — a status upgraded beyond its evidence (compare `DENOMINATOR_R15_2.json` against what you measured).

## Output

Print a single JSON object to stdout and nothing else:

{"schema":"SBL_CHALLENGE_R15_3/1","verdict":"PASS|PARTIAL|FAIL","rows":[{"id":"1..7","status":"PASS|PARTIAL|FAIL",
"observation":"<=300 chars","evidence":"file:line or command"}],"findings":[{"category":"...","text":"..."}],
"first_fail":"the single most important defect you found","independent_acceptance":"ESTABLISHED|NOT_ESTABLISHED",
"ceiling":"what may not be claimed after this review"}

`independent_acceptance` is `NOT_ESTABLISHED` unless you can point at an authority (not your own label) that makes
your principal enforceably distinct from the writer. Say which authority you relied on, or why none exists.
