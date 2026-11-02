# pipd-route-intake — worked examples

## POS — POS-001: full intake with three requirement atoms round-trips IntentCard

Input payload:

```json
{
  "goal": "Implement and verify the PIPD LITE slice so the deterministic compiler emits PI-PKG from the frozen blueprint sources",
  "sources": [
    {
      "rel": "docs/S0_CONTRACT_SPEC.md"
    },
    {
      "rel": "openspec/changes/pipd-ls-sp-s0-s1/design.md"
    }
  ],
  "constraints": [
    "no LLM may sit on the deterministic compile path"
  ],
  "non_goals": [
    "publication and release claims"
  ]
}
```

Output payload:

```json
{
  "subject_id": "INTENT-abf80b04afbf9fbf",
  "content_hash": "a98029b596be2761be8a572ef7929b1be379987159676de0e9a70257f754c92a",
  "version": "1",
  "schema_version": "IntentCard@1",
  "goal": "Implement and verify the PIPD LITE slice so the deterministic compiler emits PI-PKG from the frozen blueprint sources",
  "sources": [
    {
      "rel": "docs/S0_CONTRACT_SPEC.md"
    },
    {
      "rel": "openspec/changes/pipd-ls-sp-s0-s1/design.md"
    }
  ],
  "constraints": [
    "no LLM may sit on the deterministic compile path"
  ],
  "non_goals": [
    "publication and release claims"
  ],
  "atoms": [
    {
      "req_id": "REQ-INTENT",
      "axis": "intent"
    },
    {
      "req_id": "REQ-KNOWLEDGE",
      "axis": "knowledge"
    },
    {
      "req_id": "REQ-VERIFY",
      "axis": "verification"
    }
  ]
}
```

Expected: **ACCEPT** — both payloads round-trip through the declared schemas; routing `Please route the intake for the PIPD LITE slice goal` expects **ROUTE**.

## NEG — NEG-001: a goal-less request is refused before any atom can be derived

Input payload:

```json
{
  "sources": [
    {
      "rel": "docs/S0_CONTRACT_SPEC.md"
    }
  ]
}
```

Expected: **REFUSE** with first-fail `input.required`; routing `What is the weather in Taipei today?` expects **NO_ROUTE** (non-trigger).

## SEC — SEC-001: source locators must not traverse out of the admitted root

Payload:

```json
{
  "goal": "Implement and verify the PIPD LITE slice so the deterministic compiler emits PI-PKG from the frozen blueprint sources",
  "sources": [
    {
      "rel": "../HG-KSEOS/src/hg_kseos/hg-kseos.db"
    }
  ]
}
```

Expected: **REFUSE** with first-fail `input.not`.
