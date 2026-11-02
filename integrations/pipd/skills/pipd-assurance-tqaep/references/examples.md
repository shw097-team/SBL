# pipd-assurance-tqaep — worked examples

## POS — POS-001: distinct maker and checker with a real receipt compile a two-test TQAEP

Input payload:

```json
{
  "pi": {
    "subject_id": "PI-0bd843e58ea8e70d",
    "content_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c",
    "trace": [
      {
        "to_id": "ATOM-2a23035a7108408f"
      },
      {
        "to_id": "ATOM-0b6373dc7d250dad"
      }
    ]
  },
  "ecp": {
    "subject_id": "ECP-5eec32eeac7ec0b8",
    "content_hash": "883c2cdb515beff688da74c97a31ae6cd1c650652ceb97709e0959bf13062941"
  },
  "maker": "execute/deepseek-v4.1-flash",
  "checker": "verify/glm-5.3-flash",
  "checker_execution_receipt": "receipt://chk-2026-10-09/a17f"
}
```

Output payload:

```json
{
  "subject_id": "TQAEP-27a6f0d9f2949830",
  "content_hash": "5ad36e5bbd6e2e99deace90756717cda93ad4014a34ff9d0eb199d0c9770b668",
  "version": "1",
  "schema_version": "TQAEP@1",
  "tests": [
    {
      "test_id": "TEST-REQ-INTENT",
      "requirement": "REQ-INTENT",
      "oracle": "deterministic assertion on the bound artifact",
      "positive_fixture": "fixtures/REQ-INTENT/positive",
      "negative_fixture": "fixtures/REQ-INTENT/negative",
      "evidence_expectation": "EVD-REQ-INTENT"
    },
    {
      "test_id": "TEST-REQ-VERIFY",
      "requirement": "REQ-VERIFY",
      "oracle": "deterministic assertion on the bound artifact",
      "positive_fixture": "fixtures/REQ-VERIFY/positive",
      "negative_fixture": "fixtures/REQ-VERIFY/negative",
      "evidence_expectation": "EVD-REQ-VERIFY"
    }
  ],
  "oracles": [
    "TEST-REQ-INTENT: deterministic assertion on the bound artifact",
    "TEST-REQ-VERIFY: deterministic assertion on the bound artifact"
  ],
  "fixtures": [
    "fixtures/REQ-INTENT/positive",
    "fixtures/REQ-VERIFY/positive"
  ],
  "acceptance": [
    {
      "case": "INDEPENDENT_CASE_PASS",
      "maker_identity": "execute/deepseek-v4.1-flash",
      "checker_identity": "verify/glm-5.3-flash",
      "distinct": true,
      "checker_execution_receipt": "receipt://chk-2026-10-09/a17f"
    }
  ],
  "requalification": "affected-only"
}
```

Expected: **ACCEPT** — both payloads round-trip through the declared schemas; routing `Compile the TQAEP assurance plan for the two atoms` expects **ROUTE**.

## NEG — NEG-001: maker aliased as checker fails the SoD rule (TQ_SOD) even though the shape is valid

Input payload:

```json
{
  "pi": {
    "subject_id": "PI-0bd843e58ea8e70d",
    "content_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c",
    "trace": [
      {
        "to_id": "ATOM-2a23035a7108408f"
      },
      {
        "to_id": "ATOM-0b6373dc7d250dad"
      }
    ]
  },
  "ecp": {
    "subject_id": "ECP-5eec32eeac7ec0b8",
    "content_hash": "883c2cdb515beff688da74c97a31ae6cd1c650652ceb97709e0959bf13062941"
  },
  "maker": "Maker-A",
  "checker": " maker-a ",
  "checker_execution_receipt": "receipt://chk-2026-10-09/a17f"
}
```

Expected: **REFUSE** with first-fail `semantic.distinct`; routing `Remind me to water the plants at 6pm` expects **NO_ROUTE** (non-trigger).

## SEC — SEC-001: an acceptance block claiming distinct=false is refused even if injected downstream

Payload:

```json
{
  "subject_id": "TQAEP-b6b36303014b1415",
  "content_hash": "852a89f321fb70f8db610340dcfda3fcf9a1f0981daa954e50227c0650cc1c78",
  "version": "1",
  "schema_version": "TQAEP@1",
  "tests": [
    {
      "test_id": "TEST-REQ-INTENT",
      "requirement": "REQ-INTENT",
      "oracle": "deterministic assertion on the bound artifact",
      "positive_fixture": "fixtures/REQ-INTENT/positive",
      "negative_fixture": "fixtures/REQ-INTENT/negative",
      "evidence_expectation": "EVD-REQ-INTENT"
    }
  ],
  "oracles": [
    "TEST-REQ-INTENT: deterministic assertion on the bound artifact"
  ],
  "fixtures": [
    "fixtures/REQ-INTENT/positive"
  ],
  "acceptance": [
    {
      "case": "INDEPENDENT_CASE_PASS",
      "maker_identity": "execute/deepseek-v4.1-flash",
      "checker_identity": "execute/deepseek-v4.1-flash",
      "distinct": false,
      "checker_execution_receipt": "receipt://chk-2026-10-09/a17f"
    }
  ],
  "requalification": "affected-only"
}
```

Expected: **REFUSE** with first-fail `output.const`.
