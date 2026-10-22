"""Q2 — measured proposal for the M4 semantic denominator (SBL DOC 00-13).

Counting rule (reproducible, stated in the output):
  unit      = one addressable clause heading in a frozen DOC whose text starts with an ID token
              (Rnn / Cnn / Unn / Fnn / Gnn / Knn / Pnn, optionally dotted) at heading level 2-4.
  locator   = "<doc file>:<line>" of that heading.
  sub-obl   = a normative sentence inside the unit's body: a sentence containing any of the zh/en
              normative markers below. Mechanical, not semantic interpretation.
  cited_by_build = the unit ID occurs at least once in the SBL worktree outside the DOC set
              (src/tests/evidence_ledger/contracts/skills/openspec/tools). Used as a *trace*
              signal only: a citation is not an oracle and not an acceptance.
  unresolved = a unit carrying >=1 normative sentence AND zero citations in the build tree.

Never claims a total. Prints the exact ceiling sentence.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys

DOCS = r"C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG"
BUILD = r"C:/Projects/Agent_Workspace/_r152_ev"
OUT = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/workers/q2_semantic"

HEAD = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
ID = re.compile(r"^((?:R|C|U|F|G|K|P)\d{2}(?:[A-Z])?(?:\.\d+){0,3})")
NORM = ("必須", "不得", "禁止", "應", "僅", "一律", "shall", "must", "MUST", "SHALL", "never", "cannot", "只能")
SEARCH_EXT = (".py", ".json", ".md", ".yaml", ".yml", ".toml", ".txt")
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", "_governance", "workers", "receipts", "evidence"}


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def build_corpus() -> dict[str, str]:
    """path -> concatenated text of the build tree, for citation lookup."""
    corpus: dict[str, str] = {}
    for root, dirs, files in os.walk(BUILD):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if not fn.endswith(SEARCH_EXT):
                continue
            p = os.path.join(root, fn)
            if p.startswith(DOCS):
                continue
            if os.path.getsize(p) > 4_000_000:
                continue
            try:
                corpus[p] = open(p, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
    return corpus


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    docs = sorted(f for f in os.listdir(DOCS) if f.endswith(".md"))
    corpus = build_corpus()
    blob = "\n".join(corpus.values())
    per_doc, units = [], []
    for name in docs:
        path = os.path.join(DOCS, name)
        text = open(path, encoding="utf-8", errors="ignore").read()
        lines = text.splitlines()
        heads = [(i + 1, m) for i, ln in enumerate(lines) if (m := HEAD.match(ln))]
        doc_units = 0
        for idx, (lineno, m) in enumerate(heads):
            level, title = len(m.group(1)), m.group(2)
            im = ID.match(title)
            if not im:
                continue
            cid = im.group(1)
            end = heads[idx + 1][0] - 1 if idx + 1 < len(heads) else len(lines)
            body = "\n".join(lines[lineno:end])
            sents = [s.strip() for s in re.split(r"(?<=[。；;.!?])\s*|\n", body) if s.strip()]
            norm = [s for s in sents if any(k in s for k in NORM)]
            cited = blob.count(cid)
            units.append({"doc": name, "clause_id": cid, "level": level, "locator": f"{name}:{lineno}",
                          "normative_sentences": len(norm), "cited_by_build": cited,
                          "unresolved": bool(norm) and cited == 0})
            doc_units += 1
        per_doc.append({"doc": name, "sha256": sha256(path), "bytes": os.path.getsize(path),
                        "lines": len(lines), "clause_units": doc_units})
    n_units = len(units)
    unresolved = [u for u in units if u["unresolved"]]
    cited = [u for u in units if u["cited_by_build"] > 0]
    ids = [u["clause_id"] for u in units]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    payload = {
        "schema": "SBL_Q2_SEMANTIC_DENOMINATOR_PROPOSAL/1",
        "measured_at_utc": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip(),
        "counting_rule": "unit = addressable clause heading (level 2-4, ID token R/C/U/F/G/K/P + digits) in a frozen DOC; "
                         "sub-obl = sentence containing a normative marker; cited_by_build = ID occurs in the SBL worktree "
                         "outside the DOC set; unresolved = normative unit with zero build citations.",
        "docs": per_doc,
        "denominator": {
            "identified_semantic_units": n_units,
            "units_with_normative_sentences": sum(1 for u in units if u["normative_sentences"]),
            "normative_sentences_total": sum(u["normative_sentences"] for u in units),
            "units_cited_by_build": len(cited),
            "unresolved_units": len(unresolved),
            "duplicate_clause_ids_across_docs": dupes,
            "authoritative_semantic_total": "NOT_ESTABLISHED",
        },
        "unresolved_index": [{"locator": u["locator"], "clause_id": u["clause_id"],
                              "normative_sentences": u["normative_sentences"]} for u in unresolved],
        "claim_ceiling": "Measured proposal only. This is a mechanical clause census with locators and a citation trace; "
                         "it is not an authoritative semantic total, not an applicability determination and not an acceptance.",
        "full_semantic_pass": False,
    }
    json.dump(payload, open(os.path.join(OUT, "DENOMINATOR_PROPOSAL.json"), "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=2)
    json.dump({"schema": "SBL_Q2_UNIT_INDEX/1", "units": units},
              open(os.path.join(OUT, "UNIT_INDEX.json"), "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=1)
    print(json.dumps(payload["denominator"], ensure_ascii=False, indent=1))
    print(f"Measured proposal only: {n_units} identified semantic units; {len(unresolved)} unresolved obligations; "
          f"authoritative semantic total and FULL_SEMANTIC_PASS not established.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
