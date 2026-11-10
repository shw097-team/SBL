"""Measure the L1 blueprint with the r26 round's own conventions. Read-only."""
from __future__ import annotations

import hashlib
import json
import os
import sys

for p in sys.argv[1:]:
    b = open(p, "rb").read()
    print(json.dumps({"path": p,
                      "st_size": os.stat(p).st_size,
                      "len_bytes": len(b),
                      "lines_LF_split": len(b.split(b"\n")),
                      "lines_newline_count": b.count(b"\n"),
                      "sha256": hashlib.sha256(b).hexdigest(),
                      "ends_with_newline": b.endswith(b"\n")}, indent=1))
