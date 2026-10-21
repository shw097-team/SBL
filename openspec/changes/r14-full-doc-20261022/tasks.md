# r14-full-doc-20261022 — tasks

## 1. Baseline and compile (done in round-20261022-r14)

- [x] 1.1 Fresh dual-SHA readback of SBL / HG-KSEOS / Fabric / PIPD / SWOF with dirty-owner inventory
- [x] 1.2 Verify 14/14 DOC against the pinned manifest and reproduce rollup `01b972c8…`
- [x] 1.3 Compile the R14 C0–C9 contract: lint/activation/acceptance/compile all exit 0
- [x] 1.4 Reproduce the HGK denominator (18F/580P/90) and capture per-case first failures for all 18
- [x] 1.5 Probe PLAN / EXECUTE / VERIFY_SECURITY with a typed nonce and forced rank

## 2. M1 native chain

- [ ] 2.1 Close the 12 lane-declaration/serving reds with one HGK-owner workorder per cause (registry epoch,
      declared-vs-projected arm, `ERR_MANDATE_ARM_UNRESOLVED`, `ERR_LANE_REQUIRED_ARM_ABSENT`)
- [ ] 2.2 Close the 5 doc-projection / canonical-runtime reds (denominator head, guide projection, config path)
- [ ] 2.3 Record the foreign dirty tree as an owner-owned baseline, not as a rewrite of the allowed-files test
- [ ] 2.4 Add a dynamic independent checker: frozen candidate, isolated copy, raw stdout/exit/denominator
- [ ] 2.5 Emit `commander_invocation_id` from a real Commander-SP call in the PLAN pre-handoff
- [ ] 2.6 Emit `challenge_invocation_id` from a real Challenge-SP call in the VERIFY pre-spawn
- [ ] 2.7 HGK native delta ABI: install/doctor is not an upgrade; add replay/expiry/partial-effect negatives
- [ ] 2.8 Fabric F0 six-edge readback on one subject tuple

## 3. M2 isolated dogfood

- [ ] 3.1 Non-prefabricated requirement → PI/PD → TaskSpec in an isolated copy
- [ ] 3.2 Real red→green with defect injection, bounded repair, checkpoint, rollback
- [ ] 3.3 Independent checker re-runs the same raw commands on the copy

## 4. M3 (blocked until SWOF W3)

- [ ] 4.1 W2 frozen readset accepted by the SWOF owner
- [ ] 4.2 W3 permit + receiver ACK with an explicit write set
- [ ] 4.3 First real governed SWOF change with remote readback

## 5. M4 (stays open)

- [ ] 5.1 Owner-signed semantic denominator
- [ ] 5.2 Five-tool host lifecycle, three ZIPs, three plugins (plugins stay pending)
- [ ] 5.3 149/441/38/8 skills/39 gates/12x8 applicability ledgers
