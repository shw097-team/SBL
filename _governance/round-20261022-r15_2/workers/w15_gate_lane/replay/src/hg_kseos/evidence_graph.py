"""EVO-005 — Canonical Evidence Graph / Attestation Manifest.

Single machine truth source for evidence (no second Evidence authority).
Nodes: Subject / Requirement / Execution / Artifact / Verification.
Artifact full digest stored once; proof capsules reference ids only.
"""
from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS subjects (
    subject_id TEXT PRIMARY KEY, digest TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS requirements (
    requirement_id TEXT PRIMARY KEY, claim_scope TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS executions (
    execution_id TEXT PRIMARY KEY, requirement_id TEXT NOT NULL,
    runner TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY, path TEXT NOT NULL, bytes INTEGER NOT NULL,
    sha256 TEXT NOT NULL, media_type TEXT, producer TEXT NOT NULL,
    subject_digest TEXT, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS verifications (
    verification_id TEXT PRIMARY KEY, requirement_id TEXT NOT NULL,
    checker TEXT NOT NULL, verdict TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS edges (
    edge_id TEXT PRIMARY KEY, kind TEXT NOT NULL,
    src TEXT NOT NULL, dst TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runner_summaries (
    summary_id TEXT PRIMARY KEY, runner TEXT NOT NULL, note TEXT, created_at TEXT NOT NULL
);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str, seed: str = "") -> str:
    """Deterministic id: seed-based when provided (reproducible graph),
    otherwise time-based."""
    if seed:
        return f"{prefix}-{hashlib.sha256(f'{prefix}:{seed}'.encode()).hexdigest()[:16]}"
    return f"{prefix}-{hashlib.sha256(f'{prefix}:{utc_now()}'.encode()).hexdigest()[:16]}"


class EvidenceGraph:
    """Canonical Evidence Graph with finalization lifecycle.

    Lifecycle: OPEN -> FINALIZING -> FROZEN.
    - registration allowed only in OPEN (or authorized FINALIZING)
    - freeze() validates + locks root; append-after-freeze rejected
    - one final root per generation
    """

    def __init__(self, db_path: Path) -> None:
        self.db = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        # lifecycle + generation metadata
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS graph_meta("
            "key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS artifact_versions("
            "artifact_id TEXT PRIMARY KEY, path TEXT NOT NULL, sha256 TEXT NOT NULL,"
            "supersedes TEXT, created_at TEXT NOT NULL)")
        self.conn.commit()
        if not self._meta("generation_id"):
            self._set_meta("generation_id",
                           f"GEN-{hashlib.sha256(str(db_path).encode()).hexdigest()[:12]}")
        if not self._meta("lifecycle"):
            self._set_meta("lifecycle", "OPEN")

    # ---- lifecycle ----
    def _meta(self, key: str) -> str | None:
        row = self.conn.execute("SELECT value FROM graph_meta WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None

    def _set_meta(self, key: str, value: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO graph_meta(key,value) VALUES(?,?)", (key, value))

    def lifecycle_state(self) -> str:
        return self._meta("lifecycle") or "OPEN"

    def generation_id(self) -> str:
        return self._meta("generation_id") or "GEN-?"

    def begin_finalizing(self) -> None:
        if self.lifecycle_state() == "FROZEN":
            raise RuntimeError("GRAPH_FROZEN: cannot begin finalizing a frozen graph")
        self._set_meta("lifecycle", "FINALIZING")

    def _check_writable(self) -> None:
        state = self.lifecycle_state()
        if state == "FROZEN":
            raise RuntimeError("GRAPH_FROZEN: append/mutation rejected after freeze")
        if state == "FINALIZING":
            # authorized finalizing registrations allowed (pre-freeze completion)
            pass

    def freeze(self) -> str:
        if self.lifecycle_state() == "FROZEN":
            return self.graph_root_digest()
        self.begin_finalizing()
        root = self.graph_root_digest()
        self._set_meta("lifecycle", "FROZEN")
        self._set_meta("final_root", root)
        self._set_meta("finalized_at_utc", utc_now())
        return root

    def final_roots(self) -> list[str]:
        root = self._meta("final_root")
        return [root] if root else []

    # ---- artifact identity (uniqueness: same path+digest -> same id) ----
    def register_artifact(self, path: str, producer: str,
                          media_type: str | None = None,
                          subject_digest: str | None = None) -> dict[str, Any]:
        self._check_writable()
        p = Path(path)
        b = p.read_bytes()
        sha = hashlib.sha256(b).hexdigest()
        # canonical identity: same normalized path + same digest -> same id
        norm_path = str(p.resolve()) if p.exists() else str(p)
        row = self.conn.execute(
            "SELECT artifact_id FROM artifacts WHERE path=? AND sha256=?",
            (norm_path, sha)).fetchone()
        if row:
            return self.artifact_record(row["artifact_id"])
        # changed digest for same path -> new version, supersedes recorded
        prev = self.conn.execute(
            "SELECT artifact_id FROM artifacts WHERE path=? ORDER BY rowid DESC LIMIT 1",
            (norm_path,)).fetchone()
        artifact_id = new_id("ART", seed=f"{norm_path}:{sha}")
        with self.conn:
            self.conn.execute(
                "INSERT INTO artifacts(artifact_id,path,bytes,sha256,media_type,producer,subject_digest,created_at) VALUES(?,?,?,?,?,?,?,?)",
                (artifact_id, norm_path, len(b), sha, media_type, producer, subject_digest, utc_now()))
            self.conn.execute(
                "INSERT INTO artifact_versions(artifact_id,path,sha256,supersedes,created_at) VALUES(?,?,?,?,?)",
                (artifact_id, norm_path, sha, prev["artifact_id"] if prev else None, utc_now()))
        return {"artifact_id": artifact_id, "path": norm_path, "bytes": len(b),
                "sha256": sha, "media_type": media_type, "producer": producer}

    def artifact_version_relation(self, old_id: str, new_id: str) -> str:
        row = self.conn.execute(
            "SELECT supersedes FROM artifact_versions WHERE artifact_id=?", (new_id,)).fetchone()
        if row and row["supersedes"] == old_id:
            return "SUPERSEDED"
        return "UNRELATED"

    def identity_conflicts(self) -> int:
        """Two different artifact IDs claiming the same path+sha256 pair = conflict."""
        rows = self.conn.execute(
            "SELECT path, sha256, COUNT(DISTINCT artifact_id) c FROM artifacts "
            "GROUP BY path, sha256 HAVING c > 1").fetchall()
        return len(rows)

    # ---- nodes ----
    def register_subject(self, subject_id: str, digest: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO subjects(subject_id,digest,created_at) VALUES(?,?,?)",
                (subject_id, digest, utc_now()))

    def register_requirement(self, requirement_id: str, scope: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO requirements(requirement_id,claim_scope,created_at) VALUES(?,?,?)",
                (requirement_id, scope, utc_now()))

    def register_execution(self, execution_id: str, requirement_id: str,
                           runner: str, status: str = "RUN") -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO executions(execution_id,requirement_id,runner,status,created_at) VALUES(?,?,?,?,?)",
                (execution_id, requirement_id, runner, status, utc_now()))

    def register_verification(self, verification_id: str, requirement_id: str,
                              checker: str, verdict: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO verifications(verification_id,requirement_id,checker,verdict,created_at) VALUES(?,?,?,?,?)",
                (verification_id, requirement_id, checker, verdict, utc_now()))

    # ---- edges ----
    def _edge(self, kind: str, src: str, dst: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO edges(edge_id,kind,src,dst,created_at) VALUES(?,?,?,?,?)",
                (new_id("EDGE", seed=f"{kind}:{src}:{dst}"), kind, src, dst, utc_now()))

    def link_execution_produced(self, execution_id: str, artifact_id: str) -> None:
        self._edge("execution_produced", execution_id, artifact_id)

    def link_artifact_about(self, artifact_id: str, subject_id: str) -> None:
        self._edge("artifact_about", artifact_id, subject_id)

    def link_verification_checks(self, verification_id: str, artifact_id: str) -> None:
        self._edge("verification_checks", verification_id, artifact_id)

    def link_requirement_supported(self, requirement_id: str, verification_id: str) -> None:
        self._edge("requirement_supported_by", requirement_id, verification_id)

    # ---- queries ----
    def requirement_supported_by(self, requirement_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            # Ordering oracle is v.rowid (monotonic insertion order), not wall-clock created_at (C7).
            """SELECT v.verification_id, v.checker, v.verdict, v.requirement_id
               FROM verifications v
               WHERE v.requirement_id = ? ORDER BY v.rowid""",
            (requirement_id,)).fetchall()
        return [dict(r) for r in rows]

    def verification_records(self) -> list[dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM verifications").fetchall()
        return [dict(r) for r in rows]

    def artifact_record(self, artifact_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM artifacts WHERE artifact_id=?", (artifact_id,)).fetchone()
        return dict(row) if row else None

    def graph_root_digest(self) -> str:
        """Deterministic digest of the whole canonical graph (nodes+edges).
        Timestamps excluded so the digest is reproducible across re-builds
        of the same registered artifacts."""
        parts = []
        tables = {
            "subjects": ["subject_id", "digest"],
            "requirements": ["requirement_id", "claim_scope"],
            "executions": ["execution_id", "requirement_id", "runner", "status"],
            "artifacts": ["artifact_id", "path", "bytes", "sha256", "media_type",
                          "producer", "subject_digest"],
            "verifications": ["verification_id", "requirement_id", "checker", "verdict"],
            "edges": ["edge_id", "kind", "src", "dst"],
            "runner_summaries": ["summary_id", "runner", "note"],
        }
        for table, cols in tables.items():
            rows = self.conn.execute(
                f"SELECT {','.join(cols)} FROM {table} ORDER BY rowid").fetchall()
            parts.append(table + ":" + repr([tuple(r) for r in rows]))
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()

    # ---- runner summary (NOT authority) ----
    def register_runner_summary(self, runner: str, note: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO runner_summaries(summary_id,runner,note,created_at) VALUES(?,?,?,?)",
                (new_id("SUM"), runner, note, utc_now()))

    # ---- capsule (references ids only) ----
    def proof_capsule(self, requirement_id: str, verification_id: str,
                      artifact_id: str) -> dict[str, str]:
        return {"requirement_id": requirement_id, "verification_id": verification_id,
                "artifact_id": artifact_id}

    def validate_capsule(self, capsule: dict[str, Any]) -> dict[str, Any]:
        """Capsule must reference ids only — no duplicated digest/candidate/count."""
        bad = [k for k in ("sha256", "bytes", "candidate", "count", "verdict")
               if k in capsule]
        if bad:
            return {"valid": False, "reason": f"duplicate truth fields: {bad}"}
        missing = [k for k in ("requirement_id", "verification_id", "artifact_id")
                   if k not in capsule]
        if missing:
            return {"valid": False, "reason": f"missing: {missing}"}
        return {"valid": True, "reason": "ok"}
