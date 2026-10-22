# R14-TS14 — Source-bound guided PI/PD proposal

**Result:** original PIPD input schema validates; Native PI/PD not issued. No human internal-field entry or follow-up was required. This is an agent-authored test, not proof of an installed TPM Host UX.

## New plain-language need

> Before I archive a release handoff folder, show me which acceptance checks would lose their only evidence file if I removed it.

Agent-selected hypothetical utterance; no claim that a real human volunteered this sentence. It is frozen as `AGENT-SELECTED-UTTERANCE/1@sha256:ddcdbaf82b9b2b85fe4c6dd03ae05ab4857cbea4389dc597fac8574773c49a3a` and preserved above and in JSON.

## Non-prefabricated evidence

```json
{
  "root": "C:\\Projects\\Agent_Workspace\\PIPD",
  "excluded_directories": [
    ".git",
    ".hgk",
    ".venv",
    "__pycache__",
    "node_modules"
  ],
  "readable_utf8_files": 8954,
  "skipped_count": 4373,
  "queries": {
    "Before I archive a release handoff folder, show me which acceptance checks would lose their only evidence file if I removed it.": [],
    "Before I archive a release handoff folder": [],
    "only evidence file": [],
    "handoff folder": [],
    "evidence-loss-preview": [],
    "evidence loss": []
  },
  "reason": "New counterfactual archive/removal impact preview for release-evidence consumers, not the existing PI compilation fixtures. No matching utterance or searched feature phrases in the readable product tree. Generic trace/orphan checks are reused constraints, not evidence that this product requirement already exists.",
  "limit": "Lexical evidence in PIPD only; not a proof of semantic novelty across all repos or binary/generated files. Initial unrestricted traversal failed on .hgk/.../lib64 (WinError 1920); recovered by excluding generated .hgk and other listed directories."
}
```

## Source ledger and exact section basis

| Source | SHA-256 | Sections actually read |
|---|---|---|
| DOC-01 | `43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f` | C05.1/U05-U13 L768-L786; C05.2/U06.1-U06.4 L849-L852; C05.4 L1003-L1007; C08.1-C08.2 L1098-L1119; C08.2B-C08.3 L1148-L1171; R09.3-R09.4 L2458-L2465; R09.6 L2688-L2695 |
| DOC-02 | `4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035` | r2 shared FirstFail rules L74-L86; C17.3 L1739-L1749; R02-04.1 L4633-L4653; R02-04.3 L4951-L4963; ChangeImpactGraph/ADR/Rollback & No-effect L10648-L10679; Eight PIPD P4 Skills Typed IO L10790-L10803 |

Round order: §6.2 R14-TS14 L156 requires JTBD/FUO/GoalCard/Decision, source-bound PI/PD, ADR/NFR, atomic ACC/NEG without manual internal contracts; §8.1 R14-CHK14 L224 requires a new source-bound need and no fabricated source. Order SHA: `6fa44f5570032acd767942a922ff256995bdc287531084f3183cc54e410e12ce`.

TPM skill steps used: clarify intent; keep source ledger; bounded handoff; route, do not build. Skill path/hash and all source paths/full cited spans are in JSON `sources`.

**Definition limits:** JTBD/FUO and MVP/Non-goals: DOC-01/C05.1 U05 and C08.1/C08.3. NFR/architecture/ADR responsibility: DOC-01/C05.1 U06 and C05.2 U06.1–U06.4 (these do not prescribe a complete NFR object schema). Decision provenance and pending ratification: DOC-01/C05.1 U11 and R09.6. ADR examples: DOC-02/ChangeImpactGraph/ADR/Rollback & No-effect (an unnumbered real heading; no invented C section). Atomicity/trace: DOC-01/C05.4, DOC-02/R02-04.1 and R02-04.3. Per-child negatives: DOC-01/R09.4 and C05.2. **GoalCard not specified in DOC-01; GoalCard not specified in DOC-02** (full-file literal hit counts both zero). GoalCard below is a local summary, not a Native DOC schema.

## Proposal / bounded handoff

