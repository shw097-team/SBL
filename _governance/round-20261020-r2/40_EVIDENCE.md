# 40 — Evidence pack, SBL v0.1 candidate (round R2)

```yaml
round: SBL-PIPDLS-20261020-R2
claim_ceiling: LOCAL_QUALIFIED_CANDIDATE   # never "accepted", never "released", never "production"
control_plane: HG-KSEOS
runtime_plane: current canonical Hermes (this session)
candidates:
  c1: ab17440ab68f8c7a1bd9702aba3624149d3f0506   # R1 FAIL (4 HIGH / 3 MED / 1 INFO)
  c2: 8640f0220e8209b83bc7bbdea4144084eaa7722a   # R2 FAIL (3 new HIGH + env)
  c3: 49dab082dcb638ebdf63996764f3473e5b1be60c   # R3 FAIL (1 new HIGH + 2 ENV); A..I closed 9/9
  c4: 72029221f01847e89f87555278447aace74601ec   # R4 FAIL (1 new MEDIUM)
  c5: 718a48d71ebb1a5860aafeb90b669a7e6ff15468   # R5 FAIL (2 new, both closed next round)
  c6: eb2e07c11dc44ef1789e7c3e468d43816057bc28   # R6 FAIL; sole item classified GATE TOOLING
  c7: f793e1d2fcfd5c136fa9f654452865e7b6e5677f   # R7 PARTIAL: 0 product findings, 0 new defects, ENV only
  c8: fb7af87aeeb0b596d6000404e2df9821e9205ccd   # CURRENT: gate env pinning + explicit ENV skip
continuation_contract:
  task_id: SBL-PIPDLS-20261020-R2-C1
  changeset: CONTINUATION
  verdict: PROMPT_COMPILE_PASS   # lint / activation / acceptance / compile all exit 0
  compiler_sha256: 2c282ad6539a465c3b1d751868cab98437a8f35e9728be686117e364a70857d9
  contract_sha256: 5e8a2399f43adb5fd60323a3007f3252fb471b4809f80bce0f14081cc9fed343
```

## 1. What a reader can run right now

```
git clone https://github.com/shw097-team/SBL
cd SBL && git checkout candidate/r2-20261020-v4
C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe -m pytest -p no:cacheprovider
C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe tools/run_gates.py
```
`pytest` alone is 119 tests; `run_gates.py` re-derives every gate and writes raw receipts under
`evidence/gates/`. Both are green on CPython 3.12.14 and 3.11.9 on this host.

## 2. Gates, with denominators (not just exit codes)

| gate | exit | denominator | raw receipt |
|---|---|---|---|
| G-CORE-MODULES | 0 | 44 | `evidence/gates/G-CORE-MODULES.stdout.txt` |
| G-MODES-NOEFFECT | 0 | 10 | … |
| G-KNOW | 0 | 6 | … |
| G-SP-ISOLATION | 0 | 18 | … |
| G-GJ03-BRIDGE | 0 | 7 | … |
| G-GJ01-CLI | 0 | 7 | … |
| G-GJ02-PATCH | 0 | 7 | … |
| G-ROLLBACK | 0 | 4 | … |
| G-SOURCE-FREEZE | 0 | — | `tools/verify_source.py --verify` → `ok true, docs 14` |
| G-SEC-SCAN | 0 | — | `CLEAN, 151 files, 0 findings` |
| G-SUITE-FULL | 0 | 119 | … |
| **total** | **11/11** | **222 executions** | `evidence/gates/GATES_RAW.json` |

The runner fails any pytest gate whose denominator is 0, so "green" cannot mean "measured nothing".

## 3. The three journeys (real, not simulated)

- **GJ01** `sbl-todo`: isolated `--data-dir`, `init`, `add --title` (unique id), `list --json`, a second
  process reading the same state (restart), duplicate/empty-title refusals with exit codes, `uninstall`
  refusing foreign files. 7 tests, `tests/e2e/test_gj01_cli.py`.
