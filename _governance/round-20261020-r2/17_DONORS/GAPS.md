# GAPS — the honest delta

Author-side, local-only. Claim ceiling for everything in this directory:
**`CANDIDATE_ONLY` / `AUTHOR_SIDE_STATIC_READBACK`**. No independent checker has
seen it, and nothing here is a release statement.

---

## 1. The denominators: corpus implies, and what was confirmed

| Item | Corpus-implied | Confirmed | How confirmed |
|---|---|---|---|
| Method donors | 6 | **6** | `SBL_PIPD-LS-PKG_DOC-00.md:599-622` (R04.r3.base.1) — four slots each; `SBL_PIPD-LS-PKG_DOC-06.md:130-139` (C32.1) |
| Capability slots | 24 | **24** | same two tables; each slot appears once in each, all 24 distinct |
| §9D methods | 25 | **25** | `SBL_PIPD-LS-PKG_DOC-06.md:1131-1159` (C33.3), `METHOD-01..METHOD-25`, contiguous |
| Named technology keys | 386 | **386** | `SBL_PIPD-LS-PKG_DOC-00.md:652-1047` (R04.r3.2), 386 data rows, bucket sum = 386 |
| Bucket arithmetic | `24+19+31+17+17+78+40+160` | **386** | `SBL_PIPD-LS-PKG_DOC-01.md:1987` states the identity; my extraction reproduces it exactly |
| Total disposition rows | — | **441** | 6 + 24 + 25 + 386 |

**The corpus does state 386.** It is not an expected-but-absent number. It is stated
in at least six places and is internally consistent with the 8-bucket formula. Every
one of the 386 rows was extracted, and every cited locator was re-opened and
re-matched against the document line (851 citations across 441 rows,
`RUNS/run_05_verify.txt`, 0 failures).

What the corpus **also** says, and what changes the shape of the answer:

- `SBL_PIPD-LS-PKG_DOC-00.md:652` — "226 技術/協定/研究與 160 歷史規則不混為安裝數".
  Only 226 of the 386 are technology-shaped; **160 are governance rules**
  (`MUST` / `MUST NOT` / `SHOULD`), not installable software.
- `SBL_PIPD-LS-PKG_DOC-00.md:1437` — `CR-386UNIVERSE` is still **OPEN**:
  "386 technology rows claimed across 8 buckets | currently partially enumerated in
  current master excerpt | do not claim all 386 individually qualified".
  So the corpus itself disclaims full individual qualification even though the full
  roster now exists. A disposition table does not close that conflict.
- `SBL_PIPD-LS-PKG_DOC-00.md:1519` — the audit order requires "24 cap / 386 universe /
  25 methods / 38 surfaces 的 source 分母 honesty".

---

## 2. Shape of the 386 — the number that matters

| Bucket | Rows | What they actually are |
|---|---|---|
| `LEGACY160` | 160 | Rule ledger (`MUST`/`MUST NOT`/`SHOULD`). DOC-06 routes all 160 to slot value `N/A_RULE`. Not installable. |
| `P0_TOOL78` | 78 | Coding/quality/supply tools from the Group-07 register |
| `NTD40` | 40 | Named-technology donors: 33 `policy=DEFERRED_BY_EVIDENCE`, 6 `policy=DONOR_PATTERN_ONLY`, 1 `policy=REJECTED` |
| `PD06_31` | 31 | Product-line technologies (Mem0, Letta, Postgres, SQLite, …) |
| `NOBJ24` | 24 | The 24 protected capability objects, cross-referenced to the 24 slots |
| `OSS19` | 19 | Open-source research/method donors |
| `SUPPLY17` | 17 | Supply-chain tooling (Syft, Trivy, Cosign, SLSA, …) |
| `W3_TECH17` | 17 | Windows-3 host technologies |
| **Total** | **386** | **226 technologies + 160 rules** |

Independent cross-check from the corpus's own routing column: exactly 160 rows carry
`N/A_RULE` and exactly 226 carry a `SLOT-*` target (36 → `SLOT-MP-03`, 35 →
`SLOT-MP-01`, 32 → `SLOT-SP-01`, …). The 226/160 split is therefore not my
interpretation; it is the corpus's own routing.

---

## 3. Which of the 386 are genuinely addressed

