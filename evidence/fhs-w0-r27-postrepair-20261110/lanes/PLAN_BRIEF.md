# PLAN lane brief — FHS W0 r26 post-repair round (READ-ONLY planning, no writes)

You are the **PLAN** lane for a governed repair round. You may read files and reason. You must not write,
edit, create or delete any file, must not run any command that mutates state, and must not call any
provider. Your entire output is prose returned in your reply.

## Subject

An external challenge report judged the FHS W0 r26 candidate `PARTIAL` with `HOLD_NOT_ACCEPTED` and
raised 13 findings (`EC-R26-001` … `EC-R26-013`) plus 12 resume predicates (`R26-01` … `R26-12`).
Read, in this order, from the local filesystem:

1. `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/實作/W0/FHS_W0_r26_External_Challenge_PostRepair_Acceptance_Report_2026-11-09.md`
2. `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/實作/W0/FHS_W0_R26_FHS3LM_HardEntry_and_HGK_Main_Convergence_Execution_Contract_2026-11-09.md`
3. The round board: `C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110/KANBAN.md`

## What to produce (one reply, structured)

A. **Closure classification for every one of the 13 findings**, each labelled exactly one of:
   `CLOSABLE_LOCAL_MECHANICAL` (a bounded code/doc change in a repo we hold, provable by an executed negative),
   `CLOSABLE_BUT_REQUIRES_OWNER_SIGNATURE` (the mechanism can be fixed, the acceptance instrument cannot be re-signed by an agent),
   `NOT_CLOSABLE_HERE` (needs another host, another repo owner, or an external party), or
   `CLAIM_WITHDRAWAL_ONLY` (the correct action is to retract the claim, not to change code).
   One line of justification each, quoting the report's own words.

B. **The minimum ordered change-set** that closes the CLOSABLE ones, as a DAG: for each node give the
   file, the single responsibility, the negative test that proves it, and which finding it closes. Name any
   node that must NOT be attempted because it would create a second authority (a second router, a second
   registry, a second issuer, a rewritten governed byte).

C. **The honest verdict token** this round may claim when the change-set lands and its negatives fire, and
   the token it may NOT claim. Justify each with the report's own verdict vocabulary.

D. **The three highest risks** of doing this work at all, and the detection you would want for each.

Be specific and terse. Quote real identifiers (codes, shas, paths). Do not invent measurements you did not
read. If a document is unreadable or a path is absent, say so explicitly instead of guessing.
