# Proposal: native admission and convergent evidence packaging

## Why

This round executed the R15.2 command with HG-KSEOS as the native issuer. Two things were learned the hard way and
should stop being re-learned:

1. **A lifecycle state is not an effect.** HG-KSEOS reaches `WORKORDERS_ADMITTED` and `DELIVERY_READY` without issuing
   or verifying anything, so a reader who trusts the state name concludes the opposite of the truth.
2. **A package that contains its own verification receipts never converges.** Three consecutive exact-set readbacks
   failed because the measuring file was a member of the measured set, and because each dispatch added files to the
   tree it had just measured.

Both are cheap to encode as requirements, and expensive to leave as tribal knowledge.

## What changes

- `sbl_core` gains no new product behaviour; the change binds *evidence* behaviour that already exists in practice
  (`sbl_core.gknow` ingestion, the 227-test suite, CAPE receipts) to explicit, checkable requirements.
- Work-order admission must be demonstrated by reading the rows back, never by quoting the lifecycle state.
- A delivery package declares its scope rule, excludes its own verification receipts, and states `DELIVERY_READY`
  separately from `DELIVERED`.

## Impact

- Affected specs: `sbl-native-admission` (new capability).
- Affected code: governance tooling under `_governance/round-*/tools/` only; no product module changes.
- Release impact: none. This change does not assert a release; it asserts how evidence for one must be shaped.
