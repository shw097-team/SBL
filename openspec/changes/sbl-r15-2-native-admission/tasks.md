# Tasks

## 1. Native admission

- [x] 1.1 Bind every source root before admission (`ERR_INTAKE_STATE` makes later correction impossible)
- [x] 1.2 Walk the lifecycle to `PLAN_READY` and stop there (`admit_workorders` requires that state)
- [x] 1.3 Call `admit_workorders(project_id)` and read the work-order rows back from the spine
- [x] 1.4 Give every project a unique id tail (`spec_id` collides otherwise: `UNIQUE constraint failed`)
- [ ] 1.5 Re-gate `DELIVERY_READY` so it cannot be reached with FAILED work orders

## 2. Bounded execution

- [x] 2.1 EXECUTE lane: Codex CLI + `opencode-go/minimax-m3.1-flash-free`, write-set `workers/codex_exec/**`
- [x] 2.2 Before/after whole-tree digest plus `git status` on every governed repo
- [x] 2.3 Record the measured truth: in the `_r152_ev` worktree, 638 tracked text files join to a 37,693-character path
      list — 37,733 with the `git -C … check-attr eol -- ` prefix — against the Windows 32,767 cap. SBL main joins to
      23,136 and stays under it, so the defect only bites in large worktrees.
- [x] 2.4 EXECUTE lane write effect proven, with the caveat stated: one file survives (`EXEC_RECEIPT.json`); a helper
      script was created and removed inside the same dispatch; the dispatcher reports `subject_mutation=not_guarded`, so
      write-set containment rests on the round's external snapshot rather than on the dispatcher
- [x] 2.5 Number reconciliation recorded: 37,693 path chars; 37,733 with a 40-char prefix; 37,757 with a 64-char one;
      and 639 tracked text entries by git pathspec versus 638 by a Python suffix filter (one C-style-quoted non-ASCII
      path)

## 3. Acceptance

- [x] 3.1 VERIFY_SECURITY lane on `gpt-6.1-sol`, distinct principal from the writer value `codex`
- [x] 3.2 Six of six work orders VERIFIED with numbers the checker re-derived itself
- [x] 3.3 Product suite 227 tests, 0 failed, 4 skipped after two Windows portability fixes
- [x] 3.4 Ingestion: 3,033 chunks over 24 documents, zero coverage gaps, retrieval returns locators

## 4. Packaging

- [x] 4.1 Declare the scope rule: round tree minus `receipts/dispatch/` minus the readback itself
- [x] 4.2 Readback excluded from the set it measures
- [x] 4.3 Manifest rebuilt after all bundles; 172 in-scope files, 172 declared, zero hash mismatch
- [ ] 4.4 Independent external acceptance officer (SOD006-C6 still open: checker and writer share host and session)
