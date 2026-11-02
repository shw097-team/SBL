#!/usr/bin/env python3
"""Materialise the two R10 SSOT artefacts that were adjudicated BUILDABLE-FAITHFULLY.

Adjudication context (round R10-20261011-s4-bclass-decisions): three SPEC/DEL crosswalk rows were
active because the object each required did not exist. Two of them are satisfiable WITHOUT inventing
content, because the repository already contains the material and the artefact is a RESTATEMENT:

  DEL-015            -> ADAPTER_REGISTRY@1
      Source of truth is the canonical adapter-mapping object `ADAPTER_MAPPING` in
      src/pipd_ls_sp/projection.py (schema PIPD-ADAPTER-MAPPING/1). NOTE the correction this round
      established: .hgk/artifacts/s3/HOST_PROJECTIONS.json is a gate CHECK RECEIPT
      (PIPD-HOST-PROJECTIONS-CHECK/1), NOT a registry. The registry is generated here from the
      mapping itself, so no field can drift from its source.

  PIPD-SP-SPEC-030   -> an MCP materialization record, NEGATIVE FORM ONLY
      The only truthful assertion available is that MCP is NOT materialized (nothing is installed,
      no live/authenticated/action/dynamic-discovery need is present). A positive 'materialized'
      object would assert something the repository's own records refute and is therefore forbidden.

The third row, PIPD-SP-SPEC-002 (PIPD-LIFECYCLE-SPEC@1.1.0), was adjudicated NOT-OWED-HERE-EXTERNAL:
that standard is the external normative document this repo IMPLEMENTS, and a copy in-repo would be
precisely the "competing lifecycle SSOT" the row forbids. Nothing is generated for it.

HONEST LIMITS, recorded inside each artefact rather than only here:
  - The MCP record is PROVISIONAL and NOT canonical: no PIPD schema for it exists, and defining one is
    a design act. It is emitted as an evidence record requiring ratification, not as a canonical object.
  - The registry states materialised 3 / live 0 / FIXTURE_MOCK and lists the 22 declared-but-not-
    installed technology adapters rather than omitting them, so the declared surface is not understated.
  - Generating an artefact does not make a crosswalk row PASS. EVIDENCED is not PASS.

Usage:
    python tools/build_bclass_artifacts.py            # write both artefact files
    python tools/build_bclass_artifacts.py --check     # exit 1 if either file is stale
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp.projection import ADAPTER_MAPPING  # noqa: E402
from pipd_ls_sp.util import canonical_json, sha256_text  # noqa: E402

REGISTRY_PATH = ROOT / ".hgk" / "artifacts" / "s3" / "ADAPTER_REGISTRY.json"
MCP_PATH = ROOT / ".hgk" / "artifacts" / "s2" / "MCP_MATERIALIZATION_DECISION.json"
TECH_ADMISSIONS = ROOT / ".hgk" / "artifacts" / "s1" / "TECHNOLOGY_ADMISSIONS.json"

REGISTRY_SCHEMA = "PIPD-ADAPTER-REGISTRY/1"
MCP_SCHEMA = None  # NOT a schema id: this record asserts no schema authority (see R10 FAR)


def _canonical_mapping_hash() -> str:
    """Hash the canonical mapping with the PROJECT'S OWN helpers, never a reimplementation."""
    return sha256_text(canonical_json(ADAPTER_MAPPING))


def _declared_technologies() -> list[dict]:
    """The declared-but-not-installed technology adapters, read from the admissions record."""
    if not TECH_ADMISSIONS.exists():
        return []
    data = json.loads(TECH_ADMISSIONS.read_text(encoding="utf-8"))
    out: list[dict] = []
    for cand in data.get("candidates", data.get("admissions", [])):
        if not isinstance(cand, dict):
            continue
        out.append({
            "technology_id": cand.get("technology_id"),
            "external_name": cand.get("external_name"),
            "adapter_ref": cand.get("adapter_ref"),
            "adapter_materialization_state": cand.get("adapter_materialization_state"),
            "current_runtime_state": cand.get("current_runtime_state"),
            "source_hash": None,
            "source_hash_absent_because": "pin UNAVAILABLE; no installed artefact exists to hash",
        })
    return sorted(out, key=lambda r: str(r.get("technology_id")))


