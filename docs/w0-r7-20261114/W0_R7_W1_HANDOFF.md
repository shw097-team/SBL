# W0 R7 → W1 handoff (2026-11-14)

**Subject**: `FHS-W0-R7-20261114` · **Profile**: `fhs_next` · **Ceiling**: see below.

## What is usable now

- Three-spec identity check passes (`ops/tools/spec_identity_check.py`, exit 0): same Goal, four differences.
- The 31-document corpus gate is 31/31; the copy register re-reads 41 groups / 343 members PASS.
- `L1` is structurally complete: 50 chapters, 5/5 sections each (`CH-00..CH-49`), no missing POS/NEG/consumer.

## What is NOT established (do not inherit as done)

- The original SBL/PIPD reader has not accepted anything (`H-READER`). The owner key can sign
  `original_reader_ack`; that signature is the owner's, not this agent's.
- Four of the six W0 work packages have a trace but no done-evidence file:
  `WP-FHS-01` (AuthorityConflictLedger / Oracle-Profile binding), `WP-FHS-16` (485 four-column
  disposition table), `WP-FHS-19` (CI/License/NOTICE/SBOM raw for one CandidateSHA),
  `WP-FHS-21` (96-case Oracle plan). See the HG-KSEOS round folder for the exact missing fields.

## First W1 actions that are lawful today

1. Read the HG-KSEOS round folder `docs/w0-r7-20261114/` before touching any write set.
2. Ask the owner for an exact write set before `WP-FHS-06`; nothing here authorises a repo write.
3. Treat `FHS-08` slot dispositions as source data, not as an install list.

Claim ceiling: SOURCE_READ + HOST_RAW + AUTHOR_DESIGN + LOCAL_CHECK + LANE_SERVED + WRAPPER_SCOPED_SOD.
Not claimed: ORIGINAL_ACK, NATIVE_PASS, INDEPENDENT_PASS, RELEASE. No merge, no main write.
