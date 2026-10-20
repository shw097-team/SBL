# Tasks — sbl-v01-candidate-build

Status vocabulary: `[x]` = done with a raw receipt in this round · `[~]` = partially done (scope stated) ·
`[ ]` = not done (blocker or pending named). A bare `[ ]` with no note is a defect.

Round R2 note: the original text named helper scripts (`tools/source_ledger.py`,
`tools/knowledge_probe.py`, `tests/test_core_registry.py`, `test_spec_flow.py`, ...) that were never built; the
commands below are the ones that actually exist and ran. The rename is disclosed, not back-filled silently.

## 1. Source freeze and knowledge base

- [x] 1.1 Byte-level source freeze over 306 corpus files with the two >MAX_PATH originals mirrored short.
      Verify: `python tools/verify_source.py --verify` → `{"ok": true, "docs": 14, "mismatches": []}` (exit 0).
- [~] 1.2 G-KNOW retrieval: the index/query surface exists and refuses unanswerable queries
      (`python -m pytest tests/test_gknow.py -q` → 6 passed). NOT done: an index built over the real
      DOC-00..DOC-13 corpus as a published artefact — the positive/negative probes run on fixture corpora.
- [x] 1.3 C0..C9 contract compiled by the canonical compiler: `lint`/`activation`/`acceptance`/`compile`
      all exit 0 (`PROMPT_COMPILE_PASS`); receipt `contracts/compiled/compiler-receipt.json`.

## 2. Shared Core and modules

- [x] 2.1 `sbl_core` package with typed DTOs, one error model and the six modules wired through `SharedCore`.
      Verify: `python -m pytest tests/test_core_modules.py -q` → 32 passed.
- [x] 2.2 `SBLM01` goal intake + `SBLM02` guided specification (unlocated clause refused). Covered inside 2.1's suite.
- [x] 2.3 `SBLM03` governed routing + `SBLM04` bridge with a bounded write-set and stale-HEAD refusal.
      Covered inside 2.1's suite and `tests/e2e/test_gj02_patch.py`.
- [x] 2.4 `SBLM05` evidence verification + `SBLM06` bounded repair. Covered inside 2.1's suite.

## 3. SP separation and modes

- [x] 3.1 Three SP manifests with permission sets; the challenge SP cannot mutate product state and a maker
      cannot sign its own challenge. Verify: `python -m pytest tests/test_sp_isolation.py -q` → 8 passed.
- [x] 3.2 Mode gate: `PREW3_SHADOW` is `NO_EFFECT` for every effect; `SWOF_CONNECTED` refuses without a native ACK.
      Verify: `python -m pytest tests/test_modes.py -q` → 10 passed (39-gate matrix asserted).

## 4. Golden journeys

- [x] 4.1 `GJ01` `sbl-todo`: init/add/list/restart/uninstall with typed refusals.
      Verify: `python -m pytest tests/e2e/test_gj01_cli.py -q` → 7 passed.
- [x] 4.2 `GJ02` brownfield scoped patch: bind → red → green → out-of-writeset refusal → stale-HEAD refusal →
      rollback to the baseline digest. Verify: `python -m pytest tests/e2e/test_gj02_patch.py -q` → 7 passed.
- [x] 4.3 `GJ03` skill host bridge: discover → effective load → trigger/non-trigger → provider-off refusal →
      unload with no residue. Verify: `python -m pytest tests/test_gj03_bridge.py -q` → 7 passed.

## 5. Evidence, publication and independent acceptance

- [x] 5.1 Evidence pack: per-gate raw receipts (`evidence/gates/GATES_RAW.json`), scrubbed secret scan
      (`evidence/security/SECRET_SCAN.json`, verdict CLEAN), manifest (`evidence/EVIDENCE_MANIFEST.json`).
      NOT done: SBOM and licence — the licence is an open owner decision (`TX-LICENSE-OWNER-RULING`).
- [x] 5.2 Public repo `shw097-team/SBL` exists (`private: false`), candidate branch and evidence commit pushed,
      exact remote SHAs read back in `_governance/round-20261020-r2/30_PUBLICATION_READBACK.json`.
- [ ] 5.3 VERIFY/SECURITY lane (`openai-codex/gpt-6.1-sol`, read-only) against the frozen candidate with
      `required_arm == served_arm` and a raw verdict: dispatched after the candidate SHA was frozen; the verdict
      and its admissibility are recorded in the round evidence MD. Until an independent checker's raw receipt
      exists, the claim stays `LOCAL`, never `INDEPENDENT_CASE_PASS`.

## 6. Closure

- [ ] 6.1 Single evidence MD (claim ceiling / binding / gates / nonclaims / STOP) frozen last —
      `_governance/round-20261020-r2/40_EVIDENCE.md`; it is written after the last lane exits.
- [x] 6.2 TT/CR register updated (`_governance/round-20261020-r2/00_ROUND_STATE.md` §5) and a resume checkpoint
      written (`_governance/round-20261020-r2/20_RESUME_CHECKPOINT.json`).