Every value below is a proposed design or an explicitly unresolved prerequisite, not a fabricated authority receipt. Normative product obligations are indexed to the five canonical atoms; JSON ACC/NEG records also carry source_clause, owner, acceptance_cue and risk_guard.

```json
{
  "jtbd": {
    "value": "When preparing to archive release handoff material, a maintainer wants to identify acceptance checks that would lose their sole usable evidence so they can preserve it before removal.",
    "source_clause": "AGENT-SELECTED-UTTERANCE/1@sha256:ddcdbaf82b9b2b85fe4c6dd03ae05ab4857cbea4389dc597fac8574773c49a3a; DOC-01/C08.1:L1098-L1109@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
    "atom_indices": [
      0,
      1,
      2
    ]
  },
  "fuo": {
    "value": "Given a local acceptance-to-evidence mapping and proposed folder, receive a report that distinguishes sole-evidence loss, retained alternatives and unresolved evidence, with source files unchanged.",
    "source_clause": "DOC-01/C08.3:L1169-L1171@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
    "atom_indices": [
      0,
      1,
      2,
      3,
      4
    ],
    "command": "PROPOSED: evidence-loss-preview --mapping <local-mapping> --remove-folder <folder>",
    "host": "Local CLI; proposed, not installed",
    "environment": "Read-only approved local input mapping and evidence roots; no network",
    "input": "Candidate digest, check ids, evidence locators/digests, proposed folder",
    "stdout_schema": "Rows: check_id, classification, evidence_locators; textual status NO_CHECKS for empty input",
    "exit_checker": "Proposed: 0 for fully resolved report, 2 when any UNKNOWN or NO_CHECKS; product owner ratification pending",
    "negative": "ACC/NEG pair list below",
    "expected_raw_receipt_locator": "Future isolated checker output: input digests, stdout, exit, before/after evidence digests; not present",
    "observed_raw_receipt": "NOT_EXECUTED"
  },
  "goalcard": {
    "goal": "Preview which acceptance checks lose their only usable evidence under a proposed release-handoff folder removal, without changing files.",
    "persona": "Release handoff maintainer",
    "mvp": "Read-only counterfactual evidence-loss report for a supplied local mapping",
    "success": "Each check classified by usable retained evidence, unresolved entries explicit, no source bytes changed",
    "source_clause": "AGENT-SELECTED-UTTERANCE/1@sha256:ddcdbaf82b9b2b85fe4c6dd03ae05ab4857cbea4389dc597fac8574773c49a3a; DOC-01/C08.1:L1098-L1109@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
    "status": "LOCAL_SUMMARY_NOT_CANONICAL_GOALCARD",
    "definition_limit": "GoalCard not specified in DOC-01; GoalCard not specified in DOC-02 (literal full-file scans both zero). This local summary shape is agent-proposed, not a cited DOC schema."
  },
  "decisions": [
    {
      "id": "DEC-TS14-01",
      "status": "PROPOSED_OWNER_RATIFICATION_REQUIRED",
      "decision": "Keep the first useful slice read-only and accept an explicit local mapping; do not discover or delete release assets automatically.",
      "alternatives": "Automatic archive operation rejected because the seed asks for a preview, not permission for effects.",
      "consequence": "Mapping completeness remains explicit; no claim that all acceptance checks in the world are known.",
      "source_clause": "DOC-01/C05.1/U11:L784@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f; DOC-01/R09.6:L2688-L2695@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
      "atom_indices": [
        3,
        4
      ]
    },
    {
      "id": "ADR-TS14-01",
      "status": "PROPOSED_OWNER_RATIFICATION_REQUIRED",
      "decision": "Use candidate-bound evidence locators and digest-checked local resolution, then evaluate a counterfactual folder-removal predicate per check.",
      "alternatives": "Filename-only matching rejected because stale/foreign files could falsely appear to preserve evidence.",
      "consequence": "Missing or stale identity yields UNKNOWN; no automatic release gate override.",
      "source_clause": "DOC-01/C05.2/U06.4:L852@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f; DOC-02/ChangeImpactGraph/ADR/Rollback & No-effect:L10648-L10679@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035",
      "atom_indices": [
        0,
        1,
        2
      ]
    }
  ],
  "nfr": [
    {
      "id": "NFR-TS14-01",
      "value": "No source/evidence mutations: compare before/after byte digests.",
      "source_clause": "DOC-01/C05.2/U06.2:L850@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f; DOC-01/C05.4:L1003-L1007@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
      "atom_index": 4
    },
    {
      "id": "NFR-TS14-02",
      "value": "Coverage integrity: each input check id appears once, including UNKNOWN; classifications and provenance readable without color.",
      "source_clause": "DOC-01/C05.2/U06.2:L850@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f; DOC-01/C08.1.1:L1112-L1114@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
      "atom_index": 3
    }
  ],
  "pd_proposal": {
    "status": "HOLD_UNBOUND_DESIGN_ONLY",
    "domain": "AcceptanceCheck -> candidate-bound EvidenceFile; ProposedRemovalFolder is a what-if input, not an authorized action",
    "proposed_components": "Local mapping reader -> identity/path resolver -> per-check classifier -> plain-text report",
    "repo_context": null,
    "bound_pi_reference": null,
    "future_write_scope": "UNVERIFIED: implementation/test paths require target-repo discovery and separate Native WorkOrder; no write path authorized here",
    "binding_gate": "PIPD PD Owner must supply real root/head/tracked_files/currentness/writable_scope from discovery and compiled PI ref. Do not fabricate HEAD or PI-PKG identity.",
    "source_clause": "DOC-02/C17.3:L1739-L1749@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035; DOC-02/Eight PIPD P4 Skills Typed IO:L10790-L10803@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035"
  },
  "handoff": {
    "goal": "Preview which acceptance checks lose their only usable evidence under a proposed release-handoff folder removal, without changing files.",
    "non_goals": [
      "Actually archive/delete files",
      "Approve a release or mint PI/PD/ECP/Permit",
      "Infer completeness from missing or stale evidence"
    ],
    "assumptions": [
      "Agent selected this hypothetical user need as requested; it is not a recorded human product interview.",
      "STANDARD is an agent-proposed profile value, not an effective Native ProfileBinding.",
      "Local mapping and candidate digest are future runtime inputs; none fabricated here."
    ],
    "acceptance": "acc_neg_pairs: one positive and one discriminating negative for each atom index",
    "open_questions": [
      "Product owner must ratify this proposed MVP, command and exit policy before implementation.",
      "Target product repo and mapping format are not yet selected; discovery and Native PD admission remain required.",
      "CR-ORACLE-001 remains an upstream authority gap; JSON Schema success cannot close it."
    ],
    "sources": [
      "AGENT-SELECTED-UTTERANCE/1@sha256:ddcdbaf82b9b2b85fe4c6dd03ae05ab4857cbea4389dc597fac8574773c49a3a",
      "AGENT-SELECTED-UTTERANCE/1@sha256:ddcdbaf82b9b2b85fe4c6dd03ae05ab4857cbea4389dc597fac8574773c49a3a; DOC-01/C08.1:L1098-L1109@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
      "DOC-02/C17.3:L1739-L1749@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035; DOC-02/Eight PIPD P4 Skills Typed IO:L10790-L10803@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035"
    ],
    "exact_current_write_scope": [
      "C:/Projects/Agent_Workspace/_r14_packet/raw/ts14_*"
    ],
    "next": "Route proposal to PIPD Source/Profile/PI Writer, then PD Owner; do not execute product changes."
  }
}
```

