# rc.2 engineering closeout — tasks

Status vocabulary: `[x]` = done and read back in this closing pass · `[~]` = partially done, gap stated ·
`[ ]` = not done, owner named. A bare `[ ]` with no note would be a defect.

No task below changes code. Every command is read-only; the only writes in this change are these three
documents.

## Paths used

- `RUN` — `_run_sbl_tpm_sp_20261102/RUN-20261102-GJ02-01` (this run directory)
- `WT` — `_candidate_sbl_tpm_sp_20261102/patch` (`sbl-wt` and `pipd-wt` are git worktrees of the two repos)
- `PY` — `_candidate_sbl_tpm_sp_20261102/.venv-sbl/Scripts/python.exe` (CPython 3.11.9)

## 1. Package and host identity

- [x] 1.1 Candidate zip identity re-read: sha256 `3a9da655…26a8`, 173 members, 14 Skills, CRC OK; the
      sealed input `c4181e24…` is unchanged.
      Receipt: `RUN/00_run_manifest/00_run_manifest.json` (`package`).
- [x] 1.2 Real host install on an isolated `CODEX_HOME`:
      `codex plugin add sbl-tpm-sp@sbl-pre-primary-local` → *installed, enabled, 0.3.0-rc.2*
      (codex-cli 0.164.0); remove → *not installed*, reinstall → *installed, enabled*.
      Receipts: `RUN/raw/host_final_add.txt`, `host_remove.txt`, `host_reinstall.txt`.
- [x] 1.3 Model route `deepseek-v4.1-flash` via `opencode_go` confirmed from the run's own
      `host_notes.md` and from the lane receipt `served_arm=opencode-go/deepseek-v4.1-flash`,
      `nonce=None` (a lane-model receipt, **not** an effect grant).
      Receipt: `RUN/00_run_manifest/00_run_manifest.json` (`host.model_route`).

## 2. M2 — author gate on the rc.2 bundle

```sh
$PY WT/sbl-tpm-sp/scripts/pre_v2_gate_r2.py bundle_r2
```

- [x] 2.1 Re-run in this closing pass: **exit 0**,
      `{"verdict":"AUTHOR_CONTRACT_CONSISTENT","requirements":2,"cases":2,
      "candidate_sha256":"93387936…d405","effect_state":"DESIGN_ONLY_NOT_ADMITTED",
      "authority":"AUTHOR_SIDE_DESIGN_ONLY","source_authority":"ORIGINAL_OWNER_UNVERIFIED",
      "host_invoked":"NOT_RUN","native_e2e":"NOT_RUN","checker":"NOT_RUN","release":"FAIL_CLOSED"}`.
      The gate proves byte/id consistency only — not authority, grant or independence.
- [x] 2.2 Three negatives fail closed (verified independently in `RUN/gstack/VERIFY_REPORT.md`):
      `PlannedTQAEP` deleted → exit 1; PI polarity flipped with fully recomputed SHAs →
      `PI_TRACE_OR_ORACLE_MISMATCH`; `checker_execution_receipt` injected with a re-signed artifact
      SHA → `FORBIDDEN_DESIGN_KEY:$.checker_execution_receipt`; an unmodified control copy still exits 0.
- [~] 2.3 Publish the M2 evidence. The bundle and any gate output are **absent** from the pushed
      evidence tree of PR #18, so the fail-closed proof currently exists only in the `gstack/` run.
      Owner: round owner (next evidence PR). See `RUN/gstack/VERIFY_REPORT.md` "Observations" 1.

## 3. M2b — PIPD four-object denominator (merged)

```sh
cd RUN/01_products/pipd
PYTHONPATH=WT/pipd-wt/src $PY -m pipd_ls_sp.cli validate --bundle bundle.json --require-four
PYTHONPATH=WT/pipd-wt/src $PY -m pipd_ls_sp.cli validate --bundle bundle_missing_tqaep.json --require-four
```

- [x] 3.1 Full bundle: exit **0**, `scope=FOUR_OBJECT`, `complete=true`, `checked=4`, `missing=[]`,
      `closure=FULL`, `verdict=PASS`, `required=[PI-PKG, PD-PKG, ECP, TQAEP]`.
- [x] 3.2 Bundle without the TQAEP under the strict flag: exit **1**, `scope=PARTIAL_BUNDLE`,
      `complete=false`, `checked=3`, `missing=["TQAEP"]`, finding
      `{"contract":"*","kind":"DENOMINATOR","detail":"missing required object(s): TQAEP"}`.
      Note `closure` is still `FULL` — the graph among the three present records *is* closed. That is the
      distinction this change introduced, not a bug (see `design.md`).
