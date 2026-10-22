# lane-routing — delta spec (R14)

## ADDED Requirements

### Requirement: The deployment plane must serve the declared lane mandate

The lane routing registry, the model/lane assignment, every projection binding and the
deployment pool (`config/lane-route-slots.candidate.json`) SHALL all name the same arm at rank 1
for every governed lane. A mandate that is only declared (registry/projection) while the pool the
dispatcher actually reads still ranks a different arm first SHALL be treated as a defect, because
`--require-arm` then refuses on a pool that no operator can satisfy by intent alone.

#### Scenario: rank-1 agreement across all four declaration surfaces

- **WHEN** an owner order declares PLAN = `openai-codex/gpt-6.1-sol`, EXECUTE = `opencode-go/minimax-m3.1-flash-free`, VERIFY_SECURITY = `openai-codex/gpt-6.1-sol`
- **THEN** registry `routes[].provider/model`, the assignment `lane_chains[0]`, the projection bindings and the pool `lanes[].ordered_pool[0]` all resolve to that arm
- **AND** the demoted arm keeps its place later in the chain instead of being dropped

#### Scenario: a stale pool is caught before dispatch

- **WHEN** the pool's rank 1 disagrees with the registry for a lane
- **THEN** the lane-policy conformance run fails on that lane rather than silently serving the stale arm

### Requirement: An acceptance binding's scope is enforced, not merely declared

Acceptance SHALL refuse a verdict whose evidence subject falls outside the binding's declared
`scope`, with a typed error, instead of recording the verdict and leaving the mismatch to a reviewer.

#### Scenario: out-of-scope subject is refused

- **WHEN** a verdict is recorded against a subject outside the binding scope
- **THEN** the acceptance path raises `ERR_ROLE_BINDING_SUBJECT_OUT_OF_SCOPE` naming the authorised scope
- **AND** nothing is recorded

### Requirement: Lease release returns a typed receipt with explicit revocation semantics

Releasing a lease SHALL return a typed receipt that states what revocation does and does not mean,
so that a released permit is never read as evidence for a later acceptance.

#### Scenario: release receipt is forward-only

- **WHEN** a holder releases a lease
- **THEN** the result carries schema `HGK-LEASE-RELEASE/1` and `revocation_scope = FORWARD_ONLY`
- **AND** previously recorded verdicts are explicitly not retracted by the release
