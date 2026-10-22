# sbl-native-admission Specification

## ADDED Requirements

### Requirement: Admission is proven by rows, not by state names

HG-KSEOS SHALL be treated as the sole issuer of work orders. A claim that work orders exist MUST be supported by the
work-order rows read back from the shared spine, and MUST NOT be supported by a lifecycle state name alone.

#### Scenario: Lifecycle says admitted but no rows exist

- **WHEN** a project's lifecycle state is `WORKORDERS_ADMITTED` and the spine holds zero work-order rows for it
- **THEN** the admission claim is false and MUST be reported as not admitted

#### Scenario: Rows exist for the project

- **WHEN** the spine holds work-order rows for the project with states `CREATED` or `VERIFIED`
- **THEN** admission may be claimed, citing the row ids

### Requirement: Source binding is complete before admission

Every source root MUST be bound at project creation, because native intake is refused once the project passes
`SOURCE_ADMISSION`. A later discovery of an unbound root MUST be treated as a project defect, not corrected silently.

#### Scenario: A root is discovered late

- **WHEN** a source root is found after admission
- **THEN** the project MUST be re-created with both roots bound, and the abandoned project MUST be annotated, not deleted

### Requirement: A work order result records a distinct checker

Each work order result MUST record a checker principal distinct from the writer value, MUST reference non-empty
evidence, and MUST NOT be recorded by the party that produced the effect.

#### Scenario: Same principal writes and checks

- **WHEN** writer and checker resolve to the same principal
- **THEN** the record is refused, and the independence limitation (same host, same session) MUST be stated separately
  rather than implied by distinct strings

### Requirement: A delivery package excludes its own verification receipts

A package MUST declare its scope rule, MUST exclude the receipts produced by verifying it, and MUST NOT contain the
file that measures the set.

#### Scenario: Exact-set readback after a dispatch

- **WHEN** a verification dispatch writes receipts inside the tree it measures
- **THEN** the package scope MUST exclude that receipts directory, or the readback can never converge

### Requirement: Delivery readiness is not delivery

`DELIVERY_READY` MUST be reported alongside the work-order verdict table. A project with any FAILED work order MUST NOT
be described as delivered, and `DELIVERED` MUST require an owner seal.

#### Scenario: Ready state with failed rows

- **WHEN** the lifecycle reaches `DELIVERY_READY` while work orders are FAILED
- **THEN** the round MUST report the failure set, MUST withhold `DELIVERED`, and MUST file the gate defect
