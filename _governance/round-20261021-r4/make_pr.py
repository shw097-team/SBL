"""Open the c3 portable-manifest PR. The token is read in-process and never printed."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

TOKEN_FILE = Path(r"C:\Projects\Agent_Workspace\API KEY\GITHUB-REPO_SHW097-4.txt")
API = "https://api.github.com/repos/shw097-team/SBL/pulls"


def token() -> str:
    raw = TOKEN_FILE.read_text(encoding="utf-8").strip()
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("gh") or line.startswith("github_pat_"):
            return line
    return raw.splitlines()[0].strip()


def post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token()}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:  # type: ignore[attr-defined]
        return {"error": exc.code, "body": exc.read().decode()[:400]}


body = """Round 4 narrow repair of `F-R4-C3-PLUGIN-SCHEMA-001`, plus two installable surfaces.

**What was wrong.** `plugin_manifest()` emitted `"schema": "SBL-AGENT-PLUGIN/1"` with no `$schema`,
and put `identity` / `permissions` / `forbidden` / `claim_ceiling` at the top level. The portable
Agent Plugins 1.0.0 schema sets `additionalProperties: false` and requires `$schema` and `name`, so no
conforming host could recognise these packages.

**What changed.** The manifest is now `{$schema, name, version, description, license, keywords,
extensions}`, with principal metadata under `extensions["org.sbl.principal"]`. Every package is
validated against a vendored copy of the published schema before the ZIP is closed, and validator
non-vacuity is proven by injection (missing/foreign `$schema`, extra top-level key, the legacy
`schema` key, illegal name pattern, non-object extension, unknown author key).

**A second defect, found by the Docker sandbox and not by any local test:** the wheel shipped without
`sbl_sp/manifests/*.json`, so every `load_manifest` call in an *installed* package raised
`SBL_E_UNKNOWN_SP` while the source tree was green — CI ran `pip install -e .`, which resolves data
files straight from the source tree. `package-data` is fixed and `tools/check_wheel_contents.py` now
builds the real wheel in CI and asserts its members.

**New surfaces.** `sbl_stack` (install / doctor / selftest / status / uninstall over the composed
M01..M06 core, with an integrity manifest of the exact bytes it validated) and `sbl_harness` (pinned
HGK dependency + harness ABI + probe / install / doctor / uninstall; it declares the native boundary
rather than crossing it).

**Ceiling.** `PACKAGED_HOST_PENDING`. Three packages were installed and loaded by a real host loader
on one machine, with a rollback point taken first; no host-issued plugin identity was obtained and no
independent checker signed. Merge is an owner act and does not raise the ceiling.

183 tests, 11/11 gates, secret scan CLEAN, CI 2/2 on ubuntu + windows 3.11 (run 39525131900).

Evidence: `evidence/r4-20261021-c4` — `_governance/round-20261021-r4/` (contract, five-tool matrix,
sandbox receipt, rollback manifest, install receipt, SWOF shadow handoff, CR, corrections).
"""

result = post(
    API,
    {
        "title": "c3 round 2: portable plugin manifests, the wheel that shipped without its data, and two installable surfaces",
        "head": "candidate/c3-20261021-v2",
        "base": "main",
        "body": body,
        "draft": False,
    },
)
print(json.dumps({k: result.get(k) for k in ("number", "html_url", "state", "error")}, indent=2))
if "error" in result:
    print(result.get("body", "")[:400])
