# VERIFY_REPORT — M2 (PlannedTQAEP@2 author bundle) / M2b (PIPD four-object denominator)

- Independent verifier: Hermes subagent (hgk-governed), read-only outside `gstack/`
- Date: 2026-11-03 00:44 (host local)
- Interpreter: `C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/.venv-sbl/Scripts/python.exe` (CPython 3.11.9)
- Bundle under test: `RUN-20261102-GJ02-01/bundle_r2` (mtimes 00:32, unmodified by this run)
- Tamper copies: `RUN-20261102-GJ02-01/gstack/tmp/{ctl_baseline,a_missing_tqaep,b_polarity,c_forbidden_key}`
- Nothing pushed, nothing committed, gate/bundle/repos not modified.

Verdict summary: **10 / 11 checks PASS**. One check FAILS — the *archived* PIPD evidence
(`validate.out`, `validate_missing.out`) predates the denominator change and does not carry
`scope`/`complete`/`missing`; the CLI itself reproduces the claim when re-run.
(The 11 rows are the 4 gate runs incl. a control copy, 4 PIPD CLI runs, the archived-output
comparison, and the two scans of the pushed tree.)

---

## Check 1 — Author gate on the real bundle — **PASS**

Command:
```
C:/Projects/.../.venv-sbl/Scripts/python.exe \
  C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/sbl-tpm-sp/scripts/pre_v2_gate_r2.py \
  C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/bundle_r2
```
Exit code: **0**

Output:
```json
{"authority": "AUTHOR_SIDE_DESIGN_ONLY", "candidate_sha256": "9338793684eab1b08498a683448757678e87783485ec843c35972f003838d405",
 "cases": 2, "checker": "NOT_RUN", "effect_state": "DESIGN_ONLY_NOT_ADMITTED", "host_invoked": "NOT_RUN",
 "native_e2e": "NOT_RUN", "release": "FAIL_CLOSED", "requirements": 2,
 "source_authority": "ORIGINAL_OWNER_UNVERIFIED", "verdict": "AUTHOR_CONTRACT_CONSISTENT"}
```

Claim (1) reproduced exactly: exit 0, `AUTHOR_CONTRACT_CONSISTENT`, **2 requirements**, **2 cases**,
`effect_state = DESIGN_ONLY_NOT_ADMITTED`.
Note on scope of proof: the gate self-declares `authority = AUTHOR_SIDE_DESIGN_ONLY`,
`source_authority = ORIGINAL_OWNER_UNVERIFIED`, `host_invoked/native_e2e/checker = NOT_RUN`,
`release = FAIL_CLOSED`. This proves byte/ID consistency only — it is **not** any authority,
grant, or independence claim, consistent with the gate docstring.

---

## Check 2a — Delete `PlannedTQAEP.json` — **PASS (fail-closed)**

Command:
```
python <gate> .../gstack/tmp/a_missing_tqaep
```
Exit code: **1**

Output / `first_fail`:
```json
{"verdict": "FAIL_CLOSED", "first_fail": "[WinError 2] 系統找不到指定的檔案。:
 'C:\\\\...\\\\gstack\\\\tmp\\\\a_missing_tqaep\\\\PlannedTQAEP.json'"}
```

Caveat (robustness, not a claim failure): the refusal is an **uncaught-path OSError string**, not a
semantic code such as `ARTIFACT_MISSING:PlannedTQAEP.json`. The verdict is still fail-closed (exit 1),
but the message is Windows-locale-dependent (Chinese system text here), so the exact `first_fail`
string is not reproducible across locales — downstream assertions should match on
`verdict == FAIL_CLOSED` / non-zero exit, never on this text.

---

## Check 2b — Tampered PI polarity with fully recomputed SHAs — **PASS (fail-closed, correct code)**

Tamper applied (copy only): `PI.json.requirements[0].polarity` `POS -> NEG`, then re-signed per
`SBL.PRE_V2.CANDIDATE@2` framing
`sha256(b'SBL.PRE_V2.CANDIDATE@2\0' + Σ(name+'\0'+len8BE+bytes) for PI,PD,ECP)`,
plus `manifest.artifacts["PI.json"].sha256`, `manifest.candidate_sha256`, and
`PlannedTQAEP.candidate_sha256`.

