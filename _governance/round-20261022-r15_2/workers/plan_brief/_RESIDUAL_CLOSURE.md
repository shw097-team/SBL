NONCE: PLAN-R152-RESIDUAL-NONCE-6B31D84E

Begin your reply with exactly this token on its own line: PLAN-R152-RESIDUAL-NONCE-6B31D84E

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# PLAN brief: how to actually close the residual set (R15.2)

You are the PLAN lane (SBL-Commander & PLAN), `openai-codex/gpt-6.1-sol`. Read-only analysis; no repository writes.

## What is being asked

For every residual item below, give the **lowest-friction engineering decision that can actually close it**, aligned with
the parent control package `SBL_PIPD-LS-PKG`. For each, answer four things:

1. **Class** — `CLOSE_NOW_AGENT` (an agent can finish it in this round), `CLOSE_BY_ONE_OWNER_STEP` (an owner must do
   exactly one thing; state the literal action), or `ACCEPT_AS_CEILING` (cannot be closed this round; state the exact
   claim ceiling that must be printed instead).
2. **Minimal sufficient evidence** — the smallest artefact set that would let an independent checker accept closure.
3. **What NOT to build** — the over-engineered version to avoid, and why it is not required by the parent package.
4. **Checkability** — one command or predicate that turns your recommendation into pass/fail.

Do not propose new abstractions unless a residual item cannot be closed without one.

## Residual inventory (measured, current)

WorkPackages 18: **4 DONE** (W00/W01/W03/W04), **12 PARTIAL** (W05 W06 W07 W08 W09 W10 W11 W13 W14 W15 W16 W17),
**2 NOT_RUN** (W02 Fabric active policy consumption; W12 SWOF W3).

CheckRuns 25: 3 DONE, 13 PARTIAL, **9 NOT_RUN** (C02 policy, C11 OpenSpec strict command, C12 FirstFail→repair→regression,
C13 FAR standing scope, C15 evolution sandbox/holdout/promotion, C16 PIPD trace all atoms, C19 W2→W3 permit + SWOF PR,
C21 three private ChatGPT hosts, C22 CI/SBOM/provenance/secrets/release).

E-series 9: 5 PARTIAL (E01 E03 E04 E05 E07), **4 NOT_RUN** (E02 PIPD/TPM/SPEC, E06 five tools/host/ZIP,
E08 SWOF-type isolated dogfood, E09 first real SWOF).

Milestones 4: M1 PARTIAL, **M2/M3/M4 NOT_RUN**.

Open TTs (19 not RESOLVED_MEASURED), severities as filed: 2 BLOCKER (Fabric active policy; SWOF W3 absent), 1
CRITICAL_CONTAINED class open (HGK execute cwd escape), 1 CRITICAL_CONTAINED (lane wrote control plane), 8 HIGH,
5 MEDIUM, 2 LOW, 1 INFO.

Facts you may rely on (all measured this round):
- 8 kinds declared, **5 implemented** (`CLI_TOOL`, `BROWN_PATCH`, `SKILL`, `AGENT_OS`, `AI_SYSTEM` in
  `sbl_core/m03_routing.py DEFAULT_POLICY`).
- Denominators closed arithmetically: 50 parents / 149 children; 441 = 6 + 24 + 25 + 386; 38 surfaces;
  39 mode gates = 13 `GATE_IDS` × 3 `MODES`.
- M4's semantic denominator: R14 TS27 records `semantic_total_state: UNMEASURED`, 20 units, 1,743 structural packets.
- Five tools: 3 of 5 exist as packaging bundles (`_r14s12_ev/pkg{,2}`: tpm, commander, challenge, 8 files each),
  **0 of 8 lifecycle verbs** anywhere.
- `hg-kseos doctor` PASS only under Python 3.12.13; host default 3.11.17 fails `python_supported`.
- `lifecycle.py:172` refuses `DELIVERED` with open/FAILED orders, but `DELIVERY_READY` has no guard; a candidate diff
  exists and `git apply --check` returns 0.
- Paired B1/B2 benchmark on one fixed suite: run 1 delta −0.082 s, run 2 +0.007 s (sign flips; no benefit claimable).
  B0 HGK-only is `NOT_COMPARABLE` — no owner-defined matched workload.
- EXECUTE arm `opencode-go/minimax-m3.1-flash-free` returned 410 Gone (deprecated); rebound to
  `opencode-go/deepseek-v4.1-flash` by owner order, pool revision 21.
- Four files appeared inside HG-KSEOS during lane dispatch windows (an SP-identity module, +100 lines in the
  dispatcher, a fixture and a test). Quarantined copies exist with hashes; the working tree is still dirty.

## The specific questions

Q1. **W06 / C17** — is `CLOSE_NOW_AGENT` correct for the three missing kinds, and what is the minimal sufficient
    evidence (candidate diff + tests vs. a real product write)? What must NOT be built?
Q2. **M4 / W14 / C18** — the semantic denominator is UNMEASURED. Is an agent-issued *measured proposal* (units counted
    from the DOC corpus with an explicit UNRESOLVED remainder) an acceptable closure, or is it owner-gated? State the
    exact claim ceiling either way.
Q3. **M2 / C12** — the smallest sufficient evidence set for "isolated E2E + complete mutation/repair".
Q4. **W02 and W12** — the two BLOCKERs. Give the literal one-step owner action for each, and the pre-built artefact
    that makes that step a single decision rather than a project.
Q5. **W13 / C20 / C21** — five tools, 0 lifecycle verbs, three hosts. What can be closed locally (double-build digest
    equality, doctor, effective-load) versus what is strictly host-issued?
Q6. **The four HG-KSEOS files** — adopt, or revert to the last commit (copies already preserved)? Give the criterion,
    not a preference, and say what evidence decides it.
Q7. **SOD006-C6** — checker and maker share a host. Is lane-level separation (`codex-lane:openai-codex/gpt-6.1-sol`
    as checker principal) ever sufficient, or is external AO mandatory for M1? State the condition.

## Output shape

A table with one row per residual group (Q1–Q7 plus any grouping you prefer), then a short section
"what I would do first, second, third" with the reason. Keep it under 1,200 words. No repository changes.
