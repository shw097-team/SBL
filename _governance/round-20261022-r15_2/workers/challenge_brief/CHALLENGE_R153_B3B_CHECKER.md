# VERIFY brief — the supersession rule only (one artefact, answer fast)

Artefact: `C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15-2/tools/check_lane_consistency.py` (function `classify_arm` ~line 306,
wired ~483/519/578). Declaration it is run against: `C:/Projects/Agent_Workspace/HG-KSEOS/config/lane-route-slots.candidate.json`.
Current measurement: 69 receipts -> CONSISTENT 42, SUPERSEDED 4, VIOLATION 0, NOT_GREEN 23.

A previous checker said, in 95 characters, "supersession accepts an unauthorized model". Take that as the hypothesis and
settle it: can a receipt that served an arm which was NEVER authorized be excused as SUPERSEDED? Consider
(a) an arm that no pool revision ever declared, (b) an unknown/absent timestamp, (c) a pool that moved twice,
(d) a receipt dated after the pool in force but before the current file's mtime.

You have a HARD 200-second budget. Answer FIRST, investigate second, and never spend the budget reading whole
files: use grep to find the lines you need and read at most 60 lines per file. If you run out of time, emit the JSON
anyway with "coverage":"PARTIAL" and name what you did not check. Emit exactly one JSON object, nothing after it.

Cite the SBL knowledge base with `file#line` (root:
`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL`).

## Output
{"verdict":"PASS|FAIL","finding":"...","failure_modes":[{"mode":"...","reachable":true,"why":"...","test_that_pins":"..."}],
 "worst_case":"...","fix":"<=200 chars","earns":"TOUCHED|PARTIALLY_VERIFIED|VERIFIED","coverage":"FULL|PARTIAL"}