- [x] 3.3 Merged as `7073fe2` (PR #26, parents `aeb0d47` + `67ba96e`); full PIPD suite 664 passed /
      20 skipped; 4 new tests.
      Read back: `git -C WT/pipd-wt log -1 --format='%H | %P | %s' 7073fe2`.
- [x] 3.4 The three `closure: FULL` assertions that must **not** move were located, not re-edited:
      `tests/test_s4ext_trace_closure.py` (lines 99 / 106 / 114) and
      `tests/test_s4ext_first_run_portable.py` (lines 162 / 187).
      Read back: `grep -rn 'closure' tests/*.py | grep FULL`.
- [ ] 3.5 Re-capture the archived evidence. `01_products/pipd/validate.out` and `validate_missing.out`
      predate the denominator and carry no `scope`/`complete`/`missing`; the same stale pair is what the
      pushed tree carries, and `m2b_partial.out` / `m2b_strict.out` were never published.
      This is a re-capture, not a code change. Owner: round owner.
      Evidence: `RUN/gstack/VERIFY_REPORT.md` Check 4 (**FAIL**).

## 4. M3 — natural-goal routing

- [x] 4.1 Fresh Codex session, `deepseek-v4.1-flash` via `opencode_go`, no skill named in the goal;
      goal asked only for the fix, the tests and "the planning documents the project requires".
      Receipts: `RUN/raw/m3_events.jsonl`, `m3_exit.txt`.
- [x] 4.2 Output: three planning documents plus four `@2` objects written by the host
      (`docs/product-requirement.md`, `docs/technical-architecture.md`, `docs/execution-plan.md`,
      `docs/pipd/{PI,PD,ECP,PlannedTQAEP}.json` + manifest/registry/source).
- [x] 4.3 The host's own bundle passes the author gate: `AUTHOR_CONTRACT_CONSISTENT`, 2 requirements,
      3 cases, exit 0.
- [x] 4.4 Canonical ACK attempted and **fails closed**: `checked 4`, first finding
      `PI-PKG/: Additional properties are not allowed ('claim_ceiling','requirements','schema','source_sha256')`
      and `'stable_semantic_contract' is a required property`.
      Receipt: `RUN/raw/m3_canonical_validate.out`. Recorded as `CANONICAL_ACK_HOLD`, not as a PASS.
- [ ] 4.5 Give the host-authored objects a canonical path (host writes canonical shapes, or the reader
      gains a declared `@2` adapter). Owner: PIPD owner + host. Out of scope for this record.

## 5. M4 — design-level governance

- [x] 5.1 Two dependent design steps completed with **0** human approvals; both runs byte-identical
      (KnownAnswer reuse, candidate `9338793684…`).
- [x] 5.2 READ/DRAFT ran with no grant, no issuer contact and no unrelated OPS/RELEASE gate.
- [x] 5.3 6/6 design-level refusals hold: cross-subject, blind retry, nested fake grant, false-qualified
      claim, wrong host, nested receipt.
- [x] 5.4 `NOT_RUN` stays stated: G06/G07/G08 native autonomy, settlement and UNKNOWN recovery
      (no broker, no spine).
      Receipt: `RUN/05_M1_M4_results.json` (`M4_thin_governance`).

## 6. Git / PR readback

```sh
git -C WT/sbl-wt  log -1 --format='%H | %P | %s' aac7ab9 24d1205 25a4c13
git -C WT/pipd-wt log -1 --format='%H | %P | %s' 7073fe2
```

- [x] 6.1 SBL: `aac7ab9` = *Merge pull request #15* (parents `24d1205` + `dadeb91`);
      `24d1205` = *evidence: pre-primary GJ02 run on a real Codex host (#18)*;
      `25a4c13` = *Merge pull request #20* (parents `67c29be` + `e148fda`). All three objects present and
      parents read back locally.
- [x] 6.2 PIPD: `7073fe2` = *pre-v2: additive planning adapters + four-object validate denominator (#26)*
      (parents `aeb0d47` + `67ba96e`); `67ba96e` = *fix(validate): name the four-object denominator,
      add --require-four*.
- [~] 6.3 PR #28 (PIPD docstring 14→13) is recorded as merged `a25fb56` in
      `RUN/06_closeout_addendum.md`, but that object is **not** in the local object database
      (`git cat-file -t a25fb56` → *unknown revision*). No fetch was performed — this round does not
      write to any repo — so the merge commit is carried from the round's readback, not re-verified here.
- [~] 6.4 `gh` is not available in this shell (`gh: command not found`), so PR *state* (open/merged) and
      the API-side merge parents were not re-read in this closing pass. The merge commits themselves are
      verified in 6.1/6.2; treat the PR-state column as carried from the round.

## 7. Decision

- [x] 7.1 Promotion decided once and recorded: **`PRE_V2_DESIGN_SIDECAR_READY`** +
      **`NATIVE_GOLDEN_HOLD`**; not generation-ready, not native-golden-pass.
      Receipt: `RUN/05_M1_M4_results.json` (`promotion`).
- [x] 7.2 Reason for the ceiling stated in terms of two unbound artefacts, not in terms of effort:
      `EFFECT_REGISTRY_UNBOUND` and `CANONICAL_ACK_HOLD`.
- [ ] 7.3 Bind an original Operation/Effect Registry (see `design.md` § "Next owner action"). Owner: PIPD
      owner. Nothing in this record fabricates one.

## Explicitly not done

- [ ] No code change of any kind: no test, schema, gate, adapter, validator or CLI byte is touched here.
- [ ] No Native qualification, no Release, no new governance plane.
- [ ] No claim-ladder movement for the host-authored objects; `@2` stays `@2`.
- [ ] No fix for `HOST-124` (sandbox `workspace-write` → `pwsh.exe` store alias → `exec_command`
      blocked, turn hangs to exit 124). Recorded, owner decision, not patched.
