# FAR ruling — disposition of every open item, and the merge decision

Ruling produced by the PLAN lane (`hgk-lane-dispatch.py --lane PLAN --force-rank 2 --require-arm
openai-codex/gpt-6.1-sol`, nonce `SBLFAR-R2-01`, 169.9 s, `ok: true`, `required_arm == served_arm`).
Verbatim ruling: `81_FAR_RULING.json`, sha256 `bb6ea225ea5b8dba1bb053670ba77ffc1d2f7ab06850048905377b06170816ce`.

The owner pre-authorised this ruling and ordered execution. This file records what the ruling decided,
what has already been executed against it, and what is waiting on a human signature.

## 1. Headline decision

> **MERGE NOTHING UNTIL M4 IS SATISFIED.** Prepare v10 now; do not merge it with a merely declared receipt
> gap. A signed procedural substitution may change *how* M4 is fulfilled, but does not itself constitute
> fulfilment.

That is the ruling's own defence: the external report makes M1–M4 conditions of conditional merge approval,
and its §F2 removes the *unrelated* blockers (donors, full trace, host grid, W3, hygiene) — not M4.

## 2. Sixteen dispositions

| Item | Disposition | Route (condensed) |
|---|---|---|
| M4 independent receipt | `HOLD_SCOPED` | Keep open; a transport failure is not a verdict. Close only with a real receipt on the frozen full SHA |
| R1 licence | `OWNER_DECISION` | MIT for owner-controlled original code, conditional on a shipped-material rights inventory and the copyright owner's signature |
| R2 reproducible package | `HOLD_SCOPED` | Release gate, not a merge prerequisite |
| R3 native/HITL scope | `OWNER_DECISION` | Declare `STANDALONE_ONLY` for any preview; native-effect claims only with a real GJ02 binding |
| `VERIFY10-TOOLING-01` | `DEFER` | Fix in a later isolated patch; do not touch the frozen candidate for hygiene |
| G-KNOW limits | `HOLD_SCOPED` | Keep the limitations register and the new refusal/stamp behaviour |
| 50/149 child trace | `DEFER` | Publish measured status; require closure only when the capability enters committed scope |
| 39 Host×SP grid | `HOLD_SCOPED` | Claim only evidenced combinations |
| `CR-ORACLE-001` / `N14` / Profile-GRP | `HOLD_SCOPED` | Retain unresolved; exclude dependent claims |
| Donor ledger | `DEFER` | Keep the 441-row ledger; no 386-installation programme; `METHOD-18` stays inactive |
| `TS11`/`CHK09` missing ids | `CLOSE_NOW` | Add a compact crosswalk to existing gates; record `NOT_IMPLEMENTED` where coverage is absent; close the identifier gap only |
| `main` protection | `OWNER_DECISION` | Repository administrator confirms rules, or signs a bounded manual merge control; API `403` is unknown visibility, not proof of absent rules |
| SWOF W3 | `HOLD_SCOPED` | Refusal stands; only the SWOF owner can ACK |
| Remote branches | `CLOSE_NOW` | Archive tags first, then delete superseded names; merge only v10 |
| Kanban | `CLOSE_NOW` | Record M1 closed / M2, M3 maker-fixed / M4 blocked in the existing round record |
| OpenSpec v10 delta | `CLOSE_NOW` | Append a v8→v10 delta to the existing change; never report an unrun validator as passed |

## 3. Land / drop

Land: the v10 Shared Core and three SPs (after M4); the M1/M2/M3 repairs with their tests; the manifests,
verification tools and gate commands; `construction-acceptance-prompt-compiler`; `challenge-review`;
the Fabric and PIPD-LS-SP interfaces as locators; HG-KSEOS integration locators.

Drop: vendored copies of the 20 KP documents and the GENIEMAKER volumes (keep permitted locators and
provenance — availability is not redistribution approval); the parallel v1–v9 implementations and the
private-mirror CI dependency; `METHOD-18` activation and any bulk donor installation.

## 4. Executed in this round, against the ruling

