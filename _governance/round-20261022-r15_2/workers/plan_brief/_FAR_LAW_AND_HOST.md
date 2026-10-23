NONCE: PLAN-R153-LAWHOST-115322

Begin your reply with exactly this token on its own line: PLAN-R153-LAWHOST-115322

HARD RULES: do the work in this turn. Do NOT dispatch, spawn or poll another lane or agent (no lane-dispatch, no sub-agent, no waiting loop). If a step would require another lane, write that in your output and stop.

# PLAN brief — three owner-authorised gaps: author the clause, define the two issuance paths

Read-only, one JSON object on stdout. The owner has authorised all three; your job is to produce text and procedures
that can be executed today without forging a signature or inflating a claim.

## Gap 1 — C05/M1: no clause that makes the checker principal enforceably distinguishable

`Fabric/FABRIC/control/SOD_POLICY.yaml` (schema FABRIC-SOD-POLICY/1) lists `incompatible_roles: [[maker, final_checker]]`
but never says how a principal is identified, how the incompatibility is *checked*, or what makes a verdict
inadmissible. `Fabric/FABRIC/assurance/ACCEPTANCE_SCHEMA.yaml` requires `producer_identity` and
`independent_checker_identity` per PASS candidate, again with no enforcement semantics. Result: an external
acceptance officer can only return NOT_ESTABLISHED.

Required: a **complete, usable clause** (YAML block, ready to add to SOD_POLICY.yaml) plus the enforcement
predicates, the principal-record fields, the admissibility rule, and the three negative cases that must make a
verdict inadmissible (same principal as producer; missing principal record; role held by delegation from the
producer). It must be checkable by a local script with no network and no third party, and it must not claim more
than "the two identities are distinct and attested" - not that the checker is competent or independent in intent.

## Gap 2 — C19/M3: W3 native admission, SWOF Domain Owner

The owner states in chat that they are the SWOF Domain Owner and authorises W3. What may the agent legitimately
produce? Design the artefact so that it is an **owner-attested authorisation recorded by the runtime**, never a
cryptographic signature the agent invents, and so that a later real signature supersedes rather than duplicates it.
Name the fields, the TTL, the subject binding (frozen candidate sha + env + ABI), and the claim ceiling string.

## Gap 3 — C21: host-issued plugin IDs, reusing a proven path

Proven precedent (PIPD-LS-SP, round R5Y, private path PASS): upload the zip at `chatgpt.com/plugins` -> sidebar
plugin -> add -> upload archive -> native file dialog -> add plugin -> install -> settings; the host returned
`https://chatgpt.com/plugins/Plugin_5ba168f715b8819190ccbe33a4a926b0`, the installed list showed the manifest
shortDescription, and an `@plugin` invocation in a real chat executed the skill body with fail-closed behaviour.
Driving layer was FDA (cua-driver): background first, structured `background_unavailable` before escalating to
foreground, UIA set_value+Invoke for the native file dialog, zero mouse and zero focus theft where possible.
Owner actions that stayed human in that round: developer identity verification, brand art approval, publish.

Required: the exact step list and the evidence fields that turn a host-issued plugin ID into an admissible C21
cell (URL/ID as returned, install receipt, settings-list readback, invocation transcript, timestamp, account), the
steps that must remain human, and the claim ceiling when only one of three bundles is installed.

## Output

{"clause":{"yaml":"...","enforced_by":"script/function","predicates":["..."],"principal_record_fields":["..."],
  "inadmissible_when":["..."],"claim_ceiling":"..."},
 "w3":{"artefact":"path","fields":["..."],"ttl":"...","may_not":["..."],"verdict_if_superseded":"..."},
 "c21":{"steps":["..."],"evidence_fields":["..."],"human_only":["..."],"claim_ceiling_one_of_three":"..."},
 "tests":[{"file":"...","asserts":"..."}],
 "ordering":"which of the three must land first and why",
 "do_not_claim":["..."]}