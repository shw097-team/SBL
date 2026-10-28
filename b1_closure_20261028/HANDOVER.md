# HANDOVER — B1 closure 2026-10-28 (SBL)

1. What was asked: verify/accept FHS-MSC B1 against PKG_00~08 and close the Native E2E loop.
2. What is proven: `evidence/GATES.json` → `G-A 6/6 PASS`, three GWOs PASS, `G-B PASS`,
   conjunction PASS, `mission_complete true`, `why_not_complete []`.
3. Native path, not sandbox: 245 `native_admission` events (1 first workorder + 244-case corpus),
   735 nonces, 245 leases — see `evidence/NATIVE_ADMISSION_RECEIPT.json` and
   `evidence/CORPUS_NATIVE_RECEIPT.json`.
4. Owner decisions are signed, not implied: `evidence/OWNER_DECLARATION.json` (claim ceiling) and
   `evidence/OWNER_RULING.json` (principal separation, SourceFreeze HOLD) both verify against the
   enrolled owner key.
5. What the 30-route denominator is: this registry's own row count. PKG_00~08 state no 30-route
   requirement; the only written rule (OpenSpec tasks.md L19) asks for `INSTALLED`, satisfied 30/30.
6. What is NOT claimed: `release: NOT_RUN`, no promotion, no third-party acceptance, upstream
   `formal_sourcefreeze: HOLD` unchanged.
7. How to re-measure: `python gates.py` in the B1 workspace; `git verify` the signed registry;
   re-run the declaration/ruling verification with `declaration_lib.verify`.
8. Known incident on record: the first re-sign pass signed cached shas (18 rows); fixed by rebuilding
   rows from disk before signing and a fail-closed `sha_not_on_disk` gate.
9. Cost of this round: see `evidence/SESSION_STATE.json` (unlocks, signatures, elevation).
10. Next owner action, if any: sign `PROMOTION_RECEIPT` before merging this branch to `main`.
