#!/usr/bin/env python3
"""R5 TS00 — read-only environment snapshot. No writes to any product or control-plane file.

The GitHub token is read inside this process from the owner's credential file and is NEVER printed,
stored in the JSON, or passed on a command line; only the API response fields we need are kept.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "ENV_SNAPSHOT.json"
KEY_FILE = Path(r"C:\Projects\Agent_Workspace\API KEY\GITHUB-REPO_SHW097-4.txt")
REPOS = {
    "SBL": Path(r"C:\Projects\Agent_Workspace\SBL"),
    "HG-KSEOS": Path(r"C:\Projects\Agent_Workspace\HG-KSEOS"),
    "Fabric": Path(r"C:\Projects\Agent_Workspace\Fabric"),
}


def run(args: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=str(cwd) if cwd else None, capture_output=True, text=True, timeout=120)
    return (proc.stdout or proc.stderr).strip()


def token() -> str | None:
    if not KEY_FILE.is_file():
        return None
    for line in KEY_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith(("ghp_", "github_pat_")):
            return line
    return None


def api(path: str, tok: str | None) -> dict:
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "sbl-r5-preflight"},
    )
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - a failed read is recorded, not raised
        return {"error": type(exc).__name__, "detail": str(exc)[:200]}


def main() -> int:
    snap: dict = {
        "round": "SBL-R5-20261021-C5",
        "task": "TS00",
        "generated_utc": run([sys.executable, "-c", "import datetime;print(datetime.datetime.now(datetime.UTC).isoformat())"]),
        "host": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "executable": sys.executable,
        },
        "repos": {},
        "lanes": {},
        "github": {},
    }

    for name, path in REPOS.items():
        snap["repos"][name] = {
            "path": str(path),
            "head": run(["git", "rev-parse", "HEAD"], path),
            "branch": run(["git", "branch", "--show-current"], path),
            "dirty_files": len([l for l in run(["git", "status", "--porcelain"], path).splitlines() if l.strip()]),
        }
    sbl = REPOS["SBL"]
    snap["repos"]["SBL"]["remote_refs"] = {
        line.split("\t")[1]: line.split("\t")[0]
        for line in run(["git", "ls-remote", "origin"], sbl).splitlines()
        if "\t" in line and line.split("\t")[1] in {"refs/heads/main", "refs/heads/candidate/c3-20261021-v2", "refs/heads/evidence/r4-20261021-c4"}
    }

    codex = Path(r"C:\Users\user\AppData\Local\OpenAI\Codex\bin\896a0166b774037a\codex.exe")
    snap["toolchain"] = {
        "codex_version": run([str(codex), "--version"]) if codex.is_file() else "MISSING",
        "hgk_version": run([sys.executable, "-c", "import hg_kseos;print(getattr(hg_kseos,'__version__','?'))"]),
        "docker": run(["docker", "version", "--format", "{{.Server.Version}}"]),
    }

    for lane, filename in (("PLAN", "plan_probe.json"), ("EXECUTE", "execute_probe.json"), ("VERIFY_SECURITY", "verify_probe.json")):
        p = Path(r"C:\Projects\Agent_Workspace\HG-KSEOS\var\R5-PREFLIGHT") / filename
        if p.is_file():
            d = json.loads(p.read_text(encoding="utf-8"))
            snap["lanes"][lane] = {
                "ok": d.get("ok"),
                "required_arm": d.get("required_arm"),
                "served_arm": d.get("served_arm"),
                "used_seconds": d.get("used_seconds"),
                "usage_receipt_ok": d.get("usage_receipt_ok"),
                "receipt": str(p),
            }

    tok = token()
    snap["github"]["token_present"] = bool(tok)
    snap["github"]["pr_2"] = {
        k: v
        for k, v in api("/repos/shw097-team/SBL/pulls/2", tok).items()
        if k in ("number", "state", "mergeable", "merged", "commits", "changed_files", "created_at", "updated_at")
        or k in ("head", "base")
    }
    if "head" in snap["github"]["pr_2"]:
        snap["github"]["pr_2"]["head_sha"] = snap["github"]["pr_2"]["head"].get("sha")
        snap["github"]["pr_2"]["base_sha"] = snap["github"]["pr_2"]["base"].get("sha")
        snap["github"]["pr_2"].pop("head", None)
        snap["github"]["pr_2"].pop("base", None)
    runs = api("/repos/shw097-team/SBL/actions/runs?per_page=5", tok)
    snap["github"]["recent_runs"] = [
        {"id": r["id"], "head_sha": r["head_sha"], "conclusion": r["conclusion"], "event": r["event"]}
        for r in runs.get("workflow_runs", [])
    ]
    rel = api("/repos/shw097-team/SBL/releases", tok)
    snap["github"]["releases"] = [
        {"tag": r["tag_name"], "prerelease": r["prerelease"], "assets": [a["name"] for a in r.get("assets", [])]}
        for r in (rel if isinstance(rel, list) else [])
    ]

    OUT.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "lanes": {k: v["served_arm"] for k, v in snap["lanes"].items()},
        "pr2": {k: snap["github"]["pr_2"].get(k) for k in ("state", "head_sha", "mergeable", "merged")},
        "heads": {k: v["head"][:12] for k, v in snap["repos"].items()},
        "runs": snap["github"]["recent_runs"][:3],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
