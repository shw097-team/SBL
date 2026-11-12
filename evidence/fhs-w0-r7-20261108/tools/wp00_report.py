#!/usr/bin/env python3
"""WP-00 report writer: turns the source-lock measurement into a lane report.

WP-FHS-00 is the base lane of this round (no subagent), so its report is written
here from the measurement itself rather than transcribed.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys


def sha(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> int:
    round_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    wp = os.path.join(round_dir, "evidence", "WP00")
    lock = json.load(open(os.path.join(wp, "raw", "SOURCE_LOCK.json"), encoding="utf-8"))

    arts = []
    for dirpath, dirnames, filenames in os.walk(wp):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for f in sorted(filenames):
            if f == "REPORT.json":
                continue
            full = os.path.join(dirpath, f)
            arts.append({"path": os.path.relpath(full, round_dir).replace("\\", "/"),
                         "bytes": os.path.getsize(full), "sha256": sha(full)})

    rep = {
        "schema": "FHS.WP00.Report/1",
        "wp": "WP-FHS-00",
        "effect_class": "SOURCE_READ",
        "title": "SourceManifest + RepoContext readback",
        "done_predicate": "SourceManifest + RepoContext readback",
        "status": "MEASURED",
        "generated_at": lock["generated_at"],
        "counts": {
            "sources_declared": lock["counts"]["declared"],
            "sources_match": lock["counts"]["match"],
            "sources_absent": lock["counts"]["absent"],
            "sources_mismatch": lock["counts"]["mismatch"],
            "upper_documents": len(lock["upper_documents"]),
            "upper_documents_match": sum(1 for u in lock["upper_documents"] if u["verdict"] == "MATCH"),
            "repos": len(lock["repositories"]),
        },
        "measurement": {
            "sources": "SHA-256, byte count and line count recomputed from disk for all 31 declared sources and compared with the CH-04 table",
            "upper": "L0, L1, L2, the W0 skeleton, the r6 control document and its r5 parent digested against the frontmatter bindings",
            "repos": "HEAD, branch, origin/main and dirty-path count read from each worktree before any lane ran; this is the baseline G8 compares against",
        },
        "closed_holds": ["H-W0-1"],
        "holds": [],
        "not_claimed": ["ORIGINAL_SOURCE_FREEZE", "OWNER_CURRENTNESS_CONFIRMED", "ORIGINAL_READER_ACK"],
        "claim_ceiling": "AUTHOR_SIDE_SNAPSHOT_VERIFIED",
        "commands": ["python tools/wp00_source_lock.py --out evidence/WP00/raw/SOURCE_LOCK.json"],
        "artifacts": arts,
    }
    json.dump(rep, open(os.path.join(wp, "REPORT.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"WP00 REPORT.json written, {len(arts)} artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
