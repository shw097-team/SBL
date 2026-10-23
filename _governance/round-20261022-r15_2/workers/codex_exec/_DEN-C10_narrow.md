NONCE: EXEC-C10N-131940

Begin your reply with exactly this token on its own line: EXEC-C10N-131940

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# EXECUTE brief — C10 GSTACK named-method route, one narrow artefact

Write exactly one file. Do not run pytest (the driver does acceptance). Keep the whole run under 4 minutes.

## Target file (create it)
`C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_gstack_named_method_route.py`

## The surface you are testing (already implemented, read it first, do not change it)
`C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/named_methods.py`

It exposes: `ACTIVE_SELECTED` (a set of route names), `route(flow: str)` returning a decision with a
`selected_route` plus a reason/state, `registry_snapshot()`, and `evaluate_activation_invariants()`.
The GSTACK rule is that route() is a registry lookup, so every flow - including an unknown one - must return a
decision; `NATIVE` is itself a valid disposition and must never be read as "no execution surface".

## Rules the tests must assert (four tests, no more)
1. Totality: for each of 8 flows - plan, implementation done, qa, security, brownfield migration, release
   readiness, retro, "checker adapter unknown flow" - `route(f)` returns a decision dict carrying `selected_route`.
2. Determinism: `route("security")` twice in a row yields the same `selected_route`.
3. Registry not empty and stable: `ACTIVE_SELECTED` is non-empty and `registry_snapshot()` contains every name in it.
4. No fail-open: an unknown flow must not raise; it must return a decision (assert type and that a state/reason key
   is present if the implementation provides one - read the code rather than guessing the key name).

## Constraints
- Import as `from hg_kseos import named_methods as nm` and make the test skip cleanly if the import fails, with
  `pytest.importorskip`, because the package needs `HG-KSEOS/src` on the path.
- No network, no temp files, no fixtures, no `tmp_path`, no writes outside the test process.
- Do not edit any other file, the queue, the receipts, or the mandate.
- If a rule above contradicts the implementation, assert what the implementation and its docstring actually
  guarantee and put the reason in the test docstring. Never weaken a test to make it pass.
