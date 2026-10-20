"""Run retrieval probes against index.json via sbl_core.gknow.query.

Expectations are derived from the corpus file itself (anchor line -> enclosing
heading), never from the index, so a probe can fail.

Usage: python run_probes.py
Writes ../probes.json
"""

from __future__ import annotations

import json
import os
import re
import sys
from hashlib import sha256

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(HERE, "index.json")
SPEC = os.path.join(HERE, "probes_spec.json")
OUT = os.path.join(HERE, "probes.json")
CORPUS = (
    "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/"
    "Semantic World OS Fabric/SBL"
)
DOC_DIR = os.path.join(CORPUS, "SBL_PIPD-LS-PKG")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TOP_K = 5
MIN_SCORE = 0.34
REFUSAL = "SBL_E_KNOWLEDGE_NO_ANSWER"

sys.path.insert(0, "C:/Projects/Agent_Workspace/SBL")
import sbl_core.gknow as gknow  # noqa: E402


def file_sha256(path: str) -> str:
    h = sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def expected_heading(path: str, anchor: str) -> dict:
    """Independently derive the enclosing heading for the anchor's first line."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    anchor_line = None
    for i, line in enumerate(lines, start=1):
        if anchor in line:
            anchor_line = i
            break
    if anchor_line is None:
        return {"found": False}
    heading, heading_line = None, None
    for i, line in enumerate(lines[:anchor_line], start=1):
        m = HEADING_RE.match(line)
        if m:
            heading, heading_line = m.group(2).strip(), i
    return {
        "found": True,
        "anchor_line": anchor_line,
        "heading": heading,
        "heading_line": heading_line,
        "occurrences_in_file": sum(1 for line in lines if anchor in line),
    }


def heading_match(top: dict, derived: dict) -> bool:
    """True when the returned chunk covers the heading that governs the anchor line.

    A 40-line chunk can straddle a section boundary: the chunk's own `heading` is
    the entry heading at the chunk start, so either it equals the derived heading
    or the derived heading line falls inside the chunk's own line range.
    """
    if not derived.get("found"):
        return False
    expected_line = derived.get("heading_line")
    expected_text = derived.get("heading")
    if expected_line is None:
        return top.get("heading") is None
    if top.get("heading_line") == expected_line:
        return True
    if expected_text and (top.get("heading") or "") == expected_text:
        return True
    return top["start"] <= expected_line <= top["end"]


def governing_heading(top: dict, anchor_line: int | None) -> str | None:
    """The heading that actually governs the anchor line within the chunk."""
    best = top.get("heading")
    best_line = top.get("heading_line")
    for item in top.get("headings_within_chunk") or []:
        if anchor_line is not None and item["line"] <= anchor_line:
            if best_line is None or item["line"] > best_line:
                best, best_line = item["heading"], item["line"]
    return best


def main() -> int:
    spec = json.load(open(SPEC, encoding="utf-8"))
    probes = []
    pos_pass = neg_pass = 0

    for p in spec["positives"]:
        path = os.path.join(DOC_DIR, p["expected_file"])
        derived = expected_heading(path, p["anchor"])
        record = {
            "id": p["id"],
            "kind": "positive",
            "question": p["question"],
            "query": p["query"],
            "expected": {
                "file": f"SBL_PIPD-LS-PKG/{p['expected_file']}",
                "heading": derived.get("heading"),
                "heading_line": derived.get("heading_line"),
                "anchor": p["anchor"],
                "anchor_line": derived.get("anchor_line"),
                "anchor_occurrences_in_file": derived.get("occurrences_in_file"),
                "basis": "heading derived from corpus file at anchor line, not from the index",
            },
        }
        try:
            hits = gknow.query(INDEX, p["query"], top_k=TOP_K, min_score=MIN_SCORE)
            top = hits[0]
            record["actual"] = {
                "status": "ANSWERED",
                "top1": {
                    "locator": top["locator"],
                    "file": top["path_rel"],
                    "heading": top["heading"],
                    "score": top["score"],
                    "start": top["start"],
                    "end": top["end"],
                    "chunk_sha256": top["chunk_sha256"],
                    "anchor_present_in_chunk": p["anchor"] in top["text"],
                },
                "hit_count": len(hits),
                "all_hits": [
                    {"locator": h["locator"], "score": h["score"], "heading": h["heading"]}
                    for h in hits
                ],
            }
            checks = {
                "file_match": top["path_rel"] == f"SBL_PIPD-LS-PKG/{p['expected_file']}",
                "heading_match": heading_match(top, derived),
                "anchor_in_chunk": p["anchor"] in top["text"],
            }
            record["actual"]["top1"]["governing_heading_for_anchor"] = governing_heading(
                top, derived.get("anchor_line")
            )
            record["checks"] = checks
            record["pass"] = all(checks.values())
        except Exception as exc:  # SBLError refusal
            record["actual"] = {
                "status": "REFUSED",
                "refusal_code": getattr(exc, "code", None),
                "message": getattr(exc, "message", str(exc)),
            }
            record["checks"] = {"answered": False}
            record["pass"] = False
        record["kind"] = "positive"
        if p.get("coverage_gap_probe"):
            record["coverage_gap_probe"] = True
            record["note"] = p.get("note")
        pos_pass += 1 if record["pass"] else 0
        probes.append(record)

    for n in spec["negatives"]:
        record = {
            "id": n["id"],
            "kind": "negative",
            "question": n["question"],
            "query": n["query"],
            "category": n["category"],
            "expected": {"behavior": "REFUSED", "refusal_code": REFUSAL},
        }
        try:
            hits = gknow.query(INDEX, n["query"], top_k=TOP_K, min_score=MIN_SCORE)
            record["actual"] = {
                "status": "ANSWERED",
                "false_accept": True,
                "top1": {
                    "locator": hits[0]["locator"],
                    "file": hits[0]["path_rel"],
                    "heading": hits[0]["heading"],
                    "score": hits[0]["score"],
                },
                "hit_count": len(hits),
            }
            record["pass"] = False
        except Exception as exc:
            record["actual"] = {
                "status": "REFUSED",
                "refusal_code": getattr(exc, "code", None),
                "message": getattr(exc, "message", str(exc)),
            }
            record["pass"] = getattr(exc, "code", None) == REFUSAL
        neg_pass += 1 if record["pass"] else 0
        probes.append(record)

    payload = {
        "schema": "SBL-GKNOW-PROBES/1",
        "index_path": INDEX,
        "index_sha256": file_sha256(INDEX),
        "corpus_root": CORPUS,
        "query_params": {"top_k": TOP_K, "min_score": MIN_SCORE},
        "counts": {
            "positive": len(spec["positives"]),
            "positive_pass": pos_pass,
            "positive_fail": len(spec["positives"]) - pos_pass,
            "negative": len(spec["negatives"]),
            "negative_pass": neg_pass,
            "negative_fail": len(spec["negatives"]) - neg_pass,
            "total": len(probes),
            "total_pass": pos_pass + neg_pass,
        },
        "probes": probes,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    for r in probes:
        print(
            f"{r['id']} {r['kind'][:8]:8s} pass={str(r['pass']):5s} "
            f"{r['actual']['status']:8s} "
            f"{(r['actual'].get('top1', {}) or {}).get('locator', r['actual'].get('refusal_code', ''))}"
        )
    print("COUNTS " + json.dumps(payload["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
