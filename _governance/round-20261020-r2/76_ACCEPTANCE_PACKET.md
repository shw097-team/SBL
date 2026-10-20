# Frozen acceptance packet — candidate `2d1c32d`

FAR step 3: bind everything an independent checker needs to one subject, and say plainly what each item
does and does not prove. Nothing here is called independent unless it is.

## Subject

| Field | Value |
|---|---|
| repo | `github.com/shw097-team/SBL` (public) |
| base | `main` @ `ca6830d9fc9d89b7b87e818670dd67b393472d79` (bootstrap, 26 entries) |
| candidate | `candidate/r2-20261020-v10` @ `2d1c32d6c48fdc09a7d529fc4535482283552487` |
| tree | `7dd4d69f249e7d6028c2e8771b15fb31c1ffe704` |
| ancestry | `v8 fb7af87 → v9 47a428a → v10 2d1c32d`; `main` is a separate root, so **no fast-forward** |
| evidence | `evidence/r2-20261020-c2` (this branch); `-c1` for the v8 round |
| archive tags | `archive/main-premerge-ca6830d`, `archive/cand-v1-ab17440` … `-v9-47a428a`, `archive/wip-r6-7f33e5c` |

## What was measured, and by whom

| Item | Value | Maker or independent |
|---|---|---|
| Local gates | 11/11 `exit 0` | maker |
| Suite | 137 passed; denominators `46, 10, 9, 18, 7, 7, 7, 4, 137` | maker |
| Secret scan | `CLEAN`, 190 files, 0 hard findings | maker |
| Interpreter matrix | 3.12.14 venv, `py -3.11`, clean 3.11.9 venv from a copy | maker |
| Hosted CI | run `39411780991`; ubuntu `118591058137`, windows `118591058453`; `136 passed, 1 skipped` each | GitHub, not a checker |
| Source manifest | `--self-check` `{"ok": true}`, 14 docs, aggregate `754cf7be…`; **`byte_verification: NOT_PERFORMED`** on a hosted runner | GitHub, and it says what it did not do |
| M2 escape probe | `lexical src/link/pwned.py in scope` vs `real ../outside/pwned.py` → `SBL_E_WRITE_OUTSIDE_WRITESET` | maker (`evidence/m2/`) |
| M3 refusal probes | `DOC-27` → `SBL_E_KNOWLEDGE_NO_ANSWER`; skipped source → `SBL_E_KNOWLEDGE_COVERAGE_GAP`; hits stamped `NON_AUTHORITATIVE_LOCATOR` | maker (`evidence/m3/`) |
| M4 | **not executed** | — |

The one-skip difference between 137 local and 136 hosted is a link-capability `ENV` skip, not a disabled
test: on hosts that can create neither a symlink nor a junction the M2 tests skip with an explicit reason.

## The four M4 dispatches

`openai-codex/gpt-6.1-sol`, rank 2, `required_arm == served_arm`, nonces `SBLR2-VERIFY-11..14`, receipts in
`_sbl_verify/runs-m4{,b,c,d}/VERIFY_candidate_2d1c32d.json`, all `ERR_LANE_ALL_ROUTES_EXHAUSTED` with

```
codex_api::endpoint::responses_websocket: failed to connect to websocket:
HTTP error: 426 Upgrade Required, url: ws://127.0.0.1:10101/v1/responses
```

`subject_mutation` on each: 838 → 838 files, added/changed/removed 0. Freeze held; there is no checker
verdict, and no substitute for one.

## What an independent checker must exercise

1. M1 honesty: does CI really install before running, is `--self-check` a real check (tamper a copy of
   `evidence/source/SOURCE_VERIFY.json`), and is anything masked.
2. M2: outside-link denial, inside-link success, and its own variants (nested link, link as final
   component, relative link, sibling-prefix link); note whether a TOCTOU window is realistic.
3. M3: oversized source coverage, recorded skips, explicit error paths, locator stamps, and attempts to
   bypass the doc-id binding.
4. The sixteen earlier security probes, the three golden journeys, the suite, and a secret scan.
5. Report `subject_mutation` and refuse to sign if the subject moved.

## Not in this packet, by design

Release artefacts (`R1` licence, `R2` installable package, `R3` native/HITL scope) and every
`HOLD_SCOPED` item in `80_FAR_RULING.md` §2.
