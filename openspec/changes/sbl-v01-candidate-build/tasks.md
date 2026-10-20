# Tasks — sbl-v01-candidate-build

## 1. Source freeze and knowledge base

- [ ] 1.1 Build byte-level SOURCE_LEDGER over 306 corpus files (path, bytes, sha256) and record the mirror
      mapping for the two >MAX_PATH originals. Verify: `python tools/source_ledger.py --verify`.
- [ ] 1.2 Emit the AI knowledge index (routing table over DOC-00..DOC-13 + KP 00..19 + GENIEMAKER DOC00-19)
      with anchors; negative retrieval probe must refuse out-of-corpus questions.
      Verify: `python tools/knowledge_probe.py --pos --neg`.
- [ ] 1.3 Compile the C0..C9 contract with the canonical `prompt_contract_compiler.py`
      (`lint` → `activation` → `acceptance` → `compile`) and store exit codes + redacted logs + report SHAs.

## 2. Shared Core and modules

- [ ] 2.1 Land `sbl_core` package with typed DTOs, an event log and the six module stubs wired through one registry.
      Verify: `pytest tests/test_core_registry.py -q`.
- [ ] 2.2 Implement `SBLM01` goal intake + `SBLM02` guided specification with schema validation.
      Verify: `pytest tests/test_spec_flow.py -q`.
- [ ] 2.3 Implement `SBLM03` governed routing and `SBLM04` build bridge with a bounded write-set record.
      Verify: `pytest tests/test_routing_and_bridge.py -q`.
- [ ] 2.4 Implement `SBLM05` evidence verification (manifest + digest) and `SBLM06` bounded repair loop.
      Verify: `pytest tests/test_evidence_and_repair.py -q`.

## 3. SP separation and modes

- [ ] 3.1 Three SP manifests with permission sets; negative test: challenge SP cannot mutate product state.
- [ ] 3.2 Mode gate: `PREW3_SHADOW` returns `NO_EFFECT` for every effect stage; `SWOF_CONNECTED` refuses
      without a native ACK/Permit. Verify: `pytest tests/test_modes.py -q`.

## 4. Golden journeys

- [ ] 4.1 `GJ01` `sbl-todo` CLI: install/add/list/restart/uninstall. Verify: `pytest tests/e2e/test_gj01_cli.py -q`.
- [ ] 4.2 `GJ02` brownfield scoped patch on a temp repo: diff → red → green → affected regression → rollback hash.
- [ ] 4.3 `GJ03` skill/minimal-agent host bridge: discover → effective load → trigger/non-trigger → provider-off refusal.

## 5. Evidence, publication and independent acceptance

- [ ] 5.1 Evidence pack: manifest, per-test raw logs, SEC/secret scan, SBOM/license, rollback pointer.
- [ ] 5.2 Create public repo `shw097-team/SBL` under OPS ECP; push a candidate branch + scrubbed evidence
      commit; read back exact SHAs (never print the token).
- [ ] 5.3 Dispatch the VERIFY/SECURITY lane (`openai-codex/gpt-6.1-sol`, read-only) against the frozen
      candidate; record `required_arm == served_arm` and the raw verdict; repair loop on CONFIRMED_DEFECT.

## 6. Closure

- [ ] 6.1 Single evidence MD (claim ceiling / binding / gates / nonclaims / STOP) frozen last,
      byte-identical to the review mirror.
- [ ] 6.2 TT/CR register updated; resume checkpoint written; no `[ ]` left unlabelled in the task list.
