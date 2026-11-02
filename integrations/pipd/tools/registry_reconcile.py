#!/usr/bin/env python3
"""Single-source reconciliation of schemas/registry.json FROM the schema files.

FW-02 repair of audit finding R-AUD-001 (TechnologyAdmission drift: registry 9
required fields vs schema 14, `$id` carrying version 2).

Single-source rule (docs/S0_CONTRACT_SPEC.md "Single-source reconciliation"):
each `schemas/<Contract>.schema.json` is the sole source of truth for its own
`required` field set and identity; `schemas/registry.json` is a DERIVED view and
must equal the recomputation byte-content-wise. The S0 spec table (§7.3) is the
canonical floor for the exact 19/19 family set, order, materialization,
owner/consumer metadata and the minimum required fields.

Version scheme: every schema `$id` is `urn:pipd:s0:<Contract>:1` — one
v1-consistent scheme for all 19 families; no per-schema version drift.

Monotone guard: a schema may add required fields (tightening) but never drop a
previously registered one (weakening). A drop is refused in BOTH modes.

Usage:
    python tools/registry_reconcile.py --check [--schemas-dir DIR]
    python tools/registry_reconcile.py --write [--schemas-dir DIR]

Exit codes: 0 reconciled / written, 1 drift-or-refusal (details on stderr), 2 usage.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REGISTRY_SCHEMA_ID = "PIPD-S0-CONTRACT-REGISTRY/1"
DRAFT = "https://json-schema.org/draft/2020-12/schema"
IDENTITY = ["subject_id", "version", "content_hash", "schema_version"]

# Canonical S0 contract table (總藍圖 §7.3 "Canonical Machine Contracts — exact 19/19").
# index, contract, materialization, owner, consumers, spec-minimum required fields.
_CANONICAL: list[dict[str, Any]] = [
    {"index": "01", "contract": "ArtifactIdentity", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["all planes"],
     "spec_fields": IDENTITY + ["supersedes", "invalidates"]},
    {"index": "02", "contract": "AuthorityBinding", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["all compilers/adapters"],
     "spec_fields": ["source_id", "authority_rank", "locator", "supersession", "conflict_state"] + IDENTITY},
    {"index": "03", "contract": "RequirementAtom", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["PI compiler/TQAEP"],
     "spec_fields": ["req_id", "source_clause", "owner", "acceptance_cue", "risk_guard"] + IDENTITY},
    {"index": "04", "contract": "ProfileBinding", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["Skills/JIT/HGK"],
     "spec_fields": ["profile", "axes", "vetoes", "artifact_depth", "assurance"] + IDENTITY},
    {"index": "05", "contract": "TechnologyAdmission", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["tool/provider adapters"],
     "spec_fields": ["capability_need", "candidate", "disposition",
                     "pin_license_currentness", "fallback_exit"] + IDENTITY},
    {"index": "06", "contract": "PI-PKG", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["PD binder"],
     "spec_fields": ["stable_semantic_contract", "trace", "acceptance"] + IDENTITY},
    {"index": "07", "contract": "PD-PKG", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["execution handoff"],
     "spec_fields": ["RepoContext", "currentness", "late_bound_construction_binding"] + IDENTITY},
    {"index": "08", "contract": "TraceLink", "materialization": "REQUIRED_NOW",
     "owner": "PIPD/TQAEP", "consumers": ["validators/checkers"],
     "spec_fields": ["from_type", "from_id", "from_hash", "to_type", "to_id", "to_hash", "rationale"] + IDENTITY},
    {"index": "09", "contract": "TaskSpecSeed", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["receiver adapter"],
     "spec_fields": ["goal", "inputs", "outputs", "constraints", "dependencies",
                     "tests", "rollback", "evidence"] + IDENTITY},
    {"index": "10", "contract": "ConstructionContract", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["HGK adapter"],
     "spec_fields": ["subject", "writable_scope", "expected_changes", "tests",
                     "rollback", "evidence_expectations"] + IDENTITY},
    {"index": "11", "contract": "WorkOrderCandidate", "materialization": "REQUIRED_NOW_NONAUTHORITY",
     "owner": "PIPD", "consumers": ["HGK admission"],
     "spec_fields": ["candidate_only"] + IDENTITY},
    {"index": "12", "contract": "ECP", "materialization": "REQUIRED_NOW",
     "owner": "PIPD/ECP semantics", "consumers": ["HGK/TQAEP"],
     "spec_fields": ["effect_intent", "permission", "retries", "idempotency",
                     "readback", "rollback"] + IDENTITY},
    {"index": "13", "contract": "TQAEP", "materialization": "REQUIRED_NOW",
     "owner": "PIPD/TQAEP semantics", "consumers": ["Independent checker/release"],
     "spec_fields": ["tests", "oracles", "fixtures", "acceptance", "requalification"] + IDENTITY},
    {"index": "14", "contract": "ExecutionHandoff", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["HGK/other receiver"],
     "spec_fields": ["receiver", "abi_version", "payload_refs", "ack_nack_state"] + IDENTITY},
    {"index": "15", "contract": "EvidenceExpectation", "materialization": "REQUIRED_NOW",
     "owner": "PIPD/TQAEP", "consumers": ["HGK/CI/provider"],
     "spec_fields": ["expected_evidence_type", "producer", "postcondition",
                     "freshness", "claim_effect"] + IDENTITY},
    {"index": "16", "contract": "ClaimCeiling", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["all planes"],
     "spec_fields": ["allowed_claims", "forbidden_escalation", "close_conditions"] + IDENTITY},
    {"index": "17", "contract": "SurfaceProjectionManifest", "materialization": "REQUIRED_NOW",
     "owner": "PIPD", "consumers": ["surface compiler"],
     "spec_fields": ["surface", "source_hashes", "generated_files", "parity_loss", "stale_rule"] + IDENTITY},
    {"index": "18", "contract": "GENIEProjectionRef", "materialization": "SCHEMA_SEAM_ONLY_UNTIL_S6",
     "owner": "GENIE adapter", "consumers": ["GENIE compiler"],
     "spec_fields": ["target_refs"] + IDENTITY},
    {"index": "19", "contract": "ExecutionBindingRef", "materialization": "SCHEMA_SEAM_ONLY_UNTIL_S5",
     "owner": "HGK adapter", "consumers": ["HGK"],
     "spec_fields": ["receiver_binding_id", "receiver_binding_version",
                     "receiver_binding_hash", "lease", "state"] + IDENTITY},
]
_BY_CONTRACT = {row["contract"]: row for row in _CANONICAL}
SOURCE_ORDER = [row["contract"] for row in _CANONICAL]


def _fail(errors: list[str]) -> int:
    for line in errors:
        print(f"REFUSE: {line}", file=sys.stderr)
    print(f"registry_reconcile: {len(errors)} violation(s) — refusing", file=sys.stderr)
    return 1


def compute_registry(schemas_dir: Path, errors: list[str]) -> dict[str, Any] | None:
    """Recompute the registry FROM the schema files (single source of truth).

    Returns the derived registry dict, or None when the schemas themselves
    violate the S0 contract (each violation appended to `errors`, naming the
    offending family and field/key).
    """
    expected_files = {f"{c}.schema.json" for c in SOURCE_ORDER}
    found_files = {p.name for p in sorted(schemas_dir.glob("*.schema.json"))}
    ok = True
    for name in sorted(found_files - expected_files):
        errors.append(f"{name[:-len('.schema.json')]}: unexpected schema family not in the "
                      f"S0 exact 19/19 set ({schemas_dir.name}/{name}) — a 20th family is refused")
        ok = False
    for name in sorted(expected_files - found_files):
        errors.append(f"{name[:-len('.schema.json')]}: schema file missing "
                      f"({schemas_dir.name}/{name})")
        ok = False
    if not ok:
        return None

    families: list[dict[str, Any]] = []
    for canon in _CANONICAL:
        contract = canon["contract"]
        path = schemas_dir / f"{contract}.schema.json"
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{contract}: schema file unreadable: {exc}")
            continue

        expected_id = f"urn:pipd:s0:{contract}:1"
        if schema.get("$id") != expected_id:
            errors.append(f"{contract}: $id {schema.get('$id')!r} breaks the v1 scheme "
                          f"(expected {expected_id!r})")
        if "2020-12" not in str(schema.get("$schema", "")):
            errors.append(f"{contract}: $schema must be Draft 2020-12 ({DRAFT})")
        if schema.get("type") != "object":
            errors.append(f"{contract}: type must be 'object'")
        if schema.get("additionalProperties", True) is not False:
            errors.append(f"{contract}: additionalProperties must be false")

        required = schema.get("required")
        if not isinstance(required, list) or not required:
            errors.append(f"{contract}: required must be a non-empty list")
            continue
        if len(required) != len(set(required)):
            errors.append(f"{contract}: required has duplicate fields")
        missing_floor = [f for f in canon["spec_fields"] if f not in required]
        if missing_floor:
            errors.append(f"{contract}: required is missing spec-mandated field(s): {missing_floor}")
        for f in required:
            if f not in schema.get("properties", {}):
                errors.append(f"{contract}: required field {f!r} has no property definition")

        x_s0 = schema.get("x-s0")
        if not isinstance(x_s0, dict):
            errors.append(f"{contract}: x-s0 owner/consumer metadata block is missing")
            continue
        for key, expected in (("index", canon["index"]), ("contract", contract),
                              ("materialization", canon["materialization"]),
                              ("owner", canon["owner"]), ("consumers", canon["consumers"])):
            if x_s0.get(key) != expected:
                errors.append(f"{contract}: x-s0 {key} {x_s0.get(key)!r} != canonical {expected!r}")

        families.append({
            "index": canon["index"],
            "contract": contract,
            "materialization": canon["materialization"],
            "owner": canon["owner"],
            "consumers": list(canon["consumers"]),
            "required_fields": list(required),
            "schema_file": f"schemas/{contract}.schema.json",
        })

    if errors:
        return None
    return {"schema": REGISTRY_SCHEMA_ID, "families": families}


def guard_no_weakening(schemas_dir: Path, derived: dict[str, Any], errors: list[str]) -> bool:
    """Refuse any schema change that DROPS a previously registered required field.

    Schemas are single-sourced, but the registered set is a monotone ratchet:
    tightening (adding required fields) is fine, weakening (deleting one) is not.
    """
    reg_path = schemas_dir / "registry.json"
    if not reg_path.is_file():
        return True  # nothing registered yet; nothing to weaken
    try:
        current = json.loads(reg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"registry.json: unreadable ({exc})")
        return False
    now = {f.get("contract"): f for f in derived["families"]}
    ok = True
    for row in current.get("families", []):
        contract = row.get("contract")
        if contract not in now:
            continue  # exact-set drift is reported elsewhere
        dropped = [f for f in row.get("required_fields", []) if f not in now[contract]["required_fields"]]
        if dropped:
            errors.append(f"{contract}: schema.required drops previously registered required "
                          f"field(s) {dropped} — weakening refused (never delete required fields)")
            ok = False
    return ok


def check_drift(schemas_dir: Path, derived: dict[str, Any], errors: list[str]) -> None:
    """--check: the on-disk registry.json must equal the recomputation exactly."""
    reg_path = schemas_dir / "registry.json"
    if not reg_path.is_file():
        errors.append(f"registry.json: missing under {schemas_dir} — run --write to derive it")
        return
    try:
        current = json.loads(reg_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"registry.json: unreadable ({exc})")
        return
    if current.get("schema") != REGISTRY_SCHEMA_ID:
        errors.append(f"registry.json: schema {current.get('schema')!r} != {REGISTRY_SCHEMA_ID!r}")
    cur_rows = {f.get("contract"): f for f in current.get("families", [])}
    new_rows = {f["contract"]: f for f in derived["families"]}
    for contract in sorted(set(cur_rows) - set(new_rows)):
        errors.append(f"{contract}: registry.json lists a family the schemas do not declare")
    for contract in sorted(set(new_rows) - set(cur_rows)):
        errors.append(f"{contract}: registry.json is missing the family row")
    for contract in SOURCE_ORDER:
        if contract not in cur_rows:
            continue
        cur, new = cur_rows[contract], new_rows[contract]
        for key in ("index", "materialization", "owner", "consumers",
                    "required_fields", "schema_file"):
            if cur.get(key) != new.get(key):
                if key == "required_fields":
                    only_reg = [f for f in cur.get(key, []) if f not in new[key]]
                    only_schema = [f for f in new[key] if f not in cur.get(key, [])]
                    errors.append(f"{contract}: registry.json drift on required_fields vs "
                                  f"schema.required (only in registry: {only_reg}; "
                                  f"only in schema: {only_schema})")
                else:
                    errors.append(f"{contract}: registry.json drift on {key} "
                                  f"({cur.get(key)!r} != {new[key]!r})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Reconcile schemas/registry.json FROM the schema files.")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="verify registry.json matches the schemas (default)")
    mode.add_argument("--write", action="store_true",
                      help="regenerate registry.json from the schemas")
    ap.add_argument("--schemas-dir", default=None,
                    help="schemas directory (default: <repo>/schemas)")
    args = ap.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    schemas_dir = Path(args.schemas_dir) if args.schemas_dir else root / "schemas"
    if not schemas_dir.is_dir():
        print(f"REFUSE: schemas dir not found: {schemas_dir}", file=sys.stderr)
        return 1

    errors: list[str] = []
    derived = compute_registry(schemas_dir, errors)
    if derived is None:
        return _fail(errors)

    if not guard_no_weakening(schemas_dir, derived, errors):
        return _fail(errors)

    if args.write:
        reg_path = schemas_dir / "registry.json"
        reg_path.write_text(json.dumps(derived, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8", newline="\n")
        print(f"registry_reconcile: registry.json written FROM the schemas — 19/19 field-exact")
        return 0

    check_drift(schemas_dir, derived, errors)
    if errors:
        return _fail(errors)
    print("registry_reconcile: OK 19/19 families field-exact "
          "(registry.json == schemas, single-sourced)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
