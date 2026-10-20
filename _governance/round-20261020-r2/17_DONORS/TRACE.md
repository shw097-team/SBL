# TRACE — requirement → implementation → test, per executed row

Scope: this file traces **every row whose `current_execution_disposition` is `ACTIVE`
or `NATIVE_SUBSTITUTED`** — i.e. every row that something in this repository actually
executes today. All other rows are listed at the end with an explicit "no
implementation" statement.

Table: `DISPOSITION_TABLE.json` (441 rows). Executed rows: **7** — 1 `ACTIVE`
(`NOBJ24/NOBJ-019` pytest) and 6 `NATIVE_SUBSTITUTED` slots (`SK-02`, `MP-01`,
`GS-01`, `GT-03`, `SP-03`, `SP-04`).

Every `file:line` below was read from the working tree in this round, not from
memory. Test hops were executed: **81 passed** under CPython 3.12.14
(`RUNS/run_03_pytest.txt`), 71 passed / 1 failed / 9 errors under CPython 3.11.9
(same file) — the 3.11 failures are a harness defect described in `GAPS.md` §5 and
do not touch any row traced here.

---

## 0. Tree binding (so later drift is detectable)

Read at `2026-10-20T07:05Z` (round-2 working tree, `git HEAD = ab17440ab68f8c7a1bd9702aba3624149d3f0506`).
`sha256` prefixes below are of the **working-tree files as read**, not of `HEAD` —
`sbl_core/m05_verify.py`, `sbl_sp/sp.py` and `tests/e2e/*` were already dirty
(uncommitted) when this table was built, and another lane is editing them. If a file's
digest no longer matches, re-read the line before trusting a `file:line` hop here.

| File | sha256[:16] | Bytes |
|---|---|---|
| `sbl_core/m01_intake.py` | `4657a529b74fd6cc` | 1229 |
| `sbl_core/m02_spec.py` | `40334929817546d5` | 1848 |
| `sbl_core/m03_routing.py` | `fdb62afadaf00fd2` | 1446 |
| `sbl_core/m04_bridge.py` | `bec88b2e51d6f65b` | 5567 |
| `sbl_core/m05_verify.py` | `217a0344950ba424` | 5760 |
| `sbl_core/m06_repair.py` | `51b1f0c16c6b11b3` | 1674 |
| `sbl_core/gknow.py` | `0ab60e3017338c26` | 6884 |
| `sbl_core/modes.py` | `6d10668946e09f98` | 2976 |
| `sbl_core/dto.py` | `791b23a010e7f8ff` | 3335 |
| `sbl_sp/sp.py` | `b6b0da17d1bf4527` | 5716 |
| `sbl_sp/bridge.py` | `96fe3a362906e434` | 3456 |
| `pyproject.toml` | `ef7270c794891fd9` | 455 |
| `.github/workflows/ci.yml` | `43922189d54739bf` | 1148 |
| `tests/test_core_modules.py` | `1fc18f375df7191f` | 10355 |
| `tests/test_sp_isolation.py` | `19c5d288a0720509` | 2992 |
| `tests/test_modes.py` | `329c87ba28ad9871` | 2782 |
| `tests/test_gknow.py` | `e015e0f16b4bc742` | 4529 |
| `tests/test_gj03_bridge.py` | `3390a27a1217bd17` | 2628 |
| `tests/e2e/test_gj02_patch.py` | `d00b4ee98127f024` | 4571 |
| `tests/e2e/test_rollback.py` | `3cfe6a956eaa313a` | 4602 |
| `README.md` | `d4ad760cfa4ff624` | 5269 |
| `docs/ARCHITECTURE.md` | `ea043994c34b157a` | 6534 |

Corpus side is frozen and independently addressable: every row in
`DISPOSITION_TABLE.json` cites `SBL_PIPD-LS-PKG_DOC-XX.md:NNN`, and all 851 such
citations were re-opened and re-matched by `RUNS/verify_table.py`
(441/441 rows, 0 failures, `RUNS/run_05_verify.txt`).

## 1. `NOBJ24/NOBJ-019` — pytest · `ACTIVE`

Corpus: `SBL_PIPD-LS-PKG_DOC-00.md:674` (R04.r3.2 row `NOBJ24/NOBJ-019`), original
disposition `ADOPT`; `SBL_PIPD-LS-PKG_DOC-06.md:319` (C33.2.NOBJ24). Slot route in
the corpus: `SLOT-SP-02`.

