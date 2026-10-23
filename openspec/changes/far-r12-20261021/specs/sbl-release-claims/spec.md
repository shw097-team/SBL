# sbl-release-claims Specification

## ADDED Requirements

### Requirement: Public claim text matches the published artefacts

The public claim text SHALL name only artefacts that exist: the two pre-release tags `v0.1.0-foundation-preview`
and `v0.1.1rc1`, and the three console scripts the packaging metadata installs. A claim that names a release the
repository does not carry, or a console-script count that disagrees with `pyproject.toml`, MUST be treated as a
defect and fixed, not restated.

#### Scenario: Claim section is read against the published tags

- **WHEN** the README status and claim section is read against the tags present in the repository
- **THEN** every release it names is a tag that exists, and it describes both as pre-release rather than production

#### Scenario: Claim states how many console scripts exist

- **WHEN** the claim text states the number or names of the installed console scripts
- **THEN** that statement matches the entry points declared in `pyproject.toml`, which installs three

### Requirement: A conformance count is only valid with its tree state

A conformance count SHALL be published only together with the tree state it was measured on. A count published
without its tree state MUST NOT be compared against a count taken on a different tree.

#### Scenario: A count is reported

- **WHEN** a round reports a pass/fail count from the conformance suite
- **THEN** the report states the tree state the count was measured on, so the count can be reproduced or discarded

#### Scenario: Two counts disagree

- **WHEN** two counts for the same revision differ
- **THEN** the tree states are compared before the difference is called a regression, because other authors'
  uncommitted files change the tree a count is measured on

### Requirement: The control package is pinned by identity, with its negative controls

The control package SHALL be pinned by identity, and the pin MUST be accompanied by three negative controls that
demonstrate what the pin refuses. An identity pin SHALL NOT be described as a native admission or as a host
installation, because it establishes neither.

#### Scenario: The pin is claimed as landed

- **WHEN** a claim states that the control package is pinned
- **THEN** the pin is identified and the three negative controls exist alongside it

#### Scenario: The pin is described in claim text

- **WHEN** the pin is mentioned in public claim text
- **THEN** it is described as an identity pin only, and no native effect or host installation is implied

### Requirement: The native chain is not claimed by this change

This change SHALL NOT claim the native chain WorkOrder to ONE ECP to Permit to writer to isolated checker. The round
MUST report that chain as still not established, and `SBL_FULL_PRODUCT` MUST remain OPEN. No completion percentage
SHALL be published, because the semantic denominator stays `UNKNOWN` until an owner signs one.

#### Scenario: The claim ceiling is read

- **WHEN** the claim ceiling of this change is read
- **THEN** it names the native chain as not established and keeps `SBL_FULL_PRODUCT` OPEN

#### Scenario: A completion figure is requested

- **WHEN** a percentage or completion figure is requested from this change
- **THEN** the answer is `UNKNOWN`, because no signed semantic denominator exists
