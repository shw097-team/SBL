# 30 — Lane, model and base reuse (what was reused instead of rebuilt)

R3 inherits the HG-KSEOS lane plane rather than inventing a second dispatch path. The distinction the
instruction insists on is kept: **the lane model and the session model are two different planes.** This
session's interactive model pins nothing; `hgk-lane-dispatch.py --model` pins the child process.

## 1. Reused, not rebuilt

| Asset | Path | How R3 used it |
|---|---|---|
| Lane dispatch CLI | `HG-KSEOS/scripts/hgk-lane-dispatch.py` | the only way a lane process was started |
| Lane route slots | `HG-KSEOS/config/lane-route-slots.candidate.json` | arm/pool resolution, never a session pin |
| Codex binary pin | `.../Codex/bin/896a0166b774037a/codex.exe` (0.163.0-alpha.10.2) | required explicitly; the path inside `hermes-codex-lane.json` is stale |
| Gate runner | `SBL/tools/run_gates.py` | 11 gates, pytest env pinned |
| Secret scanner | `SBL/tools/secret_scan.py` | 229 files scanned on the candidate branch worktree, 0 hard findings |
| Source verifier | `SBL/tools/verify_source.py` | `--verify` re-hashed 14/14 books locally |
| Gate matrix | `SBL/sbl_core/modes.py` | 3 modes × 13 gates = 39 cells, unchanged |
| Donor ledger | `_governance/round-20261020-r2/17_DONORS/DISPOSITION_TABLE.json` | 441 rows reused verbatim, 2 amended |
| Human review pack | `84_HUMAN_REVIEW_PACK.md` | the six properties in R3 M4-LITE are the same six |

## 2. Lane reality measured this round

```
10100 CLOSED   10101 OPEN (/healthz 200, websocket handshake 426)
10102 OPEN (/healthz 200, websocket handshake 426)
10103 CLOSED   10105 CLOSED
```

Recorded facts, unchanged from R2:

- `openai-codex` traffic goes over a websocket; the relay answers **426 Upgrade Required**. This is a
  transport refusal, not a model refusal, and it is why VERIFY-11..14 never produced a receipt.
- `-c prefer_websockets=false` is ignored by codex 0.163 — it logs the key as unknown and connects over
  the websocket anyway. There is no supported switch to force HTTP.
- `10103`/`10105` are HTTP model-id proxies in front of the same relay. Restarting them cannot create a
  websocket endpoint, so "restart the door and retry" was ruled out by measurement, not by opinion.
- `opencode-go/deepseek-v4.1-flash` on the same lane plane answered `ok:true` (EXECUTE smoke
  `SBLEXEC-SMOKE-01`), so the fault is specific to the `openai-codex` transport, not to the lanes.

## 3. Consequence for R3, and the authorised substitute

The mandated checker is `openai-codex/gpt-6.1-sol`. Two carriers were tried in R2:

1. `VERIFY_SECURITY` lane → `ERR_LANE_ALL_ROUTES_EXHAUSTED` on the 426.
2. `PLAN` lane with `--sandbox read-only` → **works** (VERIFY-15 ran 501 s and produced a FAIL with four
   real defects). Rounds 16 and 17 were then cut by the provider's content filter
   (`This content was flagged for possible cybersecurity risk`), not by the lane.

R3 does **not** retry that path a fourth time. Per the audit's §2 and `90_OWNER_DECISIONS.md`, the
remaining carrier for M4-LITE is a human reviewer running `M4LITE/run_m4lite.py`, which this round
produced and executed as far as a maker legitimately can.

## 4. PIPD official writer — not executed here

`pipd-route-intake`, `pipd-authority-source`, `pipd-profile-tailor`, `pipd-pi-compile`, `pipd-pd-bind`,
`pipd-execution-contract`, `pipd-assurance-tqaep`, `pipd-package-project` are **specifications and
skills**, not executables in this workspace. No native PI/PD was produced this round, so
`PIPD_PI_PD_BOUND` is not claimed and TS12/CHK10 stay `NOT_RUN`. `construction-acceptance-prompt-compiler`
compiles a contract; it is not a substitute for a PIPD native PI/PD, and `PROMPT_COMPILE_PASS` says only
that the contract's shape and acceptance edges are sound.

## 5. What was deliberately *not* reused

- The R2 `candidate/r2-20261020-v13` tree was not re-litigated. A and B build on `bedc119` exactly.
- v8-era defect rulings are not re-applied to v13; the audit says those were fixed in v10–v13 and this
  round agrees with the tree, not the old narrative.
- The private corpus was not copied into the public repo; only hashes and locators.
