# CHECKPOINT — SBL R7 / FAR-023 / owner order 2026-10-21

**Paused by owner instruction (shutdown).** Every background task is stopped; nothing is running.
Resume by reading this file, then the three "resume" blocks at the bottom.

| | |
|---|---|
| Session | `20261021_111630_fdf37c` |
| Paused at | 2026-10-21 ~15:55 CST |
| R7 task id | `SBL-R7-FAR-RESIDUAL-CLOSURE` |
| R6 task id | `SBL-R6-DOC00-13-CONTINUATION` |
| FAR run id | `FAR-20261021-023-sbl-r7-residual-closure` |
| Self-check state | **15 / 16 PASS** (only C6 = independent checker verdict is open) |
| Contract state | **OPEN / PARTIAL** — unchanged by this round; see "Honest ceilings" below |

---

## 1. Where everything stands

### 1.1 Repositories (all remote SHAs equal local — verified by read-back)

| Repo | Branch | HEAD | Remote | State |
|---|---|---|---|---|
| `C:\Projects\_sbl_r4\c3v2` (SBL product) | `candidate/r7-20261021-repro-build` | `26a289f` | `26a289f` ✔ | clean |
| `C:\Projects\Agent_Workspace\SBL` (SBL evidence) | `evidence/r7-20261021-c7` | `9bb58cb` | `9bb58cb` ✔ | clean |
| `C:\Projects\Agent_Workspace\Fabric` (FAR) | `pub/far-minimax-mandate-20261021` | `9b2ae5e` | `9b2ae5e` ✔ | clean |
| `C:\Projects\Agent_Workspace\HG-KSEOS` (control plane) | `codex/hgk-final-closure-002` | `3a73b38` | **no remote** | local-only |

Remote = `https://github.com/shw097-team/SBL.git` and the Fabric repo. The GitHub credential
source is `C:\Projects\Agent_Workspace\API KEY\GITHUB-REPO_SHW097-4.txt`; it is only ever
consumed through the sealed askpass helper
`C:\Projects\Agent_Workspace\_handover\R5R3-20261016-preview4-closeout\_askpass_r5r3.cmd`.
**Do not print it, do not commit it.**

The proven push invocation on this host (GIT_ASKPASS alone is ignored by git here — the
`-c core.askPass=` form is what works):

```bash
cd <repo>
GIT_ASKPASS="C:/Projects/Agent_Workspace/_handover/R5R3-20261016-preview4-closeout/_askpass_r5r3.cmd" \
GIT_TERMINAL_PROMPT=0 \
git -c credential.helper= -c credential.interactive=always \
    -c "core.askPass=C:/Projects/Agent_Workspace/_handover/R5R3-20261016-preview4-closeout/_askpass_r5r3.cmd" \
    push origin <branch>
```

---

## 2. What this round actually achieved

### 2.1 Owner order 2026-10-21 applied (GPT quota restored)

The owner restored PLAN and VERIFY/SECURITY to **GPT 6.1 SOL-MEDIUM (Open AI OAuth)** and kept
EXECUTE on **DeepSeek V4.1 Flash (OpenCode Go)**. This is applied to **every governed surface at
once** — the canonical pool, the routing registry, the model-lane assignment, the Hermes lane
surfaces, and the registry's 33 drift-pinned bindings were re-spinned together.

Applied and committed in HG-KSEOS:

* `f4a2ec4` — pool + registry + assignment rebind (PLAN→GPT, EXECUTE→DeepSeek, VERIFY→GPT);
  33 bindings re-pinned; `source_of_routes` revision/SHA recomputed from the new assignment bytes.
* `bf209cf` — the pool's `identity_overlaps_recorded_not_enforced` is now **derived from the pool**
  by `recompute_pool_overlaps.py`, not hand-written. A hand-written overlap list drifts the moment
  the pool is re-bound and then misreports a collision as absent.
* `3a73b38` — a handoff checkpoint written by a concurrent process (not mine).

**Live proof, not assertion** — three lane probes run against the canonical pool *after* the
rebind, each with a nonce, each with a usage receipt (HTTP 200):

