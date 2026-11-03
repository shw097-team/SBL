# LANE_EVIDENCE — what HG-KSEOS's lane + model routing + checker actually does

Round: `_run_sbl_tpm_pre_v2_final_20261103` / far/lane
Source repo: `C:/Projects/Agent_Workspace/HG-KSEOS` @ `candidate/r18-fhs-skeleton-spine-20261029`
HEAD `f5474257aa7d2005937867340f4cd01b39751129`, committed 2026-11-01 12:38 +0800
Method: read-only. No model call was made in producing this document. No credential value was read,
printed or hashed; where a credential exists only its presence, field name and length are reported.

Host checks re-measured for this document (not assumed):

| Check | Command | Result |
|---|---|---|
| Codex auth | `codex login status` | `Logged in using ChatGPT` (exit 0) — OpenAI **OAuth**, not an API key |
| Model catalogue | `codex debug models` | `gpt-6.1-sol` present; reasoning levels low/medium/high/xhigh/max/ultra; `shell_type: unified_exec`; context 272000 |
| PowerShell 7 install path | `ls "/c/Program Files/PowerShell/7"` | `No such file or directory` — **F2 confirmed absent** |
| `pwsh` on PATH | `command -v pwsh` | `<HOME>/AppData/Local/Microsoft/WindowsApps/pwsh` → `PowerShell 7.6.9` (Store alias, not the Program Files install) |

---

## 1. The lane manifest: what it isolates, and what it does not claim

Primary file: `config/hermes-codex-lane.json`, schema `HGK-HERMES-CODEX-LANE/1`.
Task id is self-describing: `HGK_CODEX_DESKTOP_HERMES_CLI_PROVIDER_LANE_ISOLATION_ONLY`.

| Field | Value | What it means |
|---|---|---|
| `status` | `ACTIVE_FAIL_CLOSED` | Operational posture marker for the *launcher*, not an authority grant |
| `scope` | `launcher-process-tree-only` | The isolation claim is bounded to processes the launcher spawns |
| `human_codex_home` | `<HOME>\.codex` | The human's home; the lane declares it must not be used |
| `hermes_codex_home` | `%LOCALAPPDATA%\HG-KSEOS\codex-hermes` | Isolated CODEX_HOME for the lane |
| `hermes_opencodex_home` | `%LOCALAPPDATA%\HG-KSEOS\opencodex-hermes` | Relay state home |
| `opencodex_port` | `10101` | Shared loopback relay (`http://127.0.0.1:10101/v1`) |
| `execute_frontdoor_port` | `10100`, host `127.0.0.1` | Sealed single-model EXECUTE door; exact path/method allowlist |
| `execute_frontdoor.upstream` | `http://127.0.0.1:10101` | The door proxies the shared relay |
| `execute_frontdoor.sanctioned_pair` | `opencode-go/deepseek-v4.1-flash` | One provider/model only |
| `default_execute_route` | `CODEX_CLI_SEALED_LANE` | Dispatch path |
| `model` / `provider` | `deepseek-v4.1-flash` / `opencode-go` | EXECUTE-lane primary |
| `credential_env` | `OPENCODE_GO_API_KEY` | Declared only; value never read (see §3 note) |
| `openai_fallback` | `false` | No silent OpenAI substitution on this route |

The manifest is unusually explicit about **not** claiming privilege:

- `execute_frontdoor.residual_risk`: `LOCAL_RUNTIME_CONTROL_NOT_OS_BOUNDARY` — "raw http://127.0.0.1:10101
  remains directly reachable and is explicitly out of scope; the front door does not sandbox the OS or
  block a caller who bypasses the launcher."
- `execute_frontdoor.enforcement_honesty`: it enforces the model **field**, "not a byte-level content filter".
- `sod_note` (R15): "Model-axis separation is ABSENT and recorded as OPEN_OWNER_ORDERED, not hidden. What
  remains is PROCESS separation …, LANE separation, EVIDENCE-PATH separation and the no-self-acceptance
  rule. No principal-independence and no cross-family-independence claim is made."
