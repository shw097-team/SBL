# VERIFY_C0 — Independent verification of the C0 closing state

- Run: `RUN-20261102-GJ02-01`
- Verifier: independent read-only subagent (no use of prior run's conclusions as evidence)
- Verified at: 2026-11-03 (Asia/Taipei, UTC+08:00)
- Working copy: `C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/deliver-wt`
- GitHub auth: existing curl config `…/scratch/gh.curlrc` (token never read or printed)
- Mode: read-only outside this output directory. No commits, no pushes.

## Verdict

**C0 closing state CONFIRMED.** 23/23 checks passed, 0 mismatches. Every claimed SHA, run
conclusion, artifact digest and decision string was reproduced from the authoritative source
(GitHub API for remote state, the artifact itself for the zip, the checked-out tree for evidence).

## Check log

`exit` is the shell exit status of the command shown. Values are quoted exactly as read.

### 1. Branch heads and CI (GitHub API)

| # | Command | exit | Value read | Result |
|---|---------|------|-----------|--------|
| C1 | `curl -s --config gh.curlrc https://api.github.com/repos/shw097-team/SBL/commits/main` | 0 | `sha = 25a4c13c341400e7692ac3852d26bfdc65111779`, committer date `2026-11-02T17:10:22Z` | PASS — matches claimed `25a4c13c34` |
| C2 | same as C1 | 0 | `commit.message[0] = "Merge pull request #20 from shw097-team/evidence/pre-primary-gj02-closeout"`, parents `67c29be…`, `e148fda…` | PASS — merge of PR #20 |
| C3 | `curl -s --config gh.curlrc "…/SBL/actions/runs?branch=main&per_page=10"` + `…/runs/41488602259/jobs` | 0 | latest main run `id=41488602259`, `name=ci`, `head_sha=25a4c13c3414…`, `status=completed`, `conclusion=success`, created `2026-11-02T17:10:26Z`; jobs: `test (ubuntu-latest, py3.11)` 11/11 steps, `pipd-compat (ubuntu, py3.11)` 14/14, `test (windows-latest, py3.11)` 11/11 — all `success` | PASS — main CI green on the claimed SHA |
| C4 | `curl -s --config gh.curlrc https://api.github.com/repos/shw097-team/PIPD-LS-SP/commits/main` | 0 | `sha = a25fb569104c58afe3daa6e054a2e841a4c1e127`, date `2026-11-02T17:02:07Z` | PASS — matches claimed `a25fb56910` |
| C5 | same as C4 | 0 | `commit.message[0] = "Merge pull request #28 from shw097-team/fix/cli-docstring-count"`, parents `be72c90…`, `75fe7de…` | PASS — merge of PR #28 |
| C6 | `curl -s --config gh.curlrc "…/PIPD-LS-SP/actions/runs?branch=main&per_page=10"` | 0 | latest main run `id=41487230366`, `head_sha=a25fb569104c…`, `conclusion=success`, created `2026-11-02T17:02:11Z` | PASS |
| C7 | `curl -s --config gh.curlrc "…/PIPD-LS-SP/commits/a25fb569…/check-runs"` | 0 | `total_count=1`; `offline-gate` → `status=completed`, `conclusion=success`, completed `2026-11-02T17:04:09Z` | PASS — claimed check-runs success confirmed |

Note (not a mismatch): an earlier main run `41487070321` on `be72c90` shows `conclusion=cancelled`.
It is **not** the latest run for main and does not bear on the closing SHA `a25fb56910`, whose own run
`41487230366` is `success`.

### 2. Merged PRs (GitHub API)

| # | Command | exit | `state` | `merged` | `merge_commit_sha` | Claimed | Result |
|---|---------|------|---------|----------|--------------------|---------|--------|
| C8 | `curl -s --config gh.curlrc …/SBL/pulls/15` | 0 | `closed` | `true` | `aac7ab9c09811c5a98b39149ee85ebc8b24de65a` | `aac7ab9c` | PASS |
| C9 | `…/SBL/pulls/18` | 0 | `closed` | `true` | `24d1205f667efcb09d19247b0a20545736f77ca4` | `24d1205f` | PASS |
| C10 | `…/SBL/pulls/20` | 0 | `closed` | `true` | `25a4c13c341400e7692ac3852d26bfdc65111779` | `25a4c13c` | PASS |
| C11 | `…/PIPD-LS-SP/pulls/26` | 0 | `closed` | `true` | `7073fe2d4e8be78dc253f83c307f3f6d7a46fd23` | `7073fe2d` | PASS |
| C12 | `…/PIPD-LS-SP/pulls/28` | 0 | `closed` | `true` | `a25fb569104c58afe3daa6e054a2e841a4c1e127` | `a25fb569` | PASS |

All five are `closed` + `merged=true`, and each `merge_commit_sha` equals the claimed SHA at the full
40-character precision (no prefix-only match accepted).

### 3. rc.2 artifact (local)

| # | Command | exit | Value read | Result |
|---|---------|------|-----------|--------|
| C13 | `sha256sum sbl-tpm-sp-0.3.0-rc.2-private.zip` | 0 | `3a9da65561ab19cad90a6d7cbfb2eae0abf59b87ba565a118790bce5612326a8` | PASS — equals claimed digest |
| C14 | `zipfile.ZipFile(...).namelist()` | 0 | `173` members (0 directory entries; all 173 are files) | PASS — 173 as claimed |
| C15 | same, filter `*/SKILL.md` | 0 | `14` `SKILL.md`, `14` distinct skill directories: `pipd-assurance-tqaep, pipd-authority-source, pipd-execution-contract, pipd-package-project, pipd-pd-bind, pipd-pi-compile, pipd-profile-tailor, pipd-route-intake, tpm-handoff, tpm-product-plan, tpm-program-plan, tpm-setup, tpm-sp, tpm-system-plan` | PASS — 14 skills as claimed |

Cross-check: `evidence/pp261102/05_M1_M4_results.json` records
`candidate_sha = 3a9da65561ab19cad90a6d7cbfb2eae0abf59b87ba565a118790bce5612326a8` — identical to the
zip digest actually on disk, so the evidence names the artifact it was produced against.

### 4. Evidence presence and decisions (local, checked-out tree)

| # | Command | exit | Value read | Result |
|---|---------|------|-----------|--------|
| C16 | `find evidence/pre-primary-20261102 evidence/pp261102 -type f` | 0 | 48 files, **0** zero-byte files, 256,714 bytes total; `pre-primary-20261102/{README.md,RUN-20261102-GJ02-01/{00_run_manifest.json,01_products,02_checkrun.json,03_native_receipt_refs.json,04_closeout.md,raw}}`; `pp261102/{05_M1_M4_results.json,06_closeout_addendum.md,b/,g/,m/,o/}` | PASS — both trees exist and are non-empty |
| C17 | `json.load(05_M1_M4_results.json)` | 0 | parses; `schema = "SBL.Rc2FourItemClosure@1"`, `run_id = "RUN-20261102-GJ02-01"`, keys `M1_operation_registry_ecp, M2_planned_tqaep_at2, M2b_pipd_validate_four_objects, M3_natural_goal_routing, M4_thin_governance, promotion` | PASS |
| C18 | same | 0 | `promotion.decision = "PRE_V2_DESIGN_SIDECAR_READY"` | PASS |
| C19 | same | 0 | `promotion.native = "NATIVE_GOLDEN_HOLD (unchanged: no issuer, checker or publisher)"` | PASS |
| C20 | `grep -nE "PRE_V2_DESIGN_SIDECAR_READY|NATIVE_GOLDEN_HOLD" 06_closeout_addendum.md` | 0 | L68 `**\`PRE_V2_DESIGN_SIDECAR_READY\`** — not \`PRE_V2_GENERATION_READY\`, because (a) …`; L70 `**\`NATIVE_GOLDEN_HOLD\`** stands: no original issuer, checker or publisher was reachable …` | PASS — same two decisions as the JSON |
| C23 | `git rev-parse HEAD:evidence` vs `git rev-parse origin/main:evidence` | 0 | both `8f81ffc6f410b4a9dced8f73c63f626ebe6190f3` | PASS — the evidence tree scanned is byte-identical to `main` (`25a4c13c`) |

Location nuance (documented, not a mismatch): `05_M1_M4_results.json` and `06_closeout_addendum.md`
exist **only** under `evidence/pp261102/`, not under `evidence/pre-primary-20261102/` (which holds the
GJ02 run bundle). `evidence/pp261102/` additionally contains `m/` beyond the claimed `b/`, `g/`, `o/`.
The claim's groupings are consistent with the tree; no path in the claim is absent.

Working-copy integrity: `HEAD = e148fdaecf64c31f0493efee0c50d109783a3166` (PR #20 head), clean
`git status`. Compared with `origin/main = 25a4c13c…`, one file differs —
`docs/pipd-migration/U04-CUTOVER.md` — and **no** evidence path differs, so the decision records read
here are exactly main's.

### 5. Secret scan of the evidence trees

Scope: `evidence/pre-primary-20261102` and `evidence/pp261102` in the working copy (48 files).

| # | Command | exit | Value read | Result |
|---|---------|------|-----------|--------|
| C21 | `grep -rInoE 'ghp_\|github_pat_\|sk-\|Bearer \|BEGIN [A-Z ]*PRIVATE KEY'` (python equivalent, exact line context) | 0 | **7 matching lines**, every one prose or a JSON key: 3× `"ghp_01": {` in `01_products/specs/{Architecture,Product,Program}SPEC.json` (= *GitHub delivery decision phase 01*, a document key — no token body follows the prefix); 3× self-referential scan text in `g/VERIFY_REPORT.md` (L160 grep pattern, L165 explaining `ghp_01`, L169 token regex); 1× self-referential scan text in `g/gate.json:73`. `BEGIN PRIVATE KEY` → **0**; `Bearer <token>` → **0**; `sk-` real token → **0** | PASS — no credential of any kind |
| C22 | high-entropy scan: contiguous `[A-Za-z0-9_\-\.~+/]{40,}` tokens, excluding 40/64/128-char pure-hex digests, entropy ≥ 4.0, ≥ 3 character classes | 0 | 366 candidate 40+ tokens → 40-hex/64-hex digests all excluded as sha1/sha256 → **2** residual: `pluginrel_6ae839cbc3c88191a906f64d31f0e449` in `host_notes.md` and in `g/VERIFY_REPORT.md` (same value, ent 4.22) | PASS — a plugin *release* identifier (`pluginrel_` + 32-hex content id), as the evidence itself states |

Known-prefix regex (`gh[pousr]_`, `github_pat_`, `sk-`, `AKIA`, `AIza`, `xox[baprs]-`, `eyJ…`) over
both trees returned **0** matches. No secret material was read from any `API KEY` path; the GitHub
token was used only through the pre-existing curl config and never printed.

## Mismatches

**None.** 23 of 23 checks passed.

## Residual observations (no effect on the verdict)

1. `PIPD-LS-SP` main has a `cancelled` intermediate run (`41487070321`, `be72c90`) predating the closing
   merge; the closing SHA's own run and check-run are green.
2. `evidence/pp261102/m/` (M2b strict/partial outputs) exists but was not named in the claim.
3. `05`/`06` live under `pp261102` only, as described above.

## How to reproduce

```bash
cd C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/scratch
curl -s --config ./gh.curlrc https://api.github.com/repos/shw097-team/SBL/commits/main
curl -s --config ./gh.curlrc https://api.github.com/repos/shw097-team/PIPD-LS-SP/commits/main
curl -s --config ./gh.curlrc "https://api.github.com/repos/shw097-team/SBL/actions/runs?branch=main&per_page=10"
curl -s --config ./gh.curlrc "https://api.github.com/repos/shw097-team/PIPD-LS-SP/actions/runs?branch=main&per_page=10"
for n in 15 18 20; do curl -s --config ./gh.curlrc https://api.github.com/repos/shw097-team/SBL/pulls/$n; done
for n in 26 28;    do curl -s --config ./gh.curlrc https://api.github.com/repos/shw097-team/PIPD-LS-SP/pulls/$n; done
sha256sum C:/Projects/Agent_Workspace/_candidate_sbl_tpm_sp_20261102/output/sbl-tpm-sp-0.3.0-rc.2-private.zip
python C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/gstack2/_scan_tokens.py \
  C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/gstack2/_token_hits.json
python C:/Projects/Agent_Workspace/_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01/gstack2/_scan_entropy.py \
  evidence/pre-primary-20261102 evidence/pp261102
```

Helper scripts in this directory: `_scan_tokens.py` (token-shape census), `_scan_entropy.py`
(high-entropy census), `_check_zip.py` (member/skill counts), `_token_hits.json` (raw token-scan hits).
