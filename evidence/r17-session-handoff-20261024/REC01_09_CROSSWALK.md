# REC01–REC09 crosswalk — phenomenon → root cause → repair → receipt → still open

Every line points at a real artefact under `var/R17-20261023/`. Nothing here upgrades a probe to a pass.

| round | phenomenon | root cause (measured) | repair / artefact | still open |
|---|---|---|---|---|
| REC01–03 | "not built at all" framing | 10105 EXECUTE shim was in fact working (nonce + usage rows); early-exit `advance.py`; 145/146 denominator confusion | `receipts/`, `ADVANCE_*`, 145-vs-146 split documented | historical only |
| REC04–05 | cron/runner typed errors, lease fencing, idle sweep | runner had no lease fence; `exit 0` treated as product DONE | 8 subtasks, PIPD/SoD candidates, typed errors | superseded by REC09 runner |
| REC06–07 | Codex Windows sandbox re-provisioning; `danger-full-access` breach; batch exit mis-read as green; served-arm attribution | dual `CODEX_HOME` fighting one provisioned install; `--identity-source codex-rollout` double-prefixed the model | HGK `086a940` (refuse unqualified arm), Fabric `bb06b7a6` (resolve policy relative to module) | local SHAs only; **not** Native-accepted |
| REC08 | three new Kinds 17/17; isolated checker workarea; `row_resume.py`; SBL Draft PR #9 | checker workarea needed three anchors (PIPD_ROOT depth, sibling TEST_RESULTS, scratch outside tree) | `candidates/sbl-kinds-rec08/`, `F2_CHECKER_FULL_SUITE.json` (717 passed / 0 PermissionError), PR #9 | `row_resume.py` had `queue[:max]`, `shell=True`, PROBE_PARTIAL→ADVANCED → replaced by `mission_runner.py` |
| REC09 | repeated `REPORT_AND_STOP`; `probe_c_family.py` interrupted; receipts of unknown effect | no fairness cursor; `NOT_RUN` rows invisible; prose placed in the action field; evidence judged by filename | `mission_runner.py` (28/28 controls), orphan reconcile, `P1_UNBOUND_CLASSIFICATION.json`, C-evidence fix (field assertions) | see OPEN_TT_FAR_OWNER_DECISIONS.md |
| REC10 (this session) | owner ordered role→model binding + KANBAN/SWARM/OPENSPEC, then a session handoff | 10100 frontdoor had no `aiohttp`; relay 10101 holds a dead upstream key; `--prompt` is literal text, not a path | `tools/probe_lanes_r17.py` (PLAN/VERIFY admitted), `tools/ocg_shim_10105.py`, `KANBAN_SWARM_R17.json` | EXECUTE nonce unsettled; handoff published candidate-only |

## Reconciliation facts that must not be re-derived

- The 145 denominator is **145 unique IDs**; `FABRIC-CANARY` is the only non-denominator row.
- `PROBE_*` coverage is never obligation closure (`coverage_only=true`, `obligation_closed=false`).
- The REC09 orphan probe run was reconciled read-only: no torn write, 25/25 rows, `RECEIPT_MATCHES_CURRENT_SCRIPT`.
- `C18` remains typed `UNBOUND`: no TQAEP cell manifest exists on disk, and inventing one is forbidden.