Re-sign evidence: manifest `candidate_sha256` moved `9338793684eab1b0…` -> `7f92a0a30a533f71…`,
`artifacts["PI.json"].sha256` moved `cc6493d4baa71920…` -> `cd461d976880d092…`. Because the gate
checks the candidate digest (line 164) *before* the PI trace comparison (line 180), a reachable
`PI_TRACE_OR_ORACLE_MISMATCH` proves the re-sign was accepted and the failure is genuine.

Exit code: **1**

Output:
```json
{"verdict": "FAIL_CLOSED", "first_fail": "PI_TRACE_OR_ORACLE_MISMATCH"}
```

---

## Check 2c — Injected `checker_execution_receipt` with re-signed artifact SHA — **PASS (fail-closed, correct code)**

Tamper applied (copy only): added `"checker_execution_receipt": "fake/receipt-0001"` to
`PlannedTQAEP.json` and re-signed `manifest.artifacts["PlannedTQAEP.json"].sha256` (candidate digest
intentionally untouched — PlannedTQAEP is excluded from the candidate framing, so no re-sign needed;
confirmed unchanged at `9338793684eab1b0…`).

Exit code: **1**

Output:
```json
{"verdict": "FAIL_CLOSED", "first_fail": "FORBIDDEN_DESIGN_KEY:$.checker_execution_receipt"}
```

Ordering proof: artifact SHA check (line 160) passes, so the gate reached `walk_no_credentials`
(line 166) and rejected on the key before the PlannedTQAEP schema-field check (line 222).

Control: an unmodified copy `ctl_baseline` returned exit 0 / `AUTHOR_CONTRACT_CONSISTENT`,
so the three failures are caused by the tampering, not by copying.

---

## Check 3 — PIPD validator: scope / complete / missing, and `--require-four` — **PASS**

Environment: `PYTHONPATH=C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/patch/pipd-wt/src`,
cwd `01_products/pipd`.

| # | Command | Exit | scope | complete | checked | missing | verdict |
|---|---------|------|-------|----------|---------|---------|---------|
| 3.1 | `python -m pipd_ls_sp.cli validate --bundle bundle.json` | 0 | `FOUR_OBJECT` | `true` | 4 | `[]` | `PASS` |
| 3.2 | `… --bundle bundle.json --require-four` | 0 | `FOUR_OBJECT` | `true` | 4 | `[]` | `PASS` |
| 3.3 | `… --bundle bundle_missing_tqaep.json` | 0 | `PARTIAL_BUNDLE` | `false` | 3 | `["TQAEP"]` | `PASS` |
| 3.4 | `… --bundle bundle_missing_tqaep.json --require-four` | **1** | `PARTIAL_BUNDLE` | `false` | 3 | `["TQAEP"]` | `FAIL` |

3.4 finding:
```json
{"contract": "*", "detail": "missing required object(s): TQAEP", "kind": "DENOMINATOR"}
```
`required` = `["PI-PKG","PD-PKG","ECP","TQAEP"]`, `closure` = `FULL` in all four runs.

Claim (3) reproduced: the current CLI returns `scope`/`complete`/`missing`, and `--require-four`
fails closed (exit 1) with a `DENOMINATOR` finding.

---

## Check 4 — Archived PIPD outputs match the current CLI — **FAIL**

`01_products/pipd/validate.out` (mtime 23:08) contains only
`{checked:4, closure:"FULL", findings:[], schema_source:…, verdict:"PASS"}` — **no `scope`, no
`complete`, no `missing`, no `required`**. `validate_missing.out` (23:08) likewise has
`checked:3 … verdict:"PASS"` and no denominator fields. Both predate the change evidenced by
`m2b_partial.out` / `m2b_strict.out` (00:37), which *do* carry the fields.

The same stale pair is what PR #18's pushed tree carries
(`deliver-wt/evidence/pre-primary-20261102/RUN-20261102-GJ02-01/01_products/pipd/validate.out`,
`validate_missing.out` — byte-identical to the products copies), and the pushed tree contains
**no** `m2b_partial.out` / `m2b_strict.out` at all.

Command: `cat validate.out; cat validate_missing.out` (exit 0); re-run comparison above.
Impact: the published M2b evidence does not itself demonstrate `scope`/`complete`/`missing`;
the claim rests on re-running the CLI. Fix is a re-capture of the two `.out` files (and publishing
the `--require-four` pair), not a code change.

