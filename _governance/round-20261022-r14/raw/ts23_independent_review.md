# R14-TS23 independent review — FAIL

**Failed checks: 2 (test sufficiency) and 3 (behavioral RED evidence).** Checks 1, 4 and the bounded repository/package-origin reading of 5 pass.

| Check | Verdict | Finding |
|---|---|---|
| 1 | PASS | All installed launchers worked on reviewer-selected inputs; independent output oracles matched. |
| 2 | FAIL | Shipped tests passed seeded broken implementations, including fixture-constant headings and wrong review byte counts/halt reason. |
| 3 | FAIL | All three captured RED runs stop at missing modules, not failed behavioral output assertions. |
| 4 | PASS | PI/PD input/output schemas validate; both schema deletion negatives and native writeset negative are refused. |
| 5 | PASS, bounded | Source tracked tree unchanged; sandbox additions are visible; installed modules and launcher targets bind to sandbox sources. Venv is not hermetic. |

## Findings and limits

### Check 1 — PASS
- All three installed console launchers ran successfully under the sandbox venv, without PYTHONPATH, on reviewer-selected inputs different from the claim examples.
- Newline input was ts23_newline/__init__.py: 490 bytes, 9 LF bytes, SHA256 fa8134f7298b73d06ff96a372c5771ac5ea92e9bef316d41aea56015d03dfb0a. Independently checked length, per-byte LF tally and digest.
- Heading input was ts23_live_wo_note.md, treated only as input text, not as evidence of the maker claims: expected four headings at lines 1, 5, 17, 30 matched exactly.
- New three-item queue used the CLI source, the skill SKILL.md, and an absent third path: steps=2, remaining=1, halt_reason=BUDGET and both independently recomputed hashes matched. An absent third path was not accessed. One-step, invalid-budget, wrong-JSON-type, missing-input, and empty/exhausted API probes also exercised.
- The .md output path temporarily held only the reviewer-selected JSON queue to honor the two-file write allowlist; its exact input contents are embedded in reviewer_queue_fixture below and it is replaced by this final report.

### Check 2 — FAIL
- Read the complete program Python sources, packaging configuration, skill document and all three tests; all three unmodified shipped tests passed when re-run against the installed sandbox packages. Tests genuinely call program entrypoints and assert output; they are not wholly vacuous. Their single-fixture/partial-oracle coverage nevertheless admits demonstrated broken implementations.
- test_census_and_missing_input compares a separately read file with output and checks a missing input. Its expected byte count/LF count/digest closely mirror the implementation primitives. An in-memory mutation returning BROKEN_EMPTY_FILE bytes for an empty file still passed this test. This is a missing edge-case oracle, not evidence the current implementation mishandles empty files.
- test_heading_inventory_and_bundle has a literal, independent expected result, but for only the One/Two/Three fixture. Replacing inventory with a fixture-constant result for every nonempty inventory (while preserving real missing-input errors) still passed. That mutant produced One/Two/Three for the reviewer document that actually has four different headings. The test cannot distinguish a fixture echo from general heading inventory.
- test_two_step_limit_and_hashes does exercise the default two-step selection, path order, file digests, --max-steps 1 and rejection of 3. It does not assert review byte counts or halt_reason. A mutant emitting bytes=-999 and halt_reason=WRONG still passed the entire test, and its incorrect output was separately captured on the reviewer queue. Empty/exhausted queues, malformed queue contents, and a missing selected input are also absent from this shipped test.
- Mutations were injected only into child-process memory. No program, test, installation or sandbox file was edited. These findings concern regression-test sufficiency, not a claim that the actual installed programs are those mutants.

