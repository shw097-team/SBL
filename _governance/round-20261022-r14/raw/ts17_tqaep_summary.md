# TS17 — measured applicability projection; qualification HOLD

## Dimension correction
DOC-08/C39 explicitly defines **12 TestClass × 8 OracleType**, NOT 12 × 8 skills (lines 356, 360–386). Twelve = POS, NEG, EDGE, SEC, PERF, PARITY, RECOVERY, UPGRADE, ROLLBACK, UNINSTALL, MUT, JOURNEY. Eight official skills are separately named in DOC-08 SkillRouteReadback lines 46–59 and R14-TS13. R14-TS17/CHK17 says 12×8 without redefining those axes. Thus the requested skills matrix is an **additional reviewer projection**, not the normative 96-cell oracle matrix. The order does not legally establish a different eight-axis; Owner clarification is required. Original oracle cells are preserved in ts17_normative_oracle_cells.json.

All skill cells are conservatively APPLICABLE **conditional obligations**, not assertions that each class predicate is currently true. Source predicates are carried verbatim per cell. No Owner-signed false predicate/exclusion supplied; UNKNOWN cannot become NOT_APPLICABLE. No invented legal NA. This is a planning applicability matrix, NOT Native qualification or Owner-ratified applicability.

## Measured denominators
{
  "rows": 96,
  "applicable_conditional": 96,
  "not_applicable": 0,
  "existing_case_exercised_cells_schema_only": 32,
  "asserted_not_exercised_cells": 64,
  "existing_cases_schema_run": 56,
  "schema_expectation_matches": 54,
  "runtime_covered_cells": 0
}

Existing cases were actually fed to their original input/output Draft202012 schemas, not inferred from SKILL.md presence. POS/NEG/EDGE/SEC exercise typed shapes only; fixture output is not produced by a skill invocation. No semantic distinct-principal validator was added to conceal schema gaps. Other eight class rows per skill are asserted obligations only. Runtime/Host lifecycle/consumer/no-effect coverage is zero. Rows retain failures rather than labelling all exercised cells PASS.

## Schema disagreements (measured, not fixed)
- pipd-assurance-tqaep/NEG-001: expect REFUSE, schema_refused=False; maker aliased as checker fails the SoD rule (TQ_SOD) even though the shape is valid
- pipd-package-project/NEG-001: expect REFUSE, schema_refused=False; LOCAL_QUALIFIED without a bound approval receipt and checker identity is refused

The intake's known “2 of 4 TQAEP REFUSE cases not schema-enforced” is **not reproduced with both input AND output schemas**: this run finds only TQAEP NEG-001 accepted. SEC-001 has a valid input but its injected output is refused by output.const (distinct=false). Input-only validation would miss that downstream security case as well. This run does not claim either schema validates real checker independence or receipt authenticity.

## Qualification still missing
- Per-atom objective/strictness comes from C22 source-to-user predicate and C39 class objective; no fabricated SLO or loss function. Existing POS/NEG/ADV coverage is separately listed, including NONE.
- Native Oracle Owner PIPD DOC07 / CR-ORACLE-001 remains required (C40); reviewer projection cannot issue TEST/OR or override ALL.
- Holdout dataset pins, false-positive/negative rates, calibrated LLM-judge rubric and model pin, randomized/counterbalanced candidate ordering, judge disagreement/human veto and reproducible seed have **not been measured**. No numeric claim.
- C42.1 requires distinct principal_uuid/credential/ACL/signing/frozen readset, not a role name; this schema-only run is not a signed independent checker receipt.

Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 python C:/Projects/Agent_Workspace/_r14_packet/raw/ts17_ts18_measure.py`
Exit 0 means evidence script completed, NOT qualification PASS. Detailed raw per-case schema errors and source hashes: ts17_case_schema_results.json. DOC bytes and UTF-8 integrity: ts18_sources_and_anchors.json. All CJK decoded strictly; no encoding error. Subject is file-SHA pinned, not commit-pinned: git prohibited by delegated scope.
