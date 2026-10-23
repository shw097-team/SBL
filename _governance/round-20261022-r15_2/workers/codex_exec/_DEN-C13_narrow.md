NONCE: DEN_C13-AUTHOR-1792733324

Begin your reply with exactly this token on its own line: DEN_C13-AUTHOR-1792733324

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# EXECUTE brief — C13: FAR standing scope needs no routine HITL and cannot widen itself

Target file: `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c13_standing_scope_no_routine_hitl.py`
Surface to read first, do not modify: `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lane_policy.py`


Write exactly one file. Do not run pytest (the driver runs acceptance). Keep the run under 4 minutes.
No network, no temp files, no fixtures, no writes outside the test process. Do not edit any other file.

Import with `sys.path` insertion of `C:/Projects/Agent_Workspace/HG-KSEOS/src`, or `pytest.importorskip`, so the test works standalone.
If a rule below contradicts the implementation, assert what the code and its docstring actually guarantee and put
the reason in the test docstring. Never weaken an assertion to make a test pass.

## Four tests
1. A lane role resolves to a permission set without asking for human approval: resolve the declared roles for
   PLAN, EXECUTE and VERIFY_SECURITY and assert the resolver returns them without an interactive prompt or an
   "awaiting approval" state.
2. Scope cannot be widened by the caller: request a permission that is not in the role's declared scope and assert
   the call is refused with a typed error (raise or a typed refusal object - match the implementation).
3. The declared scope is finite: the set of permissions for a role equals what the policy file declares, so an
   unknown permission cannot be assumed.
4. Standing scope is stable across repeated resolution: two consecutive resolutions of the same role give the same
   permission set (order-insensitive comparison).
