#!/usr/bin/env bash
# Push with the PAT file, non-interactively, and never open a credential prompt.
#
# Why this exists: the previous recipe passed `credential.interactive=always`, which makes git ASK whenever the askpass
# wrapper is not picked up. On this host that surfaced as a GitHub login window plus a pile of hung
# git-remote-https.exe processes. A credential store file satisfies the request without any prompt, and
# credential.interactive=never guarantees git fails rather than opening a GUI.
#
# Usage: tools/push_pat.sh <remote> <refspec>
set -euo pipefail

# hardest guarantee available: git must never ask, under any flag combination
export GIT_TERMINAL_PROMPT=0
export GIT_ASKPASS=/bin/false
export SSH_ASKPASS=/bin/false

REMOTE="${1:-origin}"
REFSPEC="${2:-HEAD:evidence/r15_2-20261022}"
TOKEN_FILE="C:/Projects/Agent_Workspace/API KEY/GITHUB-REPO_SHW097-4.txt"
TMPCRED="$(mktemp -t ghcred.XXXXXX)"

cleanup() { rm -f "$TMPCRED"; }
trap cleanup EXIT

TOK="$(tr -d '\r\n' < "$TOKEN_FILE")"
if [ -z "$TOK" ]; then echo "PAT_MISSING" >&2; exit 2; fi
printf 'https://x-access-token:%s@github.com\n' "$TOK" > "$TMPCRED"
chmod 600 "$TMPCRED" 2>/dev/null || true

git -c credential.helper= \
    -c credential.helper="store --file=$TMPCRED" \
    -c credential.interactive=never \
    push "$REMOTE" "$REFSPEC"

echo "pushed $(git rev-parse --short HEAD) -> $REMOTE $REFSPEC"