- `execute_route_contract.child_model_enforcement.enforcement_status`: `UNPROVEN_AS_ENFORCEMENT` (finding F7).
- `far_exec_identity_002.residual_notes`: "the front door is not in the request path until the owner-gated
  APPLY wires this candidate config + launcher; **this file alone enforces nothing**."
- `lane_dispatch_note`: the single-model 10100 door is "retired from the pool path (it 403s every model
  except one)".

Adjacent manifests, same read:

- `config/lane-routing-registry.yaml` — schema `HGK-LANE-ROUTING-REGISTRY/1`, `status: IN_FORCE`, epoch 40.
  Authority basis is an owner order, and it says of itself: "this registry carries no cryptographic
  signature, so the change is REPO_BOUND owner-order provenance, not NATIVE_SIGNED." It also records
  `transport_model_constraints.claim_ceiling`: a successful lane turn "does NOT prove the model ran with
  its catalog metadata".
- `config/verify-lane-contract.json` — `HGK-VERIFY-1`, `claim_ceiling: CANDIDATE_ONLY`. It constrains the
  *shape and ordering of a checker verdict* (skeleton-first, no heredoc writes, tool-call budget 28, typed
  refusal, required keys). It grants no execution ability.

**Answer to Q1:** the lane isolates a Codex-CLI process tree: a separate `CODEX_HOME`, a separate relay
state home, a loopback port, a path/method-allowlisted front door and a pinned, sha256-checked binary. It
claims exactly that and no more — it repeatedly states it is not an OS boundary, does not prove model
identity of the child, and enforces nothing until an owner-gated APPLY wires it. The strongest thing it
claims is *bounded routing plus a usage receipt*, which is what §2 shows.

---

## 2. Receipts proving a Codex run actually COMPLETED a model turn on this host

Every row below is a machine-written receipt or raw transcript already in the repo, not a narrative.
`served_arm` is the arm the relay actually served, read from the receipt — not the flag that was passed.

| # | Path | Date (UTC) | Lane / role | Served arm | What the receipt proves |
|---|---|---|---|---|---|
| R1 | `evidence/FAR-LANE-ROUTE-REBIND-20261015/receipts_EXECUTE_1/dispatch.json` (+ `stdout.txt`, `raw/attempt-9400-1792037723-1-stdout.txt`) | 2026-10-15T04:15:46Z | EXECUTE / writer | `opencode-go/deepseek-v4.1-flash` | `ok: true`, `exit: 0`, `timed_out: false`, 22.72 s, `usage_receipt_ok: true`, `usage_rows_shape_invalid: 0`, stdout 33 032 B byte-exact. Raw stream ends `{"type":"turn.completed","usage":{"input_tokens":100874,"cached_input_tokens":92288,"output_tokens":1470,"reasoning_output_tokens":848}}` and contains the agent's closing `REBIND_EXECUTE_1_DONE`. A full model turn ran end-to-end through the relay on this host, under `sandbox: workspace-write`, with `sandbox_escalation_authorised: false`. |
| R2 | `evidence/FAR-LANE-ROUTE-REBIND-20261015/receipts_VERIFY_SECURITY_1/dispatch.json` (+ `stdout.txt`) | 2026-10-15T04:18:32Z | VERIFY_SECURITY / checker | `opencode-go/glm-5.3-flash` | `ok: true`, `exit: 0`, 24.7 s, `turn.completed` with 46 853 in / 616 out, `served_arm` equals `required_arm`, `subject_mutation.files_before/after = 1/1` with empty added/removed/changed. Proves the checker lane runs a real turn **and** that the non-mutation guard was measured, not asserted. |
| R3 | `evidence/review/OWNER-ORDER-20261021-GPT-QUOTA-RESTORED/probe_gpt_61sol_VERIFY3.json` | 2026-10-21T07:30:59Z | VERIFY_SECURITY / checker | `openai-codex/gpt-6.1-sol` | `ok: true`, `exit: 0`, `served_arm = required_arm = openai-codex/gpt-6.1-sol`, `used_transport_model: gpt-6.1-sol`, identity gate arm satisfied by "non-empty **refreshable credential** present in `codex-accounts.json`". Proves the **OpenAI OAuth** arm itself serves a turn on this host, not only opencode-go arms. |
| R4 | `ops/session-20261031/FHS-ALLPASS-20261031/receipts/VERIFY_a2.json` | 2026-10-31T14:01:49Z | VERIFY_SECURITY / checker, `mode: pinned_primary` | `openai-codex/gpt-6.1-sol` | `ok: true`, `exit: 0`, 6.11 s, `nonce_present: true`, raw stdout ends `{"type":"turn.completed","usage":{"input_tokens":21222,...}}` with `agent_message` text `NONCE-VERIFY-A2-20261031`. `codex_home: <HOME>\.codex`, `human_home_transport_acknowledged: true` — i.e. the OAuth arm runs from the **human** home, with that fact promoted into the receipt instead of hidden. |
| R5 | `ops/session-20261031/FHS-ALLPASS-20261031/receipts/PLAN_reqarm2.json` | 2026-10-31T14:25:42Z | PLAN / writer, `pinned_primary` | `openai-codex/gpt-6.1-sol` | `ok: true`, 12.05 s, `reasoning_effort: "medium"` recorded on the attempt. Proves the medium-reasoning Sol binding is dispatchable on this host today (2 days before this document). |
| R6 | `var/B1-HERMES-R10/wt-pipd/.hgk/rounds/R10-20261011-s4-bclass-decisions/verify-codex/INDEPENDENT_ACCEPTANCE_R10_CROSSMODEL.md` | R10, 2026-10-11 | VERIFY_SECURITY / independent acceptance officer | `openai-codex/gpt-6.1-sol` | Cross-model independent acceptance: `verdict = FAIL` on 1 of 12 items, `nonce = HGK_LANE_NONCE_OK`, `served_arm = openai-codex/gpt-6.1-sol`, relay usage row "provider openai-p6a1fe3 / model gpt-6.1-sol / status 200 / **effort medium**", `used_seconds 230.69`, subject tree 3979→3979 files with matching digests, plus a verbatim 8-item `could_not_verify` block. |

