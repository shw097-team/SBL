#!/usr/bin/env python3
"""Publish the frozen PIPD-LS-SP candidate to GitHub as a public repo.

Security contract (binding):
  * the PAT is read from a single known file inside THIS process only;
  * the token never reaches argv, stdout, stderr, a log, a URL, git history or any artifact;
  * only non-sensitive codes are printed (PAT_PRESENT / AUTH_VALID / PERMISSION_SCOPED / ...).
"""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

PAT_FILE = Path(r"C:\Projects\Agent_Workspace\API KEY\Fine-grained personal access tokens.txt")
REPO_ROOT = Path(r"C:\Projects\Agent_Workspace\PIPD")
ORG = "shw097-team"
NAME = "PIPD-LS-SP"
API = "https://api.github.com"


def load_token() -> str | None:
    if not PAT_FILE.is_file():
        return None
    data = PAT_FILE.read_bytes()
    m = (re.search(rb"github_pat_[A-Za-z0-9_]{20,}", data)
         or re.search(rb"gh[pousr]_[A-Za-z0-9]{20,}", data))
    return m.group(0).decode("ascii") if m else None


def _https_only(url: str) -> str:
    """Refuse any scheme other than https before a request is opened (bandit B310).

    The base URL is a module constant, so this is a guard rather than a live fix: it makes the
    allow-list explicit and fails closed if a future caller ever passes a different scheme.
    """
    from urllib.parse import urlsplit

    if urlsplit(url).scheme != "https":
        raise ValueError(f"refusing a non-https URL: {url!r}")
    return url

def api(path: str, token: str, method: str = "GET", body: dict | None = None):
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "User-Agent": "PIPD-LS-SP-governed-round", "X-GitHub-Api-Version": "2022-11-28",
                 "Content-Type": "application/json"})
    try:
        # the URL is scheme-allow-listed by _https_only() immediately above, so B310 cannot apply here
        with urllib.request.urlopen(_https_only(req.full_url), timeout=40) as r:  # nosec B310
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            return e.code, {}
    except Exception as e:
        return None, {"error": type(e).__name__}


def anon(url: str):
    _https_only(url)
    req = urllib.request.Request(url, headers={"User-Agent": "PIPD-anon-readback"})
    try:
        with urllib.request.urlopen(_https_only(req.full_url), timeout=40) as r:  # nosec B310 - scheme allow-listed above
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return None, ""


def main() -> int:
    out: dict = {"PAT_PRESENT": PAT_FILE.is_file()}
    token = load_token()
    if not token:
        print(json.dumps({**out, "verdict": "GITHUB_AUTH_BLOCKED"}, indent=1))
        return 2
    s, me = api("/user", token)
    out["AUTH_VALID"] = s == 200
    out["LOGIN"] = me.get("login") if s == 200 else None
    if not out["AUTH_VALID"]:
        print(json.dumps({**out, "verdict": "GITHUB_AUTH_BLOCKED"}, indent=1))
        return 2

    s, repo = api(f"/repos/{ORG}/{NAME}", token)
    out["REPO_EXISTED"] = s == 200
    if s != 200:
        s, repo = api(f"/orgs/{ORG}/repos", token, "POST",
                      {"name": NAME, "private": False,
                       "description": "PIPD-LS-SP review candidate - governed HG-KSEOS round",
                       "has_issues": True, "has_wiki": False})
        out["CREATE_HTTP"] = s
        if s not in (200, 201):
            print(json.dumps({**out, "verdict": "GITHUB_AUTH_BLOCKED", "create": repo.get("message")}, indent=1))
            return 2
    out["REPO_URL"] = repo.get("html_url")
    out["VISIBILITY"] = repo.get("visibility")

    # Push WITHOUT ever putting the token in argv or a URL: the credential travels only in the
    # child process environment, which is process memory and is never persisted to .git/config.
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode("ascii")
    push_env = {**os.environ,
                "GIT_TERMINAL_PROMPT": "0",
                "GIT_CONFIG_COUNT": "1",
                # URL-scoped on purpose. The previous run set the bare `http.extraheader` here AND
                # passed `-c http.https://github.com/.extraheader=` (empty) on the command line; the
                # more specific command-line value won and cleared the Authorization header, so the
                # push went out unauthenticated ("Invalid username or token"). Nothing on the command
                # line may override this key now.
                "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
                "GIT_CONFIG_VALUE_0": f"Authorization: Basic {basic}",
                "GIT_ASKPASS": "echo", "GIT_CONFIG_NOSYSTEM": "1"}
    push = subprocess.run(["git", "-C", str(REPO_ROOT), "-c", "credential.helper=",
                           "push", "--quiet", f"https://github.com/{ORG}/{NAME}.git",
                           "HEAD:refs/heads/main", "--force"],
                          capture_output=True, text=True, env=push_env)
    del basic, push_env
    out["PUSH_EXIT"] = push.returncode
    err = (push.stderr or "").replace(token, "")
    out["PUSH_ERROR_REDACTED"] = bool(err.strip())
    out["PUSH_ERROR_HAS_TOKEN"] = bool(re.search(r"gh[pousr]_|github_pat_", err))
    if err.strip():
        out["PUSH_ERROR_TAIL"] = err.strip()[-300:]

    s, repo2 = api(f"/repos/{ORG}/{NAME}", token)
    out["VISIBILITY_AFTER"] = repo2.get("visibility")
    s2, commits = api(f"/repos/{ORG}/{NAME}/commits?per_page=1", token)
    out["HEAD_SHA"] = commits[0]["sha"] if s2 == 200 and commits else None
    local = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                           capture_output=True, text=True).stdout.strip()
    out["LOCAL_HEAD"] = local
    out["COMMIT_MATCH"] = out["HEAD_SHA"] == local

    a1, readme = anon(f"{out['REPO_URL'] or ''}/raw/main/README.md")
    out["ANON_README_HTTP"] = a1
    out["ANON_README_BYTES"] = len(readme)
    a2, _ = anon(f"https://api.github.com/repos/{ORG}/{NAME}")
    out["ANON_API_HTTP"] = a2
    out["PUBLIC_ANON_READABLE"] = (a1 == 200 and a2 == 200)

    ok = bool(out["PUSH_EXIT"] == 0 and out["COMMIT_MATCH"] and out["PUBLIC_ANON_READABLE"]
              and out["VISIBILITY_AFTER"] == "public")
    out["verdict"] = "PASS" if ok else "PUBLISH_INCOMPLETE"
    Path(REPO_ROOT / ".hgk" / "artifacts" / "github_publish.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8", newline="")
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
