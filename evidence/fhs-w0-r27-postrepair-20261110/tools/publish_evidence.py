#!/usr/bin/env python3
"""publish_evidence — copy the round's own artefacts into the SBL payload branch under a size cap.

Why a cap: several evidence lanes kept full copies of the 6 MB blueprints to run prefix/negative tests on
them. Those copies are inputs, not evidence; the driven command, its exit code and its log are the
evidence. Publishing the copies would add ~56 MB of duplicated governed documents to a repo and invite a
reader to treat a copy as an original.

So: every file at or under MAX_BYTES is copied, every skipped file is RECORDED (path, bytes, reason) in
SKIPPED.json beside the manifest - a silent omission would be the same defect this round is repairing.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import sys

SRC = pathlib.Path("C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110")
DST = pathlib.Path("C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-integration/evidence/fhs-w0-r27-postrepair-20261110")
MAX_BYTES = 1_000_000
SKIP_PARTS = {"__pycache__", ".pytest_cache", "mirror_neg"}


def main() -> int:
    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir(parents=True)
    copied, skipped = [], []
    for p in sorted(SRC.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(SRC)
        if any(part in SKIP_PARTS for part in rel.parts) or ("L7" in rel.parts and "neg" in rel.parts):
            skipped.append({"path": rel.as_posix(), "bytes": p.stat().st_size,
                            "why": ("excluded directory" if not ("L7" in rel.parts and "neg" in rel.parts)
                                    else "L7's negative fixtures are byte-copies of governed blueprints; the driven "
                                         "command, exit code and log are published instead")})
            continue
        n = p.stat().st_size
        if n > MAX_BYTES:
            skipped.append({"path": rel.as_posix(), "bytes": n,
                            "why": f"over the {MAX_BYTES} B cap: a copy of a governed input, not evidence"})
            continue
        out = DST / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, out)
        copied.append({"path": rel.as_posix(), "bytes": n,
                       "sha256": hashlib.sha256(out.read_bytes()).hexdigest()})
    man = {"schema": "FHS.R27.PublishedEvidence/1",
           "source_root": str(SRC), "published_root": str(DST),
           "cap_bytes": MAX_BYTES, "files": len(copied), "skipped": len(skipped),
           "note": ("every published file is byte-identical to the file the round produced; a skipped file is listed "
                    "in SKIPPED.json, never dropped silently"),
           "files_index": copied}
    (DST / "PUBLISH_MANIFEST.json").write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    (DST / "SKIPPED.json").write_text(json.dumps({"schema": "FHS.R27.SkippedEvidence/1", "rows": skipped},
                                                 ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"published": len(copied), "skipped": len(skipped),
                      "bytes": sum(c["bytes"] for c in copied)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