- **GJ02** brownfield patch: real `git init` fixture, `bind_repo_context` (HEAD + dirty + writeset),
  red→green, writeset escape refused (`SBL_E_WRITE_OUTSIDE_WRITESET`), stale HEAD refused
  (`SBL_E_STALE_HEAD`), rollback to the baseline tree hash. 7 + 4 tests.
- **GJ03** skill bridge: manifest discovery, `effective_load` trace, trigger/non-trigger, provider-off
  refusal (`SBL_E_PROVIDER_OFF`), forbidden action refusal, unload leaves no residue. 7 tests.

## 4. Source freeze

14 design books, `doc_count = 14`, aggregate
`754cf7bed08f58b89003a93cbf3e2d5349b85dd503121d38b74628683efcda3b`, re-derived by
`tools/verify_source.py --verify` and required to be exactly `DOC-00..DOC-13` (an empty or partial
inventory is refused). Corpus普查: 306 files under the read-only source root; the G-KNOW index built from
227 of them (23,174 chunks) is **local-only** — 127 MB of verbatim source text must not reach a public
remote, so only its digests are published (`16_GKNOW/LOCAL_ONLY_MANIFEST.json`).

## 5. Compiler and contract

`contracts/SBL_C0_C9_CONTRACT.json` → `lint`, `activation`, `acceptance`, `compile` all exit 0 with the
canonical `prompt_contract_compiler.py`; receipt `contracts/compiled/compiler-receipt.json`, thin command
`contracts/compiled/thin-prompt.md`. Verdict: `PROMPT_COMPILE_PASS` for contract shape only. The compiler's
own `independent_verification`/`runtime_readiness` fields remain `NOT_EVALUATED` — a compiled prompt is
not an accepted product.

## 6. Independent challenge history (this is the honest part)

| round | candidate | checker | verdict | what it found |
|---|---|---|---|---|
| R1 | ab17440 | `openai-codex/gpt-6.1-sol` (VERIFY_SECURITY r2), 494.79 s | **FAIL** | 4 HIGH + 3 MEDIUM + 1 INFO: principal impersonation, caller-owned ceiling, PASS unbound to evidence, scanner line-allowlist, empty source inventory, denominator undercount, 3.12-only test API |
| R2 | 8640f02 | same arm, 403.94 s | **FAIL** | SEC-03/VERIFY-01..03 **closed**; opened NEW-01 (constructor ceiling), NEW-02 (package exported key + digest helper), NEW-03 (allowlist inside the value), ENV-01 (fixture needed a clean git env) |
| R3 | 49dab08 | same arm, 410.81 s | **FAIL** | **A..I all closed (9/9)**; one new HIGH: `"xxxx=changeme"` collapsed to the placeholder `changeme`; two ENV findings (git fixtures, no 3.11 in its sandbox) |
| R4 | 7202922 | same arm | **FAIL** | `R3-NEW-01` closed; all 12 prior probes closed; one new MEDIUM: `attackerexample.com` matched the `example.com` allowance (no label boundary) |
| R5 | 718a48d | same arm | **FAIL** | `R4-NEW-01` closed; two new: the email matcher truncated the domain at `-`, and a missing root returned CLEAN instead of an error |
| R6 | eb2e07c | same arm | **FAIL** | `R5-NEW-01`/`R5-NEW-02` closed (9 variants blocked); its only remaining finding was classified by the checker itself as **GATE TOOLING**: `alice!user@…` truncated to an allowlisted local part |
| R7 | f793e1d | same arm | **PARTIAL** | `R6-NEW-01` **closed** (6 attack variants), all 16 prior probes **closed**, **0 new defects**, **0 product findings**. The PARTIAL was environmental: a third-party pytest plugin autoloaded on the checker host zeroed nine gate denominators, and its sandbox could not create a git repository |
| R8 | fb7af87 | same arm | **PARTIAL** | Both changes judged **sound** (`change_1`: no pytest-plugin dependency exists, so pinning autoload weakens nothing; `change_2`: the skip cannot mask a product defect). Every pytest gate now reports a positive denominator on the checker's host (44/10/6/18/7/7/7/4/125) — the zero-denominator problem is gone. All 16 prior probes **closed**. Verdict is PARTIAL for two reasons that are not product defects: its own adversarial probe files under `_local/verify10/` tripped `G-SEC-SCAN` in its copy, and one **LOW tooling** item — `tests/test_core_modules.py:140` assumes `tempfile.mkdtemp` lands outside any git worktree |