| Hop | Evidence |
|---|---|
| Requirement | A real test runner with a non-zero denominator: every gate is one command, one exit code, one denominator (audit order `SBL_PIPD-LS-PKG_DOC-00.md:1519`; gate discipline `docs/ARCHITECTURE.md:94-98`). |
| Implementation | `pyproject.toml:18-20` (`[tool.pytest.ini_options]`, `testpaths=["tests"]`, `addopts="-q -p no:cacheprovider"`); `pyproject.toml:7` declares `dependencies = []`, so pytest is a dev/test tool and not a runtime import. |
| Implementation (CI) | `.github/workflows/ci.yml:35` — `run: python -m pytest -q -p no:cacheprovider` on a 2-OS × py3.11 matrix (`.github/workflows/ci.yml:18-25`). |
| Test | `pytest` over `tests/`: `tests/test_core_modules.py` (25 tests), `tests/test_sp_isolation.py` (8), `tests/test_modes.py` (10), `tests/test_gknow.py` (6), `tests/test_gj03_bridge.py` (6), `tests/e2e/*` (10), plus fixtures in `tests/conftest.py`. |
| Run receipt | `81 passed in 6.86s` (CPython 3.12.14) — `RUNS/run_03_pytest.txt`. Also frozen in-repo at `evidence/gates/GATES_RAW.json` with per-gate denominators (G-CORE-MODULES 32, G-MODES-NOEFFECT 10, G-KNOW 6, …). |

Boundary: the corpus routes this key to `SLOT-SP-02` (true test-first). pytest is the
runner only — it does not enforce a RED-before-GREEN log. `SP-02` is therefore
`DEFERRED`, and this row must not be read as satisfying it.

---

## 2. `SK-02` — Specify / clarify into atomic acceptance atoms · `NATIVE_SUBSTITUTED`

Donor `Spec Kit` is **not** installed. The function is served by `SBLM02`.

| Hop | Evidence |
|---|---|
| Requirement | "Specify／Clarify／Atomic Acceptance — Source/REQ/ACC 非空；拒零分母 PI" (`SBL_PIPD-LS-PKG_DOC-00.md:604`, R04.r3.base.1 row `SK-02`); full contract row at `SBL_PIPD-LS-PKG_DOC-06.md:183` (C32.3, `SLOT-SK-02`). |
| Implementation | `sbl_core/m02_spec.py:14` `GuidedSpecification.derive(goal, clauses)`; `:38-43` raises `SBL_E_UNLOCATED_REQUIREMENT` when a clause has no locator; `:15-20` raises `SBL_E_BAD_STATE` on zero clauses; `:44-46` collapses duplicate text; `:47-49` emits `SpecAtom` with a content-addressed id (`sbl_core/dto.py:21-24`). |
| Test (positive) | `tests/test_core_modules.py:70` `test_spec_positive_order_and_idempotence` — asserts atom order `["first","second"]`, duplicate collapse, deterministic `atom_id`, and locator preservation. |
| Test (negative) | `tests/test_core_modules.py:85` `test_spec_negative_missing_locator` (asserts `SBL_E_UNLOCATED_REQUIREMENT`); `:93` `test_spec_negative_zero_clauses`. |

Delta from the corpus requirement: the corpus row asks for ACC (acceptance criteria)
to be non-empty. `SpecAtom` has no acceptance field (`sbl_core/dto.py:68-72`), so
"atomic acceptance" is only half present. Recorded, not papered over.

---

## 3. `MP-01` — Smart method routing · `NATIVE_SUBSTITUTED`

Donor `Matt Pocock` is **not** installed. The function is served by `SBLM03`.

| Hop | Evidence |
|---|---|
| Requirement | "Smart Method Routing — 不要求使用者選六工具；錯誤任務不誤啟 Skill" (`SBL_PIPD-LS-PKG_DOC-00.md:607`, row `MP-01`); contract row `SBL_PIPD-LS-PKG_DOC-06.md:186` (`SLOT-MP-01`). |
| Implementation | `sbl_core/m03_routing.py:10-16` `DEFAULT_POLICY` — 5 kinds, exactly one target each, `AGENT_OS` and `AI_SYSTEM` mapped to `None`; `:27-46` `route()` raises `SBL_E_UNKNOWN_KIND` (`:28-33`) and `SBL_E_PROHIBITED_KIND` (`:35-40`) instead of defaulting. |
| Test (positive) | `tests/test_core_modules.py:102` `test_routing_positive_default_policy` |
| Test (negative) | `tests/test_core_modules.py:114` `test_routing_negative_unknown_kind`; `:122` `test_routing_negative_prohibited_kind` (parametrised over `AGENT_OS`/`AI_SYSTEM`). |

