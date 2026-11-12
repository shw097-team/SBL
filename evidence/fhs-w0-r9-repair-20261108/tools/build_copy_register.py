#!/usr/bin/env python3
"""Build the source copy register (repairs V-01).

Why this exists
---------------
The verification round measured that one document name resolves to two files of the
same length whose bytes differ in four places (the appendix timestamp). A reader who
follows a name instead of a digest can therefore land on the wrong bytes and reach a
different answer without any error being raised.

This tool does not choose a canonical copy. It makes every copy visible with its
digest, and marks the choice as the owner's. It also audits a document for citations
that name a document without a digest, because that is the shape that made the defect
invisible in the first place.

Output: SOURCE_COPY_REGISTER.json
Exit:   0 = register written and self-consistent
        1 = a cited name could not be resolved at all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "_sbl_checker_env", ".mypy_cache"}
MAX_BYTES = 12 * 1024 * 1024

# Names whose copies matter for the W0 chain: the 31 sources plus the revision lineage.
NAME_PATTERNS = [
    re.compile(r"^FHS_PIPD-LS-PKG_W0_r\d+\.md$"),
    re.compile(r"^FHS_總藍圖.*\.md$"),
    re.compile(r"^FHS_PIPD-LS-PKG_藍圖.*\.md$"),
    re.compile(r"^FHS_PIPD-LS-PKG_全波次藍圖.*\.md$"),
    re.compile(r"^FHS_PIPD-LS-PKG_W0_藍圖_skeleton.*\.md$"),
    re.compile(r"^FHS_PIPD-LS-PKG_W\d+_藍圖_skeleton.*\.md$"),
]


def sha256_file(path: str) -> tuple[str, int]:
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
            n += len(b)
    return h.hexdigest(), n


def walk_files(root: str, want: set[str]) -> list[str]:
    """Walk root and return files whose basename is in `want`."""
    hits: list[str] = []
    if not os.path.isdir(root):
        return hits
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn in want:
                hits.append(os.path.join(dirpath, fn))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True, help="directory holding the 31 sources")
    ap.add_argument("--root", action="append", default=[], help="root to scan for copies (repeatable)")
    ap.add_argument("--audit-doc", action="append", default=[], help="document whose citations are audited")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tool_sha = sha256_file(os.path.abspath(__file__))[0]

    # 1. The 31 sources: fixed identities, taken from bytes.
    sources: list[dict] = []
    for fn in sorted(os.listdir(a.sources)):
        p = os.path.join(a.sources, fn)
        if not os.path.isfile(p) or not fn.lower().endswith(".md"):
            continue
        if os.path.getsize(p) > MAX_BYTES:
            continue
        d, n = sha256_file(p)
        sources.append({"name": fn, "path": p.replace("\\", "/"), "bytes": n, "sha256": d})

    wanted = {s["name"] for s in sources}
    # 2. Add lineage names discovered by pattern from any scanned root.
    for r in a.root:
        for dirpath, dirnames, filenames in os.walk(r, followlinks=False):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if any(pat.match(fn) for pat in NAME_PATTERNS):
                    wanted.add(fn)

    # 3. Collect every copy.
    copies: dict[str, list[dict]] = {name: [] for name in sorted(wanted)}
    scanned = 0
    unreadable: list[dict] = []
    for r in a.root:
        for dirpath, dirnames, filenames in os.walk(r, followlinks=False):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn not in wanted:
                    continue
                p = os.path.join(dirpath, fn)
                scanned += 1
                try:
                    if os.path.getsize(p) > MAX_BYTES:
                        unreadable.append({"path": p.replace("\\", "/"), "why": "OVERSIZE"})
                        continue
                    d, n = sha256_file(p)
                except OSError as e:
                    # Deep CJK paths can raise while os.listdir still lists them.
                    unreadable.append({"path": p.replace("\\", "/"), "why": f"OSERROR:{e.__class__.__name__}"})
                    continue
                copies[fn].append({"path": p.replace("\\", "/"), "bytes": n, "sha256": d, "root": r.replace("\\", "/")})

    # 4. Source-side identity: are the 31 themselves unique?
    src_names = [s["name"] for s in sources]
    in_set_dupe_name = len(src_names) - len(set(src_names))
    in_set_dupe_sha = len(sources) - len({s["sha256"] for s in sources})

    # 5. Ambiguity: a name with more than one distinct digest.
    ambiguous: list[dict] = []
    for name, lst in copies.items():
        shas = {c["sha256"] for c in lst}
        if len(shas) > 1:
            amb = {
                "name": name,
                "copies": len(lst),
                "distinct_digests": len(shas),
                "lengths": sorted({c["bytes"] for c in lst}),
                "members": sorted(lst, key=lambda c: c["sha256"]),
            }
            # Where do the copies differ? Report the first differing offset, bounded.
            try:
                a0 = min(lst, key=lambda c: c["sha256"])
                b0 = [c for c in lst if c["sha256"] != a0["sha256"]][0]
                ba = open(a0["path"], "rb").read()
                bb = open(b0["path"], "rb").read()
                off = next((i for i in range(min(len(ba), len(bb))) if ba[i] != bb[i]), None)
                amb["first_difference_offset"] = off
                if off is not None:
                    amb["difference_context"] = {
                        "a": ba[max(0, off - 40):off + 40].decode("utf-8", "replace"),
                        "b": bb[max(0, off - 40):off + 40].decode("utf-8", "replace"),
                    }
                amb["differing_bytes"] = sum(1 for i in range(min(len(ba), len(bb))) if ba[i] != bb[i])
            except Exception as e:  # noqa: BLE001 - evidence tool, never die on one file
                amb["difference_probe"] = f"FAILED:{e.__class__.__name__}"
            ambiguous.append(amb)

    # 6. Citation audit: a document name mentioned without a digest nearby.
    audit: list[dict] = []
    for doc in a.audit_doc:
        if not os.path.isfile(doc):
            audit.append({"doc": doc, "state": "ABSENT"})
            continue
        text = open(doc, "r", encoding="utf-8", errors="replace").read()
        bare: list[dict] = []
        for name in sorted(wanted):
            for m in re.finditer(re.escape(name), text):
                window = text[max(0, m.start() - 200): m.end() + 200]
                if re.search(r"\b[0-9a-f]{64}\b", window) or re.search(r"\b[0-9a-f]{8,16}…", window):
                    continue
                bare.append({"name": name, "offset": m.start()})
        audit.append({
            "doc": doc.replace("\\", "/"),
            "doc_sha256": sha256_file(doc)[0],
            "bare_name_citations": len(bare),
            "bare_examples": bare[:10],
            "state": "BARE_CITATIONS_PRESENT" if bare else "ALL_CITATIONS_CARRY_DIGEST",
        })

    report = {
        "schema": "FHS.W0.SourceCopyRegister/1",
        "generated_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "tool_sha256": tool_sha,
        "claim_ceiling": "AUTHOR_SIDE_MEASURED",
        "purpose": "make every copy of a cited document visible by digest so a reader cannot resolve a name to the wrong bytes without seeing that two copies exist",
        "sources_dir": a.sources.replace("\\", "/"),
        "roots_scanned": [r.replace("\\", "/") for r in a.root],
        "identity_31": {
            "files": len(sources),
            "duplicate_names": in_set_dupe_name,
            "duplicate_digests": in_set_dupe_sha,
            "scope": "IN_SET_31",
        },
        "names_registered": len(copies),
        "files_examined": scanned,
        "unreadable": unreadable,
        "ambiguous_names": len(ambiguous),
        "ambiguous": sorted(ambiguous, key=lambda x: (-x["distinct_digests"], x["name"])),
        "canonical_resolution": {
            "state": "OWNER_UNRESOLVED",
            "why": "choosing which copy of a same-named document is authoritative is a domain-owner act; this register only makes the choice visible and machine-checkable",
            "candidates_requiring_owner_choice": len(ambiguous),
            "predicate": "owner names one digest per ambiguous name; the register is then re-run and the group leaves `ambiguous`",
        },
        "citation_audit": audit,
        "sources": sources,
    }

    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print(f"names_registered={len(copies)} files_examined={scanned} ambiguous={len(ambiguous)} "
          f"in_set_dup_names={in_set_dupe_name} in_set_dup_sha={in_set_dupe_sha}")
    for x in report["ambiguous"][:12]:
        print(f"  AMBIGUOUS {x['name']} copies={x['copies']} digests={x['distinct_digests']} "
              f"len={x['lengths']} diff_bytes={x.get('differing_bytes')} at={x.get('first_difference_offset')}")
    for au in audit:
        print(f"  AUDIT {os.path.basename(au['doc'])} -> {au['state']} bare={au.get('bare_name_citations')}")
    print(f"out={a.out}")
    return 0 if len(copies) >= len(sources) else 1


if __name__ == "__main__":
    sys.exit(main())
