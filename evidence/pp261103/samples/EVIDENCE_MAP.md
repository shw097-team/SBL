# EVIDENCE_MAP — ten P0 views → real artifacts

Run under test: `RUN-20261102-GJ02-01`
Root `R` = `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01`
Author gate `G` = `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/sbl-tpm-sp/scripts/pre_v2_gate_r2.py`
PIPD python `PY` = `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/.venv-pipd/Scripts/python.exe` (CPython 3.11.9)
`PYTHONPATH` = `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt/src`
Validate scratch root `V` = `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/samples/_validate_root`
Fresh outputs written by this pass: `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/samples/logs/{A,B,C,D}_*.out`, `.../samples/_validate_root/{evidence_xcheck.py,xcheck.out}`

Rule applied: every row below points at a file that exists **and** was read or re-executed in this pass. A claim with no artifact says `NO_EVIDENCE` and names the minimum artifact that would close it. Nothing was re-run in full; only the four requested checks plus one read-only cross-check script.

## Summary table

| # | P0 view | Status | Anchor artifact | Key value |
|---|---|---|---|---|
| 1 | P0_SOURCE_BASELINE | **PASS-evidenced** | `bundle_r2/manifest.json` + `bundle_r2/source/test_billing.py` | sha256 `33170cc1…2148d`, 4/4 manifest digests match bytes |
| 2 | P0_LIFECYCLE | **PASS-evidenced** (isolated host only) | `raw/plugin_list_{installed,removed,final}.txt` | installed,enabled → not installed → installed,enabled (0.3.0-rc.2) |
| 3 | P0_PI_ID | **PASS-evidenced** | `bundle_r2/PI.json` + `01_products/pipd/pi.json` | 2/2 REQ + 2/2 ORACLE ids present in original writer PI |
| 4 | P0_PD_REALITY | **PASS-evidenced** (moving worktree) | `bundle_r2/PD.json` + live `shadow/gj02-repo` | HEAD `70757870ef495b0c…` matches; tree dirty |
| 5 | P0_ECP_TYPED | **PARTIAL — design ceiling only** | `bundle_r2/ECP.json` + `bundle_r2/registry/operation_registry.json` + `c1/REGISTRY_RECON.md` | `EFFECT_REGISTRY_UNBOUND` |
| 6 | P0_TQAEP_FUO | **PARTIAL — planned only** | `bundle_r2/PlannedTQAEP.json` + `01_products/pipd/tqaep_noReceipt.out` | 2 cases / 1 FUO; `TQ_SOD`; RUNNER_UNBOUND |
| 7 | P0_COMPATIBILITY | **PASS-evidenced (one direction)** | `c2/validate_pos.out`, `c2/validate_neg.out` (reproduced) | POS PASS checked 4 complete true; NEG FAIL exit 1 |
| 8 | P0_AUTHOR_TESTS | **PASS-evidenced (5 tests)** | `tests/test_pre_v2_adapters.py`, `tests/test_pre_v2_planned_reader.py`, `logs/D_five_negatives.out` | 5 passed in 2.81s |
| 9 | P0_HOST_INVOKE | **NO_EVIDENCE** | — | gate: `host_invoked=NOT_RUN`, world_effect `NOT_RUN` |
| 10 | P0_ROLLBACK | **NO_EVIDENCE (executed)** — declared only | `bundle_r2/ECP.json`, `c2/ecp.json`, `tests/test_negative_and_rollback.py` | pointer `baseline_commit` (symbolic, not a SHA) |

Totals: **6 PASS-evidenced, 2 PARTIAL, 2 NO_EVIDENCE.**

---

## 1. P0_SOURCE_BASELINE — PASS-evidenced

**Claim.** The author bundle is built on real source bytes: `tests/test_billing.py` at sha256 `33170cc166df18814f6749034f552591b1bb498936d834a56d3d19619942148d`, pinned in the manifest and in every derived object.

**Artifacts.**
- `R/bundle_r2/manifest.json` → `source_sha256`, `source_file: source/test_billing.py`, plus per-artifact sha256 for ECP/PD/PI/PlannedTQAEP
- `R/bundle_r2/source/test_billing.py` (2 tests, the real file)
- `R/shadow/gj02-repo/tests/test_billing.py` (the repo copy the bundle was cut from)
- `samples/_validate_root/xcheck.out` §1, §3 (this pass)

**Reproduction.** `sha256sum R/bundle_r2/source/test_billing.py R/shadow/gj02-repo/tests/test_billing.py`; then `PY samples/_validate_root/evidence_xcheck.py`.

