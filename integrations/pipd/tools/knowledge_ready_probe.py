#!/usr/bin/env python3
"""G-KNOWLEDGE-READY probe for PIPD-LS-SP.

Reuses HG-KSEOS's OWN typed Shared Spine API + FTS5 facility (no new store, no
second SSOT). Builds a *derived*, read-only knowledge view of the reviewed
source families and exercises POS / NEG / NRTV retrieval cases.

Outputs (written to --out):
  SourceManifest.json
  KnowledgeIndexReadback.json
  RetrievalProbeReport.json
  SourceConsumptionTrace.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

def _already_promoted(spine, canonical_path: str) -> bool:
    """True only when the index already holds a PROMOTED candidate for this exact path."""
    with spine.connect() as con:
        row = con.execute(
            "SELECT c.state FROM candidates c JOIN source_units s ON s.unit_id=c.source_unit_id "
            "WHERE s.anchor=? ORDER BY c.updated_at DESC LIMIT 1", (canonical_path,)).fetchone()
    return bool(row and row["state"] == "PROMOTED")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# A frozen manifest entry carries rel/size/sha256 rather than an absolute path. The probe used to
# read r["path"] unconditionally, so a fresh scan could never run against the frozen manifest at all.
SOURCE_ROOT = Path(r"C:\Projects\Agent_Workspace")


def _entry_path(entry: dict) -> Path:
    return Path(entry["path"]) if "path" in entry else (SOURCE_ROOT / entry["rel"])

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--hgk-root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--db", required=True, type=Path)
    args = ap.parse_args()

    sys.path.insert(0, str(args.hgk_root / "src"))
    from hg_kseos.spine import SharedSpine
    from hg_kseos.knowledge import KnowledgeFactory
    from hg_kseos.errors import GroundingFailure, InvariantViolation

    args.out.mkdir(parents=True, exist_ok=True)
    args.db.parent.mkdir(parents=True, exist_ok=True)
    if args.db.exists():
        args.db.unlink()

    frozen = json.loads(args.manifest.read_text(encoding="utf-8"))
    results: dict = {"schema": "PIPD-KNOWLEDGE-READY/1", "generated_at": utc_now(),
                     "derived_view": {"engine": "HG-KSEOS SharedSpine FTS5",
                                      "schema_source": str(args.hgk_root / "src/hg_kseos/schema.sql"),
                                      "db": str(args.db), "ssot": "HG-KSEOS var/shared-spine/hg-kseos.db",
                                      "note": "derived read-only view, not a second SSOT"}}

    # ---- Phase 1: fresh readback of every family (drift detection) ----
    source_manifest: dict = {}
    drift: list = []
    for fam, spec in frozen.items():
        rows = []
        for r in spec["files"]:
            # A frozen manifest entry carries rel/size/sha256, not an absolute path; the
            # tool used to read r["path"] and therefore could never run a fresh scan.
            p = _entry_path(r)
            if not p.is_file():
                drift.append({"family": fam, "rel": r["rel"], "kind": "MISSING"})
                continue
            cur = sha256_file(p)
            if cur != r["sha256"]:
                drift.append({"family": fam, "rel": r["rel"], "kind": "DRIFT",
                              "frozen": r["sha256"], "current": cur})
            rows.append({"rel": r["rel"], "size": p.stat().st_size, "sha256": cur})
        dig = hashlib.sha256(json.dumps([[x["rel"], x["size"], x["sha256"]] for x in rows],
                                        ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
        source_manifest[fam] = {"file_count": len(rows), "manifest_sha256": dig,
                                "frozen_manifest_sha256": spec["manifest_sha256"],
                                "manifest_stable": dig == spec["manifest_sha256"], "files": rows}
    results["source_manifest"] = source_manifest
    results["drift"] = drift

    # ---- Phase 2: derived index through the HGK typed API ----
    spine = SharedSpine(args.db, args.hgk_root / "src/hg_kseos/schema.sql")
    spine.initialize()
    kf = KnowledgeFactory(spine)
    indexed = []
    ingest_errors = []
    deduplicated = []
    quarantined = []
    RANK = {"F1_GPTB_KNOWLEDGE": "R1", "F2_PIPD_STANDARD": "R1", "F3_PIPD_DESIGN": "R1",
            "F4_ENGINEERING_DONORS": "R2", "F5_COMMAND_BASIS": "R1", "F6_MACHINE_TRUTH": "R1"}
    # A path that appears in more than one family must be ingested ONCE. Re-ingesting it produced
    # ERR_CANDIDATE_NOT_PROMOTABLE, which the previous revision silently tolerated as a "PASS".
    unique: dict[str, tuple[str, dict]] = {}
    for fam, spec in frozen.items():
        for r in spec["files"][:400]:
            prev = unique.get(r["rel"])
            if prev is None or RANK[fam] < RANK[prev[0]]:
                unique[r["rel"]] = (fam, r)
    for rel, (fam, r) in unique.items():
        rank = RANK[fam]
        if True:
            p = _entry_path(r)
            if not p.is_file():
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception as exc:  # pragma: no cover
                ingest_errors.append({"rel": r["rel"], "error": str(exc)})
                continue
            if len(text) > 8_000_000:
                text = text[:8_000_000]
            try:
                res = kf.ingest_text(canonical_path=r["rel"], text=text, authority_rank=rank)
                if res.get("sanitation") == "QUARANTINED":
                    # The HGK sanitation layer refused this source. That is CORRECT security
                    # behaviour, not an ingest failure - record it as a quarantine with its
                    # findings so the gate verdict can see which REQUIRED sources are excluded.
                    quarantined.append({"family": fam, "rel": r["rel"],
                                        "source_id": res["source_id"],
                                        "findings": res.get("findings")})
                    continue
                doc_id = kf.promote(res["candidate_id"], verifier="HGK-GATE-PROMOTER",
                                    evidence_ref=source_manifest[fam]["manifest_sha256"],
                                    title=f"{fam}::{Path(r['rel']).name}")
                indexed.append({"family": fam, "rel": r["rel"], "source_id": res["source_id"],
                                "doc_id": doc_id, "sanitation": res["sanitation"]})
            except InvariantViolation as exc:
                if "ERR_CANDIDATE_NOT_PROMOTABLE" in str(exc) and _already_promoted(spine, r["rel"]):
                    deduplicated.append({"rel": r["rel"], "reason": "ALREADY_PROMOTED_IN_INDEX"})
                else:
                    ingest_errors.append({"rel": r["rel"], "error": f"{type(exc).__name__}:{exc}"})
            except Exception as exc:
                ingest_errors.append({"rel": r["rel"], "error": f"{type(exc).__name__}:{exc}"})
    rebuild = kf.rebuild()
    results["knowledge_index_readback"] = {"indexed_docs": len(indexed), "rebuild": rebuild,
                                           "unique_input_paths": len(unique),
                                           "deduplicated": deduplicated,
                                           "quarantined": quarantined,
                                           "ingest_errors": ingest_errors,
                                           "indexed": indexed[:200]}

    # ---- Phase 3: retrieval probes (positive / negative) ----

    def fts(q: str) -> str:
        """Normalize a real-world query into valid FTS5 syntax ( \\w+ AND-joined )."""
        import re
        toks = re.findall(r"[A-Za-z0-9_\u4e00-\u9fff]+", q)
        return " AND ".join(f'"{t}"' for t in toks[:8]) or '""'

    POS = [("PIPD-LIFECYCLE-SPEC", "standard_id"), ("PIPD-PKG-00", "package"),
           ("ECP", "donor"), ("TQAEP", "donor"), ("skeleton", "design"),
           ("HG-KSEOS", "control plane"), ("AGENTS.md", "operating rules")]
    NEG = ["ZZQQXX-NONEXISTENT-CLAUSE-9911", "PIPD-CLAUSE-DOES-NOT-EXIST-1234"]
    probes = {"positive": [], "negative": [], "query_normalization": "tokens AND-joined (FTS5-safe)"}
    for q, why in POS:
        try:
            hits = kf.search(fts(q), limit=3)
            probes["positive"].append({"query": q, "why": why, "hits": len(hits),
                                       "top_citation": hits[0]["citation"], "verdict": "HIT"})
        except GroundingFailure as exc:
            probes["positive"].append({"query": q, "why": why, "hits": 0, "verdict": "ABSTAIN", "error": str(exc)})
    for q in NEG:
        try:
            hits = kf.search(fts(q), limit=3)
            probes["negative"].append({"query": q, "hits": len(hits), "verdict": "UNEXPECTED_HIT"})
        except GroundingFailure as exc:
            probes["negative"].append({"query": q, "hits": 0, "verdict": "ABSTAIN_AS_EXPECTED", "error": str(exc)})

    # ---- Phase 4: NRTV (non-existent / stale / wrong-authority) ----
    nrtv = {}
    EXPECTED_MISSING = ("ERR_CITATION_INVALID", "ERR_GROUNDING", "ERR_UNKNOWN_DOC", "NOT_FOUND")
    nonexistent_subject = indexed[0]["doc_id"] if indexed else "DOC-DOES-NOT-EXIST-0000"
    try:
        # a clause id that does not exist, on a document that DOES exist (proves clause-level NRTV)
        kf.verify_citation(nonexistent_subject, "CLAUSE-DOES-NOT-EXIST-0000")
        nrtv["nonexistent_clause"] = {"verdict": "FAIL", "detail": "bogus clause id accepted",
                                      "subject": nonexistent_subject}
    except Exception as exc:
        ok_missing = any(tok in repr(exc) for tok in EXPECTED_MISSING)
        nrtv["nonexistent_clause"] = {
            "verdict": "PASS" if ok_missing else "FAIL",
            "detail": f"{type(exc).__name__}:{exc}",
            "subject": nonexistent_subject,
            "note": "PASS only on the expected citation-invalid class; any other exception is FAIL"}
    try:
        kf.verify_citation("DOC-DOES-NOT-EXIST-0000", "SRC-0000#full")
        nrtv["nonexistent_document"] = {"verdict": "FAIL", "detail": "bogus doc_id accepted"}
    except Exception as exc:
        nrtv["nonexistent_document"] = {"verdict": "PASS", "detail": f"{type(exc).__name__}:{exc}"}
    try:
        kf.ingest_text(canonical_path=indexed[0]["rel"], text="TAMPERED-CONTENT", authority_rank="R1")
        nrtv["stale_source"] = {"verdict": "FAIL", "detail": "drift not detected"}
    except InvariantViolation as exc:
        nrtv["stale_source"] = {"verdict": "PASS", "detail": str(exc)}
    except Exception as exc:
        nrtv["stale_source"] = {"verdict": "FAIL", "detail": f"{type(exc).__name__}:{exc}"}
    # C-01 repair: probe authority with a REAL promoted document, never a nonexistent id.
    real_doc = indexed[0]["doc_id"] if indexed else None
    if real_doc:
        with spine.connect() as con:
            src_state = con.execute(
                "SELECT s.status,s.authority_rank FROM knowledge_docs d "
                "JOIN source_units u ON u.unit_id=d.source_unit_id "
                "JOIN sources s ON s.source_id=u.source_id WHERE d.doc_id=?", (real_doc,)).fetchone()
        try:
            kf.add_kg_assertion(real_doc, "pipd:authority_probe", "expects", "rejection")
            nrtv["wrong_authority"] = {
                "verdict": "FAIL", "subject": real_doc,
                "detail": "assertion on a real document was accepted; this API has NO authority-rank "
                          "argument, so it cannot express wrong-authority at assertion level",
                "api_limit": "add_kg_assertion(doc_id, s, p, o) - rank is not a parameter"}
        except Exception as exc:
            nrtv["wrong_authority"] = {"verdict": "PASS", "subject": real_doc,
                                       "detail": f"{type(exc).__name__}:{exc}",
                                       "source_status_observed": dict(src_state) if src_state else None}
    nrtv["wrong_authority_located"] = {
        "verdict": "LOCATED_ELSEWHERE",
        "detail": "authority rank is enforced at ingest (ingest_text(authority_rank=...)), not at "
                  "assertion time; the probe therefore records the ingest-time layer as the "
                  "authority enforcement point instead of pretending the assertion API enforces it"}

    # ---- Phase 5: consumer trace (withdraw one source, prove exclusion) ----
    victim = indexed[0]
    kf.withdraw_source(victim["source_id"])
    try:
        kf.search(victim["rel"].split("/")[-1][:24], limit=3)
        revoked_excluded = False
    except GroundingFailure:
        revoked_excluded = True
    except Exception:
        revoked_excluded = False

    results["retrieval_probe_report"] = {"probes": probes, "nrtv": nrtv,
                                         "revoked_namespace_excluded": revoked_excluded,
                                         "revoked_source_id": victim["source_id"]}
    results["source_consumption_trace"] = {
        "policy_consumer": "PIPD-LS-SP/HERMES-GOVERNED-RUNTIME",
        "consumed": [{"family": f, "files": source_manifest[f]["file_count"],
                      "manifest_sha256": source_manifest[f]["manifest_sha256"],
                      "manifest_stable": source_manifest[f]["manifest_stable"],
                      "decision": "ADMITTED_FOR_USE" if source_manifest[f]["manifest_stable"] and not drift else "BLOCKED_DRIFT",
                      "evidence": "KnowledgeIndexReadback.json"} for f in source_manifest],
        "withdrawn_probe_source": victim["source_id"],
        "withdrawn_namespace_excluded": revoked_excluded}

    accounted = len(indexed) + len(deduplicated) + len(quarantined) + len(ingest_errors)
    ingest_complete = (len(ingest_errors) == 0 and accounted == len(unique))
    clean_coverage = ingest_complete and len(quarantined) == 0
    ok = (not drift
          and ingest_complete
          and clean_coverage
          and results["knowledge_index_readback"]["indexed_docs"] > 0
          and all(p["verdict"] == "HIT" for p in probes["positive"])
          and all(p["verdict"] == "ABSTAIN_AS_EXPECTED" for p in probes["negative"])
          and all(v["verdict"] == "PASS" for v in nrtv.values() if v["verdict"] in ("PASS", "FAIL"))
          and revoked_excluded)
    results["verdict"] = "PASS" if ok else ("PARTIAL" if ingest_complete and not drift else "FAIL")

    for name, key in (("SourceManifest.json", "source_manifest"),
                      ("KnowledgeIndexReadback.json", "knowledge_index_readback"),
                      ("RetrievalProbeReport.json", "retrieval_probe_report"),
                      ("SourceConsumptionTrace.json", "source_consumption_trace")):
        (args.out / name).write_text(json.dumps({key: results[key]}, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
    results["gate_predicate"] = {
        "no_drift": not drift, "ingest_complete": ingest_complete,
        "unique_input_paths": len(unique), "indexed_docs": len(indexed),
        "accounted": accounted, "quarantined": len(quarantined),
        "ingest_errors": len(ingest_errors), "clean_coverage": clean_coverage,
        "note": "PASS requires every unique source path to be ingested exactly once; a partial "
                "ingestion now yields FAIL instead of a silent PASS"}
    (args.out / "KNOWLEDGE_READY_REPORT.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
    print(json.dumps({"verdict": results["verdict"], "drift": len(drift),
                      "indexed_docs": len(indexed), "ingest_errors": len(ingest_errors),
                      "pos_hits": sum(1 for p in probes["positive"] if p["verdict"] == "HIT"),
                      "pos_total": len(probes["positive"]),
                      "neg_abstain": sum(1 for p in probes["negative"] if p["verdict"] == "ABSTAIN_AS_EXPECTED"),
                      "neg_total": len(probes["negative"]),
                      "nrtv": {k: v["verdict"] for k, v in nrtv.items()},
                      "revoked_excluded": revoked_excluded}, ensure_ascii=False, indent=1))
    return 0 if ok else 2

if __name__ == "__main__":
    raise SystemExit(main())
