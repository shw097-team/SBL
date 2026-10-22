#!/usr/bin/env bash
# Push with the PAT file, non-interactively. Never opens a credential prompt.
# 1) credential.interactive=always orders git to ASK -> Git Credential Manager opens a login window.
# 2) A store file under an MSYS path (/tmp/...) cannot be read by native git.exe -> silent miss -> prompt.
set -euo pipefail
export GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false

REMOTE="${1:-origin}"
REFSPEC="${2:-HEAD:evidence/r15_2-20261022}"
TOKEN_FILE="C:/Projects/Agent_Workspace/API KEY/GITHUB-REPO_SHW097-4.txt"

BASE="$(cygpath -m "${TMPDIR:-C:/Users/user/AppData/Local/Temp}" 2>/dev/null || echo 'C:/Users/user/AppData/Local/Temp')"
TMPCRED="$BASE/ghcred.$$.txt"
cleanup() { rm -f "$TMPCRED"; }
trap cleanup EXIT

TOK="$(tr -d '\r\n' < "$TOKEN_FILE")"
[ -n "$TOK" ] || { echo "PAT_MISSING" >&2; exit 2; }
printf 'https://%s:%s@%s\n' 'x-access-token' "$TOK" 'github.com' > "$TMPCRED"
chmod 600 "$TMPCRED" 2>/dev/null || true

if ! printf 'protocol=https\nhost=github.com\n\n' | git credential-store --file="$TMPCRED" get | grep -q '^password='; then
  echo "CRED_STORE_UNREADABLE $TMPCRED" >&2; exit 3
fi

git -c credential.helper= -c credential.helper="store --file=$TMPCRED" -c credential.interactive=never \
    push "$REMOTE" "$REFSPEC"
echo "pushed $(git rev-parse --short HEAD) -> $REMOTE $REFSPEC"