**Result.** All 4 manifest artifact digests equal the bytes on disk (`ECP/PD/PI/PlannedTQAEP match=True`); bundle source sha == shadow repo file sha, `equal: True`; `PI.source_sha256`, `PlannedTQAEP.source_sha256` and registry `source_sha256` all equal the manifest value.

**Caveat.** The gate self-declares `source_authority = ORIGINAL_OWNER_UNVERIFIED`. This proves byte identity inside this host only — not upstream provenance. Also note `R/shadow/gj02-repo-m3/tests/test_billing.py` is `acfd555b…ff44` (different file: post-fix copy with two added tests); do not treat the two as the same source.

## 2. P0_LIFECYCLE — PASS-evidenced (isolated host only)

**Claim.** The shipped plugin `sbl-tpm-sp@0.3.0-rc.2` installs, uninstalls and reinstalls cleanly, ending installed+enabled.

**Artifacts.** `R/raw/plugin_list_installed.txt`, `R/raw/plugin_list_removed.txt`, `R/raw/plugin_list_final.txt`.

**Reproduction.** `codex plugin list` inside the isolated `CODEX_HOME` at `R/shadow/codex-case` (marketplace `sbl-pre-primary-local`), three times around the remove step.

**Result.** installed: `sbl-tpm-sp@sbl-pre-primary-local  installed, enabled  0.3.0-rc.2` → removed: `not installed` → final: `installed, enabled  0.3.0-rc.2`. Listing header in all three names the run-local marketplace path.

**Caveat.** This is the isolated shadow `CODEX_HOME`, **not** `~/.codex` (06_addendum: "`~/.codex` … never modified"). The removed listing carries an empty VERSION column, so version identity across the uninstall is not evidenced. No exit codes were archived beside the three listings.

## 3. P0_PI_ID — PASS-evidenced

**Claim.** PI requirement and oracle identities are the original PIPD writer's, not re-minted by the host, and polarity is preserved.

**Artifacts.** `R/bundle_r2/PI.json` (2 requirements, `original_requirement_id` / `original_oracle_id`), `R/01_products/pipd/pi.json` (original writer output), `R/bundle_r2/registry/operation_registry.json`, `samples/_validate_root/xcheck.out` §4.

**Reproduction.** `PY samples/_validate_root/evidence_xcheck.py` (§4 membership test), plus `PY G R/bundle_r2`.

**Result.** `REQ-1fc8f6183df66bd53642` and `REQ-bf8f22cb1ff8c7f5ade0` both `present_in_original_writer_PI=True`, with their ORACLE ids also present; all four P0 objects carry one `subject_id` (`SUBJ-GJ02-BILLING-ROUNDING`); gate verdict `AUTHOR_CONTRACT_CONSISTENT`, `requirements: 2`.

**Caveat.** Identity preservation covers REQ/ORACLE only. `fuo_id FUO-ROUND-ONCE`, the case ids and the operation-type registry are author-derived and labelled as such. The host's own label `GJ02-BILLING-ROUND-ONCE` / `SUBJ-GJ02-BILLING-ROUNDING` is **not** the writer subject `PI-974a4204962f5dc8` (see `c2/C2_RESULTS.json` → `host_label_crosswalk`), so no cross-artifact subject equality may be asserted.

## 4. P0_PD_REALITY — PASS-evidenced (moving worktree)

**Claim.** PD binds to a real repository probe: HEAD `70757870ef495b0c3c7193fbf35df1223f8a6566`, branch master, 2 tracked files, dirty, write scope `src/demo/billing.py`, with a probe receipt.

**Artifacts.** `R/bundle_r2/PD.json` (`binding_state: PROBE_OBSERVED`, `repo.probe_receipt: sha256:6944e5f9…`), live repo at `R/shadow/gj02-repo`, `R/c2/pd.json` (writer-side pin with per-claim verification), `samples/_validate_root/xcheck.out` §2.

**Reproduction.** `git -C R/shadow/gj02-repo rev-parse HEAD` and `git -C R/shadow/gj02-repo status --porcelain`.

**Result.** HEAD reads exactly `70757870ef495b0c3c7193fbf35df1223f8a6566` = the PD value. `status --porcelain` shows ` M src/demo/billing.py` plus untracked `README.md`, `host_notes.md`, `specs/`, `__pycache__/` → PD `dirty: true` is honest. `PD.pi_digest == sha256(PI.json)` and `ECP.pd_digest == sha256(PD.json)` both `True`.

**Caveat.** The binding is "base commit + uncommitted edits": HEAD is immutable, the worktree is not, so the PD describes a moving tree. `c2/pd.json` records `writable_scope … verified: false` while every other caller claim is `verified: true` — the `src/**` scope is caller-asserted, not probe-confirmed. The `probe_receipt` digest is referenced, not re-derived here (no probe log archived in this pass).

