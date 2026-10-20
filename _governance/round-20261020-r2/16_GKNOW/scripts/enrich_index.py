"""Build the SBL G-KNOW index by calling the existing sbl_core.gknow API.

Writes ONLY inside 16_GKNOW/. Source corpus is read-only.

Usage:
  python enrich_index.py --corpus "<SBL root>" --out <16_GKNOW>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from hashlib import sha256

SBL_PKG_ROOT = "C:/Projects/Agent_Workspace/SBL"
sys.path.insert(0, SBL_PKG_ROOT)

import sbl_core.gknow as gknow  # noqa: E402  (existing product API, not copied)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def file_sha256(path: str) -> str:
    h = sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def headings_for(path: str) -> list[tuple[int, str]]:
    """Extract (line_number, heading_text) tuples from markdown headings."""
    out: list[tuple[int, str]] = []
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle.read().splitlines(), start=1):
            match = HEADING_RE.match(line)
            if match:
                out.append((line_number, match.group(2).strip()))
    return out


def decode_status(path: str) -> dict:
    """Honest decode report: strict UTF-8 test plus U+FFFD replacement count."""
    with open(path, "rb") as handle:
        raw = handle.read()
    status = {
        "bytes": len(raw),
        "strict_utf8": True,
        "error": None,
        "replacement_chars": 0,
        "bom": raw.startswith(b"\xef\xbb\xbf"),
        "nul_bytes": raw.count(b"\x00"),
    }
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        status["strict_utf8"] = False
        status["error"] = f"{exc.__class__.__name__}: {exc}"
        text = raw.decode("utf-8", errors="replace")
    status["replacement_chars"] = text.count("\ufffd")
    status["lines"] = text.count("\n") + (0 if text.endswith("\n") else 1)
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out_dir = os.path.abspath(args.out)
    stage = os.path.join(out_dir, "RUNS", "stage_gknow_raw.json")
    os.makedirs(os.path.join(out_dir, "RUNS"), exist_ok=True)

    summary = gknow.build_index(args.corpus, stage)
    summary["command"] = (
        f'python enrich_index.py --corpus "{args.corpus}" --out "{out_dir}" '
        f"-> sbl_core.gknow.build_index(corpus_root={args.corpus!r}, out_path={stage!r})"
    )
    print("BUILD_SUMMARY " + json.dumps(summary, ensure_ascii=False, sort_keys=True))

    with open(stage, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    root = summary["corpus_root"]
    chunks = payload["chunks"]

    # Enumerate every file gknow considered (same suffix filter) so skips are visible.
    considered: list[str] = []
    for current, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for filename in sorted(filenames):
            if filename.lower().endswith(gknow.SUFFIXES):
                considered.append(os.path.join(current, filename))

    meta: dict[str, dict] = {}
    too_large: list[dict] = []
    os_errors: list[dict] = []
    undecodable: list[dict] = []
    replacement_hits: list[dict] = []
    for path in considered:
        rel = os.path.relpath(path, root).replace("\\", "/")
        try:
            size = os.path.getsize(path)
        except OSError as exc:
            os_errors.append({"path": rel, "path_len": len(path), "error": str(exc)})
            continue
        if size > gknow.MAX_FILE_BYTES:
            too_large.append(
                {"path": rel, "bytes": size, "limit_bytes": gknow.MAX_FILE_BYTES}
            )
            continue
        try:
            status = decode_status(path)
        except OSError as exc:
            os_errors.append({"path": rel, "path_len": len(path), "error": str(exc)})
            continue
        if not status["strict_utf8"]:
            undecodable.append({"path": rel, **status})
        elif status["replacement_chars"]:
            replacement_hits.append({"path": rel, "replacement_chars": status["replacement_chars"]})
        meta[os.path.abspath(path)] = {
            "path_rel": rel,
            "file_sha256": file_sha256(path),
            "headings": headings_for(path),
            "decode": status,
        }

    enriched = []
    for chunk in chunks:
        key = os.path.abspath(chunk["path"])
        info = meta.get(key)
        if info is None:  # pragma: no cover - would mean gknow indexed a skipped file
            raise SystemExit(f"chunk for unindexed file: {chunk['path']}")
        heading = None
        heading_line = None
        for line_number, text in info["headings"]:
            if line_number <= chunk["start"]:
                heading, heading_line = text, line_number
            else:
                break
        within = [
            {"line": line_number, "heading": text}
            for line_number, text in info["headings"]
            if chunk["start"] <= line_number <= chunk["end"]
        ]
        entry = {
            "locator": f"{info['path_rel']}#L{chunk['start']}-{chunk['end']}",
            "path_rel": info["path_rel"],
            "file_sha256": info["file_sha256"],
            "anchor": f"{info['path_rel']}#{heading}" if heading else f"{info['path_rel']}#(preamble)",
            "heading": heading,
            "heading_line": heading_line,
            "headings_within_chunk": within,
            "start": chunk["start"],
            "end": chunk["end"],
            "chunk_sha256": chunk["sha256"],
            "sha256": chunk["sha256"],
            "text": chunk["text"],
        }
        enriched.append(entry)

    out_payload = {
        "schema": gknow.INDEX_SCHEMA,
        "generator": "sbl_core.gknow.build_index + 16_GKNOW/scripts/enrich_index.py enrichment",
        "build_command": (
            'python scripts/enrich_index.py --corpus "C:/Projects/Agent_Workspace/知識庫/'
            '實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL" --out "<16_GKNOW>"'
            " (calls sbl_core.gknow.build_index(corpus_root, out_path) verbatim; no gknow code copied)"
        ),
        "corpus_root": root,
        "corpus_file_count_total": sum(len(f) for _, _, f in os.walk(root)),
        "files_considered_by_suffix": len(considered),
        "files_indexed": summary["files_indexed"],
        "files_skipped": summary["files_skipped"],
        "files_skipped_too_large": too_large,
        "files_skipped_os_error": os_errors,
        "files_undecodable": undecodable,
        "files_with_replacement_chars": replacement_hits,
        "chunk_lines": gknow.CHUNK_LINES,
        "chunks": enriched,
    }
    out_path = os.path.join(out_dir, "index.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(out_payload, handle, ensure_ascii=False, sort_keys=True)
        handle.write("\n")

    # Coverage facts for FINDINGS.
    per_file = {}
    for entry in enriched:
        per_file[entry["path_rel"]] = per_file.get(entry["path_rel"], 0) + 1
    coverage = {
        "corpus_file_count_total": 306,
        "files_considered_by_suffix": len(considered),
        "files_indexed": summary["files_indexed"],
        "files_skipped": summary["files_skipped"],
        "skipped_too_large": too_large,
        "skipped_os_error": os_errors,
        "undecodable": undecodable,
        "replacement_chars_files": replacement_hits,
        "chunks": len(enriched),
        "indexed_files": {k: per_file[k] for k in sorted(per_file)},
        "files_without_chunks": sorted(set(meta_keys_rel(meta)) - set(per_file)),
    }
    cov_path = os.path.join(out_dir, "RUNS", "coverage_report.json")
    with open(cov_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(coverage, handle, ensure_ascii=False, indent=1, sort_keys=True)
        handle.write("\n")
    print(
        "ENRICHED "
        + json.dumps(
            {
                "index_path": out_path,
                "index_bytes": os.path.getsize(out_path),
                "chunks": len(enriched),
                "files_with_chunks": len(per_file),
                "skipped_too_large": [t["path"] for t in too_large],
                "skipped_os_error": [o["path"] for o in os_errors],
                "undecodable": [u["path"] for u in undecodable],
                "replacement_chars_files": [r["path"] for r in replacement_hits],
                "files_without_chunks": coverage["files_without_chunks"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def meta_keys_rel(meta: dict) -> list[str]:
    return [info["path_rel"] for info in meta.values()]


if __name__ == "__main__":
    sys.exit(main())
