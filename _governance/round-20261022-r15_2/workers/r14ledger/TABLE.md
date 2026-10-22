# R14 obligation evidence readback — branch `evidence/r14-20261022-native`

Commit `e6623ba1e9a4a477d07048cd3a5a906f33d6029d` · 31 items · **readback only, no verdict recomputed.** Presence of a blob is not a judgement of its content; no tests were run; nothing was written to the repo.

## Method
Evidence paths in `_governance/round-20261022-r14/OBLIGATIONS.json` are declared against mixed bases, so each was resolved in order:
1. `_governance/…`-prefixed → repo-root-relative
2. `HG-KSEOS …`-prefixed → cross-repo reference, unresolvable inside this branch
3. otherwise → round-relative (`_governance/round-20261022-r14/`), then repo-root-relative, then round-relative `raw/` for bare filenames

Existence: `git cat-file -e <branch>:<candidate>` (exit 0) · sha: `git rev-parse <branch>:<candidate>`. Every in-branch "missing" was re-checked against the whole branch tree (490 entries) so a base-resolution artifact could not be reported as absence.

## Per-item table

| # | id | state | declared | present | missing | classification |
|---|---|---|---|---|---|---|
| 1 | R14-TS00 | DONE | 1 | 1 | — | EVIDENCE_PRESENT |
| 2 | R14-TS01 | DONE | 2 | 2 | — | EVIDENCE_PRESENT |
| 3 | R14-TS02 | DONE | 1 | 1 | — | EVIDENCE_PRESENT |
| 4 | R14-TS03 | DONE | 3 | 3 | — | EVIDENCE_PRESENT |
| 5 | R14-TS04 | DONE | 1 | 1 | — | EVIDENCE_PRESENT |
| 6 | R14-TS05 | DONE | 1 | 1 | — | EVIDENCE_PRESENT |
| 7 | R14-TS06 | DONE | 2 | 2 | — | EVIDENCE_PRESENT |
| 8 | R14-TS07 | DONE | 2 | 2 | — | EVIDENCE_PRESENT |
| 9 | R14-TS08 | DONE | 3 | 3 | — | EVIDENCE_PRESENT |
| 10 | R14-TS09 | DONE | 4 | 3 | HG-KSEOS scripts/f0_trace.py | EVIDENCE_PARTIAL |
| 11 | R14-TS10 | PARTIAL | 3 | 0 | raw/ts10_lifecycle/receipts.json; raw/ts10_lifecycle/VERBS.md; raw/ts10_lifecycle/SUMMARY.json | EVIDENCE_MISSING |
| 12 | R14-TS11 | PARTIAL | 4 | 2 | raw/ts11_SUMMARY.md; raw/ts11_build_output/ | EVIDENCE_PARTIAL |
| 13 | R14-TS12 | BLOCKED_SOFT | 1 | 1 | — | EVIDENCE_PRESENT |
| 14 | R14-TS13 | PARTIAL | 4 | 2 | HG-KSEOS src/hg_kseos/semantic_oracle.py; HG-KSEOS tests/test_semantic_oracle.py | EVIDENCE_PARTIAL |
| 15 | R14-TS14 | DONE | 4 | 3 | HG-KSEOS scripts/pi_compile_h0.py | EVIDENCE_PARTIAL |
| 16 | R14-TS15 | DONE | 4 | 4 | — | EVIDENCE_PRESENT |
| 17 | R14-TS16 | DONE | 3 | 3 | — | EVIDENCE_PRESENT |
| 18 | R14-TS17 | PARTIAL | 3 | 3 | — | EVIDENCE_PRESENT |
| 19 | R14-TS18 | DONE | 4 | 1 | raw/ts18_gknow.md; HG-KSEOS src/hg_kseos/knowledge.py citation_integrity/detect_conflicts; HG-KSEOS src/hg_kseos/security.py INJECTION_PATTERNS (CJK set) | EVIDENCE_PARTIAL |
| 20 | R14-TS19 | PARTIAL | 3 | 2 | raw/ts1921_evidence_anchors.csv | EVIDENCE_PARTIAL |
| 21 | R14-TS20 | PARTIAL | 2 | 1 | raw/ts1921_evidence_anchors.csv | EVIDENCE_PARTIAL |
| 22 | R14-TS21 | DONE | 2 | 1 | raw/ts1921_evidence_anchors.csv | EVIDENCE_PARTIAL |
| 23 | R14-TS22 | DONE | 4 | 4 | — | EVIDENCE_PRESENT |
| 24 | R14-TS23 | PARTIAL | 4 | 4 | — | EVIDENCE_PRESENT |
| 25 | R14-TS24 | DONE | 2 | 1 | HG-KSEOS scripts/ts24_w3_route_out.py | EVIDENCE_PARTIAL |
| 26 | R14-TS25 | BLOCKED | 1 | 1 | — | EVIDENCE_PRESENT |
| 27 | R14-TS26 | BLOCKED | 1 | 1 | — | EVIDENCE_PRESENT |
| 28 | R14-TS27 | BLOCKED | 3 | 3 | — | EVIDENCE_PRESENT |
| 29 | R14-TS28 | PARTIAL | 4 | 4 | — | EVIDENCE_PRESENT |
| 30 | R14-TS29 | PARTIAL | 2 | 1 | HG-KSEOS scripts/ts29_debt_closure.py | EVIDENCE_PARTIAL |
| 31 | R14-TS30 | BLOCKED | 2 | 2 | — | EVIDENCE_PRESENT |

