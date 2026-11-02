#!/usr/bin/env python3
"""Immutable publication-subject attestation (REQ-PIPD-R4-W1 / R3-EXT-01, R-AUD-014).

The projection manifest states, per entry, what the published subject contains. This sidecar adds a
single *immutable* fingerprint of the subject itself: the commit, the tree, the product digest and
the full-tree manifest digest -- so that no local evidence manifest, seal, or report may be read as
a statement about a *different* subject, and any substitution of the subject fails immediately.

A seal for the frozen local candidate (``10cb3d31...`` / tree ``bba26ad0...``) must NEVER verify
against the published subject (``3aebbbce...`` / tree ``1a7dc57f...``).

Self-hash cycle avoidance
-------------------------
The digest is computed over the *payload* (commit, tree, digests, policy, checker identity,
timestamp and the source-manifest seal reference) and then stored **next to** the payload as
``payload_digest`` -- never inside the digested bytes. Verification recomputes the payload hash from
the stored bytes and compares, so tampering with any payload field is detectable, while the digest
itself introduces no fixed point.

Git access is read-only and offline (no ``git`` binary in the writer image): the reader decodes
loose objects in ``.git/objects`` through :mod:`build_publication_manifest`. It never commits,
pushes, checks out, resets or rewrites anything.

Commands
--------
``--build``   write the sidecar ``.hgk/ao/pub/PUBLICATION_SUBJECT_ATTESTATION.json``.
``--verify``  recompute from the local git objects; exit non-zero if commit, tree, product_digest or
              manifest_digest differ (from either the stored sidecar or the expected subject).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_publication_manifest as PM  # noqa: E402

PUB_DIR = ROOT / ".hgk" / "ao" / "pub"
ATTESTATION = PUB_DIR / "PUBLICATION_SUBJECT_ATTESTATION.json"
FROZEN_CANDIDATE = ROOT / ".hgk" / "ao" / "FROZEN_CANDIDATE_R3.json"

SCHEMA = "PIPD-PUBLICATION-SUBJECT-ATTESTATION/1"
POLICY_VERSION = PM.POLICY_VERSION

# Default subject == the published GitHub subject (see the projection manifest).
DEFAULT_COMMIT = PM.PUBLISHED_COMMIT
DEFAULT_TREE = PM.PUBLISHED_TREE


def _checker_identity() -> dict:
    """The independent checker identity bound to the frozen candidate (from FROZEN_CANDIDATE_R3)."""
    fallback = {
        "id": "INDEPENDENT_ACCEPTANCE_OFFICER_R3",
        "model": "unknown",
        "provider": "unknown",
        "role": "VERIFY/SECURITY",
        "independent_of_maker": True,
    }
    if FROZEN_CANDIDATE.exists():
        try:
            data = json.loads(FROZEN_CANDIDATE.read_text(encoding="utf-8"))
            ident = data.get("checker_identity")
            if isinstance(ident, dict):
                return ident
        except Exception:
            pass
    return fallback


def _source_manifest_seal() -> dict:
    """Reference (never a copy) to the local evidence manifest and its seal."""
    seal = PM.EVIDENCE_SEAL
    ref: dict = {
        "path": str(PM.EVIDENCE_MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "sha256": hashlib.sha256(PM.EVIDENCE_MANIFEST.read_bytes()).hexdigest()
        if PM.EVIDENCE_MANIFEST.exists() else None,
        "seal_path": str(seal.relative_to(ROOT)).replace("\\", "/") if seal.exists() else None,
        "seal_sha256": hashlib.sha256(seal.read_bytes()).hexdigest() if seal.exists() else None,
        "seal_candidate": None,
        "bound_to": "local_candidate",
    }
    if seal.exists():
        try:
            ref["seal_candidate"] = json.loads(seal.read_text(encoding="utf-8")).get("candidate")
        except Exception:
            ref["seal_candidate"] = None
    return ref


def build_payload(*, commit: str, tree: str, generated_at: str | None = None) -> dict:
    """The digested payload (everything except the digest itself)."""
    tree_map = PM.walk_tree(tree)
    return {
        "schema": SCHEMA,
        "policy_version": POLICY_VERSION,
        "commit": commit,
        "tree": tree,
        "product_digest": PM.product_digest(tree_map),
        "manifest_digest": PM.manifest_digest(tree_map),
        "checker_identity": _checker_identity(),
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "source_manifest_seal": _source_manifest_seal(),
    }


def _canonical_bytes(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def payload_digest(payload: dict) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def build_document(*, commit: str, tree: str) -> dict:
    payload = build_payload(commit=commit, tree=tree)
    doc = dict(payload)
    doc["payload_digest"] = payload_digest(payload)  # stored NEXT TO the payload, never inside it
    doc["immutable"] = True
    return doc


def verify_document(doc: dict, *, expect_commit: str, expect_tree: str) -> list[str]:
    """Return violations. Empty == the attestation verifies against the expected subject."""
    violations: list[str] = []
    for field in ("commit", "tree", "product_digest", "manifest_digest"):
        if field not in doc:
            violations.append(f"MISSING_FIELD: {field}")
    if violations:
        return violations

    # (a) the stored payload must not have been tampered with.
    stored_payload = {k: v for k, v in doc.items() if k not in ("payload_digest", "immutable")}
    if doc.get("payload_digest") != payload_digest(stored_payload):
        violations.append(
            f"PAYLOAD_TAMPERED: payload_digest {doc.get('payload_digest')} != recomputed "
            f"{payload_digest(stored_payload)}"
        )

    # (b) the stored subject must be the expected subject.
    if doc["commit"] != expect_commit:
        violations.append(f"SUBJECT_COMMIT_MISMATCH: attestation commit {doc['commit']} != expected {expect_commit}")
    if doc["tree"] != expect_tree:
        violations.append(f"SUBJECT_TREE_MISMATCH: attestation tree {doc['tree']} != expected {expect_tree}")

    # (c) recompute the digests from the local git objects for the *attested* subject.
    try:
        tree_map = PM.walk_tree(doc["tree"])
        recomputed_product = PM.product_digest(tree_map)
        recomputed_manifest = PM.manifest_digest(tree_map)
    except PM.GitObjectUnavailable as exc:
        violations.append(f"UNAVAILABLE: {exc}")
        return violations

    if doc["product_digest"] != recomputed_product:
        violations.append(
            f"PRODUCT_DIGEST_MISMATCH: stored {doc['product_digest']} != recomputed {recomputed_product}"
        )
    if doc["manifest_digest"] != recomputed_manifest:
        violations.append(
            f"MANIFEST_DIGEST_MISMATCH: stored {doc['manifest_digest']} != recomputed {recomputed_manifest}"
        )
    return violations


def _resolve(commit: str | None, tree: str | None) -> tuple[str, str]:
    commit = commit or PM.resolve_ref(PM.PUBLISHED_REF)
    tree = tree or PM.commit_tree(commit)
    return commit, tree


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publication subject attestation (REQ-PIPD-R4-W1).")
    parser.add_argument("--build", action="store_true", help="write the immutable sidecar")
    parser.add_argument("--verify", action="store_true", help="recompute and verify; non-zero on mismatch")
    parser.add_argument("--commit", help="subject commit for --build (default: resolve r3-candidate)")
    parser.add_argument("--tree", help="subject tree for --build (default: from --commit)")
    parser.add_argument("--expect-commit", help="subject the sidecar must attest (default: published)")
    parser.add_argument("--expect-tree", help="subject tree the sidecar must attest (default: published)")
    parser.add_argument("--out", help=f"sidecar path (default: {ATTESTATION.relative_to(ROOT)})")
    args = parser.parse_args(argv)

    if not args.build and not args.verify:
        parser.error("at least one of --build / --verify is required")

    out_path = Path(args.out) if args.out else ATTESTATION
    exit_code = 0

    if args.build:
        try:
            commit, tree = _resolve(args.commit, args.tree)
        except PM.GitObjectUnavailable as exc:
            print(json.dumps({"verdict": "FAIL", "reason": str(exc)}), file=sys.stderr)
            return 1
        doc = build_document(commit=commit, tree=tree)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {out_path} (payload_digest={doc['payload_digest']})")

    if args.verify:
        if not out_path.exists():
            print(json.dumps({"verdict": "FAIL", "reason": f"no attestation at {out_path}"}), file=sys.stderr)
            return 1
        doc = json.loads(out_path.read_text(encoding="utf-8"))
        try:
            expect_commit = args.expect_commit or PM.PUBLISHED_COMMIT
            expect_tree = args.expect_tree or PM.PUBLISHED_TREE
        except Exception:
            expect_commit, expect_tree = PM.PUBLISHED_COMMIT, PM.PUBLISHED_TREE
        violations = verify_document(doc, expect_commit=expect_commit, expect_tree=expect_tree)
        report = {
            "verdict": "PASS" if not violations else "FAIL",
            "attested": {"commit": doc.get("commit"), "tree": doc.get("tree")},
            "expected": {"commit": expect_commit, "tree": expect_tree},
            "product_digest": doc.get("product_digest"),
            "manifest_digest": doc.get("manifest_digest"),
            "payload_digest": doc.get("payload_digest"),
            "violations": violations,
        }
        print(json.dumps(report, ensure_ascii=False, indent=1))
        exit_code = 0 if not violations else 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
