# NARROW_REPAIR round — M1/M2/M3 fixed, M4 blocked by the VERIFY lane transport

Instruction: `SBL-HGK-THIN-POST-EIAR-20261020-R2` · `compiler_changeset: NARROW_REPAIR`
External input: `SBL-EIAR-20261020-R1`
Product candidate: `candidate/r2-20261020-v10` @ `2d1c32d6c48fdc09a7d529fc4535482283552487`
Superseded candidate: `candidate/r2-20261020-v9` @ `47a428a8ba3447ef3e1b2bc2ac5b12af83dfeefc` (its CI failed; see §2)

Claim ceiling for this round: **`CANDIDATE_ONLY`**. No merge, no tag, no release, no `INDEPENDENT_CASE_PASS`.

## 1. Verdict per blocker

| Blocker | State | Basis |
|---|---|---|
| M1 CI | `CLOSED_WITH_EVIDENCE` | Real GitHub CI on the candidate SHA: run `39411780991`, ubuntu job `118591058137`, windows job `118591058453`, both `success`, `136 passed, 1 skipped`, manifest step `{"ok": true}` |
| M2 write-set escape | `FIXED_MAKER_SIDE` | Code change + 3 tests; mechanism file `evidence/m2/M2_MECHANISM.txt` shows lexical in-scope / real escape on this host. **No independent receipt** |
| M3 G-KNOW false authority | `FIXED_MAKER_SIDE` | Cap raised above the largest book, skips recorded as coverage gaps, unindexed/covered-gap source ids refused, hits stamped non-authoritative. **No independent receipt** |
| M4 clean-room checker | `NOT_EXECUTED` | Four dispatches, four failures on the same lane transport error. Repairs below |

## 2. M1 — CI really runs the suite now, and the run that failed first was honest

`v9` (`47a428a`) CI: run `39411165230`, **failure** on both platforms. Not a product defect and not the old
`No module named pytest`: two test defects that only a hosted runner exposes.

1. `test_inventory_with_a_wrong_digest_is_refused` depended on the private source mirror. Without it every
   document reports `missing`, so the digest branch was never reached and the assertion on `reason == "sha256"`
   could not hold. The test now builds its own 14-document corpus, pins `FALLBACK_ROOT` at it with
   `monkeypatch`, asserts the good record passes and only then flips one digest.
2. `test_bind_repo_context_reads_clean_head` compared a literal path; Windows runners hand out 8.3 short
   names (`RUNNER~1`) while `resolve()` returns the long form. It now compares
   `normcase(realpath(...))` on both sides.

Both were reproduced from the run log archive (sha256 in `evidence/ci/CI_V10_SUMMARY.json`), fixed, and
re-verified on a clean Python 3.11.9 venv with the package installed from a copy — the shape CI uses —
before pushing.

M1 changes on `v10`:

- `Install test tooling` (`pytest>=8,<9`) runs **before** the suite; runtime dependencies stay empty.
- The Windows-only step that read `C:/Projects/Agent_Workspace/_sbl_src_mirror` is gone. A hosted runner
  cannot see it, and a step that can only fail is not a check. CI now runs
  `tools/verify_source.py --self-check`, which proves inventory and aggregate consistency and states
  `"byte_verification": "NOT_PERFORMED (no corpus on this host)"` in its own output. It cannot be mistaken
  for a green source freeze.
- The run line no longer passes a second `-q`. `pyproject` already sets `addopts = "-q"`, and a second `-q`
  raises the quiet level until pytest stops printing its summary — the trap that previously zeroed gate
  denominators. The job log now carries `136 passed, 1 skipped`.
- `tests/test_ci_contract.py` guards all of it: install before run, no mirror path, `--self-check` present,
  no second `-q`, and no `continue-on-error` / `|| true` / `if: false` that could swallow a failure.

## 3. M2 — the write set now refuses a destination outside the real root

`GovernedBuildBridge.apply` used `abspath` + `relpath`, which is a lexical test. A directory junction or
symlink inside an allowed prefix therefore carried the write outside the repository while every lexical
check passed.