Aggregate over the repo (machine count, not impression): `served_arm` occurrences —
`openai-codex/gpt-6.1-sol` ≈ 3 040 rows, `opencode-go/deepseek-v4.1-flash` ≈ 689,
`opencode-go/minimax-m3.1-flash-free` ≈ 465, `opencode-go/glm-5.3-flash` ≈ 78,
`openai-codex/gpt-6-luna` 1, `null` 55.

**What these receipts collectively prove:** on this Windows host, a Codex-CLI process, pointed at the
loopback relay with a pinned model, completes a real model turn (token usage accounted, nonce echoed,
`turn.completed` emitted) on both the opencode-go arms and the OpenAI OAuth arm. **What they do not
prove:** that the turn could create a child process — see §5 F1. Note the receipts' own ceiling string:
"a pass here proves the Codex-CLI lane served this turn through the relay with a matching usage receipt;
it is not an acceptance of any subject."

Common stderr on every one of these receipts, worth recording because it is a real limitation:
`ERROR codex_api::endpoint::responses_websocket: failed to connect to websocket: HTTP error: 426 Upgrade
Required` — the relay does not speak the Responses WebSocket, so turns fall back to HTTP streaming. Turns
still complete; the transport is degraded, not broken.

---

## 3. The checker / acceptance lane, and its authentication

An independent acceptance genuinely ran through `codex` with an OpenAI model. Evidence:

- **R6** above is literally titled "Independent acceptance — R10, cross-model (CODEX CLI / VERIFY_SECURITY
  lane)", records `served_arm = openai-codex/gpt-6.1-sol`, effort `medium`, a real verdict (`FAIL` on one
  item, i.e. the checker was willing to fail the maker), and separates "what this verdict does and does
  not cover".
- `config/lane-routing-registry.yaml` `owner_in_force.lane_rank1` binds PLAN and VERIFY_SECURITY to
  `openai-codex/gpt-6.1-sol`, `reasoning_effort: medium`, transport `codex-native-oauth`.
- `config/verify-lane-contract.json` (`HGK-VERIFY-1`, `claim_ceiling: CANDIDATE_ONLY`) governs the shape of
  the checker's verdict object.

