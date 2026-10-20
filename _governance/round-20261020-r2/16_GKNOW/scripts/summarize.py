"""Final accounting: per-file chunk stats, query latency, checksums, summary.json."""

import json
import os
import subprocess
import sys
import time
from collections import Counter
from hashlib import sha256

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(HERE, "index.json")
PROBES = os.path.join(HERE, "probes.json")
PY = sys.executable


def sha(path):
    h = sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


idx = json.load(open(INDEX, encoding="utf-8"))
probes = json.load(open(PROBES, encoding="utf-8"))
chunks = idx["chunks"]

per_doc = Counter(c["path_rel"] for c in chunks if c["path_rel"].startswith("SBL_PIPD-LS-PKG/"))
top_files = Counter(c["path_rel"] for c in chunks).most_common(5)

# Query latency: one cold subprocess call (index load dominates).
code = (
    "import sys,time;sys.path.insert(0,'C:/Projects/Agent_Workspace/SBL');"
    "import sbl_core.gknow as g;"
    "t=time.time();g.query(%r,'FullScanLocatorIndex',top_k=5);"
    "print(round(time.time()-t,3))" % INDEX
)
start = time.time()
out = subprocess.run([PY, "-c", code], capture_output=True, text=True)
latency = out.stdout.strip()
wall = round(time.time() - start, 3)

summary = {
    "schema": "SBL-GKNOW-RUN-SUMMARY/1",
    "index_path": INDEX,
    "index_sha256": sha(INDEX),
    "index_bytes": os.path.getsize(INDEX),
    "probes_path": PROBES,
    "probes_sha256": sha(PROBES),
    "probes_bytes": os.path.getsize(PROBES),
    "corpus_file_count": idx["corpus_file_count_total"],
    "files_considered_by_suffix": idx["files_considered_by_suffix"],
    "files_indexed": idx["files_indexed"],
    "files_skipped": idx["files_skipped"],
    "files_skipped_too_large": len(idx["files_skipped_too_large"]),
    "files_skipped_os_error": len(idx["files_skipped_os_error"]),
    "files_undecodable": len(idx["files_undecodable"]),
    "files_with_replacement_chars": len(idx["files_with_replacement_chars"]),
    "chunks": len(chunks),
    "chunk_lines": idx["chunk_lines"],
    "counts": probes["counts"],
    "single_query_latency_seconds": latency,
    "single_query_wall_seconds": wall,
    "query_stderr": out.stderr.strip()[:400],
    "per_doc_book_chunks": dict(sorted(per_doc.items())),
    "top_files_by_chunks": top_files,
}
path = os.path.join(HERE, "RUNS", "summary.json")
with open(path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=1, sort_keys=True)
    fh.write("\n")
print(json.dumps(summary, ensure_ascii=False, indent=1, sort_keys=True))