`evidence/m2/M2_MECHANISM.txt` (this host, junction):

```
lexical_relpath : src/link/pwned.py -> in writeset: True
real_relpath    : ../outside/pwned.py -> in repo: False
```

The bridge now resolves the real destination and re-checks it against the real root and the writeset
immediately before the file is touched, and refuses with `SBL_E_WRITE_OUTSIDE_WRITESET`. Tests:

- `test_bridge_apply_negative_symlink_escape` — link inside the writeset to an outside directory **must**
  NACK, and the outside file must not exist afterwards.
- `test_bridge_apply_positive_inside_a_link_that_stays_inside` — a link whose real target is inside the
  root must still write; a containment check that refuses everything is not a fix.
- Existing lexical negatives unchanged.

Hosts that can create neither a symlink nor a junction skip with an explicit `ENV:` reason; on Linux CI the
symlink path runs. Windows runners may skip — that is disclosed, not hidden.

## 4. M3 — the knowledge locator no longer answers with false authority

Three defects, all from `sbl_core/gknow.py`:

1. `MAX_FILE_BYTES = 2 MiB` silently skipped DOC-05 (2,382,349 bytes, one of the fourteen authoritative
   books). A question about it was then answered from the nearest neighbour's chunks with a confident score.
2. A question naming a document that does not exist (`DOC-27`, `DOC-99`) was answered the same way.
3. Hits carried no authority marking, so retrieval could be read as entailment.

Now: the cap sits above the largest book; every skip and unreadable file is recorded in
`coverage_gaps` at index build; a question naming an unindexed source raises
`SBL_E_KNOWLEDGE_NO_ANSWER` declaring the unresolved ids; one naming a skipped source raises
`SBL_E_KNOWLEDGE_COVERAGE_GAP`; every hit is stamped `authority: NON_AUTHORITATIVE_LOCATOR` and the payload
carries `authority_note` saying a hit is a locator, not an entailment, an Oracle result or an approval.

Not fixed, and therefore stated as a limitation rather than papered over: CJK tokenisation, the 61 Windows
long-path files, and semantic recall. They are `HOLD_SCOPED`; the product must not claim CJK search or full
coverage, and no specification decision may be taken from a locator alone.

## 5. M4 — not executed, and why (this is the round's blocker)

Four dispatches of the mandated VERIFY route (`codex-cli`, `openai-codex/gpt-6.1-sol`, rank 2,
`required_arm == served_arm`), nonces `SBLR2-VERIFY-11..14`:

| Attempt | Receipt | Outcome |
|---|---|---|
| 11 | `runs-m4/VERIFY_candidate_2d1c32d.json` | `ERR_LANE_ALL_ROUTES_EXHAUSTED`, 247.8 s |
| 12 | `runs-m4b/...` | same, 490.1 s |
| 13 (+`-c prefer_websockets=false`) | `runs-m4c/...` | same; codex answered `session-flags: prefer_websockets is ignored` |
| 14 | `runs-m4d/...` | same, 188.2 s after the turn had started and emitted one agent message |

Exact error, byte-identical in all four:

```
ERROR codex_api::endpoint::responses_websocket: failed to connect to websocket:
HTTP error: 426 Upgrade Required, url: ws://127.0.0.1:10101/v1/responses
```

Diagnosis, with what was actually measured:

- The relay answers `http://127.0.0.1:10101/healthz` `200` (`opencodex 2.11.0`, pid 15564) and a `/v1/models`
  list; it does **not** serve `/v1/responses` over websocket — a handshake probe returns `426`.
- `10102` is the same service and also returns `426`; `10103`/`10105` (the lane-scoped doors seen in earlier
  receipts) are **down** (`000`), as is `10100`.
- The client-side workaround is gone: this codex build (`0.163.0-alpha.10.2`) rejects
  `-c prefer_websockets=false` as an unrecognised setting, so the override cannot restore HTTP-only.
