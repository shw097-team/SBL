# SBL-ACK@2 — why the gate, not the tool, must check the ACK

This note accompanies the D-18 candidate (`r4/d18-ack-binding-20261107`). It records the measured
defect, the new contract, and what an existing issuer must change.

## 1. The defect, measured on the pre-patch gate

`sbl_core/modes.py` at `b0d81ee6…` verified one HMAC over `(issuer, permit_id, subject_id)` and nothing
else. Reproduced before the patch:

* an ACK that had **expired an hour earlier** returned `allowed=True`, `reason=NATIVE_ACK_VERIFIED`;
* a single signature (`461472d2…`) authorised **six different claims**, including an unrelated scope and
  an ACK with **no `expires_at` field at all**;
* `permit_id` resolved against no permit store, and `subject_id` was never compared to the ECP.

Adding a TTL check to the issuer tool cannot fix this: the tool is the party being checked. The check has
to be where the decision is made.

## 2. The new contract

Signed payload (`SBL-ACK@2`, scheme-tagged canonical form, every field covered):

```
issuer, permit_id, subject_id, permit_sha256, scope, issued_at, expires_at
```

* `scope` is `scope_digest(ecp_scope)` — the digest over the **sorted, length-prefixed** scope members,
  so `["a:b"]` and `["a","b"]` cannot collide.
* `permit_sha256` is the sha256 of the **exact bytes** of `<SBL_SWOF_PERMIT_STORE>/<permit_id>.json`, so a
  permit edited after the ACK stops matching.
* `issued_at` / `expires_at` must be exactly `YYYY-MM-DDTHH:MM:SSZ`. `+00:00` is refused as
  `SBL_E_ACK_MALFORMED_FIELD`.
* The permit document itself must carry `permit_id` (equal to the file stem), `subject_id`, `scope` (the
  digest string — **not** the path list) and `issued_at` / `expires_at` in the same strict format.

New refusals: `SBL_E_ACK_MISSING_FIELD`, `SBL_E_ACK_SUBJECT_MISMATCH`, `SBL_E_ACK_SCOPE_MISMATCH`,
`SBL_E_ACK_PERMIT_UNKNOWN`, `SBL_E_ACK_PERMIT_MISMATCH`, `SBL_E_ACK_EXPIRED`, plus
`SBL_E_ACK_ECP_MISSING` when `SWOF_CONNECTED` is asked to decide without an ECP.

## 3. Breaking on purpose

Every existing `SBL-ACK@1` ACK stops verifying: it fails `SBL_E_ACK_MISSING_FIELD` on the four new
required fields, and its signature does not match the new scheme-tagged canonical form. That is the
point — an ACK that never expires is the defect, not a feature.

The four-field form is **closed**. `SBL_SWOF_ACK_LEGACY` no longer enables acceptance at all: setting
it (to any value, including the exact `1`) yields `SBL_E_REQUIRES_NATIVE_ACK` with
`detail.state = "SBL_ACK_LEGACY_ACCEPTANCE_CLOSED"`. The variable is kept only so an operator who sets
it is told why nothing verifies, instead of silently reading a strict-mode refusal.

## 4. What an issuer has to change

1. Populate `SBL_SWOF_PERMIT_STORE` with one `<permit_id>.json` per permit, in the shape above.
2. Build the payload with all seven fields and sign it with `ack_signature_v2(...)`.
3. Pass the ECP to `ModeGate(mode, ack, ecp)` — without it `SWOF_CONNECTED` refuses rather than allows.

An issuer tool that implements this end to end, with a self-test matrix that exercises the gate itself,
lives in the round worktree (`issue_sbl_ack_v2_owner.py`, 8/8 against the patched gate). It refuses to
sign when any bound field cannot be sourced, and it never prints key material.

## 5. Test evidence

* `tests/test_ack_binding.py` — 44 cases, run against both gates: **41 failed pre-patch** (each
  `AssertionError: ACCEPTED: allowed=True reason=NATIVE_ACK_VERIFIED`), **44/44 pass post-patch**.
* `tests/test_modes.py` — 14 pass, with two cases repointed: the four-string ACK is now refused as
  `SBL_E_ACK_MISSING_FIELD` before the MAC check, and the positive case exercises the env-gated legacy
  form explicitly.
* The six defects an operator would hit first (missing expiry, missing issued_at, wrong subject, wrong
  scope, unknown permit, mismatched permit digest) each have a case that shows ACCEPT before and REFUSE
  after.

## 6. Known limits of this change

* The gate now binds subject, scope, permit and expiry; it still does **not** bind the ACK to a
  repository HEAD or a write set. That belongs to the ECP/WriteSet layer, not to this gate.
* Replay is prevented within the permit's lifetime by the permit digest and expiry, not by a nonce
  ledger. If replay-within-validity matters, a used-ACK store is a separate change.
