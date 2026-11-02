# Quarantine fixture corpus: unanchored key pattern vs an identifier tail

This minimal fixture reproduces the real quarantine finding (TT-PIPD-KNOWLEDGE-QUARANTINE,
source SRC-97355259edde717eeaf2 / 05_SDD_ADR_TASKSPEC.md) without shipping the external
corpus. In the lines below `sk-` appears ONLY as the tail of the longer identifier
`spec-plan-task-code-test-review-release`: an unanchored `sk-...` pattern matches it, an
anchored form does not. No credential is present in this file.

extracted_from: ["GPTB-DOC03#system-design-sdd-adr", "GPTA-DOC05#sdd-adr-architecture", "AgenticSWE#issue-task-pr", "SDLC_PRW#spec-plan-task-code-test-review-release"]

| GPTB-KP05-R04 | MUST NOT | Produce reversible PR plan | SDLC_PRW#spec-plan-task-code-test-review-release | TT-KP05-04 when produce reversible PR plan is violated |
| GPTB-KP05-R08 | MUST | Link OROCHI order to TaskSpec IDs | SDLC_PRW#spec-plan-task-code-test-review-release | TT-KP05-08 when link OROCHI order to TaskSpec IDs is violated |