## Requirement atoms

`owner=PIPD-EC` is required by the original schema, not proof of PIPD invocation. req_id is a category enum; stable per-test IDs are in the paired acceptance list.

```json
[
  {
    "req_id": "REQ-INTENT",
    "source_clause": "AGENT-SELECTED-UTTERANCE/1@sha256:ddcdbaf82b9b2b85fe4c6dd03ae05ab4857cbea4389dc597fac8574773c49a3a; DOC-01/C08.1:L1098-L1109@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
    "owner": "PIPD-EC",
    "acceptance_cue": "For each acceptance check with resolvable evidence references, classify WOULD_LOSE_ONLY_EVIDENCE exactly when every usable evidence file for that check is inside the proposed removal folder.",
    "risk_guard": "A counterfactual classification never authorizes deletion or declares a release safe."
  },
  {
    "req_id": "REQ-KNOWLEDGE",
    "source_clause": "AGENT-SELECTED-UTTERANCE/1@sha256:ddcdbaf82b9b2b85fe4c6dd03ae05ab4857cbea4389dc597fac8574773c49a3a; DOC-02/R02-04.3:L4951-L4963@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035",
    "owner": "PIPD-EC",
    "acceptance_cue": "For a check with at least one usable evidence file outside the proposed folder, classify RETAINS_EVIDENCE.",
    "risk_guard": "Count only resolvable evidence bound to that check and the same candidate digest; unrelated or stale files are not alternatives."
  },
  {
    "req_id": "REQ-VERIFY",
    "source_clause": "DOC-02/R02-04.3:L4951-L4963@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035; DOC-02/R02-04.1:L4633-L4653@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035",
    "owner": "PIPD-EC",
    "acceptance_cue": "For a check whose evidence reference cannot be resolved or candidate identity cannot be verified, classify UNKNOWN.",
    "risk_guard": "Never convert unresolved evidence into RETAINS_EVIDENCE or claim complete coverage."
  },
  {
    "req_id": "REQ-DELIVER",
    "source_clause": "AGENT-SELECTED-UTTERANCE/1@sha256:ddcdbaf82b9b2b85fe4c6dd03ae05ab4857cbea4389dc597fac8574773c49a3a; DOC-01/C08.1.1:L1112-L1114@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
    "owner": "PIPD-EC",
    "acceptance_cue": "Emit a plain-text-readable report row for every input acceptance-check id, including its classification and the evidence locators used for that classification.",
    "risk_guard": "Do not omit UNKNOWN rows; a zero-input report must explicitly state NO_CHECKS rather than imply release acceptance."
  },
  {
    "req_id": "REQ-GOVERN",
    "source_clause": "DOC-01/C05.4:L1003-L1007@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f; DOC-02/C17.3:L1739-L1749@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035; DOC-02/Eight PIPD P4 Skills Typed IO:L10790-L10803@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035",
    "owner": "PIPD-EC",
    "acceptance_cue": "The preview leaves the proposed removal folder and all referenced evidence files byte-identical.",
    "risk_guard": "No delete/archive/write to source or evidence, no release promotion, no external upload; product implementation requires separate authority."
  }
]
```

