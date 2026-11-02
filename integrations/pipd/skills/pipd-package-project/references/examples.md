# pipd-package-project — worked examples

## POS — POS-001: LOCAL_QUALIFIED with independent approval evidence closes the package

Input payload:

```json
{
  "bundle": {
    "artifacts": [
      {
        "name": "PI-PKG",
        "subject_id": "PI-0bd843e58ea8e70d",
        "content_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c"
      },
      {
        "name": "PD-PKG",
        "subject_id": "PD-4bfd476b5670ff7e",
        "content_hash": "f4f519674b16990749d91be734cc34eab4e706e0a0e819605e33703aab5dd365"
      },
      {
        "name": "TQAEP",
        "subject_id": "TQAEP-27a6f0d9f2949830",
        "content_hash": "5ad36e5bbd6e2e99deace90756717cda93ad4014a34ff9d0eb199d0c9770b668"
      }
    ],
    "trace_edges": 2
  },
  "allowed_claims": [
    "LOCAL_QUALIFIED",
    "RUNTIME_READY"
  ],
  "producer": "PIPD-EC",
  "approval": {
    "checker_identity": "verify/glm-5.3-flash",
    "approval_receipt": "receipt://ao-2026-10-09/7c2b"
  }
}
```

Output payload:

```json
{
  "subject_id": "CCL-5e0811f4191f77bb",
  "content_hash": "72d649872e8510d7cd691e269915833c6e3791515b000ed96e2068755dd3cb42",
  "version": "1",
  "schema_version": "ClaimCeiling@1",
  "allowed_claims": [
    "LOCAL_QUALIFIED",
    "RUNTIME_READY"
  ],
  "forbidden_escalation": [
    "INDEPENDENT_PASS",
    "PUBLICATION_APPROVED",
    "RELEASED",
    "PRODUCTION_VERIFIED"
  ],
  "close_conditions": [
    "raw receipt bound to candidate hash",
    "independent checker verdict"
  ],
  "evidence": [
    {
      "subject_id": "EE-5d2ac0157e7fcaa3",
      "content_hash": "50cc71cf05e57d3d4a4a0ca684d21e57a9cedc8b23618048106c550815934ec7",
      "version": "1",
      "schema_version": "EvidenceExpectation@1",
      "expected_evidence_type": "RAW_RECEIPT",
      "producer": "PIPD-EC",
      "postcondition": "TEST-REQ-INTENT returned its oracle verdict",
      "freshness": "same_candidate_hash",
      "claim_effect": "LOCAL"
    },
    {
      "subject_id": "EE-70969a11513b9492",
      "content_hash": "b17a5b3cabd7270dd1b1a566a259365c65fab6c91b63688d689b7255f8831e2a",
      "version": "1",
      "schema_version": "EvidenceExpectation@1",
      "expected_evidence_type": "RAW_RECEIPT",
      "producer": "PIPD-EC",
      "postcondition": "TEST-REQ-VERIFY returned its oracle verdict",
      "freshness": "same_candidate_hash",
      "claim_effect": "LOCAL"
    },
    {
      "subject_id": "EE-e4bfec3e64aefcf9",
      "content_hash": "02ca8555eb43e4f5c538b42b003e9860f06fb729aac590c0608b923010ef5211",
      "version": "1",
      "schema_version": "EvidenceExpectation@1",
      "expected_evidence_type": "RAW_RECEIPT",
      "producer": "PIPD-EC",
      "postcondition": "TEST-REQ-GOVERN returned its oracle verdict",
      "freshness": "same_candidate_hash",
      "claim_effect": "LOCAL"
    }
  ],
  "trace_closure": {
    "subject_id": "TRC-5e0811f4191f77bb",
    "content_hash": "c72c6f48acbe787a5859645edcd33175f55cd567d60ed8165786967fb3b45222",
    "version": "1",
    "schema_version": "TraceClosureReport@1",
    "edges": 2,
    "orphans": [],
    "bad_hashes": [],
    "verdict": "PASS"
  }
}
```

Expected: **ACCEPT** — both payloads round-trip through the declared schemas; routing `Package the project and set the claim ceiling` expects **ROUTE**.

## NEG — NEG-001: LOCAL_QUALIFIED without a bound approval receipt and checker identity is refused

Input payload:

```json
{
  "bundle": {
    "artifacts": [
      {
        "name": "PI-PKG",
        "subject_id": "PI-0bd843e58ea8e70d",
        "content_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c"
      },
      {
        "name": "PD-PKG",
        "subject_id": "PD-4bfd476b5670ff7e",
        "content_hash": "f4f519674b16990749d91be734cc34eab4e706e0a0e819605e33703aab5dd365"
      },
      {
        "name": "TQAEP",
        "subject_id": "TQAEP-27a6f0d9f2949830",
        "content_hash": "5ad36e5bbd6e2e99deace90756717cda93ad4014a34ff9d0eb199d0c9770b668"
      }
    ],
    "trace_edges": 2
  },
  "allowed_claims": [
    "LOCAL_QUALIFIED"
  ],
  "producer": "PIPD-EC"
}
```

Expected: **REFUSE** with first-fail `semantic.claim_gate`; routing `Water my plants while I am away` expects **NO_ROUTE** (non-trigger).

## SEC — SEC-001: a smuggled publish flag must not force publication past the claim ceiling

Payload:

```json
{
  "bundle": {
    "artifacts": [
      {
        "name": "PI-PKG",
        "subject_id": "PI-0bd843e58ea8e70d",
        "content_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c"
      },
      {
        "name": "PD-PKG",
        "subject_id": "PD-4bfd476b5670ff7e",
        "content_hash": "f4f519674b16990749d91be734cc34eab4e706e0a0e819605e33703aab5dd365"
      },
      {
        "name": "TQAEP",
        "subject_id": "TQAEP-27a6f0d9f2949830",
        "content_hash": "5ad36e5bbd6e2e99deace90756717cda93ad4014a34ff9d0eb199d0c9770b668"
      }
    ],
    "trace_edges": 2
  },
  "allowed_claims": [
    "LOCAL_QUALIFIED",
    "RUNTIME_READY"
  ],
  "producer": "PIPD-EC",
  "approval": {
    "checker_identity": "verify/glm-5.3-flash",
    "approval_receipt": "receipt://ao-2026-10-09/7c2b"
  },
  "publish": true
}
```

Expected: **REFUSE** with first-fail `input.additionalProperties`.
