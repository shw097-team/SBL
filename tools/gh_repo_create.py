"""Create the public SBL repository under OPS control — non-model credential handling.

The token is read from a local file by THIS process only. It is never printed, never placed in argv,
never written to logs or artifacts; only availability/permission outcomes are emitted.

Usage:
  python tools/gh_repo_create.py --owner shw097-team --repo SBL [--dry-run]
Env:
  SBL_GH_TOKEN_FILE  path to the token file (default: the owner-provided local file)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_TOKEN_FILE = r"C:\Projects\Agent_Workspace\API KEY\GITHUB-REPO_SHW097-4.txt"
API = "https://api.github.com"


def _token() -> str:
    path = os.environ.get("SBL_GH_TOKEN_FILE", DEFAULT_TOKEN_FILE)
    with open(path, "r", encoding="utf-8-sig") as fh:
        token = fh.read().strip()
    if not token:
        raise SystemExit("ERR_TOKEN_EMPTY")
    return token


def _call(method: str, url: str, token: str, payload: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "sbl-ops-bootstrap")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read().decode("utf-8", "replace")
            return resp.status, (json.loads(body) if body.strip() else {})
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"message": body[:300]}
        return exc.code, parsed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", default="shw097-team")
    ap.add_argument("--repo", default="SBL")
    ap.add_argument("--description", default="SBL / SpecBuild Loop — Guided Spec -> Governed Build -> Evidence-based Verify -> Bounded Repair (candidate, not independently accepted)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    token = _token()
    full = f"{args.owner}/{args.repo}"

    status, who = _call("GET", f"{API}/user", token)
    if status != 200:
        print(json.dumps({"step": "auth", "status": status, "message": who.get("message"), "verdict": "FAIL"}, ensure_ascii=False))
        return 2

    status, existing = _call("GET", f"{API}/repos/{full}", token)
    if status == 200:
        print(json.dumps({
            "step": "exists",
            "full_name": existing.get("full_name"),
            "visibility": existing.get("visibility"),
            "default_branch": existing.get("default_branch"),
            "html_url": existing.get("html_url"),
            "verdict": "EXISTS_NO_OVERWRITE",
        }, ensure_ascii=False))
        return 0
    if status not in (404,):
        print(json.dumps({"step": "lookup", "status": status, "message": existing.get("message"), "verdict": "FAIL"}, ensure_ascii=False))
        return 2

    if args.dry_run:
        print(json.dumps({"step": "create", "would_create": full, "visibility": "public", "verdict": "DRY_RUN"}, ensure_ascii=False))
        return 0

    status, created = _call("POST", f"{API}/orgs/{args.owner}/repos", token, {
        "name": args.repo,
        "description": args.description,
        "private": False,
        "visibility": "public",
        "has_issues": True,
        "has_wiki": False,
        "auto_init": False,
    })
    if status in (201, 200):
        print(json.dumps({
            "step": "created",
            "full_name": created.get("full_name"),
            "visibility": created.get("visibility"),
            "private": created.get("private"),
            "default_branch": created.get("default_branch"),
            "html_url": created.get("html_url"),
            "verdict": "CREATED_PUBLIC",
        }, ensure_ascii=False))
        return 0
    print(json.dumps({"step": "create", "status": status, "message": created.get("message"), "verdict": "FAIL"}, ensure_ascii=False))
    return 3


if __name__ == "__main__":
    sys.exit(main())
