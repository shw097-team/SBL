# L3 — Source-metadata hygiene + owner Ed25519 crypto verification (EC-R26-004, EC-R26-009, EC-R26-011, EC-R26-008 / R26-02, R26-06)

Read `_COMMON.md` first. Worktree: `C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-meta` (branch r27/metadata-hygiene).
Round payload dir (relative to worktree): `evidence/fhs-w0-r26-repair-20261109/`

## Part A — L1 byte/line metadata (EC-R26-004, EC-R26-011)
Real truth, measured on this host — re-measure it yourself and record the commands:
- `doc/FHS_PIPD-LS-PKG_W0_r26.md` is the frozen r26 subject.
- The L1 blueprint《PIPD-LS-PKG_藍圖 r4》 real file is `6,224,679` bytes and `28,005` LF-split lines.
- The published ACK claims `subject_scope.source_contract.l1.bytes = 111331`, which is the 31-volume source inventory's total LINE count, not L1's byte size.

Required:
1. Locate the source file (`evidence/FHS_ORIGINAL_ACK.json` and any duplicate under the round). Re-measure L1 with `os.stat().st_size` + `len(bytes.split(b"\n"))`; compare against the declared value.
2. Repair the ACK metadata so that `l1.bytes` and `l1.lines` carry the REAL L1 values, and `source_inventory.total_lines = 111331` carries the 31-source line total in its own field. Every changed number must be accompanied by `measured_from`, `measured_sha256_of_source`, and `measured_at`.
3. `unaffected_proof`: the four unaffected WPs (WP-FHS-15 12 clauses, WP-FHS-16 4, WP-FHS-19 2, WP-FHS-21 1) are 19 clauses -> `19 x 4 = 76` preservation properties, NOT `32-4=28`. Recompute from the receipts with a script (count `preservation` keys per clause per WP), print the per-WP counts, and repair the proof text. If the receipt parser disagrees with 76, report the measured number and the disagreement — do not force 76.
4. Add a typed check to the round's gate tooling: find the G24 implementation (grep for `G24` under `evidence/fhs-w0-r26-repair-20261109/tools/` and `.github/`) and add a check that every declared `bytes`/`lines` for L0/L1/L2 and the W1–W4 skeletons is re-derived from the file and rejected on mismatch with code `SOURCE_CONTRACT_BYTES_MISMATCH`. Then EXECUTE the negative: a mutated copy of the ACK (bytes field set to 111331 for l1) must be refused by the new check, captured to a log with non-zero exit.
5. Do not alter any `receipts/**/*.signed.json`. If the ACK JSON is itself covered by a signature, do NOT edit it in place: write the repaired ACK as `evidence/FHS_ORIGINAL_ACK_R27.json`, keep the old file byte-identical, and record `superseded_by` + the old sha256 in the new file. State which path you took and why.

## Part B — EVIDENCE_SCOPE (EC-R26-009)
`evidence/EVIDENCE_SCOPE.json` currently lists six gates (`G11,G13,G16a,G16b,G19,G26`) under `profiles.full.excluded` while the author's own full gate self-reports executing them.
Repair: `profiles.full.excluded = {}` and add a separate `profiles.full.not_runnable_in_CI = [...]` list with the same six names and a one-line reason each. Recompute any digest/manifest that binds EVIDENCE_SCOPE, and report which shas changed.

## Part C — Owner Ed25519 verification (EC-R26-008, R26-06) — REAL CRYPTO, no simulation
`evidence/PUBLIC_VERIFICATION_BUNDLE.json` carries the owner public key `d42c654cd1afba803ef78bee501aa3e2a3d33ff1305c52f914d3ff27bb9be379` and 7 signature references (6 reader receipts under `receipts/reader/*.signed.json` + `receipts/OWNER_SEMANTIC_ACK_R26.signed.json`).
1. Write `evidence/fhs-w0-r26-repair-20261109/tools/verify_public_bundle.py` using `cryptography` (run it with `python` on PATH, which has cryptography 50.0.2). For each of the 7: canonicalise the signed payload EXACTLY as the signer did (determine the canonicalisation from the receipt's own `body`/`payload_sha256` field and from the sibling tools — `sign_r26.py`, `post_sign_r26.py`, `verify_reader_ack.py` in `FHS_W0_R13_ACCEPTANCE_20261108/tools/` are readable references), re-derive `payload_sha256`, check it equals the declared one, then verify the Ed25519 signature against the public key.
2. Print per-signature: file, payload_sha256 recomputed vs declared, signature_valid true/false, signature_hex_prefix vs declared. Exit 0 only if all 7 verify; otherwise exit 1 with the first failing file.
3. Record the `preauth_at` timezone defect: `2026-11-09T19:22:25` carries no offset while `verify_pass_at` is `+08:00`. Do NOT rewrite the signed bundle. Report it as `FINDING_R26-06_TZ_UNQUALIFIED` and state precisely what the owner must re-sign to close it.
4. If canonicalisation cannot be reproduced exactly, say so: report `CANONICALISATION_UNRESOLVED` with the two candidate canonicalisations you tried and their measured payload shas. Never claim a signature is valid because the prefix matches.

## Deliverables
`.../out/L3_RESULT.json` + `.md`, per `_COMMON.md`, plus the raw logs under `.../evidence/L3/`.
