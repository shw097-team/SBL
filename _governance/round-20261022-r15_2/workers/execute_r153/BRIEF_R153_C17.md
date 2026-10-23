# EXECUTE brief — C17: three kinds, real lifecycle (one test file)

You are SBL-EXECUTE, a bounded writer in `C:/Projects/Agent_Workspace/_r152_ev`. Write **exactly one new file** and one receipt, then stop. Do not edit the product, do not touch `_governance/` outside the receipt path, do not dispatch.

## Read these first (read-only)

- `sbl_core/m03_routing.py` — `GovernedRouting.route(atom, kind)`, `DEFAULT_DISPOSITIONS`, the error codes
  `SBL_E_DEFERRED_KIND` / `SBL_E_PROHIBITED_KIND`, and `SpecAtom`'s required fields.
- `sbl_core/m04_bridge.py` — `bind_repo_context(root)`, `GovernedBuildBridge.prepare(ctx, writeset)`,
  `.apply(order, path, content)`, `WriteSet`'s fields, and what `apply` refuses.
- `sbl_sp/bridge.py` — `SkillBridge(manifest_path)` with `discover`, `match`, `effective_load(host)`, `invoke(action,
  provider_on)`, `unload`.
- `sbl_sp/manifests/*.json` — a real manifest to point `SkillBridge` at.
- `tests/test_kind_matrix.py` — the existing 25 tests. Reuse their fixtures and import style; do not duplicate them.

## Write `tests/test_c17_three_kind_lifecycle.py`

Session scope for C17 is three kinds: `CLI_TOOL`, `AGENT_SKILL`, `SIMPLE_AGENT`. Each test name must start with
`test_c17_` and each docstring must say which kind and which verb it exercises.

1. `CLI_TOOL` positive: in a pytest `tmp_path` git repo, `bind_repo_context` -> `prepare` with a writeset that includes the target path -> `apply` writes a file -> assert the file's bytes and that the returned order carries a digest. 
2. `CLI_TOOL` negative: a writeset naming a path outside the repo prefix is refused, and nothing is written.
3. `AGENT_SKILL` positive: `discover` -> `match` on an intent the manifest declares -> `effective_load` with a host dict -> `invoke(action, provider_on=True)` -> `unload`; assert each returns its documented success shape.
4. `AGENT_SKILL` negative: `invoke` with `provider_on=False` is refused, and `unload` before load is refused.
5. `SIMPLE_AGENT` NoFit: `route(atom, "SIMPLE_AGENT")` raises with `SBL_E_DEFERRED_KIND` and constructs no decision.
6. Unknown kind: `route(atom, "NOT_A_KIND")` raises with the prohibited/unknown code.

Rules: no network, no sleeps, no `git commit` (init is fine), nothing written outside `tmp_path`, and every assertion must be satisfiable from the code you read. If the source does not support a clause, write the test to assert the **actual** documented behaviour and record the deviation in the receipt — do not weaken an assertion to fit a guess.

## Write `workers/execute_r153/EXECUTE_RECEIPT_C17.json`

`{"schema":"SBL_EXECUTE_RECEIPT/2","item":"C17","files":[...],"clauses":[{"clause":"...","line":NN,"source":"file:line"}],"deviations":[...],"not_done":[...],"claim_ceiling":"a written test proves nothing until it runs; the orchestrator runs it"}`
