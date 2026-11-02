# pipd-execution-contract — worked examples

## POS — POS-001: bound PD compiles into ConstructionContract + ECP with token-gated permission

Input payload:

```json
{
  "pd": {
    "subject_id": "PD-4bfd476b5670ff7e",
    "content_hash": "f4f519674b16990749d91be734cc34eab4e706e0a0e819605e33703aab5dd365"
  },
  "pi": {
    "subject_id": "PI-0bd843e58ea8e70d",
    "content_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c"
  }
}
```

Output payload:

```json
{
  "construction_contract": {
    "subject_id": "CC-5eec32eeac7ec0b8",
    "content_hash": "2869822e371ea84f029afd1960e8146cd1ab0881f9224df8ee34f5048ad67a8c",
    "version": "1",
    "schema_version": "ConstructionContract@1",
    "subject": "PD-4bfd476b5670ff7e",
    "writable_scope": [
      "src/**"
    ],
    "expected_changes": [
      "bounded edits inside the writable scope"
    ],
    "tests": [
      "tests/test_s1_lite_slice.py"
    ],
    "rollback": "git revert to baseline commit",
    "evidence_expectations": [
      "EVD-POS",
      "EVD-NEG"
    ]
  },
  "ecp": {
    "subject_id": "ECP-5eec32eeac7ec0b8",
    "content_hash": "883c2cdb515beff688da74c97a31ae6cd1c650652ceb97709e0959bf13062941",
    "version": "1",
    "schema_version": "ECP@1",
    "effect_intent": "apply bounded edits inside the writable scope",
    "permission": {
      "scope": "src/**",
      "token_required": true
    },
    "retries": {
      "max": 1,
      "backoff": "none"
    },
    "idempotency": {
      "key": "IDEM-5eec32eeac7ec0b8",
      "guarantee": "at_most_once"
    },
    "readback": {
      "required": true,
      "kind": "residue_scan"
    },
    "rollback": {
      "pointer": "baseline_commit",
      "required": true
    }
  }
}
```

Expected: **ACCEPT** — both payloads round-trip through the declared schemas; routing `Emit the execution contract for the bound PD` expects **ROUTE**.

## NEG — NEG-001: an ECP without a permission block is not an execution contract

Input payload:

```json
{
  "pd": {
    "subject_id": "PD-4bfd476b5670ff7e",
    "content_hash": "f4f519674b16990749d91be734cc34eab4e706e0a0e819605e33703aab5dd365"
  },
  "pi": {
    "subject_id": "PI-0bd843e58ea8e70d",
    "content_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c"
  }
}
```

Expected: **REFUSE** with first-fail `output.required`; routing `Share the latest photo on Instagram` expects **NO_ROUTE** (non-trigger).

## SEC — SEC-001: the '**' whole-tree scope is refused as an unbounded effect

Payload:

```json
{
  "construction_contract": {
    "subject_id": "CC-5021d4a42891267a",
    "content_hash": "451c1618a7a956c4aaaab35ea751b4bd373387b9e5b5421a612afe5d98dd4eb8",
    "version": "1",
    "schema_version": "ConstructionContract@1",
    "subject": "PD-4bfd476b5670ff7e",
    "writable_scope": [
      "**"
    ],
    "expected_changes": [
      "bounded edits inside the writable scope"
    ],
    "tests": [
      "tests/test_s1_lite_slice.py"
    ],
    "rollback": "git revert to baseline commit",
    "evidence_expectations": [
      "EVD-POS",
      "EVD-NEG"
    ]
  },
  "ecp": {
    "subject_id": "ECP-5021d4a42891267a",
    "content_hash": "820b6c108388a289b04a5a6a603e30ce69940e424fb7b9d861e010565e981507",
    "version": "1",
    "schema_version": "ECP@1",
    "effect_intent": "apply bounded edits inside the writable scope",
    "permission": {
      "scope": "src/**",
      "token_required": true
    },
    "retries": {
      "max": 1,
      "backoff": "none"
    },
    "idempotency": {
      "key": "IDEM-5021d4a42891267a",
      "guarantee": "at_most_once"
    },
    "readback": {
      "required": true,
      "kind": "residue_scan"
    },
    "rollback": {
      "pointer": "baseline_commit",
      "required": true
    }
  }
}
```

Expected: **REFUSE** with first-fail `output.not`.
