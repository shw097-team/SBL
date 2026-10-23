# SESSION HANDOVER — lane / model routing and the R15.2 ledger (2026-10-23)

Entry point for the next session is **`RESUME_HERE.md`** in this same directory. This document is the evidence and
rationale behind it: what was changed, what was measured, what was refused, and what remains owed.

**Ceiling:** `LOCALLY_VERIFIED_PARTIAL__CANDIDATE_ONLY__NO_INDEPENDENT_ACCEPTANCE`. Nothing below is an external
acceptance, a native admission, a host installation or a release.

---

## 1. The question this session was asked

> Use FAR to study the lanes and model routing HG-KSEOS already built, distinguish the **lane** model from the
> **session** model, apply this role split — PLAN = GPT 6.1 SOL-MEDIUM (OpenAI OAuth); EXECUTE / bounded writer =
> CODEX CLI with DEEPSEEK V4.1 FLASH (OPENCODE GO); Independent Acceptance Officer & VERIFY & SECURITY = CODEX CLI with
> checker GPT 6.1 SOL-MEDIUM (OpenAI OAuth) — then propose a low-friction, engineering-necessary, non-over-engineered
> solution, execute it, and if it works, solidify the experience so other sessions can reuse it.

## 2. FAR: what already existed, and what was actually broken

Everything the round needed already existed; nothing had to be invented.

| existing piece | role | verdict |
|---|---|---|
| `scripts/hgk-lane-dispatch.py` | lane → ordered pool → forced rank → per-attempt receipt | sound, one evidence gap |
| `lane_policy.py` + `config/lane-route-slots.candidate.json` | declared arms, transport, revision history | sound |
| `scripts/hgk-exec-model-frontdoor.py` | closes the EXECUTE lane, binds the active-policy digest | `BOUND`, digest `a3df959d…` matches |
| `lane_launcher.sh` + sealed `CODEX_HOME` | the proven invocation recipe | sound |

Three things were broken, none of them designed that way:

1. **`--relay-base` was missing `/v1`** — codex composed `ws://…/responses`, burned seven upgrade retries and exited in
   ~12 s. Eight dispatches died this way before it was seen.
2. **The three OPENCODEGO keys are in three different states** — `shw0968` → 200; `shw097` → 429 `GoUsageLimitError`
   (monthly quota); `OPENCODEGO_7776004` → 401. The proxy on `:10101` holds the dead key, the one on `:10102` holds the
   exhausted key. Upstream also requires an `x-opencode-session` header or answers 400 `MissingSessionID`.
   **The model was always available; the local proxies were lying about it.**
3. **Identity could only be read from the relay usage ledger** — so the OAuth direct path always produced
   `model=null, ok=false`, while the relay path produced a *green* receipt paid for out of the relay's own pool
   (proven: the relay answers 200 with a fake key and with no key at all). Green receipt and real token spend were
   mutually exclusive, which is exactly why the owner could not see their OAuth being consumed.

## 3. The solution that was adopted (small on purpose)

| change | size | why it is the minimum |
|---|---|---|
| `--identity-source {relay-usage, codex-rollout}` | one flag, one rollout reader, one provider-alias map | an OAuth turn has no ledger; the rollout is the only artifact that names the served arm |
| identity mode suppresses `--ephemeral` | one condition | ephemeral deletes the very evidence the mode depends on |
| `--relay-base` default ends in `/v1` | one line | removes the 12-second death |
| `:10105` passthrough shim (`ocg_passthrough.py`, 147 lines) | one file, `TRANSPORT_ONLY_NOT_AN_AUTHORITY` | reaches opencode-go with the good key without touching anyone else's proxy |
| `HGK_LANE_RECEIPT_TAG` | one env var | a second run of the same brief used to overwrite the first run's receipt |

No schema change, no new subsystem, no change to the receipt contract, no relaxation of rank/pool enforcement: an arm
that contradicts `--require-arm` is still refused (`ERR_REQUIRED_ARM_NOT_SERVED`).

## 4. Evidence

**Lane identity, before and after (same brief, same backend, one change apart):**

| run | seconds | `--ephemeral` | rollout | receipt | served arm |
|---|---|---|---|---|---|
| B6 | 227.97 | on | none | `ok=false`, `model=null` | — |
| B7 | 131.92 | off (implied by the flag) | present | **`ok=true`** | **`openai-codex/gpt-6.1-sol`** (rank 2, nonce ✓) |

**OAuth really is being spent on the direct path:** 243,886 input / 183,168 cached / 1,182 output / 194 reasoning
tokens, 60.46 s, exit 0, nonce ✓ (`TOKEN_EVIDENCE_PLAN_OAUTH.json`; the receipt of that run was overwritten by a later
run of the same brief, which is what motivated the receipt tag).

**PLAN's verdict, reached twice independently:** withdraw C10, C13, C15; build C14 later
(`PLAN_DECISION_R153_C10_C15.json`).

**Checker, measured over 91 real receipts** (`--declaration config/lane-route-slots.candidate.json`):

