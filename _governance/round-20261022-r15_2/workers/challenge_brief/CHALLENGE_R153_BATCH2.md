# VERIFY_SECURITY brief — independent challenge of four new artefacts

You are the checker. Do not fix anything, do not write product code. Start your reply with the nonce on its own line.
Ground every ruling in the SBL knowledge base and cite `file#line`:
`C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL`

## Artefacts under challenge
1. `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c13_standing_scope_no_routine_hitl.py` (C13)
2. `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c14_checkpoint_resume_no_repeat_effect.py` (C14)
3. `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c15_evolution_holdout.py` (C15)
4. `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_gstack_named_method_route.py` (C10)

## Questions per artefact
Q1 Does each test assert the governing rule, or merely that a function exists / returns a dict? Name the weakest test
   per file and say what a stronger assertion would check.
Q2 Is any test tautological (asserting the mock, or asserting a value it just constructed), or does it use
   `importorskip`/`xfail` to hide a missing product rule? `xfail` without a cited missing rule is a finding.
Q3 Do these four files actually make C13/C14/C15/C10 verifiable, or do they only sample the surface? State the claim
   ceiling each file earns: TOUCHED / PARTIALLY_VERIFIED / VERIFIED, with the reason.
Q4 Does any KB passage require something these tests do not exercise (e.g. DOC-13 ModeGate, ShadowResult five fields,
   independent_checker_ref)? Cite it.

## Output
{"nonce":"<the token>","per_file":[{"file":"...","weakest_test":"...","stronger":"...","findings":["..."],
 "earns":"TOUCHED|PARTIALLY_VERIFIED|VERIFIED","why":"..."}],
 "kb_gaps":[{"citation":"path#line","requirement":"...","unexercised_by":"..."}],
 "verdict":"PASS|FAIL","blocking":["..."],"claim_ceiling":"..."}
