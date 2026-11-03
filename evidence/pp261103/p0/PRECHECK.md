# P0 PRECHECK - adversarial reproduction of the ten-P0 evidence

Independent, read-only attack on the pre-v2 evidence before publication.
No repo, published bundle or installed plugin was modified; every tamper run used a
throwaway copy under `p0/tamper/`.

| rows run | rows passed | refuted | unreproducible |
|---|---|---|---|
| 10 | 10 | 0 | 0 |

Result: **every tested assertion reproduced**. Nothing here is a refutation. The notes
carry six wording corrections that should land before publication, because in each case
the evidence is true but a plausible paraphrase of it would not be.

## Environment

| item | value |
|---|---|
| root R | `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01` |
| plugin source P | `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/sbl-tpm-sp` |
| gate G | `P/scripts/pre_v2_gate_r2.py` (268 lines, read in full) |
| python PY | `_candidate_sbl_tpm_sp_20261102/.venv-pipd/Scripts/python.exe` (3.11.9) |
| pipd PYTHONPATH | `_candidate_sbl_tpm_sp_20261102/patch/pipd-wt/src` (`-m pipd_ls_sp.cli`) |
| tamper workspace | `C:/Projects/Agent_Workspace/_run_sbl_tpm_pre_v2_final_20261103/p0/tamper` |

## Rows

### 1. 1 Acceptance: author gate accepts R/bundle_r2 with AUTHOR_CONTRACT_CONSISTENT (2 requirements, 2 cases)

- **verdict**: `PASS` | **exit**: `0`
- **command**: `PY scripts/pre_v2_gate_r2.py C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/bundle_r2`
- **observed**: `{"verdict":"AUTHOR_CONTRACT_CONSISTENT","authority":"AUTHOR_SIDE_DESIGN_ONLY","source_authority":"ORIGINAL_OWNER_UNVERIFIED","candidate_sha256":"9338793684eab1b08498a683448757678e87783485ec843c35972f003838d405","requirements":2,"cases":2,"effect_state":"DESIGN_ONLY_NOT_ADMITTED","host_invoked":"NOT_RUN","native_e2e":"NOT_RUN","checker":"NOT_RUN","release":"FAIL_CLOSED"}`
- **note**: Reproduced verbatim against the published bundle; requirements=2 and cases=2 match 05_M1_M4_results.json. Negative ceiling fields (checker NOT_RUN, release FAIL_CLOSED) are present, so the pass cannot be read as a native claim.

### 2. 1a Refusal: gate refuses a copy of bundle_r2 with PlannedTQAEP.json deleted

- **verdict**: `PASS` | **exit**: `1`
- **command**: `PY scripts/pre_v2_gate_r2.py p0/tamper/c1_missing_tqaep   (copy of bundle_r2 with PlannedTQAEP.json removed)`
- **observed**: `{"verdict":"FAIL_CLOSED","first_fail":"[WinError 2] the system cannot find the file specified: 'C:\\...\\p0\\tamper\\c1_missing_tqaep\\PlannedTQAEP.json'"}`
- **note**: Refuses and exits non-zero, so the claim holds. Weakness worth recording before publication: the refusal surfaces as an untyped OSError string that echoes an absolute host path, not as a typed code such as ARTIFACT_MISSING:PlannedTQAEP.json. 05_M1_M4_results.json's wording 'file missing (fail closed)' is accurate but the raw first_fail is not machine-classifiable.

### 3. 1b Refusal: gate refuses a copy whose PI polarity is flipped and its digest re-signed

- **verdict**: `PASS` | **exit**: `1`
- **command**: `PY resign.py p0/tamper/c1_polarity polarity  (PI.requirements[0].polarity POS->NEG, then re-signed PD.pi_digest, ECP.pd_digest, manifest artifact shas and candidate_sha256) && PY scripts/pre_v2_gate_r2.py p0/tamper/c1_polarity`
- **observed**: `resign -> candidate_sha256 908267ccfb2c4371593b2ee76206f6854a427589524d3e578549af1e6d995539; gate -> {"verdict":"FAIL_CLOSED","first_fail":"PI_TRACE_OR_ORACLE_MISMATCH"}`
- **note**: The whole re-sign chain had to be forged (PI sha, PD.pi_digest, ECP.pd_digest, candidate digest, manifest) for the gate to reach the semantic layer, and it still refused. Confirms the reported first_fail exactly: the digest seal alone cannot launder a polarity flip; the registry is the real anchor.

### 4. 1c Refusal: gate refuses a copy with an injected checker receipt key

- **verdict**: `PASS` | **exit**: `1`
- **command**: `PY resign.py p0/tamper/c1_receipt receipt  (adds top-level 'checker_execution_receipt' to PlannedTQAEP.json, re-signed) && PY scripts/pre_v2_gate_r2.py p0/tamper/c1_receipt`
- **observed**: `{"verdict":"FAIL_CLOSED","first_fail":"FORBIDDEN_DESIGN_KEY:$.checker_execution_receipt"}`
- **note**: Exact match to the reported first_fail. Note the injection does not move candidate_sha256 (PlannedTQAEP is outside the three-body candidate frame), so only the FORBIDDEN key walk catches it - and it does, because walk_no_credentials runs before the per-body schema check.

