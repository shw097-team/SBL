"""Coverage + MAX_PATH hypothesis check (read-only)."""

import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = (
    "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/"
    "Semantic World OS Fabric/SBL"
)

cov = json.load(open(os.path.join(HERE, "RUNS", "coverage_report.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(HERE, "index.json"), encoding="utf-8"))
files = {c["path_rel"] for c in idx["chunks"]}

print("chunks", len(idx["chunks"]), "files_with_chunks", len(files))
print(
    "considered_by_suffix", cov["files_considered_by_suffix"],
    "indexed", cov["files_indexed"],
    "skipped", cov["files_skipped"],
)
print("too_large", [t["path"] for t in cov["skipped_too_large"]])
oserr = cov["skipped_os_error"]
lens = [o["path_len"] for o in oserr]
print("os_error", len(oserr), "path_len min/max", min(lens), max(lens))
print("all under GPTs_GENIEMAKER:", all(o["path"].startswith("參考工程資料庫/GPTs_GENIEMAKER") for o in oserr))

docs = sorted(f.split("/")[-1] for f in files if f.startswith("SBL_PIPD-LS-PKG/"))
print("DOC books indexed:", len(docs))
print("missing DOC books:", [
    f"SBL_PIPD-LS-PKG_DOC-{i:02d}.md" for i in range(14)
    if f"SBL_PIPD-LS-PKG_DOC-{i:02d}.md" not in docs
])

sample = oserr[0]["path"]
plain = os.path.join(CORPUS, sample)
ext = "\\\\?\\" + plain.replace("/", "\\")
for label, p in (("plain", plain), ("extended", ext)):
    try:
        print(label, "size", os.path.getsize(p))
    except OSError as exc:
        print(label, "FAIL", exc.errno, exc.strerror)

print("corpus files on disk 306 (verified by find)")