- The attempt that got furthest also logged `Model metadata for gpt-6.1-sol not found. Defaulting to fallback
  metadata`; the lane catalogue lists `gpt-5.6-sol` and 89 others by `slug`, never `gpt-6.1-sol`.

So the mandated checker route cannot complete a turn right now. Per the standing instruction not to swap the
model plan silently, this round **stops here** instead of substituting a different checker.

**The freeze held.** Every attempt recorded `subject_mutation`: files `838 -> 838`, added `0`, changed `0`,
removed `0`. The failure mode that voided R7/R8 (`ERR_CHECKER_MUTATED_SUBJECT`) did not recur, because the
maker finished every write before dispatching and touched the subject for none of the four runs.

Remedies, cheapest first (owner decision, not mine to take):

1. Start the lane-scoped relay doors again (`10103` VERIFY_SECURITY, `10105` EXECUTE) and confirm each serves
   `ws://.../v1/responses`, then re-dispatch M4 unchanged.
2. Enable websocket transport on the `10101` relay, or pin a codex build that still honours
   `prefer_websockets=false`.
3. Register `gpt-6.1-sol` in `opencodex-catalog.json` so the client stops falling back to default metadata.
4. Only if none of the above is possible: authorise a different independent checker principal explicitly.
   I will not do that unilaterally; it would break the model SoD the instruction fixes.

## 6. TS / CHK affected rows only

| ID | State | Locator |
|---|---|---|
| TS02 G-KNOW M3 | `AFFECTED_RETEST` | `evidence/m3/M3_FOCUSED.txt`, `tests/test_gknow.py` |
| TS12 GJ02 / M2 | `AFFECTED_RETEST` | `evidence/m2/M2_FOCUSED.txt`, `evidence/m2/M2_MECHANISM.txt` |
| TS15 CI / license split | `AFFECTED_RETEST` | CI run `39411780991`; licence untouched (`R1` deferred) |
| TS16 three GJ + M2/M3 cases | `REUSED_PASS` | `G-GJ01-CLI 7`, `G-GJ02-PATCH 7`, `G-ROLLBACK 4`, suite 137 |
| TS17 isolated checker M4 | `BLOCKED` | §5 |
| TS18 publish candidate + evidence | `PASS_SCOPED` | candidate `2d1c32d` pushed; evidence branch follows |
| CHK02 G-KNOW NEG | `FIXED_MAKER_SIDE` | `tests/test_gknow.py::test_a_named_source_that_does_not_exist_is_refused`, `...::test_a_named_source_with_a_coverage_gap_is_refused` |
| CHK06 GJ02 symlink/junction | `FIXED_MAKER_SIDE` | §3 |
| CHK12 Windows+Ubuntu CI | `PASS` | §2 |
| CHK15 independent M4 | `BLOCKED` | §5 |
| CHK17 licence / release scope | `HOLD` | `R1`–`R3` deferred by instruction |

## 7. Local denominators (maker side, this host)

`11/11` gates `exit 0`; `G-SUITE-FULL` `137 passed`; per-gate denominators `46, 10, 9, 18, 7, 7, 7, 4, 137`;
`G-SEC-SCAN` `CLEAN`, `181` files, `0` hard findings; `py -3.11` green; clean 3.11.9 venv from a copy green.

## 8. What is still not proven

- No independent receipt for M1–M3 on `2d1c32d`. A maker-side test result is not a checker result.
- `M4`, and therefore `CONDITIONAL_MERGE_APPROVED`, is `NOT_GRANTED` this round. No PR is opened for merge
  approval; the branch is published so the external reviewer can read it.
- Release blockers `R1` (licence), `R2` (reproducible package), `R3` (native/HITL boundary) untouched —
  deferred by the instruction, and the licence is the owner's call, not mine.
- CJK retrieval, long paths, all 39 Host×SP grids, 149-child trace closure, `CR-ORACLE-001`, `N14`:
  unchanged `HOLD_SCOPED`.