def build_registry() -> dict:
    hosts = ADAPTER_MAPPING["hosts"]
    materialised = []
    for host_id in sorted(hosts):
        h = hosts[host_id]
        materialised.append({
            "adapter_id": host_id,
            "dir": h.get("dir"),
            "entry_file": h.get("entry_file"),
            "entry_kind": h.get("entry_kind"),
            "loader": h.get("loader"),
            "skill_id": h.get("skill_id"),
            "source_objects": h.get("source_objects"),
            "required_mappings": h.get("required_mappings"),
            "field_contract_sources": h.get("field_contract_sources"),
            "allowed_permissions": h.get("allowed_permissions"),
            "provider": h.get("provider"),
            "capability_loss": h.get("capability_loss"),
            "nack": h.get("nack"),
            "materialisation_state": "MATERIALISED",
            "live_state": "NOT_RUN",
        })
    declared = _declared_technologies()
    return {
        "schema": REGISTRY_SCHEMA,
        "version": "1",
        "purpose": ("Declared input artifact identities + source hashes for adapters, with no implicit "
                    "dependency. Generated from the canonical adapter-mapping object."),
        "generated_by": "tools/build_bclass_artifacts.py",
        "no_implicit_dependency": {
            "statement": ("Every adapter identity below is declared explicitly. Nothing is resolved "
                          "implicitly at load time; an adapter not listed here is not available."),
            "enforcement": "the list is derived from ADAPTER_MAPPING, so it cannot drift from the loader's source",
        },
        "source": {
            "object_id": "ADAPTER:MAPPING",
            "schema": ADAPTER_MAPPING.get("schema"),
            "version": ADAPTER_MAPPING.get("version"),
            "location": "src/pipd_ls_sp/projection.py#ADAPTER_MAPPING",
            "sha256": _canonical_mapping_hash(),
            "hash_method": "sha256_text(canonical_json(ADAPTER_MAPPING)) using pipd_ls_sp.util",
        },
        "routing": ADAPTER_MAPPING.get("routing"),
        "writable_scope": ADAPTER_MAPPING.get("writable_scope"),
        "adapters_materialised": materialised,
        "adapters_declared_not_installed": declared,
        "counts": {
            "materialised": len(materialised),
            "declared_not_installed": len(declared),
            "live": 0,
        },
        "honest_limits": [
            "materialised counts adapters whose projection entries exist; live is 0 - all three host "
            "adapters are FIXTURE_MOCK and their live_status is NOT_RUN.",
            "The declared-not-installed adapters are listed with source_hash null, because no installed "
            "artefact exists to hash. Omitting them would understate the declared surface.",
            "This artefact restates existing material; it introduces no adapter and no dependency.",
            "NOT a gate receipt: .hgk/artifacts/s3/HOST_PROJECTIONS.json is the check receipt "
            "(PIPD-HOST-PROJECTIONS-CHECK/1); this file is the registry the crosswalk row asks for.",
        ],
    }


def build_mcp_record() -> dict:
    declared = {r.get("technology_id"): r for r in _declared_technologies()}
    mcp = None
    for cid, rec in declared.items():
        if "MCP" in str(rec.get("external_name") or "").upper():
            mcp = rec
            break
    return {
        "schema": MCP_SCHEMA,
        "record_kind": "EVIDENCE_NOTE_NON_CANONICAL",
        "claims_schema_authority": False,
        "provisional": False,
        "canonical": False,
        "ratification_required": False,
        "adjudication": ("R10 adjudication: this file is a non-canonical evidence note. It cites the existing canonical records for MCP state instead of defining a schema, because this repo has no generic schema registry and minting one would assert an undesigned authority."),
        "schema_authority_note": ("NONE CLAIMED. This note is not a canonical object and must not be "
                                  "cited as one. The authoritative statements about MCP live in "
                                  ".hgk/artifacts/s1/TECHNOLOGY_ADMISSIONS.json (CAND-06) and "
                                  ".hgk/artifacts/CapabilityActivationLedger.json."),
        "gate": ("MCP materializes only for live/authenticated/action/dynamic-discovery needs "
                 "(crosswalk normative_summary for PIPD-SP-SPEC-030)"),
        "materialized": False,
        "materialized_count": 0,
        "why_not_materialized": ("No live, authenticated, action-capable or dynamic-discovery need is "
                                 "present in this project's current scope, so the stated gate is not "
                                 "met. Nothing MCP-shaped is installed on this host."),
        "observed_state": {
            "adapter_materialization_state": (mcp or {}).get("adapter_materialization_state"),
            "current_runtime_state": (mcp or {}).get("current_runtime_state"),
            "adapter_ref": (mcp or {}).get("adapter_ref"),
        },
        "citations": [
            {"path": ".hgk/artifacts/s1/TECHNOLOGY_ADMISSIONS.json", "record": (mcp or {}).get("technology_id")},
            {"path": ".hgk/artifacts/CapabilityActivationLedger.json", "field": "deferred_profile_gated"},
        ],
        "forbidden_reading": ("This record must NOT be read as satisfying a claim that MCP IS "
                              "materialized. A positive form would assert something the repository's own "
                              "records refute."),
        "honest_limits": [
            "NON-CANONICAL and no schema authority claimed - adjudicated in R10, not pending ratification.",
            "STATES AN ABSENCE. It supplies evidence for the row; EVIDENCED is not PASS.",
        ],
    }


def render() -> dict[Path, str]:
    return {
        REGISTRY_PATH: json.dumps(build_registry(), ensure_ascii=False, indent=1, sort_keys=False) + "\n",
        MCP_PATH: json.dumps(build_mcp_record(), ensure_ascii=False, indent=1, sort_keys=False) + "\n",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="exit 1 if either artefact is stale")
    args = ap.parse_args(argv)

    want = render()
    if args.check:
        stale = []
        for path, text in want.items():
            have = path.read_text(encoding="utf-8") if path.exists() else ""
            if have != text:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            print("STALE: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("OK: %d artefacts match their sources" % len(want))
        return 0

    for path, text in want.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        print("wrote %s (%d bytes)" % (path.relative_to(ROOT), len(text)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
