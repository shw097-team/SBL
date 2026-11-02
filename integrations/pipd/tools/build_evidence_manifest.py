#!/usr/bin/env python3
"""Build, seal and verify the evidence manifest (R-AUD-014 / WO-TS-req-pipd-r3-fw-11).

Repairs two audited defects:

1. **self-hash cycle** — the old manifest listed its own file (and a bare path list was treated as
   independent evidence). The manifest now applies a canonical self-exclusion: it NEVER lists or
   hashes itself, nor its own outer seal file. A manifest that references either is refused.
2. **no freshness outer seal** — an outer immutable seal is written next to the manifest recording
   the manifest's byte-level sha256, the seal algorithm and the candidate tuple (repo commit sha,
   candidate tree sha, stage, policy version). Sealing does not change the manifest bytes.

Commands
--------
``--seal``    regenerate the manifest and its seal from the current tree.
``--verify``  read the manifest bytes back, recompute the sha256 and compare against the seal; also
              refuse a manifest that references itself or a seal bound to a foreign/stale candidate
              head (typed reason).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / ".hgk" / "artifacts"
MANIFEST = ART / "evidence_manifest.json"
SEAL = ART / "evidence_manifest.seal.json"

SEAL_ALGORITHM = "sha256"
SCHEMA = "PIPD-EVIDENCE-MANIFEST-SEAL/1"


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True).stdout.strip()


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return _sha256_bytes(p.read_bytes())


def _excluded_paths() -> set[Path]:
    """Canonical self-exclusion: the manifest and its seal are never listed or hashed."""
    return {MANIFEST.resolve(), SEAL.resolve()}


def iter_files() -> list[Path]:
    excluded = _excluded_paths()
    out: list[Path] = []
    for f in sorted(ROOT.rglob("*")):
        if not f.is_file():
            continue
        if ".git" in f.parts or "__pycache__" in f.parts or f.suffix in (".db", ".pyc"):
            continue
        if f.resolve() in excluded:
            continue
        out.append(f)
    return out


def build_entries() -> dict[str, str]:
    man: dict[str, str] = {}
    for f in iter_files():
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        man[rel] = sha256_file(f)
    return man


def manifest_bytes(entries: dict[str, str]) -> bytes:
    """Byte-deterministic manifest serialization (no timestamp, sorted keys)."""
    return json.dumps(entries, indent=0, sort_keys=True).encode("utf-8")


def write_manifest() -> bytes:
    entries = build_entries()
    data = manifest_bytes(entries)
    MANIFEST.write_bytes(data)
    return data


def _round_state() -> dict:
    p = ROOT / ".hgk" / "rounds" / "R3-20261009-audit-repair" / "ROUND_STATE.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def candidate_tuple() -> dict:
    """The candidate tuple the seal binds to: repo commit sha, candidate tree sha, stage, policy."""
    rs = _round_state()
    ft = rs.get("frozen_tuple", {}) if isinstance(rs, dict) else {}
    policy = ft.get("policy_version")
    if not policy:
        frozen = ROOT / ".hgk" / "ao" / "FROZEN_CANDIDATE_R3.json"
        if frozen.exists():
            try:
                policy = json.loads(frozen.read_text(encoding="utf-8")).get("policy_version")
            except Exception:
                policy = None
    return {
        "repo_commit_sha": _git("rev-parse", "HEAD"),
        "candidate_tree_sha": _git("rev-parse", "HEAD^{tree}"),
        "stage": (rs.get("stage") if isinstance(rs, dict) else None) or "S0-S4",
        "policy_version": policy or "UNKNOWN_POLICY",
    }


def seal_bytes(data: bytes, cand: dict, *, entries: int) -> bytes:
    """The outer seal document binding the manifest bytes to a candidate tuple."""
    seal = {
        "schema": SCHEMA,
        "seal_algorithm": SEAL_ALGORITHM,
        "manifest": {
            "path": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
            "sha256": _sha256_bytes(data),
            "bytes": len(data),
            "entries": entries,
        },
        "candidate": cand,
        "sealed_at": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(seal, ensure_ascii=False, indent=1).encode("utf-8")


def seal() -> dict:
    data = write_manifest()
    entries = json.loads(data.decode("utf-8"))
    cand = candidate_tuple()
    seal_doc = json.loads(seal_bytes(data, cand, entries=len(entries)).decode("utf-8"))
    SEAL.write_bytes(json.dumps(seal_doc, ensure_ascii=False, indent=1).encode("utf-8"))
    return {
        "manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "seal": str(SEAL.relative_to(ROOT)).replace("\\", "/"),
        "entries": len(entries),
        "manifest_sha256": seal_doc["manifest"]["sha256"],
        "manifest_bytes": seal_doc["manifest"]["bytes"],
        "seal_algorithm": SEAL_ALGORITHM,
        "candidate": cand,
    }


def verify(manifest_path: Path = MANIFEST, seal_path: Path = SEAL,
           head: str | None = None) -> dict:
    """Read the manifest bytes back, recompute the sha256 and compare against the seal.

    Returns a typed result; ``status`` is ``PASS`` only when the manifest is non-self-referential,
    its byte-level sha256 matches the seal, and the seal's candidate head equals the current head.
    """
    if not manifest_path.exists():
        return {"status": "FAIL", "reason_code": "MISSING_MANIFEST",
                "detail": f"{manifest_path} does not exist"}
    if not seal_path.exists():
        return {"status": "FAIL", "reason_code": "MISSING_SEAL",
                "detail": f"{seal_path} does not exist"}

    data = manifest_path.read_bytes()
    try:
        entries = json.loads(data.decode("utf-8"))
    except Exception as exc:
        return {"status": "FAIL", "reason_code": "MALFORMED_MANIFEST", "detail": str(exc)}
    if not isinstance(entries, dict):
        return {"status": "FAIL", "reason_code": "MALFORMED_MANIFEST",
                "detail": "manifest must be an object of path -> sha256"}

    # 1. canonical self-exclusion: never reference the manifest or its seal.
    def _self_key(p: Path) -> str:
        try:
            return p.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            return p.name

    forbidden = {_self_key(manifest_path), _self_key(seal_path)}
    self_refs = sorted(p for p in entries if p in forbidden)
    if self_refs:
        return {"status": "FAIL", "reason_code": "SELF_REFERENTIAL_MANIFEST",
                "detail": f"manifest references its own path(s): {self_refs}"}

    try:
        seal_doc = json.loads(seal_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "FAIL", "reason_code": "MALFORMED_SEAL", "detail": str(exc)}

    # 2. byte-level readback of the manifest against the seal.
    recorded = seal_doc.get("manifest", {}).get("sha256")
    actual = _sha256_bytes(data)
    if recorded != actual:
        return {"status": "FAIL", "reason_code": "MANIFEST_HASH_MISMATCH",
                "detail": f"seal records {recorded}, recomputed {actual}"}

    # 3. freshness: the seal's candidate head must match the current candidate head.
    current = head if head is not None else _git("rev-parse", "HEAD")
    sealed_head = (seal_doc.get("candidate") or {}).get("repo_commit_sha")
    if sealed_head != current:
        return {"status": "FAIL", "reason_code": "REFUSED_STALE_OR_FOREIGN_MANIFEST",
                "detail": f"seal candidate head {sealed_head} != current head {current}"}

    return {"status": "PASS", "reason_code": "OK",
            "detail": f"{len(entries)} entries; manifest sha256 {actual} matches the seal",
            "manifest_sha256": actual, "seal_algorithm": seal_doc.get("seal_algorithm"),
            "candidate": seal_doc.get("candidate"), "entries": len(entries)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Evidence manifest self-exclusion + outer seal.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--seal", action="store_true", help="regenerate the manifest and its seal")
    g.add_argument("--verify", action="store_true",
                   help="read back the bytes, recompute sha256 and compare against the seal")
    args = ap.parse_args(argv)

    ART.mkdir(parents=True, exist_ok=True)
    if args.seal:
        result = seal()
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 0

    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=1))
    if result["status"] == "PASS":
        return 0
    if result["reason_code"] == "REFUSED_STALE_OR_FOREIGN_MANIFEST":
        return 3
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
