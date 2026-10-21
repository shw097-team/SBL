# FAR R9 — Ruling on residuals, installation, SP integration, and the DOC-00..13 contract

Round: `SBL-R9-CTRLPKG-CLOSURE` · HGK requirement `REQ-HGK-PRJ-SBL-PIPDLS-R9-CTRLPKG` (FROZEN)
Governing contract: `SBL_PIPD-LS-PKG_DOC-00..13`, 14 documents, **17,473,442 bytes**, 75,630 lines
Research: 4 independent read-only workers, served by `gpt-6.1-sol` (openai-codex), 306–581 s each
Claim ceiling of this document: `CANDIDATE_ONLY` — a ruling and an execution record, **not an acceptance**

---

## 0. The single most important finding

Four independent workers, working four different questions, converged on one property of this programme:

> **Every gate we have certified PRESENCE. None of them certified CORRESPONDENCE.**

| gate | what it actually checks | what it was read as |
|---|---|---|
| drift gate (R8-D1) | each pin matches the file it points at | the governed surfaces agree |
| registry epoch (R8-D2) | the pin matches the assignment | the registry and assignment agree |
| compiler lint/compile (R9-03) | ids and locators are present and legal | the acceptance belongs to the capability |
| lane probe (INT-01) | a model served the request | the SP was invoked and handed off |
| `selftest 9/9` (INSTALL-02) | M01/M02/M03 local journey | the governed native chain works |
| `ROOT_READY 6/6` (INSTALL-03) | paths exist, package imports | native admission / Permit issuance |
| `14 components` (INSTALL-02) | 14 hashes are present | 14 independently qualified capabilities |
| `208 passed` | tests pass | the contract is satisfied |

This is the round's actual product. Every one of those gates is honest about what it measures and dishonest when read as something else. The defects this programme keeps finding — a 4-way mis-binding that compiled clean, an epoch bumped on one side only, a fallback list that dropped the demoted primary — are all the same defect: **a green signal for a property adjacent to the one that mattered.**

The corrective rule, adopted into the standing method:

> **A gate may only be cited for the property it directly measures. Any claim of correspondence needs a check that compares the two things to each other, not each one to its own pin.**

---

## 1. The denominator, stated honestly

Worker D scanned all 14 documents programmatically and independently reproduced the extraction with a second reader.

| quantity | value | what it is |
|---|---|---|
| document-qualified requirement records | **4,738** | entries in identified registers |
| distinct literal requirement identifiers | **4,589** | union, deduplicated |
| linked explicit `ACC-` identifiers | **1,341** | named acceptance ids |
| total physical size | **17,473,442 B / 75,630 lines** | all 14 files |

**This is a selected-register inventory, not the semantic contract denominator.** The control package says so itself:

- `DOC-02` L128 — `D_clause_semantic = UNRESOLVED`
- `DOC-04` L99 — `semantic_source_clauses_total = NOT_ESTABLISHED`
- `DOC-12` L7829 — global requirement denominator `= UNKNOWN`

**Therefore no completion percentage is claimable.** Not "62% done", not "mostly complete". The denominator that a percentage would divide by has not been established by the document that defines the work. Any number offered here would be an artefact of our own counting choice, presented as if it were the contract's.

---

## 2. Ruling on the four target areas

### 2.1 Residual / gap / blocker / unclosed items — `RUNNING, PARTIALLY CLOSED`

Worker A found 8 items with falsifiable close conditions and ranked them. I adopted the ranking **with one correction**: it ranked repo hygiene (RES-08) first and the contract mis-binding (RES-03) second. I executed RES-03 first, because it was the only item with **zero external dependency and a deterministic close condition** — no owner review, no host access, no issuer. Ranking by "lowest friction" should weigh *whether the round can actually finish it*, not only how small it is.

| item | severity | this round | why |
|---|---|---|---|
| RES-03 four capability bindings | high | **CLOSED** | `4 → 0` mismatches, compiler green, regression test with proven teeth |
| RES-08 three untracked HG-KSEOS tests | medium | **OWNER_DECISION_REQUIRED** | staging ~800 lines of another party's uncommitted test code would misattribute authorship; Worker A agrees: obtain the owner's review, do not blind-add |
| RES-07 `_repo_head()` uses CWD, swallows `InvariantViolation` | high | **NOT DONE** | see §4 |
| RES-02 formal Hermes plane binding | high | **PARTIAL** | a truthful binding record is producible; a *permit* is not, and must not be impersonated |
| RES-01 independent acceptance | blocker | **OPEN** | needs an authorised checker environment with writable scratch; see §5 |
| RES-04 host installation | high | **OPEN** | `host_install_state=NOT_INSTALLED`; no host admission held |
| RES-05 full DOC-00..13 | blocker | **OPEN** | see §1 — denominator itself unresolved |
| RES-06 bounded-writer provenance | high | **OPEN, irreversible** | historical authorship cannot be manufactured after the event |

