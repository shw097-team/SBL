# Bounded writer task v2 (EXECUTE lane) — small, must finish

First line of your reply: EXEC-R15-2-WO04-NONCE-B84F12D7

Write-set: `workers/codex_exec/` only. Read-only everywhere else. No git write commands, no installs.

Do exactly this, then stop:

1. `cd` to the round directory. Run: `git ls-files | wc -l` and
   `git ls-files "*.py" "*.md" "*.json" "*.toml" "*.yml" "*.yaml" "*.txt" | wc -l`.
   Record both numbers.
2. Run this PowerShell one-liner and record its raw output and exit code:
   `pwsh -NoProfile -Command "$p = git ls-files '*.md'; 'paths=' + $p.Count; 'chars=' + (($p -join ' ').Length)"`
3. Write `workers/codex_exec/EXEC_RECEIPT.json` with exactly these keys: `token`, `tracked_total`,
   `tracked_text`, `pathlist_chars`, `command_line_chars`, `over_windows_limit` (true if command_line_chars
   plus 40 exceeds 32767), `commands` (list of {cmd, stdout, stderr, exit}), `verdict` ("PASS").
   `command_line_chars` = pathlist_chars + 40 for the `git -C <repo> check-attr eol -- ` prefix.

Do not edit tests. Do not run the full suite. Do not write anything outside `workers/codex_exec/`.
When the file is written, reply with one line: the token and the path you wrote.
