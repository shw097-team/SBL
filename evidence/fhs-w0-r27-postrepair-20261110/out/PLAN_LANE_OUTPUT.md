# PLAN lane output (openai-codex/gpt-6.1-sol, Codex CLI, read-only)

Receipt: ok=true, exit 0, nonce present, 106.04 s. Source: `lanes/runs-plan/PLAN/R27PLANWORK2-20261111T003421/`

R27PLANWORK2

I’ll read the brief and follow its scope and gates.

R27PLANWORK2

Read the three requested documents in order. No files changed, providers called, or tests executed. This is a proposed plan—not a verified PLAN-lane receipt or acceptance result.

## A. Closure classification

“Local mechanical” describes a bounded candidate repair by the original repository writer; it does not authorize this read-only lane to write outside HGK.

| Finding | Classification | Justification quoting the report |
|---|---|---|
| EC-R26-001 | `NOT_CLOSABLE_HERE` | Requires the original Host and fresh-process enforcement: “不可繞過的 native startup/dispatcher hook 真驗收證據”. A repository guard alone cannot close it. |
| EC-R26-002 | `CLOSABLE_LOCAL_MECHANICAL` | Repair the existing tool; “不同 Session 可以覆寫” is deterministically testable through concurrent binding and replay negatives. |
| EC-R26-003 | `CLOSABLE_LOCAL_MECHANICAL` | The checker accepts “JSON 整數 `1` 票”; exact types and rehashed evidence can close the mechanism without rewriting signed receipts. |
| EC-R26-004 | `CLOSABLE_LOCAL_MECHANICAL` | Correct the separate metadata candidate: “L1 `6,224,679 bytes`” versus “111,331”. Never silently alter a signed Body; affected signatures would remain separately held. |
| EC-R26-005 | `NOT_CLOSABLE_HERE` | “No common ancestor” requires authoritative two-source DAG reconciliation; this lane cannot establish remote ancestry or authorize migration. |
| EC-R26-006 | `NOT_CLOSABLE_HERE` | “main registry **epoch 33**、branch **epoch41**” requires original-owner PR/Host convergence, excluded from this board’s merge/install scope. |
| EC-R26-007 | `NOT_CLOSABLE_HERE` | “沒有 PLAN 的 MiMo live inference ActualServed” requires real Host/provider receipts; static tests cannot supply them. |
| EC-R26-008 | `CLOSABLE_BUT_REQUIRES_OWNER_SIGNATURE` | “Owner preauth 時間不帶 timezone”: public crypto verification is mechanical, but enrollment and a corrected signed authorization instrument require the original Owner/Issuer. |
| EC-R26-009 | `CLOSABLE_LOCAL_MECHANICAL` | “full profile 不當列六項 excluded” is a bounded scope-schema correction with contradictory-profile negatives. |
| EC-R26-010 | `CLOSABLE_LOCAL_MECHANICAL` | “append-only 更正最新 HEAD 及 superseded”; append the historical correction in a new candidate, preserving r26. |
| EC-R26-011 | `CLOSABLE_LOCAL_MECHANICAL` | “19 clauses=**76 properties**” can be re-derived from receipts and guarded by typed-count negatives; signed originals remain immutable. |
| EC-R26-012 | `CLOSABLE_BUT_REQUIRES_OWNER_SIGNATURE` | “原 Owner 明確區分” model freedom from protected permissions requires an owner-ratified governance clarification, not an agent’s reinterpretation. |
| EC-R26-013 | `NOT_CLOSABLE_HERE` | Requires “原 Fabric Policy Reader admission/manifest、HGK Original Consumer 驗收”; manifest editing alone cannot confer policy effectiveness. |

**No finding is solely `CLAIM_WITHDRAWAL_ONLY`.** Unsupported Native/main/served claims must nevertheless be withdrawn immediately; withdrawal does not supply the missing mechanism or external evidence.

## B. Minimum ordered change-set DAG

Path shorthand:  
`S = SBL/evidence/fhs-w0-r26-repair-20261109`.

The report specifies several files only by basename. Their exact local locations—and the G24 implementation/test paths—were **not established by the requested documents**; resolve them before assigning writes. Do not invent replacements.

### Local candidate nodes