### 5. 2 Acceptance: pipd validate --bundle R/c2/bundle.json --require-four => FOUR_OBJECT / complete true / checked 4

- **verdict**: `PASS` | **exit**: `0`
- **command**: `PYTHONPATH=patch/pipd-wt/src .venv-pipd/Scripts/python.exe -m pipd_ls_sp.cli validate --bundle <R>/c2/bundle.json --require-four`
- **observed**: `checked=4, closure=FULL, complete=true, missing=[], required=[PI-PKG,PD-PKG,ECP,TQAEP], scope=FOUR_OBJECT, verdict=PASS, findings=[]`
- **note**: Matches R/c2/validate_pos.out field for field. Only difference is schema_source.tried[0], which depends on CWD, not on the bundle.

### 6. 2b Refusal: same command on R/01_products/pipd/bundle_missing_tqaep.json => PARTIAL_BUNDLE and fails closed with exit != 0

- **verdict**: `PASS` | **exit**: `1`
- **command**: `PYTHONPATH=patch/pipd-wt/src .venv-pipd/Scripts/python.exe -m pipd_ls_sp.cli validate --bundle <R>/01_products/pipd/bundle_missing_tqaep.json --require-four`
- **observed**: `checked=3, complete=false, scope=PARTIAL_BUNDLE, verdict=FAIL, missing=[TQAEP], findings=[{contract:'*',kind:'DENOMINATOR',detail:'missing required object(s): TQAEP'}]`
- **note**: Exact match to R/01_products/pipd/m2b_strict.out. Precision for the published text: the same bundle WITHOUT --require-four exits 0 / verdict PASS / scope PARTIAL_BUNDLE (reproduced, matches m2b_partial.out). Fail-closed comes from the flag, not from the validator default - do not state it as 'a missing TQAEP fails validation'.

### 7. 3 Refusals: fake grant, cross-subject PI, blind retry (named tests only)

- **verdict**: `PASS` | **exit**: `0`
- **command**: `PYTHONPATH=patch/pipd-wt/src .venv-pipd/Scripts/python.exe -m pytest tests/test_pre_v2_adapters.py -k 'fake_grant_refused or cross_subject_refused or blind_retry_refused' -v`
- **observed**: `3 selected / 9 deselected: test_nested_fake_grant_refused_by_original_writer, test_cross_subject_refused, test_blind_retry_refused -- all 3 passed in 2.31s`
- **note**: Read the bodies to confirm they are real refusals and not vacuous: each plants one defect (details['grant']='forged'; subject_id='OTHER'; details['on_unknown']='RETRY') and asserts EffectUnknown from pipeline.compile_effect_ecp. The refusal is enforced by the original PIPD writer, not by the sbl-tpm-sp plugin - do not attribute it to the plugin.

### 8. 4 Install/remove record under R/raw/ is consistent (version 0.3.0-rc.2; removal list shows it gone); live cache untouched

- **verdict**: `PASS` | **exit**: `0`
- **command**: `read R/raw/{plugin_list_installed,plugin_list_removed,plugin_list_final,host_reinstall,host_remove,host_final_add}.txt + ls of shadow/codex-home/plugins/cache + read-only mtime probe of ~/.codex/plugins/cache`
- **observed**: `installed: 'sbl-tpm-sp@sbl-pre-primary-local installed, enabled 0.3.0-rc.2'; removed: same line 'not installed'; hosts: Added(...)->Removed(...)->Added(...); shadow/codex-home/plugins/cache/sbl-pre-primary-local/sbl-tpm-sp/0.3.0-rc.2 exists; config.toml [plugins."sbl-tpm-sp@sbl-pre-primary-local"] enabled=true; ~/.codex has no sbl-pre-primary-local marketplace`
- **note**: Timeline is coherent by mtime: reinstall 23:11:42.11 -> installed-list 23:11:43.17 -> remove 23:11:43.53 -> removed-list 23:11:44.50 -> final add 23:11:44.97 -> final-list 23:11:45.86. Two caveats for the published text: (i) plugin_list_final.txt shows the plugin INSTALLED again, so 'the removal list shows it gone' is true of plugin_list_removed.txt only, not of the final state; (ii) a live-cache entry ~/.codex/plugins/cache/created-by-me-remote/sbl-tpm-sp/0.3.0-rc.2 exists with mtime 2026-11-03 07:41 (+08:00), ~8.5h AFTER this run and under a different (remote) marketplace id - this run did not write it, but no claim may say the real host has never held 0.3.0-rc.2.

### 9. 5 Extra falsification: bundle_r2 with PI.json replaced by the real canonical R/01_products/pipd/pi.json, no re-signing

