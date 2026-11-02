# ADR-0007 — Plugin distribution: private-first, public directory on hold

- **Status:** accepted 2026-10-14 (owner ruling in chat, executed by the round `R5Z-20261014-session-conformance`)
- **Context:** the plan of record asked for a ChatGPT plugin listing. On 2026-10-14 the agent drove
  `platform.openai.com/plugins` with the desktop tooling and the Portal answered *“You need a verified
  developer identity before you can create or upload a plugin.”* Identity/KYC is a human act and the agent
  must not perform it. The **private** path has no such precondition.
- **Decision:** distribute the Skills-only plugin **privately first**. The candidate ZIP is uploaded through
  ChatGPT (`Plugins → Add → Upload plugin archive`), installed, and its skills invoked from a chat. The public
  Directory path stays `HOLD` until the owner completes developer identity verification.
- **Consequences:**
  - `PRIVATE_PLUGIN_CREATED_INSTALLED_INVOKED` is claimed, with per-action evidence
    (`PIPD_S4_R5Y_GPT_PLUGIN_EVIDENCE_RETURN/09_ui_fda/`).
  - `PUBLIC_DIRECTORY_PUBLISHED` and `PUBLIC_CONSUMER_VERIFIED` remain **NOT claimed**.
  - Evidence for external verifiers is published on its own branch
    (`r5z-evidence-return-20261014`), because this stage's positive write-set gate
    (`.github/workflows/public-plugin-verify.yml`) admits only `packaging/public-plugin/`, `docs/install/`,
    `docs/USER_GUIDE.md`, `docs/adr/`, the named tools/tests and `README.md`. Widening that gate to carry
    evidence would weaken a shipped guard; a separate branch does not.
  - Anyone can install it privately today: download the ZIP at the path named in `README.md` and follow the four
    UI steps there. The ZIP's bytes are pinned by SHA-256 in the README.
