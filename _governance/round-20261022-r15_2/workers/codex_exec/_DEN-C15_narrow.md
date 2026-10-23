NONCE: DEN_C15-AUTHOR-1792733711

Begin your reply with exactly this token on its own line: DEN_C15-AUTHOR-1792733711

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# EXECUTE brief — C15: evolution needs a sandbox, an independent holdout, and a lawful promotion

Target file: `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c15_evolution_sandbox_holdout_promotion.py`
Surface to read first, do not modify: `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/evolution.py`


Write exactly one file. Do not run pytest (the driver runs acceptance). Keep the run under 4 minutes.
No network, no temp files, no fixtures, no writes outside the test process. Do not edit any other file.

Import with `sys.path` insertion of `C:/Projects/Agent_Workspace/HG-KSEOS/src`, or `pytest.importorskip`, so the test works standalone.
If a rule below contradicts the implementation, assert what the code and its docstring actually guarantee and put
the reason in the test docstring. Never weaken an assertion to make a test pass.

## Four tests
1. There is a sandbox boundary: read `GovernedEvolutionController` and assert that a candidate is evaluated in a
   sandbox/staging state before any promotion - the promotion entry point must not be reachable without it.
2. The holdout is independent: assert the holdout set is not derived from the training/tuning input the controller
   was given (no overlap by identity).
3. Promotion requires a passing signal: a failing `EvolutionSignal` does not promote (assert a typed error or a
   refusal, matching the implementation).
4. A lawful promotion is recorded: on success the controller returns or records the evidence needed to replay the
   decision (signal, holdout result, promoting actor) - assert those keys exist.
