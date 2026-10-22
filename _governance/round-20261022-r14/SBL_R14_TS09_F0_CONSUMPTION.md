# R14-TS09 — Fabric F0 consumption, six edges, one subject

Measured 2026-10-22 · evidence `raw/ts09_f0_trace.json` + `raw/e6_observer.json`
Tracer: `HG-KSEOS/var/R14-F0-20261022/f0_trace.py` (re-runnable; refuses to fill a missing edge)

## Verdict

`PASS_F0_CONSUMPTION` — six edges, one subject tuple, one of them observed by a **different principal**.

| edge | owner | readback | state |
|---|---|---|---|
| **E1** Fabric policy | Fabric (policy owner) | sha256 of `FABRIC/rp002/RP002_CHANGE_CLASS_ROUTER.yaml`, `control/ACCEPTANCE_POLICY.yaml`, `control/SOD_POLICY.yaml` | read |
| **E2** HGK route (policy consumption) | HGK orchestrator wrapper | `route_event(STACK_CHANGE)` → `route=ORACLE_TO_HGK`, `verdict=ROUTE_OK`, and `router_sha256_used == E1.router_sha256` | read |
| **E3** HGK native method | `hg_kseos.named_methods.route` | returns its own route decision for the round's flow | read |
| **E4** HGK WorkOrder | Shared Spine | `WO-TS-WO-01` / `TS-WO-01`, writer `codex`, `base_head b22706eb…`, state `VERIFIED` | read |
| **E5** effect | Codex writer → git object | working-tree sha256 `fc34fb7d…` equals the git blob of `fca4dfa:src/hg_kseos/capability_delta.py` | read |
| **E6** observer | VERIFY_SECURITY lane (`openai-codex/gpt-6.1-sol`) | measured the same file **itself** with `Get-FileHash` → `fc34fb7d…`, matches E5 | OBSERVED (independent principal) |

Subject tuple asserted identical across edges: `{policy_sha256, workorder_id, artifact_sha256, commit}`.
Join checks: 6/6 true, including `fabric_not_issuer`.

## E2 is a real consumption, not a mention

The order rejects "policy file exists" as evidence. So E2 does not assert that the policy *exists*; it asserts that
the decision was computed **from the same bytes** E1 digested (`router_sha256_used == E1.router_sha256`), i.e. the
route verdict would change if that file changed. The first version of this tracer checked a meaningless inequality
instead; it was rewritten before the verdict was reported.

## Fabric is not a second issuer

`fabric_is_not_an_issuer` scans the consumer source for issuance verbs (`issue_permit`, `grant_permit`, `issue_ecp`,
`sign_acceptance`) — none exist. Fabric routes and classifies; HGK issues WorkOrders/permits and signs acceptance.
That is the boundary the order demands, checked in code rather than asserted in prose.

## Measured defect found by doing this (TT-R14-020)

The shipped consumer `Fabric/FABRIC/fabric/consumers/hgk_policy_consumer.py` hardcodes

```python
FAB = Path(r"C:\Projects\Agent_Workspace\Fabric")
router = FAB / "rp002" / "RP002_CHANGE_CLASS_ROUTER.yaml"     # -> Fabric\rp002\...
```

while the canonical file is `Fabric\FABRIC\rp002\RP002_CHANGE_CLASS_ROUTER.yaml`. Running `selfcheck` therefore dies:

```
FileNotFoundError: 'C:\\Projects\\Agent_Workspace\\Fabric\\rp002\\RP002_CHANGE_CLASS_ROUTER.yaml'
```

So as shipped, **the Fabric policy consumer cannot route at all**. This round's tracer loads the module and supplies
the real path, and the defect is recorded rather than patched into Fabric, because Fabric's contract face is not this
round's to change. The one-line upstream fix (`FAB = Fabric / "FABRIC"`) belongs to Fabric's owner; until then no
consumer of this module can produce E2 honestly.

## Ceiling

One subject tuple. It proves the path is real for this subject; it does not prove that every HGK task consumes Fabric
policy, and it does not promote M1 — TS09 is one of the obligations M1 waits on, not M1 itself.