| Ruling step | What was done | Evidence |
|---|---|---|
| 1 — establish subject and base | `origin/main` = `ca6830d9fc…`, `v10` = `2d1c32d6c4…`, tree `7dd4d69f24…` | this file §5 |
| 2 — preserve tips before cleanup | 11 `archive/*` tags created and pushed, one per deleted branch tip plus pre-merge `main`; verified by `git ls-remote --tags` | `git ls-remote --tags origin` |
| 10 — delete archived superseded branches | 10 branches deleted, each after its tip was matched against its archive tag; only `v10`, `c1`, `c2`, `main` remain | remote head list below |
| 3 — frozen acceptance packet | `76_ACCEPTANCE_PACKET.md` | that file |
| 4 — reconcile governance records | this file, `82_TS11_CHK09_CROSSWALK.md`, OpenSpec delta, Kanban cards `t_43ae71fd`/`t_41517547`/`t_16531159` done and `t_6754f2a9` blocked | Kanban board `sbl-pipdls-20261020` |
| 5 — bounded lane recovery | attempted and **failed**, see §6 | four receipts in `_sbl_verify/runs-m4*` |

## 5. Frozen subject

- base `main`: `ca6830d9fc9d89b7b87e818670dd67b393472d79`
- candidate: `2d1c32d6c48fdc09a7d529fc4535482283552487`, tree `7dd4d69f249e7d6028c2e8771b15fb31c1ffe704`
- evidence: `evidence/r2-20261020-c2` (this branch), `-c1` for the v8 round
- archive tags: `archive/main-premerge-ca6830d`, `archive/cand-v1-ab17440`, `-v2-8640f02`, `-v3-49dab08`,
  `-v4-7202922`, `-v5-718a48d`, `-v6-eb2e07c`, `-v7-f793e1d`, `-v8-fb7af87`, `-v9-47a428a`,
  `archive/wip-r6-7f33e5c`
- hosted CI: run `39411780991`, jobs `118591058137` (ubuntu) and `118591058453` (windows), `136 passed,
  1 skipped` each

## 6. M4 — why the bounded recovery attempt failed

The ruling's option 1 asks for the VERIFY door on `10103` to be restarted and the *actual* route tested.
Two measurements close that option rather than merely deferring it:

1. The door script `scripts/hgk-exec-model-frontdoor.py` describes itself as a "loopback-only EXECUTE-lane
   protocol proxy … forwarding to the shared relay". It is a model-id policy proxy over HTTP; starting it
   does not add websocket transport, and the failure is a websocket handshake, not a model-id refusal.
2. The shared relay itself answers the upgrade with `426`: measured again this round on `10101` and
   `10102` (`/healthz` 200, `/v1/models` ok, ws handshake 426). `10103`/`10105` are not listening.

So recovery needs a relay-side transport change or an authorised different principal — options 2–5, each of
which the ruling assigns to the lane operator or the acceptance authority, not to the orchestrator. In
parallel this round, an EXECUTE smoke dispatch on the same codex binary succeeded, which locates the fault
precisely: the `opencode-go` provider path is HTTP and works; the `openai-codex` provider path is the one
that demands websocket.

## 7. Waiting on a human signature (nothing below was executed)

1. **Acceptance route** — either repair the relay transport (option 2) or authorise a substitute checker /
   independent human reviewer (options 4–5). Without one, M4 stays open and nothing merges.
2. **`main` publication control** — administrator confirmation of rules, or a signed bounded manual merge
   control naming SHA, base, checks and publisher.
3. **R1 licence** — MIT recommendation plus the shipped-material inventory; the copyright owner signs.
4. **R3 scope** — sign `STANDALONE_ONLY` for any preview.

## 8. Claim ceiling after this round

`v10` is a CI-green candidate. M1 closed; M2/M3 maker-fixed; M4 **OPEN**; `main` unchanged; release
`HOLD_UNTIL_R1_R3`. Not claimed: `MERGED`, `RELEASED`, `INDEPENDENT_CASE_PASS`, `PRODUCTION`,
`SWOF_CONNECTED`.