Repairs are recorded with the test that would fail if the fix were removed:
`16_REPAIR_R1_RESULT.md`, `18_REPAIR_R2_RESULT.md`, `19_REPAIR_R3_RESULT.md`.

Two things this says plainly:
1. The first three candidates were **not** safe, and the checker proved it each time with its own probes.
   A maker-side green suite was not evidence of a sound property.
2. The EXECUTE writer lane failed twice on the repair shape (`ERR_LANE_ALL_ROUTES_EXHAUSTED`), so PLAN
   authored the repairs and a **different principal** re-verified them. That substitution is a governance
   deviation, recorded in `16_REPAIR_R1_RESULT.md`, not a hidden shortcut.

### 6.0 Governance deviation: the orchestrator kept writing while the checker ran

Both of this round's checker dispatches returned `ok: false, code: ERR_CHECKER_MUTATED_SUBJECT` while
also producing a usable verdict. The guard is right and the fault is mine: I committed the evidence
branch and consolidated receipts inside `SBL` during the checker windows.

| round | candidate | files before → after | added | changed | removed |
|---|---|---|---|---|---|
| R7 | f793e1d | 638 → 648 | 10 | 4 | 0 (all `.git` internals: my branch and commits) |
| R8 | fb7af87 | 689 → 734 | 50 | 17 | **5** (evidence consolidation: `RECEIPTS_INDEX.json`, `MANIFEST.json`, and the removal of the copied receipt files) |

What this does and does not break:
- **Does not break the probe results.** The checker printed `git rev-parse HEAD` and worked in its own
  copy, so its findings describe the tree at `f793e1d` / `fb7af87`.
- **Does break the freeze claim.** A frozen-subject receipt requires that nothing under the subject
  move, and in R8 files were removed and changed. An external assessor should treat R8 as
  *checker findings on a copy of fb7af87*, not as a frozen-subject acceptance.
- **Correction to an earlier note in the skill:** `subject_mutation` does **not** treat `added` as
  merely informational — this dispatcher fails the receipt on added, changed **and** removed.

Rule adopted from here: all orchestrator writes for a round finish **before** the checker is
dispatched, and nothing under the subject is touched until its receipt returns. Evidence publication
happens after the receipt, not during it.

### 6.1 Open after round 8 (recorded, deliberately not fixed under this SHA)

| id | class | finding | decision |
|---|---|---|---|
| `VERIFY10-TOOLING-01` | LOW, tooling | `tests/test_core_modules.py:140` assumes the temp root is outside any git worktree; if `TMP`/`TEMP` point inside a repo, git discovers the enclosing repository and the "not a repository" negative case does not raise | **Open.** Fixing it now would produce a ninth candidate that no checker has seen, which is worse than publishing the SHA the checker actually examined. It is a test-hygiene assumption, not a product behaviour; the next round should fix it *and* re-run a checker on that SHA |
| checker probe artifacts | not a defect | the checker writes adversarial literals under `_local/verify10/`, which the repo scanner then correctly rejects, so its `G-SEC-SCAN` exits 1 | **No action.** The scan is doing its job on files the checker created; the candidate's own tree is CLEAN over 175 files |

## 7. What is NOT done — do not read this pack as more than it is

