# Open TT / FAR / owner decisions

## Owner decisions still required

1. **Resume the R17 durable runner** — cron `3602bce285e8` has been paused since 2026-10-23T22:20:02+08:00.
   Until an owner resumes it, autonomous continuation does not exist. This handoff must not start a
   background process to fake it.
2. **Rotate the OpenCode Go key** that was echoed into tool output in an earlier round.
3. **Issue real Native authority** — HGK WorkOrder/Permit, Fabric Active Designation, SWOF W3, independent
   AO, Release seal. Textual owner order is not a permit.
4. **Deliver the three principal requests** (Native WO/Permit, Host durable runner, independent AO); all three
   are `UNDELIVERED` with no channel receipt.

## Open technical items (agent-doable, listed in AGENT_RESIDUALS_R17.json)

- C18 TQAEP cell manifest (96 cells) — bindable from DOC-08, agent can author
- DEST-01..16 destructive fixtures — agent can build in isolation
- W01-CONF conformance receipt — agent can produce then re-probe
- W05-WIRE two candidate patches — agent can install and re-probe the write chain
- F3B Fabric tamper/revoke/readback — agent can build the negative fixtures
- F3C pipd validate family/schema defect — agent can write the failing fixture
- G1-E2E bounded Codex CLI EXECUTE — needs lane recipe + time-boxed brief

## FAR / TT

Open items are carried in `TT_FAR_R17.json` (embedded in `SESSION_STATE_R17.json`). Two standing conflicts
remain recorded rather than resolved: `CR_R17_LANE_MANDATE_VS_REGISTRY` (per-round role mandate vs registry
epoch 33 declaring deepseek primary for all three lanes) and `TT_R17_SBL_HEAD_NOT_MAIN` (SBL local candidate
branch vs origin/main `dc5428f`).

No FAR claim in this pack asserts a policy, permit or acceptance.
