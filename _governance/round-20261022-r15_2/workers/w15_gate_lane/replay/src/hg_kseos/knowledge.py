from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from .errors import GroundingFailure, InvariantViolation
from .security import contains_pii, sanitation_findings
from .spine import SharedSpine
from .util import canonical_json, new_id, sha256_file, sha256_text, utc_now


class KnowledgeFactory:
    def __init__(self, spine: SharedSpine) -> None:
        self.spine = spine

    def ingest_text(
        self,
        canonical_path: str,
        text: str,
        authority_rank: str,
        anchor: str = "full",
    ) -> dict[str, Any]:
        source_hash = sha256_text(text)
        source_id = "SRC-" + source_hash[:20]
        unit_id = "UNIT-" + sha256_text(f"{source_id}#{anchor}:{source_hash}")[:20]
        findings = sanitation_findings(text)
        sanitation = "QUARANTINED" if findings else "CLEAN"
        now = utc_now()
        with self.spine.transaction() as connection:
            existing = connection.execute(
                "SELECT sha256 FROM sources WHERE canonical_path=? AND status!='WITHDRAWN'",
                (canonical_path,),
            ).fetchone()
            if existing and existing["sha256"] != source_hash:
                raise InvariantViolation(f"ERR_SOURCE_DRIFT:{canonical_path}")
            connection.execute(
                """INSERT OR IGNORE INTO sources
                   (source_id,canonical_path,sha256,authority_rank,status,created_at)
                   VALUES(?,?,?,?,?,?)""",
                (source_id, canonical_path, source_hash, authority_rank, "QUARANTINED" if findings else "ACTIVE", now),
            )
            connection.execute(
                """INSERT OR IGNORE INTO source_units
                   (unit_id,source_id,anchor,content,content_sha256,sanitation_status,created_at)
                   VALUES(?,?,?,?,?,?,?)""",
                (unit_id, source_id, anchor, text, source_hash, sanitation, now),
            )
            candidate_id = new_id("CAND")
            connection.execute(
                """INSERT INTO candidates
                   (candidate_id,source_unit_id,kind,body,state,created_at,updated_at)
                   VALUES(?,?,'KNOWLEDGE',?,?,?,?)""",
                (candidate_id, unit_id, text, "QUARANTINED" if findings else "CANDIDATE", now, now),
            )
        return {
            "source_id": source_id,
            "unit_id": unit_id,
            "candidate_id": candidate_id,
            "sanitation": sanitation,
            "findings": findings,
        }

    def promote(self, candidate_id: str, verifier: str, evidence_ref: str, title: str) -> str:
        if not evidence_ref.strip():
            raise InvariantViolation("ERR_PROMOTION_EVIDENCE_REQUIRED")
        if verifier.casefold() in {"maker", "self", "candidate"}:
            raise InvariantViolation("ERR_SELF_APPROVAL")
        with self.spine.transaction() as connection:
            row = connection.execute(
                """SELECT c.state,c.body,c.source_unit_id,s.source_id,s.anchor
                   FROM candidates c JOIN source_units s ON s.unit_id=c.source_unit_id
                   WHERE c.candidate_id=?""",
                (candidate_id,),
            ).fetchone()
            if not row or row["state"] != "CANDIDATE":
                raise InvariantViolation("ERR_CANDIDATE_NOT_PROMOTABLE")
            doc_id = "DOC-" + sha256_text(candidate_id + evidence_ref)[:20]
            citation = f"{row['source_id']}#{row['anchor']}"
            now = utc_now()
            connection.execute(
                """UPDATE candidates SET state='PROMOTED',verifier=?,promotion_evidence=?,updated_at=?
                   WHERE candidate_id=?""",
                (verifier, evidence_ref, now, candidate_id),
            )
            connection.execute(
                """INSERT INTO knowledge_docs(doc_id,source_unit_id,title,body,citation,created_at)
                   VALUES(?,?,?,?,?,?)""",
                (doc_id, row["source_unit_id"], title, row["body"], citation, now),
            )
            connection.execute(
                "INSERT INTO knowledge_fts(doc_id,title,body,citation) VALUES(?,?,?,?)",
                (doc_id, title, row["body"], citation),
            )
        return doc_id

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        if not query.strip():
            raise GroundingFailure("ABSTAIN_EMPTY_QUERY")
        with self.spine.connect() as connection:
            try:
                rows = connection.execute(
                    """SELECT doc_id,title,citation,snippet(knowledge_fts,2,'[',']','…',20) AS snippet,
                              bm25(knowledge_fts) AS score
                       FROM knowledge_fts WHERE knowledge_fts MATCH ? ORDER BY score LIMIT ?""",
                    (query, limit),
                ).fetchall()
            except sqlite3.OperationalError as exc:
                raise GroundingFailure(f"ABSTAIN_UNSUPPORTED_QUERY:{query}") from exc
        if not rows:
            raise GroundingFailure(f"ABSTAIN_NO_GROUNDING:{query}")
        return [dict(row) for row in rows]

    def detect_conflicts(self) -> list[dict[str, Any]]:
        """Flag the same (subject, predicate) asserted with different objects by different active sources.

        R14-TS18 found that contradictory claims across sources were never surfaced: each assertion was individually
        admissible, so the graph held both and nothing said so. This does not decide which one is right - it reports the
        pair with both source doc ids, which is what a reviewer needs to adjudicate.
        """
        with self.spine.connect() as connection:
            rows = connection.execute(
                """SELECT a.subject,a.predicate,a.object,a.source_doc_id
                   FROM kg_assertions a
                   JOIN knowledge_docs k ON k.doc_id=a.source_doc_id
                   JOIN source_units u ON u.unit_id=k.source_unit_id
                   JOIN sources s ON s.source_id=u.source_id
                   WHERE s.status='ACTIVE'
                   ORDER BY a.subject,a.predicate,a.object"""
            ).fetchall()
        grouped: dict[tuple[str, str], dict[str, set[str]]] = {}
        for row in rows:
            grouped.setdefault((row["subject"], row["predicate"]), {}).setdefault(row["object"], set()).add(
                row["source_doc_id"])
        conflicts = []
        for (subject, predicate), objects in grouped.items():
            if len(objects) > 1:
                conflicts.append({"subject": subject, "predicate": predicate,
                                  "objects": {obj: sorted(docs) for obj, docs in objects.items()}})
        return conflicts

    def rebuild(self) -> dict[str, int]:
        with self.spine.transaction() as connection:
            connection.execute("DELETE FROM knowledge_fts")
            connection.execute("DELETE FROM kg_edges")
            docs = connection.execute(
                """SELECT k.doc_id,k.title,k.body,k.citation
                   FROM knowledge_docs k
                   JOIN source_units u ON u.unit_id=k.source_unit_id
                   JOIN sources s ON s.source_id=u.source_id
                   WHERE s.status='ACTIVE'"""
            ).fetchall()
            for row in docs:
                connection.execute(
                    "INSERT INTO knowledge_fts(doc_id,title,body,citation) VALUES(?,?,?,?)",
                    (row["doc_id"], row["title"], row["body"], row["citation"]),
                )
            assertions = connection.execute(
                """SELECT a.edge_id,a.source_doc_id,a.subject,a.predicate,a.object,a.created_at
                   FROM kg_assertions a
                   JOIN knowledge_docs k ON k.doc_id=a.source_doc_id
                   JOIN source_units u ON u.unit_id=k.source_unit_id
                   JOIN sources s ON s.source_id=u.source_id
                   WHERE s.status='ACTIVE'"""
            ).fetchall()
            for row in assertions:
                connection.execute(
                    """INSERT INTO kg_edges(edge_id,source_doc_id,subject,predicate,object,created_at)
                       VALUES(?,?,?,?,?,?)""",
                    tuple(row),
                )
        return {"fts_documents": len(docs), "kg_edges": len(assertions),
                "conflicts": len(self.detect_conflicts())}

    def add_kg_assertion(self, doc_id: str, subject: str, predicate: str, object_: str) -> str:
        if not all((subject.strip(), predicate.strip(), object_.strip())):
            raise InvariantViolation("ERR_KG_ASSERTION_FIELD_MISSING")
        edge_id = "EDGE-" + sha256_text(f"{doc_id}:{subject}:{predicate}:{object_}")[:20]
        with self.spine.transaction() as connection:
            active = connection.execute(
                """SELECT 1 FROM knowledge_docs k
                   JOIN source_units u ON u.unit_id=k.source_unit_id
                   JOIN sources s ON s.source_id=u.source_id
                   WHERE k.doc_id=? AND s.status='ACTIVE'""",
                (doc_id,),
            ).fetchone()
            if not active:
                raise GroundingFailure(f"ERR_KG_SOURCE_NOT_ACTIVE:{doc_id}")
            now = utc_now()
            values = (edge_id, doc_id, subject, predicate, object_, now)
            connection.execute(
                """INSERT OR IGNORE INTO kg_assertions
                   (edge_id,source_doc_id,subject,predicate,object,created_at) VALUES(?,?,?,?,?,?)""",
                values,
            )
            connection.execute(
                """INSERT OR IGNORE INTO kg_edges
                   (edge_id,source_doc_id,subject,predicate,object,created_at) VALUES(?,?,?,?,?,?)""",
                values,
            )
        return edge_id

    def citation_integrity(self, doc_id: str) -> dict[str, Any]:
        """Compare the digest recorded at ingest with the bytes on disk right now.

        R14-TS18 found that verify_citation() only compared the stored citation STRING, so a source file could be
        edited after ingestion and the citation still verified. This reports MATCH / DRIFT / UNREADABLE without deciding
        for the caller, because "the file is not on this host" is a different fact from "the file changed".
        """
        with self.spine.connect() as connection:
            row = connection.execute(
                """SELECT s.canonical_path,s.sha256 FROM knowledge_docs k
                   JOIN source_units u ON u.unit_id=k.source_unit_id
                   JOIN sources s ON s.source_id=u.source_id WHERE k.doc_id=?""",
                (doc_id,),
            ).fetchone()
        if not row:
            raise GroundingFailure(f"ERR_CITATION_INVALID:{doc_id}")
        path = Path(row["canonical_path"])
        if not path.is_file():
            return {"doc_id": doc_id, "path": str(path), "status": "UNREADABLE",
                    "stored_sha256": row["sha256"], "live_sha256": None}
        live = sha256_text(path.read_text(encoding="utf-8", errors="replace"))
        return {"doc_id": doc_id, "path": str(path),
                "status": "MATCH" if live == row["sha256"] else "DRIFT",
                "stored_sha256": row["sha256"], "live_sha256": live}

    def verify_citation(self, doc_id: str, citation: str, *, require_source_bytes: bool = False) -> bool:
        with self.spine.connect() as connection:
            row = connection.execute(
                """SELECT k.citation,s.status,s.canonical_path FROM knowledge_docs k
                   JOIN source_units u ON u.unit_id=k.source_unit_id
                   JOIN sources s ON s.source_id=u.source_id WHERE k.doc_id=?""",
                (doc_id,),
            ).fetchone()
        if not row or row["status"] != "ACTIVE" or row["citation"] != citation:
            raise GroundingFailure(f"ERR_CITATION_INVALID:{doc_id}")
        integrity = self.citation_integrity(doc_id)
        if integrity["status"] == "DRIFT":
            raise GroundingFailure(f"ERR_CITATION_SOURCE_DRIFT:{doc_id}")
        if require_source_bytes and integrity["status"] == "UNREADABLE":
            raise GroundingFailure(f"ERR_CITATION_SOURCE_UNREADABLE:{doc_id}")
        return True

    def withdraw_source(self, source_id: str) -> None:
        with self.spine.transaction() as connection:
            docs = connection.execute(
                """SELECT k.doc_id FROM knowledge_docs k JOIN source_units u ON u.unit_id=k.source_unit_id
                   WHERE u.source_id=?""",
                (source_id,),
            ).fetchall()
            for row in docs:
                connection.execute("DELETE FROM knowledge_fts WHERE doc_id=?", (row["doc_id"],))
                connection.execute("DELETE FROM kg_edges WHERE source_doc_id=?", (row["doc_id"],))
            connection.execute(
                "UPDATE sources SET status='WITHDRAWN',withdrawn_at=? WHERE source_id=?",
                (utc_now(), source_id),
            )

    def repoint_source(
        self,
        source_id: str,
        new_canonical_path: str,
        *,
        actor: str,
        evidence_ref: str,
    ) -> dict[str, Any]:
        """Move a source's `canonical_path` pointer to where the SAME content now lives.

        WHY this exists: `ingest_text()` keys a source by `SRC-<sha256[:20]>` and inserts with
        `INSERT OR IGNORE`, so it structurally can never re-point an existing row. When the corpus
        is relocated on disk the recorded path goes dead and `ERR_SOURCE_DRIFT` becomes unpassable,
        while re-ingesting is a no-op and a direct SQL UPDATE is forbidden to consumers. This is the
        missing canonical transition, NOT a bypass.

        Discipline (same shape as `transition_requirement`):
          * content must be UNCHANGED -- the file at the new path must hash to the recorded
            `sources.sha256`; a re-point is a pointer move, never a content swap (no silent drift)
          * the source must still be ACTIVE; a WITHDRAWN source is never resurrected by a re-point
          * the evidence ref must already exist in `evidence_refs` (no orphan re-points)
          * the pointer change and its canonical event are written in ONE transaction
          * an identical replay returns the original event instead of appending a second one
          * the rollback pointer is the previous path
        """
        if not actor.strip():
            raise InvariantViolation("ERR_REPOINT_ACTOR_MISSING")
        if not evidence_ref.strip():
            raise InvariantViolation("ERR_REPOINT_EVIDENCE_REQUIRED")
        target = os.path.normpath(new_canonical_path)
        if not os.path.isfile(target):
            raise InvariantViolation(f"ERR_REPOINT_PATH_MISSING:{target}")
        live_sha = sha256_file(Path(target))
        idempotency_key = f"repoint:{source_id}:{target}"
        now = utc_now()
        with self.spine.transaction() as connection:
            if not connection.execute(
                "SELECT 1 FROM evidence_refs WHERE evidence_id=?", (evidence_ref,)
            ).fetchone():
                raise InvariantViolation(f"ERR_REPOINT_EVIDENCE_UNREGISTERED:{evidence_ref}")
            row = connection.execute(
                "SELECT canonical_path,sha256,status FROM sources WHERE source_id=?", (source_id,)
            ).fetchone()
            if not row:
                raise InvariantViolation(f"ERR_REPOINT_UNKNOWN_SOURCE:{source_id}")
            if row["status"] != "ACTIVE":
                raise InvariantViolation(f"ERR_REPOINT_SOURCE_STATE:{source_id}:{row['status']}")
            from_path = row["canonical_path"]
            if live_sha != row["sha256"]:
                raise InvariantViolation(f"ERR_REPOINT_SHA_DRIFT:{source_id}")
            if os.path.normpath(from_path) == target:
                spent = connection.execute(
                    "SELECT event_id FROM canonical_events WHERE idempotency_key=?",
                    (idempotency_key,),
                ).fetchone()
                return {
                    "source_id": source_id,
                    "from_path": from_path,
                    "to_path": target,
                    "event_id": spent["event_id"] if spent else None,
                    "idempotent_replay": True,
                }
            event_id = new_id("EVT")
            connection.execute(
                "UPDATE sources SET canonical_path=? WHERE source_id=?", (target, source_id)
            )
            connection.execute(
                """INSERT INTO canonical_events
                   (event_id,idempotency_key,entity_type,entity_id,from_state,to_state,actor,
                    expected_version,resulting_version,payload_json,evidence_ref,rollback_pointer,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    event_id,
                    idempotency_key,
                    "source",
                    source_id,
                    from_path,
                    target,
                    actor,
                    0,
                    1,
                    canonical_json({"from_path": from_path, "to_path": target, "sha256": live_sha}),
                    evidence_ref,
                    from_path,
                    now,
                ),
            )
        return {
            "source_id": source_id,
            "from_path": from_path,
            "to_path": target,
            "event_id": event_id,
            "idempotent_replay": False,
        }

    def remember(
        self,
        scope: str,
        body: str,
        provenance: str,
        expires_at: str | None = None,
        *,
        allow_pii: bool = False,
    ) -> str:
        findings = sanitation_findings(body)
        if findings:
            raise InvariantViolation("ERR_MEMORY_POISONED:" + ",".join(findings))
        if contains_pii(body) and not allow_pii:
            raise InvariantViolation("ERR_PII_PERSISTENCE_NOT_ADMITTED")
        memory_id = new_id("MEM")
        with self.spine.transaction() as connection:
            connection.execute(
                """INSERT INTO memory_records(memory_id,scope,body,provenance,expires_at,created_at)
                   VALUES(?,?,?,?,?,?)""",
                (memory_id, scope, body, provenance, expires_at, utc_now()),
            )
        return memory_id

    def active_memory(self, scope: str, now: str | None = None) -> list[dict[str, Any]]:
        now = now or utc_now()
        with self.spine.connect() as connection:
            rows = connection.execute(
                """SELECT * FROM memory_records WHERE scope=? AND revoked_at IS NULL
                   AND (expires_at IS NULL OR expires_at>?) ORDER BY rowid""",
                (scope, now),
            ).fetchall()
        return [dict(row) for row in rows]

    def revoke_memory(self, memory_id: str) -> None:
        with self.spine.transaction() as connection:
            updated = connection.execute(
                "UPDATE memory_records SET revoked_at=? WHERE memory_id=? AND revoked_at IS NULL",
                (utc_now(), memory_id),
            )
            if updated.rowcount != 1:
                raise InvariantViolation(f"ERR_MEMORY_NOT_ACTIVE:{memory_id}")