---

## Check 5 — Secret scan of the pushed evidence tree — **PASS**

Scope: `deliver-wt/evidence/pre-primary-20261102` (25 files, 243 KB, no file > 200 KB).

Commands and results:
```
grep -rIn -E 'ghp_|github_pat_|OPENCODEGO|OPENCODE_GO_API_KEY|Bearer |BEGIN [A-Z ]*PRIVATE KEY' .
```
-> 5 hits, all non-secret:
- `00_run_manifest.json:24` — prose: `"credential_source": "local key file, injected as OPENCODE_GO_API_KEY for the process only; never written to a commit, log or artifact"`
- `04_closeout.md:49` — prose invocation template with the literal placeholder `OPENCODE_GO_API_KEY=<local key>`
- `specs/{Architecture,Product,Program}SPEC.json` — JSON key `"ghp_01"` = *GitHub delivery decision phase 01*
  (`SBL.GitHubDeliveryDecision@1`, `state: LOCAL_ONLY`), **not** a token

```
grep -rIn -oE '\b(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-…|AKIA[0-9A-Z]{12,}|AIza…|eyJ…)' .
```
-> exit 1, **zero matches** (no credential-shaped token anywhere in the tree)

High-entropy sweep (40+ chars, non-hex, Shannon ≥ 4.3 + bare-token regex): 161 candidates,
every one a **sha256/sha1 design digest** or a design identifier
(`fixtures/REQ-<hex>/positive`, `test_total_rounds_once_on_the_invoice_total`,
`pluginrel_6ae839cbc3c88191a906f64d31f0e449`). No token, key, or bearer material.

Broad word scan (`api_key|secret|token|password|credential`) hits only:
`README.md:32` ("No corpus, credential, grant, nonce or private key is included"),
`00_run_manifest.json` (`credential_source` prose), `04_closeout.md` (placeholder), and
`bundle.json` / `ecp.json` / `02_checkrun.json` field-name matches inside design contracts.

---

## Check 6 — No corpus / 24-DOC body in the pushed tree — **PASS**

```
find . -iname "*corpus*" -o -iname "*references*" -o -iname "*24*DOC*" -o -iname "*.pdf"   -> (empty)
find . -type f -size +200k                                                                  -> (empty)
du -sh .                                                                                    -> 243K
grep -rIl -iE 'corpus_manifest|documents\(\)|24 documents|DOC-24' .                          -> exit 1 (none)
```
No `references/` or `corpus/` directory, no corpus manifest, no 24-document body, no PDF.
Only **textual citations by name** exist, all inside design records, e.g.
`specs/*SPEC.json`: `"source_ref": "plugin corpus PIPD DOC-02 (1).md"` (in a
`SOURCE_UNAVAILABLE` state record naming the FileNotFoundError) and
`pipd/pi.json:21`: `"oracle_source": "DOC-03 DOMAIN_ORACLES"`. These are identifiers, not bodies —
the corpus content is not present.

---

## Observations (outside the four claims, no verdict attached)

1. The pushed tree carries only the PIPD v0 artefacts. **M2 author evidence — `bundle_r2`
   (`manifest.json`, `PlannedTQAEP.json`) and any `pre_v2_gate_r2.py` output — is not in
   `deliver-wt/evidence/pre-primary-20261102` at all.** Claim (2)'s fail-closed proof exists only
   in this verification run, not in the PR.
2. `gstack/tmp/` retains the four bundle copies and `tamper.py` / `tamper_results.json`; they are
   throwaway and safe to delete.
3. Underlying artifact counts, for reference: registry `requirements = 2`, `cases = 2`,
   `required_fuo = ["FUO-ROUND-ONCE"]`, `candidate_sha256 = 93387936…d405` (identical in
   `bundle_r2/manifest.json` and `PlannedTQAEP.json`).

## Files written by this verification (all under `RUN-20261102-GJ02-01/gstack/`)

- `VERIFY_REPORT.md` (this file)
- `gate.json` (machine-readable rows)
- `tmp/tamper.py`, `tmp/tamper_results.json`
- `tmp/{ctl_baseline,a_missing_tqaep,b_polarity,c_forbidden_key}/` (bundle copies)