| Lane | Served arm | Rank | Transport id | Receipt |
|---|---|---|---|---|
| PLAN | `openai-codex/gpt-6.1-sol` | 1 | `gpt-6.1-sol` (bare) | `probe_final_PLAN_gpt.json` |
| VERIFY_SECURITY | `openai-codex/gpt-6.1-sol` | 1 | `gpt-6.1-sol` (bare) | `probe_final_VERIFY_gpt.json` |
| EXECUTE | `opencode-go/deepseek-v4.1-flash` | 1 | — | `probe_final_EXECUTE_deepseek.json` |

Receipts are sealed in
`SBL/_governance/round-20261021-r7/40_VERIFY/lane_rebind_gpt61/` (byte-identical copies of
`HG-KSEOS/evidence/review/OWNER-ORDER-20261021-GPT-QUOTA-RESTORED/`).

**The two defects the apply itself found and fixed** (both caught by the HG-KSEOS conformance
suite, not by inspection):

1. **Registry `fallbacks` dropped the demoted primary.** After promoting GPT, the registry's
   fallback list no longer contained `minimax-m3.1-flash-free`, so a GPT failure had nowhere to
   fall back to. Fixed by `repair_registry_fallbacks.py`; minimax is now first fallback on all
   three lanes.
2. **The SoD declaration was stale.** `sod_invariants.pairs` still declared
   `EXECUTE↔VERIFY: distinct_required: false` — true under the old MiniMax-everywhere state,
   false now that EXECUTE runs DeepSeek and VERIFY runs GPT. `check_sod` returns True (the
   separation genuinely holds), but the DECLARATION did not match reality. Fixed by
   `update_registry_sod.py`: `EXECUTE↔VERIFY` is now `distinct_required: true`, while
   `PLAN↔VERIFY` stays `false` because both are GPT **by owner order** (SOD006-C4,
   `OPEN_OWNER_ORDERED` — process/lane/evidence-path separation only, model independence
   explicitly NOT claimed).

HG-KSEOS conformance after both fixes: **179 passed, 90 subtests passed**. Drift gate: **0 findings**.

### 2.2 Product repair (SBL candidate `26a289f`)

The independent checker (round 2, GPT arm) found three real defects, all now fixed:

* **W1** — `_has_build()` probed with `import build`. This repo contains a gitignored `build/`
  directory, so `import build` succeeded as a **namespace package** and the resolver picked an
  interpreter that could not build. Now probes `python -m build --version`.
* **W2** — every test asserted a *local* property; **nothing built anything twice**. The checker
  demonstrated a mutation that turned the suite green while destroying reproducibility. Now there
  are two end-to-end assertions: two builds as **separate processes** compared byte-for-byte, and
  the epoch read in two processes more than a second apart and required to be equal.
* **W3** — the mutation probe copied a **linked worktree's** `.git`, which is a pointer into a
  shared admin dir, so the copy's `git add -A` staged into the **protected** tree. Now the copy
  gets its own git dir, and the probe asserts the protected repo's staged tree / HEAD / status
  are unchanged.