**Auth mechanism: OpenAI OAuth (ChatGPT), not an API key.** Three independent confirmations:

1. `codex login status` → `Logged in using ChatGPT`.
2. The lane's own identity gate records for the gpt-6.1-sol arm:
   `requirement: "relay_pool"`, `detail: "non-empty refreshable credential present in codex-accounts.json"`.
3. I inspected `%LOCALAPPDATA%\HG-KSEOS\opencodex-hermes\codex-accounts.json` **by field name and length
   only**: one account key `chatgpt-1791610865690`, containing `credential/accessToken` (len 1878),
   `credential/refreshToken` (len 211), `credential/expiresAt`, `credential/chatgptAccountId`,
   `refreshGrantFingerprint`, `lastCodexValidationStatus: ok`. A scan for any `apiKey` / `api_key` /
   `openai_api_key` field returned **NONE** — there is no API-key material in the OAuth account store at
   all. Values were not read out; only names and lengths.

Separately, the opencode-go arms authenticate with an API key named by
`credential_env: OPENCODE_GO_API_KEY` (resolved from the Hermes root `.env` per
`credential_resolution: existing-process-env-then-canonical-hermes-root-env`). I did **not** read that
value; its presence and length are out of scope for this document. Degradation of that pool is already on
record in the slice: `06_closeout_addendum.md` §5 "OpenCode Go key pool: two of three keys return `429
GoUsageLimitError`, one returns `401`."

Governance caveat the registry states about itself, important for any acceptance claim built on it: the
checker binding is "REPO_BOUND owner-order provenance, **not NATIVE_SIGNED**", and after epoch 40 PLAN and
VERIFY again share `gpt-6.1-sol`, so "SOD006-C4 describes the live binding again … shared-model
correlation is an accepted deviation under this order, not a satisfied invariant."

---

## 4. Owner envelope: what a FAR-15 window can and cannot sign

Files read: `ops/session-20261031/tools/owner_window.py` (441 lines) and
`C:/Projects/Agent_Workspace/var/B1-PIPD-PKG-20261027/owner_window.py` (441 lines) — **byte-identical**
(`diff` → no output). Companion modules `owner_vault.py` (189 lines, ed25519 + scrypt + AES-256-GCM +
DPAPI escrow) and `owner_prompt.py` (258 lines) are both present in the package, so the envelope is
complete, not a stub.

### 4.1 Structural limits (constants at the top of the file)

| Element | Value | Effect |
|---|---|---|
| `EFFECT_ORDER` | `READ_ONLY_PROBE < REPOSITORY_WRITE < HOST_OPERATIONS < USER_DATA_EFFECT` | Total order for the effect ceiling |
| default `--effect-ceiling` | `REPOSITORY_WRITE` (cap index 1) | A default window cannot sign `HOST_OPERATIONS` or `USER_DATA_EFFECT` |
| — (fallback) | an unrecognised ceiling string silently maps to cap 1 | Fail-closed on typos |
| `--ttl-hours` default | `8` | Window lifetime |
| `--max-ops` default | `40` | Hard signing budget; `REFUSED_OP_BUDGET_EXHAUSTED` past it |
| `ALLOWED_KINDS` | `{merkle_root, row}` | Any other kind → `REFUSED_KIND_NOT_IN_SCOPE` |
| `DEDICATED_KINDS` | `{sourcefreeze, release}` | Signable **only** by a window opened with `--allow-dedicated` |
| dedicated limits | `ttl_hours <= 1`, `max_ops <= 4`, kind must also be in `--scope` | Otherwise `REFUSED_DEDICATED_WINDOW_TOO_BROAD` / `REFUSED_DEDICATED_NOT_IN_SCOPE` |
| `FORBIDDEN_KINDS` | `release, sourcefreeze, policy_authority, trust_anchor, owner_enrollment, elevated_effect, userdata_effect, remote_publish` | `REFUSED_ESCALATION_NEEDS_DEDICATED_AUTH` (`owner_enrollment` → `REFUSED_ENROLLMENT_CHANGE_IN_WINDOW`) |
| `ENROLLMENT_KEYS` | `("owner_enrollment",)` | Owner identity is pinned at open; a changed owner key sha → `REFUSED_ENROLLMENT_CHANGE_IN_WINDOW` |

Every refusal is written to the window file (`refusals[]`) **and** to the signing log — refusals are
evidence, not silence. The private key is loaded into process memory only and `del`-eted on close; on disk
it exists solely as `owner.key.enc` (scrypt + AES-256-GCM).

### 4.2 Files written

| Path | When | Content |
|---|---|---|
| `~/.hgk-owner/window.json` (or `$HGK_OWNER_WINDOW_PATH`) | on open, on each sign, on close | `OwnerSigningWindow@1`: id, task, scope, `max_ops`, `ops_used`, `effect_class_ceiling`, `expires_at`, `owner_public_hex`, `port`, `state`, `refusals[]` |
| `~/.hgk-owner/window.token` | on open; deleted on close | 24-byte random hex bearer token; ACL'd to the current user via `icacls /inheritance:r`; `chmod 600` |
| `<workspace>/artifacts/SIGNING_LOG.jsonl` | every open/sign/refusal/close | Append-only ledger: ts, `window_id`, op, decision, `payload_sha256`, `ops_used` |
| `<workspace>/artifacts/OWNER_WINDOW.json` | on open | Owner-**signed** receipt of the window itself (ed25519 over a canonical projection) |
| `~/.hgk-owner/artifacts/WINDOW_CLOSE_FORCE_<ts>.json` | only with `close --force` | Recovery receipt with `"signed_anything": false` |

Note the correction to a common assumption: `SIGNING_LOG.jsonl` is **workspace-relative**
(`<workspace>/artifacts/`), not under `~/.hgk-owner`. Only `window.json`, `window.token` and the force-close
receipts live in the owner home.

### 4.3 Can any code path sign a HOST_OPERATIONS?

**Yes — by choosing the ceiling at open time.** `HOST_OPERATIONS` is an *effect class*, not a kind: it sits
in `EFFECT_ORDER` and is absent from `FORBIDDEN_KINDS`. A window opened with
`--effect-ceiling HOST_OPERATIONS` (or `USER_DATA_EFFECT`) accepts a `/sign` request carrying
`effect_class: "HOST_OPERATIONS"`, subject to TTL, op budget, payload-sha match and the
`merkle_root`/`row` kind restriction. Nothing in the code refuses it; the bound is the operator-chosen
ceiling, and that choice is written into `window.json`, `OWNER_WINDOW.json` and the log.

This is not hypothetical — it is what is live on this host right now, and it has produced a real permit:

- Live window `WIN-f3452453f719`, task `HERMES-FAR-R3-HOST-UNBLOCK`, opened 2026-11-03T11:28:39,
  TTL 4 h, `max_ops 20`, `ops_used 2`, `dedicated_scope []`, **`effect_class_ceiling: HOST_OPERATIONS`**,
  `state: OPEN`, 0 refusals, broker reachable.
- `SIGNING_LOG.jsonl` shows its `WINDOW_OPEN` (`effect_class_ceiling: HOST_OPERATIONS`, `prompt_source:
  tkinter`) and two `row` signatures at 11:29:37 and 11:30:48.
- `ops/session-20261031/FHS-ALLPASS-20261031/WP-FHS-12/RUNTIME_PATH_LAB.v2.json` `b_canonical_positive.permit`:
  `permit_id PERMIT-WP12-HOST-20261101-01`, `effect_class HOST_OPERATIONS`, `window_id WIN-91b01b7cd918`,
  **`signature_verifies: true`**, `delegation_id R21-CANON-c0542636`. That permit authorised retiring a
  stale `hermes.cmd` shim on the host.

So the honest statement is: **a window can sign a host-operation permit if, and only if, the owner opened it
with that ceiling.** The default is `REPOSITORY_WRITE`, and an agent cannot raise a ceiling on an existing
window — `effect_class` above `cap` returns `REFUSED_EFFECT_CLASS_ABOVE_WINDOW`.

### 4.4 Can any code path sign a sourcefreeze (or release) escalation?

**Yes, but only through the explicitly-flagged dedicated path**, and never through a normal window:

- Default window + kind `sourcefreeze` → `_dedicated_ok` is false → the kind is in `FORBIDDEN_KINDS` →
  `REFUSED_ESCALATION_NEEDS_DEDICATED_AUTH` (HTTP 403). This is the FAR-15 invariant and it holds.
- With `open --allow-dedicated sourcefreeze` **and** `sourcefreeze` also listed in `--scope` **and**
  `ttl_hours <= 1` **and** `max_ops <= 4`, `_dedicated_ok` becomes true and the signature is issued, with a
  `DEDICATED_AUTHORISATION` row in the log recording scope/TTL/budget, and
  `dedicated_authorisation: "explicit"` stored in the window.
- Unknown dedicated kind → `REFUSED_DEDICATED_KIND_UNKNOWN`; broad dedicated window →
  `REFUSED_DEDICATED_WINDOW_TOO_BROAD`.

That is a *narrowing* of the original FAR-15 invariant (FAR-18 §2 乙案), made by owner authorisation and
fully receipted — not a bypass. It is one command-line flag away from a normal window, which is the residual
policy risk worth naming: the only thing separating "may sign a sourcefreeze" from "may not" is four
arguments chosen at open time by whoever runs the tool, and the private-key passphrase prompt is the sole
human gate.

### 4.5 Residual weakness (measured, not inferred)

The bearer token in `window.token` is the *only* caller check: `if req.get("token") != token:` → 403. The
token is not bound to a process, user SID or pid, and it sits in a 0600/ACL'd but plainly readable file for
the lifetime of the window. Any local process running as the same user that can read that file can request
signatures within the window's scope for as long as it is open — including a `codex` child process. The
mitigations are the ceiling, the TTL, the op budget and the log; there is no caller authentication. Also
measured 2026-10-31 and recorded in-code: because the signing service lives inside the `open` process, if
that process dies the window stays `OPEN` and `open` refuses a new one (`WINDOW_ALREADY_OPEN`) until TTL —
hence the `close --force` recovery path, which signs nothing.

---

## 5. Per-FirstFail judgement

**F1 — the Windows sandbox cannot create child processes in non-interactive `codex exec`.**
The lane does **not** touch this, and cannot. This is a `CreateProcess` policy decision taken inside the
Codex CLI before any child exists; the lane controls *which model and which home and which relay*, so it
never reaches that code path. Grounded evidence from this slice's own probes
(`_run_sbl_tpm_pre_v2_final_20261103/host/SANDBOX_EVIDENCE.md`, `host/host_probe3_err.txt`, 2026-11-03):

```
ERROR codex_core::tools::router: error=exec_command failed: CreateProcess { message:
"Rejected(\"`\\\"C:\\Users\\user\\pwsh7\\pwsh.exe\\\" -Command 'echo HOST_PROBE_OK'` rejected: blocked by policy\")" }
... same rejection for C:\WINDOWS\system32\cmd.exe /c 'echo HOST_PROBE_OK'
```

Two facts sharpen the diagnosis and both are *against* the lane being a remedy: (a) a real, non-alias
binary path is rejected exactly like `cmd.exe`, so this is not a path-resolution bug that a better
`CODEX_HOME` or binary pin could fix; (b) `codex sandbox "<HOME>/pwsh7/pwsh.exe" -NonInteractive
-Command '$PSVersionTable...'` **succeeds** (`7.6.9`, `14`), while `codex sandbox` on the WindowsApps alias
fails `CreateProcessAsUserW failed: 5 (access denied)` — so the OS and the sandbox helper *can* create
children; it is the exec-mode policy gate that refuses. Meanwhile all six receipts in §2 show model turns
completing under the same `workspace-write` sandbox with `sandbox_escalation_authorised: false`, which is
the proof that *model service and child-process creation are independent axes*. The only observed way past
F1 is `--sandbox danger-full-access`, used for isolated diagnosis only and explicitly "**not** an
unattended default" (`06_closeout_addendum.md` residual debt 1), and the slice's own handoff forbids using
danger-full-access results as host qualification evidence.
→ **does not remove F1; does not partially mitigate it.** It is orthogonal: lane/routing makes turns
served, F1 makes processes denied. What the lane *does* contribute is negative knowledge worth keeping —
the ability to prove that a failing turn failed at `CreateProcess`, not at model transport, because the
receipt separates `served_arm`/`usage_receipt_ok` from tool errors.

**F2 — `C:/Program Files/PowerShell/7` is absent.**
Confirmed absent on this host just now (`ls` → no such directory). The lane does **not** remove this either:
nothing in the lane, the registry or the front door installs, provisions or shadows a PowerShell
installation. What exists is a *different* PowerShell — `PowerShell 7.6.9` reachable only through the
`WindowsApps` Store execution alias, which the sandbox refuses with `CreateProcessAsUserW failed: 5`, and a
working non-alias copy at `<HOME>/pwsh7/pwsh.exe` outside the expected install root. So there is a
partial *mitigation available* (point the host at a real pwsh binary), but it is a host-side path/install
action, not something the lane or routing provides, and it does not by itself clear F1, because the
`pwsh7` binary is also rejected inside non-interactive exec. The owner window is the only piece of this
stack with any bearing on F2: it can sign a `HOST_OPERATIONS`-ceiling permit authorising the install
(`PERMIT-WP12-HOST-20261101-01` is precedent) — but a signature authorises a change; it does not perform it.
→ **does not remove F2; does not partially mitigate it.** The window supplies authorisation paperwork for a
host fix, which is a precondition for the repair, not the repair.

**F3 — this slice has no original Case/Oracle registry.**
Untouched, and structurally untouchable by anything in this stack. Lane routing decides *who is asked*; the
checker lane decides *whether a claim is well-formed and evidenced*; neither can manufacture the required
set. The slice says so itself (`HANDOFF.md` §3): the gap is "Slice 無原 Case／Oracle registry … SBL/PIPD 原
Case Owner 提供該 Slice 的 required 集", and `06_closeout_addendum.md` records
`EFFECT_REGISTRY_UNBOUND: needs the original registry owner, **not a fabricated one**`. A checker run over a
fabricated registry would produce a `CANDIDATE_ONLY` verdict with exactly the defect the R10 acceptance
already caught in a different form (a manifest pinning a path that never existed). The one real contribution
here is a guard, not a capability: `config/verify-lane-contract.json` (`claim_ceiling: CANDIDATE_ONLY`,
typed refusal, `NOT_RUN`/`BLOCKED` statuses) plus the `could_not_verify` discipline in R6 give the checker a
mechanism to record "this required set does not exist" as a blocking finding instead of papering over it.
→ **does not remove F3; does not partially mitigate it.** It only makes the gap impossible to close by
assertion.

### One-line verdicts

```
F1 PROCESS_CREATION   : NOT_REMOVED — lane/routing/checker govern model service, not CreateProcess; every
                        exec probe is "blocked by policy" while turns complete, so the two axes are proven
                        independent. Only danger-full-access passes, and it is disqualified as evidence.
F2 PWSH7_PATH_ABSENT  : NOT_REMOVED — no lane artifact installs or shadows PowerShell; the window can sign a
                        HOST_OPERATIONS permit for the install but performs nothing.
F3 NO_CASE_ORACLE_REG : NOT_REMOVED — a routing/verdict capability cannot supply an owner-held required set;
                        the checker's only contribution is to make the absence a blocking, receipted finding.
```

Overall: **the lane + model routing + success capability is real and evidenced, and it removes none of the
three FirstFails.** What it demonstrably delivers is (i) a served, receipted model turn per lane on this host
on both the opencode-go and the ChatGPT-OAuth arms, including `gpt-6.1-sol` at `medium`; (ii) a checker lane
that will fail a maker and states its own ceilings; and (iii) separation of concerns clean enough that a
failure can be attributed to transport or to `CreateProcess` rather than guessed at. What it does not
deliver — and does not claim to — is any ability to create a child process, to install a host interpreter,
or to originate a Case/Oracle registry.

Claim ceiling for this document: it reports what repository artifacts and one read-only host inspection
show on 2026-11-03; it does not re-run any lane, does not verify any live integration, and does not
adjudicate any subject.