## Atomic ACC/NEG pairs — expected, product tests NOT EXECUTED

```json
[
  {
    "atom_index": 0,
    "req_id": "REQ-INTENT",
    "acc_id": "ACC-TS14-01",
    "neg_id": "NEG-TS14-01",
    "positive": "Given check C1 references one verified candidate-bound file inside folder F; when preview F; then C1=WOULD_LOSE_ONLY_EVIDENCE.",
    "negative": "Given the same C1 but add one verified candidate-bound file outside F; when preview F; then C1 must not be WOULD_LOSE_ONLY_EVIDENCE.",
    "source_clause": "AGENT-SELECTED-UTTERANCE/1@sha256:ddcdbaf82b9b2b85fe4c6dd03ae05ab4857cbea4389dc597fac8574773c49a3a; DOC-01/C08.1:L1098-L1109@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
    "owner": "PIPD-EC",
    "acceptance_cue": "For each acceptance check with resolvable evidence references, classify WOULD_LOSE_ONLY_EVIDENCE exactly when every usable evidence file for that check is inside the proposed removal folder.",
    "risk_guard": "A counterfactual classification never authorizes deletion or declares a release safe.",
    "observed": "NOT_EXECUTED_PRODUCT_TEST_DESIGN_ONLY"
  },
  {
    "atom_index": 1,
    "req_id": "REQ-KNOWLEDGE",
    "acc_id": "ACC-TS14-02",
    "neg_id": "NEG-TS14-02",
    "positive": "Given C2 has one verified candidate-bound file outside F; when preview F; then C2=RETAINS_EVIDENCE.",
    "negative": "Given C2 outside-file reference has a foreign candidate digest; when preview F; then it must not be counted as usable retained evidence.",
    "source_clause": "AGENT-SELECTED-UTTERANCE/1@sha256:ddcdbaf82b9b2b85fe4c6dd03ae05ab4857cbea4389dc597fac8574773c49a3a; DOC-02/R02-04.3:L4951-L4963@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035",
    "owner": "PIPD-EC",
    "acceptance_cue": "For a check with at least one usable evidence file outside the proposed folder, classify RETAINS_EVIDENCE.",
    "risk_guard": "Count only resolvable evidence bound to that check and the same candidate digest; unrelated or stale files are not alternatives.",
    "observed": "NOT_EXECUTED_PRODUCT_TEST_DESIGN_ONLY"
  },
  {
    "atom_index": 2,
    "req_id": "REQ-VERIFY",
    "acc_id": "ACC-TS14-03",
    "neg_id": "NEG-TS14-03",
    "positive": "Given C3 has an unresolved evidence locator; when preview F; then C3=UNKNOWN.",
    "negative": "Given the same unresolved locator; when a preview returns RETAINS_EVIDENCE; then reject that result as unsafe.",
    "source_clause": "DOC-02/R02-04.3:L4951-L4963@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035; DOC-02/R02-04.1:L4633-L4653@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035",
    "owner": "PIPD-EC",
    "acceptance_cue": "For a check whose evidence reference cannot be resolved or candidate identity cannot be verified, classify UNKNOWN.",
    "risk_guard": "Never convert unresolved evidence into RETAINS_EVIDENCE or claim complete coverage.",
    "observed": "NOT_EXECUTED_PRODUCT_TEST_DESIGN_ONLY"
  },
  {
    "atom_index": 3,
    "req_id": "REQ-DELIVER",
    "acc_id": "ACC-TS14-04",
    "neg_id": "NEG-TS14-04",
    "positive": "Given C1,C2,C3; when preview F; then the report contains all three ids, textual classifications and their used evidence locators.",
    "negative": "Given the same input; when the report omits C3 because it is UNKNOWN; then reject the report as incomplete.",
    "source_clause": "AGENT-SELECTED-UTTERANCE/1@sha256:ddcdbaf82b9b2b85fe4c6dd03ae05ab4857cbea4389dc597fac8574773c49a3a; DOC-01/C08.1.1:L1112-L1114@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
    "owner": "PIPD-EC",
    "acceptance_cue": "Emit a plain-text-readable report row for every input acceptance-check id, including its classification and the evidence locators used for that classification.",
    "risk_guard": "Do not omit UNKNOWN rows; a zero-input report must explicitly state NO_CHECKS rather than imply release acceptance.",
    "observed": "NOT_EXECUTED_PRODUCT_TEST_DESIGN_ONLY"
  },
  {
    "atom_index": 4,
    "req_id": "REQ-GOVERN",
    "acc_id": "ACC-TS14-05",
    "neg_id": "NEG-TS14-05",
    "positive": "Given recorded before digests of F and referenced files; when preview F; then all after digests equal before digests.",
    "negative": "Given a preview implementation that deletes one evidence file; when checking after digests; then reject the implementation and retain the failed no-effect evidence.",
    "source_clause": "DOC-01/C05.4:L1003-L1007@sha256:43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f; DOC-02/C17.3:L1739-L1749@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035; DOC-02/Eight PIPD P4 Skills Typed IO:L10790-L10803@sha256:4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035",
    "owner": "PIPD-EC",
    "acceptance_cue": "The preview leaves the proposed removal folder and all referenced evidence files byte-identical.",
    "risk_guard": "No delete/archive/write to source or evidence, no release promotion, no external upload; product implementation requires separate authority.",
    "observed": "NOT_EXECUTED_PRODUCT_TEST_DESIGN_ONLY"
  }
]
```

