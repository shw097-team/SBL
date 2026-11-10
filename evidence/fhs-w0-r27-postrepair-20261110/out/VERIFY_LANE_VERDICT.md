# VERIFY_SECURITY lane verdict (openai-codex/gpt-6.1-sol, Codex CLI, read-only)

Source: `lanes/runs/VERIFY_SECURITY/R27VERIFYACCEPT-20261111T002546/attempt-4800-1794327946-1-stdout.txt`
Receipt: ok=true, exit 0, nonce present, 306.37 s, usage input 1,194,662 / output 10,542.

R27VERIFYACCEPT

| claim | verdict | command | exit | decisive output |
|---|---|---|---|---|
| C1 — Missing candidate binding refused | UNPROVEN | Inline Python predicate probe with `votes_r25={'A':True,'B':True}`; selftest withheld because it writes fixtures | Not started: ENOENT | Python executable could not be launched; predicate not exercised. |
| C2 — Fabricated raw digest refused | UNPROVEN | Inline Python probe: passing control, then `raw_sha256='00'*32` | Not started: ENOENT | No runtime result for `RAW_DIGEST_MISMATCH`. |
| C3 — Integer vote refused | UNPROVEN | Inline Python probe: passing control, then `vote=1` | Not started: ENOENT | No runtime result for `VOTE_TYPE_INVALID`. |
| C4 — Real repair votes count | UNPROVEN | `PY -B tools/verify_quorum.py --root .` in payload | Not started: ENOENT | `properties_checked` and scanner findings unavailable. Independent receipt count is 128 properties, but predicate acceptance remains untested. |
| C5 — Per-run, unoverwritable bindings | UNPROVEN | Reviewed `selftest_fhs_3lm.py`; did not execute binds | Not run | Selftest creates/copies/deletes scratch files; binding creation conflicts with the brief’s read-only prohibition. |
| C6 — Drift, expiry, tampering refused | UNPROVEN | Reviewed `assert_binding`; did not create or alter copies | Not run | Required binding/copy mutations prohibited; refusal codes not exercised. |
| C7 — Retired arm refused | UNPROVEN | `PY -B tools/fhs_3lm.py --assert-arm opencode-go/mimo-v2.6-pro --hgk-root B` | Not started: ENOENT | Expected exit 9 not observed. |
| C8 — Seven signatures verify | UNPROVEN | `PY -B tools/verify_public_bundle.py`; supplementary Node Ed25519 verification | Python: ENOENT; Node: N/A | Node independently verified **7/7**, matching both declared payload digests; one-byte in-memory mutations failed verification for all seven. Required Python/file-copy test unexecuted. |
| C9 — L1 metadata true | CONFIRMED | Node `fs.stat`, `fs.readFile`, SHA-256, newline count; compare ACK | N/A | `bytes=6224679`, `lines=28005`, SHA `cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b`; all agree. |
| C10 — 76-property denominator | CONFIRMED | Count each clause’s `preservation` keys in six receipts | N/A | WP00: 8/32; WP01: 5/20; WP15: 12/48; WP16: 4/16; WP19: 2/8; WP21: 1/4. Last four total **19 clauses / 76 properties**. |
| C11 — Scope exclusions corrected | CONFIRMED | Read payload `evidence/EVIDENCE_SCOPE.json` | N/A | `profiles.full.excluded={}`; `not_runnable_in_CI` contains exactly `G11,G13,G16a,G16b,G19,G26`. |
| C12 — r27 append-only | CONFIRMED | Node byte comparison: complete payload r26 against r27 prefix; SHA-256 both files | N/A | Prefix equality **true**. r26: **667205 B**, SHA `09c666dad4f31099f862c12cc5d3758620c46c70bc5f410af727c465bbb6b0f7`. r27: **688148 B**, SHA `151645f86e20a79f2a3b8def52d61cc9d80f98d5b61afdf8a33ed730351d63d5`. |
| C13 — HGK histories disjoint | CONFIRMED | `git merge-base acd9196f 86f40ec`; `git rev-list --left-right --count acd9196f...86f40ec` | 1; 0 | Merge-base stdout/stderr empty. Count output: `90	328`. |
| C14 — Bridge is content port | UNPROVEN | In B: requested log, diff-stat, and merge-log commands | 128; 129; 128 | `fatal: detected dubious ownership in repository`; diff reported `Not a git repository`. |
| C15 — Fresh-process guard, zero spawn | UNPROVEN | `PY -B scripts/hgk-lane-dispatch.py --lane EXECUTE --prompt PROBE_FHS_ENTRY --nonce PROBE_NONCE --max-candidates 1` in H | Not started: ENOENT | Dispatcher never ran; neither `FHS_ENTRY_ASSERT_REQUIRED` nor guarded zero-spawn behavior was demonstrated. Selftest withheld because it writes. |
| C16 — Fabric admission digest | UNPROVEN | Rehash mirror; `PY -B INTEGRATION/FHS/tools/validate_manifest_admission.py` in F | Hash: N/A; validator: ENOENT | Mirror and manifest agree: **668540 B**, SHA `0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f`. Validator and negatives unexecuted. |
| C17 — Payload gate and metadata negative | UNPROVEN | `PY -B tools/gate_r20.py --profile payload` | Not started: ENOENT | No gate verdict. Copy/mutation negative withheld under read-only restriction. |

**findings[]**

- **C1–C4, C7–C8, C15–C17 — Runtime unavailable.** Each attempted Python command returned empty stdout/stderr and:
  ```text
  spawn C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe ENOENT
  ```
  `PY` above denotes that exact executable. No numeric application exit exists because execution never began. PATH Python also failed with exit **103**; `py.exe -0p` printed `No installed Pythons found!`. C4’s findings cannot honestly be reported as `[]`.

- **C1, C5–C6, C8, C15–C17 — Read-only conflict.** The brief prohibits creating, editing, or deleting files while requesting scratch bindings, copies, and mutation tests. Source inspection confirms `verify_quorum.py:441–452` writes fixtures, `selftest_fhs_3lm.py` creates/copies files and calls `shutil.rmtree`, and the guard/admission tests write artifacts. These operations were not performed. C8’s supplementary mutation used memory only.

- **C14 — Git ownership protection prevented verification.** Raw log-command evidence:
  ```text
  fatal: detected dubious ownership in repository at 'C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-bridge'
  ```
  Git identified different owner/current-user SIDs. No ownership exception or configuration change was applied.

- **C17 — Command scope mismatch.** Independently inspected source:
  ```text
  2048: --scope ... default="full"
  2050: --profile ... default="round"
  2072: if a.scope == "payload":
  ```
  Thus `--profile payload` alone does not select the advertised 16-check scope. This is a reproduction-command discrepancy, not an observed gate failure.

**claim_ceiling_recommendation**

- **May use:** `CONFIRMED` for C9–C13 only; `UNPROVEN` for the remaining claims; `NOT_ACCEPTED` for overall acceptance status.
- **May not use:** overall `PASS`, `INDEPENDENT_PASS`, `RP002_LOCAL_ACCEPTANCE_PASS`, `ACCEPTED`, `EXTERNALLY_ACCEPTED`, `NATIVE_SIGNED`, or `RELEASE_GRANTED`.
- The requested opening token is not an acceptance receipt. No files were modified.