| `current_execution_disposition` | Count | Meaning |
|---|---|---|
| `ACTIVE` | **1** | `NOBJ24/NOBJ-019` pytest — the runner this repo actually executes (81 tests passed on CPython 3.12.14) |
| `STANDBY` | **3** | `NOBJ-020` GitHub Actions (workflow file exists, no run receipt); `NOBJ-011` SKILL.md (artifact exists, no format validator); `NOBJ-013` Prompt projection (generated artifact, no test) |
| `PROHIBITED` | **8** | Original deny preserved: `NOBJ-017` (QUARANTINED), `OSS19/353-355` (REJECT), `P0_TOOL-039` LangGraph, `P0_TOOL-040` CrewAI, `P0_TOOL-050` Chroma, `NTD-033` (REJECTED) |
| `DEFERRED` | **374** | Confirmed in the corpus, zero contact with this repository |

**Genuinely addressed: 1 of 386 executed, 3 more present as artifacts, 8 correctly
prohibited, 374 untouched.**

That is the number. It is not 386, and it is not a defect in the table — it is the
state of the repository, which says so itself: `README.md:99` "No 386-donor
technology installation"; `contracts/SBL_C0_C9_CONTRACT.json:102-103` lists
"install all 386 donor technologies" under **`non_goals`**; and
`openspec/changes/sbl-v01-candidate-build/proposal.md:25` "No installation of all 386
named donor technologies; only admitted slots (DOC-06)".

### Evidence for the 374 zeros

`RUNS/run_02_grep.txt`: 435 identifiers (386 key ids + 25 method ids + 24 slot ids)
searched against `sbl_core/ sbl_sp/ sbl_cli/ tests/ tools/ docs/ contracts/ skills/
.github/ openspec/`. **11 identifiers produce any textual hit, and none of the 11 is
an implementation:**

| Hit | Why it is not implementation |
|---|---|
| `NOBJ-003` / `PD06-13` / `P0-TOOL-011` = "OpenSpec" | Matches the directory name `openspec/` (`tools/build_prompt_contract.py:397`, `contracts/SBL_C0_C9_CONTRACT.json:237`). No OpenSpec code, CLI or adapter. |
| `NOBJ-010` / `P0-TOOL-026` = "AGENTS.md" | External path constants `HG-KSEOS/AGENTS.md`, `Fabric/FABRIC/AGENTS.md` (`tools/build_prompt_contract.py:27,29`). The repo has no `AGENTS.md`. |
| `NOBJ-011` = "SKILL.md" | `README.md:87` describes the file; no parser. |
| `NOBJ-019` = "pytest" | **Genuine** — see `TRACE.md` §1. |
| `P0-TOOL-005` = "Codex" | Host name in bridge tests (`tests/test_gj03_bridge.py:51`), not the Codex product as an admitted technology. |
| `P0-TOOL-064` = "SBOM" | A task note that SBOM is *not* done (`openspec/.../tasks.md:49`). |
| `P0-TOOL-070` = "Kubernetes" | Negative-test search string (`tests/test_gknow.py:70`). |

---

## 4. Findings the round did not expect

1. **The gate ids `TS11` / `CHK09` do not exist in this corpus.**
   `grep -n "TS11\|CHK09\|CHK-09"` over DOC-00..DOC-13 returns nothing
   (`RUNS/run_00_raw_grep.txt` §5). They are also absent from
   `_governance/round-20261020-r2/00_ROUND_STATE.md`. The substantive requirement they
   appear to point at — an explicit, sourced disposition per technology slot — is
   real and is what this directory answers, cited to DOC-00 R04.r3 / DOC-01 R08.2A /
   DOC-06 C32-C33. **The closing of a gate item named TS11/CHK09 must be declared by
   the control plane that owns those ids, not by this table.**

2. **"Donor" is overloaded in the corpus.** Besides the six method donors, DOC-00
   `:1317-1333` defines **17 documentary source families**, eight of them literally
   named `*_DONOR` (`AI_AGENT_SPEC_DONOR`, `FABRIC_HGK_DONOR`,
   `GENIEMAKER_DESIGN_DONOR`, `GENIEMAKER_DOC_DONOR`, `OROCHI_DONOR`,
   `SDLC_HLPE_DONOR`, `SWOF_PD_DONOR`, `SWOF_PI_DONOR`). This table dispositions the
   **six technology donors** only. A reader who greps "donor" gets both populations,
   and they are not the same concept.