## Real schema validation output

Reproduce from C:/Users/user:

```text
python C:/Projects/Agent_Workspace/_r14_packet/raw/ts14_build_guided_spec.py
```

The validator receives `pi_compile_input`, not the outer report (the original schema disallows extra properties). Intent identity is SHA-256 of the preserved canonical local intent proposal body; it has the schema-compatible shape but is NOT a Native frozen IntentCard. STANDARD is proposed, not an effective ProfileBinding. Schema validation proves shape only, not source resolution, source authority, Native acceptance, semantic correctness or product behavior.

```json
{
  "python": "3.11.17",
  "schema_validation": {
    "ok": true,
    "errors": [],
    "validator": "python jsonschema 4.26.0",
    "draft": "https://json-schema.org/draft/2020-12/schema",
    "schema_path": "C:\\Projects\\Agent_Workspace\\PIPD\\skills\\pipd-pi-compile\\schemas\\input.schema.json",
    "schema_sha256": "af5a04e7a63ec4d1412f7f8aa8a54727ee837d89f54d27f972b76724793b7d75",
    "validated_target": "pi_compile_input (full envelope); each atoms item also validated against original atoms.items subschema",
    "atoms_validated": 5,
    "per_atom_errors": [
      {
        "index": 0,
        "errors": []
      },
      {
        "index": 1,
        "errors": []
      },
      {
        "index": 2,
        "errors": []
      },
      {
        "index": 3,
        "errors": []
      },
      {
        "index": 4,
        "errors": []
      }
    ],
    "negative_schema_checks": [
      {
        "mutation": "remove atoms[0].source_clause",
        "rejected": true,
        "errors": [
          "'source_clause' is a required property"
        ]
      },
      {
        "mutation": "remove atoms[0].owner",
        "rejected": true,
        "errors": [
          "'owner' is a required property"
        ]
      },
      {
        "mutation": "remove atoms[0].acceptance_cue",
        "rejected": true,
        "errors": [
          "'acceptance_cue' is a required property"
        ]
      },
      {
        "mutation": "remove atoms[0].risk_guard",
        "rejected": true,
        "errors": [
          "'risk_guard' is a required property"
        ]
      },
      {
        "mutation": "replace required PIPD-EC owner with TPM-SP",
        "rejected": true,
        "errors": [
          "'PIPD-EC' was expected"
        ]
      }
    ],
    "native_compile_invoked": false
  },
  "field_accounting": {
    "counting_unit": "scalar/null leaf occurrence in canonical pi_compile_input + proposal + acc_neg_pairs; root atoms alias and report metadata excluded",
    "pi_input_internal_leaf_fields": 29,
    "all_internal_leaf_fields": 161,
    "human_supplied_internal_fields": 0,
    "human_supplied_product_fields": 0,
    "agent_selected_utterance_count": 1,
    "human_followup_questions": 0,
    "authority_values_invented": 0,
    "explanation": "Agent proposed design values and derived schema fields; unknown Native refs remain null/HOLD. The human supplied task instructions, local source paths and an output schema, not an IntentCard, ProfileBinding, atom owner, clause locator or acceptance contract. This proves no human internal-field entry in this bounded authored run, not a deployed guided-intake UX."
  },
  "acc_neg_pair_coverage": {
    "atoms": 5,
    "pairs": 5,
    "missing": []
  }
}
```