### 2.2 Installation into HERMES / FABRIC / HGK / CODEX / CODEX CLI — `MEASURED, CEILING EXPLICIT`

Worker B's key contribution is refusing to let one word cover five achievements. Its five-way split is adopted verbatim:

| achievement | on this machine | evidence |
|---|---|---|
| (a) Python package installation | **ACHIEVED** | `sbl-v01 0.1.1rc1` in the canonical Hermes venv, 141 dists, zero runtime deps, 3 console entry points, independently re-verified |
| (b) standalone stack bootstrap | **ACHIEVED** | 14 components, 3 principals, doctor clean, `selftest 9/9` incl. two refusals, manifest digest `9d458910…` matches |
| (c) HGK adapter files installed | **ACHIEVED** | 3 digest-pinned files, `ROOT_READY 6/6`, ABI `hgk-harness-abi/1` |
| (d) effective Host installation | **NOT ACHIEVED** | `host_install_state=NOT_INSTALLED`; the ten-step HostInstall FSM has not been walked on any host |
| (e) native integration (WorkOrder/ECP/Permit) | **NOT ACHIEVED** | the ABI *itself* declares `native_effect`, `permit_signing`, `workorder_admission` as `not_provided` |

Worker B also corrected a factual error I had propagated in its brief: **`C:/Projects/Agent_Workspace/SBL/src` does not exist on this machine.** The real pinned sources are under `_sbl_release_011rc1/`, and their four Python files match the installed wheel byte-for-byte. Future evidence must cite the resolvable locator. Recording my own error here rather than letting the brief silently outlive the correction.

- **FABRIC**: `NO_SBL_INSTALL_TARGET`. Ruling: **do not manufacture a target.** Fabric is a native observer/assurance seam under DOC-11; the correct action is an owner applicability disposition, not a package installation.
- **CODEX / CODEX CLI**: neither has SBL-specific effective-load qualification. Serving a lane is not the same as the three SP packages being discovered, loaded and cleanly uninstalled. Per DOC-10, brand name does not transfer qualification between distributions.

### 2.3 PLAN↔Commander-SP and VERIFY↔Challenge-SP integration — `NOT INTEGRATED, DESIGN SET`

Worker C's finding is blunt and correct: **the dispatcher binds models, not SPs.** No inspected path in the dispatcher, in `hg_kseos`, or in `sbl_core` invokes `commander_sp`, `external_challenge_sp`, or `sign_verdict`. A principal name in a manifest, an installed Skill body, and a permission checker are three declarations — none of them is an invocation.

Minimum honest integration (adopted as the design, **not implemented this round**): two thin typed adapters at the seams that already exist — the PLAN handoff and the VERIFY pre-spawn — plus mandatory checks at the existing admission and acceptance boundaries. No new service, no second registry, no fourth SP. `PREW3_SHADOW` must return `NOT_DISPATCHED`.

Also recorded because it must not be quietly dropped: **PLAN and VERIFY both serve `gpt-6.1-sol`.** That is an owner-selected route and is not overridden here, but it means there is **no model diversity reviewing planning artefacts**. Model-level SoD is also not principal-level SoD — separate role names, separate homes and separate model ids do not prove separate authenticated identities (DOC-07 / DOC-08 C42). Disclosed, not fixed.

### 2.4 Full DOC-00..13 execution → landing → delivery — `CANNOT BE CLOSED, PLAN SET`

Adopting Worker D's 6-phase plan with its 10-engineer-day stop-loss. The plan's first phase is the one that is genuinely missing and genuinely cheap: **freeze the contract's identity and make it discoverable from inside the repository.** That is what §3 executed.

The stop-loss conditions are adopted as written: stop and deliver `PARTIAL` with exact carry-forward items if the semantic denominator remains unratified, if source/issuer/Host access is absent, if checker scratch execution is refused, or if an acceptance requirement would need a new product surface. **Do not add rounds to chase a green aggregate.**

---

## 3. What this round actually executed

### 3.1 R9-03 — four capability bindings gave way to their own acceptance `CLOSED`

