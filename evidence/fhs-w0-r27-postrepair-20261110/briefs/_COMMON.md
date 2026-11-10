# COMMON RULES — FHS W0 r26 post-repair round (APPEND-ONLY, EVIDENCE-FIRST)

Run root: `C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110`
Evidence dir (write ALL logs + JSON here): `C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110/evidence/<LANE>/`
Out dir (write result summaries here): `.../out/`

Interpreters:
- tests / general python: `C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe` (pytest 9.1.1)
- crypto (cryptography 50.0.2): `python` on PATH (Hermes venv)
- NOTE: native python cannot read MSYS `/tmp`. Write scratch under the evidence dir, never /tmp.

Git rules (hard):
- Work ONLY inside your assigned worktree/branch (already created). Never `git checkout main`, never commit to main, never `git push`, never `--force`, never `git merge --allow-unrelated-histories`.
- Commit your work on your branch with a message ending in the line `subject_sha256=0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f`.
- Do NOT edit signed receipts (`receipts/**/*.signed.json`), do NOT edit the frozen r26 document, do NOT edit another lane's files.

Evidence rules (hard):
- Every factual claim in your summary MUST cite: the exact command, its exit code, the raw log path, and the log's sha256.
- A negative test is only evidence if THIS run produced a named refusal code + non-zero exit, captured to a log. Never type a result into a generator.
- Never fabricate. If something is blocked, write `BLOCKED` + the exact error + what you tried. `BLOCKED` is an acceptable answer; an invented PASS is not.
- Do not create a second routing registry, a second issuer, or a parallel copy of a governed tool. Repair the existing one in place.

Deliverable shape (write to `.../out/<LANE>_RESULT.json`):
{"lane": "...", "status": "PASS|PARTIAL|BLOCKED", "changed_files": [...], "commands": [{"cmd","exit","log","log_sha256"}],
 "negatives": [{"id","expected_code","observed_code","exit","log"}], "findings_closed": ["EC-R26-00X","R26-0Y"],
 "not_claimed": [...], "notes": "..."}
Then also write `.../out/<LANE>_RESULT.md` (short, Traditional Chinese + code tokens verbatim).
