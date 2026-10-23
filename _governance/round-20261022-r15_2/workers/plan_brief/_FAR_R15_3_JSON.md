NONCE: PLAN-R153-FARJ3-093812

Begin your reply with exactly this token on its own line: PLAN-R153-FARJ3-093812

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# PLAN brief — R15.3 FAR adjudication (read-only; emit JSON to stdout)

You are SBL-Commander and PLAN on the SBL / HG-KSEOS / Fabric stack. This turn is READ-ONLY and it has ONE
deliverable: a single JSON object printed to stdout. Do not write any file; the orchestrator persists your text.

Do not dispatch, spawn or poll another lane or agent. Do not sign any Permit, Admission, acceptance or release.

## New fact that changes the previous rulings

The owner issued a standing pre-authorization on 2026-10-23: treat the FAR ruling as the owner ruling and execute it.
So an item whose ONLY missing artefact was an owner designation is now CLOSE_NOW_AGENT, provided the record says
"owner-declared by standing order 2026-10-23" with the digest and timestamp, instead of impersonating a signature.

It does NOT authorise: a third party native signature (SWOF Domain Owner W3 admission, ChatGPT host-issued plugin
IDs), a change to policy CONTENT, a credential use, or a release seal for an unaccepted subject.

## Measured state (verified this session; do not re-derive, cite it as given)

Round head f848dc6 on branch evidence/r15_2-20261022; SBL main bedc119 (the dc5428f in the docs is stale);
Fabric d626356 with 7 dirty files; PIPD rescue 39079c0 with 218 dirty files; SWOF 417f115 with 9 dirty files;
HG-KSEOS 237969e clean.

Queue 26 items = 21 DONE / 5 PARKED / 0 READY.
18 WorkPackages: DONE W00,W01,W03,W04; PARTIAL W05..W11,W13..W17; NOT_RUN W02,W12.
25 CheckRuns: DONE C00,C01,C03,C12; NOT_RUN C02,C11,C13,C15,C16,C19,C21,C22; the other 13 PARTIAL.
9 E-series: PARTIAL E01,E03,E04,E05,E07; NOT_RUN E02,E06,E08,E09.
4 Milestones: PARTIAL M1,M2,M4; NOT_RUN M3.
Parked: W02.policy (OWNER), W12.swof (OWNER), W13.hosts (HOST), W15.release (OWNER), W16.perf (OWNER).
independent_acceptance NOT_RUN; M1 LOCAL_REVIEW_ONLY; release BLOCKED.
Lanes: PLAN and VERIFY on openai-codex/gpt-6.1-sol (OAuth, rank 2); EXECUTE on opencode-go/deepseek-v4.1-flash
(rank 1). Both re-probed alive this session.

Unmerged SBL branches, ahead/behind against main, measured with git rev-list --count:
candidate/c3-20261020-v1 1/0; candidate/c3-20261021-v2 6/0; candidate/r14-openspec-20261022 28/0;
candidate/r14-ts15-kinds 46/0; candidate/r7-20261021-repro-build 13/0; candidate/r9-20261021-ctrlpkg 19/0;
docs/r12-claims-20261021 21/0; evidence/r11-20261021-intake 48/0; evidence/r12-20261021-far 25/0;
evidence/r12-far-close-20261023 28/0; evidence/r13-20261021-native 29/0; evidence/r14-20261022-native 75/0;
evidence/r15_2-20261022 117/0; evidence/r5-20261021-c5 19/0; evidence/r7-20261021-c7 45/0;
fix/r12-far-skills 23/0; fix/r12-far-skills-2 25/0; release/0.1.1rc1 17/0; evidence/r2-20261020 1/16 (diverged).

## The deliverable: ONE JSON object, printed to stdout, nothing else

Shape:

{"schema":"SBL_FAR_DECISIONS/3","rows":[
 {"id":"C02","set":"checkrun","class":"CLOSE_NOW_AGENT|CLOSE_BY_ONE_OWNER_STEP|ACCEPT_AS_CEILING|HARD_BLOCKED",
  "decision":"DECIDE|DEFER|NO_ACTION","ruling":"<=240 chars",
  "action":"the literal next command or the single owner sentence","evidence":"path that will prove it",
  "predicate":"pass/fail test","ceiling":"what may not be claimed after it","depends_on":["id"]}],
 "adopt":[{"artefact":"path","as":"PRODUCT|EVIDENCE|ADVISORY","claim":"...","precondition":"...","verified_by":"..."}],
 "merge":[{"branch":"...","verdict":"MERGE|CHERRY_PICK|NEVER","deciding_defect":"...","why":"<=200 chars"}],
 "binding_constraint":"the one sentence that says what stops R15.1 from being complete",
 "answers":{"r15_2_complete":"NO|YES + reason","r15_1_complete":"NO|YES + reason"},
 "irreversible":["..."],"reversible":["..."]}

Rows you must include, one per id, no consolidation unless both ids appear in "id":
W02, W05, W06, W07, W08, W09, W10, W11, W12, W13, W14, W15, W16, W17,
C02, C04, C05, C06, C07, C08, C09, C10, C11, C13, C14, C15, C16, C17, C18, C19, C20, C21, C22, C23, C24,
E01, E02, E03, E04, E05, E06, E07, E08, E09, M1, M2, M3, M4,
W02.policy, W12.swof, W13.hosts, W15.release, W16.perf.

Rules for the content:
- "action" must be executable as written: a command line, or one sentence an owner says out loud. Not a topic.
- Prefer the cheapest legal closure. Do not recommend a second issuer, reducer, RBWI, scheduler or semantic framework.
- Do not recommend git add -A, reset --hard, force push, or writing another principal's dirty tree.
- For anything the agent cannot legally close, use ACCEPT_AS_CEILING and put the ceiling sentence in "ceiling".
- "adopt" must name real paths that exist in the round tree under workers/candidate_proposals or _governance.
- "merge" must give one defect per branch; NEVER is a valid verdict and a blind merge is never one.
- If a locator does not resolve, do not paraphrase from memory: set ruling to TT_SOURCE_LOCATOR.

Print only the JSON. No prose before or after it.
