"""Fetch a GitHub Actions run log to disk without ever exposing the token.

The token is read from the local locator inside this process, is never printed, never passed on a
command line and never written anywhere except the HTTP header of the request.
"""
from __future__ import annotations

import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

TOKEN_FILE = Path(r"C:\Projects\Agent_Workspace\API KEY\GITHUB-REPO_SHW097-4.txt")
RUN_ID = sys.argv[1]
OUT = Path(sys.argv[2])


def token() -> str:
    raw = TOKEN_FILE.read_text(encoding="utf-8").strip()
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("gh") or line.startswith("github_pat_"):
            return line
    return raw.splitlines()[0].strip()


def main() -> int:
    url = f"https://api.github.com/repos/shw097-team/SBL/actions/runs/{RUN_ID}/logs"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token()}"})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
    OUT.write_bytes(payload)
    names = []
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
    print(json.dumps({"bytes": len(payload), "entries": len(names), "sample": names[:6]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
