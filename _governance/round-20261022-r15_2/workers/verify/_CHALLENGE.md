NONCE: VERIFY-R152-CHALLENGE-NONCE-e29aa33c

Begin your reply with exactly this token on its own line: VERIFY-R152-CHALLENGE-NONCE-e29aa33c

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# VERIFY brief — independent challenge of the 2026-10-23 R15.2 continuation artefacts

You are the independent acceptance challenge. **Read-only**: you may write exactly one file,
`workers/verify/VERDICT.json`, under the round tree. You may run commands, create temporary files under
`C:/Users/user/AppData/Local/Temp/verify_*`, and read anything. You may not modify the SBL tree, the round tree,
`HG-KSEOS`, or any candidate. No commits, no lane dispatch, no sub-agents.

Your maker is a different arm (`opencode-go/deepseek-v4.1-flash`). You are `openai-codex/gpt-6.1-sol`. Say in the
verdict what that separation does and does **not** prove (same host, same relay, same operator).

## Frozen subject

`C:/Projects/Agent_Workspace/_r152_ev` at branch `evidence/r15_2-20261022`. The artefacts under review:

| id | artefact | what it claims |
|---|---|---|
A1 | `workers/q2_semantic/DENOMINATOR_PROPOSAL.json` + `Q2_SEMANTIC_DENOMINATOR.md` | 1274 units, 858 normative, 35 cited, 829 unresolved, 143 duplicate IDs |
A2 | `workers/q5_tools/LIFECYCLE_RECEIPT.json` | 5/8 sbl-stack verbs pass, three ZIPs equal across two builds, hgk doctor PASS on 3.12.13, negative control on a tampered manifest |
A3 | `workers/w15_gate_lane/RESULT.json` + `proposal.reapplied.diff` | 4/4 behavioural tests pass, unpatched control fails T1 only, replay byte-identical, live control plane untouched |
A4 | `workers/q3_e2e/Q3_RESULT.json` | the six-predicate M2 chain (baseline/mutant/repaired/regression/outside-scope/cleanup) |
A5 | `workers/candidate_proposals/w06_kinds2/APPLIED.json` | eight-kind routing candidate applied, kind tests + full suite green |
A6 | `workers/plan_brief/PLAN_ANSWER_Q7_CHECKER.md` | SEPARATION_ABSENT → ACCEPT_AS_CEILING |
A7 | `workers/q5_repair/REPAIR.json` | doctor crash repaired with a regression test |

An artefact that is absent is `NOT_RUN`, not `PASS`. Record its absence.

## What to check (each produces `{id, claim, evidence, holds, status}`)

1. **Reproduce, do not trust.** Recompute sha256 for every artefact above. Then re-run at least these two and
   compare against the claimed numbers: `python tools/measure_semantic_denominator.py` and
   `python tools/q5_lifecycle_probe.py`. A count that does not reproduce is `FAIL`.
2. **Crash vs refusal.** In A2's negative control, decide whether `doctor` refused with a typed code or died with
   a traceback. `rc != 0` alone is not a refusal. This is the single most likely place where the round's own
   instrument over-claims.
3. **Predicate honesty in A4.** For each boolean in `predicate`, name the command + exit code in the raw logs that
   licenses it. Any boolean without that pairing is `FAIL` for that row.
4. **A3 replay.** Re-apply `proposal.reapplied.diff` onto a fresh copy of `HG-KSEOS/src/hg_kseos/lifecycle.py`,
   confirm the resulting sha256 equals `lifecycle_sha256_after`, and run the four tests. Confirm
   `HG-KSEOS/src/hg_kseos/lifecycle.py` is still `28c0fa40…` (the diff must not have touched the live tree).
5. **Scope discipline.** `git -C C:/Projects/Agent_Workspace/_r152_ev status --porcelain` — list every modified
   tracked file. Any product file modified outside the files its brief allowed is a violation; name it.
6. **One criterion of your own**, derived from the round's own contract wording rather than from this brief
   (read `CONTRACT.json` or the C00–C24 table in the order and pick something the brief did not ask about,
   e.g. a denominator, a POS/NEG pair, or a claim-ceiling clause). State where you took it from.
7. **Ceiling check.** Does any artefact claim more than "candidate / locally measured"? Look specifically for
   words like PASS, accepted, released, verified in A1–A7 that the evidence does not license.

## Output

`workers/verify/VERDICT.json` with exactly these top-level keys, every string ≤ 250 characters:

`round`, `verifier_model_and_provider`, `verdict` (`PASS|PARTIAL|FAIL`), `checks` (array of
`{id, claim, evidence, holds, status}` with status in `PASS|FAIL|NOT_RUN|BLOCKED`), `caveats`, `unfinished`,
`phase`, `matrix_sha256`, `contract_sha256`, `manifest_sha256` (of the artefacts you hashed), `claim_ceiling`.

`verdict` is `PASS` only if every check you ran holds. If any artefact is missing, `PARTIAL` at best.
Your final message: the verdict, the list of failing check ids, and one sentence on what your separation proves.