| Node / predecessors | File | Single responsibility | Required executed negative | Finding |
|---|---|---|---|---|
| **N0 — admission prerequisite** | Original-domain WorkOrder/ExecutionBinding; actual path unresolved | Bind original owner, allowed writes, source identities, rollback and preregistered checker oracle. | Foreign subject or unauthorized writeset must block assignment. | All downstream work |
| **N1 ← N0** | `S/tools/verify_quorum.py` | Validate genuine, precisely typed, subject-bound votes. | Independently mutate a valid fixture: omit candidate SHA → `MISSING_CANDIDATE_BINDING`; falsify Raw digest → `RAW_DIGEST_MISMATCH`; replace Boolean with `1` → `VOTE_TYPE_INVALID`. | 003 |
| **N2 ← N0** | `S/tools/fhs_3lm.py` | Make existing bindings immutable, run-scoped and fully revalidated. | Concurrent same-slot sessions cannot overwrite; pool-only mutation → `POOL_DIGEST_DRIFT`; retired Pro → `RETIRED_ARM`; stale nonce/session/TTL rejected; missing numeric epoch rejected. | 002 |
| **N3 ← N0** | New candidate counterpart of `FHS_ORIGINAL_ACK.json` | Correct source metadata and explicitly separated denominators. | Against real source bytes, `l1.bytes=111331` → `SOURCE_CONTRACT_BYTES_MISMATCH`; `28 properties` and clauses/properties substitution must fail typed validation. | 004, 011 |
| **N4 ← N3** | Existing G24 implementation, path unresolved | Mechanically enforce source-size and receipt-count invariants. | Mutate each corrected field individually from a passing fixture; each must produce a named rejection and nonzero exit. | 004, 011 |
| **N5 ← N0** | `EVIDENCE_SCOPE.json`, exact location unresolved | Separate full-profile coverage from CI portability. | Reintroducing six full exclusions while declaring them executed must fail; payload evidence must not satisfy full-profile requirements. | 009 |
| **N6 ← N1,N2,N4,N5** | Existing selftests/G29 integration/CI files, paths unresolved | Ensure production validation—not merely copied predicates—executes the regressions. | Deliberately restore each vulnerable predicate; its corresponding regression must fail. Missing inputs must never yield PASS. | 002, 003, 004, 009, 011 |
| **N7 ← N0** | New `writeback/W0/FHS_PIPD-LS-PKG_W0_r27.md` candidate | Append the historical HEAD correction and bounded claim ceiling. | Alter one frozen-prefix byte or promote an unsupported Native/full-closeout claim: reject; E12 ceiling violation → `CLAIM_CEILING_VIOLATION`. | 010 |
| **N8 ← N6,N7** | Original independent checker’s separately bound evidence output; path unresolved | Re-derive candidate results without accepting maker summaries. | Missing/foreign Raw, changed candidate, or incomplete coverage → FAIL/INCONCLUSIVE, never acceptance. | Local closure evidence |

For N3, the report’s reference values are **6,224,679 bytes**, **28,005 split-by-LF fragments**, **111,331 total source lines**, and **19 × 4 = 76 properties**. Recompute; do not merely hard-code them.

N7 must retain the original **668,540-byte** r26 prefix:

`0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f`

Record `52c9c21...` as superseded by the report’s historical `86f40ec...`; do not describe that abbreviated SHA as a newly verified current HEAD.

### Owner-gated continuation

- **N9 ← N8:** original Owner/Issuer verifies enrollment, all seven complete Ed25519 instruments, timezone-qualified authorization chronology and replay protection. Any replacement authorization is newly signed; originals remain unchanged. Closes **008** only with that external evidence.
- **N10 ← N8:** original L0/design Owner ratifies `model_diversity_optional` versus `protected_identity_permissions`. Negative: maker credentials cannot issue protected checker/issuer/publisher authority. Closes **012** only after ratification.
- **001/005/006/007/013 remain external dependencies**, corresponding to R26-03/05/07/08/09. Local nodes cannot substitute for them.
- **R26-11 remains incomplete** without the original full-source round and protected independent checker. R26-12 applies only when release is actually sought.

Every executed node needs passing positive/boundary controls, individually attributable negative failures, candidate/source/HEAD binding, command/exit/Raw evidence, readback, rollback and independent checking. No board card becomes DONE from this plan.

### Nodes that must NOT be attempted

- **SECOND_ROUTER:** workspace replacement `fhs_3lm.py` or private model pool.
- **SECOND_REGISTRY:** independently editing HGK pool/assignment projections instead of reconciling from `config/lane-routing-registry.yaml`.
- **SECOND_ISSUER:** agent-created enrollment, authorization, canonical acceptance or owner signature.
- **REWRITE_GOVERNED_BYTES:** in-place edits to r26, signed Bodies or frozen blueprint sources.
- **FORCED_HISTORY_CONVERGENCE:** unrelated-history merge, force-push, default-branch switch or treating “327 ahead” as established ancestry.

## C. Honest verdict ceiling

**Permissible ceiling after independently checked local repairs:**

`AUTHOR_DESIGN_COMPLETE_WITH_SCOPE_BOUND_EXTERNAL_CHALLENGE_HOLDS`

The report explicitly permits author-design completion with holds. Local repair success does not erase Host, owner-signature, policy-admission or history-convergence dependencies.

**Not permissible:**

`FULL_W0_CLOSEOUT`

Its report status remains **`HOLD_NOT_ACCEPTED`**. Likewise, `NATIVE_SIGNED`, `INDEPENDENT_PASS_CHALLENGE` and `RELEASE_GRANTED` remain **`NOT_GRANTED`** absent their original authorities. Negative tests firing alone cannot upgrade the external verdict from `PARTIAL`.

## D. Three highest risks

1. **False-green evidence laundering.** Copied predicates, static menu membership or maker summaries get presented as native success.  
   **Detection:** execute the real candidate entry points; use known-good single-mutation controls; independently rehash Raw; require ActualServed receipts for service claims.

2. **Authority substitution or signed-byte destruction.** Repair introduces another router/registry/issuer, or “corrects” signed historical material.  
   **Detection:** allowlisted diffs, original-byte preservation checks, unique-authority discovery, denied maker-signing tests and explicit owner-signature holds.

3. **Unbounded history/epoch migration.** Repair silently treats branch epoch41 as effective main or carries unrelated changes into convergence.  
   **Detection:** complete pinned dual-root H0 evidence, shallow/graft/replace checks, H1 dispositions, registry/pool/runtime binding and `AUTHORITY_HEAD_DRIFT` / `GIT_ANCESTRY_UNRESOLVED` rejection. No merge or cutover in this round.

