# RESUME HERE — lane routing session handover (2026-10-23)

You are picking up the SBL R15.2 round at `C:/Projects/Agent_Workspace/_r152_ev`.
Read this page, run §1, then go straight to §4 (the work that is actually owed). Do not re-litigate §5.

**Claim ceiling right now:** `LOCALLY_VERIFIED_PARTIAL__CANDIDATE_ONLY__NO_INDEPENDENT_ACCEPTANCE`
R15.2 is **not** complete and nothing here is externally accepted. No authority recognises an enforceably
distinct checker principal (M1), so every "independent" verdict in this tree is a local claim.

---

## 1. Sixty seconds of environment proof (run these first)

```bash
cd /c/Projects/Agent_Workspace/_r152_ev && git rev-parse --short HEAD   # expect 74ae7f1 or later on evidence/r15_2-20261022
cd /c/Projects/Agent_Workspace/HG-KSEOS && git rev-parse --short HEAD  # expect ece8e8a or later on codex/hgk-final-closure-002
netstat -ano | grep LISTENING | grep -E ":1010[0-9]"                  # expect four ports below
```

| port | what | who owns it |
|---|---|---|
| 10100 | EXECUTE lane front door (declaration digest bound) | `scripts/hgk-exec-model-frontdoor.py --host 127.0.0.1 --port 10100 --upstream http://127.0.0.1:10101 --declaration config/hermes-codex-lane.json --active-policy config/active-policy.json --pool config/lane-route-slots.candidate.json --pool-lanes EXECUTE` |
| 10101 | opencodex proxy (holds a key that returns 401 — do not trust it) | someone else's process, leave it alone |
| 10102 | desktop-model-router (holds a key that returns 429 quota) | someone else's process, leave it alone |
| 10105 | **our** opencode-go passthrough shim | `python _governance/round-20261022-r15_2/tools/ocg_passthrough.py --port 10105 --key-file "C:/Projects/Agent_Workspace/API KEY/shw0968_OPENCODEGO_KEY.txt"` |

If 10105 is dead, restart it from the round worktree root (`_r152_ev`). If 10100 is dead, restart it from
`HG-KSEOS`. Both are needed for the EXECUTE lane only; PLAN and VERIFY run without them.

## 2. The three lanes, exactly as they run today

All commands run from `_r152_ev`. `R=_governance/round-20261022-r15_2`.

**PLAN — GPT 6.1 SOL-MEDIUM over the user's own OAuth (this is the one that spends their tokens):**

```bash
cd /c/Projects/Agent_Workspace/_r152_ev && \
HGK_LANE_HUMAN_HOME="C:/Users/user/.codex" \
HGK_LANE_RELAY_BASE="https://chatgpt.com/backend-api/codex" \
HGK_LANE_IDENTITY_SOURCE="codex-rollout" \
HGK_LANE_RECEIPT_TAG="plan1" \
python $R/tools/run_lane.py --role PLAN --brief workers/plan_brief/<BRIEF>.md --nonce "PL-$(date +%H%M%S)" --timeout 300
```

**VERIFY / Independent Acceptance — same OAuth, checker model gpt-6.1-sol. This exact shape produced the first honest
green receipt of the round (B7: `ok=true`, `served_arm=openai-codex/gpt-6.1-sol`, 131s):**

```bash
cd /c/Projects/Agent_Workspace/_r152_ev && \
HGK_LANE_HUMAN_HOME="C:/Users/user/.codex" \
HGK_LANE_RELAY_BASE="https://chatgpt.com/backend-api/codex" \
HGK_LANE_IDENTITY_SOURCE="codex-rollout" \
HGK_LANE_RECEIPT_TAG="v1" \
python $R/tools/run_lane.py --role VERIFY --brief workers/challenge_brief/<BRIEF>.md --nonce "VER-$(date +%H%M%S)" --timeout 260
```

**EXECUTE — deepseek-v4.1-flash via our passthrough. The work lands, the receipt stays RED by design:**

```bash
cd /c/Projects/Agent_Workspace/_r152_ev && \
HGK_LANE_RELAY_BASE="http://127.0.0.1:10105/v1" \
HGK_LANE_RECEIPT_TAG="ex1" \
python $R/tools/run_lane.py --role EXECUTE --brief workers/codex_exec/<BRIEF>.md --nonce "EX-$(date +%H%M%S)" --timeout 300
```

Why red: the shim is a transport I built, not a declared arm, so the receipt cannot name the served arm
(`model=null`, `ok=false`). The edits still land on disk and the tests still run. **A red EXECUTE receipt means
"edited but not attributable", not "failed"** — verify the product by running the tests yourself, and never quote the
receipt as a pass.

## 3. What is already solid (do not redo)

