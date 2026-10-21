# TT-R6-VERIFY-TRANSPORT-VOCAB-001

- Subject: config/lane-route-slots.candidate.json (commit c442f07, 2026-10-21 12:11, epoch 23 realignment)
  set transport_model='openai-codex/gpt-6.1-sol' on the openai-codex arms; the opencodex relay route
  answers 400 'Model is unavailable' for that qualified vocabulary.
- Evidence A (fail): var/R6-CHKS/verify_probe5.json — attempts[0] usage_status=400,
  stderr 'Provider error 400: Upstream request failed: Model is unavailable.'
- Evidence B (pass, controlled probe pool in var/, NO config mutation): var/R6-CHKS/verify_probe6_bare.json —
  required/served arm openai-codex/gpt-6.1-sol, transport_model 'gpt-6.1-sol' (bare), usage 200,
  nonce present, usage provider openai-p6a1fe3. Same vocabulary proven in
  var/FAR-LANE-VERSION-MIX-20261021 (R5-era receipts, tp 'gpt-6.1-sol', 200).
- Earliest owner: HGK lane-routing owner (or Codex who landed c442f07 via WO-FAR-LANE-MIX-001).
- Impacted gate: R6-TS29 independent checker run (PLAN/VERIFY lane under the GPT mandate).
- Next probe: owner-authorized config repair changing ONLY the transport_model literal back to
  'gpt-6.1-sol' on the openai-codex arms (or a relay-side alias), then re-run health probes.
- Interim legal path: dispatch with --pool var/R6-CHKS/probe-pool-bare.json (this file carries the same
  identity gate and sandbox declarations; deviation is disclosed per round, not silently normalized).
