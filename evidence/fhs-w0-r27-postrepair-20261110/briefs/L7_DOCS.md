# L7 — r27 append-only candidate + seven-blueprint affected-scope delta (EC-R26-010, EC-R26-012, R26-10, E12)

Read `_COMMON.md` first. Worktree: `C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-docs` (branch r27/doc-r27, cut from `origin/main`).

You are writing documents, not code. The governing rule is: **never rewrite a governed byte; append, and mark the old text superseded in place.**

## Deliverable 1 — `evidence/fhs-w0-r27-repair-20261110/doc/FHS_PIPD-LS-PKG_W0_r27.md`
Construction must be mechanical:
1. Copy `evidence/fhs-w0-r26-repair-20261109/doc/FHS_PIPD-LS-PKG_W0_r26.md` byte-for-byte as the prefix.
2. Append a new top-level chapter `## CH27 — r27 append-only correction (2026-11-10)` that contains, each as its own numbered subsection with the finding id in the heading:
   - **CH27.1 (EC-R26-010)** — supersede the stale HGK branch SHA. r26 CH26.5 names `52c9c21...`; the integrated head is `86f40ec114f19bbd35314e376da4d0bed9805b22` and its predecessor `52c9c21` is retained as history. State: what the old text said, why it was wrong (a later commit moved the head), the new value, and that the old line is `superseded`.
   - **CH27.2 (EC-R26-004)** — L1 metadata truth: `bytes = 6224679`, `lines = 28005` (LF split), and the 31-source inventory total `111331` lines belongs in `source_inventory.total_lines`, not in `l1.bytes`. Cite the measurement command and the source file sha256.
   - **CH27.3 (EC-R26-011)** — `unaffected_proof` denominator: 4 unaffected WPs = 12+4+2+1 = 19 clauses = 76 preservation properties, not `32-4=28`. Show the per-WP arithmetic.
   - **CH27.4 (EC-R26-009)** — `EVIDENCE_SCOPE.profiles.full.excluded = {}`; the six gates move to `not_runnable_in_CI`. Explain that "excluded from the full profile" and "cannot run in CI" are different facts and conflating them produced a self-contradicting metadata file.
   - **CH27.5 (EC-R26-002 / EC-R26-003)** — record the repaired verifier and binding contract by reference: the new refusal codes (`VOTE_TYPE_INVALID`, `MISSING_CANDIDATE_BINDING`, `RAW_DIGEST_MISMATCH`, `PROCESS_ID_DUPLICATE`, `POOL_DIGEST_DRIFT`, `RETIRED_ARM`, `BINDING_EXPIRED`, `BINDING_TAMPERED`, `HOLD_REGISTRY_POOL_DRIFT`, `FHS_ENTRY_*`) and where the code lives. Quote the code names verbatim.
   - **CH27.6 (EC-R26-005 / EC-R26-006)** — HGK ancestry: DISJOINT roots (`a2389c13...` vs `ec58a0be...`), `merge-base` exit 1, left-right `90 / 328`; the `327 commits / main_is_ancestor=true` claim is retracted as an unverified author-side number; the adopted strategy is a main-derived bridge PR, not a merge.
   - **CH27.7 (EC-R26-012)** — the governance split. This is the most delicate paragraph in the document; write it exactly like this in substance: `model_diversity_optional = true` (no lane may be refused because it shares a model or provider with another lane; `same_arm_lanes` is recorded, never a failure) **and separately** `protected_identity_permissions = UNCHANGED`: Maker ≠ Issuer/Checker/Publisher on the **credential** axis; a Writer may not self-sign a protected pass; one general-purpose token may not become a Publisher key. Model freedom and credential separation are different axes and the first does not weaken the second. Any proposal to remove credential separation is a separate governance amendment with its own risk, effect-by-effect.
   - **CH27.8 (E12 / claim ceiling)** — an explicit `claim_ceiling` block: what this document does NOT license (no FULL_W0_CLOSEOUT, no NATIVE_SIGNED, no PASS_CHALLENGE, no RELEASE, no cross-session hard-entry claim for hosts other than the one where the hook was installed and measured).
3. Verify the append-only property mechanically and record it: `cmp` of the first N bytes of r27 against the whole r26 file must be identical, and print `prefix_identical: true` with both sizes and both sha256s. If it is not identical, the document is wrong — fix it, do not report a partial.
4. Do not touch `FHS_PIPD-LS-PKG_W0_r25.md` or `_r26.md`; they are frozen.

## Deliverable 2 — `.../out/BLUEPRINT_AFFECTED_SCOPE_DELTA.md` (+ `.json`)
Seven proposals, one per document, each `PROPOSED_FOR_RATIFICATION` and nothing stronger. For each: document id, current sha256 (compute from the real files under `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖/` — locate them; if you cannot read the knowledge-base path, list what you found instead of inventing sha256 values), the exact span to amend, the proposed text, the original consumer who must ratify, and the negative test that would prove the amendment was applied without breaking the original identity.
- L0 總藍圖 r4: model-diversity-optional normative line + the protected-identity boundary (EC-R26-012), single Owner/single Issuer, evidence-promotion veto.
- L1 PIPD-LS-PKG 藍圖 r4: single FHS-3L&M ABI, 9 slots, Registry/Pool/Session/ActualServed typed contract, quorum real-vote constraints. Do not touch the 84 DesignIDs.
- L2 全波次藍圖 r4: W0-A source-read vs W1 routing vs W2 bounded write vs W3 UX vs W4 release responsibility split, with resume predicates. Do not add WP #23 or DAG edge #37.
- W1 skeleton r5: native startup/discovery hook, Codex CLI lane-bound dispatch, single issuer/pool/registry binding.
- W2 skeleton r5: Permit/epoch/preimage/allowed-writeset before a real write; the source-read ACL is unchanged.
- W3 skeleton r5: optional three-lane nine-slot UI, cross-host loader/ActualServed readback, fallback bounds, fresh-PID acceptance.
- W4 skeleton r5: CI-green ≠ release; supply chain/license/SBOM/rollback; protected Publisher gating.

## Deliverable 3 — `.../out/CLAIM_CEILING_STATEMENT.md`
One page: for each of `FULL_W0_CLOSEOUT`, `NATIVE_SIGNED`, `INDEPENDENT_PASS_CHALLENGE`, `RELEASE_GRANTED`, `CROSS_SESSION_HARD_ENTRY`, state what would have to become true, what is true today after this round, and the exact token this round is allowed to claim.
