# sbl-core delta — SBL v0.1

## ADDED Requirements

### Requirement: Single Shared Core with six logical modules
The system SHALL expose exactly one Shared Core that hosts the six logical modules `SBLM01` (Goal Intake),
`SBLM02` (Guided Specification), `SBLM03` (Governed Routing), `SBLM04` (Governed Build Bridge),
`SBLM05` (Evidence Verification) and `SBLM06` (Bounded Repair/Evolution), and SHALL NOT create a second
orchestrator, task database, evidence authority or reducer.

#### Scenario: module dispatch stays inside the single core
- **WHEN** a caller submits a goal through the CLI or API
- **THEN** the request is handled by the Shared Core registry, every stage transition is recorded, and no
  second router or store is created

### Requirement: Three responsibility-separated SPs
The system SHALL provide `TPM-SP`, `Commander-SP` and `External Challenge-SP` as separate surfaces with
their own manifests and permissions, and the external challenge surface SHALL be read-only with respect to
product state.

#### Scenario: maker cannot self-sign acceptance
- **WHEN** the maker identity attempts to record an external acceptance verdict
- **THEN** the system refuses with a typed error and the verdict remains absent

### Requirement: Mode gating with NoEffect shadow
The system SHALL support `STANDALONE`, `PREW3_SHADOW` and `SWOF_CONNECTED`, where `PREW3_SHADOW` performs no
world-affecting effect and `SWOF_CONNECTED` stays blocked until a native receiver ACK and Permit are present.

#### Scenario: shadow mode performs no effect
- **WHEN** the product runs in `PREW3_SHADOW`
- **THEN** every effect stage reports `NO_EFFECT` and no external write is attempted

### Requirement: Golden journey GJ01 CLI tool lifecycle
The system SHALL provide an installable `CLI_TOOL` (`sbl-todo`) whose lifecycle is verified end to end:
install into an isolated user data directory, `add --title <unique>`, `list --json` returning the same
id/title/status, survive a restart, and uninstall without residue.

#### Scenario: add then list after restart
- **WHEN** a user installs the tool, adds one item and restarts the process
- **THEN** `list --json` returns exactly that item with an unchanged id, title and status, and uninstall
  leaves no files in the isolated data directory