3. **The donor name is not stable across the two authoritative tables.** DOC-00
   `:607-610` writes the third donor as `Matt`; DOC-06 `:138` writes it as
   `Matt Pocock`. This table preserves the DOC-00 literal (`Matt`) so the slot rows
   key off the slot ledger, and records the alias in the donor row's locator. No
   merge was invented.

4. **The declared Python floor cannot run the end-to-end tests.** `pyproject.toml:9`
   says `requires-python = ">=3.11"` and `.github/workflows/ci.yml:21` pins the matrix
   to 3.11, but `tests/e2e/test_gj02_patch.py:64` and `tests/e2e/test_rollback.py:71`
   call `shutil.rmtree(..., onexc=...)`, a keyword that only exists from 3.12.
   Measured this round: **3.12.14 → 81 passed; 3.11.9 → 71 passed, 1 failed,
   9 errors** (`RUNS/run_03_pytest.txt`). Consequence: the CI workflow in this
   repository would be red on its own pinned interpreter. I did not fix it — `tests/`
   is outside this round's write root, and `tests/e2e/` is dirty in the working tree
   with another lane editing it, so this is a snapshot at the timestamp in
   `TRACE.md` §0, not a claim about the lane's final state.

5. **`NOBJ-024` "Ruff + type checker" is declared `WRAP_WITH_ADAPTER`, but the repo
   uses neither.** `pyproject.toml` has no ruff/mypy configuration and no lint gate
   runs in this round. Its `current_execution_disposition` is `DEFERRED`.

6. **One row is `UNCONFIRMED` — and it is the corpus's own admission, not my
   failure.** `METHOD-18` (Dependabot) carries `NO_SOURCE_EVIDENCE` in its source
   disposition. No row had to be marked `UNCONFIRMED` for "could not find it": all
   435 corpus identifiers were located at an exact file:line.

7. **Slot coverage is thin and lopsided.** Of 24 slots, 18 have no implementation.
   The six that do are the ones with a mechanical predicate (atomise, route, index,
   independence, bounded repair, bounded write). The six that do not — explore,
   domain model, phases, ship, brainstorm, test-first — are exactly the ones a
   1,206-line core+SP skeleton (`sbl_core/` + `sbl_sp/`) cannot fake. Note also that the corpus routes 36 keys to
   `SLOT-MP-03` (domain model) and 32 to `SLOT-SP-01` (brainstorm), both
   unimplemented, so the thinnest slots carry the heaviest routing load.

---

## 5. What this round must NOT claim

- **Not** "386 technologies dispositioned and qualified". 374 are `DEFERRED`, and
  `CR-386UNIVERSE` stays open.
- **Not** "all 386 installed / admitted". The contract lists that as a `non_goal`.
- **Not** "the six donors are integrated". Zero donor binaries, pins, licences or
  adapters exist.
- **Not** "24/24 slots implemented". 18 of 24 have nothing; the 6 that do are
  `NATIVE_SUBSTITUTED`, i.e. the donor was deliberately replaced, not adopted.
- **Not** "the 25 methods are routed". `MP-01` routes 5 requirement kinds, not 25
  methods; all 25 `METHOD-*` rows are `DEFERRED`.
- **Not** "gate TS11 / CHK09 closed". Those ids are not in the corpus; the control
  plane must name and close its own gate item.
- **Not** "CI green". The 3.11 matrix is red on `onexc=` (§4.4).
- **Not** any independent or external acceptance. Every hop in `TRACE.md` is a local
  test I ran; the maker is the author of this table.
- **Not** "160 rules are satisfied locally". Those 160 rows are `ACTIVE` at source
  (binding) and `DEFERRED` in execution (no local reader).

---

## 6. What would raise this from CANDIDATE

1. A control-plane-named gate item with an explicit acceptance predicate (the ids
   `TS11`/`CHK09` need an owner before anyone can close them).
2. An independent checker re-running `RUNS/run_05_verify.txt` and the 81-test suite
   on a clean interpreter.
3. A decision on `CR-386UNIVERSE`: either accept "roster complete, qualification
   per-item" or keep the conflict open — the table supports either, but does not
   decide it.
4. Pin/licence receipts for any donor the round actually wants to admit. None exist,
   so none is `ACTIVE`.
5. A fix for the `onexc=` floor mismatch, owned by whoever owns `tests/`.
