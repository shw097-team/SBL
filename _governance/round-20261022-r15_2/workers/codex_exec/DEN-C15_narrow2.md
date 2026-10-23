# EXECUTE brief — C15 (second attempt, deliberately small)

The previous attempt ran 300 s and wrote nothing. This one writes TWO tests only. Finish fast.

Target file: `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c15_evolution_holdout.py`
Surface to read first (read it, do not modify): `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/evolution.py`

Start your reply with the nonce on its own line, then do the work. Do not run pytest. Do not edit any other file.
No network, no temp files, no fixtures.

## The two tests
1. `test_holdout_is_not_the_tuning_input`: construct the controller the way the module's own docstring or signature
   shows, feed it a tuning input, and assert the holdout set shares no element with that input (set intersection empty).
   If the controller does not expose a holdout attribute, assert instead that the promotion path requires a holdout
   argument and refuse to invent an API - write the test against what exists and say so in the docstring.
2. `test_failed_signal_does_not_promote`: pass a failing EvolutionSignal to the promotion entry point and assert a
   typed error or a refusal object is returned; assert nothing was recorded as promoted on that path.

Import `hg_kseos.evolution` with `sys.path.insert(0, "C:/Projects/Agent_Workspace/HG-KSEOS/src")` and `pytest.importorskip` fallback.
If a rule contradicts the implementation, assert what the code guarantees and explain in the docstring.