| item | state |
|---|---|
| `SWOF_CONNECTED` | **blocked** by design: no SWOF native ACK/permit exists on this host, so the mode refuses to start (`SBL_E_REQUIRES_NATIVE_ACK`). Not claimed as connected. |
| `PREW3_SHADOW` | implemented as `NoEffect` only (10 gate assertions); no world-effect path exists to prove against. |
| SBL 39 mode gates | matrix generated and tested for count/uniqueness/no-effect; not exercised against a real host×SP cell. |
| U01–U50 / 149 children, P01–P07, M00–M15 trace closure | **not built**. The contract has 17 ACTIVE capabilities with acceptance edges; the full requirement corpus closure is not done. |
| 24 slots / 25 methods / 386 keys | table built with 441 rows, **1 ACTIVE / 6 NATIVE_SUBSTITUTED / 423 DEFERRED / 8 PROHIBITED**; the corpus states 386 and the extraction reproduces it, but almost nothing is installed by design. |
| PIPD P4 native intake, ECP/permit, TQAEP compilation | **not executed** — no native PIPD writer on this host; only the C0..C9 contract and this repo's own gate/evidence layer exist. |
| GitHub CI | workflow committed; **no Actions run has been observed**, so CI green is not claimed. |
| Branch protection / ruleset | not configured (`protected: false` on every branch) — open TT. |
| LICENSE | not chosen; that is an Owner ruling, not a guess the build may make. |
| Release / production | not requested, not claimed, not possible without a human/native gate. |

## 8. Rollback

```
git -C C:/Projects/Agent_Workspace/SBL reset --hard ca6830d9fc9d89b7b87e818670dd67b393472d79   # round bootstrap
git -C C:/Projects/Agent_Workspace/SBL branch -D candidate/r2-20261020-v4                       # local
# remote: delete the four candidate/* branches by name; main is untouched since bootstrap
python -m sbl_cli.sbl_todo uninstall --yes --data-dir <dir>                                     # GJ01 uninstall
```
`main` still points at the bootstrap commit `ca6830d`; every candidate is an immutable side branch.

## 9. Publication

Repo `https://github.com/shw097-team/SBL` (public, default `main`), branches
`candidate/r2-20261020`, `-v2` … `-v8` with readback matching the local SHAs
(`30_PUBLICATION_READBACK.json`). Token handling: read only by a local credential helper script; never
printed, never in argv, never in a commit — the scanner gate enforces the "no credential in the tree" side
of that.


## 10. NARROW_REPAIR round (external report SBL-EIAR-20261020-R1)

This section is the pointer for the repair round that follows the external acceptance report; the detail
lives in `70_NARROW_REPAIR_M1_M4.md` and the machine-readable return in `75_EVIDENCE_RETURN.json`.

| Item | State |
|---|---|
| Candidate | `candidate/r2-20261020-v10` @ `2d1c32d6c48fdc09a7d529fc4535482283552487` (supersedes `47a428a`, whose CI failed) |
| M1 CI | `CLOSED_WITH_EVIDENCE` — run `39411780991`, both platforms `136 passed, 1 skipped` |
| M2 write-set escape | `FIXED_MAKER_SIDE` — real-path containment, `SBL_E_WRITE_OUTSIDE_WRITESET` |
| M3 G-KNOW false authority | `FIXED_MAKER_SIDE` — coverage gaps recorded, unindexed ids refused, hits non-authoritative |
| M4 clean-room checker | `NOT_EXECUTED` — four dispatches died on `ws://127.0.0.1:10101/v1/responses` `426`; freeze verified `838 -> 838` each time |
| Merge / release | `NOT_GRANTED` — no independent receipt, no licence ruling |

The earlier statement in `30_PUBLICATION_READBACK.json` that CI had never been observed is a historical
record of that moment. GitHub CI has since been observed, and it failed eight times before M1; this round's
runs are the authoritative state.
