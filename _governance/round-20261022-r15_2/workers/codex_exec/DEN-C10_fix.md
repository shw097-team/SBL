# EXECUTE brief — repair C10: routing is not authority (small)

File to EDIT: `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_gstack_named_method_route.py`
Surfaces for reference: `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/named_methods.py`, `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lane_policy.py`

## The challenge
The checker ruled that `final_authority=True` inside a returned dict demonstrates no permission boundary, and that no
named-method execution is exercised (KB `SBL_HGK_FABRIC_PIPD_LS_PKG_R15_1_FULL_SUBSTANTIVE_INTEGRATED_REPAIR_REPLACEMENT_2026-10-22.md#285`).

## Add exactly two tests
1. `test_route_decision_is_not_authority`: assert that a route decision alone does NOT grant a permission - i.e. whatever
   the decision carries, an action the role's declared scope does not include must still be refused when resolved
   through `lane_policy`. Call the scope resolver with a permission outside the declared set and assert a typed refusal.
   If no such resolver exists, `xfail(strict=True, reason="R15_1#285 authority boundary absent from the routing surface")`.
2. `test_registry_route_is_deterministic_and_non_empty`: assert `ACTIVE_SELECTED` is non-empty and that two calls give the
   same route for every one of the eight flows (bulk form, one assert with a collected list, not eight tests).

Do not edit any other file, the queue, the receipts or the mandate. Do not run pytest. No network, no fixtures.
Where the product lacks the rule, mark the test `@pytest.mark.xfail(strict=True, reason="<citation> <rule>")` so the
gap stays visible; never weaken an assertion to manufacture green.
