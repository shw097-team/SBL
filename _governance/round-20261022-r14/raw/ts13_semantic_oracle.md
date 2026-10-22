# TS13 — HG-KSEOS semantic oracle

## Outcome

Both original NEG-001 inputs are accepted by their PIPD input schemas and refused by the HG-KSEOS oracle (VIOLATED). Neither negative case supplies an output; no output was invented.

## Source-authoritative case text (verbatim)

### pipd-assurance-tqaep/tests/cases.yaml

```yaml
- id: NEG-001
  kind: NEG
  expect: REFUSE
  first_fail: semantic.distinct
  rationale: maker aliased as checker fails the SoD rule (TQ_SOD) even though the shape is valid
  input:
    pi: *id001
    ecp: *id002
    maker: Maker-A
    checker: ' maker-a '
    checker_execution_receipt: receipt://chk-2026-10-09/a17f
  route:
    utterance: Remind me to water the plants at 6pm
    expect: NO_ROUTE
  semantic:
    rule: distinct
    fields:
    - maker
    - checker
```

### pipd-package-project/tests/cases.yaml

```yaml
- id: NEG-001
  kind: NEG
  expect: REFUSE
  first_fail: semantic.claim_gate
  rationale: LOCAL_QUALIFIED without a bound approval receipt and checker identity is refused
  input:
    bundle: *id001
    allowed_claims:
    - LOCAL_QUALIFIED
    producer: PIPD-EC
  route:
    utterance: Water my plants while I am away
    expect: NO_ROUTE
  semantic:
    rule: claim_gate
```

YAML aliases above are preserved verbatim; the JSON results include fully resolved source payloads.

## Inferred predicates and boundaries

- **semantic.distinct:** Maker/checker separation of duties: reject equal casefolded identities after removing whitespace, including supplied output acceptance pairs. Not a generic novelty/reordered-items test.
- **semantic.claim_gate:** LOCAL_QUALIFIED and all higher rungs requested or emitted require input approval.checker_identity and approval.approval_receipt as nonblank strings; checker must not alias producer. Below threshold is NOT_APPLICABLE. Output evidence expectations cannot substitute for approval.

The distinct case names `fields: [maker, checker]`; it does not specify novel entities in an output list. Implementing generic output novelty would be an unsupported reinterpretation. Assurance SKILL.md rules 1–2 and contract TQ_SOD corroborate identity separation. Whitespace removal includes internal whitespace per the contract's whitespace-insensitive rule; the actual case demonstrates leading/trailing whitespace and case aliasing.

Package NEG-001 explicitly includes LOCAL_QUALIFIED in the gate. Package SKILL.md rule 4 and Typed IO confirm 'LOCAL_QUALIFIED and above'; this resolves the reference failure section's imprecise 'above LOCAL_QUALIFIED' wording. Bound receipt authenticity and hash binding cannot be inferred from a URI string and are not claimed.

Schema validation precedes these bounded checks. Unknown claim rungs, malformed structures and unrelated trace/receipt rules remain with schemas or other validators. NOT_APPLICABLE must not be treated as global acceptance.

## Source fixture executions

| Predicate | Skill / case | Input schema | Output schema | Oracle |
|---|---|---|---|---|
| semantic.distinct | pipd-assurance-tqaep / POS-001 | ACCEPT | ACCEPT | SATISFIED |
| semantic.distinct | pipd-assurance-tqaep / NEG-001 | ACCEPT | NOT_PROVIDED | VIOLATED |
| semantic.distinct | pipd-package-project / POS-001 | ACCEPT | ACCEPT | NOT_APPLICABLE |
| semantic.claim_gate | pipd-package-project / POS-001 | ACCEPT | ACCEPT | SATISFIED |
| semantic.claim_gate | pipd-package-project / NEG-001 | ACCEPT | NOT_PROVIDED | VIOLATED |
| semantic.claim_gate | pipd-package-project / POS-002 | ACCEPT | ACCEPT | NOT_APPLICABLE |

## Tests