## Classification counts

- EVIDENCE_PRESENT: **20**
- EVIDENCE_PARTIAL: **10**
- EVIDENCE_MISSING: **1**

By declared state: DONE 17, PARTIAL 9, BLOCKED 4, BLOCKED_SOFT 1.

| state | PRESENT | PARTIAL | MISSING |
|---|---|---|---|
| DONE | 12 | 5 | 0 |
| PARTIAL | 3 | 5 | 1 |
| BLOCKED_SOFT | 1 | 0 | 0 |
| BLOCKED | 4 | 0 | 0 |

## Divergence summary

**12 of 17 DONE items have every declared evidence artefact present in the branch.** 5 DONE items are short:

- **R14-TS09** (DONE, 3/4) — cross-repo (not in branch by construction): `HG-KSEOS scripts/f0_trace.py`
- **R14-TS10** (PARTIAL, 0/3) — in-branch absent: `raw/ts10_lifecycle/receipts.json`, `raw/ts10_lifecycle/VERBS.md`, `raw/ts10_lifecycle/SUMMARY.json`
- **R14-TS11** (PARTIAL, 2/4) — in-branch absent: `raw/ts11_SUMMARY.md`, `raw/ts11_build_output/`
- **R14-TS13** (PARTIAL, 2/4) — cross-repo (not in branch by construction): `HG-KSEOS src/hg_kseos/semantic_oracle.py`, `HG-KSEOS tests/test_semantic_oracle.py`
- **R14-TS14** (DONE, 3/4) — cross-repo (not in branch by construction): `HG-KSEOS scripts/pi_compile_h0.py`
- **R14-TS18** (DONE, 1/4) — in-branch absent: `raw/ts18_gknow.md`; cross-repo (not in branch by construction): `HG-KSEOS src/hg_kseos/knowledge.py citation_integrity/detect_conflicts`, `HG-KSEOS src/hg_kseos/security.py INJECTION_PATTERNS (CJK set)`
- **R14-TS19** (PARTIAL, 2/3) — in-branch absent: `raw/ts1921_evidence_anchors.csv`
- **R14-TS20** (PARTIAL, 1/2) — in-branch absent: `raw/ts1921_evidence_anchors.csv`
- **R14-TS21** (DONE, 1/2) — in-branch absent: `raw/ts1921_evidence_anchors.csv`
- **R14-TS24** (DONE, 1/2) — cross-repo (not in branch by construction): `HG-KSEOS scripts/ts24_w3_route_out.py`
- **R14-TS29** (PARTIAL, 1/2) — cross-repo (not in branch by construction): `HG-KSEOS scripts/ts29_debt_closure.py`

### Findings worth the parent's attention

- **R14-TS21 is DONE but its core artefact is absent.** `raw/ts1921_evidence_anchors.csv` has **zero** occurrences anywhere in the branch tree, yet it is the primary evidence for TS21 and is also cited by TS19/TS20. TS21's only surviving evidence is `raw/ts1921_evidence_SUMMARY.json`.
- **R14-TS18 is DONE on 1 of 4.** `raw/ts18_gknow.md` does not exist anywhere in the branch; the two remaining refs are cross-repo symbols. Only `raw/final_r14_full14.log` is actually pinned.
- **R14-TS10 is the only EVIDENCE_MISSING item.** Its declared directory `raw/ts10_lifecycle/` *does* exist in-branch, but holds only `doctor.after.json`, `stack.json.after`, `stack.json.before` — none of the three declared files (`receipts.json`, `VERBS.md`, `SUMMARY.json`).
- **R14-TS11** declares `raw/ts11_build_output/` (a directory) and `raw/ts11_SUMMARY.md`; neither exists as tree or blob.
- **7 cross-repo refs** (`HG-KSEOS …`) touch TS09, TS13, TS14, TS18, TS24, TS29. These can never resolve inside this branch; they are counted missing under the branch-only rule but are *not* evidence of absent work — they are simply out of scope for this readback. They alone account for the EVIDENCE_PARTIAL status of TS09, TS14, TS24 and half of TS13's gap.
- Every BLOCKED item still has its declared evidence present (TS25/TS26/TS27/TS30) — blocked status is not an evidence-absence problem here.

*(readback only; no verdict recomputed)*
