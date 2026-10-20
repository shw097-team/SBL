"""Slice A acceptance: G-KNOW local-first, source-bound retrieval."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

from sbl_core import gknow
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


def test_the_ids_the_real_corpus_uses_are_recognised():
    """V15-GKNOW-01: a \\b before DOC never matched SBL_PIPD-LS-PKG_DOC-05.md, so every real question refused."""

    for name, expected in {
        "SBL_PIPD-LS-PKG_DOC-05.md": "DOC-05",
        "DOC-00.md": "DOC-00",
        "SBL_PIPD-LS-PKG_DOC-13.md": "DOC-13",
    }.items():
        assert gknow._doc_id_of(name) == expected
    for text in ("what does DOC-05 say", "DOC/27", "DOC--27", "DOC27", "doc_27", "DOC 27"):
        assert gknow._referenced_doc_ids(text), text
        assert gknow._referenced_doc_ids(text) <= {f"DOC-{n:02d}" for n in range(0, 100)}


@pytest.mark.parametrize("text", ["DOC/27", "DOC--27", "DOC27", "doc_27"])
def test_separator_variants_of_an_unknown_source_are_refused(text, corpus, tmp_path):
    """V15-GKNOW-03: DOC/27 and DOC--27 used to slip past the named-source check."""

    index = tmp_path / "i.json"
    gknow.build_index(str(corpus), str(index))
    with pytest.raises(gknow.SBLError) as caught:
        gknow.query(str(index), f"{text} shadow mode rule")
    assert caught.value.code == "SBL_E_KNOWLEDGE_NO_ANSWER"


def test_a_named_source_constrains_the_answer_to_that_source(tmp_path):
    """V15-GKNOW-02: a DOC-05 question was answered from DOC-00 at score 1.0."""

    root = tmp_path / "two"
    root.mkdir()
    (root / "SBL_PIPD-LS-PKG_DOC-00.md").write_text(
        "permission denied for every shadow effect and native permit\n" * 20, encoding="utf-8"
    )
    (root / "SBL_PIPD-LS-PKG_DOC-05.md").write_text(
        "shadow effect description for the governed build bridge\n" * 20, encoding="utf-8"
    )
    index = tmp_path / "two.json"
    gknow.build_index(str(root), str(index))
    hits = gknow.query(str(index), "DOC-05 shadow effect")
    assert hits, "the indexed source must still be answerable"
    assert {os.path.basename(h["path"]) for h in hits} == {"SBL_PIPD-LS-PKG_DOC-05.md"}, [h["path"] for h in hits]
    other = gknow.query(str(index), "DOC-00 permission denied")
    assert other and {os.path.basename(h["path"]) for h in other} == {"SBL_PIPD-LS-PKG_DOC-00.md"}


def test_a_named_source_that_does_not_exist_is_refused(corpus, tmp_path):
    """M3: a question about a DOC that is not in the index must refuse, not answer nearest-neighbour."""

    index = tmp_path / "i-unknown.json"
    build_index(str(corpus), str(index))
    with pytest.raises(SBLError) as caught:
        query(str(index), "DOC-27 says the shadow mode rule is which")
    assert caught.value.code == "SBL_E_KNOWLEDGE_NO_ANSWER"
    assert caught.value.detail["unresolved_doc_ids"] == ["DOC-27"]


def test_a_document_over_the_old_cap_is_indexed(tmp_path):
    """M3: DOC-05 is 2,382,349 B and the 2 MiB cap silently dropped it."""

    root = tmp_path / "big"
    root.mkdir()
    body = "# Native\n\n" + ("native permission denied requires hgk approval\n" * 60000)
    (root / "DOC-05.md").write_text(body, encoding="utf-8")
    assert (root / "DOC-05.md").stat().st_size > 2 * 1024 * 1024
    index = tmp_path / "i-big.json"
    report = build_index(str(root), str(index))
    assert report["files_indexed"] == 1
    assert report["files_skipped"] == 0
    hits = query(str(index), "native permission denied")
    assert hits[0]["path"].endswith("DOC-05.md")
    assert hits[0]["authority"] == "NON_AUTHORITATIVE_LOCATOR"


def test_a_named_source_with_a_coverage_gap_is_refused(tmp_path):
    """M3: an indexed-but-skipped source must answer with a coverage gap, never with a locator."""

    root = tmp_path / "gap"
    root.mkdir()
    (root / "DOC-00.md").write_text("# Router\n\nnative permission denied\n", encoding="utf-8")
    (root / "DOC-05.md").write_text("native permission denied\n", encoding="utf-8")
    index = tmp_path / "i-gap.json"
    build_index(str(root), str(index))
    payload = json.loads(index.read_text(encoding="utf-8"))
    payload["coverage_gaps"] = [
        {"doc_id": "DOC-05", "bytes": 27, "reason": "UNREADABLE:PermissionError"}
    ]
    index.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SBLError) as caught:
        query(str(index), "DOC-05 native permission denied")
    assert caught.value.code == "SBL_E_KNOWLEDGE_COVERAGE_GAP"
    assert caught.value.detail["gap_doc_ids"] == ["DOC-05"]


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
