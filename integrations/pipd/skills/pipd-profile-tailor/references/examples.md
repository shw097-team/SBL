# pipd-profile-tailor — worked examples

## POS — POS-001: three axes on LITE stay LITE at L1 depth

Input payload:

```json
{
  "profile": "LITE",
  "axes": [
    "intent",
    "knowledge",
    "verification"
  ],
  "provider_off_required": false
}
```

Output payload:

```json
{
  "subject_id": "PB-5334138a887a2f11",
  "content_hash": "0cdac2a5eb15236499724ef64f00cc50d580d072c49618a0792f1d611d78b415",
  "version": "1",
  "schema_version": "ProfileBinding@1",
  "profile": "LITE",
  "requested_profile": "LITE",
  "escalated": false,
  "escalation_reason": null,
  "axes": [
    "intent",
    "knowledge",
    "verification"
  ],
  "vetoes": [],
  "artifact_depth": "L1_SCHEMA_CONTRACT",
  "assurance": [
    "deterministic_validator"
  ],
  "canonical_truth": "single"
}
```

Expected: **ACCEPT** — both payloads round-trip through the declared schemas; routing `Tailor the profile for the three-axis LITE slice` expects **ROUTE**.

## NEG — NEG-001: an unknown profile name is refused before any veto runs

Input payload:

```json
{
  "profile": "ELITE",
  "axes": [
    "intent"
  ],
  "provider_off_required": false
}
```

Expected: **REFUSE** with first-fail `input.enum`; routing `Set my wallpaper to a mountain photo` expects **NO_ROUTE** (non-trigger).

## SEC — SEC-001: a smuggled escalation override must not bypass the safety veto

Payload:

```json
{
  "profile": "LITE",
  "axes": [
    "intent"
  ],
  "provider_off_required": false,
  "escalation": "none"
}
```

Expected: **REFUSE** with first-fail `input.additionalProperties`.