Measured: **207 passed / 2 skipped**. Focused reproducibility+mutation: **15/15 PASS**. Six
contract-breaking mutations (MUT_A…E plus the checker's MUT_D/MUT_E) are all caught.

> **Correction worth keeping:** the "protected tree was written through" alarm was a **false
> positive**. `git` rewrites the index file's stat cache on any read, so the raw index file's
> bytes change without anything being staged. The correct invariant is the **staged tree**
> (`git write-tree`), the **cached diff**, **HEAD** and **status** — all confirmed unchanged.
> Do not reintroduce a raw index-file hash comparison.

### 2.3 Reproducibility receipt regenerated for the repaired head

`50_TS06/regen_repro_result.py` builds twice, independently, with the candidate's own build tool
and seals the artefacts:

* wheel `4e78688d3ee1a1295a622253b8d1804fb3e05c935221eb7b3d0b6f0ff6ea5e19`
* sdist `7c974cf772013736a3df8d6e6813bbceb237ccb7b351f2c27db4ec9cea55d8b2`
* `identical: true`, wheel distinct member timestamps: **1**

The wheel digest is **unchanged** from the pre-repair receipt — the stronger statement: the repair
did not alter the built product. The sdist digest changed because the source changed.

### 2.4 FAR-023 artifact set

35 files, restored to the working tree and committed on the Fabric branch (they had been committed
earlier as `8fdb9f3` on `pub/far-lane-remediation-20261021`, but a concurrent process switched the
working tree to another branch and the files left the disk — which is what broke self-check
C5/C13/C15 with `FileNotFoundError`). All 35 are present again; the self-check reads them.

---

## 3. What is OPEN — do not claim these as done

| id | item | why it is still open |
|---|---|---|
| **C6** | independent checker verdict for `26a289f` | attempt 3 was dispatched on the GPT arm and **stopped by this pause**. No verdict. Not a pass, not a failure. |
| C7 | candidate/evidence published | **now satisfied** — both branches pushed, remote == local. Re-run self-check to confirm the check flips. |
| C9 | reproducibility | **now satisfied** — receipt regenerated for `26a289f`. |
| — | HGK workorder | still `ROLLED_BACK`; acceptance `NOT_RUN`. Do **not** record PASS before the C6 verdict lands. |
| — | canonical Hermes formal binding receipt | still missing. The governed profile `profiles/hgk-governed/config.yaml` is correct (GPT 6.1 SOL / medium) and the pool/registry are correct, but there is **no explicit Runtime/Orchestration Plane binding, permit or rollback receipt**. Correct profile ≠ binding receipt. |
| — | 4 contract capability bindings | 4 capabilities still point at `ACC-SBL_SHARED_CORE`; the compiler SSOT was not rebuilt. |
| — | PR #2 merge | R6 candidate `a6bcdd0` is a clean fast-forward over `main`, but **no merge actually happened**. No merge receipt. |
| — | R6-TS06-A | `0.1.1rc1`, experimental wheel/sdist, clean-venv lifecycle and release digest are not complete. |
| — | DOC-00…13 full contract | **OPEN / PARTIAL**. Native PI/PD/ECP, ChatGPT 3 host plugin, full multi-Kind production, 149 children, 38 surfaces, cross-host and a signed `PASS_CHALLENGE` are all unclosed. |
| — | HG-KSEOS upstream admission defect | `ProjectLifecycleController._repo_head()` takes the CWD instead of the project repo and swallows `InvariantViolation`. |
| — | native / owner-authorised items | owner pre-authorisation is **not** a native issuer, a merge, a release or a host authorisation. These stay OPEN. |

---

## 4. Resume blocks

### 4.1 First thing: the independent checker (closes C6)

This is the only thing standing between the round and a verdict. Re-dispatch **identically**:

```bash
cd C:/Projects/Agent_Workspace/HG-KSEOS
./.venv/Scripts/python.exe scripts/hgk-lane-dispatch.py \
  --lane VERIFY_SECURITY \
  --require-arm openai-codex/gpt-6.1-sol \
  --nonce R7CHK-NC-20261021-A3 \
  --timeout 1500 \
  --round SBL-R7-FAR-RESIDUAL-CLOSURE \
  --attempt 3 \
  --brief "C:/Projects/Agent_Workspace/SBL/_governance/round-20261021-r7/40_VERIFY/CHECKER_BRIEF.md" \
  --json-out var/R7-LANES/verify_chk_r7_a3.json \
  --guard-subject "C:/Projects/_sbl_r4/c3v2" \
  --prompt "Read the brief at C:/Projects/Agent_Workspace/SBL/_governance/round-20261021-r7/40_VERIFY/CHECKER_BRIEF.md and execute every check in it exactly as written. You are READ-ONLY on every product and evidence tree; use a throwaway copy under your own scratch for any mutation. Be efficient and finish within the time budget. Your final message MUST contain the nonce R7CHK-NC-20261021-A3 verbatim, the literal summary lines of every command you ran, and a VERDICT section. If you run out of time, say exactly which checks you completed and which you did not, and still emit the nonce and a VERDICT."
```

Notes that will save time:

* The **brief must not contain the token "publish"** — the dispatcher's remote-write detector
  rejects it. The phrase "the published `v0.1.0-foundation-preview` bytes" tripped it; it is now
  "the bytes of the existing `v0.1.0-foundation-preview` release". If you regenerate the brief
  with `make_checker_brief.py`, do not reintroduce that word.
* The nonce must appear **in the prompt text**, not only as a flag — a prompt that does not echo
  the nonce yields `ERR_NO_ARM_EMITTED_NONCE`.
* `--require-arm` is an **assertion, not a selector**. Arm selection is `--force-rank`. With GPT
  promoted to rank 1, `--force-rank 2` is no longer needed for VERIFY.
* The OpenAI transport requires the **bare** id `gpt-6.1-sol`. The qualified form
  `openai-codex/gpt-6.1-sol` returns HTTP 400 `Model is unavailable`.
* Expect **20–25 minutes**. A previous round ran 1395 s. It is not stuck unless the stdout file
  stops growing for more than 10 minutes.
* It writes to `HG-KSEOS/var/R7-LANES/verify_chk_r7_a3.json` and
  `.../verify_chk_r7_a3.json.logs/attempt-*-stdout.txt`.

After the verdict: seal it into `40_VERIFY/`, update `CHECKER_STATUS.json` round3, re-run the
self-check, and **only then** consider recording the HGK workorder result.

### 4.2 Re-run the self-check

```bash
cd C:/Projects/Agent_Workspace/SBL/_governance/round-20261021-r7
SCR="C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/cache/scratch"
export TMPDIR="$SCR" TEMP="$SCR" TMP="$SCR" PYTHONDONTWRITEBYTECODE=1
python 90_EVIDENCE/self_check_r7.py
```

Expected at resume: **15/16 → 16/16** once C6 is closed. C7 and C9 should already flip because
the branches are pushed and the receipt is regenerated — verify they did.

### 4.3 Then, in order

1. HGK workorder: record the checker result through the **typed API** (never raw SQL). If the
   checker does not pass, use `rollback_workorder` — an honest `ROLLED_BACK` beats a false PASS.
2. Commit + push the SBL evidence branch.
3. The four contract capability bindings → rebuild the compiler SSOT.
4. PR #2: R6 candidate `a6bcdd0` fast-forwards over `main` cleanly. Merging is a real remote
   write; confirm with the owner before performing it, and record a genuine merge receipt.
5. The remaining open items in §3, in FAR's order.

---

## 5. Notes, traps and lessons from this round

1. **The parallel writer is real.** During this round a concurrent Codex process twice wrote to
   the canonical pool: once injecting 6 merge-conflict markers into
   `lane-route-slots.candidate.json`, once committing `a1bd583`/`1cbb9d2` that changed EXECUTE to
   MiniMax and left `declared_by` claiming "unchanged" — self-contradictory. Both were caught by
   read-back, not by the write itself. **Every write to the canonical pool must be preceded by a
   pre-image digest guard and followed by a read-back.**
2. **A stash variant silently disagreed with the owner.** One concurrent variant changed EXECUTE
   to MiniMax too, contradicting the owner's "only PLAN and VERIFY/CHECKER". The owner was asked
   and confirmed EXECUTE stays on DeepSeek. Do not re-litigate; the answer is recorded in
   `OWNER_DECISIONS.md`.
3. **`_repo_head()` takes the CWD, not the project repo.** The first HGK admission returned an id
   but created no WorkOrder, because the API was called from the wrong working directory. An
   orphan DRAFT TaskSpec had to be removed and the admission redone through the typed API.
4. **A half-admission is worse than none.** The typed API is not re-entrant — `admit_requirement`
   on an existing requirement needs the missing TaskSpec/WorkOrder supplied, not a second call.
5. **The `import build` trap generalises.** Any `import X` probe for a build tool is unsafe in a
   repo that contains an `X/` directory. Probe with `python -m X --version`.
6. **Local-property tests hide global-property failures.** The mutation probe existed to catch
   exactly this and initially did not, because the mutation was applied to a tree that did not
   contain the new tests. A mutation probe must copy the **whole working tree**, not
   `git checkout --force HEAD`.
7. **Raw index-file hashes are not an invariant.** git rewrites the stat cache on read.
8. **`git commit -F -` hangs.** Write the message to a file and use `git commit -F <file>`.
9. **A `build/` directory in the repo breaks `import build`.** Also: the checker's venv had no
   `build` package, so the builder needs the `SBL_BUILD_PYTHON` fallback.
10. **The dispatcher rejects a prompt containing "publish".** Reword, do not disable the guard.
11. **A git remote write needs the `-c core.askPass=<wrapper.cmd>` form**; the `GIT_ASKPASS`
    environment variable alone is ignored by git on this host.

---

## 6. Stopped processes (for the record)

At the pause, verified by process inspection:

* lane dispatchers (`python … hgk-lane-dispatch`): **0**
* codex exec workers (excluding the app-server/exec-server pair): **0**
* hermes background kernel runners: idle
* the two surviving `codex.exe` (PIDs 8924, 14948) are the **resident app-server / exec-server**
  that the Codex CLI keeps alive; they are not checker runs and they exit with the machine.
