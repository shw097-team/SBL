"""Rare-token analysis: find tokens whose chunk support is tiny (precise anchors)."""

from __future__ import annotations

import json
import os
import re
from collections import defaultdict

INDEX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.json")
TOKEN_RE = re.compile(r"[a-z0-9]+")


def main():
    payload = json.load(open(INDEX, encoding="utf-8"))
    chunks = payload["chunks"]
    support = defaultdict(list)
    for i, chunk in enumerate(chunks):
        for tok in set(TOKEN_RE.findall(chunk["text"].lower())):
            if len(tok) >= 7:
                support[tok].append(i)

    rows = []
    for tok, idxs in support.items():
        if len(idxs) > 2:
            continue
        i = idxs[0]
        c = chunks[i]
        rows.append(
            {
                "token": tok,
                "chunk_count": len(idxs),
                "file": c["path_rel"],
                "heading": c["heading"],
                "locator": c["locator"],
                "sample": c["text"][:120].replace("\n", " "),
            }
        )
    rows.sort(key=lambda r: (r["file"], r["token"]))
    by_file = defaultdict(list)
    for row in rows:
        by_file[row["file"]].append(row)
    print(json.dumps({"rare_token_rows": len(rows), "by_file": by_file}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
