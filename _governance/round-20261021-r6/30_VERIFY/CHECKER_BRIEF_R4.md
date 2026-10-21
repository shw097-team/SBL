# R6 Independent Verify Brief — ROUND 4 (CHK29)
Round-3 environment blocker: the read-only sandbox denied pytest's temp-dir writes. This round the checker
lane runs with a workspace-write sandbox BUT the SBL candidate tree is guard-subject enforced: any mutation
VOIDs your verdict, and only your own scratch (C:/Projects/Agent_Workspace/HG-KSEOS/var/R6-CHKS/tmp) is for temp.

Mandate (same as round-3 brief pointer):
1. sha256 of in-repo wheel _governance/round-20261021-r6/50_TS06/sbl_v01-0.1.0-py3-none-any.whl must equal
   wheel.sha256 inside _governance/round-20261021-r6/20_TS05/TS05_READBACK.json.
2. From C:/Projects/_sbl_r4/c3v2 run:
   C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe -B -m pytest tests/ -p no:cacheprovider
   Expect exactly "192 passed, 2 skipped".
3. Output STRENGTHS/WEAKNESSES/ITEMS-LIST(max 3)/VERDICT: PASS | PASS_WITH_DISCLOSURES | FAIL, end token R6CHK29R4-NC.
