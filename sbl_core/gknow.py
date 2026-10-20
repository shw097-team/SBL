"""G-KNOW: local-first, source-bound knowledge index and query."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from hashlib import sha256
from typing import Any, Iterable, Iterator

from .errors import SBLError

INDEX_SCHEMA = "SBL-GKNOW-INDEX/1"
# 2 MiB silently dropped DOC-05 (2,382,349 B) out of the corpus, so a query about it returned a
# confident wrong locator instead of a refusal (external acceptance report R1, D3). The cap now sits
# above the largest authoritative book and every skip is recorded as a coverage gap.
MAX_FILE_BYTES = 8 * 1024 * 1024
CHUNK_LINES = 40
SUFFIXES = (".md", ".json")
TOKEN_RE = re.compile(r"[a-z0-9]+")
# A source id a reader can name in a question ("what does DOC-05 say", "DOC-27", "DOC_99").
DOC_ID_RE = re.compile(r"\bdoc[-_ ]?(\d{1,3})\b", re.IGNORECASE)


def _iter_corpus_files(corpus_root: str) -> Iterator[str]:
    for current, dirnames, filenames in os.walk(corpus_root):
        dirnames.sort()
        for filename in sorted(filenames):
            if filename.lower().endswith(SUFFIXES):
                yield os.path.join(current, filename)


def _chunks_for(path: str) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        lines = handle.read().splitlines()
    buffer: list[tuple[int, str]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        buffer.append((line_number, line))
        if len(buffer) == CHUNK_LINES:
            yield _chunk(path, buffer)
            buffer = []
    if buffer:
        yield _chunk(path, buffer)


def _chunk(path: str, buffer: list[tuple[int, str]]) -> dict[str, Any]:
    start = buffer[0][0]
    end = buffer[-1][0]
    text = "\n".join(line for _, line in buffer)
    return {
        "locator": f"{path}#L{start}-{end}",
        "path": path,
        "start": start,
        "end": end,
        "sha256": sha256(text.encode("utf-8")).hexdigest(),
        "text": text,
    }


def build_index(corpus_root: str, out_path: str) -> dict[str, Any]:
    """Indexes ``**/*.md`` and ``**/*.json`` under ``corpus_root`` into JSON."""

    if not corpus_root or not os.path.isdir(corpus_root):
        raise SBLError(
            "SBL_E_BAD_STATE",
            "corpus root is not a directory",
            {"corpus_root": corpus_root},
        )
    root = os.path.abspath(corpus_root)
    chunks: list[dict[str, Any]] = []
    files_indexed = 0
    files_skipped = 0
    coverage_gaps: list[dict[str, Any]] = []
    for path in _iter_corpus_files(root):
        try:
            size = os.path.getsize(path)
            if size > MAX_FILE_BYTES:
                files_skipped += 1
                coverage_gaps.append(
                    {"doc_id": _doc_id_of(path), "bytes": size, "reason": "OVER_MAX_FILE_BYTES"}
                )
                continue
        except OSError as exc:
            files_skipped += 1
            coverage_gaps.append(
                {"doc_id": _doc_id_of(path), "bytes": None, "reason": f"UNREADABLE:{type(exc).__name__}"}
            )
            continue
        try:
            file_chunks = list(_chunks_for(path))
        except OSError as exc:
            files_skipped += 1
            coverage_gaps.append(
                {"doc_id": _doc_id_of(path), "bytes": size, "reason": f"UNREADABLE:{type(exc).__name__}"}
            )
            continue
        files_indexed += 1
        chunks.extend(file_chunks)
    payload = {"schema": INDEX_SCHEMA, "chunks": chunks, "coverage_gaps": coverage_gaps}
    parent = os.path.dirname(os.path.abspath(out_path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=1, sort_keys=True)
        handle.write("\n")
    return {
        "ok": True,
        "schema": INDEX_SCHEMA,
        "corpus_root": root,
        "out_path": os.path.abspath(out_path),
        "files_indexed": files_indexed,
        "files_skipped": files_skipped,
        "coverage_gaps": coverage_gaps,
        "chunks": len(chunks),
    }


def _doc_id_of(path: str) -> str | None:
    """The DOC-NN identity carried by a corpus file name, if it carries one."""
    match = DOC_ID_RE.search(os.path.basename(path))
    return f"DOC-{int(match.group(1)):02d}" if match else None


def _referenced_doc_ids(text: str) -> set[str]:
    return {f"DOC-{int(match.group(1)):02d}" for match in DOC_ID_RE.finditer(str(text))}


def _tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(str(text).lower()))


def _load_chunks_and_gaps(index_path: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payload = _load_payload(index_path)
    chunks = payload.get("chunks")
    gaps = payload.get("coverage_gaps")
    return (
        chunks if isinstance(chunks, list) else [],
        [gap for gap in gaps if isinstance(gap, dict)] if isinstance(gaps, list) else [],
    )


def _load_payload(index_path: str) -> dict[str, Any]:
    try:
        with open(index_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as exc:
        raise SBLError(
            "SBL_E_BAD_STATE",
            "knowledge index cannot be read",
            {"index_path": index_path, "error": str(exc)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise SBLError(
            "SBL_E_BAD_STATE",
            "knowledge index is not valid JSON",
            {"index_path": index_path, "error": str(exc)},
        ) from exc
    if not isinstance(payload, dict) or payload.get("schema") != INDEX_SCHEMA:
        raise SBLError(
            "SBL_E_BAD_STATE",
            "knowledge index schema mismatch",
            {"index_path": index_path, "expected": INDEX_SCHEMA},
        )
    return payload


def query(
    index_path: str, text: str, top_k: int = 5, min_score: float = 0.34
) -> list[dict[str, Any]]:
    """Token-overlap retrieval; refuses rather than fabricating a hit."""

    query_tokens = _tokens(text)
    if not query_tokens:
        raise SBLError(
            "SBL_E_KNOWLEDGE_NO_ANSWER",
            "query has no searchable tokens",
            {"text": str(text)},
        )
    chunks, gaps = _load_chunks_and_gaps(index_path)
    referenced = _referenced_doc_ids(text)
    indexed_ids = {_doc_id_of(str(chunk.get("source", chunk.get("path", "")))) for chunk in chunks}
    indexed_ids.discard(None)
    gap_ids = {gap.get("doc_id") for gap in gaps if gap.get("doc_id")}
    # A named source that is not in the index must be a refusal, not a nearest-neighbour answer:
    # token overlap happily returns DOC-00 for a question about a DOC-27 that never existed.
    unknown = sorted(referenced - indexed_ids - gap_ids)
    if unknown:
        raise SBLError(
            "SBL_E_KNOWLEDGE_NO_ANSWER",
            "the question names a source id that is not in the index",
            {"unresolved_doc_ids": unknown, "indexed_doc_ids": sorted(indexed_ids)},
        )
    covered_gaps = sorted(referenced & gap_ids)
    if covered_gaps:
        raise SBLError(
            "SBL_E_KNOWLEDGE_COVERAGE_GAP",
            "the named source exists but was not indexed, so it cannot be answered",
            {"gap_doc_ids": covered_gaps, "gaps": [g for g in gaps if g.get("doc_id") in covered_gaps]},
        )
    scored: list[dict[str, Any]] = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        overlap = query_tokens & _tokens(chunk.get("text", ""))
        score = len(overlap) / len(query_tokens)
        if score < min_score:
            continue
        hit = dict(chunk)
        hit["score"] = round(float(score), 6)
        # Retrieval is a locator, never an authority: a hit is not entailment, not an Oracle and not
        # an approval (external acceptance report R1, D3).
        hit["authority"] = "NON_AUTHORITATIVE_LOCATOR"
        scored.append(hit)
    if not scored or max(hit["score"] for hit in scored) < min_score:
        raise SBLError(
            "SBL_E_KNOWLEDGE_NO_ANSWER",
            "no indexed chunk meets the minimum score",
            {"text": str(text), "min_score": min_score, "chunks": len(chunks)},
        )
    scored.sort(key=lambda hit: (-hit["score"], str(hit.get("locator", ""))))
    return scored[: max(int(top_k), 0)]


def _build_cli(args: argparse.Namespace) -> int:
    summary = build_index(args.corpus, args.out)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


def _query_cli(args: argparse.Namespace) -> int:
    hits = query(args.index, args.text, top_k=args.top_k, min_score=args.min_score)
    print(json.dumps({"ok": True, "hits": hits}, ensure_ascii=False, sort_keys=True))
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m sbl_core.gknow")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="build a source-bound index")
    build.add_argument("--corpus", required=True)
    build.add_argument("--out", required=True)
    build.set_defaults(handler=_build_cli)

    find = sub.add_parser("query", help="query a built index")
    find.add_argument("--index", required=True)
    find.add_argument("--text", required=True)
    find.add_argument("--top-k", type=int, default=5)
    find.add_argument("--min-score", type=float, default=0.34)
    find.add_argument("--json", action="store_true")
    find.set_defaults(handler=_query_cli)

    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        return int(args.handler(args))
    except SBLError as exc:
        print(json.dumps(exc.as_dict(), ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
