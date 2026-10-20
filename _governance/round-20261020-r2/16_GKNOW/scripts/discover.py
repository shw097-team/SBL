"""Discovery pass: find distinctive ASCII anchors in the 14 authoritative DOC books.

Read-only over the corpus. Prints JSON to stdout so the probe expectations are
derived from the corpus, not from the index (avoids circular expectations).
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict

CORPUS = (
    "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/"
    "Semantic World OS Fabric/SBL"
)
DOC_DIR = os.path.join(CORPUS, "SBL_PIPD-LS-PKG")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IDENT_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+){1,}\b")


def load(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def heading_at(lines, target):
    best = None
    for i, line in enumerate(lines[:target], start=1):
        m = HEADING_RE.match(line)
        if m:
            best = (i, m.group(2).strip())
    return best


def main():
    docs = sorted(
        f for f in os.listdir(DOC_DIR) if f.startswith("SBL_PIPD-LS-PKG_DOC-") and f.endswith(".md")
    )
    ident_counts = defaultdict(Counter)
    for name in docs:
        lines = load(os.path.join(DOC_DIR, name))
        for line in lines:
            for ident in set(IDENT_RE.findall(line)):
                ident_counts[ident][name] += 1

    # Identifiers that live in exactly one DOC book and appear at least twice there.
    unique = {
        ident: {"doc": list(c)[0], "count": sum(c.values())}
        for ident, c in ident_counts.items()
        if len(c) == 1 and sum(c.values()) >= 2 and len(ident) >= 12
    }
    ranked = sorted(unique.items(), key=lambda kv: -kv[1]["count"])[:40]

    report = {"doc_files": docs, "rows": []}
    for ident, meta in ranked:
        path = os.path.join(DOC_DIR, meta["doc"])
        lines = load(path)
        hits = [i for i, line in enumerate(lines, start=1) if ident in line]
        first = hits[0]
        head = heading_at(lines, first)
        report["rows"].append(
            {
                "ident": ident,
                "doc": meta["doc"],
                "count": meta["count"],
                "first_line": first,
                "heading_line": head[0] if head else None,
                "heading": head[1] if head else None,
                "sample": lines[first - 1].strip()[:160],
            }
        )
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
