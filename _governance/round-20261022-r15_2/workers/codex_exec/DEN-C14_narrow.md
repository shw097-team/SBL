# EXECUTE brief — C14: a checkpoint resume must not repeat a world effect

Target file: `C:/Projects/Agent_Workspace/HG-KSEOS/tests/test_c14_checkpoint_resume_no_repeat_effect.py`
Surface to read first, do not modify: `C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/recovery.py`


Write exactly one file. Do not run pytest (the driver runs acceptance). Keep the run under 4 minutes.
No network, no temp files, no fixtures, no writes outside the test process. Do not edit any other file.

Import with `sys.path` insertion of `C:/Projects/Agent_Workspace/HG-KSEOS/src`, or `pytest.importorskip`, so the test works standalone.
If a rule below contradicts the implementation, assert what the code and its docstring actually guarantee and put
the reason in the test docstring. Never weaken an assertion to make a test pass.

`recovery.backup_database(database: Path, backup_root: Path)` returns a dict of hashes;
`recovery.restore_database(backup: Path, expected_sha256: str, restore_target: Path)` verifies the digest before writing.

## Four tests
1. A backup produces a digest that a restore accepts.
2. Restoring the same verified backup twice leaves the target file's bytes identical after the second restore
   (no accumulating effect) - assert sha256 before and after.
3. A resume with a mismatched expected digest is refused and the target is left untouched (compare bytes).
4. A resume after an interrupted restore (target missing, backup intact) reproduces exactly the backup bytes.