## 5. P0_ECP_TYPED — PARTIAL (design ceiling only)

**Claim.** The effect is typed: `effect_class: REPOSITORY_WRITE`, `exact_scope: [src/demo/billing.py]`, `on_unknown: RECONCILE_NO_BLIND_RETRY`, `recoverability: REVERSIBLE`, tied to operation `OP-GJ02-ROUND-FIX` via `effect_registry_ref: AUTHOR-OPREG-billing-round-v1#OP-GJ02-ROUND-FIX`.

**Artifacts.** `R/bundle_r2/ECP.json`; `R/bundle_r2/registry/operation_registry.json` (single `operation_types: ["REPOSITORY_WRITE"]`, AUTHOR-DERIVED, labelled in NOTE); `R/c1/REGISTRY_RECON.md`; `R/05_M1_M4_results.json` → `M1_operation_registry_ecp.decision = EFFECT_REGISTRY_UNBOUND`; `R/06_closeout_addendum.md` M1.

**Reproduction.** `PY G R/bundle_r2` → `effect_state: DESIGN_ONLY_NOT_ADMITTED`; read `M1` decision from `05_M1_M4_results.json`.

**Result.** The typed ECP parses, gate-accepts and is internally consistent, but the gate returns `effect_state = DESIGN_ONLY_NOT_ADMITTED` and the run's own decision is `EFFECT_REGISTRY_UNBOUND` (0 `OperationRegistry` hits in SBL/PIPD/Fabric/HG-KSOS; 0 of 19 canonical PIPD schema families carry an enum; `ECP.schema.json` `effect_class` is an enum-less string with `CANDIDATE_VOCABULARY_PENDING_OWNER`).

**Caveat / gap.** "Typed" here means typed **against an author-invented registry**. No original effect classifier exists, so this ECP can never be admitted as effect-specific; the value set is unapproved. Minimum artifact to close: an owner-approved `PIPD/schemas/operation-registry.json` + `OperationRegistry.schema.json` declaring `SBL.OperationRegistry.Binding@2` with per-`operation_type` `effect_class`, owner, version/policy epoch and `authority_state`, registered as a family in `PIPD/schemas/registry.json`, plus one gate run against it returning an effect state other than `DESIGN_ONLY_NOT_ADMITTED`.

## 6. P0_TQAEP_FUO — PARTIAL (planned only)

**Claim.** A PlannedTQAEP@2 links 2 cases to FUO `FUO-ROUND-ONCE` with resolvable positive/negative fixtures, and the reader refuses self-attested independence.

**Artifacts.** `R/bundle_r2/PlannedTQAEP.json` (`cases: 2`, `required_fuo: [FUO-ROUND-ONCE]`, `runner_binding: RUNNER_UNBOUND` on both cases, `claim_ceiling: DESIGN_ONLY`); `R/bundle_r2/fixtures/{pos,neg}_case{1,2}.txt`; `R/01_products/pipd/tqaep_noReceipt.out`; `R/c2/bundle.json` → `TQAEP.acceptance`; `R/05_M1_M4_results.json` M2; `c2/C2_RESULTS.json` → `CANONICAL_TQAEP_HANDOFF_HOLD`.

**Reproduction.** `PY G R/bundle_r2` (→ `cases: 2`), `PY samples/_validate_root/evidence_xcheck.py` §5 (fixture resolution), `cat R/01_products/pipd/tqaep_noReceipt.out`.

**Result.** Gate: `cases: 2`, `requirements: 2`. All four fixture pointers exist (27/27/33/33 bytes). Reader with a missing checker receipt: `{"code": "TQ_SOD", "verdict": "FAIL"}` — "an independent checker must supply a checker_execution_receipt; a maker cannot self-attest independence". Writer-chain TQAEP records `claim_ceiling: TQAEP_DESIGNED`, `independent_acceptance: NOT_GRANTED`, `checker_execution_receipt: "design/fixture-no-live-receipt"` (a placeholder string, explicitly noted as not verification).

**Caveat / gap.** No FUO usability claim is supportable: `runner_binding = RUNNER_UNBOUND` on both cases and no live checker receipt exists. Minimum artifact to close: a real checker execution receipt bound to the same subject/candidate/host/scope/epoch, plus one archived run of both cases (positive passes, negative fails) under that checker.

## 7. P0_COMPATIBILITY — PASS-evidenced (one direction)

**Claim.** The same source bytes yield a four-object bundle that the **original** PIPD reader accepts, and the same reader refuses a wrong-schema ECP.