| thing | state | where |
|---|---|---|
| lane identity on the OAuth path | works: `--identity-source=codex-rollout` reads the served arm from the codex rollout, so green receipt and real token spend coexist | `HG-KSEOS/scripts/hgk-lane-dispatch.py`, `tests/test_lane_identity_rollout.py` (4 passed) |
| lane model vs session model | separated and written down; a session answer may not become a lane verdict (`mandate_gate.py audit`) | `FAR_LANE_VS_SESSION_R153.json`, skill `hgk-codex-lane-recipe` |
| lane consistency checker | hardened: identity ≠ billing evidence, fourth verdict `UNVERIFIED`, evidence not injectable, fail-closed on unreadable lists | `$R/tools/check_lane_consistency.py`, 20 tests green |
| receipts cannot be silently overwritten | `HGK_LANE_RECEIPT_TAG` appends to the receipt name | `$R/tools/run_lane.py` |
| push | `python $R/tools/push_pat.py origin HEAD:refs/heads/evidence/r15_2-20261022` (plain `git push` cannot get credentials) | PAT file `API KEY/GITHUB-REPO_SHW097-4.txt`, never printed |

## 4. The work that is actually owed (start here)

Measured 2026-10-23 over 25 checks / 18 work packages:

```
Checks: DONE 8 | PARTIAL 12 | WITHDRAWN 3 (C10, C13, C15) | NOT_RUN 1 (C16) | PARKED 1 (C24)
WP:     DONE 4 | PARTIAL 13 | NOT_RUN 1 (W12)
```

**Agent-actionable, in this order:**

1. **C04** — a lawful Native WorkOrder/ECP/Permit with bounded effect and readback. Nothing was exercised today.
   Start in `HG-KSEOS/src/hg_kseos/` + `tests/`, drive with a narrow PLAN brief, judge with VERIFY.
2. **C22** — remainder of CI/SBOM/Provenance/Release. Pinned actions and scoped secret scan exist; the evidence
   surface is the open gap (see `HANDOVER_R15_3_20261023.md`).
3. **C16** — PIPD Intent/PI/PD/ECP/TQAEP trace, all atoms. NOT_RUN, no attempt has ever been made.
4. **W08** — parked on purpose, see §5. Leave it unless the owner re-opens it.

**Owner-blocked (do not attempt to self-sign):** W02 active policy digest, W12/SWOF W3 admission, C19 W2→W3 permit,
C24 hard gates and release, M3 independent authority, and the C21 three-host claim (see §6).

## 5. Do not reopen without an owner order

- **The checker loop is paused at six.** The same challenge brief was dispatched B8–B13 and failed six times, each
  time exposing a different bypass. `TT-R15.3-CHECKER-BRIEF-REPEAT-6X` records the six verdicts and the resume
  condition: **do not reuse that brief**; if it is resumed, rewrite the oracle around one declared identity tuple
  rather than adding an eighth patch.
- **Do not invent a new EXECUTE arm.** The mandated arm is `opencode-go/deepseek-v4.1-flash`; `mimo-v2.6-flash` is
  fallback 1 and was never needed (it answers 200).
- **Do not declare the lane "unavailable" from one worker's failure.** Measure the transport first: three OPENCODEGO
  keys have three different states, and the proxies on 10101/10102 hold the two bad ones.

## 6. Open conflicts you must not paper over

- **C21** is counted DONE in the denominator while an earlier note records no invocation evidence. It is flagged as a
  conflict; until someone decides, the DONE count is optimistic by one.
- **EXECUTE attribution**: until `:10105` is declared (or 10101/10102 get working keys), any EXECUTE work is
  `EDITED_NOT_ATTRIBUTED`.
- **M1**: no enforceably distinct checker principal exists in any authority's eyes.

## 7. Traps that cost this session real time (each one measured)

1. `--relay-base` **must end in `/v1`**. Without it codex builds `ws://…/responses`, retries the upgrade seven times
   and dies in ~12 s.
2. On the OAuth direct path the receipt says `model=null` **unless** `HGK_LANE_IDENTITY_SOURCE=codex-rollout`, and that
   mode must not pass `--ephemeral` (ephemeral suppresses the rollout, which is the only arm evidence).
3. Same brief twice = two receipts with the same name = evidence destroyed. Set `HGK_LANE_RECEIPT_TAG`.
4. opencode-go refuses requests without an `x-opencode-session` header (400 `MissingSessionID`); the shim adds it.
5. A file mtime can never prove a pool revision; the checker answers `UNVERIFIED` and exits 1.
6. Missing billing evidence is not a forged identity — that mistake made the checker convict its own green receipts.
7. `git push` fails with "unable to get password from user"; use `push_pat.py`.
8. Native tools cannot read MSYS paths: pass `C:/...` and put scratch under `$TMPDIR`.
9. Four or more repeats of a blocked step require measurement, not a fifth attempt (owner rule).
