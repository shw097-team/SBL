# SBL v0.1 architecture

Claim ceiling for every statement in this document: **`CANDIDATE_ONLY`**.
Nothing here is a release statement, a production claim, or an independent
acceptance. The tables describe the code as it exists in this repository and
were checked against the source at the time of writing.

## Shape

```
 Goal ──▶ Spec ──▶ Route ──▶ Bridge ──▶ Verify ──▶ Repair
   │        │         │         │          │          │
   │        │         │         │          │          └─ M06: plan only,
   │        │         │         │          │             NARROW_REPAIR or
   │        │         │         │          │             STOP_ESCALATE
   │        │         │         │          └─ M05: raw receipt + digest,
   │        │         │         │             maker != checker, ceiling
   │        │         │         └─ M04: writeset + HEAD binding,
   │        │         │            apply refused on drift or escape
   │        │         └─ M03: one permitted target per kind, or refusal
   │        └─ M02: source-bound atoms (locator required)
   └─ M01: deterministic goal id, typed refusal on empty title
```

`SharedCore` (`sbl_core/core.py`) holds one instance of each module and exposes
`doctor()`, which reports the module list and the bound root. Classes do not
call each other directly; the caller passes DTOs from one module to the next.

## Module map

| Module | File | Responsibility |
|---|---|---|
| `SBLM01` Goal Intake | `sbl_core/m01_intake.py` | Turns a request into a validated `Goal` with a deterministic id; refuses empty, non-string, and over-200-character titles. |
| `SBLM02` Guided Specification | `sbl_core/m02_spec.py` | Derives ordered `SpecAtom`s from clauses; every atom needs a non-empty `locator`; duplicate text collapses. |
| `SBLM03` Governed Routing | `sbl_core/m03_routing.py` | Maps one requirement kind to exactly one permitted target, or raises; `AGENT_OS` / `AI_SYSTEM` are prohibited in v0.1. |
| `SBLM04` Governed Build Bridge | `sbl_core/m04_bridge.py` | Binds repo `HEAD`, issues a `BuildOrder` for a writeset, and applies writes only inside that writeset and only while `HEAD` is unchanged. |
| `SBLM05` Evidence Verification | `sbl_core/m05_verify.py` | Records command evidence with a stdout digest and denominator; refuses self-check, proxy statuses, and claims above the ceiling. |
| `SBLM06` Bounded Repair | `sbl_core/m06_repair.py` | Plans a narrow repair from an evidence reference and hard-stops at the attempt cap; no repair without evidence. |

Supporting core files: `dto.py` (frozen dataclasses and deterministic ids),
`errors.py` (the single table of typed refusal codes), `modes.py` (the 39
mode/gate rows), `gknow.py` (local, source-bound retrieval), `core.py`
(composition root).

The SP layer is `sbl_sp/sp.py` (manifest loading, permission checks, challenge
signing) and `sbl_sp/bridge.py` (`SkillBridge`). The CLI is
`sbl_cli/sbl_todo.py`. `tools/verify_source.py` recomputes the frozen source
digests; `tools/run_gates.py` freezes raw gate receipts; `tools/secret_scan.py`
scans the published tree.

## SP separation

Each manifest lives in `sbl_sp/manifests/` and declares exactly what the
principal may do and what it must never do. `assert_permission` refuses an
action that is absent from `permissions` *or* listed in `forbidden`.

| Manifest | Permissions | Forbidden |
|---|---|---|
| `tpm_sp.json` | `goal.read`, `spec.write`, `evidence.read` | `product.write`, `challenge.sign` |
| `commander_sp.json` | `product.write`, `build.route`, `evidence.read` | `challenge.sign`, `verdict.sign` |
| `external_challenge_sp.json` | `evidence.read`, `challenge.sign` | `product.write`, `goal.write` |

Only `external_challenge_sp` is read-only and only it may sign a challenge.
The build principal cannot sign; the signing principal cannot write product.
`sign_verdict` additionally refuses when the signing principal is the maker
(`SBL_E_SELF_CHECK_FORBIDDEN`), and that check runs even for a permitted
signing principal.

## Modes

`MODES` is `STANDALONE`, `PREW3_SHADOW`, `SWOF_CONNECTED`; `GATE_IDS` is
`G00..G12`, so `mode_gate_matrix()` returns 39 unique rows. Dispositions are
`ACTIVE`, `SHADOW_NOEFFECT`, `BLOCKED_EXTERNAL`.

| Mode | Effect allowed | Refusal code |
|---|---|---|
| `STANDALONE` | `local.write` and `local.read` only; any other effect returns `allowed=False, no_effect=True, reason="EFFECT_NOT_ALLOWED"` | none — the refusal is a value, not an exception |
| `PREW3_SHADOW` | none, for any effect; returns `allowed=False, no_effect=True, reason="SHADOW_READ_ONLY_NO_EFFECT"` | none — shadow never acts |
| `SWOF_CONNECTED` | only with a complete native ack (`issuer`, `permit_id`, `subject_id`, `signature`, all non-empty) | `SBL_E_REQUIRES_NATIVE_ACK` |

An unknown mode name raises `SBL_E_UNKNOWN_MODE`. `SWOF_CONNECTED` is not
claimed connected: the code path exists, no native receiver has issued an ack
for this build.

## Evidence flow

```
 gate command ──▶ raw receipt ──▶ independent checker ──▶ verdict
   (exit code)     (stdout/err     (distinct principal,      (ceiling-bounded)
                    + sha256         read-only)
                    + denominator)
```

1. **Gate.** One command with one exit code and a non-zero denominator. A gate
   is never "passed" by inspection.
2. **Raw receipt.** `EvidenceVerification.record` stores the command, exit
   code, stdout `sha256`, and denominator; `tools/run_gates.py` freezes the raw
   stdout/stderr under `evidence/gates/`.
3. **Independent checker.** `EvidenceVerification.verdict` refuses
   `maker == checker` (`SBL_E_SELF_CHECK_FORBIDDEN`), refuses proxy statuses
   such as `FILE_EXISTS` or `SUMMARY_ONLY`, and refuses a claim ranked above the
   ceiling (`SBL_E_CLAIM_CEILING_EXCEEDED`, ranks `LOCAL` < `PACKAGE` <
   `EXTERNAL_ACCEPTANCE` < `PRODUCTION`).

Maker and checker are separate lanes in the governance model; a green local
run is `LOCAL` evidence only.

## Trust boundaries

- Product code is standard library only; `pytest` appears in tests, not in
  runtime imports.
- Every refusal is an `SBLError` with a code from `sbl_core/errors.py`; bare
  exceptions and silent `None` are not part of the contract.
- Path handling in the bridge resolves against the order root, rejects
  absolute paths and `..` traversal, and then checks the resolved relative
  path against the writeset prefixes.
