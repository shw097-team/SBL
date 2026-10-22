# EXECUTE brief — restore the `SKILL` kind as a compatibility alias (regression from the eight-kind candidate)

Bounded writer. Change only `sbl_core/m03_routing.py` and `tests/test_kind_matrix.py`. No commits, no dispatch.

## Measured red

```bash
cd C:/Projects/Agent_Workspace/_r152_ev
python -m pytest -q -p no:cacheprovider tests/test_core_modules.py::test_routing_positive_default_policy
```

```
assert routing.route(atom, "SKILL").target == "GJ03_SKILL_AGENT_BRIDGE"
E  sbl_core.errors.SBLError: SBL_E_UNKNOWN_KIND: unknown requirement kind: 'SKILL'
```

The applied eight-kind candidate renamed the canonical kind to `AGENT_SKILL` and dropped `SKILL`. The existing
contract test (and therefore the product's contract with its callers) still routes `SKILL`. The reconciliation must
be additive: keep `AGENT_SKILL` canonical, keep `SKILL` working as a deprecated alias, do not edit the old test.

## Fix

1. In the policy table, add the alias so `SKILL` resolves to the **same target** as `AGENT_SKILL`
   (`GJ03_SKILL_AGENT_BRIDGE`). Mark it deprecated in one comment line, with the reason: callers and the C01/C17
   contract use `SKILL`; the canonical rename is additive.
2. Add one test to `tests/test_kind_matrix.py`:
   `test_skill_is_a_deprecated_alias_of_agent_skill` — asserts both kinds route to the same target and that the
   canonical disposition for `AGENT_SKILL` is still SUPPORTED.
3. Run **only**: `python -m pytest -q -p no:cacheprovider tests/test_core_modules.py tests/test_kind_matrix.py`.
   Both must be green. Do not run the whole suite; the orchestrator owns that run.
4. Write `workers/q1_apply/ALIAS.json`:
   `{"alias": "SKILL -> AGENT_SKILL", "target": "GJ03_SKILL_AGENT_BRIDGE",
     "tests": {"core_modules": {"passed": N}, "kind_matrix": {"passed": N}},
     "old_test_edited": false, "before_sha256": "...", "after_sha256": "...",
     "claim_ceiling": "compatibility alias on the evidence branch; canonical kind unchanged"}`

If the alias cannot be added without touching the old test, write the blocker and stop — do not edit the oracle.
Final message: the two test counts, the alias line you added, and the sha256 pair.
