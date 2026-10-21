# R6 Independent Verify Brief (round SBL-R6-DOC00-13-CONTINUATION, CHK29)

## Your task
You are the separate model-axis independent checker for SBL round R6. Your mandate:
1. Read back the raw inputs listed below and independently recompute the checks — accept nothing on the maker's say-so.
2. For each finding, copy the exact cfg/args/exit code/case that proves it.
3. Output a SHORT verdict (English, markdown) with sections: STRENGTHS / WEAKNESSES / ITEMS-LIST / VERDICT.
4. Do not modify any file. You are read-only.

## Inputs (raw, machine-generated this round; all under C:/Projects/Agent_Workspace/SBL)
- _governance/round-20261021-r6/00_NORTH_STAR_AND_SPEC.md              (round spec, lane/session plane separation)
- _governance/round-20261021-r6/10_PREFLIGHT/SSOT_FACTS.json           (46-source intake hashes + git + HGK readback)
- _governance/round-20261021-r6/30_CONTRACT/…, contracts/SBL_C0_C9_CONTRACT-R6.json + compiled-r6/compiler-receipt.json   (PROMPT_COMPILE_PASS)
- _governance/round-20261021-r6/40_TS05/TS05_READBACK.json             (a6bcdd0 tests 192/2 vs CI 191+3/189+5; wheel manifest parity)
- evidence_ledger/child_outcome_ledger.json + surface_c001_c038_ledger.json + source_identity_441_ledger.json  (50/149/38/441 skeleton; every row OPEN, no fabricated PASS)
- _governance/round-20261021-r6/20_TS20/SP_SEPARATION_CHECK.json       (13 POS/NEG permission probes, 13/13)
- upstream frozen subject: https://github.com/shw097-team/SBL commit a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2 (local worktree C:/Projects/_sbl_r4/c3v2 @ same SHA)

## Baseline R6 reference
- R6 external review report sha256 ac2db3cb…42cde; merge decision RECOMMEND_MERGE_SCOPED_NOW (Owner-only, NOT performed).
- Full-contract verdict stays FAIL_FULL_CONTRACT / PARTIAL_CHALLENGE; three ChatGPT plugins 0/3 host-issued IDs; DeepSeek surfaces NOT_ADMITTED.

## Model-axis deviation to disclose (do NOT re-derive)
Round identity: R6-TS19/CHK29 independent checker is openai-codex/gpt-6.1-sol (OAuth), role mandate openai-codex/gpt-6.1-sol.
Upstream R6 report was produced by two different lanes in rounds R5; its identity deviates by model axis. That is an upstream additive disclosure, NOT yours to re-derive: focus on whether the maker-side R6 facts hold under your independent re-checks.

## Output
Return exactly one artifact: an English markdown document with a VERDICT line of the form
VERDICT: PASS_WITH_DISCLOSURES | FAIL | PASS
and a numbered ITEMS-LIST (max 8 lines) — each item: id, severity(BLOCKER/MAJOR/MINOR), what you re-executed to prove it.
Be adversarial: actively try to find a fabricated PASS row, an orphan id, a hash mismatch, an SP-permission leak, or a proxy-evidence shortcut in the R6 round.
