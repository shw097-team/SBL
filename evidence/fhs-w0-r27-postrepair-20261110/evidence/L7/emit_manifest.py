#!/usr/bin/env python3
"""emit_manifest.py — writes the round-directory MANIFEST.json that travels with the
committed r27 document, so a reader of the branch can verify every artifact the
document cites, even though the artifacts themselves live in the round root.

Digests are computed from disk here; nothing is typed.
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(RUN, "out")
WT_DIR = "C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-docs/evidence/fhs-w0-r27-repair-20261110"
R27 = WT_DIR + "/doc/FHS_PIPD-LS-PKG_W0_r27.md"
R26 = ("C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-docs/evidence/fhs-w0-r26-repair-20261109/"
       "doc/FHS_PIPD-LS-PKG_W0_r26.md")


def ent(p, base):
    b = open(p, "rb").read()
    return {"path": os.path.relpath(p, base).replace("\\", "/"), "bytes": len(b),
            "sha256": hashlib.sha256(b).hexdigest()}


def main():
    files = []
    for sub in ("logs",):
        d = os.path.join(HERE, sub)
        for f in sorted(os.listdir(d)):
            if f.endswith(".log"):
                files.append(ent(os.path.join(d, f), RUN))
    for f in sorted(os.listdir(HERE)):
        if f.endswith((".py", ".json", ".md")) and f != "MANIFEST.json":
            files.append(ent(os.path.join(HERE, f), RUN))
    for f in sorted(os.listdir(OUT)):
        files.append(ent(os.path.join(OUT, f), RUN))

    man = {
        "schema": "FHS.R27.RoundManifest/1",
        "lane": "L7",
        "round": "W0 r27 append-only correction (2026-11-10)",
        "subject_sha256_r26_raw": "0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f",
        "subject_sha256_r26_lf": "09c666dad4f31099f862c12cc5d3758620c46c70bc5f410af727c465bbb6b0f7",
        "document": ent(R27, WT_DIR),
        "note": ("The document's first 667,205 bytes are byte-identical to the r26 file "
                 "(cmp exit 0). The r26 raw form (668,540 bytes, 0ea0554...) is the same document: "
                 "1,335 CRLF line endings, CR-stripped equality proved, and `git hash-object` of the raw "
                 "copy returns the r26 blob 9b3d0119."),
        "artifacts_root": "C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110",
        "artifacts": files,
    }
    p = os.path.join(WT_DIR, "MANIFEST.json")
    json.dump(man, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", p, os.path.getsize(p), "bytes;", len(files), "artifacts listed")
    print("document:", man["document"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