TDD: distinct first failed 3 tests for the absent module, then passed 3; claim_gate first failed 3 tests for the absent function with the distinct 3 still passing, then passed 6. Final focused tests also cover nonblank evidence, all five gated emitted claims, self-approval, blank identities and the source SEC-001 downstream alias. Supplemental mutations are labeled and do not replace either actual NEG-001 fixture.

### Focused

Exit code: `0`; timeout: `False`.

```text
.........................                                                [100%]
25 passed in 0.70s

```

### Full suite (initial run; --diagnose reuses its saved log)

Exit code: `None`; timeout: `True`.

```text
[w3_solution] REPO_ROOT=C:\Projects\Agent_Workspace\HG-KSEOS
[w3_solution] SCRIPTS=C:\Projects\Agent_Workspace\HG-KSEOS\scripts
[w3_solution] FIXTURES=C:\Projects\Agent_Workspace\HG-KSEOS\tests\w3_solution\fixtures
........................................................................ [ 11%]
....F................................................................... [ 22%]
........................................................................ [ 33%]
........................................................................ [ 45%]
........................................................................ [ 56%]
...................................................... [ 64%]
...................s.................................................... [ 76%]
........................................................................ [ 87%]
........................................F.........................F.FF.. [ 98%]
.....

```

### First-failure diagnostic

Exit code: `1`; timeout: `False`.

```text
[w3_solution] REPO_ROOT=C:\Projects\Agent_Workspace\HG-KSEOS
[w3_solution] SCRIPTS=C:\Projects\Agent_Workspace\HG-KSEOS\scripts
[w3_solution] FIXTURES=C:\Projects\Agent_Workspace\HG-KSEOS\tests\w3_solution\fixtures
........................................................................ [ 11%]
....F
================================== FAILURES ===================================
_____________ CaseRunCliTests.test_r4_only_allowed_files_changed ______________

self = <tests.test_c2_case_run.CaseRunCliTests testMethod=test_r4_only_allowed_files_changed>

    def test_r4_only_allowed_files_changed(self) -> None:
        porcelain = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        changed: set[str] = set()
        for line in porcelain.splitlines():
            if line.strip():
                changed.add(line[3:].strip())
        unexpected = changed - ALLOWED_CHANGED_FILES - PRE_EXISTING_UNTRACKED
>       self.assertEqual(set(), unexpected)
E       AssertionError: Items in the second set but not the first:
E       'tests/ts13_semantic_tmp/'
E       'tests/test_semantic_oracle.py'
E       'src/hg_kseos/semantic_oracle.py'
E       'tests/test_lane_scope_isolation.py'
E       'scripts/lane_scope_isolation.py'
E       'config/lane_scope_exceptions.json'

tests\test_c2_case_run.py:148: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_c2_case_run.py::CaseRunCliTests::test_r4_only_allowed_files_changed
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 76 passed in 18.16s

```

## Verification limitations

The initial full-suite run exceeded its 180-second limit after displaying failures; it is not a full-suite pass. The first-failure diagnostic identifies test_c2_case_run.py::CaseRunCliTests::test_r4_only_allowed_files_changed, an existing repository-status allowlist assertion that rejects the newly requested oracle/test files (and reports other workspace paths). That assertion was not edited. Remaining initial-run failures were not diagnosed, and no baseline-green claim is made.

## Claim ceiling

HG-KSEOS-side opt-in callable semantic oracle only. PIPD remains authoritative over its own contracts and schemas; no PIPD files or schemas were changed. No existing HG-KSEOS runtime entry point was rewired, so callers must invoke these checks and refuse on VIOLATED. SATISFIED establishes only the bounded predicate, not full artifact validity, receipt authenticity, cryptographic candidate binding, or real-world checker independence.

Source SHA-256 fingerprints before and after verification match for both skills' case files, SKILL.md, contracts and input/output schemas. See ts13_semantic_results.json for hashes, resolved payloads and complete oracle evidence; ts13_semantic_capture.py reproduces this report. Only new implementation/tests and ts13_semantic_* evidence artifacts were authored; no config edits or push were performed.
