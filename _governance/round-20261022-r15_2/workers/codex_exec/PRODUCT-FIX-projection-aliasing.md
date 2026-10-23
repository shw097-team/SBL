# EXECUTE brief — make the policy projection hand out copies, not aliases (one-line class of fix)

Product file to EDIT: `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lane_policy.py`
Keep the run under 3 minutes. No other file. Do not touch tests.

## The reproduced defect
`_compact_route()` (around line 165) copies the `fallbacks` LIST but not its ELEMENT dicts:

    "fallbacks": list(route.get("fallbacks", [])),

`arms` right below it already uses `copy.deepcopy`. Because the fallback dicts are shared with the registry, a caller
that mutates one projection writes straight into the registry, and every other projection resolved from it changes too.
Reproduction (now a failing test in `tests/test_c13_standing_scope_no_routine_hitl.py:419`): mutate one projection's
`fallbacks[i]["provider"]`, then a separately resolved projection reports `('attacker-provider','attacker-model')`
instead of the five declared fallbacks.

## The change
1. Make `fallbacks` a deep copy exactly like `arms`: `copy.deepcopy(list(route.get("fallbacks", [])))`.
2. Audit the rest of `_compact_route` for the same class of aliasing (any mutable container returned by reference) and
   deep-copy it too. Nested values that are immutable (str/int/bool/None) must be left alone - do not deep-copy the
   whole route dict blindly if that would change the document's shape.
3. Leave the projection's keys, ordering and schema untouched.

## Done means
`python -m pytest C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c13_standing_scope_no_routine_hitl.py -q` (run from
`C:/Projects/Agent_Workspace/HG-KSEOS` with `PYTHONPATH=C:/Projects/Agent_Workspace/HG-KSEOS/src`) passes, including
`test_standing_scope_is_stable_across_repeated_resolution`. You MAY run that one command to check; report its real
output. Do not weaken the test.
