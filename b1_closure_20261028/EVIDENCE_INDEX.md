# EVIDENCE INDEX — SBL

Every row is: question → file → how to reproduce.

| question | file | reproduce |
|---|---|---|
| Do all gates pass? | `evidence/GATES.json` | read `gates_conjunction`, `G-A`, `GWO`, `G-B` |
| Is `mission_complete` honest? | `evidence/GATES.json` | `mission_complete` + `why_not_complete` + `declared_ceilings[].blocks_mission_completion` |
| Did the native path run, or was it sandboxed? | `evidence/NATIVE_ADMISSION_RECEIPT.json`, `evidence/CORPUS_NATIVE_RECEIPT.json` | compare `entity_id`/`event_id` with `$b1_closure_20261028/evidence/SESSION_STATE.json#gate_c_corpus_native` |
| Who signed the claim ceiling? | `evidence/OWNER_DECLARATION.json` | `declaration_lib.verify(dec, registry.owner_enrollment.public_hex)` |
| Who ruled the two declarations? | `evidence/OWNER_RULING.json` | same verifier; `rulings[].bound_value` must equal the measured value |
| What changed in the registry? | `evidence/claim_ceiling_edit.json`, `evidence/signed_runner_registry.json` | diff `before`/`after`; verify the registry merkle root |
| Why is 12/30 not a gap? | `far/FAR_B1_v9_20261028.md` | the denominator is the registry row count; PKG_00~08 require `INSTALLED` only |
| Which branches could merge to main? | `analysis/candidate_screen.json` | `git merge-tree --write-tree origin/main <branch>` per row |
| What did this round cost? | `evidence/SESSION_STATE.json` | unlock / signature / elevation counters |

Reproduction commands (B1 workspace):

```
python gates.py
python wave1/wave1_owner_console.py --dry-run
PYTHONPATH=HG-KSEOS/src python -c "from hg_kseos.native_admission import ProtectedRegistry as P; print(P().snapshot())"
git -C <repo> merge-tree --write-tree origin/main <branch>
```
