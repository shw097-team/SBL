#!/usr/bin/env python3
"""TT-S4EXT-007 -- S4-active SPEC/DEL row adjudication (deterministic generator).

Reads ``docs/SPEC_DEL_CROSSWALK.json`` (the 32 SPEC + 25 DEL = 57 row readback) and emits
``docs/S4_SPEC_DEL_ADJUDICATION.json``: one adjudicated disposition per row, derived from an
EXPLICIT table for the 13 rows the crosswalk does not mark ``EVIDENCED``.

Why a generator and not a hand-written document: the adjudication must never silently drift from the
crosswalk, and it must never rewrite it. The checked-in JSON is re-derived here, so a hand edit to
either side is caught by ``tests/test_s4ext_spec_del_adjudication.py`` (drift / no-upgrade oracle).

Vocabulary (disposition):

* ``UNCHANGED_EVIDENCED``          the crosswalk's own status is untouched; EVIDENCED != PASS.
* ``LOCAL_ORACLE_ADDED_CANDIDATE`` this round added a running oracle for the row's gate. CANDIDATE
                                   only: a maker-run oracle is not independent acceptance.
* ``OWNER_DEFER``                  the row needs an owner artefact/decision that this bounded round
                                   is not authorised to manufacture.
* ``EXTERNAL_STANDARD_ADJUDICATED``the row is satisfied by an external normative standard and an
                                   in-repo copy would be the competing SSOT the row forbids.
* ``S5_PLUS_OUT_OF_SCOPE``         the row's stage is S5+ (or the S5 half dominates) - out of this
                                   round's gate.
* ``DESIGN_ONLY_NOT_IMPLEMENTED``  a typed seam exists, no implementation is claimed.

``s4_blocking`` is true only where the row's gate is on the S4 release/provenance line, i.e. where a
false PASS would escape into a published subject. Everything else is explicitly NOT silently folded
into "S4 blocking".
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROSSWALK = os.path.join(ROOT, "docs", "SPEC_DEL_CROSSWALK.json")
OUT = os.path.join(ROOT, "docs", "S4_SPEC_DEL_ADJUDICATION.json")

SCHEMA = "PIPD-S4-SPEC-DEL-ADJUDICATION/1"
CLAIM_CEILING = "MAKER_CANDIDATE_AND_LOCAL_TESTS_ONLY_UNTIL_EXTERNAL_REQUALIFICATION"
SUBJECT_MAIN = "0a05f4fde899d5990a8c098e3feaa2d9d1d7e0de"

# ---------------------------------------------------------------------------------------------
# The adjudication. One entry per crosswalk row that is NOT ``EVIDENCED`` (9 EVIDENCE_GAP +
# 4 DESIGN_ONLY at the readback of this round). Every other row stays ``UNCHANGED_EVIDENCED``.
# ---------------------------------------------------------------------------------------------
DISPOSITIONS: dict[str, dict] = {
    # ---- EVIDENCE_GAP: SPEC side ---------------------------------------------------------
    "PIPD-SP-SPEC-002": {
        "disposition": "EXTERNAL_STANDARD_ADJUDICATED",
        "s4_blocking": False,
        "oracle_candidate": "",
        "negative_mutation_candidate": ("a test that asserts no second in-tree lifecycle standard "
                                        "document exists would have to fail if one were added"),
        "raw_evidence": (".hgk/rounds/R10-20261011-s4-bclass-decisions/far/"
                         "FAR-PIPD-R10-AUTHORING-001.md"),
        "rationale": ("PIPD-LIFECYCLE-SPEC@1.1.0 is the external normative standard this repo "
                      "implements (preflight NC-02; sha256 6f6aafec...). An in-repo copy would BE "
                      "the competing lifecycle SSOT the row forbids, so the row is closed by "
                      "adjudication + recorded digest, not by manufacturing an artefact. Accepted "
                      "by the owner in R10; no S4 release line depends on it."),
    },
    "PIPD-SP-SPEC-020": {
        "disposition": "LOCAL_ORACLE_ADDED_CANDIDATE",
        "s4_blocking": True,
        "oracle_candidate": "tests/test_s4ext_release_provenance.py",
        "negative_mutation_candidate": ("a provenance/asset-digest readback that claims functional "
                                        "or security acceptance must be refused, and a wrong "
                                        "release_tag_target must fail the 8/8 document check"),
        "raw_evidence": "tests/test_s4ext_release_provenance.py",
        "rationale": ("F001 is exactly a case of provenance claiming what it cannot support (a "
                      "correct ZIP hash protecting a wrong source narrative). The new provenance "
                      "suite separates supply-chain readback from acceptance claims and refuses the "
                      "upgrade. The crosswalk row is deliberately NOT re-marked EVIDENCED by this "
                      "round: a maker-run oracle is a candidate, not independent acceptance."),
    },
    "PIPD-SP-SPEC-023": {
        "disposition": "OWNER_DEFER",
        "s4_blocking": False,
        "oracle_candidate": "",
        "negative_mutation_candidate": ("a hard-coded package count must fail once the count is "
                                        "recomputed from the responsibility graph"),
        "raw_evidence": ".hgk/artifacts/PackageDerivationReceipt.json",
        "rationale": ("A PackageDerivationReceipt object exists but nothing recomputes the package "
                      "count from the responsibility graph. Building a deterministic-repartition "
                      "oracle is new engineering outside this narrow repair; the S0 row is routed "
                      "to the package owner."),
    },
    "PIPD-SP-SPEC-032": {
        "disposition": "OWNER_DEFER",
        "s4_blocking": False,
        "oracle_candidate": "",
        "negative_mutation_candidate": ("a claim that package-local construction depth is delivered "
                                        "must be refused while the S5..S8 backlog is still open"),
        "raw_evidence": ".hgk/artifacts/s4/S5_S8_BACKLOG.json",
        "rationale": ("The row freezes global architecture and explicitly pushes package-local "
                      "construction depth downstream. By its own wording it is satisfied by "
                      "declaring the S5..S8 boundary, which the repo does."),
    },
    # ---- EVIDENCE_GAP: DEL side ----------------------------------------------------------
    "DEL-004": {
        "disposition": "OWNER_DEFER",
        "s4_blocking": False,
        "oracle_candidate": "",
        "negative_mutation_candidate": ("a declared input identity/hash that does not resolve must "
                                        "fail the SPEC_REGISTRY check"),
        "raw_evidence": "",
        "rationale": ("No SPEC_REGISTRY@1 object exists in-tree: the registry lives in the external "
                      "blueprint. Materialising it means transcribing an external standard "
                      "document, which needs the source owner's decision - routed, not guessed."),
    },
    "DEL-008": {
        "disposition": "S5_PLUS_OUT_OF_SCOPE",
        "s4_blocking": False,
        "oracle_candidate": "",
        "negative_mutation_candidate": ("a TaskSpecSeed set claiming an S5 receiver materialisation "
                                        "must be refused while the S5 gate is not admitted"),
        "raw_evidence": "schemas/TaskSpecSeed.schema.json",
        "rationale": ("Stage is S1/S5. The typed TaskSpecSeed schema exists but no set object is "
                      "materialised. The row must NOT be treated as uniformly S4-blocking: its S5 "
                      "half is behind the S5 gate, which is out of this round, and its S1 half is a "
                      "candidate for a later round rather than a false S4 pass."),
    },
    "DEL-018": {
        "disposition": "OWNER_DEFER",
        "s4_blocking": True,
        "oracle_candidate": "docs/RELEASE_TUPLE.json + tools/build_publication_manifest.py",
        "negative_mutation_candidate": ("regenerating the projection against the frozen tuple must "
                                        "exit 0, and a manifest bound to a stale commit/tree must "
                                        "be refused (--verify / --check --current)"),
        "raw_evidence": "docs/RELEASE_TUPLE.json",
        "rationale": ("RELEASE_MANIFEST@1 is an S4 release-line row. This round froze the release "
                      "identity tuple in docs/RELEASE_TUPLE.json (F001 repair) so a manifest can be "
                      "regenerated from a frozen subject instead of a floating branch, but the "
                      "manifest object itself is NOT materialised here and no S4 pass is claimed."),
    },
    "DEL-019": {
        "disposition": "LOCAL_ORACLE_ADDED_CANDIDATE",
        "s4_blocking": True,
        "oracle_candidate": "tests/test_s4ext_release_provenance.py",
        "negative_mutation_candidate": ("an asset digest that differs from the frozen tuple must be "
                                        "refused, and SBOM/provenance bytes must not be accepted as "
                                        "functional or security acceptance"),
        "raw_evidence": "SBOM.cdx.json",
        "rationale": ("SBOM_PROVENANCE_BUNDLE@1 is an S4 release-line row. The new provenance suite "
                      "checks cryptographic/provenance readback and refuses to let it substitute for "
                      "acceptance (SPEC-020). The crosswalk row stays EVIDENCE_GAP: candidate "
                      "evidence only, pending independent requalification."),
    },
    "DEL-021": {
        "disposition": "OWNER_DEFER",
        "s4_blocking": False,
        "oracle_candidate": "",
        "negative_mutation_candidate": ("a declared package partition that differs from the "
                                        "recomputed responsibility graph must fail"),
        "raw_evidence": ".hgk/artifacts/PackageDerivationReceipt.json",
        "rationale": ("Stage S2 (upstream of the S4 release line). The receipt object exists but no "
                      "deterministic-repartition oracle exists; building one is new engineering, so "
                      "the row is routed to the package generator owner."),
    },
    # ---- DESIGN_ONLY (never to be read as implemented) -----------------------------------
    "PIPD-SP-SPEC-028": {
        "disposition": "DESIGN_ONLY_NOT_IMPLEMENTED",
        "s4_blocking": False,
        "oracle_candidate": "",
        "negative_mutation_candidate": "",
        "raw_evidence": "schemas/GENIEProjectionRef.schema.json",
        "rationale": ("S3/S5 row gated by G-S6-GENIE. A typed projection ref is all that exists; no "
                      "GENIE runtime is claimed and none is built here."),
    },
    "PIPD-SP-SPEC-029": {
        "disposition": "DESIGN_ONLY_NOT_IMPLEMENTED",
        "s4_blocking": False,
        "oracle_candidate": "",
        "negative_mutation_candidate": "",
        "raw_evidence": "schemas/ExecutionHandoff.schema.json",
        "rationale": ("S3/S5 row gated by G-S5-SHADOW/G-S5-CANARY. A typed contract + compat fixture "
                      "is all that exists; no HGK receiver execution is claimed."),
    },
    "DEL-022": {
        "disposition": "DESIGN_ONLY_NOT_IMPLEMENTED",
        "s4_blocking": False,
        "oracle_candidate": "",
        "negative_mutation_candidate": "",
        "raw_evidence": "fixtures/s5_s8/s5_compat.json",
        "rationale": "S5 HGK receiver adapter spec is design-only this round; no runtime claimed.",
    },
    "DEL-023": {
        "disposition": "DESIGN_ONLY_NOT_IMPLEMENTED",
        "s4_blocking": False,
        "oracle_candidate": "",
        "negative_mutation_candidate": "",
        "raw_evidence": "schemas/GENIEProjectionRef.schema.json",
        "rationale": "S6 GENIE projection adapter spec is design-only this round; no runtime claimed.",
    },
}

# The crosswalk's own oracle field is never rewritten by this round; an oracle this round added is
# recorded ONLY in the adjudication, so the two documents cannot be confused.
S4_BLOCKING_REQUIRED = ("PIPD-SP-SPEC-020", "DEL-018", "DEL-019")


def _row_disposition(row: dict) -> tuple[str, dict]:
    """Return ``(disposition, extra)`` for one crosswalk row."""
    if row["status"] == "EVIDENCED":
        return "UNCHANGED_EVIDENCED", {
            "s4_blocking": False,
            "oracle_candidate": "",
            "negative_mutation_candidate": "",
            "raw_evidence": "",
            "rationale": ("Crosswalk status untouched by this round. EVIDENCED means a candidate "
                          "evidence path exists - it is NOT a verified PASS, and this round does not "
                          "upgrade it."),
        }
    entry = DISPOSITIONS.get(row["id"])
    if entry is None:
        raise SystemExit(
            f"UNDJUDICATED ROW {row['id']} (status={row['status']}): every non-EVIDENCED row must "
            "carry an explicit disposition in DISPOSITIONS")
    return entry["disposition"], {k: v for k, v in entry.items() if k != "disposition"}


def build() -> dict:
    crosswalk = json.load(open(CROSSWALK, encoding="utf-8"))
    rows = []
    for row in crosswalk["rows"]:
        disposition, extra = _row_disposition(row)
        rows.append({
            "id": row["id"],
            "kind": row["kind"],
            "stage": row["stage"],
            "gate": row["gate"],
            "owner": row["owner"],
            "source_locator": row["source_locator"],
            "normative_summary": row["normative_summary"],
            "crosswalk_status": row["status"],
            "crosswalk_oracle": row["oracle"],
            "disposition": disposition,
            **extra,
        })

    by_disposition: dict[str, int] = {}
    for r in rows:
        by_disposition[r["disposition"]] = by_disposition.get(r["disposition"], 0) + 1

    return {
        "schema": SCHEMA,
        "claim_ceiling": CLAIM_CEILING,
        "subject": {
            "baseline_main_commit": SUBJECT_MAIN,
            "crosswalk": "docs/SPEC_DEL_CROSSWALK.json",
            "crosswalk_schema": crosswalk.get("schema"),
            "crosswalk_counts": crosswalk["counts"],
            "crosswalk_status_summary": crosswalk["status_summary"],
        },
        "denominator_note": (
            "57 is the ROW COUNT of the crosswalk, never 57 accepted items. "
            "status_summary.EVIDENCED counts rows with a candidate evidence path; EVIDENCED != PASS. "
            "DESIGN_ONLY rows are not in the S4 runtime denominator and are not upgrades to done."
        ),
        "adjudication_rules": [
            "the crosswalk is READ-ONLY here: no row's crosswalk_status or crosswalk_oracle is rewritten",
            "a maker-run oracle added this round is a CANDIDATE, not independent acceptance",
            "s4_blocking is true only for rows whose gate is on the S4 release/provenance line",
            "any non-EVIDENCED row without an explicit disposition is a generator error, not a default",
        ],
        "rows": rows,
        "summary": {
            "rows_total": len(rows),
            "by_disposition": by_disposition,
            "s4_blocking_rows": [r["id"] for r in rows if r["s4_blocking"]],
            "local_oracle_added_candidate": [r["id"] for r in rows
                                             if r["disposition"] == "LOCAL_ORACLE_ADDED_CANDIDATE"],
            "owner_defer_rows": [r["id"] for r in rows if r["disposition"] == "OWNER_DEFER"],
            "design_only_not_implemented": [r["id"] for r in rows
                                            if r["disposition"] == "DESIGN_ONLY_NOT_IMPLEMENTED"],
            "closed_outright_this_round": [],
            "closure_note": ("No row is closed outright by this round. Independent fresh "
                             "requalification is required before any row moves off EVIDENCE_GAP."),
        },
    }


def main() -> int:
    doc = build()
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"wrote {OUT}: {doc['summary']['rows_total']} rows, "
          f"{len(doc['summary']['s4_blocking_rows'])} S4-blocking, "
          f"dispositions={doc['summary']['by_disposition']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
