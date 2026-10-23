NONCE: EXEC-R153-SECSCAN-095315

Begin your reply with exactly this token on its own line: EXEC-R153-SECSCAN-095315

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# EXECUTE brief — R15.3 writes #2: scoped secret-scan gate (C22)

You are SBL-EXECUTE and a bounded writer. Work in `C:/Projects/Agent_Workspace/_r152_ev`. Write **exactly the four
files below**, then stop. No lane dispatch, no sub-agent, no polling, no `git add`, no commit, no formatter.

## Measured fact you are fixing

`python tools/secret_scan.py` returns exit 1 with 54 hard findings (52 `email_address`, 2 `assigned_secret`), and
**every one of them is under `_governance/`** — published evidence logs, a G-KNOW index, a PR-creation record and the
TT register. The tool has no way to exclude a subtree (`--root` and `--json-out` are its only options), so the CI step
`Secret scan (hard gate)` added earlier would fail on its first run for a reason that is not a product leak.

Evidence must not be redacted to buy a green: those files are hashed by other rounds. The gate must become
**scoped** instead, and the evidence findings must stay visible as a separate typed report.

## File 1 — `tools/secret_scan.py` (edit, additive)

Add a repeatable `--exclude` option (glob, POSIX-style, matched against the file's path relative to `--root`, e.g.
`_governance/**`). Requirements:

- default: no exclusions, so the existing behaviour and its exit codes are unchanged;
- an excluded path is not scanned and is reported in the JSON as `excluded_files` (count) and `excludes` (the globs);
- matching must use `fnmatch` on the normalised relative path with `\` converted to `/`, and must be **case-insensitive
  on Windows**;
- `--exclude` never silences a finding in a non-excluded file.

## File 2 — `tests/test_secret_scan_exclude.py` (new)

Three tests, using `tmp_path` only (never the real repo):

1. a planted `email_address` finding inside `_governance/x.log` is **not** reported when `--exclude _governance/**`;
2. the same finding **is** reported when no `--exclude` is passed (the gate is not weakened globally);
3. a planted finding in `sbl_core/x.py` is still reported when `--exclude _governance/**` is passed.

Run them and print the count.

## File 3 — `.github/workflows/ci.yml` (edit, minimal)

Replace the single `Secret scan (hard gate)` step with these three steps, indented like their neighbours:

```yaml
      - name: Secret scan (hard gate, product surface)
        run: python tools/secret_scan.py --exclude "_governance/**" --json-out evidence/security/SECRET_SCAN.json

      - name: Secret scan (evidence surface, advisory)
        continue-on-error: true
        run: python tools/secret_scan.py --root _governance --json-out evidence/security/SECRET_SCAN_EVIDENCE.json
```

Keep the `Dependency inventory (SBOM input)` step. Add nothing else.

## File 4 — `workers/execute_r153/EXECUTE_RECEIPT_2.json` (new)

Same schema as `EXECUTE_RECEIPT.json` (`SBL_EXECUTE_RECEIPT/1`), one row per file with real byte size and sha256 read
back from disk, plus `not_done` listing anything you declined.

## Rules

- Exactly these four files.
- If a test fails, fix the code, not the test's premise; if you cannot make it pass, say so in the receipt and leave
  the test in place with the failing assertion visible.
- Print one line per file with its byte size at the end.