### Check 3 — FAIL
- There are three captured RED runs in ts23_commands.json, and their bytes match the manifest-bound artefact. Each exits 1 because its subprocess reports No module named ts23_newline / ts23_headings / ts23_review; the enclosing test first fails its return-code assertion. None reaches an assertion comparing incorrect program behavior.
- ts23_build.py lines 118-123 write a test, execute it, explicitly require No module named in stderr, assert the module __init__.py is absent, then write the implementation. Thus missing-module failure is deliberately expected by the build harness, not a surprise or an invented RED. It is still import/implementation-absence RED, not a captured behavioral RED from a loadable implementation.
- A before-code historical run cannot be independently recreated on this immutable sandbox without altering the subject. I inspected the raw captures and build source rather than treating an exit-code pair or the maker summary as proof of behavioral TDD. The narrow claim missing modules failed and later tests passed holds; the stronger behavioral RED->GREEN claim does not.

### Check 4 — PASS
- Independently revalidated PI input/output and PD input/output against the current corresponding PIPD JSON Schemas, including validator_for(schema) and check_schema(schema): all four valid, no errors.
- Deleting acceptance from the actual PI output was refused with required-property error. Deleting RepoContext from the actual PD output was likewise refused. These are in-memory copies; no PI/PD artefact was edited.
- Native build writeset negative control was also independently exercised. outside_scope.py was refused with SBL_E_WRITE_OUTSIDE_WRITESET, and the target did not exist afterward. Read the bridge code first and installed open/makedirs tripwires during the call so a guard regression could not write a prohibited path.
- Initial schema invocation in the sandbox venv failed because jsonschema is not installed there. Retried successfully using the existing HG-KSEOS venv used by the maker; no packages were installed. All three programs and their tests were still executed with the sandbox venv.
- These results prove schema shape and the named controls, not semantic PI completeness or a PIPD compiler execution.

### Check 5 — PASS
- PASS for the precise repository/package-origin checks requested, not for hermetic or historical all-files confinement.
- Source SBL HEAD is 10d510f7b052e6139fd4eb536f970c0245002e17, matching the claim. Tracked diff against HEAD is empty. Its status is not clean: R9 contract plus four compiled-r9 files are untracked. These paths agree with the grouped untracked paths disclosed in the claim, not TS23 program writes.
- Sandbox SBL HEAD is d3c8c2401cb9232f09c1cec825eb66bf2b0931de, matching the claim. Its tracked diff is empty, but ts23_programs, ts23_tests and prior regression_tmp fixtures are untracked. Do not call this sandbox clean. Initial and final complete porcelain outputs are byte-identical for both trees.
- For all three distributions direct_url.json points to the sandbox ts23_programs source directory, imported module __file__ is inside sandbox venv site-packages, all package source/data files compared byte-identical to those installed, console entrypoints target the expected module:main, and each launcher embedded shebang targets the sandbox venv python. All final launcher hashes match the claim. This supports locally built sandbox packages, not accidental execution of a globally installed copy.
- pyvenv.cfg has include-system-site-packages = true and sys.path exposes base-runtime site-packages. Therefore the venv is not hermetic, even though these three packages actually resolve locally. No reinstallation was performed during this read-only review.
- Git cannot prove no historical writes were later reverted, cannot establish the prior contents of ignored/untracked files, and does not vindicate the disclosed initial pip temp escape. Those broader claims remain outside this PASS.

## Exact primary commands and output
All commands ran from `C:/Users/user`; `PYTHONDONTWRITEBYTECODE=1`, `GIT_OPTIONAL_LOCKS=0`, and `PYTHONPATH` removed. Full command argv, additional environment overrides, stdout, stderr and exit codes for every executed probe are embedded under the checks in the JSON report.

The queue input below existed only temporarily in this allowed .md output path; recreating it is necessary before replaying the queue commands:
```json
["C:/Projects/Agent_Workspace/_r14_packet/raw/ts23_sandbox/SBL/ts23_programs/cli/ts23_newline/__init__.py", "C:/Projects/Agent_Workspace/_r14_packet/raw/ts23_sandbox/SBL/ts23_programs/skill/ts23_headings/SKILL.md", "C:/Projects/Agent_Workspace/_r14_packet/raw/ts23_sandbox/independent-deliberately-absent-third-input"]
```