## Field accounting / claim boundary

Machine-counted full internal field ledger: JSON `field_derivation_ledger`. The stricter PI-input-only count is also shown above. Human-supplied internal fields: 0. Human-required internal fields: 0. Human-supplied product utterances: 0; this test selected one itself, as instructed. Design choices are explicitly proposed, while Native HEAD/PI references remain null or HOLD; no Native authority value was invented.

**PD is an actionable design handoff, not a validated bound PD-PKG.** Real RepoContext and PIPD PI ref must come from their Owners/discovery, not from making the user type internal contract fields. No git commands or repository writes were used. All current writes are ts14_* evidence outputs only.

**Issues:** unrestricted novelty traversal encountered a generated .hgk lib64 access failure; scoped rerun completed, exclusions are disclosed. Upstream DOCs retain SourceFreeze/Owner/Oracle qualification limits; no attempt made to close them. No runtime product tests, Host lifecycle, official PIPD Writer invocation, independent checker or release was performed.

**Claim ceiling:** `SOURCE_BOUND_GUIDED_PROPOSAL_AND_LOCAL_JSONSCHEMA_VALIDATED_ONLY; NOT_NATIVE_PI_PD; NOT_HOST_INVOKED; NOT_INDEPENDENTLY_ACCEPTED; NO_PRODUCT_EFFECT`
