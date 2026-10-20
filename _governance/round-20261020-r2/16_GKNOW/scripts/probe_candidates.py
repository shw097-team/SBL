"""Candidate probe evaluation: positive anchors (camelCase identifiers) + negative queries."""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(HERE, "index.json")
sys.path.insert(0, "C:/Projects/Agent_Workspace/SBL")
import sbl_core.gknow as gknow  # noqa: E402

TOKEN_RE = re.compile(r"[a-z0-9]+")

POSITIVE_CANDIDATES = [
    "HandoffEnvelope",
    "SourceFreezeManifest",
    "QuestionLedger",
    "AdmissionDecision",
    "TechnologyDispositionCrosswalk",
    "FullScanLocatorIndex",
    "CellRuleProof",
    "OriginalIdentity",
    "DecisionLedger",
    "RouteCard",
    "GoalCard",
    "MethodDecision",
    "SourceClauseLedger",
    "PermitEnvelope",
    "TypedConsumer",
    "ReadThrough",
]

NEGATIVE_CANDIDATES = [
    "",
    "量子退火稀釋冷凍機的低溫恆溫器",
    "dilution refrigerator cryostat helium",
    "thylakoid chlorophyll photosynthesis",
    "SBL_PIPD-LS-PKG_DOC-27 v2099.12.31",
    "SBL_PIPD-LS-PKG_DOC-99 phantom artifact",
    "HGK grants SBL Writer native effect without token",
    "SBL Writer may issue Native Effect without HGK approval",
]


def main() -> int:
    payload = json.load(open(INDEX, encoding="utf-8"))
    chunks = payload["chunks"]

    pos_rows = []
    for name in POSITIVE_CANDIDATES:
        tok = name.lower()
        hits = [
            {"file": c["path_rel"], "heading": c["heading"], "locator": c["locator"], "start": c["start"]}
            for c in chunks
            if tok in set(TOKEN_RE.findall(c["text"].lower()))
        ]
        pos_rows.append({"identifier": name, "token": tok, "chunk_count": len(hits), "hits": hits[:4]})

    neg_rows = []
    for text in NEGATIVE_CANDIDATES:
        row = {"query": text}
        try:
            res = gknow.query(INDEX, text, top_k=3)
            row["outcome"] = "ANSWERED"
            row["hits"] = [
                {"locator": h["locator"], "score": h["score"], "heading": h["heading"]} for h in res
            ]
        except Exception as exc:  # SBLError
            row["outcome"] = "REFUSED"
            row["code"] = getattr(exc, "code", None) or getattr(exc, "error_code", None)
            row["detail"] = str(exc)[:200]
        neg_rows.append(row)

    print(json.dumps({"positives": pos_rows, "negatives": neg_rows}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
