# EXTERNAL CHALLENGE REPORT R1 — intake, verification of identity, classification

```yaml
report_id: EXT-CHALLENGE-SBL-R2-01
subject_candidate: ab17440ab68f8c7a1bd9702aba3624149d3f0506
subject_branch: candidate/r2-20261020
checker_lane: VERIFY_SECURITY
checker_arm_required: openai-codex/gpt-6.1-sol
checker_arm_served: openai-codex/gpt-6.1-sol
checker_rank: 2
nonce: SBLR2-VERIFY-02
used_seconds: 494.79
verdict: FAIL
counts: { HIGH: 4, MEDIUM: 3, INFO: 1 }
raw_receipt: (scratch) sbl-verify-runs/VERIFY_candidate_ab17440.json
parsed_verdict: (scratch) sbl-verify-runs/VERDICT_parsed.json
```

## Identity and admissibility check (done before accepting the findings)

| Check | Observed | Admissible |
|---|---|---|
| required arm == served arm | `openai-codex/gpt-6.1-sol` both | yes |
| nonce present in first and last agent message | `SBLR2-VERIFY-02` both | yes |
| checker ran on the frozen candidate | copy of `ab17440` in an outside-scratch cwd; all 117 candidate files re-hashed unchanged | yes |
| maker/checker principal separation | checker never held a writer turn; findings were produced without editing candidate source | yes |
| guard subject | `C:/Projects/Agent_Workspace/SBL`; `subject_mutation.verdict = CLEAN`, `removed=[]`, `changed=[]`, 2 additions recorded — the checkpoint/readback files the ORCHESTRATOR wrote while the lane ran | **partial** (see D1) |
| sandbox | `workspace-write` with `--allow-sandbox-escalation`, not read-only | **deviation** (see D2) |
| execution boundary | checker reports its shell started at `C:\` before cwd applied; initial suite runs used the OS temp dir; a 3.11 run fell back to OS temp | **deviation** (see D3) |

### Disclosed defects of THIS round's harness (not of the candidate)
- **D1** The orchestrator wrote `20_RESUME_CHECKPOINT.json` and `30_PUBLICATION_READBACK.json` inside the guarded
  subject while the checker ran. The guard recorded them as additions (not mutations), so the verdict stands, but
  the freeze was not airtight: **next round, all orchestrator writes stop before the checker is dispatched.**
- **D2** The checker needed `workspace-write` to run pytest in its own copy. Read-only was not achieved; the
  isolation came from cwd discipline, not from the sandbox.
- **D3** The checker's copy had no `.git`, so it could not authenticate commit `ab17440` and one
  real-repository-context test failed for lack of Git metadata. **Next round the copy carries `.git`.**

## Classification (contract §7) and disposition

| id | severity | class | disposition |
|---|---|---|---|
| SEC-01 | HIGH | CONFIRMED_DEFECT | principal identity was a caller-supplied string; repair = HMAC credential per SP key (repair spec SEC-01) |
| SEC-02 | HIGH | CONFIRMED_DEFECT | claim ceiling was caller-supplied; repair = instance-owned immutable ceiling |
| SEC-03 | HIGH | CONFIRMED_DEFECT | PASS not bound to evidence; proxy/case-variant bypass; repair = evidence lookup + status normalisation |
| SEC-04 | HIGH | CONFIRMED_DEFECT | allow-substring suppressed the whole line in the scanner; repair = allowlist applies to the matched span |
| VERIFY-01 | MEDIUM | CONFIRMED_DEFECT | `verify_source.py` accepted an empty inventory; repair = require the 14 declared documents |
| VERIFY-02 | MEDIUM | EVIDENCE_GAP (harness) | gate denominator undercounted mixed outcomes; repair = parse all summary counts |
| VERIFY-03 | MEDIUM | CONFIRMED_DEFECT | tests used `shutil.rmtree(onexc=...)` (3.12+) against a declared 3.11 floor |
| CONTRACT-01 | INFO | NON_BLOCKING_OBSERVATION | contract edges and receipt byte bindings verified; no action |

No finding was classified `ORACLE_DISAGREEMENT` or `OUT_OF_SCOPE`; all seven were accepted as legitimate.
Repair work order: `14_REPAIR_R1.md`. The checker did **not** participate in the repair.

## What the checker independently confirmed (so it is not re-litigated)

- Every one of 17 ACTIVE_REQUIRED capabilities has a CAPABILITY acceptance edge; contract ↔ active-requirement
  ids agree; all 13 evidence gates declare `LOCAL`, matching the declared ceiling.
- Recomputed `contract_sha256` and `thin_prompt_sha256` match `compiler-receipt.json` byte for byte.
- `README.md`/`docs/` do **not** overclaim: no claim above LOCAL / CANDIDATE_ONLY, no release or production claim.
- `tools/verify_source.py --verify` reproduces the 14-document digest on the real receipt.
- `secret_scan` scans 260 files, verdict CLEAN, on the published tree.
- 35 `pytest.raises` sites all carry exact `SBL_E_*` assertions rather than exception-only checks.