**Artifacts.** `R/c2/bundle.json` (families `PI-PKG`, `PD-PKG`, `ECP`, `TQAEP`), `R/c2/validate_pos.out`, `R/c2/bundle_bad_ecp.json`, `R/c2/validate_neg.out`, `R/c2/C2_RESULTS.json`, `R/gstack2/VERIFY_C0.md` C3 (`pipd-compat (ubuntu, py3.11)` 14/14 steps success on `a25fb569`), fresh reruns `samples/logs/B_validate_pos.out`, `samples/logs/C_validate_neg.out`.

**Reproduction.** `PYTHONPATH=…/pipd-wt/src PY -m pipd_ls_sp.cli --root V validate --bundle R/c2/bundle.json --require-four` (and the `bundle_bad_ecp.json` variant).

**Result.** POS: `verdict PASS`, `checked 4`, `complete true`, `closure FULL`, `scope FOUR_OBJECT`, `missing []`, `findings []`, **exit 0**. NEG: `verdict FAIL`, `checked 4`, **exit 1**, first finding `SCHEMA · ECP · "ECP/: Additional properties are not allowed ('effect_class', 'schema' were unexpected)"` (15 findings total, all ECP). Both reruns reproduce the archived outputs exactly.

**Caveat.** Compatibility is proven for writer-produced canonical objects only. The same reader **rejects** host-authored `@2` objects (`05_M1_M4_results.json` M3 `canonical_ack: FAIL`, `PI-PKG/: Additional properties … 'stable_semantic_contract' is a required property`; `06_closeout_addendum.md` M3). Interop with any third-party writer is untested.

## 8. P0_AUTHOR_TESTS — PASS-evidenced (5 tests)

**Claim.** The five named negative cases are real, encoded as tests, and pass: cross-subject, blind retry, fake grant, wrong host, nested receipt.

**Artifacts.** `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt/tests/test_pre_v2_adapters.py` (`test_cross_subject_refused` L50, `test_blind_retry_refused` L53, `test_nested_fake_grant_refused_by_original_writer` L44), `…/tests/test_pre_v2_planned_reader.py` (`test_wrong_host` L52, `test_nested_receipt` L49), `…/tests/test_validate_four_objects.py` (4 denominator cases L44–L71), `samples/logs/D_five_negatives.out`.

**Reproduction.**
```
cd C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt
PYTHONPATH=src PY -m pytest -q \
  tests/test_pre_v2_adapters.py::OriginalEffectAdapters::test_cross_subject_refused \
  tests/test_pre_v2_adapters.py::OriginalEffectAdapters::test_blind_retry_refused \
  tests/test_pre_v2_adapters.py::OriginalEffectAdapters::test_nested_fake_grant_refused_by_original_writer \
  tests/test_pre_v2_planned_reader.py::PlannedReader::test_wrong_host \
  tests/test_pre_v2_planned_reader.py::PlannedReader::test_nested_receipt
```
**Result.** `.....  [100%]` → `5 passed in 2.81s`, exit 0.

**Caveat.** Five tests, not the suite. The round's headline figure "664 passed / 20 skipped" (`06_closeout_addendum.md` M2b, `05_M1_M4_results.json`) has **no archived pytest log in `R/`** — it is a claim this pass did not reproduce. `test_negative_and_rollback.py::test_rollback_pointer_is_a_real_git_commit` `skipTest`s when `.git` is absent, so a green suite does not imply a real rollback check.

## 9. P0_HOST_INVOKE — NO_EVIDENCE

