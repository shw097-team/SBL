# Independent challenge — pass 3 (read-only)

- receipt: `receipts/dispatch/VERIFY_SECURITY__CHALLENGE_PASS3.json` — ok=true, gpt-6.1-sol, rank 2, 109.07s, nonce present
- transcript is the orchestrator's copy of the lane's final message

```
VERDICT: FAIL

basis: C6’s evidence-integrity repair passes the requested on-disk checks. A7 has credible recorded behavioural evidence, but the green dispatch does not retroactively establish mandate-compliant provenance for code authored under a red receipt. It also violated its hard command budget. The unchanged acceptance limits remain; this is not independent acceptance.

1) C6 raw evidence — PASS. Recursively checked all 11 rows carrying `raw_path` in `workers/q5_tools/LIFECYCLE_RECEIPT.json:1`: 11 distinct resolved paths; zero missing files, SHA-256 mismatches, or recorded-byte-length mismatches. All 11 adjacent `.sha256` sidecars exist, match the computed file hashes, and match their declared sidecar paths. Referenced capture prefixes cover `001`–`011` without duplication. JSON traversal order is not capture order.

2) A7 doctor repair — NARROWED, not closed. The green receipt records `ok=true`, 102.12 seconds, and nonce presence; I independently confirmed its stdout bytes/hash and the repair nonce in that stdout. Recorded execution shows doctor rc 2, `SBL_E_MANIFEST_UNTRUSTED`, no traceback in that result, and nine test progress marks with pytest rc 0. However:
- `workers/q5_repair/DOCTOR_REPAIR.json:1` explicitly says `product_code_changed: false`: this lane tested the existing repair, rather than repairing its authorship provenance.
- Its before/after digests concern the tampered installed manifest, not a bound product-code patch.
- The claimed eight-command compliance is false: the repair report admits 15 commands; the green stdout contains 16 completed shell-command events.
- The removed-entry check is not a clean fresh-install demonstration: its logged `install_rc=2` precedes the removal.

3) what still bites —
1. `TT-R15.2-MANDATE-AUDIT-IS-SHALLOW`: item-specific receipt validation still requires manual matching. This run returned `AUDIT_CLEAN` for 26 items; that does not establish A7’s validity.
2. A4 still lacks a before/after content manifest for `outside_scope_unchanged`.
3. One host and one family cannot establish independent acceptance.
4. No clean continuation result was obtained: running the unchanged guard with write-denial enforcement stopped its attempted write to `QUEUE_R15_2.json` and returned rc 2. No files were changed.

conditions before an independent PASS could exist —
1. Resolve A7’s code-change provenance through a mandate-compliant, patch-bound repair or explicitly authorized adoption process; behavioural retesting alone is insufficient.
2. Meet the hard command budget and establish clean setup evidence for each claimed variant.
3. Supply A4’s missing content-manifest evidence and validate each item’s actual bound receipt.
4. Satisfy independent coverage requirements and obtain clean terminal gates without violating the read-only constraint."}}
{"type":"turn.completed
```
