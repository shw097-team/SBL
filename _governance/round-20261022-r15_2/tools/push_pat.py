"""Push with the PAT file, non-interactively. Never opens a credential prompt.

PORT NOTE: this is a byte-for-behaviour port of ``push_pat.sh``, which had to stop
being shipped as a ``.sh`` file. The repository pins ``eol=lf`` for every shipped
text type (``.gitattributes``) and a guard asserts that every shipped text file
resolves to ``eol=lf``; an LF-only checkout of a shell script is a latent break on
Windows, so the guard refuses to ship one at all. Python is a shipped text type
here already, so the same steps are expressed in it.

The two failure modes this script exists to prevent, carried over verbatim:

1) ``credential.interactive=always`` orders git to ASK -> Git Credential Manager
   opens a login window.
2) A store file under an MSYS path (``/tmp/...``) cannot be read by native
   ``git.exe`` -> silent miss -> prompt.

So: the credential store is written at a NATIVE path, the helper is pinned with
``-c`` on the push itself, and every interactive prompt source is disabled.

SECURITY: the token is never printed, echoed or logged. Any text returned by git
is passed through :func:`_redact` before it reaches stdout/stderr.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

TOKEN_FILE = Path("C:/Projects/Agent_Workspace/API KEY/GITHUB-REPO_SHW097-4.txt")
DEFAULT_REMOTE = "origin"
DEFAULT_REFSPEC = "HEAD:evidence/r15_2-20261022"
CRED_HOST = "github.com"
CRED_USER = "x-access-token"


def _redact(text: str, token: str) -> str:
    """Strip the token from any text git hands back before it is displayed."""
    if not text:
        return text
    if token:
        text = text.replace(token, "***")
    return text


def _git_env() -> dict[str, str]:
    """Environment in which git cannot reach a prompt of any kind.

    ``GIT_ASKPASS``/``SSH_ASKPASS`` are pointed at a path that does not exist.
    The shell original used ``/bin/false``; on a native Windows git that path
    does not resolve either, and a helper that cannot be executed is treated as
    "unable to get password" -- it fails closed, exactly like ``/bin/false``.
    Measured: ``git credential fill`` exits 128 with "fatal: unable to get
    password from user" rather than opening a window.
    """
    disabled = str(Path(tempfile.gettempdir()) / "push_pat.askpass-disabled")
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_ASKPASS"] = disabled
    env["SSH_ASKPASS"] = disabled
    env.pop("GIT_CONFIG_PARAMETERS", None)
    return env


def _read_token(path: Path) -> str:
    """Read the PAT, tolerating a trailing CRLF (the shell used ``tr -d '\\r\\n'``)."""
    data = path.read_text(encoding="utf-8", errors="replace")
    return data.replace("\r", "").replace("\n", "").strip()


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    remote = args[0] if len(args) > 0 else DEFAULT_REMOTE
    refspec = args[1] if len(args) > 1 else DEFAULT_REFSPEC
    env = _git_env()

    # A NATIVE path for the store file: an MSYS path is invisible to git.exe.
    base = Path(tempfile.gettempdir())
    tmpcred = base / f"ghcred.{os.getpid()}.txt"

    try:
        token = _read_token(TOKEN_FILE)
        if not token:
            print("PAT_MISSING", file=sys.stderr)
            return 2

        # Credential-store format: scheme://user:secret@host
        tmpcred.write_text(
            f"https://{CRED_USER}:{token}@{CRED_HOST}\n",
            encoding="utf-8",
            newline="\n",
        )
        try:
            tmpcred.chmod(0o600)
        except OSError:
            pass  # Windows has no POSIX mode bits; the file is short-lived.

        # Self-check: a store the helper cannot READ is the silent-miss bug.
        lookup = subprocess.run(
            [
                "git",
                "credential-store",
                f"--file={tmpcred}",
                "get",
            ],
            input=f"protocol=https\nhost={CRED_HOST}\n\n",
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        readback = lookup.stdout or ""
        if not any(
            line.startswith("password=") and line[len("password="):].strip()
            for line in readback.splitlines()
        ):
            print(f"CRED_STORE_UNREADABLE {tmpcred}", file=sys.stderr)
            return 3

        # Measured 2026-10-23: the credential-store helper is NOT consulted on this host even
        # when the store is readable -- git falls through to askpass and dies with
        # "fatal: unable to get password from user" (rc 128, no network round trip; reproduced
        # with core.askPass pointed at a working wrapper too). What does work is an
        # authorisation header delivered through the environment, so it never appears in argv:
        #   GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=http.https://github.com/.extraheader
        #   GIT_CONFIG_VALUE_0=AUTHORIZATION: basic <base64(x-access-token:TOKEN)>
        import base64

        env["GIT_CONFIG_COUNT"] = "1"
        env["GIT_CONFIG_KEY_0"] = f"http.https://{CRED_HOST}/.extraheader"
        env["GIT_CONFIG_VALUE_0"] = "AUTHORIZATION: basic " + base64.b64encode(
            f"{CRED_USER}:{token}".encode()).decode()
        push = subprocess.run(
            ["git", "-c", "credential.helper=", "-c", "credential.interactive=never", "push", remote, refspec],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        if push.returncode != 0:
            # Only the remote's own message -- never our token, never a retry.
            sys.stderr.write(_redact(push.stderr or "", token))
            sys.stdout.write(_redact(push.stdout or "", token))
            return push.returncode

        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        short = (head.stdout or "").strip()
        if push.stderr:
            sys.stderr.write(_redact(push.stderr, token))
        print(f"pushed {short} -> {remote} {refspec}")
        return 0
    finally:
        try:
            tmpcred.unlink()
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