Boundary: the policy is a static 5-entry table, not a method resolver over 25
methods. `METHOD-*` rows are all `DEFERRED`; this row must not be cited as routing
them.

---

## 4. `GS-01` — Context engineering · `NATIVE_SUBSTITUTED`

Donor `GSD` is **not** installed. The function is served by `sbl_core/gknow.py`.

| Hop | Evidence |
|---|---|
| Requirement | "Context Engineering — 來源定位與版本保留；拒記憶假資料" (`SBL_PIPD-LS-PKG_DOC-00.md:611`, row `GS-01`); contract row `SBL_PIPD-LS-PKG_DOC-06.md:190` (`SLOT-GS-01`). |
| Implementation | `sbl_core/gknow.py:59` `build_index(corpus_root, out_path)`; `:45-56` `_chunk()` emits `locator = "{path}#L{start}-{end}"` plus a per-chunk `sha256`; `:30-42` 40-line chunking; `:135` `query()` raises `SBL_E_KNOWLEDGE_NO_ANSWER` rather than synthesising. |
| Test (positive) | `tests/test_gknow.py:35` `test_build_index_positive`; `:52` `test_query_positive_returns_source_bound_hits`. |
| Test (negative) | `tests/test_gknow.py:66` `test_query_negative_no_answer`; `:74` `test_query_negative_upper_bound_is_enforced`; `:82` `test_build_index_negative_missing_corpus`; `:88` CLI exit codes. |

Boundary: the index is a JSON file over `.md`/`.json` (`sbl_core/gknow.py:18`), not a
version database and not SQLite/FTS5. `PD06-20`/`P0-TOOL-072` (SQLite) remain
`DEFERRED`.

---

## 5. `GT-03` — QA / code review that is independent and non-proxy · `NATIVE_SUBSTITUTED`

Donor `gstack` is **not** installed. The independence and anti-proxy predicates are
served by `sbl_sp/sp.py` + `sbl_core/m05_verify.py`.

| Hop | Evidence |
|---|---|
| Requirement | "QA／Code Review — Diff/Policy/E2E 鑑定；拒只靠 LLM 語意說 PASS" (`SBL_PIPD-LS-PKG_DOC-00.md:617`, row `GT-03`); contract row `SBL_PIPD-LS-PKG_DOC-06.md:196` (`SLOT-GT-03`). |
| Implementation (independence) | `sbl_sp/sp.py:67-78` `assert_permission()` refuses an action absent from `permissions` **or** listed in `forbidden`; `:81-99` `sign_verdict()` requires `challenge.sign` and raises `SBL_E_SELF_CHECK_FORBIDDEN` when `principal == maker` (`:85-90`). Manifests: `sbl_sp/manifests/external_challenge_sp.json` (only read-only, only signer), `commander_sp.json` (cannot sign). |
| Implementation (anti-proxy) | `sbl_core/m05_verify.py:17` `PROXY_STATUSES = {FILE_EXISTS, SYMBOL_EXISTS, SUMMARY_ONLY, DOCUMENTED}`; `:67-72` refuses any of them as verdict backing; `:61-66` duplicates the maker≠checker refusal; `:81-86` refuses a claim above the ceiling. |
| Test (independence) | `tests/test_sp_isolation.py:48` `test_commander_cannot_sign_challenge`; `:58` `test_maker_cannot_sign_own_verdict`; `:64` `test_distinct_principal_signs_verdict`; `tests/test_core_modules.py:226` `test_verify_negative_self_check`. |
| Test (anti-proxy) | `tests/test_core_modules.py:243` `test_verify_negative_proxy_status` (parametrised over all four proxy statuses); `:232` `test_verify_negative_claim_ceiling`; `:220` zero-denominator refusal. |

Boundary: this is **separation-of-principal and anti-proxy enforcement**, not a
diff/E2E analysis engine. There is no code reviewer, no diff parser and no E2E
runner in the tree. `GT-01`, `GT-02`, `GT-04` are `DEFERRED`.

---

## 6. `SP-03` — Root cause / smallest repair · `NATIVE_SUBSTITUTED`

Donor `Superpowers` is **not** installed. The function is served by `SBLM06`.

