"""Slice A acceptance: G-KNOW local-first, source-bound retrieval."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from sbl_core.errors import SBLError
from sbl_core.gknow import INDEX_SCHEMA, build_index, query

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


@pytest.fixture()
def corpus(tmp_path):
    root = tmp_path / "corpus"
    (root / "nested").mkdir(parents=True)
    (root / "gate.md").write_text(
        "# Gate\n\nevidence denominator must exceed zero\n"
        "self check is forbidden for makers\n",
        encoding="utf-8",
    )
    (root / "nested" / "policy.json").write_text(
        json.dumps({"rule": "shadow mode is read only and has no effect"}),
        encoding="utf-8",
    )
    (root / "ignored.txt").write_text("shadow mode", encoding="utf-8")
    return root


def test_build_index_positive(corpus, tmp_path):
    out = tmp_path / "index" / "gknow.json"
    summary = build_index(str(corpus), str(out))
    assert summary["ok"] is True
    assert summary["schema"] == INDEX_SCHEMA
    assert summary["files_indexed"] == 2
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema"] == INDEX_SCHEMA
    assert payload["chunks"]
    paths = {chunk["path"] for chunk in payload["chunks"]}
    assert all(path.startswith(str(corpus)) for path in paths)
    for chunk in payload["chunks"]:
        assert set(chunk) == {"locator", "path", "start", "end", "sha256", "text"}
        assert chunk["locator"] == f"{chunk['path']}#L{chunk['start']}-{chunk['end']}"
        assert len(chunk["sha256"]) == 64


def test_query_positive_returns_source_bound_hits(corpus, tmp_path):
    out = tmp_path / "gknow.json"
    build_index(str(corpus), str(out))
    hits = query(str(out), "evidence denominator zero", top_k=2)
    assert hits
    assert len(hits) <= 2
    assert hits[0]["locator"].startswith(str(corpus))
    assert "#L" in hits[0]["locator"]
    assert hits[0]["score"] >= 0.34
    assert [hit["score"] for hit in hits] == sorted(
        (hit["score"] for hit in hits), reverse=True
    )


def test_query_negative_no_answer(corpus, tmp_path):
    out = tmp_path / "gknow.json"
    build_index(str(corpus), str(out))
    with pytest.raises(SBLError) as caught:
        query(str(out), "kubernetes ingress certificate rotation")
    assert caught.value.code == "SBL_E_KNOWLEDGE_NO_ANSWER"


def test_query_negative_upper_bound_is_enforced(corpus, tmp_path):
    out = tmp_path / "gknow.json"
    build_index(str(corpus), str(out))
    with pytest.raises(SBLError) as caught:
        query(str(out), "shadow mode read only no effect", min_score=1.01)
    assert caught.value.code == "SBL_E_KNOWLEDGE_NO_ANSWER"


def test_build_index_negative_missing_corpus(tmp_path):
    with pytest.raises(SBLError) as caught:
        build_index(str(tmp_path / "absent"), str(tmp_path / "out.json"))
    assert caught.value.code == "SBL_E_BAD_STATE"


def test_cli_positive_and_refusal_exit_codes(corpus, tmp_path):
    out = tmp_path / "cli-index.json"
    built = subprocess.run(
        [
            sys.executable,
            "-m",
            "sbl_core.gknow",
            "build",
            "--corpus",
            str(corpus),
            "--out",
            str(out),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert built.returncode == 0, built.stderr
    assert json.loads(built.stdout)["ok"] is True

    hit = subprocess.run(
        [
            sys.executable,
            "-m",
            "sbl_core.gknow",
            "query",
            "--index",
            str(out),
            "--text",
            "shadow mode no effect",
            "--json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert hit.returncode == 0, hit.stderr
    assert json.loads(hit.stdout)["ok"] is True

    refused = subprocess.run(
        [
            sys.executable,
            "-m",
            "sbl_core.gknow",
            "query",
            "--index",
            str(out),
            "--text",
            "quantum chromodynamics lattice",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert refused.returncode == 2
    payload = json.loads(refused.stdout)
    assert payload["ok"] is False
    assert payload["code"] == "SBL_E_KNOWLEDGE_NO_ANSWER"