```
CONSISTENT 51 | VIOLATION 0 | UNVERIFIED 4 | NOT_GREEN 36   exit=1 (UNVERIFIED)
```

Earlier in the session the same run reported `VIOLATION 16`, including the round's own green receipts — because R3
folded "billing label absent" into "identity forged". Split into R3 (identity) and R7 (billing evidence); an absent
billing label is now an evidence gap, a disagreeing one is still a violation.

## 5. What was refused, and why (the honest part)

- **Six dispatches of one challenge brief, six FAILs.** B8 → B13 each found a different bypass of the same rule: pair
  guard → qualified label → stripped prefix → forged prefix → unreadable pair map → self-consistent secondary fields →
  injectable evidence. Every repair was mine; no independent PASS was ever obtained. The loop is **paused** at six by
  the owner's four-repeat rule (`TT-R15.3-CHECKER-BRIEF-REPEAT-6X`), not because the code is thought to be perfect.
- **Over-engineering, named.** The lane fix was three small changes and was green by B7. The six extra rounds hardened
  a checker that no R15 item depends on. They consumed ~15 minutes of model time and moved **zero** R15 checks. That
  judgement is recorded here so the next session does not repeat it.
- **No self-acceptance.** C10/C13/C15 were withdrawn rather than left looking like pending work; C14 is
  `BUILD_LATER`; W08 keeps `PARTIAL` with a ceiling that says the tests are green and the independent verdict is not.
- **A conflict is flagged, not resolved.** C21 is counted DONE in the denominator while an earlier note records no
  invocation evidence. The DONE count is therefore optimistic by one until someone decides.

## 6. R15.2 position, measured

```
Checks (25): DONE 8 | PARTIAL 12 | WITHDRAWN 3 (C10 C13 C15) | NOT_RUN 1 (C16) | PARKED 1 (C24)
WP    (18): DONE 4 | PARTIAL 13 | NOT_RUN 1 (W12)
Queue (53): DONE 33 | PARTIAL 5 | PARKED 3 | HOLD 3 | NEEDS_RECIPE 3 | EXPERIENCE_RUN_REQUIRED 5 | RECEIPT_RED 1 | RUNNING 0
TT: 73 entries, 16 open
```

Advanced this session: **C07** (lane identity readable on the OAuth path) and **W08** (checker hardened, 24 tests
green). Not advanced: **C04**, **C22**, **C16** — the three items that are genuinely owed.

## 7. Order of work for the next session

1. `C04` — lawful Native WorkOrder/ECP/Permit with bounded effect and readback (never exercised).
2. `C22` — CI/SBOM/Provenance/Release remainder (evidence surface is the gap).
3. `C16` — PIPD trace, all atoms (never attempted).
4. Owner-gated, do not self-sign: W02 policy digest, W12/SWOF W3, C19 permit, C24 release, M3 authority, C21 conflict.

## 8. What would falsify the claims above

- A VERIFY run on the OAuth path that returns `ok=true` with no token movement → the identity fix would be reading a
  label rather than an arm.
- A receipt whose `usage_model` disagrees with `transport_model` and still passes → the R3/R7 split leaked.
- An EXECUTE receipt that claims a served arm while `:10105` is the transport → attribution would be fabricated.
- Any C21 invocation evidence → the DONE count would be right and the flag should be dropped.

## 9. Files this session wrote or changed

```
_r152_ev (branch evidence/r15_2-20261022 @ 74ae7f1)
  _governance/round-20261022-r15_2/tools/run_lane.py                  identity source, /v1 default, receipt tag
  _governance/round-20261022-r15_2/tools/ocg_passthrough.py           :10105 transport shim
  _governance/round-20261022-r15_2/tools/check_lane_consistency.py    hardened oracle, R3/R7 split, UNVERIFIED
  _governance/round-20261022-r15_2/DENOMINATOR_R15_2.json             measured counts + withdrawal accounting
  _governance/round-20261022-r15_2/R15_STATUS_2026_10_23.md           the short version of §6
  _governance/round-20261022-r15_2/RESUME_HERE.md                     entry point for the next session
  _governance/round-20261022-r15_2/QUEUE_R15_2.json                   stale RUNNING cleared
  _governance/round-20261022-r15_2/TT_R15_2_REGISTER.json             TT-R15.3-CHECKER-BRIEF-REPEAT-6X
  tests/test_lane_consistency_{provider_and_path,time_sources,retired_arms,supersession}.py
HG-KSEOS (branch codex/hgk-final-closure-002 @ ece8e8a)
  scripts/hgk-lane-dispatch.py                                        --identity-source, provider aliases, rollout reader
  tests/test_lane_identity_rollout.py                                 4 passed
```

Skill `hgk-codex-lane-recipe` carries the reusable half: the two identity sources and how to choose between them, the
"200 does not prove who paid" probe, the `/v1` trap, the three-key state of OPENCODEGO, the three hardening shapes to
expect from an adversarial reviewer, and the rule that a guard which must be switched on is not a guard.