**Claim under test.** A host invoked the effect under an authorization (the gate's `host_invoked` axis).

**Artifacts inspected.** `R/bundle_r2/manifest.json`, `R/03_native_receipt_refs.json`, `R/05_M1_M4_results.json`, `R/raw/ds_events.jsonl` (+ `raw/ds_exit.txt`).

**What exists.** Gate: `"host_invoked": "NOT_RUN", "native_e2e": "NOT_RUN", "checker": "NOT_RUN", "release": "FAIL_CLOSED"`. `03_native_receipt_refs.json`: `world_effect.state = NOT_RUN`, `work_id/operation_id/policy_epoch/preimage/postimage = null`, with the note that the sandbox change "was made by the Codex agent inside an isolated test repo … it is a test fixture, not a governed DEV effect"; `decision = NATIVE_GOLDEN_HOLD`. `raw/ds_events.jsonl` (`EXITCODE=0`) evidences a host *session* driving the tooling (M3: docs + four `@2` objects produced), not a governed effect invocation. The negative test `PlannedReader::test_wrong_host` proves refusal of a foreign host, the opposite direction.

**Verdict.** NO_EVIDENCE.  
**Minimum artifact to close.** One gate run whose output carries `host_invoked != NOT_RUN` (and `native_e2e`, `checker` no longer `NOT_RUN`), plus a host execution receipt file in `R/03_native_receipt_refs.json` keyed by `{work_id, operation_id, policy_epoch, host_id, os_principal, receiver_abi, preimage, postimage, readback}` and cross-referenced by hash from the gate output.

## 10. P0_ROLLBACK — NO_EVIDENCE (executed); declared only

**Claim under test.** The effect is reversible and a rollback pointer resolves to a real commit that was actually exercised.

**Artifacts inspected.** `R/bundle_r2/ECP.json` (`recoverability: REVERSIBLE`, `readback: git_diff_and_test_exit`), `R/c2/ecp.json` (`rollback: {required: true, pointer: "baseline_commit"}`), `…/tests/test_negative_and_rollback.py::TestRollback::test_rollback_pointer_is_a_real_git_commit` (L62–L76), `R/06_closeout_addendum.md` (promotion section), `R/raw/ds_events.jsonl`.

**What exists.** Declared reversibility and a rollback *requirement*. The canonical ECP's pointer is the symbolic token `"baseline_commit"`, **not** a commit SHA. The test only asserts that `git log --reverse` is non-empty in ROOT and that `git status` exits 0 — it never reverts anything, and it `skipTest`s without `.git`. `grep` of `raw/ds_events.jsonl` for `git reset|git revert|git checkout` returns **0** hits (only 6 occurrences of the word `rollback`, all prose). The closing note is explicit: "No host setting was switched … so the 'switch and roll back' step is a no-op rather than a claim."

**Verdict.** NO_EVIDENCE for an executed rollback; the reversibility claim is a design attribute only.  
**Minimum artifact to close.** An archived run in `R/` recording: baseline commit (full SHA, expected `70757870ef495b0c3c7193fbf35df1223f8a6566`), the revert/reset command, its exit code, the post-rollback `git rev-parse HEAD` + `git status --porcelain`, and the test suite exit after rollback; plus replacing the symbolic `"baseline_commit"` pointer with the concrete SHA in the ECP.

---

## Gaps (named, not narrated)

1. **P0_HOST_INVOKE — NO_EVIDENCE.** Needs a gate run with `host_invoked`/`native_e2e`/`checker` ≠ `NOT_RUN` plus a host execution receipt (`work_id, operation_id, policy_epoch, host_id, os_principal, receiver_abi, preimage, postimage, readback`) wired into `R/03_native_receipt_refs.json`.
2. **P0_ROLLBACK — NO_EVIDENCE (executed).** Needs an archived revert/reset against baseline `70757870…` with exit code, post-rollback HEAD/status readback and post-rollback suite exit; the ECP pointer must be a SHA, not `"baseline_commit"`.
3. **P0_ECP_TYPED — design ceiling.** Needs the owner-approved `PIPD/schemas/operation-registry.json` + `OperationRegistry.schema.json` (typed `effect_class` per `operation_type`, owner, policy epoch, `authority_state`) registered in `PIPD/schemas/registry.json`; without it `EFFECT_REGISTRY_UNBOUND` stands and no effect-specific ECP is admissible.
4. **P0_TQAEP_FUO — planned only.** Needs a live protected-checker execution receipt (same subject/candidate/host/scope/epoch) plus archived pass/fail of both cases under that checker; `runner_binding=RUNNER_UNBOUND` currently voids any FUO usability claim.
5. **P0_AUTHOR_TESTS — headline count unreproduced.** The "664 passed / 20 skipped" figure has no archived log under `R/`; only the 5 requested negatives were re-run (`5 passed`).
6. **P0_LIFECYCLE — isolated host only.** No evidence outside the shadow `CODEX_HOME`; the removed listing has an empty version column and no exit codes were archived.
7. **P0_PD_REALITY — moving worktree.** `dirty: true`; `c2/pd.json` marks `writable_scope` `verified: false`; `probe_receipt` digest is referenced but not re-derived.
8. **P0_COMPATIBILITY — one direction.** The same reader rejects host-authored `@2` objects (M3 `canonical_ack: FAIL`); no third-party writer tested.
9. **P0_SOURCE_BASELINE — provenance.** `source_authority = ORIGINAL_OWNER_UNVERIFIED`; byte identity only, no upstream ownership evidence.
10. **P0_PI_ID — id scope.** FUO id and case ids are author-derived; the host subject label is explicitly not the writer subject (`PI-974a4204962f5dc8`).
