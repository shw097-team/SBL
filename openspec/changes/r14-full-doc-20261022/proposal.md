# r14-full-doc-20261022 — proposal

## Why

R14 order `SBL-R14-FULL-DOC-POST-R13-20261022` requires the full DOC-00..13 product obligation to continue
after R13, starting with the M1 native command chain, while keeping every unproven claim open.
R13 delivered a scoped native workorder flow (`_repo_head` repair, WO VERIFIED) but left: 18 conformance
reds, `LANE_ONLY` instead of SP invocation, a static-only checker, three plugins `HOST_PENDING`, and an
`UNKNOWN` semantic denominator.

## What changes

1. **Compiled intent first.** A C0–C9 contract (`SBL_C0_C9_CONTRACT-R14.json`, `contract_sha256 8643749…`)
   compiles to `PROMPT_COMPILE_PASS` before any mutation. `claim_ceiling=LOCAL`.
2. **M1 chain as the only path to mutation**: PLAN Commander-SP → HGK WorkOrder + role binding + lease →
   bounded writer → VERIFY Challenge-SP with dynamic, independently executed tests on an isolated copy.
3. **Conformance is closed case by case, never by editing assertions.** The 18 reds are grouped into
   three owner clusters (12 lane declaration/serving, 5 doc projection/canonical runtime, 1 foreign dirty tree).
4. **M2** isolated SWOF-shaped dogfood; **M3** only with a lawful SWOF W3 permit and receiver ACK; **M4** stays open
   until the PIPD source owner signs the semantic denominator.
5. Plugins stay `HOST_PENDING` while Agent Plugins 1.0 remains a prohibited draft.

## Impact

- Governance: new round packet `_governance/round-20261022-r14/` on an evidence branch.
- Product: no product source change in this change set yet; the first product change arrives with M2/M3.
- Risk: the 18 reds include a lane-registry drift that also affects which model a lane serves; it must be closed
  by the HGK owner, not by adapting tests.

## Out of scope

Rebuilding the R13 repair, a second permit/ECP system, installing non-admitted OSS, installing draft plugin
packaging, any SWOF world write without W3.