- **verdict**: `PASS` | **exit**: `1`
- **command**: `cp <R>/01_products/pipd/pi.json p0/tamper/c5_pi_swap/PI.json && PY scripts/pre_v2_gate_r2.py p0/tamper/c5_pi_swap`
- **observed**: `{"verdict":"FAIL_CLOSED","first_fail":"ARTIFACT_SHA_MISMATCH:PI.json"}`
- **note**: The gate fails, but one layer earlier than a reader might expect: the manifest artifact sha is checked before anything semantic, so a genuine-but-unbound canonical PI is rejected as a hash mismatch and never reaches PI_TRACE_OR_ORACLE_MISMATCH or PI_BINDING. Correct fail-closed behaviour, and evidence that a swapped-in 'real' artifact cannot be smuggled past the manifest.

### 10. 6 Extra falsification: no code path mints grant / nonce / QUALIFIED / INDEPENDENT_PASS / signed_verdict

- **verdict**: `PASS` | **exit**: `0`
- **command**: `grep -rn -i over patch/sbl-tpm-sp for each token, code scope (py/json/yaml) excluding references/corpus; plus mint/issue/emit/sign scan of scripts/ and skills/, plus manual read of core.py:306-311, check_semantics.py:29-34, pre_v2.py:13-14,36,41`
- **observed**: `In code the five tokens appear only as: FORBIDDEN/ESCALATIONS/BAD_CLAIMS denylists (pre_v2.py:13-14, pre_v2_gate_r2.py:19-25), refusal branches (need(...)/raise Refusal('EXTERNAL_RAW_AND_AUTHORITY_REQUIRED') in core.py:307, FORBIDDEN_AUTHORITY_KEY/FORBIDDEN_DESIGN_CLAIM in pre_v2.py:36,41, claim_gate error in check_semantics.py:32), schema consts that pin the opposite state ('independent_acceptance': 'NOT_GRANTED', 'grant_state': 'NOT_GRANTED'), negative-test strings and descriptive text. No mint/issue/emit/sign helper exists in scripts/ or skills/.`
- **note**: One honesty caveat rather than a refutation: the phrase 'appear only as denylist/forbidden keys' is slightly too strong. skills/pipd-package-project/{input,output}.schema.json list LOCAL_QUALIFIED and INDEPENDENT_PASS as admissible allowed_claims VALUES, and the claim_gate rule will pass such a case only when an externally supplied approval_receipt AND checker_identity are present. So the plugin can propagate a ceiling someone else established; it cannot create the evidence. Say 'no code path mints' - do not say 'the strings never appear as accepted values'.

## Corrections to apply to the published text

1. Row 2 - do not present the deleted-file refusal as a typed gate code. The first_fail is a
   raw `[WinError 2]` string carrying an absolute path. It fails closed, but it is not
   machine-classifiable and it leaks a host path into the verdict record.
2. Row 6 - the missing-TQAEP bundle PASSES validation on its own (exit 0, scope
   `PARTIAL_BUNDLE`). Only `--require-four` makes it fail. Never state it as 'a bundle
   without TQAEP fails validation'.
3. Row 7 - the three refusals are enforced by the original PIPD writer
   (`pipeline.compile_effect_ecp`), not by the `sbl-tpm-sp` plugin. Attribute them correctly.
4. Row 8 - `plugin_list_final.txt` shows the plugin **installed** again after the removal.
   'The removal list shows it gone' is true of `plugin_list_removed.txt` only; the recorded
   final state is installed + enabled. Also: a live-cache entry
   `~/.codex/plugins/cache/created-by-me-remote/sbl-tpm-sp/0.3.0-rc.2` exists with mtime
   2026-11-03 07:41 (+08:00), about 8.5 h after this run and from a different (remote)
   marketplace id. This run did not write it, but nothing may claim the real host has never
   held 0.3.0-rc.2.
5. Row 9 - a genuine canonical PI swapped in without re-signing is rejected as
   `ARTIFACT_SHA_MISMATCH:PI.json`, before any semantic check. Correct, but say 'hash
   mismatch' rather than 'trace mismatch' - the trace check is never reached.
6. Row 10 - say 'no code path mints grant / nonce / QUALIFIED / INDEPENDENT_PASS /
   signed_verdict'. Do not say the strings never appear as accepted values:
   `skills/pipd-package-project/{input,output}.schema.json` admit `LOCAL_QUALIFIED` and
   `INDEPENDENT_PASS` as `allowed_claims` values, gated on an externally supplied
   `approval_receipt` + `checker_identity`. The plugin propagates such a ceiling; it cannot
   create the evidence behind it.

## Method note on row 3

Re-signing the polarity flip required forging five linked digests in order: `PI.json` sha,
`PD.pi_digest`, `ECP.pd_digest`, the framed three-body candidate digest, and the manifest
artifact shas. After all of that the gate still refused with `PI_TRACE_OR_ORACLE_MISMATCH`.
The registry, not the digest seal, is what actually binds PI polarity - which is the
strongest single result in this precheck.
