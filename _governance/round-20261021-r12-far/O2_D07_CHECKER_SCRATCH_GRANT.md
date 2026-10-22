# O-2 / D-07 — Checker scratch grant and subject freeze (FAR R12)

**Worker**: `t_c7c44c52` · **Decision id**: `DEC-R12-D07-O2-20261023` · **Date**: 2026-10-23 (UTC+8)
**Adjudication applied**: FAR R12 §3 (D-07 / O-2 rows) as refined by `FAR_R13.md` §3 —
the checker does **not** need write access to the candidate; it needs an isolated output
root plus a disposable staged copy. Authorization is a record of
**scope + expiry + subject digest**, not a blank writable pass.

---

## 1. Decision

**O-2 = GRANT.** Scope is exactly one checker-only scratch round root; the candidate
repository stays read-only; the subject is bound by a frozen byte manifest; the grant
carries a 24-hour expiry and voids itself.

| Field | Value |
|---|---|
| Grant record | `out/GRANT.json` (schema `HGK-CHECKER-SCRATCH-GRANT/1`) |
| Holder | checker role (VERIFY lane), role-based not model-based |
| Scope | `tmp/**`, `out/**`, `staged/**` under the round root only |
| Expiry | 24h from grant; expired grants are void, re-grant is one record |
| Subject digest | `origin/main` @ `dc5428f2`, tree `3f95125c`, 225 files, rollup `eb5325d4…` |
| Enforcement | explicit grant + sha256 digest guard + temp-root redirection. Writes outside scope are **detected, not OS-prevented** (measured: codex-lane `-s read-only` / `-s workspace-write` refuse every `CreateProcess` on this host, so an OS read-only sandbox cannot execute the suite; house recipe is full access + before/after guard) |

## 2. Subject freeze

