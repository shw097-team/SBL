# pipd-pi-compile — worked examples

## POS — POS-001: two atoms compile into PI-PKG with two trace links

Input payload:

```json
{
  "intent": {
    "subject_id": "INTENT-abf80b04afbf9fbf",
    "content_hash": "a98029b596be2761be8a572ef7929b1be379987159676de0e9a70257f754c92a"
  },
  "profile": "LITE",
  "atoms": [
    {
      "req_id": "REQ-INTENT",
      "source_clause": "docs/S0_CONTRACT_SPEC.md",
      "owner": "PIPD-EC",
      "acceptance_cue": "REQ-INTENT has an oracle and a negative fixture",
      "risk_guard": "REQ-INTENT cannot self-accept"
    },
    {
      "req_id": "REQ-VERIFY",
      "source_clause": "docs/S0_CONTRACT_SPEC.md",
      "owner": "PIPD-EC",
      "acceptance_cue": "REQ-VERIFY has an oracle and a negative fixture",
      "risk_guard": "REQ-VERIFY cannot self-accept"
    }
  ],
  "goal": "Implement and verify the PIPD LITE slice"
}
```

Output payload:

```json
{
  "subject_id": "PI-0bd843e58ea8e70d",
  "content_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c",
  "version": "1",
  "schema_version": "PI-PKG@1",
  "stable_semantic_contract": {
    "contract": "stable",
    "profile_binding": {
      "profile": "LITE",
      "axes": [
        "intent",
        "knowledge",
        "verification"
      ],
      "vetoes": [],
      "artifact_depth": "L1_SCHEMA_CONTRACT",
      "assurance": [
        "deterministic_validator"
      ]
    },
    "atoms": [
      {
        "subject_id": "ATOM-2a23035a7108408f",
        "content_hash": "03f1797799550383202fcd81c975179e64dc613996931bf9c748af30097ada32",
        "version": "1",
        "schema_version": "RequirementAtom@1",
        "req_id": "REQ-INTENT",
        "source_clause": "docs/S0_CONTRACT_SPEC.md",
        "owner": "PIPD-EC",
        "acceptance_cue": "REQ-INTENT has an oracle and a negative fixture",
        "risk_guard": "REQ-INTENT cannot self-accept"
      },
      {
        "subject_id": "ATOM-0b6373dc7d250dad",
        "content_hash": "7911023afc19a7c0ec7c89d5804d9f4044cc36f92bbe2887e4b59672a4f51683",
        "version": "1",
        "schema_version": "RequirementAtom@1",
        "req_id": "REQ-VERIFY",
        "source_clause": "docs/S0_CONTRACT_SPEC.md",
        "owner": "PIPD-EC",
        "acceptance_cue": "REQ-VERIFY has an oracle and a negative fixture",
        "risk_guard": "REQ-VERIFY cannot self-accept"
      }
    ],
    "goal": "Implement and verify the PIPD LITE slice"
  },
  "acceptance": {
    "mode": "bound",
    "oracle_source": "DOC-03 DOMAIN_ORACLES"
  },
  "trace": [
    {
      "from_type": "PI-PKG",
      "from_id": "PI-0bd843e58ea8e70d",
      "from_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c",
      "to_type": "RequirementAtom",
      "to_id": "ATOM-2a23035a7108408f",
      "to_hash": "747c3cc4a58c095462bf211bafbb36ff88a546a70325f8de9042edada67fc3dc",
      "rationale": "PI derives this atom from the frozen intent"
    },
    {
      "from_type": "PI-PKG",
      "from_id": "PI-0bd843e58ea8e70d",
      "from_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c",
      "to_type": "RequirementAtom",
      "to_id": "ATOM-0b6373dc7d250dad",
      "to_hash": "f4360d9b29b4bce9cc8e9c2b167de1134500d3c91fc6ed8e28d2ee2ce4cbf572",
      "rationale": "PI derives this atom from the frozen intent"
    }
  ]
}
```

Expected: **ACCEPT** — both payloads round-trip through the declared schemas; routing `Compile the PI package for the LITE slice intent` expects **ROUTE**.

## NEG — NEG-001: zero atoms cannot form a stable semantic contract

Input payload:

```json
{
  "intent": {
    "subject_id": "INTENT-abf80b04afbf9fbf",
    "content_hash": "a98029b596be2761be8a572ef7929b1be379987159676de0e9a70257f754c92a"
  },
  "profile": "LITE",
  "atoms": [],
  "goal": "Implement and verify the PIPD LITE slice"
}
```

Expected: **REFUSE** with first-fail `input.minItems`; routing `Write a haiku about compilers` expects **NO_ROUTE** (non-trigger).

## SEC — SEC-001: a smuggled _profile_meta sidecar must not ride into the compiler

Payload:

```json
{
  "intent": {
    "subject_id": "INTENT-abf80b04afbf9fbf",
    "content_hash": "a98029b596be2761be8a572ef7929b1be379987159676de0e9a70257f754c92a"
  },
  "profile": "LITE",
  "atoms": [
    {
      "req_id": "REQ-INTENT",
      "source_clause": "docs/S0_CONTRACT_SPEC.md",
      "owner": "PIPD-EC",
      "acceptance_cue": "REQ-INTENT has an oracle and a negative fixture",
      "risk_guard": "REQ-INTENT cannot self-accept"
    },
    {
      "req_id": "REQ-VERIFY",
      "source_clause": "docs/S0_CONTRACT_SPEC.md",
      "owner": "PIPD-EC",
      "acceptance_cue": "REQ-VERIFY has an oracle and a negative fixture",
      "risk_guard": "REQ-VERIFY cannot self-accept"
    }
  ],
  "goal": "Implement and verify the PIPD LITE slice",
  "_profile_meta": {
    "max_axes": 0
  }
}
```

Expected: **REFUSE** with first-fail `input.additionalProperties`.