| Hop | Evidence |
|---|---|
| Requirement | "Root Cause／Smallest Repair — 第一失敗 invariant、變更錐、回歸；拒全域掃射" (`SBL_PIPD-LS-PKG_DOC-00.md:621`, row `SP-03`); contract row `SBL_PIPD-LS-PKG_DOC-06.md:200` (`SLOT-SP-03`). |
| Implementation | `sbl_core/m06_repair.py:20-49` `plan(first_fail, evidence_refs, attempts, max_attempts)`; `:27-38` raises `SBL_E_REPAIR_WITHOUT_EVIDENCE` when no non-blank evidence ref exists; `:39` binds `rollback_pointer` to the first evidence ref; `:40` derives scope; `:41-48` returns `STOP_ESCALATE` at the cap instead of looping. |
| Test (positive) | `tests/test_core_modules.py:252` `test_repair_positive_narrow_plan`; `:261` `test_repair_positive_escalates_at_cap`. |
| Test (negative) | `tests/test_core_modules.py:266` `test_repair_negative_without_evidence`. |

Boundary: "變更錐" (repair cone) is not computed — `scope` is the literal string
`"NARROW"` (`sbl_core/m06_repair.py:40`). The first-failure invariant, the evidence
requirement, the rollback pointer and the attempt cap are real; the cone geometry is
not.

---

## 7. `SP-04` — Plan execution / review with a bounded work order · `NATIVE_SUBSTITUTED`

Donor `Superpowers` is **not** installed. The function is served by `SBLM04` + the
SP layer.

| Hop | Evidence |
|---|---|
| Requirement | "Plan Execution／Review — 有界 WorkOrder、獨立 Review；拒 Maker 自簽" (`SBL_PIPD-LS-PKG_DOC-00.md:622`, row `SP-04`); contract row `SBL_PIPD-LS-PKG_DOC-06.md:201` (`SLOT-SP-04`). |
| Implementation (bounded order) | `sbl_core/m04_bridge.py:87-99` `prepare()` binds `order_id` to `HEAD` + sorted writeset (`sbl_core/dto.py:27-37`); `:101-160` `apply()` refuses an absolute path (`:109-114`), traversal (`:125-130`), a path outside the writeset (`:134-139`) and a moved HEAD (`:140-146`, `SBL_E_STALE_HEAD`). |
| Implementation (independent review) | `sbl_sp/sp.py:81-99` (signing principal ≠ maker); `sbl_sp/manifests/commander_sp.json` forbids `challenge.sign` and `verdict.sign`. |
| Test (bounded order) | `tests/test_core_modules.py:159` `test_bridge_prepare_positive_and_empty_negative`; `:171` `test_bridge_apply_positive_writes_under_writeset`; `:187` `test_bridge_apply_negative_outside_writeset` (5 escape shapes); `:195` `test_bridge_apply_negative_stale_head`; `tests/e2e/test_rollback.py` exercises rollback end-to-end but is RED under 3.11 (see `GAPS.md` §5). |
| Test (independent review) | `tests/test_sp_isolation.py:48`, `:58`, `:64`. |

Boundary: there is no WorkOrder *review* step — the order is issued, applied and
recorded; the independent principal signs a verdict over evidence, not over a
work order. Half the slot predicate is met, half is not, and the row says so.

---

## 8. Rows with no implementation — explicit statement

The following are `DEFERRED` or `STANDBY` in `current_execution_disposition` and
have **no implementation in this repository**. For each, the disposition row in
`DISPOSITION_TABLE.json` carries the corpus locator and the reason.

| Group | Count | Statement |
|---|---|---|
| Donors | 6 | No donor (OpenSpec, Spec Kit, Matt Pocock, GSD, gstack, Superpowers) is installed. No binary, CLI, pin, licence receipt or adapter exists. `README.md:99`. |
| Slots | 18 | `OS-01..04`, `SK-01`, `SK-03`, `SK-04`, `MP-02..04`, `GS-02..04`, `GT-01`, `GT-02`, `GT-04`, `SP-01`, `SP-02` — no module implements the slot predicate. Three (`OS-03`, `MP-02`, `GS-03`) and three more (`OS-02`, `MP-04`, `GS-04`) have an adjacent primitive but not the predicate; each row names the primitive it lacks. |
| §9D methods | 25 | No method adapter, no method skill, no pin. `METHOD-18` is `UNCONFIRMED` at source (`NO_SOURCE_EVIDENCE`). |
| Named keys | 382 | 374 `DEFERRED` + 8 `PROHIBITED`. No key id (`NOBJ-001`, `TECH-01`, `SUPPLY-01`, …) appears anywhere in the tree; `RUNS/run_02_grep.txt` shows 0 hits for 433 of 435 identifiers. The 11 name-level hits that do exist are incidental (see `GAPS.md` §4). |

There is no partially-true "implemented but untested" row in this file. A row is
traced above only if a named test in `tests/` executes the code path.
