#!/usr/bin/env python3
"""Build / check the 32 SPEC + 25 DEL crosswalk from live repo objects.

The normative text is the PIPD-LS-SP blueprint (see BLUEPRINT).  Every row's
``normative_summary`` is copied from the blueprint table; nothing is invented.
Where a link cannot be established from objects that actually exist in this
repo, the row is marked ``EVIDENCE_GAP`` (or ``DESIGN_ONLY`` for the S5/S6
seams) with the reason in ``first_fail``.

Modes:
  --write            write docs/SPEC_DEL_CROSSWALK.json
  --check            non-zero exit on any violation
  --row <ID>         print a single row as JSON
  --write --check    write then immediately check
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "docs", "SPEC_DEL_CROSSWALK.json")

BLUEPRINT = (
    "/src-ro/Fabric vNext/Semantic World OS Fabric/PIPD/"
    "PIPD-LS-SP_藍圖/PIPD-LS-SP_藍圖.md"
)
BLUEPRINT_NAME = "PIPD-LS-SP_藍圖.md"

# ---------------------------------------------------------------------------
# Normative tables, transcribed from the blueprint (no invention).
# SPEC table = §19.2 "Executable SpecContract@2"; compact names in §19.1.
# DEL table  = §27.1 "Exact denominator = 25".
# ---------------------------------------------------------------------------

SPEC_LINES = {f"{i:03d}": 1381 + i for i in range(1, 33)}   # 19.2 rows: 1382..1413
DEL_LINES = {f"{i:03d}": 1858 + i for i in range(1, 26)}    # 27.1 rows: 1859..1883

# id -> (topic, normative statement)  from the compact normative index §19.1
SPEC_COMPACT = {
    "001": ("Authority/source binding", "No semantic compilation without exact owner/source/supersession resolution"),
    "002": ("Single lifecycle authority", "All Skills/packages project PIPD-LIFECYCLE-SPEC@1.1.0; no competing lifecycle SSOT"),
    "003": ("Requirement narrow waist", "Every CURRENT requirement traces SRC→REQ→SPEC→ACC→VER→EVD→DEL→GATE"),
    "004": ("Exactly-one writer", "Every canonical semantic object has one primary writer"),
    "005": ("Search-Before-Build", "Material capability choices execute admission algorithm before BUILD_MINIMAL"),
    "006": ("Technology terminal disposition", "Every considered candidate has terminal disposition or blocking TT"),
    "007": ("Profile invariance", "LITE/STANDARD/ASSURED alter depth, not canonical semantics/permission"),
    "008": ("PI compilation", "PI encodes stable semantic construction contracts and rejectable handoff"),
    "009": ("PD binding", "PD resolves current repo/environment facts without silent semantic rewrite"),
    "010": ("Seed/order separation", "TaskSpecSeed != WorkOrder != ECP identities"),
    "011": ("WorkOrder authority", "PIPD WorkOrderCandidate is never runtime-authoritative"),
    "012": ("Execution admission", "Only receiver authority may ADMIT bounded execution"),
    "013": ("Effect reconciliation", "Provider/tool success cannot establish world-effect confirmation"),
    "014": ("Evidence identity", "Evidence must bind subject/version/hash and freshness"),
    "015": ("SoD", "Maker cannot self-issue independent qualification"),
    "016": ("Receiver rejectability", "Handoff is versioned, machine-readable and ACK/NACK-able"),
    "017": ("Adapter non-override", "Provider/host adapters cannot widen authority or rewrite canonical truth"),
    "018": ("Projection staleness", "Generated projection is invalid when source hash/version differs"),
    "019": ("Provider exit", "Adopted external capability includes fallback, exit, uninstall and residue check"),
    "020": ("Supply-chain separation", "Provenance/SBOM/attestation never substitutes for functional/security acceptance"),
    "021": ("Affected-only invalidation", "Change invalidates only dependency-affected artifacts/evidence"),
    "022": ("Rollback continuity", "Promotion requires reachable rollback/compensation for applicable effects"),
    "023": ("Package dynamic derivation", "Package count is recomputed from responsibility graph, not hard-coded"),
    "024": ("Package owner boundary", "Each package has one primary semantic owner and explicit consumers"),
    "025": ("Security fail-closed", "Injection, permission escalation, secret/PII and irreversible effect risks fail closed"),
    "026": ("Currentness", "External pins/versions/licenses/security status carry TTL/recheck triggers"),
    "027": ("Self-bootstrap limit", "Self-build/test/repair candidate allowed; self-independent-accept/release forbidden"),
    "028": ("GENIE anti-reverse-write", "GENIE projections/runtime findings feed CR, never direct truth mutation"),
    "029": ("HGK seam", "HGK receives typed contracts; does not own PIPD lifecycle semantics"),
    "030": ("MCP optionality", "MCP materializes only for live/authenticated/action/dynamic-discovery needs"),
    "031": ("Release truth separation", "design/artifact/schema/test/bound/runtime/independent/human/release/production states are non-inheriting"),
    "032": ("Downstream package contract", "This blueprint freezes global architecture; package-local construction depth belongs downstream"),
}

# id -> (owner, outputs(deliverables), gate)  from §19.2 full rows
SPEC_ROWS = {
    "001": ("PIPD Core", "DEL-001", "G-S0-OBJECTS"),
    "002": ("PIPD Core", "DEL-003", "G-S0-OBJECTS"),
    "003": ("PIPD Core", "DEL-002/DEL-004", "G-S0-OBJECTS"),
    "004": ("PIPD Core", "DEL-003", "G-S0-OBJECTS"),
    "005": ("Technology Admission / PIPD", "DEL-005", "G-S0-OBJECTS"),
    "006": ("Technology Admission / PIPD", "DEL-005", "G-S0-OBJECTS"),
    "007": ("PIPD Core", "DEL-003", "G-S0-OBJECTS"),
    "008": ("PI/PD Compiler", "DEL-006", "G-PI-READY"),
    "009": ("PI/PD Compiler", "DEL-007", "G-PREDEV-READY"),
    "010": ("Execution Contract / Receiver Adapter", "DEL-008/DEL-010", "G-S5-SHADOW/G-S5-CANARY"),
    "011": ("PIPD Core", "DEL-010", "G-S5-SHADOW/G-S5-CANARY"),
    "012": ("Execution Contract / Receiver Adapter", "DEL-014", "G-S5-SHADOW/G-S5-CANARY"),
    "013": ("TQAEP / Assurance", "DEL-011", "G-S5-SHADOW/G-S5-CANARY"),
    "014": ("TQAEP / Assurance", "DEL-013", "G-TQAEP/G-RELEASE"),
    "015": ("TQAEP / Assurance", "DEL-012", "G-TQAEP/G-RELEASE"),
    "016": ("Execution Contract / Receiver Adapter", "DEL-014", "G-S5-SHADOW/G-S5-CANARY"),
    "017": ("Surface/GENIE Adapter", "DEL-015/DEL-016", "G-S3-HOST/G-S3-WEB"),
    "018": ("Surface/GENIE Adapter", "DEL-016/DEL-017", "G-S3-HOST/G-S3-WEB"),
    "019": ("Technology Admission / PIPD", "DEL-005/DEL-015", "G-TECH-ADMISSION"),
    "020": ("PIPD Core", "DEL-018/DEL-019", "G-TQAEP/G-RELEASE"),
    "021": ("Evolution / Requalification", "DEL-020", "G-S7-REQUAL"),
    "022": ("Evolution / Requalification", "DEL-020", "G-S7-REQUAL"),
    "023": ("PIPD Core", "DEL-021", "G-PACKAGE-DERIVATION"),
    "024": ("PIPD Core", "DEL-021", "G-PACKAGE-DERIVATION"),
    "025": ("TQAEP / Assurance", "DEL-024", "G-TQAEP/G-RELEASE"),
    "026": ("Technology Admission / PIPD", "DEL-005", "G-TECH-ADMISSION"),
    "027": ("Evolution / Requalification", "DEL-020", "G-S7-REQUAL"),
    "028": ("Surface/GENIE Adapter", "DEL-023", "G-S6-GENIE"),
    "029": ("Execution Contract / Receiver Adapter", "DEL-022", "G-S5-SHADOW/G-S5-CANARY"),
    "030": ("Technology Admission / PIPD", "DEL-015", "G-S3-HOST/G-S3-WEB"),
    "031": ("TQAEP / Assurance", "DEL-018/DEL-025", "G-TQAEP/G-RELEASE"),
    "032": ("PIPD Core", "DEL-021", "G-PACKAGE-DERIVATION"),
}

# id -> (artifact type)  from §27.1
DEL_ROWS = {
    "001": ("AUTHORITYBINDING_SOURCEFREEZE_BUNDLE@1", "SK-02"),
    "002": ("REQUIREMENT_LEDGER@1", "SK-01/SK-04"),
    "003": ("CANONICAL_OBJECT_REGISTRY@1", "PIPD core"),
    "004": ("SPEC_REGISTRY@1", "PIPD core"),
    "005": ("TECHNOLOGY_ADMISSION_LEDGER@1", "SK-04/Tech"),
    "006": ("PI_PACKAGE_SET@1", "SK-04"),
    "007": ("PD_PACKAGE_SET@1", "SK-05"),
    "008": ("TASKSPECSEED_SET@1", "SK-06"),
    "009": ("CONSTRUCTIONCONTRACT_SET@1", "SK-06"),
    "010": ("WORKORDERCANDIDATE_SET@1", "SK-06"),
    "011": ("ECP_SET@1", "SK-06"),
    "012": ("TQAEP_SET@1", "SK-07"),
    "013": ("EVIDENCEEXPECTATION_REGISTRY@1", "SK-07"),
    "014": ("EXECUTIONHANDOFF_SET@1", "SK-06"),
    "015": ("ADAPTER_REGISTRY@1", "SK-08"),
    "016": ("SURFACE_PROJECTION_MANIFEST@1", "SK-08"),
    "017": ("WEB_HOST_PROJECTION_PACK@1", "SK-08"),
    "018": ("RELEASE_MANIFEST@1", "Release package"),
    "019": ("SBOM_PROVENANCE_BUNDLE@1", "Release package"),
    "020": ("MIGRATION_COMPATIBILITY_LEDGER@1", "Evolution"),
    "021": ("PACKAGE_DERIVATION_RECEIPT@1", "Package generator"),
    "022": ("HGK_RECEIVER_ADAPTER_SPEC@1", "HGK seam"),
    "023": ("GENIE_PROJECTION_ADAPTER_SPEC@1", "GENIE seam"),
    "024": ("RISK_TT_LEDGER@1", "Control"),
    "025": ("FINAL_READBACK_RECEIPT@1", "SK-08"),
}


def spec_stage(owner: str) -> str:
    if owner in ("PI/PD Compiler",):
        return "S1"
    if owner in ("Execution Contract / Receiver Adapter", "Surface/GENIE Adapter"):
        return "S3/S5"
    if owner in ("Evolution / Requalification",):
        return "S7"
    if owner in ("Technology Admission / PIPD",):
        return "S2"
    return "S0"


def del_stage(owner: str) -> str:
    return {
        "SK-01/SK-04": "S0",
        "SK-02": "S0",
        "PIPD core": "S0",
        "SK-04/Tech": "S2",
        "SK-04": "S1",
        "SK-05": "S1",
        "SK-06": "S1/S5",
        "SK-07": "S2",
        "SK-08": "S3",
        "Release package": "S4",
        "Evolution": "S7",
        "Package generator": "S2",
        "HGK seam": "S5",
        "GENIE seam": "S6",
        "Control": "S0..S7",
    }.get(owner, "S0")


# ---------------------------------------------------------------------------
# Link maps: which repo objects establish evidence for each row.
# statuses: EVIDENCED (object+oracle exist), EVIDENCE_GAP, DESIGN_ONLY.
# ---------------------------------------------------------------------------

def _spec_links():
    L = {}
    def e(ev, oracle, mut="tests/test_negative_and_rollback.py", tt=None):
        return dict(evidence_refs=ev, oracle=oracle, negative_mutation=mut,
                    status="EVIDENCED", first_fail="", tt_refs=tt or [])
    L["001"] = e(["schemas/AuthorityBinding.schema.json"], "tests/test_s0_contracts.py",
                 "tests/test_oracle_disagreement.py", ["TT-PIPD-KNOWLEDGE-QUARANTINE"])
    # R10 adjudication: still NOT evidenced, but no longer an unexplained gap. The required object is the
    # EXTERNAL normative standard this repo implements; a copy in-repo would be the "competing lifecycle
    # SSOT" this row itself forbids. The ref points at the adjudication that says so.
    L["002"] = dict(evidence_refs=[".hgk/rounds/R10-20261011-s4-bclass-decisions/far/FAR-PIPD-R10-AUTHORING-001.md"],
                    oracle="", negative_mutation="", status="EVIDENCE_GAP",
                    first_fail="ADJUDICATED EXTERNAL: PIPD-LIFECYCLE-SPEC@1.1.0 is the external normative standard this repo implements (preflight NC-02; located outside the repo, sha256 6f6aafec...). Not buildable here - an in-repo copy would be the competing lifecycle SSOT this row forbids.",
                    tt_refs=["TT-PIPD-KNOWLEDGE-QUARANTINE"])
    L["003"] = e([".hgk/artifacts/s1/trace_closure.json"], "tests/test_s1_lite_slice.py")
    L["004"] = e(["schemas/registry.json"], "tests/test_s0_contracts.py")
    L["005"] = e([".hgk/artifacts/s1/TECHNOLOGY_ADMISSIONS.json"], "tests/test_technology_admission.py")
    L["006"] = e(["schemas/TechnologyAdmission.schema.json"], "tests/test_technology_admission.py")
    L["007"] = e(["schemas/ProfileBinding.schema.json"], "tests/test_s0_contracts.py")
    L["008"] = e([".hgk/artifacts/s1/pi_pkg.json", "schemas/PI-PKG.schema.json"], "tests/test_s1_lite_slice.py")
    L["009"] = e([".hgk/artifacts/s1/pd_pkg.json", "schemas/PD-PKG.schema.json"], "tests/test_atomic_requirements.py")
    L["010"] = e(["schemas/TaskSpecSeed.schema.json", "schemas/WorkOrderCandidate.schema.json", "schemas/ECP.schema.json"],
                 "tests/test_negative_and_rollback.py")
    L["011"] = e(["schemas/WorkOrderCandidate.schema.json"], "tests/test_negative_and_rollback.py")
    L["012"] = e(["schemas/ExecutionBindingRef.schema.json"], "tests/test_negative_and_rollback.py")
    L["013"] = e([".hgk/artifacts/s1/ecp.json", "schemas/ECP.schema.json"], "tests/test_negative_and_rollback.py")
    L["014"] = e([".hgk/artifacts/evidence_manifest.seal.json"], "tests/test_evidence_manifest.py")
    L["015"] = e(["schemas/ClaimCeiling.schema.json"], "tests/test_s1_lite_slice.py")
    L["016"] = e(["schemas/ExecutionHandoff.schema.json"], "tests/test_negative_and_rollback.py")
    L["017"] = e([".hgk/artifacts/s3/HOST_PROJECTIONS.json"], "tests/test_host_projection.py")
    L["018"] = e(["schemas/SurfaceProjectionManifest.schema.json", ".hgk/artifacts/s3/HOST_PROJECTIONS.json"],
                 "tests/test_host_projection.py")
    L["019"] = e([".hgk/artifacts/CapabilityActivationLedger.json"], "tests/test_technology_admission.py")
    L["020"] = dict(evidence_refs=["SBOM.cdx.json"], oracle="", negative_mutation="",
                    status="EVIDENCE_GAP",
                    first_fail="SBOM/provenance bundle present but no acceptance oracle separates supply-chain from functional/security acceptance",
                    tt_refs=[])
    L["021"] = e([".hgk/artifacts/s1/trace_closure.json"], "tests/test_negative_and_rollback.py")
    L["022"] = e([".hgk/artifacts/rollback_drill.json"], "tests/test_negative_and_rollback.py")
    L["023"] = dict(evidence_refs=[".hgk/artifacts/PackageDerivationReceipt.json"], oracle="", negative_mutation="",
                    status="EVIDENCE_GAP",
                    first_fail="PackageDerivationReceipt object exists but no oracle recomputes package count from responsibility graph",
                    tt_refs=[])
    L["024"] = e(["schemas/registry.json"], "tests/test_s0_contracts.py")
    L["025"] = e([".hgk/artifacts/history_secret_scan.json"], "tests/test_secret_patterns.py")
    L["026"] = e(["schemas/TechnologyAdmission.schema.json"], "tests/test_technology_admission.py")
    L["027"] = e(["schemas/ClaimCeiling.schema.json"], "tests/test_negative_and_rollback.py")
    L["028"] = dict(evidence_refs=["schemas/GENIEProjectionRef.schema.json"], oracle="", negative_mutation="",
                    status="DESIGN_ONLY",
                    first_fail="S6 GENIE seam out of this round's gate; typed projection ref only (see .hgk/artifacts/s4/S5_S8_BACKLOG.json)",
                    tt_refs=[])
    L["029"] = dict(evidence_refs=["schemas/ExecutionHandoff.schema.json", "fixtures/s5_s8/s5_compat.json"],
                    oracle="", negative_mutation="", status="DESIGN_ONLY",
                    first_fail="S5 HGK receiver seam out of this round's gate; typed contract + compat fixture only",
                    tt_refs=[])
    # R10 adjudication: the MCP state is a recorded ABSENCE, and the record claims no schema authority.
    # An absence is evidence; a positive materialization claim would assert what the records refute.
    L["030"] = e([".hgk/artifacts/s2/MCP_MATERIALIZATION_DECISION.json",
                  ".hgk/artifacts/s1/TECHNOLOGY_ADMISSIONS.json"],
                 "tests/test_r10_bclass_evidence.py",
                 "tests/test_r10_bclass_evidence.py")
    L["031"] = e([".hgk/artifacts/evidence_manifest.seal.json", ".hgk/artifacts/s1/claim_ceiling.json"],
                 "tests/test_evidence_manifest.py")
    L["032"] = dict(evidence_refs=[".hgk/artifacts/s4/S5_S8_BACKLOG.json"], oracle="", negative_mutation="",
                    status="EVIDENCE_GAP",
                    first_fail="package-local construction depth is downstream; repo only declares the S5..S8 boundary",
                    tt_refs=[])
    return L


def _del_links():
    L = {}
    def e(ev, oracle, mut="tests/test_negative_and_rollback.py"):
        return dict(evidence_refs=ev, oracle=oracle, negative_mutation=mut,
                    status="EVIDENCED", first_fail="", tt_refs=[])
    L["001"] = e([".hgk/artifacts/s1/bundle.json", "schemas/AuthorityBinding.schema.json"], "tests/test_s1_lite_slice.py")
    L["002"] = e([".hgk/artifacts/s1/intent_card.json", "schemas/RequirementAtom.schema.json"], "tests/test_atomic_requirements.py")
    L["003"] = e(["schemas/registry.json"], "tests/test_s0_contracts.py")
    L["004"] = dict(evidence_refs=[], oracle="", negative_mutation="", status="EVIDENCE_GAP",
                    first_fail="no SPEC_REGISTRY object in repo (SPEC registry lives in the external blueprint)",
                    tt_refs=[])
    L["005"] = e([".hgk/artifacts/s1/TECHNOLOGY_ADMISSIONS.json"], "tests/test_technology_admission.py")
    L["006"] = e([".hgk/artifacts/s1/pi_pkg.json", "schemas/PI-PKG.schema.json"], "tests/test_s1_lite_slice.py")
    L["007"] = e([".hgk/artifacts/s1/pd_pkg.json", "schemas/PD-PKG.schema.json"], "tests/test_atomic_requirements.py")
    L["008"] = dict(evidence_refs=["schemas/TaskSpecSeed.schema.json"], oracle="", negative_mutation="",
                    status="EVIDENCE_GAP",
                    first_fail="TaskSpecSeed typed schema exists but no TaskSpecSeed set object is materialized",
                    tt_refs=[])
    L["009"] = e([".hgk/artifacts/s1/construction_contract.json", "schemas/ConstructionContract.schema.json"],
                 "tests/test_negative_and_rollback.py")
    L["010"] = e(["schemas/WorkOrderCandidate.schema.json"], "tests/test_negative_and_rollback.py")
    L["011"] = e([".hgk/artifacts/s1/ecp.json", "schemas/ECP.schema.json"], "tests/test_negative_and_rollback.py")
    L["012"] = e([".hgk/artifacts/s1/tqaep.json", "schemas/TQAEP.schema.json"], "tests/test_oracle_disagreement.py")
    L["013"] = e([".hgk/artifacts/s1/evidence_expectations.json", "schemas/EvidenceExpectation.schema.json"],
                 "tests/test_evidence_manifest.py")
    L["014"] = e(["schemas/ExecutionHandoff.schema.json"], "tests/test_negative_and_rollback.py")
    # R10 adjudication: the registry is materialised as a faithful RESTATEMENT of ADAPTER_MAPPING.
    # .hgk/artifacts/s3/HOST_PROJECTIONS.json is a gate CHECK RECEIPT, not a registry - corrected here.
    L["015"] = e([".hgk/artifacts/s3/ADAPTER_REGISTRY.json"],
                 "tests/test_r10_bclass_evidence.py",
                 "tests/test_r10_bclass_evidence.py")
    L["016"] = e([".hgk/artifacts/s3/HOST_PROJECTIONS.json", "schemas/SurfaceProjectionManifest.schema.json"],
                 "tests/test_host_projection.py")
    L["017"] = e([".hgk/artifacts/s3/WEB_PACK.json"], "tests/test_web_pack.py")
    L["018"] = dict(evidence_refs=[], oracle="", negative_mutation="", status="EVIDENCE_GAP",
                    first_fail="no RELEASE_MANIFEST object materialized in this round",
                    tt_refs=[])
    L["019"] = dict(evidence_refs=["SBOM.cdx.json"], oracle="", negative_mutation="", status="EVIDENCE_GAP",
                    first_fail="SBOM.cdx.json exists but no oracle verifies cryptographic/provenance claims",
                    tt_refs=[])
    L["020"] = e([".hgk/artifacts/rollback_drill.json"], "tests/test_negative_and_rollback.py")
    L["021"] = dict(evidence_refs=[".hgk/artifacts/PackageDerivationReceipt.json"], oracle="", negative_mutation="",
                    status="EVIDENCE_GAP",
                    first_fail="PackageDerivationReceipt object exists but no deterministic-repartition oracle exists",
                    tt_refs=[])
    L["022"] = dict(evidence_refs=["fixtures/s5_s8/s5_compat.json", "schemas/ExecutionHandoff.schema.json"],
                    oracle="", negative_mutation="", status="DESIGN_ONLY",
                    first_fail="S5 HGK receiver adapter spec is design-only this round (typed seam + compat fixture)",
                    tt_refs=[])
    L["023"] = dict(evidence_refs=["schemas/GENIEProjectionRef.schema.json"], oracle="", negative_mutation="",
                    status="DESIGN_ONLY",
                    first_fail="S6 GENIE projection adapter spec is design-only this round (typed ref only)",
                    tt_refs=[])
    L["024"] = e([".hgk/artifacts/TT_REGISTER.json"], "tests/test_tt_summary.py")
    L["025"] = e([".hgk/artifacts/evidence_manifest.seal.json"], "tests/test_evidence_manifest.py")
    return L


def build_rows():
    specs = _spec_links()
    dels = _del_links()
    rows = []
    for i in range(1, 33):
        k = f"{i:03d}"
        topic, summary = SPEC_COMPACT[k]
        owner, outputs, gate = SPEC_ROWS[k]
        link = specs[k]
        rows.append({
            "id": f"PIPD-SP-SPEC-{k}",
            "kind": "SPEC",
            "source_locator": f"{BLUEPRINT_NAME} §19.2 L{SPEC_LINES[k]}",
            "normative_summary": summary,
            "owner": owner,
            "stage": spec_stage(owner),
            "requirement_refs": [f"REQ-PIPD-{k}"],
            "deliverable_refs": outputs.split("/"),
            "evidence_refs": list(link["evidence_refs"]),
            "gate": gate,
            "oracle": link["oracle"],
            "negative_mutation": link["negative_mutation"],
            "status": link["status"],
            "first_fail": link["first_fail"],
            "tt_refs": list(link["tt_refs"]),
        })
    for i in range(1, 26):
        k = f"{i:03d}"
        artifact, owner = DEL_ROWS[k]
        link = dels[k]
        rows.append({
            "id": f"DEL-{k}",
            "kind": "DEL",
            "source_locator": f"{BLUEPRINT_NAME} §27.1 L{DEL_LINES[k]}",
            "normative_summary": f"{artifact} — declared input artifact identities + source hashes; no implicit dependency",
            "owner": owner,
            "stage": del_stage(owner),
            "requirement_refs": [f"REQ-PIPD-DEL-{k}"],
            "deliverable_refs": [],
            "evidence_refs": list(link["evidence_refs"]),
            "gate": "DELIVERABLES_MASTER_LEDGER",
            "oracle": link["oracle"],
            "negative_mutation": link["negative_mutation"],
            "status": link["status"],
            "first_fail": link["first_fail"],
            "tt_refs": list(link["tt_refs"]),
        })
    return rows


def _blueprint_line(n: int):
    if not os.path.exists(BLUEPRINT):
        return None
    with open(BLUEPRINT, encoding="utf-8") as fh:
        for idx, line in enumerate(fh, 1):
            if idx == n:
                return line
    return None


def resolve_source_locator(locator: str) -> bool:
    """A locator resolves when its id/section/line match the transcribed table
    and, when the blueprint is present, the actual line begins with the id."""
    try:
        left, line_s = locator.split(" L")
        line = int(line_s)
        _fname, section = left.rsplit(" §", 1)
    except ValueError:
        return False
    row_id = None
    if section == "19.2":
        for k, ln in SPEC_LINES.items():
            if ln == line:
                row_id = f"PIPD-SP-SPEC-{k}"
                break
    elif section == "27.1":
        for k, ln in DEL_LINES.items():
            if ln == line:
                row_id = f"DEL-{k}"
                break
    if row_id is None:
        return False
    actual = _blueprint_line(line)
    if actual is not None and not actual.startswith(f"| {row_id} "):
        return False
    return True


def check_rows(rows) -> list:
    violations = []
    specs = [r for r in rows if r["kind"] == "SPEC"]
    dels = [r for r in rows if r["kind"] == "DEL"]
    if len(specs) != 32:
        violations.append(f"SPEC count is {len(specs)}, expected 32")
    if len(dels) != 25:
        violations.append(f"DEL count is {len(dels)}, expected 25")
    for r in rows:
        if not resolve_source_locator(r["source_locator"]):
            violations.append(f"{r['id']}: source_locator unresolvable: {r['source_locator']}")
        for ref in r["evidence_refs"]:
            if not os.path.exists(os.path.join(ROOT, ref)):
                violations.append(f"{r['id']}: evidence_ref missing: {ref}")
        if r["status"] == "EVIDENCED" and not r["oracle"]:
            violations.append(f"{r['id']}: EVIDENCED row has no oracle")
        # An EVIDENCED row's oracle must resolve to a real object: a pointer at a non-existent
        # oracle path is an unproven claim, not evidence (W9 / independent finding A3).
        if r["status"] == "EVIDENCED" and r["oracle"] and \
                not os.path.exists(os.path.join(ROOT, r["oracle"])):
            violations.append(f"{r['id']}: EVIDENCED oracle file missing: {r['oracle']}")
    return violations


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build/check SPEC+DEL crosswalk")
    ap.add_argument("--write", action="store_true", help="write docs/SPEC_DEL_CROSSWALK.json")
    ap.add_argument("--check", action="store_true", help="verify the crosswalk")
    ap.add_argument("--row", metavar="ID", help="print one row as JSON")
    args = ap.parse_args(argv)

    if args.row and not (args.write or args.check):
        rows = build_rows()
        for r in rows:
            if r["id"] == args.row:
                print(json.dumps(r, ensure_ascii=False, indent=2))
                return 0
        print(f"row not found: {args.row}", file=sys.stderr)
        return 2

    rows = build_rows()
    if args.write:
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        doc = {
            "schema": "PIPD-SPEC-DEL-CROSSWALK/1",
            "blueprint": BLUEPRINT_NAME,
            "counts": {"SPEC": 32, "DEL": 25, "total": len(rows)},
            "status_summary": _status_summary(rows),
            "rows": rows,
        }
        with open(OUT_PATH, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")

    if args.check:
        violations = check_rows(rows)
        if violations:
            for v in violations:
                print(f"VIOLATION: {v}")
            print(f"check failed: {len(violations)} violation(s)")
            return 1
        print("crosswalk check: OK (32 SPEC + 25 DEL)")
        return 0
    return 0


def _status_summary(rows):
    summary = {}
    for r in rows:
        summary[r["status"]] = summary.get(r["status"], 0) + 1
    return summary


if __name__ == "__main__":
    raise SystemExit(main())
