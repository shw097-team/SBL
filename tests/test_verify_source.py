"""VERIFY-01: the source verifier must refuse an empty or incomplete document inventory.

The first independent challenge wrote a receipt with ``docs: []`` and the matching empty
aggregate, and the verifier returned ok=true. An empty inventory is not a pass.
"""

from __future__ import annotations

import json
import sys
from hashlib import sha256
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))

import verify_source  # noqa: E402  (path-managed import on purpose)


def _empty_aggregate() -> str:
    joined = "\n".join(sorted([])) + "\n"
    return sha256(joined.encode("utf-8")).hexdigest()


def _write_record(tmp_path: Path, docs: list[dict]) -> Path:
    payload = {
        "schema": "SBL-SOURCE-VERIFY/1",
        "doc_count": len(docs),
        "aggregate_sha256": verify_source._aggregate([d["sha256"] for d in docs]),
        "docs": docs,
    }
    path = tmp_path / "SOURCE_VERIFY.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_empty_inventory_is_refused(tmp_path):
    empty = {
        "schema": "SBL-SOURCE-VERIFY/1",
        "doc_count": 0,
        "aggregate_sha256": _empty_aggregate(),
        "docs": [],
    }
    path = tmp_path / "EMPTY.json"
    path.write_text(json.dumps(empty), encoding="utf-8")

    report = verify_source.verify(path)
    assert report["ok"] is False
    inventory = [m for m in report["mismatches"] if m.get("doc") == "INVENTORY"]
    assert inventory, "the verifier must flag a missing inventory"
    assert len(inventory[0]["missing_docs"]) == 14


def test_partial_inventory_is_refused(tmp_path):
    real = json.loads((REPO / "evidence" / "source" / "SOURCE_VERIFY.json").read_text(encoding="utf-8"))
    path = _write_record(tmp_path, real["docs"][:3])
    report = verify_source.verify(path)
    assert report["ok"] is False
    assert any(m.get("reason") == "document_inventory" for m in report["mismatches"])


def test_inventory_with_a_wrong_digest_is_refused(tmp_path):
    real = json.loads((REPO / "evidence" / "source" / "SOURCE_VERIFY.json").read_text(encoding="utf-8"))
    docs = [dict(d) for d in real["docs"]]
    docs[0]["sha256"] = "0" * 64
    path = _write_record(tmp_path, docs)
    report = verify_source.verify(path)
    assert report["ok"] is False
    assert any(m.get("reason") == "sha256" for m in report["mismatches"])


def test_cli_exit_code_follows_the_inventory_check(tmp_path):
    empty = tmp_path / "EMPTY.json"
    empty.write_text(
        json.dumps(
            {
                "schema": "SBL-SOURCE-VERIFY/1",
                "doc_count": 0,
                "aggregate_sha256": _empty_aggregate(),
                "docs": [],
            }
        ),
        encoding="utf-8",
    )
    assert verify_source.main(["--verify", "--record", str(empty)]) == 1


def test_real_receipt_passes_when_the_mirror_is_present():
    real = REPO / "evidence" / "source" / "SOURCE_VERIFY.json"
    record = json.loads(real.read_text(encoding="utf-8"))
    if not verify_source.FALLBACK_ROOT.is_dir():
        pytest.skip("source mirror is not mounted on this host")
    report = verify_source.verify(real)
    assert record["doc_count"] == 14
    assert report["ok"] is True, report["mismatches"]


def test_self_check_accepts_the_published_record_without_the_corpus():
    real = REPO / "evidence" / "source" / "SOURCE_VERIFY.json"
    report = verify_source.self_check(real)
    assert report["ok"] is True, report["problems"]
    assert report["byte_verification"].startswith("NOT_PERFORMED")


def test_self_check_catches_a_tampered_digest(tmp_path):
    """The manifest check must be a real check: flipping one digest breaks the aggregate."""

    real = REPO / "evidence" / "source" / "SOURCE_VERIFY.json"
    payload = json.loads(real.read_text(encoding="utf-8"))
    payload["docs"][0]["sha256"] = "0" * 64
    tampered = tmp_path / "SOURCE_VERIFY.json"
    tampered.write_text(json.dumps(payload), encoding="utf-8")
    report = verify_source.self_check(tampered)
    assert report["ok"] is False
    assert any(problem["reason"] == "aggregate_sha256" for problem in report["problems"])
    assert verify_source.main(["--self-check", "--record", str(tampered)]) == 1
