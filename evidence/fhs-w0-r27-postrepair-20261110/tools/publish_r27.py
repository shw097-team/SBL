#!/usr/bin/env python3
"""publish_r27 — push candidate branches and open PRs, never printing the token.

Reads the owner's fine-grained token from the file the owner designated, uses it only in the
Authorization header, and reports the resulting PR URL. It refuses to:
  * push to main / master,
  * force-push,
  * print the token (the subprocess env carries it; stdout never does),
  * open a PR whose base is not the repo's default branch.

Usage:
  python publish_r27.py push   --repo DIR --branch B [--remote origin]
  python publish_r27.py pr     --repo-slug shw097-team/SBL --head B --base main --title T --body-file F
  python publish_r27.py prlist --repo-slug shw097-team/SBL
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request

TOKEN_FILE = pathlib.Path("C:/Projects/Agent_Workspace/API KEY/GITHUB-REPO_SHW097-4.txt")
ASKPASS = pathlib.Path("C:/Projects/Agent_Workspace/FHS/.git-askpass-shw097-team.sh")


def token() -> str:
    if not TOKEN_FILE.is_file():
        sys.exit("ERR_TOKEN_FILE_MISSING")
    return TOKEN_FILE.read_text(encoding="utf-8").strip()


def api(method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(f"https://api.github.com{path}", data=data, method=method)
    req.add_header("Authorization", "Bearer " + token())
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(body)
        except ValueError:
            return e.code, {"raw": body[:800]}


def _b64_basic() -> str:
    import base64
    return base64.b64encode(f"shw097-team:{token()}".encode("utf-8")).decode("ascii")


def cmd_push(a) -> int:
    if a.branch in ("main", "master"):
        print(json.dumps({"pushed": False, "error": "REFUSED_BASE_BRANCH"}))
        return 2
    env = dict(os.environ)
    env["GIT_ASKPASS"] = ""
    env["GIT_TERMINAL_PROMPT"] = "0"
    # the secret travels in the CHILD'S ENVIRONMENT, never in argv and never in a file git reads:
    # GIT_CONFIG_* is git's own env-based config channel.
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "http.https://github.com/.extraheader"
    env["GIT_CONFIG_VALUE_0"] = "AUTHORIZATION: basic " + _b64_basic()
    argv = ["git", "-C", a.repo, "push", "--set-upstream", a.remote, f"refs/heads/{a.branch}:refs/heads/{a.branch}"]
    p = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=600)
    out = {"pushed": p.returncode == 0, "exit": p.returncode, "branch": a.branch,
           "stderr_tail": "\n".join(p.stderr.strip().splitlines()[-4:])}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if p.returncode == 0 else 1


def cmd_pr(a) -> int:
    body = pathlib.Path(a.body_file).read_text(encoding="utf-8") if a.body_file else ""
    if a.base not in ("main", "master"):
        print(json.dumps({"opened": False, "error": "BASE_MUST_BE_DEFAULT_BRANCH"}))
        return 2
    code, res = api("POST", f"/repos/{a.repo_slug}/pulls",
                    {"title": a.title, "head": a.head, "base": a.base, "body": body, "draft": bool(getattr(a, "draft", False))})
    print(json.dumps({"status": code, "number": res.get("number"), "url": res.get("html_url"),
                      "message": res.get("message"), "errors": res.get("errors")}, ensure_ascii=False, indent=1))
    return 0 if code in (200, 201) else 1


def cmd_prlist(a) -> int:
    code, res = api("GET", f"/repos/{a.repo_slug}/pulls?state=all&per_page=20")
    rows = [{"number": p.get("number"), "state": p.get("state"), "merged": p.get("merged_at") is not None,
             "head": (p.get("head") or {}).get("ref"), "url": p.get("html_url")} for p in (res if isinstance(res, list) else [])]
    print(json.dumps({"status": code, "pulls": rows}, ensure_ascii=False, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("push"); p.add_argument("--repo", required=True); p.add_argument("--branch", required=True)
    p.add_argument("--remote", default="origin"); p.set_defaults(fn=cmd_push)
    q = sub.add_parser("pr"); q.add_argument("--repo-slug", required=True); q.add_argument("--head", required=True)
    q.add_argument("--base", default="main"); q.add_argument("--title", required=True)
    q.add_argument("--body-file", default=None); q.add_argument("--draft", action="store_true"); q.set_defaults(fn=cmd_pr)
    r = sub.add_parser("prlist"); r.add_argument("--repo-slug", required=True); r.set_defaults(fn=cmd_prlist)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
