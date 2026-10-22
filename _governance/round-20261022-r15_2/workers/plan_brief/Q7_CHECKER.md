# PLAN brief — Q7: is an enforceably distinct checker principal already recognised by existing authority?

You are the PLAN lane. Read-only analysis. Write exactly one output file:
`C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/workers/plan_brief/PLAN_ANSWER_Q7_CHECKER.md`.
Do not modify any other file, do not run git commit, do not dispatch or spawn anything.

## The question

Round R15.2 must decide whether milestone **M1** can claim independent acceptance, or must be recorded as
`LOCAL_REVIEW_ONLY; independent acceptance not established.` The trigger is `SOD006-C6`: the maker and the
checker are currently the same model family on the same host, reached through the same relay. The label
`codex-lane:openai-codex/gpt-6.1-sol` is **not** identity evidence.

PLAN's own earlier ruling (verbatim, in `FAR_DECISIONS_RESIDUAL.md` §Q7) sets the test:

> `CLOSE_NOW_AGENT` **iff** existing authority already recognises an enforceably distinct checker principal;
> else `CLOSE_BY_ONE_OWNER_STEP` or `ACCEPT_AS_CEILING`. Required: distinct maker/checker principals,
> frozen subject/readset, checker write-denial, fresh context, blind Pass A sealed before maker reasoning is
> disclosed, independent raw receipt.

Your job is to answer that "iff" **from the authority documents**, not from preference.

## Read these (path:line citations required in the answer)

- `C:/Projects/Agent_Workspace/HG-KSEOS/AGENTS.md`
- `C:/Projects/Agent_Workspace/HG-KSEOS/config/verify-acceptance-matrix.json`
- `C:/Projects/Agent_Workspace/HG-KSEOS/config/verify-lane-contract.json`
- `C:/Projects/Agent_Workspace/HG-KSEOS/config/lane-routing-registry.yaml` (the `openai_codex` transport section)
- `C:/Projects/Agent_Workspace/HG-KSEOS/config/model-lane-assignment.json` (the declaration that all checker
  slots bind the same checker and "no alternate checker identity or diversity is implied")
- `C:/Projects/Agent_Workspace/HG-KSEOS/.hgk/checker-upgrade-20261009/` (what was actually built: preflight,
  adapter, IAO runner)
- any `SOD006`, `checker`, `independent` clause you can find by searching the Fabric policy tree
  `C:/Projects/Agent_Workspace/Fabric` and `HG-KSEOS/docs`, `HG-KSEOS/control`

## Answer shape (markdown, <= 1200 words)

1. **Verdict** — one of `ENFORCEABLE_SEPARATION_PRESENT` / `SEPARATION_ABSENT` / `UNDETERMINED`, plus the
   disposition this implies for M1 (`CLOSE_NOW_AGENT`, `CLOSE_BY_ONE_OWNER_STEP`, or `ACCEPT_AS_CEILING`).
2. **Condition table** — one row per required condition (distinct principal, frozen subject, write-denial,
   fresh context, blind Pass A, independent raw receipt): `condition | satisfied? | evidence path:line |
   what would have to change`. A condition with no authority clause behind it is `NOT_ESTABLISHED`, not "assumed".
3. **What the existing tooling actually enforces** — for `.hgk/checker-upgrade-20261009/tools/*`: is the
   separation enforced by code (write-denial, separate home, separate principal) or only by convention?
   Quote the mechanism, not the intent.
4. **The single cheapest owner step** that would make separation enforceable, if it is absent — phrased as a
   decision the owner can sign, not as a design you would build.
5. **Ceiling sentence** — the exact one-sentence claim M1 may carry if nothing changes.

Do not recommend building a second machine for appearances. Do not treat a session name as a principal.
