# Owner adjudication — R4 focused-repair (2026-10-09)

Machine-readable record: `docs/OWNER_ADJUDICATION_R4_2026-10-09.json` (schema `PIPD-OWNER-ADJUDICATION/1`).

**Authority.** The repository owner directed: *"直接執行研究後的建議最佳工程裁決，並且把相關實作內容和證據更新至
GITHUB REPO，讓外部官進行驗收"* — execute the recommended engineering rulings, and publish the implementation and
evidence to the GitHub repo for external verification.

**Basis.** `PIPD-LS-SP_R4_PLAN_RULINGS_A1A5V7_2026-10-09` — a FAR-style analysis produced by the PLAN lane
(GPT 6.1 SOL-MEDIUM via the CODEX CLI) over the supplied local evidence only.

**Ceiling.** `CANDIDATE_ONLY`. `INDEPENDENT_PASS`, `RELEASED` and `PRODUCTION_VERIFIED` remain **NOT GRANTED**.

## The six rulings, and what executing each actually did

| item | ruling | what was executed |
|---|---|---|
| **A1** | `DISPOSITION_COMPLETE_GATE_PARTIAL` | Recorded. The seven knowledge-owner dispositions already exist in R3 (2 clean / 5 reference / 0 retained). The remaining blocker is **external**: an owner-authorised sanitizer repair plus a fresh 160/160 probe. No per-source disposition waits on the owner. |
| **A2** | `ACCEPT_EXISTING_NO_LICENSE_NOTICE` | **The only authority act taken.** It grants **nothing** — no licence, no release, no independent pass, no production verification. This publication is a candidate for external verification, not a release. |
| **A3** | `FAIL_WITH_UNPROVENANCED_BUDGETS` | Recorded. The perf gate stays **FAIL** (`context_bytes_per_artefact` 343,547 vs 20,000; stable across runs). All four thresholds keep `UNPROVENANCED`; the three timing rows keep `UNDECIDABLE`. **No threshold was raised.** |
| **A4** | `KEEP_CROSSWALK_EVIDENCE_GAPS` | Recorded. 42 EVIDENCED / 11 EVIDENCE_GAP / 4 DESIGN_ONLY of 57 rows, each keeping its first-fail reason. No overall PASS claim. |
| **A5** | `CARRY_OPEN_TTS_WITHOUT_BLANKET_CLOSURE` | Recorded. 22 rows / 18 blocking treated as the recorded projection. **No row was bulk-closed and the register was not rewritten.** |
| **V7** | `NOT_RUN_ACCEPTANCE_PARTIAL` | Recorded and linked separately from the 22-row register. Accepted correction: **a commit alone cannot convert V7 to PASS** — a newly committed baseline cannot prove an absent historical baseline was preserved. |

## Custodian bookkeeping — executed or explicitly carried

- **PYCACHE / TOOLING projection:** already satisfied — both rows carry the fresh projection in their authoritative
  `state` field (`PYCACHE state=CLOSED`, `TOOLING state=PARTIAL`). **No register write was needed or made.**
  `tools/tt_summary_check.py --assert` → `TT_SUMMARY_ASSERT_OK total=22 unknown=0 blocking_count=18`.
- **V7:** linked separately; the 22-row count was not silently changed.
- **Gate-verdict scope:** the failing hard gate (perf context budget) is surfaced at the **top** of this record, of the
  README and of the closure report — not buried in a subsection.
- **Label / disclosure amendments:** recorded as append-only corrections; no historical verdict text was rewritten.
- **HG-KSEOS-side rows** (`TT-HGK-*`) and the admission/oracle items are **outside this candidate's scope** and are
  carried open, each needing its own WorkOrder in the control-plane repository.

## Not self-granted — these belong to other owners

`TT-ORACLE-DISAGREEMENT-KP-R04` (KP source owner) · `TT-PIPD-PREFLIGHT-ORDER` (admission contract) ·
`TT-PIPD-WORKORDER-WORKTREES` · `TT-PIPD-S2-S8` (stage admission) · `TT-PRE-W3-CROSS-PROJECT` (its own HITL owner).

## Closing statement

> Close this round with residual gates open and `ClaimCeiling=CANDIDATE_ONLY`; publication is a candidate for external
> verification and grants no licence, release, independent pass or production verification.
