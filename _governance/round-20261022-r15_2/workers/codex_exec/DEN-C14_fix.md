# EXECUTE brief — repair C14: name the missing resume contract instead of simulating it (small)

File to EDIT: `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c14_checkpoint_resume_no_repeat_effect.py`
Surface for reference: `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/recovery.py`

## The challenge
The checker ruled that unlinking the target simulates an absent destination, not an interrupted restore, and that the
file never exercises an `operation_id`, a readback after timeout, or UNKNOWN/PARTIAL reconciliation
(KB `...R15_1...#1418`).

## Change exactly one test and add one
1. Rewrite `test_resume_after_interrupted_restore_reproduces_the_backup_exactly` so the interruption is realistic:
   start a restore into a target, interrupt it by making the target a directory (or by removing the target mid-way in a
   way the implementation reports), then resume and assert the final bytes equal the backup exactly. Keep the assertion
   about bytes, not about a message string.
2. Add `test_resume_requires_operation_identity`: assert the product records or requires an `operation_id` for a resume.
   If `recovery` exposes none, write it as `xfail(strict=True, reason="R15_1#1418 operation_id / readback reconciliation absent")`
   and put the citation in the docstring.

Do not edit any other file, the queue, the receipts or the mandate. Do not run pytest. No network, no fixtures.
Where the product lacks the rule, mark the test `@pytest.mark.xfail(strict=True, reason="<citation> <rule>")` so the
gap stays visible; never weaken an assertion to manufacture green.
