# FAR r12 — O-4 / D-14 closure: plugin packaging authority + NOBJ-017 exception record

- **Status**: `CANDIDATE_ONLY` — owner-decision *record*; NOT self-accepted; verifier gate (`t_00d2062c`) pending; synthesizer (`t_5f76be91`) lands into canonical docs.
- **Round**: FAR r12 swarm (board `sbl-r12-far`), worker `t_0d384783`.
- **Recorded**: 2026-10-23 (UTC+8).
- **Decision basis**: R13 `CR-PLUGIN-SCHEMA-AUTHORITY` (`DECIDED_BY_OWNER_PREAUTHORIZATION`) + R14 surface-selection adjudication (current, 2026-10-22). This record **confirms and formalises** that owner-preauthorized decision for FAR r12 O-4; it does not invent a new ruling and does not self-accept.

---

## 1. Decision (O-4: choose the plugin packaging authority)

The compliant **plugin packaging authority** for the three SPs (TPM / Commander / Challenge) is:

> **ChatGPT private GPT (GA) surface, under `DOC-12 C36.3`** — a lawful, non-draft host surface.

Explicitly **REJECTED** as a packaging authority:

> **Agent Plugins 1.0 Working Draft** (`agent-plugins.org/schemas/1.0.0`) — this is `NOBJ-017`, a QUARANTINED / PROHIBITED draft. It is NOT adopted, NOT shipped, NOT installed, NOT validated.

**Rationale.** The only plugin-*marketplace* packaging currently consumable is the NOBJ-017 draft (prohibited). The ChatGPT private GPT (GA) surface is a separate, lawful delivery surface named by `DOC-12 C36.3`, and satisfies the delivery-surface *intent* of `C-016..C-018` without adopting the prohibited draft (R14s12 finding, `CR-R14S12-PLUGIN-SCHEMA = ADJUDICATED_FOR_SURFACE_SELECTION`).

## 2. NOBJ-017 exception record

| Field | Value |
|---|---|
| Named object | `NOBJ24/NOBJ-017` = "Agent Plugins 1.0 Working Draft" |
| Frozen disposition | `PROHIBITED` — **UNCHANGED; not de-prohibited by this record** |
| Source | `DOC-06:L317` (441 identity ledger `SBL/evidence_ledger/source_identity_441_ledger.json:513-518`) |
| Conflicting requirement | `DOC-12#C-016..C-018` = capability `SP_HOST_INSTALL_REQUEST` + `ACC-SP_HOST_INSTALL_REQUEST` + `ACC-TOOL_TPM_SP` (contract `contracts/SBL_C0_C9_CONTRACT-R9.json:589-606, 1805-1839`): the three SPs must install / invoke / uninstall in a host harness |
| Exception granted | Select the **lawful non-draft surface** (`ChatGPT private GPT (GA)`, `DOC-12 C36.3`) as the packaging authority. `NOBJ-017` (draft) is NOT used. |
| Surfaces affected | `C-016`, `C-017`, `C-018` remain **`HOST_PENDING`** (three private GPTs 0/3, no Host-issued id). **None** upgraded to `HOST_ACCEPTED`. |
| Reading position | **B1** (treat `$schema` as host-ingestion metadata only; NOBJ-017 stays PROHIBITED) — reaffirmed; no ZIP/package capability upgraded to `HOST_ACCEPTED` (r6 `90_EVIDENCE/TT_CR_REGISTER.json`). |
| Reversal condition | If an official, non-draft, verifiable Host packaging surface appears, owner opens a **NEW** CR; `C-016..C-018` full lifecycle (create→install→`@invoke`→deny→uninstall) must then be re-run. |
| NOT claimed | No Host install, no Host-issued id, no native effect, no "3/3 installed". Any such claim is false. |

## 3. Claim ceiling — what this record does NOT do

- Does **NOT** de-prohibit `NOBJ-017`: `DOC-06:L317` stays `PROHIBITED` in the frozen 441 ledger — **ledger untouched**.
- Does **NOT** install or validate the `agent-plugins.org` draft.
- Does **NOT** close `C-016..C-018`: they stay `HOST_PENDING` until host permission.
- **Candidate-only**: locally verified against source this round; **not** externally accepted (no verifier gate yet, no independent-checker run this round). Control-package pin **not** regressed (contract R9 untouched; no disposition edited).

## 4. Evidence (direct reads this round — independently verifiable)

- 441 identity ledger: `NOBJ-017` = `PROHIBITED` @ `source_identity_441_ledger.json:513-518` (source `DOC-06:L317`).
- Control-package contract: `DOC-12#C-016..C-018` @ `SBL_C0_C9_CONTRACT-R9.json:589-606` (capability `SP_HOST_INSTALL_REQUEST`, action `INSTALL`) and `:1805-1839` (acceptance `ACC-SP_HOST_INSTALL_REQUEST`, terminal `INDEPENDENT_CASE_PASS`).
- R13 CR (decision): `_governance/round-20261021-r13-native/CR-PLUGIN-SCHEMA-AUTHORITY.md` (byte-identical copy at `_r13_far/`), `DECIDED_BY_OWNER_PREAUTHORIZATION`.
- R14 registers (current, Oct 22): `_r14_ev/_governance/round-20261022-r14/SBL_R14_TT_CR_REGISTER.json` (`CR-PLUGIN-SCHEMA-AUTHORITY = HOST_PENDING`); `_r14s12_ev/SBL_R14S12_TT_CR.json` (`CR-R14S12-PLUGIN-SCHEMA = ADJUDICATED_FOR_SURFACE_SELECTION`; draft stays QUARANTINED).

## 5. Landing edit for the synthesizer (do NOT apply on the shared evidence branch here)

`_r12_docs` sits on branch `evidence/r13-20261021-native`; four sibling workers are closing O-1/O-2/O-3/O-5 against the same `tasks.md`. Landing is the synthesizer's job (`t_5f76be91`). Prepared edit:

- `openspec/changes/far-r12-20261021/tasks.md` line 19:
  - from: `- [!] O-4 plugin schema authority: pick the compliant packaging surface and record the exception to NOBJ-017.`
  - to:   `- [x] O-4 plugin schema authority: chosen surface = ChatGPT private GPT (GA, DOC-12 C36.3); NOBJ-017 (Agent Plugins 1.0 WD) stays PROHIBITED; C-016..C-018 remain HOST_PENDING. See CR-PLUGIN-SCHEMA-AUTHORITY + O4_NOBJ017_EXCEPTION_RECORD.`
- `_governance/round-20261021-r12-far/FAR_DEVIATION_STUDY.md` D-14 row `FAR 裁決` cell → decided (point to the CR). `O-4` table row → decided.