### independent newline launcher
```text
C:\Projects\Agent_Workspace\_r14_packet\raw\ts23_sandbox\venv\Scripts\ts23-newlines.exe C:\Projects\Agent_Workspace\_r14_packet\raw\ts23_sandbox\SBL\ts23_programs\cli\ts23_newline\__init__.py
exit_code=0
stdout:
{"bytes": 490, "newlines": 9, "path": "C:\\Projects\\Agent_Workspace\\_r14_packet\\raw\\ts23_sandbox\\SBL\\ts23_programs\\cli\\ts23_newline\\__init__.py", "sha256": "fa8134f7298b73d06ff96a372c5771ac5ea92e9bef316d41aea56015d03dfb0a"}
stderr:

```

### independent heading launcher
```text
C:\Projects\Agent_Workspace\_r14_packet\raw\ts23_sandbox\venv\Scripts\ts23-headings.exe C:\Projects\Agent_Workspace\_r14_packet\raw\ts23_live_wo_note.md
exit_code=0
stdout:
{"headings": [{"level": 1, "line": 1, "text": "WO-R14-TS23-M2-TRIAD (live spine record) \u2014 what passed, what did not"}, {"level": 2, "line": 5, "text": "What passed (verified by the round orchestrator, not by the subagent's own report)"}, {"level": 2, "line": 17, "text": "Why the verdict is FAIL"}, {"level": 2, "line": 30, "text": "Consequence"}], "path": "C:\\Projects\\Agent_Workspace\\_r14_packet\\raw\\ts23_live_wo_note.md"}
stderr:

```

### independent queue launcher
```text
C:\Projects\Agent_Workspace\_r14_packet\raw\ts23_sandbox\venv\Scripts\ts23-review.exe C:\Projects\Agent_Workspace\_r14_packet\raw\ts23_independent_review.md
exit_code=0
stdout:
{"halt_reason": "BUDGET", "remaining": 1, "reviews": [{"bytes": 490, "path": "C:/Projects/Agent_Workspace/_r14_packet/raw/ts23_sandbox/SBL/ts23_programs/cli/ts23_newline/__init__.py", "sha256": "fa8134f7298b73d06ff96a372c5771ac5ea92e9bef316d41aea56015d03dfb0a"}, {"bytes": 378, "path": "C:/Projects/Agent_Workspace/_r14_packet/raw/ts23_sandbox/SBL/ts23_programs/skill/ts23_headings/SKILL.md", "sha256": "965abcff4174bc77b7751d7b4e0e335170422949af2d7d2cb7159bd43faf9c0a"}], "steps": 2}
stderr:

```

## Residual gaps
- Behavioral RED from a loadable-but-incorrect implementation is not captured; all captured RED runs terminate at missing modules.
- Shipped tests admit the seeded defects described in check 2. The current programs nevertheless passed the reviewer-selected execution cases.
- System-site-packages is enabled; no hermetic-environment assertion is supported.
- Current git state is consistent with the disclosed source status, but retrospective no-write history and original untracked/ignored contents cannot be reconstructed from it.
- Initial pip out-of-root temporary writes and isolated-spine-vs-live-spine divergence were disclosed by the maker; this review neither repeats nor erases them.
- No live-spine update, WO acceptance, repository mutation, general-purpose synthesis, universal novelty, full Markdown semantics, host portability, or broader governance closure was performed or certified.

## Integrity and write scope
Recomputed 14 manifest bindings and 22 program/installed/launcher bindings; all matched. Complete source/test snapshots and schema hashes are in the JSON.
Only the two independent-review output files were written. No sandbox, source repository, installation, PI/PD artefact or spine record was modified. The JSON verdict does not promote or accept the WO.
