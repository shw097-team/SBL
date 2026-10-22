# R14 — TS30: the M4 verdict

**Verdict: BLOCKED.** M4 does not pass, so `SBL_FULL_PRODUCT` is not complete.

Issued 2026-10-22T03:15:40.875554Z from the obligation ledger (31 rows): BLOCKED 3, BLOCKED_SOFT 1, DONE 17, OPEN 1, PARTIAL 9.

## The four gates, as measured

| Gate | Status | Why |
|---|---|---|
| M1 | **SIGNED** | 4/4 levels measured; signed under the Owner's explicit authorization |
| M2 | **NOT_PASSED** | the dogfood change works and was re-run here, but no independent principal accepted it; the live spine records WO-R14-TS23-M2-TRIAD verdict FAIL |
| M3 | **BLOCKED** | no W3 permit exists by field signature (0 hits); route-out written, nothing claimed |
| M4 | **BLOCKED** | cannot pass while M2 is not passed and M3 is blocked |

## What still stands between here and M4

| Obligation | State | Residual gap | Who can close it |
|---|---|---|---|
| R14-TS10 | PARTIAL | vendor commands load/invoke/upgrade/rollback do not exist; a local wrapper is not the tool | SBL tooling owner (four vendor verbs do not exist) |
| R14-TS11 | PARTIAL | no third-party scanner on this host: SBOM/licence/secret results are self-authored | host owner (install a third-party scanner set) |
| R14-TS12 | BLOCKED_SOFT | a CR must grant the plugin schema/host authority; until then the three surfaces stay HOST_PENDING | host owner (three plugin surfaces HOST_PENDING) |
| R14-TS13 | PARTIAL | PIPD bundle Owner enforces the two remaining semantic-only refusals (pipd-assurance-tqaep NEG-001, pipd-package-project NEG-001) | PIPD bundle owner (two schema-only negatives) |
| R14-TS17 | PARTIAL | 66 rows stay DECLARED_ONLY; 2 negatives are accepted by their own schemas (PIPD bundle owner) | PIPD bundle owner + suite owner (66 declared-only rows) |
| R14-TS19 | PARTIAL | upstream historical pointers cite files absent on this host; nothing can make them verifiable here | document archive owner (upstream 全DOC藍圖(8).md absent on this host) |
| R14-TS20 | PARTIAL | 411 rows cite SpecBuild_整合工程總藍圖_v2.0r1(1).md which is absent; and the inventory's digest column is not per-row | document archive owner (upstream SpecBuild v2.0r1(1).md absent) + inventory author (single digest column) |
| R14-TS23 | PARTIAL | M2 needs an independent principal to accept the dogfood change; the maker cannot supply that for itself | independent reviewer / Owner (M2 acceptance never happened) |
| R14-TS25 | BLOCKED | SWOF Native Owner must issue a W3 permit (or typed NACK) before any governed SWOF change can exist | SWOF Native Owner (no W3 permit) |
| R14-TS26 | BLOCKED | depends on TS25, which depends on a W3 permit | SWOF Native Owner (depends on TS25) |
| R14-TS27 | BLOCKED | PIPD Source Owner signs the denominator (proposal is ready and unsigned) | PIPD Source Owner (semantic denominator unsigned) |
| R14-TS28 | PARTIAL | publish the new evidence files, then re-run the blob readback so identical>6 | release owner (candidate branch has no remote) |
| R14-TS29 | PARTIAL | D-19 canonical bundle needs an owner-defined canonical list; CR plugin authority stays host-pending | SBL owner (D-19 needs an owner-defined canonical list) + host owner (CR authority) |
| R14-TS30 | OPEN | M4 full contract verdict - only a different checker plus owner HITL may sign SBL_FULL_PRODUCT_PASS | unassigned |

## Claim ceiling

M4 is NOT passed. SBL_FULL_PRODUCT is NOT complete, no semantic completion percentage may be quoted (TS27 denominator unsigned), and no DOC-00..13 semantic acceptance is claimed. What is claimed: 17 obligations closed with their own receipts, M1 signed, one real WorkOrder chain executed end to end, and every remaining gap named with its owner.

## Why this is not rounded up

A terminal verdict computed from a ledger cannot be better than the ledger. Every row above was closed only by a receipt the audit could resolve; the rows that remain are the work, not a reporting gap. Three of them (TS25/26/27) need a signature that belongs to another principal, two need an artifact this host does not have, and one (TS23) needs an independent reviewer to read what was built.