- Defect: `SP_PLUGIN_PACKAGE_TPM`, `SP_PLUGIN_PACKAGE_COMMANDER`, `SP_PLUGIN_PACKAGE_CHALLENGE`, `SP_HOST_INSTALL_REQUEST` were each satisfied by `ACC-SBL_SHARED_CORE`, whose `subject_id` is `SBL_SHARED_CORE`. The other 17 readiness rows are self-consistent, so this was a mis-binding, not a design.
- No new acceptance edge was needed — all four `ACC-*` ids already existed (34 edges unchanged). Only the `/runtime_readiness` pointers were wrong.
- Locators were **not invented**: each capability's own `source_locators` from `/execution_scope` were reused, and every anchor was confirmed to resolve to a real heading or table row (`DOC-04#C15`, `DOC-12#C-001/002/003`, `DOC-12#C-016/017/018`).
- Result: **mismatches 4 → 0**; compiler `lint / activation / acceptance / compile` all `PROMPT_COMPILE_PASS`, 0 errors; contract sha256 `dd200277…` matches the receipt.
- `tests/test_contract_binding.py` was **shown failing on the previous state before it was made to pass** (2 failed against the prior contract). It reads the current contract by highest R-number, not a hard-coded filename, so it survives R10.
- Suite: `208 passed / 2 skipped` → `210 passed / 2 skipped`, rc=0.

### 3.2 R9-07 — the contract is now pinned inside the repository it governs `CLOSED`

- `contracts/CONTROL_PACKAGE_MANIFEST.json` records all 14 documents: size, sha256, DOC id, and a rollup digest `01b972c8…`.
- `tools/check_control_package.py --verify` fails closed. Three negative controls produce **three distinct, specific errors**: wrong size → `ERR_SIZE_DRIFT`; **same-length 1-byte tamper → `ERR_SHA256_DRIFT`**; absent document → `ERR_DOC_ABSENT`. A missing contract is a failure, never a skip.
- `tests/test_control_package_manifest.py` (6 tests, unittest, no pytest import) builds a synthetic 14-doc package so it runs anywhere, cannot pass vacuously when the real package is absent, and asserts the **sha256** path specifically — so a size-only check cannot make it green for the wrong reason.
- The 17 MB is deliberately **not vendored**: a duplicate becomes a second authority that drifts from the first, which is precisely the class of defect this programme keeps finding.

### 3.3 R9-01 — HGK admission `DONE`

`REQ-HGK-PRJ-SBL-PIPDLS-R9-CTRLPKG`: `CANDIDATE → FROZEN` (v1) → TaskSpec `ADMITTED` → WorkOrder `CREATED` (base_head `fa1ac06`), through the typed API under a lease, never raw SQL. Acceptance remains **`NOT_RUN`** and no result was pre-recorded.

---

## 4. What was deliberately not executed, and why

| item | reason |
|---|---|
| **R9-06** `_repo_head()` fix | Real defect, and the fix is small. Not executed because HG-KSEOS currently carries 16 pre-existing test failures and concurrent writers; changing `lifecycle.py` against that baseline risks attributing someone else's breakage to this change — or hiding this change inside theirs. It needs its own focused round with a clean baseline, not a tail-end patch. Named, not silently dropped. |
| **R9-05** untracked test files | Staging another party's ~800 uncommitted test lines under this commit misattributes authorship. `OWNER_DECISION_REQUIRED`. The consequence stays visible: **a clean checkout cannot reproduce `580/16`** until they are tracked. |
| **R9-02** independent checker | Needs an authorised writable scratch root. R7's checker returned `INCONCLUSIVE — NOT ACCEPTED` because its sandbox forbade even scratch writes. Running it again without that authority would produce a second `INCONCLUSIVE` and prove nothing. |
| **R9-04** plane *permit* | A truthful binding record is producible; a permit is not. An agent-authored description must never be dressed as an issuer grant. |
| **SP integration (§2.3)** | Design set; implementation is two adapters and a set of boundary checks that must land under their own admitted change. |

---

## 5. The pre-authorisation boundary

The owner pre-authorised executing the FAR ruling. That pre-authorisation covers the work in §3 — contract correction, contract pinning, admission, candidate branch, evidence. It does **not** manufacture what only an authority can issue:

- an HGK **Permit** or native WorkOrder issuance
- a **Host** admission or host-issued ID
- a **signed `PASS_CHALLENGE`**
- an **acceptance verdict** on the R7/R9 subject
- an owner **disposition** of the historical writer-provenance deviation
- approval to **track** another party's test files

These remain open. Naming them is the deliverable, not an obstacle to it.

---

## 6. Claim ceiling

`CANDIDATE_ONLY`.

- **Not** an acceptance. R7's independent verdict remains `INCONCLUSIVE — NOT ACCEPTED`, honestly mapped to HGK `FAIL`.
- **Not** native integration. The ABI declares `native_effect`, `permit_signing`, `workorder_admission` as `not_provided`.
- **Not** host installation. `host_install_state=NOT_INSTALLED`.
- **Not** a full-contract closure, and **not** a completion percentage — the denominator is `UNKNOWN` by the control package's own declaration.
- **Is** two verified corrections: a 4-way mis-binding to zero, and the contract pinned inside the repository with three proven failure modes.

The lanes are **available and serving**. Availability is not acceptance. A green gate is not a closed item.
