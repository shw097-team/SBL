# pipd-pd-bind — worked examples

## POS — POS-001: fresh repo context binds a PD-PKG with an affected-only scope

Input payload:

```json
{
  "pi": {
    "subject_id": "PI-0bd843e58ea8e70d",
    "content_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c"
  },
  "repo_context": {
    "root": "C:/Projects/Agent_Workspace/PIPD",
    "head": "6e9c3c1f424abec6048f975d5b4d9fab1ade84a0",
    "tracked_files": 128,
    "currentness": "FRESH",
    "writable_scope": "src/**"
  }
}
```

Output payload:

```json
{
  "subject_id": "PD-4bfd476b5670ff7e",
  "content_hash": "f4f519674b16990749d91be734cc34eab4e706e0a0e819605e33703aab5dd365",
  "version": "1",
  "schema_version": "PD-PKG@1",
  "RepoContext": {
    "root": "C:/Projects/Agent_Workspace/PIPD",
    "head": "6e9c3c1f424abec6048f975d5b4d9fab1ade84a0",
    "tracked_files": 128
  },
  "currentness": "FRESH",
  "late_bound_construction_binding": {
    "bound_at": "PD",
    "binding_scope": "affected_only",
    "writable_scope": "src/**"
  }
}
```

Expected: **ACCEPT** — both payloads round-trip through the declared schemas; routing `Bind the PD package to the repository context` expects **ROUTE**.

## NEG — NEG-001: PD late-binding requires a RepoContext; without one nothing binds

Input payload:

```json
{
  "pi": {
    "subject_id": "PI-0bd843e58ea8e70d",
    "content_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c"
  }
}
```

Expected: **REFUSE** with first-fail `input.required`; routing `What is the capital of France?` expects **NO_ROUTE** (non-trigger).

## SEC — SEC-001: a writable scope escaping the repo root is refused before binding

Payload:

```json
{
  "pi": {
    "subject_id": "PI-0bd843e58ea8e70d",
    "content_hash": "352cd79abfeea403f6d94cd2dabdcd7f5d9de21d0d8c8447d62bb04f254f633c"
  },
  "repo_context": {
    "root": "C:/Projects/Agent_Workspace/PIPD",
    "head": "6e9c3c1f424abec6048f975d5b4d9fab1ade84a0",
    "tracked_files": 128,
    "currentness": "FRESH",
    "writable_scope": "../HG-KSEOS/**"
  }
}
```

Expected: **REFUSE** with first-fail `input.not`.
