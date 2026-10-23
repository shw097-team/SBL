# PLAN brief — R15.3 FAR adjudication (owner pre-authorized)

You are **SBL-Commander & PLAN** on the SBL × HG-KSEOS × Fabric stack. This is a **read-only** turn: you may read
every file under `C:/Projects/Agent_Workspace` but you must **not** write product code, must not dispatch or spawn
another lane or agent, and must not sign any Permit, Admission, acceptance or release.

## New fact that changes the previous rulings

The owner has now issued a **standing pre-authorization** (2026-10-23, this session): *"maximum pre-authorization:
treat the FAR recommendation as the owner's ruling and execute it"*. So an item whose only missing artefact was an
**owner designation** is no longer `CLOSE_BY_ONE_OWNER_STEP`; it is `CLOSE_NOW_AGENT` **provided** the agent records
the designation as owner-declared-by-standing-order (with the order text, digest and timestamp) instead of
impersonating a signature.

It does **not** authorise: fabricating a *third party's* native signature (SWOF Domain Owner W3 admission, ChatGPT
host-issued plugin IDs), a Constitution/policy **content** change, a credential use, or a release seal for an
unaccepted subject. Those stay typed, with the honest ceiling.

## Measured state you must adjudicate against (verified this session, do not re-derive)

| Thing | Value |
|---|---|
| Round worktree | `C:/Projects/Agent_Workspace/_r152_ev` branch `evidence/r15_2-20261022` |
| Round head | `f848dc6` (remote equal) |
| Round tree | `_r152_ev/_governance/round-20261022-r15_2` |
| SBL main | `bedc119` (the DOC-cited `dc5428f` is stale) |
| Fabric | branch `pub/far-minimax-mandate-20261021` @ `d626356`, 7 dirty |
| PIPD rescue tree | `rescue/r5p-uncommitted-20261016` @ `39079c0`, 218 dirty |
| SWOF | `evidence/swof-w2r5-closure-repair` @ `417f115`, 9 dirty |
| HG-KSEOS | `codex/hgk-final-closure-002` @ `237969e`, clean |
| Queue | 26 items: **21 DONE / 5 PARKED / 0 READY** (`QUEUE_R15_2.json`) |
| 18 WorkPackages | 4 DONE (W00,W01,W03,W04) / 12 PARTIAL / **2 NOT_RUN (W02,W12)** |
| 25 CheckRuns | 4 DONE (C00,C01,C03,C12) / 13 PARTIAL / **8 NOT_RUN (C02,C11,C13,C15,C16,C19,C21,C22)** |
| 9 E-series | 0 DONE / 5 PARTIAL / **4 NOT_RUN (E02,E06,E08,E09)** |
| 4 Milestones | 0 PASSED / 3 PARTIAL / **M3 NOT_RUN** |
| Parked | `W02.policy` OWNER, `W12.swof` OWNER, `W13.hosts` HOST, `W15.release` OWNER, `W16.perf` OWNER |
| Independent acceptance | `NOT_RUN`; M1 = `LOCAL_REVIEW_ONLY` (Q7 checker separation unproven) |
| Release | `BLOCKED` |
| Mandated lanes | PLAN/VERIFY `openai-codex/gpt-6.1-sol` (OAuth, rank 2), EXECUTE `opencode-go/deepseek-v4.1-flash` (rank 1) — both re-probed alive this session |

## Deliverable 1 — `FAR_R15_3_ADJUDICATION.md` (the report the owner asked for)

Answer, with citations to files/paths (never from memory), each of the owner's six questions:

1. **Is R15.2 complete?** No/yes with the exact denominator above and the single strongest reason.
2. **Is R15.1 complete?** Use R15.1 §5/§6 (18 W, 25 C) and §15/§16 (R14 31 TS/31 CHK, E01–E09, M1–M4) plus
   `R14_LEDGER_READBACK.json` and `DENOMINATOR_R15_2.json`; give the same three-state count (DONE/PARTIAL/NOT_RUN)
   and say which rows are the binding constraint.
3. **How does every residual/gap/blocked/unclosed item close?** One row per open item — no grouping that hides a row.
   For each: `class` (`CLOSE_NOW_AGENT` / `CLOSE_BY_ONE_OWNER_STEP` / `ACCEPT_AS_CEILING` / `HARD_BLOCKED`),
   the **literal command or action** that closes it, the evidence that proves it, and the pass/fail predicate.
4. **Which candidate items / SKILLs can be adopted directly?** Name the artefact path, what it claims, the
   verification already recorded, and the pre-condition for adoption (e.g. `git apply --check` rc=0 + tests green).
   Separate "adopt as product" from "adopt as evidence/advisory".
5. **Which unmerged candidates could be merged into MAIN?** Use the real ahead/behind table
   (`candidate/r14-ts15-kinds` ahead 46, `candidate/r14-openspec-20261022` ahead 28, `candidate/c3-20261021-v2`
   ahead 6, `evidence/r14-20261022-native` ahead 75, `evidence/r15_2-20261022` ahead 117, …). For each: merge,
   cherry-pick, or never — and the one defect that decides it. Never recommend a blind merge or a force push.
6. **Every pending owner/host decision**, with your ruling and the exact owner-side sentence that would change it.

## Deliverable 2 — `FAR_DECISIONS_R15_3.json`

Machine-readable, one object per open row and per owner item:

```json
{"schema":"SBL_FAR_DECISIONS/3","rows":[
 {"id":"W02.policy","class":"CLOSE_NOW_AGENT","decision":"DECIDE|DEFER|NO_ACTION",
  "ruling":"...","action":"the literal next command","evidence":"path that will prove it",
  "predicate":"...","ceiling":"what may NOT be claimed after it","depends_on":[]}]}
```

Cover every row that is not DONE in the 18 W / 25 C / 9 E / 4 M sets plus the five parked items — that is the
minimum; a row may be consolidated only if you name both ids in `id`.

## Deliverable 3 — `PLAN_ANSWER_R15_3.md`

Your own reasoning trail: what you read, what you rejected and why, and the three decisions you consider reversible
vs irreversible. Keep the honest ceiling sentence: *recommendations, not closure receipts.*

## Hard rules

- **Exactly these three files**, written under `workers/plan_brief/`; then stop. Do not modify anything else.
- Cite `path:line` or a file digest for every factual claim. If a locator does not resolve, write
  `TT_SOURCE_LOCATOR` for it rather than paraphrasing from memory.
- Do not recommend building a second issuer, reducer, RBWI, scheduler or semantic framework.
- Do not recommend `git add -A`, `reset --hard`, force push, or overwriting another principal's dirty tree.
- If you believe an item cannot legally close this round, say `ACCEPT_AS_CEILING` and print the exact ceiling
  sentence to carry, instead of inventing a path.