| Field | Value |
|---|---|
| Freeze record | `out/SUBJECT_FREEZE.json` (schema `HGK-SUBJECT-FREEZE/1`) |
| Frozen ref | `origin/main` @ `dc5428f23d15f0ec56cbc3d25b22f5381fce8771` (remote readback `git ls-remote` == local; PR #6–#8) |
| Ancestor check | the R12 docs/claims alignment `4519f768` (PR #6) **is** an ancestor of frozen main — the claims work is landed, not dangling |
| Manifest | 225 files / 1,570,225 B staged; rollup `sha256` over sorted `<relpath> <sha256>` lines = `eb5325d4abd00aeb…`; manifest digest reported separately from the rollup |
| Claim ceiling | byte-identity of the staged copy to the frozen git tree at freeze time. Not an acceptance, not owner-signed |

Note: the **local** `main` in `C:/Projects/Agent_Workspace/SBL` is stale (`bedc119`,
2026-10-20); remote main advanced to `dc5428f` via PR #6–#8. Any future round quoting
"main" must quote the remote readback, not the local branch.

## 3. Mechanism probes (raw kept under `out/`)

| Probe | Result | Evidence |
|---|---|---|
| P1 admitted write inside the granted root | **ADMITTED**, host-side readback sha256 matches | `PROBES.json` |
| P2 temp redirection (child `tempfile.mkstemp`) | landed inside granted `tmp/`, exit 0 | `out/p2_tmp_redirect.log` |
| P3 guard discrimination (mutate one subject byte → rollup changes → restore → rollup matches freeze) | **GUARD_DISCRIMINATES**; restore verified against the frozen rollup | `PROBES.json` |
| P4 non-interference with the product repo | `git status --porcelain` identical before/after the whole round | `PROBES.json` |

## 4. One real bounded run in the granted scratch (raw kept)

First attempt staged the subject with `git archive | tar -x` (no `.git`).
Result: **4 git-dependent tests failed** (`test_bind_repo_context_*`,
`test_git_applies_lf_to_the_shipped_text_files`,
`test_two_independent_builds_are_byte_identical`) — the failures measured the
*staging method*, not the subject. Disclosed, not hidden.

Corrected staging: `git clone --no-hardlinks` + `git checkout dc5428f2`
(real `.git`, subject outside every product repo, at
`C:/Projects/Agent_Workspace/_r12o2_checker_scratch/round-20261023/staged`).
Then, with `TMP`/`TEMP`/`TMPDIR`/`SBL_TEST_TMP` all redirected into the granted
`tmp/`, `PYTHONDONTWRITEBYTECODE=1`, `pytest -p no:cacheprovider`:

| Run | Result |
|---|---|
| Full SBL suite (220 collected) | **exit 0**, 218 passed / 2 skipped / 0 failed, 312.7 s, log sha256 `8172aa6f…` (run2) |
| Control-package pin | **`CONTROL_PACKAGE_PINNED`** — 14 docs, 17,473,442 B, rollup `01b972c80341e1b8` all match, exit 0 |
| Subject tree after run | `git status --porcelain` empty — the checker run left the frozen subject byte-clean |

This is the capability R7's checker lacked: R7 C6 returned `INCONCLUSIVE — NOT ACCEPTED`
solely because its sandbox forbade every filesystem write (two-build comparison, full
pytest, mutation experiments could not run). The granted scratch makes those steps
executable, with the candidate still read-only.

## 5. Recipe refinement (measured, feeds the lane skill)

FAR_R13 §3.3 allows "a staged copy via `git worktree` or `cp -r`". Measured here:
**a `git archive`/plain-copy extraction is NOT equivalent** for any suite with
git-dependent tests — repo-context, `git check-attr`, and reproducible-build tests
measure the staging artefact and fail. Staged copies for test execution must carry a
real `.git` (clone or worktree) pinned to the frozen commit.

## 6. What this does NOT claim

- Not an independent-checker verdict. R9-02's close condition still requires one
  VERIFY lane round against the frozen subject producing `ACCEPTED` in a readable
  artifact; this grant removes the blocker, it does not satisfy the condition.
- Model-axis independence is **not** claimed: the current VERIFY arm
  (`opencode-go/deepseek-v4.1-flash`) is the same model as PLAN
  (`SOD006-C6 OPEN_OWNER_ORDERED`) — process/lane/evidence-path separation only.
- No permit, no native effect, no host installation, no completion percentage.
- The first (archive-staged) run's 4 failures are a disclosed staging defect, fixed by
  re-staging; they are not product defects and were not counted as such.

## 7. Prepared one-line edits for the synthesizer (`t_5f76be91`)

This worker did **not** edit the shared `_r12_docs` study/tasks files (hotspot:
four siblings + O-1's uncommitted edits live there; consolidate once, at the synthesizer).

- `openspec/changes/far-r12-20261021/tasks.md` line 17:
  `- [!] O-2 grant an isolated writable scratch root to the checker (unblocks R9-02).`
  → `- [x] O-2 GRANTED 2026-10-23 (DEC-R12-D07-O2-20261023): checker-only scratch round root, candidate read-only, subject frozen at origin/main@dc5428f2 (225 files, rollup eb5325d4…), 24h expiry, digest guard discriminates. Full SBL suite 218 passed / 2 skipped / 0 failed inside the granted scratch; control-package pin CONTROL_PACKAGE_PINNED; subject tree unchanged. R9-02 acceptance round itself still OPEN. Record: _governance/round-20261021-r12-far/O2_D07_CHECKER_SCRATCH_GRANT.md.`
- `FAR_DEVIATION_STUDY.md` D-07 row: append `**CLOSED-GUARD 2026-10-23**：grant 已落地（scope+expiry+subject digest），候選唯讀；R9-02 驗收回合仍 OPEN`.
- `FAR_DEVIATION_STUDY.md` O-2 row: 授權格 → `**已授權 2026-10-23**（`DEC-R12-D07-O2-20261023`，24h expiry，scope 限 checker scratch round root）`.

## 8. Rollback

Delete the round root; the grant self-expires in 24 h. No product file was written in
this round (P4 + `git status` readbacks). The evidence-branch commit is additive.
